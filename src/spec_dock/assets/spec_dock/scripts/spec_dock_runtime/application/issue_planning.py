from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from spec_dock_runtime.domain.ids import normalize_id_input

if TYPE_CHECKING:
    from collections.abc import Sequence

    from spec_dock_runtime.infra.contracts import StoredMetaRecord


@dataclass(frozen=True)
class PlanningCreateRequest:
    issue_id: str
    output_dir: Path


@dataclass(frozen=True)
class PlanningReviseRequest:
    candidate_path: Path
    request_path: Path
    output_dir: Path


@dataclass(frozen=True)
class PlanningReviewRequest:
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    output_dir: Path
    candidate_path: Path | None = None
    reviewed_head: str | None = None


@dataclass(frozen=True)
class PlanningApplyRequest:
    issue_id: str
    mode: Literal["archive-candidate", "git-bound"]
    review_result_path: Path
    human_decision_path: Path
    expected_head: str
    output_dir: Path
    candidate_path: Path | None = None
    logical_filename: str | None = None
    zip_sha256: str | None = None
    reviewed_head: str | None = None


@dataclass(frozen=True)
class ExistingIssueTarget:
    issue_id: str
    parent_epic_id: str
    parent_initiative_id: str
    canonical_issue_paths: tuple[str, str, str]


def resolve_existing_issue_target(
    issue: str,
    records: Sequence[StoredMetaRecord],
    repo_root: Path,
) -> ExistingIssueTarget:
    try:
        issue_id = normalize_id_input(issue, prefix="iss", field="issue")
    except RuntimeError as error:
        raise ValueError("an existing Issue ID is required") from error

    matches = [record for record in records if record.id == issue_id]
    if len(matches) != 1:
        raise ValueError(f"existing Issue not found: {issue_id}")
    record = matches[0]
    if record.kind != "issue":
        raise ValueError(f"existing Issue required: {issue_id}")
    if record.epic_id is None or record.initiative_id is None:
        raise ValueError(f"existing Issue parent identity is incomplete: {issue_id}")
    try:
        parent_epic_id = normalize_id_input(record.epic_id, prefix="epic", field="epic_id")
        parent_initiative_id = normalize_id_input(
            record.initiative_id,
            prefix="init",
            field="initiative_id",
        )
    except RuntimeError as error:
        raise ValueError(f"existing Issue parent identity is invalid: {issue_id}") from error

    root = repo_root.resolve(strict=True)
    raw_path = Path(record.path)
    if ".." in raw_path.parts:
        raise ValueError(f"canonical Issue path must be a safe path without '..': {issue_id}")
    issue_dir = raw_path if raw_path.is_absolute() else root / raw_path
    lexical_issue_dir = issue_dir.absolute()
    if _contains_symlink(root, lexical_issue_dir):
        raise ValueError(f"canonical Issue path must not contain symlinks: {issue_id}")
    try:
        resolved_issue_dir = issue_dir.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"canonical Issue path does not exist: {issue_id}") from error
    initiatives_root = (root / "spec-dock" / "initiatives").resolve(strict=False)
    if not resolved_issue_dir.is_relative_to(initiatives_root):
        raise ValueError(f"canonical Issue path escapes spec-dock/initiatives: {issue_id}")

    paths: list[str] = []
    for filename in ("design.md", "plan.md", "requirement.md"):
        target = resolved_issue_dir / filename
        if target.is_symlink() or not target.is_file():
            raise ValueError(f"canonical Issue target is incomplete: {filename}")
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError("canonical Issue target escapes repository") from error
        paths.append(relative)
    ordered = tuple(sorted(paths, key=lambda path: path.encode("utf-8")))
    return ExistingIssueTarget(
        issue_id=issue_id,
        parent_epic_id=parent_epic_id,
        parent_initiative_id=parent_initiative_id,
        canonical_issue_paths=(ordered[0], ordered[1], ordered[2]),
    )


def _contains_symlink(root: Path, target: Path) -> bool:
    try:
        relative = target.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False
