"""Public Scope reads and title edits preserve existing data without control."""

from __future__ import annotations

import json
import stat
from typing import TYPE_CHECKING

from spec_dock.cli import main
from spec_dock.runtime.application.project_context import resolve_context
from spec_dock.runtime.domain.work_target import WorkTarget
from spec_dock.runtime.infra.tree_backup import tree_digest
from spec_dock.runtime.infra.work_target_store import WorkTargetStore
from tests.cli_runtime.test_issue413_finish import github_fixture
from tests.cli_runtime.test_issue413_work_start import committed_workspace
from tests.cli_runtime.test_scope_lifecycle_commands_vnext import existing_local_workspace

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_scope_query_filters_existing_local_data_without_network_or_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, _metadata = existing_local_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    context = resolve_context(str(root), root)
    WorkTargetStore(root).publish(
        WorkTarget(
            "specdock.work-target/v1",
            "init-00001",
            None,
            "main",
            "2026-09-30T00:00:00Z",
            context.clone_identity,
            context.worktree_identity,
        )
    )
    before = tree_digest(root)
    prefix = ["--project", str(root), "scope"]
    assert main([*prefix, "list", "--kind", "initiative", "--state", "open", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    items = result["data"]["result"]["items"]
    assert [item["id"] for item in items] == ["init-00001"]
    assert items[0]["backend"] == "local"
    assert items[0]["status"]["state"] == "open" and items[0]["status"]["source"] == "local"
    assert result["effects"] == [] and not output.err
    assert main([*prefix, "list", "--kind", "issue", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["items"] == [] and result["effects"] == [] and not output.err
    for selector in ("init-00001", "@current"):
        assert main([*prefix, "show", selector, "--json"]) == 0
        output = capsys.readouterr()
        result = json.loads(output.out)
        scope = result["data"]["result"]["scope"]
        assert scope["id"] == "init-00001" and scope["backend"] == "local"
        assert scope["github_ref"] is None and result["effects"] == [] and not output.err
    assert not log.exists() and tree_digest(root) == before
    assert not (root / ".git/spec-dock").exists()


def test_scope_query_ignores_retired_github_status_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = committed_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    cache = root / "spec-dock/.agent/github-status-cache.json"
    cache.parent.mkdir()
    cache.write_text(
        json.dumps({
            "schema_version": 1,
            "items": {
                "init-00001": {
                    "github_ref": "gh:example/repo#1",
                    "state": "completed",
                    "observed_at": "2026-09-25T00:00:00Z",
                }
            },
        })
    )
    before = tree_digest(root)
    prefix = ["--project", str(root), "scope"]
    assert main([*prefix, "show", "init-00001", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    status = result["data"]["result"]["scope"]["status"]
    assert status == {"state": "unknown", "authority": "github", "source": "unknown", "observed_at": None}
    assert result["effects"] == [] and not output.err
    assert main([*prefix, "list", "--state", "completed", "--json"]) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["data"]["result"]["items"] == []
    assert result["data"]["result"]["unknown_filtered_count"] == 1
    assert result["effects"] == [] and not output.err
    assert not log.exists() and tree_digest(root) == before


def test_scope_title_edit_preserves_existing_fields_documents_and_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root, meta_path = existing_local_workspace(tmp_path / "consumer")
    log = github_fixture(tmp_path, monkeypatch, {"1": "open"})
    before = json.loads(meta_path.read_bytes())
    before["custom_note"] = {"owner": "test", "priority": 4}
    meta_path.write_text(json.dumps(before))
    meta_path.chmod(0o444)
    for name in ("requirement.md", "design.md", "plan.md"):
        (meta_path.parent / name).write_text(f"# Existing {name}\nKeep this exact body.\n")
    before_mode = stat.S_IMODE(meta_path.stat().st_mode)
    document_bytes = {path.name: path.read_bytes() for path in meta_path.parent.glob("*.md")}
    command = ["--project", str(root), "scope", "edit", "init-00001", "--title", "Revised", "--json"]
    assert main(command) == 0
    output = capsys.readouterr()
    result = json.loads(output.out)
    assert result["status"] == "succeeded" and result["data"]["result"]["changed"] is True
    assert result["data"]["result"]["scope"]["backend"] == "local" and not output.err
    after_bytes = meta_path.read_bytes()
    after = json.loads(after_bytes)
    assert after["title"] == "Revised"
    assert after["revision"] == before["revision"] + 1
    assert {key: value for key, value in after.items() if key not in ("title", "revision")} == {
        key: value for key, value in before.items() if key not in ("title", "revision")
    }
    assert stat.S_IMODE(meta_path.stat().st_mode) == before_mode
    assert {path.name: path.read_bytes() for path in meta_path.parent.glob("*.md")} == document_bytes
    edited_tree = tree_digest(root)
    assert main(command) == 0
    output = capsys.readouterr()
    same = json.loads(output.out)
    assert same["status"] == "unchanged" and same["data"]["result"]["changed"] is False
    assert same["effects"] == [] and not output.err
    assert meta_path.read_bytes() == after_bytes and tree_digest(root) == edited_tree
    assert not log.exists() and not (root / ".git/spec-dock").exists()
