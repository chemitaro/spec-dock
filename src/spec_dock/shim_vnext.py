#!/usr/bin/env -S python3 -I
"""Standalone repository shim: delegate only to the absolute pinned engine."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _common_directory(repo_root: Path) -> Path:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        env=environment,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise ValueError("Git common directory could not be resolved")
    common = Path(completed.stdout.strip())
    if not common.is_absolute() or not common.is_dir() or common.is_symlink():
        raise ValueError("Git common directory is invalid")
    return common.resolve(strict=True)


def _pinned_executable(common_dir: Path) -> Path:
    control_dir = common_dir / "spec-dock/control"
    locator = control_dir / "engine.json"
    control = control_dir / "control.json"
    if any(path.is_symlink() for path in (control_dir, locator, control)):
        raise ValueError("engine control is redirected")
    try:
        engine_data = json.loads(locator.read_text(encoding="utf-8"))
        control_data = json.loads(control.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("engine control is missing or invalid") from error
    if (
        not isinstance(engine_data, dict)
        or set(engine_data) != {"schema_version", "executable", "distribution_root", "distribution_digest"}
        or engine_data.get("schema_version") != 1
        or not isinstance(engine_data.get("executable"), str)
        or not isinstance(engine_data.get("distribution_root"), str)
        or not isinstance(engine_data.get("distribution_digest"), str)
        or _DIGEST.fullmatch(engine_data["distribution_digest"]) is None
        or not isinstance(control_data, dict)
        or control_data.get("engine_digest") != engine_data["distribution_digest"]
    ):
        raise ValueError("engine control identity is invalid")
    executable = Path(engine_data["executable"])
    distribution = Path(engine_data["distribution_root"])
    if (
        not executable.is_absolute()
        or not distribution.is_absolute()
        or executable.is_symlink()
        or distribution.is_symlink()
        or not executable.is_file()
        or not executable.is_relative_to(distribution)
    ):
        raise ValueError("pinned engine executable is unavailable")
    return executable


def main() -> int:
    try:
        repo_root = Path(__file__).resolve(strict=True).parents[2]
        executable = _pinned_executable(_common_directory(repo_root))
        environment = os.environ.copy()
        for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PYTHONSTARTUP"):
            environment.pop(key, None)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        os.execve(str(executable), [str(executable), *sys.argv[1:]], environment)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"spec-dock: {error}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
