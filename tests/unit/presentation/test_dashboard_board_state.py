"""The ready-board state of an Issue: an explicit board_state (iss-00438) and unchanged legacy behavior."""

from __future__ import annotations

import itertools
from typing import Any

from spec_dock.runtime.presentation.markdown import _render_dashboard_md
from spec_dock.runtime.presentation.puml import _issue_ready_board_state, _render_tree_ready_board_puml


def _legacy_board_state(
    issue_id: str, issue_item: dict[str, Any], *, active_issue_id: str | None
) -> tuple[str, list[str]]:
    """A copy of the function before iss-00438; legacy inputs must keep this exact result."""
    status = str(issue_item.get("status") or "unknown").lower()
    deps = issue_item.get("deps")
    ready = False
    blockers_top: list[str] = []
    if isinstance(deps, dict):
        raw_ready = deps.get("ready")
        if isinstance(raw_ready, bool):
            ready = raw_ready
        raw_blockers_top = deps.get("blockers_top")
        if isinstance(raw_blockers_top, list):
            blockers_top = [str(dep_id) for dep_id in raw_blockers_top if isinstance(dep_id, str)]
    if status == "done":
        return ("DONE", [])
    if issue_id == active_issue_id:
        return ("DOING", blockers_top)
    if status == "unknown":
        return ("UNKNOWN", blockers_top)
    if ready:
        return ("READY", [])
    return ("BLOCKED", blockers_top)


def test_legacy_items_without_board_state_keep_the_previous_state() -> None:
    statuses = ("done", "todo", "doing", "unknown", None, "DONE")
    deps_values: tuple[object, ...] = (
        None,
        {"ready": True, "blockers_top": []},
        {"ready": False, "blockers_top": ["iss-00002", 3]},
        {"ready": "yes"},
    )
    for status, deps, active in itertools.product(statuses, deps_values, ("iss-00001", None)):
        item: dict[str, Any] = {"deps": deps}
        if status is not None:
            item["status"] = status
        assert _issue_ready_board_state("iss-00001", item, active_issue_id=active) == _legacy_board_state(
            "iss-00001", item, active_issue_id=active
        )


def test_board_state_decides_the_state_so_several_issues_can_be_doing() -> None:
    blocked = {"status": "open", "board_state": "BLOCKED", "deps": {"ready": False, "blockers_top": ["#7"]}}
    assert _issue_ready_board_state("iss-00001", blocked, active_issue_id=None) == ("BLOCKED", ["#7"])
    ready = {"status": "open", "board_state": "READY", "deps": {"ready": True, "blockers_top": ["x"]}}
    assert _issue_ready_board_state("iss-00001", ready, active_issue_id=None) == ("READY", [])
    unknown = {"status": "open", "board_state": "UNKNOWN", "deps": {"ready": True, "blockers_top": []}}
    assert _issue_ready_board_state("iss-00001", unknown, active_issue_id="iss-00001")[0] == "UNKNOWN"
    doing: dict[str, object] = {"type": "issue", "title": "一つ目", "status": "open", "board_state": "DOING"}
    nodes: dict[str, object] = {
        "iss-00001": doing,
        "iss-00002": {"type": "issue", "title": "二つ目", "status": "open", "board_state": "DOING"},
        "iss-00003": {"type": "issue", "title": "Closed", "status": "done", "board_state": "DONE"},
    }
    text = _render_dashboard_md(nodes, active=None)
    assert "- doing: 2" in text and "- `iss-00001` 一つ目\n- `iss-00002` 二つ目" in text
    tree = {
        "tree": [
            {
                "id": "init-00010",
                "title": "計画",
                "epics": [{"id": "epic-00011", "title": "核", "issues": [{**doing, "id": "iss-00001"}]}],
            }
        ]
    }
    assert 'rectangle "iss-00001\\n[DOING]" as Niss_00001 #DAE8FC' in _render_tree_ready_board_puml(
        tree, active=None, todo_only=True
    )
