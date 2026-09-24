"""Active selection changes are local CAS operations independent of lifecycle."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import cast

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.active_selection import (  # noqa: E402
    change_active_selection,
    clear_selection,
    select_scope,
)
from spec_dock_runtime.application.create_local_scope import AncestorState, create_local_scope  # noqa: E402
from spec_dock_runtime.application.scope_query import load_scope_views  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.infra.active_store import load_selection_v3, save_selection_v3  # noqa: E402
from tests.cli_runtime.test_scope_github_vnext import _ready_repo  # noqa: E402


def _three_scopes(tmp_path: Path):
    common = _ready_repo(tmp_path)
    initiative = create_local_scope(kind="initiative", title="Init", parent=None, ancestors=(), **common)
    init_state = AncestorState(initiative.id, "initiative", "local", "open", False)
    epic = create_local_scope(kind="epic", title="Epic", parent=init_state, ancestors=(), **common)
    epic_state = AncestorState(epic.id, "epic", "local", "open", False, initiative.id)
    issue = create_local_scope(kind="issue", title="Issue", parent=epic_state, ancestors=(init_state,), **common)
    specdock_dir = cast("Path", common["repo_root"]) / "spec-dock"
    return specdock_dir, load_scope_views(specdock_dir), initiative, epic, issue


def test_select_each_scope_builds_exact_chain_and_same_target_is_noop(tmp_path: Path) -> None:
    _specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    empty = SelectionState("main", 0, None, None, None, None)
    selected_initiative = select_scope(views, initiative.id, current=empty)
    assert selected_initiative == SelectionState("main", 1, initiative.id, None, None, initiative.id)
    selected_epic = select_scope(views, epic.id, current=selected_initiative)
    assert selected_epic == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)
    selected_issue = select_scope(views, issue.id, current=selected_epic)
    assert selected_issue == SelectionState("main", 3, initiative.id, epic.id, issue.id, issue.id)
    assert select_scope(views, issue.id, current=selected_issue) == selected_issue


def test_clear_from_scope_preserves_ancestors_and_nonmember_is_noop(tmp_path: Path) -> None:
    _specdock_dir, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    cleared_issue = clear_selection(views, current=selected, from_target=issue.id)
    assert cleared_issue == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)
    cleared_epic = clear_selection(views, current=cleared_issue, from_target=epic.id)
    assert cleared_epic == SelectionState("main", 3, initiative.id, None, None, initiative.id)
    assert clear_selection(views, current=cleared_epic, from_target=issue.id) == cleared_epic
    assert clear_selection(views, current=cleared_epic, all_scopes=True) == SelectionState(
        "main", 4, None, None, None, None
    )
    with pytest.raises(LookupError, match="Scope was not found"):
        clear_selection(views, current=selected, from_target="iss-local-99999")


def test_selection_store_checks_revision_and_identity(tmp_path: Path) -> None:
    specdock_dir, views, _initiative, _epic, issue = _three_scopes(tmp_path)
    empty, identity = load_selection_v3(specdock_dir, worktree_id="main")
    assert empty == SelectionState("main", 0, None, None, None, None)
    assert identity is None
    selected = select_scope(views, issue.id, current=empty)
    save_selection_v3(specdock_dir, selected, views=views, expected_identity=identity)
    loaded, new_identity = load_selection_v3(specdock_dir, worktree_id="main")
    assert loaded == selected
    assert new_identity is not None
    with pytest.raises(FileExistsError):
        save_selection_v3(specdock_dir, selected, views=views, expected_identity=None)
    cleared = clear_selection(views, current=selected, all_scopes=True)
    save_selection_v3(specdock_dir, cleared, views=views, expected_identity=new_identity)
    assert load_selection_v3(specdock_dir, worktree_id="main")[0] == cleared


def test_active_change_is_independent_of_scope_metadata_and_noop_does_not_write(tmp_path: Path) -> None:
    specdock_dir, _views, _initiative, _epic, issue = _three_scopes(tmp_path)
    common = {
        "repo_root": specdock_dir.parent,
        "common_dir": (specdock_dir.parent / ".git").resolve(),
        "worktree_id": "main",
        "engine_digest": "engine-a",
        "expected_epoch": 1,
    }
    before_meta = (issue.path / ".meta.json").read_bytes()
    first = change_active_selection(target=issue.id, **common)
    assert first.changed and first.selection.focus_id == issue.id
    active_path = specdock_dir / ".agent" / "active.json"
    first_bytes = active_path.read_bytes()
    second = change_active_selection(target=issue.id, **common)
    assert not second.changed
    assert active_path.read_bytes() == first_bytes
    assert (issue.path / ".meta.json").read_bytes() == before_meta
    cleared = change_active_selection(clear_all=True, **common)
    assert cleared.changed and cleared.selection.focus_id is None
