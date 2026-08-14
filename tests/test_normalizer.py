import pytest
from src.services.language_normalizer import normalize_language, KNOWN_LANGUAGES
from src.services.providers.deepl_provider import DeepLProvider


@pytest.mark.asyncio
async def test_normalize_ukrainian_language_names():
    res_pt = await normalize_language("Португальська")
    assert res_pt.canonical_name == "Portuguese"
    assert res_pt.deepl_target_code == "PT-PT"

    res_de = await normalize_language("Німецька")
    assert res_de.canonical_name == "German"
    assert res_de.deepl_target_code == "DE"

    res_pl = await normalize_language("Польська")
    assert res_pl.canonical_name == "Polish"
    assert res_pl.deepl_target_code == "PL"

    res_es = await normalize_language("Іспанська")
    assert res_es.canonical_name == "Spanish"
    assert res_es.deepl_target_code == "ES"

    res_en = await normalize_language("Англійська")
    assert res_en.canonical_name == "English"
    assert res_en.deepl_target_code == "EN-US"


@pytest.mark.asyncio
async def test_normalize_codes_and_english_names():
    res1 = await normalize_language("pt")
    assert res1.deepl_target_code == "PT-PT"

    res2 = await normalize_language("german")
    assert res2.deepl_target_code == "DE"

    res3 = await normalize_language("PL")
    assert res3.deepl_target_code == "PL"


@pytest.mark.asyncio
async def test_normalize_conversational_utterance_mock():
    from unittest.mock import patch, MagicMock, AsyncMock
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(message=MagicMock(content='{"canonical_name": "Portuguese", "iso_code": "pt", "deepl_target_code": "PT-PT"}'))
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.language_normalizer.AsyncOpenAI", return_value=mock_client):
        res = await normalize_language("я хочу перекладати на португальську будь ласка", openrouter_api_key="fake-or-key")
        assert res.canonical_name == "Portuguese"
        assert res.deepl_target_code == "PT-PT"



def test_deepl_provider_maps_portuguese_and_ukrainian_names():
    provider = DeepLProvider()
    assert provider._map_language("Португальська", is_target=True) == "PT-PT"
    assert provider._map_language("португальська", is_target=True) == "PT-PT"
    assert provider._map_language("Portuguese", is_target=True) == "PT-PT"
    assert provider._map_language("Німецька", is_target=True) == "DE"
    assert provider._map_language("Іспанська", is_target=True) == "ES"
    assert provider._map_language("Польська", is_target=True) == "PL"


def test_deepl_provider_unsupported_language():
    provider = DeepLProvider()
    with pytest.raises(ValueError, match="DeepL API does not support target language"):
        provider._map_language("Georgian", is_target=True)
