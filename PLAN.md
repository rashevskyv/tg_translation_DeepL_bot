# План розробки: Telegram Translation DeepL & Multi-LLM Bot

## Версія: v0.2.0

### Мета проекту
Створення високопродуктивного, асинхронного Telegram-бота для автоматичного двонаправленого перекладу (Українська $\leftrightarrow$ Інші мови) з підтримкою **DeepL (Standalone)** та передових моделей через **OpenRouter** (Gemini 3.5 Flash Lite, Gemini 3.7 Flash, OpenAI GPT-5.6 Luna, DeepSeek V4 Flash) у Non-Thinking mode, інтерактивним GUI-налаштуванням мови і ключів, стрімінгом відповідей у реальному часі та фінальним виведенням у форматі коду для копіювання в один клік.

---

### Етапи виконання

- [x] **Етап 1: Базова структура та безпека**
  - [x] Створення `.gitignore` (ігнорування секретів, `.env`, бази даних `*.db`)
  - [x] Створення `.env.example` та шаблону конфігурації
  - [x] Налаштування залежностей (`requirements.txt`, `pyproject.toml`)
  - [x] Модуль конфігурації `src/config.py`

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
  - [x] Диспетчер та фабрика провайдерів (`src/services/manager.py`) з підтримкою єдиного ключа OpenRouter

- [x] **Етап 4: Інтерфейс Telegram (GUI на кнопках, FSM та стрімінг)**
  - [x] Inline-клавіатури для головного меню налаштувань, вибору моделі, зміни мови, керування API ключами (`src/keyboards/inline.py`)
  - [x] FSM-хендлери для введення мови текстом та додавання ключів з автовидаленням введеного ключа з чату (`src/handlers/settings.py`)
  - [x] Основний хендлер перекладу зі стрімінг-троттлінгом, видаленням проміжного стріму та відправкою результату у `<code>...</code>` для миттєвого Tap-to-Copy (`src/handlers/translation.py`)
  - [x] Додавання inline-кнопки `[ ⚙️ Settings ]` безпосередньо під кожним перекладеним повідомленням
  - [x] Постійна клавіатура доступу до налаштувань та допомоги (`src/keyboards/reply.py`)
  - [x] Реєстрація системного меню команд Telegram (`BotCommand`) у `src/main.py`
  - [x] Точка входу бота (`src/main.py`)

- [x] **Етап 5: Мультимовна нормалізація назв мов та інтеграція з DeepL/OpenAI**
  - [x] Створення інтелектуального модуля нормалізації мов (`src/services/language_normalizer.py`) з підтримкою українських назв ("Португальська", "Німецька", "Іспанська" тощо) та AI resolution.
  - [x] Автоматичний мапінг на офіційні коди DeepL (`PT-PT`, `DE`, `PL`, `ES` тощо) та валідація непідтримуваних мов з підказкою перемкнутись на LLM.

- [x] **Етап 6: Тестування (паралельний запуск)**
  - [x] Модульні тести детектора мов
  - [x] Тести бази даних
  - [x] Тести OpenRouter та DeepL провайдерів
  - [x] Тести нормалізатора мов та DeepL мапінгу (`tests/test_normalizer.py`)
  - [x] Тести клавіатур та меню (`tests/test_keyboards.py`)
  - [x] Тести менеджеру з уніфікованим OpenRouter ключем (`tests/test_manager.py`)
  - [x] Запуск тестів через `pytest -n auto` (23 тести пройдено успішно)

- [x] **Етап 7: Розгортання та Документація**
  - [x] Створення systemd сервісу (`systemd/tg-translator.service`)
  - [x] Створення та оновлення `README.md`, `CHANGELOG.md` з інструкцією по реєстрації та отриманню ключів OpenRouter
  - [x] Оновлення `TASK.md` та `WALKTHROUGH.md`
