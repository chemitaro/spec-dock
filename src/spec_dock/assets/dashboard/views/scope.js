// Scope の詳しい画面（iss-00531 D-07；Epic R-18、F-05）。見出しと、概要・依存・配下・文書・Artifact のタブ。
// ctx.scope に scopes/<ID> の JSON、ctx.data に構造が入る。選んだタブは問い合わせの tab に持つ（Epic R-17）。
import { ancestors, byRank, fmtDateTime, fmtDay, formatSize, pullRequestNotice, stateCounts, TABS, tabOf, withParam } from "./_shared/logic.js";
import {
  assuranceMark,
  card,
  changeBadge,
  chip,
  emptyState,
  esc,
  humanCount,
  humanMark,
  icon,
  kindLabel,
  legend,
  mergeBadge,
  newTabLink,
  prMark,
  progressBar,
  stateIcon,
  STATES,
} from "./_shared/parts.js";
import { repositoryPath, todoPath, todosPath } from "../core/route.js";
import { dueWords, KIND_WORDS } from "./todos/logic.js";

const DOC_INFO = {
  requirement: ["要件", "何を満たすか"],
  design: ["設計", "どう作るか"],
  plan: ["計画", "どの順で進めるか"],
  explanation: ["説明資料", "人が読む説明"],
  report: ["報告", "実装の記録"],
};

const link = (ctx, scope) =>
  `<a data-nav href="${esc(ctx.href(scope.path))}">${stateIcon(scope.state, false)}<span class="ds-docid">${esc(scope.id)}</span></a>`;

function section(n, heading, aside = "") {
  return `<h2 class="sd-sec"><span class="sd-sec__n">${n}</span>${heading}${aside ? `<span class="sd-sec__aside">${aside}</span>` : ""}</h2>`;
}

function summaryTab(ctx, scope, doc, byId) {
  const kids = (scope.children || []).map((id) => byId.get(id)).filter(Boolean);
  const counts = stateCounts(kids);
  const details = doc.details;
  const worktrees = details?.worktrees;
  let worktree;
  if (!worktrees || worktrees.status !== "ok") worktree = `<span class="sd-muted">分からない（このPCの worktree を読めなかった）</span>`;
  else if (worktrees.items.length) {
    worktree = worktrees.items.map((item) => `<span class="sd-mono">${esc(item.branch)}</span><span class="sd-muted sd-mono">${esc(item.path)}</span>`).join("<br>");
  } else worktree = `<span class="sd-muted">このPCにはない（ほかのPCの worktree は分からない）</span>`;
  const tone = scope.state === "blocked" ? "danger" : scope.state === "unknown" ? "warning" : "note";
  let body = `<div class="sd-callout" data-tone="${tone}" data-st="${esc(scope.state)}">${stateIcon(scope.state, false)}<div><p class="sd-callout__title">${esc(STATES[scope.state]?.label ?? scope.state)}</p><p>${esc(scope.reason?.text ?? "")}</p></div></div>`;
  let n = 1;
  if (kids.length) {
    body +=
      section(n++, "配下の進み具合", `${counts.done}／${kids.length} 終わった`) +
      `<div class="sd-progress">${progressBar(counts)}<ul>${["done", "doing", "ready", "blocked", "unknown"]
        .map((state) => `<li data-st="${state}">${stateIcon(state, false)}${STATES[state].label}<b>${counts[state]}</b></li>`)
        .join("")}</ul></div>`;
  }
  const rows = [
    ["作られた", esc(fmtDay(scope.created_at))],
    ...(scope.closed_at ? [["終わった", esc(fmtDay(scope.closed_at))]] : []),
    ["このPCの worktree", worktree],
    ["PR", scope.pr ? prMark(scope.pr, { words: true }) : pullRequestNotice(ctx.data)?.level === "unknown" ? `<span class="sd-muted">分からない</span>` : `<span class="sd-muted">ない</span>`],
    ["前回からの変化", scope.change ? changeBadge(scope) : `<span class="sd-muted">ない</span>`],
  ];
  body += section(n, "記録") + `<dl class="sd-kv">${rows.map(([key, value]) => `<dt>${key}</dt><dd>${value}</dd>`).join("")}</dl>`;
  return body;
}

function depsTab(ctx, scope, doc, byId) {
  const waits = doc.dependencies?.waits_for || [];
  const roots = new Set(doc.root_waits?.scope_ids || []);
  const rootExternal = new Set(doc.root_waits?.external || []);
  const row = (item) => {
    const target = item.scope_id ? byId.get(item.scope_id) : null;
    const root = (item.scope_id && roots.has(item.scope_id)) || (!item.scope_id && rootExternal.has(item.number));
    const nameHtml = target
      ? link(ctx, target) + `<span class="sd-muted">#${esc(item.number)}</span>`
      : `${stateIcon(item.open ? "unknown" : "done", false)}<span class="sd-muted">Scope でない Issue</span> #${esc(item.number)}`;
    const state = item.external ? (item.open ? "開いている" : "閉じた") : STATES[item.state]?.label ?? item.state;
    const from = item.inherited ? `<span class="sd-badge" data-tone="warning">${esc(item.declared_by)} から引き継いだ</span>` : "";
    return `<tr data-open="${item.open}"><td>${nameHtml}${root ? `<span class="sd-badge" data-tone="danger">${icon("target")}大もと</span>` : ""}</td><td>${esc(item.title ?? "")}</td><td>${esc(state)}</td><td>${from}</td></tr>`;
  };
  const own = waits.filter((item) => !item.inherited);
  const inherited = waits.filter((item) => item.inherited);
  const table = (items) =>
    items.length ? `<table class="sd-table"><thead><tr><th>待ち先</th><th>題名</th><th>状態</th><th></th></tr></thead><tbody>${items.map(row).join("")}</tbody></table>` : `<p class="sd-col__empty">ない</p>`;
  const open = waits.filter((item) => item.open).length;
  const waitedBy = (doc.dependencies?.waited_by || []).map((id) => byId.get(id)).filter(Boolean).sort(byRank);
  const indirect = doc.downstream?.indirect?.length || 0;
  // Roots reached only through other Scopes (e.g. an open child of an Epic this Scope waits for) are not rows of
  // waits_for; list them separately so the mark always has a place to stand (Epic R-18).
  const listed = new Set(waits.map((item) => item.scope_id ?? `#${item.number}`));
  const deepRoots = [
    ...[...roots].filter((id) => !listed.has(id)).map((id) => byId.get(id)).filter(Boolean).sort(byRank).map((item) => `<li>${link(ctx, item)} <span>${esc(item.title)}</span> <span class="sd-muted">${esc(STATES[item.state]?.label ?? item.state)}</span></li>`),
    ...[...rootExternal].filter((number) => !listed.has(`#${number}`)).map((number) => `<li>${stateIcon("unknown", false)}<span class="sd-muted">Scope でない Issue</span> #${esc(number)}</li>`),
  ];
  return (
    section(1, "この Scope が待つもの", `${open}件が未完了`) +
    (scope.state === "blocked" && roots.size + rootExternal.size ? `<p class="sd-note">${icon("target")}「大もと」は、上流の端で止められていない待ち先。そこから進めると、この Scope が動き出す。</p>` : "") +
    (deepRoots.length ? `<h3 class="sd-sub">${icon("target")}間接の大もとの待ち先（ここから進めると動き出す）</h3><ul class="sd-list" data-code="deep-roots">${deepRoots.join("")}</ul>` : "") +
    `<h3 class="sd-sub">自分で持つ依存</h3>${table(own)}` +
    `<h3 class="sd-sub">親から引き継いだ依存</h3>${table(inherited)}` +
    section(2, "この Scope を待つもの", `直接 ${waitedBy.length}件・間接 ${indirect}件`) +
    (waitedBy.length ? `<div class="sd-lane">${waitedBy.map((item) => card(item, ctx)).join("")}</div>` : `<p class="sd-col__empty">直接に待つものはない</p>`) +
    (indirect ? `<p class="sd-muted">ほかに、間接に後に続く開いた Scope が ${indirect}件ある。</p>` : "")
  );
}

function childrenTab(ctx, scope, doc, byId, showDone) {
  const kids = (scope.children || []).map((id) => byId.get(id)).filter(Boolean);
  if (!kids.length) return emptyState("配下はない。");
  // Stages from open children and open waits only (open_child_stages), so one stage really can run in parallel.
  const stageMap = doc.open_child_stages || doc.child_stages || { stages: [], external: [], cyclic: [] };
  const closedKids = kids.filter((item) => item.state === "done").sort((a, b) => (b.closed_at || "").localeCompare(a.closed_at || ""));
  const shownClosed = closedKids.filter((item) => showDone || item.keep_visible);
  const hidden = closedKids.length - shownClosed.length;
  const toggle = `<a class="sd-toggle" role="switch" aria-checked="${showDone}" data-nav href="${esc(ctx.href(withParam(ctx.route.path, "done", !showDone)))}"><span class="sd-toggle__box">${showDone ? icon("check") : ""}</span>終わったものも示す</a>`;
  const stages = stageMap.stages
    .map((ids) => ids.map((id) => byId.get(id)).filter((item) => item && item.state !== "done").sort(byRank))
    .filter((items) => items.length);
  const done = closedKids.length
    ? section(icon("check"), "終わった配下", `${closedKids.length}件`) +
      (shownClosed.length ? `<div class="sd-lane">${shownClosed.map((item) => card(item, ctx)).join("")}</div>` : "") +
      (hidden ? `<p class="sd-muted">終わった ${hidden}件を隠している（「終わったものも示す」で札を出す）。</p>` : "")
    : "";
  const rows = stages
    .map(
      (items, index) =>
        `${index ? `<div class="sd-stage-arrow">${icon("arrowDown")}</div>` : ""}<div class="sd-stage" data-stage="${index + 1}"><div class="sd-stage__n"><b>${index + 1}</b>段${index + 1}</div><div class="sd-lane">${items.map((item) => card(item, ctx)).join("")}</div></div>`,
    )
    .join("");
  const external = stageMap.external.length
    ? section("外", "この Scope の外への依存") +
      `<ul class="sd-list">${stageMap.external
        .map(({ child, number }) => {
          const owner = byId.get(child);
          const target = [...byId.values()].find((item) => item.number === number);
          return `<li>${owner ? link(ctx, owner) : esc(child)} ${icon("arrowRight")} ${target ? link(ctx, target) : `#${esc(number)}`}</li>`;
        })
        .join("")}</ul>`
    : "";
  const cyclic = stageMap.cyclic.length
    ? `<div class="sd-callout" data-tone="warning">${stateIcon("unknown", false)}<p>依存が循環していて段に入れられない：${stageMap.cyclic.map((id) => (byId.get(id) ? link(ctx, byId.get(id)) : esc(id))).join("、")}</p></div>`
    : "";
  return (
    `<div class="sd-ctl">${toggle}${hidden ? `<span class="sd-muted">終わった ${hidden}件を隠している</span>` : ""}</div>` +
    `<p class="sd-note">${icon("info")}配下どうしの依存（子孫どうしの依存も数える）で段に分ける。段1 から順に進め、同じ段のものは並べて進められる。</p>` +
    (rows ? `<div class="sd-stages">${rows}</div>` : `<p class="sd-col__empty">示す配下はない</p>`) +
    cyclic +
    external +
    done
  );
}

function catalogProblem(details) {
  const text =
    details?.catalog === "ambiguous"
      ? "このリポジトリのクローンが2つ登録されていて、カタログを選べません。"
      : details?.catalog === "scope_missing"
        ? "カタログに、この Scope のディレクトリがありません。"
        : details
          ? "カタログがありません（リンクがないか、作られていない）。"
          : "カタログを読めませんでした。";
  const steps = details?.next_steps?.length ? details.next_steps : ["spec-dock canonical link", "spec-dock canonical status"];
  return `<div class="sd-callout" data-tone="warning" data-code="catalog-${esc(details?.catalog ?? "unreadable")}">${icon("book")}<div><p class="sd-callout__title">${esc(text)}</p><p>次の1手：${steps.map((step) => `<code>${esc(step)}</code>`).join("、")}</p></div></div>`;
}

function docsTab(doc) {
  const details = doc.details;
  if (!details || details.catalog !== "ok") return catalogProblem(details);
  return `<div class="sd-docs">${details.documents
    .map((item) => {
      const [label, note] = DOC_INFO[item.key] ?? [item.key, ""];
      const open = item.href
        ? `<a href="${esc(item.href)}" target="_blank" rel="noopener">${icon("external")}新しいタブで開く</a>`
        : item.exists
          ? `<span class="sd-muted">ある（文書の画面は 0.7.0）</span>`
          : `<span class="sd-muted">まだない</span>`;
      return `<div class="sd-doc" data-has="${item.exists}"><div class="sd-doc__head"><span class="sd-doc__icon">${icon(item.key === "explanation" ? "book" : "file")}</span><div><p class="sd-doc__title">${esc(label)}</p><p class="sd-mono">${esc(item.name)}</p></div></div><p>${esc(note)}</p><p>${open}</p></div>`;
    })
    .join("")}</div>`;
}

function artifactsTab(doc) {
  const details = doc.details;
  if (!details || details.catalog !== "ok") return catalogProblem(details);
  if (!details.artifacts.length) return emptyState("Artifact はまだない。試作や調べた結果をこの Scope に結び付けると、ここに並ぶ。");
  return (
    `<div class="sd-table-wrap"><table class="sd-table"><thead><tr><th>名前</th><th>形式</th><th>大きさ</th><th>更新</th></tr></thead><tbody>${details.artifacts
      .map(
        (item) =>
          `<tr><td><a class="sd-mono" href="${esc(item.href)}" target="_blank" rel="noopener">${esc(item.name)}</a></td><td>${item.html ? "HTML（切り離して開く）" : esc(item.name.split(".").pop() ?? "")}</td><td>${esc(formatSize(item.size))}</td><td>${esc(fmtDateTime(item.modified_at))}</td></tr>`,
      )
      .join("")}</tbody></table></div>` + (details.artifacts_truncated ? `<p class="sd-muted">多いので、最初の ${details.artifacts.length}件だけを示す。</p>` : "")
  );
}

// The human tasks tab (iss-00554 D-06; Epic R-13): blocking it, blocking only a Scope below it, and related.
function todosTab(ctx, scope, doc) {
  const todos = doc.todos;
  if (!todos || todos.status !== "ok") {
    const problem = todos?.problem;
    return `<div class="sd-callout" data-tone="warning" data-code="todos-unavailable">${icon("person")}<div><p class="sd-callout__title">人のタスクが読めない</p><p>${esc(problem?.message ?? "このリポジトリのカタログの人のタスクを読めませんでした。")}${problem?.next_step ? ` 次の1手：<code>${esc(problem.next_step)}</code>` : ""}</p></div></div>`;
  }
  const table = (items, withBlocks) =>
    items.length
      ? `<div class="sd-table-wrap"><table class="sd-table" data-todos><thead><tr><th>人のタスク</th><th>期限</th><th>種類</th>${withBlocks ? "<th>止めている Scope</th>" : ""}</tr></thead><tbody>${items
          .map((item) => {
            const due = dueWords(item.due, { overdue: item.overdue });
            const blocks = withBlocks ? `<td>${(item.blocks || []).map((target) => `<span class="ds-docid">${esc(target)}</span>`).join(" ")}</td>` : "";
            return `<tr data-overdue="${item.overdue ? 1 : 0}"><td><a data-nav href="${esc(ctx.href(todoPath(item.repository, item.id)))}"><span class="ds-docid">${esc(item.id)}</span>${esc(item.title)}</a></td><td><span class="sd-due" data-tone="${due.tone}">${icon(due.tone === "danger" ? "alert" : "clock")}${esc(due.text)}</span></td><td>${esc(KIND_WORDS[item.kind] ?? item.kind ?? "")}</td>${blocks}</tr>`;
          })
          .join("")}</tbody></table></div>`
      : `<p class="sd-col__empty">ない</p>`;
  const parent = scope.kind !== "issue";
  return (
    section(1, "この Scope を止めている人のタスク", `${todos.blocking.length}件`) +
    table(todos.blocking, false) +
    (parent ? section(2, "配下の Scope を止めている人のタスク", `${todos.descendants.length}件`) + table(todos.descendants, true) : "") +
    section(parent ? 3 : 2, "関係する人のタスク", `${todos.related.length}件`) +
    table(todos.related, true) +
    `<p class="sd-note">${icon("info")}人のタスクは Scope の状態を変えない（印だけ）。登録と完了は CLI（<code>spec-dock todo</code>）で行う。<a data-nav href="${esc(ctx.href(todosPath(ctx.repository)))}">このリポジトリの人のタスク</a></p>`
  );
}

function humanTag(scope, ctx, path) {
  const { count, descendants } = humanCount(scope);
  return count ? `<a class="sd-hm-link" data-nav href="${esc(ctx.href(withParam(path, "tab", "todos")))}">${humanMark(count, { descendants, cls: "sd-hm" })}</a>` : "";
}

function render(root, ctx) {
  const id = ctx.route.scope;
  const byId = new Map((ctx.data?.scopes || []).map((item) => [item.id, item]));
  const back = `<a class="sd-back" data-nav href="${esc(ctx.href(repositoryPath(ctx.repository, "board")))}">${icon("chevronLeft")}ボードへ戻る</a>`;
  const doc = ctx.scope;
  if (!doc || doc.scope?.id !== id) {
    const known = byId.has(id);
    const text = !ctx.data
      ? "構造を読めませんでした。上の知らせの次の1手を確かめてください。"
      : known
        ? `${id} の詳しい内容を読めませんでした。少し待って開き直してください。`
        : `${id} は、このリポジトリの構造にありません（消されたか、ID の誤り）。`;
    root.innerHTML = `<div class="sd-page">${newTabLink(ctx)}${back}${emptyState(text)}</div>`;
    return;
  }
  const scope = { ...(byId.get(id) || {}), ...doc.scope };
  const tab = tabOf(ctx.route.params);
  const showDone = ctx.route.params.get("done") === "1";
  const path = ctx.route.path;
  const chain = ancestors(byId, scope);
  const pathHtml = chain.length
    ? `<nav class="sd-path" aria-label="親の道筋">${chain.map((item) => `<a data-nav href="${esc(ctx.href(item.path))}" title="${esc(item.title)}">${esc(item.id)}</a>${icon("chevronRight")}`).join("")}<span>${esc(scope.id)}</span></nav>`
    : `<span class="sd-muted">最上位</span>`;
  const assurance = doc.details?.assurance;
  const assuranceHtml =
    assurance?.level ? `${assuranceMark(assurance.level)}${esc(assurance.level)}` : assurance?.source === "unset"
        ? `<span class="sd-muted">なし（Markdown の Scope）</span>`
        : doc.details && doc.details.catalog !== "ok"
          ? `<span class="sd-muted">分からない（カタログにこの Scope がない）</span>`
          : `<span class="sd-muted">分からない（requirement.cue を読めない）</span>`;
  const prNotice = pullRequestNotice(ctx.data);
  const prHtml = scope.pr
    ? `${prMark(scope.pr)}<a href="${esc(scope.pr.url)}" target="_blank" rel="noopener">#${esc(scope.pr.number)}</a>`
    : prNotice?.level === "unknown"
      ? `<span class="sd-muted">分からない</span>`
      : `<span class="sd-muted">ない</span>`;
  const branches = doc.details?.worktrees?.status === "ok" ? doc.details.worktrees.items.map((item) => item.branch) : [];
  const todoCount = doc.todos?.status === "ok" ? doc.todos.blocking.length + doc.todos.descendants.length + doc.todos.related.length : null;
  const counts = { deps: (doc.dependencies?.waits_for?.length || 0) + (doc.dependencies?.waited_by?.length || 0), children: (scope.children || []).length, artifacts: doc.details?.artifacts?.length, todos: todoCount };
  const tabs = TABS.map(
    ([key, label]) =>
      `<a class="sd-tab" role="tab" data-nav href="${esc(ctx.href(withParam(path, "tab", key === "summary" ? null : key)))}" aria-selected="${tab === key}">${label}${counts[key] != null ? `<small>${counts[key]}</small>` : ""}</a>`,
  ).join("");
  let body;
  if (tab === "deps") body = depsTab(ctx, scope, doc, byId);
  else if (tab === "children") body = childrenTab(ctx, scope, doc, byId, showDone);
  else if (tab === "docs") body = docsTab(doc);
  else if (tab === "artifacts") body = artifactsTab(doc);
  else if (tab === "todos") body = todosTab(ctx, scope, doc);
  else body = summaryTab(ctx, scope, doc, byId);
  root.innerHTML =
    `<div class="sd-page">${newTabLink(ctx)}${back}` +
    `<header class="sd-cover" data-st="${esc(scope.state)}"><div class="sd-cover__main">` +
    `<p class="sd-cover__kicker">${esc(kindLabel(scope.kind))}<span class="ds-docid">${esc(scope.id)}</span><span class="sd-no">#${esc(scope.number)}</span></p>` +
    `<h1 class="sd-cover__title">${esc(scope.title)}</h1>` +
    `<div class="sd-cover__tags">${chip(scope.state)}<span class="sd-badge" data-tone="${scope.state === "blocked" ? "danger" : scope.state === "unknown" ? "warning" : "accent"}">${esc(scope.reason?.text ?? "")}</span>${mergeBadge(scope)}${changeBadge(scope)}${humanTag(scope, ctx, path)}</div>` +
    `</div><div class="sd-cover__side"><dl>` +
    `<dt>親の道筋</dt><dd>${pathHtml}</dd>` +
    `<dt>保証レベル</dt><dd>${assuranceHtml}</dd>` +
    `<dt>GitHub</dt><dd>${scope.url ? `<a href="${esc(scope.url)}" target="_blank" rel="noopener">${icon("external")}Issue #${esc(scope.number)}</a>` : ""}</dd>` +
    `<dt>PR</dt><dd>${prHtml}</dd>` +
    (branches.length ? `<dt>ブランチ</dt><dd>${branches.map((branch) => `<span class="sd-mono">${esc(branch)}</span>`).join(" ")}</dd>` : "") +
    `</dl></div></header>` +
    `<div class="sd-tabs-row"><nav class="sd-tabs" role="tablist" aria-label="詳しい画面のタブ">${tabs}</nav>${legend()}</div>` +
    `<div class="sd-tabpanel" role="tabpanel" data-tab="${tab}">${body}</div></div>`;
}

export default {
  id: "scope",
  title: "詳しい画面",
  icon: "info",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/scope.css"],
  render,
};
