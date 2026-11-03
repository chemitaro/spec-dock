"""The dashboard server's JSON (`specdock.dashboard/v1`; iss-00529 D-06).

The shape of `structure` and `scope` is for the screens (#531, #532 may add fields) and is not a public
contract. Notices carry the reason and the next step for the top band (Epic R-09, D-12).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_structure import parse_timestamp
from spec_dock.runtime.domain.dashboard_model import (
    child_stages,
    compare_seen,
    downstream_ids,
    recent_events,
    root_waits,
    upstream,
    weekly_totals,
)
from spec_dock.runtime.presentation.dashboard_summary import scope_path

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime

    from spec_dock.runtime.application.dashboard_site import RepositoryView
    from spec_dock.runtime.domain.canonical_structure import PullRequest
    from spec_dock.runtime.domain.dashboard_model import (
        ChildStages,
        DashboardModel,
        DependencyPath,
        ScopeChange,
        ScopeModel,
    )
    from spec_dock.runtime.infra.dashboard_store import SeenRecord

API_SCHEMA: Final = "specdock.dashboard/v1"
EVENT_LIMIT: Final = 50


def _notice(code: str, level: str, text: str, *next_steps: str) -> dict[str, object]:
    return {"code": code, "level": level, "text": text, "next_steps": list(next_steps)}


def _age(seconds: int) -> str:
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}分"
    hours = minutes // 60
    return f"{hours}時間" if hours < 48 else f"{hours // 24}日"


def notices(view: RepositoryView, *, now: datetime) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    model = view.model
    if view.status == "missing":
        found.append(
            _notice(
                "SNAPSHOT_MISSING",
                "error",
                "構造のスナップショットがありません。定期の同期が構造を取るまで、画面は空です。",
                "spec-dock canonical link",
                "spec-dock canonical status",
            )
        )
    elif view.status == "unsupported":
        found.append(
            _notice(
                "SNAPSHOT_UNSUPPORTED",
                "error",
                "構造のスナップショットが、この SpecDock の知らない版です。SpecDock を更新してください。",
                "spec-dock --version",
            )
        )
    elif view.status == "unreadable":
        text = (
            "構造のスナップショットが読めません。最後に読めた内容を表示しています。"
            if model is not None
            else "構造のスナップショットが読めません。"
        )
        found.append(
            _notice("SNAPSHOT_UNREADABLE", "error", text, "spec-dock canonical status", "spec-dock canonical sync")
        )
    if model is not None:
        age = int((now - parse_timestamp(model.fetched_at)).total_seconds())
        if model.stale or age > 30 * 60:
            found.append(
                _notice(
                    "SNAPSHOT_STALE",
                    "warning",
                    f"構造が{_age(age)}前から更新されていません（定期の同期を確かめてください）。",
                    "spec-dock canonical status",
                )
            )
        if model.anomalies:
            found.append(
                _notice(
                    "STRUCTURE_ANOMALIES",
                    "warning",
                    f"構造の異常が {len(model.anomalies)}件あります。該当する Scope は「不明」になります。",
                    "spec-dock workspace validate",
                )
            )
        if model.pull_request_status == "unknown":
            found.append(
                _notice("PULL_REQUESTS_UNKNOWN", "info", "PR の状態が分かりません。", "spec-dock canonical status")
            )
        elif model.pull_request_status == "stale":
            found.append(
                _notice("PULL_REQUESTS_STALE", "info", "PR の最後の取得が失敗しました。前回の値を示しています。")
            )
    if view.repository.problem == "ambiguous":
        found.append(
            _notice(
                "REPOSITORY_AMBIGUOUS",
                "warning",
                "同じリポジトリのクローンが2つ登録されているため、資料を開けません。どちらかの登録を外してください。",
                "spec-dock dashboard list",
                "spec-dock canonical remove",
            )
        )
    return found


def _pr(pr: PullRequest | None) -> dict[str, object] | None:
    return None if pr is None else asdict(pr)


def _change(change: ScopeChange | None) -> dict[str, object] | None:
    if change is None:
        return None
    return {"kinds": sorted(change.kinds), "state_before": change.state_before, "pr_before": change.pr_before}


def ranks(model: DashboardModel) -> dict[str, int]:
    """Each Scope's place in the recommended order (Epic R-31); the screens sort by it (iss-00531 D-01)."""
    return {scope_id: index for index, scope_id in enumerate(model.ordered(model.scopes))}


def scope_item(
    model: DashboardModel, scope: ScopeModel, change: ScopeChange | None, rank: int | None = None
) -> dict[str, object]:
    node = model.snapshot.find(scope.id)
    return {
        "id": scope.id,
        "number": scope.number,
        "kind": scope.kind,
        "title": scope.title,
        "parent_id": scope.parent_id,
        "children": list(scope.children),
        "state": scope.state,
        "reason": {"code": scope.reason.code, "text": scope.reason.text, "numbers": list(scope.reason.numbers)},
        "lane": scope.lane,
        "merge": scope.merge,
        "downstream": scope.downstream,
        "waits": scope.waits,
        "keep_visible": scope.keep_visible,
        "created_at": scope.created_at,
        "closed_at": scope.closed_at,
        "url": scope.url,
        "path": scope_path(model.repository, scope.id),
        "pr": _pr(scope.pr),
        "change": _change(change),
        "rank": rank,
        "in_progress": bool(node.in_progress) if node is not None else False,
    }


def _snapshot_block(view: RepositoryView, *, now: datetime) -> dict[str, object]:
    model = view.model
    return {
        "status": view.status,
        "fetched_at": model.fetched_at if model else None,
        "age_seconds": int((now - parse_timestamp(model.fetched_at)).total_seconds()) if model else None,
        "stale": model.stale if model else None,
        "detail": view.detail,
    }


def structure_document(
    view: RepositoryView,
    *,
    now: datetime,
    baseline: SeenRecord | None,
    latest: SeenRecord | None,
) -> dict[str, object]:
    model = view.model
    changes: Mapping[str, ScopeChange] = (
        compare_seen(model, baseline.scopes) if model is not None and baseline is not None else {}
    )
    document: dict[str, object] = {
        "schema": API_SCHEMA,
        "repository": view.repository.key,
        "revision": view.revision,
        "snapshot": _snapshot_block(view, now=now),
        "notices": notices(view, now=now),
        "seen": {
            "latest_id": latest.seen_id if latest else None,
            "baseline_id": baseline.seen_id if baseline else None,
        },
        "changes_count": len(changes),
    }
    if model is None:
        document.update({
            "pull_requests": None,
            "anomalies": [],
            "scopes": [],
            "cleanup": [],
            "timeline": {"weeks": [], "events": []},
        })
        return document
    error = model.pull_requests.error
    scopes = sorted(model.scopes.values(), key=lambda item: item.number)
    order = ranks(model)
    document.update({
        "pull_requests": {
            "status": model.pull_request_status,
            "fetched_at": model.pull_requests.fetched_at,
            "error": None if error is None else {"code": error.code, "message": error.message, "at": error.at},
        },
        "anomalies": [{"number": a.number, "code": a.code, "message": a.message} for a in model.anomalies],
        "scopes": [scope_item(model, scope, changes.get(scope.id), order[scope.id]) for scope in scopes],
        "cleanup": [{"id": c.scope_id, "code": c.code, "text": c.text} for c in model.cleanup],
        "timeline": {
            "weeks": [asdict(week) for week in weekly_totals(model, now=now)],
            "events": [asdict(event) for event in recent_events(model, limit=EVENT_LIMIT)],
        },
    })
    return document


def _stages(stages: ChildStages) -> dict[str, object]:
    return {
        "stages": [list(stage) for stage in stages.stages],
        "external": [{"child": child, "number": number} for child, number in stages.external],
        "cyclic": list(stages.cyclic),
    }


def _path(item: DependencyPath) -> dict[str, list[str]]:
    return {"direct": list(item.direct), "indirect": list(item.indirect)}


def dependencies(model: DashboardModel, scope_id: str) -> dict[str, object]:
    """The Scope's recorded waits, its own first and then each ancestor's (nearest first), and the Scopes that
    record a wait for it; copied from the snapshot without judging anything (iss-00531 D-02)."""
    snapshot = model.snapshot
    by_number = {scope.number: scope for scope in model.scopes.values()}
    chain: list[str] = []
    current: str | None = scope_id
    while current is not None and current not in chain:
        chain.append(current)
        current = model.scopes[current].parent_id if current in model.scopes else None
    waits: list[dict[str, object]] = []
    seen: set[int] = set()
    for member in chain:
        node = snapshot.find(member)
        for number in node.blocked_by if node is not None else ():
            if number in seen:
                continue
            seen.add(number)
            target = by_number.get(number)
            if target is not None:
                item: dict[str, object] = {
                    "number": number,
                    "scope_id": target.id,
                    "title": target.title,
                    "state": target.state,
                    "open": target.open,
                    "external": False,
                }
            else:
                outside = snapshot.external.get(number)
                is_open = outside is None or outside.state == "open"
                item = {
                    "number": number,
                    "scope_id": None,
                    "title": outside.title if outside is not None else None,
                    "state": "open" if is_open else "done",
                    "open": is_open,
                    "external": True,
                }
            item.update({"declared_by": member, "inherited": member != scope_id})
            waits.append(item)
    own = model.scopes[scope_id].number
    waited_by = [
        scope.id
        for scope in sorted(model.scopes.values(), key=lambda item: item.number)
        if (node := snapshot.find(scope.id)) is not None and own in node.blocked_by
    ]
    return {"waits_for": waits, "waited_by": waited_by}


def scope_document(
    view: RepositoryView,
    scope_id: str,
    *,
    baseline: SeenRecord | None,
    details: Mapping[str, object] | None = None,
) -> dict[str, object] | None:
    model = view.model
    if model is None or scope_id not in model.scopes:
        return None
    changes = compare_seen(model, baseline.scopes) if baseline is not None else {}
    stages = child_stages(model, scope_id)
    open_stages = child_stages(model, scope_id, open_only=True)
    waits = root_waits(model, scope_id)
    return {
        "schema": API_SCHEMA,
        "repository": view.repository.key,
        "revision": view.revision,
        "scope": scope_item(model, model.scopes[scope_id], changes.get(scope_id), ranks(model)[scope_id]),
        "upstream": _path(upstream(model, scope_id)),
        "downstream": _path(downstream_ids(model, scope_id)),
        "root_waits": {"scope_ids": list(waits.scope_ids), "external": list(waits.external)},
        "child_stages": _stages(stages),
        "open_child_stages": _stages(open_stages),
        "dependencies": dependencies(model, scope_id),
        "details": dict(details) if details is not None else None,
    }
