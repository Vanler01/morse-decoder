#!/usr/bin/env python3
"""
morse-code converter overlay
─────────────────────────────
A floating panel that converts text ↔ Morse code in real time.

Supported directions (auto-detected from input):
  English text → Morse      e.g. "SOS" → "... --- ..."
  Morse → English text      e.g. "... --- ..." → "SOS"
  Thai text → Morse         e.g. "กน" → ".. .-"
  Morse → Thai text

Hotkey: Option+M  →  show / hide the panel.

Requires Accessibility permission only for the global hotkey
(CGEventTap on flagsChanged + keyDown).  The converter panel
itself works without any special permissions.
"""

import sys
import os
import signal
import time
import fcntl
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import Quartz
from AppKit import NSApplication
from CoreFoundation import (
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    kCFRunLoopCommonModes,
)
from PyObjCTools.AppHelper import runEventLoop

_DIR = Path(__file__).parent
_PID_FILE = _DIR / "cache" / "daemon.pid"
_LOCK_FILE = _DIR / "cache" / "daemon.lock"

_KC_M = 46            # kVK_ANSI_M
_MOD_ALT = Quartz.kCGEventFlagMaskAlternate
_MOD_CMD = Quartz.kCGEventFlagMaskCommand
_MOD_CTRL = Quartz.kCGEventFlagMaskControl

_overlay = None
_synth_skip = 0


def _callback(proxy, event_type, event, refcon):
    global _synth_skip

    if _synth_skip > 0:
        _synth_skip -= 1
        return event

    if event_type != Quartz.kCGEventKeyDown:
        return event

    keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
    flags = Quartz.CGEventGetFlags(event)

    # Option+M — toggle panel (no Cmd/Ctrl to avoid conflicts)
    if (
        keycode == _KC_M
        and (flags & _MOD_ALT)
        and not (flags & _MOD_CMD)
        and not (flags & _MOD_CTRL)
    ):
        if _overlay:
            _overlay.toggle()
        return None   # consume event

    return event


def _kill_existing() -> None:
    if _PID_FILE.exists():
        try:
            old = int(_PID_FILE.read_text().strip())
            if old != os.getpid():
                os.kill(old, signal.SIGTERM)
                time.sleep(0.4)
                try:
                    os.kill(old, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        except (ValueError, ProcessLookupError, PermissionError):
            pass


def _claim_singleton() -> None:
    """Take over as the single running daemon: kill any prior instance and
    record our PID, serialized by an exclusive file lock so two simultaneous
    starts can't both survive (BUG-10). The lock is held only for this
    critical section, so a later start still sees our PID and replaces us."""
    _PID_FILE.parent.mkdir(exist_ok=True)
    lock_fd = os.open(str(_LOCK_FILE), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        _kill_existing()
        _PID_FILE.write_text(str(os.getpid()))
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def main() -> None:
    global _overlay

    _claim_singleton()

    import atexit
    atexit.register(
        lambda: (
            _PID_FILE.unlink(missing_ok=True)
            if _PID_FILE.exists()
            and _PID_FILE.read_text().strip() == str(os.getpid())
            else None
        )
    )

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(1)  # NSApplicationActivationPolicyAccessory

    from overlay import MorseOverlay
    _overlay = MorseOverlay.alloc().init()
    _overlay.show()   # show on startup; Option+M toggles thereafter

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
        _callback,
        None,
    )

    if tap is None:
        print(
            "WARNING: Cannot create event tap — Option+M hotkey unavailable.\n"
            "  System Settings → Privacy & Security → Accessibility → add python3\n"
            "  The converter panel is still visible; close with the window button.",
            flush=True,
        )
    else:
        src = CFMachPortCreateRunLoopSource(None, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), src, kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(tap, True)
        print("morse-code running.  Option+M = show/hide panel.", flush=True)

    runEventLoop()


if __name__ == "__main__":
    main()
