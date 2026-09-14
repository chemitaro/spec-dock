from __future__ import annotations

import json
import os
import signal
import stat
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


def _install_runtime_failure_hook(directory: Path) -> None:
    directory.mkdir()
    (directory / "sitecustomize.py").write_text(
        "import builtins\n"
        "_original_import = builtins.__import__\n"
        "def _raise(*args, **kwargs):\n"
        "    raise RuntimeError('post-admission failure')\n"
        "def _import(name, *args, **kwargs):\n"
        "    module = _original_import(name, *args, **kwargs)\n"
        "    if name == 'spec_dock_runtime.app':\n"
        "        module.run = _raise\n"
        "    return module\n"
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
            assert busy.stderr == (
                "error: repository-operation-busy: Another SpecDock command holds repository coordination; "
                "retry after it exits.\n"
            )
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
        assert not_ready.stderr == (
            "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
            "to complete recovery before running repository commands.\n"
        )
        assert not imported.exists(), "runtime was imported before ready admission"

    def test_t08_post_admission_runtime_defect_is_not_mapped_to_not_ready(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0

        hook_dir = tmp_path / "runtime-failure-hook"
        _install_runtime_failure_hook(hook_dir)
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{hook_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
        result = subprocess.run(
            [sys.executable, str(target / "spec-dock" / "scripts" / "spec-dock"), "--help"],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
            timeout=3,
        )

        assert result.returncode != 0
        assert "RuntimeError: post-admission failure" in result.stderr
        assert "error: runtime-installation-not-ready:" not in result.stderr

    def test_t08_strict_record_admission_rejects_unsafe_bindings_before_import(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0

        spy_dir = tmp_path / "spy"
        imported = tmp_path / "imported"
        _install_import_spy(spy_dir, imported)
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{spy_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"
        script = target / "spec-dock" / "scripts" / "spec-dock"
        record = target / "spec-dock" / "spec-dock.version"
        original = record.read_bytes()
        original_mode = stat.S_IMODE(record.stat().st_mode)
        assert original_mode == 0o644
        decoded = json.loads(original)

        malformed = [
            ("duplicate-key", b'{"schema_version":1,' + original[1:]),
            (
                "schema-bool",
                (
                    json.dumps({**decoded, "schema_version": True}, ensure_ascii=False, separators=(",", ":")) + "\n"
                ).encode("utf-8"),
            ),
            (
                "schema-float",
                (
                    json.dumps({**decoded, "schema_version": 1.0}, ensure_ascii=False, separators=(",", ":")) + "\n"
                ).encode("utf-8"),
            ),
            ("non-canonical", json.dumps(decoded, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"),
            (
                "unknown-key",
                (json.dumps({**decoded, "unknown": True}, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
                    "utf-8"
                ),
            ),
            ("oversized", b"x" * 4097),
            ("wrong-mode", original),
        ]

        for label, payload in malformed:
            record.unlink(missing_ok=True)
            record.write_bytes(payload)
            record.chmod(0o755 if label == "wrong-mode" else original_mode)
            imported.unlink(missing_ok=True)
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                timeout=3,
            )
            assert result.returncode != 0, label
            assert result.stdout == "", label
            assert result.stderr == (
                "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
                "to complete recovery before running repository commands.\n"
            ), label
            assert not imported.exists(), label

        hardlink = tmp_path / "record-hardlink"
        record.unlink(missing_ok=True)
        record.write_bytes(original)
        record.chmod(original_mode)
        os.link(record, hardlink)
        try:
            imported.unlink(missing_ok=True)
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                timeout=3,
            )
            assert result.returncode != 0
            assert result.stderr == (
                "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
                "to complete recovery before running repository commands.\n"
            )
            assert not imported.exists()
        finally:
            hardlink.unlink(missing_ok=True)

        symlink_target = tmp_path / "record-symlink-target"
        symlink_target.write_bytes(original)
        symlink_target.chmod(original_mode)
        record.unlink(missing_ok=True)
        record.symlink_to(symlink_target)
        try:
            imported.unlink(missing_ok=True)
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                timeout=3,
            )
            assert result.returncode != 0
            assert result.stderr == (
                "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
                "to complete recovery before running repository commands.\n"
            )
            assert not imported.exists()
        finally:
            record.unlink(missing_ok=True)

        if hasattr(os, "mkfifo"):
            os.mkfifo(record)
            try:
                imported.unlink(missing_ok=True)
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    cwd=target,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                assert result.returncode != 0
                assert result.stderr == (
                    "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
                    "to complete recovery before running repository commands.\n"
                )
                assert not imported.exists()
            finally:
                record.unlink(missing_ok=True)

        record.write_bytes(original)
        record.chmod(original_mode)
        marker = target / ".agents" / "skills" / "spec-dock" / ".spec-dock-provider-slot.json"
        marker_mode = stat.S_IMODE(marker.stat().st_mode)
        assert marker_mode == 0o644
        marker.chmod(0o755)
        try:
            imported.unlink(missing_ok=True)
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                timeout=3,
            )
            assert result.returncode != 0
            assert result.stderr == (
                "error: runtime-installation-not-ready: SpecDock tooling is not ready; use the external installer "
                "to complete recovery before running repository commands.\n"
            )
            assert not imported.exists()
        finally:
            marker.chmod(marker_mode)

        record.write_bytes(original)
        record.chmod(original_mode)
