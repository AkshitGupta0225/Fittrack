import streamlit as st
import gpxpy
import folium
from streamlit_folium import st_folium
from db import get_conn
from utils import haversine_km
from datetime import datetime


def show_gpx(uid):
    conn = get_conn()

    st.title("🗺 GPX Upload & Route Visualization")

    uploaded_file = st.file_uploader("Upload GPX File", type=["gpx"])

    if not uploaded_file:
        st.info("Upload a GPX file to visualize your route.")
        return

    try:
        gpx = gpxpy.parse(uploaded_file)

        points = []
        total_distance = 0

        for track in gpx.tracks:
            for segment in track.segments:
                prev_point = None
                for point in segment.points:
                    latlon = (point.latitude, point.longitude)
                    points.append(latlon)

                    if prev_point:
                        total_distance += haversine_km(prev_point, latlon)

                    prev_point = latlon

        if not points:
            st.error("No valid GPS points found in file.")
            return

        # ---------------------------------------------------------
        # MAP VISUALIZATION
        # ---------------------------------------------------------
        st.subheader("Route Map")

        m = folium.Map(location=points[0], zoom_start=13)
        folium.PolyLine(points, color="blue", weight=4).add_to(m)

        folium.Marker(points[0], tooltip="Start",
                      icon=folium.Icon(color="green")).add_to(m)

        folium.Marker(points[-1], tooltip="End",
                      icon=folium.Icon(color="red")).add_to(m)

        st_folium(m, width=800, height=450)

        st.markdown("---")

        # ---------------------------------------------------------
        # WORKOUT SAVE OPTION
        # ---------------------------------------------------------
        st.subheader("Save As Workout")

        title = st.text_input("Workout Title", value="GPX Activity")
        sport = st.selectbox(
            "Sport Type",
            ["Running", "Cycling", "Hiking", "Walking", "Trail"]
        )

        duration_min = st.number_input(
            "Duration (minutes)",
            min_value=1.0,
            value=30.0
        )

        st.metric("Calculated Distance (km)", f"{total_distance:.2f}")

        if st.button("Save Workout"):
            conn.execute(
                """
                INSERT INTO workouts
                (user_id, title, sport, date, distance_km, duration_min, ascent_m, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    title,
                    sport,
                    datetime.now().isoformat(),
                    round(total_distance, 2),
                    duration_min,
                    None,
                    "Imported from GPX"
                )
            )
            conn.commit()
            st.success("Workout saved successfully.")

    except Exception as e:
        st.error(f"Error processing GPX file: {e}")

    conn.close()
