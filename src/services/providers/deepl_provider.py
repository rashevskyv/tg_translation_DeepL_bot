import aiohttp
from typing import Optional, Dict
from src.services.providers.base import BaseTranslationProvider


DEEPL_LANG_MAP: Dict[str, str] = {
    "ukrainian": "UK",
    "uk": "UK",
    "english": "EN-US",
    "en": "EN-US",
    "en-us": "EN-US",
    "en-gb": "EN-GB",
    "german": "DE",
    "de": "DE",
    "french": "FR",
    "fr": "FR",
    "spanish": "ES",
    "es": "ES",
    "italian": "IT",
    "it": "IT",
    "polish": "PL",
    "pl": "PL",
    "portuguese": "PT-PT",
    "pt": "PT-PT",
    "dutch": "NL",
    "nl": "NL",
    "japanese": "JA",
    "ja": "JA",
    "chinese": "ZH",
    "zh": "ZH",
    "russian": "RU",
    "ru": "RU",
    "czech": "CS",
    "cs": "CS",
    "slovak": "SK",
    "sk": "SK",
    "swedish": "SV",
    "sv": "SV",
    "danish": "DA",
    "da": "DA",
    "finnish": "FI",
    "fi": "FI",
    "greek": "EL",
    "el": "EL",
    "hungarian": "HU",
    "hu": "HU",
    "romanian": "RO",
    "ro": "RO",
    "turkish": "TR",
    "tr": "TR",
    "bulgarian": "BG",
    "bg": "BG",
}


class DeepLProvider(BaseTranslationProvider):
    name = "deepl"
    supports_streaming = False

    def _get_api_url(self, api_key: str) -> str:
        if api_key.strip().endswith(":fx"):
            return "https://api-free.deepl.com/v2/translate"
        return "https://api.deepl.com/v2/translate"

    def _map_language(self, lang: str, is_target: bool = True) -> str:
        clean = lang.strip().lower()
        if clean in DEEPL_LANG_MAP:
            mapped = DEEPL_LANG_MAP[clean]
            # DeepL source_lang cannot be EN-US, only EN
            if not is_target and mapped.startswith("EN"):
                return "EN"
            if not is_target and mapped.startswith("PT"):
                return "PT"
            return mapped
        # Fallback to uppercase 2-letter code if valid length
        return clean.upper()[:2] if len(clean) >= 2 else "EN-US"

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
            source_code = self._map_language(source_lang, is_target=False)
            if source_code:
                payload["source_lang"] = source_code

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
