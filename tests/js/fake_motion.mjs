// The clock, the page's visibility and IntersectionObserver for the command lines' motion (iss-00646 T-03), beside
// fake_dom.mjs. setTimeout with a delay above 0 waits on a clock that only advance(ms) moves (0 stays the real one, so
// settle() still runs the page's tasks); setHidden(bool) sets document.visibilityState and sends visibilitychange;
// useObserver(true) gives the page a fake IntersectionObserver whose answers tell(selector, hit) sends.
const realSet = globalThis.setTimeout;
const realClear = globalThis.clearTimeout;

export function installMotion(page) {
  let now = 0;
  let next = 0;
  const timers = new Map();
  globalThis.setTimeout = (fn, ms = 0, ...args) => {
    if (!(ms > 0)) return realSet(fn, 0, ...args);
    const id = `fake-${++next}`;
    timers.set(id, { at: now + ms, fn: () => fn(...args) });
    return id;
  };
  globalThis.clearTimeout = (id) => (typeof id === "string" && id.startsWith("fake-") ? timers.delete(id) : realClear(id));
  globalThis.document.visibilityState = "visible";

  const observers = [];
  class FakeObserver {
    constructor(cb, opts) {
      this.cb = cb;
      this.opts = opts || {};
      this.els = new Set();
      this.alive = true;
      observers.push(this);
    }
    observe(el) {
      this.els.add(el);
    }
    unobserve(el) {
      this.els.delete(el);
    }
    disconnect() {
      this.els.clear();
      this.alive = false;
    }
  }

  return {
    advance(ms) {
      now += ms;
      for (;;) {
        const due = [...timers.entries()].filter(([, t]) => t.at <= now).sort((a, b) => a[1].at - b[1].at)[0];
        if (!due) break;
        timers.delete(due[0]);
        due[1].fn();
      }
    },
    pending: () => timers.size,
    setHidden(hidden) {
      globalThis.document.visibilityState = hidden ? "hidden" : "visible";
      globalThis.document.hidden = hidden;
      for (const fn of [...(page.docListeners.visibilitychange || [])]) fn({ type: "visibilitychange" });
    },
    useObserver(on) {
      if (on) globalThis.IntersectionObserver = FakeObserver;
      else delete globalThis.IntersectionObserver;
    },
    // the live observers' answers: every observed element matching the selector is (not) on the screen
    tell(selector, hit) {
      for (const o of observers.filter((x) => x.alive)) {
        const entries = [...o.els].filter((el) => el.matches(selector)).map((target) => ({ target, isIntersecting: hit }));
        if (entries.length) o.cb(entries, o);
      }
    },
    // the live observers, what they watch and how many of those left the given root
    observed(root) {
      const live = observers.filter((o) => o.alive);
      const els = live.flatMap((o) => [...o.els]);
      return {
        live: live.length,
        made: observers.length,
        count: els.length,
        gone: els.filter((el) => !root?.contains(el)).length,
        roots: live.map((o) => o.opts.root?.getAttribute?.("class") ?? null),
        threshold: live.map((o) => o.opts.threshold ?? null),
      };
    },
    reset() {
      timers.clear();
      observers.length = 0;
      globalThis.document.visibilityState = "visible";
      globalThis.document.hidden = false;
    },
  };
}
