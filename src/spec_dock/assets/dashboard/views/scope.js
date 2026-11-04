// Scope の詳しい画面（iss-00531 D-07；Epic R-18、F-05）。見出しと、概要・依存・配下・文書・Artifact のタブ。
// 文書のタブは、その場で描いた文書を sandbox の枠に示し、検査の結果と計画の進み具合を出す（iss-00535 D-04）。
// ctx.scope に scopes/<ID> の JSON、ctx.data に構造が入る。選んだタブは問い合わせの tab に持つ（Epic R-17）。
import { ancestors, byRank, fmtDateTime, fmtDay, formatSize, pullRequestNotice, stateCounts, TABS, tabOf, withParam } from "./_shared/logic.js";
import {
  assuranceMark,
  card,
  changeBadge,
  chip,
  emptyState,
  esc,
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
import { repositoryPath } from "../core/route.js";

const DOC_INFO = {
  spec: ["要件・設計・計画", "CUE の正本から、その場で描く"],
  requirement: ["要件", "何を満たすか"],
  design: ["設計", "どう作るか"],
  plan: ["計画", "どの順で進めるか"],
  explanation: ["説明資料", "人が読む説明（新しいタブ）"],
  report: ["報告", "実装の記録"],
  adr: ["ADR", "決めたことの記録"],
};
// The document frame runs each page in an opaque origin, like the server's own sandbox header (iss-00535 F-02).
const FRAME_SANDBOX = "allow-scripts allow-popups";

const link = (ctx, scope) =>
  `<a data-nav href="${esc(ctx.href(scope.path))}">${stateIcon(scope.state, false)}<span class="ds-docid">${esc(scope.id)}</span></a>`;

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

// Every document the tab can show: id (the `doc` query), label key, file name, frame path, new-tab path.
function documentEntries(details) {
  const entries = [];
  if (details.spec) {
    const names = details.documents.filter((item) => item.name.endsWith(".cue") && item.exists).map((item) => item.name);
    entries.push({ id: "spec", key: "spec", name: names.join("・") || "requirement.cue", view: details.spec, exists: true });
  }
  for (const item of details.documents) {
    if (details.spec && item.name.endsWith(".cue")) continue;
    entries.push({ id: item.key, key: item.key, name: item.name, view: item.view, href: item.href, exists: item.exists });
  }
  for (const adr of details.adrs || []) entries.push({ id: "adr:" + adr.path, key: "adr", name: adr.name, view: adr.view, exists: true });
  return entries;
}

function checkResults(check, scopeId) {
  if (!check) return "";
  if (check.status === "failed") {
    return `<div class="sd-callout" data-tone="warning" data-code="render-failed">${icon("zap")}<div><p class="sd-callout__title">文書を描けませんでした（<code>${esc(check.code)}</code>）</p><p>${esc(check.message)}</p><p>次の1手：${(check.next_steps || []).map((step) => `<code>${esc(step)}</code>`).join("、")}</p></div></div>`;
  }
  const row = (item, tone) => `<li><span class="sd-badge" data-tone="${tone}">${esc(item.code)}</span> ${esc(item.message)}${item.file ? ` <span class="sd-muted sd-mono">${esc(item.file)}</span>` : ""}</li>`;
  const errors = check.errors || [];
  const warnings = check.warnings || [];
  const head = errors.length
    ? `<p class="sd-callout__title">検査の誤り ${errors.length}件・警告 ${warnings.length}件</p>`
    : `<p class="sd-callout__title">検査の誤りなし${warnings.length ? `（警告 ${warnings.length}件）` : ""}</p>`;
  const list = errors.length + warnings.length ? `<ul class="sd-list sd-findings">${errors.map((item) => row(item, "danger")).join("")}${warnings.map((item) => row(item, "warning")).join("")}</ul>` : "";
  const next = errors.length ? `<p>次の1手：<code>spec-dock scope check ${esc(scopeId)}</code></p>` : "";
  return `<div class="sd-callout" data-tone="${errors.length ? "danger" : warnings.length ? "warning" : "note"}" data-code="check-${errors.length ? "invalid" : "ok"}">${icon(errors.length ? "zap" : "check")}<div>${head}${list}${next}</div></div>`;
}

function docsTab(ctx, doc) {
  const details = doc.details;
  if (!details || details.catalog !== "ok") return catalogProblem(details);
  const entries = documentEntries(details);
  const shown = entries.filter((item) => item.view);
  const wanted = ctx.route.params.get("doc");
  const selected = shown.find((item) => item.id === wanted) || shown[0] || null;
  const cards = entries
    .map((item) => {
      const [label, note] = DOC_INFO[item.key] ?? [item.key, ""];
      const current = selected && item.id === selected.id;
      const head = `<div class="sd-doc__head"><span class="sd-doc__icon">${icon(item.key === "explanation" ? "book" : "file")}</span><div><p class="sd-doc__title">${esc(label)}</p><p class="sd-mono">${esc(item.name)}</p></div></div><p>${esc(note)}</p>`;
      let actions;
      if (item.view) {
        actions = `<p class="sd-doc__actions"><a data-nav href="${esc(ctx.href(withParam(ctx.route.path, "doc", item.id === "spec" && !wanted ? null : item.id)))}"${current ? ' aria-current="true"' : ""}>${icon("arrowDown")}${current ? "ここに表示中" : "ここに表示"}</a><a href="${esc(item.view)}" target="_blank" rel="noopener">${icon("external")}新しいタブ</a></p>`;
      } else if (item.href) {
        actions = `<p><a href="${esc(item.href)}" target="_blank" rel="noopener">${icon("external")}新しいタブで開く</a></p>`;
      } else {
        actions = `<p><span class="sd-muted">${item.exists ? "ある" : "まだない"}</span></p>`;
      }
      return `<div class="sd-doc" data-has="${item.exists}"${current ? ' data-current="true"' : ""}>${head}${actions}</div>`;
    })
    .join("");
  const check = details.check;
  let viewer;
  if (!selected) viewer = emptyState("画面の中で読める文書はまだない。");
  else if (selected.id === "spec" && check?.status === "failed") viewer = "";
  else {
    const [label] = DOC_INFO[selected.key] ?? [selected.key];
    viewer = `<iframe class="sd-docframe" src="${esc(selected.view)}" sandbox="${FRAME_SANDBOX}" referrerpolicy="no-referrer" loading="lazy" title="${esc(label)}：${esc(selected.name)}"></iframe>`;
  }
  const progress = details.progress
    ? section(icon("check"), "計画の進み具合", `${details.progress.done}／${details.progress.total} 終わった`) + planProgress(details.progress)
    : "";
  return checkResults(check, doc.scope.id) + progress + `<div class="sd-docs">${cards}</div>` + `<div class="sd-docview">${viewer}</div>`;
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
  const counts = { deps: (doc.dependencies?.waits_for?.length || 0) + (doc.dependencies?.waited_by?.length || 0), children: (scope.children || []).length, artifacts: doc.details?.artifacts?.length };
  const tabs = TABS.map(
    ([key, label]) =>
      `<a class="sd-tab" role="tab" data-nav href="${esc(ctx.href(withParam(path, "tab", key === "summary" ? null : key)))}" aria-selected="${tab === key}">${label}${counts[key] != null ? `<small>${counts[key]}</small>` : ""}</a>`,
  ).join("");
  let body;
  if (tab === "deps") body = depsTab(ctx, scope, doc, byId);
  else if (tab === "children") body = childrenTab(ctx, scope, doc, byId, showDone);
  else if (tab === "docs") body = docsTab(ctx, doc);
  else if (tab === "artifacts") body = artifactsTab(doc);
  else body = summaryTab(ctx, scope, doc, byId);
  root.innerHTML =
    `<div class="sd-page">${newTabLink(ctx)}${back}` +
    `<header class="sd-cover" data-st="${esc(scope.state)}"><div class="sd-cover__main">` +
    `<p class="sd-cover__kicker">${esc(kindLabel(scope.kind))}<span class="ds-docid">${esc(scope.id)}</span><span class="sd-no">#${esc(scope.number)}</span></p>` +
    `<h1 class="sd-cover__title">${esc(scope.title)}</h1>` +
    `<div class="sd-cover__tags">${chip(scope.state)}<span class="sd-badge" data-tone="${scope.state === "blocked" ? "danger" : scope.state === "unknown" ? "warning" : "accent"}">${esc(scope.reason?.text ?? "")}</span>${mergeBadge(scope)}${changeBadge(scope)}</div>` +
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
