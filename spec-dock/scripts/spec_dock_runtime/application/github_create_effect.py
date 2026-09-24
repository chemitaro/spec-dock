"""Durable remote Issue effect used by vNext GitHub Scope creation."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Protocol

from spec_dock_runtime.application.operation_executor import (
    can_send_effect,
    record_effect_intent,
    record_effect_result,
)
from spec_dock_runtime.infra.github_lifecycle import RemoteIssueError

if TYPE_CHECKING:
    from pathlib import Path

    from spec_dock_runtime.domain.operation import OperationRecord
    from spec_dock_runtime.infra.contracts import GithubIssueRecord
    from spec_dock_runtime.infra.operation_journal import JournalStore


class GithubCreateGateway(Protocol):
    def create(self, repo_root: Path, repository: str, *, title: str, body: str) -> GithubIssueRecord: ...


def create_github_issue_effect(
    *,
    operation: OperationRecord,
    journal: JournalStore,
    gateway: GithubCreateGateway,
    repo_root: Path,
    repository: str,
    title: str,
    body: str,
) -> tuple[OperationRecord, GithubIssueRecord]:
    """Record intent before POST, then persist a verified ref before local writes."""
    if operation.command != "scope.create" or operation.effect_plan[:1] != ("github-create",):
        raise ValueError("operation is not a GitHub Scope create")
    if (
        dict(operation.fixed_targets).get("repository") != repository
        or dict(operation.fixed_targets).get("title") != title
    ):
        raise ValueError("GitHub create request differs from its fixed operation")
    if not title.strip() or not repository or not body:
        raise ValueError("GitHub create request is incomplete")
    if not can_send_effect(operation, "github-create"):
        raise ValueError("GitHub create effect was already sent")
    intent = record_effect_intent(operation, effect_id="github-create", kind="remote", target=repository)
    journal.update(intent, expected_sequence=operation.sequence)
    try:
        created = gateway.create(repo_root, repository, title=title, body=body)
        if created.repository.lower() != repository.lower() or created.state != "open" or created.number <= 0:
            raise RemoteIssueError("GITHUB_CREATE_IDENTITY_UNKNOWN", uncertain=True)
    except RemoteIssueError as error:
        failed = record_effect_result(
            intent, effect_id="github-create", status="unknown" if error.uncertain else "failed"
        )
        journal.update(failed, expected_sequence=intent.sequence)
        if not error.uncertain:
            terminal = replace(failed, phase="complete", terminal_status="failed", sequence=failed.sequence + 1)
            journal.update(terminal, expected_sequence=failed.sequence)
        raise
    except Exception as error:
        unknown = record_effect_result(intent, effect_id="github-create", status="unknown")
        journal.update(unknown, expected_sequence=intent.sequence)
        raise RemoteIssueError("GITHUB_EFFECT_UNKNOWN", uncertain=True) from error
    advanced = record_effect_result(
        intent,
        effect_id="github-create",
        status="succeeded",
        remote_ref=f"gh:{created.repository.lower()}#{created.number}",
    )
    journal.update(advanced, expected_sequence=intent.sequence)
    return advanced, created
