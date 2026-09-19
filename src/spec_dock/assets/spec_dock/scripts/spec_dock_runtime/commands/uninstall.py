from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

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
_PURGE_REMOVED_ERROR = "Spec history purge has been removed; uninstall is tooling-only."


@dataclass(frozen=True)
class UninstallArgs(CommandArgs):
    target: str
    apply: bool
    keep_specs: bool
    remove_specs: bool
    json: bool
    invocation_cwd: Path | None = None


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
        help="Unsupported: consumer data is never removed",
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
        invocation_cwd=getattr(ns, "_invocation_cwd", None),
    )


def _run_uninstall(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    typed = _expect_uninstall_args(args)
    if typed.remove_specs:
        return _removed_purge_outcome(typed)
    target = Path(typed.target).expanduser()
    if typed.invocation_cwd is not None and not target.is_absolute():
        target = typed.invocation_cwd / target
    elif not target.is_absolute():
        target = Path.cwd() / target
    target = Path(os.path.normpath(target))
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

    message = _PURGE_REMOVED_ERROR
    text = CliText(
        stdout_lines=[json.dumps({"status": "error", "command": "uninstall", "error": message})] if args.json else [],
        stderr_lines=[] if args.json else [f"error: {message}"],
        warnings=[],
    )
    return CommandOutcome(exit_code=2, text=text)


def _expect_uninstall_args(args: CommandArgs) -> UninstallArgs:
    if not isinstance(args, UninstallArgs):
        raise RuntimeError("Invalid command args for uninstall")
    return args
