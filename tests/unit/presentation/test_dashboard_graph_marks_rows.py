"""The rows of the agents' marks in the structure graph's boxes and frames (iss-00620), run in node like the other graph checks.

The page measures the marks it drew and passes their widths to the layout as the options' marks
({Scope id: {lead, items, gap}}); the layout decides each box's and frame's rows of marks with markRows and grows the box
(the nested frame's heading) by MARK_ROW for every row past the first. The widths here are close to the component's sm
marks: the other marks 60px, an agent's mark 36px, 2px between the agents' marks.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import AUDIT_KEYS, _context, _run, _small

GAP = 2
AGENT = 36
LEAD = 60


def mark(agents: int, lead: int = LEAD) -> dict[str, Any]:
    return {"lead": lead, "items": [AGENT] * agents, "gap": GAP}


# --- T-01: markRows ---------------------------------------------------------------------------------------------

# [m, avail, reserve, rows]
ROW_CASES: list[tuple[Any, float, float, int]] = [
    (None, 152, 0, 1),  # no marks
    ({"lead": 60, "items": [], "gap": 2}, 152, 0, 1),  # no agent
    (mark(2), 152, 0, 1),  # 60 + 74 fits the rest of the first row
    ({"lead": 40, "items": [36, 36, 36], "gap": 2}, 152, 0, 1),  # 40 + 112 = 152: just fits
    ({"lead": 41, "items": [36, 36, 36], "gap": 2}, 152, 0, 2),  # 153: one px over, the agents move to the next row
    (mark(3), 152, 0, 2),  # 60 + 112 > 152: one row of agents below
    (mark(6), 152, 0, 3),  # four agents a row (150 ≤ 152), so two rows below
    (mark(6, lead=0), 152, 0, 2),  # no other mark: the agents wrap from the first row
    (mark(3, lead=0), 152, 0, 1),  # no other mark and the agents fit
    ({"lead": 0, "items": [200, 36], "gap": 2}, 152, 0, 2),  # a mark wider than the box takes a row of its own
    ({"lead": 10, "items": [200, 36], "gap": 2}, 152, 0, 3),
    ({"lead": 0, "items": [200], "gap": 2}, 152, 0, 1),
    (mark(3), 274, 96, 1),  # 60 + 96 + 112 = 268 ≤ 274: beside the title
    (mark(3), 274, 103, 2),  # 275: below the heading
    ({"lead": 0, "items": [36, 36, 36], "gap": 2}, 200, 96, 2),  # the title alone reserves the first row
]


@pytest.fixture(scope="module")
def rows(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    request = {"documents": {}, "markRows": [[m, avail, reserve] for m, avail, reserve, _ in ROW_CASES], "checks": []}
    return _run(tmp_path_factory.mktemp("mark-rows"), request)


def test_the_row_constants_are_exported(rows: dict[str, Any]) -> None:
    assert rows["markConsts"] == {"MARK_ROW": 20, "MARK_INSET": {"box": 26}, "FRAME_TITLE_MIN": 96}


def test_mark_rows_follows_the_rule_of_the_rows(rows: dict[str, Any]) -> None:
    """T-01: the first row's right when every agent fits, else 1 + the agents' rows, or the agents' rows alone."""
    assert rows["markRows"] == [want for *_, want in ROW_CASES]


# --- T-02, T-03, T-05: the layout with marks --------------------------------------------------------------------

# the small structure: Epics 10, 20, 30 with their Issues
SMALL_MARKS = {
    "iss-00021": mark(1),
    "iss-00022": mark(3),
    "iss-00023": mark(6),
    "iss-00011": mark(6, lead=0),
    "epic-00030": mark(6),
    "epic-00010": mark(6),
}
# every box and frame of the small structure with one agent: all of them on one row
ONE_ROW = {
    sid: mark(1, lead=20)
    for sid in [
        *(f"iss-{n:05d}" for n in (2, 3, 5, 7, 9, *range(11, 18), 21, 22, 23, 24, 25, 31, 32, 33, 34)),
        *(f"epic-{n:05d}" for n in (1, 6, 8, 10, 20, 30)),
    ]
}
WAYS = {
    "nest|all": {"mode": "nest", "range": "all"},
    "nest|now": {"mode": "nest", "range": "now"},
    "nest|next": {"mode": "nest", "range": "next"},
    "tree|all": {"mode": "tree", "range": "all"},
    "tree|now": {"mode": "tree", "range": "now"},
    "nest|374": {"mode": "nest", "range": "all", "width": 374},
}
VARIANTS: dict[str, Any] = {"none": None, "empty": {}, "one": ONE_ROW, "marks": SMALL_MARKS}


def _layouts() -> dict[str, dict[str, Any]]:
    out = {}
    for way, opts in WAYS.items():
        for variant, marks in VARIANTS.items():
            for how in ("plain", "routed"):
                out[f"{way}|{variant}|{how}"] = {**opts, **({} if marks is None else {"marks": marks})}
    return out


@pytest.fixture(scope="module")
def laid(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    layouts = _layouts()
    request = {
        "documents": {"small": _small()},
        "layouts": {"small": layouts},
        "routed": {"small": [key for key in layouts if key.endswith("|routed")]},
        "nodeRows": {"small": list(layouts)},
        "checks": ["layout"],
    }
    return _run(tmp_path_factory.mktemp("mark-layout"), request)["layout"]["small"]


def _nodes(entry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {n["id"]: n for n in entry["nodes"]}


def _kept(entry: dict[str, Any]) -> str:
    return json.dumps({key: entry[key] for key in ("nodes", "groups", "edges", "trunks", "wraps")}, sort_keys=True)


def test_without_marks_or_with_one_row_the_layout_is_the_same(laid: dict[str, Any]) -> None:
    """T-03: no marks, {} and marks of one row each lay out as the layout without marks."""
    differ = [
        f"{way}|{variant}|{how}"
        for way in WAYS
        for how in ("plain", "routed")
        for variant in ("empty", "one")
        if _kept(laid[f"{way}|{variant}|{how}"]) != _kept(laid[f"{way}|none|{how}"])
    ]
    assert differ == []
    for entry in laid.values():
        assert all(("rows" in n) == ("agents" in n) for n in entry["nodes"])


def test_a_box_grows_by_a_row_of_marks(laid: dict[str, Any]) -> None:
    """T-02: a box with one, three and six agents is 88, 108 and 128 tall, nested and in the tree; widths stay."""
    for way in ("nest|all", "tree|all"):
        plain = _nodes(laid[f"{way}|none|plain"])
        nodes = _nodes(laid[f"{way}|marks|plain"])
        height = {sid: nodes[sid]["y2"] - nodes[sid]["y1"] for sid in ("iss-00021", "iss-00022", "iss-00023")}
        assert height == {"iss-00021": 88, "iss-00022": 108, "iss-00023": 128}, way
        assert "rows" not in nodes["iss-00021"] and "agents" not in nodes["iss-00021"]
        assert (nodes["iss-00022"]["rows"], nodes["iss-00022"]["agents"]) == (2, "below")
        assert (nodes["iss-00023"]["rows"], nodes["iss-00023"]["agents"]) == (3, "below")
        assert (nodes["iss-00011"]["rows"], nodes["iss-00011"]["agents"]) == (2, "wrap")
        assert nodes["iss-00011"]["y2"] - nodes["iss-00011"]["y1"] == 108
        assert {sid: n["x2"] - n["x1"] for sid, n in nodes.items()} == {
            sid: n["x2"] - n["x1"] for sid, n in plain.items()
        }


def test_a_tree_frame_box_grows_too(laid: dict[str, Any]) -> None:
    """T-02: the tree's frame box (236 wide) with six agents holds five a row: 1 + 2 rows."""
    nodes = _nodes(laid["tree|all|marks|plain"])
    frame = nodes["epic-00030"]
    assert frame["type"] == "tframe"
    assert (frame["rows"], frame["agents"], frame["y2"] - frame["y1"]) == (3, "below", 128)


def test_a_nested_frame_heading_grows_and_its_body_moves_down(laid: dict[str, Any]) -> None:
    """T-02: a nested frame with two rows has a heading MARK_ROW taller; what it holds moves down as much."""
    before = laid["nest|all|none|plain"]
    after = laid["nest|all|marks|plain"]
    frame0, frame1 = _nodes(before)["epic-00030"], _nodes(after)["epic-00030"]
    assert frame1["type"] == "frame"
    assert (frame1["rows"], frame1["agents"]) == (2, "below")
    assert frame1["x2"] - frame1["x1"] == frame0["x2"] - frame0["x1"]
    head0 = before["heads"]["epic-00030"] - frame0["y1"]
    head1 = after["heads"]["epic-00030"] - frame1["y1"]
    assert head1 == head0 + 20
    assert (frame1["y2"] - frame1["y1"]) - (frame0["y2"] - frame0["y1"]) == 20
    for sid in ("iss-00032", "iss-00033", "iss-00034"):
        n0, n1 = _nodes(before)[sid], _nodes(after)[sid]
        assert n1["y1"] - frame1["y1"] == n0["y1"] - frame0["y1"] + 20, sid


def test_node_mark_rows_agrees_with_the_layout(laid: dict[str, Any]) -> None:
    """T-05: the page's nodeMarkRows of a laid out node equals the rows the layout used."""
    differ = [
        (key, row)
        for key, entry in laid.items()
        for row in entry["nodeRows"]
        if row["want"] != row["got"]
    ]
    assert differ == []
    assert any(row["got"] > 1 for entry in laid.values() for row in entry["nodeRows"])


# --- T-04: the routing check with grown boxes ---------------------------------------------------------------------

CONTEXT_MARKS = {
    "iss-00005": mark(1),
    "iss-00006": mark(3),
    "iss-00007": mark(6),
    "iss-00013": mark(6, lead=0),
    "iss-00021": mark(3),
    "epic-00002": mark(6),
    "epic-00030": mark(3),
    "init-00001": mark(6),
}


@pytest.fixture(scope="module")
def audited(tmp_path_factory: pytest.TempPathFactory) -> list[dict[str, Any]]:
    request = {
        "documents": {"small": _small(), "context": _context()},
        "marks": {"small": SMALL_MARKS, "context": CONTEXT_MARKS},
        "checks": ["audit"],
    }
    return _run(tmp_path_factory.mktemp("mark-audit"), request)["audit"]


def test_grown_boxes_route_cleanly(audited: list[dict[str, Any]]) -> None:
    """T-04: nested and tree × all, now, next × focus, with boxes of one, three and six agents: no violation."""
    assert {run["name"] for run in audited} == {"small", "context"}
    assert all("marks" in run["opts"] for run in audited)
    assert {run["opts"]["mode"] for run in audited} == {"nest", "tree"}
    assert any(run["opts"].get("focus") for run in audited)
    dirty = [
        {"name": run["name"], "opts": {k: v for k, v in run["opts"].items() if k != "marks"}}
        | {key: run[key] for key in AUDIT_KEYS if run[key]}
        for run in audited
        if any(run[key] for key in AUDIT_KEYS)
    ]
    assert dirty == []
