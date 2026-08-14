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
    kb = get_settings_keyboard("Portuguese", "deepl")
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Target Language: Portuguese" in text for text in button_texts)
    assert any("Active Engine: DeepL" in text for text in button_texts)
    assert any("Manage API Keys" in text for text in button_texts)
