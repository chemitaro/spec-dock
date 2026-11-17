"""The command lines of the structure graph (iss-00616 T-01..T-03), run in node like the other graph checks.

`views/graph/command.js` turns orca-web's summary (agents[].parent) into pairs (parent, child), places each end (a box's
or frame's mark, a folded group, the nearest drawn ancestor frame, or the command band above every Initiative), and
draws the curves, the arcs of one box and the ripples from the layout, the measured marks and their recorded order.
`views/graph/layout.js` gives the marks' positions (markSpots) from the same packing as markRows.
Every value is synthetic: no real path, address or session id.
"""

from __future__ import annotations

import copy
from itertools import pairwise
import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node, _small

if TYPE_CHECKING:
    from pathlib import Path

CHECK = ROOT / "tests" / "js" / "dashboard_graph_command.mjs"
SCHEMA = "orca-web.worktree-summary/v1"
OWN = ("p-own", "own")
OTHER = ("p-other", "other")
W = 36  # a mark's width
GAP = 2


def _run(tmp_path: Path, request: dict[str, Any], assets: Path = ASSETS) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(assets), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def ag(agent_id: str, mark: str = "working", parent: Any = None, **extra: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "id": agent_id,
        "mark": mark,
        "workingMode": "monitoring" if mark == "working" else None,
        "agentType": "claude",
        "detail": f"/embed/agent?id={agent_id}",
    }
    if isinstance(parent, str):
        out["parent"] = {"id": parent, "worktreeId": None}
    elif parent is not None:
        out["parent"] = parent
    return out | extra


def wt(
    worktree_id: str,
    path: str,
    branch: str | None,
    agents: list[Any],
    *,
    project: tuple[str, str | None] | None = OWN,
    main: bool | None = False,
) -> dict[str, Any]:
    return {
        "id": worktree_id,
        "path": path,
        "branch": branch,
        "project": None if project is None else {"id": project[0], "name": project[1]},
        "main": main,
        "agents": agents,
        "counts": {},
    }


def summary(*worktrees: dict[str, Any]) -> dict[str, Any]:
    return {"schema": SCHEMA, "connection": {"state": "connected"}, "worktrees": list(worktrees)}


# the worktrees of the small structure (Epics 1, 6, 8, 10, 20, 30 and their Issues) in this repository
RECORDS = {
    "iss-00021": "/w/r-21",
    "iss-00022": "/w/r-22",
    "iss-00023": "/w/r-23",
    "iss-00031": "/w/r-31",
    "iss-00033": "/w/r-33",
    "epic-00030": "/w/r-e30",
    "iss-00009": "/w/r-09",
}


def structure(records: dict[str, str] = RECORDS, status: str = "ok") -> dict[str, Any]:
    doc = copy.deepcopy(_small())
    doc["worktrees"] = {"status": status, "paths": ["/w/r", *records.values()]}
    for scope in doc["scopes"]:
        if scope["id"] in records:
            scope["worktrees"] = [{"path": records[scope["id"]], "branch": scope["id"]}]
    return doc


def mark(*ids: str) -> dict[str, Any]:
    return {"items": [W] * len(ids), "gap": GAP, "ids": list(ids)}


# The real data's shape (Epic report): five pairs, one directed by another repository's coordinator, two inside one
# worktree (an Issue's worktree, the main checkout).
FIVE = summary(
    wt(
        "wt-main",
        "/w/r",
        "main",
        [ag("a-coord"), ag("a-research", "waiting", "a-coord")],
        main=True,
    ),
    wt("wt-21", "/w/r-21", "iss-00021", [ag("a-own21", parent="a-coord"), ag("a-impl21", parent="a-own21")]),
    wt("wt-22", "/w/r-22", "iss-00022", [ag("a-own22", "waiting", "x-coord")]),
    wt("wt-e30", "/w/r-e30", "epic-00030", [ag("a-e30", "done", "a-coord")]),
    wt("wt-x", "/x/other", "main", [ag("x-coord")], project=OTHER, main=True),
)
FIVE_MARKS = {"iss-00021": mark("a-own21", "a-impl21"), "iss-00022": mark("a-own22"), "epic-00030": mark("a-e30")}
FIVE_PAIRS = [
    ["a-coord", "a-e30"],
    ["a-own21", "a-impl21"],
    ["a-coord", "a-own21"],
    ["x-coord", "a-own22"],
    ["a-coord", "a-research"],
]
NEST_ALL = {"mode": "nest", "range": "all"}


def _scenario(sc: dict[str, Any]) -> dict[str, Any]:
    return {"structure": structure(), "layout": NEST_ALL, "routed": True} | sc


SCENARIOS: dict[str, dict[str, Any]] = {
    "five": _scenario({"summary": FIVE, "marks": FIVE_MARKS}),
    # an Issue hidden by "next" (iss-00031, done) inside the Epic frame 30, directed from the Epic's mark and the band
    "hidden": _scenario({
        "layout": {"mode": "nest", "range": "next"},
        "summary": summary(
            wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True),
            wt("wt-e30", "/w/r-e30", "epic-00030", [ag("a-e30", parent="a-coord")]),
            wt(
                "wt-31",
                "/w/r-31",
                "iss-00031",
                [
                    ag("a-own31", parent="a-e30"),
                    ag("a-impl31", parent="a-own31"),
                    ag("a-help31", parent="a-coord"),
                    ag("a-two31", parent="a-coord"),
                ],
            ),
        ),
        "marks": {"epic-00030": mark("a-e30")},
    }),
    # iss-00009 sits in the folded group of its done Epic 8 ("now")
    "folded": _scenario({
        "layout": {"mode": "nest", "range": "now"},
        "summary": summary(
            wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True),
            wt("wt-09", "/w/r-09", "iss-00009", [ag("a-own09", parent="a-coord")]),
        ),
    }),
    # the Epic's coordinator directs an Issue inside its frame; two agents in the frame's heading; two rows in a box
    "epic": _scenario({
        "summary": summary(
            wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True),
            wt("wt-e30", "/w/r-e30", "epic-00030", [ag("a-e30", parent="a-coord"), ag("a-e30b", "blocked", "a-e30")]),
            wt("wt-33", "/w/r-33", "iss-00033", [ag("a-own33", "sleeping", "a-e30")]),
            wt(
                "wt-23",
                "/w/r-23",
                "iss-00023",
                [ag("a-p23", "unknown"), *(ag(f"a-x{i}", "done") for i in range(4)), ag("a-c23", "zzz", "a-p23")],
            ),
        ),
        "marks": {
            "epic-00030": mark("a-e30", "a-e30b"),
            "iss-00033": mark("a-own33"),
            "iss-00023": mark("a-p23", "a-x0", "a-x1", "a-x2", "a-x3", "a-c23"),
        },
    }),
    # F-04: no measured marks for the boxes and the frame
    "unknown": _scenario({"summary": FIVE, "marks": {"iss-00021": {"items": [W, W], "gap": GAP}}}),
    # two ends in other repositories only, and a pair inside the main checkout's band item in the order of orderAgents
    "others": _scenario({
        "summary": summary(
            wt("wt-main", "/w/r", "main", [ag("a-coord"), ag("a-idle"), ag("a-research", parent="a-coord")], main=True),
            wt("wt-y1", "/y/one", "main", [ag("y-a")], project=OTHER, main=True),
            wt("wt-y2", "/y/two", "topic", [ag("y-b", parent="y-a")], project=OTHER),
        ),
        "order": {"wt-main": ["a-research", "a-idle", "a-coord"]},
    }),
    # the labels of the band's items (F-03) and their order
    "labels": _scenario({
        "summary": summary(
            wt("wt-z", "/z/x", None, [ag("z-a", parent="a-coord")], project=None),
            wt("wt-o", "/x/other", "main", [ag("o-a", parent="a-coord")], project=OTHER, main=True),
            wt("wt-nb", "/w/r-nb", None, [ag("nb-a", parent="a-coord")]),
            wt("wt-f", "/w/r-f", "feature-b", [ag("f-a", parent="a-coord")], main=None),
            wt("wt-e", "/w/r-e", "feature-a", [ag("e-a", parent="a-coord")]),
            wt("wt-main", "/w/r", "main", [ag("a-coord")], main=True),
        ),
    }),
    "unreadable": _scenario({"structure": structure(status="unreadable"), "summary": FIVE, "marks": FIVE_MARKS}),
    "invalid": _scenario({"summary": {"schema": "other", "worktrees": FIVE["worktrees"]}, "marks": FIVE_MARKS}),
}


# --- arcs in a box with little room: a raw layout ----------------------------------------------------------------

RAW_SCOPES = [
    {"id": "iss-00001", "parent_id": None, "worktrees": [{"path": "/w/a", "branch": "a"}]},
    {"id": "iss-00002", "parent_id": None, "worktrees": []},
    {"id": "iss-00003", "parent_id": None, "worktrees": []},
]
RAW_SUMMARY = summary(wt("wt-a", "/w/a", "a", [ag("p"), ag("c", parent="p")]))
A: dict[str, Any] = {"type": "box", "id": "iss-00001", "x1": 100, "y1": 100, "x2": 278, "y2": 188, "rows": 2}


def _raw(below: float | None, right: float | None, routes: tuple[list[dict[str, Any]], ...] = ()) -> dict[str, Any]:
    nodes = [A]
    if below is not None:
        nodes.append({"type": "box", "id": "iss-00002", "x1": 100, "y1": 188 + below, "x2": 278, "y2": 276 + below})
    if right is not None:
        nodes.append({"type": "box", "id": "iss-00003", "x1": 278 + right, "y1": 100, "x2": 456 + right, "y2": 188})
    return {
        "structure": {"worktrees": {"status": "ok", "paths": ["/w/a"]}, "scopes": RAW_SCOPES},
        "summary": RAW_SUMMARY,
        "layout": {"nodes": nodes, "groups": [], "width": 1000, "height": 1000},
        "marks": {"iss-00001": mark("p", "c")},
        "routes": [{"pts": pts} for pts in routes],
    }


H_RUN = [{"x": 50, "y": 195}, {"x": 400, "y": 195}]  # a dependency line's horizontal run just below the box
V_RUN = [{"x": 285, "y": 50}, {"x": 285, "y": 300}]  # and a vertical one just right of it
SCENARIOS |= {
    "room": _raw(None, None),
    "shallow": _raw(12, None),
    "flip": _raw(6, None),
    "crowded": _raw(6, 6),
    "routeflip": _raw(None, None, (H_RUN,)),
    "routeboth": _raw(None, None, (H_RUN, V_RUN)),
}


@pytest.fixture(scope="module")
def got(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    return _run(tmp_path_factory.mktemp("command"), {"scenarios": SCENARIOS, "key": True})["scenarios"]


def _link(entry: dict[str, Any], link_id: str) -> dict[str, Any]:
    found = [link for link in entry["model"]["links"] if link["id"] == link_id]
    assert len(found) == 1, (link_id, [link["id"] for link in entry["model"]["links"]])
    return found[0]


def _points(d: str) -> list[tuple[float, float]]:
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
    return list(zip(nums[::2], nums[1::2], strict=True))


# --- T-01: the pairs, their places and the band's items ----------------------------------------------------------


def test_the_five_pairs_of_the_real_shape(got: dict[str, Any]) -> None:
    """T-01 / R-01: the five pairs come out as they are, ordered by the child's id."""
    assert got["five"]["allPairs"] == FIVE_PAIRS
    assert got["five"]["placed"]["pairs"] == FIVE_PAIRS


def test_malformed_parents_make_no_pair(tmp_path: Path) -> None:
    """T-01 / F-02: no parent, null, an unknown id, itself, not a string, not an object: no pair; a cycle counts each pair once."""
    agents: list[Any] = [
        ag("n0"),
        ag("n1", parent={"id": None}),
        ag("n2", parent={"id": "ghost"}),
        ag("n3", parent={"id": "n3"}),
        ag("n4", parent={"id": 7}),
        ag("n5", parent="ok"),  # becomes {"id": "ok"}: the one good pair
        ag("n6", parent=["ok"]),
        ag("n7") | {"parent": None},
        ag("n8") | {"parent": "ok"},  # a string, not an object
        ag("c1", parent="c2"),
        ag("c2", parent="c1"),
        ag("ok"),
        ag("c1", parent="ok"),  # a second agent with the same id: the first one counts
        {"id": 9, "parent": {"id": "ok"}},
        "not an agent",
    ]
    request = {
        "pairs": [
            summary(wt("w", "/w/r", "main", agents)),
            {"schema": "other", "worktrees": [wt("w", "/w/r", "main", [ag("a"), ag("b", parent="a")])]},
            None,
        ]
    }
    assert _run(tmp_path, request)["pairs"] == [[["c2", "c1"], ["c1", "c2"], ["ok", "n5"]], [], []]


def test_the_places_of_the_ends(got: dict[str, Any]) -> None:
    """T-01 / R-01: a box's mark, the nearest drawn ancestor frame of a hidden Issue, a folded group, the band."""
    places = got["five"]["placed"]["places"]
    assert places["a-own21"] == {"kind": "mark", "id": "iss-00021", "scope": "iss-00021"}
    assert places["a-impl21"] == places["a-own21"]
    assert places["a-e30"] == {"kind": "mark", "id": "epic-00030", "scope": "epic-00030"}
    assert places["a-coord"] == {"kind": "band", "key": "wt-main"}
    assert places["x-coord"] == {"kind": "band", "key": "wt-x"}
    hidden = got["hidden"]["placed"]["places"]
    assert "iss-00031" not in got["hidden"]["nodes"]
    assert hidden["a-own31"] == {"kind": "frame", "id": "epic-00030"}
    folded = got["folded"]["placed"]["places"]
    assert "iss-00009" not in got["folded"]["nodes"]
    assert folded["a-own09"]["kind"] == "group" and "epic-00008" in folded["a-own09"]["ids"]


def test_pairs_with_both_ends_in_other_repositories_are_dropped(got: dict[str, Any]) -> None:
    """T-01 / R-01: y-a > y-b lives in other repositories only."""
    entry = got["others"]
    assert ["y-a", "y-b"] in entry["allPairs"]
    assert entry["placed"]["pairs"] == [["a-coord", "a-research"]]
    assert [it["key"] for it in entry["items"]] == ["wt-main"]


def test_without_the_worktree_list_or_a_valid_summary_nothing_is_placed(got: dict[str, Any]) -> None:
    """T-01 / F-01."""
    assert got["unreadable"]["placed"] is None
    assert got["invalid"]["allPairs"] == []
    assert got["invalid"]["placed"] is None


def test_the_band_holds_the_main_checkout_with_both_agents(got: dict[str, Any]) -> None:
    """T-01 / R-02: one item for the main checkout with the coordinator and the researcher; the other repository after it."""
    assert got["five"]["items"] == [
        {
            "key": "wt-main",
            "label": "main のチェックアウト",
            "own": True,
            "main": True,
            "agents": ["a-coord", "a-research"],
        },
        {"key": "wt-x", "label": "other · main", "own": False, "main": False, "agents": ["x-coord"]},
    ]


def test_the_band_labels_and_their_order(got: dict[str, Any]) -> None:
    """T-01 / R-02, F-03: main first, this repository by label, then the other repositories by label."""
    assert [(it["key"], it["label"]) for it in got["labels"]["items"]] == [
        ("wt-main", "main のチェックアウト"),
        ("wt-e", "feature-a"),
        ("wt-f", "feature-b"),  # main is null: the branch
        ("wt-nb", "ブランチ不明"),
        ("wt-o", "other · main"),
        ("wt-z", "ほかのリポジトリ · ブランチ不明"),
    ]


def test_an_items_agents_follow_order_agents(got: dict[str, Any]) -> None:
    """T-01 / R-02: the order of orderAgents without the agents the band does not show."""
    assert got["others"]["items"][0]["agents"] == ["a-research", "a-coord"]


# --- T-02: the marks' positions ----------------------------------------------------------------------------------


def _row_cases() -> list[tuple[Any, float, int]]:
    from tests.unit.presentation.test_dashboard_graph_marks_rows import ROW_CASES

    return ROW_CASES


BOX1 = {"type": "box", "id": "b", "x1": 100, "y1": 200, "x2": 278, "y2": 288, "rows": 2}
BOX2 = {"type": "box", "id": "b", "x1": 100, "y1": 200, "x2": 278, "y2": 308, "rows": 3}
TFRAME = {"type": "tframe", "id": "t", "x1": 40, "y1": 0, "x2": 276, "y2": 128, "rows": 3}
EPIC = {"type": "frame", "kind": "epic", "id": "e", "x1": 0, "y1": 0, "x2": 300, "y2": 500, "rows": 2, "compact": False}
INI = {
    "type": "frame",
    "kind": "initiative",
    "id": "i",
    "x1": 10,
    "y1": 20,
    "x2": 600,
    "y2": 900,
    "rows": 2,
    "compact": False,
}
COMPACT = {
    "type": "frame",
    "kind": "epic",
    "id": "c",
    "x1": 0,
    "y1": 0,
    "x2": 236,
    "y2": 87,
    "rows": 2,
    "compact": True,
}
FIT = COMPACT | {"y2": 101, "fit": 101}


def _six() -> dict[str, Any]:
    return mark(*"abcdef")


SPOT_CASES: list[tuple[dict[str, Any], Any]] = [
    (BOX1, mark("a", "b")),
    (BOX2, _six()),
    (TFRAME, _six()),
    (EPIC, mark("a", "b")),
    (INI, mark("a")),
    (COMPACT, mark("a")),
    (FIT, mark("a")),
    # F-04
    (BOX1, {"items": [W, W], "gap": GAP}),
    (BOX1, {"items": [W, W], "gap": GAP, "ids": ["a"]}),
    (BOX1, _six()),  # three rows of marks in a box laid out with two
    (BOX1, None),
    (BOX1 | {"rows": 1}, {"items": [], "gap": GAP, "ids": []}),
]


@pytest.fixture(scope="module")
def spots(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    request = {"packMarks": [[m, avail] for m, avail, _ in _row_cases()], "markSpots": [list(c) for c in SPOT_CASES]}
    return _run(tmp_path_factory.mktemp("spots"), request)


def test_the_constants_of_the_marks_and_the_band(spots: dict[str, Any]) -> None:
    assert spots["consts"] == {
        "MARK_H": 16,
        "MARK_LEAD": 10,
        "MARK_LEFT": {"box": 15},
        "MARK_BOTTOM": {"box": 9},
        "FRAME_TITLE": 22,
        "FRAME_GAP": 4,
        "BAND": {"top": -16, "h": 28, "left": 24, "border": 1, "pad": 6, "gap": 10, "labelGap": 6, "slot": 52},
    }


def test_pack_marks_packs_as_mark_rows(spots: dict[str, Any]) -> None:
    """T-02: markRows is 1 + the rows packMarks uses (the old table), and the packing is left to right."""
    assert [p["rows"] for p in spots["packMarks"]] == [want for *_, want in _row_cases()]
    for p, (m, _, rows) in zip(spots["packMarks"], _row_cases(), strict=True):
        if m is None:
            assert p["packed"] is None
            continue
        assert len(p["packed"]) == len(m["items"])
        assert (p["packed"][-1]["row"] + 2 if p["packed"] else 1) == rows
    six = spots["packMarks"][6]["packed"]
    assert six == [
        {"row": 0, "x": 0},
        {"row": 0, "x": 38},
        {"row": 0, "x": 76},
        {"row": 0, "x": 114},
        {"row": 1, "x": 0},
        {"row": 1, "x": 38},
    ]


def _rect(s: dict[str, Any]) -> tuple[Any, ...]:
    return (s["id"], s["x"], s["y"], s["w"], s["h"])


def test_mark_spots_of_boxes_and_frames(spots: dict[str, Any]) -> None:
    """T-02: the box's rows end at its inner bottom edge; a frame's row is below its title row (and a fitted title)."""
    got = spots["markSpots"]
    assert [_rect(s) for s in got[0]] == [("a", 115, 263, 36, 16), ("b", 153, 263, 36, 16)]
    assert [_rect(s) for s in got[1]] == [
        ("a", 115, 263, 36, 16), ("b", 153, 263, 36, 16), ("c", 191, 263, 36, 16), ("d", 229, 263, 36, 16),
        ("e", 115, 283, 36, 16), ("f", 153, 283, 36, 16),
    ]  # fmt: skip
    # the tree's frame box is 236 wide: five marks a row
    assert [(s["id"], s["x"], s["y"]) for s in got[2]] == [
        ("a", 55, 83), ("b", 93, 83), ("c", 131, 83), ("d", 169, 83), ("e", 207, 83), ("f", 55, 103),
    ]  # fmt: skip
    assert [_rect(s) for s in got[3]] == [("a", 13, 35, 36, 16), ("b", 51, 35, 36, 16)]
    assert [_rect(s) for s in got[4]] == [("a", 27, 62, 36, 16)]
    assert [_rect(s) for s in got[5]] == [("a", 13, 35, 36, 16)]
    assert [_rect(s) for s in got[6]] == [("a", 13, 49, 36, 16)]  # a title of two lines: 14px taller


def test_mark_spots_are_unknown_without_the_record(spots: dict[str, Any]) -> None:
    """T-02 / F-04: no ids, a different number of ids, other rows than the layout's, no measure; no agent is no mark."""
    assert spots["markSpots"][7:11] == [None, None, None, None]
    assert spots["markSpots"][11] == []


# --- T-03: the band, the ends, the curves and the arcs ----------------------------------------------------------


def test_the_band_items_size_and_place(got: dict[str, Any]) -> None:
    """T-03 / R-02: each item 2·border + 2·pad + label + labelGap + slot × n wide, 10 apart, left from the margin."""
    band = got["five"]["model"]["band"]
    assert (band["top"], band["h"]) == (-16, 28)
    x = 24
    for item in band["items"]:
        lw = item["labelWidth"]
        assert (item["x"], item["y"], item["h"]) == (x, -16, 28)
        assert item["w"] == 2 + 12 + lw + 6 + 52 * len(item["agents"])
        assert [(a["x"], a["y"], a["w"], a["h"]) for a in item["agents"]] == [
            (x + 1 + 6 + lw + 6 + 52 * i, -16, 52, 28) for i in range(len(item["agents"]))
        ]
        x += item["w"] + 10
    assert band["right"] == x - 10
    assert [it["labelWidth"] for it in band["items"]] == [125, 85]
    assert got["five"]["model"]["top"] == -32
    assert got["five"]["model"]["width"] == max(got["five"]["width"], band["right"] + 24)
    labels = got["labels"]["model"]["band"]["items"]
    assert len(labels) == 6 and all(b["x"] - (a["x"] + a["w"]) == 10 for a, b in pairwise(labels))


def test_label_width(tmp_path: Path) -> None:
    """T-03: ASCII 6.6px, others 11.5px, rounded up, within 24..200."""
    got = _run(tmp_path, {"labelWidth": ["main", "main のチェックアウト", "", "長" * 30, "abcdefgh"]})["labelWidth"]
    assert got == [27, 125, 24, 200, 53]


def test_without_a_band_the_top_is_zero(got: dict[str, Any]) -> None:
    model = got["folded"]["model"]
    assert model["band"] is not None
    raw = got["room"]["model"]
    assert raw["band"] is None and raw["top"] == 0 and raw["width"] == 1000


def _control(link: dict[str, Any]) -> tuple[tuple[float, float], ...]:
    pts = _points(link["d"])
    assert len(pts) == 4, link["d"]
    return tuple(pts)


def _k(p: tuple[float, float], c: tuple[float, float]) -> float:
    return min(140, max(24, 0.45 * ((c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2) ** 0.5))


def test_curve_ends_of_marks_and_the_band(got: dict[str, Any]) -> None:
    """T-03 / R-03: from the band agent's lower edge down, into a box's lower edge from below with a stub from the mark."""
    entry = got["five"]
    link = _link(entry, "a-coord>a-own21")
    slot = entry["model"]["band"]["items"][0]["agents"][0]
    spot = next(s for s in entry["spots"]["iss-00021"] if s["id"] == "a-own21")
    box = entry["nodes"]["iss-00021"]
    p, c1, c2, c = _control(link)
    assert p == (slot["x"] + 26, 12)
    assert c == (spot["x"] + spot["w"] / 2, box["y2"])
    k = _k(p, c)
    assert c1 == pytest.approx((p[0], p[1] + k), abs=0.1)
    assert c2 == pytest.approx((c[0], c[1] + k), abs=0.1)
    assert link["stubs"] == [f"M {c[0]:g} {spot['y'] + 16:g} L {c[0]:g} {box['y2']:g}"]
    # a nested frame's heading mark: from the mark's lower edge, no stub
    frame = _link(entry, "a-coord>a-e30")
    fspot = entry["spots"]["epic-00030"][0]
    assert _control(frame)[3] == (fspot["x"] + 18, fspot["y"] + 16)
    assert frame["stubs"] == []


def test_curve_ends_on_groups_and_frames(got: dict[str, Any]) -> None:
    """T-03 / R-03: a folded group's edge facing the other end; a frame holding the other end: its inner lower edge, up."""
    folded = got["folded"]
    group = next(g for g in folded["groups"] if "epic-00008" in g["ids"])
    _, _, c2, c = _control(_link(folded, "a-coord>a-own09"))
    assert c == ((group["x1"] + group["x2"]) / 2, group["y1"])  # the band is above: the top edge
    assert c2[1] < c[1]  # leaving the top edge upward
    hidden = got["hidden"]
    frame = hidden["nodes"]["epic-00030"]
    _, _, c2, c = _control(_link(hidden, "a-e30>a-own31"))
    assert c == ((frame["x1"] + frame["x2"]) / 2, frame["y2"] - 1)
    assert c2[1] < c[1]


def test_lines_leaving_one_edge_are_spread(got: dict[str, Any]) -> None:
    """T-03: the band's two lines into the frame's edge facing the band are 10px apart around the edge's middle."""
    hidden = got["hidden"]
    frame = hidden["nodes"]["epic-00030"]
    (ax, ay), (bx, by) = [_control(_link(hidden, f"a-coord>{c}"))[3] for c in ("a-help31", "a-two31")]
    mid = ((frame["x1"] + frame["x2"]) / 2, (frame["y1"] + frame["y2"]) / 2)
    if ax == bx:  # a left or right edge
        assert ax in (frame["x1"], frame["x2"]) and (ay, by) == (mid[1] - 5, mid[1] + 5)
    else:
        assert ay == by and ay in (frame["y1"], frame["y2"]) and (ax, bx) == (mid[0] - 5, mid[0] + 5)


def test_no_line_inside_one_group_or_ancestor_frame(got: dict[str, Any]) -> None:
    """T-03 / R-03: both ends in the same ancestor frame without a mark: no line."""
    ids = [link["id"] for link in got["hidden"]["model"]["links"]]
    assert "a-own31>a-impl31" not in ids
    assert len(ids) == 4


def _arc(link: dict[str, Any]) -> tuple[float, float, tuple[float, float]]:
    """The chord, the bulge (from the control points: 4d/3) and the edge's coordinate of an arc."""
    p, c1, _, c = _control(link)
    chord = ((c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2) ** 0.5
    bulge = abs((c1[0] - p[0]) + (c1[1] - p[1])) * 3 / 4
    return chord, round(bulge, 1), p


def test_arcs_on_one_row_and_on_two_rows_of_a_box(got: dict[str, Any]) -> None:
    """T-03 / R-03: one row: the lower edge; two rows: the right edge; chord ≥ 40, bulge 16."""
    five = got["five"]
    box = five["nodes"]["iss-00021"]
    link = _link(five, "a-own21>a-impl21")
    assert link["kind"] == "arc"
    chord, bulge, p = _arc(link)
    assert chord >= 40 and bulge == 16 and p[1] == box["y2"]
    assert link["from"]["y"] == link["to"]["y"] == box["y2"]
    assert len(link["stubs"]) == 2
    epic = got["epic"]
    box23 = epic["nodes"]["iss-00023"]
    two = _link(epic, "a-p23>a-c23")
    chord, bulge, p = _arc(two)
    assert two["kind"] == "arc" and chord >= 40 and 8 <= bulge <= 16  # shallower toward the next box on the right
    assert two["from"]["x"] == two["to"]["x"] == box23["x2"]


def test_arcs_in_a_frame_heading_and_in_a_band_item(got: dict[str, Any]) -> None:
    """T-03 / R-03: below the heading's marks (d 12), above the band item (d 16)."""
    epic = got["epic"]
    heading = _link(epic, "a-e30>a-e30b")
    spot = epic["spots"]["epic-00030"]
    chord, bulge, p = _arc(heading)
    assert heading["kind"] == "arc" and chord >= 40 and bulge == 12
    assert p[1] == spot[0]["y"] + 16 and _control(heading)[1][1] > p[1]  # it bulges down
    band = _link(got["five"], "a-coord>a-research")
    chord, bulge, p = _arc(band)
    assert band["kind"] == "arc" and chord >= 40 and bulge == 16
    assert p[1] == -16 and _control(band)[1][1] < -16  # above the band


def test_arcs_with_little_room(got: dict[str, Any]) -> None:
    """T-03 / R-03: shallower down to 8, then the other edge, then the first edge at 8 counted as crowded."""
    room = _link(got["room"], "p>c")
    assert _arc(room)[1:] == (16, (A["x1"] + 15 + 18 - 1, A["y2"]))  # marks 38 apart, widened to 40
    shallow = _link(got["shallow"], "p>c")
    assert _arc(shallow)[1] == 9 and shallow["from"]["y"] == A["y2"]
    flip = _link(got["flip"], "p>c")
    assert _arc(flip)[1] == 16 and flip["from"]["x"] == A["x2"]
    assert _arc(flip)[0] >= 40
    crowded = _link(got["crowded"], "p>c")
    assert _arc(crowded)[1] == 8 and crowded["from"]["y"] == A["y2"]
    assert got["crowded"]["model"]["audit"]["crowded"] == 1
    assert all(got[name]["model"]["audit"]["crowded"] == 0 for name in ("room", "shallow", "flip"))


def test_arcs_turn_away_from_parallel_dependency_runs(got: dict[str, Any]) -> None:
    """T-03 / R-03: a horizontal run under the box sends the arc right; runs on both sides: the lower edge, counted."""
    flip = _link(got["routeflip"], "p>c")
    assert flip["from"]["x"] == A["x2"]
    assert got["routeflip"]["model"]["audit"]["edgeOverlaps"] == 0
    both = _link(got["routeboth"], "p>c")
    assert both["from"]["y"] == A["y2"]
    assert got["routeboth"]["model"]["audit"]["edgeOverlaps"] == 1


def test_the_synthetic_layouts_have_no_overlap(got: dict[str, Any]) -> None:
    """T-03 / R-03: boxOverlaps and edgeOverlaps are 0 with the routed layouts."""
    for name in ("five", "hidden", "folded", "epic", "others", "labels"):
        audit = got[name]["model"]["audit"]
        assert (audit["boxOverlaps"], audit["edgeOverlaps"], audit["crowded"]) == (0, 0, 0), name
        assert got[name]["routes"], name
    assert got["five"]["model"]["audit"] == {"links": 5, "arcs": 2, "boxOverlaps": 0, "edgeOverlaps": 0, "crowded": 0}


def test_the_epic_coordinator_line_stays_inside_its_frame(got: dict[str, Any]) -> None:
    """T-03 / R-03: from the Epic frame's heading down to the Issue inside: never above the frame's top edge."""
    epic = got["epic"]
    frame = epic["nodes"]["epic-00030"]
    link = _link(epic, "a-e30>a-own33")
    assert link["kind"] == "curve"
    assert min(y for _, y in _control(link)) >= frame["y1"]


def test_lengths_are_multiples_of_eight(got: dict[str, Any]) -> None:
    """T-03 / D-05: one round of the flowing dots, for the line and its stubs."""
    links = [link for entry in got.values() if entry.get("model") for link in entry["model"]["links"]]
    assert links and all(link["len"] % 8 == 0 and link["len"] >= 8 for link in links)


def test_the_state_follows_the_child(got: dict[str, Any]) -> None:
    """T-03 / R-04: working flows, done is faint, waiting, blocked, sleeping, unknown and others wait."""
    state = {link["id"]: link["state"] for link in got["five"]["model"]["links"]}
    assert state == {
        "a-coord>a-e30": "done",
        "a-own21>a-impl21": "flow",
        "a-coord>a-own21": "flow",
        "x-coord>a-own22": "wait",
        "a-coord>a-research": "wait",
    }
    state = {link["id"]: link["state"] for link in got["epic"]["model"]["links"]}
    assert state == {
        "a-coord>a-e30": "flow",
        "a-e30>a-e30b": "wait",  # blocked
        "a-e30>a-own33": "wait",  # sleeping
        "a-p23>a-c23": "wait",  # an unknown value
    }


def test_one_ripple_per_parent_at_its_mark(got: dict[str, Any]) -> None:
    """T-03 / R-04: a-coord (band), a-own21 (box), x-coord (band): one each, at the middle of the mark or the slot."""
    entry = got["five"]
    ripples = {r["agent"]: (r["x"], r["y"]) for r in entry["model"]["ripples"]}
    slot = entry["model"]["band"]["items"][0]["agents"][0]
    spot = next(s for s in entry["spots"]["iss-00021"] if s["id"] == "a-own21")
    assert len(entry["model"]["ripples"]) == 3
    assert ripples["a-coord"] == (slot["x"] + 26, -2)
    assert ripples["a-own21"] == (spot["x"] + 18, spot["y"] + 8)
    assert "x-coord" in ripples


def test_unknown_marks_end_on_the_edge(got: dict[str, Any]) -> None:
    """T-03 / F-04: a box's lower edge, a frame's upper edge (outward); no arc in a box without both marks."""
    entry = got["unknown"]
    box = entry["nodes"]["iss-00022"]
    _, _, c2, c = _control(_link(entry, "x-coord>a-own22"))
    assert c == ((box["x1"] + box["x2"]) / 2, box["y2"]) and c2[1] > c[1]
    frame = entry["nodes"]["epic-00030"]
    _, _, c2, c = _control(_link(entry, "a-coord>a-e30"))
    assert c == ((frame["x1"] + frame["x2"]) / 2, frame["y1"]) and c2[1] < c[1]
    ids = [link["id"] for link in entry["model"]["links"]]
    assert "a-own21>a-impl21" not in ids
    assert {r["agent"] for r in entry["model"]["ripples"]} == {"a-coord", "x-coord"}


def test_the_key_is_the_same_for_the_same_inputs(tmp_path: Path) -> None:
    """T-03 / R-08: the same objects and equal marks give the same key; another summary, routing or mark does not."""
    assert _run(tmp_path, {"key": True})["key"] == {
        "same": True,
        "copiedMarks": True,
        "otherSummary": False,
        "otherRouting": False,
        "otherWidth": False,
        "otherIds": False,
    }
