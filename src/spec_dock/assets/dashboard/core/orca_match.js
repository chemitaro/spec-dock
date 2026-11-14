// Pure Scope/worktree correspondence (iss-00591 D-04).
export const SUMMARY_SCHEMA = "orca-web.worktree-summary/v1";

export function normPath(value) {
  if (typeof value !== "string") return null;
  return value.replace(/\/+$/, "") || (value.startsWith("/") ? "/" : "");
}

export function summaryValid(summary) {
  return summary !== null && typeof summary === "object" && !Array.isArray(summary)
    && summary.schema === SUMMARY_SCHEMA && Array.isArray(summary.worktrees);
}

export function orcaStatus({ enabled, read, summary }) {
  if (!enabled) return "off";
  if (read === "none") return "loading";
  if (read === "failed" || !summaryValid(summary)) return "unreachable";
  switch (summary.connection?.state) {
    case "connected": return "ok";
    case "unreachable": return "orca-unreachable";
    case "starting": return "orca-starting";
    default: return "unreachable";
  }
}

export function matchWorktrees(structure, summary) {
  if (structure?.worktrees?.status !== "ok") return { status: "no-records", byScope: new Map() };
  if (!summaryValid(summary)) return { status: "invalid", byScope: new Map() };
  const byPath = new Map();
  const byBranch = new Map();
  const scopes = Array.isArray(structure.scopes) ? structure.scopes : [];
  for (const scope of scopes) {
    const records = Array.isArray(scope?.worktrees) ? scope.worktrees : [];
    records.forEach((record, index) => {
      const target = { scopeId: scope.id, index };
      const path = normPath(record?.path);
      if (path !== null && !byPath.has(path)) byPath.set(path, target);
      const branch = record?.branch;
      if (typeof branch === "string" && !byBranch.has(branch)) byBranch.set(branch, target);
    });
  }
  const paths = new Set(structure.worktrees.paths.map(normPath).filter((path) => path !== null));
  const projects = new Set(summary.worktrees
    .filter((worktree) => paths.has(normPath(worktree?.path)) && typeof worktree?.project?.id === "string")
    .map((worktree) => worktree.project.id));
  const buckets = new Map();
  for (const worktree of summary.worktrees) {
    if (worktree === null || typeof worktree !== "object") continue;
    let target = byPath.get(normPath(worktree.path));
    if (!target && typeof worktree.project?.id === "string" && projects.has(worktree.project.id)) {
      target = byBranch.get(worktree.branch);
    }
    if (!target) continue;
    if (!buckets.has(target.scopeId)) buckets.set(target.scopeId, []);
    buckets.get(target.scopeId).push({ index: target.index, worktree });
  }
  const byScope = new Map();
  for (const scope of scopes) {
    const entries = buckets.get(scope.id);
    if (entries) byScope.set(scope.id, entries.sort((a, b) => a.index - b.index).map((entry) => entry.worktree));
  }
  return { status: "ok", byScope };
}

export function mergedWorktree(list) {
  if (!list.length) return null;
  if (list.length === 1) return list[0];
  const { id, path, branch, project } = list[0];
  const counts = new Map();
  const agents = [];
  for (const worktree of list) {
    if (Array.isArray(worktree.agents)) agents.push(...worktree.agents);
    for (const [key, value] of Object.entries(worktree.counts ?? {})) {
      counts.set(key, (counts.get(key) ?? 0) + (typeof value === "number" ? value : 0));
    }
  }
  return { id, path, branch, project, agents, counts: Object.fromEntries(counts) };
}
