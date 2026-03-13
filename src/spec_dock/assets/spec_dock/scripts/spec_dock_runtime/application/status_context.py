from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import IssueSnapshot, IssueStatusSnapshot, SpecGraph
from ..domain.status import resolve_issue_statuses


@dataclass(frozen=True)
class IssueStatusContext:
    issue_statuses: dict[str, IssueStatusSnapshot]
    warnings: list[str]


def resolve_issue_status_context(
    graph: SpecGraph,
    *,
    github_enabled: bool,
    issue_snapshots: list[IssueSnapshot] | None,
    cached_issue_status_by_id: dict[str, str],
) -> IssueStatusContext:
    warnings: list[str] = []
    issue_statuses = resolve_issue_statuses(
        graph,
        github_enabled=github_enabled,
        issue_snapshots=issue_snapshots,
        cached_issue_status_by_id=cached_issue_status_by_id,
    )
    return IssueStatusContext(issue_statuses=issue_statuses, warnings=warnings)
