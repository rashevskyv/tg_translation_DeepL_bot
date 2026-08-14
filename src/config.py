import os
from pathlib import Path
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    
    # Optional default API keys
    deepl_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    dashscope_api_key: str = ""
    deepseek_api_key: str = ""

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


# Supported providers metadata
PROVIDERS_INFO: Dict[str, Dict[str, str]] = {
    "deepl": {
        "name": "DeepL",
        "model": "default",
        "description": "High-accuracy neural machine translation (DeepL API)",
        "supports_streaming": "false",
    },
    "openai": {
        "name": "OpenAI",
        "model": "gpt-4o-mini",
        "description": "Fast and intelligent translation via GPT-4o-mini",
        "supports_streaming": "true",
    },
    "gemini": {
        "name": "Google Gemini",
        "model": "gemini-2.0-flash",
        "description": "Ultra-fast multimodal translation with Gemini Flash",
        "supports_streaming": "true",
    },
    "qwen": {
        "name": "Qwen",
        "model": "qwen-plus",
        "description": "Alibaba Cloud Qwen AI translation",
        "supports_streaming": "true",
    },
    "deepseek": {
        "name": "DeepSeek",
        "model": "deepseek-chat",
        "description": "DeepSeek V3 high quality translation",
        "supports_streaming": "true",
    },
}

SUPPORTED_PROVIDERS: List[str] = list(PROVIDERS_INFO.keys())

# Ensure base directories exist
Path("data").mkdir(parents=True, exist_ok=True)

settings = Settings()
