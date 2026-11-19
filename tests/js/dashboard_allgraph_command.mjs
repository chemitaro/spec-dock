// The cross-repository command lines' pure computation (iss-00617 T-01, T-03). Run by
// tests/unit/presentation/test_dashboard_allgraph_command.py:
//   node dashboard_allgraph_command.mjs <assets/dashboard directory> <request.json>
// request.json:
//   repoOf: [{repos: [{key, structure}], summary}, …]  -> repoOfWorktrees of each as {of: {worktree id: key}, unknown}
//   rowWidth: [[[{label, agents: n}, …], lead], …]      -> bandRowWidth of each
//   placer: [{structure, summary, layout: {options}}]   -> whether placer gives placeAgents' places, and the places
//   rows: [{layout, pairs: [[parent, child, item]], rows, bounds, marks}] -> commandModel with rows (and boundsOf)
//   scenarios: {name: {repos: [{key, parent, structure|null, failed}], summary, range, width, marks: {key: {scope: m}},
//              order: {worktree id: [agent id, …]}}}   -> the whole pipeline as allgraph.js runs it
//   key: true                                           -> crossKey's answers for the same and for changed inputs
// Prints one JSON object; the Python test asserts on it. Every value is synthetic.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const L = await load("views/graph/layout.js");
const C = await load("views/graph/command.js");
const P = await load("views/allgraph/compose.js");
const X = await load("views/allgraph/command.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = {};

const byId = (summary) => new Map((summary?.worktrees || []).map((w) => [w, w.id]));
const placeJson = (p) => {
  const base = { kind: p.kind, repo: p.repo ?? null, row: p.row ?? null };
  if (p.kind === "mark") return { ...base, id: p.node.src?.id ?? p.node.id, scope: p.scope };
  if (p.kind === "frame") return { ...base, id: p.node.src?.id ?? p.node.id };
  if (p.kind === "group") return { ...base, key: p.group.key };
  return { ...base, key: p.key };
};
const compJson = (c) => ({ frames: Object.fromEntries(c.frames), order: c.order, width: c.width, height: c.height, other: c.other ?? null });
const rowsJson = (rows) => Object.fromEntries([...rows].map(([k, items]) => [k, items.map((it) => {
  const base = { key: it.key, label: it.label, own: it.own, main: it.main, agents: it.agents.map((a) => a.id) };
  // iss-00668: the Unscoped row's fields when the item has them
  for (const f of ["badge", "count", "kind", "idle"]) if (it[f] !== undefined && it[f] !== null && it[f] !== false && !(f === "kind" && it[f] === "worktree")) base[f] = it[f];
  return base;
})]));
const bandJson = (band) => band && {
  top: band.top, h: band.h, right: band.right,
  rows: (band.rows || []).map((r) => ({
    key: r.key, left: r.left, top: r.top, h: r.h, lead: r.lead, leadTitle: r.leadTitle ?? null, leadWidth: r.leadWidth,
    items: r.items.map((it) => ({ key: it.key, label: it.label, x: it.x, y: it.y, w: it.w, h: it.h, agents: it.agents.map(({ id, x, y, w, h }) => ({ id, x, y, w, h })) })),
  })),
  items: band.items.map((it) => ({ key: it.key, x: it.x, y: it.y, w: it.w, h: it.h })),
};
const modelJson = (m) => ({ band: bandJson(m.band), links: m.links, ripples: m.ripples, audit: m.audit, top: m.top, width: m.width });

if (request.repoOf) {
  out.repoOf = request.repoOf.map(({ repos, summary }) => {
    const r = X.repoOfWorktrees(repos, summary);
    const ids = byId(summary);
    return { of: Object.fromEntries([...r.of].map(([w, k]) => [ids.get(w), k])), unknown: r.unknown };
  });
}

if (request.rowWidth) {
  out.rowWidth = request.rowWidth.map(([items, lead]) => C.bandRowWidth(items.map((it) => ({ label: it.label, agents: Array.from({ length: it.agents }, (_, i) => ({ id: `a${i}` })) })), lead));
}

if (request.placer) {
  out.placer = request.placer.map(({ structure, summary, layout: opts }) => {
    const ix = L.index(structure.scopes);
    const layout = L.layout(structure.scopes, structure.cleanup || [], opts);
    const pairs = C.commandPairs(summary);
    const placed = C.placeAgents(pairs, { structure, summary, layout, ix });
    const place = C.placer({ structure, summary, layout, ix });
    const same = [...placed.places].every(([id, p]) => {
      const ref = pairs.flatMap((q) => [q.parent, q.child]).find((r) => r.id === id);
      return JSON.stringify(placeJson(place(ref))) === JSON.stringify(placeJson(p));
    });
    return { same, count: placed.places.size, places: Object.fromEntries([...placed.places].map(([id, p]) => [id, placeJson(p)])) };
  });
}

if (request.rows) {
  out.rows = request.rows.map((rc) => {
    const layout = { groups: [], ...rc.layout };
    const nodes = new Map(layout.nodes.map((n) => [n.id, n]));
    const wt = { id: "wt", agents: [] };
    const ref = (id) => ({ id, mark: "working", worktree: wt });
    const pairs = [];
    const places = new Map();
    for (const [p, c, where] of rc.pairs) {
      pairs.push({ parent: ref(p), child: ref(c) });
      for (const id of [p, c]) {
        const w = where[id];
        places.set(id, w.band !== undefined ? { kind: "band", key: w.band } : { kind: "mark", node: nodes.get(w.mark), scope: w.mark });
      }
    }
    const rows = rc.rows.map((r) => ({ ...r, items: r.items.map((it) => ({ key: it.key, label: it.label, own: true, main: false, worktree: wt, agents: it.agents.map(ref) })) }));
    const spotsOf = (n) => L.markSpots(n, rc.marks?.[n.id]);
    const boundsOf = rc.bounds ? () => rc.bounds : undefined;
    return modelJson(C.commandModel({ pairs, places, rows, layout, spotsOf, boundsOf }));
  });
}

// The pipeline of allgraph.js (D-05) without the DOM: each repository's layout, compose without a band, crossPlace,
// bandShape, compose with the shape, crossModel.
function scenario(sc) {
  const range = sc.range || "all";
  const width = sc.width || 1400;
  const listed = sc.repos.map((r) => ({ repository: r.key, parent: r.parent ?? null }));
  const state = new Map();
  for (const r of sc.repos) {
    const st = { key: r.key, structure: r.structure, layout: null, routes: [], ix: null, failed: !!r.failed };
    if (r.structure && r.structure.scopes.length) {
      st.ix = L.index(r.structure.scopes);
      const marks = Object.fromEntries(Object.entries(sc.marks?.[r.key] || {}).map(([id, m]) => [id, { items: m.items, gap: m.gap }]));
      const res = L.routeLayout(r.structure.scopes, r.structure.cleanup || [], { mode: "nest", range, focus: null, width: P.bodyWidth(width, 0), marks });
      st.layout = res.layout;
      st.routes = res.routes;
    }
    state.set(r.key, st);
  }
  const sizes = {};
  for (const st of state.values()) {
    if (st.failed) sizes[st.key] = { status: "failed" };
    else if (!st.structure) continue;
    else {
      const Lo = st.layout;
      sizes[st.key] = { status: "ok", w: Lo ? Lo.width : 0, h: Lo ? Lo.height : 0, shown: Lo ? Lo.nodes.length + Lo.groups.length : 0, scopes: st.structure.scopes.length };
    }
  }
  const plain = P.compose(listed, sizes, { range, width });
  const visible = new Set(plain.order);
  const visibleWith = (keep) => new Set(P.compose(listed, sizes, { range, width, keep }).order);
  const repos = [...state.values()].map((st) => ({ ...st, graph: plain.frames.get(st.key)?.body.kind === "graph" }));
  const summary = sc.summary;
  const pairs = C.commandPairs(summary);
  const order = sc.order || {};
  const orderOf = (w) => order[w.id] || null;
  const placed = X.crossPlace(pairs, { repos, summary, visible, visibleWith, orderOf, range });
  const shape = X.bandShape(placed.rows, placed.keep);
  const comp = P.compose(listed, sizes, { range, width, bands: shape.bands, keep: shape.keep, other: shape.other });
  const spots = {};
  const spotsOf = (src, key) => {
    const s = L.markSpots(src, sc.marks?.[key]?.[src.id]);
    (spots[key] ||= {})[src.id] = s;
    return s;
  };
  const model = X.crossModel({ comp, repos, placed, spotsOf });
  const flat = X.crossModel({ comp: plain, repos, placed, spotsOf: () => null });
  const ids = byId(summary);
  const { of, unknown } = X.repoOfWorktrees(repos, summary);
  return {
    of: Object.fromEntries([...of].map(([w, k]) => [ids.get(w), k])),
    unknown,
    allPairs: pairs.map((p) => [p.parent.id, p.child.id]),
    pairs: placed.pairs.map((p) => [p.parent.id, p.child.id]),
    places: Object.fromEntries([...placed.places].map(([id, p]) => [id, placeJson(p)])),
    rows: rowsJson(placed.rows),
    keep: [...placed.keep],
    visible: [...visible],
    shape: { bands: shape.bands, keep: shape.keep, other: shape.other, key: shape.key },
    shapeAgain: X.bandShape(placed.rows, new Set(placed.keep)).key === shape.key,
    plain: compJson(plain),
    comp: compJson(comp),
    nodes: Object.fromEntries(repos.filter((r) => r.layout).map((r) => [r.key, Object.fromEntries(r.layout.nodes.map((n) => [n.id, { type: n.type, x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, kind: n.kind ?? null }]))])),
    groups: Object.fromEntries(repos.filter((r) => r.layout).map((r) => [r.key, (r.layout.groups || []).map((g) => ({ key: g.key, x1: g.x1, y1: g.y1, x2: g.x2, y2: g.y2 }))])),
    spots,
    model: modelJson(model),
    flat: { links: flat.links.length, band: !!flat.band },
    frameKeys: model.world.nodes.filter((n) => n.type === "frame").reduce((acc, n) => ((acc[n.src.id] ||= []).push(n.key), acc), {}),
  };
}
if (request.scenarios) out.scenarios = Object.fromEntries(Object.entries(request.scenarios).map(([name, sc]) => [name, scenario(sc)]));

if (request.key) {
  const summary = { schema: "x" };
  const structure = { scopes: [] };
  const eg = { layout: {} };
  const comp = { frames: new Map() };
  const repos = [{ key: "a", structure, eg, marks: { s: { items: [36], gap: 2 } }, ids: { s: ["x"] } }];
  const k = (o) => X.crossKey({ summary, repos, comp, visible: ["a"], ...o });
  out.key = {
    same: k({}) === k({}),
    copied: k({}) === k({ repos: JSON.parse(JSON.stringify(repos)).map((r, i) => ({ ...r, structure: repos[i].structure, eg: repos[i].eg })) }),
    otherSummary: k({}) === k({ summary: { schema: "x" } }),
    otherEg: k({}) === k({ repos: [{ ...repos[0], eg: { layout: {} } }] }),
    otherStructure: k({}) === k({ repos: [{ ...repos[0], structure: { scopes: [] } }] }),
    otherMarks: k({}) === k({ repos: [{ ...repos[0], marks: { s: { items: [40], gap: 2 } } }] }),
    otherIds: k({}) === k({ repos: [{ ...repos[0], ids: { s: ["y"] } }] }),
    otherComp: k({}) === k({ comp: { frames: new Map() } }),
    otherVisible: k({}) === k({ visible: [] }),
    otherRange: k({ range: "all" }) === k({ range: "next" }),
    sameRange: k({ range: "next" }) === k({ range: "next" }),
    withoutComp: k({ comp: null }) === k({ comp: { frames: new Map() } }),
    withoutCompSame: k({ comp: null }) === k({ comp: null }),
  };
}

process.stdout.write(JSON.stringify(out));
