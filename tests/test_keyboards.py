import pytest
from src.keyboards.reply import get_main_reply_keyboard
from src.keyboards.inline import get_settings_keyboard


def test_main_reply_keyboard():
    kb = get_main_reply_keyboard()
    assert kb.is_persistent is True
    assert kb.resize_keyboard is True
    button_texts = [btn.text for row in kb.keyboard for btn in row]
    assert "⚙️ Settings" in button_texts
    assert "ℹ️ Help" in button_texts


def test_settings_inline_keyboard():
    kb = get_settings_keyboard("Portuguese", "deepl", assistant_mode=False)
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Target Language: Portuguese" in text for text in button_texts)
    assert any("Translator: DeepL" in text for text in button_texts)
    assert any("Mode: ⚡ Direct Translation" in text for text in button_texts)
    assert any("Manage API Keys" in text for text in button_texts)

    # With assistant mode enabled
    kb_assist = get_settings_keyboard("German", "gemini_flash", assistant_mode=True, assistant_provider="openai_luna")
    assist_buttons = [btn.text for row in kb_assist.inline_keyboard for btn in row]
    assert any("Mode: 💡 Assistant Mode" in text for text in assist_buttons)
    assert any("Assistant Engine: OpenAI GPT-5.6 Luna" in text for text in assist_buttons)
