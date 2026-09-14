"""
Dashboard: map view.

Reads events from the shared database and plots them, colored/sized by
severity. Works for any event_type stored in the events table.

Run from the project root:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

sys.path.append(str(Path(__file__).parent.parent))
from storage.db import get_connection


def load_events() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM events ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def severity_color(sev: float) -> str:
    if sev is None:
        return "gray"
    if sev < 3:
        return "green"
    elif sev < 4.5:
        return "orange"
    else:
        return "red"


def severity_radius(sev: float) -> float:
    if sev is None:
        return 4
    return max(4, sev * 3)


def build_map(df: pd.DataFrame) -> folium.Map:
    if df.empty:
        return folium.Map(location=[20, 0], zoom_start=2)

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=2,
        tiles="CartoDB dark_matter",
    )

    for _, row in df.iterrows():
        popup_text = (
            f"<b>{row['location']}</b><br>"
            f"Type: {row['event_type']}<br>"
            f"Severity: {row['severity']}<br>"
            f"Time: {row['timestamp']}"
        )
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=severity_radius(row["severity"]),
            color=severity_color(row["severity"]),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=250),
        ).add_to(m)

    return m


def main():
    st.set_page_config(page_title="Disaster Intelligence Map", layout="wide")
    st.title("🌍 Real-Time Disaster Intelligence")
    st.caption("Live event data, stored locally and rendered on a map.")

    df = load_events()

    if df.empty:
        st.warning("No events found. Run an ingestion script first (e.g. ingestion/fetch_earthquakes.py).")
        return

    st.sidebar.header("Filters")
    event_types = sorted(df["event_type"].unique())
    selected_types = st.sidebar.multiselect("Event type", event_types, default=event_types)
    min_sev = st.sidebar.slider(
        "Minimum severity", 0.0, float(df["severity"].max()), 2.5, 0.1
    )

    filtered = df[(df["event_type"].isin(selected_types)) & (df["severity"] >= min_sev)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total events shown", len(filtered))
    col2.metric("Highest severity", f"{filtered['severity'].max():.1f}" if not filtered.empty else "—")
    col3.metric("Last updated", df["fetched_at"].max()[:19] if "fetched_at" in df else "—")

    st.subheader("Event map")
    m = build_map(filtered)
    st_folium(m, width=1200, height=600)

    st.subheader("Raw event data")
    st.dataframe(
        filtered[["event_type", "location", "severity", "timestamp"]].reset_index(drop=True)
    )


if __name__ == "__main__":
    main()
