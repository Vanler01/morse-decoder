"""
Morse code conversion: English <-> Morse, Thai <-> Morse.

Thai covers 44 consonants + 15 vowels (sara) + 2 tone marks + sara am
+ 5 symbols = 64 characters total.  Vowels and tone marks are required
for readable Thai text.

Word separator in Morse output: ' / '  (space-slash-space).
Unknown chars: '?' when encoding, '[???]' when decoding.
"""
from __future__ import annotations

# ── English (ITU standard) ───────────────────────────────────────────────────
EN_TO_MORSE: dict[str, str] = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",   "E": ".",
    "F": "..-.",  "G": "--.",   "H": "....",  "I": "..",    "J": ".---",
    "K": "-.-",   "L": ".-..",  "M": "--",    "N": "-.",    "O": "---",
    "P": ".--.",  "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",
    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",  "Y": "-.--",
    "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.",
    "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",
    "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.",
    "$": "...-..-", "@": ".--.-.",
}
MORSE_TO_EN: dict[str, str] = {v: k for k, v in EN_TO_MORSE.items()}

# ── Thai (consonants + vowels + tone marks + symbols) ───────────────────────
# Codes are unique within Thai mode; they may overlap EN_TO_MORSE because
# language is always specified when decoding.
#
# Stored as (codepoint, morse) tuples so this file stays ASCII-safe.
#   2-el: ก น ม ว
#   3-el: ข ค ง ต ท บ ป ร
#   4-el: จ ช ซ ญ ด ถ ธ ณ พ ผ ฝ ฟ ภ ย ล ส
#   5-el (.): ฃ ฅ ฆ ฉ ฌ ฎ ฏ ฐ ฑ ฒ ห ฬ อ ฮ ศ ษ
#   5-el (-): า ั ิ ี ุ ู เ แ โ ไ ่ ้ ำ ึ ื
#   6-el: ใ ะ ็ ์ ๆ
_THAI_DATA: list[tuple[int, str]] = [
    (0x0E01, '..'),
    (0x0E19, '.-'),
    (0x0E21, '-.'),
    (0x0E27, '--'),
    (0x0E02, '...'),
    (0x0E04, '..-'),
    (0x0E07, '.-.'),
    (0x0E15, '.--'),
    (0x0E17, '-..'),
    (0x0E1A, '-.-'),
    (0x0E1B, '--.'),
    (0x0E23, '---'),
    (0x0E08, '....'),
    (0x0E0A, '...-'),
    (0x0E0B, '..-.'),
    (0x0E0D, '..--'),
    (0x0E14, '.-..'),
    (0x0E16, '.-.-'),
    (0x0E18, '.--.'),
    (0x0E13, '.---'),
    (0x0E1E, '-...'),
    (0x0E1C, '-..-'),
    (0x0E1D, '-.-.'),
    (0x0E1F, '-.--'),
    (0x0E20, '--..'),
    (0x0E22, '--.-'),
    (0x0E25, '---.'),
    (0x0E2A, '----'),
    (0x0E03, '.....'),
    (0x0E05, '....-'),
    (0x0E06, '...-.'),
    (0x0E09, '...--'),
    (0x0E0C, '..-..'),
    (0x0E0E, '..-.-'),
    (0x0E0F, '..--.'),
    (0x0E10, '..---'),
    (0x0E11, '.-...'),
    (0x0E12, '.-..-'),
    (0x0E2B, '.-.-.'),
    (0x0E2C, '.--..'),
    (0x0E2D, '.--.-'),
    (0x0E2E, '.---.'),
    (0x0E28, '.----'),
    (0x0E29, '-....'),
    (0x0E32, '-...-'),
    (0x0E31, '-..-.'),
    (0x0E34, '-..--'),
    (0x0E35, '-.-..'),
    (0x0E38, '-.-.-'),
    (0x0E39, '-.--.'),
    (0x0E40, '-.---'),
    (0x0E41, '--...'),
    (0x0E42, '--..-'),
    (0x0E44, '--.-.'),
    (0x0E48, '--.--'),
    (0x0E49, '---..'),
    (0x0E33, '---.-'),
    (0x0E36, '----.'),
    (0x0E37, '-----'),
    (0x0E43, '......'),
    (0x0E30, '.....-'),
    (0x0E47, '....-.'),
    (0x0E4C, '....--'),
    (0x0E46, '...-..'),
    (0x0E24, '...-.-'),
    (0x0E26, '...--.'),
]
THAI_TO_MORSE: dict[str, str] = {chr(cp): code for cp, code in _THAI_DATA}
MORSE_TO_THAI: dict[str, str] = {v: k for k, v in THAI_TO_MORSE.items()}


# ── Public API ───────────────────────────────────────────────────────────────

def text_to_morse(text: str, lang: str = "en") -> str:
    """Convert plain text to Morse code, with cross-language fallback.

    Primary mapping is chosen by lang ("en" or "th").
    Characters not found in the primary mapping are looked up in the
    other mapping so that mixed-language text (e.g. "Hello สวัสดี")
    encodes without producing '?' for every foreign character.
    """
    primary  = THAI_TO_MORSE if lang == "th" else EN_TO_MORSE
    fallback = EN_TO_MORSE   if lang == "th" else THAI_TO_MORSE

    tokens: list[str] = []
    for ch in text:
        if ch == " ":
            tokens.append("/")
            continue
        # primary lookup (Thai keeps case; English uppercases)
        key = ch if lang == "th" else ch.upper()
        if key in primary:
            tokens.append(primary[key])
            continue
        # fallback: try the other language (always try both cases)
        for candidate in (ch.upper(), ch):
            if candidate in fallback:
                tokens.append(fallback[candidate])
                break
        else:
            tokens.append("?")
    return " ".join(tokens)


def morse_to_text(morse: str, lang: str = "en") -> str:
    """Convert Morse code to plain text (English or Thai)."""
    mapping = MORSE_TO_THAI if lang == "th" else MORSE_TO_EN
    normalised = morse.replace(" / ", " WORDSEP ").replace("/", " WORDSEP ")
    parts = normalised.split()
    chars: list[str] = []
    for token in parts:
        if token == "WORDSEP":
            chars.append(" ")
        elif token in mapping:
            chars.append(mapping[token])
        elif token:
            chars.append("[???]")
    return "".join(chars)


def is_morse(text: str) -> bool:
    """True when text looks like Morse code.

    Rules:
    - At least 2 dot/dash characters (avoids false-positive on a lone '-' or '.')
    - Every non-separator character must be '.' or '-'
    - Separators (space, /, tab, newline) are ignored
    """
    stripped = text.strip()
    if not stripped:
        return False
    non_sep = stripped.replace(" ", "").replace("/", "").replace("\t", "").replace("\n", "")
    return len(non_sep) >= 2 and all(c in ".-" for c in non_sep)


def detect_lang(text: str) -> str:
    """Return "th" if text contains any Thai Unicode character, else "en"."""
    for ch in text:
        if 0x0E00 <= ord(ch) <= 0x0E7F:
            return "th"
    return "en"
