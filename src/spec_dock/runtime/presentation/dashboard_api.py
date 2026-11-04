"""The dashboard server's JSON (`specdock.dashboard/v1`; iss-00529 D-06).

The shape of `structure` and `scope` is for the screens (#531, #532 may add fields) and is not a public
contract. Notices carry the reason and the next step for the top band (Epic R-09, D-12).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.domain.canonical_structure import parse_timestamp
from spec_dock.runtime.domain.dashboard_model import (
    KINDS,
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


def layout_facts(model: DashboardModel) -> dict[str, dict[str, object]]:
    """What the structure graph (#532) lays out by, decided by the model: each Scope's declared prerequisites inside
    the repository and its stage among its siblings (all, and among the open ones)."""
    by_number = {scope.number: scope.id for scope in model.scopes.values()}
    nodes = {node.id: node for node in model.snapshot.scopes if node.id is not None}
    stages: dict[str, dict[str, int | None]] = {scope_id: {"all": None, "open": None} for scope_id in model.scopes}
    parents: set[str | None] = {None, *(scope.parent_id for scope in model.scopes.values() if scope.parent_id)}
    for parent in sorted(parents, key=lambda item: "" if item is None else item):
        for key, open_only in (("all", False), ("open", True)):
            for level, members in enumerate(child_stages(model, parent, open_only=open_only).stages, start=1):
                for member in members:
                    stages[member][key] = level
    facts: dict[str, dict[str, object]] = {}
    for scope_id in model.scopes:
        targets = {by_number[n] for n in nodes[scope_id].blocked_by if n in by_number and by_number[n] != scope_id}
        facts[scope_id] = {
            "blocked_by": sorted(targets, key=lambda item: model.scopes[item].number),
            "stage": stages[scope_id],
        }
    return facts


def _active_at(scope: ScopeModel, updated_at: str | None) -> str:
    """The Scope's last change (iss-00556 D-04): creation, the Issue's last update, completion, and the chosen pull
    request's opening, merge and closing; a missing or unreadable time is not used."""
    pr = scope.pr
    candidates = (
        scope.created_at,
        updated_at,
        scope.closed_at,
        *((pr.created_at, pr.merged_at, pr.closed_at) if pr is not None else ()),
    )
    latest: tuple[datetime, str] | None = None
    for text in candidates:
        if not text:
            continue
        try:
            at = parse_timestamp(text)
        except (TypeError, ValueError):
            continue
        if latest is None or at > latest[0]:
            latest = (at, text)
    return scope.created_at if latest is None else latest[1]


def scope_item(
    model: DashboardModel,
    scope: ScopeModel,
    change: ScopeChange | None,
    rank: int | None = None,
    facts: Mapping[str, Mapping[str, object]] | None = None,
    readings: Mapping[str, Mapping[str, str | None]] | None = None,
) -> dict[str, object]:
    node = model.snapshot.find(scope.id)
    read = (readings or {}).get(scope.id, {})
    placed = (facts or {}).get(scope.id, {})
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
        "active_at": _active_at(scope, node.updated_at if node is not None else None),
        "url": scope.url,
        "path": scope_path(model.repository, scope.id),
        "pr": _pr(scope.pr),
        "change": _change(change),
        "rank": rank,
        "in_progress": bool(node.in_progress) if node is not None else False,
        "blocked_by": list(placed.get("blocked_by", [])),  # type: ignore[call-overload]
        "stage": dict(placed.get("stage", {"all": None, "open": None})),  # type: ignore[call-overload]
        # The CUE assurance level and this PC's worktree branch (iss-00544 D-02); null when unknown.
        "assurance": read.get("assurance"),
        "branch": read.get("branch"),
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
    readings: Mapping[str, Mapping[str, str | None]] | None = None,
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
            "timeline": {"weeks": [], "events": [], "weeks_by_kind": {kind: [] for kind in KINDS}},
        })
        return document
    error = model.pull_requests.error
    scopes = sorted(model.scopes.values(), key=lambda item: item.number)
    order = ranks(model)
    facts = layout_facts(model)
    document.update({
        "pull_requests": {
            "status": model.pull_request_status,
            "fetched_at": model.pull_requests.fetched_at,
            "error": None if error is None else {"code": error.code, "message": error.message, "at": error.at},
        },
        "anomalies": [{"number": a.number, "code": a.code, "message": a.message} for a in model.anomalies],
        "scopes": [
            scope_item(model, scope, changes.get(scope.id), order[scope.id], facts, readings) for scope in scopes
        ],
        "cleanup": [{"id": c.scope_id, "code": c.code, "text": c.text} for c in model.cleanup],
        "timeline": {
            "weeks": [asdict(week) for week in weekly_totals(model, now=now)],
            "events": [asdict(event) for event in recent_events(model, limit=EVENT_LIMIT)],
            "weeks_by_kind": {
                kind: [asdict(week) for week in weekly_totals(model, now=now, kinds=(kind,))] for kind in KINDS
            },
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
    readings: Mapping[str, Mapping[str, str | None]] | None = None,
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
        "scope": scope_item(
            model,
            model.scopes[scope_id],
            changes.get(scope_id),
            ranks(model)[scope_id],
            layout_facts(model),
            readings,
        ),
        "upstream": _path(upstream(model, scope_id)),
        "downstream": _path(downstream_ids(model, scope_id)),
        # The graph highlights what waits for a closed Scope too (iss-00532 D-01); `downstream` stays open-only.
        "downstream_all": _path(downstream_ids(model, scope_id, open_only=False)),
        "root_waits": {"scope_ids": list(waits.scope_ids), "external": list(waits.external)},
        "child_stages": _stages(stages),
        "open_child_stages": _stages(open_stages),
        "dependencies": dependencies(model, scope_id),
        "details": dict(details) if details is not None else None,
    }
