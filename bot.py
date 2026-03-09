import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_ID, TIMEZONE, SUNDAY_TEXT
from keyboards import admin_keyboard
from database import (
    init_db,
    add_user,
    save_submission,
    get_total_users,
    get_total_submissions,
    get_today_submissions,
    get_all_user_ids,
    get_unique_submitters_count,
    get_today_unique_submitters_count,
    get_today_sender_ids,
    get_user_info,
    get_all_users_info,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi. .env faylga token yozing.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

scheduler = AsyncIOScheduler(timezone=TIMEZONE)


def format_user_line(user_id: int, full_name: str | None, username: str | None) -> str:
    name = full_name if full_name else "Noma'lum"
    user_tag = f"@{username}" if username else "yo'q"
    return f"• {name} | ID: {user_id} | Username: {user_tag}"


async def build_sent_users_text() -> str:
    sender_ids = await get_today_sender_ids()
    if not sender_ids:
        return "Bugun hali hech kim screenshot yubormagan."

    lines = ["👥 Bugun screenshot yuborganlar:\n"]
    for user_id in sender_ids:
        user = await get_user_info(user_id)
        if user:
            lines.append(format_user_line(user[0], user[1], user[2]))
        else:
            lines.append(f"• ID: {user_id}")

    return "\n".join(lines)


async def build_not_sent_users_text() -> str:
    all_users = await get_all_users_info()
    sender_ids = set(await get_today_sender_ids())

    not_sent = [u for u in all_users if u[0] not in sender_ids]

    if not not_sent:
        return "Bugun hamma screenshot yuborgan."

    lines = ["❌ Bugun screenshot yubormaganlar:\n"]
    for user in not_sent:
        lines.append(format_user_line(user[0], user[1], user[2]))

    return "\n".join(lines)


async def send_sunday_reminder():
    user_ids = await get_all_user_ids()
    sent_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, SUNDAY_TEXT)
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logging.error(f"{user_id} ga yuborilmadi: {e}")

    try:
        await bot.send_message(
            ADMIN_ID,
            f"📢 Yakshanbalik eslatma yuborildi\n"
            f"✅ Yuborildi: {sent_count}\n"
            f"❌ Yuborilmadi: {failed_count}"
        )
    except Exception as e:
        logging.error(f"Admin ga hisobot yuborilmadi: {e}")

    return sent_count, failed_count


async def scheduled_sunday_job():
    logging.info("Yakshanbalik eslatma ishga tushdi")
    await send_sunday_reminder()


def setup_scheduler():
    scheduler.add_job(
        scheduled_sunday_job,
        trigger="cron",
        day_of_week="sun",
        hour=9,
        minute=0,
        id="weekly_kundalik_reminder",
        replace_existing=True,
    )
    scheduler.start()


@router.message(Command("start"))
async def start_handler(message: Message):
    user = message.from_user

    await add_user(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username
    )

    await message.answer(
        "Botga xush kelibsiz.\n"
        "Har yakshanba sizga Kundalik.com screenshot yuborish eslatmasi keladi."
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Buyruqlar:\n"
        "/start - botga kirish\n"
        "/help - yordam\n\n"
        "Admin uchun:\n"
        "/admin - admin panel\n"
        "/stat - statistika\n"
        "/send_now - hozir hammaga eslatma yuborish"
    )


@router.message(Command("admin"))
async def admin_panel_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Siz admin emassiz.")
        return

    await message.answer(
        "Admin panel:",
        reply_markup=admin_keyboard()
    )


@router.message(Command("stat"))
async def stat_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total_users = await get_total_users()
    total_submissions = await get_total_submissions()
    today_submissions = await get_today_submissions()
    total_unique_submitters = await get_unique_submitters_count()
    today_unique_submitters = await get_today_unique_submitters_count()

    text = (
        "📊 Statistika\n\n"
        f"👥 Botga kirganlar: {total_users}\n"
        f"🖼 Jami screenshotlar: {total_submissions}\n"
        f"🙋 Screenshot yuborganlar: {total_unique_submitters}\n"
        f"📅 Bugun screenshotlar: {today_submissions}\n"
        f"✅ Bugun yuborganlar: {today_unique_submitters}"
    )
    await message.answer(text)


@router.message(Command("send_now"))
async def send_now_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    sent_count, failed_count = await send_sunday_reminder()
    await message.answer(
        f"📢 Xabar yuborildi\n\n"
        f"✅ Yuborildi: {sent_count}\n"
        f"❌ Yuborilmadi: {failed_count}"
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz", show_alert=True)
        return

    total_users = await get_total_users()
    total_submissions = await get_total_submissions()
    today_submissions = await get_today_submissions()
    total_unique_submitters = await get_unique_submitters_count()
    today_unique_submitters = await get_today_unique_submitters_count()

    text = (
        "📊 Statistika\n\n"
        f"👥 Botga kirganlar: {total_users}\n"
        f"🖼 Jami screenshotlar: {total_submissions}\n"
        f"🙋 Screenshot yuborganlar: {total_unique_submitters}\n"
        f"📅 Bugun screenshotlar: {today_submissions}\n"
        f"✅ Bugun yuborganlar: {today_unique_submitters}"
    )

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "admin_today")
async def admin_today_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz", show_alert=True)
        return

    today_submissions = await get_today_submissions()
    today_unique_submitters = await get_today_unique_submitters_count()

    await callback.message.answer(
        "🖼 Bugungi natija\n\n"
        f"Jami screenshotlar: {today_submissions}\n"
        f"Yuborgan odamlar: {today_unique_submitters}"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_sent")
async def admin_sent_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz", show_alert=True)
        return

    text = await build_sent_users_text()

    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await callback.message.answer(text[i:i + 4000])
    else:
        await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data == "admin_not_sent")
async def admin_not_sent_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz", show_alert=True)
        return

    text = await build_not_sent_users_text()

    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await callback.message.answer(text[i:i + 4000])
    else:
        await callback.message.answer(text)

    await callback.answer()


@router.callback_query(F.data == "admin_send_now")
async def admin_send_now_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz", show_alert=True)
        return

    sent_count, failed_count = await send_sunday_reminder()
    await callback.message.answer(
        f"📢 Hammaga eslatma yuborildi\n\n"
        f"✅ Yuborildi: {sent_count}\n"
        f"❌ Yuborilmadi: {failed_count}"
    )
    await callback.answer("Yuborildi")


@router.message(F.photo)
async def photo_handler(message: Message):
    user = message.from_user
    photo = message.photo[-1]

    await save_submission(user_id=user.id, photo_file_id=photo.file_id)

    full_name = user.full_name if user.full_name else "Noma'lum"
    username = f"@{user.username}" if user.username else "yo'q"

    caption = (
        "📥 Yangi screenshot keldi\n\n"
        f"👤 Ismi: {full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"🔗 Username: {username}\n"
        f"🕒 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=caption
    )

    await message.answer("✅ Screenshot adminga yuborildi.")


async def main():
    await init_db()
    setup_scheduler()

    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())