import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.assistant import AssistantService


@pytest.mark.asyncio
async def test_assistant_process_turn_dialogue_no_tool():
    service = AssistantService()
    
    mock_msg = MagicMock()
    mock_msg.tool_calls = []
    mock_msg.content = "Ось 3 варіанти привітання. Який варіант вам більше підходить?"

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=mock_msg)]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        result = await service.process_turn(
            conversation_history=[{"role": "user", "content": "напиши текст з підйобом"}],
            source_lang="Ukrainian",
            target_lang="French",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert result.status == "clarifying"
        assert "варіанти" in result.assistant_message
        assert result.approved_source_text is None


@pytest.mark.asyncio
async def test_assistant_process_turn_invokes_translate_tool():
    service = AssistantService()
    
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "translate_text"
    mock_tool_call.function.arguments = '{"source_text": "О, живий ще, слава богам! Як справи?"}'

    mock_msg = MagicMock()
    mock_msg.tool_calls = [mock_tool_call]
    mock_msg.content = "Перекладаю обраний варіант."

    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=mock_msg)]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

    with patch("src.services.assistant.AsyncOpenAI", return_value=mock_client):
        result = await service.process_turn(
            conversation_history=[
                {"role": "user", "content": "напиши текст з підйобом"},
                {"role": "assistant", "content": "Ось варіанти..."},
                {"role": "user", "content": "перекладай другий варіант"},
            ],
            source_lang="Ukrainian",
            target_lang="French",
            provider_name="gemini_flash",
            api_key="fake-key",
        )
        assert result.status == "ready"
        assert result.approved_source_text == "О, живий ще, слава богам! Як справи?"
