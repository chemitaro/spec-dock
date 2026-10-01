"""Readonly Sync observes direct selection and lifecycle without publishing a cache."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from spec_dock.cli import main
from spec_dock.runtime.infra.tree_backup import tree_digest
from tests.cli_runtime.test_issue413_active import select_fixture
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_scope_lifecycle_commands_vnext import existing_local_workspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("preview", [False, True])
def test_sync_preserves_direct_selection_and_opaque_old_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    preview: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    generation = root / "spec-dock/.agent/generation.json"
    generation.write_bytes(b"opaque old generation, never read or repaired")
    before = tree_digest(root)
    log = github_fixture(tmp_path, monkeypatch, {})
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "sync",
            *(["--dry-run"] if preview else []),
            "--json",
        ])
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    data = result["data"]
    assert result["status"] == ("planned" if preview else "succeeded") and result["effects"] == []
    assert data["source"] == "local" and data["complete"] is True
    assert data["scopes"] == [{"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "unknown"}]
    assert data["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 1, "descendant_selected_count": 0, "complete": True},
    ]
    assert data["worktrees"][0]["selection"]["scope_id"] == "init-00001"
    assert data["worktrees"][0]["process_state"] == "not_observed"
    assert not log.exists() and tree_digest(root) == before
    assert set(record.parent.iterdir()) == {record} and not (root / ".git/spec-dock").exists()


def test_sync_keeps_existing_local_lifecycle_and_empty_workspace_readonly(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root, metadata = existing_local_workspace(tmp_path / "consumer")
    command = ["--project", str(root), "workspace", "sync", "--json"]
    before = tree_digest(root)
    assert main(command) == 0
    local = json.loads(capsys.readouterr().out)
    assert local["data"]["scopes"] == [{"scope_id": "init-00001", "github_ref": None, "lifecycle": "open"}]
    assert local["data"]["counts"] == [
        {"scope_id": "init-00001", "direct_selected_count": 0, "descendant_selected_count": 0, "complete": True},
    ]
    assert local["effects"] == [] and tree_digest(root) == before
    metadata.unlink()
    metadata.parent.rmdir()
    empty_before = tree_digest(root)
    assert main(command) == 0
    empty = json.loads(capsys.readouterr().out)
    assert empty["data"]["scopes"] == [] and empty["data"]["counts"] == []
    assert empty["data"]["complete"] is True and empty["effects"] == []
    assert tree_digest(root) == empty_before and not (root / "spec-dock/.agent").exists()


def test_live_sync_failure_returns_unknown_and_keeps_the_captured_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    record = select_fixture(root)
    before = tree_digest(root)
    log = github_fixture(tmp_path, monkeypatch, {})
    assert main(["--project", str(root), "workspace", "sync", "--source", "github", "--json"]) == 7
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "partial" and result["effects"] == []
    assert result["data"]["complete"] is False
    assert result["data"]["scopes"] == [
        {"scope_id": "init-00001", "github_ref": "gh:example/repo#1", "lifecycle": "unknown"},
    ]
    assert any(item["details"].get("github_ref") == "gh:example/repo#1" for item in result["data"]["findings"])
    assert [json.loads(line)["method"] for line in log.read_text().splitlines()] == ["GET"]
    assert tree_digest(root) == before and set(record.parent.iterdir()) == {record}


@pytest.mark.parametrize("allow_invalid", [False, True])
def test_sync_never_treats_invalid_parent_metadata_as_a_complete_observation(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    allow_invalid: bool,
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    metadata = root / "spec-dock/initiatives/init-00001-fixture/.meta.json"
    payload = json.loads(metadata.read_bytes())
    payload["parent_id"] = "epic-99999"
    metadata.write_text(json.dumps(payload))
    before = tree_digest(root)
    assert (
        main([
            "--project",
            str(root),
            "workspace",
            "sync",
            *(["--allow-invalid"] if allow_invalid else []),
            "--json",
        ])
        == 7
    )
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "failed" and result["error"]["code"] == "SYNC_INPUT_INVALID"
    assert result["effects"] == [] and tree_digest(root) == before
    assert not (root / "spec-dock/.agent").exists() and not (root / ".git/spec-dock").exists()
