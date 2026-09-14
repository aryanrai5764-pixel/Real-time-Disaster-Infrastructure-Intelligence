"""
Shared configuration for the Disaster/Infrastructure Intelligence project.

Keep API keys and thresholds here instead of scattered across scripts.
Never commit real API keys to a public repo — use environment variables
for anything shared publicly (see the commented-out os.environ lines below).
"""

import os

# --- USGS Earthquake settings (no API key required) ---
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
EARTHQUAKE_MIN_MAGNITUDE = 2.5
EARTHQUAKE_HOURS_BACK = 24

# --- Weather API settings (fill in once you add fetch_weather.py) ---
# Get a free key at https://openweathermap.org/api
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# --- Risk scoring thresholds (used later in processing/risk_scoring.py) ---
HIGH_SEVERITY_THRESHOLD = 5.0
MEDIUM_SEVERITY_THRESHOLD = 3.5
