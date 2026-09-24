"""Finishing work closes one Scope and clears only its selected subtree."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[2] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.application.active_selection import select_scope  # noqa: E402
from spec_dock_runtime.application.work_lifecycle import plan_finish_work  # noqa: E402
from spec_dock_runtime.domain.lifecycle import SelectionState  # noqa: E402
from tests.cli_runtime.test_active_vnext import _three_scopes  # noqa: E402


def test_issue_finish_preserves_selected_epic_and_initiative(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(
        views,
        target=issue.id,
        statuses={issue.id: "open"},
        selection=selected,
    )
    assert plan.target_id == issue.id
    assert plan.completion.after == "completed"
    assert plan.selection_after == SelectionState("main", 2, initiative.id, epic.id, None, epic.id)


def test_epic_finish_requires_completed_child_then_preserves_initiative(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(
        views,
        target=epic.id,
        statuses={epic.id: "open", issue.id: "completed"},
        selection=selected,
    )
    assert plan.target_id == epic.id
    assert plan.selection_after == SelectionState("main", 2, initiative.id, None, None, initiative.id)


def test_parent_finish_rejects_unfinished_descendant_before_selection_change(tmp_path: Path) -> None:
    _root, views, initiative, epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, issue.id, current=SelectionState("main", 0, None, None, None, None))
    with pytest.raises(ValueError, match="DESCENDANT_NOT_COMPLETED"):
        plan_finish_work(
            views,
            target=initiative.id,
            statuses={initiative.id: "open", epic.id: "completed", issue.id: "open"},
            selection=selected,
        )
    assert selected.focus_id == issue.id


def test_explicit_finish_outside_selected_chain_does_not_clear_selection(tmp_path: Path) -> None:
    _root, views, initiative, _epic, issue = _three_scopes(tmp_path)
    selected = select_scope(views, initiative.id, current=SelectionState("main", 0, None, None, None, None))
    plan = plan_finish_work(views, target=issue.id, statuses={issue.id: "open"}, selection=selected)
    assert plan.target_id == issue.id
    assert plan.selection_after == selected
