"""The shell grid, one home for the small marks' values and the "seen" call (iss-00544 T-01, T-06, T-07).

The static checks always run. The marks' HTML check runs the page's modules under node: on CI node must exist,
elsewhere a missing node skips with the reason (as the structure graph check does).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "src" / "spec_dock" / "assets" / "dashboard"
DUMP = ROOT / "tests" / "js" / "dashboard_marks_dump.mjs"
GOLDEN = ROOT / "tests" / "fixtures" / "issue544" / "marks-golden.json"


def _rule(css: str, selector: str) -> str:
    found = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
    assert found is not None, selector
    return found.group(1)


# --- T-01: the grid rows ---------------------------------------------------------------------------------------


def test_the_shell_places_every_band_in_its_own_row() -> None:
    css = (ASSETS / "app.css").read_text()
    assert "grid-template-rows: var(--ds-topbar-h) auto auto minmax(0, 1fr)" in _rule(css, ".app")
    for selector, row in ((".top", 1), (".mtabs", 2), (".notices", 3), (".main", 4)):
        assert f"grid-row: {row};" in _rule(css, selector), selector


def test_the_screens_no_longer_work_around_the_grid() -> None:
    for name in ("graph", "timeline", "board", "scope", "overview"):
        assert "grid-row" not in (ASSETS / "views" / f"{name}.css").read_text(), name


# --- T-06: one home for the values -----------------------------------------------------------------------------


def test_the_marks_values_live_only_in_core_ui() -> None:
    ui = (ASSETS / "core" / "ui.js").read_text()
    for name in ("ICONS", "STATES", "KIND_LABEL", "ASSURANCE_LEVELS", "PR_STATE_WORDS", "STATE_WORDS"):
        assert re.search(rf"export const {name}\b", ui), name
    for rel in ("views/_shared/parts.js", "views/_shared/logic.js", "views/graph/marks.js", "views/timeline.js"):
        source = (ASSETS / rel).read_text()
        assert not re.search(r":\s*'<(path|circle|rect)", source), rel  # no icon shapes of their own
        assert not re.search(r'\{\s*initiative:\s*"Initiative"', source), rel
        assert not re.search(r"\{\s*light:\s*1", source), rel
        assert not re.search(r'open:\s*"開いている"', source), rel
        assert not re.search(r'done:\s*"終わった"', source), rel
        assert "GRAPH_ICONS" not in source and "MORE_ICONS" not in source, rel


def test_the_graph_box_shows_the_worktree_only_while_doing() -> None:
    graph = (ASSETS / "views" / "graph.js").read_text()
    assert 'M.wtMark(s.state === "doing" ? s.branch : null)' in graph


def _node() -> str:
    found = shutil.which("node")
    if found is None:
        if os.environ.get("CI"):
            pytest.fail("node is required on CI for the marks check (iss-00544)")
        pytest.skip("node is not installed: the marks check runs the page's JavaScript in node")
    return found


def test_the_marks_html_is_unchanged() -> None:
    done = subprocess.run([_node(), str(DUMP), str(ASSETS)], capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 0, done.stderr
    assert json.loads(done.stdout) == json.loads(GOLDEN.read_text(encoding="utf-8"))


# --- T-07: "seen" only with a structure ------------------------------------------------------------------------


def test_the_shell_records_seen_only_when_the_structure_has_a_model() -> None:
    app = (ASSETS / "app.js").read_text()
    assert app.count("api.markSeen(") == 1
    assert re.search(r"if \(state\.data\?\.snapshot\?\.fetched_at\) \{[^}]*api\.markSeen\(", app)
    api = (ASSETS / "core" / "api.js").read_text()
    body = api[api.index("export async function markSeen") :]
    assert ".catch(() => null)" in body and "response?.ok ?" in body
