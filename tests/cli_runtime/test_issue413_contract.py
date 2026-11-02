"""Legacy schema-3 workspace fixtures kept for other modules (iss-00440).

Its tests moved to tests/cli_runtime/test_issue440_g1_contract.py.
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


# TODO(iss-00440): remove after all groups migrate
def make_workspace(root: Path) -> Path:
    """Build a GitHub-backed schema-3 test fixture, never real dogfood metadata."""
    root.mkdir()
    subprocess.run(["git", "init", "--initial-branch=main", "-q", str(root)], check=True, capture_output=True)
    # Snapshot tests must not race Git's detached maintenance after fixture commits.
    subprocess.run(
        ["git", "-C", str(root), "config", "--local", "maintenance.auto", "false"],
        check=True,
        capture_output=True,
    )
    workspace = root / "spec-dock"
    scope = workspace / "initiatives/init-00001-fixture"
    scope.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        '{"schema_version":3,"writer_protocol":"specdock.worktree-writer/v1"}\n', encoding="utf-8"
    )
    (workspace / ".gitignore").write_text(".agent/\n.workbench/\n", encoding="utf-8")
    (scope / ".meta.json").write_text(
        json.dumps({
            "schema_version": 3,
            "id": "init-00001",
            "type": "initiative",
            "title": "Fixture",
            "slug": "fixture",
            "parent_id": None,
            "initiative_id": None,
            "epic_id": None,
            "backend": "github",
            "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
            "lifecycle": None,
            "revision": 0,
            "depends_on": [],
            "created_at": "2026-09-30T00:00:00Z",
            "updated_at": "2026-09-30T00:00:00Z",
        })
        + "\n",
        encoding="utf-8",
    )
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (scope / filename).write_text("# Fixture\n", encoding="utf-8")
    return root


# TODO(iss-00440): remove after all groups migrate
def add_scope(root: Path, scope_id: str, kind: str, parent_id: str, parent: Path) -> Path:
    metadata = json.loads((root / "spec-dock/initiatives/init-00001-fixture/.meta.json").read_bytes())
    path = parent / ("epics" if kind == "epic" else "issues") / f"{scope_id}-fixture"
    path.mkdir(parents=True)
    (path / ".meta.json").write_text(
        json.dumps(
            dict(
                metadata,
                id=scope_id,
                type=kind,
                parent_id=parent_id,
                initiative_id="init-00001",
                epic_id=parent_id if kind == "issue" else None,
                github=dict(metadata["github"], issue_number=int(scope_id.split("-")[-1])),
            )
        )
    )
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (path / filename).write_text("# Fixture\n", encoding="utf-8")
    return path
