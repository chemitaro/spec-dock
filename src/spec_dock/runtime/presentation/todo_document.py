"""The JSON contracts and text of `spec-dock todo` (epic-00547 D-13; iss-00549 D-07).

- One task (add, show, update, done, snooze, cancel, reopen): `{todo, derived, ref, repository, path, warnings_detail}`.
- `todo list`: `specdock.todo-list/v1`. This version writes `mode: repository`; the all-repositories mode is iss-00550.
Fields may be added without a new version; removing one or changing its meaning needs a new version.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from spec_dock.runtime.domain.todo_model import derived, format_time, parse_time

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from datetime import datetime

    from spec_dock.runtime.infra.github_structure import GithubRepository
    from spec_dock.runtime.presentation.envelope import Diagnostic

LIST_SCHEMA: Final = "specdock.todo-list/v1"


def todo_ref(repository: GithubRepository | None, todo_id: str) -> str | None:
    """`<owner>/<name>/t-xxxx`, with the host first when it is not github.com; None for an unknown repository."""
    if repository is None:
        return None
    prefix = repository.slug if repository.host == "github.com" else repository.key
    return f"{prefix}/{todo_id}"


def warning_details(warnings: Iterable[Diagnostic]) -> list[dict[str, object]]:
    return [{"code": item.code, "message": item.message, "details": item.details} for item in warnings]


def todo_view(
    record: Mapping[str, object],
    *,
    now: datetime,
    repository: GithubRepository | None,
    path: str,
    warnings: Sequence[Diagnostic] = (),
) -> dict[str, object]:
    return {
        "todo": dict(record),
        "derived": derived(record, now),
        "ref": todo_ref(repository, str(record.get("id"))),
        "repository": repository.key if repository is not None else None,
        "path": path,
        "warnings_detail": warning_details(warnings),
    }


def list_item(
    record: Mapping[str, object], *, now: datetime, repository: GithubRepository | None, path: str
) -> dict[str, object]:
    return {
        "ref": todo_ref(repository, str(record.get("id"))),
        "repository": repository.key if repository is not None else None,
        "path": path,
        "derived": derived(record, now),
        "todo": dict(record),
    }


def repository_row(
    *,
    repository: str | None,
    catalog: str,
    main_checkout: str,
    hidden: bool,
    status: str,
    problem: Mapping[str, object] | None,
    counts: Mapping[str, object] | None = None,
    invalid_files: Sequence[str] = (),
    conflict_copies: Sequence[str] = (),
) -> dict[str, object]:
    """One `repositories[]` row; `unreadable` and `duplicate` rows have no counts (iss-00550 D-03)."""
    return {
        "repository": repository,
        "catalog": catalog,
        "main_checkout": main_checkout,
        "hidden": hidden,
        "status": status,
        "problem": dict(problem) if problem is not None else None,
        "counts": dict(counts) if counts is not None else None,
        "invalid_files": list(invalid_files),
        "conflict_copies": list(conflict_copies),
    }


def todo_list_document(
    *,
    now: datetime,
    filters: Mapping[str, object],
    repositories: Sequence[Mapping[str, object]],
    items: Sequence[Mapping[str, object]],
    mode: str = "repository",
) -> dict[str, object]:
    return {
        "schema": LIST_SCHEMA,
        "generated_at": format_time(now),
        "mode": mode,
        "filters": dict(filters),
        "repositories": [dict(row) for row in repositories],
        "items": [dict(item) for item in items],
    }


def _local(value: object) -> str:
    try:
        return parse_time(str(value)).astimezone().strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(value)


def _marks(view: Mapping[str, object], record: Mapping[str, object]) -> str:
    status = record.get("status")
    if status == "done":
        return "済"
    if status == "cancelled":
        return "取消"
    marks = []
    if view.get("overdue"):
        marks.append("!期限切れ")
    elif view.get("due_soon"):
        marks.append("期限間近")
    if view.get("blocking"):
        marks.append("止める")
    if view.get("effective_status") == "snoozed":
        marks.append("延期中")
    return " ".join(marks) or "-"


def _line(view: Mapping[str, object], record: Mapping[str, object], ref: object = None) -> str:
    name = ref or record.get("id")
    return f"{name}  {_marks(view, record)}  {_local(record.get('due'))}  {record.get('title')}"


def _rows(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def todo_text(command: str, result: Mapping[str, object]) -> list[str]:
    """Short lines for people; JSON carries everything."""
    if command == "todo list":
        lines = []
        across = result.get("mode") == "all_repositories"
        for row in _rows(result.get("repositories")):
            name = row.get("repository") or row.get("catalog")
            problem = _object(row.get("problem"))
            if row.get("status") == "unreadable":
                lines.append(f"{name}: unreadable [{problem.get('code')}] {problem.get('message')}")
                continue
            if row.get("status") == "duplicate":
                lines.append(f"{name}: duplicate {row.get('catalog')} ({problem.get('message')})")
                continue
            counts = _object(row.get("counts"))
            lines.append(
                f"{name}: open={counts.get('open')} "
                f"overdue={counts.get('overdue')} blocking={counts.get('blocking')} snoozed={counts.get('snoozed')}"
            )
        items = _rows(result.get("items"))
        lines.extend(
            _line(_object(item.get("derived")), _object(item.get("todo")), item.get("ref") if across else None)
            for item in items
        )
        if not items:
            lines.append("(no tasks)")
        return lines
    if command == "todo check":
        errors = _rows(result.get("errors"))
        lines = [
            f"valid={str(result.get('valid')).lower()} files={result.get('checked_files')} "
            f"errors={len(errors)} cue={_object(result.get('cue')).get('status')}"
        ]
        for item in errors:
            field = f" field={item['field']}" if item.get("field") else ""
            lines.append(f"error [{item['code']}] file={item['file']}{field} ({item['source']}) {item['message']}")
        return lines
    if command == "todo settings":
        values = _object(result.get("values"))
        lines = [
            f"{key}={_object(entry).get('value')} source={_object(entry).get('source')}"
            for key, entry in values.items()
        ]
        for layer in _rows(result.get("layers")):
            reason = f" reason={layer['reason']}" if layer.get("reason") else ""
            lines.append(f"layer {layer['layer']} state={layer['state']} path={layer['path']}{reason}")
        return lines
    record = _object(result.get("todo"))
    view = _object(result.get("derived"))
    if not record or not view:
        return []
    lines = [_line(view, record)]
    lines.append(f"kind={record.get('kind')} status={record.get('status')} path={result.get('path')}")
    origin = _object(record.get("origin"))
    if origin.get("by") == "agent":
        lines.append(f"from={origin.get('role')} reply_to={record.get('reply_to')} effort={record.get('effort')}")
    subtasks = _rows(record.get("subtasks"))
    lines.extend(f"  {item.get('id')} [{item.get('status')}] {item.get('title')}" for item in subtasks)
    remaining = _rows(view.get("open_subtasks"))
    if subtasks:
        titles = "、".join(str(item.get("title")) for item in remaining)
        lines.append(f"残り {len(remaining)} 件：{titles}" if remaining else "残り 0 件")
    if view.get("parent_closable"):
        lines.append(f"next: spec-dock todo done {record.get('id')}")
    return lines
