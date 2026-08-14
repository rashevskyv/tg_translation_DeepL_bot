# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - Integrated **DeepL API** with automatic detection for Free (`:fx`) and Pro API endpoints.
  - Integrated **OpenAI API** (`gpt-4o-mini`) with real-time response streaming.
  - Integrated **Google Gemini API** (`gemini-2.0-flash`) with asynchronous SSE streaming.
  - Integrated **Qwen API** (`qwen-plus`) via Alibaba Cloud DashScope.
  - Integrated **DeepSeek API** (`deepseek-chat`) with streaming capability.
- **Smart Bidirectional Translation:**
  - Automated language detection distinguishing Ukrainian from foreign languages.
  - If text is Ukrainian $\rightarrow$ translated into configured Target Language.
  - If text is Non-Ukrainian $\rightarrow$ auto-detected source language and translated into Ukrainian.
- **Streaming & One-Click Copy UX:**
  - Real-time token streaming with throttled updates (~0.4s) to adhere to Telegram rate limits.
  - Automatic deletion of intermediate streamed message upon generation completion.
  - Final translation delivered inside code formatting tags (`<pre><code>...</code></pre>`), enabling instant one-click copy to clipboard in Telegram clients.
- **Interactive In-Chat Settings GUI (`/settings`):**
  - Interactive Inline keyboard navigation for configuring target language, switching active model, and managing API keys.
  - FSM text input for choosing any custom target language.
  - Per-user API key management with instant auto-deletion of user messages containing sensitive keys from chat history.
- **Storage & Security:**
  - Local asynchronous SQLite storage (`aiosqlite`) storing user preferences and encrypted/isolated personal API keys.
  - Full `.gitignore` protection preventing `.env` and database files from being committed to source control.
- **Deployment & Service:**
  - Production-ready `systemd` service unit file (`systemd/tg-translator.service`) for 24/7 background operation on Ubuntu Linux with automatic restart.
  - Comprehensive documentation in `README.md`.
- **Test Suite:**
  - 16 parallelized unit and integration tests covering language detection, database CRUD, provider adapters, and translation manager (`pytest-xdist`).
