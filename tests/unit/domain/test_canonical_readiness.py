"""Start readiness from a structure snapshot (iss-00431, used by work start and the dashboard)."""

from __future__ import annotations

from dataclasses import replace

import pytest

from spec_dock.runtime.domain.canonical_readiness import evaluate_all, evaluate_readiness
from spec_dock.runtime.domain.canonical_structure import (
    ExternalIssue,
    ScopeNode,
    StructureAnomaly,
    StructureSnapshot,
)

_PREFIX = {"initiative": "init", "epic": "epic", "issue": "iss"}


def node(number: int, kind: str, *, parent: int | None = None, **changes: object) -> ScopeNode:
    base = ScopeNode(
        number=number,
        database_id=1000 + number,
        id=f"{_PREFIX[kind]}-{number:05d}",
        kind=kind,  # type: ignore[arg-type]
        slug=f"s{number}",
        title=f"Scope {number}",
        state="open",
        state_reason=None,
        labels=(f"spec-dock:{kind}",),
        assignees=(),
        in_progress=False,
        parent=parent,
        sub_issues=(),
        blocked_by=(),
        blocking=(),
        updated_at="2026-10-26T00:00:00Z",
        url=f"https://github.com/o/r/issues/{number}",
        created_at="2026-10-25T00:00:00Z",
        closed_at=None,
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def snapshot(*nodes: ScopeNode, external: tuple[ExternalIssue, ...] = (), anomalies=()) -> StructureSnapshot:
    return StructureSnapshot(
        "github.com/o/r",
        "2026-10-26T00:00:00Z",
        "2026-10-26T00:00:00Z",
        {item.number: item for item in nodes},
        {item.number: item for item in external},
        tuple(anomalies),
        (),
    )


def tree(*extra: ScopeNode, issue: dict[str, object] | None = None, **options: object) -> StructureSnapshot:
    """Initiative 1 > Epic 2 > Issue 3, plus extra nodes."""
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "issue", parent=2, **(issue or {})),
        *extra,
        **options,  # type: ignore[arg-type]
    )


def test_an_open_scope_without_dependencies_is_ready() -> None:
    result = evaluate_readiness(tree(), "iss-00003")
    assert (result.state, result.ready, result.blockers, result.unknown) == ("READY", True, (), ())
    assert (result.scope_id, result.number) == ("iss-00003", 3)


def test_an_open_scope_prerequisite_blocks_and_names_the_scope() -> None:
    result = evaluate_readiness(tree(node(4, "issue", parent=2), issue={"blocked_by": (4,)}), "iss-00003")
    assert (result.state, result.ready) == ("BLOCKED", False)
    [blocker] = result.blockers
    assert (blocker.number, blocker.scope_id, blocker.role) == (4, "iss-00004", "prerequisite")
    assert (blocker.required_state, blocker.observed_state, blocker.declared_by) == ("completed", "open", "iss-00003")


def test_a_completed_prerequisite_passes_and_a_not_planned_one_blocks() -> None:
    done = node(4, "issue", parent=2, state="closed", state_reason="completed")
    assert evaluate_readiness(tree(done, issue={"blocked_by": (4,)}), "iss-00003").ready is True
    dropped = replace(done, state_reason="not_planned")
    result = evaluate_readiness(tree(dropped, issue={"blocked_by": (4,)}), "iss-00003")
    assert result.state == "BLOCKED" and result.blockers[0].observed_state == "not-planned"


def test_an_ancestor_dependency_is_inherited() -> None:
    nodes = (node(1, "initiative"), node(2, "epic", parent=1, blocked_by=(5,)), node(3, "issue", parent=2))
    result = evaluate_readiness(snapshot(*nodes, node(5, "initiative")), "iss-00003")
    assert result.state == "BLOCKED" and result.blockers[0].declared_by == "epic-00002"


def test_a_closed_ancestor_blocks() -> None:
    nodes = (node(1, "initiative", state="closed", state_reason="completed"), node(2, "epic", parent=1))
    result = evaluate_readiness(snapshot(*nodes, node(3, "issue", parent=2)), "iss-00003")
    assert result.state == "BLOCKED"
    assert [(item.number, item.role, item.required_state) for item in result.blockers] == [(1, "ancestor", "open")]


def test_an_open_non_scope_dependency_blocks_and_a_closed_one_does_not() -> None:
    blocked = tree(issue={"blocked_by": (17,)}, external=(ExternalIssue(17, "Upstream", "open"),))
    result = evaluate_readiness(blocked, "iss-00003")
    assert result.state == "BLOCKED"
    assert [(item.number, item.scope_id, item.role, item.required_state) for item in result.blockers] == [
        (17, None, "external", "closed")
    ]
    closed = tree(issue={"blocked_by": (17,)}, external=(ExternalIssue(17, "Upstream", "closed"),))
    assert evaluate_readiness(closed, "iss-00003").ready is True


def test_in_progress_is_doing_but_still_ready() -> None:
    result = evaluate_readiness(tree(issue={"in_progress": True}), "iss-00003")
    assert (result.state, result.ready, result.in_progress) == ("DOING", True, True)


def test_a_blocked_scope_in_progress_is_doing_and_not_ready() -> None:
    result = evaluate_readiness(
        tree(node(4, "issue", parent=2), issue={"in_progress": True, "blocked_by": (4,)}), "iss-00003"
    )
    assert (result.state, result.ready) == ("DOING", False)


@pytest.mark.parametrize("reason", ["completed", "not_planned"])
def test_a_closed_scope_is_done_whatever_the_reason(reason: str) -> None:
    result = evaluate_readiness(tree(issue={"state": "closed", "state_reason": reason}), "iss-00003")
    assert (result.state, result.ready) == ("DONE", False)
    assert [(item.role, item.required_state) for item in result.blockers] == [("self", "open")]


@pytest.mark.parametrize(
    ("number", "code"),
    [
        (3, "DEPENDENCY_FOREIGN_REPOSITORY"),
        (3, "SUB_ISSUE_FOREIGN_REPOSITORY"),
        (2, "PARENT_FOREIGN_REPOSITORY"),
        (1, "SLUG_MARKER_MISSING"),
    ],
)
def test_an_anomaly_on_the_scope_or_an_ancestor_is_unknown(number: int, code: str) -> None:
    result = evaluate_readiness(tree(anomalies=(StructureAnomaly(number, code, "x"),)), "iss-00003")
    assert (result.state, result.ready) == ("UNKNOWN", False)
    assert [(item.number, item.code) for item in result.unknown] == [(number, code)]


def test_a_dependency_missing_from_the_snapshot_is_unknown() -> None:
    result = evaluate_readiness(tree(issue={"blocked_by": (99,)}), "iss-00003")
    assert result.state == "UNKNOWN"
    assert [(item.number, item.code) for item in result.unknown] == [(99, "DEPENDENCY_NOT_IN_SNAPSHOT")]


def test_a_dependency_whose_id_is_undecided_reports_its_anomaly() -> None:
    broken = replace(node(4, "issue", parent=2), id=None, kind=None, slug=None)
    anomaly = StructureAnomaly(4, "SLUG_MARKER_MISSING", "no marker")
    result = evaluate_readiness(tree(broken, issue={"blocked_by": (4,)}, anomalies=(anomaly,)), "iss-00003")
    assert result.state == "UNKNOWN"
    assert [(item.number, item.scope_id, item.code) for item in result.unknown] == [(4, None, "SLUG_MARKER_MISSING")]


def test_unknown_outranks_doing_and_done_outranks_unknown() -> None:
    anomaly = (StructureAnomaly(3, "DEPENDENCY_FOREIGN_REPOSITORY", "x"),)
    assert evaluate_readiness(tree(issue={"in_progress": True}, anomalies=anomaly), "iss-00003").state == "UNKNOWN"
    closed: dict[str, object] = {"state": "closed", "state_reason": "completed"}
    assert evaluate_readiness(tree(issue=closed, anomalies=anomaly), "iss-00003").state == "DONE"


def test_a_non_scope_or_unknown_id_is_a_lookup_error() -> None:
    with pytest.raises(LookupError):
        evaluate_readiness(tree(), "iss-00099")
    with pytest.raises(LookupError):
        evaluate_readiness(tree(), "not-an-id")


def test_evaluate_all_covers_every_scope() -> None:
    results = evaluate_all(tree(node(4, "issue", parent=2), issue={"blocked_by": (4,)}))
    assert {key: value.state for key, value in results.items()} == {
        "init-00001": "READY",
        "epic-00002": "READY",
        "iss-00003": "BLOCKED",
        "iss-00004": "READY",
    }
