// The structure graph's toolbar, marks, legend and "next" notice, drawn by views/graph.js in node (iss-00603 T-08, T-11).
//
// usage: node dashboard_graph_toolbar.mjs <dashboard assets dir> <request.json>
// request: {runs: [{name, doc, saved: {key: raw string} | null, clicks: [{act, range?, deps?}]}]}
// Prints {runs: {name: [snapshot after the first render, snapshot after each click]}}.
//
// graph.js draws by writing HTML strings, so a minimal stand-in for the DOM is enough: each element keeps the HTML
// it was given, the screen's shell hands out one element per selector, and a click reaches the screen's own listener.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const [assets, requestPath] = process.argv.slice(2);
const request = JSON.parse(readFileSync(requestPath, "utf8"));

class El {
  constructor(name = "") {
    this.name = name;
    this.html = "";
    this.textContent = "";
    this.hidden = false;
    this.dataset = {};
    this.style = {};
    this.attrs = {};
    this.listeners = {};
    this.parts = new Map();
    const classes = new Set();
    this.classList = {
      add: (...c) => c.forEach((x) => classes.add(x)),
      remove: (...c) => c.forEach((x) => classes.delete(x)),
      toggle: (c, on = !classes.has(c)) => (on ? classes.add(c) : classes.delete(c), on),
      contains: (c) => classes.has(c),
    };
    this.clientWidth = 1200;
    this.clientHeight = 800;
    this.offsetWidth = 0;
    this.offsetHeight = 0;
  }
  get innerHTML() {
    return this.html;
  }
  set innerHTML(value) {
    this.html = value;
    this.parts = new Map();
  }
  querySelector(sel) {
    // only the shell (mount) asks for its parts; the parts' own drawings are read as strings
    if (this.name !== "root") return null;
    if (!this.parts.has(sel)) this.parts.set(sel, new El(sel));
    return this.parts.get(sel);
  }
  querySelectorAll() {
    return [];
  }
  addEventListener(type, fn) {
    (this.listeners[type] ||= []).push(fn);
  }
  removeEventListener() {}
  setAttribute(k, v) {
    this.attrs[k] = String(v);
  }
  getAttribute(k) {
    return this.attrs[k] ?? null;
  }
  contains() {
    return false;
  }
  replaceChildren() {
    this.html = "";
  }
  getBoundingClientRect() {
    return { left: 0, top: 0, right: 1200, bottom: 800, width: 1200, height: 800 };
  }
}

const store = new Map();
globalThis.localStorage = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: (k) => store.delete(k),
  clear: () => store.clear(),
};
const noop = () => {};
globalThis.window = { addEventListener: noop, removeEventListener: noop };
globalThis.document = { addEventListener: noop, removeEventListener: noop, documentElement: { dataset: {}, clientWidth: 1440 } };
globalThis.innerWidth = 1440;
globalThis.innerHeight = 900;
globalThis.location = { origin: "http://127.0.0.1:47800" };
globalThis.matchMedia = () => ({ matches: false, addEventListener: noop, removeEventListener: noop });
globalThis.getComputedStyle = () => ({ position: "" }); // the screen's CSS never loads: no first view to place
globalThis.requestAnimationFrame = noop;
globalThis.CSS = { escape: (s) => s };

const graph = (await import(pathToFileURL(`${assets}/views/graph.js`).href)).default;

function snap(root) {
  const part = (sel) => root.parts.get(sel);
  const none = part(".gx-none");
  return {
    tools: part(".gx-tools").innerHTML,
    legend: part(".legend").innerHTML,
    world: part(".gx-world").innerHTML,
    range: part(".gx-world").dataset.range ?? null,
    mode: part(".gx-world").dataset.mode ?? null,
    none: none ? { hidden: none.hidden, text: none.textContent } : null,
    bar: !part(".gx-bar").hidden,
    view: !part(".gx-view").hidden,
    saved: Object.fromEntries(store),
  };
}

function click(root, { act, ...data }) {
  const target = {
    dataset: { act, ...data },
    closest: (sel) => (sel === "[data-act]" ? target : null),
  };
  for (const fn of root.parts.get(".gx").listeners.click || []) fn({ target });
}

const out = {};
for (const run of request.runs) {
  store.clear();
  for (const [k, v] of Object.entries(run.saved || {})) store.set(k, v);
  const root = new El("root");
  const ctx = {
    data: run.doc,
    route: { params: new URLSearchParams(run.focus ? `focus=${run.focus}` : ""), path: "/r/x" },
    orca: null,
    repository: "x",
    baseline: null,
    navigate: noop,
  };
  graph.render(root, ctx);
  const shots = [snap(root)];
  for (const c of run.clicks || []) {
    click(root, c);
    shots.push(snap(root));
  }
  graph.dispose();
  out[run.name] = shots;
}
process.stdout.write(JSON.stringify({ runs: out }));
