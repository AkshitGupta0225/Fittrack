# sections/Achievements.py

import streamlit as st
from db import get_conn
import pandas as pd
from datetime import datetime


def show_achievements(uid):
    st.title("🏆 Achievements & Progress")

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT COUNT(*), 
               SUM(distance_km), 
               SUM(duration_min)
        FROM workouts 
        WHERE user_id=?
    """, (uid,))

    row = c.fetchone()

    total_workouts = row[0] or 0
    total_distance = row[1] or 0
    total_duration = row[2] or 0

    # ==========================================================
    # XP SYSTEM
    # ==========================================================
    xp = (total_workouts * 10) + (total_distance * 5) + (total_duration * 2)
    level = int(xp // 100)
    next_level_xp = (level + 1) * 100
    progress = (xp % 100) / 100

    col1, col2 = st.columns(2)
    col1.metric("⭐ Total XP", int(xp))
    col2.metric("🎯 Level", level)

    st.progress(progress)
    st.caption(f"{int(xp)} / {next_level_xp} XP to reach Level {level+1}")

    st.markdown("---")

    # ==========================================================
    # ACHIEVEMENT BADGES
    # ==========================================================
    st.subheader("🏅 Milestones")

    achievements = []

    if total_workouts >= 5:
        achievements.append("🔥 5 Workouts Starter")
    if total_workouts >= 10:
        achievements.append("🏅 10 Workouts Completed")
    if total_workouts >= 25:
        achievements.append("💪 25 Workouts Warrior")

    if total_distance >= 20:
        achievements.append("🚶 20 KM Walker")
    if total_distance >= 50:
        achievements.append("🏃 50 KM Milestone")
    if total_distance >= 100:
        achievements.append("🚀 100 KM Elite")

    if total_duration >= 200:
        achievements.append("⏱️ 200 Minutes Active")
    if total_duration >= 500:
        achievements.append("🏆 500 Minutes Champion")
    if total_duration >= 1000:
        achievements.append("👑 1000 Minutes Legend")

    if achievements:
        for a in achievements:
            st.success(a)
    else:
        st.info("No achievements unlocked yet. Keep going!")

    st.markdown("---")

    # ==========================================================
    # STREAK SYSTEM
    # ==========================================================
    st.subheader("🔥 Activity Streak")

    df = pd.read_sql_query(
        "SELECT date FROM workouts WHERE user_id=? ORDER BY date",
        conn,
        params=(uid,)
    )

    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna()

        df = df.sort_values("date")
        df["diff"] = df["date"].diff().dt.days

        streak = 1
        max_streak = 1

        for diff in df["diff"][1:]:
            if diff == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1

        st.metric("Current Streak (days)", streak)
        st.metric("Longest Streak (days)", max_streak)
    else:
        st.info("No workout data for streak calculation.")

    st.markdown("---")

    # ==========================================================
    # NEXT GOAL PROGRESS
    # ==========================================================
    st.subheader("🎯 Next Goals")

    next_workout_goal = 10
    next_distance_goal = 50
    next_duration_goal = 500

    st.write("Workouts Progress")
    st.progress(min(total_workouts / next_workout_goal, 1.0))

    st.write("Distance Progress")
    st.progress(min(total_distance / next_distance_goal, 1.0))

    st.write("Duration Progress")
    st.progress(min(total_duration / next_duration_goal, 1.0))
