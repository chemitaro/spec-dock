// 状態のボード（iss-00531 D-06；Epic R-13、R-14、R-31）。列は 止められている → 着手できる → 作業中 →
// マージ待ち（マージできる／直す必要あり）→（終わった）。列と並びはサーバーの lane、merge、rank を写すだけ。
import { boardColumns, boardCounts, boardOptions, groupByParent, KINDS, pullRequestNotice, withParam } from "./_shared/logic.js";

const byNumber = (a, b) => a.number - b.number;
import { card, emptyState, esc, icon, legend, newTabLink, stateIcon } from "./_shared/parts.js";

let dialogScope = null; // the cleanup dialog stays open across the 5-second refresh

function columnBody(column, ctx, byId, group) {
  const list = (items) => {
    if (!items.length) return `<p class="sd-col__empty">ない</p>`;
    if (!group) return items.map((item) => card(item, ctx)).join("");
    return groupByParent(items)
      .map(({ parent, items: members }) => {
        const head = parent && byId.get(parent);
        const label = head
          ? `${stateIcon(head.state, false)}<span class="ds-docid">${esc(head.id)}</span><span>${esc(head.title)}</span>`
          : `<span>最上位</span>`;
        return `<div class="sd-col__grp">${label}</div>${members.map((item) => card(item, ctx)).join("")}`;
      })
      .join("");
  };
  if (column.lane !== "awaiting_merge") {
    const more = column.hidden ? `<p class="sd-col__empty">ほかに ${column.hidden}件（古いもの）</p>` : "";
    return list(column.items) + more;
  }
  const notice = pullRequestNotice(ctx.data);
  if (notice?.level === "unknown") return `<p class="sd-col__empty" data-pr-unknown>${esc(notice.text)}</p>`;
  return (
    `<div class="sd-col__sub" data-mg="ok">${icon("check")}マージできる<small>CI 成功・実行中・なし、衝突なし</small><b>${column.mergeable.length}</b></div>${list(column.mergeable)}` +
    `<div class="sd-col__sub" data-mg="fix">${icon("zap")}直す必要あり<small>CI の失敗・衝突</small><b>${column.needsFix.length}</b></div>${list(column.needsFix)}`
  );
}

function cleanupDialog(ctx, byId) {
  const rows = (ctx.data.cleanup || [])
    .map((item) => {
      const scope = byId.get(item.id);
      const nameHtml = scope
        ? `<a data-nav href="${esc(ctx.href(scope.path))}">${stateIcon(scope.state, false)}<span class="ds-docid">${esc(scope.id)}</span></a><div class="sd-muted">${esc(scope.title)}</div>`
        : `<span class="ds-docid">${esc(item.id)}</span>`;
      const github = scope?.url ? `<a href="${esc(scope.url)}" target="_blank" rel="noopener">${icon("external")}GitHub</a>` : "";
      return `<tr><td>${nameHtml}</td><td>${esc(item.text)}</td><td>${github}</td></tr>`;
    })
    .join("");
  return (
    `<dialog class="sd-dialog" id="sd-cleanup" aria-labelledby="sd-cleanup-title">` +
    `<div class="sd-dialog__head"><h2 id="sd-cleanup-title">${icon("box")}片付けの候補 ${(ctx.data.cleanup || []).length}件</h2>` +
    `<button type="button" class="sd-iconbtn" data-act="close-cleanup" aria-label="閉じる">${icon("x")}</button></div>` +
    `<div class="sd-dialog__body"><p>閉じ忘れや、置き場所の誤りかもしれないもの。閉じるかどうかは GitHub か SpecDock のコマンドで決める（この画面は見るだけ）。</p>` +
    (rows ? `<table class="sd-table"><thead><tr><th>Scope</th><th>理由</th><th></th></tr></thead><tbody>${rows}</tbody></table>` : `<p>ない</p>`) +
    `</div></dialog>`
  );
}

function render(root, ctx) {
  const data = ctx.data;
  if (!data || !data.scopes?.length) {
    root.innerHTML = `<div class="sd-page">${newTabLink(ctx)}<div class="sd-page-head"><h1>ボード</h1></div>${emptyState("表示できる構造がありません。上の知らせの次の1手を確かめてください。")}</div>`;
    return;
  }
  const options = boardOptions(ctx.route.params);
  const byId = new Map(data.scopes.map((item) => [item.id, item]));
  const { columns, unknown } = boardColumns(data.scopes, options);
  const counts = boardCounts(data.scopes);
  const prNotice = pullRequestNotice(data);
  const path = ctx.route.path;
  const kindButtons = KINDS.map(
    ([kind, label]) => `<a role="button" data-nav href="${esc(ctx.href(withParam(path, "kind", kind)))}" aria-pressed="${options.kind === kind}">${label}</a>`,
  ).join("");
  const toggle = (name, on, label) =>
    `<a class="sd-toggle" role="switch" aria-checked="${on}" data-nav href="${esc(ctx.href(withParam(path, name, !on)))}"><span class="sd-toggle__box">${on ? icon("check") : ""}</span>${label}</a>`;
  const metric = (state, label, value, extra = "") =>
    `<div class="sd-metric" data-st="${state}"><div class="sd-metric__label">${state === "merge" ? icon("branch") : stateIcon(state, false)}${label}</div><div class="sd-metric__value">${value}</div>${extra}</div>`;
  const cleanupCount = (data.cleanup || []).length;
  // Epic R-12: with done hidden, closed parents that still have open descendants stay visible.
  const keptParents = options.done ? [] : data.scopes.filter((item) => item.keep_visible && (!options.kind || item.kind === options.kind)).sort(byNumber);
  const scrollTop = root.scrollTop;
  root.innerHTML =
    `<div class="sd-page">${newTabLink(ctx)}` +
    `<div class="sd-page-head"><h1>ボード</h1><p>Scope ${counts.total}件のうち終わった ${counts.done}件。数は Issue だけを数える。</p></div>` +
    `<div class="sd-board-top"><div class="sd-metrics">` +
    metric("blocked", "止められている", counts.blocked) +
    metric("ready", "着手できる", counts.ready) +
    metric("doing", "作業中", counts.doing) +
    metric(
      "merge",
      "マージ待ち",
      prNotice?.level === "unknown" ? "?" : counts.merge,
      `<div class="sd-metric__sub"><span data-mg="fix">${icon("zap")}直す ${counts.needsFix}</span><span data-mg="ok">${icon("check")}できる ${counts.mergeable}</span></div>`,
    ) +
    (counts.unknown ? metric("unknown", "不明", counts.unknown) : "") +
    `<div class="sd-ratio"><span class="sd-ring" style="--p:${counts.percent}" aria-hidden="true"></span><p>終わった割合<b>${counts.percent}%</b><span>${counts.done}／${counts.total}</span></p></div>` +
    `</div><button type="button" class="sd-cleanup" data-act="cleanup" aria-haspopup="dialog">${icon("box")}<span><b>${cleanupCount}</b> 片付けの候補<small>配下が終わったのに開いている、など</small></span>${icon("chevronRight")}</button></div>` +
    (prNotice ? `<div class="sd-callout" data-tone="${prNotice.level === "unknown" ? "warning" : "note"}" data-code="pr-${prNotice.level}">${icon("branch")}<p>${esc(prNotice.text)}</p></div>` : "") +
    `<div class="sd-ctl"><span class="sd-seg" role="group" aria-label="種類">${kindButtons}</span>${toggle("group", options.group, "親ごとにまとめる")}${toggle("done", options.done, "終わったものも（列を足す）")}${legend()}</div>` +
    (unknown.length
      ? `<div class="sd-callout" data-tone="warning" data-code="unknown">${stateIcon("unknown", false)}<div><p class="sd-callout__title">不明 ${unknown.length}件：記録の食い違いを直すまで、どの列にも入れない</p><p>${unknown
          .map((item) => `<a data-nav href="${esc(ctx.href(item.path))}">${esc(item.id)} ${esc(item.title)}</a>（${esc(item.reason?.text ?? "")}）`)
          .join("、")}</p></div></div>`
      : "") +
    (keptParents.length
      ? `<div class="sd-callout" data-tone="note" data-code="kept-parents">${stateIcon("done", false)}<div><p class="sd-callout__title">開いた配下を持つ閉じた親 ${keptParents.length}件（終わったものを隠していても残す）</p><p>${keptParents
          .map((item) => `<a data-nav href="${esc(ctx.href(item.path))}">${esc(item.id)} ${esc(item.title)}</a>`)
          .join("、")}</p></div></div>`
      : "") +
    `<p class="sd-note">${icon("info")}列の中は推奨順：着手できる・作業中は「後に続く」数（${icon("down")}）の多い順、マージ待ちは「マージできる」を先に、止められている は待ち先の少ない順。</p>` +
    `<div class="sd-cols" style="--ncol:${columns.length}">${columns
      .map(
        (column) =>
          `<section class="sd-col" data-st="${column.lane === "awaiting_merge" ? "merge" : column.lane}" data-lane="${column.lane}" aria-label="${esc(column.label)}">` +
          `<div class="sd-col__head">${column.lane === "awaiting_merge" ? icon("branch") : stateIcon(column.lane, false)}${esc(column.label)}<b>${column.items.length + column.hidden}</b></div>` +
          `<p class="sd-col__desc">${esc(column.note)}</p><div class="sd-col__list">${columnBody(column, ctx, byId, options.group)}</div></section>`,
      )
      .join("")}</div>` +
    cleanupDialog(ctx, byId) +
    `</div>`;
  root.scrollTop = scrollTop;
  const dialog = root.querySelector("#sd-cleanup");
  root.querySelector('[data-act="cleanup"]').addEventListener("click", () => {
    dialogScope = ctx.repository;
    dialog.showModal();
  });
  root.querySelector('[data-act="close-cleanup"]').addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    dialogScope = null;
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close(); // a click on the backdrop
    else if (event.target.closest("a[data-nav]")) dialog.close();
  });
  if (dialogScope === ctx.repository) dialog.showModal();
}

export default {
  id: "board",
  title: "ボード",
  icon: "table",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/board.css"],
  render,
  dispose() {
    dialogScope = null;
  },
};
