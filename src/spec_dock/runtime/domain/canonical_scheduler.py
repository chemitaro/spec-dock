"""Which periodic mechanism runs the sync, and the exact job files it installs (Epic ch. 5, R-C7)."""

from __future__ import annotations

from dataclasses import dataclass
import plistlib
import shlex
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from spec_dock.runtime.domain.canonical_sync_state import SchedulerKind

LAUNCHD_LABEL: Final = "io.github.chemitaro.spec-dock.canonical-sync"
SYSTEMD_SERVICE: Final = "spec-dock-canonical-sync.service"
SYSTEMD_TIMER: Final = "spec-dock-canonical-sync.timer"
INTERVAL_SECONDS: Final = 60
LOG_FILE: Final = "canonical-sync.log"
_LAUNCHD_PATH_TAIL: Final = "/usr/bin:/bin:/usr/sbin:/sbin"
_SYSTEMD_PATH_TAIL: Final = "/usr/local/bin:/usr/bin:/bin"


@dataclass(frozen=True)
class SchedulerSpec:
    """What a periodic job runs: this spec-dock, with the root computed at link time and the recorded git first."""

    executable: Path
    state_root: Path
    git_dir: Path
    home: Path
    gh_dir: Path | None = None  # the gh found at link time, so step 7 finds gh in the job's narrow PATH

    def search_path(self, tail: str) -> str:
        directories = [str(self.git_dir)]
        if self.gh_dir is not None and self.gh_dir != self.git_dir:
            directories.append(str(self.gh_dir))
        return ":".join([*directories, tail])

    @property
    def log(self) -> Path:
        return self.state_root / LOG_FILE

    def arguments(self) -> tuple[str, ...]:
        return (str(self.executable), "canonical", "sync", "--registered", "--state-root", str(self.state_root))


def select_scheduler(
    system: Literal["darwin", "linux"],
    *,
    systemd_present: bool | None,
    systemd_user: bool | None,
    previous: SchedulerKind | None,
) -> SchedulerKind:
    """launchd on macOS; a usable systemd user manager on Linux; otherwise the resident loop. Keep a usable choice."""
    systemd = bool(systemd_present) and bool(systemd_user)
    # An unknown user manager (None: its bus was unreachable) keeps a previous systemd choice.
    keeps_systemd = bool(systemd_present) and systemd_user is not False
    usable = {"launchd": system == "darwin", "systemd": system == "linux" and keeps_systemd, "loop": system == "linux"}
    if previous is not None and usable[previous]:
        return previous
    if system == "darwin":
        return "launchd"
    return "systemd" if systemd else "loop"


def launchd_plist(spec: SchedulerSpec, *, label: str = LAUNCHD_LABEL) -> bytes:
    return plistlib.dumps({
        "Label": label,
        "ProgramArguments": list(spec.arguments()),
        "WorkingDirectory": str(spec.home),
        "StartInterval": INTERVAL_SECONDS,
        "RunAtLoad": True,
        "StandardOutPath": str(spec.log),
        "StandardErrorPath": str(spec.log),
        "EnvironmentVariables": {"PATH": spec.search_path(_LAUNCHD_PATH_TAIL)},
    })


def systemd_quote(value: str, *, command: bool = False) -> str:
    """Escape specifiers (%), in a command line also variables ($), and quote whitespace, quotes or backslashes.

    systemd expands $VAR only in ExecStart=; in Environment= a `$` is an ordinary character.
    """
    escaped = value.replace("%", "%%")
    if command:
        escaped = escaped.replace("$", "$$")
    if any(character.isspace() or character in "\"'\\" for character in escaped):
        return '"' + escaped.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return escaped


def systemd_units(spec: SchedulerSpec) -> tuple[str, str]:
    command = " ".join(systemd_quote(argument, command=True) for argument in spec.arguments())
    service = (
        "[Unit]\n"
        "Description=SpecDock canonical sync\n"
        "[Service]\n"
        "Type=oneshot\n"
        "WorkingDirectory=%h\n"
        f"Environment={systemd_quote('PATH=' + spec.search_path(_SYSTEMD_PATH_TAIL))}\n"
        f"ExecStart={command}\n"
    )
    timer = (
        "[Unit]\n"
        "Description=SpecDock canonical sync timer\n"
        "[Timer]\n"
        "OnActiveSec=10s\n"
        f"OnUnitActiveSec={INTERVAL_SECONDS}s\n"
        "AccuracySec=5s\n"
        "[Install]\n"
        "WantedBy=timers.target\n"
    )
    return service, timer


def restart_line(state_root: Path) -> str:
    """The one line a container start script runs to bring the resident runner back."""
    return f"spec-dock canonical sync --registered --loop --detach --state-root {shlex.quote(str(state_root))}"


def state_root_argument(arguments: Sequence[object]) -> Path | None:
    """The `--state-root` value of an installed job's command line, or None when it has none."""
    from itertools import pairwise
    from pathlib import Path

    for flag, value in pairwise(arguments):
        if flag == "--state-root" and isinstance(value, str) and value:
            return Path(value)
    return None
