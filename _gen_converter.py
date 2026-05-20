"""Script that generates converter.py using codepoints — avoids any encoding issues."""

# All Thai character mappings expressed as (unicode_codepoint, morse_code)
# so no Thai characters appear in this source file's string literals.
THAI_DATA = [
    # ── Consonants (พยัญชนะ) ──────────────────────────────────────────────────
    # 2-element
    (0x0E01, ".."),    # ก
    (0x0E19, ".-"),    # น
    (0x0E21, "-."),    # ม
    (0x0E27, "--"),    # ว
    # 3-element
    (0x0E02, "..."),   # ข
    (0x0E04, "..-"),   # ค
    (0x0E07, ".-."),   # ง
    (0x0E15, ".--"),   # ต
    (0x0E17, "-.."),   # ท
    (0x0E1A, "-.-"),   # บ
    (0x0E1B, "--."),   # ป
    (0x0E23, "---"),   # ร
    # 4-element
    (0x0E08, "...."),  # จ
    (0x0E0A, "...-"),  # ช
    (0x0E0B, "..-."),  # ซ
    (0x0E0D, "..--"),  # ญ
    (0x0E14, ".-.."),  # ด
    (0x0E16, ".-.-"),  # ถ
    (0x0E18, ".--." ), # ธ
    (0x0E13, ".---"),  # ณ
    (0x0E1E, "-..."),  # พ
    (0x0E1C, "-..-"),  # ผ
    (0x0E1D, "-.-."),  # ฝ
    (0x0E1F, "-.--"),  # ฟ
    (0x0E20, "--.."),  # ภ
    (0x0E22, "--.-"),  # ย
    (0x0E25, "---."),  # ล
    (0x0E2A, "----"),  # ส
    # 5-element (start with .)
    (0x0E03, "....."), # ฃ
    (0x0E05, "....-"), # ฅ
    (0x0E06, "...-." ), # ฆ
    (0x0E09, "...--"), # ฉ
    (0x0E0C, "..-.." ), # ฌ
    (0x0E0E, "..-.-"), # ฎ
    (0x0E0F, "..--." ), # ฏ
    (0x0E10, "..---"), # ฐ
    (0x0E11, ".-..."), # ฑ
    (0x0E12, ".-..-"), # ฒ
    (0x0E2B, ".-.-." ), # ห
    (0x0E2C, ".--.."), # ฬ
    (0x0E2D, ".--.-"), # อ
    (0x0E2E, ".---."), # ฮ
    (0x0E28, ".----"), # ศ
    (0x0E29, "-...."), # ษ
    # ── Vowels (สระ) — 5-element codes starting with - ────────────────────────
    (0x0E32, "-...-"),  # า  sara aa   (long a)
    (0x0E31, "-..-." ), # ั  mai han akat
    (0x0E34, "-..--"),  # ิ  sara i
    (0x0E35, "-.-.." ), # ี  sara ii
    (0x0E38, "-.-.-"),  # ุ  sara u
    (0x0E39, "-.--." ), # ู  sara uu
    (0x0E40, "-.---"),  # เ  sara e  (prefix)
    (0x0E41, "--..."),  # แ  sara ae (prefix)
    (0x0E42, "--..-"),  # โ  sara o  (prefix)
    (0x0E44, "--.-." ), # ไ  sara ai maimalai
    (0x0E48, "--.--"),  # ่  mai ek  (low tone)
    (0x0E49, "---.."),  # ้  mai tho (falling)
    (0x0E33, "---.-"),  # ำ  sara am
    (0x0E36, "----."),  # ึ  sara ue
    (0x0E37, "-----"),  # ื  sara uee
    # ── Less-common (6-element) ───────────────────────────────────────────────
    (0x0E43, "......"), # ใ  sara ai maimuan
    (0x0E30, ".....-"), # ะ  sara a short
    (0x0E47, "....-." ), # ็  mai taikhu
    (0x0E4C, "....--"), # ์  thanthakat
    (0x0E46, "...-.."), # ๆ  maiyamok
    # ── Semivowels ────────────────────────────────────────────────────────────
    (0x0E24, "...-.-"), # ฤ  ro rue  (อังกฤษ, ฤดู, ฤกษ์)
    (0x0E26, "...--."), # ฦ  lue    (rare)
]

# Verify uniqueness before writing
codes = [c for _, c in THAI_DATA]
assert len(codes) == len(set(codes)), f"Duplicate codes: {[c for c in codes if codes.count(c)>1]}"
print(f"Thai: {len(THAI_DATA)} entries, all unique")

# Build the converter.py content
out = []
out.append('"""')
out.append('Morse code conversion: English <-> Morse, Thai <-> Morse.')
out.append('')
out.append('Thai covers 44 consonants + 15 vowels (sara) + 2 tone marks + sara am')
out.append('+ 5 symbols = 64 characters total.  Vowels and tone marks are required')
out.append('for readable Thai text.')
out.append('')
out.append("Word separator in Morse output: ' / '  (space-slash-space).")
out.append("Unknown chars: '?' when encoding, '[???]' when decoding.")
out.append('"""')
out.append('from __future__ import annotations')
out.append('')
out.append('# ── English (ITU standard) ───────────────────────────────────────────────────')
out.append('EN_TO_MORSE: dict[str, str] = {')
out.append('    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",   "E": ".",')
out.append('    "F": "..-.",  "G": "--.",   "H": "....",  "I": "..",    "J": ".---",')
out.append('    "K": "-.-",   "L": ".-..",  "M": "--",    "N": "-.",    "O": "---",')
out.append('    "P": ".--.",  "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",')
out.append('    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",  "Y": "-.--",')
out.append('    "Z": "--..",')
out.append('    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",')
out.append('    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",')
out.append("    \".\": \".-.-.-\", \",\": \"--..--\", \"?\": \"..--..\", \"'\": \".----.\",")
out.append('    "!": "-.-.--", "/": "-..-.", "(": "-.--.", ")": "-.--.-",')
out.append('    "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",')
out.append("    \"+\": \".-.-.\", \"-\": \"-....-\", \"_\": \"..--.-\", '\"': \".-..-.\",")
out.append('    "$": "...-..-", "@": ".--.-.",')
out.append('}')
out.append('MORSE_TO_EN: dict[str, str] = {v: k for k, v in EN_TO_MORSE.items()}')
out.append('')
out.append('# ── Thai (consonants + vowels + tone marks + symbols) ───────────────────────')
out.append('# Codes are unique within Thai mode; they may overlap EN_TO_MORSE because')
out.append('# language is always specified when decoding.')
out.append('#')
out.append('# Stored as (codepoint, morse) tuples so this file stays ASCII-safe.')
out.append('#   2-el: ก น ม ว')
out.append('#   3-el: ข ค ง ต ท บ ป ร')
out.append('#   4-el: จ ช ซ ญ ด ถ ธ ณ พ ผ ฝ ฟ ภ ย ล ส')
out.append('#   5-el (.): ฃ ฅ ฆ ฉ ฌ ฎ ฏ ฐ ฑ ฒ ห ฬ อ ฮ ศ ษ')
out.append('#   5-el (-): า ั ิ ี ุ ู เ แ โ ไ ่ ้ ำ ึ ื')
out.append('#   6-el: ใ ะ ็ ์ ๆ')
out.append('_THAI_DATA: list[tuple[int, str]] = [')
for cp, code in THAI_DATA:
    out.append(f'    (0x{cp:04X}, {code!r}),')
out.append(']')
out.append('THAI_TO_MORSE: dict[str, str] = {chr(cp): code for cp, code in _THAI_DATA}')
out.append('MORSE_TO_THAI: dict[str, str] = {v: k for k, v in THAI_TO_MORSE.items()}')
out.append('')
out.append('')
out.append('# ── Public API ───────────────────────────────────────────────────────────────')
out.append('')
out.append('def text_to_morse(text: str, lang: str = "en") -> str:')
out.append('    """Convert plain text to Morse code, with cross-language fallback.')
out.append('')
out.append('    Primary mapping is chosen by lang ("en" or "th").')
out.append('    Characters not found in the primary mapping are looked up in the')
out.append('    other mapping so that mixed-language text (e.g. "Hello สวัสดี")')
out.append('    encodes without producing \'?\' for every foreign character.')
out.append('    """')
out.append('    primary  = THAI_TO_MORSE if lang == "th" else EN_TO_MORSE')
out.append('    fallback = EN_TO_MORSE   if lang == "th" else THAI_TO_MORSE')
out.append('')
out.append('    tokens: list[str] = []')
out.append('    for ch in text:')
out.append('        if ch == " ":')
out.append('            tokens.append("/")')
out.append('            continue')
out.append('        key = ch if lang == "th" else ch.upper()')
out.append('        if key in primary:')
out.append('            tokens.append(primary[key])')
out.append('            continue')
out.append('        for candidate in (ch.upper(), ch):')
out.append('            if candidate in fallback:')
out.append('                tokens.append(fallback[candidate])')
out.append('                break')
out.append('        else:')
out.append('            tokens.append("?")')
out.append('    return " ".join(tokens)')
out.append('')
out.append('')
out.append('def morse_to_text(morse: str, lang: str = "en") -> str:')
out.append('    """Convert Morse code to plain text (English or Thai)."""')
out.append('    mapping = MORSE_TO_THAI if lang == "th" else MORSE_TO_EN')
out.append('    normalised = morse.replace(" / ", " WORDSEP ").replace("/", " WORDSEP ")')
out.append('    parts = normalised.split()')
out.append('    chars: list[str] = []')
out.append('    for token in parts:')
out.append('        if token == "WORDSEP":')
out.append('            chars.append(" ")')
out.append('        elif token in mapping:')
out.append('            chars.append(mapping[token])')
out.append('        elif token:')
out.append('            chars.append("[???]")')
out.append('    return "".join(chars)')
out.append('')
out.append('')
out.append('def is_morse(text: str) -> bool:')
out.append('    """True when text is Morse: only dots/dashes/spaces/slashes, at least one . or -."""')
out.append('    stripped = text.strip()')
out.append('    if not stripped:')
out.append('        return False')
out.append('    non_sep = stripped.replace(" ", "").replace("/", "").replace("\\t", "").replace("\\n", "")')
out.append('    return len(non_sep) >= 2 and all(c in ".-" for c in non_sep)')
out.append('')
out.append('')
out.append('def detect_lang(text: str) -> str:')
out.append('    """Return "th" if text contains any Thai Unicode character, else "en"."""')
out.append('    for ch in text:')
out.append('        if 0x0E00 <= ord(ch) <= 0x0E7F:')
out.append('            return "th"')
out.append('    return "en"')
out.append('')

import os
dest = os.path.join(os.path.dirname(__file__), "converter.py")
with open(dest, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"converter.py written ({len(out)} lines)")

# quick sanity check
import importlib.util, sys
spec = importlib.util.spec_from_file_location("converter", dest)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.text_to_morse("SOS") == "... --- ..."
sawatdii = chr(0x0E2A)+chr(0x0E27)+chr(0x0E31)+chr(0x0E2A)+chr(0x0E14)+chr(0x0E35)  # สวัสดี
result = mod.text_to_morse(sawatdii, "th")
print(f"  SOS -> {mod.text_to_morse('SOS')}")
print(f"  sawatdii -> {result}")
roundtrip = mod.morse_to_text(result, "th")
print(f"  roundtrip -> {roundtrip!r}")
assert roundtrip == sawatdii, f"roundtrip failed: {roundtrip!r}"
assert "?" not in result, f"unknown chars in output: {result}"
print("All checks passed!")
