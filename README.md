[README.md](https://github.com/user-attachments/files/33633393/README.md)
# CaneSense: Irrigation Advisory for Sugarcane

CaneSense reads a sugarcane plot's hourly soil sensor data and tells the farmer which night to run the pump and for how long, inside the hours when electricity is available.

It cleans the raw sensor signal, learns how the plot's soil responds to irrigation and rain, uses a live 7-day rain forecast for the plot's village, and estimates the risk of water stress if watering is delayed. The farmer's advice is in English by default, with optional Hindi, Marathi and Kannada.

Built in Python: Streamlit for the web app, pandas and numpy for the signal processing and the model, Plotly for the charts. The rain forecast comes from [Open-Meteo](https://open-meteo.com).

## Files
| File | What it does |
|---|---|
| `app.py` | The web app: sidebar and 4 tabs (Advisor, Field monitor, Signal analysis, How it works) |
| `core.py` | All the logic: CSV loading, signal cleaning, the water-balance model, the 7-day plan, Monte Carlo risk, the spectrum and the rain forecast |
| `lang.py` | The farmer-facing text in English, Hindi, Marathi and Kannada |
| `sugarcane_soil_sensor_data.csv` | Sample field data (1–30 Sep 2026, hourly, 720 rows) |
| `requirements.txt` | Python packages |

## Run on your laptop
```bash
pip install -r requirements.txt
streamlit run app.py
```
The app opens at http://localhost:8501. The live rain forecast needs internet; without it, the rain can be typed in by hand.

## Use your own data
Upload an hourly CSV from the sidebar. Required columns: `timestamp` and `soil_moisture_pct` (or `sensor_voltage_v`). Optional: `rainfall_mm`, `irrigation_mm`, `pump_on`, `power_available`, `soil_temp_c`, `air_temp_c`, `humidity_pct`. At least 3 days (72 rows) are needed.

## Put it online for free (Streamlit Community Cloud)
1. Upload `app.py`, `core.py`, `lang.py`, `requirements.txt` and `sugarcane_soil_sensor_data.csv` to a GitHub repository.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, choose the repository, branch `main` and main file `app.py`.
4. Pick a URL and click **Deploy**.
