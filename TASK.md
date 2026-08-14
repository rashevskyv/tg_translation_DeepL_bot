# Завдання проекту (Task Tracker)

## Версія: v0.2.1

### Список завдань

- [x] **TASK-001**: Створити структуру конфігурації та безпеки (`.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`, `src/config.py`).
- [x] **TASK-002**: Реалізувати асинхронне сховище на базі SQLite (`src/database/db.py`) для збереження вибору цільової мови, моделі та персональних API ключів.
- [x] **TASK-003**: Розробити модуль розпізнавання мови (`src/services/detector.py`) з підтримкою української та іноземних мов.
- [x] **TASK-004**: Інтегрувати провайдери OpenRouter (`src/services/providers/openrouter_provider.py`) для моделей Gemini 3.5/3.7, GPT-5.6 Luna, DeepSeek V4 у non-thinking mode зі стрімінгом.
- [x] **TASK-005**: Зберегти standalone підтримку DeepL API (`src/services/providers/deepl_provider.py`).
- [x] **TASK-006**: Реалізувати єдине керування API ключами: DeepL API Key + універсальний OpenRouter API Key.
- [x] **TASK-007**: Створити CLI утиліту `src/tools/manage_user.py` для керування та призначення персональних ключів конкретним `user_id`.
- [x] **TASK-008**: Додати команди адміністрування в чаті бота (`/assign_key <user_id> <provider> <key>` та `/user_info <user_id>`).
- [x] **TASK-009**: Створити інтерактивні GUI Inline-клавіатури та FSM-хендлери налаштувань (`src/keyboards/inline.py`, `src/handlers/settings.py`).
- [x] **TASK-010**: Реалізувати пайплайн перекладу повідомлень зі стрімінгом, троттлінгом та автокопійованим виводом у тегах коду `<code>...</code>` для миттєвого Tap-to-Copy (`src/handlers/translation.py`).
- [x] **TASK-011**: Додати кнопку `[ ⚙️ Settings ]` безпосередньо під кожною відповіддю бота з перекладом.
- [x] **TASK-012**: Модуль багатомовної нормалізації мов (`src/services/language_normalizer.py`).
- [x] **TASK-013**: Постійна нижня клавіатура `[⚙️ Settings] [ℹ️ Help]` та реєстрація нативного меню команд Telegram (`BotCommand`).
- [x] **TASK-014**: Написати модульні тести та запустити їх паралельно (`tests/`, 23 тести пройдено).
- [x] **TASK-015**: Оновити документацію `README.md`, `CHANGELOG.md`, `WALKTHROUGH.md`.
