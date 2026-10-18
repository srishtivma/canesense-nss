"""
CaneSense core: signal processing, water-balance model and advisory logic.

Everything here is plain Python (numpy + pandas) so it can be tested without the UI.
"""
from __future__ import annotations

import json
import math
import urllib.request
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

PUMP_RATE_DEFAULT = 3.75      # mm per hour
KC_REFERENCE = 1.25           # crop coefficient at which the data is assumed recorded (grand growth)
KY_SUGARCANE = 1.2            # FAO-33 yield response factor
ACRE_M2 = 4046.86

KIAAR_LAT, KIAAR_LON = 16.3333, 75.2867   # KIAAR, Sameerwadi (Bagalkot, Karnataka)
VILLAGES = {                               # approximate town centres, used for the weather forecast
    "Sameerwadi (KIAAR)": (KIAAR_LAT, KIAAR_LON),
    "Jamkhandi": (16.5040, 75.2910),
    "Bagalkot": (16.1817, 75.6958),
    "Gokak": (16.1667, 74.8333),
    "Belagavi": (15.8497, 74.4977),
}

CROP_STAGES = {
    "Germination (0–45 days)": 0.40,
    "Tillering (45–120 days)": 0.75,
    "Grand growth (120–270 days)": 1.25,
    "Maturity (270+ days)": 0.75,
}


# ----------------------------------------------------------------------------- data loading
def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]
    if "timestamp" not in df.columns:
        raise ValueError("The file needs a 'timestamp' column.")
    if "soil_moisture_pct" not in df.columns and "sensor_voltage_v" not in df.columns:
        raise ValueError("The file needs a 'soil_moisture_pct' column.")
    if len(df) < 72:
        raise ValueError("Need at least 3 days (72 hourly rows) of readings.")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    for c, default in [("rainfall_mm", 0.0), ("irrigation_mm", 0.0), ("pump_on", 0), ("power_available", 1)]:
        if c not in df.columns:
            df[c] = default
        df[c] = df[c].fillna(default)
    for c in ["soil_moisture_pct", "sensor_voltage_v", "soil_temp_c", "air_temp_c", "humidity_pct"]:
        if c not in df.columns:
            df[c] = np.nan
    df["hour"] = df["timestamp"].dt.hour
    df["date"] = df["timestamp"].dt.date
    return df


# ----------------------------------------------------------------------------- weather forecast
def rain_forecast(lat: float, lon: float, days: int = 7) -> list[float] | None:
    """Daily rain (mm) for the next `days` days from Open-Meteo (free, no key). None if offline."""
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat:.4f}&longitude={lon:.4f}&daily=precipitation_sum"
           f"&timezone=Asia%2FKolkata&forecast_days={days + 1}")
    try:
        with urllib.request.urlopen(url, timeout=6) as r:
            rain = json.load(r)["daily"]["precipitation_sum"]
        return [round(float(x or 0), 1) for x in rain[1:days + 1]]   # skip today, take the next 7 days
    except Exception:
        return None


# ----------------------------------------------------------------------------- helpers
def ols(X: np.ndarray, y: np.ndarray) -> dict:
    """Ordinary least squares. X already contains the intercept column."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    res = y - pred
    sst = float(((y - y.mean()) ** 2).sum())
    sse = float((res ** 2).sum())
    return {
        "beta": beta,
        "r2": 1 - sse / sst if sst > 0 else 0.0,
        "sigma": math.sqrt(sse / max(1, len(y) - X.shape[1])),
        "n": len(y),
    }


def median_filter(x: np.ndarray, w: int = 5) -> np.ndarray:
    return pd.Series(x).rolling(w, center=True, min_periods=1).median().to_numpy()


def moving_average(x: np.ndarray, w: int) -> np.ndarray:
    """Convolution with h[n] = 1/w (centred, shorter window at the edges)."""
    return pd.Series(x).rolling(w, center=True, min_periods=1).mean().to_numpy()


# ----------------------------------------------------------------------------- main processing
@dataclass
class Field:
    df: pd.DataFrame
    raw: np.ndarray
    filled: np.ndarray
    med: np.ndarray
    trend: np.ndarray
    gaps: list
    spikes: list
    cal: dict | None
    days: pd.DataFrame
    A: dict
    power_on: np.ndarray
    w_start: int
    w_len: int
    pump_rate: float
    events: list
    thr: dict = field(default_factory=dict)


def process(df: pd.DataFrame) -> Field:
    raw = df["soil_moisture_pct"].to_numpy(float)
    volt = df["sensor_voltage_v"].to_numpy(float)

    # Voltage → moisture calibration (linear least squares)
    ok = ~np.isnan(raw) & ~np.isnan(volt)
    cal = None
    if ok.sum() > 10:
        f = ols(np.c_[np.ones(ok.sum()), volt[ok]], raw[ok])
        a, b = f["beta"]
        cal = {"a": a, "b": b, "r": float(np.corrcoef(volt[ok], raw[ok])[0, 1]), "n": int(ok.sum()),
               "v": volt[ok], "m": raw[ok]}
        use_v = np.isnan(raw) & ~np.isnan(volt)          # moisture missing but voltage present
        raw = raw.copy(); raw[use_v] = a + b * volt[use_v]

    gaps = list(np.where(np.isnan(raw))[0])
    filled = pd.Series(raw).interpolate(limit_direction="both").to_numpy()
    med = median_filter(filled, 5)
    spikes = list(np.where(np.abs(filled - med) > 2)[0])
    trend = moving_average(med, 24)

    work = df.assign(trend=trend)
    days = work.groupby("date").agg(m=("trend", "last"), rain=("rainfall_mm", "sum"), irr=("irrigation_mm", "sum")).reset_index()
    days["m_prev"] = days["m"].shift()
    days["dm"] = days["m"] - days["m_prev"]
    d = days.dropna()

    # Water-balance model: Δm = β0 + β1·I + β2·R
    A = ols(np.c_[np.ones(len(d)), d.irr, d.rain], d.dm.to_numpy())
    A["assumed_irr"] = False
    if not A["beta"][1] > 0:          # no irrigation in the file → fall back to a typical response
        f = ols(np.c_[np.ones(len(d)), d.rain], d.dm.to_numpy())
        A = {**f, "beta": np.array([f["beta"][0], 0.06, f["beta"][1]]), "assumed_irr": True}
    if not A["beta"][2] > 0:
        A["beta"][2] = A["beta"][1]

    # Electricity window from power_available
    by_hour = df.groupby("hour")["power_available"].mean().reindex(range(24), fill_value=1)
    on = (by_hour > 0.5).to_numpy()
    starts = [h for h in range(24) if on[h] and not on[(h - 1) % 24]]
    w_start = starts[0] if starts else 0
    w_len = 0
    while w_len < 24 and on[(w_start + w_len) % 24]:
        w_len += 1

    irr = df["irrigation_mm"].to_numpy(float)
    idx = np.where(irr > 0)[0]
    pump_rate = float(irr[idx].mean()) if len(idx) else PUMP_RATE_DEFAULT
    events = []
    for i in idx:
        if events and i == events[-1]["end"] + 1:
            events[-1]["end"] = i; events[-1]["hours"] += 1; events[-1]["mm"] += irr[i]
        else:
            events.append({"start": i, "end": i, "hours": 1, "mm": irr[i]})

    dm = days["m"].to_numpy()
    thr = {"target": round(float(np.percentile(dm, 75)), 1),
           "refill": round(float(np.percentile(dm, 25)), 1),
           "stress": round(float(dm.min()) - 0.5, 1)}
    return Field(df, df["soil_moisture_pct"].to_numpy(float), filled, med, trend, gaps, spikes, cal, days,
                 A, on, w_start, w_len, pump_rate, events, thr)


# ----------------------------------------------------------------------------- advisory
def make_plan(F: Field, m0: float, rain: list, thr: dict, kc_ratio: float, delay: int = 0, irrigate: bool = True):
    """Day-by-day forecast. Decision on night k (k=0 is tonight) acts on day k+1."""
    b0, b1, b2 = F.A["beta"]
    dry = b0 * kc_ratio
    m = m0
    path, plan, notes = [m0], [0.0] * len(rain), [""] * len(rain)
    delayed, first = 0, -1
    for k in range(len(rain)):
        water = 0.0
        if irrigate and m <= thr["refill"]:
            r_next = rain[k] + (rain[k + 1] if k + 1 < len(rain) else 0)
            need = (thr["target"] - m) / b1 - r_next * b2 / b1
            if need <= 0:
                notes[k] = "rain"
            elif delayed < delay:
                delayed += 1; notes[k] = "delayed"
            else:
                water = need; plan[k] = need
                if first < 0:
                    first = k
        m = m + dry + b1 * water + b2 * rain[k]
        path.append(m)
    return {"path": path, "plan": plan, "notes": notes, "first": first}


def monte_carlo(F: Field, m0, rain, thr, kc_ratio, delay=0, irrigate=True, sims=1000, seed=7):
    rng = np.random.default_rng(seed)
    b0, b1, b2 = F.A["beta"]
    dry, sig = b0 * kc_ratio, F.A["sigma"]
    hit = sdays = deficit = 0.0
    for _ in range(sims):
        m, delayed, any_stress = m0, 0, False
        for k in range(len(rain)):
            water = 0.0
            if irrigate and m <= thr["refill"]:
                r_next = rain[k] + (rain[k + 1] if k + 1 < len(rain) else 0)
                need = (thr["target"] - m) / b1 - r_next * b2 / b1
                if need > 0:
                    if delayed < delay:
                        delayed += 1
                    else:
                        water = need
            m = m + dry + b1 * water + b2 * rain[k] + sig * rng.standard_normal()
            if m < thr["stress"]:
                any_stress = True; sdays += 1; deficit += min(1.0, (thr["stress"] - m) / 3)
        hit += any_stress
    return {"p": hit / sims, "stress_days": sdays / sims,
            "yield_loss": KY_SUGARCANE * (deficit / sims) / 30 * 100}


def hour_label(h: int) -> str:
    h %= 24
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def advice(F: Field, rain7: list, thr: dict, kc: float, area_acres: float, pump_kw: float, stage_name: str):
    last = F.days.iloc[-1]
    m0 = float(last.m)
    rain = list(rain7) + [0.0] * 3
    kc_ratio = kc / KC_REFERENCE
    plan = make_plan(F, m0, rain, thr, kc_ratio)
    none = make_plan(F, m0, rain, thr, kc_ratio, irrigate=False)
    base = pd.Timestamp(last.date)
    k = plan["first"]

    def night(j):
        if j == 0: return "tonight"
        if j == 1: return "tomorrow night"
        return "on the night of " + (base + pd.Timedelta(days=j)).strftime("%A %d %b")

    status = "Water stress" if m0 < thr["stress"] else "Needs water" if m0 <= thr["refill"] else "Moisture OK"
    out = {"m0": m0, "status": status, "plan": plan, "none": none, "base": base}
    if 0 <= k < 7:
        mm = plan["plan"][k]
        hrs = math.ceil(mm / F.pump_rate * 2) / 2
        nights = math.ceil(hrs / max(1, F.w_len))
        say = f"Irrigate {night(k)} from {hour_label(F.w_start)} for {hrs:.1f} hours."
        if nights > 1:
            say = f"Irrigate {night(k)} from {hour_label(F.w_start)}: {hrs:.1f} hours, split over {nights} nights."
        when = "" if k == 0 else f" by {(base + pd.Timedelta(days=k)).strftime('%d %b')}"
        why = (f"Soil moisture is {m0:.1f}%{', at or below' if k == 0 else ' and will fall to'} the refill point of "
               f"{thr['refill']:.1f}%{when}. Apply about {mm:.0f} mm to bring it back to {thr['target']:.1f}%. "
               f"Electricity is available from {hour_label(F.w_start)} to {hour_label(F.w_start + F.w_len)}, "
               f"so the pump runs inside that window.")
        out.update(say=say, why=why, mm=mm, hours=hrs, kwh=hrs * pump_kw,
                   kilolitres=mm * area_acres * ACRE_M2 / 1000,
                   fert=f"Inject fertilizer during the middle half of the {hrs:.1f}-hour run. Water alone for the "
                        f"first and last quarters so nutrients stay in the root zone.")
    else:
        rain_hold = "rain" in plan["notes"][:7]
        out.update(say="Rain is expected. Irrigation is not required this week." if rain_hold
                   else "No irrigation needed in the next 7 days.",
                   why=(f"Soil moisture is {m0:.1f}%. " + ("Forecast rain will refill the root zone, so pumping now "
                        "would waste water and power." if rain_hold else
                        f"It stays above the refill point of {thr['refill']:.1f}% for the coming week.")),
                   mm=0, hours=0, kwh=0, kilolitres=0,
                   fert="No fertigation this week. Fertilizer should go in with an irrigation run.")
    out["stage"] = stage_name
    return out


def backtest(F: Field, thr: dict) -> dict:
    """Replay the advisory rule over the recorded days using the actual rain."""
    b0, b1, b2 = F.A["beta"]
    d = F.days
    m = float(d.m.iloc[0]); total = 0.0; runs = []; low = m
    for i in range(1, len(d)):
        r = float(d.rain.iloc[i]); rn = float(d.rain.iloc[i + 1]) if i + 1 < len(d) else 0.0
        water = 0.0
        if m <= thr["refill"]:
            need = (thr["target"] - m) / b1 - (r + rn) * b2 / b1
            if need > 0:
                water = need; runs.append((d.date.iloc[i], need))
        m = m + b0 + b1 * water + b2 * r
        total += water; low = min(low, m)
    return {"mm": total, "runs": runs, "lowest": low,
            "actual_mm": float(d.irr.sum()), "actual_runs": len(F.events), "actual_lowest": float(d.m.min())}


# ----------------------------------------------------------------------------- signal analysis
def spectrum(F: Field):
    x = F.med - F.med.mean()
    N = len(x)
    X = np.fft.rfft(x)
    mag = np.abs(X)
    f_cpd = np.arange(len(X)) * 24 / N                     # cycles per day
    lim = f_cpd <= 4
    k_peak = 1 + int(np.argmax(mag[1:][lim[1:]]))
    e_time = float((x ** 2).sum())
    w = np.full(len(X), 2.0); w[0] = 1
    if N % 2 == 0: w[-1] = 1
    e_freq = float((w * mag ** 2).sum() / N)
    share = 2 * mag[k_peak] ** 2 / N / e_time
    return {"f": f_cpd, "mag": mag, "peak_f": f_cpd[k_peak], "k_peak": k_peak,
            "share": share, "e_time": e_time, "e_freq": e_freq, "lim": lim}


def ma_freq_response(w: int = 24, f_max_cpd: float = 6):
    f = np.linspace(0, f_max_cpd, 600)
    om = 2 * np.pi * f / 24
    with np.errstate(invalid="ignore", divide="ignore"):
        H = np.abs(np.sin(w * om / 2) / (w * np.sin(om / 2)))
    H[0] = 1
    return f, H


def alias_freq(Ts: float, f=1 / 24):
    return abs(f - round(f * Ts) / Ts)

