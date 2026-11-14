// The dashboard shell (iss-00529 D-09): routing, API reads, the top band, the 5-second refresh, the "seen"
// record and the embedding bridge. Screens are separate modules in views/ (see views/index.js); the shell
// calls their render(root, ctx) whenever the data or the route changes and never knows their insides.
import * as api from "./core/api.js";
import { createEmbedBridge } from "./core/embed.js";
import { createOrca } from "./core/orca.js";
import { parseRoute, withEmbed } from "./core/route.js";
import { renderNotices, renderTop } from "./core/topbar.js";
import { LIVE_MS, movedAt } from "./core/ui.js";
import { VIEWS } from "./views/index.js";
import { mountSearch } from "./views/_shared/search.js";
import { withParam } from "./views/_shared/logic.js";

const REFRESH_MS = 5000;
const SERVER_MS = 60000; // the server reads the installed version every 60 seconds (iss-00530)
const root = document.getElementById("view");
const top = document.getElementById("top");
const mobileTabs = document.getElementById("mtabs");
const noticeArea = document.getElementById("notices");

const state = {
  route: parseRoute(location.href),
  repositories: [],
  orca: null, // one reader shared by every screen
  server: null, // the listing's `server` (version, restart_required)
  data: null, // structure JSON of the current repository
  loadedAt: 0, // performance.now() when data arrived; the band counts the age on from it
  scope: null, // scope JSON on the detail screen
  baseline: null, // the seen_id that change marks compare with, fixed for this page (Epic D-18)
  revision: null,
  error: null,
  view: null, // the mounted screen module
};

const loadedStyles = new Set();
let booted = false; // the first render has run: a theme change redraws from then on

// The screens pass the theme on to the frames they hold (the agents tab, iss-00593 D-06), so a change redraws.
function setTheme(scheme) {
  if (scheme === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = scheme;
  if (booted) render();
}

const bridge = createEmbedBridge({
  getState: () => ({ repository: state.route.repository, path: state.route.path, scope: state.route.scope }),
  navigate: (path) => navigate(path),
  setTheme,
});

function href(path) {
  return withEmbed(path, state.route.embed);
}

// A choice a screen keeps by itself replaces the query without a new history entry (iss-00593 D-06). It is called
// from inside a render, so it neither redraws nor tells the embedding parent.
function replaceParam(name, value) {
  const path = withParam(state.route.path, name, value);
  history.replaceState(null, "", path);
  state.route = parseRoute(new URL(path, location.origin).href);
  return state.route;
}

function ensureStyles(module) {
  for (const path of module.styles || []) {
    if (loadedStyles.has(path)) continue;
    loadedStyles.add(path);
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = path;
    document.head.append(link);
  }
}

function title() {
  const module = VIEWS[state.route.view];
  const repo = state.route.repository?.split("/").slice(1).join("/");
  const scope = state.route.scope ? `${state.route.scope} · ` : "";
  if (!repo && state.route.view === "todos") return "人のタスク · すべてのリポジトリ · SpecDock"; // iss-00554
  return repo ? `${scope}${module?.title ?? ""} · ${repo} · SpecDock` : "すべてのリポジトリ · SpecDock";
}

function render() {
  const module = VIEWS[state.route.view] || VIEWS.graph;
  document.title = title();
  renderTop(top, mobileTabs, state);
  mountSearch(top.querySelector("#search-slot"), { route: state.route, data: state.data, navigate }); // iss-00531
  renderNotices(noticeArea, state.data, state.error, state.server);
  if (state.view !== module) {
    state.view?.dispose?.();
    root.replaceChildren();
    root.dataset.view = module.id;
    ensureStyles(module);
    state.view = module;
  }
  module.render(root, {
    repository: state.route.repository,
    route: state.route,
    data: state.data,
    scope: state.scope,
    repositories: state.repositories,
    embed: state.route.embed,
    orca: state.orca,
    orcaProblem: state.server?.orca_web?.problem ?? null, // iss-00593 D-06
    replaceParam,
    baseline: state.baseline, // the panels read a Scope against the same seen_id as the structure (iss-00587)
    navigate,
    href,
  });
}

async function loadRepository() {
  const repo = state.route.repository;
  if (!repo) return;
  try {
    state.data = await api.structure(repo, state.baseline);
    state.loadedAt = performance.now();
    state.revision = state.data.revision;
    state.liveUntil = liveUntil(state.data);
    state.scope = state.route.scope ? await api.scope(repo, state.route.scope, state.baseline).catch(() => null) : null;
    state.error = null;
  } catch (error) {
    state.error = `このリポジトリを読めませんでした（${error.message}）。`;
  }
}

// The earliest end of the 30-minute window of a Scope in progress that is moving now, or null (iss-00574 D-04).
function liveUntil(data) {
  const scopes = data?.scopes || [];
  const byId = new Map(scopes.map((item) => [item.id, item]));
  const now = Date.now();
  let first = null;
  for (const scope of scopes) {
    if (scope.state !== "doing") continue;
    const moved = movedAt(scope, byId);
    if (moved == null || now - moved > LIVE_MS) continue;
    const end = moved + LIVE_MS + 1;
    if (first == null || end < first) first = end;
  }
  return first;
}

async function refresh() {
  const repo = state.route.repository;
  if (!repo || document.hidden) return;
  try {
    const { revision } = await api.revision(repo);
    if (revision === state.revision) {
      renderTop(top, mobileTabs, state); // the fetch age keeps counting while nothing changes
      if (state.liveUntil != null && Date.now() >= state.liveUntil) {
        state.liveUntil = liveUntil(state.data); // a mark in progress passed its 30 minutes: stop its blinking
        render();
      }
      return;
    }
    await loadRepository();
    render();
  } catch {
    // keep showing the last data; the next tick tries again
  }
}

// Same-repository moves stay in this page (baseline kept, no new "seen"); another repository loads a page.
async function navigate(path, { push = true } = {}) {
  const target = parseRoute(new URL(href(path), location.origin).href);
  if (target.repository !== state.route.repository) {
    location.assign(target.path);
    return;
  }
  if (push && target.path !== state.route.path) history.pushState(null, "", target.path);
  state.route = target;
  state.scope = target.scope ? await api.scope(target.repository, target.scope, state.baseline).catch(() => null) : null;
  render();
  root.focus({ preventScroll: true });
  bridge.navigated();
}

function interceptLinks(event) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const anchor = event.target.closest("a[href]");
  if (!anchor || anchor.target === "_blank" || anchor.hasAttribute("download")) return;
  const url = new URL(anchor.href, location.href);
  if (url.origin !== location.origin) {
    // Outside links always open a new tab (Epic D-15), never inside the frame.
    event.preventDefault();
    window.open(url.href, "_blank", "noopener");
    return;
  }
  const screen = url.pathname === "/" || url.pathname === "/todos" || (url.pathname.startsWith("/r/") && !url.pathname.includes("/files/"));
  if (!screen) return; // materials and other files open as ordinary pages
  const target = parseRoute(url.href);
  if (!target.repository || target.repository !== state.route.repository) {
    event.preventDefault();
    location.assign(href(url.pathname + url.search)); // another repository or the overview: a page load
    return;
  }
  event.preventDefault();
  navigate(url.pathname + url.search);
}

// Re-read the listing's `server` so a package update shows the restart notice without reloading (iss-00535 R-05).
async function checkServer() {
  if (document.hidden) return;
  try {
    const listing = await api.repositories();
    const before = state.server?.restart_required;
    state.server = listing.server ?? null;
    if (state.server?.restart_required !== before) renderNotices(noticeArea, state.data, state.error, state.server);
  } catch {
    // keep the last answer; the next tick tries again
  }
}

async function boot() {
  document.title = title(); // a `hello` answered before the first render still reports the screen's title
  if (state.route.embed) document.documentElement.dataset.embed = "1";
  document.addEventListener("click", interceptLinks);
  window.addEventListener("popstate", () => navigate(location.pathname + location.search, { push: false }));
  try {
    const listing = await api.repositories();
    state.repositories = listing.repositories;
    state.server = listing.server ?? null;
    bridge.setAllowedHosts(listing.server?.embed_hosts);
  } catch (error) {
    bridge.setAllowedHosts([]);
    state.error = `リポジトリの一覧を読めませんでした（${error.message}）。`;
  }
  state.orca = createOrca(state.server?.orca_web ?? null);
  if (state.route.repository) {
    await loadRepository();
    if (state.data) {
      // Compare with the record that was latest when this page opened, then record this visit once.
      state.baseline = state.data.seen?.latest_id ?? null;
      // Only a structure with a model has anything to record (Epic D-18); the server refuses the rest with 409,
      // which the browser would log as an error (iss-00544).
      if (state.data?.snapshot?.fetched_at) {
        await api.markSeen(state.route.repository);
      }
    }
  }
  render();
  booted = true;
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render); // the OS theme (iss-00593 D-06)
  setInterval(refresh, REFRESH_MS);
  setInterval(checkServer, SERVER_MS);
  document.addEventListener("visibilitychange", refresh);
}

boot();
