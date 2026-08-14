# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.2] - 2026-08-14

### Added
- **Automated Root Deployment Script (`scripts/deploy.sh`):**
  - Instant One-Liner deployment for Ubuntu Server in user home directory (`~/tg_translation_DeepL_bot`).
  - Automatic `systemd` unit setup, Python virtual environment creation, configuration, and pre-seeding of admin keys.

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
