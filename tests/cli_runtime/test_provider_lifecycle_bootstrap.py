from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from typing import TYPE_CHECKING

from tests.cli_runtime.harness import CliRuntimeHarness, main

if TYPE_CHECKING:
    from pathlib import Path


def _wait_for(path: Path, process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        if process.poll() is not None:
            raise AssertionError(f"lock helper exited early: {process.returncode}")
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {path}")


def _lock_process(target: Path, ready: Path) -> subprocess.Popen[str]:
    code = (
        "import fcntl, os, pathlib, time; "
        f"fd=os.open({str(target)!r}, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)); "
        "fcntl.flock(fd, fcntl.LOCK_EX); "
        f"pathlib.Path({str(ready)!r}).write_text('ready', encoding='utf-8'); "
        "time.sleep(30)"
    )
    return subprocess.Popen([sys.executable, "-c", code], text=True)


def _install_import_spy(directory: Path, marker: Path) -> None:
    directory.mkdir()
    (directory / "sitecustomize.py").write_text(
        "import builtins\n"
        "from pathlib import Path\n"
        f"_marker = Path({str(marker)!r})\n"
        "_original = builtins.__import__\n"
        "def _import(name, *args, **kwargs):\n"
        "    if name == 'spec_dock_runtime' or name.startswith('spec_dock_runtime.'):\n"
        "        _marker.write_text(name, encoding='utf-8')\n"
        "    return _original(name, *args, **kwargs)\n"
        "builtins.__import__ = _import\n",
        encoding="utf-8",
    )


class TestProviderLifecycleBootstrap(CliRuntimeHarness):
    def test_t08_pre_import_shared_lease_and_ready_admission_are_enforced(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0

        spy_dir = tmp_path / "spy"
        imported = tmp_path / "imported"
        _install_import_spy(spy_dir, imported)
        ready = tmp_path / "lock-ready"
        lock_process = _lock_process(target, ready)
        try:
            _wait_for(ready, lock_process)
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{spy_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
            script = target / "spec-dock" / "scripts" / "spec-dock"
            busy = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
            )
            assert busy.returncode != 0
            assert busy.stdout == ""
            assert "repository coordination is busy" in busy.stderr
            assert not imported.exists(), "runtime was imported before shared lease admission"
        finally:
            lock_process.send_signal(signal.SIGTERM)
            lock_process.wait(timeout=5)

        record = target / "spec-dock" / "spec-dock.version"
        payload = json.loads(record.read_text(encoding="utf-8"))
        payload["state"] = "incomplete"
        record.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
        not_ready = subprocess.run(
            [sys.executable, str(target / "spec-dock" / "scripts" / "spec-dock"), "--help"],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert not_ready.returncode != 0
        assert "repository runtime is not ready" in not_ready.stderr
        assert not imported.exists(), "runtime was imported before ready admission"
