# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.5.2] - 2026-08-15

### Changed
- **Assistant Prompt Recalibration for Intent & Tone Control (`src/services/assistant.py`):**
  - Shifted assistant persona from generic wit to accurate context understanding and user-driven emotional calibration.
  - Assistant analyzes context, clarifies missing details, and adjusts text tone on demand (from calm/neutral or diplomatic to threatening, firm, or sarcastic).
  - Strictly calls `translate_text` once user confirms satisfaction with the drafted formulation.

---

## [0.5.1] - 2026-08-15

### Changed
- Full Ukrainian localization of all bot interface buttons.

---

## [0.5.0] - 2026-08-15

### Added
- Tool Calling Architecture for Assistant (`translate_text` callable tool).
