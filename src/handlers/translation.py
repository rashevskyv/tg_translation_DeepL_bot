import asyncio
import html
import time
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from src.config import settings, PROVIDERS_INFO
from src.database.db import db_manager
from src.services.manager import translation_manager
from src.services.assistant import assistant_service
from src.handlers.settings import SettingsStates

translation_router = Router(name="translation")


def _get_error_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Open Settings", callback_data="open_main_settings")]
        ]
    )


@translation_router.message(SettingsStates.waiting_for_clarification)
async def handle_clarification_response(message: Message, state: FSMContext) -> None:
    """Handles the user's response to an assistant clarification question."""
    data = await state.get_data()
    original_text = data.get("original_text")
    source_lang = data.get("source_lang", "Ukrainian")
    target_lang = data.get("target_lang", "English")
    assistant_provider = data.get("assistant_provider", "gemini_flash")
    user_clarification = message.text.strip() if message.text else ""

    if not original_text or not user_clarification:
        await state.clear()
        return

    user_id = message.from_user.id
    api_key = await db_manager.get_effective_api_key(user_id, assistant_provider)

    status_msg = await message.reply(
        "⏳ <i>Formulating clarified translation...</i>",
        parse_mode="HTML",
    )

    try:
        translated_text = await assistant_service.finalize_clarified_translation(
            original_text=original_text,
            user_clarification=user_clarification,
            source_lang=source_lang,
            target_lang=target_lang,
            provider_name=assistant_provider,
            api_key=api_key,
        )

        try:
            await status_msg.delete()
        except Exception:
            pass

        final_html = f"<code>{html.escape(translated_text)}</code>"
        await message.reply(final_html, parse_mode="HTML")
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>Translation failed:</b>\n{html.escape(str(e))}",
            parse_mode="HTML",
            reply_markup=_get_error_settings_keyboard(),
        )
    finally:
        await state.clear()


@translation_router.message(F.text & ~F.text.startswith("/"))
async def handle_translation_text(message: Message, state: FSMContext) -> None:
    # If state is waiting for language/key, let settings handlers handle it
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

    # Prepare translation metadata (direction, provider, keys)
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
            status_msg = await message.reply(
                "🧠 <i>Analyzing nuance & context...</i>",
                parse_mode="HTML",
            )
            decision = await assistant_service.analyze_and_process(
                text=input_text,
                source_lang=source_lang,
                target_lang=target_lang,
                provider_name=assist_provider,
                api_key=assist_key,
            )
            try:
                await status_msg.delete()
            except Exception:
                pass

            if decision.status == "needs_clarification" and decision.question:
                await state.set_state(SettingsStates.waiting_for_clarification)
                await state.update_data(
                    original_text=input_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    assistant_provider=assist_provider,
                )
                clarify_text = (
                    f"💡 <b>Потрібне уточнення ({source_lang} ➔ {target_lang}):</b>\n\n"
                    f"{html.escape(decision.question)}\n\n"
                    f"<i>✍️ Напишіть відповідь або потрібний контекст для точного перекладу:</i>"
                )
                await message.reply(clarify_text, parse_mode="HTML")
                return
            elif decision.translation:
                final_html = f"<code>{html.escape(decision.translation)}</code>"
                await message.reply(final_html, parse_mode="HTML")
                return

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
                text=input_text,
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
            text=input_text,
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
                text=input_text,
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
