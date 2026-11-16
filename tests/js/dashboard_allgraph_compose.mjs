// The cross-repository structure's frames (iss-00614 T-01, T-02), computed by views/allgraph/compose.js in node.
//
// usage: node dashboard_allgraph_compose.mjs <dashboard assets dir> <request.json>
// request: {cases: {name: {repos, sizes, options}}, bodyWidth: [[width, depth], …]}
// Prints {REPO, cases: {name: {frames: {key: frame}, order, width, height}}, bodyWidth: [value, …]}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const { REPO, bodyWidth, compose } = await import(pathToFileURL(path.join(assets, "views/allgraph/compose.js")).href);
const request = JSON.parse(readFileSync(requestPath, "utf8"));

const cases = {};
for (const [name, c] of Object.entries(request.cases || {})) {
  const args = [c.repos, c.sizes];
  if (c.options !== undefined) args.push(c.options);
  const r = compose(...args);
  cases[name] = { frames: Object.fromEntries(r.frames), order: r.order, width: r.width, height: r.height };
}
const widths = (request.bodyWidth || []).map(([w, d]) => bodyWidth(w, d));
process.stdout.write(JSON.stringify({ REPO, cases, bodyWidth: widths }));
