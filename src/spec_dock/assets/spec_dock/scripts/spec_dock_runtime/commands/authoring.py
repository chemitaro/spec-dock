from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_dock_runtime.commands.contracts import CommandArgs, CommandOutcome, CommandSpec
from spec_dock_runtime.presentation.contracts import CliText

if TYPE_CHECKING:
    import argparse

    from spec_dock_runtime.application.contracts import UseCases


@dataclass(frozen=True)
class AuthoringDeferredArgs(CommandArgs):
    command: str
    next_issue: str


_DEFERRED_COMMANDS: dict[str, tuple[str, str]] = {
    "authoring_preflight_github_sync": ("authoring preflight github-sync", "iss-00298"),
    "authoring_pack_prepare": ("authoring pack prepare", "iss-00299"),
    "authoring_backend_invoke": ("authoring backend invoke", "iss-00300"),
    "authoring_pack_review": ("authoring pack review", "iss-00301"),
    "authoring_pack_stage": ("authoring pack stage", "iss-00301"),
    "authoring_validate_initiative_epic_candidates": (
        "authoring validate initiative-epic-candidates",
        "iss-00302",
    ),
    "authoring_validate_epic_issue_candidates": ("authoring validate epic-issue-candidates", "iss-00302"),
    "authoring_validate_issue_draft_adoption": ("authoring validate issue-draft-adoption", "iss-00303"),
    "authoring_validate_selected_skeleton_fill": ("authoring validate selected-skeleton-fill", "iss-00303"),
    "authoring_approval_check": ("authoring approval check", "iss-00305"),
}


def command_specs() -> dict[str, CommandSpec]:
    return {
        key: CommandSpec(
            add_arguments=_add_deferred_arguments,
            args_factory=_deferred_args_factory(command=command, next_issue=next_issue),
            run=_run_deferred,
        )
        for key, (command, next_issue) in _DEFERRED_COMMANDS.items()
    }


def _add_deferred_arguments(parser: argparse.ArgumentParser) -> None:
    del parser


def _deferred_args_factory(*, command: str, next_issue: str):
    def _deferred_args(ns: argparse.Namespace) -> CommandArgs:
        del ns
        return AuthoringDeferredArgs(command=command, next_issue=next_issue)

    return _deferred_args


def _run_deferred(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    del use_cases
    deferred_args = _expect_deferred_args(args)
    return CommandOutcome(
        exit_code=1,
        text=CliText(
            stdout_lines=[
                f"spec-dock: deferred (authoring) command={deferred_args.command}",
                "status=deferred",
                "authority=evidence_only",
                f"next_issue={deferred_args.next_issue}",
                "reason=not_implemented_in_this_issue",
            ],
            stderr_lines=[],
            warnings=[],
        ),
    )


def _expect_deferred_args(args: CommandArgs) -> AuthoringDeferredArgs:
    if not isinstance(args, AuthoringDeferredArgs):
        raise RuntimeError("Invalid command args for authoring")
    return args
