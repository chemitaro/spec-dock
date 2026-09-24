"""Scope delete plans only current-snapshot local changes."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.scope_delete_vnext import plan_scope_delete  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.registry_store import RegistryStore  # noqa: E402
from spec_dock_runtime.infra.writer_lock import WriterLock  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


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
