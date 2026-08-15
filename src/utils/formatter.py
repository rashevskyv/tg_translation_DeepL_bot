import html
import re


def markdown_to_telegram_html(text: str) -> str:
    """
    Converts markdown formatting (bold, italic, code blocks, inline code)
    from LLM responses into safe, valid Telegram HTML.
    """
    if not text:
        return ""

    # First, safely escape HTML characters
    safe_text = html.escape(text)

    # 1. Multi-line code blocks: ```lang ... ```
    code_blocks = []

    def _extract_code_block(match):
        code_content = match.group(1).strip()
        idx = len(code_blocks)
        code_blocks.append(f"<pre><code>{code_content}</code></pre>")
        return f"__CODE_BLOCK_{idx}__"

    safe_text = re.sub(
        r"```(?:[a-zA-Z0-9_\-]+)?\n?(.*?)```",
        _extract_code_block,
        safe_text,
        flags=re.DOTALL,
    )

    # 2. Inline code: `code`
    safe_text = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", safe_text)

    # 3. Bold: **text** or __text__
    safe_text = re.sub(r"\*\*([^\*\n]+)\*\*", r"<b>\1</b>", safe_text)
    safe_text = re.sub(r"__([^_]+)__", r"<b>\1</b>", safe_text)

    # 4. Italic: *text* or _text_
    safe_text = re.sub(r"(?<!\w)\*([^\*\n]+)\*(?!\w)", r"<i>\1</i>", safe_text)
    safe_text = re.sub(r"(?<!\w)_([^_\n]+)_(?!\w)", r"<i>\1</i>", safe_text)

    # Restore code blocks
    for idx, block in enumerate(code_blocks):
        safe_text = safe_text.replace(f"__CODE_BLOCK_{idx}__", block)

    return safe_text
