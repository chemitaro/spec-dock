"""The tree view's routing of iss-00633 (D-01, D-02), run in node by `tests/js/dashboard_graph_route_fix.mjs`.

T-01: in the tree view, the long runs between an initiative's parent line and its epics are packed into about as many
lanes as overlap at once, and a round that leaves a problem of the line check is not taken as settled. Before the
fixes, the fixed product structure's "all" tree kept 9 lanes closer than 8px after 10 rounds.
T-02: a tall corridor whose overlapping runs chain into each other (box i -> box i + 5) fits its lanes instead of
stacking one lane further per link of the chain.
T-03: the packing is used only in the tree view, and a settled round has no problem.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src" / "spec_dock" / "assets" / "dashboard"
GRAPH = ASSETS / "views" / "graph"
CHECK = ROOT / "tests" / "js" / "dashboard_graph_route_fix.mjs"
INPUTS = ROOT / "tests" / "fixtures" / "issue627" / "route_inputs.json"
PROBLEMS = ("boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed")
LANE = 8


def _node() -> str:
    found = shutil.which("node")
    if found is None:
        if os.environ.get("CI"):
            pytest.fail("node is required on CI for the structure graph check (iss-00532)")
        pytest.skip("node is not installed: the structure graph check runs the page's JavaScript in node")
    return found


def _corridor(boxes: int = 40, step: int = 5, room: int = 120) -> dict[str, Any]:
    # A parent line (blocking vertical runs only) on the left and a column of boxes `room` px to its right; box i
    # waits for box i + step, so every line leaves a box's right side and runs down the corridor to a later box.
    height, row, x1 = 60, 30, 20 + room
    obs: list[dict[str, Any]] = [
        {"key": "t:p", "lane": "v", "x1": 10, "y1": 0, "x2": 12, "y2": boxes * (height + row), "p1": 0, "p2": 0}
    ]
    for i in range(boxes):
        y1 = i * (height + row) + 20
        obs.append({"key": f"n:b{i}", "x1": x1, "y1": y1, "x2": x1 + 200, "y2": y1 + height, "p1": y1 + 12, "p2": y1 + height - 12})
    edges = [{"a": i, "z": i + step} for i in range(1, boxes - step + 1)]
    return {"obs": obs, "frames": [], "edges": edges, "bounds": {"x1": 0, "y1": 0, "x2": x1 + 260, "y2": boxes * (height + row) + 40}, "nested": False}


@pytest.fixture(scope="module")
def checked(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    inputs = json.loads(INPUTS.read_text(encoding="utf-8"))
    inputs["cases"] = [
        {"name": f"{structure}-tree-all", "structure": structure, "mode": "tree", "range": "all", "width": 1240, "marks": False}
        for structure in ("product", "business")
    ]
    path = tmp_path_factory.mktemp("tree-route") / "request.json"
    path.write_text(json.dumps({"inputs": inputs, "graphs": {"corridor": _corridor()}}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=900, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("name", ["product-tree-all", "business-tree-all"])
def test_the_tree_of_the_fixed_inputs_routes_without_problems(checked: dict[str, Any], name: str) -> None:
    result = checked["cases"][name]
    assert {key: result[key] for key in PROBLEMS} == dict.fromkeys(PROBLEMS, 0), result["list"]
    assert result["problems"] == sum(result[key] for key in PROBLEMS)


def test_a_corridor_of_chained_runs_fits_its_lanes(checked: dict[str, Any]) -> None:
    result = checked["graphs"]["corridor"]
    assert result["overlaps"] == 0, result["list"]
    assert result["maxWiden"] <= LANE, result


def test_the_packing_is_for_the_tree_only_and_a_settled_round_is_clean() -> None:
    router = (GRAPH / "router.js").read_text(encoding="utf-8")
    calls = [m.start() for m in re.finditer(r"= packFree\(gr", router)]
    assert len(calls) == 1
    assert re.search(r"if \(!G\.nested && res\.over > 0\.5\) \{\s*const alt = packFree\(gr", router)
    layout = (GRAPH / "layout.js").read_text(encoding="utf-8")
    assert re.search(r"const settled = [^;]*&& !round\.problems;", layout)
    assert "problems: settled ? 0" not in layout
