# Журнал змін (Walkthrough)

## Версія: v0.6.1 (Виправлення експорту language_normalizer та DEEPL_VALID_TARGET_CODES)

### Зміни:
1. **Виправлено імпорт у `src/services/language_normalizer.py`:**
   - Експортовано екземпляр класу `language_normalizer` (`LanguageNormalizer`) та множину `DEEPL_VALID_TARGET_CODES`.
   - Усунено помилку `ImportError: cannot import name 'language_normalizer'` при запуску сервісу на сервері.

2. **Тестування:**
   - Всі 33 тести успішно виконані паралельно (`pytest -n auto`).

---

## Версія: v0.6.0 (Розширення лінійки моделей: Qwen 3.7 Flash та Mistral Small 3)
- Інтеграція Qwen 3.7 Flash та Mistral Small 3.

---

## Версія: v0.5.5 (Оновлення моделей OpenRouter та повна українізація меню налаштувань)
- Gemini 3.5/3.7, GPT-5.6 Luna, DeepSeek V4 Flash.
