"""The command lines and the band on the structure graph (iss-00616 T-04, T-05).

T-04 reads the shipped CSS: the command tokens in the three theme blocks of `app.css` (their hue and contrast computed
here), the layers, the flowing dots, the ripples, the reduced motion and the box rule in `graph.css`, and the legend's
rows. T-05 draws `views/graph.js` with the fake DOM and the fake orca (`tests/js/dashboard_graph_command_screen.mjs`):
the layers and their order, a summary's news that never lays out again, the band's chat, the highlight, the first
view and "fit". Every value is synthetic.
"""

from __future__ import annotations

import colorsys
import copy
import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from tests.unit.presentation.test_dashboard_graph_command import FIVE, ag, structure, summary, wt
from tests.unit.presentation.test_dashboard_graph_js import ASSETS, ROOT, _node

if TYPE_CHECKING:
    from pathlib import Path

HARNESS = ROOT / "tests" / "js" / "dashboard_graph_command_screen.mjs"
APP_CSS = (ASSETS / "app.css").read_text(encoding="utf-8")
GRAPH_CSS = (ASSETS / "views" / "graph.css").read_text(encoding="utf-8")
GRAPH_JS = (ASSETS / "views" / "graph.js").read_text(encoding="utf-8")


def _run(tmp_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    path = tmp_path / "request.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    result = subprocess.run(
        [_node(), str(HARNESS), str(ASSETS), str(path)], capture_output=True, text=True, timeout=600, check=False
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- T-04: the colour tokens -----------------------------------------------------------------------------------


def _blocks() -> dict[str, str]:
    """The light :root block, the dark block of prefers-color-scheme and the explicit dark block of app.css."""
    media = APP_CSS.index("@media (prefers-color-scheme: dark)")
    explicit = APP_CSS.index(':root[data-theme="dark"] {')
    return {"light": APP_CSS[:media], "dark": APP_CSS[media:explicit], "explicit": APP_CSS[explicit : explicit + 6000]}


def _token(block: str, name: str) -> str:
    found = re.findall(rf"{re.escape(name)}:\s*([^;]+);", block)
    assert found, name
    return found[0].strip()


def _rgb(value: str) -> tuple[float, float, float]:
    assert re.fullmatch(r"#[0-9a-f]{6}", value), value
    r, g, b = (int(value[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return r, g, b


def _hue(value: str) -> float:
    return colorsys.rgb_to_hls(*_rgb(value))[0] * 360


def _luminance(value: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in _rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_the_command_tokens_in_the_three_theme_blocks() -> None:
    """T-04 / R-05: --sd-cmd and --sd-cmd-glow in light, dark and the explicit dark theme."""
    blocks = _blocks()
    assert APP_CSS.count("--sd-cmd:") == 3 and APP_CSS.count("--sd-cmd-glow:") == 3
    assert {name: _token(b, "--sd-cmd") for name, b in blocks.items()} == {
        "light": "#8a8100",
        "dark": "#fff04d",
        "explicit": "#fff04d",
    }
    assert _token(blocks["light"], "--sd-cmd-glow") == "rgb(255 236 64 / 45%)"
    assert (
        _token(blocks["dark"], "--sd-cmd-glow")
        == _token(blocks["explicit"], "--sd-cmd-glow")
        == "rgb(255 240 77 / 22%)"
    )


def test_the_command_colour_is_yellower_than_blocked_and_readable() -> None:
    """T-04 / R-05: 10° or more toward yellow than --sd-blocked; 3:1 or more against the graph's --ds-bg-2."""
    for name, block in _blocks().items():
        cmd, blocked, bg = (_token(block, t) for t in ("--sd-cmd", "--sd-blocked", "--ds-bg-2"))
        assert _hue(cmd) - _hue(blocked) >= 10, (name, _hue(cmd), _hue(blocked))
        assert _contrast(cmd, bg) >= 3, (name, _contrast(cmd, bg))
    light = _blocks()["light"]
    assert _hue("#8a8100") == pytest.approx(56.1, abs=0.05)
    assert _hue(_token(light, "--sd-blocked")) == pytest.approx(39.3, abs=0.05)
    assert _contrast("#8a8100", _token(light, "--ds-bg-2")) == pytest.approx(3.75, abs=0.005)
    assert _contrast("#fff04d", _token(_blocks()["dark"], "--ds-bg-2")) == pytest.approx(15.1, abs=0.05)


# --- T-04: graph.css ------------------------------------------------------------------------------------------------


def _rules(css: str) -> list[tuple[str, str]]:
    """(selector, body) of every innermost rule (inside an @media too), comments left out."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(m.group(1).strip(), m.group(2)) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


def _rule(selector: str) -> str:
    found = [body for sel, body in _rules(GRAPH_CSS) if sel == selector]
    assert found, selector
    return " ".join(found)


COMMAND = re.compile(r"\.gx-cmd|\.gx-band|\.lg-cmd|\.lg-cr|\.cl(?![\w-])|\.cr(?![\w-])")


def test_the_layers_stack_and_never_take_a_press() -> None:
    """T-04 / R-03, R-06: the lines above the frames and under the boxes, the ends above the groups and under the lines."""
    both = _rule(".gx .gx-world > .gx-cmd, .gx .gx-world > .gx-cmd-top")
    assert "pointer-events: none" in both and "position: absolute" in both and "overflow: visible" in both
    assert "z-index: 1" in _rule(".gx .gx-world > .gx-cmd")
    assert "z-index: 3" in _rule(".gx .gx-world > .gx-cmd-top")
    assert "z-index: 6" in _rule(".gx .gx-world > .gx-band")
    # the frames 1, the boxes and groups 2, the dependency lines 5 (unchanged)
    assert "z-index: 1" in _rule(".gx .gx-world > .gx-frame")
    assert "z-index: 2" in _rule(".gx .gx-world > .gx-box, .gx .gx-world > .gx-clean")
    assert "z-index: 5" in _rule(".gx .gx-edges")


def test_the_dots_flow_and_the_ripples_grow() -> None:
    """T-04 / R-04: the flowing dots move stroke-dashoffset over 2.5s; waiting stands still; done is faint; ripples scale."""
    flow = _rule('.gx .cl[data-state="flow"] :is(.cl-line, .cl-stub)')
    assert "stroke-dasharray: 0.1 7.9" in flow and "animation: sd-cmd-flow 2.5s linear infinite" in flow
    wait = _rule('.gx .cl[data-state="wait"] :is(.cl-line, .cl-stub)')
    assert "stroke-dasharray: 0.1 7.9" in wait and "animation: none" in wait
    done = _rule('.gx .cl[data-state="done"] :is(.cl-line, .cl-stub)')
    assert "opacity: .35" in done and "animation: none" in done and "dasharray" not in done
    flow_frames = re.search(r"@keyframes sd-cmd-flow \{(.*?)\}\s*\}", GRAPH_CSS, re.S)
    assert flow_frames and "stroke-dashoffset: calc(-1 * var(--cl-len))" in flow_frames.group(1)
    ripple = re.search(r"@keyframes sd-cmd-ripple \{(.*?)\}\s*\}", GRAPH_CSS, re.S)
    assert ripple
    props = set(re.findall(r"([a-z-]+):", ripple.group(1)))
    assert props == {"transform", "opacity"}
    assert "animation-delay: 1.2s" in _rule(".gx .cr .cr-b")


def test_reduced_motion_stops_the_dots_and_the_ripples() -> None:
    """T-04 / R-04: no animation and one still ring."""
    media = GRAPH_CSS[GRAPH_CSS.rindex("@media (prefers-reduced-motion: reduce)") :]
    rules = dict(_rules(media))
    stop = rules[".gx .cl-line, .gx .cl-stub, .gx .cl[data-state] :is(.cl-line, .cl-stub)"]
    assert "animation: none" in stop
    assert "animation: none" in rules[".gx .cr circle"] and "transform: scale(1.4)" in rules[".gx .cr circle"]
    assert "display: none" in rules[".gx .cr-b"]


def test_a_box_never_shrinks_its_rows() -> None:
    """T-04 / D-02: in the column a two-line title (and every row) keeps its height; the rest goes to the agents' margin."""
    assert "flex-shrink: 0" in _rule(".gx .gx-box > *")


def test_the_band_ripples_rule() -> None:
    """T-04 / R-04: the band's own ripple layer lies over its items and takes no press."""
    rule = _rule(".gx .gx-band > .gx-band-cr")
    assert "position: absolute" in rule and "pointer-events: none" in rule and "overflow: visible" in rule


def test_a_box_puts_its_agents_on_its_lower_edge() -> None:
    """T-04 / D-02: the box is a column and its row of agents takes the rest (the coordinator's decision)."""
    box = _rule(".gx .gx-box")
    assert "display: flex" in box and "flex-direction: column" in box
    agents = _rule(".gx .gx-box > .gx-agents")
    assert "margin-top: auto" in agents and "padding-top: 4px" in agents
    assert "display: flex; margin-top: 4px;" in _rule(".gx .gx-agents")  # the frames' rule stays


def test_the_band_follows_the_band_constants() -> None:
    """T-04 / D-05: the item's border 1, padding 6, the label's gap 6 and the buttons 52 wide (command.js BAND)."""
    item = _rule(".gx .gx-band-item")
    assert "padding: 0 6px" in item and "border: 1px solid var(--ds-border)" in item and "white-space: nowrap" in item
    assert "margin-right: 6px" in _rule(".gx .gx-band-lab") and "text-overflow: ellipsis" in _rule(".gx .gx-band-lab")
    assert "width: 52px" in _rule(".gx .gx-band-agent")
    assert "box-shadow: inset 0 -2px 0 var(--sd-cmd)" in _rule('.gx .gx-band-agent[aria-pressed="true"]')


def test_the_command_rules_use_no_forbidden_drawing() -> None:
    """T-04 / R-04: no SVG animate, animateMotion, canvas or blur in the command rules and their keyframes."""
    bodies = [f"{sel}{{{body}}}" for sel, body in _rules(GRAPH_CSS) if COMMAND.search(sel)]
    frames = re.findall(r"@keyframes sd-cmd-[\w-]+ \{.*?\}\s*\}", GRAPH_CSS, re.S)
    assert len(bodies) >= 15 and len(frames) == 2
    text = "\n".join(bodies + frames)
    for word in ("<animate", "animateMotion", "canvas", "blur("):
        assert word not in text, word
    assert "<animate" not in GRAPH_JS and "animateMotion" not in GRAPH_JS


def test_the_command_colours_are_only_the_tokens() -> None:
    """T-04 / R-05: the command rules colour with --sd-cmd, --sd-cmd-glow and the design system's variables only."""
    colours = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgb\(|hsl\(")
    assert [sel for sel, body in _rules(GRAPH_CSS) if COMMAND.search(sel) and colours.search(body)] == []


# --- T-04: the legend ---------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def legend(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    return _run(tmp_path_factory.mktemp("legend"), {"legend": True})["legend"]


def test_the_legend_by_default_is_unchanged(legend: dict[str, str]) -> None:
    """T-04 / R-05: renderLegend's default and cmd false draw the same; cmd adds only the two rows to "そのほか"."""
    assert legend["plain"] == legend["off"]
    assert "指揮" not in legend["plain"]
    rows = (
        '<li class="wide"><span><span class="lg-cmd"></span></span>指揮（親 → 子）</li>'
        '<li><span><span class="lg-cr"></span></span>指揮している親（波紋）</li>'
    )
    assert legend["on"] == legend["plain"].replace("親子（木）</li></ul>", f"親子（木）</li>{rows}</ul>")
    assert legend["closedOn"].replace(rows, "") == legend["closed"]


# --- T-05: the page -----------------------------------------------------------------------------------------------

NO_PARENT = copy.deepcopy(FIVE)
for _w in NO_PARENT["worktrees"]:
    for _a in _w["agents"]:
        _a.pop("parent", None)
# the same agents, the researcher now working: a new summary whose rows of marks do not change
WORKING = copy.deepcopy(FIVE)
WORKING["worktrees"][0]["agents"][1]["mark"] = "working"
# the coordinator gone
GONE = summary(*[w | {"agents": [a for a in w["agents"] if a["id"] != "a-coord"]} for w in FIVE["worktrees"]])

BAND = '[data-cmd-agent="a-coord"]'
RUNS: list[dict[str, Any]] = [
    {"name": "plain", "orca": {"summary": NO_PARENT}},
    {"name": "noorca", "orca": False},
    {
        "name": "news",
        "orca": {"summary": FIVE},
        "steps": [{"news": True}, {"render": True}, {"summary": WORKING}, {"summary": NO_PARENT}, {"summary": FIVE}],
    },
    {
        "name": "band",
        "orca": {"summary": FIVE},
        "steps": [
            {"tap": BAND},  # 1: open
            {"revision": "r2"},  # 2: the structure again
            {"summary": WORKING},  # 3: the lines again
            {"key": "Escape"},  # 4
            {"key": "Enter", "on": BAND},  # 5
            {"click": '.panel [data-act="close"]'},  # 6
            {"tap": BAND},  # 7
            {"tap": BAND},  # 8: the same agent again
            {"key": " ", "on": BAND},  # 9
            {"tap": ".gx-view"},  # 10: an empty place
            {"tap": BAND},  # 11
            {"summary": GONE},  # 12: the coordinator left
        ],
    },
    {
        "name": "mark",
        "orca": {"summary": FIVE},
        "steps": [
            {"tap": '[data-orca-scope="iss-00021"] [data-agent-id="a-own21"]'},
            {"tap": '.gx-box[data-id="iss-00024"]'},
        ],
    },
    {
        "name": "view",
        "orca": {"summary": NO_PARENT},
        "steps": [{"styled": True}, {"summary": FIVE}, {"act": "fit"}, {"summary": NO_PARENT}, {"act": "fit"}],
    },
    {"name": "first", "orca": {"summary": FIVE}, "steps": [{"styled": True}]},
    {"name": "again", "orca": {"summary": FIVE}, "styled": True},
    {
        "name": "order",
        "orca": {
            "summary": summary(
                wt(
                    "wt-main",
                    "/w/r",
                    "main",
                    [ag("a-coord"), ag("a-idle"), ag("a-research", parent="a-coord")],
                    main=True,
                ),
                wt("wt-21", "/w/r-21", "iss-00021", [ag("a-own21", parent="a-coord")]),
            ),
            "order": ["a-research", "a-idle", "a-coord"],
        },
    },
]


@pytest.fixture(scope="module")
def runs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, list[dict[str, Any]]]:
    return _run(tmp_path_factory.mktemp("screen"), {"doc": structure(), "runs": RUNS})["runs"]


LAYERS = ("gx-cmd", "gx-cmd-top", "gx-band")


def _plain(layers: list[str]) -> list[str]:
    return [c for c in layers if c.split()[0] not in LAYERS]


def test_without_a_pair_there_is_no_layer(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-02, F-01: no parent or no Orca: no layer, no band; the pairs leaving restore the same world HTML."""
    for name in ("plain", "noorca"):
        shot = runs[name][0]
        assert shot["layers"] == _plain(shot["layers"]) and shot["cmd"] is None and shot["band"] is None, name
    news = runs["news"]
    assert news[4]["layers"] == _plain(news[4]["layers"])
    assert news[4]["html"] == runs["plain"][0]["html"]
    assert news[5]["band"] is not None


def test_the_layers_in_their_order(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-03: frames, .gx-cmd, boxes, groups, .gx-cmd-top, the dependency lines, the band."""
    layers = [c.split()[0] for c in runs["news"][0]["layers"]]
    cmd, top = layers.index("gx-cmd"), layers.index("gx-cmd-top")
    assert all(c == "gx-frame" for c in layers[:cmd]) and cmd > 0
    assert layers[cmd + 1] == "gx-box"
    assert "gx-frame" not in layers[cmd:]
    assert layers[top + 1 :] == ["gx-edges", "gx-band"]
    assert all(c in ("gx-box", "gx-clean") for c in layers[cmd + 1 : top])
    assert runs["news"][0]["audit"]["layers"] == runs["news"][0]["layers"]


def test_news_never_lays_out_again_and_the_same_input_draws_nothing(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-08: the same summary keeps the layers' elements; a new one draws only the layers, not the layout."""
    news = runs["news"]
    first = news[0]
    for shot in news[1:3]:  # the same summary's news, the shell's render
        assert (shot["edges"], shot["cmd"], shot["top"], shot["band"]) == (
            first["edges"],
            first["cmd"],
            first["top"],
            first["band"],
        )
    working = news[3]
    assert working["edges"] == first["edges"]  # routeLayout was not called again
    assert working["cmd"] != first["cmd"]
    assert first["states"]["a-coord>a-research"] == "wait" and working["states"]["a-coord>a-research"] == "flow"
    assert all(shot["edges"] == first["edges"] for shot in news)


def test_the_band_shows_its_items(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-02: the main checkout with the coordinator and the researcher, then the other repository."""
    shot = runs["news"][0]
    assert shot["bandItems"] == [
        "left:24px;top:-16px;width:249px;height:28px",
        "left:283px;top:-16px;width:157px;height:28px",
    ]
    assert shot["bandLabels"] == [
        "main のチェックアウト：label a-coord",
        "main のチェックアウト：label a-research",
        "other · main：label x-coord",
    ]
    assert list(runs["order"][0]["pressed"]) == ["a-research", "a-coord"]  # orderAgents' order


def _hl(shot: dict[str, Any]) -> dict[str, Any]:
    return {key: {k: v for k, v in shot[key].items() if v} for key in ("lines", "ends", "ripples")}


OFF_ALL: dict[str, dict[str, str]] = {key: {} for key in ("lines", "ends", "ripples")}


def test_pressing_the_band_agent_opens_its_chat(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-06: its lines stand out in both layers, the others fade; the panel frames /embed/agent?id=…."""
    shot = runs["band"][1]
    hl = {
        "a-coord>a-e30": "is-cmd-hl",
        "a-own21>a-impl21": "is-cmd-off",
        "a-coord>a-own21": "is-cmd-hl",
        "x-coord>a-own22": "is-cmd-off",
        "a-coord>a-research": "is-cmd-hl",
    }
    assert _hl(shot) == {
        "lines": hl,
        "ends": hl,
        "ripples": {"a-coord": "is-cmd-hl", "a-own21": "is-cmd-off", "x-coord": "is-cmd-off"},
    }
    assert shot["cmdSel"] == [True, True]
    assert shot["pressed"] == {"a-coord": "true", "a-research": "false", "x-coord": "false"}
    panel = shot["panel"]
    assert panel["open"] and panel["agent"] == "a-coord"
    assert panel["iframe"]["src"] == "http://192.0.2.1:8791/embed/agent?id=a-coord&theme=light"
    assert panel["iframe"]["sandbox"] == "allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"
    assert panel["iframe"]["referrer"] == "no-referrer"
    assert panel["text"] == "claude · main のチェックアウト"


def test_the_chat_stays_while_the_graph_draws_again(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-06: a new revision and new lines keep the same iframe and the highlight."""
    band = runs["band"]
    frame = band[1]["panel"]["iframe"]["id"]
    assert band[2]["panel"]["iframe"]["id"] == frame and band[3]["panel"]["iframe"]["id"] == frame
    assert band[3]["cmd"] != band[1]["cmd"]  # the lines were drawn again
    assert _hl(band[3]) == _hl(band[1])


def test_escape_close_again_and_an_empty_place_end_it(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-06: Esc, the close button, the same agent again and an empty tap; Enter and Space open as a tap does."""
    band = runs["band"]
    opened = band[1]
    for i in (4, 6, 8, 10):
        shot = band[i]
        assert not shot["panel"]["open"] and shot["panel"]["iframe"] is None, i
        assert _hl(shot) == OFF_ALL and shot["cmdSel"] == [False, False], i
        assert shot["pressed"]["a-coord"] == "false", i
    for i in (5, 7, 9, 11):
        assert _hl(band[i]) == _hl(opened) and band[i]["panel"]["iframe"]["src"] == opened["panel"]["iframe"]["src"], i


def test_a_gone_agent_ends_the_highlight_and_its_chat(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-06: the coordinator leaves the summary: the panel closes."""
    shot = runs["band"][12]
    assert not shot["panel"]["open"] and shot["panel"]["agent"] is None
    assert "a-coord" not in shot["pressed"]
    assert all(not v for v in shot["lines"].values())


def test_a_mark_in_a_box_highlights_its_agent(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-06: the box is selected, its agent's lines stand out; a tap on a box without a mark ends it."""
    mark, other = runs["mark"][1], runs["mark"][2]
    assert mark["selected"] == ["iss-00021"]
    assert {k for k, v in mark["lines"].items() if v == "is-cmd-hl"} == {"a-own21>a-impl21", "a-coord>a-own21"}
    assert mark["ripples"]["a-own21"] == "is-cmd-hl" and mark["ripples"]["a-coord"] == "is-cmd-hl"
    assert mark["panel"]["open"] and mark["panel"]["agent"] is None
    assert other["selected"] == ["iss-00024"] and _hl(other) == OFF_ALL


def test_a_band_parent_ripples_inside_the_band_over_its_items(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-04, D-03: a parent in the band ripples in the band's last child, at its button's middle; a box's
    parent still ripples in .gx-cmd-top. The highlight changes the band's ripples too."""
    shot = runs["news"][0]
    assert sorted(shot["bandRipples"]) == ["a-coord", "x-coord"]
    assert shot["topRipples"] == ["a-own21"]
    assert shot["bandLast"] == "gx-band-cr"
    for x, y in shot["bandRippleAt"]:
        assert y == -2  # the band's slot middle: top -16 + 28 / 2
        assert 24 < x < 273 or 283 < x < 440
    opened = runs["band"][1]
    assert opened["ripples"]["a-coord"] == "is-cmd-hl" and opened["ripples"]["x-coord"] == "is-cmd-off"
    assert opened["bandSel"] == [True]
    assert runs["band"][4]["bandSel"] == [False]


def test_the_first_view_on_a_return_holds_the_band(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-07: the screen's CSS already there (the first view placed at once) still starts above the band."""
    _, ty, s = _transform(runs["again"][0])
    assert ty == pytest.approx(48 + 32 * s)


def test_the_legend_row_only_with_orca(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-05."""
    assert runs["plain"][0]["legend"] is True
    assert runs["noorca"][0]["legend"] is False


def _transform(shot: dict[str, Any]) -> tuple[float, float, float]:
    m = re.fullmatch(r"translate\(([-\d.]+)px, ([-\d.]+)px\) scale\(([-\d.]+)\)", shot["transform"])
    assert m, shot["transform"]
    return float(m.group(1)), float(m.group(2)), float(m.group(3))


def test_the_band_never_moves_the_boxes_and_fit_shows_it(runs: dict[str, list[dict[str, Any]]]) -> None:
    """T-05 / R-07, R-08: the band coming and going keeps the zoom and the position; fit shows the band's top."""
    view = runs["view"]
    assert _transform(view[2]) == _transform(view[1])  # the band came
    assert view[2]["edges"] == view[1]["edges"] and view[2]["html"] != view[1]["html"]
    _, ty, s = _transform(view[3])  # fit with the band: from its top (-32) to the layout's bottom inside 48..792
    height = float(view[3]["size"][1].removesuffix("px"))
    assert ty - 32 * s >= 48 - 0.5 and ty + height * s <= 800 - 8 + 0.5
    assert _transform(view[4]) == _transform(view[3])  # the band went
    _, ty0, s0 = _transform(view[5])  # fit without it
    assert s0 >= s and ty0 >= 48 - 0.5
    # the first view of a summary with pairs starts above the band's top
    _, ty1, s1 = _transform(runs["first"][1])
    assert ty1 == pytest.approx(48 + 32 * s1)
