from __future__ import annotations

from ..application.contracts import DepsCheckResult, ValidationResult
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
