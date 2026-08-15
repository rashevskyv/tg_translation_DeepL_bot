import os
from pathlib import Path
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    
    # Provider API keys
    deepl_api_key: str = ""
    openrouter_api_key: str = ""
    openai_api_key: str = ""

    # Optional Admin Telegram IDs (comma-separated, e.g. "12345678,87654321")
    admin_user_ids: str = ""

    # Defaults
    default_target_language: str = "English"
    default_provider: str = "deepl"
    database_path: str = "data/translator.db"
    log_level: str = "INFO"

    # Streaming settings
    stream_chunk_interval: float = 0.4  # Throttle Telegram editMessage calls

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Supported providers & models metadata
PROVIDERS_INFO: Dict[str, Dict[str, str]] = {
    "deepl": {
        "name": "DeepL (Standalone)",
        "model": "default",
        "key_type": "deepl",
        "description": "Високоточний нейронний переклад (DeepL API)",
        "supports_streaming": "false",
    },
    "gemini_flash": {
        "name": "Gemini 3.7 Flash",
        "model": "google/gemini-3.7-flash",
        "key_type": "openrouter",
        "description": "Флагманська модель міркування та перекладу від Google",
        "supports_streaming": "true",
    },
    "gemini_lite": {
        "name": "Gemini 3.5 Flash Lite",
        "model": "google/gemini-3.5-flash-lite",
        "key_type": "openrouter",
        "description": "Надшвидка модель Google з мінімальною затримкою",
        "supports_streaming": "true",
    },
    "openai_luna": {
        "name": "OpenAI GPT-5.6 Luna",
        "model": "openai/gpt-5.6-luna",
        "key_type": "openrouter",
        "description": "Найновіша модель аналізу та перекладу від OpenAI ($0.10/M)",
        "supports_streaming": "true",
    },
    "deepseek_flash": {
        "name": "DeepSeek V4 Flash",
        "model": "deepseek/deepseek-v4-flash-0731",
        "key_type": "openrouter",
        "description": "Найновіша та найдешевша модель DeepSeek Flash ($0.14/M)",
        "supports_streaming": "true",
    },
    "qwen_flash": {
        "name": "Qwen 3.7 Flash",
        "model": "qwen/qwen3.7-flash",
        "key_type": "openrouter",
        "description": "Потужна багатомовна модель від Alibaba з контекстом 1M ($0.03/M)",
        "supports_streaming": "true",
    },
    "mistral_small": {
        "name": "Mistral Small 3",
        "model": "mistralai/mistral-small-24b-instruct-2501",
        "key_type": "openrouter",
        "description": "Європейський лідер для європейських мов (FR, DE, ES, PL) ($0.05/M)",
        "supports_streaming": "true",
    },
}

SUPPORTED_PROVIDERS: List[str] = list(PROVIDERS_INFO.keys())

settings = Settings()
