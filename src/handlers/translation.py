import asyncio
import html
import time
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from src.config import settings, PROVIDERS_INFO
from src.services.manager import translation_manager

translation_router = Router(name="translation")


def _get_error_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Open Settings", callback_data="open_main_settings")]
        ]
    )


@translation_router.message(F.text & ~F.text.startswith("/"))
async def handle_translation_text(message: Message) -> None:
    user_id = message.from_user.id
    input_text = message.text.strip()
    if not input_text:
        return

    # Prepare translation request
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

        # Delete status message and send final copyable code block
        try:
            await status_msg.delete()
        except Exception:
            pass

        final_html = f"<pre><code>{html.escape(translated_text)}</code></pre>"
        await message.reply(final_html, parse_mode="HTML")
        return

    # Streaming mode for LLM providers (OpenAI, Gemini, Qwen, DeepSeek)
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

            # Throttled editing to respect Telegram rate limits
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
                    pass  # Content unchanged or message edit error

        if not accumulated_text.strip():
            # Fallback to single translate if stream returned nothing
            accumulated_text = await provider.translate(
                text=input_text,
                source_lang=source_lang,
                target_lang=target_lang,
                api_key=api_key,
            )

        # Once streaming completes: delete streamed message and send final inside code tags
        try:
            await stream_msg.delete()
        except Exception:
            pass

        final_html = f"<pre><code>{html.escape(accumulated_text)}</code></pre>"
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
