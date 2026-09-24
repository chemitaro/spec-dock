"""GitHub Scope create records the remote effect before local publication."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_github_scope import create_github_scope  # noqa: E402
from spec_dock_runtime.application.create_local_scope import create_local_scope  # noqa: E402
from spec_dock_runtime.application.github_create_effect import create_github_issue_effect  # noqa: E402
from spec_dock_runtime.application.import_github_scope import import_github_scope  # noqa: E402
from spec_dock_runtime.application.operation_executor import prepare_operation  # noqa: E402
from spec_dock_runtime.infra.contracts import GithubIssueRecord  # noqa: E402
from spec_dock_runtime.infra.control_store import ControlState, WorktreeRegistration, store_control  # noqa: E402
from spec_dock_runtime.infra.git_cli import git_common_directory  # noqa: E402
from spec_dock_runtime.infra.github_lifecycle import RemoteIssueError  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime import harness  # noqa: E402


class FakeGateway:
    def __init__(self, result: GithubIssueRecord | Exception, *, expected_title: str = "Plan") -> None:
        self.result = result
        self.expected_title = expected_title
        self.calls = 0

    def create(self, repo_root: Path, repository: str, *, title: str, body: str) -> GithubIssueRecord:
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        assert repository == "example/repo"
        assert title == self.expected_title
        assert body.startswith("Created by SpecDock.")
        return self.result

    def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
        assert repository == "example/repo"
        assert number == 47
        return _issue()


def _prepared(store: JournalStore):
    operation = prepare_operation(
        command="scope.create",
        fixed_targets={"repository": "example/repo", "title": "Plan"},
        request_fingerprint="sha256:request",
        before_revisions={},
        engine_digest="engine-a",
        writer_epoch=1,
        effect_plan=("github-create", "scaffold"),
    )
    store.create(operation)
    return operation


def _issue() -> GithubIssueRecord:
    return GithubIssueRecord(
        47,
        "example/repo",
        "Plan",
        "open",
        "open",
        None,
        "2026-09-24T00:00:00Z",
        "https://github.com/example/repo/issues/47",
    )


def test_remote_receipt_is_durable_before_local_scaffold_and_cannot_be_replayed(tmp_path: Path) -> None:
    store = JournalStore(tmp_path)
    operation = _prepared(store)
    gateway = FakeGateway(_issue())
    advanced, created = create_github_issue_effect(
        operation=operation,
        journal=store,
        gateway=gateway,
        repo_root=tmp_path,
        repository="example/repo",
        title="Plan",
        body="Created by SpecDock.",
    )
    assert created.number == 47
    assert advanced.effects[0].remote_ref == "gh:example/repo#47"
    assert store.load(operation.operation_id) == advanced
    assert advanced.terminal_status == "pending"
    with pytest.raises(ValueError, match="already sent"):
        create_github_issue_effect(
            operation=advanced,
            journal=store,
            gateway=gateway,
            repo_root=tmp_path,
            repository="example/repo",
            title="Plan",
            body="Created by SpecDock.",
        )
    assert gateway.calls == 1


@pytest.mark.parametrize("uncertain", [False, True])
def test_remote_failure_records_confirmed_or_unknown_outcome(tmp_path: Path, uncertain: bool) -> None:
    store = JournalStore(tmp_path)
    operation = _prepared(store)
    gateway = FakeGateway(RemoteIssueError("INJECTED", uncertain=uncertain))
    with pytest.raises(RemoteIssueError, match="INJECTED"):
        create_github_issue_effect(
            operation=operation,
            journal=store,
            gateway=gateway,
            repo_root=tmp_path,
            repository="example/repo",
            title="Plan",
            body="Created by SpecDock.",
        )
    saved = store.load(operation.operation_id)
    assert saved.effects[0].status == ("unknown" if uncertain else "failed")
    assert saved.terminal_status == ("pending" if uncertain else "failed")
    assert gateway.calls == 1


def _ready_repo(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "repo"
    assert harness.main(["init", str(repo)]) == 0
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "remote", "add", "origin", "https://github.com/example/repo.git"],
        check=True,
        capture_output=True,
    )
    common_dir = git_common_directory(repo)
    registration = WorktreeRegistration("main", str(repo), 3, "specdock.writer/v1", "engine-a", True)
    store_control(
        common_dir,
        ControlState(3, "specdock.writer/v1", 1, "engine-a", "ready", (registration,)),
        expected_epoch=None,
    )
    return {
        "repo_root": repo,
        "common_dir": common_dir,
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "updated_at": "2026-09-24T00:00:00Z",
    }


def test_github_initiative_create_scaffolds_v3_after_recorded_remote_effect(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    gateway = FakeGateway(_issue())
    created = create_github_scope(kind="initiative", title="Plan", parent_id=None, slug=None, gateway=gateway, **common)
    assert created.id == "init-00047"
    assert gateway.calls == 1
    metadata = json.loads((created.path / ".meta.json").read_text(encoding="utf-8"))
    assert metadata["backend"] == "github"
    assert metadata["schema_version"] == 3
    assert metadata["github"] == {"issue_number": 47, "repo_owner": "example", "repo_name": "repo"}
    operation = JournalStore(common["common_dir"]).load(created.operation_id)
    assert operation.terminal_status == "succeeded"
    assert operation.effects[0].remote_ref == "gh:example/repo#47"


def test_github_epic_and_issue_require_explicit_open_parent_chain(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    missing_parent_gateway = FakeGateway(_issue())
    with pytest.raises(ValueError, match="explicit parent"):
        create_github_scope(
            kind="epic", title="Plan", parent_id=None, slug=None, gateway=missing_parent_gateway, **common
        )
    assert missing_parent_gateway.calls == 0
    local_initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    epic = create_github_scope(
        kind="epic", title="Plan", parent_id=local_initiative.id, slug=None, gateway=FakeGateway(_issue()), **common
    )
    assert epic.id == "epic-00047"
    remote_issue = GithubIssueRecord(
        48,
        "example/repo",
        "Plan",
        "open",
        "open",
        None,
        "2026-09-24T00:00:00Z",
        "https://github.com/example/repo/issues/48",
    )
    issue = create_github_scope(
        kind="issue", title="Plan", parent_id=epic.id, slug=None, gateway=FakeGateway(remote_issue), **common
    )
    assert issue.id == "iss-00048"
    metadata = json.loads((issue.path / ".meta.json").read_text(encoding="utf-8"))
    assert metadata["parent_id"] == epic.id
    assert metadata["initiative_id"] == local_initiative.id
    assert metadata["epic_id"] == epic.id
    assert metadata["github"]["issue_number"] == 48


def test_closed_github_parent_is_rejected_before_remote_create(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    parent = create_github_scope(
        kind="initiative", title="Plan", parent_id=None, slug=None, gateway=FakeGateway(_issue()), **common
    )

    class ClosedParentGateway(FakeGateway):
        def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
            return GithubIssueRecord(
                number,
                repository,
                "Plan",
                "completed",
                "closed",
                "completed",
                "2026-09-24T00:00:00Z",
                f"https://github.com/{repository}/issues/{number}",
            )

    gateway = ClosedParentGateway(_issue())
    with pytest.raises(ValueError, match="not open"):
        create_github_scope(kind="epic", title="Plan", parent_id=parent.id, slug=None, gateway=gateway, **common)
    assert gateway.calls == 0
    assert JournalStore(common["common_dir"]).pending() == ()


def test_remote_only_success_keeps_receipt_when_local_destination_collides(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    destination = cast("Path", common["repo_root"]) / "spec-dock/initiatives/init-00047-plan"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("other owner\n", encoding="utf-8")
    gateway = FakeGateway(_issue())
    with pytest.raises(RuntimeError, match="Destination already exists"):
        create_github_scope(kind="initiative", title="Plan", parent_id=None, slug=None, gateway=gateway, **common)
    assert gateway.calls == 1
    assert destination.read_text(encoding="utf-8") == "other owner\n"
    pending = JournalStore(common["common_dir"]).pending()
    assert len(pending) == 1
    assert [effect.status for effect in pending[0].effects] == ["succeeded", "failed"]
    assert pending[0].effects[0].remote_ref == "gh:example/repo#47"


def test_github_create_refuses_duplicate_local_issue_link(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    create_github_scope(
        kind="initiative", title="Plan", parent_id=None, slug=None, gateway=FakeGateway(_issue()), **common
    )
    with pytest.raises(RuntimeError, match="already linked"):
        create_github_scope(
            kind="initiative",
            title="Other",
            parent_id=None,
            slug=None,
            gateway=FakeGateway(_issue(), expected_title="Other"),
            **common,
        )
    pending = JournalStore(common["common_dir"]).pending()
    assert len(pending) == 1
    assert [effect.status for effect in pending[0].effects] == ["succeeded", "failed"]


def test_import_existing_issue_uses_explicit_title_and_never_posts(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    gateway = FakeGateway(_issue())
    imported = import_github_scope(
        kind="initiative",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Local title",
        parent_id=None,
        slug=None,
        gateway=gateway,
        **common,
    )
    assert imported.id == "init-00047"
    assert gateway.calls == 0
    metadata = json.loads((imported.path / ".meta.json").read_text(encoding="utf-8"))
    assert metadata["title"] == "Local title"
    assert metadata["github"]["issue_number"] == 47
    assert JournalStore(common["common_dir"]).load(imported.operation_id).terminal_status == "succeeded"


def test_import_rejects_foreign_duplicate_and_missing_title_without_post(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    gateway = FakeGateway(_issue())
    with pytest.raises(ValueError, match="foreign"):
        import_github_scope(
            kind="initiative",
            github_ref="gh:other/repo#47",
            repo_hint=None,
            title="Plan",
            parent_id=None,
            slug=None,
            gateway=gateway,
            **common,
        )
    with pytest.raises(RuntimeError, match="title"):
        import_github_scope(
            kind="initiative",
            github_ref="gh:example/repo#47",
            repo_hint=None,
            title="",
            parent_id=None,
            slug=None,
            gateway=gateway,
            **common,
        )
    imported = import_github_scope(
        kind="initiative",
        github_ref="47",
        repo_hint="example/repo",
        title="Plan",
        parent_id=None,
        slug=None,
        gateway=gateway,
        **common,
    )
    with pytest.raises(ValueError, match="already linked"):
        import_github_scope(
            kind="initiative",
            github_ref="gh:example/repo#47",
            repo_hint=None,
            title="Again",
            parent_id=None,
            slug=None,
            gateway=gateway,
            **common,
        )
    assert imported.id == "init-00047"
    assert gateway.calls == 0


def test_import_epic_and_issue_with_explicit_parent_and_read_only_github(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    local_initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)

    class ExistingGateway(FakeGateway):
        def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
            if number == 47:
                return _issue()
            assert number == 48
            return GithubIssueRecord(
                48,
                repository,
                "Remote title",
                "open",
                "open",
                None,
                "2026-09-24T00:00:00Z",
                f"https://github.com/{repository}/issues/48",
            )

    gateway = ExistingGateway(_issue())
    epic = import_github_scope(
        kind="epic",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Local epic",
        parent_id=local_initiative.id,
        slug=None,
        gateway=gateway,
        **common,
    )
    issue = import_github_scope(
        kind="issue",
        github_ref="https://github.com/example/repo/issues/48",
        repo_hint=None,
        title="Local issue",
        parent_id=epic.id,
        slug=None,
        gateway=gateway,
        **common,
    )
    metadata = json.loads((issue.path / ".meta.json").read_text(encoding="utf-8"))
    assert issue.id == "iss-00048"
    assert metadata["initiative_id"] == local_initiative.id
    assert metadata["epic_id"] == epic.id
    assert metadata["title"] == "Local issue"
    assert gateway.calls == 0


def test_import_rejects_pull_request_before_local_write(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)

    class PullRequestGateway(FakeGateway):
        def get(self, repo_root: Path, repository: str, number: int) -> GithubIssueRecord:
            raise RemoteIssueError("GITHUB_PULL_REQUEST_REJECTED")

    gateway = PullRequestGateway(_issue())
    with pytest.raises(RemoteIssueError, match="PULL_REQUEST"):
        import_github_scope(
            kind="initiative",
            github_ref="gh:example/repo#47",
            repo_hint=None,
            title="Plan",
            parent_id=None,
            slug=None,
            gateway=gateway,
            **common,
        )
    assert gateway.calls == 0
    assert JournalStore(common["common_dir"]).pending() == ()
