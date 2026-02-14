import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import get_conn
from utils import mood_to_score


def show_stress(uid):
    conn = get_conn()

    st.title("💆 Stress & Recovery Index")

    # ---------------------------------------------------------
    # FETCH DATA
    # ---------------------------------------------------------
    workouts = pd.read_sql_query(
        "SELECT duration_min FROM workouts WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    journals = pd.read_sql_query(
        "SELECT mood FROM journals WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    sleep = pd.read_sql_query(
        "SELECT hours FROM sleep WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    nutrition = pd.read_sql_query(
        "SELECT calories FROM nutrition WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    # ---------------------------------------------------------
    # CALCULATE COMPONENTS
    # ---------------------------------------------------------
    avg_work = workouts["duration_min"].mean() if not workouts.empty else 0
    avg_sleep = sleep["hours"].mean() if not sleep.empty else 0
    avg_mood = journals["mood"].apply(mood_to_score).mean() if not journals.empty else 50
    avg_cal = nutrition["calories"].mean() if not nutrition.empty else 0

    # Normalize
    workout_score = min(avg_work / 60 * 25, 25)  # up to 25 points
    sleep_score = min(avg_sleep / 8 * 25, 25)    # up to 25 points
    mood_score = min(avg_mood / 100 * 25, 25)    # up to 25 points
    nutrition_score = min(avg_cal / 2000 * 25, 25)  # up to 25 points

    stress_score = workout_score + sleep_score + mood_score + nutrition_score

    # ---------------------------------------------------------
    # STATUS COLOR
    # ---------------------------------------------------------
    if stress_score >= 75:
        color = "#10b981"
        status = "🟢 Balanced & Recovered"
        advice = "Great balance! Maintain your routine."
    elif stress_score >= 50:
        color = "#f59e0b"
        status = "🟠 Slightly Stressed"
        advice = "Consider lighter workouts and more sleep."
    else:
        color = "#ef4444"
        status = "🔴 Overtraining Risk"
        advice = "Prioritize rest and recovery immediately."

    # ---------------------------------------------------------
    # GAUGE CHART
    # ---------------------------------------------------------
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=stress_score,
        title={"text": "Stress Balance Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50], "color": "#7f1d1d"},
                {"range": [50, 75], "color": "#78350f"},
                {"range": [75, 100], "color": "#064e3b"},
            ],
        }
    ))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### {status}")
    st.info(advice)

    # ---------------------------------------------------------
    # BREAKDOWN
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Breakdown")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Workout Avg (min)", f"{avg_work:.1f}")
    col2.metric("Sleep Avg (hrs)", f"{avg_sleep:.1f}")
    col3.metric("Mood Index", f"{avg_mood:.0f}")
    col4.metric("Calories Avg", f"{avg_cal:.0f}")

    conn.close()
