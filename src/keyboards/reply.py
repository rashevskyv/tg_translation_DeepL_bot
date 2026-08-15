from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Persistent bottom keyboard providing quick access to settings and help in Ukrainian.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⚙️ Налаштування"),
                KeyboardButton(text="ℹ️ Допомога"),
            ]
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Введіть текст для перекладу або натисніть ⚙️ Налаштування...",
    )
