import os
import sqlite3
import bcrypt

DB_PATH = os.path.join("data", "fittrack.db")


# ==========================================================
# CONNECTION
# ==========================================================
def get_conn():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================================
# SCHEMA
# ==========================================================
def ensure_schema():
    conn = get_conn()
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash BLOB NOT NULL
    )
    """)

    # WORKOUTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS workouts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        sport TEXT,
        date TEXT,
        distance_km REAL,
        duration_min REAL,
        ascent_m REAL,
        notes TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # JOURNALS
    c.execute("""
    CREATE TABLE IF NOT EXISTS journals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        title TEXT,
        mood TEXT,
        content TEXT,
        sentiment REAL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # EVENTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        location TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # SLEEP
    c.execute("""
    CREATE TABLE IF NOT EXISTS sleep(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        bedtime TEXT,
        waketime TEXT,
        hours REAL,
        quality TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # NUTRITION
    c.execute("""
    CREATE TABLE IF NOT EXISTS nutrition(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # HABITS
    c.execute("""
    CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        habit_name TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # HYDRATION
    c.execute("""
    CREATE TABLE IF NOT EXISTS hydration(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        glasses INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # GOALS
    c.execute("""
    CREATE TABLE IF NOT EXISTS goals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        goal_type TEXT,
        target_value REAL,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # BMI RECORDS (IMPORTANT – was missing earlier)
    c.execute("""
    CREATE TABLE IF NOT EXISTS bmi_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        bmi REAL,
        category TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

        # ==========================================================
    # WORKOUT GPS POINTS (For Workout Map)
    # ==========================================================
    c.execute("""
    CREATE TABLE IF NOT EXISTS workout_points(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        workout_id INTEGER,
        latitude REAL,
        longitude REAL,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(workout_id) REFERENCES workouts(id) ON DELETE CASCADE
    )
    """)

    # ==========================================================
    # USER XP SYSTEM
    # ==========================================================
    c.execute("""
    CREATE TABLE IF NOT EXISTS xp_system(
        user_id INTEGER PRIMARY KEY,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()


    # ----------------------------------------------------------
    # CREATE DEFAULT ADMIN USER (if not exists)
    # ----------------------------------------------------------
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users(username,password_hash) VALUES (?,?)",
                  ("admin", hashed))
        conn.commit()

    conn.close()


# ==========================================================
# USER FUNCTIONS
# ==========================================================
def create_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    c.execute("INSERT INTO users(username,password_hash) VALUES (?,?)",
              (username, hashed))
    conn.commit()
    conn.close()


def get_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row


def verify_password(password, hash_):
    if hash_ is None:
        return False
    return bcrypt.checkpw(password.encode(), hash_)
