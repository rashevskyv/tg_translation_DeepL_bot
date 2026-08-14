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
                text="🔑 Manage API Keys",
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


def get_api_keys_menu_keyboard(configured_providers: Dict[str, bool]) -> InlineKeyboardMarkup:
    keyboard = []
    for prov_key in SUPPORTED_PROVIDERS:
        info = PROVIDERS_INFO.get(prov_key, {})
        title = info.get("name", prov_key)
        status_icon = "🟢 Custom Key" if configured_providers.get(prov_key) else "⚪ Not Set / Env Default"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{title} ({status_icon})",
                callback_data=f"manage_key_for:{prov_key}",
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Back to Settings", callback_data="open_main_settings")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_provider_key_action_keyboard(provider: str, has_custom_key: bool) -> InlineKeyboardMarkup:
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
