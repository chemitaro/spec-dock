"""The structure graph's toolbar, cleanup marks, legend and the "next" notice, drawn by views/graph.js (iss-00603).

`tests/js/dashboard_graph_toolbar.mjs` runs the screen in node with a minimal stand-in for the DOM: it renders,
presses the toolbar's buttons through the screen's own click listener, and returns what each part drew and what the
browser storage holds (T-08, T-11). iss-00607: the toolbar has no line choice and every line is drawn (T-05, T-06).
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.support.dashboard import closed, node, snapshot
from tests.support.dashboard_graph import document
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node
from tests.unit.presentation.test_dashboard_graph_range import _next

if TYPE_CHECKING:
    from pathlib import Path

HARNESS = ROOT / "tests" / "js" / "dashboard_graph_toolbar.mjs"
V3 = "specdock.graph.v3"
V2 = "specdock.graph.v2"
TITLES = {
    "all": "見せる範囲：全体（終わったものも、片付けの候補も出す）",
    "now": "見せる範囲：いま（開いている親の中の終わったものを灰色で出し、片付けの候補は畳む）",
    "next": "見せる範囲：これから（着手できる・作業中・止められている・不明だけを出す）",
}
LABELS = {"all": "全体", "now": "いま", "next": "これから"}
ICONS = {"all": "layers", "now": "clock", "next": "sparkle"}
LEGEND = "片付けの候補（全体では箱と枠に印、いまでは畳んで1つに、これからでは出さない）"
NOTICE = "これから進める Scope はありません。全体で、終わったものを見られます。"


def _run(tmp_path: Path, runs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps({"runs": runs}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["runs"]


def _saved(mode: str) -> dict[str, str]:
    return {V3: json.dumps({"mode": mode, "range": "now", "deps": "all", "legend": False})}


def _all_done() -> dict[str, Any]:
    return document(snapshot(closed(1, "epic"), closed(2, "issue", parent=1), closed(3, "issue")))


def _only_candidates() -> dict[str, Any]:
    """iss-00611 T-07: an open Initiative holding only a candidate a; everything else is done."""
    return document(
        snapshot(node(1, "initiative"), node(2, "epic", parent=1), closed(3, "issue", parent=2), closed(4, "issue"))
    )


@pytest.fixture(scope="module")
def shots(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    doc = _next()
    presses = [{"act": "range", "range": r} for r in ("next", "all", "now")]
    return _run(
        tmp_path_factory.mktemp("graph-toolbar"),
        [
            # no saved choice: now; then next, all and now again
            {"name": "nest", "doc": doc, "saved": None, "clicks": presses},
            {"name": "tree", "doc": doc, "saved": _saved("tree"), "clicks": presses},
            # a saved version 2 stays as it was; version 3 is written beside it
            {
                "name": "legacy",
                "doc": doc,
                "saved": {
                    V2: json.dumps({"mode": "nest", "showDone": True, "deps": "wait", "fold": False, "legend": True})
                },
                "clicks": [{"act": "range", "range": "next"}, {"act": "legend"}],
            },
            # iss-00607 T-06: a version 3 saved with the old line choice of none draws every line all the same
            {
                "name": "nolines",
                "doc": doc,
                "saved": {V3: json.dumps({"mode": "nest", "range": "all", "deps": "none", "legend": False})},
                "clicks": [],
            },
            {
                "name": "lines",
                "doc": doc,
                "saved": {V3: json.dumps({"mode": "nest", "range": "all", "legend": False})},
                "clicks": [],
            },
            # everything is done: next has nothing to show
            {
                "name": "empty",
                "doc": _all_done(),
                "saved": {V3: json.dumps({"mode": "nest", "range": "next", "deps": "all", "legend": False})},
                "clicks": [{"act": "range", "range": "all"}, {"act": "range", "range": "next"}],
            },
            # iss-00611: the open parent holding only a candidate goes too, so next is empty
            {
                "name": "parents",
                "doc": _only_candidates(),
                "saved": {V3: json.dumps({"mode": "nest", "range": "next", "legend": False})},
                "clicks": [{"act": "range", "range": "all"}],
            },
        ],
    )


def _icon(name: str) -> str:
    source = (ASSETS / "core" / "ui.js").read_text(encoding="utf-8")
    found = re.search(rf"^\s*{name}: '([^']+)'", source, re.M)
    assert found, name
    return found.group(1)


def _range_group(tools: str) -> str:
    found = re.search(
        r'<span class="tool-group" role="group" aria-label="見せる範囲">(.*?)</span>(?=<span class="tool-group"|<button|$)',
        tools,
    )
    assert found, tools
    return found.group(1)


def _range_buttons(tools: str) -> dict[str, dict[str, str]]:
    out = {}
    for tag, body in re.findall(r'(<button [^>]*data-act="range"[^>]*>)(.*?)</button>', _range_group(tools)):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        out[attrs["data-range"]] = {**attrs, "body": body}
    return out


def _ids(world: str) -> set[str]:
    return set(re.findall(r'class="gx-(?:box|frame)[^"]*"[^>]*data-id="([^"]+)"', world))


def _element(world: str, scope_id: str) -> str:
    """The HTML of one box or frame, up to the next one."""
    start = re.search(rf'<(?:div|section) class="gx-(?:box|frame)[^"]*" data-id="{scope_id}"', world)
    assert start, scope_id
    rest = world[start.end() :]
    end = re.search(
        r'<(?:div|section) class="gx-(?:box|frame)[^"]*" data-id="|<button type="button" class="gx-clean"|<svg class="gx-edges"',
        rest,
    )
    return rest[: end.start() if end else len(rest)]


# --- T-08: the toolbar, the cleanup marks, the legend --------------------------------------------------------


@pytest.mark.parametrize("name", ["nest", "tree"])
def test_the_toolbar_has_one_range_switch_and_no_done_or_fold(shots: dict[str, Any], name: str) -> None:
    """R-01, R-08: no done or fold button; a group of all, now and next after the mode button; fit says 収める."""
    tools = shots[name][0]["tools"]
    assert 'data-act="done"' not in tools and 'data-act="fold"' not in tools
    assert 'aria-label="終わったものも"' not in tools and "片付けの候補を畳む" not in tools
    buttons = _range_buttons(tools)
    assert list(buttons) == ["all", "now", "next"]
    for key, attrs in buttons.items():
        assert attrs["title"] == TITLES[key]
        assert f'<span class="lab">{LABELS[key]}</span>' in attrs["body"]
        assert _icon(ICONS[key]) in attrs["body"]
    # right after the mode button
    assert re.search(
        r'data-act="mode"[^>]*>.*?</button><span class="tool-group" role="group" aria-label="見せる範囲">', tools
    )
    fit = re.search(r'(<button [^>]*data-act="fit"[^>]*>)(.*?)</button>', tools)
    assert fit
    assert 'title="画面に収める"' in fit.group(1) and 'aria-label="画面に収める"' in fit.group(1)
    assert '<span class="lab">収める</span>' in fit.group(2)


def test_the_legend_explains_the_cleanup_mark_by_range(shots: dict[str, Any]) -> None:
    """R-08: the cleanup line of the legend, wide."""
    legend = shots["nest"][0]["legend"]
    assert re.search(rf'<li class="wide"><span><span class="cln">.*?</span></span>{LEGEND}</li>', legend)
    assert "片付けの候補</li>" not in legend


@pytest.mark.parametrize("name", ["nest", "tree"])
def test_all_marks_the_cleanup_issue_boxes_and_next_marks_nothing(shots: dict[str, Any], name: str) -> None:
    """R-02, D-06: in all a candidate Issue box (the tree's boxes too) has the cleanup mark; next shows none."""
    _, nxt, every, now = shots[name]
    assert every["range"] == "all"
    box = _element(every["world"], "iss-00022")
    assert 'class="cln"' in box and 'aria-label="片付けの候補"' in box
    assert 'class="cln"' not in _element(every["world"], "iss-00002")  # not a candidate
    assert 'class="gx-clean"' not in every["world"]
    # next: the frame of b (epic-00020) is shown without a mark
    assert "epic-00020" in _ids(nxt["world"])
    assert 'class="cln"' not in nxt["world"]
    # now keeps what it drew before: no mark on the Issue boxes
    assert 'class="cln"' not in _element(now["world"], "iss-00002")
    if name == "nest":
        assert 'class="gx-clean"' in now["world"]


# --- T-11: pressing the switch ---------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["nest", "tree"])
def test_pressing_a_range_presses_only_it_lays_out_with_it_and_saves_three_keys(
    shots: dict[str, Any], name: str
) -> None:
    """R-01, R-07: only the pressed button is aria-pressed, the layout takes that range; v3 holds three keys
    (iss-00607 T-06: the old saved deps is dropped by the first press)."""
    first, *after = shots[name]
    assert first["range"] == "now"
    assert first["mode"] == name
    assert {k: v["aria-pressed"] for k, v in _range_buttons(first["tools"]).items()} == {
        "all": "false",
        "now": "true",
        "next": "false",
    }
    for pressed, shot in zip(("next", "all", "now"), after, strict=True):
        states = {k: v["aria-pressed"] for k, v in _range_buttons(shot["tools"]).items()}
        assert states == {k: str(k == pressed).lower() for k in LABELS}, pressed
        assert shot["range"] == pressed
        saved = json.loads(shot["saved"][V3])
        assert list(saved) == ["mode", "range", "legend"]
        assert saved == {"mode": name, "range": pressed, "legend": False}
    nxt, every, now = after
    assert "iss-00003" not in _ids(nxt["world"]) and "iss-00022" not in _ids(nxt["world"])
    assert {"iss-00003", "iss-00022"} <= _ids(every["world"])
    assert "iss-00003" in _ids(now["world"])


def test_the_first_press_moves_a_saved_version_2_to_version_3(shots: dict[str, Any]) -> None:
    """R-07: version 2 (showDone) starts in all; presses write version 3 only, version 2 stays."""
    first, nxt, legend = shots["legacy"]
    assert first["range"] == "all"
    assert V3 not in first["saved"]
    v2 = first["saved"][V2]
    # iss-00607 T-06: the deps of version 2 is not carried over
    assert json.loads(nxt["saved"][V3]) == {"mode": "nest", "range": "next", "legend": True}
    assert json.loads(legend["saved"][V3]) == {"mode": "nest", "range": "next", "legend": False}
    assert legend["saved"][V2] == v2
    assert set(legend["saved"]) == {V2, V3}


# --- iss-00607 T-05, T-06: no line choice; every line is drawn ------------------------------------------------


@pytest.mark.parametrize("name", ["nest", "tree"])
def test_the_toolbar_has_no_line_choice_and_ends_with_the_range_group(shots: dict[str, Any], name: str) -> None:
    """iss-00607 R-01, R-03: in all, now and next the bar has no deps group nor its three words; zoom, fit, mode
    and the range group stay in their order; the legend still explains the lines."""
    for shot in shots[name]:
        tools = shot["tools"]
        assert 'data-act="deps"' not in tools and 'aria-label="依存の線"' not in tools
        for word in ("待っている線", "すべての線", "線なし"):
            assert word not in tools
        assert re.findall(r'data-act="([^"]+)"', tools) == [
            "zout",
            "z100",
            "zin",
            "fit",
            "mode",
            "range",
            "range",
            "range",
        ]
        assert tools.count('class="tool-group"') == 2
        legend = shot["legend"]
        for line in ("待っている依存", "終わった依存", "親子（木）", "直接の依存", "間接（2段目より先）", "関係ない"):
            assert f"{line}</li>" in legend, line
    assert {shot["range"] for shot in shots[name]} == {"all", "now", "next"}


def test_a_saved_deps_of_none_still_draws_every_line(shots: dict[str, Any]) -> None:
    """iss-00607 R-04, F-01: a version 3 holding deps none draws the same lines as one without it, the done
    dependencies (is-done) among them."""
    (saved_none,) = shots["nolines"]
    (plain,) = shots["lines"]
    assert saved_none["range"] == plain["range"] == "all"
    edges = saved_none["edges"]
    assert edges and edges == plain["edges"]
    assert "is-done" in edges and "is-wait" in edges
    assert saved_none["world"] == plain["world"]


# --- T-08, F-01: next with nothing to show ---------------------------------------------------------------------


def test_next_with_nothing_to_show_keeps_the_bar_and_says_so(shots: dict[str, Any]) -> None:
    """F-01, D-07: the toolbar stays, the graph area says there is nothing to go on; another range clears it."""
    empty, every, again = shots["empty"]
    assert empty["range"] == "next"
    assert _ids(empty["world"]) == set()
    assert empty["bar"] and empty["view"]
    assert empty["none"] == {"hidden": False, "text": NOTICE}
    assert _range_buttons(empty["tools"])["next"]["aria-pressed"] == "true"
    assert every["none"]["hidden"] is True and _ids(every["world"])
    assert again["none"] == {"hidden": False, "text": NOTICE}


@pytest.mark.parametrize("name", ["nest", "tree", "legacy", "nolines", "lines"])
def test_the_notice_is_hidden_when_something_is_shown(shots: dict[str, Any], name: str) -> None:
    for shot in shots[name]:
        assert shot["none"] is not None and shot["none"]["hidden"] is True


def test_next_with_only_an_empty_parent_left_says_so(shots: dict[str, Any]) -> None:
    """iss-00611 T-07 (F-01): when the parents go, next is empty, the bars stay and the notice shows."""
    empty, every = shots["parents"]
    assert empty["range"] == "next"
    assert _ids(empty["world"]) == set()
    assert empty["bar"] and empty["view"] and empty["tools"]
    assert empty["none"] == {"hidden": False, "text": NOTICE}
    assert every["none"]["hidden"] is True and {"init-00001", "epic-00002"} <= _ids(every["world"])
