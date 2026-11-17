// The cross-repository structure's frames (iss-00614 D-03; Epic epic-00612 D-04): from the list API's repositories,
// their parents, and each one's laid-out structure graph, the rectangles of the repository frames nested as their
// main checkouts' paths contain one another, which to show in the chosen range, and the band each frame can
// take later between its heading and its contents.
// Inside a frame, below its heading, warnings and band, its own graph comes first and its children follow in the
// list's order, left to right in rows no wider than the frame's usable width (iss-00629 D-01): a child that fits sits
// right of the graph. A frame without a graph (loading, no Scope, nothing in this range) puts its children below its
// line. Sibling frames, the top level included, wrap the same way.
// Pure computation: no DOM, the same px as graph/layout.js. Each repository's graph inside keeps its own layout and
// its own margin (SIZE.margin); this module only places the frames around them.

// The frame's sizes (px). Copies of allgraph.css: change them together.
export const REPO = {
  head: 40, // the heading row (.ax-head)
  warn: 24, // one warning's row (.ax-warn li)
  line: 28, // one line of text as the contents: loading, no Scope, nothing in this range (.ax-line)
  pad: 16, // inside the frame: left, right and bottom, and between a line of text and the shelf of children
  gap: 16, // between sibling frames, across and down
  minW: 360, // the least width the contents can use
  headW: 280, // the heading's least width
  margin: 8, // around the world
};

/** The width the contents of a frame at `depth` (the top is 0) can use when the graph area is `width` wide. */
export function bodyWidth(width, depth) {
  return Math.max(REPO.minW, width - 2 * REPO.margin - 2 * REPO.pad * (depth + 1));
}

const sizeOf = (sizes, key) => (sizes instanceof Map ? sizes.get(key) : sizes?.[key]) || { status: "loading" };

// The parent of every listed repository: one in the same list, else none; one whose parents lead back to itself is at
// the top (F-03), so every repository is drawn once.
function parents(repos) {
  const listed = new Map(repos.map((r) => [r.repository, r.parent ?? null]));
  const out = new Map();
  for (const [key, parent] of listed) {
    let p = listed.has(parent) && parent !== key ? parent : null;
    const seen = new Set([key]);
    for (let q = p; q; q = listed.has(listed.get(q)) ? listed.get(q) : null) {
      if (seen.has(q)) {
        if (q === key) p = null;
        break;
      }
      seen.add(q);
    }
    out.set(key, p);
  }
  return out;
}

// What the contents are (D-03's table): the kind and its height, one for every (range, status, shown, scopes).
function bodyOf(size, range) {
  const next = range === "next";
  if (size.status === "failed") return { kind: "failed", w: 0, h: 0 };
  if (size.status !== "ok") return { kind: "loading", w: 0, h: REPO.line };
  if ((size.shown || 0) > 0) return { kind: "graph", w: size.w || 0, h: size.h || 0 };
  const kind = (size.scopes || 0) > 0 ? "quiet" : "empty";
  return { kind, w: 0, h: next ? 0 : REPO.line };
}

// Pack frames of the given sizes left to right in rows no wider than `limit` (a frame wider than it has a row of
// its own): their offsets and the shelf's size.
function pack(items, limit) {
  const at = [];
  let x = 0;
  let y = 0;
  let rowH = 0;
  let w = 0;
  for (const it of items) {
    if (x > 0 && x + REPO.gap + it.w > limit) {
      y += rowH + REPO.gap;
      x = 0;
      rowH = 0;
    }
    if (x > 0) x += REPO.gap;
    at.push({ x, y });
    x += it.w;
    rowH = Math.max(rowH, it.h);
    w = Math.max(w, x);
  }
  return { at, w, h: items.length ? y + rowH : 0 };
}

/**
 * The repository frames.
 * @param repos   the list API's repositories in its order: [{repository, parent, …}]
 * @param sizes   key → {status: "loading"|"failed"|"ok", w, h, shown, scopes, warns, alerts} (a Map or an object;
 *                a missing key is loading)
 * @param options {range, width: the graph area's width at 100%, bands: key → the band's height (px, missing is 0)}
 * @returns {frames: Map(key → frame), order: [the keys shown, depth first, a parent before its children], width, height}
 */
export function compose(repos, sizes = {}, options = {}) {
  const range = options.range || "next";
  const width = options.width || 1240;
  const bands = options.bands || {};
  const parentOf = parents(repos);
  const kids = new Map([[null, []]]);
  for (const r of repos) kids.set(r.repository, []);
  for (const r of repos) kids.get(parentOf.get(r.repository)).push(r.repository);

  // Sizes, children first: whether each is shown, its frame's width and height, and its parts relative to it.
  const box = new Map();
  const measure = (key, depth) => {
    const size = sizeOf(sizes, key);
    const shown = kids.get(key).map((k) => measure(k, depth + 1)).filter(Boolean);
    const alerts = size.status === "ok" ? size.alerts || 0 : 0;
    const visible =
      range !== "next" || size.status !== "ok" || (size.shown || 0) > 0 || alerts > 0 || shown.length > 0;
    if (!visible) return null;
    const body = bodyOf(size, range);
    const warnH = (size.warns || 0) * REPO.warn;
    const bandH = Math.max(0, Number(bands[key]) || 0);
    const bodyY = REPO.head + warnH + bandH;
    const limit = bodyWidth(width, depth);
    let at;
    let h;
    let w;
    if (body.kind === "graph") {
      // the graph and the children in one flow: the graph is its first item, at (0, 0)
      const flow = pack([body, ...shown], limit);
      at = flow.at.slice(1).map((o) => ({ x: o.x, y: bodyY + o.y }));
      h = bodyY + flow.h + REPO.pad;
      w = Math.max(REPO.headW, flow.w) + 2 * REPO.pad;
    } else {
      const shelf = pack(shown, limit);
      const shelfY = bodyY + body.h + (body.h > 0 ? REPO.pad : 0);
      at = shelf.at.map((o) => ({ x: o.x, y: shelfY + o.y }));
      h = (shown.length ? shelfY + shelf.h : bodyY + body.h) + REPO.pad;
      w = Math.max(REPO.headW, body.w, shelf.w) + 2 * REPO.pad;
    }
    const b = { key, depth, w, h, warnH, bandH, bodyY, body, shown, at };
    box.set(key, b);
    return b;
  };
  const tops = kids.get(null).map((k) => measure(k, 0)).filter(Boolean);
  const top = pack(tops, width - 2 * REPO.margin);

  const frames = new Map();
  const order = [];
  const place = (b, x1, y1) => {
    const x2 = x1 + b.w;
    const y2 = y1 + b.h;
    const head = { x1, y1, x2, y2: y1 + REPO.head };
    const warn = { x1, y1: head.y2, x2, y2: head.y2 + b.warnH };
    const band = { x1, y1: warn.y2, x2, y2: warn.y2 + b.bandH };
    const body = { kind: b.body.kind, x: x1 + REPO.pad, y: y1 + b.bodyY, w: b.body.kind === "graph" ? b.body.w : 0, h: b.body.h };
    frames.set(b.key, { key: b.key, depth: b.depth, x1, y1, x2, y2, head, warn, band, body });
    order.push(b.key);
    b.shown.forEach((k, i) => place(k, x1 + REPO.pad + b.at[i].x, y1 + b.at[i].y));
  };
  tops.forEach((b, i) => place(b, REPO.margin + top.at[i].x, REPO.margin + top.at[i].y));
  return { frames, order, width: top.w + 2 * REPO.margin, height: top.h + 2 * REPO.margin };
}
