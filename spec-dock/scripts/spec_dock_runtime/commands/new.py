from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Literal

from ..application.contracts import (
    CreateDiscussionDocRequest,
    CreateNodeRequest,
    CreateNodeResult,
    UseCases,
)
from ..domain.discussion_docs import CREATABLE_DISCUSSION_DOC_TYPES
from ..presentation.cli_text import render_new_doc_text, render_new_node_text
from ..presentation.contracts import CliText
from .contracts import CommandArgs, CommandOutcome, CommandSpec

_discussion_doc_types = CREATABLE_DISCUSSION_DOC_TYPES


@dataclass(frozen=True)
class NewInitiativeArgs(CommandArgs):
    title: str
    slug: str | None
    create_github_issue: bool
    github_issue_number: int | None


@dataclass(frozen=True)
class NewEpicArgs(CommandArgs):
    initiative_id: str
    title: str
    slug: str | None
    create_github_issue: bool
    github_issue_number: int | None


@dataclass(frozen=True)
class NewIssueArgs(CommandArgs):
    epic_id: str
    title: str
    slug: str | None
    create_github_issue: bool
    github_issue_number: int | None


@dataclass(frozen=True)
class NewDocArgs(CommandArgs):
    doc_type: str
    scope_node_id: str
    scope_kind: Literal["initiative", "epic", "issue"]
    title: str
    slug: str | None


def command_specs() -> dict[str, CommandSpec]:
    return {
        "new_initiative": CommandSpec(
            add_arguments=_add_new_initiative_arguments,
            args_factory=_new_initiative_args,
            run=_run_new_initiative,
        ),
        "new_epic": CommandSpec(
            add_arguments=_add_new_epic_arguments,
            args_factory=_new_epic_args,
            run=_run_new_epic,
        ),
        "new_issue": CommandSpec(
            add_arguments=_add_new_issue_arguments,
            args_factory=_new_issue_args,
            run=_run_new_issue,
        ),
        "new_doc": CommandSpec(
            add_arguments=_add_new_doc_arguments,
            args_factory=_new_doc_args,
            run=_run_new_doc,
        ),
    }


def _add_new_initiative_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    github_group = parser.add_mutually_exclusive_group()
    github_group.add_argument(
        "--create-github-issue",
        action="store_true",
        help="Create and link a new GitHub issue (id becomes init-NNNN)",
    )
    github_group.add_argument(
        "--github-issue",
        type=int,
        help="Existing GitHub issue number to link (id becomes init-NNNN)",
    )


def _add_new_epic_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--initiative",
        required=True,
        help="Parent initiative (e.g. 123 / init-00123 / init-local-00001)",
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    github_group = parser.add_mutually_exclusive_group()
    github_group.add_argument(
        "--create-github-issue",
        action="store_true",
        help="Create and link a new GitHub issue (id becomes epic-NNNN)",
    )
    github_group.add_argument(
        "--github-issue",
        type=int,
        help="Existing GitHub issue number to link (id becomes epic-NNNN)",
    )


def _add_new_issue_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--epic",
        required=True,
        help="Parent epic (e.g. 123 / epic-00123 / epic-local-00001)",
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")
    github_group = parser.add_mutually_exclusive_group()
    github_group.add_argument(
        "--create-github-issue",
        action="store_true",
        help="Create and link a new GitHub issue (default behavior)",
    )
    github_group.add_argument(
        "--github-issue",
        type=int,
        help="Existing GitHub issue number to link (id becomes iss-NNNN)",
    )


def _add_new_doc_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "doc_type",
        metavar="doc_type",
        help=(
            "Discussion doc type: "
            f"{', '.join(_discussion_doc_types)}. "
            "'note' is retired; use 'scratch' for new raw capture docs."
        ),
    )
    scope_group = parser.add_mutually_exclusive_group(required=True)
    scope_group.add_argument("--initiative", help="Scope initiative (e.g. 123 / init-00123 / init-local-00001)")
    scope_group.add_argument("--epic", help="Scope epic (e.g. 123 / epic-00123 / epic-local-00001)")
    scope_group.add_argument("--issue", help="Scope issue (e.g. 123 / iss-00123 / iss-local-00001)")
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug")


def _new_initiative_args(ns: argparse.Namespace) -> CommandArgs:
    return NewInitiativeArgs(
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
        create_github_issue=bool(getattr(ns, "create_github_issue", False)),
        github_issue_number=getattr(ns, "github_issue", None),
    )


def _new_epic_args(ns: argparse.Namespace) -> CommandArgs:
    return NewEpicArgs(
        initiative_id=str(ns.initiative),
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
        create_github_issue=bool(getattr(ns, "create_github_issue", False)),
        github_issue_number=getattr(ns, "github_issue", None),
    )


def _new_issue_args(ns: argparse.Namespace) -> CommandArgs:
    return NewIssueArgs(
        epic_id=str(ns.epic),
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
        create_github_issue=bool(getattr(ns, "create_github_issue", False)),
        github_issue_number=getattr(ns, "github_issue", None),
    )


def _new_doc_args(ns: argparse.Namespace) -> CommandArgs:
    initiative = getattr(ns, "initiative", None)
    epic = getattr(ns, "epic", None)
    issue = getattr(ns, "issue", None)
    if initiative is not None:
        scope_kind: Literal["initiative", "epic", "issue"] = "initiative"
        scope_node_id = initiative
    elif epic is not None:
        scope_kind = "epic"
        scope_node_id = epic
    elif issue is not None:
        scope_kind = "issue"
        scope_node_id = issue
    else:
        raise RuntimeError("scope is required")
    return NewDocArgs(
        doc_type=str(ns.doc_type),
        scope_node_id=str(scope_node_id),
        scope_kind=scope_kind,
        title=str(ns.title),
        slug=getattr(ns, "slug", None),
    )


def _run_new_initiative(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_new_initiative_args(args)

    result = use_cases.create_initiative(
        CreateNodeRequest(
            title=typed.title,
            slug=typed.slug,
            parent_id=None,
            github_mode="link_existing" if typed.github_issue_number is not None else "create",
            github_issue_number=typed.github_issue_number,
        )
    )
    text = render_new_node_text(result)
    if typed.github_issue_number is None:
        text = _prepend_stderr(
            text,
            "spec-dock: (info) creating GitHub issue via gh",
        )
    return CommandOutcome(exit_code=_post_sync_exit_code(result), text=text)


def _run_new_epic(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_new_epic_args(args)

    result = use_cases.create_epic(
        CreateNodeRequest(
            title=typed.title,
            slug=typed.slug,
            parent_id=typed.initiative_id,
            github_mode="link_existing" if typed.github_issue_number is not None else "create",
            github_issue_number=typed.github_issue_number,
        )
    )
    text = render_new_node_text(result)
    if typed.github_issue_number is None:
        text = _prepend_stderr(
            text,
            "spec-dock: (info) creating GitHub issue via gh",
        )
    return CommandOutcome(exit_code=_post_sync_exit_code(result), text=text)


def _run_new_issue(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_new_issue_args(args)

    result = use_cases.create_issue(
        CreateNodeRequest(
            title=typed.title,
            slug=typed.slug,
            parent_id=typed.epic_id,
            github_mode="link_existing" if typed.github_issue_number is not None else "create",
            github_issue_number=typed.github_issue_number,
        )
    )
    text = render_new_node_text(result)
    if typed.github_issue_number is None:
        text = _prepend_stderr(
            text,
            "spec-dock: (info) creating GitHub issue via gh",
        )
    return CommandOutcome(exit_code=_post_sync_exit_code(result), text=text)


def _run_new_doc(args: CommandArgs, use_cases: UseCases) -> CommandOutcome:
    typed = _expect_new_doc_args(args)
    result = use_cases.create_discussion_doc(
        CreateDiscussionDocRequest(
            doc_type=typed.doc_type,  # type: ignore[arg-type]
            scope_node_id=typed.scope_node_id,
            scope_kind=typed.scope_kind,
            title=typed.title,
            slug=typed.slug,
        )
    )
    return CommandOutcome(exit_code=0, text=render_new_doc_text(result))


def _prepend_stderr(text: CliText, line: str) -> CliText:
    return CliText(
        stdout_lines=list(text.stdout_lines),
        stderr_lines=[line, *list(text.stderr_lines)],
        warnings=list(text.warnings),
    )


def _post_sync_exit_code(result: CreateNodeResult) -> int:
    return 1 if result.post_sync is not None and result.post_sync.failed else 0


def _expect_new_initiative_args(args: CommandArgs) -> NewInitiativeArgs:
    if not isinstance(args, NewInitiativeArgs):
        raise RuntimeError("Invalid command args for new initiative")
    return args


def _expect_new_epic_args(args: CommandArgs) -> NewEpicArgs:
    if not isinstance(args, NewEpicArgs):
        raise RuntimeError("Invalid command args for new epic")
    return args


def _expect_new_issue_args(args: CommandArgs) -> NewIssueArgs:
    if not isinstance(args, NewIssueArgs):
        raise RuntimeError("Invalid command args for new issue")
    return args


def _expect_new_doc_args(args: CommandArgs) -> NewDocArgs:
    if not isinstance(args, NewDocArgs):
        raise RuntimeError("Invalid command args for new doc")
    return args
