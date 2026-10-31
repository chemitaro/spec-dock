"""One Scope's spec check (iss-00473; contract K3 of epic-00425), shared by `scope check` and `work finish`.

A Scope with requirement.cue is a CUE Scope. Its type version is read from requirement.cue alone, then the type,
the repository's own type files and the Scope's three files are evaluated as one instance (contract K1). Shape
errors, connection findings, the assurance level and the thin explanation shape (contract K5) become Diagnostics
that name the file, the field and the fix. `scope show` reads the assurance level the same way, without the type.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Final, Literal

from spec_dock.runtime.application.canonical_errors import CanonicalCommandError
from spec_dock.runtime.domain.explanation_shape import inspect_explanation
from spec_dock.runtime.infra.cue_schemas import schema_directory, shipped_schemas
from spec_dock.runtime.infra.cue_tool import (
    CUE_FAILED,
    CUE_INSTALL_STEP,
    CUE_NOT_FOUND,
    CUE_TIMEOUT,
    CUE_VERSION_UNSUPPORTED,
    REINSTALL_STEP,
    TIMEOUT_STEP,
    CueToolError,
    locate_cue,
    parse_cue_errors,
)
from spec_dock.runtime.presentation.envelope import Diagnostic

if TYPE_CHECKING:
    from collections.abc import Mapping

    from spec_dock.runtime.infra.cue_tool import CueError, CuePosition, CueRun, CueTool

ScopeFormat = Literal["markdown", "cue", "conflict"]
MARKDOWN_DOCUMENTS: Final = ("requirement.md", "design.md", "plan.md", "report.md")
CUE_DOCUMENTS: Final = ("requirement.cue", "design.cue", "plan.cue", "report.md")
SCOPE_FILES: Final = ("requirement.cue", "design.cue", "plan.cue")
LEVELS: Final = ("light", "standard", "strict", "critical")
REPOSITORY_TYPES: Final = Path("spec-dock/cue")
TYPE_SHOWN: Final = "<spec_dock>/cue"

CUE_INVALID: Final = "CUE_INVALID"
SPEC_FINDINGS: Final = "SPEC_FINDINGS"
ASSURANCE_UNREADABLE: Final = "ASSURANCE_UNREADABLE"
SCOPE_FORMAT_CONFLICT: Final = "SCOPE_FORMAT_CONFLICT"
SCOPE_DOCUMENT_MISSING: Final = "SCOPE_DOCUMENT_MISSING"
EXPLANATION_MISSING: Final = "EXPLANATION_MISSING"
EXPLANATION_SKELETON: Final = "EXPLANATION_SKELETON"
EXPLANATION_INVALID: Final = "EXPLANATION_INVALID"
CUE_SCHEMA_UNSUPPORTED: Final = "CUE_SCHEMA_UNSUPPORTED"

# A tool failure while reading the level stops the check like any other `cue` failure: (exit code, next step).
_TOOL_STEPS: Final = {
    CUE_NOT_FOUND: (3, CUE_INSTALL_STEP),
    CUE_VERSION_UNSUPPORTED: (3, CUE_INSTALL_STEP),
    CUE_TIMEOUT: (5, TIMEOUT_STEP),
    CUE_FAILED: (5, REINSTALL_STEP),
}
_SCHEMA_SHAPE = re.compile(r"specdock/v[1-9][0-9]*")
_SCHEMA_STEP = 'Write schema: "specdock/v1" in requirement.cue (the type version is read from that file only).'
_ASSURANCE_STEP = (
    'Write assurance: {level: "<light|standard|strict|critical>", reason: "<why>"} in requirement.cue; '
    "the assurance level is read from that file only."
)
_CONFLICT_STEP = "Keep one format: remove requirement.md from a CUE Scope, or requirement.cue from a Markdown Scope."


def scope_format(directory: Path) -> ScopeFormat:
    """`cue` when requirement.cue is a regular file, `conflict` when requirement.md is there too."""
    if not (directory / "requirement.cue").is_file():
        return "markdown"
    return "conflict" if (directory / "requirement.md").is_file() else "cue"


@dataclass(frozen=True)
class AssuranceReading:
    level: str | None
    reason: str | None
    source: Literal["cue", "unset", "unreadable"]
    problem: Diagnostic | None = None

    def payload(self) -> dict[str, object]:
        problem = None if self.problem is None else {"code": self.problem.code, "message": self.problem.message}
        return {"level": self.level, "reason": self.reason, "source": self.source, "problem": problem}


_UNSET: Final = AssuranceReading(None, None, "unset")


def _unreadable(code: str, message: str) -> AssuranceReading:
    return AssuranceReading(None, None, "unreadable", Diagnostic(code, message, {}))


def read_assurance(directory: Path | None, *, timeout: float, tool: CueTool | None = None) -> AssuranceReading:
    """The assurance level of requirement.cue alone, without the type; never raises (R-C6)."""
    if directory is None or not directory.is_dir():
        return _UNSET
    found = scope_format(directory)
    if found == "markdown":
        return _UNSET
    if found == "conflict":
        return _unreadable(SCOPE_FORMAT_CONFLICT, "the Scope has both requirement.md and requirement.cue")
    try:
        tool = tool or locate_cue(timeout=timeout)
        run = tool.export(
            [directory.resolve() / "requirement.cue"], cwd=directory.resolve(), timeout=timeout, expression="assurance"
        )
    except CueToolError as error:
        return _unreadable(error.code, error.message)
    if run.returncode != 0:
        errors = parse_cue_errors(run.stderr, cwd=directory.resolve())
        if errors and all(_not_found(error, "assurance") for error in errors):
            return _unreadable(ASSURANCE_UNREADABLE, "requirement.cue has no assurance block")
        first = errors[0].message if errors else run.stderr.strip() or f"cue exited with {run.returncode}"
        return _unreadable(CUE_INVALID, f"requirement.cue cannot be evaluated: {first}")
    try:
        value = json.loads(run.stdout)
    except ValueError:
        return _unreadable(CUE_FAILED, "cue printed output that is not JSON")
    level = value.get("level") if isinstance(value, dict) else None
    reason = value.get("reason") if isinstance(value, dict) else None
    if level not in LEVELS:
        return _unreadable(ASSURANCE_UNREADABLE, f"assurance.level must be one of {', '.join(LEVELS)}")
    if not isinstance(reason, str) or not reason.strip():
        return _unreadable(ASSURANCE_UNREADABLE, "assurance.reason must be text that is not blank")
    return AssuranceReading(level, reason, "cue")


def _not_found(error: CueError, name: str) -> bool:
    return error.message == f'reference "{name}" not found'


@dataclass(frozen=True)
class ScopeCheckReport:
    format: ScopeFormat
    checked: bool
    schema: str | None
    assurance: AssuranceReading
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...]
    findings: dict[str, list[dict[str, str]]] | None
    cue_version: str | None
    cue_output: str | None
    evaluation: dict[str, object] | None = None  # the whole K1 evaluation when it succeeded (for I-5's renderer)


@dataclass(frozen=True)
class _Places:
    """How a file `cue` names is shown: Scope files under `shown`, repository and package types by their place."""

    scope: Path
    shown: str
    repository: Path
    types: Path

    def show(self, file: Path) -> str:
        for base, label in (
            (self.scope, self.shown),
            (self.repository / REPOSITORY_TYPES, REPOSITORY_TYPES.as_posix()),
            (self.types.parent, TYPE_SHOWN),
        ):
            try:
                return f"{label}/{file.relative_to(base).as_posix()}"
            except ValueError:
                continue
        return str(file)

    def rank(self, file: Path) -> int:
        """Prefer a Scope file, then a repository type, as the place an error is reported at."""
        if file.parent == self.scope:
            return 0
        return 1 if file.parent == (self.repository / REPOSITORY_TYPES) else 2


def check_scope_documents(
    directory: Path, *, kind: str, shown: str, repository_root: Path, timeout: float
) -> ScopeCheckReport:
    """Check one Scope directory; a tool failure or a type version this package lacks raises CanonicalCommandError."""
    found = scope_format(directory)
    if found == "markdown":
        return ScopeCheckReport(found, False, None, _UNSET, (), (), None, None, None)
    if found == "conflict":
        conflict = Diagnostic(
            SCOPE_FORMAT_CONFLICT,
            "the Scope has both requirement.md and requirement.cue",
            {"file": shown, "hint": _CONFLICT_STEP},
        )
        reading = _unreadable(SCOPE_FORMAT_CONFLICT, conflict.message)
        return ScopeCheckReport(found, False, None, reading, (conflict,), (), None, None, None)
    tool = _tool(timeout)
    scope = directory.resolve()
    errors: list[Diagnostic] = [
        Diagnostic(
            SCOPE_DOCUMENT_MISSING,
            f"the CUE Scope lacks {name}",
            {"file": f"{shown}/{name}", "hint": f"Create {name} with `package spec` (it may hold only that line)."},
        )
        for name in SCOPE_FILES[1:]
        if not (scope / name).is_file()
    ]
    schema, schema_errors, types, schema_output = _read_schema(tool, scope, shown, repository_root, timeout)
    errors += schema_errors
    findings: dict[str, list[dict[str, str]]] | None = None
    evaluation: dict[str, object] | None = None
    cue_output: str | None = schema_output
    checked = types is not None
    shape_errors: list[Diagnostic] = []
    if types is not None:
        places = _Places(scope, shown, repository_root.resolve(), types.resolve())
        run = _export(tool, k1_files(types, repository_root, scope), cwd=scope, timeout=timeout, tags={"kind": kind})
        if run.returncode != 0:
            cue_output = run.stderr
            shape_errors = _shape_errors(parse_cue_errors(run.stderr, cwd=scope), run.stderr, places)
            errors += shape_errors
        else:
            evaluation = _evaluation(run.stdout)
            findings = _findings(evaluation)
            errors += _finding_errors(findings, shown)
    assurance = read_assurance(directory, timeout=timeout, tool=tool)
    if assurance.problem is not None and assurance.problem.code in _TOOL_STEPS:
        code = assurance.problem.code
        raise _stopped(
            CueToolError(
                code, assurance.problem.message, exit_code=_TOOL_STEPS[code][0], next_step=_TOOL_STEPS[code][1]
            )
        )
    if assurance.problem is not None and _report_assurance(assurance, findings is not None, shape_errors):
        errors.append(
            Diagnostic(
                ASSURANCE_UNREADABLE,
                f"the assurance level cannot be read from requirement.cue alone: {assurance.problem.message}",
                {"file": f"{shown}/requirement.cue", "problem": assurance.problem.message, "hint": _ASSURANCE_STEP},
            )
        )
    explanation_errors, explanation_warnings = _explanation(directory, kind, shown)
    errors += explanation_errors
    return ScopeCheckReport(
        found,
        checked,
        schema,
        assurance,
        tuple(errors),
        explanation_warnings,
        findings,
        tool.version,
        cue_output,
        evaluation,
    )


def k1_files(types: Path, repository_root: Path, scope: Path) -> list[Path]:
    """Contract K1's file order: the shipped type, the repository's types, then the Scope's existing files.

    Every path is resolved, so the positions `cue` prints map back to these files.
    """
    scope = scope.resolve()
    files = [*sorted(types.resolve().glob("*.cue")), *_repository_types(repository_root)]
    return files + [scope / name for name in SCOPE_FILES if (scope / name).is_file()]


def _tool(timeout: float) -> CueTool:
    try:
        return locate_cue(timeout=timeout)
    except CueToolError as error:
        raise _stopped(error) from error


def _stopped(error: CueToolError) -> CanonicalCommandError:
    return CanonicalCommandError(
        error.code,
        error.message,
        exit_code=error.exit_code,
        recovery=(error.next_step,),
        details={"next_step": error.next_step},
    )


def _export(
    tool: CueTool,
    files: list[Path],
    *,
    cwd: Path,
    timeout: float,
    tags: Mapping[str, str] | None = None,
    expression: str | None = None,
) -> CueRun:
    try:
        return tool.export(files, cwd=cwd, timeout=timeout, tags=tags, expression=expression)
    except CueToolError as error:
        raise _stopped(error) from error


def _read_schema(
    tool: CueTool, scope: Path, shown: str, repository_root: Path, timeout: float
) -> tuple[str | None, list[Diagnostic], Path | None, str | None]:
    """The type version from requirement.cue alone.

    Returns (value, errors, type directory or None to skip evaluation, the cue error text when the read failed).
    """
    requirement = scope / "requirement.cue"
    run = _export(tool, [requirement], cwd=scope, timeout=timeout, expression="schema")
    places = _Places(scope, shown, repository_root.resolve(), scope)
    if run.returncode != 0:
        errors = parse_cue_errors(run.stderr, cwd=scope)
        if errors and all(_not_found(error, "schema") for error in errors):
            return None, [_schema_error(shown, "requirement.cue has no schema")], None, run.stderr
        return None, _shape_errors(errors, run.stderr, places), None, run.stderr
    try:
        value = json.loads(run.stdout)
    except ValueError as error:
        raise _stopped(
            CueToolError(CUE_FAILED, "cue printed output that is not JSON", exit_code=5, next_step=REINSTALL_STEP)
        ) from error
    if not isinstance(value, str) or _SCHEMA_SHAPE.fullmatch(value) is None:
        return (
            None,
            [_schema_error(shown, f"schema must be a type version such as specdock/v1, not {value!r}")],
            None,
            None,
        )
    types = schema_directory(value)
    if types is None:
        shipped = list(shipped_schemas())
        step = f"Upgrade SpecDock to a version that ships {value}; this one ships {', '.join(shipped) or 'none'}."
        raise CanonicalCommandError(
            CUE_SCHEMA_UNSUPPORTED,
            f"requirement.cue names {value}, which this SpecDock does not ship",
            recovery=(step,),
            details={"schema": value, "shipped": shipped, "next_step": step},
        )
    return value, [], types, None


def _schema_error(shown: str, message: str) -> Diagnostic:
    return Diagnostic(
        CUE_INVALID,
        message,
        {
            "file": f"{shown}/requirement.cue",
            "line": None,
            "column": None,
            "field": "schema",
            "cue_message": message,
            "positions": [],
            "hint": _SCHEMA_STEP,
        },
    )


def _repository_types(repository_root: Path) -> list[Path]:
    directory = repository_root / REPOSITORY_TYPES
    if not directory.is_dir():
        return []
    return sorted(path.resolve() for path in directory.glob("*.cue") if path.is_file())


def _derived(error: CueError) -> bool:
    """An error the type's own computations repeat from another one (hidden fields, builtin calls, headers)."""
    return bool(
        (error.path is not None and error.path.startswith("_"))
        or "error in call to" in error.message
        or re.fullmatch(r"\d+ errors in empty disjunction", error.message)
    )


def _shape_errors(errors: tuple[CueError, ...], stderr: str, places: _Places) -> list[Diagnostic]:
    if not errors:
        errors = ((_whole(stderr)),)
    primary = [error for error in errors if not _derived(error)] or list(errors)
    seen: set[tuple[str | None, str]] = set()
    found: list[Diagnostic] = []
    for error in primary:
        if (error.path, error.message) in seen:
            continue
        seen.add((error.path, error.message))
        found.append(_shape_error(error, places))
    return found


def _whole(stderr: str) -> CueError:
    from spec_dock.runtime.infra.cue_tool import CueError

    return CueError(None, stderr.strip() or "cue failed without a message", ())


def _shape_error(error: CueError, places: _Places) -> Diagnostic:
    at: CuePosition | None = min(error.positions, key=lambda item: places.rank(item.file), default=None)
    file = places.show(at.file) if at is not None else None
    field = error.path
    if at is not None and places.rank(at.file) == 2:
        # Only the shipped type locates it (a required field is missing, say): the fix is in the Scope's documents.
        hint = (
            f"Write or fix {field or 'the field'} in the Scope's CUE documents ({places.shown}/*.cue) so that it"
            f" meets the spec type; do not edit the SpecDock type at {file} (see cue_message)."
        )
    else:
        where = f"{field} in {file}" if field and file else field or file or "the CUE documents"
        hint = f"Fix {where} to match the spec type; see cue_message and positions."
    message = f"{field}: {error.message}" if field else error.message
    return Diagnostic(
        CUE_INVALID,
        message,
        {
            "file": file,
            "line": at.line if at is not None else None,
            "column": at.column if at is not None else None,
            "field": field,
            "cue_message": error.message,
            "positions": [
                {"file": places.show(item.file), "line": item.line, "column": item.column} for item in error.positions
            ],
            "hint": hint,
        },
    )


def _evaluation(stdout: str) -> dict[str, object]:
    try:
        value = json.loads(stdout)
    except ValueError as error:
        raise _stopped(
            CueToolError(CUE_FAILED, "cue printed output that is not JSON", exit_code=5, next_step=REINSTALL_STEP)
        ) from error
    if not isinstance(value, dict):
        raise _stopped(
            CueToolError(CUE_FAILED, "the evaluation is not a JSON object", exit_code=5, next_step=REINSTALL_STEP)
        )
    return value


def _findings(value: dict[str, object]) -> dict[str, list[dict[str, str]]]:
    findings = value.get("findings")
    if not isinstance(findings, dict) or not all(isinstance(items, list) for items in findings.values()):
        raise _stopped(
            CueToolError(CUE_FAILED, "the evaluation has no findings map", exit_code=5, next_step=REINSTALL_STEP)
        )
    return findings


def _finding_file(shown: str, finding_id: str) -> str | None:
    if re.match(r"^[RF]-\d", finding_id):
        name = "requirement.cue"
    elif re.match(r"^D-\d", finding_id):
        name = "design.cue"
    elif (
        re.match(r"^(?:[ST]-\d|(?:epic|iss)-\d)", finding_id)
        or finding_id == "rollback"
        or finding_id.startswith("execution.")
    ):
        name = "plan.cue"
    else:
        return None
    return f"{shown}/{name}"


def _finding_errors(findings: dict[str, list[dict[str, str]]], shown: str) -> list[Diagnostic]:
    errors: list[Diagnostic] = []
    for rule in sorted(findings):
        for item in findings[rule]:
            finding_id = str(item.get("id", ""))
            errors.append(
                Diagnostic(
                    SPEC_FINDINGS,
                    str(item.get("message", "")),
                    {
                        "rule": rule,
                        "id": finding_id,
                        "file": _finding_file(shown, finding_id),
                        "hint": item.get("hint"),
                    },
                )
            )
    return errors


def _report_assurance(reading: AssuranceReading, evaluated: bool, shape_errors: list[Diagnostic]) -> bool:
    """Name an unreadable level unless the evaluation already reported the same cause."""
    if evaluated:
        return True
    if reading.problem is None or reading.problem.code != ASSURANCE_UNREADABLE:
        return False
    return not any(str(error.details.get("field") or "").split(".")[0] == "assurance" for error in shape_errors)


def _explanation(directory: Path, kind: str, shown: str) -> tuple[list[Diagnostic], tuple[Diagnostic, ...]]:
    """K5's thin explanation shape: missing or skeleton weighs by kind (Epic error), a broken shape is an error."""
    file = f"{shown}/explanation.html"
    path = directory / "explanation.html"
    errors: list[Diagnostic] = []
    soft: list[Diagnostic] = []
    if not path.is_file():
        soft.append(
            Diagnostic(
                EXPLANATION_MISSING,
                "the Scope has no explanation.html",
                {
                    "file": file,
                    "hint": "Copy spec-dock/design-system/explanation-skeleton.html to explanation.html and write it.",
                },
            )
        )
    else:
        try:
            shape = inspect_explanation(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as error:
            errors.append(
                Diagnostic(
                    EXPLANATION_INVALID,
                    f"explanation.html cannot be read: {error}",
                    {"file": file, "problem": str(error), "hint": "Save explanation.html as UTF-8 text."},
                )
            )
        else:
            errors += [
                Diagnostic(
                    EXPLANATION_INVALID,
                    f"explanation.html {problem}",
                    {"file": file, "problem": problem, "hint": "Keep the shape of explanation-skeleton.html."},
                )
                for problem in shape.problems
            ]
            if shape.skeleton:
                soft.append(
                    Diagnostic(
                        EXPLANATION_SKELETON,
                        "explanation.html is still the skeleton",
                        {
                            "file": file,
                            "hint": "Rewrite the explanation, then delete the line "
                            "<!-- spec-dock:explanation-skeleton -->.",
                        },
                    )
                )
    if kind == "epic":
        return [*errors, *soft], ()
    return errors, tuple(soft)
