// Pure helpers for the board, the detail screen, the overview and the search (iss-00531). No DOM here, so
// node can test them (tests/unit/infra/test_dashboard_screens_js.py). Nothing here judges a state: lanes,
// merge groups, ranks and changes come from the server's model (#528), which the screens only copy.
import { KIND_LABEL, PR_STATE_WORDS, STATE_WORDS } from "../../core/ui.js";

export const LANES = [
  ["blocked", STATE_WORDS.blocked, "依存の先か上位が終わっていない。待ち先の少ない順"],
  ["ready", STATE_WORDS.ready, "待っているものがない。後に続く数の多い順"],
  ["doing", STATE_WORDS.doing, "作業中の印か、下書きの PR がある。後に続く数の多い順"],
  ["awaiting_merge", "マージ待ち", "作業中で、下書きでない PR が開いている"],
];
export const DONE_LANE = ["done", STATE_WORDS.done, "閉じた Scope（新しい順）"];
export const DONE_LIMIT = 30;
export const KINDS = [
  ["", "すべて"],
  ...Object.entries(KIND_LABEL),
];
export { KIND_LABEL, PR_STATE_WORDS, STATE_WORDS }; // their home is core/ui.js (iss-00544)
// The detail tabs live in views/_shared/scope_tabs.js (SCOPE_TABS, iss-00587 D-03).

export const byRank = (a, b) => (a.rank ?? 1e9) - (b.rank ?? 1e9) || a.number - b.number;

// Board options live in the query string (Epic R-17): kind, group=1, done=1.
export function boardOptions(params) {
  const kind = params.get("kind") || "";
  return {
    kind: KIND_LABEL[kind] ? kind : "",
    group: params.get("group") === "1",
    done: params.get("done") === "1",
  };
}

// The same path with one query parameter set (value "" or null removes it); embed=1 is kept as is.
export function withParam(path, name, value) {
  const url = new URL(path, "http://x");
  if (value === "" || value == null || value === false) url.searchParams.delete(name);
  else url.searchParams.set(name, value === true ? "1" : String(value));
  const query = url.searchParams.toString();
  return url.pathname + (query ? `?${query}` : "");
}

// Columns of the board from the server's lanes; rank keeps the recommended order (Epic R-31).
export function boardColumns(scopes, { kind = "", done = false } = {}) {
  const pool = scopes.filter((item) => !kind || item.kind === kind);
  const lanes = [...LANES, ...(done ? [DONE_LANE] : [])];
  const columns = lanes.map(([lane, label, note]) => {
    let items = pool.filter((item) => item.lane === lane);
    let hidden = 0;
    if (lane === "done") {
      items.sort((a, b) => (b.closed_at || "").localeCompare(a.closed_at || "") || b.number - a.number);
      hidden = Math.max(0, items.length - DONE_LIMIT);
      items = items.slice(0, DONE_LIMIT);
    } else {
      items.sort(byRank);
    }
    const column = { lane, label, note, items, hidden };
    if (lane === "awaiting_merge") {
      column.mergeable = items.filter((item) => item.merge === "mergeable");
      column.needsFix = items.filter((item) => item.merge === "needs_fix");
    }
    return column;
  });
  const unknown = pool.filter((item) => item.lane === "unknown").sort(byRank);
  return { columns, unknown };
}

// Group a column's cards by parent; parents follow their best-ranked card.
export function groupByParent(items) {
  const groups = new Map();
  for (const item of items) {
    const key = item.parent_id || "";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }
  return [...groups.entries()].map(([parent, members]) => ({ parent: parent || null, items: members }));
}

// Counts for the band above the board: Issues only (the columns' unit of work), and the done share of all.
export function boardCounts(scopes) {
  const issues = scopes.filter((item) => item.kind === "issue");
  const lane = (name) => issues.filter((item) => item.lane === name).length;
  const done = scopes.filter((item) => item.state === "done").length;
  return {
    blocked: lane("blocked"),
    ready: lane("ready"),
    doing: lane("doing"),
    merge: lane("awaiting_merge"),
    mergeable: issues.filter((item) => item.merge === "mergeable").length,
    needsFix: issues.filter((item) => item.merge === "needs_fix").length,
    unknown: lane("unknown"),
    done,
    total: scopes.length,
    percent: scopes.length ? Math.round((done / scopes.length) * 100) : 0,
  };
}

export const STATE_ORDER = ["blocked", "ready", "doing", "unknown", "done"];

export function stateCounts(items) {
  const counts = { blocked: 0, ready: 0, doing: 0, unknown: 0, done: 0 };
  for (const item of items) counts[item.state] = (counts[item.state] || 0) + 1;
  return counts;
}

// Search (Epic R-17): ID (also without zero padding, e.g. iss-531), number (531, #531), or title words.
export function normalizeId(text) {
  const match = /^(init|epic|iss)-0*(\d+)$/i.exec(text.trim());
  return match ? `${match[1].toLowerCase()}-${match[2].padStart(5, "0")}` : null;
}

export function searchScopes(scopes, query, limit = 8) {
  const text = query.trim();
  if (!text) return [];
  const lower = text.toLowerCase();
  const id = normalizeId(text);
  const number = /^#?(\d+)$/.exec(text)?.[1];
  const exact = [];
  const partial = [];
  for (const item of scopes) {
    if ((id && item.id === id) || (number && item.number === Number(number))) exact.push(item);
    else if (item.id.includes(lower) || (item.title || "").toLowerCase().includes(lower)) partial.push(item);
  }
  return [...exact.sort(byRank), ...partial.sort(byRank)].slice(0, limit);
}

const PR_PHASE_WORDS = {
  none: "PR なし",
  draft: "下書きの PR",
  open: "開いた PR",
  needs_fix: "直す必要がある PR",
  merged: "マージ済み",
  closed: "閉じた PR",
};

// What changed since the last visit, in words (Epic R-29).
export function changeWords(change, scope) {
  if (!change) return null;
  const kinds = change.kinds || [];
  if (kinds.includes("new")) return "新しい";
  const parts = [];
  if (kinds.includes("state")) {
    parts.push(`状態が変わった（${STATE_WORDS[change.state_before] ?? "?"} → ${STATE_WORDS[scope?.state] ?? "?"}）`);
  }
  if (kinds.includes("pr")) parts.push(`PR が変わった（前は${PR_PHASE_WORDS[change.pr_before] ?? "?"}）`);
  return parts.join("・") || "変わった";
}

export const CHECK_WORDS = { success: "CI 成功", failure: "CI 失敗", pending: "CI 実行中", none: "CI なし" };
export const MERGEABLE_WORDS = { mergeable: "マージできる", conflicting: "衝突がある", unknown: "マージの可否は不明" };

export function prPhase(pr) {
  if (!pr) return null;
  if (pr.state === "open" && pr.is_draft) return "draft";
  return pr.state;
}

export function prWords(pr) {
  if (!pr) return "";
  const phase = prPhase(pr);
  const parts = [`PR #${pr.number} ${PR_STATE_WORDS[phase] ?? phase}`];
  if (pr.checks) parts.push(CHECK_WORDS[pr.checks] ?? pr.checks);
  if (pr.state === "open" && !pr.is_draft && pr.mergeable) parts.push(MERGEABLE_WORDS[pr.mergeable] ?? pr.mergeable);
  return parts.join("・");
}

// The pull request band of a repository (Epic R-30): unknown hides the marks, stale keeps them.
export function pullRequestNotice(data) {
  const status = data?.pull_requests?.status;
  if (status === "unknown") return { level: "unknown", text: "PR の状態が分かりません。マージ待ちの列と PR の印は出せません（定期の同期が PR を取るまで）。" };
  if (status === "stale") return { level: "stale", text: "PR の最後の取得が失敗しました。前回の値を示しています。" };
  return null;
}

// Age text for the overview's warning band.
export function agoText(seconds) {
  if (seconds == null) return null;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${Math.max(minutes, 1)}分`;
  const hours = Math.floor(minutes / 60);
  return hours < 48 ? `${hours}時間` : `${Math.floor(hours / 24)}日`;
}

// The overview card's warnings (Epic R-09, D-16): missing, unreadable, unknown version, stale, anomalies,
// unknown pull requests, two clones, or an API failure.
export function overviewWarnings(structure, failure) {
  if (failure) {
    return [{ level: "error", text: `このリポジトリを読めませんでした（${failure}）。`, next: ["spec-dock dashboard list"] }];
  }
  const found = [];
  const snapshot = structure?.snapshot || {};
  const age = agoText(snapshot.age_seconds);
  const notices = new Map((structure?.notices || []).map((item) => [item.code, item]));
  if (snapshot.status === "missing") {
    found.push({ level: "error", text: "構造のスナップショットがありません。", next: ["spec-dock canonical link", "spec-dock canonical status"] });
  } else if (snapshot.status === "unsupported") {
    found.push({ level: "error", text: "構造のスナップショットが知らない版です。SpecDock を更新してください。", next: ["spec-dock --version"] });
  } else if (snapshot.status === "unreadable") {
    found.push({
      level: "error",
      text: `構造のスナップショットが読めません${age ? `（最後に読めたのは${age}前の取得）` : ""}。`,
      next: ["spec-dock canonical status"],
    });
  }
  const stale = snapshot.status !== "missing" && (snapshot.stale || notices.has("SNAPSHOT_STALE"));
  if (stale) {
    found.push({ level: "warning", text: `${age ?? "長い間"}前から更新されていません（定期の同期を確かめてください）。`, next: ["spec-dock canonical status"] });
  }
  const anomalies = structure?.anomalies?.length || 0;
  if (anomalies) found.push({ level: "warning", text: `構造の異常が ${anomalies}件あります。`, next: ["spec-dock workspace validate"] });
  if (structure?.pull_requests?.status === "unknown") found.push({ level: "info", text: "PR の状態が分かりません。", next: [] });
  if (notices.has("REPOSITORY_AMBIGUOUS")) found.push({ level: "warning", text: notices.get("REPOSITORY_AMBIGUOUS").text, next: notices.get("REPOSITORY_AMBIGUOUS").next_steps || [] });
  return found;
}

// Parent chain from the structure, nearest last (for the path in the detail header).
export function ancestors(byId, scope) {
  const chain = [];
  let current = scope?.parent_id ? byId.get(scope.parent_id) : null;
  while (current && !chain.includes(current)) {
    chain.unshift(current);
    current = current.parent_id ? byId.get(current.parent_id) : null;
  }
  return chain;
}

export function formatSize(bytes) {
  if (bytes == null) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function fmtDay(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? "" : `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
}

export function fmtDateTime(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// Leave the frame: the same path without embed=1 (Epic F-13).
export function withoutEmbed(path) {
  return withParam(path, "embed", null);
}
