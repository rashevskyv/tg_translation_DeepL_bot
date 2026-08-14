from typing import AsyncGenerator, Dict, Optional, Tuple
from src.config import SUPPORTED_PROVIDERS, PROVIDERS_INFO
from src.database.db import db_manager
from src.services.detector import language_detector
from src.services.providers.base import BaseTranslationProvider
from src.services.providers.deepl_provider import DeepLProvider
from src.services.providers.openrouter_provider import OpenRouterProvider


class TranslationManager:
    def __init__(self):
        self.providers: Dict[str, BaseTranslationProvider] = {
            "deepl": DeepLProvider(),
            "gemini_lite": OpenRouterProvider(
                name="gemini_lite",
                model_id="google/gemini-3.5-flash-lite",
            ),
            "gemini_flash": OpenRouterProvider(
                name="gemini_flash",
                model_id="google/gemini-3.7-flash",
            ),
            "openai_luna": OpenRouterProvider(
                name="openai_luna",
                model_id="openai/gpt-5.6-luna",
            ),
            "deepseek_flash": OpenRouterProvider(
                name="deepseek_flash",
                model_id="deepseek/deepseek-v4-flash-0731",
            ),
        }

    def get_provider(self, name: str) -> BaseTranslationProvider:
        provider = self.providers.get(name.lower())
        if not provider:
            raise ValueError(f"Unknown translation provider: {name}. Supported: {SUPPORTED_PROVIDERS}")
        return provider

    async def prepare_translation(
        self, user_id: int, text: str
    ) -> Tuple[BaseTranslationProvider, str, Optional[str], str]:
        """
        Determines language direction, gets user settings and effective API key.
        Returns:
            provider: BaseTranslationProvider
            api_key: str
            source_lang: Optional[str]
            target_lang: str
        """
        user_settings = await db_manager.get_user_settings(user_id)
        provider_name = user_settings.selected_provider
        provider = self.get_provider(provider_name)

        api_key = await db_manager.get_effective_api_key(user_id, provider_name)
        if not api_key:
            provider_title = PROVIDERS_INFO.get(provider_name, {}).get("name", provider_name)
            key_name = "DeepL API Key" if provider_name == "deepl" else "OpenRouter API Key"
            raise ValueError(
                f"API Key for {provider_title} is not configured.\n\n"
                f"Please open /settings and add your {key_name}."
            )

        # Detect language
        is_ukrainian, detected_code, detected_name = language_detector.detect(text)

        if is_ukrainian:
            # Ukrainian -> User's Target Language
            source_lang = "Ukrainian"
            target_lang = user_settings.target_language
        else:
            # Non-Ukrainian -> Ukrainian
            source_lang = detected_name
            target_lang = "Ukrainian"

        return provider, api_key, source_lang, target_lang


translation_manager = TranslationManager()
