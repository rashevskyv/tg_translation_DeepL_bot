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
        "description": "High-accuracy neural machine translation (DeepL API)",
        "supports_streaming": "false",
    },
    "gemini_lite": {
        "name": "Gemini 3.5 Flash Lite",
        "model": "google/gemini-3.5-flash-lite",
        "key_type": "openrouter",
        "description": "Ultra-fast low-latency translation via OpenRouter",
        "supports_streaming": "true",
    },
    "gemini_flash": {
        "name": "Gemini 3.7 Flash",
        "model": "google/gemini-3.7-flash",
        "key_type": "openrouter",
        "description": "Next-gen intelligent multimodal translation via OpenRouter",
        "supports_streaming": "true",
    },
    "openai_luna": {
        "name": "OpenAI GPT-5.6 Luna",
        "model": "openai/gpt-5.6-luna",
        "key_type": "openrouter",
        "description": "State-of-the-art GPT translation via OpenRouter",
        "supports_streaming": "true",
    },
    "deepseek_flash": {
        "name": "DeepSeek V4 Flash",
        "model": "deepseek/deepseek-v4-flash-0731",
        "key_type": "openrouter",
        "description": "High efficiency DeepSeek V4 translation via OpenRouter",
        "supports_streaming": "true",
    },
}

SUPPORTED_PROVIDERS: List[str] = list(PROVIDERS_INFO.keys())

# Ensure base directories exist
Path("data").mkdir(parents=True, exist_ok=True)

settings = Settings()
