# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.1] - 2026-08-14

### Changed
- **Strict Intent vs Translation Classification (`src/services/assistant.py`):**
  - Messages with action verbs ("напиши...", "склади...", "допоможи...", "з підйобом...") and any ambiguous requests are strictly classified as assistant instructions rather than literal translation inputs.
  - Assistant provides creative tailored options in Ukrainian with style explanations before dispatching to translation.
- **Automatic Back-Translation Verification in Assistant Mode (`src/handlers/translation.py`):**
  - In Assistant Mode, after translating approved text into the target foreign language, the bot automatically computes and appends a Ukrainian back-translation (`🔍 Зворотний переклад (верифікація)`), allowing the user to verify the exact rendered meaning before sending it.

---

## [0.4.0] - 2026-08-14

### Added
- Persistent Assistant Conversation Memory (30 messages / 2 hours).
- Collaborative copywriting and emotional tone styling.

---

## [0.3.2] - 2026-08-14

### Changed
- Multi-turn assistant intent clarification dialogue and separation of assistant vs translation prompts.
