// Scope の詳しい画面（iss-00531 D-07；Epic R-18、F-05）。見出しと、説明資料・概要・依存・配下・文書・Artifact・人のタスクのタブ。
// タブの並びと中身は欄と同じ views/_shared/scope_tabs.js（iss-00587 D-03）。
// ctx.scope に scopes/<ID> の JSON、ctx.data に構造が入る。選んだタブは問い合わせの tab に持つ（Epic R-17）。
import { ancestors, pullRequestNotice, withParam } from "./_shared/logic.js";
import { assuranceMark, changeBadge, emptyState, esc, humanCount, humanMark, icon, kindLabel, legend, mergeBadge, newTabLink, prMark, stateChip } from "./_shared/parts.js";
import { pickTab } from "./_shared/panel_logic.js";
import { idleBadge, pageEnv, SCOPE_TABS, TAB_KEYS } from "./_shared/scope_tabs.js";
import { repositoryPath } from "../core/route.js";

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
  const tab = pickTab(ctx.route.params.get("tab"), TAB_KEYS, doc.details);
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
  const env = pageEnv(ctx, scope, doc, byId);
  // Every tab names itself in the query (tab=summary too), so the default tab can follow the explanation (R-04).
  const tabs = SCOPE_TABS.map(({ key, label, count }) => {
    const n = count(env);
    return `<a class="sd-tab" role="tab" data-nav href="${esc(ctx.href(withParam(path, "tab", key)))}" aria-selected="${tab === key}">${label}${n != null ? `<small>${n}</small>` : ""}</a>`;
  }).join("");
  const body = SCOPE_TABS.find((item) => item.key === tab).render(env);
  root.innerHTML =
    `<div class="sd-page">${newTabLink(ctx)}${back}` +
    `<header class="sd-cover" data-st="${esc(scope.state)}"><div class="sd-cover__main">` +
    `<p class="sd-cover__kicker">${esc(kindLabel(scope.kind))}<span class="ds-docid">${esc(scope.id)}</span><span class="sd-no">#${esc(scope.number)}</span></p>` +
    `<h1 class="sd-cover__title">${esc(scope.title)}</h1>` +
    `<div class="sd-cover__tags">${stateChip(scope, byId, { motion: true })}${idleBadge(scope, byId)}<span class="sd-badge" data-tone="${scope.state === "done" ? "" : esc(scope.state)}">${esc(scope.reason?.text ?? "")}</span>${mergeBadge(scope)}${changeBadge(scope)}${humanTag(scope, ctx, path)}</div>` +
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
