import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.assistant import AssistantService


@pytest.mark.asyncio
async def test_assistant_analyze_needs_clarification():
    service = AssistantService()
    
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(
            message=MagicMock(
                content='{"status": "needs_clarification", "question": "Мається на увазі банківський рахунок чи річковий берег?", "translation": null}'
            )
        )
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        decision = await service.analyze_and_process(
            text="Я пішов у банк",
            source_lang="Ukrainian",
            target_lang="English",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert decision.status == "needs_clarification"
        assert "банківський" in decision.question


@pytest.mark.asyncio
async def test_assistant_finalize_clarified_translation():
    service = AssistantService()
    
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="I went to the financial bank."))]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        res = await service.finalize_clarified_translation(
            original_text="Я пішов у банк",
            user_clarification="фінансова установа",
            source_lang="Ukrainian",
            target_lang="English",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert res == "I went to the financial bank."
