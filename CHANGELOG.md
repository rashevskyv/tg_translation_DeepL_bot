# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.2] - 2026-08-14

### Changed
- **Multi-Turn Assistant Intent Clarification Dialogue (`src/services/assistant.py`, `src/handlers/translation.py`):**
  - Assistant model now conducts a full multi-turn conversational dialogue with the user until the exact meaning and nuances are mutually agreed upon.
  - Separate system prompt for Assistant (dialogue, nuance extraction, agreement) and Translation Engine (pure translation).
  - Once agreed (or if unambiguous immediately), the Assistant outputs the synthesized approved source text and passes it to the user's selected Translator Engine (DeepL or configured LLM) for final translation.
  - Added interactive buttons `[ ⚡ Translate As Is ]` and `[ ❌ Cancel ]` during clarification sessions.

---

## [0.3.1] - 2026-08-14

### Fixed
- Colloquial Ukrainian and slang detection heuristics in `src/services/detector.py`.

---

## [0.3.0] - 2026-08-14

### Added
- Intelligent Assistant Mode with independent model selection.
