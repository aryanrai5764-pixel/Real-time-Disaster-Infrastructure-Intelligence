"""
Shared database module for the Disaster/Infrastructure Intelligence project.

Every ingestion script (earthquakes, weather, infrastructure) imports from
here so they all write to the same table with the same schema, and so the
dashboard only has to know about one place to read from.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# DB lives at the project root, one level up from storage/
DB_PATH = Path(__file__).parent.parent / "disaster_intel.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the shared database."""
    return sqlite3.connect(DB_PATH)


def init_db(conn: sqlite3.Connection) -> None:
    """Create the events table if it doesn't exist yet.

    This schema is intentionally generic (event_type distinguishes sources)
    so earthquakes, weather alerts, and infrastructure anomalies can all
    live in the same table and be queried/filtered together.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            location TEXT,
            severity REAL,
            lat REAL,
            lon REAL,
            depth_km REAL,
            timestamp TEXT,
            source_url TEXT,
            fetched_at TEXT
        )
    """)
    conn.commit()


def store_events(conn: sqlite3.Connection, events: list[dict]) -> int:
    """Insert new events, skipping duplicates by event_id.

    Each event dict must have keys matching the events table columns
    (event_id, event_type, location, severity, lat, lon, depth_km,
    timestamp, source_url). depth_km can be None for non-earthquake events.
    Returns the count of newly inserted rows.
    """
    new_count = 0
    fetched_at = datetime.now(timezone.utc).isoformat()

    for e in events:
        try:
            conn.execute(
                """
                INSERT INTO events
                    (event_id, event_type, location, severity, lat, lon, depth_km, timestamp, source_url, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    e["event_id"], e["event_type"], e["location"], e["severity"],
                    e["lat"], e["lon"], e.get("depth_km"), e["timestamp"],
                    e.get("source_url"), fetched_at,
                ),
            )
            new_count += 1
        except sqlite3.IntegrityError:
            continue  # already stored

    conn.commit()
    return new_count
