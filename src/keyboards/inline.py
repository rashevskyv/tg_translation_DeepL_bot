from typing import Dict
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.config import PROVIDERS_INFO, SUPPORTED_PROVIDERS


def get_settings_keyboard(current_target: str, current_provider: str) -> InlineKeyboardMarkup:
    provider_title = PROVIDERS_INFO.get(current_provider, {}).get("name", current_provider.upper())
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"🌐 Target Language: {current_target}",
                callback_data="set_target_language_prompt",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"🤖 Active Engine: {provider_title}",
                callback_data="select_provider_menu",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔑 Manage API Keys (DeepL & OpenRouter)",
                callback_data="manage_api_keys_menu",
            )
        ],
        [
            InlineKeyboardButton(
                text="✖️ Close",
                callback_data="close_settings",
            )
        ],
    ]
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
        InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="open_main_settings")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_api_keys_menu_keyboard(configured_keys: Dict[str, bool]) -> InlineKeyboardMarkup:
    # 1. DeepL Key
    deepl_status = "🟢 Custom Key Set" if configured_keys.get("deepl") else "⚪ Not Set / Env Default"
    # 2. OpenRouter Key (Universal)
    openrouter_status = "🟢 Custom Key Set" if configured_keys.get("openrouter") else "⚪ Not Set / Env Default"

    keyboard = [
        [
            InlineKeyboardButton(
                text=f"DeepL API Key ({deepl_status})",
                callback_data="manage_key_for:deepl",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"OpenRouter API Key ({openrouter_status})",
                callback_data="manage_key_for:openrouter",
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="open_main_settings")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_provider_key_action_keyboard(provider: str, has_custom_key: bool) -> InlineKeyboardMarkup:
    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    keyboard = [
        [
            InlineKeyboardButton(
                text="✏️ Enter / Replace API Key",
                callback_data=f"input_key_for:{provider}",
            )
        ]
    ]
    if has_custom_key:
        keyboard.append([
            InlineKeyboardButton(
                text="🗑️ Delete Custom Key",
                callback_data=f"delete_key_for:{provider}",
            )
        ])
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Back to Keys Menu",
            callback_data="manage_api_keys_menu",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="open_main_settings")]
        ]
    )
