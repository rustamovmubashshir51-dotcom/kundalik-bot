import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()


async def init_db():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT
    )
    """)

    conn.commit()


async def add_user(user_id, full_name, username):

    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES(?,?,?)",
        (user_id, full_name, username)
    )

    conn.commit()


async def save_submission(user_id):

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO submissions(user_id,date) VALUES(?,?)",
        (user_id, today)
    )

    conn.commit()


async def get_all_user_ids():

    cursor.execute("SELECT user_id FROM users")

    return [i[0] for i in cursor.fetchall()]


async def get_today_sender_ids():

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT DISTINCT user_id FROM submissions WHERE date=?",
        (today,)
    )

    return [i[0] for i in cursor.fetchall()]


async def get_total_users():

    cursor.execute("SELECT COUNT(*) FROM users")

    return cursor.fetchone()[0]


async def get_total_submissions():

    cursor.execute("SELECT COUNT(*) FROM submissions")

    return cursor.fetchone()[0]


async def get_all_users_info():

    cursor.execute("SELECT * FROM users")

    return cursor.fetchall()


async def get_user_info(user_id):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    return cursor.fetchone()
