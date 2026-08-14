# Завдання проекту (Task Tracker)

## Версія: v0.1.0

### Список завдань

- [x] **TASK-001**: Створити структуру конфігурації та безпеки (`.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`, `src/config.py`).
- [x] **TASK-002**: Реалізувати асинхронне сховище на базі SQLite (`src/database/db.py`) для збереження вибору цільової мови, моделі та персональних API ключів.
- [x] **TASK-003**: Розробити модуль розпізнавання мови (`src/services/detector.py`) з підтримкою української та іноземних мов.
- [x] **TASK-004**: Реалізувати адаптери провайдерів перекладу (`base.py`, `deepl_provider.py`, `openai_provider.py`, `gemini_provider.py`, `qwen_provider.py`, `deepseek_provider.py`, `manager.py`).
- [x] **TASK-005**: Створити інтерактивні GUI Inline-клавіатури та FSM-хендлери налаштувань (`src/keyboards/inline.py`, `src/handlers/settings.py`).
- [x] **TASK-006**: Реалізувати пайплайн перекладу повідомлень зі стрімінгом, троттлінгом та автокопійованим виводом у тегах коду (`src/handlers/translation.py`).
- [x] **TASK-007**: Створити точку входу `src/main.py`.
- [x] **TASK-008**: Написати модульні тести та запустити їх паралельно (`tests/`).
- [x] **TASK-009**: Створити systemd service файл (`systemd/tg-translator.service`) та вичерпний `README.md`.
