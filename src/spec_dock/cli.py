"""Public installer adapter for the provider lifecycle engine.

The installer deliberately contains no lifecycle state machine.  It parses
the public command line, normalizes the target, delegates to
``ProviderLifecycleEngine``, and emits the already-validated Wire result.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import NoReturn, cast

from spec_dock import __version__
from spec_dock.provider_lifecycle import execute_provider_lifecycle
from spec_dock.provider_lifecycle.api import invalid_provider_lifecycle_request
from spec_dock.provider_lifecycle.contracts import LifecycleMode, LifecycleRequest, Operation
from spec_dock.provider_lifecycle.wire import serialize_public_result


class _ArgumentError(ValueError):
    """A parser failure that must still use the closed lifecycle result wire."""


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _ArgumentError(message)


def _tool_version() -> str:
    """Return the source version while retaining installed-package support."""

    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        source = pyproject.read_text(encoding="utf-8")
    except OSError:
        return __version__
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', source)
    return match.group(1) if match else __version__


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = _ArgumentParser(prog="spec-dock")
    parser.add_argument("--version", action="version", version=f"spec-dock {_tool_version()}")
    subparsers = parser.add_subparsers(dest="command", required=True, parser_class=_ArgumentParser)

    init = subparsers.add_parser("init", help="Install the provider lifecycle into a project")
    init.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    init.add_argument("--force", action="store_true", help="Replace provider-owned tooling in the target")
    init.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    init.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)

    update = subparsers.add_parser("update", help="Update provider-owned tooling in a project")
    update.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    update.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    update.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)

    uninstall = subparsers.add_parser("uninstall", help="Remove provider tooling while preserving consumer data")
    uninstall.add_argument("path", nargs="?", default=".", help="Target project path (default: current directory)")
    uninstall.add_argument("--apply", action="store_true", help="Apply the uninstall operation")
    specs = uninstall.add_mutually_exclusive_group()
    specs.add_argument("--keep-specs", action="store_true", help="Preserve the consumer spec history")
    specs.add_argument("--remove-specs", action="store_true", help="Deprecated: spec history is never removed")
    uninstall.add_argument("--json", action="store_true", help="Emit exactly one JSON object on stdout")
    uninstall.add_argument("--provider-cleanup-token", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def _target(path: str) -> Path:
    return Path(path).expanduser().absolute()


def _request(namespace: argparse.Namespace, target: Path) -> LifecycleRequest:
    if namespace.command == "init":
        return LifecycleRequest(
            str(target),
            "apply",
            True,
            operation="install",
            seed_policy="create-if-absent",
        )
    if namespace.command == "update":
        return LifecycleRequest(
            str(target),
            "apply",
            True,
            operation="update",
            seed_policy="preserve-only",
        )
    mode = cast("LifecycleMode", "apply" if namespace.apply else "dry-run")
    return LifecycleRequest(
        str(target),
        mode,
        bool(namespace.apply),
        specs_mode="remove" if namespace.remove_specs else "keep" if namespace.keep_specs else None,
        operation="uninstall",
        seed_policy="preserve-only",
    )


def _exit_code(status: str) -> int:
    if status in {"completed", "completed_with_warnings", "planned"}:
        return 0
    if status == "error":
        return 2
    return 1


def _none(value: object) -> str:
    return "none" if value is None else str(value)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _render_uninstall_text(result) -> str:
    continuation = result.continuation
    summary = result.summary
    lines = [
        f"spec-dock uninstall {result.mode} for {result.target}",
        f"status: {result.status}",
        f"code: {result.code}",
        f"phase: {result.phase}",
        f"last-completed-phase: {result.last_completed_phase}",
        f"operation: {_none(result.operation)}",
        f"candidate-digest: {_none(result.candidate_digest)}",
        f"seed-policy: {_none(result.seed_policy)}",
        f"mutation-started: {_bool_text(result.mutation_started)}",
        f"bootstrap-rolled-back: {_bool_text(result.bootstrap_rolled_back)}",
        f"next-action: {continuation['next_action']}",
        f"next-command: {_none(continuation['next_command'])}",
        f"after-cleanup-action: {continuation['after_cleanup_action']}",
        f"after-cleanup-command: {_none(continuation['after_cleanup_command'])}",
        "summary: "
        f"planned={summary['planned']} completed={summary['completed']} preserved={summary['preserved']} "
        f"pending={summary['pending']} failed={summary['failed']} warnings={summary['warnings']}",
    ]
    lines.extend(
        f"action: {action.path} category={action.category} status={action.status} reason={action.reason}"
        for action in result.actions
    )
    lines.extend(f"guidance: {guidance}" for guidance in result.guidance)
    lines.extend(f"warning: {warning}" for warning in result.warnings)
    lines.extend(f"error: {error}" for error in result.errors)
    return "\n".join(lines)


def _render_text(result, command: str) -> tuple[str, str]:
    if command == "uninstall":
        return _render_uninstall_text(result), ""
    if result.code == "terminal-cleanup-completed":
        return (
            "spec-dock: terminal cleanup completed; no lifecycle operation was executed.\n"
            f"next: {_none(result.continuation['next_command'])}",
            "",
        )
    if result.code == "terminal-cleanup-failed":
        return (
            "",
            "error: terminal-cleanup-failed: The requested tooling state is durable, but owned stage cleanup failed; "
            "follow the continuation object exactly.\n"
            f"next: {_none(result.continuation['next_command'])}\n"
            f"after-cleanup: {_none(result.continuation['after_cleanup_command'])}",
        )
    if result.code == "lifecycle-preparation-failed":
        return (
            "",
            "error: lifecycle-preparation-failed: Lifecycle preparation could not be completed; preserve the current "
            "state and follow the continuation object exactly.\n"
            f"next: {_none(result.continuation['next_command'])}",
        )
    if result.code in {
        "repository-operation-busy",
        "repository-coordination-unavailable",
        "unsafe-repository-binding",
    }:
        return "", f"error: {result.code}: {result.errors[0]}"
    if result.status in {"completed", "completed_with_warnings"}:
        lines = [f"spec-dock: ok ({command}) -> {result.target}"]
        if result.warnings:
            lines.append(f"warning: {result.warnings[0]}")
            lines.append(f"next: {_none(result.continuation['next_command'])}")
        return "\n".join(lines), ""
    error = result.errors[0] if result.errors else f"The SpecDock {command} request could not be completed."
    lines = [f"error: {result.code}: {error}"]
    if result.continuation["next_command"] is not None:
        lines.append(f"next: {result.continuation['next_command']}")
    return "", "\n".join(lines)


def _invalid_request(argv: list[str]) -> tuple[LifecycleRequest, str]:
    command = argv[0] if argv and argv[0] in {"init", "update", "uninstall"} else None
    operation: Operation | None
    if command == "uninstall":
        mode = cast("LifecycleMode", "apply" if "--apply" in argv else "dry-run")
        operation = "uninstall"
    else:
        mode = "apply"
        operation = "install" if command == "init" else "update" if command == "update" else None
    target = _target(".")
    if command is not None:
        ignored_values = {"--provider-cleanup-token"}
        for index, value in enumerate(argv[1:], start=1):
            if value.startswith("-"):
                if value in ignored_values:
                    continue
                continue
            if index > 1 and argv[index - 1] in ignored_values:
                continue
            target = _target(value)
            break
    request = LifecycleRequest(
        str(target),
        mode,
        mode == "apply",
        specs_mode="keep" if "--keep-specs" in argv else "remove" if "--remove-specs" in argv else None,
        operation=operation,
    )
    return request, "uninstall" if command == "uninstall" else command or "init"


def _emit_text(stdout: str, stderr: str) -> None:
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """Run the public installer command and return its process status."""

    arguments = sys.argv[1:] if argv is None else argv
    try:
        namespace = _parse_args(arguments)
    except _ArgumentError:
        request, command = _invalid_request(arguments)
        result = invalid_provider_lifecycle_request(request)
        if "--json" in arguments:
            print(serialize_public_result(result).decode("utf-8"), end="")
        else:
            stdout, stderr = _render_text(result, command)
            _emit_text(stdout, stderr)
        return _exit_code(result.status)
    target = _target(namespace.path)
    request = _request(namespace, target)
    json_requested = bool(getattr(namespace, "json", False))
    result = execute_provider_lifecycle(
        request,
        force=True if namespace.command == "init" and namespace.force else None,
        cleanup_token=getattr(namespace, "provider_cleanup_token", None),
    )
    if json_requested:
        print(serialize_public_result(result).decode("utf-8"), end="")
    else:
        stdout, stderr = _render_text(result, namespace.command)
        _emit_text(stdout, stderr)
    return _exit_code(result.status)


if __name__ == "__main__":
    raise SystemExit(main())
