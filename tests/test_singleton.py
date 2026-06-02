"""Tests for _claim_singleton() PID locking (BUG-10, mirrored from en-th).

PyObjC modules are mocked so main imports without a real event tap. os.kill,
fcntl.flock and time.sleep are mocked so no process is signalled and no real
lock is taken; _PID_FILE/_LOCK_FILE point at a tmp dir.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_MOCK_MODULES = [
    "Quartz", "AppKit", "CoreFoundation",
    "PyObjCTools", "PyObjCTools.AppHelper",
    "Foundation", "objc",
]
for _m in _MOCK_MODULES:
    if _m not in sys.modules:
        sys.modules[_m] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent.parent))

import main as _main_mod


def _point_at_tmp(monkeypatch, tmp_path):
    monkeypatch.setattr(_main_mod, "_PID_FILE", tmp_path / "daemon.pid")
    monkeypatch.setattr(_main_mod, "_LOCK_FILE", tmp_path / "daemon.lock")


class TestClaimSingleton:
    def test_no_existing_pid_writes_own_pid(self, tmp_path, monkeypatch):
        _point_at_tmp(monkeypatch, tmp_path)
        with patch("os.kill") as kill:
            _main_mod._claim_singleton()
        kill.assert_not_called()
        assert (tmp_path / "daemon.pid").read_text() == str(os.getpid())

    def test_existing_pid_is_killed_then_own_pid_written(self, tmp_path, monkeypatch):
        _point_at_tmp(monkeypatch, tmp_path)
        (tmp_path / "daemon.pid").write_text("999999")
        with patch("os.kill") as kill, patch("time.sleep"):
            _main_mod._claim_singleton()
        assert kill.call_args_list[0][0][0] == 999999
        assert (tmp_path / "daemon.pid").read_text() == str(os.getpid())

    def test_lock_is_acquired_exclusively_and_released(self, tmp_path, monkeypatch):
        _point_at_tmp(monkeypatch, tmp_path)
        with patch.object(_main_mod.fcntl, "flock") as flock, patch("os.kill"):
            _main_mod._claim_singleton()
        modes = [c[0][1] for c in flock.call_args_list]
        assert _main_mod.fcntl.LOCK_EX in modes
        assert _main_mod.fcntl.LOCK_UN in modes
