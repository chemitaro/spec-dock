// The structure graph's command lines and band on the page (iss-00616 T-05), with the fake DOM and the fake orca.
//   node dashboard_graph_command_screen.mjs <dashboard assets dir> <request.json>
// request: {doc: structure document, runs: [{name, orca: false | {summary, order}, styled?, steps: [step]}], legend: bool}
// styled: the screen's CSS is already there at the first render (a return to the screen: the first view at once)
// step: {summary, order?} (orca-web's news with this summary), {news: true} (news with the same summary),
//       {render: true} (the shell renders again), {revision: "r2"} (a new structure revision rendered),
//       {styled: true} (the screen's CSS applies: the first view is placed), {act: "fit"} (a toolbar button),
//       {tap: selector} (a pointer tap), {key: "Enter" | " " | "Escape", on: selector?}, {click: selector},
//       {drag: true} (a drag on the graph area), {wheel: {dx, dy}}, {advance: ms} (the motion's clock, iss-00646),
//       {hidden: bool} (the page goes to the back or comes back), {tell: {sel, hit}} (IntersectionObserver's answer)
// iss-00655: wheel also takes {mode (deltaMode), wy (wheelDeltaY), shift, ctrl, x, y}; key takes shift, and on: "main"
// (the screen's container) or "input" (an input in the graph area); {viewHidden: bool} hides the graph area.
// run.io: the page has an IntersectionObserver (the fake one of fake_motion.mjs); without it, none (F-01).
// Prints {runs: {name: [snapshot after the first render, snapshot after each step]}, after: {name: what is left after
// leaving the screen}, legend: the legend's HTML by renderLegend's options (legend: true)}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { Element, fakeOrca, hooks, install, json, settle } from "./fake_dom.mjs";
import { installMotion } from "./fake_motion.mjs";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const page = install({ fetch: async () => json({ error: { message: "not found" } }, 404) });
const motion = installMotion(page);
let styled = false;
const computed = globalThis.getComputedStyle;
globalThis.getComputedStyle = (el) => ({ ...computed(el), position: styled && el?.classList?.contains("gx") ? "absolute" : "" });
// the bar above the graph is 40px tall; the graph area is the fake's 1200 × 800
hooks.rect = (el) =>
  ["gx-next", "gx-crumbs", "gx-tools"].some((c) => el.classList?.contains(c)) ? { left: 0, top: 0, right: 100, bottom: 40, width: 100, height: 40 } : null;
const graph = (await import(pathToFileURL(`${assets}/views/graph.js`).href)).default;

const ids = new WeakMap();
let next = 0;
const idOf = (el) => {
  if (!el) return null;
  if (!ids.has(el)) ids.set(el, ++next);
  return ids.get(el);
};

function snap(root) {
  const q = (sel) => root.querySelector(sel);
  const world = q(".gx-world");
  const panel = q(".panel");
  const iframe = panel.querySelector("iframe");
  const classes = (sel, key) => Object.fromEntries(world.querySelectorAll(sel).map((el) => [el.dataset[key], el.classes().filter((c) => c.startsWith("is-")).join(" ")]));
  const audit = globalThis.window.specdockCmdAudit?.() ?? null;
  return {
    layers: world.children.filter((c) => c instanceof Element).map((c) => c.getAttribute("class")),
    html: world.innerHTML,
    edges: idOf(q(".gx-edges")),
    cmd: idOf(q(".gx-cmd")),
    top: idOf(q(".gx-cmd-top")),
    band: idOf(q(".gx-band")),
    cmdSel: [...world.querySelectorAll(".gx-cmd, .gx-cmd-top")].map((s) => s.classList.contains("has-cmd-sel")),
    lines: classes(".gx-cmd .cl", "id"),
    ends: classes(".gx-cmd-top .cl", "id"),
    ripples: classes(".cr", "agent"),
    topRipples: world.querySelectorAll(".gx-cmd-top .cr").map((g) => g.dataset.agent),
    bandRipples: world.querySelectorAll(".gx-band .cr").map((g) => g.dataset.agent),
    bandRippleAt: world.querySelectorAll(".gx-band .cr").map((c) => {
      const m = /^left:(-?[\d.]+)px;top:(-?[\d.]+)px$/.exec(c.getAttribute("style") || "");
      return m ? [Number(m[1]), Number(m[2])] : null;
    }),
    bandLast: (() => {
      const kids = q(".gx-band")?.children.filter((c) => c instanceof Element) ?? [];
      return kids.length ? kids[kids.length - 1].getAttribute("class") : null;
    })(),
    bandSel: world.querySelectorAll(".gx-band > .gx-band-cr").map((s) => s.classList.contains("has-cmd-sel")),
    layerTags: world.querySelectorAll(".gx-cmd, .gx-cmd-top, .gx-band-cr").map((el) => el.tag),
    svgs: world.querySelectorAll(".gx-cmd svg, .gx-cmd-top svg, .gx-band-cr svg").map((sv) => ({
      layer: sv.closest(".gx-cmd, .gx-cmd-top, .gx-band-cr").getAttribute("class").split(" ")[0],
      cls: sv.getAttribute("class"),
      id: sv.querySelector(".cl")?.dataset.id ?? null,
      ph: sv.getAttribute("data-ph"),
      style: sv.getAttribute("style"),
      width: sv.getAttribute("width"),
      height: sv.getAttribute("height"),
      viewBox: sv.getAttribute("viewBox"),
    })),
    every: world.querySelectorAll(".cl").map((g) => [g.dataset.id, g.classes().filter((c) => c.startsWith("is-")).join(" ")]),
    worldSvgs: world.children.filter((c) => c instanceof Element && c.tag === "svg").map((c) => c.getAttribute("class")),
    rings: world.querySelectorAll(".cr").map((c) => c.tag + ":" + c.children.filter((i) => i instanceof Element).map((i) => `${i.tag}.${i.getAttribute("class")}`).join(",")),
    still: q(".gx-view").classList.contains("is-still"),
    label: q(".gx-view").getAttribute("aria-label"),
    keyPrevented,
    off: world.querySelectorAll(".is-off").map((el) => (el.classList.contains("cr") ? "cr" : "ph")),
    phases: world.querySelectorAll(".cl-ph").length,
    observed: motion.observed(world),
    states: Object.fromEntries(world.querySelectorAll(".gx-cmd .cl").map((g) => [g.dataset.id, g.dataset.state])),
    pressed: Object.fromEntries(world.querySelectorAll("[data-cmd-agent]").map((b) => [b.dataset.cmdAgent, b.getAttribute("aria-pressed")])),
    bandLabels: world.querySelectorAll("[data-cmd-agent]").map((b) => b.getAttribute("aria-label")),
    bandItems: world.querySelectorAll(".gx-band-item").map((it) => it.getAttribute("style")),
    selected: world.querySelectorAll(".is-sel").map((el) => el.dataset.id),
    panel: {
      open: panel.classList.contains("is-open"),
      agent: panel.dataset.cmdAgent ?? null,
      iframe: iframe ? { id: idOf(iframe), src: iframe.getAttribute("src"), sandbox: iframe.getAttribute("sandbox"), referrer: iframe.getAttribute("referrerpolicy") } : null,
      text: panel.querySelector(".pn-head")?.textContent ?? null,
      tab: panel.querySelector('[aria-selected="true"]')?.dataset?.pnTab ?? null,
      agentPicked: panel.querySelector(".sd-agent")?.getAttribute("src") ?? null,
    },
    legend: q(".legend").innerHTML.includes("指揮（親 → 子）"),
    transform: world.style.transform,
    size: [world.style.width, world.style.height],
    audit: audit && { links: audit.links, arcs: audit.arcs, boxOverlaps: audit.boxOverlaps, edgeOverlaps: audit.edgeOverlaps, layers: audit.layers, motion: audit.motion ?? null },
  };
}

let keyPrevented = null; // whether the last key step was prevented (iss-00655)
const target = (root, sel) => {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`nothing at ${sel}`);
  return el;
};

async function step(root, s, orca, ctx) {
  keyPrevented = null;
  if (s.summary !== undefined) {
    orca.set({ summary: s.summary, order: s.order });
    orca.news();
  } else if (s.news) orca.news();
  else if (s.render) graph.render(root, ctx);
  else if (s.revision) {
    ctx.data = { ...ctx.data, revision: s.revision };
    graph.render(root, ctx);
  } else if (s.styled) {
    styled = true;
    page.flushFrames();
  } else if (s.act) target(root, `[data-act="${s.act}"]`).dispatch("click");
  else if (s.click) target(root, s.click).dispatch("click");
  else if (s.tap) {
    const el = target(root, s.tap);
    const view = target(root, ".gx-view");
    const ev = { pointerId: 1, pointerType: "mouse", button: 0, clientX: 10, clientY: 10, target: el };
    for (const fn of view.listeners.pointerdown || []) fn(ev);
    for (const fn of view.listeners.pointerup || []) fn({ ...ev, type: "pointerup" });
  } else if (s.drag) {
    const view = target(root, ".gx-view");
    const ev = { pointerId: 2, pointerType: "mouse", button: 0, target: view };
    for (const fn of view.listeners.pointerdown || []) fn({ ...ev, clientX: 100, clientY: 100 });
    for (const x of [110, 130, 150]) for (const fn of view.listeners.pointermove || []) fn({ ...ev, clientX: x, clientY: 100 });
    for (const fn of view.listeners.pointerup || []) fn({ ...ev, type: "pointerup", clientX: 150, clientY: 100 });
  } else if (s.wheel) {
    const view = target(root, ".gx-view");
    const w = s.wheel;
    const ev = { deltaX: w.dx, deltaY: w.dy, shiftKey: !!w.shift, ctrlKey: !!w.ctrl, metaKey: false, clientX: w.x ?? 0, clientY: w.y ?? 0, preventDefault() {} };
    if (w.mode !== undefined) ev.deltaMode = w.mode;
    if (w.wy !== undefined) ev.wheelDeltaY = w.wy;
    for (const fn of view.listeners.wheel || []) fn(ev);
  } else if (s.viewHidden !== undefined) target(root, ".gx-view").hidden = s.viewHidden;
  else if (s.advance) motion.advance(s.advance);
  else if (s.hidden !== undefined) motion.setHidden(s.hidden);
  else if (s.tell) motion.tell(s.tell.sel, s.tell.hit);
  else if (s.key) {
    let el;
    if (s.on === "main") el = root;
    else if (s.on === "input") el = root.querySelector(".gx-view > input") ?? target(root, ".gx-view").appendChild(new Element("input"));
    else el = s.on ? target(root, s.on) : target(root, ".gx-view");
    const ev = { key: s.key, shiftKey: !!s.shift, target: el, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
    for (const fn of page.docListeners.keydown || []) fn(ev);
    keyPrevented = ev.defaultPrevented;
  }
  await settle();
}

const out = {};
const runs = {};
const after = {};
if (request.legend) {
  const D = await import(pathToFileURL(`${assets}/views/graph/draw.js`).href);
  const html = (open, opts) => {
    const el = new Element("div");
    if (opts === undefined) D.renderLegend(el, open);
    else D.renderLegend(el, open, opts);
    return el.innerHTML;
  };
  out.legend = { plain: html(true), off: html(true, { cmd: false }), on: html(true, { cmd: true }), closed: html(false), closedOn: html(false, { cmd: true }) };
}
for (const run of request.runs || []) {
  styled = !!run.styled;
  page.store.clear();
  motion.reset();
  motion.useObserver(!!run.io);
  const root = new Element("main");
  const orca = run.orca === false ? null : fakeOrca({});
  if (orca && run.orca?.summary) orca.set({ summary: run.orca.summary, order: run.orca.order });
  const ctx = {
    data: request.doc,
    route: { params: new URLSearchParams(""), path: "/r/github.com/o/r/" },
    orca,
    repository: "github.com/o/r",
    baseline: null,
    embed: false,
    navigate: () => {},
    href: (p) => p,
  };
  ctx.current = () => ctx;
  graph.render(root, ctx);
  await settle();
  const shots = [snap(root)];
  for (const s of run.steps || []) {
    await step(root, s, orca, ctx);
    shots.push(snap(root));
  }
  const view = root.querySelector(".gx-view");
  graph.dispose();
  after[run.name] = {
    observed: motion.observed(null),
    timers: motion.pending(),
    listeners: (page.docListeners.visibilitychange || []).length,
    still: view.classList.contains("is-still"),
  };
  runs[run.name] = shots;
}
process.stdout.write(JSON.stringify({ runs, after, legend: out.legend ?? null }));
