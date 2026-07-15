#!/usr/bin/env python3
"""Invoke a configured ChatGPT backend command without hardcoded local paths."""

import argparse
from collections.abc import Mapping, Sequence
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

STATUS_EXIT_CODES = {
    "pass": 0,
    "fail": 1,
    "blocked": 2,
    "stale": 3,
    "rejected": 4,
}

PRIMARY_ENV = "SPECDOCK_CHATGPT_COMMAND"
FALLBACK_ENV = "ORACLE_CHATGPT_COMMAND"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="Conversation/session slug to pass to the backend.")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt text to pass to the backend.")
    parser.add_argument("--file", action="append", default=[], help="Attachment path. May be repeated.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print resolved invocation JSON without running backend."
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=0,
        help="Backend timeout in seconds. 0 disables the adapter timeout.",
    )
    args = parser.parse_args(argv)

    resolved = resolve_backend_command(os.environ)
    if resolved["status"] != "pass":
        _print_diagnostic(resolved)
        return STATUS_EXIT_CODES[resolved["status"]]

    file_errors = _validate_files(args.file)
    if file_errors:
        _print_diagnostic(_diagnostic("blocked", file_errors))
        return STATUS_EXIT_CODES["blocked"]

    invocation_argv = _invocation_argv(
        resolved["backend_argv"],
        slug=args.slug,
        prompt=args.prompt,
        files=args.file,
    )
    timeout = args.timeout_seconds if args.timeout_seconds and args.timeout_seconds > 0 else None

    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "pass",
                    "backend_env": resolved["backend_env"],
                    "backend_argv": resolved["backend_argv"],
                    "invocation_argv": invocation_argv,
                    "files": list(args.file),
                    "cwd": _display_path(Path.cwd()),
                    "timeout_seconds": timeout,
                    "dry_run": True,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return STATUS_EXIT_CODES["pass"]

    try:
        completed = subprocess.run(
            invocation_argv,
            cwd=Path.cwd(),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        _print_diagnostic(
            _diagnostic(
                "blocked",
                [f"configured ChatGPT backend command was not found; set {PRIMARY_ENV} or {FALLBACK_ENV}"],
            )
        )
        return STATUS_EXIT_CODES["blocked"]
    except subprocess.TimeoutExpired:
        _print_diagnostic(_diagnostic("blocked", ["configured ChatGPT backend command timed out"]))
        return STATUS_EXIT_CODES["blocked"]

    if completed.stdout:
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    return completed.returncode


def resolve_backend_command(env: Mapping[str, str]) -> dict[str, object]:
    for name in (PRIMARY_ENV, FALLBACK_ENV):
        value = (env.get(name) or "").strip()
        if not value:
            continue
        try:
            backend_argv = shlex.split(value, posix=True)
        except ValueError:
            return _diagnostic("blocked", [f"{name} could not be parsed as an argv command"])
        if not backend_argv:
            return _diagnostic("blocked", [f"{name} did not contain a command"])
        return {
            "status": "pass",
            "backend_env": name,
            "backend_argv": backend_argv,
            "errors": [],
        }

    return _diagnostic(
        "blocked",
        [f"ChatGPT backend command is not configured; set {PRIMARY_ENV} or {FALLBACK_ENV}"],
    )


def _invocation_argv(backend_argv: object, *, slug: str, prompt: str, files: Sequence[str]) -> list[str]:
    argv = list(backend_argv) if isinstance(backend_argv, list) else []
    argv.extend(["--slug", slug, "-p", prompt])
    for path in files:
        argv.extend(["--file", path])
    return argv


def _validate_files(files: Sequence[str]) -> list[str]:
    errors: list[str] = []
    for value in files:
        path = Path(value)
        if not path.exists():
            errors.append(f"attachment file does not exist: {_safe_display_path(value)}")
        elif not path.is_file():
            errors.append(f"attachment path is not a file: {_safe_display_path(value)}")
    return errors


def _diagnostic(status: str, errors: list[str]) -> dict[str, object]:
    return {"status": status, "errors": errors}


def _print_diagnostic(payload: Mapping[str, object]) -> None:
    print(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True), file=sys.stderr)


def _display_path(path: Path) -> str:
    try:
        root = _git_root()
        return path.resolve().relative_to(root).as_posix() or "."
    except (OSError, RuntimeError, ValueError):
        return "."


def _git_root() -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("not in a git repository")
    return Path(completed.stdout.strip()).resolve()


def _safe_display_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return path.name
    return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
