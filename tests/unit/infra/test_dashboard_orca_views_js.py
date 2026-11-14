"""orca-web marks in the structure graph, the board and the shared panel (iss-00592 T-03, T-04).

The node checks run the HTML parts and the small DOM helpers; the rest are static markers on the screens'
sources, which need a browser to run.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

DASHBOARD = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard"
VIEWS = DASHBOARD / "views"
SHARED = VIEWS / "_shared"
NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not installed")


def run_node(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        'import assert from "node:assert/strict";\n'
        + f"const parts = await import({json.dumps((SHARED / 'parts.js').as_uri())});\n"
        + f"const marks = await import({json.dumps((SHARED / 'orca_marks.js').as_uri())});\n"
        + "const out = {};\n"
        + textwrap.dedent(script)
        + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=30)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


def _function(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    end = source.index("\n}\n", start)
    return source[start:end]


# --- T-03: the slots in the graph and the board -------------------------------------------------------------


@needs_node
def test_the_slot_depends_only_on_the_scope_id_and_max(tmp_path: Path) -> None:
    out = run_node(
        """
        out.slot = parts.orcaSlot('iss-1"<x>', 2);
        out.again = parts.orcaSlot('iss-1"<x>', 2);
        """,
        tmp_path,
    )
    assert out["slot"] == '<span class="sd-orca" data-orca-scope="iss-1&quot;&lt;x&gt;" data-orca-max="2"></span>'
    assert out["again"] == out["slot"]


@needs_node
def test_the_card_holds_a_slot_only_when_asked(tmp_path: Path) -> None:
    out = run_node(
        """
        const ctx = {href: (p) => p, data: {scopes: []}};
        const bare = {id: "iss-00005", number: 5, kind: "issue", state: "doing", title: "t", path: "/p"};
        const marked = {...bare, downstream: 2};
        out.plain = parts.card(bare, ctx);
        out.plainOpts = parts.card(bare, ctx, {});
        out.orca = parts.card(bare, ctx, {orca: true});
        out.orcaMarks = parts.card(marked, ctx, {orca: true});
        out.marks = parts.card(marked, ctx);
        """,
        tmp_path,
    )
    slot = '<span class="sd-orca" data-orca-scope="iss-00005" data-orca-max="4"></span>'
    assert out["plain"] == out["plainOpts"]
    assert "sd-card__meta" not in out["plain"] and "sd-orca" not in out["plain"]
    assert f'<span class="sd-card__meta">{slot}</span>' in out["orca"]
    assert out["orcaMarks"].count("sd-card__meta") == 1
    assert f"{slot}</span>" in out["orcaMarks"]
    assert "sd-orca" not in out["marks"]


def test_graph_boxes_and_frames_end_their_rows_with_a_slot() -> None:
    source = (VIEWS / "graph.js").read_text()
    box = _function(source, "boxHtml")
    assert box.count('<div class="gx-marks">') == 2
    assert box.count("${orcaSlot(s.id, 2)}</div>`") == 2
    frame = _function(source, "frameHtml")
    assert "${orcaSlot(s.id, 3)}</div>`" in frame
    head = frame[frame.index("const head") : frame.index("const meta")]
    assert head.rstrip().endswith("${orcaSlot(s.id, 3)}</div>`;")


def test_the_box_size_does_not_change() -> None:
    layout = (VIEWS / "graph/layout.js").read_text()
    start = layout.index("export const SIZE = {")
    block = layout[start : layout.index("};", start)]
    for value in ("boxW: 178,", "boxH: 88,", "treeFrameW: 236,", "compactW: 236,", "head: 46,"):
        assert value in block, block


def test_graph_and_board_paint_after_drawing_and_on_news() -> None:
    graph = (VIEWS / "graph.js").read_text()
    render = _function(graph, "render")
    assert render.rstrip().endswith("paintOrca();")
    assert "orcaWatch.follow(ctx.orca)" in render
    paint = _function(graph, "paintOrca")
    assert "paintOrcaMarks(V.el.world, V.ctx, V.data)" in paint and "V.pn?.refreshOrca()" in paint
    assert "orcaWatch.stop()" in _function(graph, "dispose")

    board = (VIEWS / "board.js").read_text()
    render = _function(board, "render")
    assert render.index("renderPage(B.page, ctx)") < render.index("paintOrca()")
    assert "orcaWatch.follow(ctx.orca)" in render
    paint = _function(board, "paintOrca")
    assert "paintOrcaMarks(B.page, B.ctx, B.ctx.data)" in paint and "B.pn?.refreshOrca()" in paint
    assert "orcaWatch.stop()" in _function(board, "unmount")
    assert "card(item, ctx, { orca: true })" in board
    assert "card(item, ctx)" not in board


def test_pressing_a_mark_prefers_the_agents_tab() -> None:
    graph = (VIEWS / "graph.js").read_text()
    # A box's mark is pressed through the graph's taps; the panel takes the presses on its own heading's marks.
    tap = _function(graph, "onTap")
    assert 'closest(".sd-orca")' in tap and 'V.pn?.preferTab("agents")' in tap
    assert tap.index("select(id)") < tap.index("preferTab")
    board = _function((VIEWS / "board.js").read_text(), "onCardClick")
    assert 'closest(".sd-orca")' in board and 'B.pn?.preferTab("agents")' in board
    assert board.index("plainClick(event)") < board.index("preferTab")


@needs_node
def test_the_watch_follows_one_reader_at_a_time(tmp_path: Path) -> None:
    out = run_node(
        """
        const log = [];
        const reader = (name) => ({subscribe(fn) {log.push(`on ${name}`); return () => log.push(`off ${name}`);}});
        const a = reader("a"), b = reader("b");
        let calls = 0;
        const watch = marks.createOrcaWatch(() => calls++);
        watch.follow(a); watch.follow(a); watch.follow(b); watch.follow(null); watch.follow(b); watch.stop(); watch.stop();
        out.log = log;
        """,
        tmp_path,
    )
    assert out["log"] == ["on a", "off a", "on b", "off b", "on b", "off b"]


def test_slot_styles_stay_shared_and_leave_the_marks_to_orca_web() -> None:
    parts = (SHARED / "parts.css").read_text()
    assert "& .sd-card__meta:not(:has(> :not(.sd-orca:empty))) { display: none; }" in parts
    for path in [*DASHBOARD.glob("*.css"), *VIEWS.glob("*.css"), *SHARED.glob("*.css")]:
        text = path.read_text()
        assert ".orca-mark" not in text, path
        assert not re.search(r"\.orca-[a-z-]+\s*[{,]", text), path
    panel = (SHARED / "panel.js").read_text()
    assert "data-width" not in panel and "dataset.width" not in panel


# --- T-04: the panel's heading ------------------------------------------------------------------------------

PANEL_DOM = """
const PARTS = [".pn-grab", ".pn-top", ".pn-tabs", ".pn-body", ".pn-foot", ".pn-hl", ".pn-orca", ".pn-cover"];
class El {
  constructor(name) {this.name = name; this.dataset = {}; this.children = []; this.writes = 0; this.html = ""; this.scrollTop = 0;}
  set innerHTML(value) {this.html = value; this.writes++;}
  get innerHTML() {return this.html;}
  replaceChildren(...children) {this.children = children;}
  append(child) {this.children.push(child);}
  querySelectorAll() {return [];}
}
const listeners = {media: 0, observers: 0};
const theme = {dark: false};
globalThis.window = {addEventListener() {}, removeEventListener() {}};
globalThis.innerHeight = 800;
globalThis.matchMedia = () => ({
  get matches() {return theme.dark;},
  addEventListener(type) {assert.equal(type, "change"); listeners.media++;},
  removeEventListener(type) {assert.equal(type, "change"); listeners.media--;},
});
const observed = [];
globalThis.MutationObserver = class {
  constructor(fn) {this.fn = fn; observed.push(this);}
  observe(target, options) {assert.deepEqual(options.attributeFilter, ["data-theme"]); listeners.observers++;}
  disconnect() {listeners.observers--;}
};
globalThis.document = {
  documentElement: {dataset: {}, clientWidth: 1440},
  createElement(tag) {return {tag, dataset: {}};},
};
const aside = {
  classList: {add() {}, remove() {}},
  dataset: {}, style: {setProperty() {}, removeProperty() {}},
  setAttribute() {}, addEventListener(type, fn) {if (type === "click") this.click = fn;},
  closest() {return null;},
  built: 0, html: "",
  set innerHTML(value) {this.html = value; this.built++; this.parts = new Map(PARTS.map((s) => [s, new El(s)]));},
  get innerHTML() {return this.html;},
  querySelector(sel) {return this.parts?.get(sel) ?? null;},
  contains(el) {return [...(this.parts?.values() ?? [])].includes(el);},
};
const panelModule = await import(PANEL_URL);
const scope = {id: "iss-00007", number: 7, kind: "issue", state: "doing", title: "t", path: "/r/x/scopes/iss-00007", reason: {text: "r"}};
const structure = {scopes: [scope]};
const reader = (status = "ok") => ({status: () => status, origin: "http://192.0.2.1:8791", marks: () => null,
  forScope: (data, id) => (status === "ok" && id === scope.id ? [{id: "wt-7"}] : [])});
const stateOf = (ctx) => ({ctx: {href: (p) => p, data: structure, embed: false, ...ctx}, scope, doc: null, docState: "loading", byId: new Map([[scope.id, scope]])});
const pn = panelModule.createScopePanel(aside);
const part = (sel) => aside.querySelector(sel);
const scripts = () => part(".pn-orca").children.map((c) => `${c.src}|${c.dataset.worktree}|${c.dataset.theme}|${c.dataset.size}|${Object.keys(c.dataset).sort().join(",")}`);
"""


def run_panel(script: str, tmp_path: Path) -> dict:
    return run_node(
        f"const PANEL_URL = {json.dumps((SHARED / 'panel.js').as_uri())};\n" + PANEL_DOM + textwrap.dedent(script),
        tmp_path,
    )


@needs_node
def test_the_heading_row_is_built_once_and_redrawn_only_when_it_changes(tmp_path: Path) -> None:
    out = run_panel(
        """
        pn.show(stateOf({orca: reader()}));
        out.top = part(".pn-top").innerHTML;
        out.hl = part(".pn-hl").innerHTML;
        const writes = () => [part(".pn-top").writes, part(".pn-hl").writes, part(".pn-cover").writes];
        out.first = writes();
        pn.show(stateOf({orca: reader()}));
        out.second = writes();
        pn.show({...stateOf({orca: reader()}), scope: {...scope, title: "other"}});
        out.third = writes();
        out.built = aside.built;
        """,
        tmp_path,
    )
    top = out["top"]
    assert top.startswith('<div class="pn-head"><span class="pn-hl"></span><span class="pn-orca"></span>')
    assert '<button type="button" class="iconbtn pn-close" data-pn-act="close" aria-label="閉じる">' in top
    assert top.endswith('</button></div><div class="pn-cover"></div>')
    assert "pn-merge" in out["hl"] and 'data-orca-scope="iss-00007" data-orca-max="4"' in out["hl"]
    assert out["first"] == [1, 1, 1]
    assert out["second"] == [1, 1, 1]
    assert out["third"] == [1, 1, 2]
    assert out["built"] == 1


@needs_node
def test_the_open_button_follows_the_panel(tmp_path: Path) -> None:
    out = run_panel(
        """
        pn.show(stateOf({orca: reader()}));
        out.first = scripts();
        const first = part(".pn-orca").children[0];
        pn.show(stateOf({orca: reader()}));
        out.same = part(".pn-orca").children[0] === first;
        theme.dark = true;
        observed[0].fn();
        out.dark = scripts();
        pn.hide();
        out.hidden = scripts();
        theme.dark = false;
        pn.show(stateOf({orca: reader()}));
        out.again = scripts();
        aside.innerHTML = "<div>the cleanup list</div>";
        pn.show(stateOf({orca: reader()}));
        out.rebuilt = scripts();
        pn.show(stateOf({orca: reader(), embed: true}));
        out.embed = scripts();
        pn.show(stateOf({orca: reader("unreachable")}));
        out.unreachable = scripts();
        pn.show(stateOf({orca: null}));
        out.off = scripts();
        """,
        tmp_path,
    )
    light = "http://192.0.2.1:8791/embed/open-button.js|wt-7|light|sm|size,theme,worktree"
    assert out["first"] == [light]
    assert out["same"] is True
    assert out["dark"] == [light.replace("|light|", "|dark|")]
    assert out["hidden"] == []
    assert out["again"] == [light]
    assert out["rebuilt"] == [light]
    assert out["embed"] == [] and out["unreachable"] == [] and out["off"] == []


@needs_node
def test_prefer_tab_chooses_only_shared_tabs_and_marks_ask_for_it(tmp_path: Path) -> None:
    out = run_panel(
        """
        const selected = () => (part(".pn-tabs").innerHTML.match(/data-pn-tab="([a-z]+)" aria-selected="true"/) || [])[1] ?? null;
        pn.show(stateOf({orca: reader()}));
        out.start = selected();
        pn.preferTab("deps");
        out.deps = selected();
        pn.preferTab("no-such-tab");
        out.unknown = selected();
        const mark = {closest: (sel) => (sel === ".sd-orca" ? mark : null)};
        pn.preferTab("summary");
        aside.click({target: mark, button: 0});
        out.agents = selected();
        """,
        tmp_path,
    )
    assert out["deps"] == "deps"
    assert out["unknown"] == "deps"
    # "agents" arrives with iss-00593; until then a pressed mark keeps the tab.
    assert out["agents"] == "summary"
    panel = (SHARED / "panel.js").read_text()
    click = panel[panel.index('aside.addEventListener("click"') :]
    assert 'if (t.closest(".sd-orca")) {' in click and 'preferTab("agents");' in click


@needs_node
def test_the_theme_watch_ends_with_the_panel(tmp_path: Path) -> None:
    out = run_panel(
        """
        out.on = {...listeners};
        pn.destroy();
        out.off = {...listeners};
        """,
        tmp_path,
    )
    assert out["on"] == {"media": 1, "observers": 1}
    assert out["off"] == {"media": 0, "observers": 0}


def test_the_heading_css_keeps_the_row_and_the_close_button() -> None:
    css = (SHARED / "panel.css").read_text()
    for rule in (
        ".sd-pn .pn-head .iconbtn { margin-left: auto;",
        ".sd-pn .pn-hl { display: contents; }",
        ".sd-pn .pn-orca { display: inline-flex; align-items: center; height: 24px; flex: none; }",
        ".sd-pn .pn-orca:empty { display: none; }",
        ".sd-pn .pn-orca:not(:empty) { margin-left: auto; }",
        ".sd-pn .pn-orca:not(:empty) + .pn-close { margin-left: 0; }",
    ):
        assert rule in css, rule
    panel = (SHARED / "panel.js").read_text()
    draw = panel[panel.index("  function draw() {") : panel.index("// --- The phone sheet")]
    assert draw.rstrip().endswith("refreshOrca();\n  }")
    refresh = panel[panel.index("  function refreshOrca() {") : panel.index("  function draw() {")]
    assert "paintOrcaMarks(parts.top, ctx, ctx.data)" in refresh and "openButton.update({" in refresh
