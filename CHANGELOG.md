# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.5] - 2026-08-15

### Changed
- **Configured Exact Requested Models & Full Settings Localization (`src/config.py`, `src/handlers/settings.py`):**
  - Updated models: `google/gemini-3.7-flash`, `google/gemini-3.5-flash-lite`, `openai/gpt-5.6-luna`, `deepseek/deepseek-v4-flash-0731`.
  - Fully translated all remaining settings menu titles and prompts to Ukrainian.

---

## [0.5.4] - 2026-08-15

### Changed
- Assistant session memory persistence and auto-reset upon switching to translator mode.

---

## [0.5.3] - 2026-08-15

### Fixed
- Markdown-to-HTML formatting converter for Telegram bold, italic, and code blocks.
