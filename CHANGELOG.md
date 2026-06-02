# Changelog

All notable changes to **morse-code** are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/);
this project follows [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-06-03

First stable release (supersedes the `v0.1.0-beta` pre-release). A macOS
floating panel that converts text ↔ Morse in real time. Joined the
`build-features` monorepo as its third submodule in this release.

### Added
- Real-time conversion in both directions with auto-detected input:
  - English text ↔ Morse (ITU standard table)
  - Thai text ↔ Morse (44 consonants + vowels + tone marks + symbols)
- Global hotkey **Option+M** to show/hide the converter panel
- Floating converter `NSPanel`; the EN/TH button selects the **output**
  language when decoding Morse (input language is always auto-detected)
- Word separator `' / '` in Morse output; unknown chars render as `?`
  (encoding) / `[???]` (decoding)
- `morse` CLI: install / uninstall / update the LaunchAgent
- Test suite (52 tests; CGEventTap always mocked)

### Fixed
- **BUG-10** — the PID takeover (kill previous instance + write PID) is
  serialized with an exclusive file lock, so two simultaneous starts can't both
  survive as duplicate daemons

### Notes
- Unlike the other build-features daemons, morse-code uses `CGEventTap` **only**
  to detect its hotkey — it never monitors or injects system-wide keystrokes,
  so it carries no password-field risk. The panel and conversion need no special
  permission; Accessibility is required only for the hotkey.

### Security
- Never logs raw keystrokes

[0.1.0]: https://github.com/Vanler01/morse-decoder/releases/tag/v0.1.0
