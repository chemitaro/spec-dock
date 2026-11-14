// The tabs of a Scope, shared by the detail screen and the panel (iss-00587 D-03, D-04; R-09).
// Every tab is one row of SCOPE_TABS (key, label, count, render); a new tab is one more row. A tab draws from an
// env only: the shell's ctx, the Scope, its scopes/<ID> JSON and the structure's byId, plus param/paramLink for the
// choices inside a tab (the page keeps them in the query; the panel keeps them in its own Map) and keep, which
// records a choice the screen made by itself without a new history entry (iss-00593 D-02). A tab with visible(env)
// shows only when it says so; the others always show.
import { byRank, fmtDateTime, fmtDay, formatSize, pullRequestNotice, stateCounts, withoutEmbed, withParam } from "./logic.js";
import { card, changeBadge, emptyState, esc, icon, idleText, prMark, progressBar, scopesOf, stateIcon, stateMark, STATES } from "./parts.js";
import { explanationState } from "./panel_logic.js";
import { todoPath, todosPath } from "../../core/route.js";
import { dueWords, KIND_WORDS } from "../todos/logic.js";
import { agentsCount, agentsTab, agentsVisible } from "./agents_tab.js";

// The names of the documents the docs tab offers (iss-00589 D-01). The explanation has its own tab.
const DOC_INFO = { spec: "仕様", requirement: "要件", design: "設計", plan: "計画", report: "報告", adr: "ADR" };
// The document frame runs each page in an opaque origin, like the server's own sandbox header (iss-00535 F-02).
const FRAME_SANDBOX = "allow-scripts allow-popups";

// A link to a Scope carries data-id so the panel shows it in place (iss-00587 D-03).
export const link = (ctx, scope) =>
  `<a data-nav data-id="${esc(scope.id)}" href="${esc(ctx.href(scope.path))}">${stateMark(scope, scopesOf(ctx.data), { label: false })}<span class="ds-docid">${esc(scope.id)}</span></a>`;

// "N分動きなし" on the cover of a Scope in progress that has not moved for 30 minutes (iss-00574 R-05).
export function idleBadge(scope, byId) {
  const idle = idleText(scope, byId);
  return idle ? `<span class="sd-badge sd-idle">${icon("clock")}${esc(idle)}</span>` : "";
}

function section(n, heading, aside = "") {
  return `<h2 class="sd-sec"><span class="sd-sec__n">${n}</span>${heading}${aside ? `<span class="sd-sec__aside">${aside}</span>` : ""}</h2>`;
}

// The plan progress of a CUE Scope (iss-00535 R-04): done / total without dropped, and the steps in progress.
function planProgress(progress) {
  if (!progress) return "";
  const counts = { done: progress.done, doing: progress.doing, ready: progress.todo };
  const legendRows = [
    ["done", "終わった", progress.done],
    ["doing", "作業中", progress.doing],
    ["ready", "未着手", progress.todo],
  ];
  const doing = progress.doing_steps?.length
    ? `<ul class="sd-list sd-steps">${progress.doing_steps.map((step) => `<li data-st="doing">${stateIcon("doing", false)}<span class="sd-mono">${esc(step.id)}</span> ${esc(step.title)}</li>`).join("")}</ul>`
    : "";
  return (
    `<div class="sd-progress" data-code="plan-progress">${progressBar(counts)}<ul>${legendRows.map(([state, label, n]) => `<li data-st="${state}">${stateIcon(state, false)}${label}<b>${n}</b></li>`).join("")}` +
    (progress.dropped ? `<li class="sd-muted">やめた（数えない）<b>${progress.dropped}</b></li>` : "") +
    `</ul>${doing}</div>`
  );
}

function summaryTab({ ctx, scope, doc, byId }) {
  const kids = (scope.children || []).map((id) => byId.get(id)).filter(Boolean);
  const counts = stateCounts(kids);
  const details = doc.details;
  const worktrees = details?.worktrees;
  let worktree;
  if (!worktrees || worktrees.status !== "ok") worktree = `<span class="sd-muted">分からない（このPCの worktree を読めなかった）</span>`;
  else if (worktrees.items.length) {
    worktree = worktrees.items.map((item) => `<span class="sd-mono">${esc(item.branch)}</span><span class="sd-muted sd-mono">${esc(item.path)}</span>`).join("<br>");
  } else worktree = `<span class="sd-muted">このPCにはない（ほかのPCの worktree は分からない）</span>`;
  const tone = scope.state === "done" ? "note" : scope.state; // the state tones (iss-00574 D-02)
  let body = `<div class="sd-callout" data-tone="${tone}" data-st="${esc(scope.state)}">${stateIcon(scope.state, false)}<div><p class="sd-callout__title">${esc(STATES[scope.state]?.label ?? scope.state)}</p><p>${esc(scope.reason?.text ?? "")}</p></div></div>`;
  let n = 1;
  if (kids.length) {
    body +=
      section(n++, "配下の進み具合", `${counts.done}／${kids.length} 終わった`) +
      `<div class="sd-progress">${progressBar(counts)}<ul>${["done", "doing", "ready", "blocked", "unknown"]
        .map((state) => `<li data-st="${state}">${stateIcon(state, false)}${STATES[state].label}<b>${counts[state]}</b></li>`)
        .join("")}</ul></div>`;
  }
  const progress = details?.progress;
  if (progress) body += section(n++, "計画の進み具合", `${progress.done}／${progress.total} 終わった`) + planProgress(progress);
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

function depsTab({ ctx, scope, doc, byId }) {
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

function childrenTab(env) {
  const { ctx, scope, doc, byId } = env;
  const showDone = env.param("done") === "1";
  const kids = (scope.children || []).map((id) => byId.get(id)).filter(Boolean);
  if (!kids.length) return emptyState("配下はない。");
  // Stages from open children and open waits only (open_child_stages), so one stage really can run in parallel.
  const stageMap = doc.open_child_stages || doc.child_stages || { stages: [], external: [], cyclic: [] };
  const closedKids = kids.filter((item) => item.state === "done").sort((a, b) => (b.closed_at || "").localeCompare(a.closed_at || ""));
  const shownClosed = closedKids.filter((item) => showDone || item.keep_visible);
  const hidden = closedKids.length - shownClosed.length;
  const toggle = `<a class="sd-toggle" role="switch" aria-checked="${showDone}" ${env.paramLink("done", !showDone)}><span class="sd-toggle__box">${showDone ? icon("check") : ""}</span>終わったものも示す</a>`;
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

// Every document the docs tab offers (iss-00589 D-01): id (the `doc` query), key, label, file name, frame path.
// The explanation is left out: it has its own tab. An ADR is named by its file name, as several may sit side by side.
function documentEntries(details) {
  const entries = [];
  if (details.spec) {
    const names = details.documents.filter((item) => item.name.endsWith(".cue") && item.exists).map((item) => item.name);
    entries.push({ id: "spec", key: "spec", label: DOC_INFO.spec, name: names.join("・") || "requirement.cue", view: details.spec, exists: true });
  }
  for (const item of details.documents) {
    if (item.key === "explanation" || (details.spec && item.name.endsWith(".cue"))) continue;
    entries.push({ id: item.key, key: item.key, label: DOC_INFO[item.key] ?? item.key, name: item.name, view: item.view, exists: item.exists });
  }
  for (const adr of details.adrs || []) {
    entries.push({ id: "adr:" + adr.path, key: "adr", label: adr.name.replace(/\.md$/, ""), name: adr.name, view: adr.view, exists: true });
  }
  return entries;
}

// One thin bar over a frame (iss-00589 D-02, D-05): the left part, and an icon link opening the frame in a new tab.
export function frameBar(left, href) {
  const open = href
    ? `<a class="sd-framebar__open" href="${esc(href)}" target="_blank" rel="noopener" aria-label="新しいタブで開く" title="新しいタブで開く">${icon("external")}</a>`
    : "";
  return `<div class="sd-framebar">${left}${open}</div>`;
}

function checkResults(check, scopeId) {
  if (!check) return "";
  if (check.status === "failed") {
    return `<div class="sd-callout" data-tone="warning" data-code="render-failed">${icon("zap")}<div><p class="sd-callout__title">文書を描けませんでした（<code>${esc(check.code)}</code>）</p><p>${esc(check.message)}</p><p>次の1手：${(check.next_steps || []).map((step) => `<code>${esc(step)}</code>`).join("、")}</p></div></div>`;
  }
  // No band without errors, even with warnings (iss-00589 D-03): one closed line, the list opens below it.
  const errors = check.errors || [];
  if (!errors.length) return "";
  const warnings = check.warnings || [];
  const row = (item, tone) => `<li><span class="sd-badge" data-tone="${tone}">${esc(item.code)}</span> ${esc(item.message)}${item.file ? ` <span class="sd-muted sd-mono">${esc(item.file)}</span>` : ""}</li>`;
  return (
    `<details class="sd-checkbar" data-code="check-invalid"><summary>${icon("zap")}検査の誤り ${errors.length}件（警告 ${warnings.length}件） <code>spec-dock scope check ${esc(scopeId)}</code></summary>` +
    `<ul class="sd-list sd-findings">${errors.map((item) => row(item, "danger")).join("")}${warnings.map((item) => row(item, "warning")).join("")}</ul></details>`
  );
}

function docsTab(env) {
  const { doc } = env;
  const details = doc.details;
  if (!details || details.catalog !== "ok") return catalogProblem(details);
  const entries = documentEntries(details);
  const shown = entries.filter((item) => item.view);
  const wanted = env.param("doc");
  const selected = shown.find((item) => item.id === wanted) || shown[0] || null;
  const check = details.check;
  if (!selected) return checkResults(check, doc.scope.id) + emptyState("画面の中で読める文書はまだない。");
  const items = entries
    .map((item) => {
      if (!item.view) return `<span aria-disabled="true" title="${esc(item.name)}（まだない）">${esc(item.label)}</span>`;
      const current = item.id === selected.id ? ' aria-current="true"' : "";
      return `<a ${env.paramLink("doc", item.id === "spec" && !wanted ? null : item.id)}${current} title="${esc(item.name)}">${esc(item.label)}</a>`;
    })
    .join("");
  const frame =
    selected.id === "spec" && check?.status === "failed"
      ? ""
      : `<iframe class="sd-docframe" src="${esc(selected.view)}" sandbox="${FRAME_SANDBOX}" referrerpolicy="no-referrer" loading="lazy" title="${esc(selected.label)}：${esc(selected.name)}"></iframe>`;
  return (
    checkResults(check, doc.scope.id) +
    `<div class="sd-framebox" data-frame="docs">${frameBar(`<nav class="sd-seg" aria-label="文書">${items}</nav>`, selected.view)}${frame}</div>`
  );
}

function artifactsTab({ doc }) {
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
function todosTab({ ctx, scope, doc }) {
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

const AUTHORING = "spec-dock/docs/authoring/explanation.md";

// The explanation tab (D-04). Its HTML depends only on the ID, the href and the state, so a redraw after a new
// revision yields the same string and the panel leaves the frame alone (R-08).
function explanationTab({ scope, doc }) {
  const details = doc.details;
  const state = explanationState(details);
  if (state === "unreadable") return catalogProblem(details);
  const href = details.documents.find((item) => item.key === "explanation")?.href;
  const open = (label) => `<a href="${esc(href)}" target="_blank" rel="noopener">${icon("external")}${label}</a>`;
  if (state === "written") {
    return (
      `<div class="sd-framebox" data-frame="explanation">${frameBar(`<span class="sd-framebar__name">${icon("book")}説明資料</span>`, href)}` +
      `<iframe class="sd-explain" src="${esc(href)}" sandbox="${FRAME_SANDBOX}" referrerpolicy="no-referrer" title="説明資料：${esc(scope.id)}"></iframe></div>`
    );
  }
  const how = `<p>書き方：<code>${AUTHORING}</code></p>`;
  if (state === "skeleton") {
    return `<div class="sd-callout" data-tone="note" data-code="explanation-skeleton">${icon("book")}<div><p class="sd-callout__title">説明資料は雛形のまま（まだ書かれていない）</p>${how}<p>${open("雛形を新しいタブで開く")}</p></div></div>`;
  }
  return `<div class="sd-callout" data-tone="note" data-code="explanation-missing">${icon("book")}<div><p class="sd-callout__title">説明資料はまだない</p>${how}</div></div>`;
}

function todoCount(doc) {
  const todos = doc.todos;
  return todos?.status === "ok" ? todos.blocking.length + todos.descendants.length + todos.related.length : null;
}

export const SCOPE_TABS = [
  { key: "explanation", label: "説明資料", count: () => null, render: explanationTab },
  { key: "agents", label: "エージェント", visible: agentsVisible, count: agentsCount, render: agentsTab }, // iss-00593 D-02
  { key: "summary", label: "概要", count: () => null, render: summaryTab },
  { key: "deps", label: "依存", count: ({ doc }) => (doc.dependencies?.waits_for?.length || 0) + (doc.dependencies?.waited_by?.length || 0), render: depsTab },
  { key: "children", label: "配下", count: ({ scope }) => (scope.children || []).length, render: childrenTab },
  { key: "docs", label: "文書", count: () => null, render: docsTab },
  { key: "artifacts", label: "Artifact", count: ({ doc }) => doc.details?.artifacts?.length ?? null, render: artifactsTab },
  { key: "todos", label: "人のタスク", count: ({ doc }) => todoCount(doc), render: todosTab }, // iss-00554 D-06
];
export const TAB_KEYS = SCOPE_TABS.map((tab) => tab.key);

// The tabs this env shows, in the shared order (iss-00593 D-02). TAB_KEYS stays every key for `?tab=`.
export const visibleTabs = (env) => SCOPE_TABS.filter((tab) => !tab.visible || tab.visible(env));

// The detail screen keeps the choices in its query: the same paths as before (Epic R-17).
export function pageEnv(ctx, scope, doc, byId) {
  return {
    mode: "page",
    ctx,
    scope,
    doc,
    byId,
    param: (name) => ctx.route.params.get(name),
    paramLink: (name, value) => `data-nav href="${esc(ctx.href(withParam(ctx.route.path, name, value)))}"`,
    // A choice the screen made by itself replaces the query in place; later param and paramLink read the new route.
    keep(name, value) {
      if (ctx.route.params.get(name) !== value && ctx.replaceParam) ctx.route = ctx.replaceParam(name, value);
    },
  };
}

// The panel keeps the choices in its own Map and never changes the page's query (R-02). The href is the detail
// screen with the same choice and tab, so a modified click opens it as an ordinary page in a new tab.
export function panelEnv(ctx, scope, doc, byId, { params, tab }) {
  const detail = (name, value) => {
    let path = withoutEmbed(scope.path);
    for (const [key, current] of params) path = withParam(path, key, current);
    return withParam(withParam(path, name, value), "tab", tab);
  };
  const word = (value) => (value === true ? "1" : value == null || value === false ? "" : String(value));
  return {
    mode: "panel",
    ctx,
    scope,
    doc,
    byId,
    param: (name) => params.get(name) ?? null,
    paramLink: (name, value) => `href="${esc(detail(name, value))}" data-pn-param="${esc(name)}" data-pn-value="${esc(word(value))}"`,
    keep: (name, value) => params.set(name, value), // the same Map as the person's choices; the page is untouched
  };
}
