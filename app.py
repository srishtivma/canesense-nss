"""
CaneSense: irrigation advisory for sugarcane

Run locally:   pip install -r requirements.txt
               streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import core
from lang import LANGUAGES, T, hour, day

st.set_page_config(page_title="CaneSense · Sugarcane Irrigation Advisor", page_icon="🌱", layout="wide")

WATER, CANE, SOIL, GREY, WARN, BAD, GOOD = "#1d6aa3", "#3b7a2a", "#8a5a2b", "#8a958c", "#d98e04", "#c0392b", "#2b7a47"
SAMPLE = Path(__file__).parent / "sugarcane_soil_sensor_data.csv"


def fig_base(fig, y=None, x=None, h=340):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
                      legend=dict(orientation="h", y=1.12, x=0))
    if y: fig.update_yaxes(title_text=y)
    if x: fig.update_xaxes(title_text=x)
    return fig


# ============================================================ sidebar: data + settings
with st.sidebar:
    st.title("CaneSense")
    st.caption("Irrigation advisory for sugarcane")
    lg = LANGUAGES[st.selectbox("Language for the advice (optional)", list(LANGUAGES), index=0)]
    t = T[lg]

    st.subheader("1. Field data")
    up = st.file_uploader("Upload sensor CSV (hourly)", type="csv",
                          help="Columns: timestamp, soil_moisture_pct, sensor_voltage_v, soil_temp_c, air_temp_c, "
                               "humidity_pct, rainfall_mm, irrigation_mm, pump_on, power_available")


@st.cache_data(ttl=3600)
def _cached_forecast(lat, lon):
    rain = core.rain_forecast(lat, lon)
    if rain is None:
        raise ConnectionError("offline")      # errors are not cached, so it retries next time
    return rain


def get_forecast(lat, lon):
    try:
        return _cached_forecast(lat, lon)
    except ConnectionError:
        return None


@st.cache_data
def load(data: bytes | None):
    import io
    return core.load_csv(io.BytesIO(data) if data else SAMPLE)


try:
    df = load(up.getvalue() if up else None)
except Exception as e:
    st.error(f"Could not read this file. {e}")
    st.stop()

F = core.process(df)

with st.sidebar:
    st.caption(f"{'Uploaded: ' + up.name if up else 'Sample plot'} · {len(df)} readings · "
               f"{df.timestamp.min():%d %b} – {df.timestamp.max():%d %b %Y}")

    st.subheader("2. Crop and farm")
    stage = st.selectbox("Crop stage", list(core.CROP_STAGES), index=2)
    kc = core.CROP_STAGES[stage]
    area = st.number_input("Plot area (acres)", value=1.0, step=0.1, min_value=0.1)

    st.subheader("3. Plot location")
    place = st.selectbox("Village", list(core.VILLAGES) + ["Other (enter location)"])
    if place in core.VILLAGES:
        lat, lon = core.VILLAGES[place]
    else:
        lc1, lc2 = st.columns(2)
        lat = lc1.number_input("Latitude", value=core.KIAAR_LAT, format="%.4f", step=0.01)
        lon = lc2.number_input("Longitude", value=core.KIAAR_LON, format="%.4f", step=0.01)
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=9, height=180)

    with st.expander("Advanced settings"):
        target = st.number_input("Target moisture, % (fill to)", value=F.thr["target"], step=0.1)
        refill = st.number_input("Refill point, % (start irrigating)", value=F.thr["refill"], step=0.1)
        stress = st.number_input("Stress point, %", value=F.thr["stress"], step=0.1)
        st.caption("Defaults come from this plot's own history (75th / 25th percentile of daily moisture).")
        kw = st.number_input("Pump power (kW)", value=3.7, step=0.1, min_value=0.0)

thr = {"target": target, "refill": refill, "stress": stress}

st.title("CaneSense: Sugarcane Irrigation Advisor")
st.caption("Soil sensor data in, irrigation schedule out")

tab_adv, tab_field, tab_sig, tab_how = st.tabs(
    ["Advisor", "Field monitor", "Signal analysis", "How it works"])

# ============================================================ ADVISOR
with tab_adv:
    base_date = pd.Timestamp(F.days.date.iloc[-1])
    fc = get_forecast(round(lat, 4), round(lon, 4))
    with st.expander(t["rain_exp"]):
        st.caption(t["rain_live"] if fc else t["rain_off"])
        cols = st.columns(7)
        rain7 = []
        for j, c in enumerate(cols):
            d = base_date + pd.Timedelta(days=j + 1)
            rain7.append(c.number_input((t["tonight"] if j == 0 else "") + day(d, lg),
                                        min_value=0.0, value=float(fc[j]) if fc else 0.0, step=1.0,
                                        key=f"rain{j}_{lat:.4f}_{lon:.4f}_{bool(fc)}"))

    A = core.advice(F, rain7, thr, kc, area, kw, stage)

    # ---- the advice in plain words
    k = A["plan"]["first"]
    m0 = f"{A['m0']:.1f}"
    head = {"Moisture OK": t["head_ok"], "Needs water": t["head_need"], "Water stress": t["head_stress"]}[A["status"]]
    if A["mm"] > 0:
        when = t["when0"] if k == 0 else t["when1"] if k == 1 else t["whenN"].format(date=day(base_date + pd.Timedelta(days=k), lg))
        nights = int(np.ceil(A["hours"] / max(1, F.w_len)))
        act = (t["act_split"] if nights > 1 else t["act"]).format(when=when, start=hour(F.w_start, lg),
                                                                   hours=f"{A['hours']:.1f}", n=nights)
        why = t["why_water"].format(m=m0, mm=f"{A['mm']:.0f}",
                                    window=t["window"].format(a=hour(F.w_start, lg), b=hour(F.w_start + F.w_len, lg)))
    else:
        act = t["act_rain"] if "rain" in A["plan"]["notes"][:7] else t["act_none"]
        why = t["why_none"].format(m=m0)
    status = A["status"] if A["mm"] > 0 or A["status"] == "Water stress" else "Moisture OK"
    box = {"Moisture OK": st.success, "Needs water": st.warning, "Water stress": st.error}[status]
    icon = {"Moisture OK": "🟢", "Needs water": "🟠", "Water stress": "🔴"}[status]
    if A["mm"] > 0:
        box(f"### {icon} {head}\n#### {act}\n{why}")
    else:
        box(f"### {icon} {act}\n{why}")

    k1, k2, k3 = st.columns(3)
    k1.metric(t["m_moist"], f"{A['m0']:.1f} %")
    k2.metric(t["m_water"], f"{A['mm']:.0f} mm")
    k3.metric(t["m_pump"], f"{A['hours']:.1f} {t['hours']}")

    left, right = st.columns([2, 1])
    with left:
        st.markdown(f"##### {t['chart']}")
        hist = F.days.tail(10)
        fut = [base_date + pd.Timedelta(days=j) for j in range(8)]
        lo = min(stress - 1.5, min(A["none"]["path"][:8]) - 0.3)
        hi = max(target, max(hist.m), max(A["plan"]["path"][:8])) + 0.5
        fig = go.Figure()
        fig.add_hrect(y0=refill, y1=hi, fillcolor=GOOD, opacity=0.08, line_width=0,
                      annotation_text=t["z_good"], annotation_position="top left")
        fig.add_hrect(y0=stress, y1=refill, fillcolor=WARN, opacity=0.15, line_width=0,
                      annotation_text=t["z_soon"], annotation_position="top left")
        fig.add_hrect(y0=lo, y1=stress, fillcolor=BAD, opacity=0.12, line_width=0,
                      annotation_text=t["z_danger"], annotation_position="top left")
        fig.add_scatter(x=pd.to_datetime(hist.date), y=hist.m, name=t["l_past"], line=dict(color="black"))
        fig.add_scatter(x=fut, y=A["plan"]["path"][:8], name=t["l_plan"], line=dict(color=WATER, width=3))
        fig.add_scatter(x=fut, y=A["none"]["path"][:8], name=t["l_none"], line=dict(color=GREY, dash="dash"))
        fig.update_yaxes(range=[lo, hi])
        st.plotly_chart(fig_base(fig, t["y"]), width="stretch")

    with right:
        st.markdown(f"##### {t['risk_title']}")
        rain10 = rain7 + [0, 0, 0]
        kr = kc / core.KC_REFERENCE
        mp = core.monte_carlo(F, A["m0"], rain10, thr, kr)
        mn = core.monte_carlo(F, A["m0"], rain10, thr, kr, irrigate=False)
        st.markdown(("✅ " + t["risk_safe"]) if mp["p"] <= 0.1 else ("⚠️ " + t["risk_some"].format(p=f"{mp['p']:.0%}".rstrip("%"))))
        if A["mm"] > 0:
            st.markdown("❌ " + t["risk_none"].format(p=f"{mn['p']:.0%}".rstrip("%")))
            delay = st.slider(t["slider"], 0, 6, 0, key="delay")
            if delay:
                md = core.monte_carlo(F, A["m0"], rain10, thr, kr, delay=delay)
                st.markdown(t["risk_delay"].format(d=delay, p=f"{md['p']:.0%}".rstrip("%"), y=f"{md['yield_loss']:.1f}"))
            else:
                st.caption(t["risk_delay0"])

    st.markdown(f"##### {t['dec']}")
    if "log" not in st.session_state:
        st.session_state.log = []
    b1, b2, _ = st.columns([1, 1, 3])
    if b1.button(t["yes"], width="stretch", key="yes"):
        st.session_state.log.insert(0, f"{pd.Timestamp.now():%d %b %H:%M} · {t['said_yes']} · {act}")
    if b2.button(t["no"], width="stretch", key="no"):
        st.session_state.log.insert(0, f"{pd.Timestamp.now():%d %b %H:%M} · {t['said_no']} · {act}")
    for line in st.session_state.log[:10]:
        st.write("•", line)
    st.info(f"**{t['fert']}** {t['fert_yes'] if A['mm'] > 0 else t['fert_no']}")

# ============================================================ FIELD MONITOR
with tab_field:
    last_ev = F.events[-1] if F.events else None
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Soil moisture", f"{F.days.m.iloc[-1]:.1f} %")
    m2.metric("Last irrigation", df.timestamp[last_ev["start"]].strftime("%d %b %H:%M") if last_ev else "none",
              help=f"{last_ev['hours']} h · {last_ev['mm']:.1f} mm" if last_ev else None)
    m3.metric("Rain, last 7 days", f"{F.days.rain.tail(7).sum():.1f} mm")
    m4.metric("Water applied", f"{F.days.irr.sum():.0f} mm", help=f"{len(F.events)} pump runs")
    m5.metric("Power window", f"{core.hour_label(F.w_start)}–{core.hour_label(F.w_start + F.w_len)}",
              help=f"{F.w_len} h of electricity per day")

    watered = (f"Last watered on {df.timestamp[last_ev['start']]:%d %b} for {last_ev['hours']} hours "
               f"({last_ev['mm']:.0f} mm)." if last_ev else "No watering in this period.")
    st.info(f"{watered} Rain in the last 7 days: {F.days.rain.tail(7).sum():.0f} mm. "
            f"Electricity comes {core.hour_label(F.w_start)} – {core.hour_label(F.w_start + F.w_len)}.")
    st.markdown("##### Soil moisture, rain and irrigation")
    fig = go.Figure()
    fig.add_scatter(x=df.timestamp, y=F.raw, name="Raw sensor", line=dict(color="#c9d3c8", width=1))
    fig.add_scatter(x=df.timestamp, y=F.trend, name="Cleaned trend", line=dict(color=CANE, width=3))
    days_ts = pd.to_datetime(F.days.date) + pd.Timedelta(hours=12)
    fig.add_bar(x=days_ts, y=F.days.rain.where(F.days.rain > 0), name="Rain (mm/day)", marker_color=SOIL, yaxis="y2")
    fig.add_bar(x=days_ts, y=F.days.irr.where(F.days.irr > 0), name="Irrigation (mm/day)", marker_color=WATER, yaxis="y2")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", title="mm per day", showgrid=False, rangemode="tozero"))
    st.plotly_chart(fig_base(fig, "Soil moisture (%)", h=380), width="stretch")

    st.markdown("##### Pump use vs electricity supply")
    pump_by_hour = df.groupby("hour").pump_on.sum().reindex(range(24), fill_value=0)
    fig = go.Figure()
    fig.add_bar(x=list(range(24)), y=pump_by_hour, name="Pump-hours in record", marker_color=WATER)
    fig.add_scatter(x=list(range(24)), y=F.power_on.astype(int), name="Power available", yaxis="y2",
                    line=dict(color=WARN, shape="hvh"), fill="tozeroy")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 1.1], showgrid=False, title="Power on"))
    st.plotly_chart(fig_base(fig, "Pump hours", "Hour of day"), width="stretch")


# ============================================================ SIGNAL ANALYSIS
with tab_sig:
    st.markdown("The raw sensor signal **x[n]** (one reading per hour) has three problems: missing samples, "
                "electrical spikes and a daily ripple. This tab shows how each one is cleaned before the "
                "signal is used for the advice. Every number here is computed from the loaded CSV.")
    st.markdown("**Pipeline:** voltage → moisture calibration → gap fill (interpolation) → 5-point median filter "
                "→ 24-h moving average (convolution) → daily trend → advisory model")

    st.subheader("1 · Raw vs cleaned signal")
    show = st.multiselect("Signals", ["Raw x[n]", "Median filtered", "24-h trend"],
                          default=["Raw x[n]", "Median filtered", "24-h trend"])
    fig = go.Figure()
    if "Raw x[n]" in show: fig.add_scatter(x=df.timestamp, y=F.raw, name="Raw x[n]", line=dict(color=GREY, width=1))
    if "Median filtered" in show: fig.add_scatter(x=df.timestamp, y=F.med, name="Median filtered", line=dict(color=WATER, width=1.3))
    if "24-h trend" in show: fig.add_scatter(x=df.timestamp, y=F.trend, name="24-h trend", line=dict(color=CANE, width=3))
    st.plotly_chart(fig_base(fig, "Soil moisture (%)", h=360), width="stretch")
    st.caption(f"{len(F.gaps)} missing samples filled · {len(F.spikes)} spikes removed · ripple around trend "
               f"σ = {np.std(F.med - F.trend, ddof=1):.2f}%")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("2 · Removing spikes: median filter")
        si = max(F.spikes, key=lambda i: abs(F.filled[i] - F.med[i])) if F.spikes else len(df) // 2
        a, b = max(0, si - 12), min(len(df), si + 13)
        fig = go.Figure()
        fig.add_scatter(x=df.timestamp[a:b], y=F.filled[a:b], name="Input with spike", mode="lines+markers", line=dict(color=GREY))
        fig.add_scatter(x=df.timestamp[a:b], y=core.moving_average(F.filled, 5)[a:b], name="5-point moving average", line=dict(color=SOIL, width=2.5))
        fig.add_scatter(x=df.timestamp[a:b], y=F.med[a:b], name="5-point median", line=dict(color=WATER, width=2.5))
        st.plotly_chart(fig_base(fig, "%", h=300), width="stretch")
        st.markdown("A spike is a single wrong sample. The **median** of 5 neighbours ignores it completely, "
                    "while a **moving average** spreads it over 5 hours. So spikes are removed with the median "
                    "filter first.")
    with c2:
        st.subheader("3 · 24-h moving average as convolution")
        st.latex(r"y[n]=\sum_{k=0}^{23}h[k]\,x[n-k],\quad h[k]=\tfrac{1}{24}")
        f, H = core.ma_freq_response()
        fig = go.Figure(go.Scatter(x=f, y=H, name="|H(f)|", line=dict(color=CANE, width=2.5)))
        st.plotly_chart(fig_base(fig, "|H(f)|", "Frequency (cycles per day)", h=260), width="stretch")
        st.latex(r"|H(f)|=\left|\frac{\sin(24\pi f)}{24\sin(\pi f)}\right|")
        st.caption("Zeros at exactly 1, 2, 3… cycles/day, so the daily ripple and its harmonics are removed "
                   "while the slow drying trend (≈ 0 cycles/day) passes.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("4 · Frequency analysis (spectrum)")
        S = core.spectrum(F)
        colors = [BAD if i == S["k_peak"] else WATER for i in range(S["lim"].sum())]
        fig = go.Figure(go.Bar(x=S["f"][S["lim"]], y=S["mag"][S["lim"]], marker_color=colors, name="|X(f)|"))
        st.plotly_chart(fig_base(fig, "|X(f)|", "Frequency (cycles per day)", h=300), width="stretch")
        st.markdown(f"- Strongest periodic component: **{S['peak_f']:.2f} cycle/day** (period {24 / S['peak_f']:.1f} h)\n"
                    f"- Share of signal energy in that component: **{S['share']:.0%}**\n\n"
                    "This daily peak is the ripple, so the filter in section 3 is designed to remove exactly 1 cycle/day.")
    with c2:
        st.subheader("5 · Sampling strategy")
        Ts = st.slider("Sampling interval Tₛ (hours)", 1, 30, 1)
        end = min(len(df), 240)
        idx = np.arange(0, end, Ts)
        fig = go.Figure()
        fig.add_scatter(x=df.timestamp[:end], y=F.med[:end], name="Hourly signal", line=dict(color="#c9d3c8"))
        fig.add_scatter(x=df.timestamp[idx], y=F.med[idx], name=f"Samples every {Ts} h", mode="lines+markers",
                        line=dict(color=WATER))
        st.plotly_chart(fig_base(fig, "%", h=280), width="stretch")
        nyq, fr = 1 / (2 * Ts), 1 / 24
        if Ts < 12:
            st.success(f"Nyquist = 1/(2Tₛ) = {nyq:.3f} cycles/h > ripple {fr:.3f} cycles/h. The ripple is captured and can be filtered.")
        elif Ts == 12:
            st.warning("Nyquist equals the ripple frequency. This is the edge case: samples can miss the ripple entirely.")
        else:
            fa = core.alias_freq(Ts)
            st.error(f"Nyquist = {nyq:.3f} cycles/h < ripple {fr:.3f} cycles/h. The ripple aliases to "
                     + ("0 (a constant offset)" if fa < 1e-9 else f"{fa:.4f} cycles/h, a false wave every {1 / fa / 24:.1f} days")
                     + ", which could be mistaken for real drying.")
        st.caption("Chosen strategy: sample every 1 hour. That is well above the Nyquist limit for the daily ripple.")

    if F.cal:
        st.subheader("6 · Sensor calibration: voltage → moisture")
        c1, c2 = st.columns([2, 1])
        with c1:
            vv = np.linspace(F.cal["v"].min(), F.cal["v"].max(), 2)
            fig = go.Figure()
            fig.add_scatter(x=F.cal["v"], y=F.cal["m"], mode="markers", marker=dict(color=WATER, size=4), name="Readings")
            fig.add_scatter(x=vv, y=F.cal["a"] + F.cal["b"] * vv, name="Fitted line", line=dict(color=BAD, width=2))
            st.plotly_chart(fig_base(fig, "Soil moisture (%)", "Sensor voltage (V)", h=300), width="stretch")
        with c2:
            st.latex(rf"m = {F.cal['a']:.2f} {'-' if F.cal['b'] < 0 else '+'} {abs(F.cal['b']):.2f}\,V")
            st.metric("Correlation r", f"{F.cal['r']:.4f}")
            st.caption("Wetter soil → higher capacitance → lower voltage, so the slope is negative. "
                       "When a moisture reading is missing but the voltage is present, this line fills it in.")

    st.markdown("##### Data quality summary")
    q = pd.DataFrame({"Check": ["Readings", "Missing moisture samples", "Spikes over ±2% removed",
                                "Voltage calibration (r)", "Model fit (R²)"],
                      "Result": [f"{len(df)} ({len(F.days)} days, hourly)", f"{len(F.gaps)} (filled by interpolation)",
                                 f"{len(F.spikes)}", f"{F.cal['r']:.3f}" if F.cal else "no voltage column",
                                 f"{F.A['r2']:.2f}"]})
    st.dataframe(q, hide_index=True, width="stretch")


# ============================================================ HOW IT WORKS
with tab_how:
    st.subheader("Problem")
    st.write("About 18,000–25,000 sugarcane farmers in Northern Karnataka (KIAAR and GBL) decide when to irrigate from "
             "experience. Over-irrigation wastes water, power and fertilizer. Late irrigation stresses the crop and "
             "cuts yield. CaneSense turns one plot's sensor readings into a clear instruction.")
    st.subheader("Water-balance model (used for the advice)")
    b0, b1, b2 = F.A["beta"]
    st.latex(r"\Delta m_d=\beta_0+\beta_1 I_d+\beta_2 R_d")
    st.dataframe(pd.DataFrame({"Coefficient": ["β₀ (drying, %/day)", "β₁ (% per mm irrigation)", "β₂ (% per mm rain)", "R²", "σ (%)", "days"],
                               "Value": [f"{b0:.3f}", f"{b1:.4f}", f"{b2:.4f}", f"{F.A['r2']:.2f}", f"{F.A['sigma']:.3f}", str(F.A["n"])]}),
                 hide_index=True)
    st.subheader("Back-test on the recorded period")
    bt = core.backtest(F, thr)
    st.dataframe(pd.DataFrame({"": ["Irrigation runs", "Water applied (mm)", "Lowest daily moisture (%)"],
                               "Farmer (actual)": [str(bt["actual_runs"]), f"{bt['actual_mm']:.1f}", f"{bt['actual_lowest']:.2f}"],
                               "CaneSense rule": [str(len(bt["runs"])), f"{bt['mm']:.1f}", f"{bt['lowest']:.2f}"]}),
                 hide_index=True)
    st.subheader("Responsible AI")
    st.markdown("- **Explainable:** every advice shows the numbers behind it.\n"
                "- **Human in the loop:** accept / override buttons with a decision log.\n"
                "- **Privacy:** the CSV is processed in this app session only.\n"
                "- **Limits:** trained on one plot for 30 days; needs validation across soils and seasons by KIAAR agronomists.")
