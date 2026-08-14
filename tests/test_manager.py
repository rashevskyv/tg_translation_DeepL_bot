import os
import tempfile
import pytest
from unittest.mock import patch
from src.database.db import DatabaseManager
from src.services.manager import TranslationManager


@pytest.fixture
async def custom_manager():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_mgr.db")
    db = DatabaseManager(db_path=db_file)
    await db.init_db()
    
    with patch("src.services.manager.db_manager", db):
        mgr = TranslationManager()
        yield mgr, db

    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.mark.asyncio
async def test_prepare_translation_ukrainian_direction(custom_manager):
    mgr, db = custom_manager
    user_id = 777
    await db.set_target_language(user_id, "German")
    await db.set_user_api_key(user_id, "deepl", "fake-deepl-key:fx")

    provider, api_key, source_lang, target_lang = await mgr.prepare_translation(
        user_id, "Привіт, як справи?"
    )
    assert provider.name == "deepl"
    assert api_key == "fake-deepl-key:fx"
    assert source_lang == "Ukrainian"
    assert target_lang == "German"


@pytest.mark.asyncio
async def test_prepare_translation_openrouter_unified_key(custom_manager):
    mgr, db = custom_manager
    user_id = 777
    await db.set_user_provider(user_id, "gemini_flash")
    await db.set_user_api_key(user_id, "openrouter", "sk-or-v1-testkey")

    provider, api_key, source_lang, target_lang = await mgr.prepare_translation(
        user_id, "Hello, this is a test in English."
    )
    assert provider.name == "gemini_flash"
    assert api_key == "sk-or-v1-testkey"
    assert source_lang == "English"
    assert target_lang == "Ukrainian"


@pytest.mark.asyncio
async def test_prepare_translation_foreign_direction(custom_manager):
    mgr, db = custom_manager
    user_id = 777
    await db.set_user_api_key(user_id, "deepl", "fake-deepl-key:fx")

    provider, api_key, source_lang, target_lang = await mgr.prepare_translation(
        user_id, "Hello, this is a test in English."
    )
    assert provider.name == "deepl"
    assert api_key == "fake-deepl-key:fx"
    assert source_lang == "English"
    assert target_lang == "Ukrainian"


@pytest.mark.asyncio
async def test_prepare_translation_missing_key(custom_manager):
    mgr, db = custom_manager
    user_id = 888
    with patch("src.database.db.settings.deepl_api_key", ""):
        with pytest.raises(ValueError, match="API Key for DeepL"):
            await mgr.prepare_translation(user_id, "Hello world")
