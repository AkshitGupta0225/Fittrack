import streamlit as st
import pandas as pd
from db import get_conn


def show_admin(uid):
    conn = get_conn()

    # Only allow admin user
    if st.session_state.user["username"] != "admin":
        st.warning("Admin access only.")
        return

    st.title("👨‍💼 Admin Control Panel")

    tab1, tab2, tab3 = st.tabs([
        "👥 Users",
        "🏋️ Workouts",
        "🧾 Database Stats"
    ])

    # ==========================================================
    # TAB 1 — USERS
    # ==========================================================
    with tab1:
        users = pd.read_sql_query("SELECT id, username FROM users", conn)

        if users.empty:
            st.info("No users found.")
        else:
            st.dataframe(users, use_container_width=True)

            user_to_delete = st.selectbox(
                "Select User to Delete",
                users["username"].tolist()
            )

            if st.button("Delete Selected User"):
                conn.execute("DELETE FROM users WHERE username=?", (user_to_delete,))
                conn.commit()
                st.success("User deleted.")
                st.rerun()

    # ==========================================================
    # TAB 2 — WORKOUT RECORDS
    # ==========================================================
    with tab2:
        workouts = pd.read_sql_query(
            """
            SELECT u.username, w.title, w.date, w.distance_km
            FROM workouts w
            JOIN users u ON w.user_id = u.id
            ORDER BY w.date DESC
            """,
            conn
        )

        if workouts.empty:
            st.info("No workout records.")
        else:
            st.dataframe(workouts, use_container_width=True)

    # ==========================================================
    # TAB 3 — DATABASE STATS
    # ==========================================================
    with tab3:
        total_users = pd.read_sql_query("SELECT COUNT(*) as count FROM users", conn)["count"][0]
        total_workouts = pd.read_sql_query("SELECT COUNT(*) as count FROM workouts", conn)["count"][0]
        total_journals = pd.read_sql_query("SELECT COUNT(*) as count FROM journals", conn)["count"][0]
        total_sleep = pd.read_sql_query("SELECT COUNT(*) as count FROM sleep", conn)["count"][0]

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        col1.metric("Total Users", total_users)
        col2.metric("Total Workouts", total_workouts)
        col3.metric("Total Journals", total_journals)
        col4.metric("Total Sleep Records", total_sleep)

    conn.close()
