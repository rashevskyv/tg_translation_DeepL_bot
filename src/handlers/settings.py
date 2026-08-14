from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from src.config import settings, PROVIDERS_INFO, SUPPORTED_PROVIDERS
from src.database.db import db_manager, VALID_KEY_PROVIDERS
from src.services.language_normalizer import normalize_language
from src.keyboards.inline import (
    get_settings_keyboard,
    get_providers_keyboard,
    get_mode_selection_keyboard,
    get_assistant_providers_keyboard,
    get_api_keys_menu_keyboard,
    get_provider_key_action_keyboard,
    get_cancel_keyboard,
)
from src.keyboards.reply import get_main_reply_keyboard

settings_router = Router(name="settings")


class SettingsStates(StatesGroup):
    waiting_for_target_language = State()
    waiting_for_api_key = State()
    waiting_for_clarification = State()


@settings_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    provider_title = PROVIDERS_INFO.get(user_settings.selected_provider, {}).get("name", user_settings.selected_provider)
    mode_text = "💡 Assistant Mode" if user_settings.assistant_mode else "⚡ Direct Translation"

    welcome_text = (
        "👋 <b>Welcome to Translation Bot!</b>\n\n"
        "⚡ <b>How it works:</b>\n"
        "• Send text in <b>Ukrainian</b> ➔ Automatically translates into your chosen <b>Target Language</b>.\n"
        "• Send text in <b>Any other language</b> ➔ Automatically detects source language and translates into <b>Ukrainian</b>.\n\n"
        f"⚙️ <b>Current Settings:</b>\n"
        f"• Mode: <code>{mode_text}</code>\n"
        f"• Target Language: <code>{user_settings.target_language}</code>\n"
        f"• Translator Engine: <code>{provider_title}</code>\n\n"
        "Tap <b>⚙️ Settings</b> on the bottom keyboard or use /settings to configure options."
    )
    # First, send welcome with permanent reply keyboard attached
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(),
    )
    # Then show interactive settings inline keyboard
    await message.answer(
        "⚙️ <b>Quick Configuration Menu:</b>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )


@settings_router.message(Command("help"))
@settings_router.message(F.text.in_({"ℹ️ Help", "ℹ️ Допомога", "Help", "Допомога"}))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    help_text = (
        "📖 <b>Translation Bot Help & Usage</b>\n\n"
        "<b>Navigation & Controls:</b>\n"
        "• Tap <b>⚙️ Settings</b> on the keyboard below (or send /settings)\n"
        "• Send any text to immediately receive a translation\n\n"
        "<b>Translation Modes:</b>\n"
        "• <b>⚡ Direct Translation:</b> Fast, instant, clean code translation without interruptions.\n"
        "• <b>💡 Assistant Mode:</b> If your message is ambiguous or context is unclear, the assistant will ask clarification questions first, then give the exact translated result.\n\n"
        "<b>Supported Engines:</b>\n"
        "• <b>DeepL (Standalone):</b> High precision neural translation\n"
        "• <b>Gemini 3.5 Flash Lite:</b> Ultra-fast translation via OpenRouter\n"
        "• <b>Gemini 3.7 Flash:</b> High intelligence translation via OpenRouter\n"
        "• <b>OpenAI GPT-5.6 Luna:</b> State-of-the-art GPT translation via OpenRouter\n"
        "• <b>DeepSeek V4 Flash:</b> High efficiency translation via OpenRouter\n\n"
        "<b>One-Click Copy:</b>\n"
        "Every translation is sent in a <code>monospace box</code>. Simply tap/click on it to instantly copy it to your clipboard!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())


@settings_router.message(Command("settings"))
@settings_router.message(F.text.in_({"⚙️ Settings", "⚙️ Налаштування", "Settings", "Налаштування"}))
async def cmd_settings(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "⚙️ <b>Bot Settings Menu</b>\n\n"
        "Choose an option below to customize your translation preferences:"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )


@settings_router.callback_query(F.data == "open_main_settings")
async def callback_open_main_settings(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "⚙️ <b>Bot Settings Menu</b>\n\n"
        "Choose an option below to customize your translation preferences:"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()


@settings_router.callback_query(F.data == "close_settings")
async def callback_close_settings(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.delete()
    await query.answer("Settings closed.")


# --- Target Language Selection ---

@settings_router.callback_query(F.data == "set_target_language_prompt")
async def callback_set_target_language(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_for_target_language)
    prompt_text = (
        "🌐 <b>Set Target Translation Language</b>\n\n"
        "Please type the name or code of the language (or describe your request):\n"
        "<i>(e.g., 'Португальська', 'хочу німецьку', 'American English', 'pl', 'de')</i>"
    )
    await query.message.edit_text(
        prompt_text,
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )
    await query.answer()


@settings_router.message(SettingsStates.waiting_for_target_language)
async def process_target_language_input(message: Message, state: FSMContext) -> None:
    raw_lang = message.text.strip() if message.text else ""
    if not raw_lang or len(raw_lang) < 2 or len(raw_lang) > 250:
        await message.answer(
            "⚠️ Invalid language name or description. Please type a language or phrase (e.g., 'Португальська', 'хочу німецьку', 'American English', 'pl').",
            reply_markup=get_cancel_keyboard(),
        )
        return

    user_id = message.from_user.id
    openrouter_key = await db_manager.get_effective_api_key(user_id, "openrouter")
    lang_info = await normalize_language(raw_lang, openrouter_api_key=openrouter_key)
    
    await db_manager.set_target_language(user_id, lang_info.canonical_name)
    await state.clear()

    user_settings = await db_manager.get_user_settings(user_id)
    
    if lang_info.deepl_target_code:
        lang_note = f"<code>{lang_info.canonical_name}</code> <i>(DeepL Code: <code>{lang_info.deepl_target_code}</code>)</i>"
    else:
        lang_note = (
            f"<code>{lang_info.canonical_name}</code>\n"
            f"<i>ℹ️ Note: Supported via OpenRouter models (Gemini/GPT/DeepSeek). (Not available in DeepL).</i>"
        )

    await message.answer(
        f"✅ <b>Target language successfully updated to:</b>\n{lang_note}",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )


# --- Mode Selection (Direct vs Assistant) ---

@settings_router.callback_query(F.data == "toggle_mode_menu")
async def callback_toggle_mode_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "🔄 <b>Select Translation Mode</b>\n\n"
        "• <b>⚡ Direct Translation:</b> Fast, instant translation into code block without interruption.\n"
        "• <b>💡 Assistant Mode:</b> The bot analyzes intent. If meaning or tone is ambiguous, it clarifies first, then outputs a high-accuracy styled translation."
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_mode_selection_keyboard(user_settings.assistant_mode),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("set_mode:"))
async def callback_set_mode(query: CallbackQuery, state: FSMContext) -> None:
    mode = query.data.split(":", 1)[1]
    is_assistant = (mode == "assistant")
    user_id = query.from_user.id
    await db_manager.set_assistant_mode(user_id, is_assistant)
    user_settings = await db_manager.get_user_settings(user_id)

    mode_title = "💡 Assistant Mode" if is_assistant else "⚡ Direct Translation"
    await query.message.edit_text(
        f"✅ Translation mode updated to <b>{mode_title}</b>.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()


# --- Assistant Model Selection ---

@settings_router.callback_query(F.data == "select_assistant_provider_menu")
async def callback_select_assistant_provider_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "🧠 <b>Select Assistant Model</b>\n\n"
        "Choose which LLM will perform intent analysis and clarification questions:"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_assistant_providers_keyboard(user_settings.assistant_provider),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("choose_assistant_provider:"))
async def callback_choose_assistant_provider(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    await db_manager.set_assistant_provider(user_id, provider)
    user_settings = await db_manager.get_user_settings(user_id)
    provider_title = PROVIDERS_INFO.get(provider, {}).get("name", provider)

    await query.message.edit_text(
        f"✅ Assistant Engine set to <b>{provider_title}</b>.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()


# --- Translator Engine Selection ---

@settings_router.callback_query(F.data == "select_provider_menu")
async def callback_select_provider_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "🤖 <b>Select Active Translation Engine</b>\n\n"
        "Choose which provider/model will process your translation requests:\n"
        "<i>(All LLM models run in fast Non-Thinking mode)</i>"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_providers_keyboard(user_settings.selected_provider),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("choose_provider:"))
async def callback_choose_provider(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    if provider in SUPPORTED_PROVIDERS:
        user_id = query.from_user.id
        await db_manager.set_user_provider(user_id, provider)
        user_settings = await db_manager.get_user_settings(user_id)
        provider_title = PROVIDERS_INFO.get(provider, {}).get("name", provider)

        key_req = "DeepL API Key" if provider == "deepl" else "OpenRouter API Key"
        await query.message.edit_text(
            f"✅ Translator engine set to <b>{provider_title}</b>.\n\n"
            f"Note: Ensure you have an API key configured for {key_req} via 'Manage API Keys' or server environment.",
            parse_mode="HTML",
            reply_markup=get_settings_keyboard(
                user_settings.target_language,
                user_settings.selected_provider,
                user_settings.assistant_mode,
                user_settings.assistant_provider,
            ),
        )
    await query.answer()


# --- API Keys Management ---

@settings_router.callback_query(F.data == "manage_api_keys_menu")
async def callback_manage_api_keys_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    custom_keys = await db_manager.get_all_user_api_keys(user_id)
    configured_map = {
        "deepl": bool(custom_keys.get("deepl")),
        "openrouter": bool(custom_keys.get("openrouter")),
    }

    text = (
        "🔑 <b>API Keys Management (Per-User Storage)</b>\n\n"
        "Your API keys are stored securely and privately in the local database.\n\n"
        "• <b>DeepL API Key:</b> Used for standalone DeepL translation.\n"
        "• <b>OpenRouter API Key:</b> Universal key unlocking Gemini 3.5, Gemini 3.7, GPT-5.6 Luna, and DeepSeek V4."
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_api_keys_menu_keyboard(configured_map),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("manage_key_for:"))
async def callback_manage_key_for_provider(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    custom_key = await db_manager.get_user_api_key(user_id, provider)
    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)

    if custom_key:
        masked_key = custom_key[:4] + "..." + custom_key[-4:] if len(custom_key) > 8 else "***"
        status_msg = f"🟢 <b>Status:</b> Custom API Key is active (<code>{masked_key}</code>)"
    else:
        status_msg = "⚪ <b>Status:</b> No custom API key set (using server default if available)."

    extra_desc = ""
    if provider == "openrouter":
        extra_desc = "<i>💡 This single OpenRouter key powers all 4 smart LLM models (Gemini, GPT Luna, DeepSeek).</i>\n\n"

    text = (
        f"🔑 <b>{provider_title} API Key</b>\n\n"
        f"{extra_desc}"
        f"{status_msg}\n\n"
        "Choose an action:"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_provider_key_action_keyboard(provider, bool(custom_key)),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("input_key_for:"))
async def callback_input_key_for_provider(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    await state.set_state(SettingsStates.waiting_for_api_key)
    await state.update_data(target_provider=provider)

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    text = (
        f"✏️ <b>Enter your {provider_title} API Key:</b>\n\n"
        "Send your API key as a text message.\n"
        "<i>🔒 For your security, your message containing the API key will be immediately deleted from chat after saving.</i>"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )
    await query.answer()


@settings_router.message(SettingsStates.waiting_for_api_key)
async def process_api_key_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    provider = data.get("target_provider")
    api_key = message.text.strip() if message.text else ""

    # Delete the user's message containing sensitive key immediately
    try:
        await message.delete()
    except Exception:
        pass

    valid_keys = SUPPORTED_PROVIDERS + ["openrouter"]
    if not provider or provider not in valid_keys or not api_key:
        await state.clear()
        await message.answer("⚠️ Failed to set API key. Please try again from /settings.")
        return

    user_id = message.from_user.id
    await db_manager.set_user_api_key(user_id, provider, api_key)
    await state.clear()

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"

    await message.answer(
        f"✅ <b>{provider_title} API Key saved successfully!</b> (<code>{masked_key}</code>)\n"
        "Your key is active for your future translations.",
        parse_mode="HTML",
        reply_markup=get_provider_key_action_keyboard(provider, True),
    )


@settings_router.callback_query(F.data.startswith("delete_key_for:"))
async def callback_delete_key_for_provider(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    await db_manager.delete_user_api_key(user_id, provider)

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    await query.message.edit_text(
        f"🗑️ Custom API Key for <b>{provider_title}</b> has been deleted.\n"
        f"The bot will now use the server default key (if available).",
        parse_mode="HTML",
        reply_markup=get_provider_key_action_keyboard(provider, False),
    )
    await query.answer("Key deleted.")


# --- Admin Commands (Assign key to specific user) ---

def _is_admin(user_id: int) -> bool:
    if not settings.admin_user_ids:
        return False
    admin_ids = [aid.strip() for aid in settings.admin_user_ids.split(",") if aid.strip()]
    return str(user_id) in admin_ids


@settings_router.message(Command("assign_key"))
async def cmd_assign_key(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    try:
        await message.delete()
    except Exception:
        pass

    args = message.text.split()[1:] if message.text else []
    if len(args) != 3:
        await message.answer(
            "⚠️ <b>Usage:</b> <code>/assign_key &lt;user_id&gt; &lt;deepl|openrouter&gt; &lt;api_key&gt;</code>",
            parse_mode="HTML",
        )
        return

    try:
        target_uid = int(args[0])
    except ValueError:
        await message.answer("⚠️ Invalid user ID format.")
        return

    provider = args[1].lower()
    api_key = args[2].strip()

    if provider not in VALID_KEY_PROVIDERS:
        await message.answer(f"⚠️ Invalid provider. Supported: {', '.join(VALID_KEY_PROVIDERS)}")
        return

    await db_manager.set_user_api_key(target_uid, provider, api_key)
    masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
    await message.answer(
        f"👑 <b>Admin Action:</b>\n"
        f"Key for <b>{provider}</b> assigned to User ID <code>{target_uid}</code>: <code>{masked}</code>",
        parse_mode="HTML",
    )


@settings_router.message(Command("user_info"))
async def cmd_user_info(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("⚠️ <b>Usage:</b> <code>/user_info &lt;user_id&gt;</code>", parse_mode="HTML")
        return

    try:
        target_uid = int(args[0])
    except ValueError:
        await message.answer("⚠️ Invalid user ID.")
        return

    user_settings = await db_manager.get_user_settings(target_uid)
    custom_keys = await db_manager.get_all_user_api_keys(target_uid)
    keys_str = "\n".join(f"• <b>{k}</b>: <code>{v[:4]}...{v[-4:]}</code>" for k, v in custom_keys.items()) if custom_keys else "<i>None set (using fallback)</i>"

    mode_text = "💡 Assistant Mode" if user_settings.assistant_mode else "⚡ Direct Translation"
    await message.answer(
        f"👤 <b>User Info (ID: <code>{target_uid}</code>):</b>\n\n"
        f"• Mode: <code>{mode_text}</code>\n"
        f"• Target Language: <code>{user_settings.target_language}</code>\n"
        f"• Translator Provider: <code>{user_settings.selected_provider}</code>\n"
        f"• Assistant Provider: <code>{user_settings.assistant_provider}</code>\n\n"
        f"<b>Configured Custom Keys:</b>\n{keys_str}",
        parse_mode="HTML",
    )
