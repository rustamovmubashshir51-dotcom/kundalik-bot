from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    text="🖼 Bugungi screenshotlar",
                    callback_data="admin_today"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 Kimlar yubordi",
                    callback_data="admin_sent"
                ),
                InlineKeyboardButton(
                    text="❌ Kimlar yubormadi",
                    callback_data="admin_not_sent"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📢 Hammaga yuborish",
                    callback_data="admin_send_now"
                ),
            ],
        ]
    )