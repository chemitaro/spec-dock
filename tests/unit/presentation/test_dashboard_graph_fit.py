"""The structure graph's frames as tall as they are drawn (iss-00627 R-01, R-02, F-01, F-02).

graph.css pins the frame heading's rows to the layout's px (title row 22, summary row 18, an Epic's top padding 8 over
its 1px border), so a one-line compact frame fits `compactHeight`; a compact frame whose title wraps is measured after
drawing (`views/graph/measure.js`) and laid out again with `options.heads`, as the rows of agents are (iss-00620).
The layout and `headsDiffer` run in node (`tests/js/dashboard_graph_fit.mjs`); the page's wiring is checked in its source.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.dashboard import node, snapshot
from tests.support.dashboard_graph import document
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

CHECK = ROOT / "tests" / "js" / "dashboard_graph_fit.mjs"
VIEWS = ASSETS / "views"


def _doc() -> dict[str, Any]:
    return document(
        snapshot(
            node(1, "initiative"),  # nothing inside: a compact Initiative
            node(2, "epic"),  # nothing inside: a compact Epic
            node(3, "epic"),  # an open child inside: a frame with a body
            node(4, "issue", parent=3),
            node(5, "issue", blocked_by=(4,)),
        )
    )


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=300, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def checked(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    marks = {"epic-00002": {"items": [60], "gap": 2}}
    layouts = {
        "plain": {"mode": "nest", "range": "now"},
        "empty": {"mode": "nest", "range": "now", "heads": {}},
        "low": {"mode": "nest", "range": "now", "heads": {"epic-00002": 60, "init-00001": 78}},
        "tall": {
            "mode": "nest",
            "range": "now",
            "heads": {"epic-00002": 85, "init-00001": 90, "epic-00003": 200, "iss-00004": 200},
        },
        "rows": {"mode": "nest", "range": "now", "marks": marks},
        "rows-tall": {"mode": "nest", "range": "now", "marks": marks, "heads": {"epic-00002": 100}},
    }
    request = {
        "document": _doc(),
        "layouts": layouts,
        "compact": [["epic", 1], ["initiative", 1], ["issue", 1], ["epic", 2]],
    }
    out = _run(tmp_path_factory.mktemp("fit"), request)
    lay = out["layouts"]
    # headsDiffer's cases from the laid out nodes (T-04)
    plain = lay["plain"]["nodes"]
    tall = lay["tall"]["nodes"]
    rows = lay["rows"]["nodes"]
    request2 = {
        "document": _doc(),
        "differ": [
            {"nodes": plain, "needs": None},
            {"nodes": plain, "needs": {}},
            {"nodes": plain, "needs": {"epic-00002": 67, "init-00001": 70}},
            {"nodes": plain, "needs": {"epic-00002": 85}},
            {"nodes": tall, "needs": {"epic-00002": 85, "init-00001": 90}},
            {"nodes": tall, "needs": {"epic-00002": 67, "init-00001": 90}},
            {"nodes": rows, "needs": {"epic-00002": 87}},
            {"nodes": rows, "needs": {"epic-00002": 88}},
            {"nodes": plain, "needs": {"epic-00003": 500, "iss-00004": 500}},
        ],
    }
    out["differ"] = _run(tmp_path_factory.mktemp("fit-differ"), request2)["differ"]
    return out


def _frame(layout: dict[str, Any], scope_id: str) -> dict[str, Any]:
    return next(n for n in layout["nodes"] if n["id"] == scope_id)


def test_the_compact_height_is_the_layouts_frame_without_a_body(checked: dict[str, Any]) -> None:
    assert checked["compact"] == [67, 78, 67, 87]
    lay = checked["layouts"]["plain"]
    epic, ini = _frame(lay, "epic-00002"), _frame(lay, "init-00001")
    assert epic["compact"] and ini["compact"]
    assert epic["y2"] - epic["y1"] == 67 and ini["y2"] - ini["y1"] == 78


def test_heads_make_only_a_compact_frame_taller(checked: dict[str, Any]) -> None:
    lay = checked["layouts"]
    for name in ("empty", "low"):
        assert lay[name] == lay["plain"], name  # none, or none above the base: the same layout
    tall = lay["tall"]
    epic, ini = _frame(tall, "epic-00002"), _frame(tall, "init-00001")
    assert (epic["y2"] - epic["y1"], epic["fit"]) == (85, 85)
    assert (ini["y2"] - ini["y1"], ini["fit"]) == (90, 90)
    for scope_id in ("epic-00003", "iss-00004"):  # a frame with a body and a box do not read heads
        a, b = _frame(tall, scope_id), _frame(lay["plain"], scope_id)
        assert (a["y2"] - a["y1"], "fit" in a) == (b["y2"] - b["y1"], False), scope_id
    assert all("fit" not in n for n in lay["plain"]["nodes"])


def test_heads_count_with_the_rows_of_agents(checked: dict[str, Any]) -> None:
    lay = checked["layouts"]
    epic = _frame(lay["rows"], "epic-00002")
    assert epic["rows"] == 2 and epic["y2"] - epic["y1"] == 87 and "fit" not in epic
    tall = _frame(lay["rows-tall"], "epic-00002")
    assert tall["y2"] - tall["y1"] == 100 and tall["fit"] == 100


def test_heads_differ_only_when_a_compact_frame_would_change(checked: dict[str, Any]) -> None:
    assert checked["differ"] == [False, False, False, True, False, True, False, True, False]


def test_the_css_pins_the_heading_rows_to_the_layout() -> None:
    css = (VIEWS / "graph.css").read_text(encoding="utf-8")
    for rule in (
        ".gx .gx-epic { background: var(--ds-surface); padding: 8px 12px 12px;",
        ".gx .gx-epic.is-compact { width: 236px; padding-bottom: 11px; }",
        ".gx .gx-ini.is-compact { padding-bottom: 15px; }",
        ".gx .gx-fh > :is(.gx-kicker, .gx-fttl) { line-height: 22px; }",
        "height: 18px; line-height: 18px; }",
    ):
        assert rule in css, rule
    fh = re.search(r"^\.gx \.gx-fh \{[^}]*\}", css, re.M)
    assert fh and "min-height: 22px" in fh.group(0) and "line-height" not in fh.group(0)  # not into the agents' row
    layout = (VIEWS / "graph" / "layout.js").read_text(encoding="utf-8")
    assert "head: 46," in layout and "epic: [9, 12, 12]" in layout and "initiative: [16, 16, 16]" in layout


def test_the_page_measures_the_compact_frames_and_lays_out_again() -> None:
    measure = (VIEWS / "graph" / "measure.js").read_text(encoding="utf-8")
    assert (
        "export function compactNeeds(root, scale)" in measure
        and "export function headsDiffer(nodes, needs)" in measure
    )
    assert 'getComputedStyle(fm).display !== "flex") return null' in measure  # F-01: graph.css not applied yet
    assert "!root.getClientRects().length" in measure  # F-01: hidden
    for name in ("graph.js", "allgraph.js"):
        src = (VIEWS / name).read_text(encoding="utf-8")
        assert 'from "./graph/measure.js"' in src, name
        assert "compactNeeds(" in src and "headsDiffer(" in src, name
        assert "heads:" in src, name  # passed to routeLayout
    graph = (VIEWS / "graph.js").read_text(encoding="utf-8")
    body = graph[graph.index("function checkRows()") : graph.index("function onMarksResize()")]
    assert "V.rowsRedo >= 2" in body and "headsDiffer(V.EG.layout.nodes, H)" in body
    allgraph = (VIEWS / "allgraph.js").read_text(encoding="utf-8")
    body = allgraph[allgraph.index("function checkRows()") : allgraph.index("function onMarksResize()")]
    assert "r.rowsRedo >= 2" in body and "headsDiffer(r.eg.layout.nodes, h)" in body
    assert "JSON.stringify(r.heads)" in allgraph  # a repository's signature
