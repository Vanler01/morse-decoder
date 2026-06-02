# AGENTS.md — morse-code

Project-specific agent triggers, test rules, and file ownership. Shared
conventions live in `~/build-features/AGENTS.md`.

## Agent Triggers
| agent | when to use |
|-------|-------------|
| `macos-api-specialist` | the Option+M hotkey CGEventTap in `main.py` or the NSPanel in `overlay.py` |
| `build-error-resolver` | immediately on ImportError / AttributeError (PyObjC) |
| `code-reviewer` | after writing or modifying code |

There is no Thai/number domain agent here; Morse conversion lives entirely in
`converter.py` and is covered by its own unit tests.

## Testing Rules
- Test conversion logic in `converter.py` independently of CGEventTap/NSPanel.
- Mock all PyObjC/macOS API calls; never start a real event tap.
- Current suite: 49 tests in `tests/test_converter.py`
  (EN↔Morse, Thai↔Morse, `is_morse`, `detect_lang`, round-trips, unknown chars).
- No tests for `overlay.py` / `main.py` (UI + hotkey tap require a macOS runtime).

## File Ownership
| File | Purpose |
|------|---------|
| `main.py` | CGEventTap for the Option+M hotkey + daemon lifecycle |
| `converter.py` | EN/Thai ↔ Morse tables + `text_to_morse`/`morse_to_text`/`is_morse`/`detect_lang` |
| `overlay.py` | NSPanel converter UI (EN/TH button = output language when decoding) |
| `cli.py` | `morse` CLI entry point (install/uninstall/update LaunchAgent) |
| `_gen_converter.py` | dev-time generator for the Thai Morse table (not run by the daemon) |
| `install.sh` / `uninstall.sh` | LaunchAgent `com.user.morse-code` install/uninstall |
