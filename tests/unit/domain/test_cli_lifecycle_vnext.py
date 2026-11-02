"""GitHub lifecycle observation and the selection-state invariant."""

import pytest

from spec_dock.runtime.domain.lifecycle import SelectionState, observe_github_state


@pytest.mark.parametrize(
    ("remote_state", "reason", "expected"),
    [
        ("OPEN", None, "open"),
        ("CLOSED", "completed", "completed"),
        ("CLOSED", "not_planned", "not-planned"),
        ("CLOSED", None, "unknown"),
        ("CLOSED", "duplicate", "unknown"),
        ("CLOSED", "future_reason", "unknown"),
        ("SOMETHING_ELSE", "completed", "unknown"),
    ],
)
def test_github_reason_never_infers_completion_from_closed_alone(
    remote_state: str, reason: str | None, expected: str
) -> None:
    assert observe_github_state(remote_state, reason) == expected


def test_selection_rejects_focus_that_does_not_match_chain() -> None:
    with pytest.raises(ValueError, match="focus"):
        SelectionState(
            worktree_id="wt:123",
            revision=2,
            initiative_id="init-local-00001",
            epic_id="epic-local-00002",
            issue_id=None,
            focus_id="init-local-00001",
        )
