// The structure graph's and the cross structure's wheel and key input, shared by both screens (iss-00655).
//
// A mouse wheel zooms at the cursor; a trackpad's two fingers pan and its pinch zooms as before; Shift with the wheel
// pans sideways; the arrow keys pan and + - 0 zoom and fit like the buttons. No web standard tells a mouse wheel from a
// trackpad, so a wheel event that cannot be told apart pans (the old behaviour).

export const WHEEL = { step: 1.15, maxSteps: 2, stick: 200 };
export const KEYS = { pan: 80, fast: 4, zin: 1.25, zout: 0.8 };

// Read deltaMode before any wheelDelta*: Firefox turns deltaMode to pixels once wheelDelta* is read.
const modeOf = (e) => Number(e.deltaMode) || 0;

function kindOf(e, mode) {
  if (e.ctrlKey || e.metaKey) return "pinch"; // a trackpad's pinch (and Ctrl with a wheel)
  if (e.shiftKey) return "hpan";
  if (mode === 1 || mode === 2) return (e.deltaX || 0) === 0 ? "wheel" : "pan"; // lines or pages: a mouse wheel; a tilt pans
  const w = e.wheelDeltaY;
  if ((e.deltaX || 0) === 0 && typeof w === "number" && w !== 0 && w % 120 === 0) return "wheel?"; // a notch: likely a wheel
  return "pan";
}

// "pinch" | "hpan" | "wheel" (sure) | "wheel?" (likely) | "pan"
export function wheelKind(e) {
  return kindOf(e, modeOf(e));
}

// The wheel event's action. `last` is the previous {kind, at} (or null), `now` the time in ms, `page` one page in
// pixels (the view's width). Returns {act, kind, at}; the caller keeps {kind, at} as the next `last`.
export function wheelAction(e, last, now, page) {
  const mode = modeOf(e);
  let kind = kindOf(e, mode);
  // a notch-like value in the middle of a trackpad's stroke keeps panning
  if (kind === "wheel?" && last?.kind === "pan" && now - last.at < WHEEL.stick) kind = "pan";
  const dx = e.deltaX || 0;
  const dy = e.deltaY || 0;
  const u = mode === 1 ? 16 : mode === 2 ? page : 1;
  let act = null;
  if (kind === "pinch") act = { type: "zoom", f: Math.exp(-dy * 0.01), x: e.clientX, y: e.clientY };
  else if (kind === "wheel" || kind === "wheel?") {
    if (dy !== 0) {
      const w = mode === 0 && typeof e.wheelDeltaY === "number" ? Math.abs(e.wheelDeltaY) : 0;
      const n = w ? Math.min(WHEEL.maxSteps, Math.max(1, Math.round(w / 120))) : 1;
      act = { type: "zoom", f: WHEEL.step ** (dy < 0 ? n : -n), x: e.clientX, y: e.clientY };
    }
  } else if (kind === "hpan") act = { type: "pan", dx: -(dx !== 0 ? dx : dy) * u, dy: 0 };
  else act = { type: "pan", dx: -dx * u, dy: -dy * u };
  return { act, kind, at: now };
}

// The key's action, or null when the graph does not take it.
export function keyAction(e) {
  if (e.ctrlKey || e.metaKey || e.altKey || e.isComposing || e.defaultPrevented) return null;
  const d = KEYS.pan * (e.shiftKey ? KEYS.fast : 1);
  switch (e.key) {
    case "ArrowLeft":
      return { type: "pan", dx: d, dy: 0 };
    case "ArrowRight":
      return { type: "pan", dx: -d, dy: 0 };
    case "ArrowUp":
      return { type: "pan", dx: 0, dy: d };
    case "ArrowDown":
      return { type: "pan", dx: 0, dy: -d };
    case "+":
    case "=":
      return { type: "zoom", f: KEYS.zin };
    case "-":
      return { type: "zoom", f: KEYS.zout };
    case "0":
      return { type: "fit" };
    default:
      return null;
  }
}

const OTHER_INPUT = 'input, textarea, select, button, a[href], summary, iframe, [contenteditable]:not([contenteditable="false"])';

// Whether a keydown belongs to the graph `view`: focus on the page around it (body, html, the screen's main) or inside
// it, and not on a field, a native button or link, or anything else outside the view (the panel, the tool bar).
export function ownsKey(e, view) {
  const t = e.target;
  if (!t || typeof t.closest !== "function") return true;
  if (typeof t.contains === "function" && t.contains(view)) return true;
  if (t.closest(OTHER_INPUT)) return false;
  return !!view?.contains(t);
}
