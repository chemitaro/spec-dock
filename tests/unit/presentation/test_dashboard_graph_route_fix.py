"""The routing's fixes of iss-00627 (D-04, D-05), run in node by `tests/js/dashboard_graph_route_fix.mjs`.

T-01: routeLayout inputs taken from two real structures (titles and texts replaced by ids, the agents' marks measured on
the page) route without any problem of the line check. Before the fixes, a wide segment kept at its A* place, a
movable segment caught between fixed entry segments a lane apart, and an entry aligned with the facing box's exit left
lanes closer than 8px.
T-02: an entry that is the only line of its side is not aligned with its line's exit when the obstacle right before the
side has an exit at that height.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src" / "spec_dock" / "assets" / "dashboard"
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


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(CHECK), str(ASSETS), str(path)], capture_output=True, text=True, timeout=900, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _box(key: str, x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
    return {"key": key, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "p1": y1 + 12, "p2": y2 - 12, "path": []}


def _facing(with_facing: bool) -> dict[str, Any]:
    # A (far left) -> Z is the only line into Z's left side; F sits right before that side with its exit F -> W at the
    # same height as A's exit (both boxes span 0..100, one exit each in the middle).
    obs = [_box("n:A", 0, 0, 100, 100), _box("n:Z", 440, 0, 540, 100)]
    edges = [{"a": 0, "z": 1, "done": False, "pairs": [["A", "Z"]]}]
    if with_facing:
        obs += [_box("n:F", 300, 0, 400, 100), _box("n:W", 700, 0, 800, 100)]
        edges.append({"a": 2, "z": 3, "done": False, "pairs": [["F", "W"]]})
    return {
        "obs": obs,
        "frames": [],
        "edges": edges,
        "bounds": {"x1": 0, "y1": -40, "x2": 840, "y2": 140},
        "nested": True,
    }


@pytest.fixture(scope="module")
def checked(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    request = {
        "inputs": json.loads(INPUTS.read_text(encoding="utf-8")),
        "graphs": {"facing": _facing(True), "alone": _facing(False)},
    }
    return _run(tmp_path_factory.mktemp("route-fix"), request)


@pytest.mark.parametrize(
    "name",
    [
        "product-now-360",
        "product-all-360",
        "product-all-872",
        "product-all-1312",
        "product-all-1424",
        "business-all-1344",
    ],
)
def test_the_fixed_inputs_route_without_problems(checked: dict[str, Any], name: str) -> None:
    result = checked["cases"][name]
    assert {key: result[key] for key in PROBLEMS} == dict.fromkeys(PROBLEMS, 0), result["list"]


def test_an_entry_is_not_aligned_with_the_exit_of_the_box_facing_it(checked: dict[str, Any]) -> None:
    result = checked["graphs"]["facing"]
    ends = {end["ei"]: end for end in result["ends"]}
    assert abs(ends[0]["y2"] - ends[1]["y1"]) >= LANE - 0.5, ends
    assert {key: result[key] for key in PROBLEMS} == dict.fromkeys(PROBLEMS, 0), result["list"]


def test_an_entry_without_a_facing_box_still_aligns_with_its_exit(checked: dict[str, Any]) -> None:
    ends = checked["graphs"]["alone"]["ends"]
    assert ends[0]["y2"] == ends[0]["y1"], ends
