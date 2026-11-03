// Screen paths (Epic D-03, R-17): `/` is the overview; a repository's screens live under
// `/r/<host>/<owner>/<name>/` (home = graph), `…/graph`, `…/board`, `…/timeline`, `…/scopes/<ID>`.
// `/r/…/scopes/<ID>` and `?embed=1` are a stable contract.

export function parseRoute(url) {
  const parsed = new URL(url, location.href);
  const parts = parsed.pathname.split("/").filter(Boolean).map(decodeURIComponent);
  const params = parsed.searchParams;
  const embed = params.get("embed") === "1";
  if (parts[0] !== "r" || parts.length < 4) {
    return { view: "overview", repository: null, scope: null, params, embed, path: parsed.pathname + parsed.search };
  }
  const repository = parts.slice(1, 4).join("/");
  const rest = parts.slice(4);
  let view = "graph";
  let scope = null;
  if (rest[0] === "scopes" && rest[1]) {
    view = "scope";
    scope = rest[1];
  } else if (["graph", "board", "timeline"].includes(rest[0])) {
    view = rest[0];
  }
  return { view, repository, scope, params, embed, path: parsed.pathname + parsed.search };
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
