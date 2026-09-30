"""Import CLI binds a fixed GitHub Issue and recovers local scaffold writes."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


from spec_dock.runtime.cli import vnext_runtime
from spec_dock.runtime.cli.vnext_runtime import run_vnext
from spec_dock.runtime.infra.operation_journal import JournalStore
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_scope_import_cli_previews_and_creates_without_post(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    prefix = ("scope", "import", "github", "initiative", "gh:example/repo#47", "--title", "Local plan")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    planned = json.loads(preview.stdout)
    assert planned["status"] == "planned"
    assert planned["data"]["scope"]["id"] is None
    assert planned["data"]["scope"]["kind"] == "initiative"
    assert planned["data"]["scope"]["backend"] == "github"
    assert planned["data"]["status"]["state"] == "unknown"
    assert planned["data"]["github_ref"] == "gh:example/repo#47"
    assert planned["data"]["project"] == str(repo)
    assert planned["data"]["worktree"] == common["worktree_id"]
    assert planned["data"]["snapshot_id"]
    assert gateway.calls == 0
    imported = _run(repo, *prefix)
    assert imported.exit_code == 0
    payload = json.loads(imported.stdout)
    assert payload["data"]["scope_id"] == "init-00047"
    assert gateway.calls == 0


def test_scope_import_json_identifies_linked_scope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    imported = _run(repo, "scope", "import", "github", "initiative", "gh:example/repo#47", "--title", "Local plan")
    assert imported.exit_code == 0
    payload = json.loads(imported.stdout)
    assert payload["target"]["id"] == payload["data"]["scope"]["id"] == "init-00047"
    assert payload["data"]["scope"]["backend"] == "github"
    assert payload["data"]["github_ref"] == "gh:example/repo#47"
    assert payload["data"]["status"]["source"] in {"github", "cache", "unknown"}
    assert payload["target"]["snapshot_id"] == payload["data"]["snapshot_id"]


def test_scope_import_cli_resumes_after_uncertain_local_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    original_update = JournalStore.update
    injected = False

    def fail_once(self: JournalStore, record, *, expected_sequence: int) -> None:
        nonlocal injected
        if not injected and record.effects and record.effects[-1].status == "succeeded":
            injected = True
            raise OSError("injected journal failure")
        original_update(self, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_once)
    prefix = ("scope", "import", "github", "initiative", "gh:example/repo#47", "--title", "Plan")
    first = _run(repo, *prefix)
    assert first.exit_code == 6
    assert json.loads(first.stdout)["error"]["code"] == "EFFECT_STATE_UNKNOWN"
    monkeypatch.setattr(JournalStore, "update", original_update)
    operation = JournalStore(cast("Path", common["common_dir"])).pending()[0]
    resumed = _run(repo, *prefix, "--resume", operation.operation_id)
    assert resumed.exit_code == 0
    assert json.loads(resumed.stdout)["operation_id"] == operation.operation_id
    assert gateway.calls == 0


def test_scope_import_cli_requires_source_reference(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(repo, "scope", "import", "github", "initiative", "--title", "Plan")
    assert result.exit_code == 2
