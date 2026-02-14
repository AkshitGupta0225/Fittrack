import streamlit as st
import pandas as pd
import calendar
from datetime import date
from collections import defaultdict
from db import get_conn
from utils import safe_to_datetime


def show_calendar(uid):
    conn = get_conn()

    st.title("📅 Calendar")

    # ---------------------------------------------------------
    # SELECT MONTH
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("Year", [date.today().year - 1, date.today().year, date.today().year + 1], key="cal_year")
    with col2:
        month = st.selectbox(
            "Month",
            list(range(1, 13)),
            format_func=lambda x: calendar.month_name[x],
            key="cal_month"
        )

    st.markdown("---")

    # ---------------------------------------------------------
    # ADD EVENT & JOURNAL
    # ---------------------------------------------------------
    selected_date = st.date_input("Select Date", date.today(), key="cal_date")

    tab1, tab2 = st.tabs(["➕ Add Event", "📝 Add Journal"])

    # ADD EVENT
    with tab1:
        with st.form("add_event_form"):
            title = st.text_input("Event Title")
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")
            location = st.text_input("Location")
            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Save Event")

            if submitted:
                conn.execute(
                    """
                    INSERT INTO events
                    (user_id, title, date, start_time, end_time, location, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid,
                        title,
                        selected_date.isoformat(),
                        start_time.strftime("%H:%M"),
                        end_time.strftime("%H:%M"),
                        location,
                        notes
                    )
                )
                conn.commit()
                st.success("Event saved 📌")

    # ADD JOURNAL
    with tab2:
        with st.form("add_journal_form"):
            title = st.text_input("Journal Title")
            mood = st.selectbox(
                "Mood",
                ["💪 Energized", "🙂 Good", "😐 Okay", "🙁 Low", "😴 Tired"],
                key="journal_mood"
            )
            content = st.text_area("Write your reflection")

            submitted = st.form_submit_button("Save Journal")

            if submitted:
                sentiment_score = 0  # placeholder for future sentiment logic

                conn.execute(
                    """
                    INSERT INTO journals
                    (user_id, date, title, mood, content, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        uid,
                        selected_date.isoformat(),
                        title,
                        mood,
                        content,
                        sentiment_score
                    )
                )
                conn.commit()
                st.success("Journal saved 📝")

    st.markdown("---")

    # ---------------------------------------------------------
    # CALENDAR GRID
    # ---------------------------------------------------------
    st.subheader(f"{calendar.month_name[month]} {year}")

    month_matrix = calendar.monthcalendar(year, month)

    # Fetch events + journals for month
    month_start = date(year, month, 1).isoformat()
    month_end = date(year, month, calendar.monthrange(year, month)[1]).isoformat()

    events = pd.read_sql_query(
        "SELECT date, title FROM events WHERE user_id=? AND date BETWEEN ? AND ?",
        conn,
        params=(uid, month_start, month_end)
    )

    journals = pd.read_sql_query(
        "SELECT date, mood FROM journals WHERE user_id=? AND date BETWEEN ? AND ?",
        conn,
        params=(uid, month_start, month_end)
    )

    event_map = defaultdict(list)
    for _, row in events.iterrows():
        event_map[row["date"]].append(f"📌 {row['title']}")

    journal_map = defaultdict(list)
    for _, row in journals.iterrows():
        journal_map[row["date"]].append(f"📝 {row['mood']}")

    # Weekday headers
    cols = st.columns(7)
    for i, day_name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        cols[i].markdown(f"**{day_name}**")

    # Calendar display
    for week in month_matrix:
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].write("")
            else:
                d = date(year, month, day_num).isoformat()
                content = event_map.get(d, []) + journal_map.get(d, [])

                if content:
                    cols[i].markdown(
                        f"""
                        <div style="background:#161b22;padding:6px;border-radius:8px;">
                        <b>{day_num}</b><br>
                        {"<br>".join(content)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    cols[i].markdown(f"**{day_num}**")

    st.markdown("---")

    # ---------------------------------------------------------
    # VIEW ITEMS FOR SELECTED DATE
    # ---------------------------------------------------------
    st.subheader(f"Items on {selected_date}")

    day_events = pd.read_sql_query(
        "SELECT title, start_time, end_time FROM events WHERE user_id=? AND date=?",
        conn,
        params=(uid, selected_date.isoformat())
    )

    day_journals = pd.read_sql_query(
        "SELECT title, mood, content FROM journals WHERE user_id=? AND date=?",
        conn,
        params=(uid, selected_date.isoformat())
    )

    if day_events.empty and day_journals.empty:
        st.info("No entries for this day.")
    else:
        if not day_events.empty:
            st.markdown("### 📌 Events")
            st.dataframe(day_events, use_container_width=True)

        if not day_journals.empty:
            st.markdown("### 📝 Journals")
            st.dataframe(day_journals, use_container_width=True)

    conn.close()
