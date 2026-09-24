"""Sync publishes a derived snapshot without modifying the active selection."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.application.scope_query import ScopeView  # noqa: E402
from spec_dock_runtime.application.workspace_diagnostics_vnext import doctor_workspace  # noqa: E402
from spec_dock_runtime.application.workspace_sync_vnext import sync_workspace  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.domain.lifecycle import (  # noqa: E402
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    StatusObservation,
)
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from spec_dock_runtime.infra.generation_store import load_generation  # noqa: E402
from spec_dock_runtime.infra.github_lifecycle import GithubIssueGateway, RemoteIssueError  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _sync_args(common: dict[str, object]) -> dict[str, object]:
    return {key: common[key] for key in ("repo_root", "common_dir", "worktree_id", "engine_digest", "expected_epoch")}


def test_workspace_sync_cli_preview_and_publish_preserve_selection(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    before = load_selection_v3(repo / "spec-dock", worktree_id="main")[0]

    def run(*options: str):
        return run_vnext(
            ["workspace", "sync", *options, "--json"],
            invocation_cwd=repo,
            engine_digest="engine-a",
            engine_version="0.2.4",
        )

    preview = run("--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert load_generation(repo / "spec-dock") is None
    published = run()
    assert published.exit_code == 0
    data = json.loads(published.stdout)["data"]
    assert data["node_count"] == 0 and data["source"] == "cache"
    assert data["generation_id"] == load_generation(repo / "spec-dock").id
    assert load_selection_v3(repo / "spec-dock", worktree_id="main")[0] == before


def test_empty_and_local_workspace_sync_leave_selection_unchanged(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    selection_before = load_selection_v3(repo / "spec-dock", worktree_id="main")[0]
    empty = sync_workspace(**_sync_args(common))
    assert empty.node_count == 0 and empty.generation.valid and empty.complete
    assert json.loads(empty.generation.files["index.json"])["nodes"] == {}
    assert load_selection_v3(repo / "spec-dock", worktree_id="main")[0] == selection_before
    created = create_local_scope(kind="initiative", title="Plan", parent=None, ancestors=(), **common)
    local = sync_workspace(**_sync_args(common))
    payload = json.loads(local.generation.files["index.json"])
    assert payload["nodes"][created.id]["status"]["source"] == "local"
    assert load_generation(repo / "spec-dock") == local.generation
    assert load_selection_v3(repo / "spec-dock", worktree_id="main")[0] == selection_before


def test_live_failure_is_incomplete_and_does_not_mark_unknown_fresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    fake = ScopeView(
        "init-00047",
        "initiative",
        "Plan",
        None,
        GithubBackend(47, "example", "repo"),
        repo / "spec-dock" / "initiatives" / "fake",
        0,
        StatusObservation("unknown", "github", "unknown", None, None, True),
        "gh:example/repo#47",
    )
    monkeypatch.setattr(
        "spec_dock_runtime.application.workspace_sync_vnext.load_scope_views", lambda _directory: (fake,)
    )

    class FailingGateway:
        def get(self, _repo: Path, _repository: str, _number: int) -> None:
            raise RemoteIssueError("GITHUB_REMOTE_UNAVAILABLE")

    result = sync_workspace(**_sync_args(common), source="github", gateway=cast("GithubIssueGateway", FailingGateway()))
    node = json.loads(result.generation.files["index.json"])["nodes"][fake.id]
    assert result.complete is False
    assert node["status"]["state"] == "unknown"
    assert node["status"]["stale"] is True
    assert result.findings == ("github_unavailable:init-00047",)
    with pytest.raises(ValueError, match="offline"):
        sync_workspace(**_sync_args(common), source="github", offline=True)


def test_invalid_parent_requires_diagnostic_opt_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    orphan = ScopeView(
        "epic-local-00001",
        "epic",
        "Orphan",
        "init-local-99999",
        LocalBackend(LocalLifecycle("open", 0, "2026-09-25T00:00:00Z")),
        repo / "spec-dock" / "initiatives" / "fake" / "epics" / "fake",
        0,
        StatusObservation("open", "local", "local", "2026-09-25T00:00:00Z", None, False),
        None,
    )
    monkeypatch.setattr(
        "spec_dock_runtime.application.workspace_sync_vnext.load_scope_views", lambda _directory: (orphan,)
    )
    with pytest.raises(ValueError, match="structure"):
        sync_workspace(**_sync_args(common))
    assert load_generation(repo / "spec-dock") is None
    result = sync_workspace(**_sync_args(common), allow_invalid=True)
    assert result.generation.valid is False
    assert result.findings == ("invalid_parent:epic-local-00001",)


def test_projection_failure_keeps_generation_readable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])

    def fail_projection(*_args: object, **_kwargs: object) -> None:
        raise OSError("injected projection failure")

    monkeypatch.setattr("spec_dock_runtime.application.workspace_sync_vnext.atomic_write_json", fail_projection)
    result = sync_workspace(**_sync_args(common))
    assert result.projection_stale is True
    assert load_generation(repo / "spec-dock") == result.generation
    diagnosed = doctor_workspace(
        repo_root=repo,
        common_dir=cast("Path", common["common_dir"]),
        worktree_id="main",
        engine_digest="engine-a",
    )
    assert "projection_stale" in {finding.code for finding in diagnosed.findings}
