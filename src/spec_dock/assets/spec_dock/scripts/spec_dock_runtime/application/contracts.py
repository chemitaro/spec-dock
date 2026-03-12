from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import ValidationReport


@dataclass(frozen=True)
class ValidateTreeRequest:
    pass


@dataclass(frozen=True)
class ValidationResult:
    report: ValidationReport
    checked_node_count: int
