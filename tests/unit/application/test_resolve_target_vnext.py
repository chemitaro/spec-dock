"""A command resolves every target from one immutable selection snapshot."""

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.resolve_target import (  # noqa: E402
    ScopeSnapshot,
    WorktreeRecord,
    resolve_scope_targets,
    resolve_worktree_target,
)
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from spec_dock_runtime.domain.models import SpecNode  # noqa: E402
from spec_dock_runtime.domain.selectors import parse_scope_selector, parse_worktree_selector  # noqa: E402


def _node(kind: str, node_id: str, parent_id: str | None, number: int | None = None) -> SpecNode:
    path = Path("/project/spec-dock") / node_id
    return SpecNode(
        kind=kind,
        id=node_id,
        title=node_id,
        slug=node_id,
        path=path,
        meta_path=path / "meta.json",
        parent_id=parent_id,
        initiative_id="init-00001" if kind != "initiative" else None,
        epic_id="epic-00002" if kind == "issue" else None,
        github_issue_number=number,
        github_repo_owner="chemitaro" if number else None,
        github_repo_name="spec-dock" if number else None,
    )


def _snapshot(focus: str = "iss-00003") -> ScopeSnapshot:
    nodes = {
        "init-00001": _node("initiative", "init-00001", None, 1),
        "epic-00002": _node("epic", "epic-00002", "init-00001", 2),
        "iss-00003": _node("issue", "iss-00003", "epic-00002", 3),
    }
    if focus == "init-00001":
        selection = SelectionState("wt:one", 7, "init-00001", None, None, focus)
    else:
        selection = SelectionState("wt:one", 7, "init-00001", "epic-00002", "iss-00003", focus)
    return ScopeSnapshot(nodes, selection, ("chemitaro", "spec-dock"))


def test_multi_role_selectors_resolve_from_same_selection_snapshot() -> None:
    snapshot = _snapshot()
    targets = resolve_scope_targets(
        snapshot,
        {"target": parse_scope_selector("@current"), "parent": parse_scope_selector("@epic")},
        expected_current="iss-00003",
        require_current_guard=True,
    )
    assert targets["target"].id == "iss-00003"
    assert targets["parent"].id == "epic-00002"
    assert snapshot.selection.revision == 7


def test_current_guard_checks_focus_even_for_parent_role() -> None:
    with pytest.raises(ValueError, match="current"):
        resolve_scope_targets(
            _snapshot(),
            {"parent": parse_scope_selector("@epic")},
            expected_current="epic-00002",
            require_current_guard=True,
        )
    with pytest.raises(ValueError, match="expect-current"):
        resolve_scope_targets(
            _snapshot(),
            {"parent": parse_scope_selector("@epic")},
            require_current_guard=True,
        )


def test_empty_active_role_and_missing_id_are_not_found() -> None:
    snapshot = _snapshot("init-00001")
    with pytest.raises(LookupError):
        resolve_scope_targets(snapshot, {"target": parse_scope_selector("@issue")})
    with pytest.raises(LookupError):
        resolve_scope_targets(snapshot, {"target": parse_scope_selector("iss-99999")})


def test_snapshot_rejects_noncanonical_scope_id_before_target_resolution() -> None:
    snapshot = _snapshot()
    nodes = {**snapshot.nodes, "iss-3": _node("issue", "iss-3", "epic-00002")}
    with pytest.raises(ValueError, match="canonical"):
        ScopeSnapshot(nodes, snapshot.selection, snapshot.repository)


def test_github_ref_requires_current_repo_and_unique_imported_node() -> None:
    snapshot = _snapshot()
    found = resolve_scope_targets(snapshot, {"target": parse_scope_selector("gh:Chemitaro/Spec-Dock#3")})
    assert found["target"].id == "iss-00003"
    with pytest.raises(ValueError, match="foreign"):
        resolve_scope_targets(snapshot, {"target": parse_scope_selector("gh:other/spec-dock#3")})
    with pytest.raises(LookupError):
        resolve_scope_targets(snapshot, {"target": parse_scope_selector("gh:chemitaro/spec-dock#99")})
    duplicate = ScopeSnapshot(
        {**snapshot.nodes, "iss-00004": _node("issue", "iss-00004", "epic-00002", 3)},
        snapshot.selection,
        snapshot.repository,
    )
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_scope_targets(duplicate, {"target": parse_scope_selector("gh:chemitaro/spec-dock#3")})


def test_kind_and_parent_contract_are_checked_after_resolution() -> None:
    snapshot = _snapshot()
    with pytest.raises(ValueError, match="kind"):
        resolve_scope_targets(
            snapshot, {"target": parse_scope_selector("epic-00002")}, expected_kinds={"target": "issue"}
        )
    with pytest.raises(ValueError, match="parent"):
        resolve_scope_targets(
            snapshot, {"target": parse_scope_selector("iss-00003")}, expected_parents={"target": "init-00001"}
        )


def test_dynamic_selector_rejects_dangling_selection() -> None:
    snapshot = _snapshot()
    dangling = ScopeSnapshot(
        snapshot.nodes, SelectionState("wt:one", 8, "init-99999", None, None, "init-99999"), snapshot.repository
    )
    with pytest.raises(ValueError, match="selection"):
        resolve_scope_targets(dangling, {"target": parse_scope_selector("@current")})


def test_worktree_selector_is_limited_to_registered_identity(tmp_path: Path) -> None:
    registered = tmp_path / "registered"
    registered.mkdir()
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    records = (WorktreeRecord("planning-1", registered, "planning"),)
    assert resolve_worktree_target(records, parse_worktree_selector("wt:planning-1")).path == registered
    assert resolve_worktree_target(records, parse_worktree_selector("planning")).path == registered
    assert resolve_worktree_target(records, parse_worktree_selector(str(registered))).path == registered
    with pytest.raises(LookupError):
        resolve_worktree_target(records, parse_worktree_selector(str(foreign)))


def test_duplicate_worktree_alias_is_ambiguous(tmp_path: Path) -> None:
    one = tmp_path / "one"
    two = tmp_path / "two"
    one.mkdir()
    two.mkdir()
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_worktree_target(
            (WorktreeRecord("one", one, "planning"), WorktreeRecord("two", two, "planning")),
            parse_worktree_selector("planning"),
        )
