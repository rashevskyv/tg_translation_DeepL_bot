# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.3] - 2026-08-15

### Fixed
- **Markdown-to-HTML Formatting Converter (`src/utils/formatter.py`, `src/handlers/translation.py`):**
  - Resolved raw Markdown asterisks (`**bold**`, `*italic*`, ````code````) in Telegram messages by parsing and transforming them to valid Telegram HTML (`<b>...</b>`, `<i>...</i>`, `<pre><code>...</code></pre>`).
  - Added comprehensive test coverage in `tests/test_formatter.py`.

---

## [0.5.2] - 2026-08-15

### Changed
- Recalibrated assistant persona for accurate context understanding and user-driven emotional calibration.

---

## [0.5.1] - 2026-08-15

### Changed
- Full Ukrainian localization of all bot interface buttons.
