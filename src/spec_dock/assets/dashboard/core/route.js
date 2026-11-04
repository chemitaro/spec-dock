// Screen paths (Epic D-03, R-17): `/` is the overview; a repository's screens live under
// `/r/<host>/<owner>/<name>/` (home = graph), `…/graph`, `…/board`, `…/timeline`, `…/scopes/<ID>`.
// `/r/…/scopes/<ID>` and `?embed=1` are a stable contract. The human tasks (iss-00554): `/todos` (every repository),
// `/r/<repo>/todos` and `/r/<repo>/todos/<ID>`, all with view "todos" (`todo` is the task ID on the one-task screen).

export function parseRoute(url) {
  const parsed = new URL(url, location.href);
  const parts = parsed.pathname.split("/").filter(Boolean).map(decodeURIComponent);
  const params = parsed.searchParams;
  const embed = params.get("embed") === "1";
  if (parts[0] !== "r" || parts.length < 4) {
    const view = parts.length === 1 && parts[0] === "todos" ? "todos" : "overview";
    return { view, repository: null, scope: null, todo: null, params, embed, path: parsed.pathname + parsed.search };
  }
  const repository = parts.slice(1, 4).join("/");
  const rest = parts.slice(4);
  let view = "graph";
  let scope = null;
  let todo = null;
  if (rest[0] === "scopes" && rest[1]) {
    view = "scope";
    scope = rest[1];
  } else if (rest[0] === "todos") {
    view = "todos";
    todo = rest[1] || null;
  } else if (["graph", "board", "timeline"].includes(rest[0])) {
    view = rest[0];
  }
  return { view, repository, scope, todo, params, embed, path: parsed.pathname + parsed.search };
}

// Keep embed=1 on every path the shell builds.
export function withEmbed(path, embed) {
  if (!embed) return path;
  const url = new URL(path, location.origin);
  url.searchParams.set("embed", "1");
  return url.pathname + url.search + url.hash;
}

export const repositoryPath = (repository, view = "graph") => (view === "graph" ? `/r/${repository}/` : `/r/${repository}/${view}`);
export const scopePath = (repository, scopeId) => `/r/${repository}/scopes/${scopeId}`;
export const todosPath = (repository) => (repository ? `/r/${repository}/todos` : "/todos");
export const todoPath = (repository, todoId) => `/r/${repository}/todos/${encodeURIComponent(todoId)}`;
