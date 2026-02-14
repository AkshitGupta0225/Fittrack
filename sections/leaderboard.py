import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_conn


def show_leaderboard(uid):
    conn = get_conn()

    st.title("🏆 Leaderboard")

    # ---------------------------------------------------------
    # FETCH DATA
    # ---------------------------------------------------------
    df = pd.read_sql_query(
        """
        SELECT u.username,
               COUNT(w.id) as total_workouts,
               SUM(w.distance_km) as total_distance,
               SUM(w.duration_min) as total_duration
        FROM users u
        LEFT JOIN workouts w ON u.id = w.user_id
        GROUP BY u.username
        ORDER BY total_distance DESC
        """,
        conn
    )

    if df.empty:
        st.info("No data available yet.")
        conn.close()
        return

    df.fillna(0, inplace=True)

    # ---------------------------------------------------------
    # TOP PERFORMERS
    # ---------------------------------------------------------
    st.subheader("🥇 Top by Distance")

    st.dataframe(df, use_container_width=True)

    # Highlight current user
    if "username" in st.session_state.user:
        current_user = st.session_state.user["username"]
        user_rank = df.reset_index()
        user_rank["rank"] = user_rank.index + 1
        rank_row = user_rank[user_rank["username"] == current_user]

        if not rank_row.empty:
            rank = rank_row["rank"].values[0]
            st.success(f"Your Rank: #{rank}")

    st.markdown("---")

    # ---------------------------------------------------------
    # VISUAL CHART
    # ---------------------------------------------------------
    st.subheader("📊 Distance Leaderboard Chart")

    fig = px.bar(
        df,
        x="username",
        y="total_distance",
        color="total_distance"
    )

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    conn.close()
