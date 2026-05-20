"""Tests for morse-code/converter.py — no CGEventTap, no PyObjC UI."""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from converter import (
    text_to_morse,
    morse_to_text,
    is_morse,
    detect_lang,
    EN_TO_MORSE,
    THAI_TO_MORSE,
    MORSE_TO_EN,
    MORSE_TO_THAI,
)


# ── Mapping integrity ─────────────────────────────────────────────────────────

class TestMappingIntegrity:
    def test_en_morse_codes_unique(self):
        codes = list(EN_TO_MORSE.values())
        assert len(codes) == len(set(codes)), "EN Morse codes must be unique"

    def test_thai_morse_codes_unique(self):
        codes = list(THAI_TO_MORSE.values())
        assert len(codes) == len(set(codes)), "Thai Morse codes must be unique"

    def test_en_inverse_complete(self):
        for ch, code in EN_TO_MORSE.items():
            assert code in MORSE_TO_EN, f"Missing inverse for EN '{ch}': {code}"

    def test_thai_inverse_complete(self):
        for ch, code in THAI_TO_MORSE.items():
            assert code in MORSE_TO_THAI, f"Missing inverse for Thai '{ch}': {code}"

    def test_all_44_thai_consonants_present(self):
        consonants = set("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")
        assert consonants.issubset(set(THAI_TO_MORSE.keys()))

    def test_thai_vowels_present(self):
        vowels = set("าัิีุูเแโไ่้ำึื")
        assert vowels.issubset(set(THAI_TO_MORSE.keys()))

    def test_thai_symbols_present(self):
        symbols = set("ใะ็์ๆ")
        assert symbols.issubset(set(THAI_TO_MORSE.keys()))

    def test_sawatdii_roundtrip(self):
        word = "สวัสดี"
        assert morse_to_text(text_to_morse(word, "th"), "th") == word

    def test_mixed_thai_english_no_question_marks(self):
        # Mixed text should encode without '?' for known chars in either language
        result = text_to_morse("Hi สวัสดี", "th")
        assert "?" not in result

    def test_mixed_english_thai_fallback(self):
        # English chars in Thai-detected context use EN Morse codes via fallback
        result = text_to_morse("A", "th")   # 'A' not in THAI_TO_MORSE
        assert result == ".-"               # falls back to EN code for A

    def test_hyphen_in_thai_text_not_morse(self):
        assert is_morse("ค่า-ใช้จ่าย") is False

    def test_hyphen_in_english_text_not_morse(self):
        assert is_morse("cost-benefit") is False


# ── English text → Morse ──────────────────────────────────────────────────────

class TestEnglishToMorse:
    def test_sos(self):
        assert text_to_morse("SOS") == "... --- ..."

    def test_lowercase_normalised(self):
        assert text_to_morse("sos") == "... --- ..."

    def test_single_letter(self):
        assert text_to_morse("E") == "."

    def test_word_with_space(self):
        result = text_to_morse("HI HO")
        assert result == ".... .. / .... ---"

    def test_numbers(self):
        assert text_to_morse("1") == ".----"
        assert text_to_morse("0") == "-----"

    def test_unknown_char_placeholder(self):
        assert "?" in text_to_morse("A#B")

    def test_empty_string(self):
        assert text_to_morse("") == ""


# ── Morse → English text ──────────────────────────────────────────────────────

class TestMorseToEnglish:
    def test_sos(self):
        assert morse_to_text("... --- ...") == "SOS"

    def test_word_separator_slash(self):
        assert morse_to_text(".... .. / .... ---") == "HI HO"

    def test_word_separator_spaced(self):
        assert morse_to_text(".... .. / .... ---") == "HI HO"

    def test_unknown_code(self):
        result = morse_to_text("..........", lang="en")
        assert "[???]" in result

    def test_roundtrip(self):
        original = "HELLO WORLD"
        assert morse_to_text(text_to_morse(original)) == original

    def test_empty_string(self):
        assert morse_to_text("") == ""


# ── Thai text → Morse ─────────────────────────────────────────────────────────

class TestThaiToMorse:
    def test_single_consonant_gor(self):
        assert text_to_morse("ก", lang="th") == ".."

    def test_single_consonant_nor(self):
        assert text_to_morse("น", lang="th") == ".-"

    def test_multi_consonant(self):
        result = text_to_morse("กน", lang="th")
        assert result == ".. .-"

    def test_word_with_space(self):
        result = text_to_morse("ก น", lang="th")
        assert result == ".. / .-"


# ── Morse → Thai text ─────────────────────────────────────────────────────────

class TestMorseToThai:
    def test_gor(self):
        assert morse_to_text("..", lang="th") == "ก"

    def test_nor(self):
        assert morse_to_text(".-", lang="th") == "น"

    def test_roundtrip(self):
        original = "กนมว"
        assert morse_to_text(text_to_morse(original, lang="th"), lang="th") == original

    def test_word_separator(self):
        result = morse_to_text(".. / .-", lang="th")
        assert result == "ก น"


# ── is_morse detection ────────────────────────────────────────────────────────

class TestIsMorse:
    def test_valid_morse(self):
        assert is_morse("... --- ...") is True

    def test_with_slash_separator(self):
        assert is_morse(".- / -...") is True

    def test_english_text_not_morse(self):
        assert is_morse("HELLO") is False

    def test_thai_text_not_morse(self):
        assert is_morse("กน") is False

    def test_empty_string_not_morse(self):
        assert is_morse("") is False

    def test_whitespace_only_not_morse(self):
        assert is_morse("   ") is False

    def test_slash_only_not_morse(self):
        assert is_morse("/") is False

    def test_space_slash_space_not_morse(self):
        assert is_morse(" / ") is False

    def test_single_dash_not_morse(self):
        # A bare "-" (hyphen in regular text) must NOT trigger Morse detection
        assert is_morse("-") is False

    def test_single_dot_not_morse(self):
        assert is_morse(".") is False

    def test_two_chars_is_morse(self):
        assert is_morse("..") is True
        assert is_morse(".-") is True


# ── detect_lang ───────────────────────────────────────────────────────────────

class TestDetectLang:
    def test_english_text(self):
        assert detect_lang("HELLO") == "en"

    def test_thai_text(self):
        assert detect_lang("กนมว") == "th"

    def test_mixed_defaults_to_thai(self):
        assert detect_lang("hello กน") == "th"

    def test_numbers_default_to_en(self):
        assert detect_lang("12345") == "en"

    def test_morse_symbols_default_to_en(self):
        assert detect_lang("... --- ...") == "en"
