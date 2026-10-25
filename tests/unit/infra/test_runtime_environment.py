"""The injectable runtime environment: OS, container markers and the Git installation (contract C11)."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

import pytest

from spec_dock.runtime.infra.runtime_environment import (
    GitInstallation,
    RuntimeEnvironment,
    detect_runtime_environment,
)


def _fake_git(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git = bin_dir / "git"
    git.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    git.chmod(0o755)
    return bin_dir


def _runner(reported: bytes, returncode: int = 0) -> Any:
    calls: list[list[str]] = []

    def run(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append(argv)
        assert not any(key.startswith("GIT_") for key in kwargs["env"])
        return subprocess.CompletedProcess(argv, returncode, reported, b"")

    run.calls = calls  # type: ignore[attr-defined]
    return run


def test_a_plain_host_has_no_container_markers_and_reports_git(tmp_path: Path) -> None:
    bin_dir = _fake_git(tmp_path)
    runner = _runner(b"git version 2.54.0\n")
    environment = detect_runtime_environment(
        {"PATH": str(bin_dir), "HOME": "/home/me", "GIT_DIR": "/elsewhere"}, root=tmp_path, runner=runner
    )
    assert environment.container is False and environment.container_markers == ()
    assert environment.git == GitInstallation(str(bin_dir / "git"), (2, 54, 0), "git version 2.54.0")
    assert environment.git.supported and environment.home == Path("/home/me")
    assert runner.calls == [[str(bin_dir / "git"), "--version"]]


@pytest.mark.parametrize(
    ("files", "environ", "markers"),
    [
        ((".dockerenv",), {}, ("/.dockerenv",)),
        (("run/.containerenv",), {}, ("/run/.containerenv",)),
        ((), {"container": "podman"}, ("container",)),
        ((), {"REMOTE_CONTAINERS": "true", "CODESPACES": "true"}, ("REMOTE_CONTAINERS", "CODESPACES")),
    ],
)
def test_any_container_marker_means_a_container(
    tmp_path: Path, files: tuple[str, ...], environ: dict[str, str], markers: tuple[str, ...]
) -> None:
    for name in files:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("", encoding="utf-8")
    environment = detect_runtime_environment({"PATH": "", **environ}, root=tmp_path, runner=_runner(b""))
    assert environment.container is True and environment.container_markers == markers


def test_missing_git_has_no_version_and_is_unsupported(tmp_path: Path) -> None:
    environment = detect_runtime_environment({"PATH": str(tmp_path)}, root=tmp_path, runner=_runner(b""))
    assert environment.git == GitInstallation(None, None, None) and not environment.git.supported


@pytest.mark.parametrize(("reported", "returncode"), [(b"git version 2.37.0\n", 0), (b"garbage", 0), (b"", 1)])
def test_an_old_or_unreadable_git_is_unsupported(tmp_path: Path, reported: bytes, returncode: int) -> None:
    bin_dir = _fake_git(tmp_path)
    environment = detect_runtime_environment(
        {"PATH": str(bin_dir)}, root=tmp_path, runner=_runner(reported, returncode)
    )
    assert environment.git.path == str(bin_dir / "git") and not environment.git.supported


def test_a_git_that_cannot_start_is_unsupported(tmp_path: Path) -> None:
    bin_dir = _fake_git(tmp_path)

    def broken(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        raise OSError("exec format error")

    environment = detect_runtime_environment({"PATH": str(bin_dir)}, root=tmp_path, runner=broken)
    assert environment.git.version is None


def test_tool_sessions_are_read_from_the_environment(tmp_path: Path) -> None:
    environment = RuntimeEnvironment(
        "darwin",
        (),
        GitInstallation("/usr/bin/git", (2, 54, 0), "git version 2.54.0"),
        {"CODEX_SANDBOX": "seatbelt", "CLAUDECODE": "1", "HOME": "relative"},
    )
    assert environment.codex_sandbox and environment.claude_code and environment.home is None
    assert not RuntimeEnvironment("linux", (), environment.git, {}).codex_sandbox
