"""Workspace diagnostics preserve readonly validation and doctor outcomes."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_issue413_workspace_validate import commit_fixture

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_workspace_diagnostics_cli_reports_valid_and_required_nodes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    metadata.unlink()
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (metadata.parent / filename).unlink()
    metadata.parent.rmdir()
    commit_fixture(root)
    before = tree_digest(root)
    prefix = ["--project", str(root), "workspace"]
    assert main([*prefix, "validate", "--json"]) == 0
    valid = json.loads(capsys.readouterr().out)
    assert valid["data"]["result"]["valid"] is True
    assert valid["data"]["result"]["node_count"] == 0 and valid["effects"] == []
    assert main([*prefix, "validate", "--require-nodes", "--json"]) == 7
    required = json.loads(capsys.readouterr().out)
    assert [item["code"] for item in required["data"]["result"]["findings"]] == ["NODES_REQUIRED"]
    assert required["effects"] == []
    assert main([*prefix, "doctor", "--json"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["data"]["kind"] == "diagnostic" and doctor["effects"] == []
    assert tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent").exists()
