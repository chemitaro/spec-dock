// What the page measures after drawing for the layout (iss-00627 D-03): the compact frames' contents. graph.css fits a
// one-line title in the layout's height (compactHeight); a title that wraps to two lines needs more, which only the
// drawn page knows. headsDiffer is pure, so the node check tests it; compactNeeds reads the DOM.
import { compactHeight } from "./layout.js";

// A measured height may exceed the exact one by a rounding error of the transformed coordinates: up to this much is not
// a taller frame (a one-line title fits compactHeight exactly).
const SLACK = 0.25;

/**
 * {Scope id: px} of every compact frame's contents in `root` at 100% (its top edge to its bottom edge: the summary row's
 * bottom, the bottom padding and the bottom border), or null when they cannot be measured: the graph is hidden or has
 * no width, or graph.css does not apply yet (the summary row is not a flex row) (F-01).
 * @param root  the element holding the frames (the graph's world, or a repository's graph area)
 * @param scale the zoom the world is drawn at
 */
export function compactNeeds(root, scale) {
  if (!root || !root.isConnected || !root.getClientRects().length || !(scale > 0)) return null;
  const out = {};
  for (const el of root.querySelectorAll(".gx-frame.is-compact[data-id]")) {
    const fm = el.querySelector(":scope > .gx-fm");
    if (!fm) continue;
    if (getComputedStyle(fm).display !== "flex") return null;
    const cs = getComputedStyle(el);
    const top = el.getBoundingClientRect().top;
    const raw = (fm.getBoundingClientRect().bottom - top) / scale + (parseFloat(cs.paddingBottom) || 0) + (parseFloat(cs.borderBottomWidth) || 0);
    if (!(raw > 0)) return null;
    out[el.dataset.id] = Math.ceil(raw - SLACK);
  }
  return out;
}

/**
 * The needs above their compact frame's compactHeight (at the rows it was laid out with): what the layout's heads keep,
 * so a page that measured only frames that fit lays out as without heads (and a repository's signature does not move).
 */
export function tallNeeds(nodes, needs) {
  const out = {};
  if (!needs) return out;
  for (const n of nodes) {
    if (n.type !== "frame" || !n.compact) continue;
    const need = Number(needs[n.id]) || 0;
    if (need > compactHeight(n.kind, n.rows ?? 1)) out[n.id] = need;
  }
  return out;
}

/**
 * Whether laying out with these measured needs would give a layout's compact frames other heights: for each compact
 * frame, the larger of its compactHeight (at the rows of agents it was laid out with) and its need, against the height
 * it was laid out with (node.fit, else compactHeight).
 * @param nodes the layout's nodes
 * @param needs compactNeeds' result
 */
export function headsDiffer(nodes, needs) {
  if (!needs) return false;
  return nodes.some((n) => {
    if (n.type !== "frame" || !n.compact) return false;
    const base = compactHeight(n.kind, n.rows ?? 1);
    const want = Math.max(base, Number(needs[n.id]) || 0);
    return Math.abs(want - (n.fit ?? base)) > 0.5;
  });
}
