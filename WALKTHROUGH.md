# Журнал змін (Walkthrough)

## Версія: v0.2.2 (Автоматизований скрипт деплою в домашній каталог root)

### Зміни:
1. **Скрипт та команда One-Liner деплою (`scripts/deploy.sh`):**
   - Розгортання в каталог користувача `~/tg_translation_DeepL_bot` (без `/opt`).
   - Автоматичне встановлення Python venv, конфігурація `.env`, налаштування SQLite ключів для адмінів та реєстрація сервісу `tg-translator.service`.
2. **Оновлено systemd unit (`systemd/tg-translator.service`):**
   - Адаптовано робочу директорію під `root` (`/root/tg_translation_DeepL_bot`).

---

## Версія: v0.2.1 (Інструменти призначення ключів користувачам & Адміністрування)
- CLI утиліта `src/tools/manage_user.py`.
- Telegram адмін-команди `/assign_key` та `/user_info`.

---

## Версія: v0.2.0 (Інтеграція OpenRouter та нових розумних моделей у Non-Thinking mode)
- Інтеграція OpenRouter (Gemini 3.5, Gemini 3.7, GPT-5.6 Luna, DeepSeek V4).
- Standalone DeepL.

---

## Версія: v0.1.5 (Додано кнопку ⚙️ Settings під кожною відповіддю перекладу)
- Інлайн-кнопка під кожним перекладеним повідомленням.
