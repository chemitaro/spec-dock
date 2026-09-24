"""Scope delete plans only current-snapshot local changes."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.active_selection import select_scope  # noqa: E402
from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.import_github_scope import import_github_scope  # noqa: E402
from spec_dock_runtime.application.scope_delete_vnext import (  # noqa: E402
    delete_scope,
    plan_scope_delete,
    resume_scope_delete,
)
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3  # noqa: E402
from spec_dock_runtime.infra.json_store import atomic_write_json, read_guarded_json  # noqa: E402
from spec_dock_runtime.infra.operation_journal import JournalStore  # noqa: E402
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402
from spec_dock_runtime.infra.writer_lock import WriterLock  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import FakeGateway, _issue, _ready_repo  # noqa: E402


def test_delete_requires_explicit_recursive_active_and_dependency_choices(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    active = SelectionState("main", 1, initiative.id, epic.id, issue.id, issue.id)
    edges = {initiative.id: (), epic.id: (), issue.id: ()}
    with pytest.raises(ValueError, match="RECURSIVE_REQUIRED"):
        plan_scope_delete(views, target=epic.id, selection=active, dependencies=edges)
    with pytest.raises(ValueError, match="CLEAR_ACTIVE_REQUIRED"):
        plan_scope_delete(views, target=epic.id, selection=active, dependencies=edges, recursive=True)
    ready = plan_scope_delete(
        views, target=epic.id, selection=active, dependencies=edges,
        recursive=True, clear_active=True,
    )
    assert set(ready.deleted_ids) == {epic.id, issue.id}
    assert ready.selection_after == SelectionState("main", 2, initiative.id, None, None, initiative.id)


def test_delete_boundary_dependency_requires_explicit_detach(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    sibling = create_local_scope(
        kind="issue", title="Sibling",
        parent=AncestorState(epic.id, "epic", "local", "open", False, initiative.id),
        ancestors=(AncestorState(initiative.id, "initiative", "local", "open", False),),
        repo_root=specdock_dir.parent, common_dir=specdock_dir.parent / ".git",
        worktree_id="main", engine_digest="engine-a", expected_epoch=1,
        updated_at="2026-09-25T00:00:00Z",
    )
    views = load_scope_views(specdock_dir)
    active = SelectionState("main", 0, None, None, None, None)
    edges = {initiative.id: (), epic.id: (), issue.id: (), sibling.id: (issue.id,)}
    with pytest.raises(ValueError, match="DETACH_DEPENDENCIES_REQUIRED"):
        plan_scope_delete(views, target=issue.id, selection=active, dependencies=edges)
    plan = plan_scope_delete(
        views, target=issue.id, selection=active, dependencies=edges, detach_dependencies=True
    )
    assert plan.boundary_edges == ((sibling.id, issue.id),)
    assert plan.survivor_dependencies == {sibling.id: ()}
    assert plan.selection_after == active


def test_deleted_scope_ids_remain_reserved_in_shared_registry(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, epic, issue = _three_scopes(tmp_path)
    common_dir = specdock_dir.parent / ".git"
    registry = RegistryStore(common_dir)
    with WriterLock(common_dir):
        updated = registry.mark_deleted_locked((epic.id, issue.id))
    assert updated.deleted_ids == frozenset((epic.id, issue.id))
    assert registry.load()[0].deleted_ids == updated.deleted_ids
    with WriterLock(common_dir):
        assert registry.mark_deleted_locked((issue.id, epic.id)) == updated


def test_import_does_not_reuse_deleted_github_scope_id(tmp_path: Path) -> None:
    common = _ready_repo(tmp_path)
    common_dir = common["common_dir"]
    assert isinstance(common_dir, Path)
    with WriterLock(common_dir):
        RegistryStore(common_dir).mark_deleted_locked(("init-00047",))
    gateway = FakeGateway(_issue())
    with pytest.raises(ValueError, match="deleted Scope ID"):
        import_github_scope(
            kind="initiative", github_ref="gh:example/repo#47", repo_hint=None,
            title="Imported", parent_id=None, slug=None, gateway=gateway, **common,
        )
    assert JournalStore(common_dir).pending() == ()


def test_delete_quarantines_only_target_tree_and_keeps_branch_binding(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    before_parent = (epic.path / ".meta.json").read_bytes()
    result = delete_scope(
        repo_root=repo_root, common_dir=repo_root / ".git", worktree_id="main",
        engine_digest="engine-a", expected_epoch=1, target=issue.id,
    )
    assert result.deleted_ids == (issue.id,)
    assert not issue.path.exists()
    assert result.quarantine_path.is_dir()
    assert (result.quarantine_path / ".meta.json").is_file()
    assert (epic.path / ".meta.json").read_bytes() == before_parent
    assert RegistryStore(repo_root / ".git").load()[0].deleted_ids == frozenset((issue.id,))
    assert JournalStore(repo_root / ".git").pending() == ()


def test_delete_detaches_survivor_dependency_and_clears_selected_issue(tmp_path: Path) -> None:
    specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    sibling = create_local_scope(
        kind="issue", title="Sibling",
        parent=AncestorState(epic.id, "epic", "local", "open", False, initiative.id),
        ancestors=(AncestorState(initiative.id, "initiative", "local", "open", False),),
        repo_root=specdock_dir.parent, common_dir=specdock_dir.parent / ".git",
        worktree_id="main", engine_digest="engine-a", expected_epoch=1,
        updated_at="2026-09-25T00:00:00Z",
    )
    loaded = read_guarded_json(sibling.path / ".meta.json")
    assert loaded is not None and isinstance(loaded[0], dict)
    payload = dict(loaded[0])
    payload["depends_on"] = [issue.id]
    payload["revision"] = payload["revision"] + 1
    atomic_write_json(sibling.path / ".meta.json", payload, expected_identity=loaded[1])
    views = load_scope_views(specdock_dir)
    selection = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    save_selection_v3(specdock_dir, selection, views=views, expected_identity=None)
    result = delete_scope(
        repo_root=specdock_dir.parent, common_dir=specdock_dir.parent / ".git", worktree_id="main",
        engine_digest="engine-a", expected_epoch=1, target=issue.id,
        clear_active=True, detach_dependencies=True,
    )
    assert result.deleted_ids == (issue.id,)
    remaining = read_guarded_json(sibling.path / ".meta.json")
    assert remaining is not None and remaining[0]["depends_on"] == []
    assert remaining[0]["revision"] == payload["revision"] + 1
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == SelectionState(
        "main", 2, initiative.id, epic.id, None, epic.id
    )


def test_delete_resumes_after_tree_move_before_journal_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    arguments = {
        "repo_root": repo_root, "common_dir": repo_root / ".git", "worktree_id": "main",
        "engine_digest": "engine-a", "expected_epoch": 1,
    }
    original = JournalStore.update

    def fail_after_move(store: JournalStore, record: object, *, expected_sequence: int) -> None:
        if record.command == "scope.delete" and any(
            effect.id == "quarantine-move" and effect.status == "succeeded" for effect in record.effects
        ):
            monkeypatch.setattr(JournalStore, "update", original)
            raise OSError("injected journal failure after tree move")
        original(store, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_after_move)
    with pytest.raises(OSError, match="after tree move"):
        delete_scope(target=issue.id, **arguments)
    pending = JournalStore(repo_root / ".git").pending()
    assert len(pending) == 1 and pending[0].effects[2].status == "intent"
    assert not issue.path.exists()
    result = resume_scope_delete(operation_id=pending[0].operation_id, **arguments)
    assert result.quarantine_path.is_dir()
    assert RegistryStore(repo_root / ".git").load()[0].deleted_ids == frozenset((issue.id,))
    assert JournalStore(repo_root / ".git").pending() == ()


def test_recursive_delete_moves_subtree_and_retains_all_ids(tmp_path: Path) -> None:
    specdock_dir, _views, initiative, epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    with pytest.raises(ValueError, match="RECURSIVE_REQUIRED"):
        delete_scope(
            repo_root=repo_root, common_dir=repo_root / ".git", worktree_id="main",
            engine_digest="engine-a", expected_epoch=1, target=initiative.id,
        )
    assert initiative.path.exists()
    assert JournalStore(repo_root / ".git").pending() == ()
    result = delete_scope(
        repo_root=repo_root, common_dir=repo_root / ".git", worktree_id="main",
        engine_digest="engine-a", expected_epoch=1, target=initiative.id,
        recursive=True,
    )
    assert set(result.deleted_ids) == {initiative.id, epic.id, issue.id}
    assert not initiative.path.exists()
    assert (result.quarantine_path / "epics").is_dir()
    assert RegistryStore(repo_root / ".git").load()[0].deleted_ids == frozenset(result.deleted_ids)


def test_delete_recovery_rejects_quarantine_identity_replacement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    repo_root = specdock_dir.parent
    arguments = {
        "repo_root": repo_root, "common_dir": repo_root / ".git", "worktree_id": "main",
        "engine_digest": "engine-a", "expected_epoch": 1,
    }
    original = JournalStore.update

    def fail_after_move(store: JournalStore, record: object, *, expected_sequence: int) -> None:
        if record.command == "scope.delete" and any(
            effect.id == "quarantine-move" and effect.status == "succeeded" for effect in record.effects
        ):
            monkeypatch.setattr(JournalStore, "update", original)
            raise OSError("injected journal failure after tree move")
        original(store, record, expected_sequence=expected_sequence)

    monkeypatch.setattr(JournalStore, "update", fail_after_move)
    with pytest.raises(OSError, match="after tree move"):
        delete_scope(target=issue.id, **arguments)
    pending = JournalStore(repo_root / ".git").pending()
    fixed = dict(pending[0].fixed_targets)
    quarantine = repo_root / fixed["quarantine_path"]
    quarantine.rename(quarantine.with_name("owned-original"))
    quarantine.mkdir()
    with pytest.raises(ValueError, match="quarantine differs"):
        resume_scope_delete(operation_id=pending[0].operation_id, **arguments)
    assert quarantine.is_dir()
    assert JournalStore(repo_root / ".git").pending() == pending
