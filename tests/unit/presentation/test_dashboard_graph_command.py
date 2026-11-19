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
    from collections.abc import Mapping
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


# --- raw layouts: the room above a box, marks above each other, ends above, beside and below ---------------------

A: dict[str, Any] = {"type": "box", "id": "iss-00001", "x1": 100, "y1": 100, "x2": 278, "y2": 188, "rows": 2}


def _box(scope_id: str, x1: float, y1: float, rows: int = 2) -> dict[str, Any]:
    return {"type": "box", "id": scope_id, "x1": x1, "y1": y1, "x2": x1 + 178, "y2": y1 + 48 + 20 * rows, "rows": rows}


def _raw(
    nodes: list[dict[str, Any]],
    agents: dict[str, list[dict[str, Any]]],
    marks: dict[str, Any],
    routes: tuple[list[dict[str, Any]], ...] = (),
    band: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """A layout of the given nodes, each scope's worktree /w/<id> with its agents, and the main checkout /w/m in the band."""
    scopes = [
        {"id": n["id"], "parent_id": None, "worktrees": [{"path": f"/w/{n['id']}", "branch": n["id"]}]} for n in nodes
    ]
    worktrees = [wt(f"wt-{sid}", f"/w/{sid}", sid, list(ags)) for sid, ags in agents.items()]
    if band:
        worktrees.insert(0, wt("wt-m", "/w/m", "main", band, main=True))
    return {
        "structure": {
            "worktrees": {"status": "ok", "paths": ["/w/m", *(f"/w/{n['id']}" for n in nodes)]},
            "scopes": scopes,
        },
        "summary": summary(*worktrees),
        "layout": {"nodes": nodes, "groups": [], "width": 1000, "height": 1000},
        "marks": marks,
        "routes": [{"pts": pts} for pts in routes],
    }


LEVELS = {2: "c-up", 3: "c-side", 4: "c-down", 5: "c-under"}
PC = {"iss-00001": [ag("p"), ag("c", parent="p")]}
PC_MARKS = {"iss-00001": mark("p", "c")}


def _run_at(up: float, x1: float = 50, x2: float = 400) -> list[dict[str, float]]:
    """A dependency line's horizontal run `up` px above the box A's upper edge."""
    return [{"x": x1, "y": A["y1"] - up}, {"x": x2, "y": A["y1"] - up}]


# the hop p > c in A runs from x 133 to 171: its middle half is 142.5..161.5
RUNS_ABOVE = {
    "run10": (_run_at(10),),
    "run15": (_run_at(15),),
    "run16": (_run_at(16),),
    "runLegs": (_run_at(18, 50, 140), _run_at(18, 164, 400)),  # only where the legs are
    "runNone": (_run_at(9), _run_at(14), _run_at(18)),
}
SCENARIOS |= {
    "room": _raw([A], PC, PC_MARKS),
    # a box 14px above (the rows' gap), and 6px above
    "above14": _raw([A, _box("iss-00002", 100, -2) | {"y2": 86}], PC, PC_MARKS),
    "above6": _raw([A, _box("iss-00002", 100, 6) | {"y2": 94}], PC, PC_MARKS),
    **{name: _raw([A], PC, PC_MARKS, runs) for name, runs in RUNS_ABOVE.items()},
    # the child's mark right below the parent's (the second row's first mark)
    "stacked": _raw(
        [_box("iss-00001", 100, 100, rows=3)],
        {"iss-00001": [ag("p"), ag("c", parent="p")]},
        {"iss-00001": mark("p", "x1", "x2", "x3", "c")},
    ),
    # the child above, beside (the same height) and below the parent; one more right below it
    "levels": _raw(
        [
            _box("iss-00001", 100, 300),
            _box("iss-00002", 400, 40),
            _box("iss-00003", 400, 300),
            _box("iss-00004", 400, 600),
            _box("iss-00005", 100, 700),
        ],
        {"iss-00001": [ag("p")]} | {f"iss-0000{i}": [ag(c, parent="p")] for i, c in LEVELS.items()},
        {"iss-00001": mark("p")} | {f"iss-0000{i}": mark(c) for i, c in LEVELS.items()},
    ),
    # a tree's frame box directed from the band, its two marks one hop
    "tframe": _raw(
        [{"type": "tframe", "id": "iss-00001", "x1": 300, "y1": 200, "x2": 536, "y2": 308, "rows": 2}],
        {"iss-00001": [ag("p", parent="m"), ag("c", parent="p")]},
        {"iss-00001": mark("p", "c")},
        band=[ag("m")],
    ),
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
            "label": "main",  # iss-00668 D-03: the branch; the Primary badge says it is the main checkout
            "own": True,
            "main": True,
            "agents": ["a-coord", "a-research"],
        },
        {"key": "wt-x", "label": "other · main", "own": False, "main": False, "agents": ["x-coord"]},
    ]


def test_the_band_labels_and_their_order(got: dict[str, Any]) -> None:
    """T-01 / R-02, F-03: main first, this repository by label, then the other repositories by label."""
    assert [(it["key"], it["label"]) for it in got["labels"]["items"]] == [
        ("wt-main", "main"),
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
        "BAND": {
            "top": -16,
            "h": 28,
            "left": 24,
            "border": 1,
            "pad": 6,
            "gap": 10,
            "labelGap": 6,
            "slot": 52,
            "perLine": 4,  # iss-00668 D-03: the agents of an item wrap after four
            "lineH": 24,
        },
        "HOP": HOP,
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
    assert [it["labelWidth"] for it in band["items"]] == [27, 85]
    assert got["five"]["model"]["top"] == -16 - 56 - 6  # iss-00648 D-05: the band's highest hop (H 56), 6 above it
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


HOP = {"min": 18, "kx": 0.15, "ky": 0.1, "max": 56, "side": 40, "chord": 12, "room": 3, "low": 8}


def _sample(d: str, n: int = 400) -> list[tuple[float, float]]:
    pts = _points(d)
    assert len(pts) == 4, d
    (px, py), (ax, ay), (bx, by), (cx, cy) = pts
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((
            u**3 * px + 3 * u * u * t * ax + 3 * u * t * t * bx + t**3 * cx,
            u**3 * py + 3 * u * u * t * ay + 3 * u * t * t * by + t**3 * cy,
        ))  # fmt: skip
    return out


def _peak(d: str) -> float:
    return min(y for _, y in _sample(d))


def _height(p: Mapping[str, float], c: Mapping[str, float]) -> float:
    return min(HOP["max"], max(HOP["min"], HOP["kx"] * abs(c["x"] - p["x"]) + HOP["ky"] * abs(c["y"] - p["y"])))


def _all_links(got: dict[str, Any]) -> list[dict[str, Any]]:
    return [link for entry in got.values() if entry.get("model") for link in entry["model"]["links"]]


def _spot(entry: dict[str, Any], scope: str, agent: str) -> dict[str, Any]:
    return next(s for s in entry["spots"][scope] if s["id"] == agent)


def test_ends_of_marks_and_the_band_sit_on_the_upper_edge_right_above_the_mark(got: dict[str, Any]) -> None:
    """T-01 / R-01: the band slot's middle on its item's upper edge; a box's, a tree frame box's and a nested frame's
    heading mark's middle on that box's or frame's upper edge."""
    five = got["five"]
    link = _link(five, "a-coord>a-own21")
    slot = five["model"]["band"]["items"][0]["agents"][0]
    spot = _spot(five, "iss-00021", "a-own21")
    assert link["from"] == {"x": slot["x"] + slot["w"] / 2, "y": -16}
    assert link["to"] == {"x": spot["x"] + spot["w"] / 2, "y": five["nodes"]["iss-00021"]["y1"]}
    frame = _link(five, "a-coord>a-e30")
    fspot = five["spots"]["epic-00030"][0]
    assert frame["to"] == {"x": fspot["x"] + fspot["w"] / 2, "y": five["nodes"]["epic-00030"]["y1"]}
    tframe = got["tframe"]
    tnode = tframe["nodes"]["iss-00001"]
    assert tnode["type"] == "tframe"
    tspot = _spot(tframe, "iss-00001", "p")
    assert _link(tframe, "m>p")["to"] == {"x": tspot["x"] + tspot["w"] / 2, "y": tnode["y1"]}


def test_ends_on_groups_and_frames_sit_on_the_middle_of_the_upper_edge(got: dict[str, Any]) -> None:
    """T-01 / R-01: a folded group's upper edge; a frame holding the other end: its upper edge too (not inside)."""
    folded = got["folded"]
    group = next(g for g in folded["groups"] if "epic-00008" in g["ids"])
    assert _link(folded, "a-coord>a-own09")["to"] == {"x": (group["x1"] + group["x2"]) / 2, "y": group["y1"]}
    hidden = got["hidden"]
    frame = hidden["nodes"]["epic-00030"]
    link = _link(hidden, "a-e30>a-own31")  # the parent's mark is in the frame's heading: the frame holds it
    assert link["from"]["y"] == link["to"]["y"] == frame["y1"]


def test_lines_leaving_one_edge_are_spread(got: dict[str, Any]) -> None:
    """T-01 / R-01: the three lines into the frame's upper edge are 10px apart around its middle, in the links' order."""
    hidden = got["hidden"]
    frame = hidden["nodes"]["epic-00030"]
    mid = (frame["x1"] + frame["x2"]) / 2
    ends = [_link(hidden, i)["to"] for i in ("a-coord>a-help31", "a-coord>a-two31", "a-e30>a-own31")]
    assert ends == [{"x": mid + off, "y": frame["y1"]} for off in (-10, 0, 10)]


def test_no_line_inside_one_group_or_ancestor_frame(got: dict[str, Any]) -> None:
    """T-01 / R-01: both ends in the same ancestor frame without a mark: no line."""
    ids = [link["id"] for link in got["hidden"]["model"]["links"]]
    assert "a-own31>a-impl31" not in ids
    assert len(ids) == 4


def test_unknown_marks_end_on_the_middle_of_the_upper_edge(got: dict[str, Any]) -> None:
    """T-01 / F-01: a box's and a frame's upper edge; no hop in a box without both marks."""
    entry = got["unknown"]
    box = entry["nodes"]["iss-00022"]
    assert _link(entry, "x-coord>a-own22")["to"] == {"x": (box["x1"] + box["x2"]) / 2, "y": box["y1"]}
    frame = entry["nodes"]["epic-00030"]
    assert _link(entry, "a-coord>a-e30")["to"] == {"x": (frame["x1"] + frame["x2"]) / 2, "y": frame["y1"]}
    ids = [link["id"] for link in entry["model"]["links"]]
    assert "a-own21>a-impl21" not in ids
    assert {r["agent"] for r in entry["model"]["ripples"]} == {"a-coord", "x-coord"}


def test_no_line_has_stubs(got: dict[str, Any]) -> None:
    """T-01 / R-01: nothing is drawn inside a box."""
    links = _all_links(got)
    assert links and all(link["stubs"] == [] for link in links)


def test_every_line_leaves_and_enters_from_above(got: dict[str, Any]) -> None:
    """T-01 / R-01: the first control point above `from`, the last above `to`, with the child above, beside or below."""
    levels = got["levels"]
    to_y = {c: _link(levels, f"p>{c}")["to"]["y"] for c in ("c-up", "c-side", "c-down", "c-under")}
    from_y = _link(levels, "p>c-up")["from"]["y"]
    assert to_y["c-up"] < from_y == to_y["c-side"] < to_y["c-down"]
    for link in _all_links(got):
        (_, c1y), (_, c2y) = _control(link)[1:3]
        assert c1y < link["from"]["y"] and c2y < link["to"]["y"], link


def test_a_curve_is_a_hop_of_height_h_above_the_higher_end(got: dict[str, Any]) -> None:
    """T-01 / R-02: every curve peaks H above its higher end, H from dx and dy within 18..56."""
    curves = [link for link in _all_links(got) if link["kind"] == "curve"]
    assert len(curves) > 10
    for link in curves:
        high = min(link["from"]["y"], link["to"]["y"])
        h = _height(link["from"], link["to"])
        assert _peak(link["d"]) == pytest.approx(high - h, abs=0.5), link
        assert link["peak"] == pytest.approx(high - h, abs=0.5), link


HOP_CASES = [
    # (P, C, ceiling or None)
    ({"x": 0, "y": 0}, {"x": 60, "y": 0}, None),
    ({"x": 0, "y": 0}, {"x": 160, "y": 0}, None),
    ({"x": 0, "y": 0}, {"x": 160, "y": 100}, None),
    ({"x": 0, "y": 0}, {"x": 260, "y": 100}, None),
    ({"x": 260, "y": 100}, {"x": 0, "y": 0}, None),
    ({"x": 0, "y": 0}, {"x": 300, "y": 700}, None),
    ({"x": 0, "y": 700}, {"x": 300, "y": 0}, None),
    ({"x": 0, "y": 0}, {"x": 20, "y": 700}, None),
    ({"x": 0, "y": 0}, {"x": 0, "y": 200}, None),
    ({"x": 0, "y": 30}, {"x": 0, "y": 0}, None),
    ({"x": 100, "y": 24}, {"x": 600, "y": 600}, 4),
    ({"x": 0, "y": 10}, {"x": 300, "y": 600}, 4),
]


@pytest.fixture(scope="module")
def hops(tmp_path_factory: pytest.TempPathFactory) -> list[dict[str, Any]]:
    return _run(tmp_path_factory.mktemp("hop"), {"hop": [list(c) for c in HOP_CASES]})["hop"]


def test_hop_peaks_exactly_h_above_the_higher_end(hops: list[dict[str, Any]]) -> None:
    """T-01 / R-02: at the same height and at different heights (700px apart too), the peak is H (±0.5) above."""
    heights = []
    for (p, c, ceiling), h in zip(HOP_CASES, hops, strict=True):
        if ceiling is not None:
            continue
        want = _height(p, c)
        heights.append(want)
        assert 18 <= want <= 56
        assert _peak(h["d"]) == pytest.approx(min(p["y"], c["y"]) - want, abs=0.5), (p, c, h)
        assert h["peak"] == pytest.approx(min(p["y"], c["y"]) - want, abs=0.5)
        assert h["len"] % 8 == 0
    # H grows with dx and with dy, from the floor to the ceiling
    assert heights[:4] == [18, 24, 34, 49] and heights[5] == heights[7] == 56


def test_hop_between_ends_above_each_other_bulges_sideways(hops: list[dict[str, Any]]) -> None:
    """T-01 / R-02: dx 0: a point 8px or more off the vertical line through both ends."""
    for (p, c, ceiling), h in zip(HOP_CASES, hops, strict=True):
        if p["x"] == c["x"] and ceiling is None:
            assert max(abs(x - p["x"]) for x, _ in _sample(h["d"])) >= 8, (p, c, h)


def test_hop_stays_below_the_ceiling_but_at_least_low_above_the_higher_end(hops: list[dict[str, Any]]) -> None:
    """T-01 / F-02: the peak is lowered to the ceiling, never closer than HOP.low to the higher end."""
    for (p, c, ceiling), h in zip(HOP_CASES, hops, strict=True):
        if ceiling is None:
            continue
        want = min(ceiling, min(p["y"], c["y"]) - HOP["low"])
        assert _peak(h["d"]) == pytest.approx(want, abs=0.5) and _peak(h["d"]) >= want - 0.5, (p, c, h)


def _bulge(link: dict[str, Any]) -> float:
    """A hop's height in one box from its control points (handles 4d/3)."""
    p, c1, _, _ = _control(link)
    return round((p[1] - c1[1]) * 3 / 4, 1)


def test_hops_in_one_box_frame_heading_and_band_item(got: dict[str, Any]) -> None:
    """T-01 / R-03: one row, two rows, a tree frame box, a frame's heading and a band item: from the upper edge right
    above each mark back to the same edge, 18 above it, the chord 12 or more."""
    five, epic, tframe = got["five"], got["epic"], got["tframe"]
    cases = [
        (five, "a-own21>a-impl21", five["nodes"]["iss-00021"]["y1"], ("iss-00021", "a-own21", "a-impl21")),
        (epic, "a-p23>a-c23", epic["nodes"]["iss-00023"]["y1"], ("iss-00023", "a-p23", "a-c23")),
        (epic, "a-e30>a-e30b", epic["nodes"]["epic-00030"]["y1"], ("epic-00030", "a-e30", "a-e30b")),
        (tframe, "p>c", tframe["nodes"]["iss-00001"]["y1"], ("iss-00001", "p", "c")),
        (got["room"], "p>c", A["y1"], ("iss-00001", "p", "c")),
        (five, "a-coord>a-research", -16, None),
    ]
    for entry, link_id, edge, marks in cases:
        link = _link(entry, link_id)
        assert link["kind"] == "arc", link_id
        assert link["from"]["y"] == link["to"]["y"] == edge, link_id
        assert _bulge(link) == 18 and link["bulge"] == 18, link_id
        assert _peak(link["d"]) == pytest.approx(edge - 18, abs=0.5) and link["peak"] == edge - 18, link_id
        assert abs(link["to"]["x"] - link["from"]["x"]) >= 12, link_id
        if marks:
            scope, parent, child = marks
            sp, sc = _spot(entry, scope, parent), _spot(entry, scope, child)
            assert (link["from"]["x"], link["to"]["x"]) == (sp["x"] + sp["w"] / 2, sc["x"] + sc["w"] / 2), link_id
    two = _spot(epic, "iss-00023", "a-p23")["y"] != _spot(epic, "iss-00023", "a-c23")["y"]
    assert two  # the two marks are on different rows


def test_a_hop_between_marks_above_each_other_is_widened_to_12(got: dict[str, Any]) -> None:
    """T-01 / R-03: the second row's first mark right below the first: 12 apart around their middle, the parent left."""
    stacked = got["stacked"]
    sp, sc = _spot(stacked, "iss-00001", "p"), _spot(stacked, "iss-00001", "c")
    assert sp["x"] == sc["x"] and sp["y"] != sc["y"]
    link = _link(stacked, "p>c")
    mid = sp["x"] + sp["w"] / 2
    assert (link["from"]["x"], link["to"]["x"]) == (mid - 6, mid + 6)
    assert _bulge(link) == 18


def test_hops_with_little_room_above(got: dict[str, Any]) -> None:
    """T-01 / R-03: 14px above: 11, crowded, no overlap; 6px above: 8, crowded and overlapping; enough room: 18."""
    assert _bulge(_link(got["room"], "p>c")) == 18
    assert got["room"]["model"]["audit"]["crowded"] == 0
    low = _link(got["above14"], "p>c")
    assert _bulge(low) == 11 and low["bulge"] == 11 and low["peak"] == A["y1"] - 11
    audit = got["above14"]["model"]["audit"]
    assert (audit["crowded"], audit["boxOverlaps"], audit["edgeOverlaps"]) == (1, 0, 0)
    least = _link(got["above6"], "p>c")
    assert _bulge(least) == 8
    audit = got["above6"]["model"]["audit"]
    assert (audit["crowded"], audit["boxOverlaps"]) == (1, 1)


@pytest.mark.parametrize(
    ("name", "height", "overlaps"),
    [("run10", 18, 0), ("run15", 18, 0), ("run16", 13, 0), ("runLegs", 18, 0), ("runNone", 18, 1)],
)
def test_a_hops_peak_keeps_3px_from_the_dependency_runs(
    got: dict[str, Any], name: str, height: int, overlaps: int
) -> None:
    """T-01 / R-03 (D-03): the highest height whose peak is 3px or more from every run over the hop's middle half; the
    legs crossing a run do not count; no such height: the upper limit, counted as an edge overlap."""
    link = _link(got[name], "p>c")
    assert (link["from"]["x"], link["to"]["x"]) == (133, 171)
    assert _bulge(link) == height and link["bulge"] == height and link["peak"] == A["y1"] - height
    audit = got[name]["model"]["audit"]
    assert (audit["edgeOverlaps"], audit["crowded"], audit["boxOverlaps"]) == (overlaps, 0, 0)


def test_each_line_carries_the_childs_mark(got: dict[str, Any]) -> None:
    """T-01 / R-04: the child's mark (a band slot: band true); null for a group, an ancestor frame and an unknown mark."""
    five = got["five"]
    rect = lambda s: {"x": s["x"], "y": s["y"], "w": s["w"], "h": s["h"]}  # noqa: E731
    assert _link(five, "a-coord>a-own21")["mark"] == rect(_spot(five, "iss-00021", "a-own21")) | {"band": False}
    assert _link(five, "a-own21>a-impl21")["mark"] == rect(_spot(five, "iss-00021", "a-impl21")) | {"band": False}
    assert _link(five, "a-coord>a-e30")["mark"] == rect(five["spots"]["epic-00030"][0]) | {"band": False}
    slot = five["model"]["band"]["items"][0]["agents"][1]
    assert slot["id"] == "a-research"
    assert _link(five, "a-coord>a-research")["mark"] == rect(slot) | {"band": True}
    assert _link(got["folded"], "a-coord>a-own09")["mark"] is None
    assert _link(got["hidden"], "a-e30>a-own31")["mark"] is None
    assert _link(got["unknown"], "x-coord>a-own22")["mark"] is None
    assert _link(got["unknown"], "a-coord>a-e30")["mark"] is None


def test_the_top_holds_every_hop_above_the_band(got: dict[str, Any]) -> None:
    """T-01 / R-02 (D-05): the world's top is 6 above the highest peak, the band's hops and the band item's own hop too."""
    model = got["five"]["model"]
    peaks = [link["peak"] for link in model["links"]]
    assert model["top"] == min(-32, min(peaks) - 6)
    assert model["top"] <= _link(got["five"], "a-coord>a-research")["peak"] - 6 == -16 - 18 - 6
    assert model["top"] < -16 - 18 - 6  # the band's hops to the boxes rise higher still
    for name in ("levels", "tframe"):
        top = got[name]["model"]["top"]
        assert top == min(
            0,
            *(link["peak"] - 6 for link in got[name]["model"]["links"]),
            *([-32] if got[name]["model"]["band"] else []),
        )


def test_the_synthetic_layouts_have_no_overlap(got: dict[str, Any]) -> None:
    """T-01 / R-03: boxOverlaps and edgeOverlaps are 0 with the routed layouts."""
    for name in ("five", "hidden", "folded", "epic", "others", "labels"):
        audit = got[name]["model"]["audit"]
        assert (audit["boxOverlaps"], audit["edgeOverlaps"], audit["crowded"]) == (0, 0, 0), name
        assert got[name]["routes"], name
    assert got["five"]["model"]["audit"] == {"links": 5, "arcs": 2, "boxOverlaps": 0, "edgeOverlaps": 0, "crowded": 0}


def test_the_epic_coordinator_hops_from_the_frames_top_into_the_issue(got: dict[str, Any]) -> None:
    """T-01 / R-01, R-02: from the Epic frame's heading mark up out of the frame's top edge, down into the Issue's top."""
    epic = got["epic"]
    link = _link(epic, "a-e30>a-own33")
    assert link["kind"] == "curve"
    assert link["from"]["y"] == epic["nodes"]["epic-00030"]["y1"]
    assert link["to"]["y"] == epic["nodes"]["iss-00033"]["y1"]
    assert _peak(link["d"]) == pytest.approx(link["from"]["y"] - _height(link["from"], link["to"]), abs=0.5)


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


# --- iss-00668 T-03: the badges, the counts, the fold and the wrapped agents -----------------------------------


def _bi(key: str, label: str, agents: int, **extra: Any) -> dict[str, Any]:
    return {"key": key, "label": label, "agents": [f"{key}-{i}" for i in range(agents)], **extra}


BAND_ROWS = [
    # the main checkout with a badge, an Unlinked worktree with a count, a fold; one row, one line
    {
        "rows": [
            {
                "key": "",
                "left": 24,
                "top": -16,
                "lead": "Unscoped",
                "leadTitle": "Worktrees not shown as a Scope box",
                "items": [
                    _bi("p", "main", 1, badge="primary"),
                    _bi("u", "topic", 2, badge="unlinked", count=3),
                    _bi("f", "+3", 0, kind="fold"),
                    _bi("n", "plain", 0),
                ],
            }
        ]
    },
    # five agents wrap into two lines; the row and its other item take the height; a parent and a child on two lines
    {
        "rows": [{"key": "", "left": 24, "top": -40, "lead": None, "items": [_bi("w", "wide", 5), _bi("s", "one", 1)]}],
        "pairs": [["w-0", "w-4"], ["w-4", "s-0"]],
    },
    # no pair: a row is still drawn
    {"rows": [{"key": "", "left": 24, "top": -16, "lead": None, "items": [_bi("p", "main", 0, badge="primary")]}]},
    # nine agents: three lines
    {"rows": [{"key": "", "left": 0, "top": 0, "lead": None, "items": [_bi("w", "wide", 9)]}]},
]


@pytest.fixture(scope="module")
def rows(tmp_path_factory: pytest.TempPathFactory) -> list[dict[str, Any]]:
    return _run(tmp_path_factory.mktemp("band-rows"), {"bandRows": BAND_ROWS})["bandRows"]


def test_badges_and_counts_widen_an_item_and_a_fold_has_no_agents(rows: list[dict[str, Any]]) -> None:
    """T-03 / R-02, R-04: the badge and the count add their small text and a gap; the fold is its label alone."""
    band = rows[0]["band"]
    p, u, f, n = band["items"]
    primary = 38 + 6  # ceil(47 × 0.8) + labelGap
    unlinked = 43 + 6  # ceil(53 × 0.8) + labelGap
    count = 20 + 6  # ceil(24 × 0.8) + labelGap
    assert p["w"] == 2 + 12 + p["labelWidth"] + 6 + primary + 52
    assert u["w"] == 2 + 12 + u["labelWidth"] + 6 + unlinked + count + 52 * 2
    assert f["w"] == 2 + 12 + f["labelWidth"]
    assert f["agents"] == [] and f["kind"] == "fold"
    assert n["w"] == 2 + 12 + n["labelWidth"] + 6
    # the agents sit after the label, the badge and the count
    assert u["agents"][0]["x"] == u["x"] + 1 + 6 + u["labelWidth"] + 6 + unlinked + count
    assert (p["badge"], u["badge"], u["count"]) == ("primary", "unlinked", 3)
    # the lead's text comes first, the items 10 apart
    assert p["x"] == 24 + 53 + 6
    assert rows[0]["widths"][0] == 53 + 6 + sum(it["w"] for it in band["items"]) + 10 * 3
    assert band["rows"][0]["leadTitle"] == "Worktrees not shown as a Scope box"
    assert rows[0]["heights"] == [28] and band["h"] == 28


def test_five_agents_wrap_and_the_row_takes_the_tallest_item(rows: list[dict[str, Any]]) -> None:
    """T-03 / R-09: four columns, the item 28 + 24 high, the row and its other item as high."""
    band = rows[1]["band"]
    wide, one = band["items"]
    assert rows[1]["heights"] == [52]
    assert (wide["h"], one["h"], band["h"], band["rows"][0]["h"]) == (52, 52, 52, 52)
    assert wide["w"] == 2 + 12 + wide["labelWidth"] + 6 + 52 * 4
    left = wide["x"] + 1 + 6 + wide["labelWidth"] + 6
    assert [(a["x"], a["y"], a["w"], a["h"]) for a in wide["agents"]] == [
        (left + 52 * (i % 4), -40 + 24 * (i // 4), 52, 28) for i in range(5)
    ]
    assert rows[3]["heights"] == [28 + 24 * 2]


def test_a_wrapped_agents_end_sits_on_the_items_upper_edge(rows: list[dict[str, Any]]) -> None:
    """T-03 / R-09: the end at the slot's centre on the item's top; parent and child in one item make an arc."""
    links = {link["id"]: link for link in rows[1]["links"]}
    wide, one = rows[1]["band"]["items"]
    arc = links["w-0>w-4"]
    assert arc["kind"] == "arc"
    assert arc["from"]["y"] == arc["to"]["y"] == wide["y"]
    curve = links["w-4>s-0"]
    assert curve["kind"] == "curve"
    slot = wide["agents"][4]
    assert curve["from"] == {"x": slot["x"] + 26, "y": wide["y"]}
    assert curve["to"] == {"x": one["agents"][0]["x"] + 26, "y": one["y"]}


def test_a_row_without_a_pair_still_has_a_band(rows: list[dict[str, Any]]) -> None:
    """T-03 / R-02: commandModel draws the row's items with no pair."""
    assert rows[2]["band"] is not None
    assert [it["key"] for it in rows[2]["band"]["items"]] == ["p"]
    assert rows[2]["links"] == []
