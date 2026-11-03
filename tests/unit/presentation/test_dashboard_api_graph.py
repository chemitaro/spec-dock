"""The structure API fields the structure graph and the time axis lay out by (iss-00532 D-01, T-01)."""

from __future__ import annotations

from typing import Any

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document, scope_of


def _scopes(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in doc["scopes"]}


def test_blocked_by_lists_declared_prerequisites_inside_the_repository() -> None:
    structure = snapshot(
        node(1, "epic"),
        node(2, "issue", parent=1),
        node(3, "issue", parent=1, blocked_by=(2, 99, 3)),  # 99 is not a Scope; 3 is itself
        node(4, "issue", parent=1, blocked_by=(3, 2)),
    )
    scopes = _scopes(document(structure))
    assert scopes["iss-00003"]["blocked_by"] == ["iss-00002"]
    assert scopes["iss-00004"]["blocked_by"] == ["iss-00002", "iss-00003"]
    assert scopes["iss-00002"]["blocked_by"] == []


def test_stage_counts_sibling_order_for_all_and_open_children() -> None:
    structure = snapshot(
        node(1, "epic"),
        closed(2, "issue", parent=1),
        node(3, "issue", parent=1, blocked_by=(2,)),
        node(4, "issue", parent=1, blocked_by=(3,)),
        node(5, "issue", parent=1, blocked_by=(6,)),  # 5 and 6 wait for each other: no stage
        node(6, "issue", parent=1, blocked_by=(5,)),
        node(7, "epic"),
    )
    scopes = _scopes(document(structure))
    assert scopes["iss-00002"]["stage"] == {"all": 1, "open": None}
    assert scopes["iss-00003"]["stage"] == {"all": 2, "open": 1}
    assert scopes["iss-00004"]["stage"] == {"all": 3, "open": 2}
    assert scopes["iss-00005"]["stage"] == {"all": None, "open": None}
    assert scopes["epic-00001"]["stage"] == {"all": 1, "open": 1}  # top-level Scopes are siblings too
    assert scopes["epic-00007"]["stage"] == {"all": 1, "open": 1}


def test_rank_is_the_place_in_the_recommended_order() -> None:
    structure = snapshot(
        node(1, "epic"),
        node(2, "issue", parent=1),  # ready, nothing waits for it
        node(3, "issue", parent=1),  # ready, two wait for it: first
        node(4, "issue", parent=1, blocked_by=(3,)),
        node(5, "issue", parent=1, blocked_by=(4,)),
        node(6, "issue", parent=1, in_progress=True),  # doing comes before ready
    )
    scopes = _scopes(document(structure))
    order = sorted((item for item in scopes.values() if item["kind"] == "issue"), key=lambda item: item["rank"])
    assert [item["id"] for item in order][:3] == ["iss-00006", "iss-00003", "iss-00002"]
    assert sorted(item["rank"] for item in scopes.values()) == list(range(len(scopes)))


def test_assurance_and_branch_are_null_until_their_readers_exist() -> None:
    scopes = _scopes(document(snapshot(node(1, "epic"), node(2, "issue", parent=1))))
    for item in scopes.values():
        assert item["assurance"] is None
        assert item["branch"] is None


def test_weeks_by_kind_counts_each_kind_cumulatively_per_week() -> None:
    structure = snapshot(
        node(1, "epic", created_at="2026-10-20T10:00:00Z"),  # Tuesday of the week of 10-19
        closed(2, "issue", parent=1, created_at="2026-10-21T00:00:00Z", closed_at="2026-10-28T00:00:00Z"),
        node(3, "issue", parent=1, created_at="2026-10-27T00:00:00Z"),
    )
    weeks = document(structure)["timeline"]["weeks_by_kind"]
    assert weeks["initiative"] == []
    assert weeks["epic"] == [
        {"week_start": "2026-10-19", "created": 1, "closed": 0},
        {"week_start": "2026-10-26", "created": 1, "closed": 0},
        {"week_start": "2026-11-02", "created": 1, "closed": 0},
    ]
    assert weeks["issue"] == [
        {"week_start": "2026-10-19", "created": 1, "closed": 0},
        {"week_start": "2026-10-26", "created": 2, "closed": 1},
        {"week_start": "2026-11-02", "created": 2, "closed": 1},
    ]


def test_scope_document_adds_downstream_including_closed_scopes() -> None:
    structure = snapshot(
        node(1, "epic"),
        closed(2, "issue", parent=1),
        closed(3, "issue", parent=1, blocked_by=(2,)),
        node(4, "issue", parent=1, blocked_by=(3,)),
    )
    doc = scope_of(structure, "iss-00002")
    assert doc is not None
    assert doc["downstream"] == {"direct": [], "indirect": []}  # the open-only path stops at a closed Scope
    assert doc["downstream_all"] == {"direct": ["iss-00003"], "indirect": ["iss-00004"]}
    assert doc["scope"]["blocked_by"] == []
    assert doc["scope"]["stage"] == {"all": 1, "open": None}
