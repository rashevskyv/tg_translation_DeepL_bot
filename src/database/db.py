import os
from pathlib import Path
from typing import Dict, Optional
import aiosqlite
from pydantic import BaseModel
from src.config import settings, SUPPORTED_PROVIDERS, PROVIDERS_INFO

VALID_KEY_PROVIDERS = set(SUPPORTED_PROVIDERS) | {"openrouter", "openai", "deepl"}


class UserSettings(BaseModel):
    user_id: int
    target_language: str = "English"
    selected_provider: str = "deepl"


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self) -> None:
        """Initializes database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    target_language TEXT NOT NULL DEFAULT 'English',
                    selected_provider TEXT NOT NULL DEFAULT 'deepl',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_api_keys (
                    user_id INTEGER NOT NULL,
                    provider TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, provider)
                );
                """
            )
            await db.commit()

    async def get_user_settings(self, user_id: int) -> UserSettings:
        """Fetches user settings, creating defaults if not existing."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT target_language, selected_provider FROM user_settings WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserSettings(
                        user_id=user_id,
                        target_language=row[0],
                        selected_provider=row[1],
                    )

            # Insert default if not present
            default_lang = settings.default_target_language
            default_provider = settings.default_provider
            await db.execute(
                """
                INSERT OR IGNORE INTO user_settings (user_id, target_language, selected_provider)
                VALUES (?, ?, ?)
                """,
                (user_id, default_lang, default_provider),
            )
            await db.commit()
            return UserSettings(
                user_id=user_id,
                target_language=default_lang,
                selected_provider=default_provider,
            )

    async def set_target_language(self, user_id: int, target_language: str) -> None:
        """Updates user target language."""
        cleaned_lang = target_language.strip().capitalize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO user_settings (user_id, target_language, selected_provider, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    target_language = excluded.target_language,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, cleaned_lang, settings.default_provider),
            )
            await db.commit()

    async def set_user_provider(self, user_id: int, provider: str) -> None:
        """Updates active translation provider for the user."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO user_settings (user_id, target_language, selected_provider, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    selected_provider = excluded.selected_provider,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, settings.default_target_language, provider),
            )
            await db.commit()

    async def set_user_api_key(self, user_id: int, provider: str, api_key: str) -> None:
        """Saves custom API key for a specific provider."""
        if provider not in VALID_KEY_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        clean_key = api_key.strip()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO user_api_keys (user_id, provider, api_key, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, provider) DO UPDATE SET
                    api_key = excluded.api_key,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, provider, clean_key),
            )
            await db.commit()

    async def delete_user_api_key(self, user_id: int, provider: str) -> None:
        """Deletes user's custom API key for a specific provider."""
        if provider not in VALID_KEY_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM user_api_keys WHERE user_id = ? AND provider = ?",
                (user_id, provider),
            )
            await db.commit()

    async def get_user_api_key(self, user_id: int, provider: str) -> Optional[str]:
        """Gets user-configured API key for a provider."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT api_key FROM user_api_keys WHERE user_id = ? AND provider = ?",
                (user_id, provider),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def get_all_user_api_keys(self, user_id: int) -> Dict[str, str]:
        """Gets all custom API keys configured by the user."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT provider, api_key FROM user_api_keys WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    async def get_effective_api_key(self, user_id: int, provider: str) -> Optional[str]:
        """
        Returns custom API key if set by user, otherwise falls back to system environment key.
        Supports unified OpenRouter key mapping across all OpenRouter models.
        """
        # 1. Check direct user key
        custom_key = await self.get_user_api_key(user_id, provider)
        if custom_key:
            return custom_key

        # 2. Check unified OpenRouter key if provider uses OpenRouter
        provider_meta = PROVIDERS_INFO.get(provider, {})
        if provider_meta.get("key_type") == "openrouter":
            openrouter_user_key = await self.get_user_api_key(user_id, "openrouter")
            if openrouter_user_key:
                return openrouter_user_key
            if settings.openrouter_api_key:
                return settings.openrouter_api_key

        # 3. Fallbacks from settings
        fallback_map = {
            "deepl": settings.deepl_api_key,
            "openrouter": settings.openrouter_api_key,
            "openai": settings.openai_api_key,
        }
        return fallback_map.get(provider) or None


db_manager = DatabaseManager()
