# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.0] - 2026-08-15

### Added
- **Integrated High-Performance, Ultra-Cheap Multilingual Translation Models (`src/config.py`, `src/services/manager.py`):**
  - **Qwen 3.7 Flash (`qwen/qwen3.7-flash`):** $0.03 / $0.13 per 1M tokens, 1M context, exceptional multilingual performance.
  - **Mistral Small 3 (`mistralai/mistral-small-24b-instruct-2501`):** $0.05 / $0.08 per 1M tokens, industry leader in European languages (FR, DE, ES, IT, PL).

---

## [0.5.5] - 2026-08-15

### Changed
- Configured exact latest models and full Ukrainian localization of settings menus.

---

## [0.5.4] - 2026-08-15

### Changed
- Assistant session memory persistence and auto-reset upon switching to translator mode.
