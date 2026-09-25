"""Work start chooses one Scope without silently abandoning an open sibling."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import stat
import subprocess
import sys
from typing import TYPE_CHECKING, cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application import work_lifecycle  # noqa: E402
from spec_dock_runtime.application.active_selection import select_scope  # noqa: E402
from spec_dock_runtime.application.branch_vnext import create_scope_branch  # noqa: E402
from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.import_github_scope import import_github_scope  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.application.work_lifecycle import (  # noqa: E402
    plan_start_work,
    preview_start_work,
    resume_start_work,
    start_work,
)
from spec_dock_runtime.cli.admission import AdmissionError  # noqa: E402
from spec_dock_runtime.domain.dependency_vnext import ReadinessResult  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo  # noqa: E402

if TYPE_CHECKING:
    from spec_dock_runtime.domain.operation import OperationRecord
    from spec_dock_runtime.infra.contracts import GithubIssueRecord


def _commit_fixture(repo_root: Path, message: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", message],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _set_fixture_dependencies(meta_path: Path, targets: list[str]) -> None:
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    payload["depends_on"] = targets
    payload["revision"] += 1
    mode = stat.S_IMODE(meta_path.stat().st_mode)
    meta_path.chmod(mode | stat.S_IWUSR)
    try:
        meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        meta_path.chmod(mode)


def test_starting_open_sibling_requires_explicit_switch_active(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    other = create_local_scope(
        kind="issue",
        title="Other",
        parent=AncestorState(epic.id, "epic", "local", "open", False, initiative.id),
        ancestors=(AncestorState(initiative.id, "initiative", "local", "open", False),),
        repo_root=specdock_dir.parent,
        common_dir=specdock_dir.parent / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        updated_at="2026-09-25T00:00:00Z",
    )
    views = load_scope_views(specdock_dir)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    readiness = ReadinessResult(other.id, True, (), False)
    with pytest.raises(ValueError, match="SWITCH_ACTIVE_REQUIRED"):
        plan_start_work(
            views,
            target=other.id,
            selection=selected,
            current_state="open",
            readiness=readiness,
            switch_active=False,
        )
    allowed = plan_start_work(
        views,
        target=other.id,
        selection=selected,
        current_state="open",
        readiness=readiness,
        switch_active=True,
    )
    assert allowed.target_id == other.id
    assert allowed.selection_after == SelectionState("main", 2, initiative.id, epic.id, other.id, other.id)


def test_start_within_same_ancestry_needs_no_switch_flag(tmp_path: Path) -> None:
    _specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    upward = plan_start_work(
        views,
        target=epic.id,
        selection=selected,
        current_state="open",
        readiness=ReadinessResult(epic.id, True, (), False),
        switch_active=False,
    )
    assert upward.selection_after == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)
    downward = plan_start_work(
        views,
        target=issue.id,
        selection=upward.selection_after,
        current_state="open",
        readiness=ReadinessResult(issue.id, True, (), False),
        switch_active=False,
    )
    assert downward.selection_after == SelectionState("main", 3, initiative.id, epic.id, issue.id, issue.id)


def test_start_checks_out_registered_issue_branch_and_selects_issue(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    binding = create_scope_branch(scope_id=issue.id, base="HEAD", name=None, **arguments)
    with pytest.raises(ValueError, match="--base is valid only"):
        start_work(target=issue.id, base="HEAD", **arguments)
    result = start_work(target=issue.id, **arguments)
    assert result.target_id == issue.id and result.branch == binding.name
    assert (
        subprocess.run(
            ["git", "branch", "--show-current"], cwd=repo_root, check=True, capture_output=True, text=True
        ).stdout.strip()
        == binding.name
    )
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 1, initiative.id, epic.id, issue.id, issue.id
    )


def test_start_resumes_after_checkout_when_selection_publication_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    saved = work_lifecycle.save_selection_v3

    def fail_once(*args: object, **kwargs: object) -> None:
        monkeypatch.setattr(work_lifecycle, "save_selection_v3", saved)
        raise OSError("injected active publication failure")

    monkeypatch.setattr(work_lifecycle, "save_selection_v3", fail_once)
    with pytest.raises(OSError, match="injected active publication failure"):
        start_work(target=issue.id, base="HEAD", **arguments)
    pending = JournalStore(repo_root / ".git").pending()
    assert len(pending) == 1 and pending[0].command == "work.start"
    with pytest.raises(AdmissionError, match="pending blocking journal"):
        # The normal entrypoint must not silently recover an existing pending operation.
        start_work(target=issue.id, **arguments)
    result = resume_start_work(operation_id=pending[0].operation_id, **arguments)
    assert result.target_id == issue.id
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 1, initiative.id, epic.id, issue.id, issue.id
    )
    assert JournalStore(repo_root / ".git").pending() == ()


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_start_creates_canonical_branch_for_each_local_scope(tmp_path: Path, kind: str) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = {"initiative": initiative, "epic": epic, "issue": issue}[kind]
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    result = start_work(
        repo_root=repo_root,
        common_dir=repo_root / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        target=selected.id,
        base="HEAD",
    )
    assert result.target_id == selected.id
    assert result.branch.startswith(selected.id + "-")
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == selected.id
    assert JournalStore(repo_root / ".git").pending() == ()
    journal = JournalStore(repo_root / ".git")
    operations = tuple(
        operation
        for path in journal.root.iterdir()
        if (operation := journal.load(path.name)).command in {"branch.create", "work.start"}
    )
    assert len(operations) == 1
    assert operations[0].command == "work.start"
    assert operations[0].effect_plan == ("git-branch", "registry-bind", "checkout", "selection-set")


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_new_start_resumes_after_branch_ref_before_registry_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = {"initiative": initiative, "epic": epic, "issue": issue}[kind]
    repo_root = specdock_dir.parent
    _commit_fixture(repo_root, "fixture")
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    original = RegistryStore.bind_locked

    def stopped(self: RegistryStore, binding: object) -> object:
        raise RuntimeError("binding stopped")

    monkeypatch.setattr(RegistryStore, "bind_locked", stopped)
    with pytest.raises(RuntimeError, match="binding stopped"):
        start_work(target=selected.id, base="HEAD", **arguments)
    pending = JournalStore(repo_root / ".git").pending()
    assert len(pending) == 1 and pending[0].command == "work.start"
    assert pending[0].effect_plan == ("git-branch", "registry-bind", "checkout", "selection-set")
    monkeypatch.setattr(RegistryStore, "bind_locked", original)
    resumed = resume_start_work(operation_id=pending[0].operation_id, **arguments)
    assert resumed.target_id == selected.id and resumed.branch_created
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == selected.id
    assert JournalStore(repo_root / ".git").pending() == ()


def test_new_start_resumes_after_registry_binding_before_effect_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    _commit_fixture(repo_root, "fixture")
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    original = JournalStore.update

    def stopped(self: JournalStore, record: OperationRecord, *, expected_sequence: int) -> None:
        if record.effects and record.effects[-1].id == "registry-bind" and record.effects[-1].status == "succeeded":
            raise RuntimeError("binding result stopped")
        original(self, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", stopped)
    with pytest.raises(RuntimeError, match="binding result stopped"):
        start_work(target=issue.id, base="HEAD", **arguments)
    pending = JournalStore(repo_root / ".git").pending()
    assert len(pending) == 1 and pending[0].command == "work.start"
    assert pending[0].effects[-1].id == "registry-bind" and pending[0].effects[-1].status == "intent"
    monkeypatch.setattr(JournalStore, "update", original)
    resumed = resume_start_work(operation_id=pending[0].operation_id, **arguments)
    assert resumed.target_id == issue.id and resumed.branch_created
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == issue.id


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
def test_new_work_start_requires_explicit_base_before_any_write(tmp_path: Path, kind: str) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = {"initiative": initiative, "epic": epic, "issue": issue}[kind]
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "target": selected.id,
    }
    before_branches = subprocess.run(["git", "branch", "--list"], cwd=repo_root, check=True, capture_output=True).stdout
    for execute in (preview_start_work, start_work):
        with pytest.raises(ValueError, match="new work start requires --base"):
            execute(**arguments)
    assert (
        subprocess.run(["git", "branch", "--list"], cwd=repo_root, check=True, capture_output=True).stdout
        == before_branches
    )
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id is None
    assert JournalStore(repo_root / ".git").pending() == ()


def test_dirty_start_has_no_branch_or_journal_effect(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    (repo_root / "untracked.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="clean working tree"):
        start_work(
            repo_root=repo_root,
            common_dir=repo_root / ".git",
            worktree_id="main",
            engine_digest="engine-a",
            expected_epoch=1,
            target=issue.id,
        )
    assert JournalStore(repo_root / ".git").pending() == ()


def test_detached_start_requires_explicit_base(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "switch", "--detach", "HEAD"], cwd=repo_root, check=True, capture_output=True)
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "target": issue.id,
    }
    with pytest.raises(ValueError, match="new work start requires --base"):
        start_work(**arguments)
    assert JournalStore(repo_root / ".git").pending() == ()
    result = start_work(base="HEAD", **arguments)
    assert result.target_id == issue.id


def test_new_start_rejects_unready_base_before_branch_creation_or_checkout(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    other = create_local_scope(
        kind="issue",
        title="Prerequisite",
        parent=AncestorState(epic.id, "epic", "local", "open", False, initiative.id),
        ancestors=(AncestorState(initiative.id, "initiative", "local", "open", False),),
        repo_root=repo_root,
        common_dir=repo_root / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        updated_at="2026-09-25T00:00:00Z",
    )
    _commit_fixture(repo_root, "ready graph")
    meta_path = issue.path / ".meta.json"
    _set_fixture_dependencies(meta_path, [other.id])
    unready_base = _commit_fixture(repo_root, "unready graph")
    _set_fixture_dependencies(meta_path, [])
    current_head = _commit_fixture(repo_root, "ready current graph")
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
        "target": issue.id,
        "base": unready_base,
    }
    for execute in (preview_start_work, start_work):
        with pytest.raises(ValueError, match="START_NOT_READY"):
            execute(**arguments)
        assert (
            subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True
            ).stdout.strip()
            == current_head
        )
    assert (
        subprocess.run(
            ["git", "branch", "--list", f"{issue.id}-*"], cwd=repo_root, check=True, capture_output=True, text=True
        ).stdout.strip()
        == ""
    )
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id is None
    assert JournalStore(repo_root / ".git").pending() == ()


def test_registered_start_uses_ready_branch_instead_of_unready_current_graph(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    other = create_local_scope(
        kind="issue",
        title="Prerequisite",
        parent=AncestorState(epic.id, "epic", "local", "open", False, initiative.id),
        ancestors=(AncestorState(initiative.id, "initiative", "local", "open", False),),
        repo_root=repo_root,
        common_dir=repo_root / ".git",
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        updated_at="2026-09-25T00:00:00Z",
    )
    _commit_fixture(repo_root, "ready branch graph")
    arguments = {
        "repo_root": repo_root,
        "common_dir": repo_root / ".git",
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    binding = create_scope_branch(scope_id=issue.id, base="HEAD", name=None, **arguments)
    _set_fixture_dependencies(issue.path / ".meta.json", [other.id])
    _commit_fixture(repo_root, "unready current graph")
    preview = preview_start_work(target=issue.id, **arguments)
    assert preview.branch == binding.name and not preview.branch_creation
    result = start_work(target=issue.id, **arguments)
    assert result.branch == binding.name
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == issue.id


def test_start_snapshot_queries_github_from_real_repository(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    local = create_local_scope(kind="initiative", title="Local", parent=None, ancestors=(), **common)
    imported = import_github_scope(
        kind="initiative",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Remote prerequisite",
        parent_id=None,
        slug=None,
        gateway=FakeGateway(_issue()),
        **common,
    )
    _set_fixture_dependencies(local.path / ".meta.json", [imported.id])
    _commit_fixture(repo_root, "remote prerequisite")

    class CompletedGateway:
        calls = 0

        def get(self, observed_root: Path, repository: str, number: int) -> GithubIssueRecord:
            self.calls += 1
            assert observed_root == repo_root
            assert repository == "example/repo" and number == 47
            return replace(_issue(), state="completed", raw_state="closed", state_reason="completed")

    gateway = CompletedGateway()
    arguments = {
        "repo_root": repo_root,
        "common_dir": common["common_dir"],
        "worktree_id": common["worktree_id"],
        "engine_digest": common["engine_digest"],
        "expected_epoch": common["expected_epoch"],
        "target": local.id,
        "base": "HEAD",
        "source": "github",
        "gateway": gateway,
    }
    assert preview_start_work(**arguments).target_id == local.id
    assert start_work(**arguments).target_id == local.id
    assert gateway.calls >= 3


def test_offline_cache_start_never_queries_current_github_focus(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    repo_root = cast("Path", common["repo_root"])
    local = create_local_scope(kind="initiative", title="Local", parent=None, ancestors=(), **common)
    imported = import_github_scope(
        kind="initiative",
        github_ref="gh:example/repo#47",
        repo_hint=None,
        title="Remote focus",
        parent_id=None,
        slug=None,
        gateway=FakeGateway(_issue()),
        **common,
    )
    workspace = repo_root / "spec-dock"
    views = load_scope_views(workspace)
    current, identity = load_selection_v3(workspace, worktree_id="main")
    save_selection_v3(
        workspace, select_scope(views, imported.id, current=current), views=views, expected_identity=identity
    )
    _commit_fixture(repo_root, "offline cache start")

    class ForbiddenGateway:
        def get(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("offline start contacted GitHub")

    preview = preview_start_work(
        repo_root=repo_root,
        common_dir=cast("Path", common["common_dir"]),
        worktree_id="main",
        engine_digest="engine-a",
        expected_epoch=1,
        target=local.id,
        base="HEAD",
        source="cache",
        allow_stale=True,
        offline=True,
        switch_active=True,
        gateway=ForbiddenGateway(),
    )
    assert preview.target_id == local.id
