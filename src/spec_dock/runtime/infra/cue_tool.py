"""The `cue` boundary of CUE Scopes (iss-00473; contract K1 and K3 of epic-00425).

`cue` is found on PATH, its version checked, and called with an argument list (never through a shell) under a
time limit. Its error text is split into errors and positions; deciding which errors matter is left to callers.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

MINIMUM_CUE_VERSION: Final = (0, 17, 1)
CUE_INSTALL_STEP: Final = (
    "Install cue v0.17.1 or later on PATH (for example: go install cuelang.org/go/cmd/cue@v0.17.1), "
    "then run the command again."
)
CUE_NOT_FOUND: Final = "CUE_NOT_FOUND"
CUE_VERSION_UNSUPPORTED: Final = "CUE_VERSION_UNSUPPORTED"
CUE_TIMEOUT: Final = "CUE_TIMEOUT"
CUE_FAILED: Final = "CUE_FAILED"
TIMEOUT_STEP: Final = "Run the command again with a longer --timeout, or split very large CUE documents."
REINSTALL_STEP: Final = "Check that `cue version` runs on PATH; reinstall cue v0.17.1 or later if it does not."

_VERSION = re.compile(r"cue version v(\d+)\.(\d+)\.(\d+)")


class CueToolError(Exception):
    """`cue` cannot be used: missing, too old, timed out or failed to run."""

    def __init__(self, code: str, message: str, *, exit_code: int, next_step: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.next_step = next_step


@dataclass(frozen=True)
class CueRun:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class CuePosition:
    file: Path
    line: int
    column: int


@dataclass(frozen=True)
class CueError:
    """One error of `cue`: the field path it names (None for a syntax error), its text and its positions."""

    path: str | None
    message: str
    positions: tuple[CuePosition, ...]


@dataclass(frozen=True)
class CueTool:
    executable: str
    version: str

    def export(
        self,
        files: Sequence[Path],
        *,
        cwd: Path,
        timeout: float,
        tags: Mapping[str, str] | None = None,
        expression: str | None = None,
    ) -> CueRun:
        """`cue export --out json [-t k=v]... [-e expression] files...`; the caller judges the exit status."""
        argv = [self.executable, "export", "--out", "json"]
        for key, value in (tags or {}).items():
            argv += ["-t", f"{key}={value}"]
        if expression is not None:
            argv += ["-e", expression]
        argv += [str(path) for path in files]
        return _run(argv, cwd=cwd, timeout=timeout)


# A field path: identifiers, quoted labels and list indexes joined by dots (`steps."S-01".status`).
_SEGMENT = r'(?:[A-Za-z_#$][A-Za-z0-9_#$]*|"(?:[^"\\]|\\.)*"|\d+)'
_HEADER = re.compile(rf"^({_SEGMENT}(?:\.{_SEGMENT})*): (.*?):?$")
_POSITION = re.compile(r"^\s+(\S.*?):(\d+):(\d+)$")


def parse_cue_errors(stderr: str, *, cwd: Path) -> tuple[CueError, ...]:
    """Split `cue` error text: an unindented line starts an error, indented `file:line:column` lines are positions.

    Positions are printed relative to the working directory of `cue`; they are made absolute against `cwd`.
    An indented line that is not a position is added to the message of the error before it.
    """
    errors: list[CueError] = []
    for line in stderr.splitlines():
        if not line.strip():
            continue
        position = _POSITION.match(line)
        if line[0].isspace():
            if not errors:
                errors.append(CueError(None, line.strip(), ()))
            elif position is not None:
                last = errors[-1]
                place = CuePosition(_resolve(cwd, position.group(1)), int(position.group(2)), int(position.group(3)))
                errors[-1] = CueError(last.path, last.message, (*last.positions, place))
            else:
                last = errors[-1]
                errors[-1] = CueError(last.path, f"{last.message} {line.strip()}", last.positions)
            continue
        header = _HEADER.match(line)
        if header is not None:
            errors.append(CueError(header.group(1), header.group(2).rstrip(":"), ()))
        else:
            errors.append(CueError(None, line.rstrip().rstrip(":"), ()))
    return tuple(errors)


def _resolve(cwd: Path, printed: str) -> Path:
    return Path(os.path.normpath(cwd / printed))


def locate_cue(*, timeout: float) -> CueTool:
    """The `cue` on PATH at MINIMUM_CUE_VERSION or later; anything else stops with the install step."""
    executable = shutil.which("cue")
    if executable is None:
        raise CueToolError(CUE_NOT_FOUND, "cue is not on PATH", exit_code=3, next_step=CUE_INSTALL_STEP)
    completed = _run([executable, "version"], cwd=None, timeout=timeout)
    if completed.returncode != 0:
        raise CueToolError(
            CUE_FAILED,
            f"`{executable} version` exited with {completed.returncode}",
            exit_code=5,
            next_step=REINSTALL_STEP,
        )
    first = completed.stdout.splitlines()[0].strip() if completed.stdout.strip() else ""
    match = _VERSION.match(first)
    if match is None or tuple(int(part) for part in match.groups()) < MINIMUM_CUE_VERSION:
        found = first or "no version"
        raise CueToolError(
            CUE_VERSION_UNSUPPORTED,
            f"{executable} reports {found!r}; SpecDock needs cue v0.17.1 or later",
            exit_code=3,
            next_step=CUE_INSTALL_STEP,
        )
    return CueTool(executable, first.split()[2])


def _run(argv: list[str], *, cwd: Path | None, timeout: float) -> CueRun:
    """One `cue` process from an argument list (shell=False) under the time limit."""
    try:
        completed = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as error:
        raise CueToolError(
            CUE_TIMEOUT, f"cue did not finish within {timeout:g} seconds", exit_code=5, next_step=TIMEOUT_STEP
        ) from error
    except (OSError, UnicodeDecodeError) as error:
        raise CueToolError(CUE_FAILED, f"cue could not run: {error}", exit_code=5, next_step=REINSTALL_STEP) from error
    return CueRun(completed.returncode, completed.stdout, completed.stderr)
