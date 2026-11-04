"""The repository summary contract `specdock.dashboard-summary/v1` (epic-00427 D-05, R-21).

Both `spec-dock dashboard summary` and the dashboard server build it with `summary_document`, so the two agree.
Fields may be added without a new version; removing one or changing its meaning needs a new version.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.dashboard_model import KINDS, STATES

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from spec_dock.runtime.domain.dashboard_model import DashboardModel, ScopeModel

SUMMARY_SCHEMA: Final = "specdock.dashboard-summary/v1"


def scope_path(repository: str, scope_id: str) -> str:
    """The stable detail path of a Scope (R-17); `repository` is host/owner/name."""
    return f"/r/{repository}/scopes/{scope_id}"


def _item(scope: ScopeModel) -> dict[str, object]:
    return {
        "id": scope.id,
        "number": scope.number,
        "kind": scope.kind,
        "title": scope.title,
        "state": scope.state,
        "reason": scope.reason.text,
    }


def _items(model: DashboardModel, scope_ids: Iterable[str]) -> list[dict[str, object]]:
    return [_item(model.scopes[scope_id]) for scope_id in scope_ids]


def summary_document(
    model: DashboardModel, *, hidden: bool, server: str | None, todos: Mapping[str, object]
) -> dict[str, object]:
    """`todos` is `{status, open, blocking, overdue, problem}` of the repository's human tasks (epic-00547 D-15)."""
    scopes = list(model.scopes.values())
    by_state = {state: sum(1 for scope in scopes if scope.state == state) for state in STATES}
    by_kind = {
        kind: {
            "total": sum(1 for scope in scopes if scope.kind == kind),
            **{state: sum(1 for scope in scopes if scope.kind == kind and scope.state == state) for state in STATES},
        }
        for kind in KINDS
    }
    awaiting = []
    for scope_id in model.lane("awaiting_merge"):
        item = _item(model.scopes[scope_id])
        item["merge"] = model.scopes[scope_id].merge
        awaiting.append(item)
    cleanup = []
    for candidate in model.cleanup:
        item = _item(model.scopes[candidate.scope_id])
        item["reason"] = candidate.text
        item["cleanup"] = candidate.code
        cleanup.append(item)
    error = model.pull_requests.error
    return {
        "schema": SUMMARY_SCHEMA,
        "repository": model.repository,
        "fetched_at": model.fetched_at,
        "stale": model.stale,
        "counts": {"total": len(scopes), "by_state": by_state, "by_kind": by_kind},
        "completion_ratio": by_state["done"] / len(scopes) if scopes else None,
        "awaiting_merge": awaiting,
        "in_progress": _items(model, model.lane("doing")),
        "ready": _items(model, model.lane("ready")),
        "blocked": _items(model, model.lane("blocked")),
        "cleanup": cleanup,
        "anomaly_count": len(model.anomalies),
        "pull_requests": {
            "status": model.pull_request_status,
            "fetched_at": model.pull_requests.fetched_at,
            "error": None if error is None else {"code": error.code, "message": error.message, "at": error.at},
        },
        "paths": {scope.id: scope_path(model.repository, scope.id) for scope in sorted(scopes, key=lambda s: s.number)},
        "hidden": hidden,
        "server": server,
        "todos": dict(todos),
    }


def summary_text(summary: dict[str, object], *, limit: int = 5) -> list[str]:
    """Human lines for the text output: freshness, counts and the head of each list."""
    counts = summary["counts"]
    assert isinstance(counts, dict)
    by_state = counts["by_state"]
    assert isinstance(by_state, dict)
    stale = " (stale: older than 30 minutes)" if summary["stale"] else ""
    lines = [
        f"repository={summary['repository']} fetched_at={summary['fetched_at']}{stale}",
        "counts " + " ".join(f"{state}={by_state[state]}" for state in STATES) + f" total={counts['total']}",
        f"pull_requests={summary['pull_requests']['status']} anomalies={summary['anomaly_count']}",  # type: ignore[index]
    ]
    for key in ("awaiting_merge", "in_progress", "ready", "blocked", "cleanup"):
        items = summary[key]
        assert isinstance(items, list)
        lines.append(f"{key} {len(items)}")
        lines.extend(f"  {item['id']} {item['title']} — {item['reason']}" for item in items[:limit])
    todos = summary.get("todos")
    if isinstance(todos, dict):
        problem = todos.get("problem")
        if todos.get("status") == "ok":
            lines.append(f"todos open={todos['open']} blocking={todos['blocking']} overdue={todos['overdue']}")
        elif isinstance(problem, dict):
            lines.append(f"todos unavailable [{problem.get('code')}] {problem.get('message')}")
    if summary["server"]:
        lines.append(f"server={summary['server']}")
    return lines


def list_text(data: dict[str, object]) -> list[str]:
    lines = [f"server={data['server'] or 'not running'}"]
    for row in data["repositories"]:  # type: ignore[attr-defined]
        name = row["repository"] or "(repository unknown)"
        state = "hidden" if row["hidden"] else "shown" if row["served"] else "not served"
        problem = f" problem={row['problem']}" if row["problem"] else ""
        url = f" {row['url']}" if row["url"] else ""
        lines.append(f"{name} {state}{problem} catalog={row['catalog']}{url}")
    if data.get("marks_unreadable"):
        lines.append("hidden marks unreadable: repositories stay hidden until dashboard/repositories.json is fixed")
    if data.get("registry_error"):
        lines.append(f"registry unreadable: {data['registry_error']}")
    return lines
