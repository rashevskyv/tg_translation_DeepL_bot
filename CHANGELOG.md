# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.4] - 2026-08-15

### Changed
- **Assistant Session Memory Lifecycle Management (`src/database/db.py`, `src/handlers/settings.py`):**
  - Assistant conversation history is preserved throughout the active assistant session (up to 30 messages).
  - Memory is automatically cleared as soon as the user switches back to Direct Translation Mode.

---

## [0.5.3] - 2026-08-15

### Fixed
- Markdown-to-HTML formatting converter for Telegram bold, italic, and code blocks.

---

## [0.5.2] - 2026-08-15

### Changed
- Recalibrated assistant persona for accurate context understanding and user-driven emotional calibration.
