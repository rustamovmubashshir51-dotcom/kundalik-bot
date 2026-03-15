import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_ID, SUNDAY_TEXT
from keyboards import admin_keyboard
from database import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()
router = Router()

dp.include_router(router)

scheduler = AsyncIOScheduler()


# USER FORMAT
def format_user(user):

    name = user[1] if user[1] else "Noma'lum"
    username = f"@{user[2]}" if user[2] else "yo'q"

    return f"{name} | {username} | {user[0]}"


# HAR 2 SOATDA ESLATMA
async def send_reminder():

    users = await get_all_user_ids()

    sent_today = await get_today_sender_ids()

    for user_id in users:

        if user_id in sent_today:
            continue

        try:

            await bot.send_message(
                user_id,
                SUNDAY_TEXT
            )

        except:
            pass


# SCHEDULER
def setup_scheduler():

    scheduler.add_job(
        send_reminder,
        "interval",
        hours=2
    )

    scheduler.start()


# START
@router.message(Command("start"))
async def start(message: Message):

    user = message.from_user

    await add_user(
        user.id,
        user.full_name,
        user.username
    )

    await message.answer(
        "Botga xush kelibsiz.\n"
        "Har yakshanba Kundalik screenshot yuborasiz."
    )


# ADMIN PANEL
@router.message(Command("admin"))
async def admin(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "Admin panel",
        reply_markup=admin_keyboard
    )


# STAT
@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):

    users = await get_total_users()
    shots = await get_total_submissions()

    await callback.message.answer(
        f"Users: {users}\nScreenshotlar: {shots}"
    )


# YUBORGANLAR
@router.callback_query(F.data == "sent")
async def sent(callback: CallbackQuery):

    ids = await get_today_sender_ids()

    if not ids:
        await callback.message.answer("Bugun hech kim yubormagan")
        return

    text = "Bugun yuborganlar:\n\n"

    for i in ids:

        user = await get_user_info(i)

        text += format_user(user) + "\n"

    await callback.message.answer(text)


# YUBORMAGANLAR
@router.callback_query(F.data == "not_sent")
async def not_sent(callback: CallbackQuery):

    users = await get_all_users_info()

    sent = set(await get_today_sender_ids())

    text = "Bugun yubormaganlar:\n\n"

    for user in users:

        if user[0] not in sent:

            text += format_user(user) + "\n"

    await callback.message.answer(text)


# HAMMAGA YUBORISH
@router.callback_query(F.data == "send_all")
async def send_all(callback: CallbackQuery):

    await send_reminder()

    await callback.message.answer("Hammaga yuborildi")


# SCREENSHOT
@router.message(F.photo)
async def photo(message: Message):

    user = message.from_user

    await save_submission(user.id)

    await message.answer("Rahmat screenshot uchun")

    await bot.send_photo(

        ADMIN_ID,

        message.photo[-1].file_id,

        caption=f"""
Yangi screenshot

Ism: {user.full_name}
Username: @{user.username}
ID: {user.id}
"""
    )


async def main():

    await init_db()

    setup_scheduler()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
