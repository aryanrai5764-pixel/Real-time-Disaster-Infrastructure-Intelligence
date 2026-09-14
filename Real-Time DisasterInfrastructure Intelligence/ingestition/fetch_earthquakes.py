"""
Ingestion module: USGS Earthquake data.

Run directly from the project root:
    python ingestion/fetch_earthquakes.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import requests

# Allow importing sibling packages (storage, config) when run directly
sys.path.append(str(Path(__file__).parent.parent))

from storage.db import get_connection, init_db, store_events
from config import USGS_URL, EARTHQUAKE_MIN_MAGNITUDE, EARTHQUAKE_HOURS_BACK


def fetch_earthquakes(min_magnitude: float = EARTHQUAKE_MIN_MAGNITUDE,
                       hours_back: int = EARTHQUAKE_HOURS_BACK) -> list[dict]:
    """Fetch recent earthquakes from USGS above a magnitude threshold,
    normalized into the shared event schema."""
    start_dt = datetime.now(timezone.utc).timestamp() - hours_back * 3600
    start_iso = datetime.fromtimestamp(start_dt, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    params = {
        "format": "geojson",
        "starttime": start_iso,
        "minmagnitude": min_magnitude,
        "orderby": "time",
    }

    response = requests.get(USGS_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    events = []
    for feature in data.get("features", []):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]  # [lon, lat, depth]

        events.append({
            "event_id": feature["id"],
            "event_type": "earthquake",
            "location": props.get("place", "Unknown"),
            "severity": props.get("mag"),
            "lat": coords[1],
            "lon": coords[0],
            "depth_km": coords[2],
            "timestamp": datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc).isoformat(),
            "source_url": props.get("url"),
        })

    return events


def main():
    print("Fetching recent earthquakes from USGS...")
    events = fetch_earthquakes()
    print(f"  Retrieved {len(events)} events.")

    conn = get_connection()
    init_db(conn)
    new_count = store_events(conn, events)
    print(f"  Stored {new_count} new events (duplicates skipped).")

    print("\nMost recent events in DB:")
    for row in conn.execute(
        "SELECT location, severity, timestamp FROM events "
        "WHERE event_type='earthquake' ORDER BY timestamp DESC LIMIT 5"
    ):
        print(f"  M{row[1]:.1f} - {row[0]} ({row[2]})")

    conn.close()


if __name__ == "__main__":
    main()
