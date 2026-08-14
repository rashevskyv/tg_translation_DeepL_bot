# Завдання проекту (Task Tracker)

## Версія: v0.2.0

### Список завдань

- [x] **TASK-001**: Створити структуру конфігурації та безпеки (`.gitignore`, `.env.example`, `requirements.txt`, `pyproject.toml`, `src/config.py`).
- [x] **TASK-002**: Реалізувати асинхронне сховище на базі SQLite (`src/database/db.py`) для збереження вибору цільової мови, моделі та персональних API ключів.
- [x] **TASK-003**: Розробити модуль розпізнавання мови (`src/services/detector.py`) з підтримкою української та іноземних мов.
- [x] **TASK-004**: Інтегрувати провайдери OpenRouter (`src/services/providers/openrouter_provider.py`) для моделей:
  - `google/gemini-3.5-flash-lite` (Gemini 3.5 Flash Lite)
  - `google/gemini-3.7-flash` (Gemini 3.7 Flash)
  - `openai/gpt-5.6-luna` (OpenAI GPT-5.6 Luna)
  - `deepseek/deepseek-v4-flash-0731` (DeepSeek V4 Flash)
  з примусовим non-thinking mode та підтримкою стрімінгу.
- [x] **TASK-005**: Зберегти standalone підтримку DeepL API (`src/services/providers/deepl_provider.py`).
- [x] **TASK-006**: Реалізувати єдине керування API ключами: DeepL API Key + універсальний OpenRouter API Key (що покриває всі 4 LLM моделі).
- [x] **TASK-007**: Створити інтерактивні GUI Inline-клавіатури та FSM-хендлери налаштувань (`src/keyboards/inline.py`, `src/handlers/settings.py`).
- [x] **TASK-008**: Реалізувати пайплайн перекладу повідомлень зі стрімінгом, троттлінгом та автокопійованим виводом у тегах коду `<code>...</code>` для миттєвого Tap-to-Copy (`src/handlers/translation.py`).
- [x] **TASK-009**: Додати кнопку `[ ⚙️ Settings ]` безпосередньо під кожною відповіддю бота з перекладом.
- [x] **TASK-010**: Створити точку входу `src/main.py`.
- [x] **TASK-011**: Реалізувати модуль багатомовної нормалізації мов (`src/services/language_normalizer.py`) для коректного мапінгу українських слів (наприклад, «Португальська» $\rightarrow$ «Portuguese» / «PT-PT»).
- [x] **TASK-012**: Додати постійну нижню клавіатуру `[⚙️ Settings] [ℹ️ Help]` та зареєструвати нативне меню команд Telegram (`BotCommand`).
- [x] **TASK-013**: Написати модульні тести та запустити їх паралельно (`tests/`, 23 тести пройдено).
- [x] **TASK-014**: Оновити документацію `README.md`, `CHANGELOG.md`, `WALKTHROUGH.md` з інструкцією по реєстрації на OpenRouter.
