import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_conn
from utils import safe_to_datetime


def show_dashboard(uid):
    conn = get_conn()

    st.title("📊 Dashboard Overview")

    # Fetch workouts
    df = pd.read_sql_query(
        "SELECT * FROM workouts WHERE user_id=? ORDER BY date DESC",
        conn,
        params=(uid,)
    )

    if df.empty:
        st.info("No workouts logged yet.")
        return

    # Safe datetime parsing
    df["date"] = safe_to_datetime(df["date"])

    # Summary Metrics
    total_workouts = len(df)
    total_distance = df["distance_km"].fillna(0).sum()
    total_duration = df["duration_min"].fillna(0).sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Workouts", total_workouts)
    col2.metric("Total Distance (km)", f"{total_distance:.2f}")
    col3.metric("Total Duration (min)", f"{total_duration:.0f}")

    st.markdown("---")

    # Monthly Trend
    st.subheader("📈 Monthly Distance Trend")

    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["distance_km"].sum().reset_index()

    fig = px.bar(
        monthly,
        x="month",
        y="distance_km",
        color="distance_km",
        color_continuous_scale="viridis"
    )
    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Recent Workouts
    st.subheader("🕒 Recent Workouts")

    recent = df.head(5)[["date", "title", "sport", "distance_km", "duration_min"]]
    recent["date"] = recent["date"].dt.date

    st.dataframe(recent, use_container_width=True)

    conn.close()
