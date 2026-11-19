// The command lines of the structure graph (iss-00616 D-01, D-03): which Orca agent directs which (the summary's
// agents[].parent), where each end sits (a box's or frame's mark, a folded group, the nearest drawn ancestor frame, or
// the command band above every Initiative), and the curves, arcs and ripples the page draws.
// Pure computation like layout.js: no DOM, no clock, no network. The page passes the measured widths of the marks and
// the order it drew them; this module never measures.
import { matchWorktrees, normPath, summaryValid } from "../../core/orca_match.js";
import { SIZE } from "./layout.js";

// --- D-01: the pairs and where their ends sit ----------------------------------------------------------------

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
/** An agent of the summary as a command line's end: its marks and its worktree (the summary's own object). */
export const agentRef = (agent, worktree) => ({
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
      byId.set(agent.id, { raw: agent, ref: agentRef(agent, worktree) });
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
export function bandKeys(summary) {
  const list = summary.worktrees.filter(isObject);
  const count = new Map();
  for (const w of list) count.set(w.id, (count.get(w.id) || 0) + 1);
  return new Map(list.map((w, i) => {
    const id = typeof w.id === "string" ? w.id : `#${i}`;
    return [w, count.get(w.id) > 1 || typeof w.id !== "string" ? `${id}|${w.path}` : id];
  }));
}

/**
 * The place of an agent of the summary in one repository's layout (iss-00617 D-01): its worktree's Scope's mark, the
 * folded group holding it, the nearest drawn ancestor frame, or the band. placeAgents and the cross-repository
 * structure (allgraph/command.js) use the same rule.
 * Place: {kind: "mark", node, scope} | {kind: "group", group} | {kind: "frame", node} | {kind: "band", key}.
 * @returns (ref) => Place
 */
export function placer({ structure, summary, layout, ix }) {
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
  const keys = summaryValid(summary) ? bandKeys(summary) : new Map();
  return (ref) => {
    const scope = scopeOf.get(ref.worktree);
    if (scope !== undefined) {
      if (nodes.has(scope)) return { kind: "mark", node: nodes.get(scope), scope };
      if (groupOf.has(scope)) return { kind: "group", group: groupOf.get(scope) };
      for (const a of ix?.ancestors?.(scope) || []) if (nodes.has(a)) return { kind: "frame", node: nodes.get(a) };
    }
    return { kind: "band", key: keys.get(ref.worktree) };
  };
}

/**
 * Where each end of the pairs sits. Drops the pairs whose two ends are both in other repositories (R-01).
 * @returns {pairs, places: Map<agent id, Place>, own: Set<worktree>} or null when own is null (F-01)
 */
export function placeAgents(pairs, { structure, summary, layout, ix }) {
  const own = ownWorktrees(structure, summary);
  if (!own) return null;
  const kept = pairs.filter((p) => own.has(p.parent.worktree) || own.has(p.child.worktree));
  const placeOf = placer({ structure, summary, layout, ix });
  const places = new Map();
  for (const p of kept) for (const ref of [p.parent, p.child]) if (!places.has(ref.id)) places.set(ref.id, placeOf(ref));
  return { pairs: kept, places, own };
}

/**
 * The band's label of a worktree (iss-00616 R-02, F-03; iss-00668 D-03): this repository's worktree by its branch (the
 * main checkout too: its Primary badge says what it is), a detached one of git by its HEAD, another repository's with
 * its project's name.
 */
export function bandLabel(worktree, own) {
  const named = typeof worktree?.branch === "string" && worktree.branch;
  const head = typeof worktree?.head === "string" && worktree.head ? worktree.head : null;
  const branch = named ? worktree.branch : head ? `detached @${head.slice(0, 7)}` : "ブランチ不明";
  if (own) return branch;
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
// iss-00668 D-03: an item's agents wrap after perLine, each further line lineH lower (the item grows; nothing hides).
export const BAND = { top: -16, h: 28, left: SIZE.margin, border: 1, pad: 6, gap: 10, labelGap: 6, slot: 52, perLine: 4, lineH: 24 };
const SPREAD = 10; // lines leaving one edge of a group or frame are this far apart
/**
 * The hops (iss-00648 D-02, D-03): a line's height H = kx·dx + ky·dy within min..max above the higher end; ends closer
 * than side px across bulge sideways; the ends of a hop in one box, frame or band item at least chord px apart, room px
 * below whatever is above, never lower than low px.
 */
export const HOP = { min: 18, kx: 0.15, ky: 0.1, max: 56, side: 40, chord: 12, room: 3, low: 8 };

/** A label's width estimated from its characters: ASCII 6.6px, others 11.5px, within 24..200 (CSS cuts it with …). */
export function labelWidth(text) {
  let w = 0;
  for (const ch of String(text ?? "")) w += ch.codePointAt(0) < 128 ? 6.6 : 11.5;
  return Math.min(200, Math.max(24, Math.ceil(w)));
}

// iss-00668 D-03: a badge's or count's small text (graph.css .gx-band-badge, .gx-band-count: 0.8 of the label's size)
const smallWidth = (text) => Math.ceil(labelWidth(text) * 0.8) + BAND.labelGap;
const BADGE_TEXT = { primary: "Primary", unlinked: "Unlinked" };
const badgeWidth = (it) => (it.badge && BADGE_TEXT[it.badge] ? smallWidth(BADGE_TEXT[it.badge]) : 0);
const countWidth = (it) => (it.count ? smallWidth(String(it.count)) : 0);
const columns = (it) => Math.min(it.agents.length, BAND.perLine);
const lines = (it) => Math.max(1, Math.ceil(it.agents.length / BAND.perLine));
// the left of an item's agents from the item's left: after its label, badge and count
const agentsLeft = (it) => BAND.border + BAND.pad + labelWidth(it.label) + BAND.labelGap + badgeWidth(it) + countWidth(it);
const itemWidth = (it) =>
  it.kind === "fold"
    ? 2 * BAND.border + 2 * BAND.pad + labelWidth(it.label)
    : agentsLeft(it) + BAND.border + BAND.pad + BAND.slot * columns(it);
const itemHeight = (it) => BAND.h + (lines(it) - 1) * BAND.lineH;
const leadWidth = (lead) => (lead ? labelWidth(lead) + BAND.labelGap : 0);

/** The height of a band's row (iss-00668 D-03): its tallest item (BAND.h without an item). */
export function bandRowHeight(items) {
  return (items || []).reduce((h, it) => Math.max(h, itemHeight(it)), BAND.h);
}

/** The width of a band's row of items (iss-00617 D-01): the items and the gaps between them, after the lead's text. */
export function bandRowWidth(items, lead = null) {
  if (!items.length) return 0;
  return leadWidth(lead) + items.reduce((w, it) => w + itemWidth(it), 0) + BAND.gap * (items.length - 1);
}

// Each row's items from its left (after its lead), on its top; the rows without an item are left out.
function bandModel(rows) {
  const outRows = [];
  const all = [];
  let right = -Infinity;
  for (const row of rows) {
    if (!row.items.length) continue;
    let x = row.left + leadWidth(row.lead);
    const h = bandRowHeight(row.items);
    const items = row.items.map((it) => {
      const lw = labelWidth(it.label);
      const w = itemWidth(it);
      const left = x + agentsLeft(it);
      const at = (i) => ({ x: left + BAND.slot * (i % BAND.perLine), y: row.top + BAND.lineH * Math.floor(i / BAND.perLine) });
      const item = {
        ...it,
        x, y: row.top, w, h, labelWidth: lw,
        agents: it.kind === "fold" ? [] : it.agents.map((ref, i) => ({ id: ref.id, ref, ...at(i), w: BAND.slot, h: BAND.h })),
      };
      x += w + BAND.gap;
      return item;
    });
    right = Math.max(right, x - BAND.gap);
    all.push(...items);
    outRows.push({ key: row.key, left: row.left, top: row.top, h, lead: row.lead ?? null, leadTitle: row.leadTitle ?? null, leadWidth: row.lead ? labelWidth(row.lead) : 0, items });
  }
  if (!all.length) return null;
  return { top: Math.min(...outRows.map((r) => r.top)), h: Math.max(...outRows.map((r) => r.h)), items: all, right, rows: outRows };
}

const r1 = (v) => Math.round(v * 10) / 10;
const pt = (p) => `${r1(p.x)} ${r1(p.y)}`;
const rectOf = (o) => ({ x1: o.x1, y1: o.y1, x2: o.x2, y2: o.y2 });
const holds = (p, q) => p.x1 <= q.x1 + 0.01 && p.y1 <= q.y1 + 0.01 && p.x2 >= q.x2 - 0.01 && p.y2 >= q.y2 - 0.01;
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

// every end sits on an upper edge and leaves it upward (iss-00648 D-01)
const UP = { x: 0, y: -1 };
const topOf = (r) => ({ x: (r.x1 + r.x2) / 2, y: r.y1 });

// the y of the cubic Bézier at t
const bezierY = (p0, c1, c2, p3, t) => {
  const u = 1 - t;
  return u * u * u * p0 + 3 * u * u * t * c1 + 3 * u * t * t * c2 + t * t * t * p3;
};
const peakOf = (P, c1, c2, C) => {
  let y = Infinity;
  for (let i = 0; i <= 96; i++) y = Math.min(y, bezierY(P.y, c1.y, c2.y, C.y, i / 96));
  return y;
};

/**
 * A hop from P to C (iss-00648 D-02): one cubic Bézier leaving P upward and entering C from above, its peak exactly H
 * above the higher end (H from the ends' horizontal distance and height difference), never above `ceiling` (but at
 * least HOP.low above the higher end). Ends nearly above each other bulge sideways without changing the peak.
 * @returns {d, len, peak}
 */
export function hop(P, C, ceiling = -Infinity) {
  const dx = Math.abs(C.x - P.x), dy = Math.abs(C.y - P.y);
  const H = Math.min(HOP.max, Math.max(HOP.min, HOP.kx * dx + HOP.ky * dy));
  const high = Math.min(P.y, C.y);
  let top = high - H;
  if (top < ceiling) top = Math.min(ceiling, high - HOP.low);
  const h1 = P.y - top, h2 = C.y - top;
  // the peak falls as λ grows: λ = 0 peaks at the higher end, λ = 4/3 reaches top at t = 1/2
  const at = (lam) => peakOf(P, { y: P.y - lam * h1 }, { y: C.y - lam * h2 }, C);
  let lo = 0, hi = 4 / 3;
  for (let i = 0; i < 40; i++) {
    const mid = (lo + hi) / 2;
    if (at(mid) > top) lo = mid;
    else hi = mid;
  }
  const lam = hi;
  const kP = lam * h1, kC = lam * h2;
  const b = dx < HOP.side ? Math.min(HOP.side - dx, 0.5 * Math.min(kP, kC)) : 0;
  const s = C.x >= P.x ? 1 : -1;
  const c1 = { x: P.x + s * b, y: P.y - kP };
  const c2 = { x: C.x + s * b, y: C.y - kC };
  return { d: `M ${pt(P)} C ${pt(c1)} ${pt(c2)} ${pt(C)}`, len: roundLen(bezierLength(P, c1, c2, C)), peak: r1(peakOf(P, c1, c2, C)) };
}

/**
 * The drawing of the command lines (iss-00616 D-03, iss-00648): every end on an upper edge, every line a hop above it.
 * @param pairs   placeAgents' pairs
 * @param places  placeAgents' places
 * @param items   bandItems
 * @param layout  the layout (nodes, groups, width, height)
 * @param spotsOf node -> markSpots(node, …) or null
 * @param routes  the dependency lines' routes ([{pts: [{x, y}]}]), for the arcs' check
 * @param rows    iss-00617 D-01: the band's rows [{key, left, top, lead, items}] in place of `items` (one row of `items`
 *                at BAND.left, BAND.top without it)
 * @param boundsOf node -> the rectangle an arc's bulge stays in (the world {0, 0, layout.width, layout.height} without it)
 * @param ceiling iss-00648 D-05: no hop rises above this y (the cross-repository structure's world starts at 0)
 * @returns {band, links, ripples, audit, top, width}
 */
export function commandModel({ pairs = [], places = new Map(), items = [], layout = {}, spotsOf = () => null, routes = [], rows = null, boundsOf = null, ceiling = -Infinity }) {
  const band = bandModel(rows || [{ key: "", left: BAND.left, top: BAND.top, lead: null, items }]);
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
  const itemRect = (it) => ({ x1: it.x, y1: it.y, x2: it.x + it.w, y2: it.y + it.h });
  // the rectangles an arc's bulge must not enter: every node, group and band item but its own and the frames holding it
  const obstacles = [
    ...nodes.map((n) => ({ ...rectOf(n), self: n })),
    ...groups.map((g) => ({ ...rectOf(g), self: g })),
    ...(band?.items || []).map((it) => ({ ...itemRect(it), self: it })),
  ];
  const isItem = (self) => !!band?.items.includes(self);
  const others = (self) => {
    const own = self && !isItem(self) ? rectOf(self) : null;
    return obstacles.filter((o) => o.self !== self && !(own && o.self.type === "frame" && holds(o, own)));
  };
  const overlapsBox = (bb, self) => others(self).some((o) => Math.min(bb.x2, o.x2) - Math.max(bb.x1, o.x1) > 0 && Math.min(bb.y2, o.y2) - Math.max(bb.y1, o.y1) > 0);
  // the y of the dependency lines' horizontal runs over [x1, x2] (by a length > 0)
  const runsOver = (x1, x2) => {
    const ys = [];
    for (const rt of routes) {
      const pts = rt.pts || [];
      for (let k = 0; k + 1 < pts.length; k++) {
        const p = pts[k], q = pts[k + 1];
        if (p.y === q.y && Math.min(x2, Math.max(p.x, q.x)) - Math.max(x1, Math.min(p.x, q.x)) > 0) ys.push(p.y);
      }
    }
    return ys;
  };
  // the room above the upper edge of `self` across [lo, hi] (iss-00648 D-03): up to the nearest node, group or band item
  // above, the inner upper edge of a frame holding it, the world's bounds (not for a band item) and the ceiling
  const roomOf = (self, lo, hi) => {
    const item = isItem(self);
    const r = item ? itemRect(self) : rectOf(self);
    const own = isBox(self) || self.type === "frame" ? r : null;
    let room = r.y1 - ceiling;
    if (!item) {
      const world = (boundsOf && boundsOf(self)) || { x1: 0, y1: 0, x2: layout.width ?? Infinity, y2: layout.height ?? Infinity };
      room = Math.min(room, r.y1 - world.y1);
    }
    for (const n of nodes) if (n !== self && n.type === "frame" && own && holds(n, own)) room = Math.min(room, r.y1 - (n.y1 + 1));
    for (const o of others(self)) {
      if (o.self.type === "frame" && own && holds(o, own)) continue;
      if (o.x1 < hi && o.x2 > lo && o.y2 <= r.y1) room = Math.min(room, r.y1 - o.y2);
    }
    return room;
  };

  // the end of a placed agent that does not depend on the other end: a mark (box, frame heading) or the band, on the
  // upper edge right above the mark (iss-00648 D-01)
  const fixedEnd = (ref) => {
    const place = places.get(ref.id);
    if (!place) return null;
    if (place.kind === "band") {
      const hit = bandAgent.get(`${place.key}\n${ref.id}`);
      if (!hit) return null;
      const cx = hit.slot.x + hit.slot.w / 2;
      return { kind: "band", item: hit.item, slot: hit.slot, p: { x: cx, y: hit.item.y }, n: UP, spot: { x: hit.slot.x, y: hit.slot.y, w: hit.slot.w, h: hit.slot.h } };
    }
    if (place.kind === "mark") {
      const node = place.node;
      const spot = spotOf(node, ref.id);
      // F-01: the position is not known: the middle of the upper edge
      if (!spot) return { kind: "edge", node, p: topOf(node), n: UP, spot: null, unknown: true };
      return { kind: "mark", node, spot, p: { x: spot.x + spot.w / 2, y: node.y1 }, n: UP };
    }
    return { kind: place.kind, rect: place.kind === "group" ? place.group : place.node, place };
  };
  // the child's mark the line reaches (iss-00648 D-04), null without one
  const markOf = (e) => (e.spot ? { x: e.spot.x, y: e.spot.y, w: e.spot.w, h: e.spot.h, band: e.kind === "band" } : null);

  const links = [];
  const loose = []; // the ends on the upper edge of a group or frame, spread along the edge afterwards
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
      if (!a.spot || !b.spot || a.unknown || b.unknown) continue; // F-01: no arc without both marks
      const arc = sameHop(a, b, sameItem ? a.item : a.node);
      audit.arcs++;
      audit.links++;
      links.push({ id, parent: pair.parent.id, child: pair.child.id, state, kind: "arc", ...arc, mark: markOf(b) });
      continue;
    }
    const link = { id, parent: pair.parent.id, child: pair.child.id, state, kind: "curve", a, b, mark: markOf(b) };
    for (const e of [a, b]) {
      if (!loosen(e)) continue;
      // iss-00648 D-01: the middle of the upper edge, also for a frame holding the other end
      Object.assign(e, { side: "top", p: topOf(e.rect), n: UP });
      loose.push({ e, key: `${e.kind}:${e.rect.key ?? e.rect.id}:top`, id });
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
      l.e.p = { ...l.e.p, x: l.e.p.x + off };
    });
  }
  const out = links.map((l) => {
    if (l.kind === "arc") return l;
    const P = l.a.p, C = l.b.p;
    const { d, len, peak } = hop(P, C, ceiling);
    return { id: l.id, parent: l.parent, child: l.child, state: l.state, kind: "curve", d, len, stubs: [], from: { x: r1(P.x), y: r1(P.y) }, to: { x: r1(C.x), y: r1(C.y) }, mark: l.mark, peak };
  });

  // --- the hops in one box, frame or band item (iss-00648 D-03) ---
  function widen(e1, e2, lo, hi) {
    if (Math.abs(e2.x - e1.x) >= HOP.chord) return [e1, e2];
    const first = e1.x <= e2.x;
    const mid = Math.min(hi - HOP.chord / 2, Math.max(lo + HOP.chord / 2, (e1.x + e2.x) / 2));
    const low = mid - HOP.chord / 2, high = mid + HOP.chord / 2;
    return first ? [{ ...e1, x: low }, { ...e2, x: high }] : [{ ...e1, x: high }, { ...e2, x: low }];
  }
  // the box of a hop's bulge: its ends and d above the edge (the cubic with handles 4d/3 peaks at d)
  function bulgeBox(e1, e2, d) {
    return { x1: Math.min(e1.x, e2.x), y1: Math.min(e1.y, e2.y) - d, x2: Math.max(e1.x, e2.x), y2: Math.max(e1.y, e2.y) };
  }
  function sameHop(a, b, self) {
    const item = isItem(self);
    const r = item ? itemRect(self) : rectOf(self);
    const inset = !item && self.type === "frame" ? 1 : 0;
    const [e1, e2] = widen(a.p, b.p, r.x1 + inset, r.x2 - inset);
    const lo = Math.min(e1.x, e2.x), hi = Math.max(e1.x, e2.x);
    let u = Math.min(HOP.min, roomOf(self, lo, hi) - HOP.room);
    if (u < HOP.min) audit.crowded++;
    if (u < HOP.low) u = HOP.low;
    // the highest height whose peak keeps HOP.room from every dependency run over the middle half of the hop; the legs
    // crossing a run do not count (iss-00648 D-03)
    const q = (hi - lo) / 4;
    const ys = runsOver(lo + q, hi - q);
    let d = null;
    for (let h = u; h >= HOP.low; h--) {
      if (ys.every((y) => Math.abs(r.y1 - h - y) >= HOP.room)) {
        d = h;
        break;
      }
    }
    if (d === null) {
      d = u;
      audit.edgeOverlaps++;
    }
    if (overlapsBox(bulgeBox(e1, e2, d), self)) audit.boxOverlaps++;
    const { d: path, len } = cubic(e1, UP, e2, UP, (4 * d) / 3);
    return { d: path, len, stubs: [], bulge: d, from: { x: r1(e1.x), y: r1(e1.y) }, to: { x: r1(e2.x), y: r1(e2.y) }, peak: r1(r.y1 - d) };
  }

  const right = band ? band.right + SIZE.margin : 0;
  const peaks = out.map((l) => l.peak - 6);
  return {
    band,
    links: out,
    ripples: [...ripples.values()],
    audit,
    top: Math.min(band ? band.top - 16 : 0, 0, ...peaks),
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
