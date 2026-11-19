// The command lines' pure computation (iss-00616 D-01..D-03). Run by tests/unit/presentation/test_dashboard_graph_command.py:
//   node dashboard_graph_command.mjs <assets/dashboard directory> <request.json>
// request.json:
//   packMarks: [[m, avail], …]        -> packMarks of each, beside markRows of each
//   markSpots: [[node, m], …]         -> markSpots of each
//   labelWidth: [text, …]             -> labelWidth of each
//   pairs: [summary, …]               -> commandPairs of each as [[parent id, child id], …]
//   scenarios: {name: {structure, summary, layout: {options} | {nodes, groups, width, height}, marks: {Scope id:
//              {items, gap, ids}}, routed: bool, routes: [{pts}], order: {worktree id: [agent id, …]}}}
//              -> the pairs, places, band items and commandModel of each (null places: F-01)
//   key: true                         -> commandKey's answers for the same and for changed inputs
//   hop: [[P, C, ceiling | null], …]  -> hop of each (iss-00648 D-02)
//   bandRows: [{rows: [{key, left, top, lead, items: [{key, label, kind, badge, count, agents: [id, …]}]}],
//              pairs: [[parent, child]]}, …]  -> bandRowHeight of each row and commandModel's band and links, the ends
//              in the band item holding them (iss-00668 D-03)
// Prints one JSON object; the Python test asserts on it.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const L = await load("views/graph/layout.js");
const C = await load("views/graph/command.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = {};

out.consts = {
  MARK_H: L.MARK_H ?? null, MARK_LEAD: L.MARK_LEAD ?? null, MARK_LEFT: L.MARK_LEFT ?? null, MARK_BOTTOM: L.MARK_BOTTOM ?? null,
  FRAME_TITLE: L.FRAME_TITLE ?? null, FRAME_GAP: L.FRAME_GAP ?? null, BAND: C.BAND ?? null, HOP: C.HOP ?? null,
};
if (request.hop) out.hop = request.hop.map(([P, Q, ceiling]) => C.hop(P, Q, ceiling ?? undefined));
if (request.packMarks) out.packMarks = request.packMarks.map(([m, avail]) => ({ packed: L.packMarks(m, avail), rows: L.markRows(m, avail) }));
if (request.markSpots) out.markSpots = request.markSpots.map(([node, m]) => L.markSpots(node, m));
if (request.labelWidth) out.labelWidth = request.labelWidth.map((t) => C.labelWidth(t));
if (request.pairs) out.pairs = request.pairs.map((s) => C.commandPairs(s).map((p) => [p.parent.id, p.child.id]));

const placeJson = (p) =>
  p.kind === "mark" ? { kind: "mark", id: p.node.id, scope: p.scope }
    : p.kind === "frame" ? { kind: "frame", id: p.node.id }
      : p.kind === "group" ? { kind: "group", key: p.group.key, ids: p.group.ids }
        : { kind: "band", key: p.key };

function scenario(sc) {
  const { structure, summary } = sc;
  const ix = L.index(structure.scopes);
  let layout;
  let routes = sc.routes || [];
  if (Array.isArray(sc.layout?.nodes)) layout = { groups: [], ...sc.layout };
  else {
    const marks = Object.fromEntries(Object.entries(sc.marks || {}).map(([id, m]) => [id, { items: m.items, gap: m.gap }]));
    const opts = { ...(sc.layout || {}), ...(sc.marks ? { marks } : {}) };
    if (sc.routed) {
      const r = L.routeLayout(structure.scopes, structure.cleanup || [], opts);
      layout = r.layout;
      routes = r.routes;
    } else layout = L.layout(structure.scopes, structure.cleanup || [], opts);
  }
  const pairs = C.commandPairs(summary);
  const placed = C.placeAgents(pairs, { structure, summary, layout, ix });
  const res = {
    allPairs: pairs.map((p) => [p.parent.id, p.child.id]),
    nodes: Object.fromEntries(layout.nodes.map((n) => [n.id, { type: n.type, x1: n.x1, y1: n.y1, x2: n.x2, y2: n.y2, rows: n.rows ?? 1, kind: n.kind ?? null }])),
    groups: (layout.groups || []).map((g) => ({ key: g.key, ids: g.ids, x1: g.x1, y1: g.y1, x2: g.x2, y2: g.y2 })),
    width: layout.width,
    height: layout.height,
  };
  if (!placed) return { ...res, placed: null };
  const order = sc.order || {};
  const orderOf = (wt) => order[wt.id] || null;
  const items = C.bandItems(placed.pairs, placed.places, placed.own, orderOf);
  const spots = {};
  const spotsOf = (node) => {
    const s = L.markSpots(node, sc.marks?.[node.id]);
    spots[node.id] = s;
    return s;
  };
  const model = C.commandModel({ pairs: placed.pairs, places: placed.places, items, layout, spotsOf, routes });
  return {
    ...res,
    placed: {
      pairs: placed.pairs.map((p) => [p.parent.id, p.child.id]),
      places: Object.fromEntries([...placed.places].map(([id, p]) => [id, placeJson(p)])),
    },
    items: items.map((it) => ({ key: it.key, label: it.label, own: it.own, main: it.main, agents: it.agents.map((a) => a.id) })),
    spots,
    model: {
      band: model.band && {
        top: model.band.top, h: model.band.h, right: model.band.right,
        items: model.band.items.map((it) => ({ key: it.key, label: it.label, x: it.x, y: it.y, w: it.w, h: it.h, labelWidth: it.labelWidth, agents: it.agents.map(({ id, x, y, w, h }) => ({ id, x, y, w, h })) })),
      },
      links: model.links,
      ripples: model.ripples,
      audit: model.audit,
      top: model.top,
      width: model.width,
    },
    routes: routes.map((rt) => rt.pts),
  };
}
if (request.bandRows) {
  out.bandRows = request.bandRows.map((bc) => {
    const wt = { id: "wt", agents: [] };
    const ref = (id) => ({ id, mark: "working", worktree: wt });
    const rows = bc.rows.map((r) => ({ ...r, items: r.items.map((it) => ({ own: true, main: false, worktree: wt, badge: null, count: null, kind: "worktree", ...it, agents: it.agents.map(ref) })) }));
    const places = new Map();
    for (const r of rows) for (const it of r.items) for (const a of it.agents) places.set(a.id, { kind: "band", key: it.key });
    const pairs = (bc.pairs || []).map(([p, c]) => ({ parent: ref(p), child: ref(c) }));
    const model = C.commandModel({ pairs, places, rows, layout: { nodes: [], groups: [], width: 2000, height: 400 } });
    return {
      heights: rows.map((r) => C.bandRowHeight(r.items)),
      widths: rows.map((r) => C.bandRowWidth(r.items, r.lead)),
      band: model.band && {
        top: model.band.top, h: model.band.h, right: model.band.right,
        rows: model.band.rows.map((r) => ({ key: r.key, top: r.top, h: r.h, lead: r.lead, leadTitle: r.leadTitle ?? null })),
        items: model.band.items.map((it) => ({ key: it.key, kind: it.kind, badge: it.badge, count: it.count, x: it.x, y: it.y, w: it.w, h: it.h, labelWidth: it.labelWidth, agents: it.agents.map(({ id, x, y, w, h }) => ({ id, x, y, w, h })) })),
      },
      links: model.links,
      audit: model.audit,
    };
  });
}
if (request.scenarios) out.scenarios = Object.fromEntries(Object.entries(request.scenarios).map(([name, sc]) => [name, scenario(sc)]));

if (request.key) {
  const summary = { schema: "x" };
  const routing = { layout: {} };
  const marks = { a: { items: [36], gap: 2 } };
  const ids = { a: ["x"] };
  const k = (o) => C.commandKey({ summary, routing, marks, ids, ...o });
  out.key = {
    same: k({}) === k({}),
    copiedMarks: k({}) === k({ marks: JSON.parse(JSON.stringify(marks)), ids: JSON.parse(JSON.stringify(ids)) }),
    otherSummary: k({}) === k({ summary: { schema: "x" } }),
    otherRouting: k({}) === k({ routing: { layout: {} } }),
    otherWidth: k({}) === k({ marks: { a: { items: [40], gap: 2 } } }),
    otherIds: k({}) === k({ ids: { a: ["y"] } }),
  };
}

process.stdout.write(JSON.stringify(out));
