// The command lines' drawing as pure computation (iss-00646 D-01). Run by
// tests/unit/presentation/test_dashboard_graph_command_motion.py:
//   node dashboard_graph_command_motion.mjs <assets/dashboard directory> <request.json>
// request.json:
//   boxOf: [[ds, pad | null, dots | null], …]  -> boxOf of each (pad null: the default)
//   links: [link, …]                           -> bodyHtml and endsHtml of each
//   ripples: [ripple, …]                       -> rippleHtml of each
//   svgOpen: [[box, cls, extra], …]            -> svgOpen of each
// Always: MOTION, phaseDelay and phaseOffset of 0..3, and which phase shows at each time (0..0.4 by 0.01), computed from
// the switching keyframes (shown in 0..25% of each round) and each phase's delay.
// Prints one JSON object; the Python test asserts on it.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets, requestPath] = process.argv.slice(2);
const M = await import(pathToFileURL(path.join(assets, "views/graph/command_motion.js")).href);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const out = {};

const n = M.MOTION.phases;
out.MOTION = M.MOTION;
out.delays = [...Array(n).keys()].map((i) => M.phaseDelay(i));
out.offsets = [...Array(n).keys()].map((i) => M.phaseOffset(i));

// which phases show at time t: in thousandths of a second, so no float edge falls between two phases
const ms = (s) => Math.round(s * 1000);
const round = ms(M.MOTION.phases * M.MOTION.tick);
out.timeline = [];
for (let k = 0; k <= 40; k++) {
  const t = k * 10;
  const shown = [];
  for (let i = 0; i < n; i++) {
    const local = (((t - ms(M.phaseDelay(i))) % round) + round) % round; // the animation's time in its round
    if (local < round / 4) shown.push(i); // keyframes: opacity 1 in 0..25%, 0 after (steps(1, end))
  }
  out.timeline.push({ t: t / 1000, shown, offsets: shown.map((i) => M.phaseOffset(i)) });
}

if (request.boxOf) out.boxOf = request.boxOf.map(([ds, pad, dots]) => (pad === null ? M.boxOf(ds) : M.boxOf(ds, pad, dots ?? [])));
if (request.links) out.links = request.links.map((l) => ({ body: M.bodyHtml(l), ends: M.endsHtml(l) }));
if (request.ripples) out.ripples = request.ripples.map((r) => M.rippleHtml(r));
if (request.svgOpen) out.svgOpen = request.svgOpen.map(([box, cls, extra]) => M.svgOpen(box, cls, extra));

process.stdout.write(JSON.stringify(out));
