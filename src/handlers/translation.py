import asyncio
import html
import time
from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from src.config import settings, PROVIDERS_INFO
from src.database.db import db_manager
from src.services.manager import translation_manager
from src.services.assistant import assistant_service
from src.services.providers.base import BaseTranslationProvider
from src.handlers.settings import SettingsStates
from src.utils.formatter import markdown_to_telegram_html

translation_router = Router(name="translation")


def _get_error_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Відкрити налаштування", callback_data="open_main_settings")]
        ]
    )


def _get_assistant_turn_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚡ Перекласти як є", callback_data="force_translate_draft"),
                InlineKeyboardButton(text="🗑️ Очистити пам'ять", callback_data="reset_assistant_memory"),
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
    is_assistant_mode: bool = False,
) -> None:
    """Core translation pipeline executing translation via chosen translator engine with back-translation verification in assistant mode."""
    provider_title = PROVIDERS_INFO.get(provider.name, {}).get("name", provider.name)
    direction_info = f"<i>({source_lang} ➔ {target_lang} via {provider_title})</i>"

    translated_text = ""

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

    else:
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

            translated_text = accumulated_text

            try:
                await stream_msg.delete()
            except Exception:
                pass

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
            return

    # In Assistant Mode: automatically perform back-translation verification into Ukrainian
    if is_assistant_mode and source_lang == "Ukrainian" and target_lang != "Ukrainian":
        back_translation = None
        try:
            back_translation = await provider.translate(
                text=translated_text,
                source_lang=target_lang,
                target_lang="Ukrainian",
                api_key=api_key,
            )
        except Exception:
            pass

        if back_translation:
            final_html = (
                f"<code>{html.escape(translated_text)}</code>\n\n"
                f"🔍 <b>Зворотний переклад (верифікація):</b>\n"
                f"<blockquote>{html.escape(back_translation)}</blockquote>"
            )
        else:
            final_html = f"<code>{html.escape(translated_text)}</code>"
    else:
        # Pure clean translation
        final_html = f"<code>{html.escape(translated_text)}</code>"

    await message.reply(final_html, parse_mode="HTML")


@translation_router.message(Command("reset"))
@translation_router.message(Command("clear"))
async def cmd_reset_assistant_memory(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db_manager.clear_assistant_history(message.from_user.id)
    await message.reply("🧹 <i>Assistant memory and conversation history cleared.</i>", parse_mode="HTML")


@translation_router.callback_query(F.data == "reset_assistant_memory")
async def callback_reset_assistant_memory(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await db_manager.clear_assistant_history(query.from_user.id)
    await query.message.edit_text("🧹 <i>Assistant memory reset. Starting fresh!</i>", parse_mode="HTML")
    await query.answer("Memory reset")


@translation_router.callback_query(F.data == "force_translate_draft")
async def callback_force_translate_draft(query: CallbackQuery, state: FSMContext) -> None:
    user_id = query.from_user.id
    history = await db_manager.get_assistant_history(user_id)
    user_settings = await db_manager.get_user_settings(user_id)

    last_user_text = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    if not last_user_text:
        await query.answer("No message in memory.")
        return

    provider = translation_manager.get_provider(user_settings.selected_provider)
    api_key = await db_manager.get_effective_api_key(user_id, user_settings.selected_provider)

    await query.message.edit_reply_markup(reply_markup=None)
    await query.answer()
    await _execute_translation(
        message=query.message,
        text_to_translate=last_user_text,
        source_lang="Ukrainian",
        target_lang=user_settings.target_language,
        provider=provider,
        api_key=api_key,
        is_assistant_mode=True,
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

    # --- Assistant Mode with Persistent Memory ---
    if user_settings.assistant_mode:
        assist_provider = user_settings.assistant_provider
        assist_key = await db_manager.get_effective_api_key(user_id, assist_provider)

        if assist_key:
            # 1. Add current turn to database memory
            await db_manager.add_assistant_message(user_id, "user", input_text)

            # 2. Retrieve conversation history within last 2 hours (up to 30 messages)
            history = await db_manager.get_assistant_history(user_id)

            status_msg = await message.reply("🧠 <i>Assistant is analyzing context...</i>", parse_mode="HTML")

            turn_result = await assistant_service.process_turn(
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

            if turn_result.status == "clarifying" and turn_result.assistant_message:
                # Save assistant reply to memory
                await db_manager.add_assistant_message(user_id, "assistant", turn_result.assistant_message)

                formatted_msg = markdown_to_telegram_html(turn_result.assistant_message)
                dialog_text = (
                    f"💡 <b>Асистент ({assist_provider}):</b>\n\n"
                    f"{formatted_msg}"
                )
                await message.reply(dialog_text, parse_mode="HTML", reply_markup=_get_assistant_turn_keyboard())
                return

            elif turn_result.status == "ready":
                # Approved text -> dispatch to chosen translator engine with back-translation verification
                final_source_text = turn_result.approved_source_text or input_text
                await _execute_translation(
                    message=message,
                    text_to_translate=final_source_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    provider=provider,
                    api_key=api_key,
                    is_assistant_mode=True,
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
        is_assistant_mode=False,
    )
