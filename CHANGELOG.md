# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2026-08-14

### Added
- **Persistent Assistant Conversation Memory (`src/database/db.py`):**
  - Storing conversation history in `assistant_messages` table.
  - Automatically retains up to **30 recent messages** within a **2-hour sliding window**, pruning older context automatically.
  - Added `/reset`, `/clear` commands and `[ 🗑️ Reset Memory ]` inline button.
- **Collaborative Writing & Tone Styling (`src/services/assistant.py`):**
  - Users can ask the Assistant to draft text, adjust emotional coloring, rewrite messages politely, formally, sarcastically, or persuasively.
  - Full multi-turn iteration until the user explicitly approves, then seamlessly sends the agreed-upon text to the selected Translator Engine.

---

## [0.3.2] - 2026-08-14

### Changed
- Multi-turn assistant intent clarification dialogue and separation of assistant vs translation prompts.

---

## [0.3.1] - 2026-08-14

### Fixed
- Colloquial Ukrainian and slang detection heuristics in `src/services/detector.py`.

---

## [0.3.0] - 2026-08-14

### Added
- Intelligent Assistant Mode with independent model selection.
