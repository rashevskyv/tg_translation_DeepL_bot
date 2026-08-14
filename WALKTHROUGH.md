# Журнал змін (Walkthrough)

## Версія: v0.1.2 (Додано постійну кнопку налаштувань ⚙️ Settings та меню команд)

### Зміни:
1. **Постійна нижня клавіатура (Reply Keyboard):**
   - Створено `src/keyboards/reply.py` з кнопками `[⚙️ Settings]` та `[ℹ️ Help]`. Клавіатура закріплена під полем введення повідомлення (`is_persistent=True`, `resize_keyboard=True`).
   - Натискання на кнопку `⚙️ Settings` (або `⚙️ Налаштування`) миттєво відкриває інтерфейс налаштувань.
   - Натискання на `ℹ️ Help` відкриває довідку.

2. **Нативне меню команд Telegram (Menu Button):**
   - У `src/main.py` додано виклик `bot.set_my_commands()` для реєстрації системного меню:
     - `/settings` - ⚙️ Open settings (Languages, Engines, API keys)
     - `/start` - 🚀 Start bot & view current preferences
     - `/help` - 📖 Help & Supported providers guide
   - Завдяки цьому в Telegram-клієнті з'являється офіційна синя кнопка «Menu / Меню» ліворуч від поля вводу.

3. **Тестування:**
   - Додано `tests/test_keyboards.py`.
   - Всі 22 тести успішно пройшли паралельно (`pytest -n auto`).

---

## Версія: v0.1.1 (Виправлення розпізнавання мов та інтеграція нормалізатора DeepL/OpenAI)

### Зміни:
- Інтелектуальний нормалізатор мов (`src/services/language_normalizer.py`) для обробки українських назв мов («Португальська» $\rightarrow$ «Portuguese» / `PT-PT`).
- Запобігання помилці DeepL 400 Bad Request.

---

## Версія: v0.1.0 (Ініціалізація та перший реліз)
- Підтримка 5 провайдерів (DeepL, OpenAI, Gemini, Qwen, DeepSeek).
- Автоматичний переклад (UA $\leftrightarrow$ Foreign).
- Стрімінг та One-Click копіювання в тегах коду.
- Локальне SQLite сховище.
