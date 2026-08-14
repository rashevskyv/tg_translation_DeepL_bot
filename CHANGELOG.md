# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-08-14

### Added
- **Intelligent Assistant Mode (`src/services/assistant.py`):**
  - Added dual-mode translation capability:
    - **⚡ Direct Translation:** Instant translation into copyable code block without interruptions.
    - **💡 Assistant Mode:** Analyzes input for ambiguities, double meanings, slang, or missing context. Asks clarifying questions in Ukrainian first if uncertainty exists, then produces a polished, context-accurate translation.
- **Independent Assistant Engine Selection (`src/keyboards/inline.py`, `src/handlers/settings.py`):**
  - Users can configure independent models for Translation (e.g. DeepL) and for Assistant intent analysis (e.g. Gemini 3.7 Flash or GPT-5.6 Luna).
- **Database Schema Upgrades (`src/database/db.py`):**
  - Added `assistant_mode` and `assistant_provider` columns with non-destructive automatic SQLite schema migrations.
- **New Test Suite:**
  - Added `tests/test_assistant.py` with 27 total parallel tests passing.

---

## [0.2.3] - 2026-08-14

### Changed
- Clean translation output without persistent inline buttons.
- Conversational target language resolution using DeepSeek V4 Flash.

---

## [0.2.2] - 2026-08-14

### Added
- Automated root deployment script (`scripts/deploy.sh` & `scripts/install.sh`).

---

## [0.2.1] - 2026-08-14

### Added
- User key assignment CLI tool and in-chat admin commands.

---

## [0.2.0] - 2026-08-14

### Added
- OpenRouter unified LLM gateway integration.
