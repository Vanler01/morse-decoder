# morse-code — project rules

A floating panel that converts text ↔ Morse in real time (EN↔Morse,
Thai↔Morse), with the direction auto-detected from what is typed. Loads on
top of the root `~/build-features/CLAUDE.md` (shared stack, security, NSPanel
patterns); this file holds only morse-specific rules.

## Purpose & how it differs from the other two daemons
- Toggle the panel with the global hotkey **Option+M**.
- Unlike en-th-word-swap / num-to-text, this daemon **does NOT intercept or
  inject system-wide keystrokes**. CGEventTap is used *only* to detect the
  Option+M hotkey (flagsChanged + keyDown); the user types into the panel
  itself. There is no injection into other apps and **no password-field risk**.
- Accessibility permission is required only for the hotkey; the panel and
  conversion work without it.

## Dependencies
- `pyobjc` only (no external NLP / number libraries)

## converter.py rules
- Pure conversion logic — keep it independent of AppKit/CGEventTap so it stays
  unit-testable.
- English uses the ITU standard table (`EN_TO_MORSE` / `MORSE_TO_EN`).
- Thai covers 44 consonants + 15 vowels (sara) + tone marks + sara am +
  symbols; vowels and tone marks are required for readable Thai.
- Word separator in Morse output is `' / '` (space-slash-space).
- Unknown chars: `'?'` when encoding, `'[???]'` when decoding.
- Public API: `text_to_morse`, `morse_to_text`, `is_morse`, `detect_lang`.
- `_gen_converter.py` is a dev-time table generator, not part of the daemon.

## overlay.py rules
- NSPanel converter UI. Input language is **always auto-detected**; the EN/TH
  button only controls the **output** language when *decoding* Morse.
- NSPanel must stay non-activating (shared rule) so it never steals focus.

## CLI & lifecycle
- CLI entry point: `morse` (cli.py) — install/uninstall/update via LaunchAgent
  `com.user.morse-code`.
- Single-instance via PID file; daemon threads `daemon=True` (shared rules).
