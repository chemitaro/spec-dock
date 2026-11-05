// The structure graph's node check (iss-00532 D-07). Run by tests/unit/presentation/test_dashboard_graph_js.py:
//   node dashboard_graph_check.mjs <assets/dashboard directory> <request.json>
// request.json = {documents: {name: structure API document}, checks: ["audit", "layout", "order", "series"]}
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
  for (const [width, height] of [[1400], [374], [1400, 760], [1900, 940]])
    for (const showDone of [false, true])
      for (const deps of ["wait", "all"])
        for (const fold of [true, false]) list.push({ mode: "nest", showDone, deps, fold, width, height });
  for (const s of doc.scopes) if (s.kind !== "issue" && s.state !== "done") list.push({ mode: "nest", showDone: false, deps: "all", fold: true, focus: s.id });
  return list;
}

function check(name, doc, opts) {
  const t0 = performance.now();
  const r = routeLayout(doc.scopes, doc.cleanup, opts);
  const ms = performance.now() - t0;
  const res = audit(
    r.routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: r.G.obs[r.G.edges[rt.ei].a].key, kz: r.G.obs[r.G.edges[rt.ei].z].key })),
    r.G.obs,
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
      const L = layout(doc.scopes, doc.cleanup, opts, request.gaps?.[name]?.[key] || {});
      result[key] = {
        nodes: L.nodes.map((n) => ({ id: n.id, type: n.type, x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2 })),
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

process.stdout.write(JSON.stringify(out));
