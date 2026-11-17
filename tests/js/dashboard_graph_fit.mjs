// The compact frames' measured heights (iss-00627 D-02, D-03), run by tests/unit/presentation/test_dashboard_graph_fit.py:
//   node dashboard_graph_fit.mjs <assets/dashboard directory> <request.json>
// request.json = {document: structure API document, layouts: {name: options}, compact: [[kind, rows], …],
//                 differ: [{nodes, needs}, …]}. Prints {layouts: {name: layout}, compact: [px], differ: [bool]}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const L = await load("views/graph/layout.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = { layouts: {}, compact: null, differ: null };
const doc = request.document;
for (const [name, opts] of Object.entries(request.layouts || {})) {
  const r = L.layout(doc.scopes, doc.cleanup, opts);
  out.layouts[name] = { width: r.width, height: r.height, nodes: r.nodes, groups: r.groups, edges: r.edges };
}
if (request.compact) out.compact = typeof L.compactHeight === "function" ? request.compact.map(([kind, rows]) => L.compactHeight(kind, rows)) : null;
if (request.differ) {
  let measure = null;
  try {
    measure = await load("views/graph/measure.js");
  } catch {
    measure = null;
  }
  out.differ = measure ? request.differ.map(({ nodes, needs }) => measure.headsDiffer(nodes, needs)) : null;
}
console.log(JSON.stringify(out));
