"""The Scope panel's heading, band, tab-row link and sheet height under node (iss-00656 T-02, T-05)."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[3]
SHARED = ROOT / "src" / "spec_dock" / "assets" / "dashboard" / "views" / "_shared"
FAKE_DOM = ROOT / "tests" / "js" / "fake_dom.mjs"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

NOW = "2026-11-04T12:00:00Z"

HARNESS = """
const {Element, hooks, install} = await import(FAKE_URL);
const page = install({width: globalThis.WIDTH ?? 1440, height: 800});
const observers = [];
globalThis.ResizeObserver = class {
  constructor(fn) {this.fn = fn; this.targets = []; observers.push(this);}
  observe(el) {this.targets.push(el);}
  disconnect() {this.targets = [];}
};
const {createScopePanel} = await import(PANEL_URL);
const logic = await import(LOGIC_URL);
const at = (minutes) => new Date(Date.parse(NOW) - minutes * 60000).toISOString();
const S = (id, extra = {}) => ({id, number: Number(id.slice(-5)), kind: id.split("-")[0] === "iss" ? "issue" : id.split("-")[0],
  state: "doing", title: `題名${Number(id.slice(-5))}`, path: `/r/x/scopes/${id}`, children: [], active_at: at(1), reason: {code: "in_progress", text: "作業中"}, ...extra});
const init = S("initiative-00001", {kind: "initiative", state: "ready", reason: {code: "no_waits", text: "待っているものはない"}, parent_id: null});
const epic = S("epic-00002", {parent_id: init.id, reason: {code: "descendant_in_progress", text: "配下の 1件が作業中"}});
const issue = S("iss-00003", {parent_id: epic.id});
const all = [init, epic, issue];
const byIdOf = (list) => new Map(list.map((item) => [item.id, item]));
const ctxOf = (list = all) => ({href: (p) => p, data: {scopes: list}, embed: false, orca: null,
  route: {path: "/r/x/graph", params: new URLSearchParams()}});
const written = (extra = {}) => ({catalog: "ok", spec: null, adrs: [], artifacts: [], check: null, progress: null,
  documents: [
    {key: "requirement", name: "requirement.md", exists: true, href: "/f/requirement.md", view: "/v/requirement.md"},
    {key: "design", name: "design.md", exists: true, href: "/f/design.md", view: "/v/design.md"},
    {key: "explanation", name: "explanation.html", exists: true, skeleton: false, href: "/f/explanation.html?x=1&y=<z>"},
  ], ...extra});
const stateOf = (scope, {list = all, details = null, docState = details ? "ok" : "loading"} = {}) => ({
  ctx: ctxOf(list), scope, byId: byIdOf(list), docState, doc: details ? {scope, details} : null});
const aside = new Element("aside");
const selected = [];
let closed = 0;
const pn = createScopePanel(aside, {onSelect: (id) => selected.push(id), onClose: () => closed++});
const q = (sel) => aside.querySelector(sel);
const text = (sel) => q(sel)?.textContent ?? null;
const count = (hay, needle) => hay.split(needle).length - 1;
const click = (el) => aside.listeners.click.forEach((fn) => fn({target: el, button: 0, preventDefault() {}}));
const opener = () => {
  const a = q(".pn-tabopen a");
  return a ? {href: a.getAttribute("href"), label: a.getAttribute("aria-label"), title: a.getAttribute("title"),
    target: a.getAttribute("target"), n: aside.querySelectorAll(".pn-tabopen a").length} : null;
};
"""


def _run(script: str, tmp_path: Path, *, width: int = 1440) -> dict:
    runner = tmp_path / "check.mjs"
    runner.write_text(
        f"globalThis.WIDTH = {width};\n"
        f"const NOW = {json.dumps(NOW)};\n"
        f"const FAKE_URL = {json.dumps(FAKE_DOM.as_uri())};\n"
        f"const PANEL_URL = {json.dumps((SHARED / 'panel.js').as_uri())};\n"
        f"const LOGIC_URL = {json.dumps((SHARED / 'panel_logic.js').as_uri())};\n"
        "const out = {};\n" + HARNESS + textwrap.dedent(script) + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=60)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


# --- T-02: the first row: ancestors, then the Scope's ID once ----------------------------------------------------


def test_the_first_row_lists_ancestors_then_the_scope_id_exactly_once(tmp_path: Path) -> None:
    out = _run(
        """
        out.rows = [issue, epic, init].map((scope) => {
          pn.show(stateOf(scope));
          const top = text(".pn-top");
          return {
            ids: (text(".pn-crumb").match(/[a-z]+-\\d{5}/g) || []),
            self: count(top, scope.id),
            kind: text(".pn-self .pn-kind"),
            top: aside.querySelectorAll(".pn-crumb .pn-top-mark").map((el) => [el.getAttribute("role"), el.getAttribute("aria-label"), el.getAttribute("title")]),
            titles: aside.querySelectorAll(".pn-crumb button[data-pn-goto]").map((b) => b.getAttribute("title")),
            old: [".pn-kicker", ".pn-merge", ".pn-cover .pn-path", "p.pn-idle"].filter((sel) => q(sel)),
            order: aside.querySelector(".pn-head").elements.map((el) => el.className),
          };
        });
        pn.show(stateOf(issue));
        click(q('.pn-crumb button[data-pn-goto="initiative-00001"]'));
        click(q('.pn-crumb button[data-pn-goto="epic-00002"]'));
        out.selected = selected;
        """,
        tmp_path,
    )
    issue, epic, init = out["rows"]
    assert issue["ids"] == ["initiative-00001", "epic-00002", "iss-00003"]
    assert epic["ids"] == ["initiative-00001", "epic-00002"]
    assert init["ids"] == ["initiative-00001"]
    assert [row["self"] for row in out["rows"]] == [1, 1, 1]
    assert issue["kind"] == "#3・Issue" and epic["kind"] == "#2・Epic" and init["kind"] == "#1・Initiative"
    assert issue["top"] == [] and epic["top"] == []
    assert init["top"] == [["img", "最上位", "最上位"]]
    assert issue["titles"] == ["initiative-00001 題名1", "epic-00002 題名2"]
    assert all(row["old"] == [] for row in out["rows"])
    assert issue["order"] == ["pn-crumb", "pn-hl", "pn-orca", "iconbtn pn-close"]
    assert out["selected"] == ["initiative-00001", "epic-00002"]


def test_the_title_is_its_own_row_with_the_full_text_in_title(tmp_path: Path) -> None:
    out = _run(
        """
        const long = {...issue, title: "とても長い題名 <b>&</b> ".repeat(8).trim()};
        pn.show(stateOf(long, {list: [init, epic, long]}));
        const h = q(".pn-cover .pn-title");
        out.tag = h.tag; out.title = h.getAttribute("title"); out.text = h.textContent; out.full = long.title;
        out.first = q(".pn-cover").firstElementChild.className;
        """,
        tmp_path,
    )
    assert out["tag"] == "h2" and out["first"] == "pn-title"
    assert out["title"] == out["full"] and out["text"] == out["full"]


# --- T-02: the band only when it adds something ------------------------------------------------------------------


def test_the_band_shows_only_reasons_that_add_to_the_state(tmp_path: Path) -> None:
    out = _run(
        """
        const view = (scope) => {
          pn.show(stateOf(scope, {list: [init, epic, scope]}));
          const why = q(".pn-why");
          return {band: why ? {text: why.textContent, title: why.getAttribute("title"), st: why.getAttribute("data-st"),
              merge: why.getAttribute("data-merge"), reason: why.querySelector(".pn-reason")?.textContent ?? null,
              idle: why.querySelector(".pn-idle")?.textContent ?? null, mark: why.querySelector(".pn-merge-mark")?.innerHTML ?? null,
              icon: why.querySelector(".st-ico") ? "state" : null} : null,
            label: count(text(".pn-top"), scope.state === "done" ? "終わった" : scope.state === "ready" ? "着手できる" : "作業中"),
            badge: aside.querySelectorAll(".pn-top .sd-badge").map((b) => b.textContent)};
        };
        const id = "iss-00009";
        out.plain = [
          S(id, {parent_id: epic.id}),
          S(id, {parent_id: epic.id, state: "done", reason: {code: "closed", text: "終わった"}}),
          S(id, {parent_id: epic.id, state: "ready", reason: {code: "no_waits", text: "待っているものはない"}}),
          S(id, {parent_id: epic.id, reason: null}),
          S(id, {parent_id: epic.id, reason: {text: ""}}),
        ].map(view);
        out.adds = [
          S(id, {parent_id: epic.id, state: "blocked", reason: {code: "waiting", text: "#12 を待つ"}}),
          S("epic-00009", {kind: "epic", parent_id: init.id, reason: {code: "descendant_in_progress", text: "配下の 2件が作業中"}}),
          S(id, {parent_id: epic.id, reason: {code: "pr_mergeable", text: "PR #4 をマージできる"}}),
          S(id, {parent_id: epic.id, state: "unknown", reason: {code: "unknown", text: "構造が分からない（循環）"}}),
        ].map(view);
        out.idle = view(S(id, {parent_id: epic.id, active_at: at(45)}));
        out.blockedOld = view(S(id, {parent_id: epic.id, state: "blocked", active_at: at(45), reason: {code: "waiting", text: "#12 を待つ"}}));
        """,
        tmp_path,
    )
    for row in out["plain"]:
        assert row["band"] is None, row
        assert row["label"] == 1, row  # the state's name only on the chip
    reasons = ["#12 を待つ", "配下の 2件が作業中", "PR #4 をマージできる", "構造が分からない（循環）"]
    for row, reason in zip(out["adds"], reasons, strict=True):
        band = row["band"]
        assert band["reason"] == reason and band["title"] == reason and band["idle"] is None and band["icon"] is None
    assert out["adds"][0]["band"]["st"] == "blocked"
    idle = out["idle"]["band"]
    assert idle["reason"] is None and idle["idle"] == "45分動きなし" and idle["title"] == "45分動きなし"
    assert "作業中" not in idle["text"]
    assert out["blockedOld"]["band"]["idle"] is None  # idleText stays as it is: only a Scope in progress idles


def test_the_merge_chip_folds_into_the_band(tmp_path: Path) -> None:
    out = _run(
        """
        const view = (scope) => {
          pn.show(stateOf(scope, {list: [init, epic, scope]}));
          const why = q(".pn-why");
          return {badges: aside.querySelectorAll(".pn-top .sd-badge").length, merge: why?.getAttribute("data-merge") ?? null,
            reason: why?.querySelector(".pn-reason")?.textContent ?? null, mark: why?.querySelector(".pn-merge-mark")?.innerHTML ?? null,
            first: why?.firstElementChild?.className ?? null, hl: q(".pn-hl").innerHTML};
        };
        out.fix = view(S("iss-00009", {parent_id: epic.id, merge: "needs_fix", reason: {code: "pr_needs_fix", text: "PR #4 を直す必要がある（CI が失敗）"}}));
        out.ok = view(S("iss-00009", {parent_id: epic.id, merge: "mergeable", reason: {code: "pr_mergeable", text: "PR #4 をマージできる"}}));
        out.plain = view(S("iss-00009", {parent_id: epic.id, merge: "mergeable"}));
        out.plainFix = view(S("iss-00009", {parent_id: epic.id, merge: "needs_fix"}));
        """,
        tmp_path,
    )
    for row in (out["fix"], out["ok"], out["plain"], out["plainFix"]):
        assert row["badges"] == 0 and "マージ待ち" not in row["hl"] and row["first"] == "pn-merge-mark", row
    assert out["fix"]["merge"] == "needs_fix" and out["fix"]["reason"] == "PR #4 を直す必要がある（CI が失敗）"
    assert out["ok"]["merge"] == "mergeable" and out["ok"]["reason"] == "PR #4 をマージできる"
    assert out["fix"]["mark"] != out["ok"]["mark"]  # zap and check
    assert out["plain"]["reason"] == "マージ待ち・マージできる" and out["plain"]["mark"] == out["ok"]["mark"]
    assert out["plainFix"]["reason"] == "マージ待ち・直す必要あり" and out["plainFix"]["mark"] == out["fix"]["mark"]


def test_a_redraw_in_the_same_state_leaves_the_heading_parts_alone(tmp_path: Path) -> None:
    out = _run(
        """
        pn.show(stateOf(issue));
        const writes = () => [".pn-top", ".pn-crumb", ".pn-hl", ".pn-cover"].map((sel) => q(sel).writes);
        out.first = writes();
        pn.show(stateOf(issue));
        pn.refreshOrca();
        out.same = writes();
        pn.show(stateOf({...issue, title: "other"}));
        out.title = writes();
        """,
        tmp_path,
    )
    assert out["first"] == [1, 1, 1, 1]
    assert out["same"] == [1, 1, 1, 1]
    assert out["title"] == [1, 1, 1, 2]


# --- T-02: the tab row's link that opens the frame in a new tab --------------------------------------------------


def test_the_tab_row_links_the_shown_frame_and_nothing_else(tmp_path: Path) -> None:
    out = _run(
        """
        const tabButton = (key) => q(`.pn-tabs [data-pn-tab="${key}"]`);
        pn.show(stateOf(issue));
        out.loading = opener();
        pn.show(stateOf(issue, {details: written()}));
        out.explanation = opener();
        out.row = q(".pn-tabrow").elements.map((el) => el.className);
        click(tabButton("docs"));
        out.docs = opener();
        click(q('.pn-body a[data-pn-param="doc"][data-pn-value="design"]'));
        out.design = opener();
        click(tabButton("summary"));
        out.summary = opener();
        click(tabButton("explanation"));
        out.back = opener();
        pn.show(stateOf(issue, {details: written(), docState: "failed"}));
        out.failed = opener();
        const skeleton = written({documents: written().documents.map((d) => d.key === "explanation" ? {...d, skeleton: true} : d)});
        pn.show(stateOf(epic, {details: skeleton}));
        out.skeleton = [opener(), q('.pn-tabs [aria-selected="true"]').getAttribute("data-pn-tab")];
        click(tabButton("summary"));
        click(tabButton("explanation"));
        out.skeletonTab = opener();
        pn.show(stateOf(issue, {details: {catalog: "missing"}}));
        out.unreadable = opener();
        click(tabButton("docs"));
        out.unreadableDocs = opener();
        """,
        tmp_path,
    )
    assert out["loading"] is None
    assert out["row"] == ["pn-tabs", "pn-tabopen"]
    assert out["explanation"] == {
        "href": "/f/explanation.html?x=1&y=<z>",
        "label": "説明資料を新しいタブで開く",
        "title": "説明資料を新しいタブで開く",
        "target": "_blank",
        "n": 1,
    }
    assert out["docs"]["href"] == "/v/requirement.md" and out["docs"]["label"] == "要件を新しいタブで開く"
    assert out["design"]["href"] == "/v/design.md" and out["design"]["label"] == "設計を新しいタブで開く"
    assert out["summary"] is None
    assert out["back"]["href"] == "/f/explanation.html?x=1&y=<z>"
    assert out["failed"] is None
    assert out["skeleton"] == [None, "explanation"] and out["skeletonTab"] is None
    assert out["unreadable"] is None and out["unreadableDocs"] is None


def test_the_explanation_tab_has_no_bar_in_the_panel(tmp_path: Path) -> None:
    out = _run(
        """
        pn.show(stateOf(issue, {details: written()}));
        out.first = q(".pn-body").firstElementChild?.firstElementChild?.className ?? null;
        out.bar = !!q(".pn-body .sd-framebar");
        """,
        tmp_path,
    )
    assert out["first"] == "sd-explain" and out["bar"] is False


# --- T-02: sending the crumb to its own row only when it does not fit (D-07) ------------------------------------


def test_head_overflows_allows_one_pixel(tmp_path: Path) -> None:
    out = _run(
        """
        out.v = [[200, 200], [201, 200], [202, 200], [150, 200], [undefined, 200]].map(([scrollWidth, clientWidth]) =>
          logic.headOverflows({scrollWidth, clientWidth}));
        """,
        tmp_path,
    )
    assert out["v"] == [False, False, True, False, False]


FIT = """
let over = false;
hooks.sizes = (el) => (el.classList.contains("pn-crumb") ? {width: 200, scrollWidth: over ? 260 : 200} : null);
const stacked = () => q(".pn-head").classList.contains("is-stacked");
"""


def test_the_crumb_moves_to_its_own_row_only_when_it_overflows(tmp_path: Path) -> None:
    out = _run(
        FIT
        + """
        pn.show(stateOf(issue));
        out.fits = stacked();
        over = true;
        pn.show(stateOf(issue));
        out.draw = stacked();
        over = false;
        pn.refreshOrca();
        out.marks = stacked();
        over = true;
        page.winListeners.resize.forEach((fn) => fn());
        out.resize = stacked();
        over = false;
        const watch = observers.find((o) => o.targets.some((el) => el.classList?.contains("pn-head")));
        out.watched = watch ? watch.targets.map((el) => el.classes()[0]).sort() : null;
        watch.fn([]);
        out.observed = stacked();
        over = true;
        watch.fn([]);
        out.observedAgain = stacked();
        """,
        tmp_path,
    )
    assert out["fits"] is False and out["draw"] is True and out["marks"] is False
    assert out["resize"] is True
    assert out["watched"] == ["pn-crumb", "pn-head"]
    assert out["observed"] is False and out["observedAgain"] is True


def test_the_full_sheet_never_stacks_and_snap_changes_measure_again(tmp_path: Path) -> None:
    out = _run(
        FIT
        + """
        over = true;
        pn.show(stateOf(issue));
        out.half = [aside.dataset.snap, stacked()];
        click(q(".pn-grab"));
        out.full = [aside.dataset.snap, stacked()];
        click(q(".pn-grab"));
        out.back = [aside.dataset.snap, stacked()];
        // a drag to the top, then a cancelled drag
        const ev = (type, y) => aside.listeners[type].forEach((fn) => fn({type, pointerId: 1, pointerType: "touch", button: 0, clientY: y, target: q(".pn-cover")}));
        hooks.rect = (el) => (el === aside ? {top: 0, left: 0, right: 390, bottom: 800, width: 390, height: 790, } : null);
        ev("pointerdown", 500); ev("pointermove", 300); ev("pointerup", 300);
        out.dragged = [aside.dataset.snap, stacked()];
        hooks.rect = null;
        await new Promise((resolve) => setTimeout(resolve, 0)); // the click that ends a drag is not a tap
        click(q(".pn-grab"));
        out.tapped = [aside.dataset.snap, stacked()];
        over = false;
        ev("pointerdown", 100); ev("pointermove", 400); ev("pointercancel", 400);
        out.cancelled = [aside.dataset.snap, stacked()];
        """,
        tmp_path,
        width=390,
    )
    assert out["half"] == ["half", True]
    assert out["full"] == ["full", False]
    assert out["back"] == ["half", True]
    assert out["dragged"] == ["full", False]
    assert out["tapped"] == ["half", True]
    assert out["cancelled"] == ["half", False]


def test_another_drawings_heading_never_stacks(tmp_path: Path) -> None:
    out = _run(
        FIT
        + """
        over = true;
        pn.show(stateOf(issue));
        pn.hide();
        aside.innerHTML = '<div class="pn-head"><b>片付けの候補 1件</b><button type="button" class="iconbtn" data-act="close" aria-label="閉じる"></button></div><div class="pn-body"></div>';
        page.winListeners.resize.forEach((fn) => fn());
        observers.forEach((o) => o.fn([]));
        out.cls = q(".pn-head").className;
        """,
        tmp_path,
    )
    assert out["cls"] == "pn-head"


# --- T-05: the sheet keeps its height while another drawing redraws (D-08) --------------------------------------

SHEET = """
const cleanup = () => {
  pn.hide();
  aside.innerHTML = '<button type="button" class="pn-grab" aria-label="欄の高さを変える"></button><div class="pn-head"><b>片付けの候補</b></div><div class="pn-body"></div>';
  aside.classList.add("is-open");
};
const closeCleanup = () => pn.hide();
const grab = () => click(q(".pn-grab"));
const sheet = () => [aside.dataset.snap ?? null, aside.style.getPropertyValue("--pn-h")];
"""


def test_a_full_cleanup_list_stays_full_through_redraws(tmp_path: Path) -> None:
    out = _run(
        SHEET
        + """
        cleanup();
        out.opened = sheet();
        grab();
        out.full = sheet();
        cleanup();
        out.redrawn = sheet();
        cleanup();
        out.again = sheet();
        // a Scope chosen inside the full list keeps the height
        pn.show(stateOf(issue));
        out.chosen = sheet();
        """,
        tmp_path,
        width=390,
    )
    assert out["opened"] == [None, ""]  # an aside that never was a sheet keeps the CSS's own height (iss-00650)
    assert out["full"] == ["full", "800px"]
    assert out["redrawn"] == ["full", "800px"] and out["again"] == ["full", "800px"]
    assert out["chosen"] == ["full", "800px"]


def test_closing_starts_the_next_opening_at_half(tmp_path: Path) -> None:
    out = _run(
        SHEET
        + """
        // the Scope panel closes, then the cleanup list opens
        pn.show(stateOf(issue));
        grab();
        out.scopeFull = sheet();
        pn.hide();
        aside.classList.remove("is-open");
        cleanup();
        out.afterScope = sheet();
        // the full cleanup list closes by its button, then opens again
        grab();
        closeCleanup();
        aside.classList.remove("is-open");
        cleanup();
        out.reopened = sheet();
        // the full cleanup list closes, then a Scope is chosen
        grab();
        closeCleanup();
        aside.classList.remove("is-open");
        pn.show(stateOf(issue));
        out.scopeAfter = sheet();
        """,
        tmp_path,
        width=390,
    )
    assert out["scopeFull"] == ["full", "800px"]
    assert out["afterScope"] == ["half", "464px"]
    assert out["reopened"] == ["half", "464px"]
    assert out["scopeAfter"] == ["half", "464px"]


def test_the_hide_rule_and_show_rule_are_in_place() -> None:
    panel = (SHARED / "panel.js").read_text()
    hide = panel[panel.index("    hide() {") :]
    assert "const keep = current == null && isShown();" in hide
    show = panel[panel.index("    show(state) {") : panel.index("    hide() {")]
    assert re.search(r"if \(!isShown\(\)\) snap = \"half\";", show)
