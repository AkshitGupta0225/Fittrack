import pandas as pd
import math


# ==========================================================
# SAFE DATETIME PARSER
# Handles mixed formats safely
# ==========================================================
def safe_to_datetime(series):
    return pd.to_datetime(series, errors="coerce")


# ==========================================================
# HAVERSINE DISTANCE (KM)
# ==========================================================
def haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b

    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    x = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(x), math.sqrt(1 - x))


# ==========================================================
# MOOD TO NUMERIC SCORE
# Used in AI + Analytics + Stress Index
# ==========================================================
def mood_to_score(mood):
    mapping = {
        "💪 Energized": 90,
        "🙂 Good": 75,
        "😐 Okay": 60,
        "🙁 Low": 40,
        "😴 Tired": 30
    }
    return mapping.get(mood, 50)
