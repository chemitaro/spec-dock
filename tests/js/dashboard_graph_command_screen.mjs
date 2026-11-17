// The structure graph's command lines and band on the page (iss-00616 T-05), with the fake DOM and the fake orca.
//   node dashboard_graph_command_screen.mjs <dashboard assets dir> <request.json>
// request: {doc: structure document, runs: [{name, orca: false | {summary, order}, steps: [step]}], legend: bool}
// step: {summary, order?} (orca-web's news with this summary), {news: true} (news with the same summary),
//       {render: true} (the shell renders again), {revision: "r2"} (a new structure revision rendered),
//       {styled: true} (the screen's CSS applies: the first view is placed), {act: "fit"} (a toolbar button),
//       {tap: selector} (a pointer tap), {key: "Enter" | " " | "Escape", on: selector?}, {click: selector}
// Prints {runs: {name: [snapshot after the first render, snapshot after each step]}, legend: the legend's HTML by
// renderLegend's options (legend: true)}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { Element, fakeOrca, hooks, install, json, settle } from "./fake_dom.mjs";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
const page = install({ fetch: async () => json({ error: { message: "not found" } }, 404) });
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
    ripples: classes(".gx-cmd-top .cr", "agent"),
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
    audit: audit && { links: audit.links, arcs: audit.arcs, boxOverlaps: audit.boxOverlaps, edgeOverlaps: audit.edgeOverlaps, layers: audit.layers },
  };
}

const target = (root, sel) => {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`nothing at ${sel}`);
  return el;
};

async function step(root, s, orca, ctx) {
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
  } else if (s.key) {
    const el = s.on ? target(root, s.on) : target(root, ".gx-view");
    const ev = { key: s.key, target: el, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
    for (const fn of page.docListeners.keydown || []) fn(ev);
  }
  await settle();
}

const out = {};
const runs = {};
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
  styled = false;
  page.store.clear();
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
  graph.dispose();
  runs[run.name] = shots;
}
process.stdout.write(JSON.stringify({ runs, legend: out.legend ?? null }));
