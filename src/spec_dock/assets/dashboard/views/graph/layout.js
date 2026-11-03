// The structure graph's placement (iss-00532 D-03): from the structure API's Scopes and the chosen way of showing
// them, the coordinates of every box, frame, folded group and tree line, and the dependency pairs to draw.
// Pure computation: no DOM. The page puts the elements at these coordinates, so the routing (router.js) and its
// check see the same rectangles in the page and in the node check of the tests.
//
// The model decides everything about the Scopes (state, stage, recommended order, cleanup candidates); this module
// only arranges them: stages left to right, the recommended order (`rank`) top to bottom inside a stage.
import { portSpan, route } from "./router.js";

export const SIZE = {
  boxW: 178,
  boxH: 88,
  treeFrameW: 236,
  chipW: 150,
  chipH: 30,
  compactW: 236,
  head: 46, // the frame's heading row (22) and summary row (6 + 18)
  pad: { initiative: [16, 16, 16], epic: [9, 12, 12], issue: [9, 12, 12] }, // top, sides, bottom
  minFrameW: { initiative: 420, epic: 300, issue: 300 },
  wrapMax: 1240,
  bandCols: 6,
  margin: 24,
  indent: 40,
};
const BASE = { world: 28, body: 12, wrapRow: 14, wrapCol: 14, cols: 44, col: 12, band: 24, treeRow: 14, treeIndent: 0 };

export const DEFAULTS = { mode: "nest", showDone: false, deps: "wait", fold: true, focus: null };

// The axis a gap key spreads: x for widths (wrap items, columns, the tree's indent), y for heights.
const axisOf = (key) => (key.startsWith("wc") || /^c/.test(key) || key === "tree.indent" ? "x" : "y");
// A gap of a container: its base, what routing added to the whole container (key), to the i-th gap (key#i), and to
// every gap of the axis (all.x, all.y: the fallback for a channel that no single gap widens).
const gap = (gaps, key, base, i = null) =>
  base + (gaps[key] || 0) + (i == null ? 0 : gaps[`${key}#${i}`] || 0) + (gaps[`all.${axisOf(key)}`] || 0);

// --- Which Scopes are shown ---------------------------------------------------------------------------------

export function index(scopes) {
  const byId = new Map(scopes.map((s) => [s.id, s]));
  const kids = new Map(scopes.map((s) => [s.id, []]));
  for (const s of scopes) if (s.parent_id && kids.has(s.parent_id) && s.parent_id !== s.id) kids.get(s.parent_id).push(s);
  const ancestors = (id) => {
    const out = [];
    let p = byId.get(id)?.parent_id;
    while (p && byId.has(p) && !out.includes(p) && p !== id) {
      out.push(p);
      p = byId.get(p).parent_id;
    }
    return out;
  };
  return { byId, kids, ancestors };
}

function visibility(ix, opts) {
  const memo = new Map();
  const seen = new Set();
  const visible = (s) => {
    if (memo.has(s.id)) return memo.get(s.id);
    if (seen.has(s.id)) return false; // a broken parent cycle
    seen.add(s.id);
    const v = opts.showDone || s.state !== "done" || ix.kids.get(s.id).some(visible);
    memo.set(s.id, v);
    return v;
  };
  return visible;
}

const stageOf = (s, opts) => (opts.showDone ? s.stage?.all : s.stage?.open) || 1;
const byRank = (a, b) => (a.rank ?? 1e9) - (b.rank ?? 1e9) || a.number - b.number;
const byStageRank = (opts) => (a, b) => stageOf(a, opts) - stageOf(b, opts) || byRank(a, b);

// --- Blocks: measure (relative coordinates), then flatten to absolute rectangles -------------------------------

// A side with many lines gets taller so that its ports stay a lane apart (gaps["grow:<id>"], from routeLayout).
const grow = (ctx, s) => ctx.gaps[`grow:n:${s.id}`] || 0;

function boxBlock(s, ctx) {
  return { t: "box", s, w: SIZE.boxW, h: SIZE.boxH + grow(ctx, s) };
}

function chipBlock(key, list, ctx) {
  return { t: "chip", key, ids: list.map((s) => s.id), w: SIZE.chipW, h: SIZE.chipH + (ctx.gaps[`grow:c:${key}`] || 0) };
}

// Items of one container, with the cleanup candidates folded into one group at the end.
function folded(items, containerKey, ctx) {
  if (!ctx.opts.fold) return items.map((s) => ctx.node(s));
  // A closed parent with open descendants stays a frame (Epic R-12; the prototype's cleanup set skips it).
  const folds = (s) => ctx.cleanup.has(s.id) && !s.keep_visible;
  const keep = items.filter((s) => !folds(s));
  const fold = items.filter(folds);
  const blocks = keep.map((s) => ctx.node(s));
  if (fold.length) blocks.push(chipBlock(containerKey, fold, ctx));
  return blocks;
}

function wrapBlock(key, items, ctx) {
  const rows = [];
  let row = null;
  for (const it of items) {
    const colGap = gap(ctx.gaps, `wc${key}`, BASE.wrapCol, row ? row.items.length - 1 : 0);
    if (!row || (row.items.length && row.w + colGap + it.w > SIZE.wrapMax)) {
      row = { items: [], w: 0, h: 0 };
      rows.push(row);
    }
    it.x = row.items.length ? row.w + gap(ctx.gaps, `wc${key}`, BASE.wrapCol, row.items.length - 1) : 0;
    row.w = it.x + it.w;
    row.h = Math.max(row.h, it.h);
    row.items.push(it);
  }
  let y = 0;
  rows.forEach((r, i) => {
    r.y = y;
    r.items.forEach((it) => (it.y = 0));
    y += r.h + (i < rows.length - 1 ? gap(ctx.gaps, `wr${key}`, BASE.wrapRow, i) : 0);
  });
  // A wrap is rows (y) of items (x).
  return {
    t: "group",
    key: `wr${key}`,
    axis: "y",
    w: Math.max(0, ...rows.map((r) => r.w)),
    h: y,
    kids: rows.map((r, i) => ({ t: "group", key: `wc${key}`, axis: "x", x: 0, y: r.y, w: r.w, h: r.h, kids: r.items, i })),
  };
}

function colsBlock(key, columns, ctx) {
  const cols = columns.map((items, i) => {
    let y = 0;
    items.forEach((it, j) => {
      it.x = 0;
      it.y = y;
      y += it.h + (j < items.length - 1 ? gap(ctx.gaps, `k${key}.${i}`, BASE.col, j) : 0);
    });
    return { t: "group", key: `k${key}.${i}`, axis: "y", w: Math.max(0, ...items.map((it) => it.w)), h: y, kids: items };
  });
  const bands = [];
  for (let i = 0; i < cols.length; i += SIZE.bandCols) bands.push(cols.slice(i, i + SIZE.bandCols));
  let y = 0;
  const bandBlocks = bands.map((list, b) => {
    let x = 0;
    list.forEach((c, i) => {
      c.x = x;
      c.y = 0;
      x += c.w + (i < list.length - 1 ? gap(ctx.gaps, `c${key}`, BASE.cols, i) : 0);
    });
    const block = { t: "group", key: `c${key}`, axis: "x", x: 0, y, w: x, h: Math.max(0, ...list.map((c) => c.h)), kids: list };
    y += block.h + (b < bands.length - 1 ? gap(ctx.gaps, `band${key}`, BASE.band, b) : 0);
    return block;
  });
  return { t: "group", key: `band${key}`, axis: "y", w: Math.max(0, ...bandBlocks.map((b) => b.w)), h: y, kids: bandBlocks };
}

function childrenBlock(key, kids, ctx) {
  const sorted = kids.slice().sort(byStageRank(ctx.opts));
  const max = Math.max(1, ...sorted.map((s) => stageOf(s, ctx.opts)));
  if (max <= 1) return wrapBlock(key, folded(sorted, `${key}.0`, ctx), ctx);
  const columns = Array.from({ length: max }, () => []);
  sorted.forEach((s) => columns[stageOf(s, ctx.opts) - 1].push(s));
  return colsBlock(
    key,
    columns.filter((c) => c.length).map((c, i) => folded(c, `${key}.${i}`, ctx)),
    ctx,
  );
}

function frameBlock(s, kids, ctx) {
  const [padT, padX, padB] = SIZE.pad[s.kind] || SIZE.pad.epic;
  const body = kids.length ? childrenBlock(s.id, kids, ctx) : null;
  const bodyGap = gap(ctx.gaps, `b${s.id}`, BASE.body);
  const compact = !body;
  const head = SIZE.head + grow(ctx, s);
  const w = compact ? SIZE.compactW : Math.max(SIZE.minFrameW[s.kind] || 300, body.w + 2 * padX);
  const h = padT + head + (body ? bodyGap + body.h : 0) + padB;
  if (body) {
    body.x = padX;
    body.y = padT + head + bodyGap;
  }
  return { t: "frame", s, w, h, compact, head: padT + head, padT, body, key: `f${s.id}` };
}

// --- The nested and the tree layout ---------------------------------------------------------------------------

function nest(roots, ctx) {
  const frames = roots.filter((s) => s.kind !== "issue" || ctx.visibleKids(s).length);
  const loose = roots.filter((s) => !frames.includes(s));
  const items = folded(frames, "root", ctx);
  if (loose.length) items.push(wrapBlock("root", folded(loose, "root.loose", ctx), ctx));
  let y = 0;
  items.forEach((it, i) => {
    it.x = 0;
    it.y = y;
    y += it.h + (i < items.length - 1 ? gap(ctx.gaps, "world", BASE.world, i) : 0);
  });
  return { t: "group", key: "world", axis: "y", x: 0, y: 0, w: Math.max(0, ...items.map((it) => it.w)), h: y, kids: items };
}

function tree(roots, ctx) {
  const rows = [];
  const walk = (s, depth) => {
    const kids = ctx.visibleKids(s).slice().sort(byStageRank(ctx.opts));
    rows.push({ s, depth, frame: s.kind !== "issue" || kids.length > 0 });
    kids.forEach((k) => walk(k, depth + 1));
  };
  roots.forEach((r) => walk(r, 0));
  const indent = SIZE.indent + gap(ctx.gaps, "tree.indent", BASE.treeIndent);
  let y = 0;
  const items = rows.map((r, i) => {
    const w = r.frame ? SIZE.treeFrameW : SIZE.boxW;
    const it = { t: "tbox", s: r.s, depth: r.depth, frame: r.frame, x: r.depth * indent, y, w, h: SIZE.boxH + grow(ctx, r.s) };
    y += it.h + (i < rows.length - 1 ? gap(ctx.gaps, `tree.row.${i}`, BASE.treeRow) : 0);
    return it;
  });
  return { t: "group", key: "tree.row", axis: "y", x: 0, y: 0, w: Math.max(0, ...items.map((it) => it.x + it.w)), h: y, kids: items, tree: true };
}

// --- Flatten ---------------------------------------------------------------------------------------------------

function flatten(block, ox, oy, path, out) {
  const x = ox + (block.x || 0);
  const y = oy + (block.y || 0);
  const rect = { x1: x, y1: y, x2: x + block.w, y2: y + block.h };
  if (block.t === "box" || block.t === "tbox") {
    out.nodes.push({ type: block.t === "box" || !block.frame ? "box" : "tframe", id: block.s.id, depth: block.depth ?? null, ...rect, path });
    return;
  }
  if (block.t === "chip") {
    out.groups.push({ key: block.key, ids: block.ids, ...rect, path });
    return;
  }
  if (block.t === "frame") {
    out.nodes.push({ type: "frame", id: block.s.id, kind: block.s.kind, state: block.s.state, compact: block.compact, headY2: y + block.head, ...rect, path: [...path, { c: block.key, axis: "y", i: 0 }] });
    if (block.body) flatten(block.body, x, y, [...path, { c: block.key, axis: "y", i: 1, gapKey: `b${block.s.id}` }], out);
    return;
  }
  block.kids.forEach((kid, i) => flatten(kid, x, y, [...path, { c: block.key, axis: block.axis, i }], out));
}

/**
 * Lay the Scopes out.
 * @param scopes  structure API `scopes`
 * @param cleanup structure API `cleanup` ([{id, code, text}])
 * @param options {mode: "nest"|"tree", showDone, deps: "all"|"wait"|"none", fold, focus}
 * @param gaps    extra pixels per gap key (from earlier routing rounds)
 */
export function layout(scopes, cleanup, options = {}, gaps = {}) {
  const opts = { ...DEFAULTS, ...options };
  if (opts.mode === "tree") opts.fold = false; // the tree shows every Scope as a box
  const ix = index(scopes);
  const visibleBase = visibility(ix, opts);
  const focus = opts.focus && ix.byId.has(opts.focus) ? opts.focus : null;
  const inFocus = (s) => !focus || s.id === focus || ix.ancestors(s.id).includes(focus);
  const visible = (s) => inFocus(s) && (s.id === focus || visibleBase(s));
  const visibleKids = (s) => ix.kids.get(s.id).filter(visible);
  const ctx = { opts, gaps, cleanup: new Set((cleanup || []).map((c) => c.id)), visibleKids };
  ctx.node = (s) => {
    const kids = visibleKids(s);
    return s.kind === "issue" && !kids.length ? boxBlock(s, ctx) : frameBlock(s, kids, ctx);
  };
  const isRoot = (s) => (focus ? s.id === focus : !s.parent_id || !ix.byId.has(s.parent_id) || ix.ancestors(s.id).includes(s.id));
  const roots = scopes
    .filter((s) => visible(s) && isRoot(s))
    .sort((a, b) => (a.kind === "initiative" ? 0 : 1) - (b.kind === "initiative" ? 0 : 1) || byRank(a, b));
  const top = opts.mode === "tree" ? tree(roots, ctx) : nest(roots, ctx);
  const out = { nodes: [], groups: [], trunks: [] };
  const mx = SIZE.margin + (gaps["margin.x"] || 0);
  const my = SIZE.margin + (gaps["margin.y"] || 0);
  flatten(top, mx, my, [], out);
  const width = top.w + 2 * mx;
  const height = top.h + 2 * my;
  if (opts.mode === "tree") out.trunks = treeLines(out.nodes, ix);
  const edges = pairs(scopes, ix, out, opts);
  return { opts, width, height, nodes: out.nodes, groups: out.groups, trunks: out.trunks, edges, focus, ancestors: focus ? ix.ancestors(focus) : [] };
}

// The tree's parent lines: a vertical trunk from the parent's lower left, a short stub into each child's left side
// (14px below its top, above the ports where dependency lines enter).
function treeLines(nodes, ix) {
  const at = new Map(nodes.map((n) => [n.id, n]));
  const lines = [];
  for (const n of nodes) {
    const kids = ix.kids.get(n.id).map((k) => at.get(k.id)).filter(Boolean);
    if (!kids.length) continue;
    const tx = n.x1 + 14;
    const last = Math.max(...kids.map((k) => k.y1 + 14));
    lines.push({ key: `t:${n.id}`, lane: "v", x1: tx - 1, x2: tx + 1, y1: n.y2, y2: last + 1, path: n.path });
    for (const k of kids) lines.push({ key: `t:${n.id}>${k.id}`, lane: "h", x1: tx, x2: k.x1, y1: k.y1 + 13, y2: k.y1 + 15, path: k.path });
  }
  return lines;
}

// The dependency pairs to draw, between what is shown: a box, a frame or the folded group holding the Scope.
function pairs(scopes, ix, out, opts) {
  if (opts.deps === "none") return [];
  const holder = new Map();
  for (const n of out.nodes) holder.set(n.id, `n:${n.id}`);
  for (const g of out.groups) {
    for (const id of g.ids) {
      holder.set(id, `c:${g.key}`);
      const stack = [...ix.kids.get(id)];
      while (stack.length) {
        const k = stack.pop();
        if (holder.has(k.id) && holder.get(k.id).startsWith("n:")) continue;
        holder.set(k.id, `c:${g.key}`);
        stack.push(...ix.kids.get(k.id));
      }
    }
  }
  const rect = new Map([...out.nodes.map((n) => [`n:${n.id}`, n]), ...out.groups.map((g) => [`c:${g.key}`, g])]);
  const contains = (p, q) => p.x1 <= q.x1 + 0.01 && p.y1 <= q.y1 + 0.01 && p.x2 >= q.x2 - 0.01 && p.y2 >= q.y2 - 0.01;
  const edges = new Map();
  for (const s of scopes) {
    const z = holder.get(s.id);
    if (!z) continue;
    for (const b of s.blocked_by || []) {
      const src = ix.byId.get(b);
      const a = holder.get(b);
      if (!src || !a || a === z) continue;
      const done = src.state === "done";
      if (done && opts.deps === "wait") continue;
      const ra = rect.get(a), rz = rect.get(z);
      if (opts.mode !== "tree" && (contains(ra, rz) || contains(rz, ra))) continue; // parent and child: no line
      if (opts.mode === "tree" && (ix.ancestors(s.id).includes(b) || ix.ancestors(b).includes(s.id))) continue;
      const key = `${a}>${z}`;
      const e = edges.get(key);
      if (e) {
        e.pairs.push([b, s.id]);
        e.done = e.done && done;
      } else edges.set(key, { a, z, done, pairs: [[b, s.id]] });
    }
  }
  return [...edges.values()];
}

// --- Routing input and the widening loop ---------------------------------------------------------------------

/** The routing input G for router.js, and the obstacle keys in the same order. */
export function graphInput(L) {
  const obs = [];
  const at = new Map();
  const tree = L.opts.mode === "tree";
  for (const n of L.nodes) {
    let o;
    if (n.type === "frame") {
      o = n.compact
        ? { x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, p1: n.y1 + 10, p2: n.y2 - 8 }
        : { x1: n.x1, y1: n.y1, x2: n.x2, y2: n.headY2 + 3, p1: n.y1 + 11, p2: n.headY2 - 2 };
    } else {
      o = { x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, p1: n.y1 + (tree ? 28 : 12), p2: n.y2 - 12 };
    }
    at.set(`n:${n.id}`, obs.length);
    obs.push({ ...o, key: `n:${n.id}`, path: n.path });
  }
  for (const g of L.groups) {
    at.set(`c:${g.key}`, obs.length);
    obs.push({ x1: g.x1, y1: g.y1, x2: g.x2, y2: g.y2, p1: g.y1 + 9, p2: g.y2 - 9, key: `c:${g.key}`, path: g.path });
  }
  for (const t of L.trunks) obs.push({ ...t, p1: t.y1, p2: t.y1 });
  const frames = L.nodes
    .filter((n) => n.type === "frame")
    .map((n) => ({ x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, cls: n.kind === "initiative" ? "ini" : n.state === "done" ? "done" : "epic", id: n.id }));
  const edges = L.edges.map((e) => ({ a: at.get(e.a), z: at.get(e.z), done: e.done, pairs: e.pairs }));
  return { obs, frames, edges, bounds: { x1: 0, y1: 0, x2: L.width, y2: L.height } };
}

/**
 * The gap keys to widen for a channel between obstacles a (low side) and b (high side) on the axis ("x" = widths,
 * "y" = heights); -1 is the edge of the graph. An empty list: no gap lies between them on that axis.
 */
export function gapFor(G, axis, a, b, tree = false) {
  if (a === -1 || b === -1) return [`margin.${axis}`]; // the channel runs along the edge of the graph
  if (tree) {
    if (axis === "x") return ["tree.indent"];
    const row = (o) => o?.path?.find((step) => step.c === "tree.row")?.i;
    const ra = row(G.obs[a]), rb = row(G.obs[b]);
    if (ra == null || rb == null) return [];
    return [`tree.row.${ra === rb ? ra : Math.min(ra, rb)}`];
  }
  const pa = G.obs[a]?.path, pb = G.obs[b]?.path;
  if (!pa || !pb) return [];
  let k = 0;
  while (k < pa.length && k < pb.length && pa[k].c === pb[k].c && pa[k].i === pb[k].i) k++;
  if (a !== b && k < pa.length && k < pb.length && pa[k].c === pb[k].c && pa[k].axis === axis) {
    const step = pa[k];
    if (step.c.startsWith("f")) {
      const key = step.gapKey || pb[k].gapKey; // a frame's heading and body are apart by the body gap
      if (key) return [key];
    } else return [`${step.c}#${Math.min(step.i, pb[k].i)}`];
  }
  // Otherwise the two sit in containers of the other axis (side by side columns for a height, rows for a width):
  // widen the gap after a and the gap before b in their own nearest containers of the axis.
  const own = (path, after) => {
    for (let j = path.length - 1; j >= 0; j--) {
      const step = path[j];
      if (step.axis !== axis || step.c.startsWith("f")) continue;
      if (after) return `${step.c}#${step.i}`;
      if (step.i > 0) return `${step.c}#${step.i - 1}`;
    }
    return null;
  };
  return [...new Set([own(pa, true), own(pb, false)].filter(Boolean))];
}

// Sides whose lines would sit closer than a lane: how much taller the box or the frame's heading must be.
function portRoom(G) {
  const count = new Map();
  for (const e of G.edges) {
    count.set(`${e.a}R`, (count.get(`${e.a}R`) || 0) + 1);
    count.set(`${e.z}L`, (count.get(`${e.z}L`) || 0) + 1);
  }
  const add = {};
  for (const [side, k] of count) {
    const o = G.obs[parseInt(side, 10)];
    const need = portSpan(k) - (o.p2 - o.p1);
    if (k > 1 && need > 0.5 && !o.lane) {
      const key = `grow:${o.key}`;
      add[key] = Math.max(add[key] || 0, Math.ceil(need));
    }
  }
  return add;
}

/**
 * Lay out and route, widening the gaps where a channel lacks lanes (at most 8 rounds; the prototype's loop).
 * Returns {layout, G, routes, widen, iters, unmapped, gaps}.
 */
export function routeLayout(scopes, cleanup, options = {}, start = {}) {
  const gaps = { ...start };
  let L, G, res, iters = 0, unmapped = 0;
  let before = new Set();
  for (; iters < 8; iters++) {
    L = layout(scopes, cleanup, options, gaps);
    G = graphInput(L);
    res = route(G);
    const add = portRoom(G);
    if (!res.widen.length && !Object.keys(add).length) break;
    unmapped = 0;
    const now = new Set();
    for (const w of res.widen) {
      const sig = `${w.axis}|${G.obs[w.oa]?.key ?? w.oa}|${G.obs[w.ob]?.key ?? w.ob}`;
      now.add(sig);
      let keys = gapFor(G, w.axis, w.oa, w.ob, L.opts.mode === "tree");
      if (!keys.length) unmapped++;
      // a channel that no gap reaches, or that widening did not relieve: every gap of the axis grows a little
      if (!keys.length || before.has(sig)) keys = [...keys, `all.${w.axis}`];
      for (const key of keys) {
        const amount = key.startsWith("all.") ? Math.min(12, Math.ceil(w.amount / 4) + 2) : Math.ceil(w.amount) + 2;
        add[key] = Math.max(add[key] || 0, amount);
      }
    }
    before = now;
    if (!Object.keys(add).length) break;
    for (const [key, value] of Object.entries(add)) gaps[key] = (gaps[key] || 0) + value;
  }
  return { layout: L, G, routes: res.routes, widen: res.widen, iters, unmapped, gaps };
}
