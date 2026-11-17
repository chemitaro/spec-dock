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
    row = f'<span class="sd-card__agents">{slot}</span>'
    assert out["plain"] == out["plainOpts"]
    assert "sd-card__meta" not in out["plain"] and "sd-orca" not in out["plain"]
    # iss-00621 T-05: the agents sit on a row of their own below the other marks, never inside them
    assert "sd-card__meta" not in out["orca"] and out["orca"].count(row) == 1
    assert out["orcaMarks"].count("sd-card__meta") == 1
    meta = out["orcaMarks"][out["orcaMarks"].index('<span class="sd-card__meta">') :]
    meta = meta[: meta.index(row)]
    assert "sd-orca" not in meta and meta.endswith("</span>")
    assert out["orcaMarks"].count(row) == 1
    assert out["orcaMarks"].replace(row, "") == out["marks"]
    assert out["orca"].replace(row, "") == out["plain"]
    assert "sd-orca" not in out["marks"]


def test_the_card_row_of_agents_hides_without_marks() -> None:  # iss-00621 T-05
    css = (SHARED / "parts.css").read_text()
    assert ".sd-card__agents { display: flex;" in css
    assert ".sd-card__agents:not(:has(.orca-mark)) { display: none; }" in css
    assert ".sd-card__agents > .sd-orca { margin-left: 0; }" in css
    card = _function((SHARED / "parts.js").read_text(), "card")
    assert "meta.push(orcaSlot" not in card
    assert (
        card.index('<span class="sd-card__meta">')
        < card.index('<span class="sd-card__agents">')
        < card.index("parentLine +")
    )


@needs_node
def test_the_graph_slot_has_no_limit(tmp_path: Path) -> None:  # iss-00620 T-07
    out = run_node('out.slot = parts.orcaSlot("iss-00005", "all");', tmp_path)
    assert out["slot"] == '<span class="sd-orca" data-orca-scope="iss-00005" data-orca-max="all"></span>'


AGENTS_ROW = '<div class="gx-agents">${orcaSlot(s.id, "all")}</div>'


def test_graph_boxes_and_frames_put_the_agents_on_a_row_of_their_own() -> None:  # iss-00620 T-06
    source = (VIEWS / "graph.js").read_text()
    draw = (VIEWS / "graph/draw.js").read_text()  # iss-00614: the boxes, frames and legend are drawn there
    box = _function(draw, "boxHtml")
    # the other marks stay on their row, the downstream count with them (R-01); the agents' slot is not among them
    assert box.count('<div class="gx-marks">') == 2
    assert box.count("${M.dnMark(s.downstream)}</div>`") == 2
    assert "。後に続く ${s.downstream}件" in box
    assert "orcaSlot(s.id, 2)" not in box and "orcaSlot(s.id, 3)" not in box
    # the row of agents follows the other marks, in every box
    assert box.count(AGENTS_ROW) == 1
    assert box.index("marks +") < box.index(AGENTS_ROW) < box.index("`</div>`")
    frame = _function(draw, "frameHtml")
    head = frame[frame.index("const head") : frame.index("const meta")]
    # the frame's row of agents is the heading's last child, so that taps, the double click and dimming keep working
    assert head.rstrip().endswith(AGENTS_ROW + "</div>`;")
    assert "orcaSlot(s.id, 3)" not in frame
    meta = frame[frame.index("const meta") :]
    assert "${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`" in meta and "gx-agents" not in meta
    tap = _function(source, "onTap")
    assert 'target.closest(".gx-box, .gx-fh")' in tap
    legend = _function(draw, "renderLegend")
    assert '"後に続く数"' in legend
    marks = (VIEWS / "graph/marks.js").read_text()
    assert "export const dnMark" in marks or "export function dnMark" in marks


def test_the_graph_measures_the_marks_and_lays_out_again_only_when_the_rows_change() -> None:  # iss-00620 T-06
    graph = (VIEWS / "graph.js").read_text()
    assert 'import { DEFAULTS, index, nodeMarkRows, routeLayout } from "./graph/layout.js";' in graph
    paint = _function(graph, "paintOrca")
    assert paint.index("paintOrcaMarks(V.el.world, V.ctx, V.data)") < paint.index("checkRows()")
    build = _function(graph, "buildWorld")
    assert "marks: V.marks" in build
    assert 'querySelectorAll(".sd-orca")' in build and "V.ro.observe(" in build
    assert "V.ro?.disconnect()" in _function(graph, "dispose")
    assert "new ResizeObserver(" in graph
    resized = _function(graph, "onMarksResize")
    assert "requestAnimationFrame(" in resized and "checkRows()" in resized and "rowsRedo" not in resized
    check = _function(graph, "checkRows")
    assert "measureMarks(V.el.world)" in check
    # iss-00627: the compact frames are measured with the marks; nothing measurable lays out nothing again
    assert "if (!M && !H) return;" in check
    assert "nodeMarkRows(n, M[n.id])" in check and "(n.rows ?? 1)" in check
    assert "if (M) V.marks = M;" in check
    # a different count lays out again (twice at most per news or render), keeping the zoom and the position
    assert check.index("V.rowsRedo >= 2") < check.index("render(V.root, V.ctx)")
    assert "V.sig = null;" in check and "V.fitted" not in check
    assert "V.rowsRedo++" in check
    # only a render that checkRows did not call and the reader's news start the count again
    render = _function(graph, "render")
    assert "if (!V.fromRows) V.rowsRedo = 0;" in render
    assert "createOrcaWatch(onOrcaNews)" in graph
    news = _function(graph, "onOrcaNews")
    assert "V.rowsRedo = 0;" in news and "paintOrca()" in news
    measure = _function(graph, "measureMarks")
    for marker in (
        'querySelectorAll("[data-orca-scope]")',
        '.querySelectorAll(".orca-mark")',
        "getBoundingClientRect().width / V.s",
        "Math.ceil(",
        "columnGap",
        'flexWrap !== "wrap"',
        "return null;",
    ):
        assert marker in measure, marker
    audit = _function(graph, "edgeAudit")
    assert "markOverflow" in audit


def test_the_graph_css_wraps_the_row_of_agents() -> None:  # iss-00620 T-06, R-07
    css = (VIEWS / "graph.css").read_text()
    for rule in (
        ".gx .gx-agents { display: flex; margin-top: 4px; }",
        ".gx .gx-agents:not(:has(.orca-mark)) { display: none; }",
        ".gx .gx-agents > .sd-orca { flex: 1 1 100%; margin-left: 0; min-width: 0; }",
        ".gx .sd-orca .orca-marks { row-gap: 4px; }",
        ".gx .gx-fh:has(> .gx-agents .orca-mark) { flex-wrap: wrap; row-gap: 0; }",
        ".gx .gx-fh > .gx-agents { flex: 1 1 100%; }",
    ):
        assert rule in css, rule
    added = [line for line in css.splitlines() if "gx-agents" in line or ".orca-marks" in line]
    assert added and not [line for line in added if re.search(r"#[0-9a-fA-F]{3}|rgb|hsl|var\(", line)]
    layout = (VIEWS / "graph/layout.js").read_text()
    assert "export const MARK_ROW = 20;" in layout and "export const MARK_INSET = { box: 26 };" in layout


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


def test_pressing_a_mark_opens_the_agents_tab_on_its_agent() -> None:  # iss-00621 T-06
    graph = (VIEWS / "graph.js").read_text()
    # A box's or a frame heading's mark is pressed through the graph's taps.
    tap = _function(graph, "onTap")
    assert 'const slot = target.closest(".sd-orca");' in tap
    assert "V.pn?.openAgent(markAgentAt(slot, target));" in tap
    assert tap.index("select(id)") < tap.index("openAgent")
    allgraph = _function((VIEWS / "allgraph.js").read_text(), "onTap")
    assert 'const slot = target.closest(".sd-orca");' in allgraph
    assert "if (!same) select(hit.repo, hit.id);\n    A.pn?.openAgent(markAgentAt(slot, target));" in allgraph
    board = _function((VIEWS / "board.js").read_text(), "onCardClick")
    assert 'const slot = event.target.closest(".sd-orca");' in board
    assert "if (slot) B.pn?.openAgent(markAgentAt(slot, event.target));" in board
    assert board.index("plainClick(event)") < board.index("select(anchor.dataset.id)") < board.index("openAgent")
    panel = (SHARED / "panel.js").read_text()
    click = panel[panel.index('aside.addEventListener("click"') : panel.index("  // Choose a tab as if")]
    assert 'const slot = t.closest(".sd-orca");' in click
    assert "openAgent(markAgentAt(slot, t));" in click
    for source in (tap, allgraph, board, click):
        assert 'preferTab("agents")' not in source
    for name in ("graph.js", "allgraph.js", "board.js"):
        assert (
            "markAgentAt" in (VIEWS / name).read_text().split("\n\n")[0]
            or "markAgentAt, paintOrcaMarks" in (VIEWS / name).read_text()
        )
    assert "markAgentAt" in panel[: panel.index("export function createScopePanel")]


def test_a_mark_on_a_selected_box_opens_the_agents_tab_on_a_phone_too() -> None:  # iss-00602 T-01, iss-00621 T-06
    for name, select, call in (
        ("graph.js", "if (V.sel !== id) select(id);", "V.pn?.openAgent(markAgentAt(slot, target));"),
        ("allgraph.js", "if (!same) select(hit.repo, hit.id);", "A.pn?.openAgent(markAgentAt(slot, target));"),
    ):
        tap = _function((VIEWS / name).read_text(), "onTap")
        mark = tap.index("if (slot) {")
        second = tap.index("if (isPhone() && ")
        assert mark < second  # the mark is read before a phone's second tap opens the detail screen
        branch = tap[mark : tap.index("\n  }\n", mark)]
        assert select in branch
        assert branch.index(select) < branch.index(call)
        assert branch.rstrip().endswith("return;")
        assert tap[second:].index("goDetail(") < tap[second:].index("return;")


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
    # iss-00620: the graph only hides an empty row of agents and sets the gap between the rows of marks (R-07)
    allowed = {
        VIEWS / "graph.css": (
            ".gx .gx-agents:not(:has(.orca-mark)) { display: none; }",
            ".gx .sd-orca .orca-marks { row-gap: 4px; }",
            ".gx .gx-fh:has(> .gx-agents .orca-mark) { flex-wrap: wrap; row-gap: 0; }",
        ),
        SHARED / "parts.css": (".sd-card__agents:not(:has(.orca-mark)) { display: none; }",),  # iss-00621 D-05
    }
    for path in [*DASHBOARD.glob("*.css"), *VIEWS.glob("*.css"), *SHARED.glob("*.css")]:
        text = path.read_text()
        for rule in allowed.get(path, ()):
            assert rule in text, rule
            text = text.replace(rule, "")
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
    assert "if (slot) {" in click and "openAgent(markAgentAt(slot, t));" in click  # iss-00621 D-03


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


# --- iss-00621 T-03: the panel opens the agents' tab on the pressed agent ------------------------------------


@needs_node
def test_open_agent_chooses_the_agent_and_null_only_prefers_the_tab(tmp_path: Path) -> None:
    out = run_panel(
        """
        const selected = () => (part(".pn-tabs").innerHTML.match(/data-pn-tab="([a-z]+)" aria-selected="true"/) || [])[1] ?? null;
        const frameIds = () => [...part(".pn-body").innerHTML.matchAll(/<iframe class="sd-agent" src="[^"]*\\/embed\\/agent\\?id=([^"&]*)/g)].map((m) => decodeURIComponent(m[1]));
        const raw = (id) => ({id, mark: "working", agentType: "claude", detail: "/embed/agent?id=" + encodeURIComponent(id)});
        const one = {id: "iss-00011", number: 11, kind: "issue", state: "doing", title: "one", path: "/r/x/scopes/iss-00011", children: []};
        const two = {id: "iss-00012", number: 12, kind: "issue", state: "doing", title: "two", path: "/r/x/scopes/iss-00012", children: []};
        const records = [{path: "/w/w1", branch: "b1"}];
        const data = {worktrees: {status: "ok", paths: []}, scopes: [{...one, worktrees: records}, {...two, worktrees: records}]};
        const byIds = new Map(data.scopes.map((item) => [item.id, item]));
        const trees = {[one.id]: [{id: "w1", path: "/w/w1", branch: "b1", agents: [raw("a"), raw("b"), raw("c")]}],
          [two.id]: [{id: "w2", path: "/w/w2", branch: "b2", agents: [raw("x"), raw("y")]}]};
        const orca = {status: () => "ok", origin: "http://192.0.2.1:8791", marks: () => null, subscribe: () => () => {},
          forScope: (_, id) => trees[id] ?? []};
        const at = (s) => ({ctx: {href: (p) => p, data, orca, embed: false, route: {path: "/r/x/graph", params: new URLSearchParams()}},
          scope: s, doc: {scope: s, details: {catalog: "ok", documents: [], adrs: [], artifacts: []}}, docState: "ok", byId: byIds});
        El.prototype.querySelector = () => null; // the agents' strip paints into nothing here
        out.has = typeof pn.openAgent === "function";
        pn.show(at(one));
        // The person chose "a" in the strip, then looked at the summary.
        aside.click({target: {closest: (sel) => (sel === "a[data-pn-param]" ? {dataset: {pnParam: "agent", pnValue: "a"}} : null)}, button: 0, preventDefault() {}});
        pn.preferTab("agents");
        out.before = frameIds();
        pn.preferTab("summary");
        out.summary = selected();
        pn.openAgent("b");
        out.tab = selected();
        out.chosen = frameIds();
        // null keeps the choice, like preferTab("agents").
        pn.preferTab("summary");
        pn.openAgent(null);
        out.nullTab = selected();
        out.nullFrame = frameIds();
        pn.openAgent("");
        out.emptyFrame = frameIds();
        // Called after show() changes the Scope, the choice stays.
        pn.show(at(two));
        pn.openAgent("y");
        out.otherScope = [selected(), frameIds()];
        pn.show(at(two));
        out.again = frameIds();
        """,
        tmp_path,
    )
    assert out["has"] is True
    assert out["before"] == ["a"]
    assert out["summary"] == "summary"
    assert out["tab"] == "agents" and out["chosen"] == ["b"]
    assert out["nullTab"] == "agents" and out["nullFrame"] == ["b"]
    assert out["emptyFrame"] == ["b"]
    assert out["otherScope"] == ["agents", ["y"]]
    assert out["again"] == ["y"]


# --- iss-00621 T-04: the worktree mark on a working Epic's or Initiative's frame ----------------------------


@needs_node
def test_working_frames_show_the_worktree_mark(tmp_path: Path) -> None:
    out = run_node(
        f"const draw = await import({json.dumps((VIEWS / 'graph/draw.js').as_uri())});\n"
        + """
        const epic = {id: "epic-01234", number: 1234, kind: "epic", state: "doing", title: "E", branch: "worktree/epic-01234", parent_id: null, children: []};
        const ini = {...epic, id: "init-01235", number: 1235, kind: "initiative", branch: "worktree/init-01235"};
        const data = {scopes: [epic, ini]};
        const byId = new Map(data.scopes.map((s) => [s.id, s]));
        const V = {data, ix: {byId, kids: new Map()}, desc: () => [], cleanup: new Map(), range: "all"};
        const n = {type: "frame", x1: 0, y1: 0, x2: 300, y2: 200};
        const t = {type: "tframe", x1: 0, y1: 0, x2: 200, y2: 80};
        const html = (s) => ({frame: draw.frameHtml(V, s, n), box: draw.boxHtml(V, s, t)});
        out.epic = html(epic);
        out.ini = html(ini);
        out.ready = html({...epic, state: "ready"});
        out.readyBare = html({...epic, state: "ready", branch: null});
        out.noBranch = html({...epic, branch: null});
        """,
        tmp_path,
    )
    for key, branch in (("epic", "worktree/epic-01234"), ("ini", "worktree/init-01235")):
        frame, box = out[key]["frame"], out[key]["box"]
        wt = f'<span class="wt" title="worktree：{branch}" role="img" aria-label="worktree {branch}">'
        head = frame[frame.index('<div class="gx-fh"') : frame.index('<div class="gx-fm">')]
        assert head.count(wt) == 1 and frame.count(wt) == 1
        # after the title, outside the row of agents
        assert head.index('class="gx-fttl"') < head.index(wt) < head.index('<div class="gx-agents">')
        marks = box[box.index('<div class="gx-marks">') : box.index('<div class="gx-agents">')]
        assert marks.count(wt) == 1 and box.count(wt) == 1
    # the heading's label stays
    assert 'aria-label="epic-01234 E。作業中"' in out["epic"]["frame"]
    # not working, or no branch: the same HTML as before (no mark)
    assert out["ready"] == out["readyBare"]
    for key in ("ready", "noBranch"):
        assert 'class="wt"' not in out[key]["frame"] and 'class="wt"' not in out[key]["box"]
    assert out["noBranch"]["frame"] == re.sub(r'<span class="wt" [^>]*>.*?</span>', "", out["epic"]["frame"], count=1)
    assert out["noBranch"]["box"] == re.sub(r'<span class="wt" [^>]*>.*?</span>', "", out["epic"]["box"], count=1)


def test_the_frame_heading_keeps_the_worktree_mark_on_the_title_row() -> None:  # iss-00621 T-04
    frame = _function((VIEWS / "graph/draw.js").read_text(), "frameHtml")
    head = frame[frame.index("const head") : frame.index("const meta")]
    assert '</span>${M.wtMark(s.state === "doing" ? s.branch : null)}<div class="gx-agents">' in head
    box = _function((VIEWS / "graph/draw.js").read_text(), "boxHtml")
    assert box.count('${M.wtMark(s.state === "doing" ? s.branch : null)}') == 2
    assert ".gx .gx-fh > .wt { flex: none; }" in (VIEWS / "graph.css").read_text()
    # the title grows only to its own width, so the mark follows it instead of the heading's right end (T-04)
    css = (VIEWS / "graph.css").read_text()
    own = ".gx :is(.gx-ini, .gx-epic) > .gx-fh > .gx-fttl { max-width: max-content; }"
    layout = ".gx .gx-ini > .gx-fh .gx-fttl, .gx .gx-epic > .gx-fh .gx-fttl { max-width: none; }"
    assert own in css and layout in css
    assert css.index(layout) < css.index(own)
