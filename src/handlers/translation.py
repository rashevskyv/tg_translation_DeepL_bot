import asyncio
import html
import time
from typing import Optional
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from src.config import settings, PROVIDERS_INFO
from src.database.db import db_manager
from src.services.manager import translation_manager
from src.services.assistant import assistant_service
from src.services.providers.base import BaseTranslationProvider
from src.handlers.settings import SettingsStates

translation_router = Router(name="translation")


def _get_error_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Open Settings", callback_data="open_main_settings")]
        ]
    )


def _get_clarification_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Translate As Is", callback_data="force_translate_original"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_assistant_dialog"),
            ]
        ]
    )


async def _execute_translation(
    message: Message,
    text_to_translate: str,
    source_lang: str,
    target_lang: str,
    provider: BaseTranslationProvider,
    api_key: str,
) -> None:
    """Core translation pipeline executing translation via chosen translator engine."""
    provider_title = PROVIDERS_INFO.get(provider.name, {}).get("name", provider.name)
    direction_info = f"<i>({source_lang} ➔ {target_lang} via {provider_title})</i>"

    # DeepL or Non-streaming mode
    if not provider.supports_streaming:
        status_msg = await message.reply(
            f"⏳ <b>Translating...</b> {direction_info}",
            parse_mode="HTML",
        )
        try:
            translated_text = await provider.translate(
                text=text_to_translate,
                source_lang=source_lang,
                target_lang=target_lang,
                api_key=api_key,
            )
        except Exception as e:
            await status_msg.edit_text(
                f"❌ <b>Translation failed:</b>\n{html.escape(str(e))}",
                parse_mode="HTML",
                reply_markup=_get_error_settings_keyboard(),
            )
            return

        try:
            await status_msg.delete()
        except Exception:
            pass

        final_html = f"<code>{html.escape(translated_text)}</code>"
        await message.reply(final_html, parse_mode="HTML")
        return

    # Streaming mode for LLM providers
    stream_msg = await message.reply(
        f"⏳ <i>Translating stream via {provider_title}...</i>",
        parse_mode="HTML",
    )

    accumulated_text = ""
    last_update_time = time.time()
    update_interval = settings.stream_chunk_interval

    try:
        async for chunk in provider.translate_stream(
            text=text_to_translate,
            source_lang=source_lang,
            target_lang=target_lang,
            api_key=api_key,
        ):
            accumulated_text += chunk
            current_time = time.time()

            if current_time - last_update_time >= update_interval and accumulated_text.strip():
                try:
                    display_chunk = accumulated_text[:4000]
                    await stream_msg.edit_text(
                        f"<i>Translating ({source_lang} ➔ {target_lang})...</i>\n\n{html.escape(display_chunk)}",
                        parse_mode="HTML",
                    )
                    last_update_time = current_time
                except TelegramRetryAfter as retry_err:
                    await asyncio.sleep(retry_err.retry_after)
                except TelegramBadRequest:
                    pass

        if not accumulated_text.strip():
            accumulated_text = await provider.translate(
                text=text_to_translate,
                source_lang=source_lang,
                target_lang=target_lang,
                api_key=api_key,
            )

        try:
            await stream_msg.delete()
        except Exception:
            pass

        final_html = f"<code>{html.escape(accumulated_text)}</code>"
        await message.reply(final_html, parse_mode="HTML")

    except Exception as e:
        try:
            await stream_msg.edit_text(
                f"❌ <b>Translation failed:</b>\n{html.escape(str(e))}",
                parse_mode="HTML",
                reply_markup=_get_error_settings_keyboard(),
            )
        except Exception:
            await message.reply(
                f"❌ <b>Translation failed:</b>\n{html.escape(str(e))}",
                parse_mode="HTML",
                reply_markup=_get_error_settings_keyboard(),
            )


@translation_router.callback_query(F.data == "force_translate_original")
async def callback_force_translate_original(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    original_text = data.get("original_text")
    source_lang = data.get("source_lang", "Ukrainian")
    target_lang = data.get("target_lang", "English")
    provider_name = data.get("provider_name", "deepl")
    user_id = query.from_user.id

    if not original_text:
        await query.answer("No active text.")
        return

    provider = translation_manager.get_provider(provider_name)
    api_key = await db_manager.get_effective_api_key(user_id, provider_name)

    await query.message.edit_reply_markup(reply_markup=None)
    await query.answer()
    await _execute_translation(query.message, original_text, source_lang, target_lang, provider, api_key)


@translation_router.callback_query(F.data == "cancel_assistant_dialog")
async def callback_cancel_assistant_dialog(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.edit_text("❌ <i>Clarification dialog cancelled.</i>", parse_mode="HTML")
    await query.answer()


@translation_router.message(SettingsStates.waiting_for_clarification)
async def handle_clarification_response(message: Message, state: FSMContext) -> None:
    """Handles multi-turn dialogue with the user until intent is agreed upon."""
    user_reply = message.text.strip() if message.text else ""
    if not user_reply:
        return

    data = await state.get_data()
    history = data.get("history", [])
    original_text = data.get("original_text")
    source_lang = data.get("source_lang", "Ukrainian")
    target_lang = data.get("target_lang", "English")
    provider_name = data.get("provider_name", "deepl")
    assist_provider = data.get("assist_provider", "gemini_flash")
    user_id = message.from_user.id

    assist_key = await db_manager.get_effective_api_key(user_id, assist_provider)
    trans_key = await db_manager.get_effective_api_key(user_id, provider_name)
    trans_provider = translation_manager.get_provider(provider_name)

    # Append user turn to conversation history
    history.append({"role": "user", "content": user_reply})

    status_msg = await message.reply("🧠 <i>Analyzing clarification...</i>", parse_mode="HTML")

    result = await assistant_service.process_turn(
        conversation_history=history,
        source_lang=source_lang,
        target_lang=target_lang,
        provider_name=assist_provider,
        api_key=assist_key,
    )

    try:
        await status_msg.delete()
    except Exception:
        pass

    if result.status == "clarifying" and result.assistant_message:
        # Continue dialogue
        history.append({"role": "assistant", "content": result.assistant_message})
        await state.update_data(history=history)

        dialog_text = (
            f"💡 <b>Асистент ({assist_provider}):</b>\n\n"
            f"{html.escape(result.assistant_message)}"
        )
        await message.reply(dialog_text, parse_mode="HTML", reply_markup=_get_clarification_keyboard())
    else:
        # All agreed -> proceed to translation engine
        await state.clear()
        final_source_text = result.approved_source_text or original_text
        await _execute_translation(
            message=message,
            text_to_translate=final_source_text,
            source_lang=source_lang,
            target_lang=target_lang,
            provider=trans_provider,
            api_key=trans_key,
        )


@translation_router.message(F.text & ~F.text.startswith("/"))
async def handle_translation_text(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state in (
        SettingsStates.waiting_for_target_language.state,
        SettingsStates.waiting_for_api_key.state,
    ):
        return

    user_id = message.from_user.id
    input_text = message.text.strip()
    if not input_text:
        return

    user_settings = await db_manager.get_user_settings(user_id)

    # Prepare translation metadata
    try:
        provider, api_key, source_lang, target_lang = await translation_manager.prepare_translation(
            user_id, input_text
        )
    except ValueError as val_err:
        await message.reply(
            f"⚠️ <b>Configuration Required:</b>\n\n{html.escape(str(val_err))}",
            parse_mode="HTML",
            reply_markup=_get_error_settings_keyboard(),
        )
        return
    except Exception as e:
        await message.reply(f"⚠️ Error preparing translation: {html.escape(str(e))}")
        return

    # --- Assistant Mode Check ---
    if user_settings.assistant_mode:
        assist_provider = user_settings.assistant_provider
        assist_key = await db_manager.get_effective_api_key(user_id, assist_provider)

        if assist_key:
            status_msg = await message.reply("🧠 <i>Analyzing nuance & intent...</i>", parse_mode="HTML")
            initial_history = [{"role": "user", "content": input_text}]

            turn_result = await assistant_service.process_turn(
                conversation_history=initial_history,
                source_lang=source_lang,
                target_lang=target_lang,
                provider_name=assist_provider,
                api_key=assist_key,
            )

            try:
                await status_msg.delete()
            except Exception:
                pass

            if turn_result.status == "clarifying" and turn_result.assistant_message:
                # Enter clarification conversation state
                initial_history.append({"role": "assistant", "content": turn_result.assistant_message})
                await state.set_state(SettingsStates.waiting_for_clarification)
                await state.update_data(
                    history=initial_history,
                    original_text=input_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    provider_name=provider.name,
                    assist_provider=assist_provider,
                )
                dialog_text = (
                    f"💡 <b>Потрібне уточнення ({source_lang} ➔ {target_lang}):</b>\n\n"
                    f"{html.escape(turn_result.assistant_message)}\n\n"
                    f"<i>✍️ Напишіть відповідь для узгодження змісту або оберіть дію:</i>"
                )
                await message.reply(dialog_text, parse_mode="HTML", reply_markup=_get_clarification_keyboard())
                return
            elif turn_result.status == "ready":
                # Clear and unambiguous -> send directly to translator engine
                final_source_text = turn_result.approved_source_text or input_text
                await _execute_translation(
                    message=message,
                    text_to_translate=final_source_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    provider=provider,
                    api_key=api_key,
                )
                return

    # Direct Mode: execute translation directly
    await _execute_translation(
        message=message,
        text_to_translate=input_text,
        source_lang=source_lang,
        target_lang=target_lang,
        provider=provider,
        api_key=api_key,
    )
