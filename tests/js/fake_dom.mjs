// A small stand-in for the browser's DOM for the dashboard's screens in node (iss-00614 T-04 to T-07).
//
// The screens draw by writing HTML strings; this parses them into elements that keep their attributes in order, so
// innerHTML reads back the same string until a class or an attribute changes. Selectors: tags, #id, .class,
// [attr], [attr="v"], :is(…), :not(…), descendant and child combinators, and comma lists. Sizes come from a hook
// (`sizes`), else 1200×800; an element with data-w is that wide (the agents' marks of the fake orca module).

const VOID = new Set(["br", "img", "input", "hr", "meta", "link", "wbr"]);
const TOKEN = /<!--[\s\S]*?-->|<\/([a-zA-Z][a-zA-Z0-9-]*)\s*>|<([a-zA-Z][a-zA-Z0-9-]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*(\/?)>|([^<]+|<)/g;
const ATTR = /([^\s=>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;

const decode = (s) =>
  s.replace(/&(amp|lt|gt|quot|#39|#x27);/g, (_, e) => ({ amp: "&", lt: "<", gt: ">", quot: '"', "#39": "'", "#x27": "'" })[e]);
const encode = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const camel = (s) => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
const kebab = (s) => s.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`);

export const hooks = { sizes: null, rect: null };

export class Text {
  constructor(raw) {
    this.raw = raw;
    this.parent = null;
  }
  get textContent() {
    return decode(this.raw);
  }
  serialize() {
    return this.raw;
  }
}

export class Element {
  constructor(tag, attrs = []) {
    this.tagName = tag.toUpperCase();
    this.tag = tag.toLowerCase();
    this.attrs = attrs; // [[name, raw value or null]]
    this.children = [];
    this.parent = null;
    this.listeners = {};
    this.scrollTop = 0;
    this.writes = 0;
    const self = this;
    this.style = new Proxy(
      { props: {} },
      {
        get(t, k) {
          if (k === "setProperty") return (n, v) => (t.props[n] = String(v));
          if (k === "removeProperty") return (n) => delete t.props[n];
          if (k === "getPropertyValue") return (n) => t.props[n] ?? "";
          return t.props[k] ?? "";
        },
        set(t, k, v) {
          t.props[k] = String(v);
          return true;
        },
      },
    );
    this.dataset = new Proxy(
      {},
      {
        get: (_, k) => (typeof k === "string" ? self.getAttribute(`data-${kebab(k)}`) ?? undefined : undefined),
        set: (_, k, v) => (self.setAttribute(`data-${kebab(k)}`, v), true),
        deleteProperty: (_, k) => (self.removeAttribute(`data-${kebab(k)}`), true),
        has: (_, k) => self.hasAttribute(`data-${kebab(k)}`),
        ownKeys: () => self.attrs.filter(([n]) => n.startsWith("data-")).map(([n]) => camel(n.slice(5))),
        getOwnPropertyDescriptor: (_, k) =>
          self.hasAttribute(`data-${kebab(k)}`) ? { enumerable: true, configurable: true, value: self.getAttribute(`data-${kebab(k)}`) } : undefined,
      },
    );
    this.classList = {
      contains: (c) => self.classes().includes(c),
      add: (...cs) => cs.forEach((c) => self.classList.contains(c) || self.setClasses([...self.classes(), c])),
      remove: (...cs) => cs.forEach((c) => self.classList.contains(c) && self.setClasses(self.classes().filter((x) => x !== c))),
      toggle: (c, on) => {
        const want = on === undefined ? !self.classList.contains(c) : !!on;
        if (want) self.classList.add(c);
        else self.classList.remove(c);
        return want;
      },
    };
  }
  classes() {
    return (this.getAttribute("class") || "").split(/\s+/).filter(Boolean);
  }
  setClasses(list) {
    this.setAttribute("class", list.join(" "));
  }
  getAttribute(name) {
    const a = this.attrs.find(([n]) => n === name);
    return a ? (a[1] == null ? "" : decode(a[1])) : null;
  }
  hasAttribute(name) {
    return this.attrs.some(([n]) => n === name);
  }
  setAttribute(name, value) {
    const raw = String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;");
    const a = this.attrs.find(([n]) => n === name);
    if (a) {
      if (decode(a[1] ?? "") !== String(value)) a[1] = raw;
    } else this.attrs.push([name, raw]);
  }
  removeAttribute(name) {
    this.attrs = this.attrs.filter(([n]) => n !== name);
  }
  get id() {
    return this.getAttribute("id") || "";
  }
  get className() {
    return this.getAttribute("class") || "";
  }
  get hidden() {
    return this.hasAttribute("hidden");
  }
  set hidden(v) {
    if (v) {
      if (!this.hasAttribute("hidden")) this.attrs.push(["hidden", null]);
    } else this.removeAttribute("hidden");
  }
  get href() {
    return this.getAttribute("href");
  }
  get innerHTML() {
    return this.children.map((c) => c.serialize()).join("");
  }
  set innerHTML(html) {
    this.writes++;
    for (const c of this.children) c.parent = null;
    this.children = parse(String(html));
    for (const c of this.children) c.parent = this;
  }
  get outerHTML() {
    return this.serialize();
  }
  get textContent() {
    return this.children.map((c) => c.textContent).join("");
  }
  set textContent(v) {
    this.innerHTML = encode(v ?? "");
  }
  serialize() {
    const attrs = this.attrs.map(([n, v]) => (v == null ? ` ${n}` : ` ${n}="${v}"`)).join("");
    if (VOID.has(this.tag)) return `<${this.tag}${attrs}>`;
    if (this.selfClosed && !this.children.length) return `<${this.tag}${attrs}/>`;
    return `<${this.tag}${attrs}>${this.innerHTML}</${this.tag}>`;
  }
  get firstElementChild() {
    return this.children.find((c) => c instanceof Element) ?? null;
  }
  get elements() {
    return this.children.filter((c) => c instanceof Element);
  }
  *descendants() {
    for (const c of this.children) {
      if (!(c instanceof Element)) continue;
      yield c;
      yield* c.descendants();
    }
  }
  querySelectorAll(sel) {
    const list = compile(sel);
    return [...this.descendants()].filter((el) => list.some((s) => matchComplex(el, s, this)));
  }
  querySelector(sel) {
    const list = compile(sel);
    for (const el of this.descendants()) if (list.some((s) => matchComplex(el, s, this))) return el;
    return null;
  }
  matches(sel) {
    return compile(sel).some((s) => matchComplex(this, s, null));
  }
  closest(sel) {
    const list = compile(sel);
    for (let el = this; el instanceof Element; el = el.parent) if (list.some((s) => matchComplex(el, s, null))) return el;
    return null;
  }
  contains(other) {
    for (let el = other; el; el = el.parent) if (el === this) return true;
    return false;
  }
  append(...nodes) {
    for (const n of nodes) {
      if (n.parent) n.parent.children = n.parent.children.filter((c) => c !== n);
      n.parent = this;
      this.children.push(n);
    }
  }
  appendChild(n) {
    this.append(n);
    return n;
  }
  insertBefore(n, ref) {
    if (!ref) return this.appendChild(n);
    if (n.parent) n.parent.children = n.parent.children.filter((c) => c !== n);
    n.parent = this;
    this.children.splice(this.children.indexOf(ref), 0, n);
    return n;
  }
  replaceChildren(...nodes) {
    for (const c of this.children) c.parent = null;
    this.children = [];
    this.append(...nodes);
  }
  remove() {
    if (this.parent) this.parent.children = this.parent.children.filter((c) => c !== this);
    this.parent = null;
  }
  addEventListener(type, fn) {
    (this.listeners[type] ||= []).push(fn);
  }
  removeEventListener(type, fn) {
    this.listeners[type] = (this.listeners[type] || []).filter((f) => f !== fn);
  }
  dispatch(type, event = {}) {
    // bubble from this element up, like a real event
    const ev = { type, target: this, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; }, stopPropagation() {}, ...event };
    for (let el = this; el; el = el.parent) for (const fn of [...(el.listeners?.[type] || [])]) fn(ev);
    return ev;
  }
  size() {
    return hooks.sizes?.(this) ?? null;
  }
  get clientWidth() {
    return this.size()?.width ?? 1200;
  }
  get scrollWidth() {
    return this.size()?.scrollWidth ?? this.clientWidth;
  }
  get clientHeight() {
    return this.size()?.height ?? 800;
  }
  get offsetWidth() {
    return this.size()?.offsetWidth ?? 0;
  }
  get offsetHeight() {
    return this.size()?.offsetHeight ?? 0;
  }
  get offsetParent() {
    return this.hidden ? null : this.parent;
  }
  getBoundingClientRect() {
    const custom = hooks.rect?.(this);
    if (custom) return custom;
    const w = this.getAttribute("data-w");
    if (w != null) return { left: 0, top: 0, right: Number(w), bottom: 16, width: Number(w), height: 16 };
    return { left: 0, top: 0, right: 1200, bottom: 800, width: 1200, height: 800 };
  }
  setPointerCapture() {}
  releasePointerCapture() {}
  focus() {}
  blur() {}
  scrollIntoView() {}
}

export function parse(html) {
  const root = new Element("#root");
  let cur = root;
  for (const m of html.matchAll(TOKEN)) {
    const [whole, close, open, attrText, slash, text] = m;
    if (whole.startsWith("<!--")) continue;
    if (text !== undefined) {
      const t = new Text(text);
      t.parent = cur;
      cur.children.push(t);
    } else if (close) {
      const name = close.toLowerCase();
      let el = cur;
      while (el !== root && el.tag !== name) el = el.parent;
      if (el !== root) cur = el.parent;
    } else if (open) {
      const attrs = [];
      for (const a of (attrText || "").matchAll(ATTR)) attrs.push([a[1], a[2] ?? a[3] ?? a[4] ?? null]);
      const el = new Element(open, attrs);
      el.parent = cur;
      cur.children.push(el);
      if (slash) el.selfClosed = true;
      else if (!VOID.has(el.tag)) cur = el;
    }
  }
  const out = root.children;
  for (const c of out) c.parent = null;
  return out;
}

// --- Selectors ----------------------------------------------------------------------------------------------

const cache = new Map();

function splitTop(s, sep) {
  const out = [];
  let depth = 0;
  let quote = null;
  let start = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      if (c === quote) quote = null;
    } else if (c === '"' || c === "'") quote = c;
    else if (c === "(" || c === "[") depth++;
    else if (c === ")" || c === "]") depth--;
    else if (depth === 0 && c === sep) {
      out.push(s.slice(start, i));
      start = i + 1;
    }
  }
  out.push(s.slice(start));
  return out.map((x) => x.trim()).filter(Boolean);
}

function compile(sel) {
  if (cache.has(sel)) return cache.get(sel);
  const list = splitTop(sel, ",").map(complex);
  cache.set(sel, list);
  return list;
}

// "a > b c" → [{compound: a}, {comb: ">", compound: b}, {comb: " ", compound: c}]
function complex(s) {
  const parts = [];
  let i = 0;
  let comb = null;
  let depth = 0;
  let quote = null;
  let start = 0;
  const flush = (end) => {
    const text = s.slice(start, end).trim();
    if (text) {
      parts.push({ comb, compound: compound(text) });
      comb = null;
    }
  };
  for (; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      if (c === quote) quote = null;
      continue;
    }
    if (c === '"' || c === "'") quote = c;
    else if (c === "(" || c === "[") depth++;
    else if (c === ")" || c === "]") depth--;
    else if (depth === 0 && (c === " " || c === ">")) {
      flush(i);
      if (c === ">") comb = ">";
      else if (comb !== ">") comb = parts.length ? " " : null;
      start = i + 1;
    }
  }
  flush(s.length);
  return parts;
}

function compound(s) {
  const tests = [];
  const re = /^([a-zA-Z*][a-zA-Z0-9-]*)|\.([a-zA-Z0-9_-]+)|#([a-zA-Z0-9_-]+)|\[([^\]=^$*~|]+)(?:([\^$*]?=)"?((?:[^"\]]|\\")*)"?)?\]|:(is|not|has)\(/y;
  let i = 0;
  while (i < s.length) {
    re.lastIndex = i;
    const m = re.exec(s);
    if (!m) throw new Error(`selector not supported: ${s}`);
    if (m[1]) {
      const tag = m[1].toLowerCase();
      if (tag !== "*") tests.push((el) => el.tag === tag);
    } else if (m[2]) tests.push((el) => el.classList.contains(m[2]));
    else if (m[3]) tests.push((el) => el.id === m[3]);
    else if (m[4]) {
      const name = m[4].trim();
      const op = m[5];
      const value = m[6];
      tests.push((el) => {
        const v = el.getAttribute(name);
        if (v == null) return false;
        if (!op) return true;
        if (op === "=") return v === value;
        if (op === "^=") return v.startsWith(value);
        if (op === "$=") return v.endsWith(value);
        return v.includes(value);
      });
    } else if (m[7]) {
      let depth = 1;
      let j = re.lastIndex;
      for (; j < s.length && depth; j++) {
        if (s[j] === "(") depth++;
        else if (s[j] === ")") depth--;
      }
      const inner = compile(s.slice(re.lastIndex, j - 1));
      const kind = m[7];
      if (kind === "is") tests.push((el) => inner.some((x) => matchComplex(el, x, null)));
      else if (kind === "not") tests.push((el) => !inner.some((x) => matchComplex(el, x, null)));
      else tests.push((el) => [...el.descendants()].some((d) => inner.some((x) => matchComplex(d, x, el))));
      i = j;
      continue;
    }
    i = re.lastIndex;
  }
  return (el) => tests.every((t) => t(el));
}

function matchComplex(el, parts) {
  const at = (el, k) => {
    if (!parts[k].compound(el)) return false;
    if (k === 0) return true;
    const comb = parts[k].comb;
    if (comb === ">") return el.parent instanceof Element && at(el.parent, k - 1);
    for (let p = el.parent; p instanceof Element; p = p.parent) if (at(p, k - 1)) return true;
    return false;
  };
  return at(el, parts.length - 1);
}

// --- The page's globals ---------------------------------------------------------------------------------------

export function install({ width = 1440, height = 900, now = Date.parse("2026-11-04T12:00:00Z"), fetch: fetchFn } = {}) {
  const store = new Map();
  const frames = [];
  const docListeners = {};
  const winListeners = {};
  const noop = () => {};
  globalThis.localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
    clear: () => store.clear(),
  };
  const on = (bag) => (type, fn) => (bag[type] ||= []).push(fn);
  const off = (bag) => (type, fn) => (bag[type] = (bag[type] || []).filter((f) => f !== fn));
  const documentElement = new Element("html");
  Object.defineProperty(documentElement, "clientWidth", { get: () => globalThis.innerWidth });
  globalThis.window = { addEventListener: on(winListeners), removeEventListener: off(winListeners), open: noop };
  globalThis.document = {
    documentElement,
    hidden: false,
    addEventListener: on(docListeners),
    removeEventListener: off(docListeners),
    getElementById: () => null,
    createElement: (tag) => new Element(tag),
  };
  globalThis.innerWidth = width;
  globalThis.innerHeight = height;
  globalThis.location = { origin: "http://127.0.0.1:47800", href: "http://127.0.0.1:47800/", pathname: "/", search: "", assign: noop };
  globalThis.matchMedia = () => ({ matches: false, addEventListener: noop, removeEventListener: noop });
  globalThis.getComputedStyle = (el) => ({
    position: "",
    flexWrap: el?.classList?.contains("orca-marks") ? "wrap" : "",
    columnGap: el?.classList?.contains("orca-marks") ? "6px" : "normal",
    borderRightWidth: "0px",
    paddingRight: "0px",
  });
  globalThis.requestAnimationFrame = (fn) => (frames.push(fn), frames.length);
  globalThis.cancelAnimationFrame = noop;
  globalThis.CSS = { escape: (s) => String(s) };
  globalThis.MutationObserver = class {
    observe() {}
    disconnect() {}
  };
  Date.now = () => now;
  if (fetchFn) globalThis.fetch = fetchFn;
  return {
    store,
    docListeners,
    winListeners,
    // run the frames asked for so far (and the ones they ask for, up to `rounds`)
    flushFrames(rounds = 5) {
      for (let r = 0; r < rounds && frames.length; r++) for (const fn of frames.splice(0)) fn(performance.now());
    },
  };
}

// A response of the server's JSON API.
export const json = (body, status = 200) => ({ ok: status < 400, status, json: async () => body });

// The page's tasks that wait: answers of the stub fetch, setTimeout(0) and the like.
export const settle = async (rounds = 20) => {
  for (let i = 0; i < rounds; i++) await new Promise((r) => setTimeout(r, 0));
};

// orca-web's reader as the shell gives it (iss-00592), from {repository: {Scope id: [agent widths]}}: one worktree
// per listed Scope, one mark per agent, each mark as wide as given (data-w).
// iss-00616: set({summary}) gives a summary document instead (agents with ids, parents and widths w): summary() returns it,
// forScope gives the summary's worktrees at the paths the structure records for the Scope, and an agent with an id is
// drawn with data-agent-id. orderAgents gives the agents in their order (or `order`, a list of ids, when set).
export function fakeOrca(byRepo) {
  const subs = new Set();
  let doc = null;
  let order = null;
  const module = {
    buildMarks: (wt) => {
      const built = { w: wt.agents.map((a) => a.w) };
      if (wt.agents.length && wt.agents.every((a) => typeof a.id === "string")) built.marks = wt.agents.map((a) => ({ id: a.id, label: `label ${a.id}`, mark: a.mark }));
      return built;
    },
    renderAgentMarks: (slot, wt) => {
      const tag = (a) => (typeof a.id === "string" ? ` data-agent-id="${a.id}"` : "");
      slot.innerHTML = `<span class="orca-marks">${wt.agents.map((a, i) => `<span class="orca-mark" data-w="${a.w ?? 36}" data-i="${i}"${tag(a)}></span>`).join("")}</span>`;
    },
    orderAgents: (agents) => (order ? order.map((id) => agents.find((a) => a.id === id)).filter(Boolean) : agents.slice()),
  };
  return {
    origin: "http://192.0.2.1:8791",
    status: () => "ok",
    marks: () => module,
    summary: () => doc,
    forScope: (data, id) => {
      if (doc) {
        const paths = (data?.scopes?.find((s) => s.id === id)?.worktrees || []).map((r) => r.path);
        return doc.worktrees.filter((w) => paths.includes(w.path));
      }
      const widths = byRepo?.[data?.repository]?.[id];
      return widths ? [{ id: `wt-${id}`, agents: widths.map((w) => ({ w })) }] : [];
    },
    subscribe: (fn) => (subs.add(fn), () => subs.delete(fn)),
    news: () => [...subs].forEach((fn) => fn()),
    set(next) {
      if (next && typeof next === "object" && "summary" in next) {
        doc = next.summary;
        order = next.order ?? order;
      } else byRepo = next;
    },
  };
}
