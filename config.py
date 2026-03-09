import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8040114153"))
DB_NAME = os.getenv("DB_NAME", "bot.db")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Tashkent")

SUNDAY_TEXT = (
    "Assalomu alaykum.\n\n"
    "Iltimos, Kundalik.com ga kirib screenshot tashlang."
)