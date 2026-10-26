"""C11 additions of iss-00430: the systemd user manager (with bus retries) and linger, injectable."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.runtime_environment import detect_service_manager
from tests.support.canonical_repo import environment

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock.runtime.infra.runtime_environment import RuntimeEnvironment


def _completed(stdout: str = "", stderr: str = "", code: int = 0) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess([], code, stdout.encode(), stderr.encode())


def _linux() -> RuntimeEnvironment:
    from dataclasses import replace

    return replace(environment(environ={"USER": "dev", "PATH": "/usr/bin"}), system="linux")


def _root(tmp_path: Path, *, systemd: bool) -> Path:
    if systemd:
        (tmp_path / "run/systemd/system").mkdir(parents=True)
    return tmp_path


def test_macos_needs_no_service_manager() -> None:
    env = environment()
    assert detect_service_manager(env, runner=lambda *a, **k: _completed()) is env


def test_a_running_or_degraded_user_manager_selects_systemd_and_reads_linger(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        return _completed("degraded\n") if argv[0] == "systemctl" else _completed("no\n")

    found = detect_service_manager(_linux(), root=_root(tmp_path, systemd=True), runner=runner, sleep=lambda _s: None)
    assert (found.systemd_present, found.systemd_user, found.linger, found.user) == (True, True, False, "dev")
    assert calls == [
        ["systemctl", "--user", "is-system-running"],
        ["loginctl", "show-user", "dev", "-p", "Linger", "--value"],
    ]


def test_failed_to_connect_to_bus_is_retried_once_a_second(tmp_path: Path) -> None:
    answers = [_completed("", "Failed to connect to bus: No medium found", 1)] * 2 + [_completed("running\n")]
    slept: list[float] = []

    def runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return answers.pop(0) if argv[0] == "systemctl" else _completed("yes\n")

    found = detect_service_manager(_linux(), root=_root(tmp_path, systemd=True), runner=runner, sleep=slept.append)
    assert found.systemd_user is True and found.linger is True and slept == [1.0, 1.0]


def test_the_bus_is_given_up_after_five_retries(tmp_path: Path) -> None:
    slept: list[float] = []

    def runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        if argv[0] == "systemctl":
            return _completed("", "Failed to connect to bus: No such file or directory", 1)
        return _completed("", "", 1)

    found = detect_service_manager(_linux(), root=_root(tmp_path, systemd=True), runner=runner, sleep=slept.append)
    assert found.systemd_user is None and found.linger is None and len(slept) == 5  # unknown, not "no systemd"


def test_no_systemd_directory_means_the_loop_runner(tmp_path: Path) -> None:
    def runner(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        assert argv[0] != "systemctl"
        raise FileNotFoundError("loginctl")

    found = detect_service_manager(_linux(), root=_root(tmp_path, systemd=False), runner=runner)
    assert (found.systemd_present, found.systemd_user, found.linger) == (False, False, None)
