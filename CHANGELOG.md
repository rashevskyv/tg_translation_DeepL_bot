# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.1] - 2026-08-15

### Fixed
- **Fixed `language_normalizer` and `DEEPL_VALID_TARGET_CODES` Module Exports (`src/services/language_normalizer.py`):**
  - Resolved `ImportError` on application startup by exporting `language_normalizer` singleton instance and `DEEPL_VALID_TARGET_CODES` validation set.

---

## [0.6.0] - 2026-08-15

### Added
- Integrated high-performance translation models Qwen 3.7 Flash and Mistral Small 3.

---

## [0.5.5] - 2026-08-15

### Changed
- Configured exact latest models and full Ukrainian localization of settings menus.
