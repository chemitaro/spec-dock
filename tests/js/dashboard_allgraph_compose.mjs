// The cross-repository structure's frames (iss-00614 T-01, T-02), computed by views/allgraph/compose.js in node.
//
// usage: node dashboard_allgraph_compose.mjs <dashboard assets dir> <request.json>
// request: {cases: {name: {repos, sizes, options}}, bodyWidth: [[width, depth], …],
//           anchor: [[prev case name, next case name, view], …]}
// Prints {REPO, cases: {name: {frames: {key: frame}, order, width, height, other}}, bodyWidth: [value, …],
//         anchor: [{dx, dy}, …]} (iss-00617 T-02: anchorShift of two cases' results).
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const { REPO, anchorShift, bodyWidth, compose } = await import(pathToFileURL(path.join(assets, "views/allgraph/compose.js")).href);
const request = JSON.parse(readFileSync(requestPath, "utf8"));

const cases = {};
const results = {};
for (const [name, c] of Object.entries(request.cases || {})) {
  const args = [c.repos, c.sizes];
  if (c.options !== undefined) args.push(c.options);
  const r = compose(...args);
  results[name] = r;
  const json = { frames: Object.fromEntries(r.frames), order: r.order, width: r.width, height: r.height };
  if ("other" in r) json.other = r.other;
  cases[name] = json;
}
const widths = (request.bodyWidth || []).map(([w, d]) => bodyWidth(w, d));
const anchor = (request.anchor || []).map(([a, b, view]) => anchorShift(results[a], results[b], view));
process.stdout.write(JSON.stringify({ REPO, cases, bodyWidth: widths, anchor }));
