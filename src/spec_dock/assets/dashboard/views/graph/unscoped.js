// The Unscoped row (iss-00668 D-02): the items of one repository's row above its structure, shared by the structure
// graph (graph.js) and each repository's frame of the cross-repository structure (allgraph/command.js). The main
// checkout (Primary) is always first; the worktrees of git linked to no Scope (Unlinked) follow; the ends of the command
// lines in no such item keep today's items; the idle Unlinked worktrees fold into one "+N" when there are FOLD or more.
// Pure computation like command.js: no DOM, no clock, no network.
import { mergedWorktree, normPath, summaryValid } from "../../core/orca_match.js";
import { agentRef, bandItems, bandKeys, bandLabel } from "./command.js";
import { agentTypeLabel } from "../_shared/agents_logic.js";

/** The English words of the row and their explanations, in one place (the Issue's decisions). */
export const UNSCOPED = {
  lead: "Unscoped",
  leadTitle: "Worktrees not shown as a Scope box",
  primary: { text: "Primary", title: "The main checkout of this repository" },
  unlinked: { text: "Unlinked", title: "Not linked to any Scope. Link it with `spec-dock work start`." },
  count: (n) => `${n} ${n === 1 ? "agent" : "agents"} in progress`,
};

/** This many idle Unlinked items or more fold into one "+N" (R-04). */
export const FOLD = 2;

const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const byText = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

/**
 * The structure API's git worktree list (R-01), each path normalized; null when the list was not read or the structure
 * has no `items` (an old server, F-01).
 */
export function gitWorktrees(structure) {
  const w = structure?.worktrees;
  if (w?.status !== "ok" || !Array.isArray(w.items)) return null;
  return w.items
    .filter((r) => isObject(r) && typeof r.path === "string")
    .map((r) => ({
      path: normPath(r.path),
      branch: typeof r.branch === "string" && r.branch ? r.branch : null,
      head: typeof r.head === "string" && r.head ? r.head : null,
      main: r.main === true,
      detached: r.detached === true,
      locked: r.locked === true,
    }));
}

/** The number of children of each parent agent: Map<parent id, n> (each child once). */
export function childCount(pairs) {
  const kids = new Map();
  for (const p of pairs || []) {
    if (!kids.has(p.parent.id)) kids.set(p.parent.id, new Set());
    kids.get(p.parent.id).add(p.child.id);
  }
  return new Map([...kids].map(([id, set]) => [id, set.size]));
}

/**
 * The count's title and aria-label (R-09): the total and each commanding agent's part; null without a count. Each
 * part's kind is named from orca-web's marks component when one is given (iss-00674).
 */
export function countTitle(item, marks = null) {
  if (!item?.count) return null;
  const parts = (item.countParts || []).map((p) => `${agentTypeLabel(marks, p.agentType, "agent")} #${p.index}: ${p.n}`);
  return parts.length ? `${UNSCOPED.count(item.count)} — ${parts.join(", ")}` : UNSCOPED.count(item.count);
}

/** Whether a row has an item with a count (a frame kept for its row in "next", R-07). */
export const commanding = (items) => (items || []).some((it) => !!it.count);

// the agents of a group of summary worktrees in the component's order, each with its own worktree
function agentsOf(list, orderOf) {
  const merged = mergedWorktree(list);
  if (!merged) return { worktree: null, agents: [] };
  const owner = new Map();
  for (const w of list) for (const a of Array.isArray(w.agents) ? w.agents : []) if (isObject(a) && typeof a.id === "string" && !owner.has(a.id)) owner.set(a.id, { a, w });
  const order = (typeof orderOf === "function" ? orderOf(merged) : null) || merged.agents || [];
  const ids = order.map((a) => (typeof a === "string" ? a : a?.id)).filter((id) => owner.has(id));
  for (const id of owner.keys()) if (!ids.includes(id)) ids.push(id);
  return { worktree: merged, agents: [...new Set(ids)].map((id) => agentRef(owner.get(id).a, owner.get(id).w)) };
}

const blank = { badge: null, idle: false, count: null, countParts: [], folded: null };

/**
 * The items of one repository's row (R-02..R-04, R-06, R-09, F-01..F-04).
 * @param structure the repository's structure (worktrees.items, scopes[].worktrees)
 * @param summary   orca-web's summary (invalid: git alone, F-02)
 * @param pairs     commandPairs(summary), all of them (the counts)
 * @param places    the places of the drawn pairs' ends (empty in "next"): only their band ends make items
 * @param own       this repository's worktrees of the summary
 * @param orderOf   worktree -> its agents in the component's order, or null
 * @param range     "all" | "now" | "next"
 * @returns {items: [Item], places: the places with the ends of a merged worktree on its item's key}
 */
export function unscopedItems({ structure, summary, pairs = [], places = new Map(), own = new Set(), orderOf = null, range = "all" }) {
  const git = gitWorktrees(structure);
  const valid = summaryValid(summary);
  const keys = valid ? bandKeys(summary) : new Map();
  const ends = bandItems(pairs, places, own, orderOf);
  const outPlaces = new Map(places);
  const items = [];
  const extra = [];
  if (git) {
    const linked = new Set();
    for (const s of Array.isArray(structure.scopes) ? structure.scopes : [])
      for (const r of Array.isArray(s?.worktrees) ? s.worktrees : []) {
        const p = normPath(r?.path);
        if (p !== null) linked.add(p);
      }
    const byPath = new Map();
    if (valid)
      for (const w of summary.worktrees) {
        if (!isObject(w)) continue;
        const p = normPath(w.path);
        if (p === null) continue;
        if (!byPath.has(p)) byPath.set(p, []);
        byPath.get(p).push(w);
      }
    for (const row of git) {
      if (!row.main && linked.has(row.path)) continue;
      const list = byPath.get(row.path) || [];
      const { worktree, agents } = agentsOf(list, orderOf);
      items.push({
        ...blank,
        key: list.length ? keys.get(list[0]) : `git:${row.path}`,
        kind: "worktree",
        label: bandLabel({ branch: row.branch, head: row.detached ? row.head : null }, true),
        badge: row.main ? "primary" : "unlinked",
        own: true,
        main: row.main,
        worktree: worktree || { id: null, path: row.path, branch: row.branch, agents: [] },
        path: row.path,
        agents,
        members: new Set(list),
      });
    }
    // the ends of the drawn lines: on the item of their worktree, else today's item (no badge)
    for (const end of ends) {
      const hit = items.find((it) => it.members.has(end.worktree));
      if (!hit) {
        extra.push({ ...blank, ...end, kind: "worktree", path: normPath(end.worktree?.path) });
        continue;
      }
      for (const ref of end.agents) if (!hit.agents.some((a) => a.id === ref.id)) hit.agents.push(ref);
    }
    for (const it of items)
      for (const a of it.agents) {
        const p = outPlaces.get(a.id);
        if (p?.kind === "band" && p.key !== it.key) outPlaces.set(a.id, { ...p, key: it.key });
      }
    for (const it of items) delete it.members;
  } else {
    // F-01: today's ends alone; the summary's main checkout is Primary
    for (const end of ends) extra.push({ ...blank, ...end, kind: "worktree", badge: end.main ? "primary" : null, path: normPath(end.worktree?.path) });
  }
  const all = [...items, ...extra];
  const kids = childCount(pairs);
  for (const it of all) {
    it.idle = it.agents.length === 0;
    if (range !== "next") continue;
    const parts = it.agents.map((a, i) => ({ id: a.id, agentType: a.agentType ?? null, index: i + 1, n: kids.get(a.id) || 0 })).filter((p) => p.n > 0);
    const n = parts.reduce((s, p) => s + p.n, 0);
    it.count = n || null;
    it.countParts = parts;
  }
  const primary = all.filter((it) => it.badge === "primary");
  let unlinked = all.filter((it) => it.badge === "unlinked");
  let others = all.filter((it) => it.badge === null);
  if (range === "next") {
    unlinked = unlinked.filter((it) => it.count);
    others = [];
  }
  unlinked.sort((a, b) => byText(a.label, b.label) || byText(a.key, b.key));
  const idle = unlinked.filter((it) => it.idle);
  const out = [...primary];
  if (idle.length >= FOLD) {
    out.push(...unlinked.filter((it) => !it.idle), ...others);
    out.push({
      ...blank,
      key: "fold",
      kind: "fold",
      label: `+${idle.length}`,
      own: true,
      main: false,
      worktree: null,
      path: null,
      agents: [],
      idle: true,
      folded: idle.map((it) => ({ label: it.label, path: it.path })),
    });
  } else out.push(...unlinked, ...others);
  return { items: out, places: outPlaces };
}
