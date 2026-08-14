from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Persistent bottom keyboard providing quick access to settings and help.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⚙️ Settings"),
                KeyboardButton(text="ℹ️ Help"),
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Send text to translate or tap ⚙️ Settings...",
    )
