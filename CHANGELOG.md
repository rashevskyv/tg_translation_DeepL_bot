# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.1] - 2026-08-15

### Changed
- **Full Ukrainian Localization for All Bot Buttons (`src/keyboards/reply.py`, `src/keyboards/inline.py`, `src/handlers/translation.py`):**
  - Localized persistent reply keyboards (`⚙️ Налаштування`, `ℹ️ Допомога`).
  - Localized all interactive inline setting buttons (`🌐 Цільова мова`, `🤖 Перекладач`, `🔄 Режим`, `🧠 Модель асистента`, `🔑 Керування API ключами`, `✖️ Закрити`, `⚡ Перекласти як є`, `🗑️ Очистити пам'ять`, `❌ Скасувати`).

---

## [0.5.0] - 2026-08-15

### Added
- **Tool Calling Architecture for Assistant (`src/services/assistant.py`):**
  - Integrated `translate_text(source_text="...")` tool directly into LLM assistant context.
  - Translator is invoked strictly as a callable tool once intent is finalized and approved by the user.

---

## [0.4.2] - 2026-08-14

### Changed
- Reasoning enabled exclusively for assistant mode.
