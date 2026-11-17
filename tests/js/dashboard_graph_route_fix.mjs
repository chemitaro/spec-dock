// The routing's fixes of iss-00627 (D-04, D-05), run by tests/unit/presentation/test_dashboard_graph_route_fix.py:
//   node dashboard_graph_route_fix.mjs <assets/dashboard directory> <request.json>
// request.json = {inputs: <tests/fixtures/issue627/route_inputs.json>} for the fixed inputs (T-01), and/or
// {graphs: {name: G}} for route(G) on small inputs given directly (T-02). Prints one JSON object.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const { routeLayout } = await load("views/graph/layout.js");
const { audit, route } = await load("views/graph/router.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const KEYS = ["boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed"];
const counts = (routes, G) => {
  const a = audit(routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: G.obs[G.edges[rt.ei].a].key, kz: G.obs[G.edges[rt.ei].z].key })), G.obs);
  return { ...Object.fromEntries(KEYS.map((k) => [k, a[k]])), list: a.list };
};
const out = { cases: {}, graphs: {} };
if (request.inputs) {
  for (const c of request.inputs.cases) {
    const s = request.inputs.structures[c.structure];
    const x = routeLayout(s.scopes, s.cleanup, { mode: "nest", range: c.range, focus: null, width: c.width, marks: s.marks });
    out.cases[c.name] = counts(x.routes, x.G);
  }
}
for (const [name, G] of Object.entries(request.graphs || {})) {
  const res = route(G);
  out.graphs[name] = { ...counts(res.routes, G), ends: res.routes.map((rt) => ({ ei: rt.ei, y1: rt.pts[0].y, y2: rt.pts.at(-1).y })) };
}
console.log(JSON.stringify(out));
