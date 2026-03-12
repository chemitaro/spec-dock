from __future__ import annotations

from ..application.contracts import ActiveViewResult, DepsCheckResult, ValidationResult
from .contracts import CliText


def render_validate_text(result: ValidationResult) -> CliText:
    if result.report.errors:
        return CliText(
            stdout_lines=[],
            stderr_lines=[result.report.errors[0]],
            warnings=result.report.warnings,
        )
    return CliText(
        stdout_lines=[f"spec-dock: ok (validate) nodes={result.checked_node_count}"],
        stderr_lines=[],
        warnings=result.report.warnings,
    )


def render_deps_check_text(result: DepsCheckResult) -> CliText:
    target_id = result.inspection.target_id.value
    blockers = list(result.inspection.evaluation.blockers)
    if result.inspection.evaluation.ready:
        return CliText(
            stdout_lines=[f"spec-dock: ok (deps check) target={target_id} ready=true blockers=0"],
            stderr_lines=[],
            warnings=list(result.warnings),
        )
    return CliText(
        stdout_lines=[],
        stderr_lines=[
            f"spec-dock: blocked (deps check) target={target_id} ready=false blockers={len(blockers)}",
            *[f"- {blocker}" for blocker in blockers],
        ],
        warnings=list(result.warnings),
    )


def render_active_show_text(result: ActiveViewResult) -> CliText:
    def _format_entry(entry_id: str | None, entry_path: str | None) -> str:
        if entry_id and entry_path:
            return f"{entry_id} ({entry_path})"
        if entry_id:
            return entry_id
        return "(none)"

    all_none = (
        result.initiative.id is None
        and result.epic.id is None
        and result.issue.id is None
    )
    if all_none:
        stdout_lines = ["spec-dock: active: (not set)"]
    else:
        stdout_lines = [
            f"initiative: {_format_entry(result.initiative.id, result.initiative.path)}",
            f"epic: {_format_entry(result.epic.id, result.epic.path)}",
            f"issue: {_format_entry(result.issue.id, result.issue.path)}",
        ]

    return CliText(stdout_lines=stdout_lines, stderr_lines=[], warnings=list(result.warnings))
