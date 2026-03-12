from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import TargetDepsInspection, ValidationReport


@dataclass(frozen=True)
class ValidateTreeRequest:
    pass


@dataclass(frozen=True)
class ValidationResult:
    report: ValidationReport
    checked_node_count: int


@dataclass(frozen=True)
class TargetRef:
    kind: str
    node_id: str | None
    github_issue_number: int | None


@dataclass(frozen=True)
class CheckDepsRequest:
    target: TargetRef
    use_github: bool
    issue_limit: int


@dataclass(frozen=True)
class DepsCheckResult:
    target: TargetRef
    inspection: TargetDepsInspection
    warnings: list[str]
