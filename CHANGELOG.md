# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.2] - 2026-08-14

### Added
- **Persistent Bottom Settings Keyboard (`src/keyboards/reply.py`):**
  - Added persistent, auto-resizing bottom reply keyboard with `[ ⚙️ Settings ]` and `[ ℹ️ Help ]` buttons permanently available below the message input field.
  - Tapping `⚙️ Settings` instantly opens the interactive inline settings menu.
- **Telegram Native Command Menu Registration (`src/main.py`):**
  - Registered bot commands with Telegram Bot API (`bot.set_my_commands`):
    - `/settings` - ⚙️ Open settings (Languages, Engines, API keys)
    - `/start` - 🚀 Start bot & view current preferences
    - `/help` - 📖 Help & Supported providers guide
  - Displays the native blue `[ Menu ]` button on mobile and desktop Telegram clients.
- **Test Suite Expansion:**
  - Added `tests/test_keyboards.py` for reply and inline keyboard validation (22 parallel tests passing).

---

## [0.1.1] - 2026-08-14

### Added
- **Intelligent Multilingual Normalizer (`src/services/language_normalizer.py`):**
  - High-coverage local dictionary supporting Ukrainian language names (`Португальська`, `Німецька`, `Іспанська`, `Польська`, `Французька`, etc.) mapped directly to standardized English canonical names and official DeepL codes (`PT-PT`, `DE`, `ES`, `PL`, `FR`, etc.).
  - AI-assisted language resolution fallback using **OpenAI API** with structured JSON output for arbitrary or exotic language queries in any script.
- **Enhanced Test Coverage:**
  - Added unit test suite `tests/test_normalizer.py` validating Ukrainian language queries, ISO codes, and DeepL mapping.

### Fixed
- **DeepL 400 Bad Request Error (`target_lang not supported`):**
  - Resolved invalid slicing of Cyrillic text when mapping user-entered language names to DeepL target codes.
  - Added informative validation error suggesting switching to LLM engines (OpenAI, Gemini, DeepSeek, Qwen) when a language unsupported by DeepL is selected.
- **Settings UI Polish:**
  - Settings now cleanly displays the canonical English language title alongside the official DeepL code upon setting target language.

---

## [0.1.0] - 2026-08-14

### Added
- **Multi-Engine Translation Architecture:**
  - Integrated **DeepL API**, **OpenAI API** (`gpt-4o-mini`), **Google Gemini API** (`gemini-2.0-flash`), **Qwen API** (`qwen-plus`), and **DeepSeek API** (`deepseek-chat`).
- **Smart Bidirectional Translation:**
  - Automated language detection distinguishing Ukrainian from foreign languages.
- **Streaming & One-Click Copy UX:**
  - Real-time token streaming with throttled updates (~0.4s).
  - Final translation delivered in `<pre><code>` block for one-click copying.
- **Interactive In-Chat Settings GUI (`/settings`)** and SQLite storage.
- **Systemd Service** and test suite.
