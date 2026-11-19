"""The Unscoped row on the structure graph and the cross-repository structure (iss-00668 T-04).

`views/graph.js` and `views/allgraph.js` draw each repository's row of worktrees not shown as a Scope box with the fake
DOM and the fake orca (`tests/js/dashboard_graph_command_screen.mjs`, `tests/js/dashboard_allgraph_command_screen.mjs`):
the main checkout (Primary) with no pair and no summary, the Unlinked worktrees, the faint idle one and "+N", the
worktree's panel, "next" with counts and no line. The CSS's own rules are read here. Every value is synthetic.
"""

from __future__ import annotations

from itertools import pairwise
import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation import (
    test_dashboard_allgraph_command_screen as AS,
    test_dashboard_graph_command_screen as GS,
)
from tests.unit.presentation.test_dashboard_graph_command import ag, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, _node
from tests.unit.presentation.test_dashboard_graph_unscoped import git, row

if TYPE_CHECKING:
    from pathlib import Path

GRAPH_CSS = GS.GRAPH_CSS
PRIMARY = ("Primary", "The main checkout of this repository")
UNLINKED = ("Unlinked", "Not linked to any Scope. Link it with `spec-dock work start`.")

DOC = git(row("/w/u-a", "topic-a"), row("/w/u-big", "big"), row("/w/old-1", "old-1"), row("/w/old-2", "old-2")) | {
    "revision": "r1"
}
ONE_IDLE = git(row("/w/u-a", "topic-a"), row("/w/old-1", "old-1")) | {"revision": "r1"}


def _ag(agent_id: str, parent: str | None = None, **extra: Any) -> dict[str, Any]:
    return ag(agent_id, parent=parent, **extra) | {"w": 36}


SUMMARY = summary(
    wt("wt-main", "/w/r", "main", [_ag("a-coord")], main=True),
    wt("wt-a", "/w/u-a", "topic-a", [_ag("a-1", parent="a-coord")]),
    # five agents: they wrap; b-0 directs b-4 inside the same item
    wt("wt-big", "/w/u-big", "big", [_ag("b-0"), *(_ag(f"b-{i}") for i in range(1, 4)), _ag("b-4", parent="b-0")]),
)
WT = '[data-cmd-wt="wt-a"]'
FOLD = '[data-cmd-fold="fold"]'

RUNS: list[dict[str, Any]] = [
    # R-02, F-02: no orca at all: the row from git alone
    {"name": "u-none", "orca": False, "doc": DOC, "range": "all"},
    # R-03, R-04, R-05, R-09
    {
        "name": "u-all",
        "orca": {"summary": SUMMARY},
        "doc": DOC,
        "range": "all",
        "steps": [
            {"tap": WT},  # 1: the worktree's panel
            {"tap": WT},  # 2: again: closed
            {"tap": FOLD},  # 3: the folded worktrees
            {"key": "Escape"},  # 4: closed
            {"tap": WT},  # 5
            {"click": '.panel [data-act="close"]'},  # 6: closed
            {"tap": WT},  # 7
            {"click": '.panel [data-wt-agent="a-1"]'},  # 8: the agent's chat
            {"render": True},  # 9: the same input draws nothing again
            {"key": "Enter", "on": FOLD},  # 10: the keyboard opens +N
        ],
    },
    {"name": "u-one", "orca": {"summary": SUMMARY}, "doc": ONE_IDLE, "range": "all"},
    # R-06: "next": the main checkout and the directing Unlinked worktree with counts; no line
    {"name": "u-next", "orca": {"summary": SUMMARY}, "doc": DOC, "range": "next"},
    # the embedding has no "open in Orca"
    {
        "name": "u-embed",
        "orca": {"summary": SUMMARY},
        "doc": DOC,
        "range": "all",
        "embed": True,
        "steps": [{"tap": WT}],
    },
]


@pytest.fixture(scope="module")
def runs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    return GS._run(tmp_path_factory.mktemp("unscoped-screen"), {"doc": DOC, "runs": RUNS})["runs"]


def _items(shot: dict[str, Any]) -> list[tuple[str | None, str | None, str | None]]:
    return [
        (it["label"], it["badge"] and it["badge"]["kind"], it["count"] and it["count"]["text"])
        for it in shot["row"]["items"]
    ]


def _px(style: str, name: str) -> float:
    m = re.search(rf"(?:^|;){name}:(-?[\d.]+)px", style)
    assert m, (style, name)
    return float(m.group(1))


def test_the_row_and_primary_without_pairs_or_summary(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-02, F-02: the lead, the main checkout and every idle Unlinked worktree folded."""
    shot = runs["u-none"][0]
    assert shot["row"]["lead"] == {"text": "Unscoped", "title": "Worktrees not shown as a Scope box"}
    assert _items(shot) == [("main", "primary", None), ("+4", None, None)]
    primary = shot["row"]["items"][0]
    assert primary["badge"] | {"kind": None} == {
        "kind": None,
        "text": PRIMARY[0],
        "title": PRIMARY[1],
        "aria": PRIMARY[1],
    }
    assert primary["tag"] == "button" and primary["key"] == "git:/w/r"
    assert all(it["idle"] for it in shot["row"]["items"])
    # no English beyond the Issue's words
    assert shot["row"]["items"][1]["title"] == "エージェントのいない worktree 4件"
    assert shot["row"]["curves"] == 0 and shot["band"] is not None


def test_unlinked_items_with_their_agents_and_a_fold(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-03, R-04, R-09: Unlinked with every agent of the worktree, the idle ones in +2, faint."""
    shot = runs["u-all"][0]
    assert _items(shot) == [
        ("main", "primary", None),
        ("big", "unlinked", None),
        ("topic-a", "unlinked", None),
        ("+2", None, None),
    ]
    items = shot["row"]["items"]
    assert items[1]["badge"]["title"] == UNLINKED[1] and items[1]["badge"]["aria"] == UNLINKED[1]
    assert [it["idle"] for it in items] == [False, False, False, True]
    assert [a["id"] for a in items[1]["agents"]] == ["b-0", "b-1", "b-2", "b-3", "b-4"]
    assert items[3]["fold"] and items[3]["agents"] == []
    # the line from the band's coordinator to the Unlinked agent; b-0 > b-4 in one item: an arc
    assert set(shot["lines"]) == {"a-coord>a-1", "b-0>b-4"}


def test_a_wrapped_item_puts_its_buttons_at_the_models_slots(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-09: four in the first line, the fifth 24px lower at the first column; the row is 52px high."""
    items = runs["u-all"][0]["row"]["items"]
    big = items[1]
    lefts = [_px(a["style"], "left") for a in big["agents"]]
    tops = [_px(a["style"], "top") for a in big["agents"]]
    assert tops == [0, 0, 0, 0, 24]
    assert [b - a for a, b in pairwise(lefts[:4])] == [52, 52, 52] and lefts[4] == lefts[0]
    assert {_px(it["style"], "height") for it in items} == {52}
    # the row's lower edge stays where one line's is (BAND.top -16 + 28): it rises by 24
    assert {_px(it["style"], "top") for it in items} == {-40}


def test_a_single_idle_unlinked_worktree_is_faint_not_folded(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-04; R-03: the summary's worktree not in git that directs keeps today's item, without a badge."""
    shot = runs["u-one"][0]
    assert _items(shot) == [
        ("main", "primary", None),
        ("old-1", "unlinked", None),
        ("topic-a", "unlinked", None),
        ("big", None, None),
    ]
    assert [it["idle"] for it in shot["row"]["items"]] == [False, True, False, False]


def test_pressing_an_item_opens_its_worktree(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-05: the badge and the branch, the path, the agents and orca-web's button; again closes it."""
    shot = runs["u-all"][1]
    panel = shot["row"]["panel"]
    assert shot["panel"]["open"] and panel["wt"] == "wt-a"
    assert panel["head"] == "Unlinked topic-a"
    assert panel["dd"][:2] == ["topic-a", "/w/u-a"]
    assert panel["agents"] == ["a-1"]
    assert panel["open"] == {"src": "http://192.0.2.1:8791/embed/open-button.js", "worktree": "wt-a", "theme": "light"}
    closed = runs["u-all"][2]
    assert not closed["panel"]["open"] and closed["row"]["panel"]["wt"] is None


def test_plus_n_lists_the_folded_worktrees_and_closes(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-04: the folded worktrees' branches and paths; Escape and the close button close it."""
    fold = runs["u-all"][3]["row"]["panel"]
    assert fold["wt"] == "fold" and fold["list"] == ["old-1/w/old-1", "old-2/w/old-2"]
    assert fold["open"] is None
    assert not runs["u-all"][4]["panel"]["open"]
    assert runs["u-all"][5]["row"]["panel"]["wt"] == "wt-a"
    assert not runs["u-all"][6]["panel"]["open"]
    assert runs["u-all"][10]["row"]["panel"]["wt"] == "fold" and runs["u-all"][10]["keyPrevented"] is True


def test_an_agent_of_the_panel_opens_its_chat(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-05: the same chat and pressed state as the band's agent."""
    shot = runs["u-all"][8]
    assert shot["panel"]["agent"] == "a-1" and shot["row"]["panel"]["wt"] is None
    assert shot["panel"]["iframe"]["src"] == "http://192.0.2.1:8791/embed/agent?id=a-1&theme=light"
    assert shot["pressed"]["a-1"] == "true" and shot["pressed"]["a-coord"] == "false"
    assert shot["lines"]["a-coord>a-1"] == "is-cmd-hl"


def test_the_same_input_draws_the_row_again_never(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-08."""
    before, after = runs["u-all"][8], runs["u-all"][9]
    assert (before["band"], before["cmd"]) == (after["band"], after["cmd"])


def test_next_draws_no_line_and_counts_the_children(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-06, R-09: the main checkout always, the directing Unlinked worktree; the counts in English."""
    shot = runs["u-next"][0]
    assert _items(shot) == [("main", "primary", "1"), ("big", "unlinked", "1")]
    assert shot["row"]["items"][0]["count"]["title"] == "1 agent in progress — claude #1: 1"
    assert shot["row"]["items"][0]["count"]["aria"] == shot["row"]["items"][0]["count"]["title"]
    assert shot["row"]["curves"] == 0 and shot["lines"] == {}
    # all: no count
    assert all(it["count"] is None for it in runs["u-all"][0]["row"]["items"])


def test_the_embedding_has_no_open_button(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-04 / R-05."""
    panel = runs["u-embed"][1]["row"]["panel"]
    assert panel["wt"] == "wt-a" and panel["open"] is None


def test_without_orca_there_is_no_open_button(tmp_path: Path) -> None:
    """T-04 / R-05, F-02: the panel of a git row with no summary: its branch and path, no agent, no button."""
    run = {"name": "x", "orca": False, "doc": ONE_IDLE, "range": "all", "steps": [{"tap": '[data-cmd-wt="git:/w/r"]'}]}
    shot = GS._run(tmp_path, {"doc": ONE_IDLE, "runs": [run]})["runs"]["x"][1]
    panel = shot["row"]["panel"]
    assert panel["wt"] == "git:/w/r" and panel["head"] == "Primary main"
    assert panel["dd"] == ["main", "/w/r", "なし"] and panel["open"] is None


# --- the cross-repository structure ---------------------------------------------------------------------------

A_DOCS = {
    AS.key("a"): AS.doc(
        "/w/a", {"iss-00002": "/w/a-2"}, git=(("/w/a-x", "topic-x"), ("/w/a-o1", "old-1"), ("/w/a-o2", "old-2"))
    ),
    AS.key("c"): AS.doc("/w/c", {"iss-00002": "/w/c-2"}, git=(("/w/c-o1", "old-1"), ("/w/c-o2", "old-2"))),
}
A_SUMMARY = AS.summary(
    AS.wt("wt-a", "/w/a", "main", [AS.ag("a-coord")], AS.PROJ["a"], main=True),
    AS.wt("wt-ax", "/w/a-x", "topic-x", [AS.ag("x-1", parent="a-coord")], AS.PROJ["a"]),
    AS.wt("wt-c2", "/w/c-2", "iss-00002", [AS.ag("c-own", parent="a-coord")], AS.PROJ["c"]),
)
A_RUNS: list[dict[str, Any]] = [
    {"name": "x-none", "orca": False, "repos": AS.REPOS, "docs": A_DOCS, "range": "all"},
    {
        "name": "x-all",
        "orca": {"summary": A_SUMMARY},
        "repos": AS.REPOS,
        "docs": A_DOCS,
        "range": "all",
        "steps": [
            {"tap": '[data-cmd-wt="wt-ax"]'},
            {"tap": '[data-cmd-fold="fold|github.com/o/c"]'},
            {"key": "Escape"},
        ],
    },
    {"name": "x-next", "orca": {"summary": A_SUMMARY}, "repos": AS.REPOS, "docs": A_DOCS, "range": "next"},
]


@pytest.fixture(scope="module")
def cross(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    path = tmp_path_factory.mktemp("unscoped-cross") / "request.json"
    path.write_text(json.dumps({"runs": A_RUNS}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(AS.HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return {name: r["shots"] for name, r in json.loads(result.stdout)["runs"].items()}


def _labels(shot: dict[str, Any]) -> list[tuple[str, str | None, str | None]]:
    return [(it["label"], it["badge"], it["count"]) for it in shot["bandItems"]]


def test_every_frame_has_its_row_without_orca(cross: dict[str, Any]) -> None:
    """T-04 / R-02, R-07: each repository's frame its own row under its heading, with its lead."""
    shot = cross["x-none"][0]
    assert _labels(shot) == [
        ("main", "primary", None),
        ("+3", None, None),
        ("main", "primary", None),
        ("+2", None, None),
    ]
    assert shot["leadTexts"] == [["Unscoped", "Worktrees not shown as a Scope box"]] * 2
    for name in ("a", "c"):
        sec = AS._sec(shot, name)
        assert any(sec["y"] + 40 + AS.BAND_TOP == it["y"] for it in shot["bandItems"])


def test_the_cross_rows_and_their_panels(cross: dict[str, Any]) -> None:
    """T-04 / R-03, R-05: the Unlinked worktree with its agent and its line; one +N per frame by its own key."""
    first, wtp, fold, closed = cross["x-all"]
    assert _labels(first) == [
        ("main", "primary", None),
        ("topic-x", "unlinked", None),
        ("+2", None, None),
        ("main", "primary", None),
        ("+2", None, None),
    ]
    assert set(first["lines"]) == {"a-coord>x-1", "a-coord>c-own"}
    assert "fold|github.com/o/a" in first["rowKeys"] and "fold|github.com/o/c" in first["rowKeys"]
    assert (
        wtp["panel"]["wt"] == "wt-ax"
        and wtp["panel"]["dd"][:2] == ["topic-x", "/w/a-x"]
        and wtp["panel"]["openBtn"] == "wt-ax"
    )
    assert fold["panel"]["wt"] == "fold|github.com/o/c" and fold["panel"]["list"] == ["old-1/w/c-o1", "old-2/w/c-o2"]
    assert not closed["panel"]["open"]


def test_the_cross_next_counts_and_draws_no_line(cross: dict[str, Any]) -> None:
    """T-04 / R-06, R-07."""
    shot = cross["x-next"][0]
    assert shot["lines"] == {}
    assert _labels(shot) == [("main", "primary", "2"), ("main", "primary", None)]


# --- the CSS ----------------------------------------------------------------------------------------------------


def test_the_row_css_uses_only_the_variables() -> None:
    """T-04 / R-02..R-04: the badge, the count and the faint item; colours only from the design system's variables."""
    rules = dict(GS._rules(GRAPH_CSS))
    for sel in (
        ".gx .gx-band-badge, .gx .gx-band-count",
        '.gx .gx-band-badge[data-badge="primary"]',
        '.gx .gx-band-badge[data-badge="unlinked"]',
        ".gx .gx-band-count",
        ".gx .gx-band-item.is-idle",
        ".gx .gx-band-lab:focus-visible",
    ):
        assert sel in rules, sel
    assert "opacity: .55" in rules[".gx .gx-band-item.is-idle"]
    assert "var(--ds-accent-soft)" in rules['.gx .gx-band-badge[data-badge="primary"]']
    assert "var(--ds-warn-bg)" in rules['.gx .gx-band-badge[data-badge="unlinked"]']
    assert "var(--ds-surface-3)" in rules[".gx .gx-band-count"]
    colours = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgb\(|hsl\(")
    band = [body for sel, body in GS._rules(GRAPH_CSS) if ".gx-band" in sel or ".pn-wt" in sel]
    assert band and not any(colours.search(body) for body in band)
    assert "position: absolute" in rules[".gx .gx-band-agent"] and "width: 52px" in rules[".gx .gx-band-agent"]
