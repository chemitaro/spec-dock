// The cross-repository structure screen (views/allgraph.js) in node with the stand-in DOM (iss-00614 T-05 to T-07).
//
// usage: node dashboard_allgraph_screen.mjs <dashboard assets dir> <request.json>
// request: {runs: [run]}
// run: {name, repos: [list API repository], docs: {key: structure document | {status, message}},
//       scopes: {key: {Scope id: scope document}}, revisions: {key: revision}, saved: {key: raw} | null,
//       orca: {key: {Scope id: [mark widths]}} | null, embed, width, steps: [step]}
// step: {act, range?} | {hl} | {tap: selector} | {dbl: selector} | {click: selector} | {key: "Escape"} |
//       {tick: n} (the 5-second refresh n times) | {set: {revisions?, docs?}} (the server's answers change) |
//       {news: true} (orca-web's news) | {orca: {key: {id: [w]}}} (the reader's worktrees change, then news) |
//       {remount: true} (leave the screen and open it again) | {release: true} (the held structure answers arrive)
// run.styled: the screen's CSS is in effect (.gx is position: absolute) and the animation frames run, as in a browser;
// run.hold: the structure answers wait for a {release} step, so they arrive after the first draw (iss-00629 T-03).
// Prints {runs: {name: [snapshot after the first render, after each step]}}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { Element, fakeOrca, hooks, install, json, settle } from "./fake_dom.mjs";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
let run = null;
const calls = [];
let held = [];
const page = install({
  fetch: async (url, init = {}) => {
    calls.push(`${init.method || "GET"} ${url}`);
    const m = /^\/api\/v1\/r\/([^/]+\/[^/]+\/[^/]+)\/(structure|revision|scopes\/([^/?]+))/.exec(url);
    if (!m) return json({ error: { message: "not found" } }, 404);
    const [, key, op, id] = m;
    if (op === "revision") return json({ revision: run.revisions?.[key] ?? run.docs[key]?.revision ?? null });
    if (op === "structure") {
      if (run.hold) await new Promise((resolve) => held.push(resolve));
      const doc = run.docs[key];
      if (!doc || doc.status >= 400) return json({ error: { message: doc?.message ?? "not found" } }, doc?.status ?? 404);
      return json(doc);
    }
    const doc = run.scopes?.[key]?.[decodeURIComponent(id)];
    return doc ? json(doc) : json({ error: { message: "not found" } }, 404);
  },
});
const intervals = [];
globalThis.setInterval = (fn) => (intervals.push(fn), intervals.length);
globalThis.clearInterval = (id) => {
  if (id) intervals[id - 1] = null;
};
const navigated = [];
const plainStyle = globalThis.getComputedStyle;
const styledStyle = (el) => ({ ...plainStyle(el), position: el?.classList?.contains("gx") ? "absolute" : "" });
const frames = () => run.styled && page.flushFrames();
const allgraph = (await import(pathToFileURL(`${assets}/views/allgraph.js`).href)).default;
const { routeLayout } = await import(pathToFileURL(`${assets}/views/graph/layout.js`).href);

function snap(root, orca) {
  const q = (sel) => root.querySelector(sel);
  const world = q(".gx-world");
  const repos = [];
  for (const section of world.elements) {
    if (!section.classList.contains("ax-repo")) continue;
    const key = section.dataset.repo;
    const body = section.elements.find((el) => el.classList.contains("ax-body")) ?? null;
    const head = section.elements.find((el) => el.classList.contains("ax-head")) ?? null;
    const warn = section.elements.find((el) => el.classList.contains("ax-warn")) ?? null;
    const classes = {};
    const ids = [];
    for (const el of body ? body.querySelectorAll(".gx-box, .gx-frame, .gx-clean") : []) {
      const id = el.dataset.id ?? `clean:${el.dataset.clean}`;
      ids.push(id);
      const on = el.classes().filter((c) => c.startsWith("is-") && !["is-frame", "is-compact"].includes(c));
      if (on.length) classes[id] = on.join(" ");
    }
    repos.push({
      key,
      depth: section.dataset.depth,
      kind: section.dataset.kind ?? null,
      style: section.getAttribute("style"),
      head: head ? head.textContent : null,
      headHtml: head ? head.innerHTML : null,
      warn: warn ? warn.elements.map((li) => ({ level: li.dataset.level, text: li.textContent, title: li.getAttribute("title") })) : [],
      body: body ? { style: body.getAttribute("style"), text: body.querySelector(".ax-line")?.textContent ?? null } : null,
      ids,
      classes,
      marks: body ? body.querySelectorAll(".orca-mark").length : 0,
      edges: body?.querySelector(".gx-edges")?.getAttribute("class") ?? null,
      edgeClasses: body ? [...new Set(body.querySelectorAll(".gx-edges .e").map((e) => e.className))].sort() : [],
    });
  }
  const panel = q(".panel");
  const foot = panel?.querySelector(".pn-foot");
  const stats = globalThis.window.specdockAllGraphStats ?? null;
  return {
    repos,
    worldClass: world.className,
    transform: world.style.transform,
    size: [world.style.width, world.style.height],
    next: q(".gx-next").innerHTML,
    sum: q(".ax-sum")
      ? { hidden: q(".ax-sum").hidden, inLeft: !!q(".gx-left .ax-sum"), rows: q(".ax-sum").elements.map((li) => ({ kind: li.dataset.kind, level: li.dataset.level, text: li.textContent, title: li.getAttribute("title") })) }
      : null,
    tools: q(".gx-tools").innerHTML,
    legend: q(".legend").innerHTML,
    none: { hidden: q(".gx-none").hidden, text: q(".gx-none").textContent },
    empty: { hidden: q(".gx-empty").hidden, text: q(".gx-empty").textContent },
    bar: !q(".gx-bar").hidden,
    view: !q(".gx-view").hidden,
    screen: q(".gx")?.dataset.screen ?? null,
    panel: {
      open: panel?.classList.contains("is-open") ?? false,
      st: panel?.dataset.st ?? null,
      foot: foot ? [...foot.querySelectorAll("a, button")].map((a) => ({ label: a.textContent, href: a.getAttribute("href"), act: a.dataset.act ?? null, focus: a.dataset.focus ?? null })) : [],
      marks: panel ? panel.querySelectorAll(".pn-top .orca-mark").length : 0,
      cover: panel?.querySelector(".pn-cover")?.textContent ?? null,
    },
    stats: stats ? JSON.parse(JSON.stringify(stats)) : null,
    saved: Object.fromEntries(page.store),
    calls: calls.splice(0),
    navigated: navigated.splice(0),
    audit: typeof globalThis.window.specdockEdgeAudit === "function" ? summarize(globalThis.window.specdockEdgeAudit()) : null,
  };
}

const summarize = (a) => (a ? { repos: Object.keys(a.repos || {}).sort(), total: a.total ?? null } : null);

const target = (root, sel) => {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`nothing at ${sel}`);
  return el;
};

function pointer(root, el, type = "tap") {
  const view = target(root, ".gx-view");
  const ev = { pointerId: 1, pointerType: "mouse", button: 0, clientX: 10, clientY: 10, target: el };
  if (type === "dbl") {
    for (const fn of view.listeners.dblclick || []) fn(ev);
    return;
  }
  for (const fn of view.listeners.pointerdown || []) fn(ev);
  for (const fn of view.listeners.pointerup || []) fn({ ...ev, type: "pointerup" });
}

async function step(root, s, ctx, orca) {
  if (s.act) target(root, s.range ? `[data-act="range"][data-range="${s.range}"]` : `[data-act="${s.act}"]`).dispatch("click");
  else if (s.hl) target(root, `[data-hl="${s.hl}"]`).dispatch("click");
  else if (s.click) target(root, s.click).dispatch("click");
  else if (s.tap) pointer(root, target(root, s.tap));
  else if (s.dbl) pointer(root, target(root, s.dbl), "dbl");
  else if (s.key) for (const fn of page.docListeners.keydown || []) fn({ key: s.key, target: { closest: () => null }, preventDefault() {} });
  else if (s.tick) {
    for (let i = 0; i < s.tick; i++) {
      for (const fn of intervals) fn?.();
      await settle();
    }
  } else if (s.set) {
    Object.assign((run.revisions ||= {}), s.set.revisions || {});
    Object.assign(run.docs, s.set.docs || {});
  } else if (s.news) orca.news();
  else if (s.orca) {
    orca.set(s.orca);
    orca.news();
  } else if (s.remount) {
    allgraph.dispose();
    root.replaceChildren();
    allgraph.render(root, ctx);
  } else if (s.release) {
    for (const resolve of held.splice(0)) resolve();
  }
  frames();
  await settle();
  frames();
}

const out = {};
for (const r of request.runs) {
  run = structuredClone(r);
  page.store.clear();
  intervals.length = 0;
  calls.length = 0;
  held = [];
  globalThis.getComputedStyle = run.styled ? styledStyle : plainStyle;
  for (const [k, v] of Object.entries(run.saved || {})) page.store.set(k, v);
  globalThis.innerWidth = run.width ?? 1440;
  // run.view {width, height, bar, sum}: the graph area's size and the bottom of the bar above it (px), for the fit;
  // sum: the bottom of the notices' summary under the chips (iss-00632, default: the bar's)
  // and the screen's root is as wide as the window (isPhone)
  hooks.sizes = run.view
    ? (el) => {
        if (el.classList?.contains("gx-view")) return { width: run.view.width, height: run.view.height };
        if (el.getAttribute?.("data-view") === "allgraph") return { width: run.width ?? 1440, height: run.view.height };
        return null;
      }
    : null;
  hooks.rect = run.view
    ? (el) => {
        if (el.classList?.contains("gx-view")) return { left: 0, top: 0, right: run.view.width, bottom: run.view.height, width: run.view.width, height: run.view.height };
        if (el.classList?.contains("gx-next") || el.classList?.contains("gx-tools")) return { left: 0, top: 0, right: 100, bottom: run.view.bar, width: 100, height: run.view.bar };
        if (el.classList?.contains("ax-sum")) return { left: 0, top: 0, right: 100, bottom: run.view.sum ?? run.view.bar, width: 100, height: run.view.sum ?? run.view.bar };
        return null;
      }
    : null;
  const root = new Element("main");
  root.setAttribute("data-view", "allgraph");
  const orca = run.orca ? fakeOrca(run.orca) : null;
  const ctx = {
    repository: null,
    route: { view: "allgraph", params: new URLSearchParams(run.embed ? "embed=1" : ""), path: "/graph", embed: !!run.embed },
    data: null,
    repositories: run.repos,
    embed: !!run.embed,
    orca,
    baseline: null,
    navigate: (p) => navigated.push(p),
    href: (p) => (run.embed ? `${p}${p.includes("?") ? "&" : "?"}embed=1` : p),
  };
  ctx.current = () => ctx;
  allgraph.render(root, ctx);
  frames();
  await settle();
  frames();
  const shots = [snap(root, orca)];
  for (const s of run.steps || []) {
    await step(root, s, ctx, orca);
    shots.push(snap(root, orca));
  }
  // the boxes and frames each repository's graph would show by itself (R-05's sixth criterion)
  const alone = {};
  for (const [key, doc] of Object.entries(run.docs)) {
    if (!Array.isArray(doc?.scopes) || !doc.scopes.length) continue;
    alone[key] = {};
    for (const range of ["all", "now", "next"]) {
      const L = routeLayout(doc.scopes, doc.cleanup, { mode: "nest", range, focus: null, width: 1000 }).layout;
      alone[key][range] = [...L.nodes.map((n) => n.id), ...L.groups.map((g) => `clean:${g.key}`)].sort();
    }
  }
  allgraph.dispose();
  out[r.name] = { shots, alone, intervals: intervals.filter(Boolean).length, audit: globalThis.window.specdockEdgeAudit ? "left" : "gone" };
}
process.stdout.write(JSON.stringify({ runs: out }));
