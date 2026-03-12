from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..domain.models import ActiveSelection, BranchDecision, TargetDepsInspection, ValidationReport


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


@dataclass(frozen=True)
class ShowActiveRequest:
    pass


@dataclass(frozen=True)
class ActiveViewEntry:
    id: str | None
    path: str | None


@dataclass(frozen=True)
class ActiveViewResult:
    initiative: ActiveViewEntry
    epic: ActiveViewEntry
    issue: ActiveViewEntry
    source: Literal["agent.active", "legacy.work.active", "legacy.work.current", "none"]
    warnings: list[str]


@dataclass(frozen=True)
class SetActiveRequest:
    target: TargetRef
    force: bool
    checkout: bool
    use_github: bool
    issue_limit: int


@dataclass(frozen=True)
class ActiveSetResult:
    selection: ActiveSelection
    branch: BranchDecision | None
    manifest_written: bool
    pointer_updated: bool
    warnings: list[str]


@dataclass(frozen=True)
class ClearActiveRequest:
    pass


@dataclass(frozen=True)
class ActiveClearResult:
    cleared: bool
    previous: ActiveSelection | None
    warnings: list[str]
