from typing import Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import PROVIDERS_INFO, SUPPORTED_PROVIDERS


def get_settings_keyboard(
    current_target: str,
    current_provider: str,
    assistant_mode: bool = False,
    assistant_provider: str = "gemini_flash",
) -> InlineKeyboardMarkup:
    provider_title = PROVIDERS_INFO.get(current_provider, {}).get("name", current_provider.upper())
    assistant_title = PROVIDERS_INFO.get(assistant_provider, {}).get("name", assistant_provider)
    mode_text = "💡 Режим асистента" if assistant_mode else "⚡ Прямий переклад"

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"🌐 Цільова мова: {current_target}",
                callback_data="set_target_language_prompt",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"🤖 Перекладач: {provider_title}",
                callback_data="select_provider_menu",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"🔄 Режим: {mode_text}",
                callback_data="toggle_mode_menu",
            )
        ],
    ]

    if assistant_mode:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🧠 Модель асистента: {assistant_title}",
                callback_data="select_assistant_provider_menu",
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text="🗑️ Скинути пам'ять",
                callback_data="reset_assistant_memory_settings",
            )
        ])

    keyboard.extend([
        [
            InlineKeyboardButton(
                text="🔑 Керування API ключами",
                callback_data="manage_api_keys_menu",
            )
        ],
        [
            InlineKeyboardButton(
                text="✖️ Закрити",
                callback_data="close_settings",
            )
        ],
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_mode_selection_keyboard(current_assistant_mode: bool) -> InlineKeyboardMarkup:
    direct_mark = "✅ " if not current_assistant_mode else ""
    assist_mark = "✅ " if current_assistant_mode else ""
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{direct_mark}⚡ Прямий переклад",
                callback_data="set_mode:direct",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{assist_mark}💡 Режим асистента (допомога та діалог)",
                callback_data="set_mode:assistant",
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад до налаштувань", callback_data="open_main_settings")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_assistant_providers_keyboard(current_provider: str) -> InlineKeyboardMarkup:
    keyboard = []
    # Only LLM providers suitable for assistant
    llm_providers = [p for p in SUPPORTED_PROVIDERS if p != "deepl"]
    for prov_key in llm_providers:
        info = PROVIDERS_INFO.get(prov_key, {})
        title = info.get("name", prov_key)
        mark = "✅ " if prov_key == current_provider else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{mark}{title}",
                callback_data=f"choose_assistant_provider:{prov_key}",
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад до налаштувань", callback_data="open_main_settings")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_providers_keyboard(current_provider: str) -> InlineKeyboardMarkup:
    keyboard = []
    for prov_key in SUPPORTED_PROVIDERS:
        info = PROVIDERS_INFO.get(prov_key, {})
        title = info.get("name", prov_key)
        mark = "✅ " if prov_key == current_provider else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{mark}{title}",
                callback_data=f"choose_provider:{prov_key}",
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад до налаштувань", callback_data="open_main_settings")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_api_keys_menu_keyboard(configured_keys: Dict[str, bool]) -> InlineKeyboardMarkup:
    deepl_status = "🟢 Власний ключ" if configured_keys.get("deepl") else "⚪ Не встановлено"
    openrouter_status = "🟢 Власний ключ" if configured_keys.get("openrouter") else "⚪ Не встановлено"

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"Ключ DeepL API ({deepl_status})",
                callback_data="manage_key_for:deepl",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"Ключ OpenRouter API ({openrouter_status})",
                callback_data="manage_key_for:openrouter",
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад до налаштувань", callback_data="open_main_settings")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_provider_key_action_keyboard(provider: str, has_custom_key: bool) -> InlineKeyboardMarkup:
    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    keyboard = [
        [
            InlineKeyboardButton(
                text="✏️ Ввести / Замінити API ключ",
                callback_data=f"input_key_for:{provider}",
            )
        ]
    ]
    if has_custom_key:
        keyboard.append([
            InlineKeyboardButton(
                text="🗑️ Видалити власний ключ",
                callback_data=f"delete_key_for:{provider}",
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад до меню ключів",
            callback_data="manage_api_keys_menu",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="open_main_settings")]
        ]
    )
