import html
import re


def markdown_to_telegram_html(text: str) -> str:
    """
    Converts markdown formatting from LLM responses into safe, valid Telegram HTML.
    Supports:
    - Code blocks (``` ... ``` -> <pre><code>...</code></pre>)
    - Inline code (`code` -> <code>code</code>)
    - Blockquotes (> quote -> <blockquote>quote</blockquote>)
    - Headers (#, ##, ###, #### -> emojis + <b>header</b>)
    - Bold (**text** -> <b>text</b>)
    - Italic (*text* -> <i>text</i>)
    - Clean horizontal rules (--- -> removed/spaced)
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

    # 5. Headers: #, ##, ###, ####
    safe_text = re.sub(r"^####\s+(.+)$", r"▫️ <b>\1</b>", safe_text, flags=re.MULTILINE)
    safe_text = re.sub(r"^###\s+(.+)$", r"🔸 <b>\1</b>", safe_text, flags=re.MULTILINE)
    safe_text = re.sub(r"^##\s+(.+)$", r"🔹 <b>\1</b>", safe_text, flags=re.MULTILINE)
    safe_text = re.sub(r"^#\s+(.+)$", r"📌 <b>\1</b>", safe_text, flags=re.MULTILINE)

    # 6. Blockquotes: contiguous lines starting with &gt;
    def _replace_blockquotes(match):
        block = match.group(0)
        cleaned_lines = []
        for line in block.splitlines():
            cleaned_line = re.sub(r"^&gt;\s?", "", line)
            cleaned_lines.append(cleaned_line)
        inner = "\n".join(cleaned_lines).strip()
        return f"<blockquote>{inner}</blockquote>"

    safe_text = re.sub(
        r"(?:^&gt;[^\n]*(?:\n|$))+",
        _replace_blockquotes,
        safe_text,
        flags=re.MULTILINE,
    )

    # 7. Horizontal rules: ---, ***, ___
    safe_text = re.sub(r"^[ \t]*[-*_]{3,}[ \t]*$", r"", safe_text, flags=re.MULTILINE)

    # 8. Restore code blocks
    for idx, block in enumerate(code_blocks):
        safe_text = safe_text.replace(f"__CODE_BLOCK_{idx}__", block)

    # Clean up multiple consecutive empty lines
    safe_text = re.sub(r"\n{3,}", "\n\n", safe_text)

    return safe_text.strip()
