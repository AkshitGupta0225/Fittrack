import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import get_conn
from datetime import date


def show_bmi(uid):
    conn = get_conn()

    st.title("📊 BMI & Health Calculator")

    tab1, tab2 = st.tabs(["BMI Calculator", "Health Insights"])

    # ==========================================================
    # TAB 1 — BMI + BMR + Daily Calories
    # ==========================================================
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            unit = st.selectbox("Unit System", ["Metric (kg, cm)", "Imperial (lb, in)"])
            age = st.number_input("Age", min_value=10, max_value=100, value=22)
            gender = st.selectbox("Gender", ["Male", "Female"])

        with col2:
            if unit.startswith("Metric"):
                weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
                height = st.number_input("Height (cm)", min_value=50.0, value=170.0)
                height_m = height / 100
                bmi = weight / (height_m ** 2)
            else:
                weight = st.number_input("Weight (lb)", min_value=10.0, value=154.0)
                height = st.number_input("Height (in)", min_value=20.0, value=67.0)
                weight_kg = weight * 0.453592
                height_m = height * 0.0254
                bmi = weight_kg / (height_m ** 2)

        bmi_value = round(bmi, 2)
        st.markdown(f"## Your BMI: **{bmi_value}**")

        # BMI Category
        if bmi_value < 18.5:
            category = "Underweight"
            color = "#3b82f6"
        elif bmi_value < 25:
            category = "Normal"
            color = "#10b981"
        elif bmi_value < 30:
            category = "Overweight"
            color = "#f59e0b"
        else:
            category = "Obese"
            color = "#ef4444"

        st.markdown(f"### Category: {category}")

        # BMI Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi_value,
            title={"text": "BMI Scale"},
            gauge={
                "axis": {"range": [10, 40]},
                "bar": {"color": color},
                "steps": [
                    {"range": [10, 18.5], "color": "#93c5fd"},
                    {"range": [18.5, 25], "color": "#86efac"},
                    {"range": [25, 30], "color": "#fde68a"},
                    {"range": [30, 40], "color": "#fca5a5"},
                ],
            }
        ))

        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # BMR Calculation (Mifflin-St Jeor)
        if unit.startswith("Metric"):
            weight_kg = weight
        else:
            weight_kg = weight * 0.453592

        if gender == "Male":
            bmr = 10 * weight_kg + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height - 5 * age - 161

        st.markdown(f"### 🔥 Estimated BMR: {int(bmr)} kcal/day")

        activity = st.selectbox(
            "Activity Level",
            [
                "Sedentary",
                "Lightly Active",
                "Moderately Active",
                "Very Active",
                "Athlete"
            ]
        )

        multiplier = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Athlete": 1.9
        }

        daily_calories = int(bmr * multiplier[activity])

        st.markdown(f"### 🍽 Maintenance Calories: {daily_calories} kcal/day")

        st.markdown("---")

        # Save BMI Record
        if st.button("Save BMI Record"):
            conn.execute(
                "INSERT INTO bmi_records (user_id, date, bmi, category) VALUES (?, ?, ?, ?)",
                (uid, date.today().isoformat(), bmi_value, category)
            )
            conn.commit()
            st.success("BMI record saved.")

    # ==========================================================
    # TAB 2 — BMI History
    # ==========================================================
    with tab2:
        df = pd.read_sql_query(
            "SELECT * FROM bmi_records WHERE user_id=? ORDER BY date DESC",
            conn,
            params=(uid,)
        )

        if df.empty:
            st.info("No BMI records yet.")
        else:
            st.dataframe(df, use_container_width=True)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["bmi"],
                mode="lines+markers"
            ))
            fig.update_layout(template="plotly_dark", title="BMI Trend")
            st.plotly_chart(fig, use_container_width=True)

    conn.close()
