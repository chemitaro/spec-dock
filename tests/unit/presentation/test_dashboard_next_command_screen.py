"""The command lines in "next" on both screens (iss-00676 T-03), with the fake DOM and the fake orca.

`views/graph.js` (the structure graph) and `views/allgraph.js` (the cross-repository structure) draw the lines, the arcs,
the Unscoped row and the bands of "next" by the rule of "now" and "all"; only the Scope boxes and frames differ. The
inputs are the real data's shape: a coordinator in the main checkout directs an Issue's worktree (whose agents direct
each other: an arc), a researcher in its own band item, and an agent in a worktree of a done Issue hidden in "next".
Every value is synthetic: no real path, address, session id or name of the user's environment.
"""

from __future__ import annotations

import copy
import json
import subprocess
from typing import Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document
from tests.unit.presentation import (
    test_dashboard_allgraph_command_screen as AS,
    test_dashboard_graph_command_screen as GS,
)
from tests.unit.presentation.test_dashboard_graph_command import ag, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, _node

RANGES = ("next", "now", "all")


def _ag(agent_id: str, mark: str = "working", parent: str | None = None) -> dict[str, Any]:
    return ag(agent_id, mark, parent) | {"w": 36}


def _doc() -> dict[str, Any]:
    """Epic 1 with the open Issues 2, 3 and the done Issue 4 (hidden in "next"), worktrees for Issues 2 and 4."""
    doc = copy.deepcopy(
        document(
            snapshot(
                node(1, "epic"), node(2, "issue", parent=1), node(3, "issue", parent=1), closed(4, "issue", parent=1)
            )
        )
    )
    records = {"iss-00002": "/w/r-2", "iss-00004": "/w/r-4"}
    doc["worktrees"] = {"status": "ok", "paths": ["/w/r", *records.values()]}
    for scope in doc["scopes"]:
        if scope["id"] in records:
            scope["worktrees"] = [{"path": records[scope["id"]], "branch": scope["id"]}]
    return doc | {"revision": "r1"}


DOC = _doc()
MAIN = wt("wt-main", "/w/r", "main", [_ag("a-coord"), _ag("a-res", "waiting", "a-coord")], main=True)
OWN = wt("wt-2", "/w/r-2", "iss-00002", [_ag("a-own", parent="a-coord"), _ag("a-impl", "done", "a-own")])
FOUR = wt("wt-4", "/w/r-4", "iss-00004", [_ag("a-four", parent="a-coord")])
PLAIN = summary(MAIN, OWN)  # no Scope hidden in "next"
HIDDEN = summary(MAIN, OWN, FOUR)  # a-four's Issue 4 is hidden in "next"

G_RUNS: list[dict[str, Any]] = [
    *({"name": f"plain-{r}", "orca": {"summary": PLAIN}, "range": r} for r in RANGES),
    *({"name": f"hidden-{r}", "orca": {"summary": HIDDEN}, "range": r} for r in RANGES),
    # the same input draws nothing again; a new summary of the same shape draws only the layers
    {
        "name": "again",
        "orca": {"summary": HIDDEN},
        "range": "next",
        "steps": [{"render": True}, {"news": True}, {"summary": json.loads(json.dumps(HIDDEN))}],
    },
]


@pytest.fixture(scope="module")
def graph(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    return GS._run(tmp_path_factory.mktemp("next-graph"), {"doc": DOC, "runs": G_RUNS})["runs"]


def _audit(shot: dict[str, Any]) -> dict[str, Any]:
    a = shot["audit"]
    return {k: a[k] for k in ("links", "arcs", "boxOverlaps", "edgeOverlaps", "motion", "heads")}


def test_the_structure_graphs_next_draws_the_lines_of_now(graph: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-01: the same pairs give "next" the audit, the lines and their states of "now" and "all"."""
    nxt, now, all_ = (graph[f"plain-{r}"][0] for r in RANGES)
    assert _audit(nxt) == _audit(now) == _audit(all_)
    assert nxt["audit"]["links"] == 3 and nxt["audit"]["arcs"] == 2
    assert nxt["lines"] == now["lines"] and set(nxt["lines"]) == {"a-coord>a-own", "a-own>a-impl", "a-coord>a-res"}
    # the colour and the motion follow the child's state as in "now": flowing, standing still, faint
    assert nxt["states"] == now["states"] == {"a-coord>a-own": "flow", "a-own>a-impl": "done", "a-coord>a-res": "wait"}
    assert nxt["every"] == now["every"] and nxt["svgs"] == now["svgs"]
    assert nxt["ripples"] == now["ripples"] and nxt["topRipples"] == now["topRipples"]
    assert nxt["layers"][-3:] == ["gx-cmd-top", "gx-edges", "gx-band"]


def test_the_structure_graphs_next_ends_a_hidden_scopes_agent_on_its_frame(
    graph: dict[str, list[dict[str, Any]]],
) -> None:
    """T-03 / R-01: Issue 4 is hidden in "next": a-four's line still comes (to Epic 1's frame), one line of each pair."""
    nxt, now = graph["hidden-next"][0], graph["hidden-now"][0]
    assert (
        set(nxt["lines"]) == set(now["lines"]) == {"a-coord>a-own", "a-own>a-impl", "a-coord>a-res", "a-coord>a-four"}
    )
    assert nxt["audit"]["links"] == now["audit"]["links"] == 4
    assert 'data-id="iss-00004"' not in nxt["html"] and 'data-id="iss-00004"' in now["html"]
    # the end moved from Issue 4's box to the frame: the line's path differs, the others do not
    assert nxt["paths"]["a-coord>a-four"] != now["paths"]["a-coord>a-four"]
    assert nxt["audit"]["boxOverlaps"] == nxt["audit"]["edgeOverlaps"] == 0


def test_the_structure_graphs_row_is_the_same_in_every_range(graph: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-02: the Unscoped row of "next" is that of "now"; no count in any range."""
    rows = [graph[f"hidden-{r}"][0]["row"]["items"] for r in RANGES]
    assert rows[0] == rows[1] == rows[2]
    assert [it["label"] for it in rows[0]] == ["main"]
    for name, shots in graph.items():
        for shot in shots:
            assert "gx-band-count" not in shot["html"], name
            assert all(it["count"] is None for it in shot["row"]["items"]), name


def test_the_structure_graphs_next_draws_the_same_input_once(graph: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-01 (iss-00615 R-08): the same summary keeps the layers; a new one draws only the layers."""
    first, render, news, copied = graph["again"]
    assert (render["cmd"], render["band"]) == (news["cmd"], news["band"]) == (first["cmd"], first["band"])
    assert copied["edges"] == first["edges"] and copied["cmd"] != first["cmd"]
    assert copied["lines"] == first["lines"]


def test_reduced_motion_is_the_same_rule_in_every_range() -> None:
    """T-03 / R-01: the reduced motion's rules name no range, so "next" stands still as "now" does."""
    media = GS.GRAPH_CSS[GS.GRAPH_CSS.rindex("@media (prefers-reduced-motion: reduce)") :]
    assert ".cl-ph" in media and ".cr" in media
    assert "data-range" not in media and "data-range" not in "".join(
        sel for sel, _ in GS._rules(GS.GRAPH_CSS) if ".cl" in sel or ".cr" in sel or ".gx-cmd" in sel
    )


# --- the cross-repository structure ------------------------------------------------------------------------------

C_DOCS = AS.DOCS | {AS.key("c"): AS.doc("/w/c", {"iss-00002": "/w/c-2", "iss-00005": "/w/c-5"})}
X_PLAIN = AS.summary(
    AS.wt("wt-a", "/w/a", "main", [AS.ag("a-coord"), AS.ag("a-res", "waiting", "a-coord")], AS.PROJ["a"], main=True),
    AS.wt(
        "wt-c2",
        "/w/c-2",
        "iss-00002",
        [AS.ag("c-own", parent="a-coord"), AS.ag("c-impl", "done", "c-own")],
        AS.PROJ["c"],
    ),
)
X_HIDDEN = AS.summary(
    *X_PLAIN["worktrees"],
    AS.wt("wt-c5", "/w/c-5", "iss-00005", [AS.ag("c-five", parent="a-coord")], AS.PROJ["c"]),
)
FLIP_RUN = next(r for r in AS.RUNS if r["name"] == "flip")
X_RUNS: list[dict[str, Any]] = [
    *(
        {"name": f"plain-{r}", "orca": {"summary": X_PLAIN}, "repos": AS.REPOS, "docs": C_DOCS, "range": r}
        for r in RANGES
    ),
    *(
        {"name": f"hidden-{r}", "orca": {"summary": X_HIDDEN}, "repos": AS.REPOS, "docs": C_DOCS, "range": r}
        for r in RANGES
    ),
    # F-02: F-05's limit of composing again holds in "next" too
    copy.deepcopy(FLIP_RUN) | {"name": "flip-next", "range": "next"},
]


@pytest.fixture(scope="module")
def cross(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    path = tmp_path_factory.mktemp("next-cross") / "request.json"
    path.write_text(json.dumps({"runs": X_RUNS}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(AS.HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return {name: r["shots"] for name, r in json.loads(result.stdout)["runs"].items()}


def _x_audit(shot: dict[str, Any]) -> dict[str, Any]:
    a = shot["audit"]
    return {k: a[k] for k in ("links", "arcs", "boxOverlaps", "edgeOverlaps", "heads")} | {"motion": shot["motion"]}


def test_the_cross_next_draws_the_lines_of_now(cross: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-01: the default "next" draws a's coordinator to c's worktree and the arc in c's box, as "now" does."""
    nxt, now, all_ = (cross[f"plain-{r}"][0] for r in RANGES)
    assert _x_audit(nxt) == _x_audit(now) == _x_audit(all_)
    assert nxt["audit"]["links"] == 3 and nxt["audit"]["arcs"] == 2
    assert nxt["lines"] == now["lines"] and set(nxt["lines"]) == {"a-coord>c-own", "c-own>c-impl", "a-coord>a-res"}
    assert nxt["layers"][-3:] == ["gx-cmd", "gx-cmd-top", "gx-band"]


def test_the_cross_next_ends_a_hidden_scopes_agent_on_its_frame(cross: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-01: c's done Issue 5 is hidden in "next": c-five's line still comes, to Epic 1's frame."""
    nxt, now = cross["hidden-next"][0], cross["hidden-now"][0]
    assert (
        set(nxt["lines"]) == set(now["lines"]) == {"a-coord>c-own", "c-own>c-impl", "a-coord>a-res", "a-coord>c-five"}
    )
    assert nxt["audit"]["links"] == now["audit"]["links"] == 4
    assert nxt["audit"]["boxOverlaps"] == nxt["audit"]["edgeOverlaps"] == 0


def test_the_cross_rows_are_the_same_in_every_range(cross: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / R-02: the bands' items of "next" are those of "now"; no count in any range."""
    items = [[(it["label"], it["badge"]) for it in cross[f"hidden-{r}"][0]["bandItems"]] for r in RANGES]
    assert items[0] == items[1] == items[2]
    for name, shots in cross.items():
        for shot in shots:
            assert all(it["count"] is None and it["countTitle"] is None for it in shot["bandItems"]), name


def test_the_cross_next_composes_again_at_most_twice(cross: dict[str, list[dict[str, Any]]]) -> None:
    """T-03 / F-02 (iss-00617 F-05 in "next"): twice for the same places' inputs, then never; a new summary again."""
    first, flipped, again, reset, plain = cross["flip-next"]
    assert flipped["stats"]["composes"] - first["stats"]["composes"] == 2
    assert again["stats"]["composes"] == flipped["stats"]["composes"]
    assert reset["stats"]["composes"] - again["stats"]["composes"] == 2
    assert plain["lines"] == {"f-coord>c-own": ""}
