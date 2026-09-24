"""Work start chooses one Scope without silently abandoning an open sibling."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application import work_lifecycle  # noqa: E402
from spec_dock_runtime.application.active_selection import select_scope  # noqa: E402
from spec_dock_runtime.application.branch_vnext import create_scope_branch  # noqa: E402
from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.application.work_lifecycle import plan_start_work, resume_start_work, start_work  # noqa: E402
from spec_dock_runtime.cli.admission import AdmissionError  # noqa: E402
from spec_dock_runtime.domain.dependency_vnext import ReadinessResult  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


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
            "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "fixture",
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
    assert subprocess.run(
        ["git", "branch", "--show-current"], cwd=repo_root, check=True, capture_output=True, text=True
    ).stdout.strip() == binding.name
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 1, initiative.id, epic.id, issue.id, issue.id
    )


def test_start_resumes_after_checkout_when_selection_publication_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root, check=True, capture_output=True,
    )
    arguments = {
        "repo_root": repo_root, "common_dir": repo_root / ".git", "worktree_id": "main",
        "engine_digest": "engine-a", "expected_epoch": 1,
    }
    saved = work_lifecycle.save_selection_v3

    def fail_once(*args: object, **kwargs: object) -> None:
        monkeypatch.setattr(work_lifecycle, "save_selection_v3", saved)
        raise OSError("injected active publication failure")

    monkeypatch.setattr(work_lifecycle, "save_selection_v3", fail_once)
    with pytest.raises(OSError, match="injected active publication failure"):
        start_work(target=issue.id, **arguments)
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
        cwd=repo_root, check=True, capture_output=True,
    )
    result = start_work(
        repo_root=repo_root, common_dir=repo_root / ".git", worktree_id="main",
        engine_digest="engine-a", expected_epoch=1, target=selected.id,
    )
    assert result.target_id == selected.id
    assert result.branch.startswith(selected.id + "-")
    assert load_selection_v3(specdock_dir, worktree_id="main")[0].focus_id == selected.id
    assert JournalStore(repo_root / ".git").pending() == ()


def test_dirty_start_has_no_branch_or_journal_effect(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    (repo_root / "untracked.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="clean working tree"):
        start_work(
            repo_root=repo_root, common_dir=repo_root / ".git", worktree_id="main",
            engine_digest="engine-a", expected_epoch=1, target=issue.id,
        )
    assert JournalStore(repo_root / ".git").pending() == ()


def test_detached_start_requires_explicit_base(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"],
        cwd=repo_root, check=True, capture_output=True,
    )
    subprocess.run(["git", "switch", "--detach", "HEAD"], cwd=repo_root, check=True, capture_output=True)
    arguments = {
        "repo_root": repo_root, "common_dir": repo_root / ".git", "worktree_id": "main",
        "engine_digest": "engine-a", "expected_epoch": 1, "target": issue.id,
    }
    with pytest.raises(ValueError, match="detached HEAD requires --base"):
        start_work(**arguments)
    assert JournalStore(repo_root / ".git").pending() == ()
    result = start_work(base="HEAD", **arguments)
    assert result.target_id == issue.id
