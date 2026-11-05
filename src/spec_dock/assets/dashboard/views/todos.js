// 人のタスクの画面（iss-00554 D-05；Epic D-16、R-12）。`/todos` は表示中の全リポジトリ（横断の概況と同じ層）、
// `/r/<repo>/todos` はそのリポジトリ、`/r/<repo>/todos/<ID>` は1件。見るだけで、登録・完了・延期の口も、写せる
// コマンドも置かない（epic-00427 R-04）。並びと状態はサーバー（`specdock.todo-list/v1` の derived と並び）を写す。
import * as api from "../core/api.js";
import { esc, ic } from "../core/ui.js";
import { scopePath, todoPath, todosPath } from "../core/route.js";
import { emptyState, newTabLink } from "./_shared/parts.js";
import {
  ACTION_WORDS,
  KIND_WORDS,
  STATUS_WORDS,
  applyFilters,
  dueWords,
  groupItems,
  kindsOf,
  localTime,
  repoName,
  safeMarkdown,
  tagsOf,
  todoOptions,
  withParam,
} from "./todos/logic.js";

const REFRESH_MS = 5000;

const S = {
  key: null, // what is loaded: "<repo or *>|<status>|<todo id>"
  doc: null, // the list document or the one task
  error: null,
  revision: null, // the revision the document was read at
  loading: null,
  timer: null,
  mounted: null, // {root, ctx}
};

const statusOf = (options) => (options.closed ? "all" : "open");

function keyOf(ctx) {
  return `${ctx.repository || "*"}|${statusOf(todoOptions(ctx.route.params))}|${ctx.route.todo || ""}`;
}

async function load(ctx, key) {
  const repo = ctx.repository;
  const status = statusOf(todoOptions(ctx.route.params));
  try {
    const doc = ctx.route.todo ? await api.todo(repo, ctx.route.todo) : repo ? await api.repositoryTodos(repo, status) : await api.todos(status);
    if (S.key !== key) return;
    S.doc = doc;
    S.error = null;
  } catch (error) {
    if (S.key !== key) return;
    S.doc = null;
    S.error = { message: error.message, code: error.body?.error?.code, status: error.status, next: error.body?.error?.next_steps || [] };
  }
  if (S.mounted) draw(S.mounted.root, S.mounted.ctx);
}

function reload(ctx, key) {
  S.loading = load(ctx, key).finally(() => {
    S.loading = null;
  });
  return S.loading;
}

// Every repository's screen watches the combined revision itself; a repository's screens follow the shell's.
async function tick() {
  const mounted = S.mounted;
  if (!mounted || document.hidden || S.loading || mounted.ctx.repository) return;
  try {
    const { revision } = await api.todosRevision();
    if (revision !== S.revision) {
      S.revision = revision;
      await reload(mounted.ctx, S.key);
    }
  } catch {
    // keep the last list; the next tick tries again
  }
}

// --- Parts ---------------------------------------------------------------------------------------------------

const kindBadge = (kind) => `<span class="sd-badge" data-kind="${esc(kind)}">${esc(KIND_WORDS[kind] ?? kind ?? "")}</span>`;

function dueBadge(todo, derived) {
  const closed = todo.status === "done" || todo.status === "cancelled";
  const { text, tone } = dueWords(todo.due, { overdue: derived?.overdue, closed });
  const mark = tone === "danger" ? ic("alert") : ic("clock");
  return `<span class="td-due" data-tone="${tone}">${mark}<span>${esc(text)}</span></span>`;
}

const scopeLink = (ctx, repository, scopeId) =>
  repository
    ? `<a class="ds-docid" data-nav href="${esc(ctx.href(scopePath(repository, scopeId)))}">${esc(scopeId)}</a>`
    : `<span class="ds-docid">${esc(scopeId)}</span>`;

function card(item, ctx, showRepo) {
  const todo = item.todo || {};
  const derived = item.derived || {};
  const blocks = todo.scopes?.blocks || [];
  const counts = derived.subtask_counts || { open: 0, total: 0 };
  const meta = [];
  if (showRepo) meta.push(`<span class="td-repo">${ic("folder")}${esc(repoName(item.repository))}</span>`);
  if (blocks.length) meta.push(`<span class="td-blocks" title="これが終わるまで進められない Scope">${ic("person")}止める ${blocks.map((id) => `<span class="ds-docid">${esc(id)}</span>`).join(" ")}</span>`);
  if (counts.total) meta.push(`<span>${ic("check")}残り ${esc(counts.open)}／${esc(counts.total)}</span>`);
  for (const tag of todo.tags || []) meta.push(`<span class="td-tag">#${esc(tag)}</span>`);
  const state = todo.status !== "open" ? `<span class="sd-badge">${esc(STATUS_WORDS[derived.effective_status] ?? STATUS_WORDS[todo.status] ?? todo.status)}</span>` : "";
  return (
    `<a class="td-card" data-nav data-overdue="${derived.overdue ? 1 : 0}" data-status="${esc(todo.status)}" data-id="${esc(todo.id)}" href="${esc(ctx.href(todoPath(item.repository, todo.id)))}">` +
    `<span class="td-card__r1">${kindBadge(todo.kind)}<span class="ds-docid">${esc(todo.id)}</span>${state}${dueBadge(todo, derived)}</span>` +
    `<span class="td-card__ttl">${esc(todo.title)}</span>` +
    (meta.length ? `<span class="td-card__meta">${meta.join("")}</span>` : "") +
    `</a>`
  );
}

function rowProblems(rows) {
  const notes = [];
  for (const row of rows || []) {
    const name = esc(repoName(row.repository));
    if (row.status === "unreadable") {
      notes.push(
        `<div class="sd-callout" data-tone="warning" data-code="todos-unreadable">${ic("alert")}<div><p class="sd-callout__title">${name}：人のタスクが読めない</p><p>${esc(row.problem?.message ?? "")}${row.problem?.next_step ? ` 次の1手：<code>${esc(row.problem.next_step)}</code>` : ""}</p></div></div>`,
      );
    }
    const broken = [...(row.invalid_files || []), ...(row.conflict_copies || [])];
    if (broken.length) {
      notes.push(
        `<div class="sd-callout" data-tone="warning" data-code="todos-invalid">${ic("alert")}<div><p class="sd-callout__title">${name}：読めない記録・衝突の写し ${broken.length}件（一覧に入れていない）</p><p>${broken.map((path) => `<code>${esc(path)}</code>`).join("、")} 次の1手：<code>spec-dock todo check</code></p></div></div>`,
      );
    }
  }
  return notes.join("");
}

function controls(ctx, items, rows, options) {
  const path = ctx.route.path;
  const link = (name, value, label, on) => `<a role="button" data-nav href="${esc(ctx.href(withParam(path, name, on ? null : value)))}" aria-pressed="${on}">${label}</a>`;
  const repos = ctx.repository ? [] : (rows || []).map((row) => row.repository).filter(Boolean);
  const repoSeg = repos.length > 1
    ? `<span class="sd-seg" role="group" aria-label="リポジトリ"><a role="button" data-nav href="${esc(ctx.href(withParam(path, "repo", null)))}" aria-pressed="${!options.repo}">すべて</a>${repos.map((repo) => link("repo", repo, esc(repoName(repo)), options.repo === repo)).join("")}</span>`
    : "";
  const kinds = kindsOf(items);
  const kindSeg = kinds.length > 1 || options.kind
    ? `<span class="sd-seg" role="group" aria-label="種類"><a role="button" data-nav href="${esc(ctx.href(withParam(path, "kind", null)))}" aria-pressed="${!options.kind}">すべて</a>${kinds.map((kind) => link("kind", kind, esc(KIND_WORDS[kind]), options.kind === kind)).join("")}</span>`
    : "";
  const tags = tagsOf(items);
  const tagList = tags.length
    ? `<span class="td-tags" role="group" aria-label="タグ">${tags.map((tag) => link("tag", tag, `#${esc(tag)}`, options.tag === tag)).join("")}</span>`
    : "";
  const toggle = `<a class="sd-toggle" role="switch" aria-checked="${options.closed}" data-nav href="${esc(ctx.href(withParam(path, "closed", !options.closed)))}"><span class="sd-toggle__box">${options.closed ? ic("check") : ""}</span>延期中と閉じたものも</a>`;
  return `<div class="sd-ctl">${repoSeg}${kindSeg}${tagList}${toggle}</div>`;
}

function listView(ctx) {
  const doc = S.doc;
  const options = todoOptions(ctx.route.params);
  const all = doc.items || [];
  const shown = applyFilters(all, options);
  const groups = groupItems(shown);
  const overdue = shown.filter((item) => item.derived?.overdue).length;
  const open = shown.filter((item) => item.todo?.status === "open" || item.todo?.status === "snoozed").length;
  const heading = ctx.repository ? "人のタスク" : "人のタスク（すべてのリポジトリ）";
  const lead = ctx.repository
    ? `${esc(repoName(ctx.repository))} の人のタスク。`
    : `このPCで表示しているリポジトリ ${esc((doc.repositories || []).length)}件の人のタスク。`;
  const other = ctx.repository ? `<a data-nav href="${esc(ctx.href(todosPath(null)))}">${ic("globe")}すべてのリポジトリ</a>` : "";
  const body = groups.length
    ? groups
        .map(
          (group) =>
            `<section class="td-group" data-group="${esc(group.key)}" aria-label="${esc(group.label)}"><h2 class="td-group__head">${group.key === "overdue" ? ic("alert") : ""}${esc(group.label)}<b>${group.items.length}</b><small>${esc(group.note)}</small></h2>` +
            `<div class="td-list">${group.items.map((item) => card(item, ctx, !ctx.repository)).join("")}</div></section>`,
        )
        .join("")
    : emptyState(all.length ? "絞り込みに合う人のタスクはない。" : "開いている人のタスクはない。");
  return (
    `<div class="sd-page-head"><h1>${heading}</h1><p>${lead}開いている ${open}件${overdue ? `・<b class="td-overdue-count">期限切れ ${overdue}件</b>` : ""}。登録と完了は CLI（<code>spec-dock todo</code>）で行う（この画面は見るだけ）。</p>${other ? `<p>${other}</p>` : ""}</div>` +
    rowProblems(doc.repositories) +
    controls(ctx, all, doc.repositories, options) +
    body
  );
}

function kv(rows) {
  return `<dl class="sd-kv td-kv">${rows.filter(Boolean).map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`).join("")}</dl>`;
}

function oneView(ctx) {
  const view = S.doc;
  const todo = view.todo || {};
  const derived = view.derived || {};
  const repo = view.repository || ctx.repository;
  const closed = todo.status === "done" || todo.status === "cancelled";
  const blocks = todo.scopes?.blocks || [];
  const related = todo.scopes?.related || [];
  const origin = todo.origin || {};
  const options = (todo.options || [])
    .map((option) => {
      const recommended = todo.recommendation?.key === option.key;
      const chosen = todo.resolution?.choice === option.key;
      return `<li data-recommended="${recommended ? 1 : 0}"><span class="ds-docid">${esc(option.key)}</span><span>${esc(option.text)}</span>${recommended ? `<span class="sd-badge" data-tone="accent">${ic("sparkle")}推奨</span>` : ""}${chosen ? `<span class="sd-badge" data-tone="ok">${ic("check")}選んだ</span>` : ""}</li>`;
    })
    .join("");
  const subtasks = (todo.subtasks || [])
    .map((item) => `<li data-status="${esc(item.status)}">${item.status === "open" ? `<span class="td-box"></span>` : `<span class="td-box" data-done="1">${ic("check")}</span>`}<span class="ds-docid">${esc(item.id)}</span><span>${esc(item.title)}</span>${item.status === "cancelled" ? `<span class="sd-badge">取り消し</span>` : ""}</li>`)
    .join("");
  const history = (todo.history || [])
    .slice()
    .reverse()
    .map((entry) => `<li><span class="sd-muted">${esc(localTime(entry.at))}</span><b>${esc(ACTION_WORDS[entry.action] ?? entry.action)}</b>${entry.target ? `<span class="ds-docid">${esc(entry.target)}</span>` : ""}<span class="sd-muted">${esc(entry.by ?? "")}${entry.role ? `（${esc(entry.role)}）` : ""}</span>${entry.note ? `<span>${esc(entry.note)}</span>` : ""}${entry.fields?.length ? `<span class="sd-muted">${esc(entry.fields.join("、"))}</span>` : ""}</li>`)
    .join("");
  const resolution = todo.resolution;
  const record = resolution?.record
    ? /^https?:\/\//.test(resolution.record)
      ? `<a href="${esc(resolution.record)}" target="_blank" rel="noopener noreferrer">${ic("external")}${esc(resolution.record)}</a>`
      : `<span class="sd-mono">${esc(resolution.record)}</span>`
    : "";
  const links = (todo.links || [])
    .map((url) => (/^https?:\/\//.test(url) ? `<li><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${ic("external")}${esc(url)}</a></li>` : `<li class="sd-mono">${esc(url)}</li>`))
    .join("");
  const state = STATUS_WORDS[derived.effective_status] ?? STATUS_WORDS[todo.status] ?? todo.status;
  const back = `<a class="sd-back" data-nav href="${esc(ctx.href(todosPath(repo)))}">${ic("chevronLeft")}人のタスクの一覧へ</a>`;
  return (
    back +
    `<header class="td-cover" data-overdue="${derived.overdue ? 1 : 0}" data-status="${esc(todo.status)}">` +
    `<p class="td-cover__kicker">${kindBadge(todo.kind)}<span class="ds-docid">${esc(todo.id)}</span><span class="sd-muted">${esc(repoName(repo))}</span></p>` +
    `<h1 class="td-cover__title">${esc(todo.title)}</h1>` +
    `<div class="td-cover__tags"><span class="sd-badge" data-tone="${closed ? "" : "accent"}">${esc(state)}</span>${dueBadge(todo, derived)}${derived.blocking ? `<span class="sd-badge" data-tone="blocked">${ic("person")}Scope を止めている</span>` : ""}${derived.parent_closable ? `<span class="sd-badge" data-tone="ok">${ic("check")}サブタスクがすべて終わった</span>` : ""}</div>` +
    `</header>` +
    kv([
      ["種類", esc(KIND_WORDS[todo.kind] ?? todo.kind ?? "")],
      ["状態", esc(state) + (todo.status === "snoozed" && todo.snooze_until ? `<span class="sd-muted">（${esc(localTime(todo.snooze_until))} まで）</span>` : "")],
      ["期限", dueBadge(todo, derived)],
      ["依頼者", `${esc(origin.by === "agent" ? "エージェント" : "人")}${origin.role ? `<span class="sd-muted">（${esc(origin.role)}）</span>` : ""}`],
      ["作られた", esc(localTime(todo.created_at))],
      todo.effort ? ["見込み", esc(todo.effort)] : null,
      todo.reply_to ? ["答える場所", esc(todo.reply_to)] : null,
      ["止めている Scope", blocks.length ? blocks.map((id) => scopeLink(ctx, repo, id)).join(" ") : `<span class="sd-muted">ない</span>`],
      ["関係する Scope", related.length ? related.map((id) => scopeLink(ctx, repo, id)).join(" ") : `<span class="sd-muted">ない</span>`],
      todo.tags?.length ? ["タグ", todo.tags.map((tag) => `<span class="td-tag">#${esc(tag)}</span>`).join(" ")] : null,
    ]) +
    (todo.body ? `<h2 class="sd-sec">${ic("file")}本文</h2><div class="td-body">${safeMarkdown(todo.body)}</div>` : "") +
    (options ? `<h2 class="sd-sec">${ic("question")}選択肢</h2><ul class="td-options">${options}</ul>${todo.recommendation?.reason ? `<p class="sd-note">${ic("sparkle")}推奨の理由：${esc(todo.recommendation.reason)}</p>` : ""}` : "") +
    (subtasks ? `<h2 class="sd-sec">${ic("check")}サブタスク<span class="sd-sec__aside">残り ${esc(derived.subtask_counts?.open ?? 0)}／${esc(derived.subtask_counts?.total ?? 0)}</span></h2><ul class="td-subtasks">${subtasks}</ul>` : "") +
    (resolution
      ? `<h2 class="sd-sec">${ic("checkCircle")}答え</h2>${kv([
          ["閉じた", esc(localTime(resolution.at))],
          resolution.choice ? ["選んだもの", `<span class="ds-docid">${esc(resolution.choice)}</span>`] : null,
          resolution.note ? ["メモ", esc(resolution.note)] : null,
          record ? ["原文の記録", record] : null,
          ["閉じた人", `${esc(resolution.by ?? "")}${resolution.role ? `（${esc(resolution.role)}）` : ""}`],
        ])}`
      : "") +
    (links ? `<h2 class="sd-sec">${ic("link")}リンク</h2><ul class="td-links">${links}</ul>` : "") +
    (history ? `<h2 class="sd-sec">${ic("history")}経緯</h2><ul class="td-history">${history}</ul>` : "") +
    `<p class="sd-note">${ic("info")}この画面は見るだけ。答えや完了は CLI（<code>spec-dock todo</code>）で記録する。</p>`
  );
}

function errorView(ctx) {
  const error = S.error;
  const why = error.message; // plain text: emptyState() escapes it
  const text = ctx.route.todo
    ? error.status === 404
      ? `${ctx.route.todo} は、このリポジトリの人のタスクにありません（消されたか、ID の誤り）。`
      : `${ctx.route.todo} を読めませんでした（${why}）。`
    : `人のタスクを読めませんでした（${why}）。`;
  const next = error.next?.length ? `<p class="sd-note">次の1手：${error.next.map((step) => `<code>${esc(step)}</code>`).join("、")}</p>` : "";
  const back = ctx.route.todo ? `<a class="sd-back" data-nav href="${esc(ctx.href(todosPath(ctx.repository)))}">${ic("chevronLeft")}人のタスクの一覧へ</a>` : "";
  return back + emptyState(text) + next;
}

function draw(root, ctx) {
  let body;
  if (S.error) body = errorView(ctx);
  else if (!S.doc) body = `<p class="sd-muted" aria-busy="true">読み込んでいます…</p>`;
  else body = ctx.route.todo ? oneView(ctx) : listView(ctx);
  const scrollTop = root.scrollTop;
  root.innerHTML = `<div class="sd-page td-page">${newTabLink(ctx)}${body}</div>`;
  root.scrollTop = scrollTop;
}

function render(root, ctx) {
  S.mounted = { root, ctx };
  const key = keyOf(ctx);
  const revision = ctx.repository ? ctx.data?.revision ?? null : S.revision;
  if (key !== S.key) {
    S.key = key;
    S.doc = null;
    S.error = null;
    S.revision = revision;
    reload(ctx, key);
  } else if (ctx.repository && revision !== S.revision) {
    S.revision = revision; // the shell saw a new revision (a task written by the CLI, iss-00554 R-07)
    reload(ctx, key);
  }
  draw(root, ctx);
  if (!S.timer) S.timer = setInterval(tick, REFRESH_MS);
}

export default {
  id: "todos",
  title: "人のタスク",
  icon: "person",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/todos.css"],
  render,
  dispose() {
    clearInterval(S.timer);
    Object.assign(S, { key: null, doc: null, error: null, revision: null, timer: null, mounted: null });
  },
};

