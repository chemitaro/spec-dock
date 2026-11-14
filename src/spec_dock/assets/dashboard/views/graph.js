// The structure graph, the home screen (iss-00532; Epic R-15, D-08). The adopted design d2's look and behaviour:
// Initiatives and Epics as frames holding Issue boxes (or a tree of boxes), dependency lines routed around every
// box, the state chips above that only highlight, the folded cleanup candidates, the selection that highlights the
// upstream and downstream, the summary panel, zoom and pan with two-finger pinch.
//
// The model decides every state, order, stage and path (#528, through the structure and scope APIs). This module
// only places (graph/layout.js), routes (graph/router.js) and draws.
import * as api from "../core/api.js";
import { DEFAULTS, index, routeLayout } from "./graph/layout.js";
import { audit, svg as edgeSvg } from "./graph/router.js";
import * as M from "./graph/marks.js";
import { LEGACY_KEY, PREFS_KEY, restorePrefs } from "./graph/prefs.js";
import { createScopePanel } from "./_shared/panel.js";

const { esc, ic, stateIcon, STATES } = M;
const PHONE = 640;
const RESIZE_SETTLE = 200; // ms the window's size must hold before the graph is laid out again (iss-00575)
// Why there is no graph (F-01). The reason and the next step are in the shell's notices above.
export function emptyText(data) {
  if (!data) return "このリポジトリの構造を読めませんでした。";
  if (data.snapshot?.status !== "ok") return "構造のスナップショットがないか読めないため、図を描けません。上の知らせを見てください。";
  return "このリポジトリには、まだ Scope がありません。";
}

// The board's lane order (Epic R-13): blocked, ready, doing, awaiting merge (needs fix, mergeable), unknown.
const HL = [
  ["blocked", "blocked", "止められている"],
  ["ready", "ready", "着手できる"],
  ["doing", "doing", "作業中"],
  ["fix", "merge", "直す必要あり"],
  ["ok", "merge", "マージできる"],
  ["unknown", "unknown", "不明"],
];

const V = {
  opts: { ...DEFAULTS },
  hl: null, // the state chip pressed (blocked, ready, doing, fix, ok, unknown)
  sel: null, // the selected Scope ID
  path: null, // {up, down, roots, related} from the scope API for `sel`
  token: 0, // the latest selection; an older answer is dropped
  docState: "loading", // the scope API answer for `sel`: loading, ok or failed (iss-00587 F-01)
  docRevision: null, // the structure revision `path.doc` was read at; a new one reads it again (R-08)
  pn: null, // the shared Scope panel
  legend: false,
  cleanup: false, // the panel shows the cleanup list
  s: 1,
  tx: 0,
  ty: 0,
  fitted: false,
  sig: null,
  width: 0, // the visible width at 100% the graph was last laid out for (iss-00560 R-03)
  EG: null, // the last routing: {layout, G, routes, widen, iters, unmapped, ms}
  ctx: null,
  root: null,
  el: null,
  data: null,
  ix: null,
  desc: null,
  lastTap: null,
};

// The saved choices (iss-00556 D-05): version 2, with only some of version 1 carried over (graph/prefs.js).
function loadPrefs() {
  const read = (key) => {
    try {
      const raw = localStorage.getItem(key);
      return raw == null ? null : JSON.parse(raw);
    } catch {
      return null; // private windows, blocked storage and broken values: the defaults
    }
  };
  const { opts, legend } = restorePrefs(read(PREFS_KEY), read(LEGACY_KEY), DEFAULTS);
  Object.assign(V.opts, opts);
  V.legend = legend;
}
function savePrefs() {
  try {
    const { mode, showDone, deps, fold } = V.opts; // the focus lives in the URL, not in the preferences
    localStorage.setItem(PREFS_KEY, JSON.stringify({ mode, showDone, deps, fold, legend: V.legend }));
  } catch {
    // ignore
  }
}

const isPhone = () => (V.root?.clientWidth || innerWidth) <= PHONE;
// The graph's visible width at 100% (px), where the groups of the layout wrap (iss-00560 D-05): the same 16px of
// margin as the first view and "fit".
const seenWidth = () => Math.max(1, (V.el?.view.clientWidth || innerWidth) - 16);
// The visible height with the same margin, kept as a resize signal (placement uses width only, iss-00583).
// Leave out the toolbar's changing height so that selecting a Scope keeps the layout.
const seenHeight = () => Math.max(1, (V.el?.view.clientHeight || innerHeight) - 16);
const byId = (id) => V.ix?.byId.get(id);

// --- Shell DOM ---------------------------------------------------------------------------------------------

function mount(root) {
  loadPrefs();
  root.innerHTML =
    `<section class="gx" aria-label="構造の図">` +
    `<div class="gx-view" tabindex="0" aria-label="構造の図。ドラッグで移動、Ctrl とホイールか2本指で拡大・縮小"><div class="gx-world"></div></div>` +
    `<div class="gx-bar"><div class="gx-left"><div class="gx-crumbs" hidden></div><div class="gx-next" role="group" aria-label="状態で目立たせる"></div></div><div class="gx-tools"></div></div>` +
    `<div class="legend"></div>` +
    `<aside class="panel" aria-hidden="true" aria-label="Scope の欄"></aside>` +
    `<p class="gx-empty" hidden></p>` +
    `</section>`;
  const q = (sel) => root.querySelector(sel);
  V.root = root;
  V.el = {
    gx: q(".gx"),
    view: q(".gx-view"),
    world: q(".gx-world"),
    bar: q(".gx-bar"),
    crumbs: q(".gx-crumbs"),
    next: q(".gx-next"),
    tools: q(".gx-tools"),
    legend: q(".legend"),
    panel: q(".panel"),
    empty: q(".gx-empty"),
  };
  V.pn = createScopePanel(V.el.panel, {
    onSelect: (id) => {
      select(id);
      centerOn(id);
    },
    onClose: () => select(null),
    extraActions: (s) => (frameOf(s) ? `<button type="button" class="ds-btn" data-act="focus" data-focus="${esc(s.id)}">${ic("target")}この範囲に絞る</button>` : ""),
  });
  bindView();
  V.el.gx.addEventListener("click", onClick);
  document.addEventListener("keydown", onKey);
  for (const type of ["gesturestart", "gesturechange", "gestureend"]) document.addEventListener(type, stopGesture, { passive: false });
  window.addEventListener("resize", onResize);
}

function dispose() {
  document.removeEventListener("keydown", onKey);
  for (const type of ["gesturestart", "gesturechange", "gestureend"]) document.removeEventListener(type, stopGesture, { passive: false });
  window.removeEventListener("resize", onResize);
  if (window.specdockEdgeAudit === edgeAudit) delete window.specdockEdgeAudit;
  V.token++; // an answer of the scope API that arrives after leaving the screen is dropped
  V.root = null;
  V.el = null;
  V.sig = null;
  V.fitted = false;
  V.sel = null;
  V.path = null;
  V.docState = "loading";
  V.docRevision = null;
  V.pn = null;
}

// Safari zooms the whole page on a pinch unless its gesture events are cancelled (#527 P-5).
function stopGesture(event) {
  if (event.cancelable) event.preventDefault();
}

// --- Render ------------------------------------------------------------------------------------------------

function render(root, ctx) {
  if (V.root !== root || !root.querySelector(".gx")) mount(root);
  V.ctx = ctx;
  window.specdockEdgeAudit = edgeAudit;
  const data = ctx.data;
  const focus = ctx.route.params.get("focus") || null;
  if (!data || !Array.isArray(data.scopes) || !data.scopes.length) {
    showEmpty(emptyText(data));
    return;
  }
  V.el.empty.hidden = true;
  V.el.view.hidden = false;
  V.el.bar.hidden = false;
  if (V.data !== data) {
    V.data = data;
    V.ix = index(data.scopes);
    V.desc = descendants(V.ix);
  }
  if (V.sel && !byId(V.sel)) select(null);
  else if (V.sel && V.docRevision !== data.revision) loadSelected(V.sel, { keep: true });
  // The Scopes moving now key the world too: past their 30 minutes the boxes are drawn again, still (iss-00574 D-04).
  const now = Date.now();
  const live = data.scopes.filter((s) => s.state === "doing" && M.isLive(M.movedAt(s, V.ix.byId), now)).map((s) => s.id);
  const sig = `${data.revision}|${JSON.stringify(V.opts)}|${focus}|${live.join(",")}|${seenWidth()}|${seenHeight()}`;
  renderBar(focus);
  renderLegend();
  if (sig !== V.sig) {
    V.sig = sig;
    buildWorld(focus);
    if (!V.fitted) {
      V.fitted = true;
      whenStyled(() => {
        relayout(); // the screen's CSS can change the width the first layout used
        initialView();
        applyT();
      });
    }
    applyT();
  }
  paint();
  renderPanel();
}

// The screen's CSS loads once, after the first render: place the first view when it applies (or after 3s).
function whenStyled(done, started = performance.now()) {
  if (!V.el) return;
  const ready = getComputedStyle(V.el.gx).position === "absolute" && V.el.view.clientHeight > 0;
  if (ready || performance.now() - started > 3000) done();
  else requestAnimationFrame(() => whenStyled(done, started));
}

function showEmpty(text) {
  V.el.empty.textContent = text;
  V.el.empty.hidden = false;
  V.el.view.hidden = true;
  V.el.bar.hidden = true;
  V.el.panel.classList.remove("is-open");
}

function descendants(ix) {
  const memo = new Map();
  const walk = (id, seen = new Set()) => {
    if (memo.has(id)) return memo.get(id);
    seen.add(id);
    const out = [];
    for (const k of ix.kids.get(id) || []) {
      if (seen.has(k.id)) continue;
      out.push(k, ...walk(k.id, seen));
    }
    memo.set(id, out);
    return out;
  };
  return (id) => walk(id);
}

function tally(id) {
  const cnt = { done: 0, doing: 0, ready: 0, blocked: 0, unknown: 0 };
  const list = V.desc(id);
  for (const d of list) cnt[d.state] = (cnt[d.state] || 0) + 1;
  return { cnt, total: list.length };
}

const cleanupOf = () => new Map((V.data.cleanup || []).map((c) => [c.id, c]));

function maxOpenStage(parentId) {
  const kids = parentId ? V.ix.kids.get(parentId) || [] : V.data.scopes.filter((s) => !s.parent_id);
  return Math.max(1, ...kids.filter((k) => k.state !== "done").map((k) => k.stage?.open || 1));
}

// --- The world: frames, boxes, folded groups, tree lines and dependency lines ---------------------------------

function boxHtml(s, n) {
  const of = s.state !== "done" ? maxOpenStage(s.parent_id) : 1;
  const stg = of >= 2 ? M.stageMark(s.stage?.open, of) : "";
  const human = M.humanCount(s);
  const label = `${s.id} ${s.title}。${STATES[s.state]?.label ?? s.state}（${s.reason?.text ?? ""}）${s.downstream ? `。後に続く ${s.downstream}件` : ""}${human.count ? `。人のタスク ${human.count}件が止めている${human.descendants ? "（配下を含む）" : ""}` : ""}`;
  const frame = n.type === "tframe";
  let marks;
  if (frame) {
    const { cnt, total } = tally(s.id);
    marks = `<div class="gx-marks">${M.sbar(cnt, total, 64)}${M.frac(cnt, total)}${M.counts(cnt)}${M.asMark(s.assurance)}${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  } else {
    marks = `<div class="gx-marks">${M.asMark(s.assurance)}${M.prMark(s.pr)}${M.wtMark(s.state === "doing" ? s.branch : null)}${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  }
  return (
    `<div class="gx-box${frame ? " is-frame" : ""}" data-id="${esc(s.id)}" data-st="${s.state}" role="button" tabindex="0" aria-label="${esc(label)}" style="${pos(n)}">` +
    M.chgMark(s.change) +
    `<span class="rt" title="大もとの待ち先：ここが進めば、選んだ箱へ続く待ちがほどける" role="img" aria-label="大もとの待ち先">${ic("target")}大もと</span>` +
    `<div class="gx-r1">${M.stateMark(s, V.ix.byId, { motion: true })}<span class="gx-id">${esc(s.id)}</span><span class="gx-no">#${s.number}</span>${stg}</div>` +
    `<div class="gx-ttl${frame ? " is-one" : ""}" title="${esc(s.title)}">${esc(s.title)}</div>` +
    marks +
    `</div>`
  );
}

function frameHtml(s, n, cleanup) {
  const { cnt, total } = tally(s.id);
  const ini = s.kind === "initiative";
  const head =
    `<div class="gx-fh" data-id="${esc(s.id)}" role="button" tabindex="0" aria-label="${esc(`${s.id} ${s.title}。${STATES[s.state]?.label ?? s.state}`)}">${M.stateMark(s, V.ix.byId, { motion: true })}` +
    (ini ? `<span class="gx-kicker">Initiative</span>` : "") +
    `<span class="ds-docid">${esc(s.id)}</span><span class="gx-fttl" title="${esc(s.title)}">${esc(s.title)}</span></div>`;
  const meta =
    `<div class="gx-fm">${M.sbar(cnt, total, ini ? 150 : 84)}${M.frac(cnt, total)}${M.counts(cnt)}${M.asMark(s.assurance)}` +
    (cleanup.has(s.id) ? `<span class="cln" title="片付けの候補：${esc(cleanup.get(s.id).text)}" role="img" aria-label="片付けの候補">${ic("box")}</span>` : "") +
    `${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  return (
    `<section class="gx-frame ${ini ? "gx-ini" : "gx-epic"}${n.compact ? " is-compact" : ""}" data-id="${esc(s.id)}" data-st="${s.state}" style="${pos(n)}">` +
    M.chgMark(s.change) +
    `<span class="rt" title="大もとの待ち先" role="img" aria-label="大もとの待ち先">${ic("target")}大もと</span>` +
    head +
    meta +
    `</section>`
  );
}

function chipHtml(g) {
  const names = g.ids.map((id) => `${id} ${byId(id)?.title ?? ""}`).join("、");
  return (
    `<button type="button" class="gx-clean" data-clean="${esc(g.key)}" data-ids="${esc(g.ids.join(" "))}" style="${pos(g)}" title="片付けの候補：${esc(names)}" aria-label="片付けの候補 ${g.ids.length}件（押すと一覧）">` +
    `${ic("box")}<b>${g.ids.length}</b><span>片付けの候補</span></button>`
  );
}

const pos = (r) => `left:${r.x1}px;top:${r.y1}px;width:${r.x2 - r.x1}px;height:${r.y2 - r.y1}px`;

function buildWorld(focus) {
  const t0 = performance.now();
  V.width = seenWidth();
  V.height = seenHeight();
  const r = routeLayout(V.data.scopes, V.data.cleanup, { ...V.opts, focus, width: V.width, height: V.height });
  V.EG = { ...r, ms: Math.round(performance.now() - t0) };
  const L = r.layout;
  const cleanup = cleanupOf();
  const frames = L.nodes.filter((n) => n.type === "frame").map((n) => frameHtml(byId(n.id), n, cleanup));
  const boxes = L.nodes.filter((n) => n.type !== "frame").map((n) => boxHtml(byId(n.id), n));
  const chips = L.groups.map(chipHtml);
  const trunks = L.trunks
    .map((t) =>
      t.lane === "v"
        ? `<path d="M${(t.x1 + t.x2) / 2} ${t.y1}V${t.y2}"/>`
        : `<path d="M${t.x1} ${(t.y1 + t.y2) / 2}H${t.x2}"/>`,
    )
    .join("");
  const w = V.el.world;
  w.style.width = `${L.width}px`;
  w.style.height = `${L.height}px`;
  w.dataset.mode = L.opts.mode;
  w.innerHTML =
    (trunks ? `<svg class="gx-tree" width="${L.width}" height="${L.height}" aria-hidden="true">${trunks}</svg>` : "") +
    frames.join("") +
    boxes.join("") +
    chips.join("") +
    `<svg class="gx-edges" width="${L.width}" height="${L.height}" aria-hidden="true"></svg>`;
}

// --- Highlights: state chips and the selected path ---------------------------------------------------------

function inHl(s) {
  if (!V.hl) return true;
  if (V.hl === "ok") return s.merge === "mergeable";
  if (V.hl === "fix") return s.merge === "needs_fix";
  return s.lane === V.hl;
}

function edgeClass(e) {
  const base = e.done ? "is-done" : "is-wait";
  const P = V.path;
  if (!P) return base;
  let lv = 9;
  for (const [b, n] of e.pairs) {
    if ((n === V.sel && P.upDirect.has(b)) || (b === V.sel && P.downDirect.has(n))) lv = Math.min(lv, 1);
    else if (P.related.has(b) && P.related.has(n)) lv = Math.min(lv, 2);
  }
  return `${base}${lv === 1 ? " is-p1" : lv === 2 ? " is-p2" : " is-off"}`;
}

function paint() {
  if (!V.EG || !V.el) return;
  const { G, routes } = V.EG;
  const svg = V.el.world.querySelector(".gx-edges");
  const P = V.path;
  const selected = !!V.sel;
  if (svg) {
    svg.classList.toggle("is-hl", !!V.hl && !selected);
    svg.innerHTML = edgeSvg(G, routes, routes.map((rt) => edgeClass(G.edges[rt.ei])));
  }
  V.el.world.classList.toggle("has-path", selected);
  const sel = V.sel ? byId(V.sel) : null;
  const ancestors = sel ? new Set(V.ix.ancestors(sel.id)) : new Set();
  const inside = sel ? new Set(V.desc(sel.id).map((d) => d.id)) : new Set();
  for (const el of V.el.world.querySelectorAll(".gx-box, .gx-frame")) {
    const id = el.dataset.id;
    const s = byId(id);
    const issue = el.classList.contains("gx-box") && !el.classList.contains("is-frame");
    el.classList.toggle("is-sel", id === V.sel);
    el.classList.toggle("is-hl", !selected && !!V.hl && issue && inHl(s));
    el.classList.toggle("is-dim", !selected && !!V.hl && !(issue && inHl(s)));
    const related = !P || P.related.has(id) || ancestors.has(id) || inside.has(id) || id === V.sel;
    el.classList.toggle("is-poff", selected && !related);
    el.classList.toggle("is-root", !!P && P.roots.has(id));
  }
  for (const el of V.el.world.querySelectorAll(".gx-clean")) {
    const ids = el.dataset.ids.split(" ");
    el.classList.toggle("is-poff", selected && !!P && !ids.some((id) => P.related.has(id) || inside.has(id)));
    el.classList.toggle("is-dim", !selected && !!V.hl);
  }
  for (const b of V.el.next.querySelectorAll("[data-hl]")) b.setAttribute("aria-pressed", String(!selected && V.hl === b.dataset.hl));
}

async function select(id) {
  V.token++;
  V.sel = id;
  V.path = null;
  V.docState = "loading";
  V.cleanup = false;
  if (id) V.hl = null; // the later action wins: a selection replaces the state chip
  paint();
  renderPanel();
  if (id && isPhone()) keepAbovePanel(id);
  if (!id || !V.ctx) return;
  await loadSelected(id, { keep: false });
}

// Read the selected Scope's detail. A newer selection or read drops this answer (F-04). On a new revision the
// panel keeps drawing the last answer while it reads again (keep), and keeps it when the read fails.
async function loadSelected(id, { keep }) {
  const token = keep ? ++V.token : V.token;
  const revision = V.data?.revision ?? null;
  V.docRevision = revision; // one read per revision, even when it fails
  let doc = null;
  try {
    doc = await api.scope(V.ctx.repository, id, V.ctx.baseline);
  } catch {
    doc = null; // the selected box alone stays highlighted (F-02)
  }
  if (token !== V.token || V.sel !== id) return;
  if (!doc) {
    if (keep && V.path) return;
    V.docState = "failed"; // F-01: the header from the structure, the contents say so
    renderPanel();
    return;
  }
  const done = byId(id)?.state === "done";
  const down = (done ? doc.downstream_all : doc.downstream) || { direct: [], indirect: [] };
  const up = doc.upstream || { direct: [], indirect: [] };
  V.path = {
    upDirect: new Set(up.direct),
    downDirect: new Set(down.direct),
    related: new Set([id, ...V.ix.ancestors(id), ...up.direct, ...up.indirect, ...down.direct, ...down.indirect]),
    roots: new Set(doc.root_waits?.scope_ids || []),
    doc,
  };
  V.docState = "ok";
  paint();
  renderPanel();
}

// --- The bar above the graph: path when focused, state chips, tools ------------------------------------------

function renderBar(focus) {
  const scopes = V.data.scopes.filter((s) => s.kind === "issue" && s.state !== "done");
  const n = {};
  for (const [key] of HL) n[key] = 0;
  for (const s of scopes) {
    if (s.merge === "mergeable") n.ok++;
    else if (s.merge === "needs_fix") n.fix++;
    else if (s.lane in n) n[s.lane]++;
  }
  const chipBtn = ([key, st, label], extra) =>
    `<button type="button" class="nx" data-st="${st}" data-hl="${key}" aria-pressed="${!V.sel && V.hl === key}" title="${label}の Issue を図の中で目立たせる">${extra || stateIcon(st, false)}<span class="lab">${label}</span><b>${n[key]}</b></button>`;
  V.el.next.innerHTML =
    chipBtn(HL[0]) +
    chipBtn(HL[1]) +
    chipBtn(HL[2]) +
    `<span class="nx-grp" role="group" aria-label="マージ待ち"><span class="nx-grp__lab">${ic("branch")}<span class="lab">マージ待ち</span></span>${chipBtn(HL[3], ic("zap"))}${chipBtn(HL[4], ic("check"))}</span>` +
    (n.unknown ? chipBtn(HL[5]) : "");
  const o = V.opts;
  const tool = (act, label, icon, pressed, extra = "") =>
    `<button type="button" class="tool" data-act="${act}"${pressed == null ? "" : ` aria-pressed="${pressed}"`} aria-label="${label}" title="${label}"${extra}>${ic(icon)}<span class="lab">${label}</span></button>`;
  V.el.tools.innerHTML =
    `<span class="tool-group"><button type="button" class="tool is-icon" data-act="zout" aria-label="縮小">${ic("minus")}</button><button type="button" class="tool zoomval" data-act="z100" title="100% に戻す">${Math.round(V.s * 100)}%</button><button type="button" class="tool is-icon" data-act="zin" aria-label="拡大">${ic("plus")}</button></span>` +
    tool("fit", "全体", "fit") +
    tool("mode", o.mode === "tree" ? "木" : "入れ子", o.mode === "tree" ? "tree" : "nest", null, ` data-mode="${o.mode}"`) +
    tool("done", "終わったものも", "checkCircle", o.showDone) +
    `<span class="tool-group" role="group" aria-label="依存の線">` +
    [
      ["wait", "待っている線"],
      ["all", "すべての線"],
      ["none", "線なし"],
    ]
      .map(([v, label]) => `<button type="button" class="tool" data-act="deps" data-deps="${v}" aria-pressed="${o.deps === v}" title="依存の線：${label}">${v === "none" ? ic("x") : ic("arrowRight")}<span class="lab">${label}</span></button>`)
      .join("") +
    `</span>` +
    (o.mode === "nest" ? tool("fold", "片付けの候補を畳む", "box", o.fold) : "");
  if (focus && byId(focus)) {
    const chain = V.ix.ancestors(focus).slice().reverse();
    V.el.crumbs.hidden = false;
    V.el.crumbs.innerHTML =
      `<button type="button" class="tool" data-act="unfocus">${ic("globe")}<span class="lab">全体へ戻る</span></button>` +
      `<nav class="path" aria-label="絞った範囲の道筋">${chain.map((id) => `<button type="button" data-focus="${esc(id)}" title="${esc(byId(id)?.title ?? "")}">${esc(id)}</button>${ic("chevronRight")}`).join("")}<span>${esc(focus)}</span></nav>`;
  } else {
    V.el.crumbs.hidden = true;
    V.el.crumbs.innerHTML = "";
  }
}

function renderLegend() {
  const li = (a, b, wide) => `<li${wide ? ' class="wide"' : ""}><span>${a}</span>${b}</li>`;
  V.el.legend.dataset.open = String(V.legend);
  V.el.legend.innerHTML =
    `<button type="button" class="legend__head" data-act="legend" aria-expanded="${V.legend}">${ic("info")}凡例${ic("chevronRight")}</button><div class="legend__body">` +
    `<div class="lg-grp"><h4>状態</h4><ul>${["blocked", "ready", "doing", "unknown", "done"].map((s) => li(s === "doing" ? stateIcon(s, false, { progress: { done: 3, total: 8 } }) : stateIcon(s, false), s === "doing" ? "作業中（区切り＝計画の手順、緑＝終わった。30分以内に動いたら次が点滅）" : STATES[s].label, s === "doing")).join("")}${li('<span class="sbar" style="width:26px"><i data-st="done" style="width:60%"></i><i data-st="doing" style="width:20%"></i><i data-st="ready" style="width:20%"></i></span>', "配下の内訳")}</ul></div>` +
    `<div class="lg-grp"><h4>PR と CI</h4><ul>${li(`<span class="pr" data-pr="open">${ic("branch")}</span>`, "開いている")}${li(`<span class="pr" data-pr="draft">${ic("branch")}</span>`, "下書き")}${li(`<span class="pr" data-pr="merged">${ic("merge")}</span>`, "マージ済み")}${li(`<span class="pr" data-pr="closed">${ic("prClosed")}</span>`, "閉じた")}` +
    `${li('<span class="ci" data-ci="success"></span>', "CI 成功")}${li('<span class="ci" data-ci="failure"></span>', "CI 失敗")}${li('<span class="ci" data-ci="running"></span>', "CI 実行中")}${li(`<span class="mg" data-mg="ok">${ic("check")}</span>`, "マージできる")}${li(`<span class="mg" data-mg="conflict">${ic("zap")}</span>`, "衝突")}</ul></div>` +
    `<div class="lg-grp"><h4>保証</h4><ul>${M.AS_LEVELS.map((l) => li(M.asMark(l), l)).join("")}</ul></div>` +
    `<div class="lg-grp"><h4>そのほか</h4><ul>${li('<span class="lg-chg"></span>', "前回から変化")}${li(`<span class="wt">${ic("folder")}</span>`, "worktree あり")}${li('<span class="stg">2</span>', "進める段")}${li(`<span class="dn">${ic("down")}3</span>`, "後に続く数")}${li(`<span class="hm">${ic("person")}人 2</span>`, "人のタスクが止めている数（枠は配下も）")}${li(`<span class="cln">${ic("box")}</span>`, "片付けの候補")}${li('<span class="lg-line"></span>', "待っている依存", 1)}${li('<span class="lg-line is-done"></span>', "終わった依存", 1)}${li('<span class="lg-tree"></span>', "親子（木）", 1)}</ul></div>` +
    `<div class="lg-grp"><h4>箱を選んだとき</h4><ul>${li('<span class="lg-box is-sel"></span>', "選んだ箱（1つだけ）")}${li('<span class="lg-line is-p1"></span>', "直接の依存", 1)}${li('<span class="lg-line is-p2"></span>', "間接（2段目より先）", 1)}${li('<span class="lg-line is-off"></span><span class="lg-box is-off"></span>', "関係ない")}${li(`<span class="rt lg-rt">${ic("target")}大もと</span>`, "大もとの待ち先")}${li(ic("arrowRight"), "矢印：選んだ箱へ入る線＝待ち先、出る線＝後に続く", 1)}</ul></div>` +
    `</div>`;
}

// --- The Scope panel (iss-00587 D-06): the shared panel, or the cleanup list in the same aside ---------------

function frameOf(s) {
  return s.kind !== "issue" || (V.ix.kids.get(s.id) || []).length > 0;
}

function renderPanel() {
  const panel = V.el?.panel;
  if (!panel) return;
  if (V.cleanup) {
    V.pn.hide();
    const list = V.cleanup;
    panel.dataset.st = "unknown";
    panel.innerHTML =
      `<div class="pn-grab"></div><div class="pn-head"><b>${ic("box")} 片付けの候補 ${list.length}件</b><button type="button" class="iconbtn" data-act="close" aria-label="閉じる">${ic("x")}</button></div>` +
      `<div class="pn-body"><ul class="pn-clean">${list
        .map((c) => {
          const s = byId(c.id);
          return `<li><button type="button" data-goto="${esc(c.id)}">${stateIcon(s?.state || "unknown", false)}<span class="ds-docid">${esc(c.id)}</span><span class="pn-clean__t">${esc(s?.title ?? "")}</span></button><small>${esc(c.text)}</small></li>`;
        })
        .join("")}</ul></div>`;
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    V.el.gx.dataset.panel = "open";
    return;
  }
  const s = V.sel ? byId(V.sel) : null;
  if (!s) {
    V.pn.hide();
    delete V.el.gx.dataset.panel;
    return;
  }
  V.pn.show({ ctx: V.ctx, scope: s, doc: V.path?.doc ?? null, docState: V.docState, byId: V.ix.byId });
  V.el.gx.dataset.panel = "open";
}

// --- Events ------------------------------------------------------------------------------------------------

function setFocus(id) {
  const base = new URL(V.ctx.route.path, location.origin).pathname;
  V.fitted = false;
  V.ctx.navigate(id ? `${base}?focus=${encodeURIComponent(id)}` : base);
}

function goDetail(id) {
  const s = byId(id);
  if (s) V.ctx.navigate(s.path);
}

function onClick(event) {
  const t = event.target;
  const act = t.closest("[data-act]");
  if (act) {
    const a = act.dataset.act;
    const o = V.opts;
    if (a === "zin") zoomCenter(1.25);
    else if (a === "zout") zoomCenter(0.8);
    else if (a === "z100") zoomCenter(1 / V.s);
    else if (a === "fit") fit();
    else if (a === "legend") {
      V.legend = !V.legend;
      savePrefs();
      renderLegend();
    } else if (a === "close") {
      if (V.cleanup) {
        V.cleanup = false;
        renderPanel();
      } else select(null);
    } else if (a === "focus") setFocus(act.dataset.focus);
    else if (a === "unfocus") setFocus(null);
    else {
      if (a === "mode") o.mode = o.mode === "tree" ? "nest" : "tree";
      else if (a === "done") o.showDone = !o.showDone;
      else if (a === "deps") o.deps = act.dataset.deps;
      else if (a === "fold") o.fold = !o.fold;
      else return;
      savePrefs();
      render(V.root, V.ctx);
    }
    return;
  }
  const hl = t.closest("[data-hl]");
  if (hl) {
    // the later action wins: a state chip replaces the selection
    V.hl = !V.sel && V.hl === hl.dataset.hl ? null : hl.dataset.hl;
    if (V.sel) {
      V.token++;
      V.sel = null;
      V.path = null;
      V.docState = "loading";
      renderPanel();
    }
    paint();
    return;
  }
  const crumb = t.closest("[data-focus]");
  if (crumb && V.el.crumbs.contains(crumb)) {
    setFocus(crumb.dataset.focus);
    return;
  }
  const go = t.closest("[data-goto]");
  if (go) {
    select(go.dataset.goto);
    centerOn(go.dataset.goto);
  }
}

function onKey(event) {
  if (!V.el) return;
  if (event.key === "Escape") {
    if (V.cleanup) {
      V.cleanup = false;
      renderPanel();
    } else if (V.sel) select(null);
    else if (V.hl) {
      V.hl = null;
      paint();
    }
    return;
  }
  const target = event.target.closest?.(".gx-box, .gx-fh");
  if (target && V.el.view.contains(target) && (event.key === "Enter" || event.key === " ")) {
    event.preventDefault();
    const id = target.dataset.id;
    if (event.key === "Enter" && V.sel === id) goDetail(id);
    else select(id);
  }
}

// Only a change of the room the graph is seen in, its width or height, lays it out again (iss-00560 R-03, iss-00575
// R-03), once the resizing has stopped; zooming, panning, new data and the routing's widening keep the layout.
// The zoom and the position stay.
let resizeTimer = 0;
function onResize() {
  if (!V.el || V.el.view.hidden) return;
  applyT();
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(relayout, RESIZE_SETTLE);
}

function relayout() {
  if (!V.el || V.el.view.hidden || !V.data || !V.ctx || (seenWidth() === V.width && seenHeight() === V.height)) return;
  render(V.root, V.ctx);
}

// A tap or click on the graph (pointer events give both): select; on a phone the second tap on the selected box
// opens its detail screen. PC double click opens it directly (dblclick below).
function onTap(target) {
  const clean = target.closest(".gx-clean");
  if (clean) {
    const ids = clean.dataset.ids.split(" ");
    const all = cleanupOf();
    V.token++;
    V.sel = null;
    V.path = null;
    V.cleanup = ids.map((id) => all.get(id) || { id, text: "" });
    paint();
    renderPanel();
    return;
  }
  const hit = target.closest(".gx-box, .gx-fh");
  if (!hit) {
    if (V.sel) select(null);
    return;
  }
  const id = hit.dataset.id;
  if (isPhone() && V.sel === id) {
    goDetail(id);
    return;
  }
  if (V.sel !== id) select(id);
}

// --- Zoom and pan ------------------------------------------------------------------------------------------

function applyT() {
  if (!V.el) return;
  V.el.world.style.transform = `translate(${V.tx}px, ${V.ty}px) scale(${V.s})`;
  const z = V.el.tools.querySelector(".zoomval");
  if (z) z.textContent = `${Math.round(V.s * 100)}%`;
}

// The bottom of the bar above the graph, in the graph area's coordinates (#527 P-6: no box under the bar).
function barBottom() {
  const view = V.el.view.getBoundingClientRect();
  let bottom = view.top;
  for (const el of [V.el.next, V.el.crumbs, isPhone() ? null : V.el.tools]) {
    if (!el || el.hidden || !el.offsetParent) continue;
    bottom = Math.max(bottom, el.getBoundingClientRect().bottom);
  }
  return bottom - view.top;
}

function initialView() {
  const v = V.el.view;
  const L = V.EG.layout;
  const top = barBottom() + 8;
  if (isPhone()) {
    V.s = 0.74;
    V.tx = 4;
  } else {
    V.s = Math.min(1, Math.max(0.88, (v.clientWidth - 16) / L.width));
    V.tx = Math.max(0, (v.clientWidth - L.width * V.s) / 2);
  }
  V.ty = top;
}

// The smallest zoom: 0.12, or less when that is what it takes to show the whole graph. With no wrapping
// (iss-00556 R-07) a graph can be several thousand pixels wide, wider than 0.12 shows on a phone.
const fitScale = () => {
  const v = V.el.view;
  const L = V.EG.layout;
  const top = barBottom() + 8;
  return Math.min(1, (v.clientWidth - 16) / L.width, (v.clientHeight - top - 16) / L.height);
};
const minScale = () => Math.max(0.02, Math.min(0.12, fitScale()));

function fit() {
  const v = V.el.view;
  const L = V.EG.layout;
  const top = barBottom() + 8;
  V.s = Math.max(minScale(), fitScale());
  V.tx = (v.clientWidth - L.width * V.s) / 2;
  V.ty = top + Math.max(0, (v.clientHeight - top - 8 - L.height * V.s) / 2);
  applyT();
}

function zoomAt(f, cx, cy) {
  const ns = Math.min(2, Math.max(minScale(), V.s * f));
  V.tx = cx - (cx - V.tx) * (ns / V.s);
  V.ty = cy - (cy - V.ty) * (ns / V.s);
  V.s = ns;
  applyT();
}

function zoomCenter(f) {
  const v = V.el.view;
  zoomAt(f, v.clientWidth / 2, v.clientHeight / 2);
}

// On a phone the summary rises from the bottom: move the selected box into the free part above it, so the second
// tap can reach it (as the prototype does).
function keepAbovePanel(id) {
  const el = V.el.world.querySelector(`[data-id="${CSS.escape(id)}"]`);
  if (!el) return;
  const vb = V.el.view.getBoundingClientRect();
  const b = el.getBoundingClientRect();
  const top = vb.top + barBottom() + 8;
  const bottom = vb.bottom - V.el.panel.offsetHeight - 12;
  if (b.top >= top && b.bottom <= bottom) return;
  V.ty += top + Math.max(0, (bottom - top - b.height) / 2) - b.top;
  applyT();
}

function centerOn(id) {
  const el = V.el.world.querySelector(`[data-id="${CSS.escape(id)}"]`);
  if (!el) return;
  const vb = V.el.view.getBoundingClientRect();
  const b = el.getBoundingClientRect();
  // the middle of the room the panel leaves (iss-00587 D-06): half of its width and its 10px margin
  const off = isPhone() ? 0 : V.el.panel.classList.contains("is-open") ? (V.el.panel.offsetWidth + 10) / 2 : 0;
  V.tx += vb.left + vb.width / 2 - off - (b.left + b.width / 2);
  V.ty += vb.top + (isPhone() ? vb.height * 0.3 : vb.height / 2) - (b.top + b.height / 2);
  applyT();
}

// Pointer Events for everything on the graph: one pointer drags (after 6px) or taps, two pointers pinch-zoom and
// move by their midpoint. `touch-action: none` on the area keeps the browser from scrolling or zooming the page.
function bindView() {
  const v = V.el.view;
  const pts = new Map();
  let tap = null;
  let pinch = null;
  const two = () => {
    const [a, b] = [...pts.values()];
    const r = v.getBoundingClientRect();
    return { d: Math.hypot(a.x - b.x, a.y - b.y), cx: (a.x + b.x) / 2 - r.left, cy: (a.y + b.y) / 2 - r.top };
  };
  v.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pts.size === 1) tap = { x: e.clientX, y: e.clientY, t: performance.now(), target: e.target, moved: false };
    if (pts.size === 2) {
      if (tap) tap.moved = true;
      pinch = two();
    }
  });
  v.addEventListener("pointermove", (e) => {
    const p = pts.get(e.pointerId);
    if (!p) return;
    const dx = e.clientX - p.x;
    const dy = e.clientY - p.y;
    p.x = e.clientX;
    p.y = e.clientY;
    if (pts.size === 1 && tap) {
      if (!tap.moved && Math.hypot(e.clientX - tap.x, e.clientY - tap.y) > 6) {
        tap.moved = true;
        v.classList.add("is-drag");
        try {
          v.setPointerCapture(e.pointerId);
        } catch {
          // a synthetic or finished pointer
        }
      }
      if (tap.moved) {
        V.tx += dx;
        V.ty += dy;
        applyT();
      }
    } else if (pts.size === 2 && pinch) {
      const n = two();
      V.tx += n.cx - pinch.cx;
      V.ty += n.cy - pinch.cy;
      if (pinch.d > 0) zoomAt(n.d / pinch.d, n.cx, n.cy);
      else applyT();
      pinch = n;
    }
  });
  const end = (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (pts.size === 0) {
      const t = tap;
      tap = null;
      v.classList.remove("is-drag");
      if (t && !t.moved && e.type === "pointerup" && performance.now() - t.t < 600) onTap(t.target);
    }
  };
  v.addEventListener("pointerup", end);
  v.addEventListener("pointercancel", end);
  v.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const b = v.getBoundingClientRect();
      if (e.ctrlKey || e.metaKey) zoomAt(Math.exp(-e.deltaY * 0.01), e.clientX - b.left, e.clientY - b.top);
      else {
        V.tx -= e.deltaX;
        V.ty -= e.deltaY;
        applyT();
      }
    },
    { passive: false },
  );
  v.addEventListener("dblclick", (e) => {
    if (isPhone()) return; // phones open the detail with a second tap; a double tap is a zoom gesture there
    const hit = e.target.closest(".gx-box, .gx-fh");
    if (hit) goDetail(hit.dataset.id);
  });
}

// --- The line check on the page (the prototype's edgeAudit, for the browser check) ------------------------------

/** Check the drawn lines against the boxes as the page shows them now (0 everywhere is clean). */
export function edgeAudit(options = {}) {
  if (!V.EG || !V.el) return null;
  const { G, routes } = V.EG;
  const wb = V.el.world.getBoundingClientRect();
  const rect = (el) => {
    const b = el.getBoundingClientRect();
    return { x1: (b.left - wb.left) / V.s, y1: (b.top - wb.top) / V.s, x2: (b.right - wb.left) / V.s, y2: (b.bottom - wb.top) / V.s };
  };
  // The obstacles measured from the DOM, in the routing's order and keys (a frame: its heading and summary rows).
  const obs = G.obs.map((o) => {
    if (o.lane) return o;
    const [kind, id] = [o.key.slice(0, 1), o.key.slice(2)];
    const el = kind === "c" ? V.el.world.querySelector(`.gx-clean[data-clean="${CSS.escape(id)}"]`) : V.el.world.querySelector(`[data-id="${CSS.escape(id)}"]:is(.gx-box, .gx-frame)`);
    if (!el) return { ...o, missing: true };
    const r = rect(el);
    if (el.classList.contains("gx-frame") && !el.classList.contains("is-compact")) {
      const fm = el.querySelector(".gx-fm");
      return { ...r, y2: Math.max(rect(fm).y2 + 3, o.y2), key: o.key };
    }
    return { ...r, key: o.key };
  });
  const res = audit(
    routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: G.obs[G.edges[rt.ei].a].key, kz: G.obs[G.edges[rt.ei].z].key })),
    obs,
    options,
  );
  const drift = Math.max(0, ...G.obs.map((o, i) => (o.lane ? 0 : Math.max(Math.abs(o.x1 - obs[i].x1), Math.abs(o.y1 - obs[i].y1), Math.abs(o.x2 - obs[i].x2)))));
  return {
    ...res,
    edges: routes.length,
    iters: V.EG.iters,
    ms: V.EG.ms,
    unmapped: V.EG.unmapped,
    widenLeft: V.EG.widen.length,
    missing: obs.filter((o) => o.missing).length,
    drift: Math.round(drift * 10) / 10,
    mode: V.opts.mode,
  };
}

export default {
  id: "graph",
  title: "構造の図",
  icon: "layers",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/_shared/scope_tabs.css", "/assets/views/_shared/panel.css", "/assets/views/graph.css"],
  render,
  dispose,
};
