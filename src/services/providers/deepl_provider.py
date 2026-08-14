import aiohttp
from typing import Optional
from src.services.providers.base import BaseTranslationProvider
from src.services.language_normalizer import KNOWN_LANGUAGES, DEEPL_VALID_TARGET_CODES


class DeepLProvider(BaseTranslationProvider):
    name = "deepl"
    supports_streaming = False

    def _get_api_url(self, api_key: str) -> str:
        if api_key.strip().endswith(":fx"):
            return "https://api-free.deepl.com/v2/translate"
        return "https://api.deepl.com/v2/translate"

    def _map_language(self, lang: str, is_target: bool = True) -> str:
        clean = lang.strip().lower()

        # Check in comprehensive language normalizer
        if clean in KNOWN_LANGUAGES:
            info = KNOWN_LANGUAGES[clean]
            if is_target and info.deepl_target_code:
                return info.deepl_target_code
            elif not is_target and info.deepl_source_code:
                return info.deepl_source_code

        # If already a valid DeepL target code
        upper_code = lang.strip().upper()
        if upper_code in DEEPL_VALID_TARGET_CODES:
            if not is_target:
                if upper_code.startswith("EN"):
                    return "EN"
                if upper_code.startswith("PT"):
                    return "PT"
            return upper_code

        # Fallback if 2 ascii letters and in valid set
        if len(upper_code) >= 2 and upper_code[:2] in DEEPL_VALID_TARGET_CODES:
            return upper_code[:2]

        raise ValueError(
            f"DeepL API does not support target language '{lang}'.\n"
            f"Please switch to an LLM provider (OpenAI, Gemini, Qwen, DeepSeek) in /settings for this language."
        )

    async def translate(
        self,
        text: str,
        source_lang: Optional[str],
        target_lang: str,
        api_key: str,
    ) -> str:
        if not api_key:
            raise ValueError("DeepL API Key is not configured. Please set it in /settings.")

        url = self._get_api_url(api_key)
        headers = {
            "Authorization": f"DeepL-Auth-Key {api_key.strip()}",
            "Content-Type": "application/json",
        }

        target_code = self._map_language(target_lang, is_target=True)
        payload = {
            "text": [text],
            "target_lang": target_code,
        }

        if source_lang:
            try:
                source_code = self._map_language(source_lang, is_target=False)
                if source_code:
                    payload["source_lang"] = source_code
            except ValueError:
                # If source language cannot be mapped strictly, let DeepL auto-detect
                pass

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                if resp.status == 403:
                    raise ValueError("DeepL authentication failed: Invalid API Key.")
                elif resp.status == 456:
                    raise ValueError("DeepL quota exceeded for this API Key.")
                elif resp.status != 200:
                    err_body = await resp.text()
                    raise ValueError(f"DeepL API Error ({resp.status}): {err_body}")

                data = await resp.json()
                translations = data.get("translations", [])
                if not translations:
                    raise ValueError("DeepL returned an empty translation response.")
                return translations[0].get("text", "")
