from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="stats")
        ],

        [
            InlineKeyboardButton(text="👥 Yuborganlar", callback_data="sent")
        ],

        [
            InlineKeyboardButton(text="❌ Yubormaganlar", callback_data="not_sent")
        ],

        [
            InlineKeyboardButton(text="📢 Hammaga yuborish", callback_data="send_all")
        ]
    ]
)
