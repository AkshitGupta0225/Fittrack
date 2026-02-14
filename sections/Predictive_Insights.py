# sections/Predictive_Insights.py

import streamlit as st
import pandas as pd
from db import get_conn
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.express as px


def show_predictive_insights(uid):
    st.title("📊 Predictive Insights")

    conn = get_conn()

    df = pd.read_sql_query(
        "SELECT date, duration_min, distance_km FROM workouts WHERE user_id=? ORDER BY date",
        conn,
        params=(uid,)
    )

    conn.close()

    df = df.dropna(subset=["distance_km"])

    if len(df) < 5:
        st.warning("Need at least 5 workouts for prediction.")
        return

    # ✅ Proper date handling
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    # Convert date to numeric days
    df["days"] = (df["date"] - df["date"].min()).dt.days

    X = df[["days"]]
    y = df["distance_km"]

    model = LinearRegression()
    model.fit(X, y)

    # Predict next workout (based on next day interval)
    next_day = df["days"].max() + 7  # assume next workout in 7 days
    prediction = model.predict([[next_day]])[0]

    # ==========================================================
    # METRICS
    # ==========================================================
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Workouts", len(df))
    col2.metric("Average Distance", f"{round(df['distance_km'].mean(),2)} km")
    col3.metric("Predicted Next", f"{round(prediction,2)} km")

    st.markdown("---")

    # ==========================================================
    # TREND GRAPH
    # ==========================================================
    df["Predicted"] = model.predict(X)

    fig = px.line(
        df,
        x="date",
        y=["distance_km", "Predicted"],
        title="Actual vs Predicted Trend",
        labels={"value": "Distance (km)", "date": "Date"}
    )

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # ==========================================================
    # PERFORMANCE ANALYSIS
    # ==========================================================
    last_actual = df["distance_km"].iloc[-1]
    growth = prediction - last_actual

    if growth > 0:
        st.success(f"📈 You are improving! +{round(growth,2)} km expected.")
    elif growth < 0:
        st.warning(f"📉 Slight drop predicted: {round(abs(growth),2)} km.")
    else:
        st.info("📊 Performance stable.")

    # ==========================================================
    # NEXT 5 PREDICTIONS (WEEKLY)
    # ==========================================================
    future_days = np.array([df["days"].max() + 7*i for i in range(1,6)]).reshape(-1,1)
    future_preds = model.predict(future_days)

    future_df = pd.DataFrame({
        "Week Ahead": range(1,6),
        "Predicted Distance (km)": [round(p,2) for p in future_preds]
    })

    st.subheader("🔮 Next 5 Week Predictions")
    st.dataframe(future_df, use_container_width=True)
