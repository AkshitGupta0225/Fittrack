# sections/Workout_Map.py

import streamlit as st
import folium
from streamlit_folium import st_folium
from db import get_conn
from datetime import datetime
import math


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def show_workout_map(uid):
    st.title("🗺️ Workout Map Planner")

    conn = get_conn()
    c = conn.cursor()

    # ==========================================================
    # Interactive Map
    # ==========================================================
    if "selected_points" not in st.session_state:
        st.session_state["selected_points"] = []

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    map_data = st_folium(m, width=900, height=500)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        if not st.session_state["selected_points"] or \
           st.session_state["selected_points"][-1] != (lat, lon):
            st.session_state["selected_points"].append((lat, lon))

    # Show selected points
    if len(st.session_state["selected_points"]) >= 1:
        st.write("📍 Selected Points:")
        for i, p in enumerate(st.session_state["selected_points"]):
            st.write(f"Point {i+1}: {p}")

    # ==========================================================
    # Distance Calculation
    # ==========================================================
    if len(st.session_state["selected_points"]) >= 2:
        p1 = st.session_state["selected_points"][-2]
        p2 = st.session_state["selected_points"][-1]

        distance_km = haversine(p1[0], p1[1], p2[0], p2[1])

        st.success(f"Distance Between Last Two Points: {round(distance_km,2)} km")

        duration = st.number_input("Duration (minutes)", min_value=1)

        if st.button("💾 Save This Workout"):
            # Insert workout
            c.execute("""
                INSERT INTO workouts 
                (user_id, title, sport, date, distance_km, duration_min, ascent_m, calories, notes, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uid,
                "Map Planned Workout",
                "Running",
                datetime.utcnow().isoformat(),
                round(distance_km, 2),
                duration,
                None,
                None,
                "Created via Map Planner",
                ""
            ))

            workout_id = c.lastrowid

            # Store both points in workout_points table
            for point in [p1, p2]:
                c.execute("""
                    INSERT INTO workout_points (user_id, workout_id, latitude, longitude)
                    VALUES (?, ?, ?, ?)
                """, (uid, workout_id, point[0], point[1]))

            conn.commit()
            st.success("Workout saved successfully!")

    if st.button("🔄 Reset Points"):
        st.session_state["selected_points"] = []

    conn.close()
