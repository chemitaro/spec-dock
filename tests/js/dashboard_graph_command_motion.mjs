// The command lines' drawing as pure computation (iss-00646 D-01). Run by
// tests/unit/presentation/test_dashboard_graph_command_motion.py:
//   node dashboard_graph_command_motion.mjs <assets/dashboard directory> <request.json>
// request.json:
//   boxOf: [[ds, pad | null, dots | null], …]  -> boxOf of each (pad null: the default)
//   links: [link, …]                           -> bodyHtml, endsHtml and bandMarkHtml of each
//   arrow: [to, …]                             -> arrowPath of each (iss-00648 D-04)
//   markRect: [mark, …]                        -> markRect of each
//   ripples: [ripple, …]                       -> rippleHtml of each
//   svgOpen: [[box, cls, extra], …]            -> svgOpen of each
//   dots: [[d, off], …]                        -> dotsHtml of each (iss-00657 D-01)
// Always: MOTION, ARROW, phaseDelay and phaseOffset of 0..phases−1, and which phase shows at each time over two rounds
// (0..2·phases·tick by 0.01), computed from the switching keyframes (shown in the first 1/phases of each round) and each
// phase's delay.
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
out.ARROW = M.ARROW ?? null;
out.delays = [...Array(n).keys()].map((i) => M.phaseDelay(i));
out.offsets = [...Array(n).keys()].map((i) => M.phaseOffset(i));

// which phases show at time t: in thousandths of a second, so no float edge falls between two phases
const ms = (s) => Math.round(s * 1000);
const round = ms(M.MOTION.phases * M.MOTION.tick);
out.timeline = [];
const steps = (2 * round) / 10;
for (let k = 0; k <= steps; k++) {
  const t = k * 10;
  const shown = [];
  for (let i = 0; i < n; i++) {
    const local = (((t - ms(M.phaseDelay(i))) % round) + round) % round; // the animation's time in its round
    if (local < round / n) shown.push(i); // keyframes: opacity 1 in the first 1/phases, 0 after (steps(1, end))
  }
  out.timeline.push({ t: t / 1000, shown, offsets: shown.map((i) => M.phaseOffset(i)) });
}

if (request.boxOf) out.boxOf = request.boxOf.map(([ds, pad, dots]) => (pad === null ? M.boxOf(ds) : M.boxOf(ds, pad, dots ?? [])));
if (request.links) out.links = request.links.map((l) => ({ body: M.bodyHtml(l), ends: M.endsHtml(l), band: M.bandMarkHtml ? M.bandMarkHtml(l) : null }));
if (request.arrow) out.arrow = request.arrow.map((to) => (M.arrowPath ? M.arrowPath(to) : null));
if (request.markRect) out.markRect = request.markRect.map((m) => (M.markRect ? M.markRect(m) : null));
if (request.ripples) out.ripples = request.ripples.map((r) => M.rippleHtml(r));
if (request.dots) out.dots = request.dots.map(([d, off]) => (M.dotsHtml ? M.dotsHtml(d, off) : null));
if (request.svgOpen) out.svgOpen = request.svgOpen.map(([box, cls, extra]) => M.svgOpen(box, cls, extra));

process.stdout.write(JSON.stringify(out));
