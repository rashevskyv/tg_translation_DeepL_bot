# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1] - 2026-08-14

### Added
- **User Key Management & Admin CLI (`src/tools/manage_user.py`):**
  - Added CLI tool allowing admins to inspect registered users (`list`), assign specific API keys (`set-key`), delete keys (`delete-key`), and configure user preferences (`set-settings`).
- **In-Chat Telegram Admin Commands (`src/handlers/settings.py`):**
  - Added `/assign_key <user_id> <provider> <key>` command for admins (auto-deletes message for privacy).
  - Added `/user_info <user_id>` command to inspect user's preferences and custom keys status.
  - Added `ADMIN_USER_IDS` configuration to `src/config.py` and `.env.example`.
- **Multilevel Key Resolution:**
  - Strict precedence: User's custom key $\rightarrow$ Admin assigned key $\rightarrow$ System `.env` default $\rightarrow$ Prompt user to set key.

---

## [0.2.0] - 2026-08-14

### Added
- **OpenRouter Unified LLM Gateway (`src/services/providers/openrouter_provider.py`):**
  - Integrated 4 next-generation translation models via OpenRouter API:
    - `google/gemini-3.5-flash-lite` (Gemini 3.5 Flash Lite)
    - `google/gemini-3.7-flash` (Gemini 3.7 Flash)
    - `openai/gpt-5.6-luna` (OpenAI GPT-5.6 Luna)
    - `deepseek/deepseek-v4-flash-0731` (DeepSeek V4 Flash)
  - Enforced **Non-Thinking mode** (`reasoning: {"effort": "none"}`).
  - Real-time token streaming support across all OpenRouter models.
- **Unified API Key Management:**
  - Single universal **OpenRouter API Key** unlocking all 4 LLM engines.

---

## [0.1.5] - 2026-08-14

### Added
- Inline `[ ⚙️ Settings ]` button attached under every translation response.

---

## [0.1.4] - 2026-08-14

### Fixed
- Resolved aiogram 3 handler filter syntax error for commands and text buttons.

---

## [0.1.3] - 2026-08-14

### Changed
- Switched to `<code>` formatting for instant Telegram tap-to-copy functionality.

---

## [0.1.2] - 2026-08-14

### Added
- Persistent bottom keyboard `[ ⚙️ Settings ]` `[ ℹ️ Help ]` and Telegram command menu registration.

---

## [0.1.1] - 2026-08-14

### Added
- Multilingual language normalizer (`src/services/language_normalizer.py`) supporting Ukrainian names (`Португальська` -> `PT-PT`).

---

## [0.1.0] - 2026-08-14

### Added
- Initial project release with bidirectional translation, SQLite per-user storage, and systemd service.
