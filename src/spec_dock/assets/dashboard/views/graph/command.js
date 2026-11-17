// The command lines of the structure graph (iss-00616 D-01, D-03): which Orca agent directs which (the summary's
// agents[].parent), where each end sits (a box's or frame's mark, a folded group, the nearest drawn ancestor frame, or
// the command band above every Initiative), and the curves, arcs and ripples the page draws.
// Pure computation like layout.js: no DOM, no clock, no network. The page passes the measured widths of the marks and
// the order it drew them; this module never measures.
import { matchWorktrees, normPath, summaryValid } from "../../core/orca_match.js";
import { SIZE } from "./layout.js";

// --- D-01: the pairs and where their ends sit ----------------------------------------------------------------

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const refOf = (agent, worktree) => ({
  id: agent.id,
  mark: agent.mark,
  workingMode: agent.workingMode,
  agentType: agent.agentType,
  detail: agent.detail,
  worktree,
});
const byText = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

/**
 * The command pairs of the summary: [{parent: AgentRef, child: AgentRef}], one per (parent, child), ordered by the
 * child's id, then the parent's. A parent that is not an object, whose id is not a string, is the agent itself or is
 * not in the summary makes no pair (F-02). Each agent counts once, so a cycle simply ends.
 */
export function commandPairs(summary) {
  if (!summaryValid(summary)) return [];
  const byId = new Map();
  for (const worktree of summary.worktrees) {
    if (!isObject(worktree) || !Array.isArray(worktree.agents)) continue;
    for (const agent of worktree.agents) {
      if (!isObject(agent) || typeof agent.id !== "string" || byId.has(agent.id)) continue;
      byId.set(agent.id, { raw: agent, ref: refOf(agent, worktree) });
    }
  }
  const pairs = [];
  for (const [id, { raw, ref }] of byId) {
    const parent = raw.parent;
    if (!isObject(parent) || typeof parent.id !== "string" || parent.id === id || !byId.has(parent.id)) continue;
    pairs.push({ parent: byId.get(parent.id).ref, child: ref });
  }
  return pairs.sort((a, b) => byText(a.child.id, b.child.id) || byText(a.parent.id, b.parent.id));
}

/**
 * This repository's worktrees of the summary (the same rule as matchWorktrees): a path the structure lists, or the
 * project of such a worktree. null when the structure's list of worktrees was not read or the summary is invalid (F-01).
 */
export function ownWorktrees(structure, summary) {
  if (structure?.worktrees?.status !== "ok" || !Array.isArray(structure.worktrees.paths) || !summaryValid(summary)) return null;
  const paths = new Set(structure.worktrees.paths.map(normPath).filter((p) => p !== null));
  const listed = summary.worktrees.filter((w) => isObject(w) && paths.has(normPath(w.path)));
  const projects = new Set(listed.map((w) => w.project?.id).filter((id) => typeof id === "string"));
  return new Set(summary.worktrees.filter((w) => isObject(w) && (paths.has(normPath(w.path)) || projects.has(w.project?.id))));
}

/** The band's key of each worktree: its id, with the path when two worktrees share the id. */
function bandKeys(summary) {
  const list = summary.worktrees.filter(isObject);
  const count = new Map();
  for (const w of list) count.set(w.id, (count.get(w.id) || 0) + 1);
  return new Map(list.map((w, i) => {
    const id = typeof w.id === "string" ? w.id : `#${i}`;
    return [w, count.get(w.id) > 1 || typeof w.id !== "string" ? `${id}|${w.path}` : id];
  }));
}

/**
 * Where each end of the pairs sits. Drops the pairs whose two ends are both in other repositories (R-01).
 * Place: {kind: "mark", node, scope} | {kind: "group", group} | {kind: "frame", node} | {kind: "band", key}.
 * @returns {pairs, places: Map<agent id, Place>, own: Set<worktree>} or null when own is null (F-01)
 */
export function placeAgents(pairs, { structure, summary, layout, ix }) {
  const own = ownWorktrees(structure, summary);
  if (!own) return null;
  const kept = pairs.filter((p) => own.has(p.parent.worktree) || own.has(p.child.worktree));
  const scopeOf = new Map();
  for (const [scope, list] of matchWorktrees(structure, summary).byScope)
    for (const w of list) if (!scopeOf.has(w)) scopeOf.set(w, scope);
  const nodes = new Map((layout?.nodes || []).map((n) => [n.id, n]));
  // a folded group holds its members and their descendants that are not drawn as nodes (layout.js pairs)
  const groupOf = new Map();
  for (const g of layout?.groups || []) {
    for (const id of g.ids) {
      groupOf.set(id, g);
      const stack = [...(ix?.kids?.get(id) || [])];
      while (stack.length) {
        const k = stack.pop();
        if (nodes.has(k.id) || groupOf.has(k.id)) continue;
        groupOf.set(k.id, g);
        stack.push(...(ix.kids.get(k.id) || []));
      }
    }
  }
  const keys = bandKeys(summary);
  const placeOf = (ref) => {
    const scope = scopeOf.get(ref.worktree);
    if (scope !== undefined) {
      if (nodes.has(scope)) return { kind: "mark", node: nodes.get(scope), scope };
      if (groupOf.has(scope)) return { kind: "group", group: groupOf.get(scope) };
      for (const a of ix?.ancestors?.(scope) || []) if (nodes.has(a)) return { kind: "frame", node: nodes.get(a) };
    }
    return { kind: "band", key: keys.get(ref.worktree) };
  };
  const places = new Map();
  for (const p of kept) for (const ref of [p.parent, p.child]) if (!places.has(ref.id)) places.set(ref.id, placeOf(ref));
  return { pairs: kept, places, own };
}

/** The band's label of a worktree (R-02, F-03). */
export function bandLabel(worktree, own) {
  const branch = typeof worktree?.branch === "string" && worktree.branch ? worktree.branch : "ブランチ不明";
  if (own) return worktree?.main === true ? "main のチェックアウト" : branch;
  const name = typeof worktree?.project?.name === "string" && worktree.project.name ? worktree.project.name : "ほかのリポジトリ";
  return `${name} · ${branch}`;
}

/**
 * The band's items: the ends placed in the band, one item per worktree, this repository's main checkout first, then
 * this repository's other worktrees and then the other repositories (each by label). The agents of an item follow
 * orderOf(worktree) (the component's orderAgents; the summary's order without it).
 * @returns [{key, label, own, main, worktree, agents: [AgentRef]}]
 */
export function bandItems(pairs, places, own, orderOf) {
  const items = new Map();
  for (const p of pairs) {
    for (const ref of [p.parent, p.child]) {
      const place = places.get(ref.id);
      if (place?.kind !== "band") continue;
      if (!items.has(place.key)) items.set(place.key, { key: place.key, worktree: ref.worktree, refs: new Map() });
      items.get(place.key).refs.set(ref.id, ref);
    }
  }
  const out = [...items.values()].map((it) => {
    const mine = own.has(it.worktree);
    const order = (typeof orderOf === "function" ? orderOf(it.worktree) : null) || it.worktree.agents || [];
    const ids = order.map((a) => (typeof a === "string" ? a : a?.id)).filter((id) => it.refs.has(id));
    for (const id of it.refs.keys()) if (!ids.includes(id)) ids.push(id);
    return {
      key: it.key,
      label: bandLabel(it.worktree, mine),
      own: mine,
      main: mine && it.worktree.main === true,
      worktree: it.worktree,
      agents: [...new Set(ids)].map((id) => it.refs.get(id)),
    };
  });
  const rank = (it) => (it.main ? 0 : it.own ? 1 : 2);
  return out.sort((a, b) => rank(a) - rank(b) || byText(a.label, b.label) || byText(a.key, b.key));
}

// --- D-03: the band's size, the ends, the curves and the arcs ------------------------------------------------

// The band above the layout, on the negative side of the world's y (decisions): graph.css draws the items with the same
// border, padding and widths (.gx-band-item, .gx-band-lab, .gx-band-agent): change them together.
export const BAND = { top: -16, h: 28, left: SIZE.margin, border: 1, pad: 6, gap: 10, labelGap: 6, slot: 52 };
const SPREAD = 10; // lines leaving one edge of a group or frame are this far apart
const CHORD = 40; // an arc's ends are at least this far apart
const ARC_D = 16; // an arc's bulge
const ARC_MIN = 8;
const FRAME_ARC_D = 12; // the arc below a nested frame's heading

/** A label's width estimated from its characters: ASCII 6.6px, others 11.5px, within 24..200 (CSS cuts it with …). */
export function labelWidth(text) {
  let w = 0;
  for (const ch of String(text ?? "")) w += ch.codePointAt(0) < 128 ? 6.6 : 11.5;
  return Math.min(200, Math.max(24, Math.ceil(w)));
}

function bandModel(items) {
  if (!items.length) return null;
  let x = BAND.left;
  const out = items.map((it) => {
    const lw = labelWidth(it.label);
    const w = 2 * BAND.border + 2 * BAND.pad + lw + BAND.labelGap + BAND.slot * it.agents.length;
    const left = x + BAND.border + BAND.pad + lw + BAND.labelGap;
    const item = {
      ...it,
      x, y: BAND.top, w, h: BAND.h, labelWidth: lw,
      agents: it.agents.map((ref, i) => ({ id: ref.id, ref, x: left + BAND.slot * i, y: BAND.top, w: BAND.slot, h: BAND.h })),
    };
    x += w + BAND.gap;
    return item;
  });
  return { top: BAND.top, h: BAND.h, items: out, right: x - BAND.gap };
}

const r1 = (v) => Math.round(v * 10) / 10;
const pt = (p) => `${r1(p.x)} ${r1(p.y)}`;
const rectOf = (o) => ({ x1: o.x1, y1: o.y1, x2: o.x2, y2: o.y2 });
const contains = (r, p) => p.x >= r.x1 && p.x <= r.x2 && p.y >= r.y1 && p.y <= r.y2;
const holds = (p, q) => p.x1 <= q.x1 + 0.01 && p.y1 <= q.y1 + 0.01 && p.x2 >= q.x2 - 0.01 && p.y2 >= q.y2 - 0.01;
const center = (r) => ({ x: (r.x1 + r.x2) / 2, y: (r.y1 + r.y2) / 2 });
const isBox = (n) => n.type === "box" || n.type === "tframe";

/** The cubic Bézier's length as a polyline of 24 pieces. */
function bezierLength(p0, c1, c2, p3) {
  let len = 0;
  let prev = p0;
  for (let i = 1; i <= 24; i++) {
    const t = i / 24, u = 1 - t;
    const q = {
      x: u * u * u * p0.x + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * p3.x,
      y: u * u * u * p0.y + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * p3.y,
    };
    len += Math.hypot(q.x - prev.x, q.y - prev.y);
    prev = q;
  }
  return len;
}
// one round of the flowing dots is 8px (graph.css): the length rounds up to a multiple of 8
const roundLen = (len) => Math.max(8, Math.ceil(len / 8) * 8);

function cubic(P, dP, C, dC, k) {
  const c1 = { x: P.x + dP.x * k, y: P.y + dP.y * k };
  const c2 = { x: C.x + dC.x * k, y: C.y + dC.y * k };
  return { d: `M ${pt(P)} C ${pt(c1)} ${pt(c2)} ${pt(C)}`, len: roundLen(bezierLength(P, c1, c2, C)) };
}

const SIDES = {
  top: { n: { x: 0, y: -1 }, at: (r) => ({ x: (r.x1 + r.x2) / 2, y: r.y1 }), along: "x" },
  bottom: { n: { x: 0, y: 1 }, at: (r) => ({ x: (r.x1 + r.x2) / 2, y: r.y2 }), along: "x" },
  left: { n: { x: -1, y: 0 }, at: (r) => ({ x: r.x1, y: (r.y1 + r.y2) / 2 }), along: "y" },
  right: { n: { x: 1, y: 0 }, at: (r) => ({ x: r.x2, y: (r.y1 + r.y2) / 2 }), along: "y" },
};
const DOWN = { x: 0, y: 1 };

/**
 * The drawing of the command lines (iss-00616 D-03).
 * @param pairs   placeAgents' pairs
 * @param places  placeAgents' places
 * @param items   bandItems
 * @param layout  the layout (nodes, groups, width, height)
 * @param spotsOf node -> markSpots(node, …) or null
 * @param routes  the dependency lines' routes ([{pts: [{x, y}]}]), for the arcs' check
 * @returns {band, links, ripples, audit, top, width}
 */
export function commandModel({ pairs = [], places = new Map(), items = [], layout = {}, spotsOf = () => null, routes = [] }) {
  const band = bandModel(items);
  const nodes = layout.nodes || [];
  const groups = layout.groups || [];
  const bandAgent = new Map();
  for (const it of band?.items || []) for (const a of it.agents) bandAgent.set(`${it.key}\n${a.id}`, { item: it, slot: a });
  const spotCache = new Map();
  const spotOf = (node, id) => {
    if (!spotCache.has(node)) spotCache.set(node, spotsOf(node) || null);
    return spotCache.get(node)?.find((s) => s.id === id) || null;
  };
  const audit = { links: 0, arcs: 0, boxOverlaps: 0, edgeOverlaps: 0, crowded: 0 };
  // the rectangles an arc's bulge must not enter: every node, group and band item but its own and the frames holding it
  const obstacles = [
    ...nodes.map((n) => ({ ...rectOf(n), self: n })),
    ...groups.map((g) => ({ ...rectOf(g), self: g })),
    ...(band?.items || []).map((it) => ({ x1: it.x, y1: it.y, x2: it.x + it.w, y2: it.y + it.h, self: it })),
  ];
  const others = (self) => {
    const own = self && !band?.items.includes(self) ? rectOf(self) : null;
    return obstacles.filter((o) => o.self !== self && !(own && o.self.type === "frame" && holds(o, own)));
  };
  const overlapsBox = (bb, self) => others(self).some((o) => Math.min(bb.x2, o.x2) - Math.max(bb.x1, o.x1) > 0 && Math.min(bb.y2, o.y2) - Math.max(bb.y1, o.y1) > 0);
  // the dependency lines' runs parallel to an edge (along x: horizontal runs) inside the bulge's box
  const overlapsRoute = (bb, along) => routes.some((rt) => (rt.pts || []).some((p, k, pts) => {
    const q = pts[k + 1];
    if (!q) return false;
    if (along === "x") return p.y === q.y && p.y >= bb.y1 && p.y <= bb.y2 && Math.min(bb.x2, Math.max(p.x, q.x)) - Math.max(bb.x1, Math.min(p.x, q.x)) > 0;
    return p.x === q.x && p.x >= bb.x1 && p.x <= bb.x2 && Math.min(bb.y2, Math.max(p.y, q.y)) - Math.max(bb.y1, Math.min(p.y, q.y)) > 0;
  }));
  // the room outside an edge of `self` across [lo, hi]: up to the nearest facing node, group or band item, the inner
  // edge of a frame holding it, the world's bounds
  const roomOf = (self, side, lo, hi) => {
    const r = rectOf(self);
    const own = isBox(self) || self.type === "frame" ? r : null;
    let room = Infinity;
    const world = { x1: 0, y1: 0, x2: layout.width ?? Infinity, y2: layout.height ?? Infinity };
    const holders = [world, ...nodes.filter((n) => n !== self && n.type === "frame" && own && holds(n, own)).map((n) => ({ x1: n.x1 + 1, y1: n.y1 + 1, x2: n.x2 - 1, y2: n.y2 - 1 }))];
    for (const h of holders) {
      if (side === "bottom") room = Math.min(room, h.y2 - r.y2);
      if (side === "right") room = Math.min(room, h.x2 - r.x2);
    }
    for (const o of others(self)) {
      if (o.self.type === "frame" && own && holds(o, own)) continue;
      if (side === "bottom" && o.x1 < hi && o.x2 > lo && o.y1 >= r.y2) room = Math.min(room, o.y1 - r.y2);
      if (side === "right" && o.y1 < hi && o.y2 > lo && o.x1 >= r.x2) room = Math.min(room, o.x1 - r.x2);
    }
    return room;
  };

  // the end of a placed agent that does not depend on the other end: a mark (box, frame heading) or the band
  const fixedEnd = (ref) => {
    const place = places.get(ref.id);
    if (!place) return null;
    if (place.kind === "band") {
      const hit = bandAgent.get(`${place.key}\n${ref.id}`);
      if (!hit) return null;
      const cx = hit.slot.x + hit.slot.w / 2;
      return { kind: "band", item: hit.item, slot: hit.slot, p: { x: cx, y: BAND.top + BAND.h }, n: DOWN, spot: { x: hit.slot.x, y: hit.slot.y, w: hit.slot.w, h: hit.slot.h } };
    }
    if (place.kind === "mark") {
      const node = place.node;
      const spot = spotOf(node, ref.id);
      if (!spot) {
        // F-04: the position is not known: the middle of the edge near the row of marks
        const side = isBox(node) ? "bottom" : "top";
        return { kind: "edge", node, p: SIDES[side].at(node), n: SIDES[side].n, spot: null, unknown: true };
      }
      const cx = spot.x + spot.w / 2;
      if (isBox(node)) {
        return { kind: "mark", node, spot, p: { x: cx, y: node.y2 }, n: DOWN, stubs: [`M ${pt({ x: cx, y: spot.y + spot.h })} L ${pt({ x: cx, y: node.y2 })}`] };
      }
      return { kind: "mark", node, spot, p: { x: cx, y: spot.y + spot.h }, n: DOWN, stubs: [] };
    }
    return { kind: place.kind, rect: place.kind === "group" ? place.group : place.node, place };
  };
  // the side of a rectangle facing q (the larger of the two axes), or the inner bottom of a frame holding q
  const faceOf = (end, q) => {
    const r = end.rect;
    if (end.kind === "frame" && contains(r, q)) return { side: "inside", p: { x: (r.x1 + r.x2) / 2, y: r.y2 - 1 }, n: { x: 0, y: -1 } };
    const c = center(r);
    const dx = q.x - c.x, dy = q.y - c.y;
    const side = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "right" : "left") : dy > 0 ? "bottom" : "top";
    return { side, p: SIDES[side].at(r), n: SIDES[side].n };
  };

  const links = [];
  const loose = []; // the ends on an edge of a group or frame, spread along the edge afterwards
  const ripples = new Map();
  for (const pair of pairs) {
    const a = fixedEnd(pair.parent);
    const b = fixedEnd(pair.child);
    if (!a || !b) continue;
    const id = `${pair.parent.id}>${pair.child.id}`;
    const cm = pair.child.mark;
    const state = cm === "working" ? "flow" : cm === "done" ? "done" : "wait";
    if (a.spot && (a.kind === "mark" || a.kind === "band") && !ripples.has(pair.parent.id)) {
      ripples.set(pair.parent.id, { agent: pair.parent.id, x: a.spot.x + a.spot.w / 2, y: a.spot.y + a.spot.h / 2 });
    }
    const loosen = (e) => e.kind === "group" || e.kind === "frame";
    if (loosen(a) && loosen(b) && a.rect === b.rect) continue; // the same group or ancestor frame: no line
    const sameNode = a.node && a.node === b.node;
    const sameItem = a.kind === "band" && b.kind === "band" && a.item === b.item;
    if (sameNode || sameItem) {
      if (!a.spot || !b.spot || a.unknown || b.unknown) continue; // F-04: no arc without both marks
      const arc = sameItem ? bandArc(a, b) : isBox(a.node) ? boxArc(a, b) : frameArc(a, b);
      audit.arcs++;
      audit.links++;
      links.push({ id, parent: pair.parent.id, child: pair.child.id, state, kind: "arc", ...arc.out, from: arc.from, to: arc.to });
      continue;
    }
    const link = { id, parent: pair.parent.id, child: pair.child.id, state, kind: "curve", a, b, stubs: [...(a.stubs || []), ...(b.stubs || [])] };
    for (const [e, other] of [[a, b], [b, a]]) {
      if (!loosen(e)) continue;
      const q = loosen(other) ? center(other.rect) : other.p;
      Object.assign(e, faceOf(e, q));
      loose.push({ e, key: `${e.kind}:${e.rect.key ?? e.rect.id}:${e.side}`, id, along: e.side === "left" || e.side === "right" ? "y" : "x" });
    }
    links.push(link);
    audit.links++;
  }
  // spread the ends leaving one edge, 10px apart in the links' order
  const byEdge = new Map();
  for (const l of loose) {
    if (!byEdge.has(l.key)) byEdge.set(l.key, []);
    byEdge.get(l.key).push(l);
  }
  for (const list of byEdge.values()) {
    list.sort((x, y) => byText(x.id, y.id));
    list.forEach((l, i) => {
      const off = (i - (list.length - 1) / 2) * SPREAD;
      l.e.p = { ...l.e.p, [l.along]: l.e.p[l.along] + off };
    });
  }
  const out = links.map((l) => {
    if (l.kind === "arc") return l;
    const P = l.a.p, C = l.b.p;
    const L = Math.hypot(C.x - P.x, C.y - P.y);
    const k = Math.min(140, Math.max(24, 0.45 * L));
    const { d, len } = cubic(P, l.a.n, C, l.b.n, k);
    return { id: l.id, parent: l.parent, child: l.child, state: l.state, kind: "curve", d, len, stubs: l.stubs, from: { x: r1(P.x), y: r1(P.y) }, to: { x: r1(C.x), y: r1(C.y) } };
  });

  // --- the arcs (Epic D-10, iss-00616 D-03) ---
  function widen(e1, e2, along, lo, hi) {
    const span = Math.abs(e2[along] - e1[along]);
    if (span >= CHORD) return [e1, e2];
    const first = e1[along] <= e2[along];
    let mid = (e1[along] + e2[along]) / 2;
    mid = Math.min(hi - CHORD / 2, Math.max(lo + CHORD / 2, mid));
    const low = mid - CHORD / 2, high = mid + CHORD / 2;
    return first ? [{ ...e1, [along]: low }, { ...e2, [along]: high }] : [{ ...e1, [along]: high }, { ...e2, [along]: low }];
  }
  // the box of an arc's bulge: its ends and d out of the edge (the cubic with handles 4d/3 peaks at d)
  function bulgeBox(e1, e2, n, d) {
    const xs = [e1.x, e2.x, e1.x + n.x * d, e2.x + n.x * d];
    const ys = [e1.y, e2.y, e1.y + n.y * d, e2.y + n.y * d];
    return { x1: Math.min(...xs), y1: Math.min(...ys), x2: Math.max(...xs), y2: Math.max(...ys) };
  }
  function arcOut(e1, e2, n, d, stubs) {
    const { d: path, len } = cubic(e1, n, e2, n, (4 * d) / 3);
    return { out: { d: path, len, stubs, bulge: d }, from: { x: r1(e1.x), y: r1(e1.y) }, to: { x: r1(e2.x), y: r1(e2.y) } };
  }
  function boxArc(a, b) {
    const node = a.node;
    const sameRow = a.spot.y === b.spot.y;
    const trySide = (side) => {
      const along = side === "bottom" ? "x" : "y";
      const mid = (s) => ({ x: s.x + s.w / 2, y: s.y + s.h / 2 });
      const base = (s) => (side === "bottom" ? { x: mid(s).x, y: node.y2 } : { x: node.x2, y: mid(s).y });
      const [e1, e2] = widen(base(a.spot), base(b.spot), along, along === "x" ? node.x1 : node.y1, along === "x" ? node.x2 : node.y2);
      const lo = Math.min(e1[along], e2[along]), hi = Math.max(e1[along], e2[along]);
      const d = Math.min(ARC_D, roomOf(node, side, lo, hi) - 3);
      const n = SIDES[side].n;
      const stub = (s, e) => {
        const m = mid(s);
        if (side === "bottom") return `M ${pt({ x: m.x, y: s.y + s.h })} L ${pt({ x: m.x, y: node.y2 })}${m.x !== e.x ? ` L ${pt(e)}` : ""}`;
        return `M ${pt({ x: s.x + s.w, y: m.y })} L ${pt({ x: node.x2, y: m.y })}${m.y !== e.y ? ` L ${pt(e)}` : ""}`;
      };
      return { side, e1, e2, n, d, along, stubs: [stub(a.spot, e1), stub(b.spot, e2)] };
    };
    const sides = sameRow ? ["bottom", "right"] : ["right", "bottom"];
    const tries = sides.map(trySide).map((t) => ({ ...t, ok: t.d >= ARC_MIN, over: t.d >= ARC_MIN && overlapsRoute(bulgeBox(t.e1, t.e2, t.n, t.d), t.along) }));
    // a clean edge first; else the first edge with room, its run of a dependency line counted; else the first edge at
    // the least bulge, counted as crowded
    let pick = tries.find((t) => t.ok && !t.over);
    if (!pick) {
      pick = tries.find((t) => t.ok);
      if (!pick) {
        audit.crowded++;
        pick = { ...tries[0], d: ARC_MIN };
      }
      if (overlapsRoute(bulgeBox(pick.e1, pick.e2, pick.n, pick.d), pick.along)) audit.edgeOverlaps++;
    }
    if (overlapsBox(bulgeBox(pick.e1, pick.e2, pick.n, pick.d), node)) audit.boxOverlaps++;
    return arcOut(pick.e1, pick.e2, pick.n, pick.d, pick.stubs);
  }
  function frameArc(a, b) {
    const node = a.node;
    const base = (s) => ({ x: s.x + s.w / 2, y: s.y + s.h });
    const [e1, e2] = widen(base(a.spot), base(b.spot), "x", node.x1 + 1, node.x2 - 1);
    const bb = bulgeBox(e1, e2, DOWN, FRAME_ARC_D);
    if (overlapsRoute(bb, "x")) audit.edgeOverlaps++;
    if (overlapsBox(bb, node)) audit.boxOverlaps++;
    return arcOut(e1, e2, DOWN, FRAME_ARC_D, []);
  }
  function bandArc(a, b) {
    const up = SIDES.top.n;
    const e1 = { x: a.p.x, y: BAND.top }, e2 = { x: b.p.x, y: BAND.top };
    const bb = bulgeBox(e1, e2, up, ARC_D);
    if (overlapsBox(bb, a.item)) audit.boxOverlaps++;
    return arcOut(e1, e2, up, ARC_D, []);
  }

  const right = band ? band.right + SIZE.margin : 0;
  return {
    band,
    links: out,
    ripples: [...ripples.values()],
    audit,
    top: band ? BAND.top - 16 : 0,
    width: Math.max(layout.width || 0, right),
  };
}

// --- R-08: the key of the inputs --------------------------------------------------------------------------------

const ids = new WeakMap();
let next = 0;
const idOf = (o) => {
  if (o === null || typeof o !== "object") return String(o);
  if (!ids.has(o)) ids.set(o, ++next);
  return `#${ids.get(o)}`;
};

/**
 * The same string for the same inputs: the summary object, the routing object (V.EG), the measured widths and the
 * recorded ids of the marks used, and BAND. The page draws again only when it changes.
 */
export function commandKey({ summary, routing, marks, ids: order }) {
  return [idOf(summary), idOf(routing), JSON.stringify(marks ?? null), JSON.stringify(order ?? null), JSON.stringify(BAND)].join("|");
}
