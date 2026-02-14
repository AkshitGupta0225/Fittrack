import streamlit as st
import pandas as pd
from datetime import date
from db import get_conn
from utils import safe_to_datetime


def show_workouts(uid):
    conn = get_conn()

    st.title("🏋️ Workouts")

    tab1, tab2 = st.tabs(["➕ Add Workout", "📋 View Workouts"])

    # ==========================================================
    # ADD WORKOUT
    # ==========================================================
    with tab1:
        with st.form("add_workout_form"):
            title = st.text_input("Title")
            sport = st.selectbox(
                "Sport",
                ["Running", "Cycling", "Gym", "Walking", "Hiking", "Other"],
                key="workout_sport"
            )
            workout_date = st.date_input("Date", date.today())
            distance = st.number_input("Distance (km)", min_value=0.0)
            duration = st.number_input("Duration (min)", min_value=0.0)
            ascent = st.number_input("Ascent (m)", min_value=0.0)
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Save Workout")

            if submitted:
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
                        workout_date.isoformat(),
                        distance,
                        duration,
                        ascent,
                        notes
                    )
                )
                conn.commit()
                st.success("Workout saved successfully! 💪")

    # ==========================================================
    # VIEW WORKOUTS
    # ==========================================================
    with tab2:

        df = pd.read_sql_query(
            "SELECT * FROM workouts WHERE user_id=? ORDER BY date DESC",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No workouts logged yet.")
        else:
            df["date"] = safe_to_datetime(df["date"])

            for _, row in df.iterrows():
                with st.expander(
                    f"{row['title']} — {row['sport']} ({row['date'].date()})"
                ):
                    col1, col2 = st.columns(2)

                    col1.write(f"Distance: {row['distance_km'] or '-'} km")
                    col1.write(f"Duration: {row['duration_min'] or '-'} min")
                    col1.write(f"Ascent: {row['ascent_m'] or '-'} m")
                    col1.write(f"Notes: {row['notes'] or '-'}")

                    # Auto pace calculation
                    if row["distance_km"] and row["duration_min"]:
                        pace = row["duration_min"] / row["distance_km"]
                        col2.metric("Avg Pace (min/km)", f"{pace:.2f}")

    conn.close()
