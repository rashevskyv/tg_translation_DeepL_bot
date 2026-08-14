import re
from typing import Tuple
import langdetect
from langdetect import DetectorFactory

# Enforce deterministic results for langdetect
DetectorFactory.seed = 0

# Distinctive character sets
UKRAINIAN_EXCLUSIVE_CHARS = set("іїєґІЇЄҐ")
RUSSIAN_EXCLUSIVE_CHARS = set("ыэъёЫЭЪЁ")
CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")

# Common Ukrainian words and colloquial markers
UKRAINIAN_MARKERS = {
    "шо", "ти", "як", "це", "де", "хто", "чому", "навіщо", "шось", "хтось",
    "привіт", "дякую", "бувай", "голова", "брате", "брат", "чувак", "робиш",
    "робити", "треба", "можна", "тут", "там", "був", "була", "були", "буде",
    "буду", "дуже", "гарно", "добре", "сьогодні", "завтра", "вчора", "зараз",
    "також", "якось", "який", "яка", "яке", "які", "мене", "тебе", "його",
    "її", "нас", "вас", "їх", "собі", "чи", "або", "бо", "але", "тобто",
    "вже", "ще", "ні", "так", "ось", "чудово", "файно", "тре", "дяка", "прівєт"
}

RUSSIAN_MARKERS = {
    "что", "это", "как", "где", "кто", "почему", "зачем", "что-то", "кто-то",
    "привет", "спасибо", "пока", "делаешь", "делать", "надо", "можно", "здесь",
    "сегодня", "завтра", "вчера", "сейчас", "тоже", "какой", "меня", "тебя",
    "его", "нас", "вас", "их", "или", "но", "уже", "еще", "нет", "да", "вот"
}

LANGUAGE_NAMES_MAP = {
    "uk": "Ukrainian",
    "en": "English",
    "de": "German",
    "pl": "Polish",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "zh": "Chinese",
    "zh-cn": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "cs": "Czech",
    "sk": "Slovak",
    "tr": "Turkish",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "fi": "Finnish",
    "da": "Danish",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hu": "Hungarian",
    "el": "Greek",
    "ar": "Arabic",
}


class LanguageDetector:
    @staticmethod
    def detect(text: str) -> Tuple[bool, str, str]:
        """
        Detects whether the text is Ukrainian or a foreign language.
        Returns:
            is_ukrainian: bool
            detected_code: str (ISO language code e.g. 'uk', 'en', 'de')
            detected_name: str (Human-readable name e.g. 'Ukrainian', 'English')
        """
        clean_text = text.strip()
        if not clean_text:
            return False, "unknown", "Unknown"

        # 1. Quick check for unique Ukrainian characters (і, ї, є, ґ)
        if any(c in UKRAINIAN_EXCLUSIVE_CHARS for c in clean_text):
            return True, "uk", "Ukrainian"

        # 2. Check for Russian exclusive characters (ы, э, ъ, ё)
        if any(c in RUSSIAN_EXCLUSIVE_CHARS for c in clean_text):
            return False, "ru", "Russian"

        # 3. Check Cyrillic presence
        cyrillic_chars = CYRILLIC_PATTERN.findall(clean_text)
        non_space_len = len(clean_text.replace(" ", ""))
        is_predominantly_cyrillic = len(cyrillic_chars) > (non_space_len * 0.3)

        if is_predominantly_cyrillic:
            # Tokenize into clean lowercase words
            words = set(re.findall(r"\b[а-яА-ЯёЁіІїЇєЄґҐa-zA-Z]+\b", clean_text.lower()))

            has_ukr_marker = bool(words & UKRAINIAN_MARKERS)
            has_rus_marker = bool(words & RUSSIAN_MARKERS)

            if has_ukr_marker and not has_rus_marker:
                return True, "uk", "Ukrainian"

            if has_rus_marker and not has_ukr_marker:
                return False, "ru", "Russian"

            # Default heuristic for Cyrillic texts without explicit Russian letters:
            # For a Ukrainian translation bot, treat ambiguous cyrillic text as Ukrainian
            return True, "uk", "Ukrainian"

        # 4. Non-Cyrillic (Latin, Asian, Arabic, etc.) -> use langdetect
        try:
            detected_code = langdetect.detect(clean_text).lower()
        except Exception:
            detected_code = "en"

        lang_name = LANGUAGE_NAMES_MAP.get(detected_code, detected_code.upper())
        return False, detected_code, lang_name


language_detector = LanguageDetector()
