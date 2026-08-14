import pytest
from src.services.detector import language_detector


def test_detect_ukrainian_with_specific_chars():
    text1 = "Привіт, як твої справи сьогодні?"
    is_ukr, code, name = language_detector.detect(text1)
    assert is_ukr is True
    assert code == "uk"
    assert name == "Ukrainian"

    text2 = "Це чудова їжа та єнот"
    is_ukr, code, name = language_detector.detect(text2)
    assert is_ukr is True
    assert code == "uk"


def test_detect_ukrainian_slang_and_colloquial():
    is_ukr, code, name = language_detector.detect("шо ти, голова")
    assert is_ukr is True
    assert code == "uk"
    assert name == "Ukrainian"

    is_ukr2, code2, name2 = language_detector.detect("шо робиш, брате?")
    assert is_ukr2 is True
    assert code2 == "uk"


def test_detect_russian():
    is_ukr, code, name = language_detector.detect("Привет, как дела? Что делаешь?")
    assert is_ukr is False
    assert code == "ru"
    assert name == "Russian"


def test_detect_english():
    text = "Hello, how are you doing today? I hope everything is well."
    is_ukr, code, name = language_detector.detect(text)
    assert is_ukr is False
    assert code == "en"
    assert name == "English"


def test_detect_german():
    text = "Guten Tag, wie geht es Ihnen heute? Ich wünsche Ihnen einen schönen Tag."
    is_ukr, code, name = language_detector.detect(text)
    assert is_ukr is False
    assert code == "de"
    assert name == "German"


def test_detect_polish():
    text = "Cześć, jak się masz? Mam nadzieję, że wszystko w porządku."
    is_ukr, code, name = language_detector.detect(text)
    assert is_ukr is False
    assert code == "pl"
    assert name == "Polish"


def test_detect_empty_text():
    is_ukr, code, name = language_detector.detect("   ")
    assert is_ukr is False
    assert code == "unknown"
