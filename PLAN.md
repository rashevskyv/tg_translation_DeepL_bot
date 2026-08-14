# План розробки: Telegram Translation DeepL & Multi-LLM Bot

## Версія: v0.2.1

### Мета проекту
Створення високопродуктивного, асинхронного Telegram-бота для автоматичного двонаправленого перекладу (Українська $\leftrightarrow$ Інші мови) з підтримкою **DeepL (Standalone)** та передових моделей через **OpenRouter** (Gemini 3.5 Flash Lite, Gemini 3.7 Flash, OpenAI GPT-5.6 Luna, DeepSeek V4 Flash) у Non-Thinking mode, гнучкою багаторівневою системою ключів (Personal Key > Admin Assigned Key > Env Fallback), інтерактивним GUI-налаштуванням мови і ключів, стрімінгом відповідей у реальному часі та фінальним виведенням у форматі коду для копіювання в один клік.

---

### Етапи виконання

- [x] **Етап 1: Базова структура та безпека**
  - [x] Створення `.gitignore` (ігнорування секретів, `.env`, бази даних `*.db`)
  - [x] Створення `.env.example` та шаблону конфігурації
  - [x] Налаштування залежностей (`requirements.txt`, `pyproject.toml`)
  - [x] Модуль конфігурації `src/config.py` (з підтримкою `ADMIN_USER_IDS`)

- [x] **Етап 2: База даних та збереження налаштувань (Per-User)**
  - [x] Асинхронний менеджер SQLite (`src/database/db.py`)
  - [x] Таблиці налаштувань користувача (цільова мова, активна модель)
  - [x] Таблиця безпечного збереження персональних API ключів для DeepL та OpenRouter

- [x] **Етап 3: Детекція мов та провайдери перекладу (DeepL + OpenRouter)**
  - [x] Детектор мови: визначення української мови vs іноземної (`src/services/detector.py`)
  - [x] Базовий клас провайдера (`src/services/providers/base.py`)
  - [x] DeepL провайдер (Free :fx та Pro підтримка) (`src/services/providers/deepl_provider.py`)
  - [x] OpenRouter провайдер (`src/services/providers/openrouter_provider.py`) з підтримкою non-thinking mode та стрімінгу для моделей:
    - `google/gemini-3.5-flash-lite`
    - `google/gemini-3.7-flash`
    - `openai/gpt-5.6-luna`
    - `deepseek/deepseek-v4-flash-0731`
  - [x] Диспетчер та фабрика провайдерів (`src/services/manager.py`)

- [x] **Етап 4: Інструменти адміністрування та призначення ключів конкретним користувачам**
  - [x] CLI утиліта `src/tools/manage_user.py` для перегляду списку та призначення ключів будь-якому `user_id`
  - [x] Адмін-команди в Telegram: `/assign_key <user_id> <provider> <key>` та `/user_info <user_id>`

- [x] **Етап 5: Інтерфейс Telegram (GUI на кнопках, FSM та стрімінг)**
  - [x] Inline-клавіатури для головного меню налаштувань, вибору моделі, зміни мови, керування API ключами (`src/keyboards/inline.py`)
  - [x] FSM-хендлери для введення мови текстом та додавання ключів з автовидаленням введеного ключа з чату (`src/handlers/settings.py`)
  - [x] Основний хендлер перекладу зі стрімінг-троттлінгом, видаленням проміжного стріму та відправкою результату у `<code>...</code>` для миттєвого Tap-to-Copy (`src/handlers/translation.py`)
  - [x] Додавання inline-кнопки `[ ⚙️ Settings ]` безпосередньо під кожним перекладеним повідомленням
  - [x] Постійна клавіатура доступу до налаштувань та допомоги (`src/keyboards/reply.py`)
  - [x] Реєстрація системного меню команд Telegram (`BotCommand`) у `src/main.py`
  - [x] Точка входу бота (`src/main.py`)

- [x] **Етап 6: Мультимовна нормалізація назв мов та інтеграція з DeepL/OpenAI**
  - [x] Створення інтелектуального модуля нормалізації мов (`src/services/language_normalizer.py`)
  - [x] Автоматичний мапінг на офіційні коди DeepL та валідація непідтримуваних мов

- [x] **Етап 7: Тестування (паралельний запуск)**
  - [x] Модульні тести (23 тести виконано паралельно через `pytest -n auto`)

- [x] **Етап 8: Розгортання та Документація**
  - [x] Створення systemd сервісу (`systemd/tg-translator.service`)
  - [x] Оновлення `README.md`, `CHANGELOG.md`, `TASK.md`, `WALKTHROUGH.md`
