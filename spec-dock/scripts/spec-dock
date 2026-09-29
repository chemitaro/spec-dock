#!/usr/bin/env -S python3 -I
"""Standalone repository shim: delegate only to the absolute pinned engine."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


def _json_requested(arguments: list[str]) -> bool:
    return "--json" in arguments[: arguments.index("--") if "--" in arguments else len(arguments)]


def _preflight_failure(message: str) -> None:
    if not _json_requested(sys.argv[1:]):
        print(f"spec-dock: {message}", file=sys.stderr)
        return
    print(
        json.dumps(
            {
                "schema_version": "specdock.cli/v1",
                "command": "entrypoint",
                "status": "failed",
                "operation_id": None,
                "target": None,
                "data": {"help": None},
                "effects": [],
                "warnings": [],
                "error": {"code": "ENGINE_PREFLIGHT_FAILED", "message": message, "details": {}},
                "recovery": None,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def _distribution_digest(root: Path) -> str:
    """Verify the complete external package before executing any of its code."""
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("engine distribution root is invalid")
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("engine distribution contains a symlink")
        if path.is_file():
            files.append(path)
        elif not path.is_dir():
            raise ValueError("engine distribution contains an unsupported entry")
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        metadata = path.stat()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update((metadata.st_mode & 0o111).to_bytes(2, "big"))
        digest.update(metadata.st_size.to_bytes(8, "big"))
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest()


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


def _bound_invocation(repo_root: Path) -> None:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    completed = subprocess.run(
        ["git", "-C", str(Path.cwd()), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
        env=environment,
    )
    if (
        completed.returncode != 0
        or not completed.stdout.strip()
        or Path(completed.stdout.strip()).resolve() != repo_root
    ):
        raise ValueError("repository shim must run from its installed worktree")
    arguments = sys.argv[1:]
    if any(arguments[index : index + 2] == ["installation", "init"] for index in range(len(arguments) - 1)):
        raise ValueError("installation init must use the external fixed engine")
    for index, item in enumerate(arguments):
        if item == "--":
            break
        if item == "--project":
            if index + 1 >= len(arguments):
                raise ValueError("--project requires a path")
            value = arguments[index + 1]
        elif item.startswith("--project="):
            value = item.split("=", 1)[1]
        else:
            continue
        target = Path(value).expanduser()
        if not target.is_absolute():
            target = Path.cwd() / target
        if target.resolve(strict=True) != repo_root:
            raise ValueError("repository shim --project differs from its installed worktree")


def _pinned_executable(common_dir: Path, repo_root: Path) -> Path:
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
        or not os.access(executable, os.X_OK)
        or not executable.is_relative_to(distribution)
        or distribution.resolve(strict=True).is_relative_to(repo_root)
        or repo_root.is_relative_to(distribution.resolve(strict=True))
    ):
        raise ValueError("pinned engine executable is unavailable")
    if _distribution_digest(distribution) != engine_data["distribution_digest"]:
        raise ValueError("pinned engine distribution digest mismatch")
    return executable


def main() -> int:
    try:
        repo_root = Path(__file__).resolve(strict=True).parents[2]
        _bound_invocation(repo_root)
        executable = _pinned_executable(_common_directory(repo_root), repo_root)
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PYTHONSTARTUP"):
            environment.pop(key, None)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        os.execve(str(executable), [str(executable), *sys.argv[1:]], environment)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        _preflight_failure(str(error))
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
