# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.2] - 2026-08-15

### Added
- **Native Telegram Blockquotes and Emoji Headers Support (`src/utils/formatter.py`):**
  - Markdown quotes (`> text`) are automatically grouped and rendered as native Telegram `<blockquote>...</blockquote>` blocks.
  - Markdown headers (`#`, `##`, `###`, `####`) are styled with clean structured emojis (`📌`, `🔹`, `🔸`, `▫️`) and bold text (`<b>...</b>`).
  - Cleaned horizontal rules and consecutive line breaks.

---

## [0.6.1] - 2026-08-15

### Fixed
- Fixed `language_normalizer` and `DEEPL_VALID_TARGET_CODES` module exports.

---

## [0.6.0] - 2026-08-15

### Added
- Integrated high-performance translation models Qwen 3.7 Flash and Mistral Small 3.
