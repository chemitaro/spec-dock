// The cross-repository structure's command lines and bands on the page (iss-00617 T-05), with the fake DOM and the
// fake orca in its summary mode.
//   node dashboard_allgraph_command_screen.mjs <dashboard assets dir> <request.json>
// request: {runs: [{name, repos: [list API repository], docs: {key: structure document}, range?,
//           orca: false | {summary, order}, steps: [step]}]}
// step: {summary, order?} (orca-web's news with this summary), {news: true} (news with the same summary),
//       {flip: {summary?, worktree, paths: [a, b]}} (the summary given, then from now on each read of it moves that
//       worktree to the other path: the same summary object whose places differ each time, F-05), {tap: selector}, {click: selector},
//       {key: "Escape" | "Enter" | " ", on: selector?}, {wheel: {dx, dy}} (the reader pans: A.moved), {range: name},
//       {advance: ms} (the motion's clock, iss-00646), {hidden: bool}, {tell: {sel, hit}} (IntersectionObserver's answer)
// run.io: the page has an IntersectionObserver (the fake one of fake_motion.mjs); without it, none (F-01).
// Prints {runs: {name: [snapshot after the first render, after each step]}}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { Element, fakeOrca, hooks, install, json, settle } from "./fake_dom.mjs";
import { installMotion } from "./fake_motion.mjs";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
let run = null;
const page = install({
  fetch: async (url) => {
    const m = /^\/api\/v1\/r\/([^/]+\/[^/]+\/[^/]+)\/(structure|revision|scopes\/([^/?]+))/.exec(url);
    if (!m) return json({ error: { message: "not found" } }, 404);
    const [, key, op] = m;
    const doc = run.docs[key];
    if (op === "revision") return json({ revision: doc?.revision ?? null });
    if (op === "structure") return doc ? json(doc) : json({ error: { message: "not found" } }, 404);
    return json({ error: { message: "not found" } }, 404);
  },
});
const motion = installMotion(page);
// the bar above the graph is 40px tall; the graph area is the fake's 1200 × 800
hooks.rect = (el) =>
  ["gx-next", "gx-tools", "ax-sum"].some((c) => el.classList?.contains(c)) ? { left: 0, top: 0, right: 100, bottom: 40, width: 100, height: 40 } : null;
globalThis.setInterval = () => 0;
globalThis.clearInterval = () => {};
const allgraph = (await import(pathToFileURL(`${assets}/views/allgraph.js`).href)).default;

const ids = new WeakMap();
let next = 0;
const idOf = (el) => {
  if (!el) return null;
  if (!ids.has(el)) ids.set(el, ++next);
  return ids.get(el);
};
const px = (style, name) => {
  const m = new RegExp(`(?:^|;)${name}:(-?[\\d.]+)px`).exec(style || "");
  return m ? Number(m[1]) : null;
};

function snap(root) {
  const q = (sel) => root.querySelector(sel);
  const world = q(".gx-world");
  const panel = q(".panel");
  const iframe = panel.querySelector("iframe");
  const kids = world.children.filter((c) => c instanceof Element);
  const sections = kids.filter((c) => c.classList.contains("ax-repo")).map((s) => {
    const body = s.elements.find((el) => el.classList.contains("ax-body")) ?? null;
    const st = s.getAttribute("style");
    const bs = body?.getAttribute("style") ?? null;
    return {
      key: s.dataset.repo,
      kind: s.dataset.kind,
      id: idOf(s),
      x: px(st, "left"), y: px(st, "top"), w: px(st, "width"), h: px(st, "height"),
      body: body ? { x: px(st, "left") + px(bs, "left"), y: px(st, "top") + px(bs, "top") } : null,
      boxes: body ? Object.fromEntries(body.querySelectorAll(".gx-box").map((b) => {
        const bst = b.getAttribute("style");
        return [b.dataset.id, { x1: px(bst, "left"), y1: px(bst, "top"), x2: px(bst, "left") + px(bst, "width"), y2: px(bst, "top") + px(bst, "height") }];
      })) : {},
    };
  });
  const classes = (sel, key) => Object.fromEntries(world.querySelectorAll(sel).map((el) => [el.dataset[key], el.classes().filter((c) => c.startsWith("is-")).join(" ")]));
  const audit = globalThis.window.specdockCmdAudit?.() ?? null;
  const stats = globalThis.window.specdockAllGraphStats ?? null;
  const m = /translate\((-?[\d.]+)px, (-?[\d.]+)px\) scale\(([\d.]+)\)/.exec(world.style.transform || "");
  return {
    layers: kids.filter((c) => !c.classList.contains("ax-repo")).map((c) => c.getAttribute("class")),
    html: world.innerHTML,
    sections,
    cmd: idOf(q(".gx-cmd")),
    top: idOf(q(".gx-cmd-top")),
    band: idOf(q(".gx-band")),
    layerTags: world.querySelectorAll(".gx-cmd, .gx-cmd-top, .gx-band-cr").map((el) => el.tag),
    svgSizes: world.querySelectorAll(".gx-cmd svg, .gx-cmd-top svg").map((sv) => [sv.getAttribute("width"), sv.getAttribute("height")]),
    phases: world.querySelectorAll(".cl-ph").length,
    still: q(".gx-view").classList.contains("is-still"),
    off: world.querySelectorAll(".is-off").length,
    observed: motion.observed(world),
    size: [world.style.width, world.style.height],
    t: m ? { tx: Number(m[1]), ty: Number(m[2]), s: Number(m[3]) } : null,
    lines: classes(".gx-cmd .cl", "id"),
    paths: Object.fromEntries(world.querySelectorAll(".gx-cmd .cl").map((g) => [g.dataset.id, g.querySelector(".cl-glow, .cl-line").getAttribute("d")])),
    dots: Object.fromEntries(world.querySelectorAll(".gx-cmd-top .cl").filter((g) => g.querySelector(".cl-dot")).map((g) => {
      const c = g.querySelector(".cl-dot");
      return [g.dataset.id, [Number(c.getAttribute("cx")), Number(c.getAttribute("cy"))]];
    })),
    leads: world.querySelectorAll(".gx-band-lead").map((el) => ({ text: el.textContent, style: el.getAttribute("style") })),
    bandItems: world.querySelectorAll(".gx-band-item").map((it) => {
      const st = it.getAttribute("style");
      return { label: it.querySelector(".gx-band-lab").textContent, x: px(st, "left"), y: px(st, "top"), w: px(st, "width"), h: px(st, "height") };
    }),
    pressed: Object.fromEntries(world.querySelectorAll("[data-cmd-agent]").map((b) => [b.dataset.cmdAgent, b.getAttribute("aria-pressed")])),
    selected: world.querySelectorAll(".is-sel").map((el) => el.dataset.id),
    panel: {
      open: panel.classList.contains("is-open"),
      agent: panel.dataset.cmdAgent ?? null,
      iframe: iframe ? { id: idOf(iframe), src: iframe.getAttribute("src") } : null,
      tab: panel.querySelector('[aria-selected="true"]')?.dataset?.pnTab ?? null,
      bodyTab: panel.querySelector(".pn-body")?.getAttribute("data-tab") ?? null,
    },
    legend: q(".legend").innerHTML.includes("指揮（親 → 子）"),
    stats: stats ? { layouts: stats.layouts, composes: stats.composes ?? null } : null,
    audit: audit && Object.fromEntries(Object.entries(audit).map(([k, v]) => [k, typeof v === "number" ? v : Array.isArray(v) ? v : typeof v])),
    motion: audit?.motion ?? null,
  };
}

const target = (root, sel) => {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`nothing at ${sel}`);
  return el;
};

async function step(root, s, orca) {
  if (s.summary !== undefined) {
    orca.summary = orca.plainSummary;
    orca.set({ summary: s.summary, order: s.order });
    orca.news();
  } else if (s.news) orca.news();
  else if (s.flip) {
    orca.summary = orca.plainSummary;
    if (s.flip.summary) orca.set({ summary: s.flip.summary });
    const doc = orca.plainSummary();
    const wt = doc.worktrees.find((w) => w.id === s.flip.worktree);
    let i = 0;
    orca.summary = () => {
      wt.path = s.flip.paths[i++ % 2];
      return doc;
    };
    orca.news();
  } else if (s.tap) {
    const el = target(root, s.tap);
    const view = target(root, ".gx-view");
    const ev = { pointerId: 1, pointerType: "mouse", button: 0, clientX: 10, clientY: 10, target: el };
    for (const fn of view.listeners.pointerdown || []) fn(ev);
    for (const fn of view.listeners.pointerup || []) fn({ ...ev, type: "pointerup" });
  } else if (s.click) target(root, s.click).dispatch("click");
  else if (s.key) {
    const el = s.on ? target(root, s.on) : target(root, ".gx-view");
    const ev = { key: s.key, target: el, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
    for (const fn of page.docListeners.keydown || []) fn(ev);
  } else if (s.wheel) {
    const view = target(root, ".gx-view");
    for (const fn of view.listeners.wheel || []) fn({ deltaX: s.wheel.dx, deltaY: s.wheel.dy, ctrlKey: false, metaKey: false, clientX: 0, clientY: 0, preventDefault() {} });
  } else if (s.range) target(root, `[data-act="range"][data-range="${s.range}"]`).dispatch("click");
  else if (s.advance) motion.advance(s.advance);
  else if (s.hidden !== undefined) motion.setHidden(s.hidden);
  else if (s.tell) motion.tell(s.tell.sel, s.tell.hit);
  await settle();
  page.flushFrames();
  await settle();
}

const out = {};
for (const r of request.runs) {
  run = structuredClone(r);
  page.store.clear();
  motion.reset();
  motion.useObserver(!!run.io);
  if (run.range) page.store.set("specdock.allgraph.v1", JSON.stringify({ range: run.range }));
  const root = new Element("main");
  root.setAttribute("data-view", "allgraph");
  let orca = null;
  if (run.orca !== false) {
    orca = fakeOrca({});
    orca.plainSummary = orca.summary;
    if (run.orca?.summary) orca.set({ summary: run.orca.summary, order: run.orca.order });
  }
  const ctx = {
    repository: null,
    route: { view: "allgraph", params: new URLSearchParams(""), path: "/graph", embed: false },
    data: null,
    repositories: run.repos,
    embed: false,
    orca,
    baseline: null,
    navigate: () => {},
    href: (p) => p,
  };
  ctx.current = () => ctx;
  allgraph.render(root, ctx);
  await settle();
  page.flushFrames();
  await settle();
  const shots = [snap(root)];
  for (const s of run.steps || []) {
    await step(root, s, orca);
    shots.push(snap(root));
  }
  const view = root.querySelector(".gx-view");
  allgraph.dispose();
  const left = { observed: motion.observed(null).live, timers: motion.pending(), listeners: (page.docListeners.visibilitychange || []).length, still: view.classList.contains("is-still") };
  out[r.name] = { shots, audit: globalThis.window.specdockCmdAudit ? "left" : "gone", left };
}
process.stdout.write(JSON.stringify({ runs: out }));
