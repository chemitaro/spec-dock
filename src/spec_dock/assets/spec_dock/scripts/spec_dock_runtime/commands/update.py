from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class UpdateArgs(CommandArgs):
    target: str
    invocation_cwd: Path | None = None


def command_specs() -> dict[str, CommandSpec]:
    return {
        "update": CommandSpec(
            add_arguments=_add_update_arguments,
            args_factory=_update_args,
            run=_run_update,
        )
    }


def _add_update_arguments(parser: argparse.ArgumentParser) -> None:
    parser.description = (
        "Update a managed repo by running "
        f"uvx --no-cache --from {UPSTREAM_SOURCE} spec-dock update TARGET. "
        "TARGET defaults to the current working directory."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Managed repo target path to update (default: current working directory)",
    )


def _update_args(ns: argparse.Namespace) -> CommandArgs:
    return UpdateArgs(
        target=str(getattr(ns, "path", ".")),
        invocation_cwd=getattr(ns, "_invocation_cwd", None),
    )


def _run_update(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    typed = _expect_update_args(args)
    target = Path(typed.target).expanduser()
    if typed.invocation_cwd is not None and not target.is_absolute():
        target = typed.invocation_cwd / target
    elif not target.is_absolute():
        target = Path.cwd() / target
    target = Path(os.path.normpath(target))
    command = (
        "uvx",
        "--no-cache",
        "--from",
        UPSTREAM_SOURCE,
        "spec-dock",
        "update",
        str(target),
    )
    return CommandOutcome(
        exit_code=0,
        text=CliText(stdout_lines=[], stderr_lines=[], warnings=[]),
        terminal=InstallerExecRequest(
            kind="installer-exec",
            argv=command,
            environment_policy="inherit-without-lock-bypass",
        ),
    )


def _expect_update_args(args: CommandArgs) -> UpdateArgs:
    if not isinstance(args, UpdateArgs):
        raise RuntimeError("Invalid command args for update")
    return args
