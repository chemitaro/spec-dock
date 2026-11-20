// The Unscoped row's items (iss-00668 D-02). Run by tests/unit/presentation/test_dashboard_graph_unscoped.py:
//   node dashboard_graph_unscoped.mjs <assets/dashboard directory> <request.json>
// request.json:
//   cases: {name: {structure, summary, range, order: {worktree id: [agent id, …]}}}
//          -> placeAgents and unscopedItems of each, as the structure graph runs them (iss-00676 D-01: every range
//             places its pairs; the range only shapes the layout, and a range given to unscopedItems changes nothing)
//   labels: [[worktree, own], …]           -> bandLabel of each
// out.exports: the module's exported names (iss-00676 D-03: no count's helpers)
// Prints one JSON object; the Python test asserts on it. Every value is synthetic.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const L = await load("views/graph/layout.js");
const C = await load("views/graph/command.js");
const U = await load("views/graph/unscoped.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = { consts: { UNSCOPED: U.UNSCOPED ? { ...U.UNSCOPED, count: typeof U.UNSCOPED.count === "function" ? "function" : U.UNSCOPED.count ?? null } : null, FOLD: U.FOLD ?? null }, exports: Object.keys(U).sort() };

const placeJson = (p) => (p.kind === "band" ? { kind: "band", key: p.key } : { kind: p.kind });
const itemJson = (it) => ({
  key: it.key,
  kind: it.kind,
  label: it.label,
  badge: it.badge,
  own: it.own,
  main: it.main,
  path: it.path,
  agents: it.agents.map((a) => a.id),
  agentWorktrees: it.agents.map((a) => a.worktree?.id ?? null),
  worktree: it.worktree ? { id: it.worktree.id ?? null, agents: (it.worktree.agents || []).map((a) => a.id) } : null,
  idle: it.idle,
  folded: it.folded ?? null,
  fields: Object.keys(it).sort(),
});

function run(sc) {
  const { structure, summary } = sc;
  const range = sc.range || "all";
  const pairs = C.commandPairs(summary);
  let places = new Map();
  let own = new Set();
  if (pairs.length) {
    const scopes = structure?.scopes || [];
    const ix = L.index(scopes);
    const layout = L.layout(scopes, [], { mode: "nest", range });
    const placed = C.placeAgents(pairs, { structure, summary, layout, ix });
    if (placed) {
      places = placed.places;
      own = placed.own;
    }
  }
  own = C.ownWorktrees(structure, summary) || own;
  const order = sc.order || {};
  const orderOf = (w) => (Array.isArray(order[w?.id]) ? order[w.id] : null);
  const res = U.unscopedItems({ structure, summary, pairs, places, own, orderOf, range });
  const keys = summary && Array.isArray(summary.worktrees) && summary.schema ? C.bandKeys(summary) : new Map();
  return {
    items: res.items.map(itemJson),
    places: Object.fromEntries([...res.places].map(([id, p]) => [id, placeJson(p)])),
    placesBefore: Object.fromEntries([...places].map(([id, p]) => [id, placeJson(p)])),
    bandKeys: Object.fromEntries([...keys].map(([w, k]) => [w.id ?? "", k])),
    git: U.gitWorktrees(structure),
  };
}

if (request.cases) out.cases = Object.fromEntries(Object.entries(request.cases).map(([name, sc]) => [name, run(sc)]));
if (request.labels) out.labels = request.labels.map(([w, own]) => C.bandLabel(w, own));

process.stdout.write(JSON.stringify(out));
