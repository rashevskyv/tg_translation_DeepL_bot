# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.2] - 2026-08-14

### Changed
- **Reasoning Enabled Exclusively for Assistant Mode (`src/services/assistant.py`):**
  - Enabled deep reasoning in Assistant Mode for nuanced understanding of sarcasm, tone, intent, and colloquial drafting.
  - Kept direct translation fast and lean without reasoning overhead.
- **Model Endpoint Stability (`src/config.py`):**
  - Updated model endpoints for full compatibility with OpenRouter (`google/gemini-2.5-flash`, `google/gemini-2.5-flash-lite`, `openai/gpt-4o-mini`, `deepseek/deepseek-chat`).

---

## [0.4.1] - 2026-08-14

### Changed
- Strict Intent vs Translation Classification and automatic back-translation verification.

---

## [0.4.0] - 2026-08-14

### Added
- Persistent Assistant Conversation Memory (30 messages / 2 hours).
- Collaborative copywriting and emotional tone styling.
