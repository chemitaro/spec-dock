"""The summary contract specdock.dashboard-summary/v1 (iss-00528, epic-00427 D-05)."""

from __future__ import annotations

import json

import pytest

from spec_dock.runtime.domain.canonical_structure import StructureAnomaly
from spec_dock.runtime.domain.dashboard_model import build_model
from spec_dock.runtime.presentation.dashboard_summary import SUMMARY_SCHEMA, summary_document, summary_text
from tests.support.dashboard import NOW, closed, node, pr, prs, snapshot


def structure():
    return snapshot(
        node(1, "initiative"),
        node(2, "epic", parent=1),
        node(3, "issue", parent=2, in_progress=True, title="Merge me"),
        node(4, "issue", parent=2, in_progress=True),
        node(5, "issue", parent=2),
        node(6, "issue", parent=2, blocked_by=(5,)),
        closed(7, "issue", parent=2),
        closed(8, "epic", parent=1),
        node(9, "issue", parent=8),
        anomalies=(StructureAnomaly(99, "PARENT_MISSING", "missing"),),
    )


def summary(**options):
    model = build_model(structure(), prs(pr(30, "iss-00003", checks="failure")), now=NOW)
    return model, summary_document(model, hidden=options.get("hidden", False), server=options.get("server"))


def test_the_summary_has_every_contract_field() -> None:
    _, document = summary(server="http://127.0.0.1:47800/")
    assert list(document) == [
        "schema",
        "repository",
        "fetched_at",
        "stale",
        "counts",
        "completion_ratio",
        "awaiting_merge",
        "in_progress",
        "ready",
        "blocked",
        "cleanup",
        "anomaly_count",
        "pull_requests",
        "paths",
        "hidden",
        "server",
    ]
    assert document["schema"] == SUMMARY_SCHEMA == "specdock.dashboard-summary/v1"
    assert (document["repository"], document["fetched_at"], document["stale"]) == (
        "github.com/o/r",
        "2026-11-04T11:50:00Z",
        False,
    )
    assert (document["hidden"], document["server"], document["anomaly_count"]) == (False, "http://127.0.0.1:47800/", 1)
    assert document["pull_requests"] == {"status": "fresh", "fetched_at": "2026-11-04T11:50:00Z", "error": None}
    assert document["paths"]["iss-00003"] == "/r/github.com/o/r/scopes/iss-00003"
    json.dumps(document)


def test_counts_lists_and_order_match_the_model() -> None:
    model, document = summary()
    assert document["counts"]["total"] == len(model.scopes) == 9
    assert document["counts"]["by_state"] == {"done": 2, "doing": 4, "blocked": 2, "ready": 1, "unknown": 0}
    assert document["counts"]["by_kind"]["issue"] == {
        "total": 6,
        "done": 1,
        "doing": 2,
        "blocked": 2,
        "ready": 1,
        "unknown": 0,
    }
    assert document["completion_ratio"] == pytest.approx(2 / 9)
    assert document["awaiting_merge"] == [
        {
            "id": "iss-00003",
            "number": 3,
            "kind": "issue",
            "title": "Merge me",
            "state": "doing",
            "reason": "PR #30 を直す必要がある（CI が失敗）",
            "merge": "needs_fix",
        }
    ]
    assert [item["id"] for item in document["in_progress"]] == list(model.lane("doing"))
    assert [item["id"] for item in document["ready"]] == ["iss-00005"]
    assert [item["id"] for item in document["blocked"]] == ["iss-00009", "iss-00006"]
    assert [(item["id"], item["cleanup"]) for item in document["cleanup"]] == [
        ("iss-00009", "open_under_closed_parent"),
        ("epic-00008", "closed_with_open_descendants"),
    ]
    assert document["cleanup"][1]["reason"] == "閉じたのに、配下の 1件が開いている"


def test_the_same_input_gives_the_same_document_and_hidden_is_passed_through() -> None:
    _, first = summary(hidden=True)
    _, second = summary(hidden=True)
    assert first == second and first["hidden"] is True


def test_an_empty_structure_has_no_completion_ratio_and_text_lines_render() -> None:
    model = build_model(snapshot(), now=NOW)
    document = summary_document(model, hidden=False, server=None)
    counts = document["counts"]
    assert isinstance(counts, dict)
    assert document["completion_ratio"] is None and counts["total"] == 0
    lines = summary_text(summary()[1])
    assert lines[0] == "repository=github.com/o/r fetched_at=2026-11-04T11:50:00Z"
    assert "awaiting_merge 1" in lines and any("iss-00003 Merge me" in line for line in lines)
