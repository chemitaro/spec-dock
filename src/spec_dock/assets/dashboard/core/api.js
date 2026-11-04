// The server's JSON API (specdock.dashboard/v1). Only same-origin requests; never GitHub (Epic R-04, D-03).

async function getJson(path) {
  const response = await fetch(path, { headers: { Accept: "application/json" }, cache: "no-store", credentials: "omit" });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(body?.error?.message || `HTTP ${response.status}`);
    error.status = response.status;
    error.body = body;
    throw error;
  }
  return body;
}

const api = (repository, op) => `/api/v1/r/${repository}/${op}`;

export const repositories = () => getJson("/api/v1/repositories");
export const revision = (repository) => getJson(api(repository, "revision"));
export const summary = (repository) => getJson(api(repository, "summary"));

export function structure(repository, baseline) {
  return getJson(api(repository, "structure") + (baseline ? `?baseline=${encodeURIComponent(baseline)}` : ""));
}

export function scope(repository, scopeId, baseline) {
  return getJson(api(repository, `scopes/${encodeURIComponent(scopeId)}`) + (baseline ? `?baseline=${encodeURIComponent(baseline)}` : ""));
}

// Epic D-18: the server records the current model; the body is ignored. The fixed header and the JSON type
// make another origin need a preflight, which the server never grants.
// A refusal or a failed request never stops the page: the answer is then null.
export async function markSeen(repository) {
  const response = await fetch(api(repository, "seen"), {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-SpecDock-Dashboard": "1" },
    body: "{}",
    cache: "no-store",
    credentials: "omit",
  }).catch(() => null);
  return response?.ok ? response.json().catch(() => null) : null;
}

// The human tasks (iss-00554 D-04): read only, like everything else here.
const statusQuery = (status) => (status && status !== "open" ? `?status=${encodeURIComponent(status)}` : "");
export const todos = (status) => getJson(`/api/v1/todos${statusQuery(status)}`);
export const todosRevision = () => getJson("/api/v1/todos/revision");
export const repositoryTodos = (repository, status) => getJson(api(repository, "todos") + statusQuery(status));
export const todo = (repository, todoId) => getJson(api(repository, `todos/${encodeURIComponent(todoId)}`));
