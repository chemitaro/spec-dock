// One shared reader for the shell and its views (iss-00591 D-05).
import { matchWorktrees, orcaStatus } from "./orca_match.js";

function addStylesheet(href) {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  document.head.append(link);
}

export function createOrca(config, deps = {}) {
  const enabled = config?.enabled === true && typeof config.origin === "string";
  if (!enabled) return {
    origin: null,
    status: () => "off",
    summary: () => null,
    marks: () => null,
    forScope: () => [],
    subscribe: () => () => {},
    stop() {},
  };

  const origin = config.origin;
  const importModule = deps.importModule ?? ((url) => import(url));
  const setTimer = deps.setTimer ?? setTimeout;
  const clearTimer = deps.clearTimer ?? clearTimeout;
  const retryMs = deps.retryMs ?? 10000;
  const subscribers = new Set();
  let read = "none";
  let last = null;
  let module = null;
  let watcher = null;
  let stopped = false;
  let timer = null;
  let attempt = 0;
  let cachedStructure = null;
  let cachedSummary = null;
  let cached = null;
  const status = () => orcaStatus({ enabled, read, summary: last });

  function update(nextRead, nextSummary) {
    if (stopped) return;
    const before = status();
    const previous = last;
    read = nextRead;
    last = nextSummary;
    if (status() === before && last === previous) return;
    for (const fn of [...subscribers]) {
      try { fn(); } catch { /* one subscriber must not stop the others */ }
    }
  }

  async function load() {
    try {
      const suffix = attempt === 0 ? "" : `?r=${attempt}`;
      attempt++;
      const loaded = await importModule(`${origin}/embed/agent-marks.js${suffix}`);
      if (stopped) return;
      module = loaded;
      watcher = loaded.watchWorktreeSummary(origin, {
        onDocument: (doc) => update("ok", doc),
        onError: () => update("failed", null),
      });
      if (stopped) watcher.stop();
    } catch {
      if (stopped) return;
      update("failed", null);
      if (!stopped) timer = setTimer(() => {
        timer = null;
        load();
      }, retryMs);
    }
  }

  (deps.addStylesheet ?? addStylesheet)(`${origin}/embed/agent-marks.css`);
  load();
  return {
    origin,
    status,
    summary: () => status() === "ok" ? last : null,
    marks: () => module,
    subscribe(fn) {
      subscribers.add(fn);
      return () => subscribers.delete(fn);
    },
    forScope(structure, scopeId) {
      if (status() !== "ok") return [];
      if (cachedStructure !== structure || cachedSummary !== last) {
        cached = matchWorktrees(structure, last);
        cachedStructure = structure;
        cachedSummary = last;
      }
      return cached.byScope.get(scopeId) ?? [];
    },
    stop() {
      if (stopped) return;
      stopped = true;
      if (timer !== null) clearTimer(timer);
      timer = null;
      watcher?.stop();
      subscribers.clear();
    },
  };
}
