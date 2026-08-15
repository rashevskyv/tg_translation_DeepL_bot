import pytest
from src.utils.formatter import markdown_to_telegram_html


def test_markdown_to_telegram_html_bold_italic():
    raw = "1. **Хто ця людина?** (Наприклад, *родич* похилого віку)."
    res = markdown_to_telegram_html(raw)
    assert "<b>Хто ця людина?</b>" in res
    assert "<i>родич</i>" in res
    assert "**" not in res


def test_markdown_to_telegram_html_code_blocks():
    raw = "Ось код:\n```bash\nsystemctl restart tg-translator.service\n```\nА ось команда `git pull`."
    res = markdown_to_telegram_html(raw)
    assert "<pre><code>systemctl restart tg-translator.service</code></pre>" in res
    assert "<code>git pull</code>" in res


def test_markdown_to_telegram_html_escaping():
    raw = "Текст з <тегами> & амперсандами **жирний**."
    res = markdown_to_telegram_html(raw)
    assert "&lt;тегами&gt;" in res
    assert "&amp;" in res
    assert "<b>жирний</b>" in res
