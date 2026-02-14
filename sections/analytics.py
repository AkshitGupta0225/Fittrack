import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import get_conn
from utils import mood_to_score, safe_to_datetime


def show_analytics(uid):
    conn = get_conn()

    st.title("📈 Analytics Dashboard")

    tab1, tab2, tab3 = st.tabs([
        "Workout Trends",
        "Mood Correlation",
        "Activity Heatmap"
    ])

    # ==========================================================
    # TAB 1 — WORKOUT TRENDS
    # ==========================================================
    with tab1:

        df = pd.read_sql_query(
            "SELECT date, distance_km, duration_min FROM workouts WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No workout data yet.")
        else:
            df["date"] = safe_to_datetime(df["date"])

            # Weekly total distance
            df_week = df.copy()
            df_week["week"] = df_week["date"].dt.to_period("W").astype(str)

            weekly = df_week.groupby("week").sum(numeric_only=True).reset_index()

            st.subheader("Weekly Distance")
            fig = px.bar(weekly, x="week", y="distance_km")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Workout Duration Trend")
            fig2 = px.line(df.sort_values("date"), x="date", y="duration_min", markers=True)
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    # ==========================================================
    # TAB 2 — MOOD VS WORKOUT CORRELATION
    # ==========================================================
    with tab2:

        workouts = pd.read_sql_query(
            "SELECT date, duration_min FROM workouts WHERE user_id=?",
            conn,
            params=(uid,)
        )

        journals = pd.read_sql_query(
            "SELECT date, mood FROM journals WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if workouts.empty or journals.empty:
            st.info("Need both workout and mood data.")
        else:
            workouts["date"] = safe_to_datetime(workouts["date"])
            journals["date"] = safe_to_datetime(journals["date"])

            journals["mood_score"] = journals["mood"].apply(mood_to_score)

            merged = pd.merge(workouts, journals, on="date", how="inner")

            if merged.empty:
                st.info("No matching workout and mood dates.")
            else:
                corr = merged["duration_min"].corr(merged["mood_score"])

                st.metric("Correlation (Workout Duration vs Mood)", f"{corr:.2f}")

                fig = px.scatter(
                    merged,
                    x="duration_min",
                    y="mood_score",
                    trendline="ols"
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

                if corr > 0:
                    st.success("Positive correlation: Workouts improve mood.")
                else:
                    st.warning("Negative correlation detected.")

    # ==========================================================
    # TAB 3 — MONTHLY ACTIVITY HEATMAP
    # ==========================================================
    with tab3:

        df_heat = pd.read_sql_query(
            """
            SELECT date FROM workouts WHERE user_id=?
            UNION ALL
            SELECT date FROM journals WHERE user_id=?
            """,
            conn,
            params=(uid, uid)
        )

        if df_heat.empty:
            st.info("No data for heatmap.")
        else:
            df_heat["date"] = safe_to_datetime(df_heat["date"])
            df_heat["day"] = df_heat["date"].dt.day

            counts = df_heat.groupby("day").size().reset_index(name="count")

            fig = px.density_heatmap(
                counts,
                x="day",
                y=["Activity"] * len(counts),
                z="count",
                color_continuous_scale="Viridis"
            )

            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    conn.close()
