import streamlit as st
from db import ensure_schema

# -----------------------------
# Import All Sections
# -----------------------------
from sections.auth import show_auth
from sections.dashboard import show_dashboard
from sections.workouts import show_workouts
from sections.gpx import show_gpx
from sections.bmi import show_bmi
from sections.mood import show_mood
from sections.ai_engine import show_ai_engine
from sections.analytics import show_analytics
from sections.calendar import show_calendar
from sections.sleep import show_sleep
from sections.hydration import show_hydration
from sections.habits import show_habits
from sections.stress import show_stress
from sections.leaderboard import show_leaderboard
from sections.news import show_news
from sections.nutrition import show_nutrition
from sections.goals import show_goals
from sections.export import show_export
from sections.admin import show_admin
# NEW ADVANCED SECTIONS
from sections.Workout_Map import show_workout_map
from sections.Predictive_Insights import show_predictive_insights
from sections.Achievements import show_achievements
from sections.AI_Coach import show_ai_coach


# -----------------------------
# Initial Setup
# -----------------------------
ensure_schema()

st.set_page_config(
    page_title="FitTrack Pro+",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None


# -----------------------------
# Authentication
# -----------------------------
if not st.session_state.user:
    show_auth()
    st.stop()

uid = st.session_state.user["id"]
username = st.session_state.user["username"]


# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("🏋️ FitTrack Pro+")
st.sidebar.markdown(f"👤 Logged in as: **{username}**")

menu = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Workouts",
        "Workout Map",          # NEW
        "Predictive Insights",  # NEW
        "Achievements",         # NEW
        "GPX Upload",
        "Nutrition",
        "Goals",
        "BMI & Health",
        "Mood",
        "AI Coach",
        "Analytics",
        "Calendar",
        "Sleep",
        "Hydration",
        "Habits",
        "Stress Index",
        "Leaderboard",
        "News",
        "Export",
        "Admin Panel"
    ]
)


# Logout button
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()


# -----------------------------
# Routing
# -----------------------------
if menu == "Dashboard":
    show_dashboard(uid)

elif menu == "Workouts":
    show_workouts(uid)

elif menu == "GPX Upload":
    show_gpx(uid)

elif menu == "Nutrition":
    show_nutrition(uid)

elif menu == "Goals":
    show_goals(uid)

elif menu == "BMI & Health":
    show_bmi(uid)

elif menu == "Mood":
    show_mood(uid)

elif menu == "AI Coach":
    show_ai_engine(uid)

elif menu == "Analytics":
    show_analytics(uid)

elif menu == "Workout Map":
    show_workout_map(uid)

elif menu == "Predictive Insights":
    show_predictive_insights(uid)

elif menu == "Achievements":
    show_achievements(uid)

elif menu == "AI Coach":
    show_ai_coach(uid)

elif menu == "Calendar":
    show_calendar(uid)

elif menu == "Sleep":
    show_sleep(uid)

elif menu == "Hydration":
    show_hydration(uid)

elif menu == "Habits":
    show_habits(uid)

elif menu == "Stress Index":
    show_stress(uid)

elif menu == "Leaderboard":
    show_leaderboard(uid)

elif menu == "News":
    show_news(uid)

elif menu == "Export":
    show_export(uid)

elif menu == "Admin Panel":
    show_admin(uid)
