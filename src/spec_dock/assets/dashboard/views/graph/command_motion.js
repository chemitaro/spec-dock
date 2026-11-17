// The command lines' drawing as pure computation (iss-00646 D-01, iss-00657 D-01): each line in SVGs of its own bounding
// box, a flowing line's dots as pairs 24px apart (a large head and a small tail 6px behind it) in twelve still pictures
// shifted 2px along the line and shown in turn for 0.1s each by an opacity animation (graph.css sd-cmd-phase, run on the
// compositor: 20px/s, one round of 1.2s), and each ripple as an HTML ring pair. No DOM: node checks it.
import { esc } from "./marks.js";

/**
 * The switching: phases pictures, each step px further along the line, each shown for tick s; the dots' pairs gap px
 * apart (the dash period, phases·step: one round moves them one pair on), the tail tail px behind the head; pad px
 * around a box. graph.css copies phases·tick (1.2s), gap (0.1 23.9) and 1/phases (8.334%).
 */
export const MOTION = { phases: 12, step: 2, tick: 0.1, gap: 24, tail: 6, pad: 4 };

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

/**
 * One picture's dots (iss-00657 D-01): the path twice, its head at offset off and its tail at off + tail. A dot sits at
 * k·gap − offset along the path, so the tail's larger offset puts it tail px behind the head, on the parent's side.
 */
export function dotsHtml(d, off) {
  const p = esc(d);
  return `<path class="cl-line cl-hd" d="${p}" style="stroke-dashoffset:${off || 0}px"/><path class="cl-line cl-tl" d="${p}" style="stroke-dashoffset:${off + MOTION.tail || 0}px"/>`;
}

const phases = (box, g, inner) =>
  Array.from({ length: MOTION.phases }, (_, i) => `${svgOpen(box, "cl-svg cl-ph", `;animation-delay:${phaseDelay(i)}s`, ` data-ph="${i}"`)}${g}${inner(phaseOffset(i))}</g></svg>`).join("");

/** The line's body layer (.gx-cmd): its glow and, unless it flows, its still line; a flowing line's twelve pictures. */
export function bodyHtml(link) {
  const box = boxOf([link.d]);
  if (!box) return "";
  const g = `<g class="cl" data-id="${esc(link.id)}" data-parent="${esc(link.parent)}" data-child="${esc(link.child)}" data-state="${esc(link.state)}">`;
  const flow = link.state === "flow";
  const still = `${svgOpen(box, "cl-svg")}${g}<path class="cl-glow" d="${esc(link.d)}"/>${flow ? "" : `<path class="cl-line" d="${esc(link.d)}"/>`}</g></svg>`;
  return flow ? still + phases(box, g, (off) => dotsHtml(link.d, off)) : still;
}

/** The arrowhead at the child's end (iss-00648 D-04): len px long, half px to each side. */
export const ARROW = { len: 6, half: 3.5 };

const n1 = (v) => Math.round(v * 10) / 10;

/** A downward triangle with its tip at `to`. */
export const arrowPath = (to) =>
  `M ${n1(to.x - ARROW.half)} ${n1(to.y - ARROW.len)} L ${n1(to.x)} ${n1(to.y)} L ${n1(to.x + ARROW.half)} ${n1(to.y - ARROW.len)} Z`;

// the ring's rectangle: the mark 2px out on every side
const ringOf = (m) => ({ x: n1(m.x - 2), y: n1(m.y - 2), w: n1(m.w + 4), h: n1(m.h + 4) });

/** The ring around the child's mark (iss-00648 D-04): the mark's rectangle 2px out, rounded. */
export function markRect(m) {
  const r = ringOf(m);
  return `<rect class="cl-in" x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" rx="4"/>`;
}
const ringPath = (m) => {
  const r = ringOf(m);
  return `M ${r.x} ${r.y} L ${n1(r.x + r.w)} ${n1(r.y + r.h)}`;
};

/**
 * The line's ends layer (.gx-cmd-top): its stubs, the arrowhead at its end and the ring of the child's mark in a box or
 * a frame's heading (a band child's ring is bandMarkHtml's); a flowing line's stubs (one cl-stub each) in the pictures.
 */
export function endsHtml(link) {
  const stubs = Array.isArray(link.stubs) ? link.stubs : [];
  const arrow = link.to ? arrowPath(link.to) : null;
  const mark = link.mark && !link.mark.band ? link.mark : null;
  const box = boxOf([...stubs, ...(arrow ? [arrow] : []), ...(mark ? [ringPath(mark)] : [])]);
  if (!box) return "";
  const g = `<g class="cl" data-id="${esc(link.id)}" data-state="${esc(link.state)}">`;
  const flow = link.state === "flow";
  const lines = (off) => stubs.map((d) => `<path class="cl-stub" d="${esc(d)}"${off === null ? "" : ` style="stroke-dashoffset:${off}px"`}/>`).join("");
  const end = `${mark ? markRect(mark) : ""}${arrow ? `<path class="cl-arrow" d="${arrow}"/>` : ""}`;
  const still = `${svgOpen(box, "cl-svg")}${g}${flow ? "" : lines(null)}${end}</g></svg>`;
  return flow && stubs.length ? still + phases(box, g, lines) : still;
}

/** A band child's ring (iss-00648 D-04): one SVG of the line's own in the band's layer (.gx-band-cr); "" otherwise. */
export function bandMarkHtml(link) {
  if (!link.mark?.band) return "";
  const box = boxOf([ringPath(link.mark)]);
  return `${svgOpen(box, "cl-svg")}<g class="cl" data-id="${esc(link.id)}" data-state="${esc(link.state)}">${markRect(link.mark)}</g></svg>`;
}

/** A ripple: an HTML ring pair centred at its place (the rings' size is graph.css's). */
export const rippleHtml = (r) => `<span class="cr" data-agent="${esc(r.agent)}" style="left:${r.x}px;top:${r.y}px"><i class="cr-a"></i><i class="cr-b"></i></span>`;
