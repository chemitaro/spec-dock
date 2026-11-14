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

TAB_KEYS = ["explanation", "summary", "deps", "children", "docs", "artifacts", "todos"]
TAB_LABELS = ["説明資料", "概要", "依存", "配下", "文書", "Artifact", "人のタスク"]
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
    assert re.search(r'<a [^>]*href="[^"]*explanation\.html[^"]*" target="_blank" rel="noopener"', written)
    assert "新しいタブで開く" in written
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
    assert "SCOPE_TABS.map(" in scope and "pickTab(" in scope
    for name in MOVED:
        assert not re.search(rf"function {name}\b", scope), name
        assert re.search(rf"function {name}\b", shared), name
    assert "TABS" not in (SHARED / "logic.js").read_text().replace("SCOPE_TABS", "")


def test_the_panel_draws_its_tabs_from_the_same_list_and_the_graph_uses_it() -> None:
    panel = (SHARED / "panel.js").read_text()
    assert 'from "./scope_tabs.js"' in panel and "SCOPE_TABS.map(" in panel and "pickTab(" in panel
    assert "export function createScopePanel(" in panel
    graph = (VIEWS / "graph.js").read_text()
    assert 'import { createScopePanel } from "./_shared/panel.js";' in graph
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
    assert touch == [".sd-pn .pn-grab", ".sd-pn .pn-top"]  # the contents and the frame scroll freely (R-07)
    assert "height: var(--pn-h" in phone and ".sd-pn.is-dragging iframe { pointer-events: none; }" in phone
    assert "overscroll-behavior: contain" in css
