// The cross-repository structure's notices (iss-00632 D-01, D-02), run by
// tests/unit/presentation/test_dashboard_allgraph_notices.py:
//   node dashboard_allgraph_notices.mjs <assets/dashboard directory> <request.json>
// request.json = {warnings: {name: [structure, failure]}, split: {name: [repo]}}
// (repo = {repository, owner, name, failed, warnings} or, with `structure`/`failure` and no `warnings`, the warnings
// overviewWarnings gives them). Prints {warnings: {name: overviewWarnings' result}, split: {name: {summary, own}}}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const logic = await load("views/_shared/logic.js");
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = { warnings: {}, split: {} };
for (const [name, [structure, failure]] of Object.entries(request.warnings || {})) out.warnings[name] = logic.overviewWarnings(structure, failure);
let notices = null;
try {
  notices = await load("views/allgraph/notices.js");
} catch {
  notices = null;
}
out.shared = notices ? Object.keys(notices.SHARED) : null;
for (const [name, repos] of Object.entries(request.split || {})) {
  if (!notices) {
    out.split[name] = null;
    continue;
  }
  const input = repos.map((r) => ("warnings" in r ? r : { ...r, warnings: logic.overviewWarnings(r.structure ?? null, r.failure ?? null) }));
  const res = notices.splitNotices(input);
  out.split[name] = { summary: res.summary, own: Object.fromEntries(res.own) };
}
console.log(JSON.stringify(out));
