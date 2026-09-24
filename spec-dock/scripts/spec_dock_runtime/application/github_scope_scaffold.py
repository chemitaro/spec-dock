"""Build one GitHub-backed Scope scaffold from an already verified Issue."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from spec_dock_runtime.application.contracts import CreatePlan
from spec_dock_runtime.application.create_node import _replacements, _rules_scaffold_specs, _scaffold_file_paths
from spec_dock_runtime.domain.ids import format_id
from spec_dock_runtime.infra.contracts import StoredMetaRecord

if TYPE_CHECKING:
    from spec_dock_runtime.domain.selectors import ScopeKind


def build_github_scope_scaffold(
    *,
    specdock_dir: Path,
    kind: ScopeKind,
    title: str,
    slug: str,
    parent_id: str | None,
    parent_record: StoredMetaRecord | None,
    repository: str,
    issue_number: int,
    today: str,
) -> tuple[CreatePlan, dict[str, object]]:
    owner, repo = repository.split("/", 1)
    prefix = {"initiative": "init", "epic": "epic", "issue": "iss"}[kind]
    scope_id = format_id(prefix, issue_number)
    if parent_record is None:
        dest_parent = specdock_dir / "initiatives"
        initiative_id = None
        epic_id = None
    else:
        parent_path = Path(parent_record.path)
        dest_parent = parent_path / ("epics" if kind == "epic" else "issues")
        initiative_id = parent_record.id if kind == "epic" else parent_record.initiative_id
        epic_id = parent_record.id if kind == "issue" else None
    destination = dest_parent / f"{scope_id}-{slug}"
    metadata_payload: dict[str, object] = {
        "schema_version": 3,
        "type": kind,
        "id": scope_id,
        "title": title,
        "slug": slug,
        "parent_id": parent_id,
        "initiative_id": initiative_id,
        "epic_id": epic_id,
        "depends_on": [],
        "backend": "github",
        "github": {"issue_number": issue_number, "repo_owner": owner, "repo_name": repo},
        "lifecycle": None,
        "revision": 0,
    }
    template_dir = specdock_dir / "templates" / kind
    paths = _scaffold_file_paths(template_dir, destination)
    paths.extend(
        link for link, _target in _rules_scaffold_specs(kind=kind, dest_dir=destination, specdock_dir=specdock_dir)
    )
    paths.append(destination / ".meta.json")
    node_record = StoredMetaRecord(
        kind=kind,
        id=scope_id,
        title=title,
        slug=slug,
        path=str(destination),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=issue_number,
        meta_path=str(destination / ".meta.json"),
        github_repo_owner=owner,
        github_repo_name=repo,
    )
    plan = CreatePlan(
        meta=node_record,
        dest_dir=destination,
        replacements=_replacements(
            kind=kind,
            node_id=scope_id,
            title=title,
            parent_id=parent_id,
            initiative_id=initiative_id,
            github_issue_number=issue_number,
            today=today,
        ),
        planned_paths=paths,
    )
    return plan, metadata_payload
