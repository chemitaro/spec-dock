from __future__ import annotations

import fcntl
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from tests.cli_runtime.harness import CliRuntimeHarness, main


def _make_uvx(bin_dir: Path, log: Path) -> None:
    uvx = bin_dir / "uvx"
    uvx.write_text(
        f"#!/bin/sh\nprintf '%s\\n' \"$@\" > {log}\nprintf 'child stdout\\n'\nprintf 'child stderr\\n' >&2\nexit 7\n",
        encoding="utf-8",
    )
    uvx.chmod(0o755)


def _wait_for(path: Path, process: subprocess.Popen[str], *, timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return
        if process.poll() is not None:
            raise AssertionError(f"helper exited early: {process.returncode}")
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {path}")


class TestProviderLifecycleHandoff(CliRuntimeHarness):
    def test_t09_update_uninstall_exec_and_helper_lease_lifetime_are_terminal(self, tmp_path: Path) -> None:
        target = tmp_path / "target"
        target.mkdir()
        assert main(["init", str(target)]) == 0
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        log = tmp_path / "uvx-args"
        _make_uvx(bin_dir, log)
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

        update = subprocess.run(
            [sys.executable, str(target / "spec-dock/scripts/spec-dock"), "update", str(target)],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert update.returncode == 7
        assert update.stdout == "child stdout\n"
        assert update.stderr == "child stderr\n"
        assert log.read_text(encoding="utf-8").splitlines() == [
            "--no-cache",
            "--from",
            "git+https://github.com/chemitaro/spec-dock",
            "spec-dock",
            "update",
            str(target),
        ]

        uninstall = subprocess.run(
            [
                sys.executable,
                str(target / "spec-dock/scripts/spec-dock"),
                "uninstall",
                str(target),
                "--apply",
                "--keep-specs",
                "--json",
            ],
            cwd=target,
            env=env,
            capture_output=True,
            text=True,
        )
        assert uninstall.returncode == 7
        assert uninstall.stdout == "child stdout\n"
        assert uninstall.stderr == "child stderr\n"
        assert log.read_text(encoding="utf-8").splitlines()[-5:] == [
            "uninstall",
            str(target),
            "--apply",
            "--keep-specs",
            "--json",
        ]

        missing_env = {"PATH": str(tmp_path / "empty-bin")}
        (tmp_path / "empty-bin").mkdir()
        missing = subprocess.run(
            [sys.executable, str(target / "spec-dock/scripts/spec-dock"), "update", str(target)],
            cwd=target,
            env=missing_env,
            capture_output=True,
            text=True,
        )
        assert missing.returncode == 127
        assert missing.stdout == ""
        assert (
            missing.stderr == "error: uvx could not be executed. Install uv/uvx or ensure uvx is on PATH, then retry.\n"
        )

        runtime_scripts = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
        root_fd = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            root_stat = os.fstat(root_fd)
            fcntl.flock(root_fd, fcntl.LOCK_EX)
            marker = tmp_path / "child-ready"
            child_code = (
                "from pathlib import Path; import time; "
                f"Path({str(marker)!r}).write_text('ready', encoding='utf-8'); time.sleep(2)"
            )
            helper_env = os.environ.copy()
            helper_env["PYTHONPATH"] = str(runtime_scripts)
            helper = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "spec_dock_runtime.infra.git_helper",
                    "--lease-fd",
                    str(root_fd),
                    "--expected-device",
                    str(root_stat.st_dev),
                    "--expected-inode",
                    str(root_stat.st_ino),
                    "--",
                    sys.executable,
                    "-c",
                    child_code,
                ],
                env=helper_env,
                pass_fds=(root_fd,),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            _wait_for(marker, helper)
            helper.send_signal(signal.SIGKILL)
            helper.wait(timeout=5)
        finally:
            os.close(root_fd)

        contender = os.open(target, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            with __import__("pytest").raises(BlockingIOError):
                fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
            time.sleep(2.2)
            fcntl.flock(contender, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(contender)
