import { readFileSync } from "node:fs";
const { routeLayout } = await import(process.argv[2] + "/views/graph/layout.js");
const { audit } = await import(process.argv[2] + "/views/graph/router.js");
const doc = JSON.parse(readFileSync(process.argv[3], "utf8"));
for (const width of [1440 - 16, 374]) {
  const t0 = performance.now();
  const r = routeLayout(doc.scopes, doc.cleanup, { width });
  const a = audit(r.routes.map((rt) => ({ pts: rt.pts, failed: rt.failed, ka: r.G.obs[r.G.edges[rt.ei].a].key, kz: r.G.obs[r.G.edges[rt.ei].z].key })), r.G.obs);
  const L = r.layout;
  const at = new Map(L.nodes.map((n) => [n.id, n]));
  console.log("width", width, "size", Math.round(L.width), Math.round(L.height), "ms", Math.round(performance.now() - t0), JSON.stringify({ b: a.boxHits, o: a.overlaps, own: a.ownHits, d: a.diagonal, p: a.portShare, f: a.failed }));
  for (const id of ["epic-00424", "epic-00425", "epic-00427", "epic-00471", "epic-00526", "epic-00547"]) {
    const n = at.get(id);
    console.log(" ", id, n ? `${Math.round(n.x1)},${Math.round(n.y1)} - ${Math.round(n.x2)},${Math.round(n.y2)}` : "-");
  }
}
