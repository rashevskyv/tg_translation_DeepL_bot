import json
import logging
import re
from typing import Dict, NamedTuple, Optional
from openai import AsyncOpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class LanguageInfo(NamedTuple):
    canonical_name: str
    deepl_target_code: Optional[str]
    deepl_source_code: Optional[str]
    iso_code: str


# Comprehensive static dictionary for zero-latency, high-accuracy mapping
KNOWN_LANGUAGES: Dict[str, LanguageInfo] = {
    # Ukrainian
    "ukrainian": LanguageInfo("Ukrainian", "UK", "UK", "uk"),
    "українська": LanguageInfo("Ukrainian", "UK", "UK", "uk"),
    "украинский": LanguageInfo("Ukrainian", "UK", "UK", "uk"),
    "uk": LanguageInfo("Ukrainian", "UK", "UK", "uk"),
    "ua": LanguageInfo("Ukrainian", "UK", "UK", "uk"),

    # Portuguese
    "portuguese": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "португальська": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "португальский": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "португальська (португалія)": LanguageInfo("Portuguese (Portugal)", "PT-PT", "PT", "pt-pt"),
    "португальська (бразилія)": LanguageInfo("Portuguese (Brazil)", "PT-BR", "PT", "pt-br"),
    "portugues": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "português": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "pt": LanguageInfo("Portuguese", "PT-PT", "PT", "pt"),
    "pt-pt": LanguageInfo("Portuguese (Portugal)", "PT-PT", "PT", "pt-pt"),
    "pt-br": LanguageInfo("Portuguese (Brazil)", "PT-BR", "PT", "pt-br"),

    # English
    "english": LanguageInfo("English", "EN-US", "EN", "en"),
    "англійська": LanguageInfo("English", "EN-US", "EN", "en"),
    "английский": LanguageInfo("English", "EN-US", "EN", "en"),
    "en": LanguageInfo("English", "EN-US", "EN", "en"),
    "en-us": LanguageInfo("English (US)", "EN-US", "EN", "en-us"),
    "en-gb": LanguageInfo("English (UK)", "EN-GB", "EN", "en-gb"),

    # German
    "german": LanguageInfo("German", "DE", "DE", "de"),
    "німецька": LanguageInfo("German", "DE", "DE", "de"),
    "немецкий": LanguageInfo("German", "DE", "DE", "de"),
    "deutsch": LanguageInfo("German", "DE", "DE", "de"),
    "de": LanguageInfo("German", "DE", "DE", "de"),

    # Polish
    "polish": LanguageInfo("Polish", "PL", "PL", "pl"),
    "польська": LanguageInfo("Polish", "PL", "PL", "pl"),
    "польский": LanguageInfo("Polish", "PL", "PL", "pl"),
    "polski": LanguageInfo("Polish", "PL", "PL", "pl"),
    "pl": LanguageInfo("Polish", "PL", "PL", "pl"),

    # Spanish
    "spanish": LanguageInfo("Spanish", "ES", "ES", "es"),
    "іспанська": LanguageInfo("Spanish", "ES", "ES", "es"),
    "испанский": LanguageInfo("Spanish", "ES", "ES", "es"),
    "espanol": LanguageInfo("Spanish", "ES", "ES", "es"),
    "español": LanguageInfo("Spanish", "ES", "ES", "es"),
    "es": LanguageInfo("Spanish", "ES", "ES", "es"),

    # French
    "french": LanguageInfo("French", "FR", "FR", "fr"),
    "французька": LanguageInfo("French", "FR", "FR", "fr"),
    "французский": LanguageInfo("French", "FR", "FR", "fr"),
    "francais": LanguageInfo("French", "FR", "FR", "fr"),
    "français": LanguageInfo("French", "FR", "FR", "fr"),
    "fr": LanguageInfo("French", "FR", "FR", "fr"),

    # Italian
    "italian": LanguageInfo("Italian", "IT", "IT", "it"),
    "італійська": LanguageInfo("Italian", "IT", "IT", "it"),
    "итальянский": LanguageInfo("Italian", "IT", "IT", "it"),
    "italiano": LanguageInfo("Italian", "IT", "IT", "it"),
    "it": LanguageInfo("Italian", "IT", "IT", "it"),

    # Czech
    "czech": LanguageInfo("Czech", "CS", "CS", "cs"),
    "чеська": LanguageInfo("Czech", "CS", "CS", "cs"),
    "чешский": LanguageInfo("Czech", "CS", "CS", "cs"),
    "cesky": LanguageInfo("Czech", "CS", "CS", "cs"),
    "cs": LanguageInfo("Czech", "CS", "CS", "cs"),
    "cz": LanguageInfo("Czech", "CS", "CS", "cs"),

    # Slovak
    "slovak": LanguageInfo("Slovak", "SK", "SK", "sk"),
    "словацька": LanguageInfo("Slovak", "SK", "SK", "sk"),
    "словацкий": LanguageInfo("Slovak", "SK", "SK", "sk"),
    "slovensky": LanguageInfo("Slovak", "SK", "SK", "sk"),
    "sk": LanguageInfo("Slovak", "SK", "SK", "sk"),

    # Japanese
    "japanese": LanguageInfo("Japanese", "JA", "JA", "ja"),
    "японська": LanguageInfo("Japanese", "JA", "JA", "ja"),
    "японский": LanguageInfo("Japanese", "JA", "JA", "ja"),
    "nihongo": LanguageInfo("Japanese", "JA", "JA", "ja"),
    "ja": LanguageInfo("Japanese", "JA", "JA", "ja"),
    "jp": LanguageInfo("Japanese", "JA", "JA", "ja"),

    # Chinese
    "chinese": LanguageInfo("Chinese", "ZH", "ZH", "zh"),
    "китайська": LanguageInfo("Chinese", "ZH", "ZH", "zh"),
    "китайский": LanguageInfo("Chinese", "ZH", "ZH", "zh"),
    "zh": LanguageInfo("Chinese", "ZH", "ZH", "zh"),
    "cn": LanguageInfo("Chinese", "ZH", "ZH", "zh"),

    # Dutch
    "dutch": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "нідерландська": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "голландська": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "нидерландский": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "голландский": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "nederlands": LanguageInfo("Dutch", "NL", "NL", "nl"),
    "nl": LanguageInfo("Dutch", "NL", "NL", "nl"),

    # Swedish
    "swedish": LanguageInfo("Swedish", "SV", "SV", "sv"),
    "шведська": LanguageInfo("Swedish", "SV", "SV", "sv"),
    "шведский": LanguageInfo("Swedish", "SV", "SV", "sv"),
    "svenska": LanguageInfo("Swedish", "SV", "SV", "sv"),
    "sv": LanguageInfo("Swedish", "SV", "SV", "sv"),
    "se": LanguageInfo("Swedish", "SV", "SV", "sv"),

    # Danish
    "danish": LanguageInfo("Danish", "DA", "DA", "da"),
    "данська": LanguageInfo("Danish", "DA", "DA", "da"),
    "датский": LanguageInfo("Danish", "DA", "DA", "da"),
    "dansk": LanguageInfo("Danish", "DA", "DA", "da"),
    "da": LanguageInfo("Danish", "DA", "DA", "da"),
    "dk": LanguageInfo("Danish", "DA", "DA", "da"),

    # Finnish
    "finnish": LanguageInfo("Finnish", "FI", "FI", "fi"),
    "фінська": LanguageInfo("Finnish", "FI", "FI", "fi"),
    "финский": LanguageInfo("Finnish", "FI", "FI", "fi"),
    "suomi": LanguageInfo("Finnish", "FI", "FI", "fi"),
    "fi": LanguageInfo("Finnish", "FI", "FI", "fi"),

    # Norwegian
    "norwegian": LanguageInfo("Norwegian", "NB", "NB", "no"),
    "норвезька": LanguageInfo("Norwegian", "NB", "NB", "no"),
    "норвежский": LanguageInfo("Norwegian", "NB", "NB", "no"),
    "norsk": LanguageInfo("Norwegian", "NB", "NB", "no"),
    "no": LanguageInfo("Norwegian", "NB", "NB", "no"),
    "nb": LanguageInfo("Norwegian", "NB", "NB", "nb"),

    # Turkish
    "turkish": LanguageInfo("Turkish", "TR", "TR", "tr"),
    "турецька": LanguageInfo("Turkish", "TR", "TR", "tr"),
    "турецкий": LanguageInfo("Turkish", "TR", "TR", "tr"),
    "turkce": LanguageInfo("Turkish", "TR", "TR", "tr"),
    "tr": LanguageInfo("Turkish", "TR", "TR", "tr"),

    # Arabic
    "arabic": LanguageInfo("Arabic", "AR", "AR", "ar"),
    "арабська": LanguageInfo("Arabic", "AR", "AR", "ar"),
    "арабский": LanguageInfo("Arabic", "AR", "AR", "ar"),
    "ar": LanguageInfo("Arabic", "AR", "AR", "ar"),

    # Greek
    "greek": LanguageInfo("Greek", "EL", "EL", "el"),
    "грецька": LanguageInfo("Greek", "EL", "EL", "el"),
    "греческий": LanguageInfo("Greek", "EL", "EL", "el"),
    "el": LanguageInfo("Greek", "EL", "EL", "el"),
    "gr": LanguageInfo("Greek", "EL", "EL", "el"),

    # Bulgarian
    "bulgarian": LanguageInfo("Bulgarian", "BG", "BG", "bg"),
    "болгарська": LanguageInfo("Bulgarian", "BG", "BG", "bg"),
    "болгарский": LanguageInfo("Bulgarian", "BG", "BG", "bg"),
    "bg": LanguageInfo("Bulgarian", "BG", "BG", "bg"),

    # Hungarian
    "hungarian": LanguageInfo("Hungarian", "HU", "HU", "hu"),
    "угорська": LanguageInfo("Hungarian", "HU", "HU", "hu"),
    "венгерский": LanguageInfo("Hungarian", "HU", "HU", "hu"),
    "magyar": LanguageInfo("Hungarian", "HU", "HU", "hu"),
    "hu": LanguageInfo("Hungarian", "HU", "HU", "hu"),

    # Romanian
    "romanian": LanguageInfo("Romanian", "RO", "RO", "ro"),
    "румунська": LanguageInfo("Romanian", "RO", "RO", "ro"),
    "румынский": LanguageInfo("Romanian", "RO", "RO", "ro"),
    "ro": LanguageInfo("Romanian", "RO", "RO", "ro"),

    # Estonian
    "estonian": LanguageInfo("Estonian", "ET", "ET", "et"),
    "естонська": LanguageInfo("Estonian", "ET", "ET", "et"),
    "эстонский": LanguageInfo("Estonian", "ET", "ET", "et"),
    "et": LanguageInfo("Estonian", "ET", "ET", "et"),
    "ee": LanguageInfo("Estonian", "ET", "ET", "et"),

    # Lithuanian
    "lithuanian": LanguageInfo("Lithuanian", "LT", "LT", "lt"),
    "литовська": LanguageInfo("Lithuanian", "LT", "LT", "lt"),
    "литовский": LanguageInfo("Lithuanian", "LT", "LT", "lt"),
    "lt": LanguageInfo("Lithuanian", "LT", "LT", "lt"),

    # Latvian
    "latvian": LanguageInfo("Latvian", "LV", "LV", "lv"),
    "латиська": LanguageInfo("Latvian", "LV", "LV", "lv"),
    "латышский": LanguageInfo("Latvian", "LV", "LV", "lv"),
    "lv": LanguageInfo("Latvian", "LV", "LV", "lv"),

    # Slovenian
    "slovenian": LanguageInfo("Slovenian", "SL", "SL", "sl"),
    "словенська": LanguageInfo("Slovenian", "SL", "SL", "sl"),
    "словенский": LanguageInfo("Slovenian", "SL", "SL", "sl"),
    "sl": LanguageInfo("Slovenian", "SL", "SL", "sl"),

    # Indonesian
    "indonesian": LanguageInfo("Indonesian", "ID", "ID", "id"),
    "індонезійська": LanguageInfo("Indonesian", "ID", "ID", "id"),
    "индонезийский": LanguageInfo("Indonesian", "ID", "ID", "id"),
    "id": LanguageInfo("Indonesian", "ID", "ID", "id"),

    # Korean
    "korean": LanguageInfo("Korean", "KO", "KO", "ko"),
    "корейська": LanguageInfo("Korean", "KO", "KO", "ko"),
    "корейский": LanguageInfo("Korean", "KO", "KO", "ko"),
    "ko": LanguageInfo("Korean", "KO", "KO", "ko"),
    "kr": LanguageInfo("Korean", "KO", "KO", "ko"),

    # Russian
    "russian": LanguageInfo("Russian", "RU", "RU", "ru"),
    "російська": LanguageInfo("Russian", "RU", "RU", "ru"),
    "русский": LanguageInfo("Russian", "RU", "RU", "ru"),
    "ru": LanguageInfo("Russian", "RU", "RU", "ru"),

    # Hebrew (Non-DeepL, but supported by LLMs)
    "hebrew": LanguageInfo("Hebrew", None, None, "he"),
    "іврит": LanguageInfo("Hebrew", None, None, "he"),
    "иврит": LanguageInfo("Hebrew", None, None, "he"),
    "he": LanguageInfo("Hebrew", None, None, "he"),

    # Georgian (Non-DeepL, but supported by LLMs)
    "georgian": LanguageInfo("Georgian", None, None, "ka"),
    "грузинська": LanguageInfo("Georgian", None, None, "ka"),
    "грузинский": LanguageInfo("Georgian", None, None, "ka"),
    "ka": LanguageInfo("Georgian", None, None, "ka"),

    # Hindi (Non-DeepL, but supported by LLMs)
    "hindi": LanguageInfo("Hindi", None, None, "hi"),
    "гінді": LanguageInfo("Hindi", None, None, "hi"),
    "хинди": LanguageInfo("Hindi", None, None, "hi"),
    "hi": LanguageInfo("Hindi", None, None, "hi"),
}


# Valid DeepL target codes set for fast validation
DEEPL_VALID_TARGET_CODES = {
    "AR", "BG", "CS", "DA", "DE", "EL", "EN", "EN-GB", "EN-US", "ES",
    "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV",
    "NB", "NL", "PL", "PT", "PT-BR", "PT-PT", "RO", "RU", "SK", "SL",
    "SV", "TR", "UK", "ZH", "ZH-HANS"
}


async def _resolve_with_deepseek_v4(user_input: str, openrouter_api_key: str) -> Optional[LanguageInfo]:
    """
    Uses DeepSeek V4 Flash via OpenRouter (ultra-low cost and fast) to extract
    the intended target language from free-form user utterance/instructions.
    """
    try:
        client = AsyncOpenAI(
            api_key=openrouter_api_key.strip(),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/rashevskyv/tg_translation_DeepL_bot",
                "X-Title": "TG Translation Bot",
            },
        )
        system_prompt = (
            "You are a target language extraction engine. The user sends a command, utterance, or sentence "
            "requesting a target translation language (e.g. 'хочу перекладати на португальську, європейський варіант', "
            "'зроби німецьку будь ласка', 'перемкни на польську', 'american english', 'японська').\n"
            "Analyze the text, extract the requested language, and resolve it strictly to valid DeepL API target standards where possible.\n"
            "Return JSON only with keys:\n"
            "- 'canonical_name': Standard capitalized English name (e.g. 'Portuguese', 'German', 'Polish', 'English', 'Spanish', 'French', 'Japanese')\n"
            "- 'iso_code': 2-letter ISO 639-1 code (e.g. 'pt', 'de', 'pl', 'en', 'es', 'ja')\n"
            "- 'deepl_target_code': Official DeepL target code (e.g. 'PT-PT', 'PT-BR', 'DE', 'PL', 'EN-US', 'EN-GB', 'ES', 'FR', 'JA', 'UK') or null if not supported by DeepL\n"
            "- 'deepl_source_code': Official DeepL source code (e.g. 'PT', 'DE', 'PL', 'EN', 'ES', 'JA', 'UK') or null."
        )
        response = await client.chat.completions.create(
            model="deepseek/deepseek-v4-flash-0731",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
            extra_body={"reasoning": {"effort": "none"}},
        )
        content = response.choices[0].message.content or ""
        # Clean potential markdown wrapping ```json ... ```
        clean_json = re.sub(r"^```(?:json)?\s*", "", content.strip(), flags=re.IGNORECASE)
        clean_json = re.sub(r"\s*```$", "", clean_json.strip())

        data = json.loads(clean_json)
        canonical = data.get("canonical_name", "").strip()
        iso = data.get("iso_code", "").strip().lower()
        deepl_tgt = data.get("deepl_target_code")
        deepl_src = data.get("deepl_source_code")
        if canonical:
            return LanguageInfo(
                canonical_name=canonical,
                deepl_target_code=deepl_tgt.upper() if deepl_tgt else None,
                deepl_source_code=deepl_src.upper() if deepl_src else None,
                iso_code=iso or "unknown",
            )
    except Exception as e:
        logger.warning(f"DeepSeek V4 language resolution error: {e}")
    return None


async def normalize_language(
    user_input: str,
    openrouter_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
) -> LanguageInfo:
    """
    Normalizes any user input or conversational utterance into a standard LanguageInfo object:
    1. Checks comprehensive local dictionary (instant lookup for single words/codes).
    2. Uses DeepSeek V4 Flash via OpenRouter for smart extraction of conversational requests.
    3. Fallback to clean title case.
    """
    clean_input = user_input.strip().lower()
    
    # 1. Fast dictionary lookup for exact single words / short terms
    if clean_input in KNOWN_LANGUAGES:
        return KNOWN_LANGUAGES[clean_input]

    # 2. DeepSeek V4 Flash resolution via OpenRouter
    or_key = openrouter_api_key or settings.openrouter_api_key
    if or_key:
        ai_res = await _resolve_with_deepseek_v4(user_input, or_key)
        if ai_res:
            return ai_res

    # 3. Fallback: assume clean title case
    clean_title = user_input.strip().capitalize()
    return LanguageInfo(
        canonical_name=clean_title,
        deepl_target_code=clean_title.upper()[:2] if clean_title.isascii() and len(clean_title) >= 2 else None,
        deepl_source_code=clean_title.upper()[:2] if clean_title.isascii() and len(clean_title) >= 2 else None,
        iso_code=clean_title.lower()[:2] if clean_title.isascii() else "unknown",
    )
