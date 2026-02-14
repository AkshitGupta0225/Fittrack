import streamlit as st
import pandas as pd
from datetime import date
from db import get_conn


def show_nutrition(uid):
    conn = get_conn()

    st.title("🍎 Nutrition Tracker")

    tab1, tab2, tab3 = st.tabs([
        "➕ Log Meal",
        "📊 Daily Summary",
        "🧠 AI Insights"
    ])

    # ==========================================================
    # LOG MEAL
    # ==========================================================
    with tab1:
        with st.form("log_meal_form"):
            meal_date = st.date_input("Date", date.today(), key="meal_date")
            calories = st.number_input("Calories", min_value=0.0)
            protein = st.number_input("Protein (g)", min_value=0.0)
            carbs = st.number_input("Carbs (g)", min_value=0.0)
            fat = st.number_input("Fat (g)", min_value=0.0)

            submitted = st.form_submit_button("Save Meal")

            if submitted:
                conn.execute(
                    """
                    INSERT INTO nutrition
                    (user_id, date, calories, protein, carbs, fat)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (uid, meal_date.isoformat(), calories, protein, carbs, fat)
                )
                conn.commit()
                st.success("Meal logged successfully! 🥗")

    # ==========================================================
    # DAILY SUMMARY
    # ==========================================================
    with tab2:
        df = pd.read_sql_query(
            "SELECT * FROM nutrition WHERE user_id=? ORDER BY date DESC",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No nutrition data yet.")
        else:
            summary = df.groupby("date").sum(numeric_only=True).reset_index()
            st.dataframe(summary, use_container_width=True)

    # ==========================================================
    # AI INSIGHTS
    # ==========================================================
    with tab3:
        df = pd.read_sql_query(
            "SELECT * FROM nutrition WHERE user_id=? ORDER BY date DESC LIMIT 7",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("Log meals to see AI insights.")
        else:
            avg_cal = df["calories"].mean()
            avg_protein = df["protein"].mean()

            st.metric("Average Calories (Last 7)", f"{avg_cal:.0f} kcal")
            st.metric("Average Protein (Last 7)", f"{avg_protein:.1f} g")

            # Simple AI logic
            if avg_protein < 60:
                st.warning("🍗 Your protein intake seems low. Consider adding more lean protein.")
            elif avg_cal < 1500:
                st.info("⚡ Your calorie intake is relatively low. Ensure you are fueling your workouts.")
            else:
                st.success("🥦 Your nutrition looks balanced this week!")

    conn.close()
