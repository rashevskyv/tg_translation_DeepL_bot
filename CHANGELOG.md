# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.3] - 2026-08-14

### Changed
- **Clean Translation Output (`src/handlers/translation.py`):**
  - Removed persistent inline buttons attached to translation replies. Output messages now contain strictly the copyable translation in `<code>` formatting.
  - Settings are summoned on-demand via the Telegram command menu, persistent reply keyboard, or `/settings`.
- **DeepSeek V4 Conversational Target Language Resolution (`src/services/language_normalizer.py`):**
  - Upgraded target language normalization to process any conversational sentence or utterance (e.g., *"хочу перекладати на португальську, європейський варіант"*) using **DeepSeek V4 Flash** (`deepseek/deepseek-v4-flash-0731` via OpenRouter).
  - Automatically resolves extracted languages to official DeepL canonical names and target codes (e.g. `Portuguese` $\rightarrow$ `PT-PT`).

---

## [0.2.2] - 2026-08-14

### Added
- **Automated Root Deployment Script (`scripts/deploy.sh` & `scripts/install.sh`):**
  - Fast installation for Ubuntu Server in user home directory (`~/tg_translation_DeepL_bot`).

---

## [0.2.1] - 2026-08-14

### Added
- **User Key Management & Admin CLI (`src/tools/manage_user.py`):**
  - Added CLI tool allowing admins to inspect registered users (`list`), assign specific API keys (`set-key`), delete keys (`delete-key`), and configure user preferences (`set-settings`).
- **In-Chat Telegram Admin Commands (`src/handlers/settings.py`):**
  - Added `/assign_key <user_id> <provider> <key>` command for admins.
  - Added `/user_info <user_id>` command.

---

## [0.2.0] - 2026-08-14

### Added
- **OpenRouter Unified LLM Gateway:**
  - Integrated `Gemini 3.5 Flash Lite`, `Gemini 3.7 Flash`, `GPT-5.6 Luna`, `DeepSeek V4 Flash` in Non-Thinking mode.
