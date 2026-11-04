"""The writing `todo` commands: add, update, done, snooze, cancel, reopen (epic-00547 D-04, D-06, D-07; iss-00549 D-04).

Each command checks its input, then under the catalog lock re-reads the one record it changes, builds the new
record, checks it with `validate` and writes only that file (one changeset). Any stop before the write leaves
nothing written. Nothing contacts GitHub.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application import todo_common
from spec_dock.runtime.application.canonical_catalog import catalog_changes
from spec_dock.runtime.application.canonical_writes import CATALOG_LOCK_TIMEOUT
from spec_dock.runtime.application.todo_common import open_repository, todo_handler
from spec_dock.runtime.application.todo_list import classify, load_record, normalize_scope
from spec_dock.runtime.domain.todo_model import count_limits, format_time, parse_when, relative
from spec_dock.runtime.domain.todo_record import (
    SUBTASK_ID_PATTERN,
    TodoError,
    new_id,
    new_record,
    normalize_id,
    parent_id,
    transition,
)
from spec_dock.runtime.infra.file_publication import FilePublicationIncomplete
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import (
    Diagnostic,
    Effect,
    OperationResult,
    RecoveryInstructions,
)
from spec_dock.runtime.presentation.todo_document import todo_view

if TYPE_CHECKING:
    import argparse
    from collections.abc import Callable, Sequence
    from datetime import datetime

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.todo_common import TodoRepository
    from spec_dock.runtime.infra.file_publication import FileSnapshot
    from spec_dock.runtime.presentation.envelope import EffectStatus

TODO_WRITE_INCOMPLETE: Final = "TODO_WRITE_INCOMPLETE"
LIMIT_NEXT_STEP: Final = (
    "Close tasks that are answered (spec-dock todo list), or raise the limit in the user or repository settings."
)


def _invalid(field: str, message: str) -> TodoError:
    return TodoError(
        "TODO_INVALID",
        f"{field} {message}",
        exit_code=2,
        details={"problems": [{"field": field, "message": message}], "missing": []},
    )


def _now() -> tuple[datetime, str]:
    now = todo_common.utc_now()
    return now, format_time(now)


def _when(value: str | None, now: datetime, field: str) -> str | None:
    return None if value is None else parse_when(value, now=now, tz=None, field=field)


def _body(namespace: argparse.Namespace) -> str | None:
    body = getattr(namespace, "body", None)
    body_file = getattr(namespace, "body_file", None)
    if body is not None and body_file is not None:
        raise _invalid("body", "give either --body or --body-file, not both")
    if body_file is None:
        return body
    try:
        return Path(body_file).expanduser().read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise _invalid("body", f"--body-file cannot be read: {error}") from error


def _options(values: Sequence[str] | None) -> list[dict[str, object]] | None:
    if values is None:
        return None
    options: list[dict[str, object]] = []
    for value in values:
        key, separator, text = value.partition("=")
        if not separator:
            raise _invalid("options", f"{value!r} must be KEY=TEXT")
        options.append({"key": key.strip(), "text": text})
    return options


def _recommendation(namespace: argparse.Namespace) -> dict[str, object] | None:
    key = getattr(namespace, "recommend", None)
    reason = getattr(namespace, "reason", None)
    if key is None and reason is None:
        return None
    if key is None or reason is None:
        raise _invalid("recommendation", "--recommend KEY and --reason TEXT go together")
    return {"key": key, "reason": reason}


def _scopes(values: Sequence[str] | None) -> list[str]:
    return list(dict.fromkeys(normalize_scope(value) for value in values or ()))


def _actor(namespace: argparse.Namespace) -> tuple[str, str | None]:
    return namespace.by or "human", namespace.role


def _scope_warnings(repository: TodoRepository, scope_ids: Sequence[str]) -> list[Diagnostic]:
    if not scope_ids:
        return []
    snapshot = repository.snapshot()
    unknown = [item for item in scope_ids if snapshot is None or snapshot.find(item) is None]
    if not unknown:
        return []
    reason = "snapshot_missing" if snapshot is None else "not_in_snapshot"
    return [
        Diagnostic(
            "TODO_SCOPE_UNKNOWN",
            f"{', '.join(unknown)} is not in the saved structure snapshot; the task was written as given",
            {"scopes": unknown, "reason": reason, "next_step": "spec-dock scope show <ID> to check the Scope"},
        )
    ]


def _limit_warnings(repository: TodoRepository, todo_id: str) -> list[Diagnostic]:
    records = [item.record for item in classify(repository.store, repository.store.read_all()).valid]
    counts = count_limits(records)
    settings = repository.settings
    warnings = []
    for kind, count, key in (
        ("repository", counts.agent_parents, "parent_limit"),
        ("subtasks", counts.open_subtasks.get(todo_id, 0), "subtask_limit"),
    ):
        limit = settings.value(key)
        if isinstance(limit, int) and count > limit:
            warnings.append(
                Diagnostic(
                    "TODO_LIMIT_EXCEEDED",
                    f"{count} open {'agent tasks in this repository' if kind == 'repository' else 'subtasks of ' + todo_id}"
                    f" exceed the guide of {limit}; the task was written",
                    {
                        "kind": kind,
                        "count": count,
                        "limit": limit,
                        "source": settings.source(key),
                        "next_step": LIMIT_NEXT_STEP,
                    },
                )
            )
    return warnings


def _write(
    namespace: argparse.Namespace,
    repository: TodoRepository,
    build: Callable[[], tuple[Path, dict[str, object], FileSnapshot | None, bool]],
    *,
    extra_warnings: Callable[[str], list[Diagnostic]] = lambda _todo_id: [],
) -> OperationResult[object]:
    """Build and write one record under the catalog lock; `build` returns (path, record, expected, changed)."""
    store = repository.store
    command = namespace.command_path
    shown: str | None = None
    try:
        with catalog_changes(
            repository.catalog, command=command, origin="command", timeout=CATALOG_LOCK_TIMEOUT
        ) as changes:
            path, record, expected, changed = build()
            shown = store.relative(path)
            if changed and not namespace.dry_run:
                try:
                    if expected is None:
                        store.write_new(path, record)
                    else:
                        store.write_replace(path, record, expected)
                except FilePublicationIncomplete as error:
                    if error.confirmed:
                        changes.add(shown)
                    raise
                changes.add(shown)
    except FilePublicationIncomplete as error:
        status: EffectStatus = "succeeded" if error.confirmed else "unknown"
        return OperationResult(
            command,
            "partial",
            FamilyData("todo", {"todo": None, "path": shown}),
            6,
            effects=(Effect("todo", status, shown),),
            error=Diagnostic(TODO_WRITE_INCOMPLETE, str(error), {"path": shown}),
            recovery=RecoveryInstructions((f"Inspect {shown} with spec-dock todo check before a new command.",)),
        )
    todo_id = str(record["id"])
    warnings = [*repository.warnings()]
    if changed and not namespace.dry_run:
        warnings += extra_warnings(todo_id)
    view = todo_view(record, now=todo_common.utc_now(), repository=repository.repository, path=shown, warnings=warnings)
    if view["derived"]["parent_closable"]:  # type: ignore[index]
        view["next_step"] = f"spec-dock todo done {todo_id}"
    if namespace.dry_run:
        return OperationResult(
            command,
            "planned",
            FamilyData("todo", view),
            0,
            effects=(Effect("todo", "planned", shown),),
            warnings=tuple(warnings),
        )
    if not changed:
        return OperationResult(
            command,
            "unchanged",
            FamilyData("todo", view),
            0,
            effects=(Effect("todo", "unchanged", shown),),
            warnings=tuple(warnings),
        )
    return OperationResult(
        command,
        "succeeded",
        FamilyData("todo", view),
        0,
        effects=(Effect("todo", "succeeded", shown),),
        warnings=tuple(warnings),
    )


_RECORD_ARGUMENTS: Final = (
    "body",
    "body_file",
    "option",
    "recommend",
    "reason",
    "reply_to",
    "effort",
    "due",
    "scope",
    "blocks",
    "link",
    "tag",
    "item",
    "kind",
)


@todo_handler
def add_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    now, stamp = _now()
    by, role = _actor(namespace)
    if namespace.parent is not None:
        parent = normalize_id(namespace.parent)
        if SUBTASK_ID_PATTERN.fullmatch(parent):
            raise TodoError(
                "TODO_NESTING_TOO_DEEP",
                f"{parent} is a subtask; a subtask cannot have subtasks",
                exit_code=2,
                details={"parent": parent},
                next_step=f"spec-dock todo add --parent {parent_id(parent)} --title ...",
            )
        given = [name for name in _RECORD_ARGUMENTS if getattr(namespace, name, None) not in (None, [], False)]
        if given:
            raise _invalid(
                "subtask",
                "takes only --title; "
                + ", ".join(f"--{name.replace('_', '-')}" for name in given)
                + " belong to a task",
            )

        def build_subtask() -> tuple[Path, dict[str, object], FileSnapshot | None, bool]:
            loaded = load_record(repository.store, parent)
            record = transition(loaded.record, "subtask_add", now=stamp, by=by, role=role, title=namespace.title)
            return loaded.path, record, loaded.snapshot, True

        return _write(
            namespace, repository, build_subtask, extra_warnings=lambda todo_id: _limit_warnings(repository, todo_id)
        )
    kind = namespace.kind
    if namespace.item and kind != "checklist":
        raise _invalid("subtasks", "--item is only for --kind checklist")
    due = _when(namespace.due, now, "due")
    if due is None:
        span = relative(str(repository.settings.value("default_due")))
        assert span is not None  # the settings layer checks the value
        due = format_time(now + span)
    related = _scopes(namespace.scope)
    blocks = _scopes(namespace.blocks)
    body = _body(namespace)

    def build() -> tuple[Path, dict[str, object], FileSnapshot | None, bool]:
        taken = {path.stem for path in repository.store.scan().records}
        todo_id = new_id(taken)
        record = new_record(
            todo_id,
            title=namespace.title,
            by=by,
            role=role,
            kind=kind,
            now=stamp,
            due=due,
            body=body,
            options=_options(namespace.option) or [],
            recommendation=_recommendation(namespace),
            reply_to=namespace.reply_to,
            effort=namespace.effort,
            related=related,
            blocks=blocks,
            links=namespace.link or (),
            tags=namespace.tag or (),
            items=namespace.item or (),
        )
        return repository.store.record_path(todo_id, stamp), record, None, True

    return _write(
        namespace,
        repository,
        build,
        extra_warnings=lambda todo_id: [
            *_scope_warnings(repository, [*related, *blocks]),
            *_limit_warnings(repository, todo_id),
        ],
    )


def _target(todo_id: str) -> str | None:
    return todo_id if SUBTASK_ID_PATTERN.fullmatch(todo_id) else None


def _transition_command(
    namespace: argparse.Namespace,
    context: ProjectContext,
    action: str,
    options: Callable[[datetime], dict[str, object]],
    *,
    limits: bool = False,
) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    now, stamp = _now()
    by, role = _actor(namespace)
    todo_id = normalize_id(namespace.id)
    values = options(now)

    def build() -> tuple[Path, dict[str, object], FileSnapshot | None, bool]:
        loaded = load_record(repository.store, todo_id)
        record = transition(loaded.record, action, now=stamp, by=by, role=role, target=_target(todo_id), **values)  # type: ignore[arg-type]
        return loaded.path, record, loaded.snapshot, record != loaded.record

    return _write(
        namespace,
        repository,
        build,
        extra_warnings=(lambda parent: _limit_warnings(repository, parent)) if limits else (lambda _parent: []),
    )


@todo_handler
def done_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return _transition_command(
        namespace,
        context,
        "done",
        lambda _now: {
            "choice": namespace.choice,
            "note": namespace.note,
            "record_ref": namespace.record,
            "include_subtasks": namespace.include_subtasks,
        },
    )


@todo_handler
def cancel_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    return _transition_command(
        namespace,
        context,
        "cancel",
        lambda _now: {"note": namespace.reason, "include_subtasks": namespace.include_subtasks},
    )


@todo_handler
def snooze_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if _target(normalize_id(namespace.id)) is not None:
        raise _invalid("id", "a subtask is not snoozed; snooze its task")
    return _transition_command(
        namespace,
        context,
        "snooze",
        lambda now: {
            "until": _when(namespace.until, now, "snooze_until"),
            "due": _when(namespace.due, now, "due"),
            "note": namespace.note,
        },
    )


@todo_handler
def reopen_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    if _target(normalize_id(namespace.id)) is not None and namespace.due is not None:
        raise _invalid("due", "a subtask has no due time of its own")
    return _transition_command(
        namespace,
        context,
        "reopen",
        lambda now: {"due": _when(namespace.due, now, "due"), "note": namespace.note},
        limits=True,
    )


_UPDATE_TASK_ONLY: Final = (
    "body",
    "body_file",
    "kind",
    "due",
    "reply_to",
    "effort",
    "option",
    "recommend",
    "reason",
    "add_scope",
    "remove_scope",
    "add_blocks",
    "remove_blocks",
    "add_tag",
    "remove_tag",
    "add_link",
    "remove_link",
)


def _edited(current: Sequence[object], add: Sequence[str] | None, remove: Sequence[str] | None) -> list[object]:
    result = [item for item in current if item not in (remove or ())]
    for item in add or ():
        if item not in result:
            result.append(item)
    return result


@todo_handler
def update_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    now, stamp = _now()
    by, role = _actor(namespace)
    todo_id = normalize_id(namespace.id)
    target = _target(todo_id)
    if target is not None:
        given = [name for name in _UPDATE_TASK_ONLY if getattr(namespace, name, None) not in (None, [])]
        if given:
            raise _invalid("subtask", "takes only --title and --note")
    due = _when(namespace.due, now, "due")
    body = _body(namespace)
    options = _options(namespace.option)
    recommendation = _recommendation(namespace)
    scope_changes = {
        name: _scopes(getattr(namespace, name)) for name in ("add_scope", "remove_scope", "add_blocks", "remove_blocks")
    }

    def build() -> tuple[Path, dict[str, object], FileSnapshot | None, bool]:
        loaded = load_record(repository.store, todo_id)
        current = loaded.record
        if target is not None:
            record = transition(
                current,
                "update",
                now=stamp,
                by=by,
                role=role,
                target=target,
                title=namespace.title,
                note=namespace.note,
            )
            return loaded.path, record, loaded.snapshot, record != current
        changes: dict[str, object] = {}
        for name, value in (
            ("title", namespace.title),
            ("body", body),
            ("kind", namespace.kind),
            ("due", due),
            ("reply_to", namespace.reply_to),
            ("effort", namespace.effort),
            ("options", options),
            ("recommendation", recommendation),
        ):
            if value is not None:
                changes[name] = value
        found = current.get("scopes")
        scopes: dict[str, list[object]] = found if isinstance(found, dict) else {}
        edited_scopes = {
            "related": _edited(scopes.get("related", []), scope_changes["add_scope"], scope_changes["remove_scope"]),
            "blocks": _edited(scopes.get("blocks", []), scope_changes["add_blocks"], scope_changes["remove_blocks"]),
        }
        changes["scopes"] = {**scopes, **edited_scopes}  # type: ignore[dict-item]
        for name, add, remove in (("tags", "add_tag", "remove_tag"), ("links", "add_link", "remove_link")):
            existing = current.get(name) if isinstance(current.get(name), list) else []
            changes[name] = _edited(existing, getattr(namespace, add), getattr(namespace, remove))  # type: ignore[arg-type]
        record = transition(current, "update", now=stamp, by=by, role=role, changes=changes, note=namespace.note)
        return loaded.path, record, loaded.snapshot, record != current

    added_scopes = [*scope_changes["add_scope"], *scope_changes["add_blocks"]]
    return _write(
        namespace, repository, build, extra_warnings=lambda _todo_id: _scope_warnings(repository, added_scopes)
    )
