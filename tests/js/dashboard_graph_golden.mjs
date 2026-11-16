// The structure graph's HTML as views/graph.js draws it, for the copy kept before draw.js was taken out (iss-00614
// T-04, R-02): the same runs against the start commit's assets and the current ones must give the same output.
//
// usage: node dashboard_graph_golden.mjs <dashboard assets dir> <request.json>
// request: {docs: {name: structure document}, scopes: {doc name: {Scope id: scope API document}},
//           runs: [{name, doc: doc name or null, saved: {key: raw} | null, focus, orca: {Scope id: [mark widths]} | null,
//                   steps: [step]}]}
// step: {act, range?} (a toolbar button), {hl} (a state chip), {click: selector}, {tap: selector} (a pointer tap on what it selects),
//       {news: true} (orca-web's news)
// Prints {runs: {name: [snapshot after the first render, snapshot after each step]}}.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { Element, fakeOrca, install, json, settle } from "./fake_dom.mjs";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));
let scopes = {};
const page = install({
  fetch: async (url) => {
    const m = /\/scopes\/([^/?]+)/.exec(url);
    const doc = m ? scopes[decodeURIComponent(m[1])] : null;
    return doc ? json(doc) : json({ error: { message: "not found" } }, 404);
  },
});
const graph = (await import(pathToFileURL(`${assets}/views/graph.js`).href)).default;

function snap(root) {
  const q = (sel) => root.querySelector(sel);
  const world = q(".gx-world");
  const classes = {};
  for (const el of world.querySelectorAll(".gx-box, .gx-frame, .gx-clean")) {
    const on = el.classes().filter((c) => c.startsWith("is-") && !["is-frame", "is-compact"].includes(c));
    if (on.length) classes[el.dataset.id ?? el.dataset.clean] = on.join(" ");
  }
  const none = q(".gx-none");
  return {
    world: world.innerHTML,
    worldClass: world.className,
    size: [world.style.width, world.style.height],
    data: { mode: world.dataset.mode ?? null, range: world.dataset.range ?? null },
    classes,
    edges: q(".gx-edges")?.getAttribute("class") ?? null,
    next: q(".gx-next").innerHTML,
    tools: q(".gx-tools").innerHTML,
    crumbs: { hidden: q(".gx-crumbs").hidden, html: q(".gx-crumbs").innerHTML },
    legend: q(".legend").innerHTML,
    none: { hidden: none.hidden, text: none.textContent },
    bar: !q(".gx-bar").hidden,
    view: !q(".gx-view").hidden,
    empty: { hidden: q(".gx-empty").hidden, text: q(".gx-empty").textContent },
    saved: Object.fromEntries(page.store),
  };
}

const target = (root, sel) => {
  const el = root.querySelector(sel);
  if (!el) throw new Error(`nothing at ${sel}`);
  return el;
};

async function step(root, s, orca) {
  if (s.act) {
    const sel = s.range ? `[data-act="range"][data-range="${s.range}"]` : `[data-act="${s.act}"]`;
    target(root, sel).dispatch("click");
  } else if (s.click) target(root, s.click).dispatch("click");
  else if (s.hl) target(root, `[data-hl="${s.hl}"]`).dispatch("click");
  else if (s.tap) {
    const el = target(root, s.tap);
    const view = target(root, ".gx-view");
    const ev = { pointerId: 1, pointerType: "mouse", button: 0, clientX: 10, clientY: 10, target: el };
    for (const fn of view.listeners.pointerdown || []) fn(ev);
    for (const fn of view.listeners.pointerup || []) fn({ ...ev, type: "pointerup" });
  } else if (s.news) orca.news();
  await settle();
}

const out = {};
for (const run of request.runs) {
  page.store.clear();
  for (const [k, v] of Object.entries(run.saved || {})) page.store.set(k, v);
  const doc = run.doc == null ? null : request.docs[run.doc];
  scopes = request.scopes?.[run.doc] || {};
  const root = new Element("main");
  const orca = run.orca ? fakeOrca({ [doc?.repository]: run.orca }) : null;
  const ctx = {
    data: doc,
    route: { params: new URLSearchParams(run.focus ? `focus=${run.focus}` : ""), path: "/r/github.com/o/r/" },
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
    await step(root, s, orca);
    shots.push(snap(root));
  }
  graph.dispose();
  out[run.name] = shots;
}
process.stdout.write(JSON.stringify({ runs: out }));
