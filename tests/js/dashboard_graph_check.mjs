// The structure graph's node check (iss-00532 D-07). Run by tests/unit/presentation/test_dashboard_graph_js.py:
//   node dashboard_graph_check.mjs <assets/dashboard directory> <request.json>
// request.json = {documents: {name: structure API document}, checks: ["audit", "layout", "order", "series", "passages"]}
// Prints one JSON object with the results; the Python test asserts on it.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const { layout, routeLayout, graphInput, index, byActivity } = await load("views/graph/layout.js");
const { audit } = await load("views/graph/router.js");
const series = await load("views/timeline/series.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = { audit: [], layout: {}, series: {}, order: {} };
if (request.prefs) {
  const { restorePrefs } = await load("views/graph/prefs.js");
  const { DEFAULTS } = await load("views/graph/layout.js");
  out.prefs = request.prefs.map((p) => restorePrefs(p.current, p.legacy, DEFAULTS));
}

function combos(doc) {
  const list = [];
  for (const mode of ["nest", "tree"])
    for (const showDone of [false, true])
      for (const deps of ["wait", "all"])
        for (const fold of [true, false]) list.push({ mode, showDone, deps, fold });
  // iss-00560: the groups wrap at the width seen at 100%: a PC (1400px) and a 390px phone (374px)
  // iss-00575: and with the view's height too, where the top level wraps where the whole shows largest
  for (const [width, height] of [[1400], [374], [1400, 760], [1900, 940], [1000, 800], [1440, 900], [1920, 1080]])
    for (const showDone of [false, true])
      for (const deps of ["wait", "all"])
        for (const fold of [true, false]) list.push({ mode: "nest", showDone, deps, fold, width, height });
  for (const s of doc.scopes) if (s.kind !== "issue" && s.state !== "done") list.push({ mode: "nest", showDone: false, deps: "all", fold: true, focus: s.id });
  return list;
}

function check(name, doc, opts) {
  // iss-00572: the time is the CPU time of this process (not the wall clock, which a loaded PC stretches), and the least of
  // three runs of the asserted ones (the routing is deterministic, so the runs differ only by what the machine did meanwhile).
  let r;
  let ms = Infinity;
  // only the runs whose time is asserted (the 250-Scope structure without a focus) are repeated
  const repeats = name === "generated" && !opts.focus ? 3 : 1;
  for (let i = 0; i < repeats; i++) {
    const c0 = process.cpuUsage();
    r = routeLayout(doc.scopes, doc.cleanup, opts);
    const c = process.cpuUsage(c0);
    ms = Math.min(ms, (c.user + c.system) / 1000);
  }
  const res = audit(
    r.routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: r.G.obs[r.G.edges[rt.ei].a].key, kz: r.G.obs[r.G.edges[rt.ei].z].key })),
    r.G.obs,
    { frames: r.G.frames },
  );
  return { name, opts, edges: r.routes.length, iters: r.iters, unmapped: r.unmapped, widenLeft: r.widen.length, ms: Math.round(ms), ...res };
}

if (request.checks.includes("audit")) {
  for (const [name, doc] of Object.entries(request.documents)) for (const opts of combos(doc)) out.audit.push(check(name, doc, opts));
}

if (request.checks.includes("layout")) {
  for (const [name, doc] of Object.entries(request.documents)) {
    const result = {};
    for (const [key, opts] of Object.entries(request.layouts?.[name] || {})) {
      const L = request.routed?.[name]?.includes(key)
        ? routeLayout(doc.scopes, doc.cleanup, opts).layout
        : layout(doc.scopes, doc.cleanup, opts, request.gaps?.[name]?.[key] || {});
      result[key] = {
        nodes: L.nodes.map((n) => ({ id: n.id, type: n.type, x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, path: n.path })),
        groups: L.groups.map((g) => ({ key: g.key, ids: g.ids, x1: g.x1, y1: g.y1, x2: g.x2, y2: g.y2 })),
        trunks: L.trunks.length,
        edges: L.edges.map((e) => ({ a: e.a, z: e.z, done: e.done, pairs: e.pairs })),
        wraps: Object.fromEntries(L.wraps),
        focus: L.focus,
        ancestors: L.ancestors,
        obs: graphInput(L).obs.length,
      };
    }
    out.layout[name] = result;
  }
}

// The activity order of each parent's children (iss-00560: the order the groups start from).
if (request.checks.includes("order")) {
  for (const [name, doc] of Object.entries(request.documents)) {
    const ix = index(doc.scopes);
    const act = byActivity(ix);
    out.order[name] = Object.fromEntries([...ix.kids].filter(([, k]) => k.length).map(([id, k]) => [id, k.slice().sort(act).map((s) => s.id)]));
  }
}

if (request.checks.includes("series")) {
  for (const [name, doc] of Object.entries(request.documents)) {
    out.series[name] = {
      all: series.mergeWeeks(doc.timeline.weeks_by_kind, ["initiative", "epic", "issue"]),
      issue: series.mergeWeeks(doc.timeline.weeks_by_kind, ["issue"]),
      none: series.mergeWeeks(doc.timeline.weeks_by_kind, []),
      groups: series.groupEvents(doc.timeline.events, doc.scopes, "UTC"),
    };
  }
}

// iss-00578: the passages of every group's grid, and the lines through each. A cell's path holds the group's rows (rr…,
// i = the row) and its stage column (cc…, i = the stage).
// - axis x: the passage after column k runs from the right of its widest cell to the left of the leftmost cell of column
//   k + 1; runs = the vertical runs through it (rounded x positions).
// - axis y: in one column, the band from the bottom of a cell on row r to the top of the cell on row r + 1; runs = the
//   horizontal runs through that band across the grid (rounded y positions).
function passages(r) {
  const vs = [], hs = [];
  for (const rt of r.routes) {
    const P = rt.pts;
    for (let k = 0; k < P.length - 1; k++) {
      const dx = Math.abs(P[k].x - P[k + 1].x), dy = Math.abs(P[k].y - P[k + 1].y);
      if (dx < 0.01 && dy > 0.01) vs.push({ x: P[k].x, y1: Math.min(P[k].y, P[k + 1].y), y2: Math.max(P[k].y, P[k + 1].y) });
      if (dy < 0.01 && dx > 0.01) hs.push({ y: P[k].y, x1: Math.min(P[k].x, P[k + 1].x), x2: Math.max(P[k].x, P[k + 1].x) });
    }
  }
  const grids = new Map();
  for (const n of [...r.layout.nodes, ...r.layout.groups]) {
    const steps = n.path || [];
    for (let j = steps.length - 1; j >= 1; j--) {
      if (!steps[j].c.startsWith("cc") || !steps[j - 1].c.startsWith("rr")) continue;
      if (!grids.has(steps[j].c)) grids.set(steps[j].c, []);
      grids.get(steps[j].c).push({ col: steps[j].i, row: steps[j - 1].i, x1: n.x1, x2: n.x2, y1: n.y1, y2: n.y2 });
      break;
    }
  }
  const span = (list) => list.reduce((o, n) => ({ x1: Math.min(o.x1, n.x1), x2: Math.max(o.x2, n.x2), y1: Math.min(o.y1, n.y1), y2: Math.max(o.y2, n.y2) }), { x1: Infinity, x2: -Infinity, y1: Infinity, y2: -Infinity });
  const out = [];
  for (const [key, cells] of grids) {
    const all = span(cells);
    const cols = new Map();
    for (const c of cells) cols.set(c.col, [...(cols.get(c.col) || []), c]);
    for (const [k, list] of cols) {
      const a = span(list), next = cols.get(k + 1);
      if (next) {
        const b = span(next);
        if (b.x1 > a.x2) {
          const y1 = Math.min(a.y1, b.y1), y2 = Math.max(a.y2, b.y2);
          const xs = new Set(vs.filter((s) => s.x > a.x2 && s.x < b.x1 && s.y2 > y1 && s.y1 < y2).map((s) => Math.round(s.x)));
          out.push({ axis: "x", key, k, gap: Math.round((b.x1 - a.x2) * 10) / 10, runs: xs.size });
        }
      }
      const byRow = list.slice().sort((p, q) => p.row - q.row);
      for (let i = 0; i + 1 < byRow.length; i++) {
        const p = byRow[i], q = byRow[i + 1];
        if (q.row !== p.row + 1 || q.y1 <= p.y2) continue;
        const ys = new Set(hs.filter((s) => s.y > p.y2 && s.y < q.y1 && s.x2 > all.x1 && s.x1 < all.x2).map((s) => Math.round(s.y)));
        out.push({ axis: "y", key, k, row: p.row, gap: Math.round((q.y1 - p.y2) * 10) / 10, runs: ys.size });
      }
    }
  }
  return out;
}

if (request.checks.includes("passages")) {
  out.passages = [];
  for (const [name, doc] of Object.entries(request.documents)) {
    for (const opts of combos(doc)) out.passages.push({ name, opts, passages: passages(routeLayout(doc.scopes, doc.cleanup, opts)) });
  }
}

process.stdout.write(JSON.stringify(out));
