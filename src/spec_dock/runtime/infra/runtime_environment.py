"""The runtime environment a canonical command decides from, computed once and injectable (contract C11).

Procedures take a RuntimeEnvironment argument; command handlers call detect_runtime_environment() through
this module so a CLI test can replace it. I-3 adds systemd-user and linger fields with defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING, Final, Literal, cast

from spec_dock.runtime.domain.canonical_layout import git_supported, parse_git_version
from spec_dock.runtime.infra.git_cli import sanitized_git_environment

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

SystemName = Literal["darwin", "linux"]
CONTAINER_MARKER_FILES: Final = ("/.dockerenv", "/run/.containerenv")
CONTAINER_ENVIRONMENT_KEYS: Final = ("container", "REMOTE_CONTAINERS", "CODESPACES")


@dataclass(frozen=True)
class GitInstallation:
    path: str | None
    version: tuple[int, int, int] | None
    reported: str | None

    @property
    def supported(self) -> bool:
        return git_supported(self.version)


@dataclass(frozen=True)
class RuntimeEnvironment:
    system: SystemName
    container_markers: tuple[str, ...]
    git: GitInstallation
    environ: Mapping[str, str]

    @property
    def container(self) -> bool:
        return bool(self.container_markers)

    @property
    def codex_sandbox(self) -> bool:
        return "CODEX_SANDBOX" in self.environ

    @property
    def claude_code(self) -> bool:
        return "CLAUDECODE" in self.environ

    @property
    def home(self) -> Path | None:
        home = self.environ.get("HOME", "")
        return Path(home) if home and Path(home).is_absolute() else None


def detect_runtime_environment(
    environ: Mapping[str, str] | None = None,
    *,
    root: Path = Path("/"),
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    timeout: float = 10.0,
) -> RuntimeEnvironment:
    values = dict(os.environ if environ is None else environ)
    system = cast("SystemName", "darwin" if sys.platform == "darwin" else "linux")
    return RuntimeEnvironment(system, _container_markers(values, root), _git(values, runner, timeout), values)


def _container_markers(environ: Mapping[str, str], root: Path) -> tuple[str, ...]:
    files = tuple(marker for marker in CONTAINER_MARKER_FILES if os.path.lexists(root / marker.lstrip("/")))
    return files + tuple(key for key in CONTAINER_ENVIRONMENT_KEYS if key in environ)


def _git(
    environ: Mapping[str, str], runner: Callable[..., subprocess.CompletedProcess[bytes]], timeout: float
) -> GitInstallation:
    path = shutil.which("git", path=environ.get("PATH", ""))
    if path is None:
        return GitInstallation(None, None, None)
    try:
        completed = runner(
            [path, "--version"],
            capture_output=True,
            check=False,
            env=sanitized_git_environment(dict(environ)),
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return GitInstallation(path, None, None)
    reported = completed.stdout.decode("utf-8", errors="replace").strip().splitlines()
    first = reported[0] if reported else None
    if completed.returncode != 0 or first is None:
        return GitInstallation(path, None, first)
    return GitInstallation(path, parse_git_version(first), first)
