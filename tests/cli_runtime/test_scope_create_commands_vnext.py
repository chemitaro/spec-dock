"""The vNext Scope create leaf resolves explicit ancestry before writing."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.cli import vnext_runtime  # noqa: E402
from spec_dock_runtime.cli.vnext_runtime import run_vnext  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo  # noqa: E402


def _run(repo: Path, *args: str):
    return run_vnext([*args, "--json"], invocation_cwd=repo, engine_digest="engine-a", engine_version="0.2.4")


def test_local_scope_create_cli_uses_explicit_parent_and_dry_run(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    preview = _run(repo, "scope", "create", "initiative", "--backend", "local", "--title", "Program", "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))

    initiative = _run(repo, "scope", "create", "initiative", "--backend", "local", "--title", "Program")
    assert initiative.exit_code == 0
    initiative_id = json.loads(initiative.stdout)["data"]["scope_id"]
    assert initiative_id == "init-local-00001"
    epic = _run(repo, "scope", "create", "epic", "--backend", "local", "--parent", initiative_id, "--title", "Plan")
    assert epic.exit_code == 0
    epic_id = json.loads(epic.stdout)["data"]["scope_id"]
    issue = _run(repo, "scope", "create", "issue", "--backend", "local", "--parent", epic_id, "--title", "Build")
    assert issue.exit_code == 0
    issue_id = json.loads(issue.stdout)["data"]["scope_id"]
    shown = _run(repo, "scope", "show", issue_id)
    assert json.loads(shown.stdout)["data"]["item"]["parent_id"] == epic_id


def test_local_scope_create_cli_rejects_missing_parent(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(
        repo, "scope", "create", "epic", "--backend", "local", "--parent", "init-local-00999", "--title", "Plan"
    )
    assert result.exit_code == 4
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))


def test_local_scope_create_cli_does_not_retry_a_recovery_request_as_new(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    result = _run(
        repo,
        "scope",
        "create",
        "initiative",
        "--backend",
        "local",
        "--title",
        "Program",
        "--resume",
        "a" * 32,
    )
    assert result.exit_code == 4
    assert not tuple((repo / "spec-dock" / "initiatives").glob("init-local-*"))


def test_local_scope_create_cli_resumes_original_reserved_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    original_update = JournalStore.update
    injected = False

    def fail_once(self: JournalStore, record, *, expected_sequence: int) -> None:
        nonlocal injected
        if not injected and record.effects and record.effects[-1].status == "succeeded":
            injected = True
            raise OSError("injected journal failure")
        original_update(self, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_once)
    prefix = ("scope", "create", "initiative", "--backend", "local", "--title", "Program")
    first = _run(repo, *prefix)
    assert first.exit_code == 5
    monkeypatch.setattr(JournalStore, "update", original_update)
    operation = JournalStore(cast("Path", common["common_dir"])).pending()[0]
    assert operation.effects[-1].status == "intent"
    resumed = _run(repo, *prefix, "--resume", operation.operation_id)
    assert resumed.exit_code == 0
    payload = json.loads(resumed.stdout)
    assert payload["data"]["scope_id"] == "init-local-00001"
    assert payload["operation_id"] == operation.operation_id


def test_github_scope_create_cli_previews_and_requires_confirmation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    prefix = ("scope", "create", "initiative", "--backend", "github", "--title", "Plan")
    preview = _run(repo, *prefix, "--dry-run")
    assert preview.exit_code == 0
    assert json.loads(preview.stdout)["status"] == "planned"
    assert gateway.calls == 0
    denied = _run(repo, *prefix)
    assert denied.exit_code == 3
    assert gateway.calls == 0
    created = _run(repo, *prefix, "--yes")
    assert created.exit_code == 0
    payload = json.loads(created.stdout)
    assert payload["data"]["scope_id"] == "init-00047"
    assert payload["data"]["github_ref"] == "gh:example/repo#47"
    assert gateway.calls == 1


def test_github_scope_create_cli_resumes_without_second_post(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common = _ready_repo(tmp_path)
    repo = cast("Path", common["repo_root"])
    destination = repo / "spec-dock/initiatives/init-00047-plan"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("occupied\n", encoding="utf-8")
    gateway = FakeGateway(_issue())
    monkeypatch.setattr(vnext_runtime, "GithubIssueGateway", lambda timeout: gateway)
    prefix = ("scope", "create", "initiative", "--backend", "github", "--title", "Plan")
    first = _run(repo, *prefix, "--yes")
    assert first.exit_code == 6
    operation = JournalStore(cast("Path", common["common_dir"])).pending()[0]
    destination.unlink()
    resumed = _run(repo, *prefix, "--resume", operation.operation_id)
    assert resumed.exit_code == 0
    assert json.loads(resumed.stdout)["operation_id"] == operation.operation_id
    assert gateway.calls == 1
