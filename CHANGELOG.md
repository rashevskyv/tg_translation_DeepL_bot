# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.1] - 2026-08-14

### Fixed
- **Colloquial Ukrainian & Slang Language Detection (`src/services/detector.py`):**
  - Fixed an issue where short Ukrainian phrases and slang without unique letters (like *"шо ти, голова"*) were misclassified by `langdetect` as Russian, causing false backwards translations into Ukrainian.
  - Added strict Russian letter filtering (`ы, э, ъ, ё`) and expanded Ukrainian colloquial marker heuristics.

---

## [0.3.0] - 2026-08-14

### Added
- **Intelligent Assistant Mode (`src/services/assistant.py`):**
  - Added dual-mode translation capability (`Direct Translation` vs `Assistant Mode`).
  - Context and intent clarification dialogues before translating ambiguous messages.
- **Independent Assistant Engine Selection:**
  - Independent model configurations for translation vs assistant.

---

## [0.2.3] - 2026-08-14

### Changed
- Clean translation output without persistent inline buttons.
- Conversational target language resolution using DeepSeek V4 Flash.
