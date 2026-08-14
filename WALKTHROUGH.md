# Журнал змін (Walkthrough)

## Версія: v0.1.4 (Виправлення фільтрації aiogram 3 для команд та кнопок)

### Зміни:
1. **Виправлення помилки фільтрів aiogram (`TypeError: unsupported operand type(s) for |: 'Command' and 'bool'`):**
   - У [src/handlers/settings.py](file:///d:/git/dev/tg_translation_DeepL_bot/src/handlers/settings.py) замінено некоректне об'єднання `Command(...) | F.text...` на окремі декоратори `@settings_router.message(Command(...))` та `@settings_router.message(F.text.in_(...))`.
   - Тепер команди `/settings`, `/help`, а також натискання кнопок `⚙️ Settings`, `ℹ️ Help` на клавіатурі обробляються стабільно без жодних виключень.

2. **Тестування:**
   - Всі 22 тести успішно пройшли паралельно (`pytest -n auto`).

---

## Версія: v0.1.3 (Оновлено формат нативного Tap-to-Copy копіювання `<code>`)
- Замінено `<pre><code>...</code></pre>` на інлайн-моноширинний тег `<code>...</code>` у `src/handlers/translation.py`.

---

## Версія: v0.1.2 (Додано постійну кнопку налаштувань ⚙️ Settings та меню команд)
- Постійна нижня клавіатура `[⚙️ Settings]` та `[ℹ️ Help]` (`src/keyboards/reply.py`).
- Реєстрація системного меню команд Telegram (`bot.set_my_commands`).

---

## Версія: v0.1.1 (Виправлення розпізнавання мов та інтеграція нормалізатора DeepL/OpenAI)
- Інтелектуальний нормалізатор мов (`src/services/language_normalizer.py`).
- Запобігання помилці DeepL 400 Bad Request.

---

## Версія: v0.1.0 (Ініціалізація та перший реліз)
- Мультипровайдерність (DeepL, OpenAI, Gemini, Qwen, DeepSeek).
- Двонаправлений переклад (UA $\leftrightarrow$ Foreign).
- Стрімінг та One-Click копіювання в тегах коду.
- Локальне SQLite сховище.
