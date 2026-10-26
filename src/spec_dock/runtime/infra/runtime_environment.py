"""The runtime environment a canonical command decides from, computed once and injectable (contract C11).

Procedures take a RuntimeEnvironment argument; command handlers call detect_runtime_environment() through
this module so a CLI test can replace it. I-3 adds systemd-user and linger fields with defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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
    # Filled only by detect_service_manager (canonical link step 6 and canonical status); None means unknown.
    systemd_present: bool | None = None
    systemd_user: bool | None = None
    linger: bool | None = None
    user: str | None = None

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


SYSTEMD_RUNTIME_DIRECTORY: Final = "/run/systemd/system"
BUS_RETRIES: Final = 5
_BUS_FAILURE: Final = "Failed to connect to bus"


def detect_service_manager(
    environment: RuntimeEnvironment,
    *,
    root: Path = Path("/"),
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    sleep: Callable[[float], None] | None = None,
    timeout: float = 10.0,
) -> RuntimeEnvironment:
    """Add the systemd user manager and linger facts on Linux (Epic ch. 5); macOS is returned unchanged.

    `systemctl --user is-system-running` counts when it prints running or degraded; "Failed to connect to
    bus" (seen right after a VM boots) is retried once a second, five times at most.
    """
    if environment.system != "linux":
        return environment
    import getpass
    import time

    wait = sleep or time.sleep
    user = environment.environ.get("USER") or environment.environ.get("LOGNAME")
    if not user:
        try:
            user = getpass.getuser()
        except (KeyError, OSError):
            user = None
    present = Path(root / SYSTEMD_RUNTIME_DIRECTORY.lstrip("/")).is_dir()
    systemd_user: bool | None = False
    if present:
        systemd_user = None
        for attempt in range(BUS_RETRIES + 1):
            completed = _run_quietly(runner, ["systemctl", "--user", "is-system-running"], environment, timeout)
            if completed is None:
                break
            state = completed.stdout.decode("utf-8", errors="replace").strip().splitlines()
            if state and state[0] in ("running", "degraded"):
                systemd_user = True
                break
            if _BUS_FAILURE not in completed.stderr.decode("utf-8", errors="replace"):
                systemd_user = False
                break
            if attempt == BUS_RETRIES:
                break  # still no bus: unknown (a sandbox, su, no XDG_RUNTIME_DIR), not "no systemd"
            wait(1.0)
    linger: bool | None = None
    if user:
        completed = _run_quietly(
            runner, ["loginctl", "show-user", user, "-p", "Linger", "--value"], environment, timeout
        )
        value = completed.stdout.decode("utf-8", errors="replace").strip() if completed is not None else ""
        linger = True if value == "yes" else (False if value == "no" else None)
    return replace(environment, systemd_present=present, systemd_user=systemd_user, linger=linger, user=user)


def _run_quietly(
    runner: Callable[..., subprocess.CompletedProcess[bytes]],
    argv: list[str],
    environment: RuntimeEnvironment,
    timeout: float,
) -> subprocess.CompletedProcess[bytes] | None:
    try:
        return runner(argv, capture_output=True, check=False, env=dict(environment.environ), timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def probe_git(
    path: str, *, runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run
) -> GitInstallation:
    """The version of one recorded git (the periodic job's), without looking at PATH."""
    if not Path(path).is_absolute() or not os.access(path, os.X_OK):
        return GitInstallation(path, None, None)
    return _git({"PATH": str(Path(path).parent)}, lambda argv, **kwargs: runner([path, *argv[1:]], **kwargs), 10.0)
