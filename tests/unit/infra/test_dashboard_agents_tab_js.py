"""The agents tab in the panel and the detail screen under node (iss-00593 T-04〜T-06)."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

import pytest

ASSETS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/dashboard"
VIEWS = ASSETS / "views"
SHARED = VIEWS / "_shared"
NODE = shutil.which("node")
node = pytest.mark.skipif(NODE is None, reason="node is not installed")

SANDBOX = "allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"

# A page-free world: the theme, the page origin, a stubbed ctx.orca and one Scope with one worktree record.
WORLD = """
let theme = null; let dark = false;
globalThis.document = {documentElement: {dataset: {}}};
Object.defineProperty(globalThis.document.documentElement.dataset, "theme", {get: () => theme ?? undefined, configurable: true});
globalThis.matchMedia = () => ({matches: dark});
globalThis.location = {origin: "http://127.0.0.1:47800"};
const tabs = await import(SCOPE_TABS);
const at = await import(AGENTS_TAB);
const logic = await import(AGENTS_LOGIC);
const raw = (id, extra = {}) => ({id, mark: "working", agentType: "claude", detail: "/embed/agent?id=" + encodeURIComponent(id), ...extra});
const tree = (id, branch, agents) => ({id, path: "/w/" + id, branch, agents});
const sid = "iss-00001";
const scope = {id: sid, number: 1, kind: "issue", state: "doing", title: "T", path: "/r/github.com/o/r/scopes/iss-00001", children: []};
const other = {id: "iss-00002", number: 2, kind: "issue", state: "doing", title: "U", path: "/r/github.com/o/r/scopes/iss-00002", children: []};
const records = [{path: "/w/w1", branch: "one"}];
const structure = {worktrees: {status: "ok", paths: []}, scopes: [{...scope, worktrees: records}, {...other, worktrees: records}]};
const byId = new Map(structure.scopes.map((item) => [item.id, item]));
const doc = {scope, details: {catalog: "ok", documents: [], adrs: [], artifacts: []}};
const otherDoc = {scope: other, details: {catalog: "ok", documents: [], adrs: [], artifacts: []}};
const world = {status: "ok", trees: {[sid]: [tree("w1", "one", [raw("a")])]}, forScope: 0, marks: null};
const orca = {
  origin: "http://127.0.0.1:8791",
  status: () => world.status,
  summary: () => null,
  marks: () => world.marks,
  forScope: (data, id) => { world.forScope++; return world.trees[id] ?? []; },
  subscribe: () => () => {},
};
const pageCtx = (query = "tab=agents", extra = {}) => {
  const ctx = {
    data: structure, orca, orcaProblem: null, embed: false, repository: "github.com/o/r",
    href: (path) => path,
    route: {path: scope.path + (query ? "?" + query : ""), params: new URLSearchParams(query)},
    replaced: [],
    ...extra,
  };
  ctx.replaceParam = (name, value) => {
    ctx.replaced.push([name, value]);
    const url = new URL(ctx.route.path, "http://x");
    url.searchParams.set(name, value);
    return {path: url.pathname + "?" + url.searchParams.toString(), params: url.searchParams};
  };
  return ctx;
};
const panelCtx = (extra = {}) => ({data: structure, orca, orcaProblem: null, embed: false, href: (path) => path, route: {path: "/r/github.com/o/r/graph", params: new URLSearchParams()}, ...extra});
const panel = (params = new Map(), extra = {}, which = scope) => tabs.panelEnv(panelCtx(extra), which, which === scope ? doc : otherDoc, byId, {params, tab: "agents"});
const page = (query, extra) => tabs.pageEnv(pageCtx(query, extra), scope, doc, byId);
const counting = (env) => { env.kept = []; const keep = env.keep; env.keep = (name, value) => { env.kept.push([name, value]); keep(name, value); }; return env; };
const reset = () => { logic.memoryFor(at.mem, "reset"); };
const frames = (html) => html.match(/<iframe [^>]*><\\/iframe>/g) ?? [];

// A fake DOM just big enough for paintAgentList: the strip slot, its mark slots, the frame box and the frame.
const fake = () => ({dataset: {}, listeners: [], removed: false, addEventListener(type, fn, capture) { this.listeners.push({type, fn, capture}); }, remove() { this.removed = true; }});
function fakeStrip() {
  const el = fake(); let html = ""; el.writes = 0; el.slots = [];
  Object.defineProperty(el, "innerHTML", {get: () => html, set(value) {
    html = value; el.writes++;
    el.slots = [...value.matchAll(/data-orca-agent="([^"]*)"/g)].map((m) => { const slot = fake(); slot.dataset.orcaAgent = m[1]; return slot; });
  }});
  el.querySelectorAll = (sel) => (sel === "[data-orca-agent]" ? el.slots : []);
  return el;
}
function fakeRoot(html) {
  const strip = html.includes("data-orca-agents") ? fakeStrip() : null;
  const box = html.includes('data-frame="agents"') ? fake() : null;
  const iframe = html.includes("<iframe") ? fake() : null;
  return {strip, box, iframe, querySelector(sel) {
    if (sel === "[data-orca-agents]") return strip;
    if (sel === '.sd-framebox[data-frame="agents"]') return box;
    if (sel === "iframe.sd-agent") return iframe;
    return null;
  }};
}
"""


def _run(script: str, tmp_path: Path) -> dict:
    runner = tmp_path / "check.mjs"
    prelude = (
        WORLD
        .replace("SCOPE_TABS", json.dumps((SHARED / "scope_tabs.js").as_uri()))
        .replace("AGENTS_TAB", json.dumps((SHARED / "agents_tab.js").as_uri()))
        .replace("AGENTS_LOGIC", json.dumps((SHARED / "agents_logic.js").as_uri()))
    )
    runner.write_text(
        'import assert from "node:assert/strict";\nconst out = {};\n'
        + prelude
        + textwrap.dedent(script)
        + "\nconsole.log(JSON.stringify(out));\n"
    )
    done = subprocess.run([NODE, str(runner)], capture_output=True, text=True, timeout=60)  # type: ignore[list-item]
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout.strip().splitlines()[-1])


# --- T-04: the contents of the tab -----------------------------------------------------------------------------


@node
def test_one_agent_opens_its_frame_and_keeps_the_choice(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        const env = counting(panel());
        out.html = at.agentsTab(env);
        out.kept = env.kept;
        reset(); // a fresh Scope memory: otherwise the agent placed last stands in for the empty Map
        const params = new Map();
        const second = counting(panel(params));
        at.agentsTab(second);
        out.map = [...params];
        reset();
        const onPage = counting(page("tab=agents"));
        at.agentsTab(onPage);
        out.replaced = onPage.ctx.replaced;
        out.pageParam = onPage.param("agent");
        out.pageLink = onPage.paramLink("doc", "plan");
        """,
        tmp_path,
    )
    html = out["html"]
    assert html.startswith(
        '<div class="sd-framebox" data-frame="agents"><div class="sd-framebar"><div class="sd-agents" data-orca-agents="iss-00001"></div></div>'
    )
    found = re.findall(r"<iframe [^>]*></iframe>", html)
    assert found == [
        '<iframe class="sd-agent" src="http://127.0.0.1:8791/embed/agent?id=a&amp;theme=light" '
        f'sandbox="{SANDBOX}" referrerpolicy="no-referrer" title="エージェント：claude・one"></iframe>'
    ]
    assert out["kept"] == [["agent", "a"]]
    assert out["map"] == [["agent", "a"]]
    assert out["replaced"] == [["agent", "a"]]  # the page replaces its query in place (no new history entry)
    assert out["pageParam"] == "a"
    assert "agent=a" in out["pageLink"] and "doc=plan" in out["pageLink"]  # later links use the new query


@node
def test_the_contents_change_only_with_the_chosen_agent_the_theme_and_the_reason(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        const draw = () => at.agentsTab(panel(new Map([["agent", "a"]])));
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        const base = draw();
        const same = [];
        world.trees[sid] = [tree("w1", "one", [raw("b"), raw("a"), raw("c")])]; same.push(draw());
        world.trees[sid] = [tree("w1", "one", [raw("a")])]; same.push(draw());
        world.trees[sid] = [tree("w0", "zero", [raw("x")]), tree("w1", "one", [raw("a", {mark: "waiting", since: "2026-11-14T00:00:00Z"})])]; same.push(draw());
        out.same = same.map((html) => html === base);
        theme = "dark"; out.dark = draw(); theme = null;
        dark = true; out.osDark = draw(); dark = false;
        world.trees[sid] = [tree("w1", "two", [raw("a"), raw("b")])]; out.branch = draw();
        world.trees[sid] = [tree("w1", "one", [raw("a", {agentType: "codex"}), raw("b")])]; out.kind = draw();
        out.base = base;
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        """,
        tmp_path,
    )
    assert out["same"] == [True] * 3
    for key in ("dark", "osDark", "branch", "kind"):
        assert out[key] != out["base"], key
    assert "theme=dark" in out["dark"] and "theme=dark" in out["osDark"] and "theme=light" in out["base"]
    assert "エージェント：claude・two" in out["branch"] and "エージェント：codex・one" in out["kind"]


@node
def test_drift_gone_choose_and_shape_draw_no_frame(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        logic.memoryFor(at.mem, sid); logic.noteDrift(at.mem, "a");
        out.drift = at.agentsTab(panel(new Map([["agent", "a"]])));
        reset();
        out.choose = at.agentsTab(panel());
        out.gone = at.agentsTab(panel(new Map([["agent", "gone:z"]])));
        reset();
        world.trees[sid] = [tree("w1", "one", [{id: "a", detail: "/embed/agent?id=b"}, {id: "c", detail: 3}])];
        out.shape = at.agentsTab(panel());
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    for key in ("drift", "choose", "gone", "shape"):
        assert "<iframe" not in out[key], key
    drift = out["drift"]
    assert 'data-code="orca-agent-drift"' in drift and 'data-tone="warning"' in drift
    assert "選んだのと別のエージェントに移ったので閉じた" in drift
    assert re.search(
        r'<a data-agent-pick="a" href="[^"]*agent=a[^"]*" data-pn-param="agent" data-pn-value="a">選んだエージェントに戻す</a>',
        drift,
    )
    assert 'data-code="orca-agent-choose"' in out["choose"] and "エージェントを選ぶ" in out["choose"]
    assert 'data-code="orca-agent-gone"' in out["gone"] and "選んでいたエージェントはいなくなった" in out["gone"]
    assert 'data-code="orca-shape"' in out["shape"] and "（2件）" in out["shape"]
    assert "data-orca-agents" not in out["shape"]


@node
def test_each_reason_has_its_own_notice(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        const notices = {};
        for (const status of ["loading", "unreachable", "orca-unreachable", "orca-starting"]) {
          world.status = status; notices[status] = at.agentsTab(panel());
        }
        world.status = "ok";
        notices.config = at.agentsTab(panel(new Map(), {orcaProblem: "orca_web.port <must> be a number"}));
        notices.configEmbed = at.agentsTab(panel(new Map(), {orcaProblem: "bad", embed: true}));
        notices.embed = at.agentsTab(panel(new Map(), {embed: true}));
        out.notices = notices;
        """,
        tmp_path,
    )
    n = out["notices"]
    assert 'data-code="orca-loading"' in n["loading"] and 'data-tone="note"' in n["loading"]
    assert "orca-web を読んでいる" in n["loading"]
    assert (
        'data-code="orca-unreachable"' in n["unreachable"]
        and "orca-web（http://127.0.0.1:8791）に届かない" in n["unreachable"]
    )
    assert "ORCA_WEB_READ_ORIGINS" in n["unreachable"] and "http://127.0.0.1:47800" in n["unreachable"]
    assert (
        'data-code="orca-orca-unreachable"' in n["orca-unreachable"]
        and "connection.state：unreachable" in n["orca-unreachable"]
    )
    assert 'data-code="orca-orca-starting"' in n["orca-starting"] and "connection.state：starting" in n["orca-starting"]
    assert 'data-code="orca-config"' in n["config"] and "orca_web.port &lt;must&gt; be a number" in n["config"]
    assert "config.json" in n["config"] and "新しいタブで開く" not in n["config"]
    assert 'href="/r/github.com/o/r/scopes/iss-00001" target="_blank" rel="noopener"' in n["configEmbed"]
    assert 'data-code="orca-embed"' in n["embed"] and "埋め込みの画面ではチャットを開けない" in n["embed"]
    assert 'href="/r/github.com/o/r/scopes/iss-00001" target="_blank" rel="noopener"' in n["embed"]
    for key, html in n.items():
        assert html.count('class="sd-callout"') == 1, key
        assert 'data-tone="warning"' in html or key == "loading", key
        assert "<iframe" not in html and "data-orca-agents" not in html, key


@node
def test_the_contents_never_carry_write_paths_or_the_send_state(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const plain = at.agentsTab(panel());
        orca.sendEnabled = true; const on = at.agentsTab(panel(new Map(), {sendEnabled: true}));
        orca.sendEnabled = false; const off = at.agentsTab(panel(new Map(), {sendEnabled: false}));
        delete orca.sendEnabled;
        out.html = plain; out.same = on === plain && off === plain;
        """,
        tmp_path,
    )
    assert out["same"]
    assert "/api/" not in out["html"] and "postMessage" not in out["html"]
    source = (SHARED / "agents_tab.js").read_text(encoding="utf-8")
    assert "sendEnabled" not in source and "/api/" not in source and "postMessage" not in source


# --- T-05: the tab list, the envs, the state and the strip -------------------------------------------------------


@node
def test_the_tab_list_and_its_visibility(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        out.keys = tabs.TAB_KEYS;
        const keysOf = (env) => tabs.visibleTabs(env).map((tab) => tab.key);
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        const shown = panel();
        out.shown = keysOf(shown);
        out.count = tabs.SCOPE_TABS[1].count(shown);
        world.trees[sid] = [];
        out.empty = keysOf(panel());
        world.status = "unreachable";
        const waiting = panel();
        out.waiting = keysOf(waiting); out.waitingCount = tabs.SCOPE_TABS[1].count(waiting);
        world.status = "off";
        out.off = keysOf(panel());
        world.status = "ok";
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        world.forScope = 0;
        const once = panel();
        tabs.SCOPE_TABS[1].visible(once); tabs.SCOPE_TABS[1].count(once); tabs.SCOPE_TABS[1].render(once); at.agentsState(once);
        out.forScope = world.forScope;
        """,
        tmp_path,
    )
    rest = ["explanation", "summary", "deps", "children", "docs", "artifacts", "todos"]
    assert out["keys"] == ["explanation", "agents", *rest[1:]]
    assert out["shown"] == ["explanation", "agents", *rest[1:]] and out["count"] == 2
    assert out["empty"] == rest and out["off"] == rest
    assert out["waiting"] == ["explanation", "agents", *rest[1:]] and out["waitingCount"] is None
    assert out["forScope"] == 1  # one decision per env


@node
def test_keep_replaces_the_page_query_and_writes_the_panel_map(tmp_path: Path) -> None:
    out = _run(
        """
        const env = page("tab=agents&doc=plan");
        out.before = env.param("agent");
        env.keep("agent", "a");
        out.after = env.param("agent");
        out.link = env.paramLink("done", true);
        out.replaced = env.ctx.replaced;
        env.keep("agent", "a");
        out.again = env.ctx.replaced.length;
        const bare = tabs.pageEnv({...pageCtx("tab=agents"), replaceParam: undefined}, scope, doc, byId);
        bare.keep("agent", "a");
        out.bare = bare.param("agent");
        const params = new Map([["doc", "plan"]]);
        const ctx = panelCtx();
        const inPanel = tabs.panelEnv(ctx, scope, doc, byId, {params, tab: "agents"});
        inPanel.keep("agent", "a");
        out.map = [...params]; out.route = ctx.route.path; out.panelParam = inPanel.param("agent");
        """,
        tmp_path,
    )
    assert out["before"] is None and out["after"] == "a"
    assert out["replaced"] == [["agent", "a"]] and out["again"] == 1
    assert "agent=a" in out["link"] and "done=1" in out["link"] and "doc=plan" in out["link"]
    assert out["bare"] is None
    assert out["map"] == [["doc", "plan"], ["agent", "a"]] and out["route"] == "/r/github.com/o/r/graph"
    assert out["panelParam"] == "a"


@node
def test_the_state_reads_the_summary_and_never_keeps(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a"), {id: "x", detail: "/embed/agent?id=y"}]), tree("w2", "two", [raw("b")])];
        const env = counting(panel(new Map([["agent", "b"]])));
        const state = at.agentsState(env);
        out.agents = state.agents.map((item) => [item.id, item.branch]);
        out.isArray = Array.isArray(state.agents);
        out.invalid = state.invalid;
        out.visible = tabs.SCOPE_TABS[1].visible(env); out.count = tabs.SCOPE_TABS[1].count(env);
        out.keptBefore = env.kept.length;
        out.html = tabs.SCOPE_TABS[1].render(env);
        out.keptAfter = env.kept.length;
        // The chosen agent's entry alone goes out of shape: a shape notice, no loss, and the same agent comes back.
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a"), {id: "b", detail: "/embed/agent?id=c"}])];
        const params = new Map([["agent", "b"]]);
        const broken = counting(panel(params));
        out.brokenReason = at.agentsState(broken).reason;
        out.brokenHtml = at.agentsTab(broken);
        out.brokenGone = [...at.mem.gone]; out.brokenKept = broken.kept; out.brokenMap = [...params];
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        out.fixed = at.agentsTab(panel(params));
        // A loss seen while another tab shows: remembered, not kept, and the same id coming back stays closed.
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        const away = counting(panel(new Map([["agent", "a"]])));
        at.agentsState(away);
        out.awayGone = [...at.mem.gone]; out.awayKept = away.kept;
        const awayParams = new Map([["agent", "a"]]);
        const opened = counting(panel(awayParams));
        at.agentsTab(opened); // the agents tab opened later writes the loss into the Map
        out.openedKept = opened.kept; out.openedMap = [...awayParams];
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        out.back = at.agentsTab(panel(new Map([["agent", "a"]])));
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["agents"] == [["a", "one"], ["b", "two"]] and out["isArray"] and out["invalid"] == 1
    assert out["visible"] is True and out["count"] == 2
    assert out["keptBefore"] == 0 and out["keptAfter"] == 0  # b was chosen already: nothing to keep
    assert "エージェント：claude・two" in out["html"]
    assert out["brokenReason"] == "shape" and 'data-code="orca-shape"' in out["brokenHtml"]
    assert out["brokenGone"] == [] and out["brokenKept"] == [] and out["brokenMap"] == [["agent", "b"]]
    assert "id=b&amp;theme=light" in out["fixed"]
    assert out["awayGone"] == ["a"] and out["awayKept"] == []
    assert out["openedKept"] == [["agent", "gone:a"]] and out["openedMap"] == [["agent", "gone:a"]]
    assert "<iframe" not in out["back"] and 'data-code="orca-agent-gone"' in out["back"]


@node
def test_a_loss_is_remembered_across_envs_of_the_scope_until_another_scope(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const params = new Map();
        at.agentsTab(panel(params)); // a opens by itself
        out.auto = [...params];
        world.trees[sid] = [tree("w1", "one", [raw("b")])]; // a went away, b is left alone
        const lost = counting(panel(params));
        out.lost = at.agentsTab(lost); out.lostKept = lost.kept;
        const draws = {};
        draws.page = at.agentsTab(page("tab=agents")); // a path to the page without agent=
        draws.reopened = at.agentsTab(panel(new Map())); // the panel closed and opened again
        const backEnv = page("tab=agents&agent=a");
        draws.backOld = at.agentsTab(backEnv); // back to the query with the old id
        out.backReplaced = backEnv.ctx.replaced;
        draws.backNone = at.agentsTab(page("tab=summary")); // back to before the choice
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        draws.returned = at.agentsTab(panel(new Map([["agent", "a"]])));
        out.draws = Object.fromEntries(Object.entries(draws).map(([key, html]) => [key, html.includes("<iframe")]));
        out.goneCodes = Object.values(draws).every((html) => html.includes('data-code="orca-agent-gone"'));
        // Another Scope drops the memory; back on the first Scope, the one agent opens again.
        at.agentsState(panel(new Map(), {}, other));
        out.otherGone = [...at.mem.gone];
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        out.afterOther = at.agentsTab(panel(new Map()));
        // The person's pick forgets the loss.
        logic.memoryFor(at.mem, sid); logic.noteGone(at.mem, "a");
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        logic.forgetGone(at.mem, "a");
        out.picked = at.agentsTab(panel(new Map([["agent", "a"]])));
        out.staleQuery = at.agentsTab(page("tab=agents&agent=gone:a"));
        """,
        tmp_path,
    )
    assert out["auto"] == [["agent", "a"]]
    assert "<iframe" not in out["lost"] and 'data-code="orca-agent-gone"' in out["lost"]
    assert out["lostKept"] == [["agent", "gone:a"]]  # a reload keeps only gone:<id> (R-05)
    assert out["backReplaced"] == [["agent", "gone:a"]]
    assert out["draws"] == {"page": False, "reopened": False, "backOld": False, "backNone": False, "returned": False}
    assert out["goneCodes"]
    assert out["otherGone"] == []
    assert "id=b&amp;theme=light" in out["afterOther"]
    assert "id=a&amp;theme=light" in out["picked"]
    assert "<iframe" not in out["staleQuery"]  # the query names a loss: it stays closed


@node
def test_the_strip_is_painted_once_and_follows_the_choice(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        const calls = {build: 0, render: 0};
        world.marks = {
          buildMarks: (doc) => { calls.build++; return [doc.agents[0].mark]; },
          renderAgentMarks: (slot, doc) => { calls.render++; slot.innerHTML = doc.agents[0].mark; },
        };
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const draw = (params) => { const env = panel(params); const html = at.agentsTab(env); const root = fakeRoot(html); at.paintAgentList(root, env); return {env, html, root}; };
        const one = draw(new Map());
        out.label = one.root.strip.innerHTML;
        // The same strip again leaves the slot alone, and the same marks are not drawn again.
        const again = draw(new Map([["agent", "a"]]));
        const rendersBefore = calls.render;
        const env2 = panel(new Map([["agent", "a"]])); at.agentsTab(env2);
        at.paintAgentList(again.root, env2);
        out.writes = again.root.strip.writes; out.renders = calls.render - rendersBefore;
        world.trees[sid] = [tree("w1", "one", [raw("a", {mark: "waiting"})])];
        const env3 = panel(new Map([["agent", "a"]])); at.agentsTab(env3); at.paintAgentList(again.root, env3);
        out.rendersAfterChange = calls.render - rendersBefore; out.writesAfterChange = again.root.strip.writes;
        // Two agents: a switch with links, the chosen one marked, every text escaped, the shape note at the end.
        world.trees[sid] = [tree("w1", "<b>", [raw("a"), raw("b", {agentType: "<i>"}), {id: "c", detail: "x"}])];
        const two = draw(new Map([["agent", "b"]]));
        out.switch = two.root.strip.innerHTML;
        // Gone with one left: a pressable item without aria-current.
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        const lone = draw(new Map([["agent", "a"]]));
        out.lone = lone.root.strip.innerHTML;
        // The press is caught first and forgets the loss; the default handling goes on.
        const capture = lone.root.box.listeners.filter((item) => item.type === "click");
        out.capture = capture.map((item) => item.capture);
        let prevented = false;
        capture[0].fn({target: {closest: (sel) => (sel === "[data-agent-pick]" ? {dataset: {agentPick: "b"}} : null)}, preventDefault: () => { prevented = true; }});
        out.prevented = prevented; out.afterPress = {gone: [...at.mem.gone], picked: at.mem.picked};
        at.paintAgentList(lone.root, lone.env);
        out.captureCount = lone.root.box.listeners.filter((item) => item.type === "click").length;
        // Marks missing or throwing: the strip still draws.
        world.marks = null;
        out.noMarks = draw(new Map()).root.strip.innerHTML.includes("sd-agentpick");
        world.marks = {buildMarks: () => { throw new Error("broken"); }, renderAgentMarks: () => {}};
        out.badMarks = draw(new Map()).root.strip.innerHTML.includes("sd-agentpick");
        world.marks = null;
        // The root without a strip: nothing happens.
        at.paintAgentList({querySelector: () => null}, panel());
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    label = out["label"]
    assert label.startswith(
        '<span class="sd-agentpick" aria-current="true"><span class="sd-agentpick__mark" data-orca-agent="a"></span>'
    )
    assert "<span>claude</span>" in label and '<span class="sd-mono">one</span>' in label and "<a " not in label
    assert out["writes"] == 1 and out["renders"] == 0
    assert out["rendersAfterChange"] == 1 and out["writesAfterChange"] == 1
    items = re.findall(r"<a [^>]*>", out["switch"])
    assert len(items) == 2
    assert 'data-agent-pick="a"' in items[0] and 'data-pn-param="agent"' in items[0] and "aria-current" not in items[0]
    assert 'data-agent-pick="b"' in items[1] and 'aria-current="true"' in items[1]
    assert "&lt;b&gt;" in out["switch"] and "&lt;i&gt;" in out["switch"] and "<b>" not in out["switch"]
    assert out["switch"].endswith('<span class="sd-muted">形の違う 1件は出していない</span>')
    lone = re.findall(r"<a [^>]*>", out["lone"])
    assert len(lone) == 1 and 'data-agent-pick="b"' in lone[0] and "aria-current" not in out["lone"]
    assert out["capture"] == [True] and out["prevented"] is False
    assert out["afterPress"] == {"gone": [], "picked": "b"}
    assert out["captureCount"] == 1
    assert out["noMarks"] and out["badMarks"]


@node
def test_a_second_load_of_the_frame_closes_it(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const env = panel(new Map([["agent", "a"]]));
        const html = at.agentsTab(env);
        const root = fakeRoot(html);
        let redraws = 0;
        at.paintAgentList(root, env, {redraw: () => { redraws++; out.driftInRedraw = at.mem.drift; }});
        at.paintAgentList(root, env, {redraw: () => { redraws += 100; }});
        const loads = root.iframe.listeners.filter((item) => item.type === "load");
        out.loads = loads.length;
        loads[0].fn();
        out.afterFirst = {redraws, drift: at.mem.drift};
        loads[0].fn();
        out.afterSecond = {redraws};
        out.redrawn = at.agentsTab(panel(new Map([["agent", "a"]])));
        // Without a redraw, the frame removes itself.
        reset();
        const env2 = panel(new Map([["agent", "a"]]));
        const root2 = fakeRoot(at.agentsTab(env2));
        at.paintAgentList(root2, env2);
        const load2 = root2.iframe.listeners.find((item) => item.type === "load").fn;
        load2(); out.removedFirst = root2.iframe.removed; load2(); out.removedSecond = root2.iframe.removed;
        """,
        tmp_path,
    )
    assert out["loads"] == 1
    assert out["afterFirst"] == {"redraws": 0, "drift": None}
    assert out["afterSecond"] == {"redraws": 1} and out["driftInRedraw"] == "a"
    assert "<iframe" not in out["redrawn"] and 'data-code="orca-agent-drift"' in out["redrawn"]
    assert out["removedFirst"] is False and out["removedSecond"] is True


# --- T-06: the screens ------------------------------------------------------------------------------------------


def test_the_panel_shows_the_visible_tabs_paints_the_strip_and_follows_the_summaries() -> None:
    panel = (SHARED / "panel.js").read_text(encoding="utf-8")
    assert "shown = visibleTabs(first);" in panel
    assert "tab = pickTab(userTab, shown.map((item) => item.key), state.doc.details);" in panel
    assert 'if (env && tab === "agents") paintAgentList(parts.body, env, { redraw });' in panel
    assert "followed.subscribe(redraw)" in panel and "follow(ctx.orca);" in panel
    for name in ("hide()", "destroy()"):
        body = panel[panel.index(f"    {name} {{") :]
        assert body[: body.index("\n    },")].count("follow(null);") == 1, name


def test_the_shell_gives_the_problem_the_quiet_query_and_redraws_on_the_theme() -> None:
    app = (ASSETS / "app.js").read_text(encoding="utf-8")
    assert "orcaProblem: state.server?.orca_web?.problem ?? null," in app
    assert "ctx.replaceParam = (name, value) => replaceParam(name, value, ctx.route);" in app
    body = app[app.index("function replaceParam(") :]
    body = body[: body.index("\n}\n")]
    assert 'history.replaceState(null, "", path);' in body and "withParam(state.route.path, name, value)" in body
    assert "render(" not in body and "navigated" not in body and "pushState" not in body
    assert 'matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);' in app
    theme = app[app.index("function setTheme(") :]
    assert "if (booted) render();" in theme[: theme.index("\n}\n")]
    assert app.index("booted = true;") < app.index('addEventListener("change", render)')


def _rules(css: str, selector: str) -> list[str]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [m.group(2) for m in re.finditer(r"([^{};]+)\{([^{}]*)\}", css) if m.group(1).strip() == selector]


def test_the_agent_frame_takes_the_rest_of_the_height_with_the_existing_tokens() -> None:
    shared = (SHARED / "scope_tabs.css").read_text(encoding="utf-8")
    panel = (SHARED / "panel.css").read_text(encoding="utf-8")
    page = (VIEWS / "scope.css").read_text(encoding="utf-8")
    assert _rules(shared, "& :is(.sd-docframe, .sd-explain, .sd-agent)")
    strip = _rules(shared, "& .sd-agents")[0]
    for word in ("display: flex", "min-width: 0", "overflow-x: auto", "white-space: nowrap"):
        assert word in strip, word
    assert "flex-wrap" not in strip
    current = _rules(shared, '& .sd-agentpick[aria-current="true"]')[0]
    assert current == _rules(shared, '& .sd-seg > [aria-current="true"]')[0]  # the same words as the doc switch
    body = _rules(panel, '.sd-pn .pn-body:is([data-tab="docs"], [data-tab="explanation"], [data-tab="agents"])')
    assert len(body) == 2 and "flex-direction: column" in body[0] and "padding: 2px 4px 4px" in body[1]
    frame = _rules(panel, ".sd-pn :is(.sd-docframe, .sd-explain, .sd-agent)")[0]
    assert "flex: 1" in frame and "min-height: 240px" in frame and "height: auto" in frame
    on_page = _rules(page, "& :is(.sd-docframe, .sd-explain, .sd-agent)")[0]
    assert "flex: none" in on_page and "100dvh" in on_page
    assert _rules(page, "& .sd-scope-top") == [" display: contents; "]
    for css in (shared, panel, page):
        assert not re.search(r"#[0-9a-fA-F]{3}|rgba?\(|hsla?\(", css)  # no new colors


# The detail screen with a fake root: three parts, the contents left alone, another Scope drawn anew.
SCREEN = """
const screen = (await import(SCOPE_VIEW)).default;
function part(cls) {
  const el = {cls, dataset: {}, writes: 0, html: "", listeners: []};
  Object.defineProperty(el, "innerHTML", {get: () => el.html, set(value) { el.html = value; el.writes++; el.inner = innerOf(value); }});
  el.querySelector = (sel) => el.inner?.querySelector(sel) ?? null;
  return el;
}
function innerOf(html) {
  const r = fakeRoot(html);
  return r.strip || r.box || r.iframe ? r : null;
}
function fakePage(html) {
  const scopeId = html.match(/<div class="sd-page" data-scope="([^"]*)"/)?.[1];
  const parts = Object.fromEntries(["sd-scope-top", "sd-tabs-row", "sd-tabpanel"].map((cls) => [cls, html.includes(`class="${cls}"`) ? part(cls) : null]));
  if (parts["sd-tabpanel"]) parts["sd-tabpanel"].dataset.tab = html.match(/data-tab="([^"]*)"/)?.[1];
  return {dataset: scopeId ? {scope: scopeId} : {}, parts, querySelector: (sel) => parts[sel.slice(1)] ?? null};
}
function screenRoot() {
  const root = {writes: 0, isConnected: true, html: ""};
  Object.defineProperty(root, "innerHTML", {get: () => root.html, set(value) { root.html = value; root.writes++; root.page = fakePage(value); }});
  root.querySelector = (sel) => (sel === ".sd-page" ? root.page ?? null : null);
  return root;
}
const subs = [];
orca.subscribe = (fn) => { subs.push(fn); return () => { subs.splice(subs.indexOf(fn), 1); }; };
const screenCtx = (query, which = scope) => ({...pageCtx(query), scope: which === scope ? doc : otherDoc, route: {...pageCtx(query).route, scope: which.id, path: which.path + "?" + query}});
"""


@node
def test_the_detail_screen_keeps_its_contents_and_draws_another_scope_anew(tmp_path: Path) -> None:
    out = _run(
        SCREEN.replace("SCOPE_VIEW", json.dumps((VIEWS / "scope.js").as_uri()))
        + """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const root = screenRoot();
        screen.render(root, screenCtx("tab=agents&agent=a"));
        const first = root.page;
        const panelPart = first.parts["sd-tabpanel"];
        out.first = {root: root.writes, panel: panelPart.writes, tab: panelPart.dataset.tab, scope: first.dataset.scope};
        out.strip = panelPart.inner.strip.innerHTML.includes('data-orca-agent="a"');
        out.load = panelPart.inner.iframe.listeners.filter((item) => item.type === "load").length;
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        screen.render(root, screenCtx("tab=agents&agent=a"));
        out.same = {root: root.writes, panel: panelPart.writes, page: root.page === first};
        out.subscribed = subs.length;
        subs[0]();
        out.notified = {root: root.writes, panel: panelPart.writes};
        screen.render(root, screenCtx("tab=summary&agent=a"));
        out.summary = {panel: panelPart.writes, tab: panelPart.dataset.tab, hasAgents: first.parts["sd-tabs-row"].html.includes("エージェント")};
        screen.render(root, screenCtx("tab=agents", other));
        out.other = {root: root.writes, scope: root.page.dataset.scope, frame: root.page.parts["sd-tabpanel"].html.includes("<iframe")};
        screen.dispose();
        out.disposed = subs.length;
        """,
        tmp_path,
    )
    assert out["first"] == {"root": 1, "panel": 1, "tab": "agents", "scope": "iss-00001"}
    assert out["strip"] and out["load"] == 1
    assert out["same"] == {"root": 1, "panel": 1, "page": True}  # another agent joined: the frame stays
    assert out["subscribed"] == 1 and out["notified"] == {"root": 1, "panel": 1}
    assert out["summary"]["panel"] == 2 and out["summary"]["tab"] == "summary" and out["summary"]["hasAgents"]
    assert out["other"]["root"] == 2 and out["other"]["scope"] == "iss-00002" and out["other"]["frame"] is False
    assert out["disposed"] == 0


def test_the_detail_screen_is_split_into_three_parts() -> None:
    scope = (VIEWS / "scope.js").read_text(encoding="utf-8")
    assert '<div class="sd-page" data-scope="${esc(scope.id)}"><div class="sd-scope-top"></div>' in scope
    assert (
        '<div class="sd-tabs-row"></div><div class="sd-tabpanel" role="tabpanel" data-tab="${tab}"></div></div>'
        in scope
    )
    assert 'if (tab === "agents") paintAgentList(panel, env, { redraw });' in scope
    assert "dispose,\n};" in scope and "function dispose() {" in scope
    assert scope.index(".render(env);") < scope.index("const path = ctx.route.path;")  # keep runs before the links


@node
def test_the_strip_scrolls_the_chosen_item_into_view_only_when_needed(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        // A strip 200px wide; each item is 100px, placed by its index in the strip's content minus scrollLeft.
        function scrollingRoot(html) {
          const root = fakeRoot(html);
          const strip = root.strip;
          strip.scrollLeft = 0;
          strip.getBoundingClientRect = () => ({left: 0, right: 200});
          strip.querySelectorAll = (sel) => (sel === "[data-orca-agent]" ? strip.slots : []);
          strip.querySelector = (sel) => {
            if (sel !== '[aria-current="true"]') return null;
            const items = [...strip.innerHTML.matchAll(/<(a|span) class="sd-agentpick"([^>]*)>/g)];
            const index = items.findIndex((m) => m[2].includes('aria-current="true"'));
            if (index < 0) return null;
            return {getBoundingClientRect: () => ({left: index * 100 - strip.scrollLeft, right: index * 100 + 100 - strip.scrollLeft})};
          };
          return root;
        }
        const scrolled = (strip) => { for (const l of strip.listeners.filter((l) => l.type === "scroll")) l.fn(); };
        const agents = ["a", "b", "c", "d", "e"].map((id) => raw(id));
        world.trees[sid] = [tree("w1", "one", agents)];
        const paint = (root, wanted) => { const env = panel(new Map([["agent", wanted]])); at.agentsTab(env); at.paintAgentList(root, env); };
        const root = scrollingRoot(at.agentsTab(panel(new Map([["agent", "d"]]))));
        paint(root, "d");
        out.toD = root.strip.scrollLeft; // d spans 300..400: the strip moves right by 200
        scrolled(root.strip); // the strip's own scroll event: still following
        paint(root, "d");
        out.again = root.strip.scrollLeft; // already in view: unchanged
        root.strip.scrollLeft = 0; // the person moves the strip back
        scrolled(root.strip);
        paint(root, "d");
        out.afterPerson = root.strip.scrollLeft; // the same choice on the next summary: left alone
        paint(root, "a");
        out.toA = root.strip.scrollLeft; // a new choice follows again; a spans 0..100: visible, unchanged
        root.strip.scrollLeft = 300;
        scrolled(root.strip);
        paint(root, "b");
        out.toB = root.strip.scrollLeft; // b spans 100..200, seen at -200..-100: the strip moves left to 100
        paint(root, "c");
        out.toC = root.strip.scrollLeft; // c spans 200..300, seen at 100..200: visible, unchanged
        // No chosen item (gone, or nothing chosen): nothing moves.
        reset();
        const none = scrollingRoot(at.agentsTab(panel(new Map())));
        none.strip.scrollLeft = 50;
        at.paintAgentList(none, panel(new Map()));
        out.none = none.strip.scrollLeft;
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["toD"] == 200 and out["again"] == 200 and out["afterPerson"] == 0
    assert out["toA"] == 0 and out["toB"] == 100 and out["toC"] == 100
    assert out["none"] == 50


@node
def test_the_strip_follows_late_layout_until_the_person_moves_it(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        const observers = [];
        globalThis.ResizeObserver = class { constructor(fn) { this.fn = fn; this.seen = new Set(); observers.push(this); } observe(el) { this.seen.add(el); } unobserve(el) { this.seen.delete(el); } };
        // The chosen item starts inside the strip (no CSS yet, no marks) and moves or widens later.
        let itemRight = 150;
        const root = fakeRoot('<div class="sd-framebox" data-frame="agents"><div class="sd-agents" data-orca-agents="x"></div></div>');
        const strip = root.strip;
        strip.scrollLeft = 0;
        strip.getBoundingClientRect = () => ({left: 0, right: 200});
        const item = {getBoundingClientRect: () => ({left: itemRight - 100 - strip.scrollLeft, right: itemRight - strip.scrollLeft})};
        strip.querySelector = (sel) => (sel === '[aria-current="true"]' ? item : null);
        const scrolled = () => { for (const l of strip.listeners.filter((l) => l.type === "scroll")) l.fn(); };
        let label = "now";
        world.marks = {buildMarks: () => [label], renderAgentMarks: () => { itemRight = label === "now" ? 260 : 380; }}; // the marks widen the items
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        const draw = () => { const env = panel(new Map([["agent", "b"]])); at.agentsTab(env); at.paintAgentList(root, env); };
        draw();
        out.afterMarks = strip.scrollLeft; // revealed after the marks: 260 - 200
        out.observed = observers.length === 1 && observers[0].seen.has(strip) && observers[0].seen.has(item);
        itemRight = 330; // a stylesheet or a font arrives later
        observers[0].fn();
        out.afterLayout = strip.scrollLeft;
        scrolled(); // the strip's own scroll: still following
        label = "31m"; // the next summary redraws an earlier item's mark: the chosen item moves right
        draw();
        out.afterRedraw = strip.scrollLeft; // 380 - 200, though the choice did not change
        strip.scrollLeft = 0; // the person moves the strip
        scrolled();
        itemRight = 400;
        observers[0].fn();
        out.afterPerson = strip.scrollLeft;
        label = "32m";
        draw();
        out.sameChoice = strip.scrollLeft; // the next summary with the same choice leaves it alone
        out.observerCount = observers.length;
        out.unknownTypes = strip.listeners.filter((l) => ["wheel", "pointerdown", "touchstart", "keydown"].includes(l.type)).length;
        delete globalThis.ResizeObserver;
        world.marks = null;
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["afterMarks"] == 60 and out["observed"]
    assert out["afterLayout"] == 130 and out["afterRedraw"] == 180
    assert out["afterPerson"] == 0 and out["sameChoice"] == 0 and out["observerCount"] == 1
    assert out["unknownTypes"] == 0


# --- The final quality gate, attempt 1 (FQG-001, FQG-002 and the second opinion's P1 and P2) ---------------------


@node
def test_a_loss_is_noted_only_when_the_match_is_known(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        // The worktree records cannot be read: no tab, and no loss either.
        const unread = {...structure, worktrees: {status: "unreadable", paths: []}};
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        const blind = panel(new Map([["agent", "a"]]), {data: unread});
        out.blind = at.agentsState(blind).show;
        out.blindGone = [...at.mem.gone];
        // Every entry is out of shape: a shape notice, and no loss.
        world.trees[sid] = [tree("w1", "one", [{id: "b", detail: "x"}])];
        const broken = at.agentsState(panel(new Map([["agent", "a"]])));
        out.broken = broken.reason;
        out.brokenGone = [...at.mem.gone];
        // A known match without a: a loss.
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        at.agentsState(panel(new Map([["agent", "a"]])));
        out.known = [...at.mem.gone];
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["blind"] is False and out["blindGone"] == []
    assert out["broken"] == "shape" and out["brokenGone"] == []
    assert out["known"] == ["a"]


@node
def test_an_env_without_a_choice_uses_the_last_shown_agent(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        // The person picks a in the panel: its frame is placed and remembered as the last one.
        logic.forgetGone(logic.memoryFor(at.mem, sid), "a");
        at.agentsTab(panel(new Map([["agent", "a"]])));
        out.last = at.mem.last;
        // The panel closes (its Map is empty) and opens again: a, not "choose".
        out.reopened = at.agentsTab(panel(new Map()));
        // The page without agent= opens a too.
        out.page = at.agentsTab(page("tab=agents"));
        // While the panel is closed, a goes away and b is left alone: reopening does not open b by itself.
        world.trees[sid] = [tree("w1", "one", [raw("b")])];
        const params = new Map();
        const again = counting(panel(params));
        out.gone = at.agentsTab(again);
        out.kept = again.kept;
        // An automatic choice is remembered as the last one too.
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("c")])];
        at.agentsTab(panel(new Map()));
        out.autoLast = at.mem.last;
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["last"] == "a"
    assert "id=a&amp;theme=light" in out["reopened"] and "id=a&amp;theme=light" in out["page"]
    assert "<iframe" not in out["gone"] and 'data-code="orca-agent-gone"' in out["gone"]
    assert out["kept"] == [["agent", "gone:a"]]
    assert out["autoLast"] == "c"


@node
def test_a_summary_during_a_move_never_writes_a_choice_from_the_old_route(tmp_path: Path) -> None:
    out = _run(
        SCREEN.replace("SCOPE_VIEW", json.dumps((VIEWS / "scope.js").as_uri()))
        + """
        reset();
        // A model of the shell: one current route, a move that waits for the Scope, current() and replaceParam.
        const app = {route: null, moving: 0};
        const shellCtx = () => {
          const ctx = {...pageCtx(""), scope: doc, route: app.route};
          ctx.replaceParam = (name, value) => {
            if (ctx.route.path !== app.route.path) return app.route; // decided on a route that is gone
            const url = new URL(app.route.path, "http://x");
            url.searchParams.set(name, value);
            app.route = {...app.route, path: url.pathname + "?" + url.searchParams.toString(), params: url.searchParams};
            return app.route;
          };
          ctx.current = () => (app.moving ? null : shellCtx());
          return ctx;
        };
        const routeOf = (query) => ({scope: sid, path: scope.path + "?" + query, params: new URLSearchParams(query)});
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        app.route = routeOf("tab=agents");
        const root = screenRoot();
        screen.render(root, shellCtx()); // two agents: "choose"
        out.choose = root.page.parts["sd-tabpanel"].html.includes('data-code="orca-agent-choose"');
        // The person presses b; the shell sets the new route and waits for the Scope's JSON.
        app.route = routeOf("tab=agents&agent=b");
        app.moving++;
        world.trees[sid] = [tree("w1", "one", [raw("a")])]; // meanwhile b goes away and a is left alone
        subs[0](); // a summary arrives during the move
        out.duringMove = {route: app.route.path, frame: root.page.parts["sd-tabpanel"].html.includes("<iframe")};
        app.moving--;
        screen.render(root, shellCtx()); // the move ends
        out.afterMove = {route: app.route.path, html: root.page.parts["sd-tabpanel"].html};
        subs[0](); // a later summary draws from the shell's current route
        out.later = app.route.path;
        // replaceParam refuses a value decided on a route that is no longer current.
        const stale = shellCtx();
        stale.route = routeOf("tab=agents");
        tabs.pageEnv(stale, scope, doc, byId).keep("agent", "a");
        out.refused = {route: app.route.path, envRoute: stale.route.path};
        screen.dispose();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    b = "/r/github.com/o/r/scopes/iss-00001?tab=agents&agent=b"
    gone = "/r/github.com/o/r/scopes/iss-00001?tab=agents&agent=gone%3Ab"
    assert out["choose"]
    assert out["duringMove"] == {"route": b, "frame": False}
    assert out["afterMove"]["route"] == gone
    assert "<iframe" not in out["afterMove"]["html"] and 'data-code="orca-agent-gone"' in out["afterMove"]["html"]
    assert out["later"] == gone
    assert out["refused"] == {"route": gone, "envRoute": gone}  # nothing written; the env reads the current route


@node
def test_a_dropped_frame_is_placed_again_on_the_next_drawing(tmp_path: Path) -> None:
    out = _run(
        SCREEN.replace("SCOPE_VIEW", json.dumps((VIEWS / "scope.js").as_uri()))
        + """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const root = screenRoot();
        screen.render(root, screenCtx("tab=agents&agent=a"));
        const panelPart = root.page.parts["sd-tabpanel"];
        out.first = panelPart.writes;
        screen.render(root, screenCtx("tab=agents&agent=a"));
        out.same = panelPart.writes; // the same string: left alone
        panelPart.dataset.dropped = "1"; // the shell removed the frame before a move
        screen.render(root, screenCtx("tab=agents&agent=a"));
        out.redrawn = {writes: panelPart.writes, flag: panelPart.dataset.dropped ?? null, frame: panelPart.html.includes("<iframe")};
        screen.dispose();
        """,
        tmp_path,
    )
    assert out["first"] == 1 and out["same"] == 1
    assert out["redrawn"] == {"writes": 2, "flag": None, "frame": True}


def test_the_shell_moves_without_leaving_a_frame_and_redraws_from_the_current_state() -> None:
    app = (ASSETS / "app.js").read_text(encoding="utf-8")
    move = app[app.index("async function navigate(") :]
    move = move[: move.index("\n}\n")]
    assert "const before = state.route;" in move and "state.route = target;" in move
    changed = 'target.scope !== before.scope || target.params.get("agent") !== before.params.get("agent")'
    assert f"if ({changed}) dropAgentFrames();" in move
    assert move.index("dropAgentFrames();") < move.index("await api.scope(")
    assert "state.moving += 1;" in move and "state.moving -= 1;" in move
    assert move.index("state.moving += 1;") < move.index("await api.scope(") < move.index("state.moving -= 1;")
    early = move[move.index("if (sameScope) render();") :]
    assert early.index("render();") < early.index("await api.scope(")
    drop = app[app.index("function dropAgentFrames(") :]
    drop = drop[: drop.index("\n}\n")]
    assert (
        'root.querySelectorAll("iframe.sd-agent")' in drop
        and '.dataset.dropped = "1";' in drop
        and "frame.remove();" in drop
    )
    assert "current: () => (state.moving ? null : viewCtx())," in app
    body = app[app.index("function replaceParam(") :]
    body = body[: body.index("\n}\n")]
    assert "if (from && from.path !== state.route.path) return state.route;" in body
    scope = (VIEWS / "scope.js").read_text(encoding="utf-8")
    assert "last.ctx.current ? last.ctx.current() : last.ctx" in scope and "panel.dataset.dropped" in scope
    panel = (SHARED / "panel.js").read_text(encoding="utf-8")
    assert "current.ctx.current" in panel and "parts.body.dataset.dropped" in panel


@node
def test_the_marks_compare_and_draw_with_the_same_now(tmp_path: Path) -> None:
    out = _run(
        """
        reset();
        let clock = 1_000_000;
        Date.now = () => clock;
        const seen = {build: [], render: []};
        world.marks = {
          buildMarks: (doc, options) => { seen.build.push(options); return {marks: [{mark: doc.agents[0].mark, elapsed: Math.floor((options.now ?? 0) / 60000)}]}; },
          renderAgentMarks: (slot, doc, options) => { seen.render.push(options); },
        };
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        const draw = (root) => { const env = panel(new Map([["agent", "a"]])); const html = at.agentsTab(env); root = root ?? fakeRoot(html); at.paintAgentList(root, env); return root; };
        const root = draw();
        draw(root); // the same minute: no new drawing
        out.sameMinute = seen.render.length;
        clock += 60_000; // a minute later the elapsed time changes though the state does not
        draw(root);
        out.nextMinute = seen.render.length;
        out.options = {build: seen.build.at(-1), render: seen.render.at(-1)};
        world.marks = null;
        """,
        tmp_path,
    )
    assert out["sameMinute"] == 1 and out["nextMinute"] == 2
    assert out["options"]["build"] == {"max": 1, "now": 1_060_000}
    assert out["options"]["render"] == {"size": "sm", "max": 1, "now": 1_060_000}


# --- With iss-00592 in the same panel (the merge of origin/main) ------------------------------------------------

PANEL = """
const PARTS = [".pn-grab", ".pn-top", ".pn-tabs", ".pn-body", ".pn-foot", ".pn-hl", ".pn-orca", ".pn-cover"];
class El {
  constructor(name) { this.name = name; this.dataset = {}; this.children = []; this.writes = 0; this.html = ""; this.scrollTop = 0; }
  set innerHTML(value) { this.html = value; this.writes++; }
  get innerHTML() { return this.html; }
  replaceChildren(...children) { this.children = children; }
  append(child) { this.children.push(child); }
  querySelector() { return null; }
  querySelectorAll() { return []; }
}
globalThis.window = {addEventListener() {}, removeEventListener() {}};
globalThis.innerHeight = 800;
globalThis.matchMedia = () => ({matches: dark, addEventListener() {}, removeEventListener() {}});
globalThis.document.createElement = (tag) => ({tag, dataset: {}});
globalThis.document.documentElement.clientWidth = 1440;
const aside = {
  classList: {add() {}, remove() {}}, dataset: {}, style: {setProperty() {}, removeProperty() {}},
  setAttribute() {}, addEventListener(type, fn) { if (type === "click") this.click = fn; }, closest() { return null; },
  set innerHTML(value) { this.parts = new Map(PARTS.map((s) => [s, new El(s)])); },
  querySelector(sel) { return this.parts?.get(sel) ?? null; },
  contains(el) { return [...(this.parts?.values() ?? [])].includes(el); },
};
const panelModule = await import(PANEL_URL);
const subs2 = [];
orca.subscribe = (fn) => { subs2.push(fn); return () => subs2.splice(subs2.indexOf(fn), 1); };
const pn = panelModule.createScopePanel(aside);
const part = (sel) => aside.querySelector(sel);
const selected = () => (part(".pn-tabs").innerHTML.match(/data-pn-tab="([a-z]+)" aria-selected="true"/) || [])[1] ?? null;
const showIt = () => pn.show({ctx: panelCtx(), scope, doc, docState: "ok", byId});
"""


@node
def test_prefer_tab_and_a_doubled_redraw_in_the_panel_with_the_orca_heading(tmp_path: Path) -> None:
    out = _run(
        PANEL.replace("PANEL_URL", json.dumps((SHARED / "panel.js").as_uri()))
        + """
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        showIt();
        pn.preferTab("agents");
        out.withAgents = selected();
        const body = part(".pn-body");
        out.frame = body.innerHTML.includes("<iframe");
        const writes = body.writes;
        // The same news twice: the panel's own subscription, then the screen's refreshOrca (iss-00592) and show.
        subs2[0]();
        pn.refreshOrca();
        showIt();
        subs2[0]();
        out.rewrites = body.writes - writes;
        // No agents and no choice (the panel closed, a fresh memory): the tab does not show, and the preferred
        // agents falls back to the default tab.
        pn.hide();
        world.trees[sid] = [];
        reset();
        showIt();
        pn.preferTab("agents");
        out.withoutAgents = selected();
        out.tabs = [...part(".pn-tabs").innerHTML.matchAll(/data-pn-tab="([a-z]+)"/g)].map((m) => m[1]);
        pn.hide();
        out.subscribed = subs2.length;
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    assert out["withAgents"] == "agents" and out["frame"] is True
    assert out["rewrites"] == 0  # the frame stays
    assert out["withoutAgents"] == "summary" and "agents" not in out["tabs"]
    assert out["subscribed"] == 0


@node
def test_the_panel_foot_links_carry_the_panel_choice(tmp_path: Path) -> None:  # FQG attempt 2, ChatGPT P1
    out = _run(
        PANEL.replace("PANEL_URL", json.dumps((SHARED / "panel.js").as_uri()))
        + """
        const hrefs = () => [...part(".pn-foot").innerHTML.matchAll(/<a class="ds-btn[^"]*"( data-nav)? href="([^"]*)"/g)].map((m) => m[2]).slice(0, 2);
        reset();
        world.trees[sid] = [tree("w1", "one", [raw("a"), raw("b")])];
        showIt();
        out.none = hrefs(); // two agents and no choice yet
        pn.preferTab("agents");
        out.noChoice = hrefs();
        aside.click({target: {closest: (sel) => (sel === "a[data-pn-param]" ? {dataset: {pnParam: "agent", pnValue: "a"}} : null)}, button: 0, preventDefault() {}});
        out.chosen = hrefs();
        world.trees[sid] = [tree("w1", "one", [raw("b")])]; // a goes away; b is left alone
        showIt();
        out.gone = hrefs();
        pn.hide();
        world.trees[sid] = [tree("w1", "one", [raw("a")])];
        """,
        tmp_path,
    )
    base = "/r/github.com/o/r/scopes/iss-00001"
    assert out["none"] == [f"{base}?tab=summary"] * 2
    assert out["noChoice"] == [f"{base}?tab=agents"] * 2
    assert out["chosen"] == [f"{base}?agent=a&amp;tab=agents"] * 2
    assert out["gone"] == [f"{base}?agent=gone%3Aa&amp;tab=agents"] * 2
