import re
from typing import Tuple
import langdetect
from langdetect import DetectorFactory

# Enforce deterministic results for langdetect
DetectorFactory.seed = 0

# Unique Ukrainian characters that definitely identify Ukrainian text
UKRAINIAN_EXCLUSIVE_CHARS = set("іїєґІЇЄҐ")
CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")


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
        Detects whether the text is Ukrainian or another language.
        Returns:
            is_ukrainian: bool
            detected_code: str (ISO language code e.g. 'uk', 'en', 'de')
            detected_name: str (Human-readable name e.g. 'Ukrainian', 'English')
        """
        clean_text = text.strip()
        if not clean_text:
            return False, "unknown", "Unknown"

        # 1. Quick check for unique Ukrainian characters
        has_ukr_chars = any(c in UKRAINIAN_EXCLUSIVE_CHARS for c in clean_text)
        
        # Check cyrillic presence
        cyrillic_chars = CYRILLIC_PATTERN.findall(clean_text)
        is_predominantly_cyrillic = len(cyrillic_chars) > (len(clean_text.replace(" ", "")) * 0.3)

        if has_ukr_chars:
            return True, "uk", "Ukrainian"

        # 2. Use langdetect for general detection
        try:
            detected_code = langdetect.detect(clean_text).lower()
        except Exception:
            detected_code = "uk" if is_predominantly_cyrillic else "en"

        # If detected as Ukrainian
        if detected_code == "uk":
            return True, "uk", "Ukrainian"

        # If it's predominantly cyrillic but not clearly Russian or other, and contains common words
        lang_name = LANGUAGE_NAMES_MAP.get(detected_code, detected_code.upper())
        return False, detected_code, lang_name


language_detector = LanguageDetector()
