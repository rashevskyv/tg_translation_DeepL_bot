import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.assistant import AssistantService


@pytest.mark.asyncio
async def test_assistant_process_turn_clarifying():
    service = AssistantService()
    
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(
            message=MagicMock(
                content='{"status": "clarifying", "assistant_message": "Мається на увазі банківська установа чи берег річки?", "approved_source_text": null}'
            )
        )
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        result = await service.process_turn(
            conversation_history=[{"role": "user", "content": "Я пішов у банк"}],
            source_lang="Ukrainian",
            target_lang="French",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert result.status == "clarifying"
        assert "банківська" in result.assistant_message
        assert result.approved_source_text is None


@pytest.mark.asyncio
async def test_assistant_process_turn_ready():
    service = AssistantService()
    
    mock_resp = MagicMock()
    mock_resp.choices = [
        MagicMock(
            message=MagicMock(
                content='{"status": "ready", "assistant_message": null, "approved_source_text": "Я пішов у фінансову банківську установу"}'
            )
        )
    ]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        result = await service.process_turn(
            conversation_history=[
                {"role": "user", "content": "Я пішов у банк"},
                {"role": "assistant", "content": "Який саме банк?"},
                {"role": "user", "content": "фінансова установа"},
            ],
            source_lang="Ukrainian",
            target_lang="French",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert result.status == "ready"
        assert result.approved_source_text == "Я пішов у фінансову банківську установу"
