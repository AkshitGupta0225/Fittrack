import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from db import get_conn
from utils import mood_to_score, safe_to_datetime


def show_mood(uid):
    conn = get_conn()

    st.title("🧘 Mood & Mental Wellness")

    tab1, tab2, tab3 = st.tabs([
        "Log Mood",
        "Mood History",
        "Mood Analytics"
    ])

    # ==========================================================
    # TAB 1 — LOG MOOD
    # ==========================================================
    with tab1:
        with st.form("mood_form"):
            mood_date = st.date_input("Date", date.today())
            mood = st.selectbox(
                "How are you feeling?",
                ["💪 Energized", "🙂 Good", "😐 Okay", "🙁 Low", "😴 Tired"]
            )
            notes = st.text_area("Notes (optional)")

            submitted = st.form_submit_button("Save Mood")

            if submitted:
                sentiment = mood_to_score(mood)

                conn.execute(
                    """
                    INSERT INTO journals
                    (user_id, date, title, mood, content, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid,
                        mood_date.isoformat(),
                        "Mood Entry",
                        mood,
                        notes,
                        sentiment
                    )
                )
                conn.commit()
                st.success("Mood logged successfully.")

    # ==========================================================
    # TAB 2 — MOOD HISTORY
    # ==========================================================
    with tab2:
        df = pd.read_sql_query(
            "SELECT date, mood, content, sentiment FROM journals WHERE user_id=? ORDER BY date DESC",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No mood data yet.")
        else:
            st.dataframe(df, use_container_width=True)

    # ==========================================================
    # TAB 3 — MOOD ANALYTICS
    # ==========================================================
    with tab3:
        df = pd.read_sql_query(
            "SELECT date, mood, sentiment FROM journals WHERE user_id=?",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No mood analytics yet.")
        else:
            df["date"] = safe_to_datetime(df["date"])
            df = df.sort_values("date")

            st.subheader("Mood Trend Over Time")

            fig = px.line(
                df,
                x="date",
                y="sentiment",
                markers=True
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            avg_mood = df["sentiment"].mean()

            st.metric("Average Mood Score", f"{avg_mood:.1f}")

            if avg_mood < 40:
                st.warning("Your overall mood trend seems low. Consider recovery and support.")
            elif avg_mood < 70:
                st.info("Your mood is stable but can improve.")
            else:
                st.success("You are maintaining a strong positive mindset.")

    conn.close()
