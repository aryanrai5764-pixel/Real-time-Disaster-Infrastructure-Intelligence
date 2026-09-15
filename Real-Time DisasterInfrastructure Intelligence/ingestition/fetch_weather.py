"""
Ingestion module: severe weather alerts from the National Weather Service (NWS).

Data source: NWS API (free, no API key or signup required)
Docs: https://www.weather.gov/documentation/services-web-api

Note: NWS only covers the United States (including territories). This is
the trade-off for a zero-cost, zero-signup weather source. If you later
want global coverage, OpenWeatherMap's alerts endpoint is the paid/key-based
alternative (see config.py).

Run directly from the project root:
    python ingestion/fetch_weather.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import requests

sys.path.append(str(Path(__file__).parent.parent))

from storage.db import get_connection, init_db, store_events

NWS_ALERTS_URL = "https://api.weather.gov/alerts/active"

# NWS severity levels, mapped to a numeric scale so weather events sit on
# the same 0-10ish severity axis as earthquake magnitudes for filtering/color.
SEVERITY_MAP = {
    "Extreme": 5.0,
    "Severe": 4.0,
    "Moderate": 3.0,
    "Minor": 2.0,
    "Unknown": 1.0,
}


def fetch_weather_alerts() -> list[dict]:
    """Fetch active severe weather alerts from NWS, normalized into the
    shared event schema."""
    headers = {
        # NWS requires a descriptive User-Agent identifying the app/contact
        "User-Agent": "disaster-intel-student-project (contact: none)"
    }
    response = requests.get(NWS_ALERTS_URL, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    events = []
    for feature in data.get("features", []):
        props = feature["properties"]
        geometry = feature.get("geometry")

        # Not every alert includes geometry (some are county/zone-based only).
        # Skip alerts we can't place on the map.
        if not geometry or geometry.get("type") != "Polygon":
            continue

        coords = geometry["coordinates"][0]  # outer ring of the polygon
        lon = sum(c[0] for c in coords) / len(coords)
        lat = sum(c[1] for c in coords) / len(coords)

        severity_label = props.get("severity", "Unknown")
        severity = SEVERITY_MAP.get(severity_label, 1.0)

        events.append({
            "event_id": props["id"],
            "event_type": "weather",
            "location": props.get("areaDesc", "Unknown area"),
            "severity": severity,
            "lat": lat,
            "lon": lon,
            "depth_km": None,
            "timestamp": props.get("onset") or props.get("sent"),
            "source_url": props.get("id"),
        })

    return events


def main():
    print("Fetching active weather alerts from NWS...")
    events = fetch_weather_alerts()
    print(f"  Retrieved {len(events)} mappable alerts.")

    conn = get_connection()
    init_db(conn)
    new_count = store_events(conn, events)
    print(f"  Stored {new_count} new events (duplicates skipped).")

    print("\nMost recent weather alerts in DB:")
    for row in conn.execute(
        "SELECT location, severity, timestamp FROM events "
        "WHERE event_type='weather' ORDER BY timestamp DESC LIMIT 5"
    ):
        print(f"  Severity {row[1]:.1f} - {row[0]} ({row[2]})")

    conn.close()


if __name__ == "__main__":
    main()
