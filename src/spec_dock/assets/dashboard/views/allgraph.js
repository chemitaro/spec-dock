// The cross-repository structure (`/graph`, iss-00614; Epic epic-00612 R-04 to R-09): every shown repository's
// structure graph in one world, each inside a repository frame, the frames nested as the company is (company-os →
// business → product …; the list API's parent and tier). The default range is "next".
//
// Each repository keeps the structure graph's own placement (graph/layout.js, nest), lines (graph/router.js) and parts
// (graph/draw.js); graph/../allgraph/compose.js only places the frames. The selection, the panel, the dependency lines
// and orca-web's marks stay inside one repository. This screen never records "seen".
import * as api from "../core/api.js";
import { index, nodeMarkRows, routeLayout } from "./graph/layout.js";
import { audit, svg as edgeSvg } from "./graph/router.js";
import * as M from "./graph/marks.js";
import * as D from "./graph/draw.js";
import { compactNeeds, headsDiffer, tallNeeds } from "./graph/measure.js";
import { REPO, bodyWidth, compose } from "./allgraph/compose.js";
import { createScopePanel } from "./_shared/panel.js";
import { createOrcaWatch, markAgentAt, paintOrcaMarks } from "./_shared/orca_marks.js";
import { overviewWarnings } from "./_shared/logic.js";

const { esc, ic, stateIcon } = M;
const PHONE = 640;
const RESIZE_SETTLE = 200; // ms the window's size must hold before the frames are composed again (as graph.js)
const REFRESH_MS = 5000; // the revisions are read this often while the page is seen (R-08)
const PREFS_KEY = "specdock.allgraph.v1"; // {range}; the structure graph's specdock.graph.v3 is not read or written
const RANGE_VALUES = D.RANGES.map(([v]) => v);
const EMPTY = "表示しているリポジトリがありません。`spec-dock dashboard list` で確かめてください。";
const NONE = "これから進める Scope は、どのリポジトリにもありません。全体で、終わったものを見られます。";
const LINES = {
  loading: "読み込んでいます…",
  empty: "Scope はまだありません",
  quiet: "この範囲で見せる Scope はありません",
};

const A = {
  range: "next",
  hl: null, // the state chip pressed
  sel: null, // {repo, id}
  path: null, // {upDirect, downDirect, related, roots, doc} of the selection
  token: 0,
  docState: "loading",
  docRevision: null,
  cleanup: false, // the panel shows a repository's cleanup list: {repo, list}
  pn: null,
  legend: false,
  s: 1,
  tx: 0,
  ty: 0,
  fitted: false,
  width: 0, // the graph area's width at 100% the frames were composed for
  height: 0,
  comp: null, // the last compose() result
  ctx: null,
  root: null,
  el: null,
  ro: null,
  rowsRaf: 0,
  timer: 0,
  queued: false, // a lay-out step waits for its setTimeout
  fromRows: false,
};
// repository key → {item, status, structure, failure, revision, ix, desc, eg, sig, marks, rowsRedo, warnings, html}
const R = new Map();
const stats = { layouts: 0, loads: 0, repos: {} };

function loadPrefs() {
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    const range = raw == null ? null : JSON.parse(raw)?.range;
    A.range = RANGE_VALUES.includes(range) ? range : "next";
  } catch {
    A.range = "next"; // private windows, blocked storage and broken values: the default
  }
}
function savePrefs() {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify({ range: A.range }));
  } catch {
    // ignore
  }
}

const isPhone = () => (A.root?.clientWidth || innerWidth) <= PHONE;
const seenWidth = () => Math.max(1, (A.el?.view.clientWidth || innerWidth) - 16);
const seenHeight = () => Math.max(1, (A.el?.view.clientHeight || innerHeight) - 16);
const items = () => A.ctx?.repositories || [];
const count = (key, what) => {
  const c = (stats.repos[key] ||= { layouts: 0, loads: 0 });
  c[what]++;
  stats[what]++;
};

// A repository's own context for the panel and its redraws (D-06): the shell's ctx with this repository and its
// structure, also when the panel draws again from current().
function repoCtx(key) {
  const shell = A.ctx;
  return {
    ...shell,
    repository: key,
    data: R.get(key)?.structure ?? null,
    current: () => {
      const c = shell.current?.();
      return c ? { ...c, repository: key, data: R.get(key)?.structure ?? null } : null;
    },
  };
}

// The drawing context of graph/draw.js for one repository (the selection's path only in the selected one).
function dc(key) {
  const r = R.get(key);
  const mine = A.sel?.repo === key;
  return { data: r.structure, ix: r.ix, desc: r.desc, cleanup: D.cleanupMap(r.structure), range: A.range, path: mine ? A.path : null, sel: mine ? A.sel.id : null };
}

// --- orca-web's marks and the rows of agents (iss-00620, per repository) ------------------------------------------

function paintOrca() {
  if (!A.el || !A.ctx) return;
  for (const [key, body] of bodies()) {
    const r = R.get(key);
    if (r?.structure) paintOrcaMarks(body, A.ctx, r.structure);
  }
  A.pn?.refreshOrca();
  checkRows();
}
function onOrcaNews() {
  for (const r of R.values()) r.rowsRedo = 0;
  paintOrca();
}
const orcaWatch = createOrcaWatch(onOrcaNews);

function measureMarks(root) {
  const view = A.el?.view;
  if (!root || !view || view.hidden || !view.clientWidth) return null;
  const px = (el) => Math.ceil((el.getBoundingClientRect().width / A.s) * 10) / 10;
  const out = {};
  for (const slot of root.querySelectorAll("[data-orca-scope]")) {
    const marks = [...slot.querySelectorAll(".orca-mark")];
    if (!marks.length) continue;
    const list = slot.querySelector(".orca-marks");
    const style = list ? getComputedStyle(list) : null;
    if (!style || style.flexWrap !== "wrap") return null;
    const items = marks.map(px);
    if (items.some((w) => !(w > 0))) return null;
    out[slot.dataset.orcaScope] = { items, gap: parseFloat(style.columnGap) || 0 };
  }
  return out;
}

// After the marks are drawn: lay out again only the repositories whose rows of agents differ from their layout, at most
// twice per news or render (F-03 of iss-00620), keeping the zoom and the position.
function checkRows() {
  if (!A.el) return;
  const redo = [];
  for (const [key, body] of bodies()) {
    const r = R.get(key);
    if (!r?.eg) continue;
    const m = measureMarks(body);
    const h = compactNeeds(body, A.s); // iss-00627: the compact frames' contents, on the same count
    if (!m && !h) continue;
    const rows = !!m && r.eg.layout.nodes.some((n) => ["box", "tframe", "frame"].includes(n.type) && nodeMarkRows(n, m[n.id]) !== (n.rows ?? 1));
    const differ = rows || headsDiffer(r.eg.layout.nodes, h);
    if (m) r.marks = m;
    if (h) r.heads = tallNeeds(r.eg.layout.nodes, h);
    if (!differ || r.rowsRedo >= 2) continue;
    r.rowsRedo++;
    r.sig = null;
    redo.push(key);
  }
  if (!redo.length) return;
  A.fromRows = true;
  try {
    for (const key of redo) layoutRepo(key);
    draw();
  } finally {
    A.fromRows = false;
  }
}

function onMarksResize() {
  if (A.rowsRaf) return;
  A.rowsRaf = requestAnimationFrame(() => {
    A.rowsRaf = 0;
    checkRows();
  });
}

// --- Shell DOM ------------------------------------------------------------------------------------------------

function mount(root) {
  loadPrefs();
  root.innerHTML =
    `<section class="gx" data-screen="allgraph" aria-label="横断の構造">` +
    `<div class="gx-view" tabindex="0" aria-label="横断の構造。ドラッグで移動、Ctrl とホイールか2本指で拡大・縮小"><div class="gx-world"></div><p class="gx-none" hidden></p></div>` +
    `<div class="gx-bar"><div class="gx-left"><div class="gx-next" role="group" aria-label="状態で目立たせる"></div></div><div class="gx-tools"></div></div>` +
    `<div class="legend"></div>` +
    `<aside class="panel" aria-hidden="true" aria-label="Scope の欄"></aside>` +
    `<p class="gx-empty" hidden></p>` +
    `</section>`;
  const q = (sel) => root.querySelector(sel);
  A.root = root;
  A.el = {
    gx: q(".gx"),
    view: q(".gx-view"),
    world: q(".gx-world"),
    bar: q(".gx-bar"),
    next: q(".gx-next"),
    tools: q(".gx-tools"),
    legend: q(".legend"),
    panel: q(".panel"),
    empty: q(".gx-empty"),
    none: q(".gx-none"),
  };
  A.pn = createScopePanel(A.el.panel, {
    onSelect: (id) => {
      if (!A.sel) return;
      const repo = A.sel.repo;
      select(repo, id);
      centerOn(repo, id);
    },
    onClose: () => select(null),
    extraActions: (s) => (A.sel && frameOf(A.sel.repo, s) ? `<button type="button" class="ds-btn" data-act="focus" data-focus="${esc(s.id)}" aria-label="この範囲に絞る" title="この範囲に絞る">${ic("target")}この範囲に絞る</button>` : ""),
  });
  bindView();
  A.el.gx.addEventListener("click", onClick);
  document.addEventListener("keydown", onKey);
  document.addEventListener("visibilitychange", onVisible);
  for (const type of ["gesturestart", "gesturechange", "gestureend"]) document.addEventListener(type, stopGesture, { passive: false });
  window.addEventListener("resize", onResize);
}

function dispose() {
  document.removeEventListener("keydown", onKey);
  document.removeEventListener("visibilitychange", onVisible);
  for (const type of ["gesturestart", "gesturechange", "gestureend"]) document.removeEventListener(type, stopGesture, { passive: false });
  window.removeEventListener("resize", onResize);
  clearInterval(A.timer);
  A.timer = 0;
  A.ro?.disconnect();
  A.ro = null;
  if (A.rowsRaf) cancelAnimationFrame(A.rowsRaf);
  A.rowsRaf = 0;
  if (window.specdockEdgeAudit === edgeAudit) delete window.specdockEdgeAudit;
  A.token++;
  A.root = null;
  A.el = null;
  A.ctx = null;
  A.fitted = false;
  A.sel = null;
  A.path = null;
  A.hl = null;
  A.cleanup = false;
  A.docState = "loading";
  A.docRevision = null;
  A.comp = null;
  R.clear();
  Object.assign(stats, { layouts: 0, loads: 0, repos: {} }); // the counts are of one visit of the screen
  if (window.specdockAllGraphStats === stats) delete window.specdockAllGraphStats;
  orcaWatch.stop();
  A.pn?.destroy();
  A.pn = null;
}

function stopGesture(event) {
  if (event.cancelable) event.preventDefault();
}

// --- Loading and refreshing (R-08) ------------------------------------------------------------------------------

function stateOf(key) {
  let r = R.get(key);
  if (!r) {
    r = { status: "loading", structure: null, failure: null, revision: null, ix: null, desc: null, eg: null, sig: null, marks: {}, heads: {}, rowsRedo: 0, warnings: [], html: null };
    R.set(key, r);
  }
  return r;
}

// Read one repository's structure and queue its lay-out. The status (D-04): an HTTP failure, or an answer with no
// Scope and no readable snapshot, is failed; anything else is ok (its reasons on the warning rows).
async function load(key) {
  const r = stateOf(key);
  count(key, "loads");
  try {
    const structure = await api.structure(key, null);
    if (!A.el || R.get(key) !== r) return;
    const scopes = Array.isArray(structure?.scopes) ? structure.scopes : [];
    r.structure = { ...structure, scopes };
    r.failure = null;
    r.revision = structure?.revision ?? null;
    r.ix = index(scopes);
    r.desc = D.descendants(r.ix);
    r.warnings = overviewWarnings(structure, null);
    r.status = !scopes.length && structure?.snapshot?.status !== "ok" ? "failed" : "ok";
  } catch (error) {
    if (!A.el || R.get(key) !== r) return;
    r.failure = error.message;
    r.warnings = overviewWarnings(null, error.message);
    r.status = r.structure ? "ok" : "failed"; // a later failure keeps what was read
  }
  r.sig = null;
  if (A.sel?.repo === key) {
    if (!r.ix?.byId.get(A.sel.id)) select(null);
    else if (A.docRevision !== r.revision) loadSelected(key, A.sel.id, { keep: true });
  }
  queue();
}

// Lay out the repositories one at a time, handing the page back to the browser between them (R-08).
function queue() {
  if (A.queued) return;
  A.queued = true;
  setTimeout(stepLayout, 0);
}
function stepLayout() {
  A.queued = false;
  if (!A.el) return;
  const key = items().map((it) => it.repository).find((k) => needsLayout(k));
  if (key) layoutRepo(key);
  draw();
  if (items().some((it) => needsLayout(it.repository))) queue();
}

function liveIds(r) {
  const now = Date.now();
  return r.structure.scopes.filter((s) => s.state === "doing" && M.isLive(M.movedAt(s, r.ix.byId), now)).map((s) => s.id);
}
function sigOf(key) {
  const r = R.get(key);
  return `${r.revision}|${A.range}|${bodyWidth(A.width, depthOf(key))}|${liveIds(r).join(",")}|${JSON.stringify(r.marks)}|${JSON.stringify(r.heads)}`;
}
function needsLayout(key) {
  const r = R.get(key);
  return !!r && r.status === "ok" && r.structure.scopes.length > 0 && r.sig !== sigOf(key);
}

// One repository's layout: the structure graph's nest placement in the width its depth leaves.
function layoutRepo(key) {
  const r = R.get(key);
  if (!r || r.status !== "ok" || !r.structure.scopes.length) {
    if (r) r.eg = null;
    return;
  }
  const sig = sigOf(key);
  if (sig === r.sig && r.eg) return;
  const t0 = performance.now();
  const res = routeLayout(r.structure.scopes, r.structure.cleanup, { mode: "nest", range: A.range, focus: null, width: bodyWidth(A.width, depthOf(key)), height: A.height, marks: r.marks, heads: r.heads });
  r.eg = { ...res, ms: Math.round(performance.now() - t0) };
  r.sig = sig;
  r.html = null;
  count(key, "layouts");
}

let depths = new Map();
const depthOf = (key) => depths.get(key) ?? 0;
function updateDepths() {
  depths = new Map([...compose(items(), {}, { range: "all", width: A.width }).frames].map(([k, f]) => [k, f.depth]));
}

async function tick() {
  if (!A.el || document.hidden) return;
  await Promise.all(
    items().map(async ({ repository: key }) => {
      const r = R.get(key);
      if (!r || r.status === "loading") return;
      try {
        const { revision } = await api.revision(key);
        if (!A.el || R.get(key) !== r) return;
        if (revision !== r.revision) await load(key);
      } catch {
        // keep the last answer; the next tick tries again
      }
    }),
  );
  // a mark in progress past its 30 minutes: that repository is laid out again, still
  if (items().some((it) => needsLayout(it.repository))) queue();
}
function onVisible() {
  if (!document.hidden) tick();
}

// --- Render ---------------------------------------------------------------------------------------------------

function render(root, ctx) {
  if (A.root !== root || !root.querySelector(".gx")) mount(root);
  A.ctx = ctx;
  if (!A.fromRows) for (const r of R.values()) r.rowsRedo = 0;
  orcaWatch.follow(ctx.orca);
  window.specdockEdgeAudit = edgeAudit;
  window.specdockAllGraphStats = stats;
  if (!items().length) {
    showEmpty(EMPTY);
    return;
  }
  A.el.empty.hidden = true;
  A.el.view.hidden = false;
  A.el.bar.hidden = false;
  const width = seenWidth();
  if (width !== A.width || !depths.size) {
    A.width = width;
    updateDepths();
  }
  A.height = seenHeight();
  const fresh = items().filter((it) => !R.has(it.repository));
  for (const it of fresh) load(it.repository);
  if (!A.timer) A.timer = setInterval(tick, REFRESH_MS);
  for (const it of items()) if (needsLayout(it.repository)) queue();
  draw();
}

function showEmpty(text) {
  A.el.empty.textContent = text;
  A.el.empty.hidden = false;
  A.el.view.hidden = true;
  A.el.bar.hidden = true;
  A.el.panel.classList.remove("is-open");
}

function sizes() {
  const out = {};
  for (const it of items()) {
    const r = R.get(it.repository);
    if (!r || r.status === "loading") continue;
    const warns = r.warnings.length;
    const alerts = r.warnings.filter((w) => w.level !== "info").length;
    if (r.status === "failed") {
      out[it.repository] = { status: "failed", warns, alerts };
      continue;
    }
    const L = r.eg?.layout;
    const shown = L ? L.nodes.length + L.groups.length : 0;
    // a repository waiting for its first layout is still loading
    if (r.structure.scopes.length && !L) continue;
    out[it.repository] = { status: "ok", w: L ? L.width : 0, h: L ? L.height : 0, shown, scopes: r.structure.scopes.length, warns, alerts };
  }
  return out;
}

const repoPath = (key) => `/r/${key}/`;

function headHtml(it) {
  const tier = (it.tier || []).map((t) => `<span class="sd-badge">${esc(t)}</span>`).join(" › ");
  const name = `${it.owner ?? ""}/${it.name ?? ""}`;
  return (
    `<header class="ax-head"><span class="ax-icon">${ic("folder")}</span><span class="ax-name" title="${esc(it.repository)}">${esc(name)}</span>` +
    (tier ? `<span class="ax-tier">${tier}</span>` : "") +
    `<a class="ax-link" href="${esc(A.ctx.href(repoPath(it.repository)))}" title="このリポジトリの構造の図" aria-label="${esc(name)} の構造の図">${ic("arrowRight")}</a></header>`
  );
}

function warnHtml(warnings) {
  if (!warnings.length) return "";
  return (
    `<ul class="ax-warn">` +
    warnings
      .map((w) => {
        const next = w.next?.length ? `次の1手：${w.next.join("、")}` : "";
        const full = next ? `${w.text} ${next}` : w.text;
        return `<li data-level="${w.level}" title="${esc(full)}">${ic(w.level === "info" ? "info" : "zap")}<span class="ax-text">${esc(w.text)}${next ? `<span class="ax-next">次の1手：${w.next.map((s) => `<code>${esc(s)}</code>`).join("、")}</span>` : ""}</span></li>`;
      })
      .join("") +
    `</ul>`
  );
}

// One repository's graph, the structure graph's parts in its layout's coordinates.
function graphHtml(key) {
  const r = R.get(key);
  if (r.html) return r.html;
  const L = r.eg.layout;
  const ctx = dc(key);
  const frames = L.nodes.filter((n) => n.type === "frame").map((n) => D.frameHtml(ctx, r.ix.byId.get(n.id), n));
  const boxes = L.nodes.filter((n) => n.type !== "frame").map((n) => D.boxHtml(ctx, r.ix.byId.get(n.id), n));
  const chips = L.groups.map((g) => D.chipHtml(ctx, g));
  const trunks = D.treeSvgPaths(L.trunks);
  r.html =
    (trunks ? `<svg class="gx-tree" width="${L.width}" height="${L.height}" aria-hidden="true">${trunks}</svg>` : "") +
    frames.join("") +
    boxes.join("") +
    chips.join("") +
    `<svg class="gx-edges" width="${L.width}" height="${L.height}" aria-hidden="true"></svg>`;
  return r.html;
}

function frameHtml(it, f) {
  const key = it.repository;
  const r = R.get(key);
  const b = f.body;
  const rel = (x, y, w, h) => `left:${x - f.x1}px;top:${y - f.y1}px;width:${w}px;height:${h}px`;
  let body = "";
  if (b.kind === "graph") body = `<div class="ax-body" style="${rel(b.x, b.y, b.w, b.h)}">${graphHtml(key)}</div>`;
  else if (b.h > 0 && LINES[b.kind]) body = `<div class="ax-body" style="${rel(b.x, b.y, f.x2 - f.x1 - 2 * REPO.pad, b.h)}"><p class="ax-line">${LINES[b.kind]}</p></div>`;
  return (
    `<section class="ax-repo" data-repo="${esc(key)}" data-depth="${f.depth}" data-kind="${b.kind}" style="${D.pos(f)}"${r?.status === "loading" || !r ? ' aria-busy="true"' : ""}>` +
    headHtml(it) +
    warnHtml(r?.warnings || []) +
    body +
    `</section>`
  );
}

// Every shown repository's graph area: [key, .ax-body element] of the frames with a graph.
function bodies() {
  if (!A.el) return [];
  const out = [];
  for (const section of A.el.world.querySelectorAll("section.ax-repo")) {
    if (section.dataset.kind !== "graph") continue;
    const body = section.querySelector(".ax-body");
    if (body) out.push([section.dataset.repo, body]);
  }
  return out;
}

function draw() {
  if (!A.el || !items().length) return;
  const byKey = new Map(items().map((it) => [it.repository, it]));
  A.comp = compose(items(), sizes(), { range: A.range, width: A.width, bands: {} });
  const C = A.comp;
  const w = A.el.world;
  w.style.width = `${C.width}px`;
  w.style.height = `${C.height}px`;
  w.dataset.mode = "nest";
  w.dataset.range = A.range;
  const none = A.range === "next" && !C.order.length;
  A.el.none.hidden = !none;
  A.el.none.textContent = none ? NONE : "";
  w.innerHTML = C.order.map((key) => frameHtml(byKey.get(key), C.frames.get(key))).join("");
  if (!A.ro && typeof ResizeObserver === "function") A.ro = new ResizeObserver(onMarksResize);
  if (A.ro) {
    A.ro.disconnect();
    for (const slot of w.querySelectorAll(".sd-orca")) A.ro.observe(slot);
  }
  renderBar();
  renderLegend();
  if (!A.fitted && C.order.length) {
    A.fitted = true;
    whenStyled(() => {
      initialView();
      applyT();
    });
  }
  applyT();
  paint();
  renderPanel();
  paintOrca();
}

function whenStyled(done, started = performance.now()) {
  if (!A.el) return;
  const ready = getComputedStyle(A.el.gx).position === "absolute" && A.el.view.clientHeight > 0;
  if (ready || performance.now() - started > 3000) done();
  else requestAnimationFrame(() => whenStyled(done, started));
}

// --- Highlights ---------------------------------------------------------------------------------------------

function inHl(s) {
  if (!A.hl) return true;
  if (A.hl === "ok") return s.merge === "mergeable";
  if (A.hl === "fix") return s.merge === "needs_fix";
  return s.lane === A.hl;
}

// The graph's paint rules, per repository: the selected repository by its path, the others faded (D-06).
function paint() {
  if (!A.el) return;
  const selected = !!A.sel;
  A.el.world.classList.toggle("has-path", selected);
  for (const [key, body] of bodies()) {
    const r = R.get(key);
    if (!r?.eg) continue;
    const mine = A.sel?.repo === key;
    const P = mine ? A.path : null;
    const { G, routes } = r.eg;
    const svg = body.querySelector(".gx-edges");
    if (svg) {
      svg.classList.toggle("is-hl", !!A.hl && !selected);
      const ctx = dc(key);
      svg.innerHTML = edgeSvg(G, routes, routes.map((rt) => D.edgeClass(ctx, G.edges[rt.ei])));
    }
    const sel = mine ? r.ix.byId.get(A.sel.id) : null;
    const ancestors = sel ? new Set(r.ix.ancestors(sel.id)) : new Set();
    const inside = sel ? new Set(r.desc(sel.id).map((d) => d.id)) : new Set();
    for (const el of body.querySelectorAll(".gx-box, .gx-frame")) {
      const id = el.dataset.id;
      const s = r.ix.byId.get(id);
      const issue = el.classList.contains("gx-box") && !el.classList.contains("is-frame");
      el.classList.toggle("is-sel", mine && id === A.sel.id);
      el.classList.toggle("is-hl", !selected && !!A.hl && issue && inHl(s));
      el.classList.toggle("is-dim", !selected && !!A.hl && !(issue && inHl(s)));
      const related = mine && (!P || P.related.has(id) || ancestors.has(id) || inside.has(id) || id === A.sel.id);
      el.classList.toggle("is-poff", selected && !related);
      el.classList.toggle("is-root", !!P && P.roots.has(id));
    }
    for (const el of body.querySelectorAll(".gx-clean")) {
      const ids = el.dataset.ids.split(" ");
      el.classList.toggle("is-poff", selected && (!mine || (!!P && !ids.some((id) => P.related.has(id) || inside.has(id)))));
      el.classList.toggle("is-dim", !selected && !!A.hl);
    }
  }
  for (const b of A.el.next.querySelectorAll("[data-hl]")) b.setAttribute("aria-pressed", String(!selected && A.hl === b.dataset.hl));
}

async function select(repo, id) {
  A.token++;
  A.sel = repo && id ? { repo, id } : null;
  A.path = null;
  A.docState = "loading";
  A.cleanup = false;
  if (A.sel) A.hl = null; // the later action wins: a selection replaces the state chip
  paint();
  renderPanel();
  if (A.sel && isPhone()) keepAbovePanel(repo, id);
  if (!A.sel || !A.ctx) return;
  await loadSelected(repo, id, { keep: false });
}

async function loadSelected(repo, id, { keep }) {
  const token = keep ? ++A.token : A.token;
  const r = R.get(repo);
  A.docRevision = r?.revision ?? null;
  let doc = null;
  try {
    doc = await api.scope(repo, id, null);
  } catch {
    doc = null;
  }
  if (token !== A.token || A.sel?.repo !== repo || A.sel?.id !== id || !R.get(repo)?.ix) return;
  if (!doc) {
    if (keep && A.path) return;
    A.docState = "failed";
    renderPanel();
    return;
  }
  const ix = R.get(repo).ix;
  const done = ix.byId.get(id)?.state === "done";
  const down = (done ? doc.downstream_all : doc.downstream) || { direct: [], indirect: [] };
  const up = doc.upstream || { direct: [], indirect: [] };
  A.path = {
    upDirect: new Set(up.direct),
    downDirect: new Set(down.direct),
    related: new Set([id, ...ix.ancestors(id), ...up.direct, ...up.indirect, ...down.direct, ...down.indirect]),
    roots: new Set(doc.root_waits?.scope_ids || []),
    doc,
  };
  A.docState = "ok";
  paint();
  renderPanel();
}

// --- The bar, the legend and the panel ----------------------------------------------------------------------------

function renderBar() {
  const n = Object.fromEntries(D.HL.map(([key]) => [key, 0]));
  for (const key of A.comp?.order || []) {
    const r = R.get(key);
    if (r?.structure) D.hlCounts(r.structure.scopes, n);
  }
  A.el.next.innerHTML = D.chipsHtml(n, (key) => !A.sel && A.hl === key);
  const tool = (act, label, icon, name = label) => `<button type="button" class="tool" data-act="${act}" aria-label="${name}" title="${name}">${ic(icon)}<span class="lab">${label}</span></button>`;
  A.el.tools.innerHTML = D.zoomHtml(A.s) + tool("fit", "収める", "fit", "画面に収める") + D.rangesHtml(A.range);
}

function renderLegend() {
  D.renderLegend(A.el.legend, A.legend);
}

function frameOf(repo, s) {
  const r = R.get(repo);
  return s.kind !== "issue" || (r?.ix?.kids.get(s.id) || []).length > 0;
}

function renderPanel() {
  const panel = A.el?.panel;
  if (!panel) return;
  if (A.cleanup) {
    A.pn.hide();
    const { repo, list } = A.cleanup;
    const ix = R.get(repo)?.ix;
    panel.dataset.st = "unknown";
    panel.innerHTML =
      `<div class="pn-grab"></div><div class="pn-head"><b>${ic("box")} 片付けの候補 ${list.length}件</b><button type="button" class="iconbtn" data-act="close" aria-label="閉じる">${ic("x")}</button></div>` +
      `<div class="pn-body"><ul class="pn-clean">${list
        .map((c) => {
          const s = ix?.byId.get(c.id);
          return `<li><button type="button" data-goto="${esc(c.id)}" data-goto-repo="${esc(repo)}">${stateIcon(s?.state || "unknown", false)}<span class="ds-docid">${esc(c.id)}</span><span class="pn-clean__t">${esc(s?.title ?? "")}</span></button><small>${esc(c.text)}</small></li>`;
        })
        .join("")}</ul></div>`;
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    A.el.gx.dataset.panel = "open";
    return;
  }
  const r = A.sel ? R.get(A.sel.repo) : null;
  const s = r?.ix?.byId.get(A.sel.id);
  if (!s) {
    A.pn.hide();
    delete A.el.gx.dataset.panel;
    return;
  }
  A.pn.show({ ctx: repoCtx(A.sel.repo), scope: s, doc: A.path?.doc ?? null, docState: A.docState, byId: r.ix.byId });
  A.el.gx.dataset.panel = "open";
}

// --- Events -----------------------------------------------------------------------------------------------------

const hitOf = (target) => {
  const hit = target.closest?.(".gx-box, .gx-fh");
  const frame = target.closest?.("[data-repo]");
  return hit && frame ? { repo: frame.dataset.repo, id: hit.dataset.id } : null;
};

function goDetail(repo, id) {
  const s = R.get(repo)?.ix?.byId.get(id);
  if (s) A.ctx.navigate(s.path);
}

function onClick(event) {
  const t = event.target;
  const act = t.closest("[data-act]");
  if (act) {
    const a = act.dataset.act;
    if (a === "zin") zoomCenter(1.25);
    else if (a === "zout") zoomCenter(0.8);
    else if (a === "z100") zoomCenter(1 / A.s);
    else if (a === "fit") fit();
    else if (a === "legend") {
      A.legend = !A.legend;
      renderLegend();
    } else if (a === "close") {
      if (A.cleanup) {
        A.cleanup = false;
        renderPanel();
      } else select(null);
    } else if (a === "focus") {
      if (A.sel) A.ctx.navigate(`/r/${A.sel.repo}/?focus=${encodeURIComponent(act.dataset.focus)}`);
    } else if (a === "range") {
      A.range = act.dataset.range;
      savePrefs();
      render(A.root, A.ctx);
    }
    return;
  }
  const hl = t.closest("[data-hl]");
  if (hl) {
    A.hl = !A.sel && A.hl === hl.dataset.hl ? null : hl.dataset.hl;
    if (A.sel) {
      A.token++;
      A.sel = null;
      A.path = null;
      A.docState = "loading";
      renderPanel();
    }
    paint();
    return;
  }
  const go = t.closest("[data-goto]");
  if (go) {
    select(go.dataset.gotoRepo, go.dataset.goto);
    centerOn(go.dataset.gotoRepo, go.dataset.goto);
  }
}

function onKey(event) {
  if (!A.el) return;
  if (event.key === "Escape") {
    if (A.cleanup) {
      A.cleanup = false;
      renderPanel();
    } else if (A.sel) select(null);
    else if (A.hl) {
      A.hl = null;
      paint();
    }
    return;
  }
  const target = event.target.closest?.(".gx-box, .gx-fh");
  if (target && A.el.view.contains(target) && (event.key === "Enter" || event.key === " ")) {
    event.preventDefault();
    const hit = hitOf(target);
    if (!hit) return;
    if (event.key === "Enter" && A.sel?.repo === hit.repo && A.sel.id === hit.id) goDetail(hit.repo, hit.id);
    else select(hit.repo, hit.id);
  }
}

let resizeTimer = 0;
function onResize() {
  if (!A.el || A.el.view.hidden) return;
  applyT();
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(relayout, RESIZE_SETTLE);
}

// Only a new width composes the frames again (each repository's width depends on it); the zoom and position stay.
function relayout() {
  if (!A.el || A.el.view.hidden || !A.ctx || seenWidth() === A.width) return;
  render(A.root, A.ctx);
}

function onTap(target) {
  const clean = target.closest(".gx-clean");
  const frame = target.closest("[data-repo]");
  if (clean && frame) {
    const repo = frame.dataset.repo;
    const all = D.cleanupMap(R.get(repo).structure);
    A.token++;
    A.sel = null;
    A.path = null;
    A.cleanup = { repo, list: clean.dataset.ids.split(" ").map((id) => all.get(id) || { id, text: "" }) };
    paint();
    renderPanel();
    return;
  }
  const hit = hitOf(target);
  if (!hit) {
    if (A.sel) select(null);
    return;
  }
  const same = A.sel?.repo === hit.repo && A.sel.id === hit.id;
  const slot = target.closest(".sd-orca"); // iss-00621 D-03: the agents' tab opens on the pressed agent
  if (slot) {
    if (!same) select(hit.repo, hit.id);
    A.pn?.openAgent(markAgentAt(slot, target));
    return;
  }
  if (isPhone() && same) {
    goDetail(hit.repo, hit.id);
    return;
  }
  if (!same) select(hit.repo, hit.id);
}

// --- Zoom and pan (the structure graph's formulas on the composed world) -----------------------------------------

function applyT() {
  if (!A.el) return;
  A.el.world.style.transform = `translate(${A.tx}px, ${A.ty}px) scale(${A.s})`;
  const z = A.el.tools.querySelector(".zoomval");
  if (z) z.textContent = `${Math.round(A.s * 100)}%`;
}

function barBottom() {
  const view = A.el.view.getBoundingClientRect();
  let bottom = view.top;
  for (const el of [A.el.next, isPhone() ? null : A.el.tools]) {
    if (!el || el.hidden || !el.offsetParent) continue;
    bottom = Math.max(bottom, el.getBoundingClientRect().bottom);
  }
  return bottom - view.top;
}

const worldSize = () => ({ width: Math.max(1, A.comp?.width || 1), height: Math.max(1, A.comp?.height || 1) });

function initialView() {
  const v = A.el.view;
  const L = worldSize();
  const top = barBottom() + 8;
  if (isPhone()) {
    A.s = 0.74;
    A.tx = 4;
  } else {
    A.s = Math.min(1, Math.max(0.88, (v.clientWidth - 16) / L.width));
    A.tx = Math.max(0, (v.clientWidth - L.width * A.s) / 2);
  }
  A.ty = top;
}

const fitScale = () => {
  const v = A.el.view;
  const L = worldSize();
  const top = barBottom() + 8;
  return Math.min(1, (v.clientWidth - 16) / L.width, (v.clientHeight - top - 16) / L.height);
};
// The structure graph's least zoom (0.12, or what shows the whole graph) with a lower floor: every repository's
// graph in one world can need less than graph.js's 0.02 to fit (R-07; e.g. 12812 × 38520 px at 1000 or 390 px).
const minScale = () => Math.max(0.002, Math.min(0.12, fitScale()));

function fit() {
  const v = A.el.view;
  const L = worldSize();
  const top = barBottom() + 8;
  A.s = Math.max(minScale(), fitScale());
  A.tx = (v.clientWidth - L.width * A.s) / 2;
  A.ty = top + Math.max(0, (v.clientHeight - top - 8 - L.height * A.s) / 2);
  applyT();
}

function zoomAt(f, cx, cy) {
  const ns = Math.min(2, Math.max(minScale(), A.s * f));
  A.tx = cx - (cx - A.tx) * (ns / A.s);
  A.ty = cy - (cy - A.ty) * (ns / A.s);
  A.s = ns;
  applyT();
}

function zoomCenter(f) {
  const v = A.el.view;
  zoomAt(f, v.clientWidth / 2, v.clientHeight / 2);
}

const boxEl = (repo, id) => A.el.world.querySelector(`[data-repo="${CSS.escape(repo)}"] [data-id="${CSS.escape(id)}"]`);

function keepAbovePanel(repo, id) {
  const el = boxEl(repo, id);
  if (!el) return;
  const vb = A.el.view.getBoundingClientRect();
  const b = el.getBoundingClientRect();
  const top = vb.top + barBottom() + 8;
  const bottom = vb.bottom - A.el.panel.offsetHeight - 12;
  if (b.top >= top && b.bottom <= bottom) return;
  A.ty += top + Math.max(0, (bottom - top - b.height) / 2) - b.top;
  applyT();
}

function centerOn(repo, id) {
  const el = boxEl(repo, id);
  if (!el) return;
  const vb = A.el.view.getBoundingClientRect();
  const b = el.getBoundingClientRect();
  const off = isPhone() ? 0 : A.el.panel.classList.contains("is-open") ? (A.el.panel.offsetWidth + 10) / 2 : 0;
  A.tx += vb.left + vb.width / 2 - off - (b.left + b.width / 2);
  A.ty += vb.top + (isPhone() ? vb.height * 0.3 : vb.height / 2) - (b.top + b.height / 2);
  applyT();
}

function bindView() {
  const v = A.el.view;
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
        A.tx += dx;
        A.ty += dy;
        applyT();
      }
    } else if (pts.size === 2 && pinch) {
      const n = two();
      A.tx += n.cx - pinch.cx;
      A.ty += n.cy - pinch.cy;
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
        A.tx -= e.deltaX;
        A.ty -= e.deltaY;
        applyT();
      }
    },
    { passive: false },
  );
  v.addEventListener("dblclick", (e) => {
    if (isPhone()) return;
    const hit = hitOf(e.target);
    if (hit) goDetail(hit.repo, hit.id);
  });
}

// --- The line check on the page, per repository (D-07) -------------------------------------------------------------

const TOTALS = ["boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "frameExits", "failed", "missing", "markOverflow", "edges"];

/** The structure graph's edgeAudit for every repository frame, measured from its graph area, and the totals. */
export function edgeAudit(options = {}) {
  if (!A.el) return null;
  const repos = {};
  for (const [key, body] of bodies()) {
    const r = R.get(key);
    if (!r?.eg) continue;
    const { G, routes } = r.eg;
    const wb = body.getBoundingClientRect();
    const rect = (el) => {
      const b = el.getBoundingClientRect();
      return { x1: (b.left - wb.left) / A.s, y1: (b.top - wb.top) / A.s, x2: (b.right - wb.left) / A.s, y2: (b.bottom - wb.top) / A.s };
    };
    const obs = G.obs.map((o) => {
      if (o.lane) return o;
      const [kind, id] = [o.key.slice(0, 1), o.key.slice(2)];
      const el = kind === "c" ? body.querySelector(`.gx-clean[data-clean="${CSS.escape(id)}"]`) : body.querySelector(`[data-id="${CSS.escape(id)}"]:is(.gx-box, .gx-frame)`);
      if (!el) return { ...o, missing: true };
      const rr = rect(el);
      if (el.classList.contains("gx-frame") && !el.classList.contains("is-compact")) {
        const fm = el.querySelector(".gx-fm");
        return { ...rr, y2: Math.max(rect(fm).y2 + 3, o.y2), key: o.key };
      }
      return { ...rr, key: o.key };
    });
    const res = audit(
      routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: G.obs[G.edges[rt.ei].a].key, kz: G.obs[G.edges[rt.ei].z].key })),
      obs,
      options,
    );
    const drift = Math.max(0, ...G.obs.map((o, i) => (o.lane ? 0 : Math.max(Math.abs(o.x1 - obs[i].x1), Math.abs(o.y1 - obs[i].y1), Math.abs(o.x2 - obs[i].x2)))));
    let markOverflow = 0;
    for (const el of body.querySelectorAll(".gx-box, .gx-frame")) {
      const marks = el.querySelectorAll(".orca-mark");
      if (!marks.length) continue;
      const rr = rect(el);
      const cs = getComputedStyle(el);
      const right = rr.x2 - (parseFloat(cs.borderRightWidth) || 0) - (parseFloat(cs.paddingRight) || 0);
      if ([...marks].some((m) => rect(m).x2 > right + 0.5 || rect(m).y2 > rr.y2 + 0.5)) markOverflow++;
    }
    repos[key] = {
      ...res,
      edges: routes.length,
      iters: r.eg.iters,
      ms: r.eg.ms,
      unmapped: r.eg.unmapped,
      widenLeft: r.eg.widen.length,
      missing: obs.filter((o) => o.missing).length,
      drift: Math.round(drift * 10) / 10,
      markOverflow,
    };
  }
  const total = Object.fromEntries(TOTALS.map((name) => [name, 0]));
  for (const res of Object.values(repos)) for (const name of TOTALS) total[name] += Number(res[name]) || 0;
  return { repos, total };
}

export default {
  id: "allgraph",
  title: "横断の構造",
  icon: "layers",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/_shared/scope_tabs.css", "/assets/views/_shared/panel.css", "/assets/views/graph.css", "/assets/views/allgraph.css"],
  render,
  dispose,
};
