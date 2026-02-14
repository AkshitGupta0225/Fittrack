# sections/AI_Coach.py

import streamlit as st
import pandas as pd
from db import get_conn


def show_ai_coach(uid):
    st.title("🤖 AI Fitness Coach")

    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT duration, calories FROM workouts WHERE user_id=? ORDER BY date DESC LIMIT 10",
        conn,
        params=(uid,)
    )

    if df.empty:
        st.info("No workout data yet.")
        return

    avg_duration = df["duration"].mean()
    avg_calories = df["calories"].mean()

    st.subheader("📊 Recent Performance")
    st.write(f"Average Duration: {round(avg_duration,1)} mins")
    st.write(f"Average Calories Burned: {round(avg_calories,1)} kcal")

    st.subheader("🧠 AI Suggestions")

    if avg_duration < 20:
        st.warning("Increase workout duration to at least 30 mins for better endurance.")

    if avg_calories < 200:
        st.warning("Try high-intensity workouts to boost calorie burn.")

    if avg_duration > 45:
        st.success("Great stamina! Consider strength training for muscle growth.")

    st.info("Consistency beats intensity. Stay regular! 💪")
