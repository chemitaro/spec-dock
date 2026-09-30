"""Public contracts for the external CLI without repository control (Issue #413)."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

from spec_dock.cli import main


def make_workspace(root: Path) -> Path:
    """Build a GitHub-backed schema-3 test fixture, never real dogfood metadata."""
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
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
    return root


def test_independent_scope_read_does_not_require_control(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = metadata.read_bytes()

    exit_code = main(["--project", str(root), "scope", "show", "init-00001", "--json"])

    output = capsys.readouterr()
    assert exit_code == 0, output.out + output.err
    result = json.loads(output.out)
    assert result["data"]["result"]["scope"]["id"] == "init-00001"
    assert result["data"]["result"]["scope"]["status"]["state"] == "unknown"
    assert result["effects"] == []
    assert not output.err
    assert metadata.read_bytes() == before
    assert not (root / ".git/spec-dock").exists()
