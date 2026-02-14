import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from db import get_conn
from utils import safe_to_datetime


def show_sleep(uid):
    conn = get_conn()

    st.title("💤 Sleep Tracker")

    tab1, tab2 = st.tabs(["🛌 Log Sleep", "📊 Sleep Insights"])

    # ==========================================================
    # LOG SLEEP
    # ==========================================================
    with tab1:
        with st.form("sleep_form"):
            sleep_date = st.date_input("Date", date.today(), key="sleep_date")
            bedtime = st.time_input("Bedtime", key="bedtime")
            waketime = st.time_input("Wake Time", key="waketime")
            quality = st.selectbox(
                "Sleep Quality",
                ["😴 Poor", "😐 Fair", "🙂 Good", "💪 Excellent"],
                key="sleep_quality"
            )

            submitted = st.form_submit_button("Save Sleep Log")

            if submitted:
                # Calculate hours
                bed_dt = datetime.combine(sleep_date, bedtime)
                wake_dt = datetime.combine(
                    sleep_date + timedelta(days=1 if waketime < bedtime else 0),
                    waketime
                )

                hours = round((wake_dt - bed_dt).total_seconds() / 3600, 2)

                conn.execute(
                    """
                    INSERT INTO sleep
                    (user_id, date, bedtime, waketime, hours, quality)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid,
                        sleep_date.isoformat(),
                        bedtime.strftime("%H:%M"),
                        waketime.strftime("%H:%M"),
                        hours,
                        quality
                    )
                )
                conn.commit()
                st.success(f"Sleep logged: {hours} hrs 😴")

    # ==========================================================
    # SLEEP INSIGHTS
    # ==========================================================
    with tab2:
        df = pd.read_sql_query(
            "SELECT * FROM sleep WHERE user_id=? ORDER BY date DESC LIMIT 14",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No sleep data yet.")
        else:
            df["date"] = safe_to_datetime(df["date"])

            avg_sleep = df["hours"].mean()

            st.metric("Average Sleep (Last 14 days)", f"{avg_sleep:.2f} hrs")

            # Sleep quality insight
            if avg_sleep < 6:
                st.error("⚠️ You are sleep deprived. Aim for 7–8 hours.")
            elif avg_sleep < 7:
                st.warning("🟠 Sleep is moderate. Slight improvement recommended.")
            else:
                st.success("🟢 Healthy sleep pattern!")

            st.markdown("---")
            st.subheader("📈 Sleep Trend")

            fig = px.line(
                df.sort_values("date"),
                x="date",
                y="hours",
                markers=True
            )
            fig.update_layout(template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)

    conn.close()
