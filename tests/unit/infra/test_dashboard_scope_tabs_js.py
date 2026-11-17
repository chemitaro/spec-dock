"""The shared Scope tabs under node (iss-00587 T-04, T-05)."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

VIEWS = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "dashboard" / "views"
SHARED = VIEWS / "_shared"
NODE = shutil.which("node")
node = pytest.mark.skipif(NODE is None, reason="node is not installed")

# iss-00593 D-02: the agents tab is second (it shows only when visible(env) says so)
TAB_KEYS = ["explanation", "agents", "summary", "deps", "children", "docs", "artifacts", "todos"]
TAB_LABELS = ["説明資料", "エージェント", "概要", "依存", "配下", "文書", "Artifact", "人のタスク"]
MOVED = (
    "summaryTab",
    "depsTab",
    "childrenTab",
    "docsTab",
    "artifactsTab",
    "todosTab",
    "catalogProblem",
    "documentEntries",
)


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        f"const tabs = await import({json.dumps((SHARED / 'scope_tabs.js').as_uri())});\n"
        "const out = {};\n" + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=60)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


FIXTURE = """
const href = "/r/github.com/o/r/files/epic-00001/explanation.html?a=1&b=<x>";
const details = (explanation, catalog = "ok") => ({catalog, documents: explanation ? [explanation] : [], adrs: [], artifacts: []});
const scope = {id: "epic-00001", number: 1, kind: "epic", state: "ready", title: "T", path: "/r/github.com/o/r/scopes/epic-00001", children: []};
const ctx = {
  data: {scopes: [scope]},
  repository: "github.com/o/r",
  route: {path: "/r/github.com/o/r/scopes/epic-00001?tab=children&embed=1", params: new URLSearchParams("tab=children&embed=1")},
  embed: true,
  href: (path) => path.includes("embed=1") ? path : path + (path.includes("?") ? "&" : "?") + "embed=1",
};
const byId = new Map([[scope.id, scope]]);
const explanationTab = tabs.SCOPE_TABS.find((tab) => tab.key === "explanation");
const draw = (expl, catalog) => explanationTab.render(tabs.pageEnv(ctx, scope, {scope, details: details(expl, catalog)}, byId));
"""


@node
def test_the_tab_list_starts_with_the_explanation(tmp_path: Path) -> None:
    out = _run(
        "out.keys = tabs.SCOPE_TABS.map((tab) => tab.key); out.labels = tabs.SCOPE_TABS.map((tab) => tab.label);",
        tmp_path,
    )
    assert out["keys"] == TAB_KEYS
    assert out["labels"] == TAB_LABELS


@node
def test_the_explanation_tab_frames_a_written_document(tmp_path: Path) -> None:
    out = _run(
        FIXTURE
        + """
        out.written = draw({key: "explanation", name: "explanation.html", exists: true, href, skeleton: false});
        out.unknown = draw({key: "explanation", name: "explanation.html", exists: true, href, skeleton: null});
        out.count = explanationTab.count(tabs.pageEnv(ctx, scope, {scope, details: details(null)}, byId));
        const openOf = (expl, catalog) => explanationTab.open(tabs.pageEnv(ctx, scope, {scope, details: details(expl, catalog)}, byId));
        out.open = openOf({key: "explanation", name: "explanation.html", exists: true, href, skeleton: false});
        out.notOpen = [
          openOf({key: "explanation", name: "explanation.html", exists: true, href, skeleton: true}),
          openOf({key: "explanation", name: "explanation.html", exists: false, href: null, skeleton: null}),
          openOf(null), openOf(null, "scope_missing"),
          openOf({key: "explanation", name: "explanation.html", exists: true, href: null, skeleton: false}),
        ];
        """,
        tmp_path,
    )
    written = out["written"]
    frames = re.findall(r"<iframe [^>]*>", written)
    assert len(frames) == 1
    frame = frames[0]
    assert 'class="sd-explain"' in frame
    assert 'src="/r/github.com/o/r/files/epic-00001/explanation.html?a=1&amp;b=&lt;x&gt;"' in frame
    assert 'sandbox="allow-scripts allow-popups"' in frame and "allow-same-origin" not in written
    assert 'referrerpolicy="no-referrer"' in frame and 'title="説明資料：epic-00001"' in frame
    # iss-00656 R-05: only the frame; its new-tab link is the tab's open(env) in the tab row
    assert written.startswith('<div class="sd-framebox" data-frame="explanation"><iframe class="sd-explain"')
    assert "<a " not in written and "sd-framebar" not in written and "新しいタブで開く" not in written
    assert out["open"] == {"href": "/r/github.com/o/r/files/epic-00001/explanation.html?a=1&b=<x>", "label": "説明資料"}
    assert out["notOpen"] == [None] * 5
    assert re.findall(r"<iframe [^>]*>", out["unknown"]) == frames  # F-03: unknown is shown as written
    assert out["count"] is None


@node
def test_the_explanation_tab_tells_skeleton_missing_and_unreadable(tmp_path: Path) -> None:
    out = _run(
        FIXTURE
        + """
        out.skeleton = draw({key: "explanation", name: "explanation.html", exists: true, href, skeleton: true});
        out.missing = draw({key: "explanation", name: "explanation.html", exists: false, href: null, skeleton: null});
        out.absent = draw(null);
        out.unreadable = draw(null, "scope_missing");
        """,
        tmp_path,
    )
    assert "<iframe" not in out["skeleton"] and 'data-code="explanation-skeleton"' in out["skeleton"]
    assert "説明資料は雛形のまま（まだ書かれていない）" in out["skeleton"]
    assert "spec-dock/docs/authoring/explanation.md" in out["skeleton"]
    assert re.search(r'<a [^>]*href="[^"]*explanation\.html[^"]*" target="_blank" rel="noopener"', out["skeleton"])
    for key in ("missing", "absent"):
        assert "<iframe" not in out[key] and 'data-code="explanation-missing"' in out[key], key
        assert "説明資料はまだない" in out[key] and "spec-dock/docs/authoring/explanation.md" in out[key], key
    assert 'data-code="catalog-scope_missing"' in out["unreadable"] and "<iframe" not in out["unreadable"]


@node
def test_page_and_panel_envs_link_tab_choices_differently(tmp_path: Path) -> None:
    out = _run(
        FIXTURE
        + """
        const page = tabs.pageEnv(ctx, scope, {scope, details: details(null)}, byId);
        out.pageOn = page.paramLink("done", true);
        out.pageOff = page.paramLink("done", false);
        out.pageParam = page.param("tab");
        const params = new Map([["done", "1"]]);
        const panel = tabs.panelEnv(ctx, scope, {scope, details: details(null)}, byId, {params, tab: "children"});
        out.panelOn = panel.paramLink("doc", "plan");
        out.panelOff = panel.paramLink("done", false);
        out.panelParam = panel.param("done");
        out.panelMissing = panel.param("doc");
        out.modes = [page.mode, panel.mode];
        """,
        tmp_path,
    )
    assert out["pageOn"] == 'data-nav href="/r/github.com/o/r/scopes/epic-00001?tab=children&amp;embed=1&amp;done=1"'
    assert out["pageOff"] == 'data-nav href="/r/github.com/o/r/scopes/epic-00001?tab=children&amp;embed=1"'
    assert out["pageParam"] == "children"
    on = out["panelOn"]
    assert "data-nav" not in on
    assert 'data-pn-param="doc"' in on and 'data-pn-value="plan"' in on
    href = re.search(r'href="([^"]*)"', on)
    assert href is not None
    assert href.group(1).startswith("/r/github.com/o/r/scopes/epic-00001?")
    query = href.group(1).split("?", 1)[1].replace("&amp;", "&").split("&")
    assert sorted(query) == ["doc=plan", "done=1", "tab=children"]  # a new tab is an ordinary page
    assert 'data-pn-param="done"' in out["panelOff"] and 'data-pn-value=""' in out["panelOff"]
    assert out["panelParam"] == "1" and out["panelMissing"] is None
    assert out["modes"] == ["page", "panel"]


def test_the_detail_screen_draws_its_tabs_from_the_shared_list() -> None:
    scope = (VIEWS / "scope.js").read_text()
    shared = (SHARED / "scope_tabs.js").read_text()
    assert 'from "./_shared/scope_tabs.js"' in scope
    assert "visibleTabs(env)" in scope and "pickTab(" in scope  # iss-00593: the visible tabs of SCOPE_TABS
    for name in MOVED:
        assert not re.search(rf"function {name}\b", scope), name
        assert re.search(rf"function {name}\b", shared), name
    assert "TABS" not in (SHARED / "logic.js").read_text().replace("SCOPE_TABS", "")


def test_the_panel_draws_its_tabs_from_the_same_list_and_the_graph_uses_it() -> None:
    panel = (SHARED / "panel.js").read_text()
    assert 'from "./scope_tabs.js"' in panel and "visibleTabs(first)" in panel and "pickTab(" in panel
    assert "export function createScopePanel(" in panel
    graph = (VIEWS / "graph.js").read_text()
    assert 'import { createScopePanel, SHEET_GRAB } from "./_shared/panel.js";' in graph
    assert "V.pn.show(" in graph and "V.pn.hide()" in graph
    assert '"/assets/views/_shared/panel.css"' in graph and '"/assets/views/_shared/scope_tabs.css"' in graph
    assert ".gx .panel" not in (VIEWS / "graph.css").read_text()  # the panel's look moved to panel.css


def test_the_board_opens_the_same_panel_only_on_a_plain_click() -> None:
    board = (VIEWS / "board.js").read_text()
    assert 'import { createScopePanel } from "./_shared/panel.js";' in board
    assert "B.pn.show(" in board and "B.pn.hide()" in board
    # a modified or middle click keeps the card's ordinary link to the detail screen (R-01)
    assert "event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey" in board
    assert 'event.target.closest("a.sd-card[data-id]")' in board and "event.preventDefault();" in board
    assert '"/assets/views/_shared/panel.css"' in board and '"/assets/views/_shared/scope_tabs.css"' in board
    css = (VIEWS / "board.css").read_text()
    assert '[data-view="board"][data-panel="open"] .sd-page' in css and "var(--pn-w)" in css


def test_the_panels_read_against_the_page_baseline_and_keep_the_structure_first() -> None:
    assert "baseline: state.baseline," in (VIEWS.parent / "app.js").read_text()
    assert "api.scope(V.ctx.repository, id, V.ctx.baseline)" in (VIEWS / "graph.js").read_text()
    assert "api.scope(B.ctx.repository, id, B.ctx.baseline)" in (VIEWS / "board.js").read_text()
    assert "{ ...state.doc.scope, ...state.scope }" in (SHARED / "panel.js").read_text()


def test_the_phone_sheet_moves_only_by_the_grab_and_the_header_band() -> None:
    panel = (SHARED / "panel.js").read_text()
    for name in ("sheetHeights(innerHeight)", "settleSheet({", "nextOnTap(snap)", "setPointerCapture"):
        assert name in panel, name
    assert '<button type="button" class="pn-grab" aria-label="欄の高さを変える">' in panel
    css = (SHARED / "panel.css").read_text()
    phone = css[css.index("@container app (max-width: 640px)") :]
    touch = [line.split("{")[0].strip() for line in phone.splitlines() if "touch-action: none" in line]
    # the contents and the frame scroll freely (R-07); another drawing's heading moves the sheet too (iss-00650 D-03)
    assert touch == [".sd-pn .pn-grab", ".sd-pn .pn-top, .sd-pn > .pn-head"]
    # the full sheet folds only the Scope's heading into its top row; another drawing's heading keeps its box, so its
    # touch-action holds the finger (iss-00650 D-03)
    assert '.sd-pn[data-snap="full"] .pn-top > .pn-head { display: contents; }' in phone
    assert '.sd-pn[data-snap="full"] .pn-head {' not in phone
    assert "height: var(--pn-h" in phone and ".sd-pn.is-dragging iframe { pointer-events: none; }" in phone
    assert "overscroll-behavior: contain" in css


# --- The docs tab and the explanation tab as one bar and a frame (iss-00589 T-01〜T-03) ----------------------

DOCS = (
    FIXTURE
    + """
const base = "/r/github.com/o/r/scopes/epic-00001/doc";
const files = "/r/github.com/o/r/files/epic-00001";
const cue = (name) => ({key: name.split(".")[0], name, exists: true, href: `${files}/${name}`, view: base});
const cueDetails = ({report = true, check = {status: "ok", complete: true, errors: [], warnings: [], next_steps: []}} = {}) => ({
  catalog: "ok",
  spec: base,
  documents: [
    cue("requirement.cue"), cue("design.cue"), cue("plan.cue"),
    {key: "explanation", name: "explanation.html", exists: true, href: `${files}/explanation.html`, view: null},
    {key: "report", name: "report.md", exists: report, href: report ? `${files}/report.md` : null, view: report ? `${base}/report.md` : null},
  ],
  adrs: [{name: "20260101t000000z-adr-keep-it.md", path: "artifacts/20260101t000000z-adr-keep-it.md", view: `${base}/artifacts/20260101t000000z-adr-keep-it.md`}],
  artifacts: [],
  check,
  progress: {total: 2, done: 1, doing: 1, todo: 0, dropped: 0, doing_steps: [{id: "S-02", title: "上書きを止める"}]},
});
const mdDetails = () => ({
  catalog: "ok",
  spec: null,
  documents: ["requirement", "design", "plan", "report"].map((key) => ({key, name: `${key}.md`, exists: true, href: `${files}/${key}.md`, view: `${base}/${key}.md`}))
    .concat([{key: "explanation", name: "explanation.html", exists: false, href: null, view: null}]),
  adrs: [],
  artifacts: [],
  check: null,
  progress: null,
});
const docsTab = tabs.SCOPE_TABS.find((tab) => tab.key === "docs");
const pageAt = (query) => ({...ctx, route: {path: `/r/github.com/o/r/scopes/epic-00001?${query}`, params: new URLSearchParams(query)}});
const docsPage = (details, query = "tab=docs") => docsTab.render(tabs.pageEnv(pageAt(query), scope, {scope, details}, byId));
const docsPanel = (details, params = new Map()) => docsTab.render(tabs.panelEnv(ctx, scope, {scope, details}, byId, {params, tab: "docs"}));
const segOf = (html) => {
  const nav = html.match(/<nav class="sd-seg"[^>]*>(.*?)<\\/nav>/s);
  if (!nav) return null;
  return [...nav[1].matchAll(/<(a|span) ([^>]*)>(.*?)<\\/\\1>/gs)].map((m) => ({tag: m[1], attrs: m[2], text: m[3].replace(/<[^>]*>/g, "")}));
};
const openOf = (html) => (html.match(/<a class="sd-framebar__open"[^>]*>/) || [null])[0];
const docsOpenPage = (details, query = "tab=docs") => docsTab.open(tabs.pageEnv(pageAt(query), scope, {scope, details}, byId));
const docsOpenPanel = (details, params = new Map()) => docsTab.open(tabs.panelEnv(ctx, scope, {scope, details}, byId, {params, tab: "docs"}));
const frameOf = (html) => (html.match(/<iframe [^>]*>/) || [null])[0];
"""
)


@node
def test_a_cue_scope_offers_the_spec_and_the_report_in_one_bar(tmp_path: Path) -> None:
    out = _run(
        DOCS
        + """
        const html = docsPage(cueDetails());
        out.html = html; out.seg = segOf(html); out.open = openOf(html); out.frame = frameOf(html);
        out.tabOpen = docsOpenPage(cueDetails());
        const missing = docsPage(cueDetails({report: false}));
        out.missingSeg = segOf(missing);
        const report = docsPage(cueDetails(), "tab=docs&doc=report");
        out.reportSeg = segOf(report); out.reportOpen = openOf(report); out.reportFrame = frameOf(report);
        out.reportTabOpen = docsOpenPage(cueDetails(), "tab=docs&doc=report");
        out.compat = segOf(docsPage(cueDetails(), "tab=docs&doc=explanation"));
        """,
        tmp_path,
    )
    html = out["html"]
    assert [item["text"] for item in out["seg"]] == ["仕様", "報告", "20260101t000000z-adr-keep-it"]
    assert "説明資料" not in html and not re.search(r'class="sd-doc(?:s|"| |__)', html)
    assert 'data-code="plan-progress"' not in html and 'data-code="check-' not in html  # R-03
    assert html.startswith('<div class="sd-framebox" data-frame="docs"><div class="sd-framebar">')
    spec, report, adr = out["seg"]
    assert (
        spec["tag"] == "a"
        and 'aria-current="true"' in spec["attrs"]
        and 'title="requirement.cue・design.cue・plan.cue"' in spec["attrs"]
    )
    assert 'href="/r/github.com/o/r/scopes/epic-00001?tab=docs&amp;embed=1"' in spec["attrs"]  # no wanted: null
    assert report["tag"] == "a" and "aria-current" not in report["attrs"] and 'title="report.md"' in report["attrs"]
    assert "doc=report" in report["attrs"] and "data-nav" in report["attrs"]
    assert adr["tag"] == "a" and ("doc=adr%3Aartifacts" in adr["attrs"] or "doc=adr:artifacts" in adr["attrs"])
    # iss-00656 R-05: the bar keeps the choice only; the new-tab link is the tab's open(env) in the tab row
    assert out["open"] is None and "新しいタブで開く" not in html
    assert out["tabOpen"] == {"href": "/r/github.com/o/r/scopes/epic-00001/doc", "label": "仕様"}
    frame = out["frame"]
    assert 'class="sd-docframe"' in frame and 'src="/r/github.com/o/r/scopes/epic-00001/doc"' in frame
    assert (
        'sandbox="allow-scripts allow-popups"' in frame
        and 'referrerpolicy="no-referrer"' in frame
        and 'loading="lazy"' in frame
    )
    gone = out["missingSeg"][1]
    assert (
        gone["tag"] == "span"
        and 'aria-disabled="true"' in gone["attrs"]
        and "まだない" in gone["attrs"]
        and gone["text"] == "報告"
    )
    assert 'aria-current="true"' in out["reportSeg"][1]["attrs"] and "aria-current" not in out["reportSeg"][0]["attrs"]
    assert "doc=spec" in out["reportSeg"][0]["attrs"]
    assert out["reportOpen"] is None
    assert out["reportTabOpen"] == {"href": "/r/github.com/o/r/scopes/epic-00001/doc/report.md", "label": "報告"}
    assert 'src="/r/github.com/o/r/scopes/epic-00001/doc/report.md"' in out["reportFrame"]
    assert 'aria-current="true"' in out["compat"][0]["attrs"]  # ?doc=explanation shows the spec


@node
def test_the_panel_switches_documents_inside_itself(tmp_path: Path) -> None:
    out = _run(
        DOCS
        + """
        out.seg = segOf(docsPanel(cueDetails()));
        const report = docsPanel(cueDetails(), new Map([["doc", "report"]]));
        out.reportSeg = segOf(report); out.reportOpen = docsOpenPanel(cueDetails(), new Map([["doc", "report"]])); out.reportFrame = frameOf(report);
        """,
        tmp_path,
    )
    for item in out["seg"]:
        assert 'data-pn-param="doc"' in item["attrs"] and "data-nav" not in item["attrs"], item
    assert 'data-pn-value=""' in out["seg"][0]["attrs"] and 'data-pn-value="report"' in out["seg"][1]["attrs"]
    assert 'aria-current="true"' in out["reportSeg"][1]["attrs"]
    assert out["reportOpen"] == {"href": "/r/github.com/o/r/scopes/epic-00001/doc/report.md", "label": "報告"}
    assert 'src="/r/github.com/o/r/scopes/epic-00001/doc/report.md"' in out["reportFrame"]


@node
def test_the_check_band_shows_only_errors_and_failures_keep_their_notice(tmp_path: Path) -> None:
    out = _run(
        DOCS
        + """
        const finding = (code, message) => ({code, message, file: "epic-00001/plan.cue"});
        out.warnOnly = docsPage(cueDetails({check: {status: "ok", complete: true, errors: [], warnings: [finding("W1", "w")], next_steps: []}}));
        out.invalid = docsPage(cueDetails({check: {status: "invalid", complete: false, errors: [finding("E1", "<b>bad</b>"), finding("E2", "also")], warnings: [finding("W1", "w")], next_steps: ["spec-dock scope check epic-00001"]}}));
        out.failed = docsPage(cueDetails({check: {status: "failed", code: "CUE_NOT_FOUND", message: "no cue", next_steps: ["spec-dock scope check epic-00001"]}}));
        out.failedReport = docsPage(cueDetails({check: {status: "failed", code: "CUE_NOT_FOUND", message: "no cue", next_steps: []}}), "tab=docs&doc=report");
        out.md = docsPage(mdDetails());
        out.mdSeg = segOf(out.md);
        out.catalog = docsPage({catalog: "scope_missing", next_steps: []});
        out.empty = docsPage({catalog: "ok", spec: null, documents: [{key: "explanation", name: "explanation.html", exists: false, href: null, view: null}], adrs: [], artifacts: [], check: null, progress: null});
        """,
        tmp_path,
    )
    assert "check-" not in out["warnOnly"] and "sd-checkbar" not in out["warnOnly"]
    invalid = out["invalid"]
    band = re.search(
        r'<details class="sd-checkbar" data-code="check-invalid"><summary>(.*?)</summary>(.*?)</details>', invalid, re.S
    )
    assert band is not None
    assert (
        "検査の誤り 2件" in band.group(1)
        and "警告 1件" in band.group(1)
        and "<code>spec-dock scope check epic-00001</code>" in band.group(1)
    )
    assert band.group(2).startswith('<ul class="sd-list sd-findings">') and band.group(2).count("<li>") == 3
    assert "&lt;b&gt;bad&lt;/b&gt;" in invalid and "<b>bad</b>" not in invalid
    assert invalid.index("sd-checkbar") < invalid.index('class="sd-framebar"')  # above the bar
    assert 'data-code="render-failed"' in out["failed"] and "<iframe" not in out["failed"]  # F-01
    assert 'class="sd-framebar"' in out["failed"]  # the report stays one click away
    assert 'src="/r/github.com/o/r/scopes/epic-00001/doc/report.md"' in out["failedReport"]
    assert [item["text"] for item in out["mdSeg"]] == ["要件", "設計", "計画", "報告"]
    assert "説明資料" not in out["md"] and 'aria-current="true"' in out["mdSeg"][0]["attrs"]
    assert 'src="/r/github.com/o/r/scopes/epic-00001/doc/requirement.md"' in out["md"]
    assert 'data-code="catalog-scope_missing"' in out["catalog"] and "<iframe" not in out["catalog"]
    assert "画面の中で読める文書はまだない。" in out["empty"] and "<iframe" not in out["empty"]


@node
def test_the_explanation_tab_uses_the_same_bar_and_redraws_to_the_same_string(tmp_path: Path) -> None:
    out = _run(
        DOCS
        + """
        const expl = {key: "explanation", name: "explanation.html", exists: true, href, skeleton: false};
        out.written = draw(expl);
        out.same = draw(expl) === out.written;
        out.docsSame = docsPage(cueDetails(), "tab=docs&doc=report") === docsPage(cueDetails(), "tab=docs&doc=report");
        out.panelSame = docsPanel(cueDetails()) === docsPanel(cueDetails());
        """,
        tmp_path,
    )
    written = out["written"]
    # iss-00656 R-05: no bar over the explanation, the frame comes first
    assert written.startswith('<div class="sd-framebox" data-frame="explanation"><iframe class="sd-explain"')
    assert "sd-framebar" not in written and "sd-explainbox" not in written and "sd-explain__bar" not in written
    assert re.search(
        r'<iframe class="sd-explain" src="[^"]*explanation\.html\?a=1&amp;b=&lt;x&gt;" sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer"',
        written,
    )
    assert out["same"] and out["docsSame"] and out["panelSame"]  # F-02


def _rules(css: str, selector: str) -> list[str]:
    """The bodies of the rules whose selector is exactly `selector` (whitespace-trimmed)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [m.group(2) for m in re.finditer(r"([^{};]+)\{([^{}]*)\}", css) if m.group(1).strip() == selector]


def test_the_frames_take_the_rest_of_the_height_without_old_rules_or_new_colors() -> None:
    """iss-00589 T-04: one bar over a frame that grows in the panel and fills the screen on the page."""
    shared = (SHARED / "scope_tabs.css").read_text()
    panel = (SHARED / "panel.css").read_text()
    page = (VIEWS / "scope.css").read_text()
    body = _rules(panel, '.sd-pn .pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"])')
    assert body and "display: flex" in body[0] and "flex-direction: column" in body[0]
    assert "overflow" not in body[0]  # stays auto: only a long error list scrolls (R-04)
    assert "flex: 1" in _rules(panel, ".sd-pn .sd-framebox")[0]
    frame = _rules(panel, ".sd-pn :is(.sd-docframe, .sd-explain, .sd-agent)")[0]
    assert "flex: 1" in frame and "min-height: 240px" in frame and "height: auto" in frame
    phone = panel[panel.index("@container app (max-width: 640px)") :]
    assert (
        '.sd-pn .pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"]) { padding: 2px 4px 4px; }'
        in phone
    )
    on_page = _rules(page, "& :is(.sd-docframe, .sd-explain, .sd-agent)")[0]
    assert "flex: none" in on_page and "100dvh" in on_page
    assert (
        "& .sd-framebox" in shared
        and "& .sd-framebar" in shared
        and "& .sd-seg" in shared
        and "& .sd-checkbar" in shared
    )
    assert "height: 24px" in _rules(shared, "& .sd-framebar")[0]
    seg = _rules(shared, "& .sd-seg")[0]
    assert "min-width: 0" in seg and "overflow-x: auto" in seg
    summary = _rules(shared, "& .sd-checkbar > summary")[0]
    assert "height: 28px" in summary and "white-space: nowrap" in summary and "text-overflow: ellipsis" in summary
    for css in (shared, panel, page):
        for gone in (
            ".sd-docs",
            ".sd-doc ",
            ".sd-doc[",
            ".sd-doc__",
            ".sd-docview",
            ".sd-explainbox",
            ".sd-explain__bar",
            "min(70vh",
            "min(78vh",
        ):
            assert gone not in css, gone
        assert not re.search(r"#[0-9a-fA-F]{3}|rgba?\(|hsla?\(", css)  # the design system's tokens only


# --- iss-00656 T-03: the tab row's link, the docs tab's open(env) and the CSS -----------------------------------


@node
def test_the_tab_open_link_is_one_escaped_icon_link(tmp_path: Path) -> None:
    out = _run(
        """
        out.link = tabs.tabOpenLink({href: "/f/x.html?a=1&b=<c>", label: "要件\\"<i>"});
        out.none = [null, undefined, {href: "", label: "要件"}, {label: "要件"}].map(tabs.tabOpenLink);
        out.opens = tabs.SCOPE_TABS.filter((tab) => typeof tab.open === "function").map((tab) => tab.key);
        out.bar = tabs.frameBar("<b>left</b>");
        """,
        tmp_path,
    )
    link = out["link"]
    assert link.startswith(
        '<a class="sd-tabopen" href="/f/x.html?a=1&amp;b=&lt;c&gt;" target="_blank" rel="noopener" '
        'aria-label="要件&quot;&lt;i&gt;を新しいタブで開く" title="要件&quot;&lt;i&gt;を新しいタブで開く">'
    )
    assert link.endswith("</a>") and "<svg" in link
    assert out["none"] == [""] * 4
    assert out["opens"] == ["explanation", "docs"]
    assert out["bar"] == '<div class="sd-framebar"><b>left</b></div>'


@node
def test_the_docs_tab_opens_only_a_framed_document(tmp_path: Path) -> None:
    out = _run(
        DOCS
        + """
        const failed = {status: "failed", code: "CUE_NOT_FOUND", message: "no cue", next_steps: []};
        out.failed = docsOpenPage(cueDetails({check: failed}));
        out.failedReport = docsOpenPage(cueDetails({check: failed}), "tab=docs&doc=report");
        out.md = docsOpenPage(mdDetails());
        out.catalog = docsOpenPage({catalog: "scope_missing", next_steps: []});
        out.none = docsOpenPage(null);
        out.empty = docsOpenPage({catalog: "ok", spec: null, documents: [], adrs: [], artifacts: [], check: null, progress: null});
        out.adr = docsOpenPage(cueDetails(), "tab=docs&doc=" + encodeURIComponent("adr:artifacts/20260101t000000z-adr-keep-it.md"));
        """,
        tmp_path,
    )
    assert out["failed"] is None and out["catalog"] is None and out["none"] is None and out["empty"] is None
    assert out["failedReport"] == {"href": "/r/github.com/o/r/scopes/epic-00001/doc/report.md", "label": "報告"}
    assert out["md"] == {"href": "/r/github.com/o/r/scopes/epic-00001/doc/requirement.md", "label": "要件"}
    assert out["adr"]["label"] == "20260101t000000z-adr-keep-it"


@node
def test_the_detail_screen_puts_the_link_right_after_the_tabs(tmp_path: Path) -> None:
    fake = Path(__file__).resolve().parents[2] / "js" / "fake_dom.mjs"
    out = _run(
        f"const {{Element, install}} = await import({json.dumps(fake.as_uri())});\n"
        f"const screen = (await import({json.dumps((VIEWS / 'scope.js').as_uri())})).default;\n"
        + """
        install();
        const s = {id: "iss-00003", number: 3, kind: "issue", state: "doing", title: "T", path: "/r/x/scopes/iss-00003", children: [], reason: {text: "作業中"}};
        const details = (skeleton) => ({catalog: "ok", spec: null, adrs: [], artifacts: [], check: null, progress: null, documents: [
          {key: "requirement", name: "requirement.md", exists: true, href: "/f/requirement.md", view: "/v/requirement.md"},
          {key: "explanation", name: "explanation.html", exists: true, skeleton, href: "/f/explanation.html"}]});
        const ctxOf = (query, skeleton = false) => ({repository: "github.com/o/r", data: {scopes: [s]}, scope: {scope: s, details: details(skeleton)},
          embed: false, orca: null, href: (p) => p, route: {scope: s.id, path: s.path + "?" + query, params: new URLSearchParams(query)}});
        const root = new Element("div");
        const row = () => {
          const el = root.querySelector(".sd-tabs-row");
          const a = el.querySelectorAll(".sd-tabopen");
          return {order: el.elements.map((c) => c.classes()[0]), href: a.map((x) => x.getAttribute("href")), label: a.map((x) => x.getAttribute("aria-label"))};
        };
        screen.render(root, ctxOf("tab=explanation"));
        out.explanation = row();
        screen.render(root, ctxOf("tab=docs"));
        out.docs = row();
        screen.render(root, ctxOf("tab=summary"));
        out.summary = row();
        screen.render(root, ctxOf("tab=explanation", true));
        out.skeleton = row();
        screen.dispose();
        """,
        tmp_path,
    )
    assert (
        out["explanation"]["order"][:2] == ["sd-tabs", "sd-tabopen"] and out["explanation"]["order"][-1] == "sd-legend"
    )
    assert out["explanation"]["href"] == ["/f/explanation.html"]
    assert out["explanation"]["label"] == ["説明資料を新しいタブで開く"]
    assert out["docs"]["href"] == ["/v/requirement.md"] and out["docs"]["label"] == ["要件を新しいタブで開く"]
    assert out["summary"]["href"] == [] and out["skeleton"]["href"] == []


def test_the_heading_and_tab_row_css_follow_the_design() -> None:
    panel = (SHARED / "panel.css").read_text()
    shared = (SHARED / "scope_tabs.css").read_text()
    page = (VIEWS / "scope.css").read_text()
    pc = panel[: panel.index("@container app (max-width: 640px)")]
    phone = panel[panel.index("@container app (max-width: 640px)") :]
    head = _rules(pc, ".sd-pn .pn-head")[0]
    assert "display: flex" in head and "flex-wrap" not in head  # one row
    crumb = _rules(pc, ".sd-pn .pn-crumb")[0]
    assert "flex: 1 1 0" in crumb and "min-width: 0" in crumb and "overflow: hidden" in crumb
    assert "flex-wrap: wrap" in _rules(pc, ".sd-pn .pn-head.is-stacked")[0]
    stacked = _rules(pc, ".sd-pn .pn-head.is-stacked .pn-crumb")[0]
    assert "order: 9" in stacked and "flex: 1 0 100%" in stacked
    # the cleanup list's heading keeps its close button at the right end
    assert ".sd-pn .pn-head .iconbtn { margin-left: auto;" in pc
    title = _rules(pc, ".sd-pn .pn-title")[0]
    assert "-webkit-line-clamp: 2" in title and "-webkit-box-orient: vertical" in title and "overflow: hidden" in title
    why = _rules(pc, ".sd-pn .pn-why")[0]
    assert "white-space: nowrap" in why and "overflow: hidden" in why
    assert "text-overflow: ellipsis" in _rules(pc, ".sd-pn .pn-why .pn-reason")[0]
    assert "var(--ds-danger-ink)" in _rules(pc, '.sd-pn .pn-why[data-merge="needs_fix"] .pn-merge-mark')[0]
    assert "var(--ds-ok-ink)" in _rules(pc, '.sd-pn .pn-why[data-merge="mergeable"] .pn-merge-mark')[0]
    assert "display: flex" in _rules(pc, ".sd-pn .pn-tabrow")[0]
    assert _rules(pc, ".sd-pn .pn-tabopen:empty") == [" display: none; "]
    assert "border-bottom" not in _rules(pc, ".sd-pn .pn-tabs")[0]
    hidden = _rules(
        phone,
        '.sd-pn[data-snap="full"] :is(.pn-path > button, .pn-path > .ds-icon, .pn-top-mark, .pn-kind, .pn-why)',
    )
    assert hidden == [" display: none; "]
    full_title = _rules(phone, '.sd-pn[data-snap="full"] .pn-title')[0]
    assert "white-space: nowrap" in full_title and "display: block" in full_title
    assert _rules(phone, '.sd-pn[data-snap="full"] .pn-tabrow') == [" margin-top: 0; "]
    for gone in (".sd-framebar__open", ".sd-framebar__name", ".pn-kicker", ".pn-merge {", ".pn-merge,"):
        assert gone not in panel + shared + page, gone
    assert "& .sd-tabopen" in shared
    assert _rules(page, "& .sd-tabs-row .sd-tabopen") == [" align-self: center; margin-bottom: 6px; "]
