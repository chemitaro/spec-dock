"""Builders for dashboard model tests: structure snapshots and pull requests (iss-00528)."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from spec_dock.runtime.domain.canonical_structure import ExternalIssue, ScopeNode, StructureAnomaly, StructureSnapshot
from spec_dock.runtime.domain.dashboard_snapshot import PullRequest, PullRequestInfo

NOW = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
FETCHED = "2026-11-04T11:50:00Z"
_PREFIX = {"initiative": "init", "epic": "epic", "issue": "iss"}


def node(number: int, kind: str, *, parent: int | None = None, **changes: object) -> ScopeNode:
    base = ScopeNode(
        number=number,
        database_id=1000 + number,
        id=f"{_PREFIX[kind]}-{number:05d}",
        kind=kind,  # type: ignore[arg-type]
        title=f"Scope {number}",
        state="open",
        state_reason=None,
        labels=(f"spec-dock:{kind}",),
        assignees=(),
        in_progress=False,
        parent=parent,
        sub_issues=(),
        blocked_by=(),
        blocking=(),
        updated_at="2026-10-26T00:00:00Z",
        url=f"https://github.com/o/r/issues/{number}",
        created_at="2026-10-25T00:00:00Z",
        closed_at=None,
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def closed(
    number: int, kind: str, *, parent: int | None = None, reason: str = "completed", **changes: object
) -> ScopeNode:
    return node(
        number,
        kind,
        parent=parent,
        state="closed",
        state_reason=reason,
        closed_at=changes.pop("closed_at", "2026-10-30T00:00:00Z"),
        **changes,
    )


def snapshot(
    *nodes: ScopeNode,
    external: tuple[ExternalIssue, ...] = (),
    anomalies: tuple[StructureAnomaly, ...] = (),
    fetched_at: str = FETCHED,
) -> StructureSnapshot:
    return StructureSnapshot(
        "github.com/o/r",
        fetched_at,
        fetched_at,
        {item.number: item for item in nodes},
        {item.number: item for item in external},
        anomalies,
        (),
    )


def pr(
    number: int,
    branch: str,
    *,
    state: str = "open",
    draft: bool = False,
    checks: str = "success",
    mergeable: str = "mergeable",
    created_at: str = "2026-11-01T00:00:00Z",
    merged_at: str | None = None,
) -> PullRequest:
    return PullRequest(
        number=number,
        state=state,  # type: ignore[arg-type]
        is_draft=draft,
        head_ref_name=branch,
        mergeable=mergeable,  # type: ignore[arg-type]
        checks=checks,  # type: ignore[arg-type]
        created_at=created_at,
        merged_at=merged_at,
        closed_at=merged_at if state != "open" else None,
        url=f"https://github.com/o/r/pull/{number}",
    )


def prs(*items: PullRequest, fetched_at: str | None = FETCHED, error: object = None) -> PullRequestInfo:
    return PullRequestInfo(2, fetched_at, error, {item.number: item for item in items})  # type: ignore[arg-type]
