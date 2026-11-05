// The structure graph's placement (iss-00532 D-03): from the structure API's Scopes and the chosen way of showing
// them, the coordinates of every box, frame, folded group and tree line, and the dependency pairs to draw.
// Pure computation: no DOM. The page puts the elements at these coordinates, so the routing (router.js) and its
// check see the same rectangles in the page and in the node check of the tests.
//
// The model decides everything about the Scopes (state, stage, recommended order, cleanup candidates); this module
// only arranges them (iss-00560): the children of one parent split into the groups their dependencies connect; a
// group is a grid of stages (left to right) and rows, where what follows sits on the row of what it follows; the
// groups go left to right in the activity order (iss-00556 D-03) and wrap at the width seen at 100%, never inside a
// group.
import { audit, portNeed, route } from "./router.js";

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
  margin: 24,
  indent: 40,
};
const BASE = { world: 28, body: 12, wrapRow: 14, wrapCol: 14, cols: 44, col: 12, treeRow: 14, treeIndent: 0 };
// The width seen at 100% when the page does not say (the node check): the wrap before iss-00556 (iss-00560 F-01).
export const WRAP_WIDTH = 1240;

// iss-00556: finished dependencies between what is shown are drawn by default (faint), the waiting ones stand out.
export const DEFAULTS = { mode: "nest", showDone: false, deps: "all", fold: true, focus: null };

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
  // What a Scope holds (iss-00556 D-03): its tier (0 doing inside, 1 ready inside, 2 only blocked or unknown, 3 all
  // done; a Scope without children by its own state) and its latest move (`active_at`, itself and every descendant).
  const sums = new Map();
  const TIER = { doing: 0, ready: 1, blocked: 2, unknown: 2, done: 3 };
  const summary = (id, seen = new Set()) => {
    if (sums.has(id)) return sums.get(id);
    seen.add(id);
    const s = byId.get(id);
    let recent = s?.active_at || "";
    let tier = 3;
    let held = 0;
    for (const k of kids.get(id) || []) {
      if (seen.has(k.id)) continue;
      const sub = summary(k.id, seen);
      held++;
      tier = Math.min(tier, k.state === "done" && sub.tier === 3 ? 3 : Math.min(sub.tier, TIER[k.state] ?? 2));
      if (sub.recent > recent) recent = sub.recent;
    }
    const out = { tier: held ? tier : TIER[s?.state] ?? 2, recent };
    sums.set(id, out);
    return out;
  };
  return { byId, kids, ancestors, summary };
}

// iss-00556 D-01: a done Scope shows when its parent shows its done children (`showsDone`: open, or the focus);
// a done Scope under a done parent, or without a parent, does not (unless it holds something shown: Epic R-12).
function visibility(ix, opts, showsDone) {
  const memo = new Map();
  const seen = new Set();
  const context = (s) => {
    const p = s.parent_id && s.parent_id !== s.id ? ix.byId.get(s.parent_id) : null;
    return !!p && showsDone(p);
  };
  const visible = (s) => {
    if (memo.has(s.id)) return memo.get(s.id);
    if (seen.has(s.id)) return false; // a broken parent cycle
    seen.add(s.id);
    const v = opts.showDone || s.state !== "done" || ix.kids.get(s.id).some(visible) || context(s);
    memo.set(s.id, v);
    return v;
  };
  return visible;
}

// The stage among siblings: counting the done ones (`stage.all`) inside a parent that shows its done children (D-03),
// so a finished prerequisite shown there sits left of what waits for it; otherwise among the open ones.
const stageOf = (s, all) => (all ? s.stage?.all : s.stage?.open) || 1;
const byRank = (a, b) => (a.rank ?? 1e9) - (b.rank ?? 1e9) || a.number - b.number;
const newer = (a, b) => (a > b ? -1 : a < b ? 1 : 0); // ISO 8601 strings; a missing time ("") is the oldest

// The activity order among siblings (iss-00556 D-03): open frames (by tier, then the latest move), open boxes (the
// recommended order), then what is done (frames by the latest move, boxes by completion), then by number.
export function byActivity(ix) {
  const frame = (s) => s.kind !== "issue" || (ix.kids.get(s.id) || []).length > 0;
  const info = (s) => {
    if (frame(s)) {
      const { tier, recent } = ix.summary(s.id);
      return tier < 3 ? { group: 0, tier, recent } : { group: 2, recent };
    }
    return s.state !== "done" ? { group: 1 } : { group: 2, recent: s.closed_at || s.active_at || "" };
  };
  return (a, b) => {
    const p = info(a), q = info(b);
    if (p.group !== q.group) return p.group - q.group;
    if (p.group === 0) return p.tier - q.tier || newer(p.recent, q.recent) || a.number - b.number;
    if (p.group === 1) return byRank(a, b);
    return newer(p.recent, q.recent) || a.number - b.number;
  };
}
const byStageActivity = (all, ix) => {
  const act = byActivity(ix);
  return (a, b) => stageOf(a, all) - stageOf(b, all) || act(a, b);
};

// --- Blocks: measure (relative coordinates), then flatten to absolute rectangles -------------------------------

// A side with many lines gets taller so that its ports stay a lane apart (gaps["grow:<id>"], from routeLayout).
const grow = (ctx, s) => ctx.gaps[`grow:n:${s.id}`] || 0;

function boxBlock(s, ctx) {
  return { t: "box", s, w: SIZE.boxW, h: SIZE.boxH + grow(ctx, s) };
}

function chipBlock(key, list, ctx) {
  return { t: "chip", key, ids: list.map((s) => s.id), w: SIZE.chipW, h: SIZE.chipH + (ctx.gaps[`grow:c:${key}`] || 0) };
}

// A cleanup candidate folds into a group; a closed parent with open descendants stays a frame (Epic R-12; the
// prototype's cleanup set skips it), and the focus never folds: narrowing to a candidate shows what it holds.
const folds = (s, ctx) => ctx.opts.fold && ctx.cleanup.has(s.id) && !s.keep_visible && s.id !== ctx.focus;

// --- Groups of siblings connected by dependencies (iss-00560 D-01) -----------------------------------------

// The dependencies between siblings, as the model counts them for the stages (`child_stages`): a sibling waits for
// another when anything in its subtree is blocked by something in the other's subtree. Among the open stages, done
// Scopes and dependencies on done Scopes do not count. A cycle is broken (F-02) by keeping the stronger dependencies
// first: the siblings' own, then those between open Scopes, then the more pairs, then from the older sibling; a
// dependency that would close a cycle is dropped. Returns [from, to] pairs without a cycle.
export function siblingEdges(list, ix, all) {
  const owner = new Map();
  const members = new Map();
  for (const s of list) {
    const out = [];
    const stack = [s];
    while (stack.length) {
      const x = stack.pop();
      if (owner.has(x.id)) continue;
      owner.set(x.id, s.id);
      out.push(x);
      stack.push(...(ix.kids.get(x.id) || []));
    }
    members.set(s.id, out);
  }
  const found = new Map();
  for (const s of list) {
    for (const x of members.get(s.id)) {
      if (!all && x.state === "done") continue;
      for (const b of x.blocked_by || []) {
        const from = owner.get(b);
        if (!from || from === s.id) continue;
        const target = ix.byId.get(b);
        if (!all && target?.state === "done") continue;
        const key = `${from}>${s.id}`;
        const e = found.get(key) || { from, to: s.id, own: false, open: 0, pairs: 0 };
        e.own = e.own || (x.id === s.id && b === from);
        e.open += x.state !== "done" && target?.state !== "done" ? 1 : 0;
        e.pairs++;
        found.set(key, e);
      }
    }
  }
  const number = new Map(list.map((s) => [s.id, s.number]));
  const strong = [...found.values()].sort(
    (p, q) => q.own - p.own || q.open - p.open || q.pairs - p.pairs || number.get(p.from) - number.get(q.from) || number.get(p.to) - number.get(q.to),
  );
  const next = new Map();
  const reaches = (a, b) => {
    const stack = [a];
    const seen = new Set();
    while (stack.length) {
      const x = stack.pop();
      if (x === b) return true;
      if (seen.has(x)) continue;
      seen.add(x);
      stack.push(...(next.get(x) || []));
    }
    return false;
  };
  const kept = [];
  for (const e of strong) {
    if (reaches(e.to, e.from)) continue;
    next.set(e.from, [...(next.get(e.from) || []), e.to]);
    kept.push([e.from, e.to]);
  }
  return kept;
}

// The stages among siblings from those dependencies: one more than the latest stage before it (the model's stages
// when there is no cycle).
function stagesOf(list, edges) {
  const before = new Map();
  for (const [a, b] of edges) before.set(b, [...(before.get(b) || []), a]);
  const stage = new Map();
  const walk = (id) => {
    if (!stage.has(id)) stage.set(id, 1 + Math.max(0, ...(before.get(id) || []).map(walk)));
    return stage.get(id);
  };
  for (const s of list) walk(s.id);
  return (s) => stage.get(s.id);
}

// The groups, in the activity order of their first member; each group's members in the order of the stages and
// the activity. `list` is already in the activity order.
function components(list, edges) {
  const up = new Map(list.map((s) => [s.id, s.id]));
  const find = (id) => {
    while (up.get(id) !== id) {
      up.set(id, up.get(up.get(id)));
      id = up.get(id);
    }
    return id;
  };
  for (const [a, b] of edges) up.set(find(a), find(b));
  const groups = new Map();
  for (const s of list) {
    const root = find(s.id);
    if (!groups.has(root)) groups.set(root, []);
    groups.get(root).push(s);
  }
  return [...groups.values()];
}

// Rows inside a group (iss-00560 D-02). Columns are the group's stages; the first column takes the given order,
// every later one puts each member at the average row of what it follows (the rows already used push it down).
function placeRows(cols, preds, first, reach) {
  const row = new Map();
  cols.forEach((col, ci) => {
    const want = new Map();
    for (const s of col) {
      const p = (preds.get(s.id) || []).filter((id) => row.has(id));
      want.set(s.id, p.length ? p.reduce((sum, id) => sum + row.get(id), 0) / p.length : Infinity);
    }
    // equal wishes: the one with the longer chain after it keeps the row, so that the longest chain stays straight
    const items =
      ci === 0
        ? first
        : col
            .map((s, j) => ({ s, j }))
            .sort((a, b) => want.get(a.s.id) - want.get(b.s.id) || reach(b.s) - reach(a.s) || a.j - b.j)
            .map((x) => x.s);
    let next = 0;
    for (const s of items) {
      const w = want.get(s.id);
      const r = Number.isFinite(w) ? Math.max(Math.floor(w + 0.49), next) : next;
      row.set(s.id, r);
      next = r + 1;
    }
  });
  return row;
}

// Crossings (pairs of lines whose ends swap their order) and the rows the lines climb, for choosing between orders.
function cost(row, edges) {
  let cross = 0;
  let climb = 0;
  for (let i = 0; i < edges.length; i++) {
    const [a, b] = edges[i];
    climb += Math.abs(row.get(a) - row.get(b));
    for (let j = i + 1; j < edges.length; j++) {
      const [c, d] = edges[j];
      if (a === c || b === d) continue;
      if ((row.get(a) - row.get(c)) * (row.get(b) - row.get(d)) < 0) cross++;
    }
  }
  return [cross, climb];
}

export function rowsOf(members, edges, stage) {
  const stages = [...new Set(members.map(stage))].sort((a, b) => a - b);
  const colOf = new Map(members.map((s) => [s.id, stages.indexOf(stage(s))]));
  const cols = stages.map(() => []);
  for (const s of members) cols[colOf.get(s.id)].push(s);
  // only a dependency from a left column to a right one lines up rows (a cycle or a mismatched stage does not)
  const forward = edges.filter(([a, b]) => colOf.has(a) && colOf.has(b) && colOf.get(a) < colOf.get(b));
  const preds = new Map();
  const succs = new Map();
  for (const [a, b] of forward) {
    preds.set(b, [...(preds.get(b) || []), a]);
    succs.set(a, [...(succs.get(a) || []), b]);
  }
  const chain = new Map();
  const reach = (s) => {
    if (!chain.has(s.id)) chain.set(s.id, 1 + Math.max(0, ...(succs.get(s.id) || []).map((id) => reach({ id }))));
    return chain.get(s.id);
  };
  const first = placeRows(cols, preds, cols[0], reach);
  let best = first;
  if (cols[0].length > 1) {
    // the other order of the first column: by the average row of what follows each one
    const succ = new Map();
    for (const [a, b] of forward) succ.set(a, [...(succ.get(a) || []), first.get(b)]);
    const mean = (s) => (succ.has(s.id) ? succ.get(s.id).reduce((x, y) => x + y, 0) / succ.get(s.id).length : Infinity);
    const order = cols[0].map((s, j) => ({ s, j })).sort((a, b) => mean(a.s) - mean(b.s) || a.j - b.j).map((x) => x.s);
    const other = placeRows(cols, preds, order, reach);
    const [c1, k1] = cost(first, forward);
    const [c2, k2] = cost(other, forward);
    if (c2 < c1 || (c2 === c1 && k2 < k1)) best = other;
  }
  return { col: colOf, row: best, cols: stages.length };
}

// One group as a grid of rows and stage columns. A row is as tall as its tallest cell, so what follows sits on the
// row of what it follows. A column only orders: each cell sits right of the cell before it on its row and of what it
// follows, one column gap apart, so a wide neighbour on another row leaves no hole in a chain. The routing widens a
// row (rr<group>#i) or the passage after a column (cc<group>#k: every cell placed across column k moves right).
function gridBlock(ck, members, edges, stage, ctx, avail) {
  const { col, row, cols } = rowsOf(members, edges, stage);
  const cells = [];
  const cellOf = new Map();
  const foldsIn = new Map(); // column -> folded members
  for (const s of members) {
    if (folds(s, ctx)) {
      const c = col.get(s.id);
      if (!foldsIn.has(c)) foldsIn.set(c, []);
      foldsIn.get(c).push(s);
    } else {
      const cell = { block: ctx.node(s, avail), col: col.get(s.id), row: row.get(s.id) };
      cells.push(cell);
      cellOf.set(s.id, cell);
    }
  }
  for (const [c, list] of foldsIn) {
    const cell = { block: chipBlock(`${ck}.${c}`, list, ctx), col: c, row: Math.min(...list.map((s) => row.get(s.id))) };
    cells.push(cell);
    for (const s of list) cellOf.set(s.id, cell);
  }
  const used = [...new Set(cells.map((x) => x.row))].sort((a, b) => a - b);
  const rowH = used.map(() => 0);
  for (const x of cells) {
    x.r = used.indexOf(x.row);
    rowH[x.r] = Math.max(rowH[x.r], x.block.h);
  }
  // what each cell must sit right of: what it follows and the cell before it on its row
  const after = new Map(cells.map((x) => [x, new Set()]));
  for (const [a, b] of edges) {
    const p = cellOf.get(a), q = cellOf.get(b);
    if (p && q && p !== q && p.col < q.col) after.get(q).add(p);
  }
  const extra = Array.from({ length: cols }, (_, k) => gap(ctx.gaps, `cc${ck}`, BASE.cols, k) - BASE.cols);
  cells.sort((a, b) => a.col - b.col || a.r - b.r);
  const lastOnRow = new Map();
  for (const x of cells) {
    const left = lastOnRow.get(x.r);
    if (left) after.get(x).add(left);
    lastOnRow.set(x.r, x);
    let at = 0;
    for (const p of after.get(x)) {
      let room = BASE.cols;
      for (let k = p.col; k < x.col; k++) room += extra[k];
      at = Math.max(at, p.block.x + p.block.w + room);
    }
    x.block.x = at;
  }
  const w = Math.max(0, ...cells.map((x) => x.block.x + x.block.w));
  let h = 0;
  const rows = rowH.map((rh, r) => {
    const kids = cells.filter((x) => x.r === r);
    for (const x of kids) {
      x.block.y = 0;
      x.block.slot = x.col;
    }
    const group = { t: "group", key: `cc${ck}`, axis: "x", x: 0, y: h, w, h: rh, kids: kids.map((x) => x.block) };
    h += rh + (r < rowH.length - 1 ? gap(ctx.gaps, `rr${ck}`, BASE.col, r) : 0);
    return group;
  });
  return { t: "group", key: `rr${ck}`, axis: "y", w, h, kids: rows };
}

// Shelves (iss-00560 D-03): the groups left to right, wrapping before one that would pass the width it may use.
// Where to wrap is decided once, without the routing's widening (ctx.breaks from the layout with no gaps), so that
// widening a channel never moves a group to another shelf between the rounds.
function shelfBlock(key, items, ctx, avail, rowBase) {
  const fixed = ctx.breaks?.get(key);
  const sizes = [];
  const shelves = [];
  let shelf = null;
  for (const it of items) {
    const full = fixed ? shelf && shelf.items.length >= fixed[shelves.length - 1] : shelf && shelf.items.length && shelf.w + BASE.wrapCol + it.w > avail;
    if (!shelf || full) {
      shelf = { items: [], w: 0, h: 0 };
      shelves.push(shelf);
    }
    const n = shelf.items.length;
    it.x = n ? shelf.w + gap(ctx.gaps, `wc${key}`, BASE.wrapCol, n - 1) : 0;
    shelf.w = it.x + it.w;
    shelf.h = Math.max(shelf.h, it.h);
    shelf.items.push(it);
  }
  ctx.wraps.set(key, shelves.map((r) => r.items.length));
  let y = 0;
  shelves.forEach((r, i) => {
    r.y = y;
    r.items.forEach((it) => (it.y = 0));
    y += r.h + (i < shelves.length - 1 ? gap(ctx.gaps, `wr${key}`, rowBase, i) : 0);
  });
  return {
    t: "group",
    key: `wr${key}`,
    axis: "y",
    w: Math.max(0, ...shelves.map((r) => r.w)),
    h: y,
    kids: shelves.map((r) => ({ t: "group", key: `wc${key}`, axis: "x", x: 0, y: r.y, w: r.w, h: r.h, kids: r.items })),
  };
}

// The children of one parent (null: the top level), placed by the groups their dependencies connect.
function childrenBlock(parent, kids, ctx, avail) {
  const key = parent ? parent.id : "root";
  const all = parent ? ctx.showsDone(parent) : ctx.opts.showDone;
  const act = byActivity(ctx.ix);
  const list = kids.slice().sort(act);
  const edges = siblingEdges(list, ctx.ix, all);
  const stage = stagesOf(list, edges);
  const items = [];
  const loose = []; // groups that fold whole: one folded group at the end
  components(list, edges).forEach((members, g) => {
    if (members.every((s) => folds(s, ctx))) loose.push(...members);
    else if (members.length === 1) items.push(ctx.node(members[0], avail));
    else {
      const inside = new Set(members.map((s) => s.id));
      const own = edges.filter(([a, b]) => inside.has(a) && inside.has(b));
      members.sort((a, b) => stage(a) - stage(b) || act(a, b));
      items.push(gridBlock(`${key}~${g}`, members, own, stage, ctx, avail));
    }
  });
  if (loose.length) items.push(chipBlock(`${key}.f`, loose, ctx));
  // iss-00575: the top level wraps where the whole graph shows largest in the view (when it has a height to fit)
  const room = !parent && !ctx.breaks && ctx.opts.height > 0 ? widestRoom(items, ctx.opts, avail) : avail;
  return shelfBlock(key, items, ctx, room, parent ? BASE.wrapRow : BASE.world);
}

// Shelves of the blocks in order, wrapping where one would pass `cap`: the width and the height of the whole.
function shelved(blocks, cap) {
  let w = 0;
  let h = 0;
  let row = null;
  for (const b of blocks) {
    if (!row || (row.n && row.w + BASE.wrapCol + b.w > cap)) {
      if (row) h += row.h + BASE.world;
      row = { w: 0, h: 0, n: 0 };
    }
    row.w = row.n ? row.w + BASE.wrapCol + b.w : b.w;
    row.h = Math.max(row.h, b.h);
    row.n++;
    w = Math.max(w, row.w);
  }
  return { w, h: h + (row ? row.h : 0) };
}

// The width the top level may use (iss-00575 R-01): every cut of the order is a candidate (the widths of the first k
// blocks side by side); the one whose whole graph shows at the largest zoom in the view wins, as "fit" would zoom
// (at most 100%). A tie goes to the smaller whole, then to the narrower row. The blocks keep their own widths.
function widestRoom(blocks, opts, avail) {
  const seenW = Number(opts.width) > 0 ? Number(opts.width) : WRAP_WIDTH;
  const seenH = Number(opts.height);
  if (seenH >= seenW) return avail; // a tall view (a phone) stacks them, as the groups wrap at the width seen
  const m = 2 * SIZE.margin;
  let best = null;
  let run = 0;
  blocks.forEach((b, k) => {
    run += (k ? BASE.wrapCol : 0) + b.w;
    const { w, h } = shelved(blocks, run);
    const zoom = Math.min(1, seenW / (w + m), seenH / (h + m));
    if (!best || zoom > best.zoom + 1e-9 || (Math.abs(zoom - best.zoom) <= 1e-9 && w * h < best.area)) best = { zoom, area: w * h, cap: run };
  });
  return best ? best.cap : seenW;
}

function frameBlock(s, kids, ctx, avail) {
  const [padT, padX, padB] = SIZE.pad[s.kind] || SIZE.pad.epic;
  const body = kids.length ? childrenBlock(s, kids, ctx, avail - 2 * padX) : null;
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

function nest(roots, ctx, avail) {
  const top = childrenBlock(null, roots, ctx, avail);
  return { ...top, x: 0, y: 0 };
}

function tree(roots, ctx) {
  const rows = [];
  const walk = (s, depth) => {
    const kids = ctx.visibleKids(s).slice().sort(byStageActivity(ctx.showsDone(s), ctx.ix));
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
  // a grid cell's step carries its column (slot), shared by every row of the grid
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
  block.kids.forEach((kid, i) => flatten(kid, x, y, [...path, { c: block.key, axis: block.axis, i: kid.slot ?? i }], out));
}

/**
 * Lay the Scopes out.
 * @param scopes  structure API `scopes`
 * @param cleanup structure API `cleanup` ([{id, code, text}])
 * @param options {mode: "nest"|"tree", showDone, deps: "all"|"wait"|"none", fold, focus, width, height} — width: the graph's
 *                visible width at 100% (px), where the groups wrap (WRAP_WIDTH when absent); height: its visible
 *                height (px), with which the top level wraps where the whole shows largest (iss-00575; none: at width)
 * @param gaps    extra pixels per gap key (from earlier routing rounds)
 */
export function layout(scopes, cleanup, options = {}, gaps = {}) {
  const opts = { ...DEFAULTS, ...options };
  if (opts.mode === "tree") opts.fold = false; // the tree shows every Scope as a box
  const ix = index(scopes);
  const focus = opts.focus && ix.byId.has(opts.focus) ? opts.focus : null;
  // A parent shows its done children with "done too", when it is the focus, or when it is open, except an open
  // parent whose every descendant is done (a cleanup candidate: what it holds is no longer the plan's progress).
  const finished = new Set((cleanup || []).filter((c) => c.code === "all_descendants_closed").map((c) => c.id));
  const showsDone = (p) => opts.showDone || p.id === focus || (p.state !== "done" && !finished.has(p.id));
  const visibleBase = visibility(ix, opts, showsDone);
  const inFocus = (s) => !focus || s.id === focus || ix.ancestors(s.id).includes(focus);
  const visible = (s) => inFocus(s) && (s.id === focus || visibleBase(s));
  const visibleKids = (s) => ix.kids.get(s.id).filter(visible);
  // the shelves of the layout without the routing's widening (computed first when there is any widening)
  const breaks = Object.keys(gaps).length && opts.mode !== "tree" ? layout(scopes, cleanup, options, {}).wraps : null;
  const ctx = { opts, gaps, ix, focus, cleanup: new Set((cleanup || []).map((c) => c.id)), visibleKids, showsDone, breaks, wraps: new Map() };
  ctx.node = (s, avail) => {
    const kids = visibleKids(s);
    return s.kind === "issue" && !kids.length ? boxBlock(s, ctx) : frameBlock(s, kids, ctx, avail);
  };
  const isRoot = (s) => (focus ? s.id === focus : !s.parent_id || !ix.byId.has(s.parent_id) || ix.ancestors(s.id).includes(s.id));
  const roots = scopes
    .filter((s) => visible(s) && isRoot(s))
    .sort(byActivity(ix));
  const mx = SIZE.margin + (gaps["margin.x"] || 0);
  const seen = Number(opts.width) > 0 ? Number(opts.width) : WRAP_WIDTH;
  const top = opts.mode === "tree" ? tree(roots, ctx) : nest(roots, ctx, seen - 2 * SIZE.margin);
  const out = { nodes: [], groups: [], trunks: [] };
  const my = SIZE.margin + (gaps["margin.y"] || 0);
  flatten(top, mx, my, [], out);
  const width = top.w + 2 * mx;
  const height = top.h + 2 * my;
  if (opts.mode === "tree") out.trunks = treeLines(out.nodes, ix);
  const edges = pairs(scopes, ix, out, opts);
  return { opts, width, height, nodes: out.nodes, groups: out.groups, trunks: out.trunks, edges, focus, ancestors: focus ? ix.ancestors(focus) : [], wraps: ctx.wraps };
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
  // a crowded entry side may take a port every lane in the nested layout, where a tall box widens its whole row (iss-00578)
  return { obs, frames, edges, bounds: { x1: 0, y1: 0, x2: L.width, y2: L.height }, fineEntries: !tree };
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

// Sides whose lines would sit closer than a lane: how much taller the box or the frame's heading must be (the router
// counts the ports a side can take; a crowded entry side takes one every lane, iss-00578).
function portRoom(G) {
  const add = {};
  for (const [i, need] of portNeed(G)) add[`grow:${G.obs[i].key}`] = need;
  return add;
}

// The routing check's count of problems in one round (router.js audit: box hits, lanes too close, diagonals, ...).
function problems(G, res) {
  const a = audit(
    res.routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: G.obs[G.edges[rt.ei].a].key, kz: G.obs[G.edges[rt.ei].z].key })),
    G.obs,
  );
  return a.boxHits + a.ownHits + a.overlaps + a.diagonal + a.portShare + a.trunkOverlaps + a.failed;
}

// The prototype stopped after 8 rounds. Widening one channel can crowd another, so the rounds do not always settle:
// a large structure (284 lines) needed 9, and another round can also undo a clean one (iss-00544).
export const ROUNDS = 10;

/**
 * Lay out and route, widening the gaps where a channel lacks lanes (at most ROUNDS rounds; the prototype's loop).
 * When the rounds do not settle, the round with the fewest problems in the routing check is kept (the earliest of
 * equals), not the last one. Returns {layout, G, routes, widen, iters, unmapped, gaps, problems}.
 */
export function routeLayout(scopes, cleanup, options = {}, start = {}) {
  const gaps = { ...start };
  let iters = 0;
  let best = null;
  let before = new Set();
  for (; iters < ROUNDS; iters++) {
    const L = layout(scopes, cleanup, options, gaps);
    const G = graphInput(L);
    const res = route(G);
    const add = portRoom(G);
    const settled = !res.widen.length && !Object.keys(add).length;
    const round = { layout: L, G, routes: res.routes, widen: res.widen, unmapped: 0, gaps: { ...gaps }, problems: settled ? 0 : problems(G, res) };
    if (settled) {
      best = round;
      break;
    }
    const now = new Set();
    // A round whose sides lack ports routed lines from squeezed ends: grow the boxes first and judge the channels in the
    // next round (iss-00578: widening from such a round stays and leaves a gap wider than the lines that pass).
    const growing = Object.keys(add).length > 0;
    for (const w of growing ? [] : res.widen) {
      const sig = `${w.axis}|${G.obs[w.oa]?.key ?? w.oa}|${G.obs[w.ob]?.key ?? w.ob}`;
      now.add(sig);
      let keys = gapFor(G, w.axis, w.oa, w.ob, L.opts.mode === "tree");
      if (!keys.length) round.unmapped++;
      // a channel that no gap reaches, or that widening did not relieve: every gap of the axis grows a little
      if (!keys.length || before.has(sig)) keys = [...keys, `all.${w.axis}`];
      for (const key of keys) {
        const amount = key.startsWith("all.") ? Math.min(12, Math.ceil(w.amount / 4) + 2) : Math.ceil(w.amount) + 2;
        add[key] = Math.max(add[key] || 0, amount);
      }
    }
    if (!best || round.problems < best.problems) best = round;
    before = now;
    if (!Object.keys(add).length) break;
    for (const [key, value] of Object.entries(add)) gaps[key] = (gaps[key] || 0) + value;
  }
  return { ...best, iters };
}
