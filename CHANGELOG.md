# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.5] - 2026-08-14

### Added
- **Inline Settings Button on Translation Replies (`src/handlers/translation.py`):**
  - Attached a prominent `[ ⚙️ Settings ]` inline button directly beneath every translated message.
  - Tapping this button immediately reveals the interactive settings GUI (Target language, Active engine, API keys) directly under the translated message.

---

## [0.1.4] - 2026-08-14

### Fixed
- **Aiogram 3 Filter Operator Error:**
  - Resolved `TypeError: unsupported operand type(s) for |: 'Command' and 'bool'` by splitting combined filters into separate handler decorators for `/settings`, `/help`, and their corresponding button texts.

---

## [0.1.3] - 2026-08-14

### Changed
- **Native One-Click Copy (`<code>` tag format):**
  - Replaced `<pre><code>` blocks with `<code>` formatting in `src/handlers/translation.py`.
  - In Telegram clients (Android, iOS, Desktop), clicking or tapping anywhere inside `<code>...</code>` triggers native **Tap-to-Copy** with an instant clipboard notification.

---

## [0.1.2] - 2026-08-14

### Added
- **Persistent Bottom Settings Keyboard (`src/keyboards/reply.py`):**
  - Added persistent, auto-resizing bottom reply keyboard with `[ ⚙️ Settings ]` and `[ ℹ️ Help ]` buttons permanently available below the message input field.
- **Telegram Native Command Menu Registration (`src/main.py`):**
  - Registered bot commands with Telegram Bot API (`bot.set_my_commands`).

---

## [0.1.1] - 2026-08-14

### Added
- **Intelligent Multilingual Normalizer (`src/services/language_normalizer.py`):**
  - High-coverage local dictionary supporting Ukrainian language names mapped directly to standardized English canonical names and official DeepL codes.

---

## [0.1.0] - 2026-08-14

### Added
- **Multi-Engine Translation Architecture:**
  - Integrated **DeepL API**, **OpenAI API** (`gpt-4o-mini`), **Google Gemini API** (`gemini-2.0-flash`), **Qwen API** (`qwen-plus`), and **DeepSeek API** (`deepseek-chat`).
