// The command lines of the cross-repository structure (iss-00617 D-02; Epic epic-00615 R-10, R-11): which shown
// repository each worktree of orca-web's summary belongs to, where each end of a pair sits (in its repository's layout,
// its repository's band below the frame's heading, or the band "ほかの場所" above every frame), the frames kept for
// their band alone, and the model of the lines in the world's coordinates (graph/command.js's commandModel).
// Pure computation like compose.js: no DOM, no clock, no network. The page passes compose() as a function where the
// frames shown are needed, and the measured marks of each repository as spotsOf.
import { normPath, summaryValid } from "../../core/orca_match.js";
import { BAND, bandItems, bandKeys, bandRowHeight, bandRowWidth, commandModel, placer } from "../graph/command.js";
import { UNSCOPED, unscopedItems } from "../graph/unscoped.js";
import { REPO } from "./compose.js";

/** The text at the head of the band above every frame (R-02). */
export const OTHER_LEAD = "ほかの場所";

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const readable = (structure) => structure?.worktrees?.status === "ok" && Array.isArray(structure.worktrees.paths);

/**
 * The shown repository of each worktree (R-01, F-02): the first repository, in the list's order, whose structure lists
 * the worktree's path; else the first whose listed worktrees have the worktree's project (matchWorktrees' rule; no name
 * means anything).
 * @param repos   [{key, structure}] in the list API's order (structure null while it is not read)
 * @returns {of: Map<worktree, key>, unknown: whether a repository's worktrees are not known (not read, or not ok)}
 */
export function repoOfWorktrees(repos, summary) {
  const of = new Map();
  const unknown = repos.some((r) => !readable(r.structure));
  if (!summaryValid(summary)) return { of, unknown };
  const list = summary.worktrees.filter(isObject);
  const known = repos.filter((r) => readable(r.structure)).map((r) => ({ key: r.key, paths: new Set(r.structure.worktrees.paths.map(normPath).filter((p) => p !== null)) }));
  for (const r of known) {
    const projects = new Set(list.filter((w) => r.paths.has(normPath(w.path))).map((w) => w.project?.id).filter((id) => typeof id === "string"));
    r.projects = projects;
  }
  for (const w of list) {
    const hit = known.find((r) => r.paths.has(normPath(w.path)));
    if (hit) of.set(w, hit.key);
  }
  for (const w of list) {
    if (of.has(w) || typeof w.project?.id !== "string") continue;
    const hit = known.find((r) => r.projects.has(w.project.id));
    if (hit) of.set(w, hit.key);
  }
  return { of, unknown };
}

/**
 * Where each end of the pairs sits in the cross-repository structure (iss-00617 R-01, R-03, F-02) and each repository's
 * Unscoped row (iss-00668 D-04), by one rule in every range (iss-00676 D-02): the range only shapes the layouts.
 * Place: graph/command.js's Place with `repo` (the worktree's repository or null), and `row` for a band's end (the
 * repository's key, "" for "ほかの場所").
 * @param pairs       commandPairs(summary), all of them
 * @param repos       [{key, structure, layout, ix, graph}] in the list's order; graph: the frame's body is a graph
 * @param visible     the keys compose() shows without a band
 * @param visibleWith (keep) => the keys compose() shows with `keep`
 * @param orderOf     worktree -> its agents in the component's order (orderAgents), or null
 * @returns {pairs, places: Map<agent id, Place>, rows: Map<row, items>, keep: Set<key>, of, unknown}
 */
export function crossPlace(pairs, { repos, summary, visible, visibleWith, orderOf }) {
  const { of, unknown } = repoOfWorktrees(repos, summary);
  const keys = summaryValid(summary) ? bandKeys(summary) : new Map();
  const byKey = new Map(repos.map((r) => [r.key, r]));
  const placers = new Map();
  const placeIn = (k, ref) => {
    const r = byKey.get(k);
    if (!r?.graph || !r.layout) return { kind: "band", key: keys.get(ref.worktree), repo: k, row: k };
    if (!placers.has(k)) placers.set(k, placer({ structure: r.structure, summary, layout: r.layout, ix: r.ix }));
    const p = placers.get(k)(ref);
    return p.kind === "band" ? { ...p, repo: k, row: k } : { ...p, repo: k };
  };
  const places = new Map();
  const kept = [];
  for (const pair of pairs) {
    const ends = [pair.parent, pair.child];
    // F-02: a worktree in no repository may be one not known yet: no guess of "ほかの場所"
    if (unknown && ends.some((ref) => !of.has(ref.worktree))) continue;
    for (const ref of ends) {
      if (places.has(ref.id)) continue;
      const k = of.get(ref.worktree);
      places.set(ref.id, k === undefined ? { kind: "band", key: keys.get(ref.worktree), repo: null, row: "" } : placeIn(k, ref));
    }
    kept.push(pair);
  }
  // R-03: a repository not shown keeps its frame for the band when a pair's parent is in it
  const shown = visible instanceof Set ? visible : new Set(visible || []);
  const ownOf = (k) => new Set([...of].filter(([, key]) => key === k).map(([w]) => w));
  const rowOf = (k) => {
    const mine = new Map([...places].filter(([, p]) => p.kind === "band" && p.row === k));
    return unscopedItems({ structure: byKey.get(k)?.structure, summary, pairs, places: mine, own: ownOf(k), orderOf });
  };
  const keep = new Set();
  for (const pair of kept) {
    const p = places.get(pair.parent.id);
    if (p.kind === "band" && p.row && !shown.has(p.row)) keep.add(p.row);
  }
  const shown2 = keep.size && typeof visibleWith === "function" ? new Set(visibleWith(keep)) : shown;
  for (const [id, p] of places) {
    if (p.repo && !shown2.has(p.repo)) places.set(id, { kind: "band", key: keys.get(refOf(kept, id)?.worktree) ?? p.key, repo: p.repo, row: "" });
  }
  // the rows: "ほかの場所" first (today's band items), then each shown repository's Unscoped row
  const rows = new Map();
  const other = new Map([...places].filter(([, p]) => p.kind === "band" && p.row === ""));
  if (other.size) rows.set("", bandItems(kept, other, new Set(), orderOf));
  for (const r of repos) {
    if (!shown2.has(r.key)) continue;
    const res = rowOf(r.key);
    for (const [id, p] of res.places) if (p.kind === "band" && p.row === r.key) places.set(id, p);
    // one "+N" per frame: its key names its repository (the band's items are looked up by key across the rows)
    if (res.items.length) rows.set(r.key, res.items.map((it) => (it.kind === "fold" ? { ...it, key: `fold|${r.key}` } : it)));
  }
  return { pairs: kept, places, rows, keep, of, unknown };
}

function refOf(pairs, id) {
  for (const p of pairs) {
    if (p.parent.id === id) return p.parent;
    if (p.child.id === id) return p.child;
  }
  return null;
}

/**
 * The bands' shape for compose() (R-02, R-03) and its key: the same shape gives the same string (R-05).
 * @returns {bands: {key: {h, w}}, keep: [key], other: {h, w} | null, key}
 */
export function bandShape(rows, keep) {
  const bands = {};
  // iss-00668 D-04: a row's lead "Unscoped" and its tallest item (R-09)
  for (const k of [...rows.keys()].filter((k) => k !== "").sort()) {
    const items = rows.get(k);
    bands[k] = { h: REPO.band + bandRowHeight(items) - BAND.h, w: bandRowWidth(items, UNSCOPED.lead) + 2 * REPO.pad };
  }
  const items = rows.get("");
  const other = items?.length ? { h: REPO.other + bandRowHeight(items) - BAND.h, w: bandRowWidth(items, OTHER_LEAD) + 2 * REPO.pad } : null;
  const kept = [...(keep || [])].sort();
  return { bands, keep: kept, other, key: JSON.stringify({ bands, keep: kept, other }) };
}

/**
 * The lines' model in the world's coordinates (R-01, R-04, F-03, F-05).
 * @param comp    compose()'s result the page drew
 * @param repos   [{key, layout, routes}]
 * @param placed  crossPlace's result
 * @param spotsOf (node, key) -> markSpots(node, that repository's measured marks) in the layout's coordinates, or null
 * @returns commandModel's result with `world`: {nodes, groups, origin: Map<key, {x, y}>}
 */
export function crossModel({ comp, repos, placed, spotsOf = () => null }) {
  const nodes = [];
  const groups = [];
  const routes = [];
  const copies = new Map(); // a layout's node or group -> its copy in the world
  const origin = new Map();
  const bounds = new Map();
  for (const r of repos) {
    const f = comp.frames.get(r.key);
    const L = r.layout;
    if (!f || f.body.kind !== "graph" || !L) continue;
    const ox = f.body.x;
    const oy = f.body.y;
    origin.set(r.key, { x: ox, y: oy });
    const rect = { x1: ox, y1: oy, x2: ox + L.width, y2: oy + L.height };
    const move = (n) => {
      const c = { ...n, x1: n.x1 + ox, y1: n.y1 + oy, x2: n.x2 + ox, y2: n.y2 + oy, repo: r.key, src: n, key: `${r.key}\n${n.key ?? n.id}` };
      copies.set(n, c);
      bounds.set(c, rect);
      return c;
    };
    nodes.push(...L.nodes.map(move));
    groups.push(...(L.groups || []).map(move));
    for (const rt of r.routes || []) routes.push({ ...rt, pts: (rt.pts || []).map((p) => ({ x: p.x + ox, y: p.y + oy })) });
  }
  const places = new Map();
  for (const [id, p] of placed.places) {
    if (p.kind === "mark" || p.kind === "frame") {
      const c = copies.get(p.node);
      if (c) places.set(id, { ...p, node: c });
    } else if (p.kind === "group") {
      const c = copies.get(p.group);
      if (c) places.set(id, { ...p, group: c });
    } else places.set(id, p);
  }
  // the band's rows: a repository's row below its heading and warnings, "ほかの場所" above every frame; a row that has
  // no band in comp (F-05's limit) is left out, so its ends are not drawn
  const rows = [];
  for (const [row, items] of placed.rows) {
    if (row === "") {
      if (comp.other) rows.push({ key: "", left: comp.other.x1 + REPO.pad, top: comp.other.y1 + REPO.otherTop, lead: OTHER_LEAD, items });
      continue;
    }
    const f = comp.frames.get(row);
    if (f && f.band.y2 > f.band.y1) rows.push({ key: row, left: f.x1 + REPO.pad, top: f.band.y1 + REPO.bandTop, lead: UNSCOPED.lead, leadTitle: UNSCOPED.leadTitle, items });
  }
  const shifted = (c) => {
    const o = origin.get(c.repo);
    const s = o ? spotsOf(c.src, c.repo) : null;
    return s ? s.map((q) => ({ ...q, x: q.x + o.x, y: q.y + o.y })) : null;
  };
  const model = commandModel({
    pairs: placed.pairs,
    places,
    rows,
    layout: { nodes, groups, width: comp.width, height: comp.height },
    spotsOf: shifted,
    routes,
    boundsOf: (c) => bounds.get(c) || null,
    ceiling: 4, // iss-00648 D-05: the world starts at y 0; no hop rises above it
  });
  return { ...model, world: { nodes, groups, origin } };
}

// --- R-05, F-05: the key of the inputs ---------------------------------------------------------------------------

const ids = new WeakMap();
let next = 0;
const idOf = (o) => {
  if (o === null || typeof o !== "object") return String(o);
  if (!ids.has(o)) ids.set(o, ++next);
  return `#${ids.get(o)}`;
};

/**
 * The same string for the same inputs (graph/command.js's commandKey's way): the summary object, each repository's
 * structure and routing objects, its measured widths and recorded ids of the marks, the shown frames' keys, and the
 * composed frames (comp; null leaves it out, for F-05's count of the places' inputs) and the range (iss-00668 D-06).
 * @param repos [{key, structure, eg, marks, ids}]
 */
export function crossKey({ summary, repos = [], comp = null, visible = null, range = null }) {
  const parts = repos.map((r) => `${r.key}:${idOf(r.structure)}:${idOf(r.eg)}:${JSON.stringify(r.marks ?? null)}:${JSON.stringify(r.ids ?? null)}`);
  return [idOf(summary), ...parts, JSON.stringify(visible ?? null), comp ? idOf(comp) : "-", String(range), JSON.stringify(BAND), JSON.stringify(REPO)].join("|");
}
