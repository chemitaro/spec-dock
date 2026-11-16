"""The rows of the agents' marks in the structure graph's boxes and frames (iss-00620), run in node like the other graph checks.

The page measures the agents' marks it drew and passes their widths to the layout as the options' marks
({Scope id: {items, gap}}). A box or frame with an agent puts the marks on rows of their own below its other marks
(its heading), left aligned and wrapping at the box's inner width: markRows is 1 without an agent, else 1 + the rows the
marks take, and the box (the nested frame's heading) grows by MARK_ROW for every row past the first. The widths here are
close to the component's sm marks: an agent's mark 36px, 2px between them.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from tests.unit.presentation.test_dashboard_graph_js import AUDIT_KEYS, _context, _run, _small

GAP = 2
AGENT = 36


def mark(agents: int) -> dict[str, Any]:
    return {"items": [AGENT] * agents, "gap": GAP}


# --- T-01: markRows ---------------------------------------------------------------------------------------------

# [m, avail, rows]
ROW_CASES: list[tuple[Any, float, int]] = [
    (None, 152, 1),  # no marks: no row of agents
    ({"items": [], "gap": 2}, 152, 1),  # no agent
    (mark(1), 152, 2),  # one agent: a row of its own
    (mark(4), 152, 2),  # 4 × 36 + 3 × 2 = 150
    ({"items": [50, 50, 48], "gap": 2}, 152, 2),  # 152: just fits
    ({"items": [50, 50, 49], "gap": 2}, 152, 3),  # 153: one px over
    (mark(6), 152, 3),  # four and two
    ({"items": [200, 36], "gap": 2}, 152, 3),  # a mark wider than the box takes a row of its own
    ({"items": [200], "gap": 2}, 152, 2),
    ({"items": [75, 75], "gap": 2}, 152, 2),  # the gap counts: 152
    ({"items": [75, 75], "gap": 3}, 152, 3),  # 153
]


@pytest.fixture(scope="module")
def rows(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    request = {"documents": {}, "markRows": [[m, avail] for m, avail, _ in ROW_CASES], "checks": []}
    return _run(tmp_path_factory.mktemp("mark-rows"), request)


def test_the_row_constants_are_exported(rows: dict[str, Any]) -> None:
    assert rows["markConsts"] == {"MARK_ROW": 20, "MARK_INSET": {"box": 26}}


def test_mark_rows_follows_the_rule_of_the_rows(rows: dict[str, Any]) -> None:
    """T-01: 1 without an agent, else 1 + the rows the agents' marks take, packed left to right."""
    assert rows["markRows"] == [want for *_, want in ROW_CASES]


# --- T-02, T-03, T-05: the layout with marks --------------------------------------------------------------------

# the small structure: Epics 10, 20, 30 with their Issues
SMALL_MARKS = {
    "iss-00021": mark(1),
    "iss-00022": mark(3),
    "iss-00023": mark(6),
    "epic-00030": mark(3),
    "epic-00010": mark(6),
}
# every box and frame of the small structure without an agent
NO_AGENT = {
    sid: {"items": [], "gap": GAP}
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
VARIANTS: dict[str, Any] = {"none": None, "empty": {}, "noagent": NO_AGENT, "marks": SMALL_MARKS}


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


def test_without_an_agent_the_layout_is_the_same(laid: dict[str, Any]) -> None:
    """T-03: no marks, {} and marks without an agent lay out as the layout without marks."""
    differ = [
        f"{way}|{variant}|{how}"
        for way in WAYS
        for how in ("plain", "routed")
        for variant in ("empty", "noagent")
        if _kept(laid[f"{way}|{variant}|{how}"]) != _kept(laid[f"{way}|none|{how}"])
    ]
    assert differ == []
    for way in WAYS:
        assert all("rows" not in n for n in laid[f"{way}|none|plain"]["nodes"])


def test_a_box_grows_by_its_rows_of_agents(laid: dict[str, Any]) -> None:
    """T-02: a box with one, three and six agents is 108, 108 and 128 tall, nested and in the tree; widths stay."""
    for way in ("nest|all", "tree|all"):
        plain = _nodes(laid[f"{way}|none|plain"])
        nodes = _nodes(laid[f"{way}|marks|plain"])
        height = {sid: nodes[sid]["y2"] - nodes[sid]["y1"] for sid in ("iss-00021", "iss-00022", "iss-00023")}
        assert height == {"iss-00021": 108, "iss-00022": 108, "iss-00023": 128}, way
        assert [nodes[sid]["rows"] for sid in ("iss-00021", "iss-00022", "iss-00023")] == [2, 2, 3]
        assert "rows" not in nodes["iss-00024"] and nodes["iss-00024"]["y2"] - nodes["iss-00024"]["y1"] == 88
        assert {sid: n["x2"] - n["x1"] for sid, n in nodes.items()} == {
            sid: n["x2"] - n["x1"] for sid, n in plain.items()
        }


def test_a_tree_frame_box_grows_too(laid: dict[str, Any]) -> None:
    """T-02: the tree's frame box (236 wide, 210 inside) with six agents holds five a row: 1 + 2 rows."""
    nodes = _nodes(laid["tree|all|marks|plain"])
    frame = nodes["epic-00010"]
    assert frame["type"] == "tframe"
    assert (frame["rows"], frame["y2"] - frame["y1"]) == (3, 128)


def test_a_nested_frame_heading_grows_and_its_body_moves_down(laid: dict[str, Any]) -> None:
    """T-02: a nested frame with a row of agents has a heading MARK_ROW taller; what it holds moves down as much."""
    before = laid["nest|all|none|plain"]
    after = laid["nest|all|marks|plain"]
    frame0, frame1 = _nodes(before)["epic-00030"], _nodes(after)["epic-00030"]
    assert frame1["type"] == "frame"
    assert frame1["rows"] == 2
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
    differ = [(key, row) for key, entry in laid.items() for row in entry["nodeRows"] if row["want"] != row["got"]]
    assert differ == []
    assert any(row["got"] > 1 for entry in laid.values() for row in entry["nodeRows"])


# --- T-04: the routing check with grown boxes ---------------------------------------------------------------------

CONTEXT_MARKS = {
    "iss-00005": mark(1),
    "iss-00006": mark(3),
    "iss-00007": mark(6),
    "iss-00013": mark(6),
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
