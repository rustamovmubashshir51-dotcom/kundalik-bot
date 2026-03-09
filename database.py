import aiosqlite
from datetime import datetime
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sent_at TEXT,
                photo_file_id TEXT
            )
        """)

        await db.commit()


async def add_user(user_id: int, full_name: str, username: str | None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, full_name, username, joined_at)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            full_name,
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        await db.commit()


async def save_submission(user_id: int, photo_file_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO submissions (user_id, sent_at, photo_file_id)
            VALUES (?, ?, ?)
        """, (
            user_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            photo_file_id
        ))
        await db.commit()


async def get_total_users() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_total_submissions() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM submissions") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_today_submissions() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM submissions
            WHERE date(sent_at) = ?
        """, (today,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def get_unique_submitters_count() -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id) FROM submissions
        """) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_today_unique_submitters_count() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT COUNT(DISTINCT user_id)
            FROM submissions
            WHERE date(sent_at) = ?
        """, (today,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_today_sender_ids() -> list[int]:
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT DISTINCT user_id
            FROM submissions
            WHERE date(sent_at) = ?
        """, (today,)) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def get_user_info(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT user_id, full_name, username
            FROM users
            WHERE user_id = ?
        """, (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_all_users_info():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT user_id, full_name, username
            FROM users
            ORDER BY joined_at DESC
        """) as cursor:
            return await cursor.fetchall()