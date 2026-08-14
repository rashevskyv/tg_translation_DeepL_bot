from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from src.services.providers.deepl_provider import DeepLProvider
from src.services.providers.openrouter_provider import OpenRouterProvider


def test_deepl_url_and_language_mapping():
    provider = DeepLProvider()
    assert provider._get_api_url("12345:fx") == "https://api-free.deepl.com/v2/translate"
    assert provider._get_api_url("12345pro") == "https://api.deepl.com/v2/translate"
    assert provider._map_language("Ukrainian", is_target=True) == "UK"
    assert provider._map_language("English", is_target=True) == "EN-US"
    assert provider._map_language("German", is_target=True) == "DE"


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
async def test_openrouter_translate_stream_mock():
    provider = OpenRouterProvider(name="gemini_flash", model_id="google/gemini-3.7-flash")
    
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
        async for chunk in provider.translate_stream("Привіт Світ", "Ukrainian", "English", "fake-or-key"):
            chunks.append(chunk)
        assert "".join(chunks) == "Hello World"


@pytest.mark.asyncio
async def test_openrouter_missing_key():
    provider = OpenRouterProvider(name="openai_luna", model_id="openai/gpt-5.6-luna")
    with pytest.raises(ValueError, match="OpenRouter API Key is not configured"):
        await provider.translate("Привіт", "Ukrainian", "English", "")
