"""Pure Scope panel decisions under node (iss-00587 T-02, T-03)."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest

SHARED = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard" / "views" / "_shared"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        f"const logic = await import({json.dumps((SHARED / 'panel_logic.js').as_uri())});\n"
        "const out = {};\n" + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=60)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


DETAILS = """
const details = (skeleton) => ({catalog: "ok", documents: [
  {key: "requirement", exists: true},
  {key: "explanation", exists: true, skeleton},
]});
"""


def test_explanation_states_follow_catalog_presence_and_skeleton(tmp_path: Path) -> None:
    out = _run(
        DETAILS
        + """
        out.states = [
          null, {}, {catalog: "missing"}, {catalog: "ambiguous"},
          {catalog: "scope_missing"}, {catalog: "ok", documents: []},
          {catalog: "ok", documents: [{key: "explanation", exists: false, skeleton: true}]},
          details(true), details(false), details(null),
        ].map(logic.explanationState);
        """,
        tmp_path,
    )
    assert out["states"] == [
        "unreadable",
        "unreadable",
        "unreadable",
        "unreadable",
        "unreadable",
        "missing",
        "missing",
        "skeleton",
        "written",
        "written",
    ]


def test_default_tab_prefers_only_written_explanations(tmp_path: Path) -> None:
    out = _run(
        DETAILS
        + """
        out.tabs = [details(false), details(null), details(true),
          {catalog: "ok", documents: []}, null].map(logic.defaultTab);
        """,
        tmp_path,
    )
    assert out["tabs"] == ["explanation", "explanation", "summary", "summary", "summary"]


def test_pick_tab_keeps_known_choices_and_defaults_unknown_choices(tmp_path: Path) -> None:
    out = _run(
        DETAILS
        + """
        const keys = ["explanation", "summary", "deps", "children", "docs", "artifacts", "todos"];
        out.known = keys.map((key) => logic.pickTab(key, keys, details(true)));
        out.fallback = [null, undefined, "", "unknown"].map((wanted) => [
          logic.pickTab(wanted, keys, details(false)),
          logic.pickTab(wanted, keys, details(true)),
        ]);
        """,
        tmp_path,
    )
    assert out["known"] == ["explanation", "summary", "deps", "children", "docs", "artifacts", "todos"]
    assert out["fallback"] == [["explanation", "summary"]] * 4


def test_sheet_heights_match_viewport_and_round_half_height(tmp_path: Path) -> None:
    out = _run("out.heights = [844, 800, 667].map(logic.sheetHeights);", tmp_path)
    assert out["heights"] == [
        {"peek": 120, "half": 490, "full": 844},
        {"peek": 120, "half": 464, "full": 800},
        {"peek": 120, "half": 387, "full": 667},
    ]


def test_slow_release_settles_at_nearest_sheet_height(tmp_path: Path) -> None:
    out = _run(
        """
        const heights = {peek: 120, half: 490, full: 844};
        out.snaps = [72, 120, 200, 300, 310, 490, 660, 670, 844, 900].map((height) =>
          logic.settleSheet({height, velocity: 0, heights}));
        out.slow = [0.499, -0.499].map((velocity) => logic.settleSheet({height: 500, velocity, heights}));
        """,
        tmp_path,
    )
    assert out["snaps"] == ["peek", "peek", "peek", "peek", "half", "half", "half", "full", "full", "full"]
    assert out["slow"] == ["half", "half"]


def test_fast_release_moves_to_next_height_in_direction_and_clamps_edges(tmp_path: Path) -> None:
    out = _run(
        """
        const heights = {peek: 120, half: 490, full: 844};
        const release = (height, velocity) => logic.settleSheet({height, velocity, heights});
        out.up = [72, 120, 200, 490, 700, 844, 900].map((height) => release(height, 0.5));
        out.down = [72, 120, 200, 490, 700, 844, 900].map((height) => release(height, -0.5));
        out.faster = [release(200, 2), release(700, -2)];
        """,
        tmp_path,
    )
    assert out["up"] == ["peek", "half", "half", "full", "full", "full", "full"]
    assert out["down"] == ["peek", "peek", "peek", "peek", "half", "half", "full"]
    assert out["faster"] == ["half", "half"]


def test_release_closes_only_more_than_48_pixels_below_peek_regardless_of_velocity(tmp_path: Path) -> None:
    out = _run(
        """
        const heights = {peek: 120, half: 490, full: 844};
        out.snaps = [0, 0.5, -0.5].map((velocity) => [
          logic.settleSheet({height: 71.9, velocity, heights}),
          logic.settleSheet({height: 72, velocity, heights}),
        ]);
        """,
        tmp_path,
    )
    assert out["snaps"] == [["closed", "peek"], ["closed", "peek"], ["closed", "peek"]]


def test_grab_tap_toggles_full_and_half_and_expands_peek(tmp_path: Path) -> None:
    out = _run('out.snaps = ["peek", "half", "full"].map(logic.nextOnTap);', tmp_path)
    assert out["snaps"] == ["full", "full", "half"]
