import html
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from src.config import settings, PROVIDERS_INFO, SUPPORTED_PROVIDERS
from src.database.db import db_manager
from src.keyboards.reply import get_main_reply_keyboard
from src.keyboards.inline import (
    get_settings_keyboard,
    get_providers_keyboard,
    get_api_keys_menu_keyboard,
    get_provider_key_action_keyboard,
    get_cancel_keyboard,
    get_mode_selection_keyboard,
    get_assistant_providers_keyboard,
)
from src.services.language_normalizer import language_normalizer

settings_router = Router(name="settings")


class SettingsStates(StatesGroup):
    waiting_for_target_language = State()
    waiting_for_api_key = State()


# --- Command Handlers ---

@settings_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)

    welcome_text = (
        "👋 <b>Ласкаво просимо до Telegram Translation Bot!</b>\n\n"
        "Цей бот забезпечує автоматичний двонаправлений переклад між <b>Українською</b> та будь-якою іншою мовою світу.\n\n"
        "⚡ <b>Як це працює:</b>\n"
        "• Надішліть текст <b>українською мовою</b> $\\rightarrow$ отримаєте переклад на вашу цільову мову.\n"
        "• Надішліть текст <b>іноземною мовою</b> $\\rightarrow$ мова визначиться автоматично і перекладеться на <b>українську</b>.\n"
        "• Усі переклади надсилаються у форматі <code>блоку коду</code> — просто натисніть на нього, щоб <b>миттєво скопіювати</b>!\n\n"
        "Натисніть <b>⚙️ Налаштування</b> на клавіатурі нижче, щоб налаштувати цільову мову, обрати рушій або режим асистента."
    )
    # First send welcome with persistent reply keyboard
    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(),
    )
    # Then show interactive settings inline keyboard
    await message.answer(
        "⚙️ <b>Меню швидких налаштувань:</b>",
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
        "📖 <b>Довідка та інструкція користування ботом</b>\n\n"
        "<b>Керування:</b>\n"
        "• Натисніть <b>⚙️ Налаштування</b> на клавіатурі нижче (або надішліть /settings)\n"
        "• Надішліть будь-який текст для миттєвого перекладу\n\n"
        "<b>Режими роботи:</b>\n"
        "• <b>⚡ Прямий переклад:</b> Миттєвий переклад у блок коду для копіювання в 1 клік.\n"
        "• <b>💡 Режим асистента:</b> Допомога у формуванні думок, з'ясуванні контексту та налаштуванні тону (нейтральний, діловий, погрозливий, іронічний) перед перекладом.\n\n"
        "<b>Підтримувані моделі:</b>\n"
        "• <b>DeepL (Standalone):</b> Еталонний нейронний переклад\n"
        "• <b>Gemini 3.5 Flash Lite:</b> Надшвидка легка модель Google\n"
        "• <b>Gemini 3.7 Flash:</b> Розумна модель нового покоління від Google\n"
        "• <b>OpenAI GPT-5.6 Luna:</b> Потужна модель від OpenAI\n"
        "• <b>DeepSeek V4 Flash:</b> Найновіша високоефективна модель DeepSeek\n\n"
        "<b>Копіювання в 1 клік:</b>\n"
        "Кожен переклад надсилається у <code>блоці коду</code>. Просто натисніть на нього, щоб скопіювати в буфер обміну!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_reply_keyboard())


@settings_router.message(Command("settings"))
@settings_router.message(F.text.in_({"⚙️ Settings", "⚙️ Налаштування", "Settings", "Налаштування"}))
async def cmd_settings(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)

    await message.answer(
        "⚙️ <b>Налаштування бота:</b>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )


# --- Callback Query Navigation Handlers ---

@settings_router.callback_query(F.data == "open_main_settings")
async def callback_open_main_settings(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)

    await query.message.edit_text(
        "⚙️ <b>Налаштування бота:</b>",
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
    try:
        await query.message.delete()
    except Exception:
        await query.message.edit_text("⚙️ <i>Налаштування закрито.</i>", parse_mode="HTML")
    await query.answer()


# --- Target Language Flow ---

@settings_router.callback_query(F.data == "set_target_language_prompt")
async def callback_set_target_language_prompt(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.waiting_for_target_language)
    text = (
        "🌐 <b>Зміна цільової мови перекладу</b>\n\n"
        "Напишіть або наговоріть будь-який текст із назвою мови.\n"
        "<i>Наприклад:</i>\n"
        "• <code>Португальська</code> або <code>хочу перекладати на португальську, європейський варіант</code>\n"
        "• <code>Німецька</code> або <code>зроби німецьку будь ласка</code>\n"
        "• <code>Spanish</code>, <code>pl</code>, <code>French</code>, <code>Italian</code>, <code>Japanese</code>\n\n"
        "Бот автоматично розпізнає та встановить точний код мови."
    )
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_cancel_keyboard())
    await query.answer()


@settings_router.message(SettingsStates.waiting_for_target_language)
async def process_target_language_input(message: Message, state: FSMContext) -> None:
    raw_input = message.text or ""
    user_id = message.from_user.id

    or_key = await db_manager.get_effective_api_key(user_id, "openrouter")

    # Smart extraction with DeepSeek V4 Flash
    lang_info = await language_normalizer.resolve_conversational_language(
        user_input=raw_input,
        openrouter_api_key=or_key,
    )

    canonical_name = lang_info.canonical_name if lang_info else language_normalizer.normalize(raw_input)
    await db_manager.set_target_language(user_id, canonical_name)
    await state.clear()

    user_settings = await db_manager.get_user_settings(user_id)
    deepl_note = f" (DeepL: <code>{lang_info.deepl_target_code}</code>)" if lang_info and lang_info.deepl_target_code else ""

    await message.reply(
        f"✅ Цільову мову успішно змінено на <b>{canonical_name}</b>{deepl_note}.",
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
        "🔄 <b>Оберіть режим перекладу</b>\n\n"
        "• <b>⚡ Прямий переклад:</b> Швидкий прямий переклад у блок коду для копіювання в 1 клік.\n"
        "• <b>💡 Режим асистента:</b> Допомога у формуванні думок, з'ясуванні контексту та налаштуванні тону перед перекладом."
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

    # Automatically wipe assistant session memory when user switches to direct translation
    if not is_assistant:
        await db_manager.clear_assistant_history(user_id)

    user_settings = await db_manager.get_user_settings(user_id)

    mode_title = "💡 Режим асистента" if is_assistant else "⚡ Прямий переклад"
    await query.message.edit_text(
        f"✅ Режим перекладу змінено на <b>{mode_title}</b>.",
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
        "🧠 <b>Оберіть модель асистента</b>\n\n"
        "Оберіть LLM модель, яка буде допомагати формувати думки та з'ясовувати контекст:"
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
        f"✅ Модель асистента встановлено на <b>{provider_title}</b>.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()


@settings_router.callback_query(F.data == "reset_assistant_memory_settings")
async def callback_reset_assistant_memory_settings(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    await db_manager.clear_assistant_history(user_id)
    await query.answer("🗑️ Пам'ять асистента успішно очищено!", show_alert=True)


# --- Translator Engine Selection ---

@settings_router.callback_query(F.data == "select_provider_menu")
async def callback_select_provider_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    user_settings = await db_manager.get_user_settings(user_id)
    text = (
        "🤖 <b>Оберіть активний перекладач</b>\n\n"
        "Оберіть рушій або модель, яка виконуватиме фінальний переклад:"
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
    user_id = query.from_user.id
    await db_manager.set_user_provider(user_id, provider)
    user_settings = await db_manager.get_user_settings(user_id)
    provider_title = PROVIDERS_INFO.get(provider, {}).get("name", provider)

    await query.message.edit_text(
        f"✅ Активний перекладач змінено на <b>{provider_title}</b>.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()


# --- API Key Management Flow ---

@settings_router.callback_query(F.data == "manage_api_keys_menu")
async def callback_manage_api_keys_menu(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user_id = query.from_user.id
    keys = await db_manager.get_all_user_api_keys(user_id)
    configured = {k: bool(v) for k, v in keys.items()}

    text = (
        "🔑 <b>Керування API ключами</b>\n\n"
        "Ви можете додати власні ключі для окремих моделей або використовувати системні за замовчуванням:"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_api_keys_menu_keyboard(configured),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("manage_key_for:"))
async def callback_manage_key_for(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    provider = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    custom_key = await db_manager.get_user_api_key(user_id, provider)
    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)

    if custom_key:
        masked = custom_key[:6] + "..." + custom_key[-4:] if len(custom_key) > 10 else "***"
        status_text = f"🟢 Власний ключ встановлено: <code>{masked}</code>"
    else:
        status_text = "⚪ Власний ключ не встановлено (використовується системний)."

    text = (
        f"🔑 <b>API ключ для {provider_title}</b>\n\n"
        f"Статус: {status_text}\n\n"
        f"Оберіть дію:"
    )
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_provider_key_action_keyboard(provider, bool(custom_key)),
    )
    await query.answer()


@settings_router.callback_query(F.data.startswith("input_key_for:"))
async def callback_input_key_for(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    await state.set_state(SettingsStates.waiting_for_api_key)
    await state.update_data(target_provider=provider)

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    text = (
        f"✏️ <b>Введіть ваш API ключ для {provider_title}</b>\n\n"
        f"🔒 <i>Повідомлення з вашим ключем буде негайно видалено з чату для безпеки.</i>"
    )
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=get_cancel_keyboard())
    await query.answer()


@settings_router.message(SettingsStates.waiting_for_api_key)
async def process_api_key_input(message: Message, state: FSMContext) -> None:
    raw_key = (message.text or "").strip()
    data = await state.get_data()
    provider = data.get("target_provider", "openrouter")
    user_id = message.from_user.id

    # Delete sensitive message immediately
    try:
        await message.delete()
    except Exception:
        pass

    if not raw_key:
        await state.clear()
        return

    await db_manager.set_user_api_key(user_id, provider, raw_key)
    await state.clear()

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    user_settings = await db_manager.get_user_settings(user_id)

    await message.answer(
        f"✅ API ключ для <b>{provider_title}</b> успішно збережено!",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )


@settings_router.callback_query(F.data.startswith("delete_key_for:"))
async def callback_delete_key_for(query: CallbackQuery, state: FSMContext) -> None:
    provider = query.data.split(":", 1)[1]
    user_id = query.from_user.id
    await db_manager.delete_user_api_key(user_id, provider)

    provider_title = "OpenRouter" if provider == "openrouter" else PROVIDERS_INFO.get(provider, {}).get("name", provider)
    user_settings = await db_manager.get_user_settings(user_id)

    await query.message.edit_text(
        f"🗑️ Власний API ключ для <b>{provider_title}</b> видалено.",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(
            user_settings.target_language,
            user_settings.selected_provider,
            user_settings.assistant_mode,
            user_settings.assistant_provider,
        ),
    )
    await query.answer()
