"""Bound one project-owned init process without retaining or exposing its output."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
import os
import signal
import subprocess
from typing import TYPE_CHECKING

from spec_dock.runtime.infra.git_cli import sanitized_git_environment

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class MakeInitResult:
    started: bool
    returncode: int | None
    timed_out: bool
    diagnostic: str


def run_make_init(path: Path, *, timeout: float) -> MakeInitResult:
    if os.name != "posix":
        return MakeInitResult(False, None, False, "make init process adapter is not connected for this platform")
    environment = sanitized_git_environment()
    for key in ("MAKEFILES", "MAKEFLAGS", "GNUMAKEFLAGS", "MFLAGS", "MAKELEVEL"):
        environment.pop(key, None)
    try:
        process = subprocess.Popen(
            ["make", "init"],
            cwd=path,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            env=environment,
        )
    except OSError:
        return MakeInitResult(False, None, False, "make init could not start")
    timed_out = False
    try:
        returncode = process.wait(timeout=timeout)
    except (subprocess.TimeoutExpired, OSError) as error:
        timed_out = isinstance(error, subprocess.TimeoutExpired)
        with contextlib.suppress(OSError):
            os.killpg(process.pid, signal.SIGKILL)
        try:
            returncode = process.wait(timeout=10)
        except (subprocess.TimeoutExpired, OSError):
            returncode = None
    diagnostic = (
        "make init timed out; output omitted"
        if timed_out
        else "make init finished; output omitted"
        if returncode == 0
        else "make init did not complete; output omitted"
    )
    return MakeInitResult(True, returncode, timed_out, diagnostic)
