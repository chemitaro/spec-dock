"""Migration changes only the explicit worktree declaration after real backup."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_workspace_validate import commit_fixture
from tests.integration.test_issue413_migration import TARGET, legacy_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_migration_preview_is_local_even_when_another_worktree_has_an_unknown_declaration(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = legacy_workspace(tmp_path / "main")
    commit_fixture(root)
    linked = tmp_path / "linked"
    subprocess.run(
        ["git", "-C", str(root), "worktree", "add", "-b", "linked", str(linked)],
        check=True,
        capture_output=True,
    )
    (linked / "spec-dock/workspace.json").write_bytes(b'{"schema_version":99,"private":"do-not-echo"}')
    before = tree_digest(root)
    other = tree_digest(linked)
    assert main(["--project", str(root), "workspace", "migrate", *TARGET, "--dry-run", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    data = result["data"]["result"]
    assert result["status"] == "planned" and data["target"] == str(root)
    assert data["planned_paths"] == ["spec-dock/workspace.json"]
    assert data["changed_paths"] == [] and data["scope_count"] == 1 and data["can_apply"] is True
    assert tree_digest(root) == before and tree_digest(linked) == other
    assert "do-not-echo" not in output.out + output.err and not (root / ".git/spec-dock").exists()
    assert not (root / "spec-dock/.agent").exists()


def test_migration_apply_requires_explicit_confirmation_and_never_offers_journal_rollback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = legacy_workspace(tmp_path / "consumer")
    workspace = root / "spec-dock/workspace.json"
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    before = tree_digest(root)
    declaration = json.loads(workspace.read_bytes())
    metadata_before = metadata.read_bytes()
    backup = tmp_path / "backup"
    command = [
        "--project",
        str(root),
        "workspace",
        "migrate",
        *TARGET,
        "--backup-dir",
        str(backup),
        "--confirm-old-writers-stopped",
        "--json",
    ]
    assert main(command) == 3
    assert json.loads(capsys.readouterr().out)["effects"] == []
    assert tree_digest(root) == before and not backup.exists()
    assert main([*command, "--yes"]) == 0
    result = json.loads(capsys.readouterr().out)
    data = result["data"]["result"]
    assert data["changed_paths"] == ["spec-dock/workspace.json"]
    assert data["backup_verified"] is True and data["restore_verified"] is True
    assert tree_digest(backup / "checkout") == before
    assert metadata.read_bytes() == metadata_before
    expected = {**declaration, "writer_protocol": "specdock.worktree-writer/v1"}
    del expected["control_epoch"]
    assert json.loads(workspace.read_bytes()) == expected and "operation_id" not in result
    after = tree_digest(root)
    assert main([*command, "--rollback", "old-operation", "--yes"]) == 2
    refused = json.loads(capsys.readouterr().out)
    assert refused["error"]["code"] == "ARGUMENT_RETIRED" and refused["effects"] == []
    assert tree_digest(root) == after
    assert not (root / ".git/spec-dock").exists() and not (root / "spec-dock/.agent/work-target").exists()


def test_migration_mapping_file_is_retired_without_reading_the_file_or_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mapping = tmp_path / "mapping.json"
    mapping.write_bytes(b'{"private":"must-not-be-interpreted"}')
    assert (
        main([
            "--project",
            str(tmp_path / "missing"),
            "workspace",
            "migrate",
            *TARGET,
            "--mapping-file",
            str(mapping),
            "--dry-run",
            "--json",
        ])
        == 2
    )
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["error"]["code"] == "ARGUMENT_RETIRED" and result["effects"] == []
    assert mapping.read_bytes() == b'{"private":"must-not-be-interpreted"}'
    assert "must-not-be-interpreted" not in output.out + output.err
    assert list(tmp_path.iterdir()) == [mapping]
