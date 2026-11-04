"""`spec-dock todo check`: every file under `todos/`, by the Python check and then `cue vet` (epic-00547 D-05).

`cue vet` reads one JSON document `{<path from the catalog>: <record>}` from standard input and validates it with
`#Records`, so each error names its file in the first label of its field path (iss-00549 D-08). Without `cue`,
the Python check alone decides the result.
"""

from __future__ import annotations

from collections import defaultdict
import json
import re
from typing import TYPE_CHECKING, Final

from spec_dock.runtime.application.todo_common import open_repository, todo_handler
from spec_dock.runtime.domain.todo_record import SCHEMA, validate
from spec_dock.runtime.infra.cue_schemas import todo_schema_path
from spec_dock.runtime.infra.cue_tool import (
    CUE_INSTALL_STEP,
    CUE_NOT_FOUND,
    CUE_VERSION_UNSUPPORTED,
    CueToolError,
    locate_cue,
    parse_cue_errors,
)
from spec_dock.runtime.presentation.command_data import FamilyData
from spec_dock.runtime.presentation.envelope import Diagnostic, OperationResult, RecoveryInstructions

if TYPE_CHECKING:
    import argparse
    from collections.abc import Mapping
    from pathlib import Path

    from spec_dock.runtime.application.project_context import ProjectContext
    from spec_dock.runtime.infra.cue_tool import CueTool

TODO_CHECK_FAILED: Final = "TODO_CHECK_FAILED"
CHECK_NEXT_STEP: Final = "Fix each listed file under spec-dock/initiatives/todos/, then run spec-dock todo check again."
CONFLICT_NEXT_STEP: Final = (
    "Merge the copy's content into the original file, then delete the copy (spec-dock does not merge it)."
)
_LEADING_LABEL = re.compile(r'"((?:[^"\\]|\\.)*)"(?:\.(.*))?')


def cue_failures(
    tool: CueTool, documents: Mapping[str, Mapping[str, object]], *, cwd: Path, timeout: float
) -> tuple[dict[str, list[dict[str, str | None]]], tuple[str, ...]]:
    """`cue vet` of the documents: errors by document name, and error texts that name no document.

    `cue` leaves out "field is required" errors while other errors are reported in the same run, so the
    documents not named yet are checked again until a run passes or names no new document.
    """
    failures: dict[str, list[dict[str, str | None]]] = defaultdict(list)
    unmatched: list[str] = []
    remaining = dict(documents)
    while remaining:
        run = tool.vet(
            todo_schema_path(),
            json.dumps(remaining, ensure_ascii=False),
            expression="#Records",
            cwd=cwd,
            timeout=timeout,
        )
        if run.returncode == 0:
            break
        if run.returncode != 1:
            raise CueToolError(
                "CUE_FAILED", f"cue vet exited with {run.returncode}", exit_code=5, next_step=CUE_INSTALL_STEP
            )
        named: set[str] = set()
        for error in parse_cue_errors(run.stderr, cwd=cwd):
            matched = _LEADING_LABEL.fullmatch(error.path) if error.path is not None else None
            name = json.loads(f'"{matched.group(1)}"') if matched is not None else None
            if matched is None or name not in remaining:
                unmatched.append(error.message if error.path is None else f"{error.path}: {error.message}")
                continue
            named.add(name)
            failures[name].append({"field": matched.group(2), "message": error.message})
        if not named:
            if not unmatched:
                unmatched.append(run.stderr.strip() or "cue vet failed without an error text")
            break
        remaining = {name: value for name, value in remaining.items() if name not in named}
    return dict(failures), tuple(unmatched)


def _error(code: str, file: str, field: str | None, message: str, source: str) -> dict[str, object]:
    return {"code": code, "file": file, "field": field, "message": message, "source": source}


@todo_handler
def check_todos(namespace: argparse.Namespace, context: ProjectContext) -> OperationResult[object]:
    repository = open_repository(context, namespace)
    store = repository.store
    read = store.read_all()
    errors: list[dict[str, object]] = []
    warnings: list[Diagnostic] = list(repository.warnings())
    for path, reason in read.invalid:
        errors.append(_error("TODO_RECORD_INVALID", store.relative(path), None, reason, "python"))
    documents: dict[str, dict[str, object]] = {}
    by_id: dict[str, list[str]] = defaultdict(list)
    for item in read.records:
        relative = store.relative(item.path)
        record = item.record
        by_id[item.path.stem].append(relative)
        if record.get("schema") != SCHEMA:
            errors.append(
                _error(
                    "TODO_SCHEMA_UNSUPPORTED",
                    relative,
                    "schema",
                    f"the record declares {record.get('schema')!r}; this SpecDock reads {SCHEMA}",
                    "python",
                )
            )
            continue
        documents[relative] = record
        for problem in validate(record):
            errors.append(_error("TODO_RECORD_INVALID", relative, problem.field, problem.message, "python"))
        created = record.get("created_at")
        if record.get("id") != item.path.stem or not isinstance(created, str) or created[:7] != item.path.parent.name:
            errors.append(
                _error(
                    "TODO_RECORD_MISPLACED",
                    relative,
                    "id",
                    "the file name must be the record's id and its directory the year-month of created_at",
                    "python",
                )
            )
    for todo_id, paths in sorted(by_id.items()):
        if len(paths) > 1:
            for shown in paths:
                errors.append(
                    _error("TODO_ID_DUPLICATE", shown, "id", f"{todo_id} is also in {', '.join(paths)}", "python")
                )
    for copy in read.scan.conflict_copies:
        warnings.append(conflict_warning(store.relative(copy)))
    for unknown in read.scan.unknown:
        warnings.append(
            Diagnostic(
                "TODO_FILE_UNKNOWN",
                f"{store.relative(unknown)} is not a task record and is not read",
                {"path": store.relative(unknown), "next_step": "Move it out of todos/ if it is not needed there."},
            )
        )
    cue_status, cue_version = _cue_check(namespace, repository.catalog, documents, errors, warnings)
    valid = not errors
    result: dict[str, object] = {
        "valid": valid,
        "checked_files": len(read.records) + len(read.invalid),
        "errors": errors,
        "warnings": [{"code": item.code, "message": item.message, "details": item.details} for item in warnings],
        "cue": {"status": cue_status, "version": cue_version},
    }
    data = FamilyData("todo", result)
    if valid:
        return OperationResult(namespace.command_path, "succeeded", data, 0, warnings=tuple(warnings))
    return OperationResult(
        namespace.command_path,
        "failed",
        data,
        7,
        warnings=tuple(warnings),
        error=Diagnostic(
            TODO_CHECK_FAILED,
            f"{len(errors)} problems in the task records",
            {"errors": len(errors), "next_step": CHECK_NEXT_STEP},
        ),
        recovery=RecoveryInstructions((CHECK_NEXT_STEP,)),
    )


def conflict_warning(relative: str) -> Diagnostic:
    original = re.sub(r"\.conflict-[^/]*?(\.json)?$", r"\1", relative)
    return Diagnostic(
        "TODO_CONFLICT_COPY",
        f"{relative} is a conflict copy of {original}",
        {"path": relative, "original": original, "next_step": CONFLICT_NEXT_STEP},
    )


def _cue_check(
    namespace: argparse.Namespace,
    catalog: Path,
    documents: dict[str, dict[str, object]],
    errors: list[dict[str, object]],
    warnings: list[Diagnostic],
) -> tuple[str, str | None]:
    if not documents:
        return "not_needed", None
    try:
        tool = locate_cue(timeout=namespace.timeout)
    except CueToolError as error:
        if error.code in (CUE_NOT_FOUND, CUE_VERSION_UNSUPPORTED):
            warnings.append(
                Diagnostic(
                    "TODO_CUE_SKIPPED",
                    f"cue vet was skipped ({error.message}); only the Python check decided the result",
                    {"reason": error.code, "next_step": error.next_step},
                )
            )
            return "skipped", None
        warnings.append(_cue_failed(error.message, error.next_step))
        return "failed", None
    try:
        failures, unmatched = cue_failures(tool, documents, cwd=catalog, timeout=namespace.timeout)
    except CueToolError as error:
        warnings.append(_cue_failed(error.message, error.next_step))
        return "failed", tool.version
    for name, items in sorted(failures.items()):
        for item in items:
            errors.append(_error("TODO_CUE_INVALID", name, item["field"], str(item["message"]), "cue"))
    if unmatched:
        warnings.append(_cue_failed("; ".join(unmatched), CHECK_NEXT_STEP))
        return "failed", tool.version
    return "checked", tool.version


def _cue_failed(message: str, next_step: str) -> Diagnostic:
    return Diagnostic(
        "TODO_CUE_FAILED",
        f"cue vet did not give a usable result ({message}); only the Python check decided the result",
        {"next_step": next_step},
    )
