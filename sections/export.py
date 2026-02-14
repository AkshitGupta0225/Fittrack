import streamlit as st
import pandas as pd
from db import get_conn


def show_export(uid):
    conn = get_conn()

    st.title("📦 Export Data")

    tab1, tab2, tab3 = st.tabs([
        "🏋️ Workouts",
        "🍎 Nutrition",
        "💤 Sleep"
    ])

    # ==========================================================
    # EXPORT WORKOUTS
    # ==========================================================
    with tab1:
        df = pd.read_sql_query(
            "SELECT * FROM workouts WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No workout data to export.")
        else:
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Workouts CSV",
                csv,
                file_name="workouts_export.csv",
                mime="text/csv"
            )

    # ==========================================================
    # EXPORT NUTRITION
    # ==========================================================
    with tab2:
        df = pd.read_sql_query(
            "SELECT * FROM nutrition WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No nutrition data to export.")
        else:
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Nutrition CSV",
                csv,
                file_name="nutrition_export.csv",
                mime="text/csv"
            )

    # ==========================================================
    # EXPORT SLEEP
    # ==========================================================
    with tab3:
        df = pd.read_sql_query(
            "SELECT * FROM sleep WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No sleep data to export.")
        else:
            csv = df.to_csv(index=False)
            st.download_button(
                "Download Sleep CSV",
                csv,
                file_name="sleep_export.csv",
                mime="text/csv"
            )

    conn.close()
