from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import TYPE_CHECKING, cast

from spec_dock_runtime.commands.contracts import (
    CommandArgs,
    CommandOutcome,
    CommandSpec,
    InstallerExecRequest,
)
from spec_dock_runtime.presentation.contracts import CliText

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.contracts import UseCases

UPSTREAM_SOURCE = "git+https://github.com/chemitaro/spec-dock"
_PURGE_REMOVED_CODE = "spec-history-purge-removed"
_PURGE_REMOVED_ERROR = "Spec history purge has been removed; uninstall is tooling-only."
_PURGE_REMOVED_GUIDANCE = (
    "Use tooling-only uninstall without --remove-specs.",
    "Spec history and Workbench data remain consumer-owned.",
)


def _none(value: object) -> str:
    return "none" if value is None else str(value)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _render_uninstall_text(payload: dict[str, object]) -> list[str]:
    continuation = cast("dict[str, object]", payload["continuation"])
    summary = cast("dict[str, int]", payload["summary"])
    actions = cast("list[dict[str, str]]", payload["actions"])
    guidance = cast("list[str]", payload["guidance"])
    warnings = cast("list[str]", payload["warnings"])
    errors = cast("list[str]", payload["errors"])
    lines = [
        f"spec-dock uninstall {payload['mode']} for {payload['target']}",
        f"status: {payload['status']}",
        f"code: {payload['code']}",
        f"phase: {payload['phase']}",
        f"last-completed-phase: {payload['last_completed_phase']}",
        f"operation: {_none(payload['operation'])}",
        f"candidate-digest: {_none(payload['candidate_digest'])}",
        f"seed-policy: {_none(payload['seed_policy'])}",
        f"mutation-started: {_bool_text(bool(payload['mutation_started']))}",
        f"bootstrap-rolled-back: {_bool_text(bool(payload['bootstrap_rolled_back']))}",
        f"next-action: {continuation['next_action']}",
        f"next-command: {_none(continuation['next_command'])}",
        f"after-cleanup-action: {continuation['after_cleanup_action']}",
        f"after-cleanup-command: {_none(continuation['after_cleanup_command'])}",
        "summary: "
        f"planned={summary['planned']} completed={summary['completed']} preserved={summary['preserved']} "
        f"pending={summary['pending']} failed={summary['failed']} warnings={summary['warnings']}",
    ]
    lines.extend(
        f"action: {action['path']} category={action['category']} status={action['status']} reason={action['reason']}"
        for action in actions
    )
    lines.extend(f"guidance: {item}" for item in guidance)
    lines.extend(f"warning: {warning}" for warning in warnings)
    lines.extend(f"error: {error}" for error in errors)
    return lines


@dataclass(frozen=True)
class UninstallArgs(CommandArgs):
    target: str
    apply: bool
    keep_specs: bool
    remove_specs: bool
    json: bool


def command_specs() -> dict[str, CommandSpec]:
    return {
        "uninstall": CommandSpec(
            add_arguments=_add_uninstall_arguments,
            args_factory=_uninstall_args,
            run=_run_uninstall,
        )
    }


def _add_uninstall_arguments(parser: argparse.ArgumentParser) -> None:
    parser.description = (
        "Uninstall SpecDock-managed repo assets by running "
        f"uvx --no-cache --from {UPSTREAM_SOURCE} spec-dock uninstall TARGET. "
        "TARGET defaults to the current working directory."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Managed repo target path to uninstall (default: current working directory)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the uninstall plan instead of showing a dry-run plan",
    )
    specs_mode = parser.add_mutually_exclusive_group()
    specs_mode.add_argument(
        "--keep-specs",
        action="store_true",
        help="Keep spec history while uninstalling managed tooling",
    )
    specs_mode.add_argument(
        "--remove-specs",
        action="store_true",
        help="Remove spec history while uninstalling managed tooling",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Forward JSON output mode to the installer CLI",
    )


def _uninstall_args(ns: argparse.Namespace) -> CommandArgs:
    return UninstallArgs(
        target=str(getattr(ns, "path", ".")),
        apply=bool(getattr(ns, "apply", False)),
        keep_specs=bool(getattr(ns, "keep_specs", False)),
        remove_specs=bool(getattr(ns, "remove_specs", False)),
        json=bool(getattr(ns, "json", False)),
    )


def _run_uninstall(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    typed = _expect_uninstall_args(args)
    if typed.remove_specs:
        return _removed_purge_outcome(typed)
    target = Path(typed.target).expanduser().absolute()
    command = [
        "uvx",
        "--no-cache",
        "--from",
        UPSTREAM_SOURCE,
        "spec-dock",
        "uninstall",
        str(target),
    ]
    if typed.apply:
        command.append("--apply")
    if typed.keep_specs:
        command.append("--keep-specs")
    if typed.json:
        command.append("--json")

    return CommandOutcome(
        exit_code=0,
        text=CliText(stdout_lines=[], stderr_lines=[], warnings=[]),
        terminal=InstallerExecRequest(
            kind="installer-exec",
            argv=tuple(command),
            environment_policy="inherit-without-lock-bypass",
        ),
    )


def _removed_purge_outcome(args: UninstallArgs) -> CommandOutcome:
    """Return the request-validation result without observing the target."""

    target = Path(args.target).expanduser().absolute()
    mode = "apply" if args.apply else "dry-run"
    payload = {
        "schema_version": 1,
        "target": str(target),
        "mode": mode,
        "apply": args.apply,
        "specs_mode": "remove",
        "status": "error",
        "code": _PURGE_REMOVED_CODE,
        "operation": None,
        "candidate_digest": None,
        "seed_policy": None,
        "mutation_started": False,
        "bootstrap_rolled_back": False,
        "phase": "request-validation",
        "last_completed_phase": "not-started",
        "retry_command": None,
        "continuation": {
            "next_action": "none",
            "next_command": None,
            "after_cleanup_action": "none",
            "after_cleanup_command": None,
        },
        "failed_paths": [],
        "pending_paths": [],
        "summary": {
            "planned": 0,
            "completed": 0,
            "preserved": 0,
            "pending": 0,
            "failed": 0,
            "warnings": 0,
        },
        "actions": [],
        "guidance": list(_PURGE_REMOVED_GUIDANCE),
        "warnings": [],
        "errors": [_PURGE_REMOVED_ERROR],
    }
    if args.json:
        stdout_lines = [json.dumps(payload, ensure_ascii=False, separators=(",", ":"))]
    else:
        stdout_lines = _render_uninstall_text(payload)
    return CommandOutcome(
        exit_code=2,
        text=CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=[]),
    )


def _expect_uninstall_args(args: CommandArgs) -> UninstallArgs:
    if not isinstance(args, UninstallArgs):
        raise RuntimeError("Invalid command args for uninstall")
    return args
