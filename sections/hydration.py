import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from db import get_conn


def show_hydration(uid):
    conn = get_conn()
    st.title("💧 Hydration Tracker")

    today = date.today().isoformat()

    # Get today's record
    record = pd.read_sql_query(
        "SELECT * FROM hydration WHERE user_id=? AND date=?",
        conn,
        params=(uid, today)
    )

    if record.empty:
        conn.execute(
            "INSERT INTO hydration (user_id, date, glasses) VALUES (?, ?, ?)",
            (uid, today, 0)
        )
        conn.commit()
        glasses = 0
    else:
        glasses = record["glasses"].iloc[0]

        # 🔥 FIX: convert bytes to int if needed
        if isinstance(glasses, bytes):
            glasses = int.from_bytes(glasses, byteorder="little")

        glasses = int(glasses or 0)

    # ==========================================================
    # INTERACTIVE GLASSES
    # ==========================================================
    st.subheader("Today's Water Intake")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➖ Remove Glass"):
            glasses = max(int(glasses) - 1, 0)
            conn.execute(
                "UPDATE hydration SET glasses=? WHERE user_id=? AND date=?",
                (int(glasses), uid, today)
            )
            conn.commit()
            st.rerun()

    with col2:
        st.metric("Glasses Today", glasses)

    with col3:
        if st.button("➕ Add Glass"):
            glasses = int(glasses) + 1
            conn.execute(
                "UPDATE hydration SET glasses=? WHERE user_id=? AND date=?",
                (int(glasses), uid, today)
            )
            conn.commit()
            st.rerun()

    # Visual glasses
    st.markdown("### 🥛 Visual Tracker")
    st.write(" ".join(["🥛"] * glasses))

    st.markdown("---")

    # ==========================================================
    # WEEKLY TREND
    # ==========================================================
    st.subheader("📊 Weekly Hydration Trend")

    df = pd.read_sql_query(
        "SELECT * FROM hydration WHERE user_id=? ORDER BY date DESC LIMIT 7",
        conn,
        params=(uid,)
    )

    if not df.empty:
        # 🔥 Fix weekly data as well
        df["glasses"] = df["glasses"].apply(
            lambda x: int.from_bytes(x, "little") if isinstance(x, bytes) else int(x)
        )

        fig = px.bar(
            df.sort_values("date"),
            x="date",
            y="glasses",
            color="glasses"
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hydration history yet.")

    conn.close()
