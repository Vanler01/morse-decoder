#!/usr/bin/env python3
"""morse — CLI wrapper for the morse-code converter daemon."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_PLIST_NAME = "com.user.morse-code"
_PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{_PLIST_NAME}.plist"


def _install():
    subprocess.run(["bash", str(_DIR / "install.sh")], check=True)


def _uninstall():
    subprocess.run(["bash", str(_DIR / "uninstall.sh")], check=True)


def _update():
    if not _PLIST_PATH.exists():
        print("LaunchAgent not installed — run 'morse --install' first.")
        sys.exit(1)
    print("Restarting morse-code daemon...")
    subprocess.run(["launchctl", "unload", str(_PLIST_PATH)], check=False)
    subprocess.run(["launchctl", "load", "-w", str(_PLIST_PATH)], check=True)
    print("Done.")


def _status():
    pid_file = _DIR / "cache" / "daemon.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)
            print("Running (PID %d)" % pid)
            if _PLIST_PATH.exists():
                print("LaunchAgent: installed (auto-starts on login)")
            return
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    print("Not running")
    if not _PLIST_PATH.exists():
        print("LaunchAgent: not installed")


def main():
    parser = argparse.ArgumentParser(prog="morse", description="Morse code converter daemon")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--install",   action="store_true", help="install and start as LaunchAgent")
    group.add_argument("--uninstall", action="store_true", help="stop and remove LaunchAgent")
    group.add_argument("--update",    action="store_true", help="restart the running daemon")
    group.add_argument("--status",    action="store_true", help="show daemon status")
    args = parser.parse_args()

    if args.install:
        _install()
    elif args.uninstall:
        _uninstall()
    elif args.update:
        _update()
    elif args.status:
        _status()
    else:
        os.chdir(_DIR)
        sys.path.insert(0, str(_DIR))
        from main import main as _daemon
        _daemon()


if __name__ == "__main__":
    main()
