from __future__ import annotations

from ..application.contracts import ValidationResult
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
