import os
import tempfile
import pytest
from src.database.db import DatabaseManager


@pytest.fixture
async def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_users.db")
    db = DatabaseManager(db_path=db_file)
    await db.init_db()
    yield db
    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.mark.asyncio
async def test_user_settings_defaults(temp_db):
    user_id = 123456
    settings = await temp_db.get_user_settings(user_id)
    assert settings.user_id == user_id
    assert settings.target_language == "English"
    assert settings.selected_provider == "deepl"


@pytest.mark.asyncio
async def test_update_target_language(temp_db):
    user_id = 123456
    await temp_db.set_target_language(user_id, "german")
    settings = await temp_db.get_user_settings(user_id)
    assert settings.target_language == "German"


@pytest.mark.asyncio
async def test_update_user_provider(temp_db):
    user_id = 123456
    await temp_db.set_user_provider(user_id, "gemini_flash")
    settings = await temp_db.get_user_settings(user_id)
    assert settings.selected_provider == "gemini_flash"

    with pytest.raises(ValueError):
        await temp_db.set_user_provider(user_id, "unsupported_provider")


@pytest.mark.asyncio
async def test_update_assistant_settings(temp_db):
    user_id = 123456
    await temp_db.set_assistant_mode(user_id, True)
    await temp_db.set_assistant_provider(user_id, "openai_luna")
    settings = await temp_db.get_user_settings(user_id)
    assert settings.assistant_mode is True
    assert settings.assistant_provider == "openai_luna"


@pytest.mark.asyncio
async def test_user_api_keys_crud(temp_db):
    user_id = 999
    # Initially no key
    key = await temp_db.get_user_api_key(user_id, "deepl")
    assert key is None

    # Set key
    await temp_db.set_user_api_key(user_id, "deepl", "test-key-12345:fx")
    key = await temp_db.get_user_api_key(user_id, "deepl")
    assert key == "test-key-12345:fx"

    # Set another key
    await temp_db.set_user_api_key(user_id, "openrouter", "sk-or-v1-testkey")
    all_keys = await temp_db.get_all_user_api_keys(user_id)
    assert all_keys == {
        "deepl": "test-key-12345:fx",
        "openrouter": "sk-or-v1-testkey",
    }

    # Delete key
    await temp_db.delete_user_api_key(user_id, "deepl")
    key_after_del = await temp_db.get_user_api_key(user_id, "deepl")
    assert key_after_del is None
