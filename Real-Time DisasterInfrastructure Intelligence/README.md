# Real-Time Disaster/Infrastructure Intelligence

A combined dashboard tracking natural disasters (earthquakes, weather) and
simulated infrastructure health, built with public APIs and a local SQLite
database.

## Project structure

```
disaster-intel/
├── ingestion/
│   ├── fetch_earthquakes.py      # USGS API (live)
│   ├── fetch_weather.py          # weather/storm alerts (TODO)
│   └── fetch_infrastructure.py   # simulated sensor data (TODO)
├── storage/
│   └── db.py                     # shared SQLite schema + helpers
├── processing/
│   └── risk_scoring.py           # combines nearby events into a risk score (TODO)
├── dashboard/
│   └── app.py                    # Streamlit map dashboard
├── config.py                     # shared constants, API keys
├── requirements.txt
└── disaster_intel.db             # created automatically on first run
```

## Data sources

- **Earthquakes**: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/) — real, no API key needed
- **Weather**: OpenWeatherMap (planned) — real, requires free API key
- **Infrastructure**: simulated data (no public dataset available for this project)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. Fetch data:
   ```bash
   python ingestion/fetch_earthquakes.py
   ```
2. View the dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```

## Status

- [x] Earthquake ingestion (USGS)
- [x] SQLite storage
- [x] Map dashboard
- [ ] Weather ingestion
- [ ] Simulated infrastructure layer
- [ ] Risk scoring
- [ ] Deployment
