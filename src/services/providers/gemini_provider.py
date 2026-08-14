import json
from typing import AsyncGenerator, Optional
import aiohttp
from src.services.providers.base import BaseTranslationProvider


SYSTEM_PROMPT = (
    "You are a professional, highly accurate translation engine. "
    "Translate the user's input text accurately and naturally into {target_lang}. "
    "Preserve formatting, line breaks, code blocks, emojis, and punctuation. "
    "Output ONLY the translated text. Do NOT add any preamble, explanations, notes, or quotes."
)


class GeminiProvider(BaseTranslationProvider):
    name = "gemini"
    supports_streaming = True
    default_model = "gemini-2.0-flash"

    async def translate(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> str:
        if not api_key:
            raise ValueError("Gemini API Key is not configured. Please set it in /settings.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.default_model}:generateContent?key={api_key.strip()}"
        prompt = SYSTEM_PROMPT.format(target_lang=target_lang)

        payload = {
            "system_instruction": {
                "parts": [{"text": prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": text}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 400 or resp.status == 403:
                    error_data = await resp.text()
                    raise ValueError(f"Gemini API authentication/request error ({resp.status}): {error_data}")
                elif resp.status != 200:
                    error_data = await resp.text()
                    raise ValueError(f"Gemini API error ({resp.status}): {error_data}")

                data = await resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return ""
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join(part.get("text", "") for part in parts)

    async def translate_stream(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        if not api_key:
            raise ValueError("Gemini API Key is not configured. Please set it in /settings.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.default_model}:streamGenerateContent?alt=sse&key={api_key.strip()}"
        prompt = SYSTEM_PROMPT.format(target_lang=target_lang)

        payload = {
            "system_instruction": {
                "parts": [{"text": prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": text}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=45)) as resp:
                if resp.status != 200:
                    err_msg = await resp.text()
                    raise ValueError(f"Gemini stream error ({resp.status}): {err_msg}")

                async for raw_line in resp.content:
                    line = raw_line.decode("utf-8").strip()
                    if not line or not line.startswith("data:"):
                        continue
                    
                    data_str = line[len("data:"):].strip()
                    if not data_str:
                        continue
                    try:
                        chunk_json = json.loads(data_str)
                        candidates = chunk_json.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text_chunk = part.get("text", "")
                                if text_chunk:
                                    yield text_chunk
                    except json.JSONDecodeError:
                        continue
