import pytest
from src.keyboards.reply import get_main_reply_keyboard
from src.keyboards.inline import get_settings_keyboard


def test_main_reply_keyboard():
    kb = get_main_reply_keyboard()
    assert kb.is_persistent is True
    assert kb.resize_keyboard is True
    button_texts = [btn.text for row in kb.keyboard for btn in row]
    assert "⚙️ Налаштування" in button_texts
    assert "ℹ️ Допомога" in button_texts


def test_settings_inline_keyboard():
    kb = get_settings_keyboard("Portuguese", "deepl", assistant_mode=False)
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Цільова мова: Portuguese" in text for text in button_texts)
    assert any("Перекладач: DeepL" in text for text in button_texts)
    assert any("Режим: ⚡ Прямий переклад" in text for text in button_texts)
    assert any("Керування API ключами" in text for text in button_texts)

    # With assistant mode enabled
    kb_assist = get_settings_keyboard("German", "gemini_flash", assistant_mode=True, assistant_provider="openai_luna")
    assist_buttons = [btn.text for row in kb_assist.inline_keyboard for btn in row]
    assert any("Режим: 💡 Режим асистента" in text for text in assist_buttons)
    assert any("Модель асистента: OpenAI GPT" in text for text in assist_buttons)
