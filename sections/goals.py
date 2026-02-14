import streamlit as st
import pandas as pd
from datetime import date
from db import get_conn


def show_goals(uid):
    conn = get_conn()

    st.title("🎯 Goals")

    tab1, tab2 = st.tabs(["➕ Set Goal", "📊 View Progress"])

    # ==========================================================
    # SET GOAL
    # ==========================================================
    with tab1:
        with st.form("set_goal_form"):
            goal_type = st.selectbox(
                "Goal Type",
                ["Total Distance (km)", "Total Workouts", "Target Calories"]
            )
            target_value = st.number_input("Target Value", min_value=0.0)
            start_date = st.date_input("Start Date", date.today())
            end_date = st.date_input("End Date", date.today())

            submitted = st.form_submit_button("Save Goal")

            if submitted:
                conn.execute(
                    """
                    INSERT INTO goals
                    (user_id, goal_type, target_value, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        uid,
                        goal_type,
                        target_value,
                        start_date.isoformat(),
                        end_date.isoformat()
                    )
                )
                conn.commit()
                st.success("Goal created successfully! 🎯")

    # ==========================================================
    # VIEW PROGRESS
    # ==========================================================
    with tab2:

        goals_df = pd.read_sql_query(
            "SELECT * FROM goals WHERE user_id=? ORDER BY end_date DESC",
            conn,
            params=(uid,)
        )

        if goals_df.empty:
            st.info("No goals set yet.")
        else:
            for _, goal in goals_df.iterrows():

                st.markdown(f"### {goal['goal_type']}")
                st.write(f"Target: {goal['target_value']}")
                st.write(f"From {goal['start_date']} to {goal['end_date']}")

                # Calculate current progress
                if goal["goal_type"] == "Total Distance (km)":
                    current = pd.read_sql_query(
                        "SELECT SUM(distance_km) as total FROM workouts WHERE user_id=?",
                        conn,
                        params=(uid,)
                    )["total"][0] or 0

                elif goal["goal_type"] == "Total Workouts":
                    current = pd.read_sql_query(
                        "SELECT COUNT(*) as total FROM workouts WHERE user_id=?",
                        conn,
                        params=(uid,)
                    )["total"][0]

                elif goal["goal_type"] == "Target Calories":
                    current = pd.read_sql_query(
                        "SELECT SUM(calories) as total FROM nutrition WHERE user_id=?",
                        conn,
                        params=(uid,)
                    )["total"][0] or 0

                else:
                    current = 0

                progress = min(current / goal["target_value"], 1.0) if goal["target_value"] else 0

                st.progress(progress)
                st.write(f"Current Progress: {current:.2f}")

                st.markdown("---")

    conn.close()
