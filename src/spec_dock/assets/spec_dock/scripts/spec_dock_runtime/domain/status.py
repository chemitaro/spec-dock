from __future__ import annotations

from .ids import deps_node_sort_key
from .models import IssueSnapshot, IssueStatusSnapshot, ProgressMap, SpecGraph

_KNOWN_ISSUE_STATUSES = {"done", "open", "unknown"}


def _normalize_issue_status(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in _KNOWN_ISSUE_STATUSES:
        return normalized
    return "unknown"


def _status_from_github_state(state: str) -> str:
    return "done" if str(state).strip().upper() == "CLOSED" else "open"


def resolve_issue_statuses(
    graph: SpecGraph,
    github_enabled: bool,
    issue_snapshots: list[IssueSnapshot] | None,
    cached_issue_status_by_id: dict[str, str],
) -> dict[str, IssueStatusSnapshot]:
    issue_snapshot_by_number: dict[int, IssueSnapshot] = {}
    for issue_snapshot in issue_snapshots or []:
        issue_snapshot_by_number[int(issue_snapshot.issue_number)] = issue_snapshot

    resolved: dict[str, IssueStatusSnapshot] = {}
    issue_ids = sorted(
        [
            node_id
            for node_id, node in graph.nodes_by_id.items()
            if node.kind == "issue"
        ],
        key=deps_node_sort_key,
    )
    for issue_id in issue_ids:
        issue_node = graph.nodes_by_id[issue_id]

        status = "unknown"
        source = "unknown"

        if github_enabled and issue_node.github_issue_number is not None:
            issue_snapshot = issue_snapshot_by_number.get(int(issue_node.github_issue_number))
            if issue_snapshot is not None:
                status = _status_from_github_state(issue_snapshot.state)
                source = "github"
        elif not github_enabled:
            cached_status = cached_issue_status_by_id.get(issue_node.id)
            if cached_status is not None:
                status = _normalize_issue_status(cached_status)
                source = "cache"

        resolved[issue_id] = IssueStatusSnapshot(
            issue_id=issue_id,
            status=status,
            source=source,
            github_number=issue_node.github_issue_number,
        )

    return resolved


def build_progress_map(
    graph: SpecGraph,
    issue_statuses: dict[str, IssueStatusSnapshot],
) -> ProgressMap:
    by_node_id: dict[str, dict[str, int]] = {}
    for node_id, node in graph.nodes_by_id.items():
        if node.kind in ("initiative", "epic"):
            by_node_id[node_id] = {"total": 0, "done": 0, "open": 0, "unknown": 0}

    counts = {"total": 0, "done": 0, "open": 0, "unknown": 0}
    issue_ids = sorted(
        [
            node_id
            for node_id, node in graph.nodes_by_id.items()
            if node.kind == "issue"
        ],
        key=deps_node_sort_key,
    )
    for issue_id in issue_ids:
        issue_node = graph.nodes_by_id[issue_id]
        resolution = issue_statuses.get(
            issue_id,
            IssueStatusSnapshot(issue_id=issue_id, status="unknown", source="unknown", github_number=None),
        )
        issue_status = _normalize_issue_status(resolution.status)

        counts["total"] += 1
        counts[issue_status] += 1

        for parent_id in filter(None, (issue_node.epic_id, issue_node.initiative_id)):
            parent_progress = by_node_id.get(parent_id)
            if parent_progress is None:
                continue
            parent_progress["total"] += 1
            parent_progress[issue_status] += 1

    return ProgressMap(by_node_id=by_node_id, counts=counts)
