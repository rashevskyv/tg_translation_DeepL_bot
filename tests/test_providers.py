from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from src.services.providers.deepl_provider import DeepLProvider
from src.services.providers.openai_provider import OpenAIProvider
from src.services.providers.gemini_provider import GeminiProvider
from src.services.providers.qwen_provider import QwenProvider
from src.services.providers.deepseek_provider import DeepSeekProvider


def test_deepl_url_and_language_mapping():
    provider = DeepLProvider()
    # Free endpoint
    assert provider._get_api_url("12345:fx") == "https://api-free.deepl.com/v2/translate"
    # Pro endpoint
    assert provider._get_api_url("12345pro") == "https://api.deepl.com/v2/translate"

    # Language mapping
    assert provider._map_language("Ukrainian", is_target=True) == "UK"
    assert provider._map_language("English", is_target=True) == "EN-US"
    assert provider._map_language("English", is_target=False) == "EN"
    assert provider._map_language("German", is_target=True) == "DE"
    assert provider._map_language("Polish", is_target=True) == "PL"


@pytest.mark.asyncio
async def test_deepl_translate_mock():
    provider = DeepLProvider()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.json = AsyncMock(return_value={"translations": [{"text": "Привіт Світ"}]})

    mock_post = MagicMock()
    mock_post.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_post.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_post)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await provider.translate("Hello World", "English", "Ukrainian", "fake-key:fx")
        assert result == "Привіт Світ"


@pytest.mark.asyncio
async def test_openai_translate_stream_mock():
    provider = OpenAIProvider()
    
    # Mock stream chunks
    class MockChunk:
        def __init__(self, text):
            self.choices = [MagicMock(delta=MagicMock(content=text))]

    async def mock_stream_gen():
        yield MockChunk("Hello ")
        yield MockChunk("World")

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_stream_gen())

    with patch.object(provider, "_get_client", return_value=mock_client):
        chunks = []
        async for chunk in provider.translate_stream("Привіт Світ", "Ukrainian", "English", "fake-key"):
            chunks.append(chunk)
        assert "".join(chunks) == "Hello World"


@pytest.mark.asyncio
async def test_gemini_missing_key():
    provider = GeminiProvider()
    with pytest.raises(ValueError, match="Gemini API Key is not configured"):
        await provider.translate("Привіт", "Ukrainian", "English", "")
