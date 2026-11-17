"""The command lines and the bands on the cross-repository structure, and the headings over the lines (iss-00617 T-04, T-05).

T-04 reads the shipped CSS: the frames that make no stacking context, the heading and meta rows over the lines with an
underlay of their frame's colour, the repository frames' headings likewise, and the band's lead "ほかの場所".
T-05 draws `views/allgraph.js` with the fake DOM and the fake orca's summary
(`tests/js/dashboard_allgraph_command_screen.mjs`): the layers, the bands in the frames and above them, the frame kept
for its band, the news that never lays out again, the composing again only for a new band shape and its anchor, F-05's
limit, the band's chat, the mark's highlight, the legend and specdockCmdAudit. Every value is synthetic.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any

import pytest

from tests.unit.presentation.test_dashboard_allgraph_command import ag as _ag, key, structure, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

HARNESS = ROOT / "tests" / "js" / "dashboard_allgraph_command_screen.mjs"
VIEWS = ASSETS / "views"
GRAPH_CSS = (VIEWS / "graph.css").read_text(encoding="utf-8")
ALL_CSS = (VIEWS / "allgraph.css").read_text(encoding="utf-8")
BAND_H = 48
BAND_TOP = 16
OTHER_H = 56
OTHER_TOP = 16
ITEM_H = 28


def _rules(css: str) -> list[tuple[str, str]]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


def _rule(css: str, selector: str) -> str:
    found = [body for sel, body in _rules(css) if sel == selector]
    assert found, selector
    return " ".join(found)


# --- T-04: the headings over the lines ---------------------------------------------------------------------------


def test_the_frames_make_no_stacking_context_and_the_rows_are_over_the_lines() -> None:
    assert "z-index: auto" in _rule(GRAPH_CSS, ".gx .gx-world > .gx-frame")
    rows = _rule(GRAPH_CSS, ".gx :is(.gx-ini, .gx-epic) > :is(.gx-fh, .gx-fm)")
    assert "position: relative" in rows and "z-index: 2" in rows and "background" not in rows
    # the layers, the boxes and the dependency lines keep their order
    assert "z-index: 1" in _rule(GRAPH_CSS, ".gx .gx-world > .gx-cmd")
    assert "z-index: 3" in _rule(GRAPH_CSS, ".gx .gx-world > .gx-cmd-top")
    assert "z-index: 6" in _rule(GRAPH_CSS, ".gx .gx-world > .gx-band")
    assert "z-index: 2" in _rule(GRAPH_CSS, ".gx .gx-world > .gx-box, .gx .gx-world > .gx-clean")
    assert "z-index: 5" in _rule(GRAPH_CSS, ".gx .gx-edges")


def test_the_frames_colour_is_one_variable_of_todays_values() -> None:
    assert "--gx-fbg: color-mix(in srgb, var(--ds-surface) 55%, var(--ds-bg-2))" in _rule(GRAPH_CSS, ".gx .gx-ini")
    assert "--gx-fbg: var(--ds-surface)" in _rule(GRAPH_CSS, ".gx .gx-epic")
    assert "--gx-fbg: var(--ds-surface-2)" in _rule(GRAPH_CSS, '.gx .gx-frame[data-st="done"]')


def test_the_heading_parts_have_their_frames_underlay() -> None:
    under = _rule(
        GRAPH_CSS, ".gx :is(.gx-ini, .gx-epic) > .gx-fh > :not(.gx-agents), .gx :is(.gx-ini, .gx-epic) > .gx-fm > *"
    )
    assert "background-color: var(--gx-fbg)" in under
    # the parts with a colour of their own: that colour over the underlay, as today
    for sel, colour in (
        (".gx :is(.gx-ini, .gx-epic) > .gx-fh > .ds-docid", "var(--ds-accent-soft)"),
        (".gx :is(.gx-ini, .gx-epic) > .gx-fm > .sbar", "var(--ds-surface-3)"),
        (".gx :is(.gx-ini, .gx-epic) > .gx-fm > .hm", "var(--sd-blocked-bg)"),
        (".gx :is(.gx-ini, .gx-epic) > .gx-fm > .dn", "var(--ds-surface-2)"),
    ):
        assert f"background: linear-gradient({colour}, {colour}) var(--gx-fbg)" in _rule(GRAPH_CSS, sel), sel


def test_the_repository_headings_are_over_the_lines_with_their_frames_colour() -> None:
    assert "z-index: auto" in _rule(ALL_CSS, ".gx .ax-body > .gx-frame")
    assert "z-index: 2" in _rule(ALL_CSS, ".gx .ax-head")
    kids = _rule(ALL_CSS, ".gx .ax-head > *")
    assert "position: relative" in kids and "background-color: var(--ds-bg-2)" in kids
    assert "background-color: var(--ds-surface-2)" in _rule(
        ALL_CSS, '.gx .ax-repo:is([data-depth="1"], [data-depth="3"]) .ax-head > *'
    )
    assert "background: var(--ds-surface)" in _rule(ALL_CSS, ".gx .ax-repo:is([data-depth]) .ax-head > .ax-link:hover")
    # no colour value and no variable of its own (iss-00614)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgb\(|hsl\(", ALL_CSS)
    assert not re.search(r"--[\w-]+\s*:", ALL_CSS)


def test_the_bands_lead_rule() -> None:
    lead = _rule(GRAPH_CSS, ".gx .gx-band-lead")
    for part in ("position: absolute", "height: 28px", "line-height: 28px", "font-size: 11.5px", "white-space: nowrap"):
        assert part in lead, part
    assert "color: var(--ds-text-2)" in lead


def test_the_shared_drawing_uses_no_forbidden_drawing() -> None:
    for name in ("graph/command_view.js", "allgraph.js", "allgraph/command.js"):
        text = (VIEWS / name).read_text(encoding="utf-8")
        for word in ("<animate", "animateMotion", "canvas", "blur("):
            assert word not in text, (name, word)


# --- T-05: the page -------------------------------------------------------------------------------------------------


def ag(agent_id: str, mark: str = "working", parent: str | None = None) -> dict[str, Any]:
    return _ag(agent_id, mark, parent) | {"w": 36}


def listed(name: str, parent: str | None = None) -> dict[str, Any]:
    return {"repository": key(name), "parent": key(parent) if parent else None, "owner": "o", "name": name}


def doc(*args: Any, **kw: Any) -> dict[str, Any]:
    return structure(*args, **kw) | {"revision": "r1"}


PROJ = {n: (f"p-{n}", f"repo-{n}") for n in ("a", "b", "c", "e", "x")}
DOCS = {
    key("a"): doc("/w/a", {"iss-00002": "/w/a-2"}),
    key("c"): doc("/w/c", {"iss-00002": "/w/c-2"}),
}
REPOS = [listed("a"), listed("c")]

# a coordinator in a's main checkout directs an agent in c's Issue 2 worktree
CROSS = summary(
    wt("wt-a", "/w/a", "main", [ag("a-coord")], PROJ["a"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="a-coord")], PROJ["c"]),
)
# the same agents, no parent
FLAT = summary(
    wt("wt-a", "/w/a", "main", [ag("a-coord")], PROJ["a"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own")], PROJ["c"]),
)
# a coordinator in no shown repository: "ほかの場所"
OTHER = summary(
    wt("wt-x", "/x/one", "topic-x", [ag("x-coord")], PROJ["x"], main=True),
    wt("wt-a", "/w/a", "main", [ag("a-coord")], PROJ["a"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="x-coord")], PROJ["c"]),
)
# e has nothing to show in "next": its coordinator keeps its frame
E_DOCS = DOCS | {key("e"): doc("/w/e", done=True)}
KEEP = summary(
    wt("wt-e", "/w/e", "main", [ag("e-coord")], PROJ["e"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="e-coord")], PROJ["c"]),
)
KEEP_GONE = summary(
    wt("wt-e", "/w/e", "main", [ag("e-coord")], PROJ["e"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own")], PROJ["c"]),
)
# F-05: a worktree whose path differs at every read of the same summary
FLIP = summary(
    wt("wt-f", "/w/a", "topic-f", [ag("f-coord")], None),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="f-coord")], PROJ["c"]),
)

# iss-00648: the coordinator directs a helper in its own band item too (a band child)
BAND_KID = summary(
    wt("wt-a", "/w/a", "main", [ag("a-coord"), ag("a-help", parent="a-coord")], PROJ["a"], main=True),
    wt("wt-c2", "/w/c-2", "iss-00002", [ag("c-own", parent="a-coord")], PROJ["c"]),
)
BAND_BTN = '[data-cmd-agent="a-coord"]'
RUNS = [
    {"name": "off", "orca": False, "repos": REPOS, "docs": DOCS},
    {"name": "flat", "orca": {"summary": FLAT}, "repos": REPOS, "docs": DOCS},
    # a pair comes and goes
    {
        "name": "gone",
        "orca": {"summary": FLAT},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [{"summary": CROSS}, {"summary": FLAT}],
    },
    {
        "name": "cross",
        "orca": {"summary": FLAT},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [
            {"summary": CROSS},  # 1: the band and the line appear
            {"news": True},  # 2: the same summary
            {"summary": json.loads(json.dumps(CROSS))},  # 3: a new summary of the same shape
            {"tap": BAND_BTN},  # 4: the band's agent: its chat and its lines
            {"tap": BAND_BTN},  # 5: again: closed
            {"tap": BAND_BTN},  # 6
            {"key": "Escape"},  # 7: closed
            {"tap": BAND_BTN},  # 8
            {"click": '.panel [data-act="close"]'},  # 9: closed
            {"tap": '[data-repo="github.com/o/c"] [data-id="iss-00002"] .orca-mark'},  # 10: the mark in the box
            {"summary": FLAT},  # 11: the pair is gone
        ],
    },
    {
        "name": "other",
        "orca": {"summary": FLAT},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [
            {"wheel": {"dx": 0, "dy": 30}},  # 1: the reader moves the graph
            {"summary": OTHER},  # 2: "ほかの場所" above every frame: the frames move, the top-most stays on the screen
        ],
    },
    {"name": "otherFirst", "orca": {"summary": FLAT}, "repos": REPOS, "docs": DOCS, "steps": [{"summary": OTHER}]},
    {
        "name": "bandKid",
        "orca": {"summary": FLAT},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [
            {"summary": BAND_KID},  # 1
            {"tap": BAND_BTN},  # 2: the coordinator chosen
            {"tap": '[data-repo="github.com/o/c"] [data-id="iss-00002"] .orca-mark'},  # 3: the box's agent chosen
        ],
    },
    {
        "name": "keep",
        "range": "next",
        "orca": {"summary": KEEP_GONE},
        "repos": [*REPOS, listed("e")],
        "docs": E_DOCS,
        "steps": [{"summary": KEEP}, {"summary": KEEP_GONE}],
    },
    {
        # F-05: a summary whose worktree is in a's band and in "ほかの場所" by turns at every read; news of it again;
        # another such summary (the count starts again); a plain summary
        "name": "flip",
        "orca": {"summary": FLAT},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [
            {"flip": {"summary": FLIP, "worktree": "wt-f", "paths": ["/z/none", "/w/a"]}},
            {"news": True},
            {"flip": {"summary": json.loads(json.dumps(FLIP)), "worktree": "wt-f", "paths": ["/z/none", "/w/a"]}},
            {"summary": json.loads(json.dumps(FLIP))},
        ],
    },
]


RUNS += [
    {
        # iss-00646 T-03: the still mark and the watching on the cross-repository structure
        "name": "motion",
        "io": True,
        "orca": {"summary": CROSS},
        "repos": REPOS,
        "docs": DOCS,
        "steps": [
            {"advance": 400},  # 1
            {"wheel": {"dx": 0, "dy": 30}},  # 2
            {"advance": 200},  # 3
            {"advance": 150},  # 4
            {"tell": {"sel": ".cl-ph, .cr", "hit": False}},  # 5
            {"hidden": True},  # 6
            {"hidden": False},  # 7
            {"wheel": {"dx": 0, "dy": 30}},  # 8
            {"summary": FLAT},  # 9: the layers gone
        ],
    },
]


@pytest.fixture(scope="module")
def drawn(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    path = tmp_path_factory.mktemp("allcmdscreen") / "request.json"
    path.write_text(json.dumps({"runs": RUNS}), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)["runs"]
    assert all(r["audit"] == "gone" for r in out.values())
    return out


@pytest.fixture(scope="module")
def runs(drawn: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {name: r["shots"] for name, r in drawn.items()}


def _sec(shot: dict[str, Any], name: str) -> dict[str, Any]:
    return next(s for s in shot["sections"] if s["key"] == key(name))


def test_without_a_pair_there_is_no_layer_and_the_world_is_as_today(runs: dict[str, Any]) -> None:
    off, flat = runs["off"][0], runs["flat"][0]
    for shot in (off, flat):
        assert shot["layers"] == [] and shot["leads"] == [] and shot["bandItems"] == []
        assert "gx-cmd" not in shot["html"] and "gx-band" not in shot["html"]
    # a pair that goes away leaves the world as it was
    first, came, gone = runs["gone"]
    assert came["layers"] and gone["layers"] == [] and gone["html"] == first["html"]
    assert runs["cross"][11]["layers"] == []


def test_a_pair_draws_one_of_each_layer_and_a_band_in_its_frame(runs: dict[str, Any]) -> None:
    before, shot = runs["cross"][0], runs["cross"][1]
    assert shot["layers"] == ["gx-cmd", "gx-cmd-top", "gx-band"]
    a0, a1 = _sec(before, "a"), _sec(shot, "a")
    assert a1["h"] == a0["h"] + BAND_H and a1["body"]["y"] == a0["body"]["y"] + BAND_H
    item = shot["bandItems"][0]
    assert item["label"] == "main のチェックアウト"
    assert item["y"] == a1["y"] + 40 + BAND_TOP and item["x"] == a1["x"] + 16
    assert a1["y"] + 40 <= item["y"] and item["y"] + ITEM_H <= a1["body"]["y"]
    # iss-00646 R-02: the layers are not SVGs; each line has SVGs of its own box, none as big as the world
    assert len(shot["layerTags"]) >= 2 and set(shot["layerTags"]) == {"div"} and shot["svgSizes"]
    world = [shot["size"][0].removesuffix("px"), shot["size"][1].removesuffix("px")]
    assert all(size != world for size in shot["svgSizes"])


def test_the_line_runs_from_the_band_to_the_mark_in_the_other_repository(runs: dict[str, Any]) -> None:
    shot = runs["cross"][1]
    d = shot["paths"]["a-coord>c-own"]
    start = [float(v) for v in d.split()[1:3]]
    item = shot["bandItems"][0]
    assert item["x"] <= start[0] <= item["x"] + item["w"] and start[1] == item["y"]  # iss-00648: the item's top
    c = _sec(shot, "c")
    box = c["boxes"]["iss-00002"]
    end = shot["arrows"]["a-coord>c-own"]  # the arrowhead's tip on the box's top
    assert c["body"]["x"] + box["x1"] < end[0] < c["body"]["x"] + box["x2"]
    assert end[1] == c["body"]["y"] + box["y1"]
    assert [float(v) for v in d.split()[-2:]] == end
    assert shot["endParts"]["a-coord>c-own"] == ["cl-in", "cl-arrow"] and shot["dots"] == 0


def test_a_band_childs_ring_is_in_the_band_and_follows_the_choice(runs: dict[str, Any]) -> None:
    """iss-00648 T-03 / R-04: the band child's arrowhead in .gx-cmd-top and its ring in .gx-band-cr, highlighted with
    its coordinator, faded when the box's agent is chosen."""
    shot, chosen, other = runs["bandKid"][1], runs["bandKid"][2], runs["bandKid"][3]
    assert shot["endParts"] == {"a-coord>a-help": ["cl-arrow"], "a-coord>c-own": ["cl-in", "cl-arrow"]}
    assert shot["bandMarks"] == {"a-coord>a-help": ""} and shot["dots"] == 0
    assert chosen["bandMarks"] == {"a-coord>a-help": "is-cmd-hl"}
    assert other["bandMarks"] == {"a-coord>a-help": "is-cmd-off"}


def test_news_never_lays_out_or_composes_again_for_the_same_shape(runs: dict[str, Any]) -> None:
    shots = runs["cross"]
    first, same, copied = shots[1], shots[2], shots[3]
    assert same["stats"]["layouts"] == first["stats"]["layouts"] == copied["stats"]["layouts"]
    assert same["stats"]["composes"] == first["stats"]["composes"] == copied["stats"]["composes"]
    assert [s["id"] for s in same["sections"]] == [s["id"] for s in first["sections"]]
    assert [s["id"] for s in copied["sections"]] == [s["id"] for s in first["sections"]]
    assert same["cmd"] == first["cmd"]  # the same summary draws nothing again
    assert copied["lines"] == first["lines"]


def test_pressing_the_band_agent_opens_its_chat_and_highlights_its_lines(runs: dict[str, Any]) -> None:
    shots = runs["cross"]
    on = shots[4]
    assert on["panel"]["open"] and on["panel"]["agent"] == "a-coord"
    assert "/embed/agent?id=a-coord" in on["panel"]["iframe"]["src"]
    assert on["pressed"] == {"a-coord": "true"}
    assert on["lines"] == {"a-coord>c-own": "is-cmd-hl"}
    for closed in (shots[5], shots[7], shots[9]):
        assert not closed["panel"]["open"] and closed["panel"]["agent"] is None
        assert closed["pressed"] == {"a-coord": "false"} and closed["lines"] == {"a-coord>c-own": ""}
    assert shots[6]["panel"]["agent"] == "a-coord" and shots[8]["panel"]["agent"] == "a-coord"


def test_a_mark_in_a_box_selects_its_scope_opens_the_agents_tab_and_highlights(runs: dict[str, Any]) -> None:
    shot = runs["cross"][10]
    assert shot["selected"] == ["iss-00002"]
    assert shot["panel"]["open"] and shot["panel"]["agent"] is None
    assert shot["lines"] == {"a-coord>c-own": "is-cmd-hl"}


def test_the_other_places_band_sits_above_every_frame(runs: dict[str, Any]) -> None:
    before, shot = runs["otherFirst"][0], runs["otherFirst"][1]
    assert [lead["text"] for lead in shot["leads"]] == ["ほかの場所"]
    for name in ("a", "c"):
        assert _sec(shot, name)["y"] == _sec(before, name)["y"] + OTHER_H
    item = next(it for it in shot["bandItems"] if it["label"] == "repo-x · topic-x")
    assert item["y"] == 8 + OTHER_TOP
    # without the reader's move, the first view is placed again (the same transform)
    assert shot["t"] == before["t"]


def test_a_new_band_shape_keeps_the_top_most_frame_on_the_screen_after_a_move(runs: dict[str, Any]) -> None:
    moved, shot = runs["other"][1], runs["other"][2]
    assert shot["leads"] and shot["stats"]["composes"] > moved["stats"]["composes"]
    top = min(moved["sections"], key=lambda s: s["body"]["y"] if s["body"] else 1e9)
    after = _sec(shot, top["key"].rsplit("/", 1)[1])
    assert after["body"]["y"] == top["body"]["y"] + OTHER_H
    t0, t1 = moved["t"], shot["t"]
    assert t0 and t1 and t0["s"] == t1["s"]
    assert t1["tx"] + after["body"]["x"] * t1["s"] == pytest.approx(t0["tx"] + top["body"]["x"] * t0["s"])
    assert t1["ty"] + after["body"]["y"] * t1["s"] == pytest.approx(t0["ty"] + top["body"]["y"] * t0["s"])


def test_a_repository_with_nothing_in_next_is_kept_for_its_coordinator(runs: dict[str, Any]) -> None:
    before, kept, gone = runs["keep"]
    assert key("e") not in {s["key"] for s in before["sections"]}
    e = _sec(kept, "e")
    assert e["kind"] in {"quiet", "empty"} and e["body"] is None
    assert e["h"] == 40 + BAND_H + 16
    assert any(it["label"] == "main のチェックアウト" and it["y"] == e["y"] + 40 + BAND_TOP for it in kept["bandItems"])
    assert kept["lines"] == {"e-coord>c-own": ""}
    assert key("e") not in {s["key"] for s in gone["sections"]} and gone["layers"] == []


def test_the_band_shape_composes_again_at_most_twice_for_the_same_places(runs: dict[str, Any]) -> None:
    first, flipped, again, reset, plain = runs["flip"]
    assert flipped["stats"]["composes"] - first["stats"]["composes"] == 2
    # at the limit the frames have a's band and the parent sits in "ほかの場所" (no row there): its pair is not drawn
    assert flipped["lines"] == {} and flipped["leads"] == []
    assert again["stats"]["composes"] == flipped["stats"]["composes"]
    # another summary: the count starts again
    assert reset["stats"]["composes"] - again["stats"]["composes"] == 2
    # a summary that holds still: its line in a's band, without composing again (the shape is a's band)
    assert plain["lines"] == {"f-coord>c-own": ""}
    assert plain["stats"]["layouts"] == first["stats"]["layouts"]


def test_the_legend_row_only_with_orca(runs: dict[str, Any]) -> None:
    assert runs["flat"][0]["legend"] is True
    assert runs["off"][0]["legend"] is False


def test_the_cmd_audit(runs: dict[str, Any]) -> None:
    audit = runs["cross"][1]["audit"]
    for name in ("links", "arcs", "boxOverlaps", "edgeOverlaps", "crowded", "spotMissing", "heads"):
        assert isinstance(audit[name], (int, float)), name
    assert "spotDrift" in audit  # the fake DOM has no offsets: measured in the browser (T-06)
    assert audit["links"] == 1 and audit["boxOverlaps"] == 0 and audit["edgeOverlaps"] == 0
    assert audit["layers"][-3:] == ["gx-cmd", "gx-cmd-top", "gx-band"]
    assert len(audit["pointer"]) == 2
    flat = runs["flat"][0]["audit"]
    assert flat["links"] == 0 and flat["layers"] == ["ax-repo", "ax-repo"]


def test_the_motion_stills_and_watches_on_the_cross_repository_structure(drawn: dict[str, Any]) -> None:
    """iss-00646 T-03 / R-03, R-04, F-02: the same part as the structure graph's, on this screen."""
    shots = drawn["motion"]["shots"]
    assert [s["still"] for s in shots] == [True, False, True, True, False, False, True, False, True, False]
    first = shots[1]
    assert first["phases"] > 0
    assert first["observed"]["live"] == 1 and first["observed"]["count"] == first["phases"] + 1
    assert first["observed"]["roots"][0].split()[0] == "gx-view"
    assert first["motion"] == {"phases": first["phases"], "ripples": 1, "off": 0, "still": False}
    assert shots[5]["off"] == first["phases"] + 1 and shots[5]["motion"]["off"] == first["phases"] + 1
    gone = shots[9]
    assert gone["layers"] == [] and gone["observed"]["live"] == 0 and not gone["still"]
    assert drawn["motion"]["left"] == {"observed": 0, "timers": 0, "listeners": 0, "still": False}
    for name, run in drawn.items():
        assert run["left"]["observed"] == 0 and run["left"]["timers"] == 0, name
