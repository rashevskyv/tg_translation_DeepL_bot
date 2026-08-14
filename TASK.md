# Завдання проекту (Task Tracker)

## Версія: v0.1.4

### Список завдань

- [x] **TASK-001**: Створити структуру конфігурації та безпеки (`.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`, `src/config.py`).
- [x] **TASK-002**: Реалізувати асинхронне сховище на базі SQLite (`src/database/db.py`) для збереження вибору цільової мови, моделі та персональних API ключів.
- [x] **TASK-003**: Розробити модуль розпізнавання мови (`src/services/detector.py`) з підтримкою української та іноземних мов.
- [x] **TASK-004**: Реалізувати адаптери провайдерів перекладу (`base.py`, `deepl_provider.py`, `openai_provider.py`, `gemini_provider.py`, `qwen_provider.py`, `deepseek_provider.py`, `manager.py`).
- [x] **TASK-005**: Створити інтерактивні GUI Inline-клавіатури та FSM-хендлери налаштувань (`src/keyboards/inline.py`, `src/handlers/settings.py`).
- [x] **TASK-006**: Реалізувати пайплайн перекладу повідомлень зі стрімінгом, троттлінгом та автокопійованим виводом у тегах коду `<code>...</code>` для миттєвого Tap-to-Copy (`src/handlers/translation.py`).
- [x] **TASK-007**: Створити точку входу `src/main.py`.
- [x] **TASK-008**: Реалізувати модуль багатомовної нормалізації мов (`src/services/language_normalizer.py`) для коректного мапінгу українських слів (наприклад, «Португальська» $\rightarrow$ «Portuguese» / «PT-PT») та підключення OpenAI resolution.
- [x] **TASK-009**: Додати строгу валідацію DeepL кодів та інформативні повідомлення про перемикання на LLM у разі відсутності мови в DeepL.
- [x] **TASK-010**: Додати постійну нижню клавіатуру `[⚙️ Settings] [ℹ️ Help]` та зареєструвати нативне меню команд Telegram (`BotCommand`).
- [x] **TASK-011**: Забезпечити роботу формату `<code>` для миттєвого копіювання при одному кліку (Tap-to-Copy) у будь-якому клієнті Telegram.
- [x] **TASK-012**: Виправити фільтрацію команд та кнопок меню в aiogram 3 через незалежні декоратори хендлерів.
- [x] **TASK-013**: Написати модульні тести та запустити їх паралельно (`tests/`, 22 тести пройдено).
- [x] **TASK-014**: Оновити документацію `README.md`, `CHANGELOG.md`, `WALKTHROUGH.md`.
