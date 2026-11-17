// The command lines' drawing as pure computation (iss-00646 D-01): each line in SVGs of its own bounding box, a flowing
// line's dots as four still pictures shifted along the line and shown in turn by an opacity animation (graph.css
// sd-cmd-phase, run on the compositor), and each ripple as an HTML ring pair. No DOM: node checks it.
import { esc } from "./marks.js";

/** The switching: phases pictures, each step px further along the line, each shown for tick s; pad px around a box. */
export const MOTION = { phases: 4, step: 2, tick: 0.05, pad: 4 };

const NUM = /-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?/gi;

/**
 * The integer box {x, y, w, h} around every point of the paths ds ("M x y C …" and "M x y L …", read as pairs of
 * numbers) and the dots ({x, y, r}), pad px beyond them; null without a point. A cubic Bézier lies in the hull of its
 * control points, so the box holds the whole curve.
 */
export function boxOf(ds, pad = MOTION.pad, dots = []) {
  let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
  const take = (x, y, r = 0) => {
    x1 = Math.min(x1, x - r);
    y1 = Math.min(y1, y - r);
    x2 = Math.max(x2, x + r);
    y2 = Math.max(y2, y + r);
  };
  for (const d of ds || []) {
    const nums = (String(d).match(NUM) || []).map(Number);
    for (let i = 0; i + 1 < nums.length; i += 2) take(nums[i], nums[i + 1]);
  }
  for (const p of dots || []) take(p.x, p.y, p.r || 0);
  if (!Number.isFinite(x1)) return null;
  const x = Math.floor(x1 - pad), y = Math.floor(y1 - pad);
  return { x, y, w: Math.ceil(x2 + pad) - x, h: Math.ceil(y2 + pad) - y };
}

/** The i-th picture's animation-delay (s): it shows while t mod (phases·tick) is in [tick·i, tick·(i+1)). */
export const phaseDelay = (i) => -Math.round((((MOTION.phases - i) % MOTION.phases) * MOTION.tick) * 1000) / 1000 || 0;

/** The i-th picture's dash offset (px): a negative offset moves the dots along the path, from the parent to the child. */
export const phaseOffset = (i) => -MOTION.step * i || 0;

/** An SVG at its box in the world, its viewBox the same box (the paths keep the world's coordinates). */
export const svgOpen = (box, cls, extra = "", attrs = "") =>
  `<svg class="${cls}"${attrs} style="left:${box.x}px;top:${box.y}px${extra}" width="${box.w}" height="${box.h}" viewBox="${box.x} ${box.y} ${box.w} ${box.h}" aria-hidden="true">`;

const phases = (box, g, inner) =>
  Array.from({ length: MOTION.phases }, (_, i) => `${svgOpen(box, "cl-svg cl-ph", `;animation-delay:${phaseDelay(i)}s`, ` data-ph="${i}"`)}${g}${inner(phaseOffset(i))}</g></svg>`).join("");

/** The line's body layer (.gx-cmd): its glow and, unless it flows, its still line; a flowing line's four pictures. */
export function bodyHtml(link) {
  const box = boxOf([link.d]);
  if (!box) return "";
  const g = `<g class="cl" data-id="${esc(link.id)}" data-parent="${esc(link.parent)}" data-child="${esc(link.child)}" data-state="${esc(link.state)}">`;
  const flow = link.state === "flow";
  const still = `${svgOpen(box, "cl-svg")}${g}<path class="cl-glow" d="${esc(link.d)}"/>${flow ? "" : `<path class="cl-line" d="${esc(link.d)}"/>`}</g></svg>`;
  return flow ? still + phases(box, g, (off) => `<path class="cl-line" d="${esc(link.d)}" style="stroke-dashoffset:${off}px"/>`) : still;
}

/** The line's ends layer (.gx-cmd-top): its stubs in the boxes and the dot at its end; a flowing line's stubs in four pictures. */
export function endsHtml(link) {
  const stubs = Array.isArray(link.stubs) ? link.stubs : [];
  const dot = link.to ? [{ x: link.to.x, y: link.to.y, r: 2.5 }] : [];
  const box = boxOf(stubs, MOTION.pad, dot);
  if (!box) return "";
  const g = `<g class="cl" data-id="${esc(link.id)}" data-state="${esc(link.state)}">`;
  const flow = link.state === "flow";
  const lines = (off) => stubs.map((d) => `<path class="cl-stub" d="${esc(d)}"${off === null ? "" : ` style="stroke-dashoffset:${off}px"`}/>`).join("");
  const end = dot.length ? `<circle class="cl-dot" cx="${link.to.x}" cy="${link.to.y}" r="2.5"/>` : "";
  const still = `${svgOpen(box, "cl-svg")}${g}${flow ? "" : lines(null)}${end}</g></svg>`;
  return flow && stubs.length ? still + phases(box, g, lines) : still;
}

/** A ripple: an HTML ring pair centred at its place (the rings' size is graph.css's). */
export const rippleHtml = (r) => `<span class="cr" data-agent="${esc(r.agent)}" style="left:${r.x}px;top:${r.y}px"><i class="cr-a"></i><i class="cr-b"></i></span>`;
