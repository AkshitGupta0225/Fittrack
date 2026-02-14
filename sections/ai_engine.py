import streamlit as st
import pandas as pd
from db import get_conn
from utils import mood_to_score


def show_ai_engine(uid):
    conn = get_conn()

    st.title("🤖 AI Recommendation Engine")

    st.markdown("Personalized insights generated from your activity, mood, sleep, BMI and nutrition.")

    # ---------------------------------------------------------
    # FETCH DATA
    # ---------------------------------------------------------
    workouts = pd.read_sql_query(
        "SELECT date, duration_min FROM workouts WHERE user_id=? ORDER BY date DESC LIMIT 7",
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

    bmi = pd.read_sql_query(
        "SELECT bmi FROM bmi_records WHERE user_id=? ORDER BY date DESC LIMIT 1",
        conn,
        params=(uid,)
    )

    nutrition = pd.read_sql_query(
        "SELECT calories, protein FROM nutrition WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    st.markdown("---")

    recommendations = []

    # ---------------------------------------------------------
    # WORKOUT ANALYSIS
    # ---------------------------------------------------------
    if not workouts.empty:
        avg_duration = workouts["duration_min"].mean()

        if avg_duration > 75:
            recommendations.append("🔴 You have been training intensely. Consider a recovery or light mobility session.")
        elif avg_duration < 20:
            recommendations.append("🟠 Your workouts are short. Try extending duration for better endurance.")
        else:
            recommendations.append("🟢 Your workout duration looks balanced.")

    else:
        recommendations.append("🏃 No recent workouts detected. A light 20-minute session could boost energy.")

    # ---------------------------------------------------------
    # MOOD ANALYSIS
    # ---------------------------------------------------------
    if not journals.empty:
        mood_scores = journals["mood"].apply(mood_to_score)
        avg_mood = mood_scores.mean()

        if avg_mood < 40:
            recommendations.append("🧘 Your mood trend is low. Prioritize recovery and mindfulness.")
        elif avg_mood > 75:
            recommendations.append("💪 Strong positive mood trend! Maintain your routine.")
        else:
            recommendations.append("🙂 Mood seems stable. Keep consistent habits.")

    # ---------------------------------------------------------
    # SLEEP ANALYSIS
    # ---------------------------------------------------------
    if not sleep.empty:
        avg_sleep = sleep["hours"].mean()

        if avg_sleep < 6:
            recommendations.append("😴 Sleep is below recommended levels. Aim for 7–8 hours.")
        else:
            recommendations.append("🟢 Sleep pattern looks healthy.")

    # ---------------------------------------------------------
    # BMI ANALYSIS
    # ---------------------------------------------------------
    if not bmi.empty:
        latest_bmi = bmi["bmi"].iloc[0]

        if latest_bmi < 18.5:
            recommendations.append("⚖️ BMI indicates underweight. Focus on nutrient-dense meals.")
        elif latest_bmi < 25:
            recommendations.append("✅ BMI is within healthy range.")
        elif latest_bmi < 30:
            recommendations.append("⚠️ BMI indicates overweight. Increase cardio sessions.")
        else:
            recommendations.append("🚨 BMI indicates obesity risk. Structured fitness plan recommended.")

    # ---------------------------------------------------------
    # NUTRITION ANALYSIS
    # ---------------------------------------------------------
    if not nutrition.empty:
        avg_protein = nutrition["protein"].mean()

        if avg_protein < 60:
            recommendations.append("🍗 Protein intake seems low. Increase lean protein sources.")
        else:
            recommendations.append("🥗 Protein intake is adequate.")

    # ---------------------------------------------------------
    # DISPLAY RESULTS
    # ---------------------------------------------------------
    if recommendations:
        st.subheader("🔎 Personalized Recommendations")

        for rec in recommendations:
            st.markdown(
                f"""
                <div style='background:#161b22;padding:12px;border-radius:8px;margin-bottom:8px;'>
                {rec}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Not enough data to generate insights yet.")

    conn.close()
