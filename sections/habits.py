import streamlit as st
import pandas as pd
from datetime import date
from db import get_conn


def show_habits(uid):
    conn = get_conn()

    st.title("🧩 Habit Builder")

    today = date.today().isoformat()

    tab1, tab2 = st.tabs(["➕ Add Habit", "✅ Today's Habits"])

    # ==========================================================
    # ADD HABIT
    # ==========================================================
    with tab1:
        habit_name = st.text_input("New Habit Name")

        if st.button("Add Habit"):
            if habit_name.strip():
                conn.execute(
                    "INSERT INTO habits (user_id, date, habit_name, completed) VALUES (?, ?, ?, 0)",
                    (uid, today, habit_name.strip())
                )
                conn.commit()
                st.success("Habit added!")
                st.rerun()
            else:
                st.warning("Enter a habit name.")

    # ==========================================================
    # TODAY'S HABITS
    # ==========================================================
    with tab2:
        habits_df = pd.read_sql_query(
            "SELECT * FROM habits WHERE user_id=? AND date=?",
            conn,
            params=(uid, today)
        )

        if habits_df.empty:
            st.info("No habits added today.")
        else:
            for _, row in habits_df.iterrows():
                checked = st.checkbox(
                    row["habit_name"],
                    value=bool(row["completed"]),
                    key=f"habit_{row['id']}"
                )

                if checked != bool(row["completed"]):
                    conn.execute(
                        "UPDATE habits SET completed=? WHERE id=?",
                        (int(checked), row["id"])
                    )
                    conn.commit()

            st.markdown("---")

            # Completion Summary
            total = len(habits_df)
            completed = habits_df["completed"].sum()

            if total > 0:
                progress = completed / total
                st.progress(progress)
                st.write(f"Completed {completed} out of {total} habits today")

    # ==========================================================
    # HABIT HISTORY
    # ==========================================================
    st.markdown("---")
    st.subheader("📊 Habit History (Last 14 Days)")

    history = pd.read_sql_query(
        "SELECT date, habit_name, completed FROM habits WHERE user_id=? ORDER BY date DESC LIMIT 50",
        conn,
        params=(uid,)
    )

    if not history.empty:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No habit history yet.")

    conn.close()
