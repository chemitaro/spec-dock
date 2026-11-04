// Pure helpers of the human-task screens (iss-00554 D-05). No DOM here, so node can test them
// (tests/unit/infra/test_dashboard_todos_js.py). The server decides every state (`derived`) and the order
// (epic-00547 D-08); these helpers only group, filter and put them into words.
import { esc } from "../../core/ui.js";

export const GROUPS = [
  ["overdue", "期限切れ", "期限を過ぎた。先に片付ける"],
  ["soon", "期限が近い", "24時間以内に期限が来る"],
  ["blocking", "止めている", "これが終わるまで進められない Scope がある"],
  ["later", "あとで", "期限に余裕がある"],
  ["snoozed", "延期中", "延期の終わりまで隠している"],
  ["closed", "閉じた", "完了か取り消し（新しい順）"],
];

export const KIND_WORDS = {
  decide: "決める",
  check: "確かめる",
  operate: "操作する",
  act: "行う",
  todo: "やること",
  checklist: "束",
};

export const STATUS_WORDS = { open: "開いている", snoozed: "延期中", done: "完了", cancelled: "取り消し" };
export const ACTION_WORDS = {
  added: "登録",
  updated: "更新",
  done: "完了",
  snoozed: "延期",
  cancelled: "取り消し",
  reopened: "開き直し",
  subtask_add: "サブタスクの追加",
  subtask_done: "サブタスクの完了",
  subtask_cancel: "サブタスクの取り消し",
};

// The group of one list item, from the server's derived states (the same rule as todo_model._group).
export function groupOf(item) {
  const status = item?.todo?.status;
  const view = item?.derived || {};
  if (status === "done" || status === "cancelled") return "closed";
  if (view.effective_status === "snoozed") return "snoozed";
  if (view.overdue) return "overdue";
  if (view.due_soon) return "soon";
  if (view.blocking) return "blocking";
  return "later";
}

// Items in their groups, keeping the server's order inside each group; empty groups are left out.
export function groupItems(items) {
  const found = new Map(GROUPS.map(([key]) => [key, []]));
  for (const item of items || []) found.get(groupOf(item)).push(item);
  return GROUPS.filter(([key]) => found.get(key).length).map(([key, label, note]) => ({ key, label, note, items: found.get(key) }));
}

// Filters in the query string (Epic R-17): repo, tag, kind and closed=1 (snoozed and closed tasks too).
export function todoOptions(params) {
  const kind = params.get("kind") || "";
  return {
    repo: params.get("repo") || "",
    tag: params.get("tag") || "",
    kind: KIND_WORDS[kind] ? kind : "",
    closed: params.get("closed") === "1",
  };
}

export function applyFilters(items, options) {
  return (items || []).filter((item) => {
    const todo = item.todo || {};
    if (options.repo && item.repository !== options.repo) return false;
    if (options.kind && todo.kind !== options.kind) return false;
    if (options.tag && !(todo.tags || []).includes(options.tag)) return false;
    return true;
  });
}

export const tagsOf = (items) => [...new Set((items || []).flatMap((item) => item.todo?.tags || []))].sort();
export const kindsOf = (items) => Object.keys(KIND_WORDS).filter((kind) => (items || []).some((item) => item.todo?.kind === kind));

// "owner/name" of "github.com/owner/name" (and the host when it is not github.com).
export function repoName(key) {
  const parts = String(key || "").split("/");
  return parts[0] === "github.com" ? parts.slice(1).join("/") : parts.join("/");
}

function span(ms) {
  const minutes = Math.max(1, Math.round(Math.abs(ms) / 60000));
  if (minutes < 60) return `${minutes}分`;
  const hours = Math.floor(minutes / 60);
  if (hours < 48) return `${hours}時間`;
  return `${Math.floor(hours / 24)}日`;
}

const pad = (value) => String(value).padStart(2, "0");
export function localTime(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return `${date.getMonth() + 1}月${date.getDate()}日 ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

// The due in words: overdue says by how much (Epic R-11: color, mark and words), otherwise how long is left.
export function dueWords(due, { overdue = false, closed = false } = {}, now = Date.now()) {
  if (!due) return { text: "期限なし", tone: "" };
  const at = new Date(due).getTime();
  if (Number.isNaN(at)) return { text: String(due), tone: "" };
  if (closed) return { text: `期限 ${localTime(due)}`, tone: "" };
  if (overdue) return { text: `期限切れ（${span(now - at)}超過）`, tone: "danger" };
  const left = at - now;
  if (left <= 24 * 3600 * 1000) return { text: `あと${span(left)}（${localTime(due)}）`, tone: "warning" };
  return { text: `${localTime(due)} まで`, tone: "" };
}

// --- Safe Markdown (iss-00554 decision): everything is escaped first; then only paragraphs, bullet and numbered
// lists, fenced code, inline code, bold and http(s) links are drawn. Raw HTML never passes.
function inline(text) {
  const codes = [];
  let html = esc(text).replace(/`([^`]+)`/g, (_match, code) => {
    codes.push(`<code>${code}</code>`);
    return `\u0000${codes.length - 1}\u0000`;
  });
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)"'<>]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  html = html.replace(/(^|[^\w"'=/>;&])(https?:\/\/[^\s<>"')]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
  return html.replace(/\u0000(\d+)\u0000/g, (_match, index) => codes[Number(index)]);
}

export function safeMarkdown(source) {
  const lines = String(source ?? "").replace(/\r\n?/g, "\n").split("\n");
  const out = [];
  let paragraph = [];
  let list = null; // {tag, items}
  const flushParagraph = () => {
    if (paragraph.length) out.push(`<p>${paragraph.map(inline).join("<br>")}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (list) out.push(`<${list.tag}>${list.items.map((item) => `<li>${inline(item)}</li>`).join("")}</${list.tag}>`);
    list = null;
  };
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (/^\s*```/.test(line)) {
      flushParagraph();
      flushList();
      const code = [];
      index += 1;
      while (index < lines.length && !/^\s*```/.test(lines[index])) code.push(lines[index++]);
      out.push(`<pre><code>${esc(code.join("\n"))}</code></pre>`);
      continue;
    }
    const bullet = line.match(/^\s*[-*+]\s+(.*)$/);
    const numbered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (bullet || numbered) {
      flushParagraph();
      const tag = bullet ? "ul" : "ol";
      if (!list || list.tag !== tag) {
        flushList();
        list = { tag, items: [] };
      }
      list.items.push((bullet || numbered)[1]);
      continue;
    }
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }
    flushList();
    paragraph.push(line.replace(/^#{1,6}\s+/, ""));
  }
  flushParagraph();
  flushList();
  return out.join("");
}

// A query parameter set on a path (value "" or null removes it); embed=1 is kept as is.
export function withParam(path, name, value) {
  const url = new URL(path, "http://x");
  if (value === null || value === "" || value === false) url.searchParams.delete(name);
  else url.searchParams.set(name, value === true ? "1" : String(value));
  const query = url.searchParams.toString();
  return url.pathname + (query ? `?${query}` : "");
}
