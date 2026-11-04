"""`spec-dock todo list` and `todo show` in a checkout (epic-00547 D-13, D-14 file rules; iss-00549 D-05).

Readers take no lock and write nothing. A broken record or a conflict copy is reported and never stops the
reading of the other records.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import TYPE_CHECKING

from spec_dock.runtime.application import todo_common
from spec_dock.runtime.application.todo_check import conflict_warning
from spec_dock.runtime.application.todo_common import open_repository, todo_handler
from spec_dock.runtime.domain.todo_model import Filters, count_limits, derived, matches, order
from spec_dock.runtime.domain.todo_record import SCHEMA, TodoError, normalize_id, parent_id, validate
from spec_dock.runtime.infra.dashboard_files import read_hidden
from spec_dock.runtime.infra.file_publication import read_regular_file
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult
from spec_dock.runtime.presentation.todo_document import list_item, todo_list_document, todo_view

if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.application.todo_common import TodoRepository
    from spec_dock.runtime.infra.file_publication import FileSnapshot
    from spec_dock.runtime.infra.todo_store import ReadAll, StoredRecord

CHECK_STEP = "spec-dock todo check"


@dataclass(frozen=True)
class Classified:
    valid: tuple[StoredRecord, ...]
    invalid_files: tuple[str, ...]
    conflict_copies: tuple[str, ...]
    warnings: tuple[Diagnostic, ...]


def classify(repository: TodoRepository, read: ReadAll) -> Classified:
    """Valid v1 records, and the files that are not (each reported once, pointing to `todo check`)."""
    store = repository.store
    valid: list[StoredRecord] = []
    invalid: list[str] = [store.relative(path) for path, _reason in read.invalid]
    for item in read.records:
        if item.record.get("schema") == SCHEMA and not validate(item.record):
            valid.append(item)
        else:
            invalid.append(store.relative(item.path))
    warnings = [
        Diagnostic(
            "TODO_RECORD_INVALID",
            f"{path} is not a valid specdock.todo/v1 record and is not listed",
            {"path": path, "next_step": CHECK_STEP},
        )
        for path in sorted(invalid)
    ]
    copies = tuple(store.relative(path) for path in read.scan.conflict_copies)
    warnings += [conflict_warning(path) for path in copies]
    return Classified(tuple(valid), tuple(sorted(invalid)), copies, tuple(warnings))


_SCOPE_INPUT = re.compile(r"(init|epic|iss)-0*([1-9][0-9]*)")


def normalize_scope(value: str) -> str:
    """A Scope ID from input; the number needs no zero padding (`iss-531` is `iss-00531`)."""
    matched = _SCOPE_INPUT.fullmatch(value.strip().lower())
    if matched is None:
        raise TodoError(
            "TODO_INVALID",
            f"{value!r} is not a Scope ID (init-, epic- or iss- and its number)",
            exit_code=2,
            details={"problems": [{"field": "scopes", "message": "must be a Scope ID"}], "missing": []},
        )
    return f"{matched.group(1)}-{int(matched.group(2)):05d}"


@todo_handler
def list_todos(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    now = todo_common.utc_now()
    classified = classify(repository, repository.store.read_all())
    filters = Filters(
        status=namespace.status,
        scope=normalize_scope(namespace.scope) if namespace.scope else None,
        kind=namespace.kind,
        tag=namespace.tag,
        blocking=namespace.blocking,
        overdue=namespace.overdue,
    )
    by_record = {id(item.record): item for item in classified.valid}
    records = [item.record for item in classified.valid]
    shown = [record for record in order(records, now) if matches(record, filters, now)]
    store = repository.store
    items = [
        list_item(record, now=now, repository=repository.repository, path=store.relative(by_record[id(record)].path))
        for record in shown
    ]
    document = todo_list_document(
        now=now,
        filters=filters.to_json(),
        repositories=[repository_row(repository, records, classified, now)],
        items=items,
    )
    warnings = (*repository.warnings(), *classified.warnings)
    return OperationResult(namespace.command_path, "succeeded", FamilyData("todo", document), 0, warnings=warnings)


def repository_row(
    repository: TodoRepository, records: list[dict[str, object]], classified: Classified, now: object
) -> dict[str, object]:
    views = [derived(record, now) for record in records]  # type: ignore[arg-type]
    open_records = [record for record in records if record.get("status") not in ("done", "cancelled")]
    hidden = read_hidden(repository.state_root, repository.repository) if repository.repository is not None else False
    return {
        "repository": repository.repository.key if repository.repository is not None else None,
        "catalog": str(repository.catalog),
        "main_checkout": str(repository.linked.layout.main_checkout),
        "hidden": hidden,
        "status": "ok",
        "problem": None,
        "counts": {
            "open": len(open_records),
            "blocking": sum(1 for view in views if view["blocking"]),
            "overdue": sum(1 for view in views if view["overdue"]),
            "snoozed": sum(1 for view in views if view["effective_status"] == "snoozed"),
            "agent_parents": {
                "count": count_limits(records).agent_parents,
                "limit": repository.settings.value("parent_limit"),
                "source": repository.settings.source("parent_limit"),
            },
        },
        "invalid_files": list(classified.invalid_files),
        "conflict_copies": list(classified.conflict_copies),
    }


@dataclass(frozen=True)
class LoadedRecord:
    path: Path
    snapshot: FileSnapshot
    record: dict[str, object]


def load_record(repository: TodoRepository, todo_id: str) -> LoadedRecord:
    """The valid v1 record of a task or of a subtask's parent; anything else stops before a write."""
    path = repository.store.find(todo_id)
    relative = repository.store.relative(path)
    try:
        snapshot = read_regular_file(path)
        record = json.loads(snapshot.payload.decode("utf-8"))
    except (OSError, ValueError) as error:
        raise _record_invalid(relative, f"cannot be read as JSON: {error}") from error
    if not isinstance(record, dict):
        raise _record_invalid(relative, "is not a JSON object")
    if record.get("schema") != SCHEMA:
        raise TodoError(
            "TODO_SCHEMA_UNSUPPORTED",
            f"{relative} declares {record.get('schema')!r}; this SpecDock reads and writes only {SCHEMA}",
            details={"path": relative, "schema": record.get("schema")},
            next_step="Update SpecDock to a version that reads this record.",
        )
    problems = validate(record)
    if problems:
        raise _record_invalid(relative, "; ".join(f"{item.field} {item.message}" for item in problems))
    return LoadedRecord(path, snapshot, record)


def _record_invalid(relative: str, reason: str) -> TodoError:
    return TodoError(
        "TODO_RECORD_INVALID",
        f"{relative} is not a valid task record: {reason}",
        details={"path": relative, "reason": reason},
        next_step=CHECK_STEP,
    )


def record_conflicts(repository: TodoRepository, todo_id: str) -> tuple[Diagnostic, ...]:
    prefix = f"{parent_id(todo_id)}.conflict-"
    return tuple(
        conflict_warning(repository.store.relative(path))
        for path in repository.store.scan().conflict_copies
        if path.name.startswith(prefix)
    )


@todo_handler
def show_todo(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    todo_id = normalize_id(namespace.id)
    loaded = load_record(repository, todo_id)
    subtasks = loaded.record.get("subtasks")
    if todo_id != parent_id(todo_id) and not any(
        isinstance(item, dict) and item.get("id") == todo_id
        for item in (subtasks if isinstance(subtasks, list) else [])
    ):
        raise TodoError(
            "TODO_NOT_FOUND",
            f"{parent_id(todo_id)} has no subtask {todo_id}",
            details={"id": todo_id},
            next_step=f"spec-dock todo show {parent_id(todo_id)}",
        )
    warnings = (*repository.warnings(), *record_conflicts(repository, todo_id))
    view = todo_view(
        loaded.record,
        now=todo_common.utc_now(),
        repository=repository.repository,
        path=repository.store.relative(loaded.path),
        warnings=warnings,
    )
    if view["derived"]["parent_closable"]:  # type: ignore[index]
        view["next_step"] = f"spec-dock todo done {parent_id(todo_id)}"
    return OperationResult(namespace.command_path, "succeeded", FamilyData("todo", view), 0, warnings=warnings)
