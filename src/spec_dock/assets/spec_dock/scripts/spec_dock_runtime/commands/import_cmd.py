from __future__ import annotations

import argparse
from dataclasses import dataclass

from ..application.contracts import ImportNodeRequest, UseCases
from ..presentation.cli_text import render_import_text
from .contracts import CommandArgs, CommandOutcome, CommandSpec
from .targets import parse_github_issue_target


@dataclass(frozen=True)
class ImportInitiativeArgs(CommandArgs):
    issue_number: int
    title: str
    slug: str | None


@dataclass(frozen=True)
class ImportEpicArgs(CommandArgs):
    issue_number: int
    title: str
    slug: str | None
    initiative_id: str | None


@dataclass(frozen=True)
class ImportIssueArgs(CommandArgs):
    issue_number: int
    title: str
    slug: str | None
    epic_id: str | None


def command_specs() -> dict[str, CommandSpec]:
    return {
        "import_initiative": CommandSpec(
            add_arguments=_add_import_initiative_arguments,
            args_factory=_import_initiative_args,
            run=_run_import_initiative,
        ),
        "import_epic": CommandSpec(
            add_arguments=_add_import_epic_arguments,
            args_factory=_import_epic_args,
            run=_run_import_epic,
        ),
        "import_issue": CommandSpec(
            add_arguments=_add_import_issue_arguments,
            args_factory=_import_issue_args,
            run=_run_import_issue,
        ),
    }


def _add_import_initiative_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "target",
        help="GitHub issue number (123 / #123 / URL; URL is parsed for number only; owner/repo is ignored)",
    )
    parser.add_argument("--title", required=True, help="spec-dock title to store (GitHub title is not imported)")
    parser.add_argument("--slug")


def _add_import_epic_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "target",
        help="GitHub issue number (123 / #123 / URL; URL is parsed for number only; owner/repo is ignored)",
    )
    parser.add_argument("--title", required=True, help="spec-dock title to store (GitHub title is not imported)")
    parser.add_argument("--slug")
    parser.add_argument(
        "--initiative",
        help="Parent initiative (e.g. 123 / init-00123 / init-local-00001). Omit to resolve from active.",
    )


def _add_import_issue_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "target",
        help="GitHub issue number (123 / #123 / URL; URL is parsed for number only; owner/repo is ignored)",
    )
    parser.add_argument("--title", required=True, help="spec-dock title to store (GitHub title is not imported)")
    parser.add_argument("--slug")
    parser.add_argument(
        "--epic",
        help="Parent epic (e.g. 123 / epic-00123 / epic-local-00001). Omit to resolve from active.",
    )


def _import_initiative_args(ns: argparse.Namespace) -> CommandArgs:
    return ImportInitiativeArgs(
        issue_number=parse_github_issue_target(str(ns.target)),
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
    )


def _import_epic_args(ns: argparse.Namespace) -> CommandArgs:
    return ImportEpicArgs(
        issue_number=parse_github_issue_target(str(ns.target)),
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
        initiative_id=getattr(ns, "initiative", None),
    )


def _import_issue_args(ns: argparse.Namespace) -> CommandArgs:
    return ImportIssueArgs(
        issue_number=parse_github_issue_target(str(ns.target)),
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
        epic_id=getattr(ns, "epic", None),
    )


def _run_import_initiative(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_import_initiative_args(args)
    result = use_cases.import_initiative(
        ImportNodeRequest(
            issue_number=typed.issue_number,
            title=typed.title,
            slug=typed.slug,
            parent_id=None,
        )
    )
    return CommandOutcome(exit_code=0, text=render_import_text(result))


def _run_import_epic(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_import_epic_args(args)
    result = use_cases.import_epic(
        ImportNodeRequest(
            issue_number=typed.issue_number,
            title=typed.title,
            slug=typed.slug,
            parent_id=typed.initiative_id,
        )
    )
    return CommandOutcome(exit_code=0, text=render_import_text(result))


def _run_import_issue(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_import_issue_args(args)
    result = use_cases.import_issue(
        ImportNodeRequest(
            issue_number=typed.issue_number,
            title=typed.title,
            slug=typed.slug,
            parent_id=typed.epic_id,
        )
    )
    return CommandOutcome(exit_code=0, text=render_import_text(result))


def _expect_import_initiative_args(args: CommandArgs) -> ImportInitiativeArgs:
    if not isinstance(args, ImportInitiativeArgs):
        raise RuntimeError("Invalid command args for import initiative")
    return args


def _expect_import_epic_args(args: CommandArgs) -> ImportEpicArgs:
    if not isinstance(args, ImportEpicArgs):
        raise RuntimeError("Invalid command args for import epic")
    return args


def _expect_import_issue_args(args: CommandArgs) -> ImportIssueArgs:
    if not isinstance(args, ImportIssueArgs):
        raise RuntimeError("Invalid command args for import issue")
    return args

