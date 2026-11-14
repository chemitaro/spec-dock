// 状態のボード（iss-00531 D-06；Epic R-13、R-14、R-31）。列は 止められている → 着手できる → 作業中 →
// マージ待ち（マージできる／直す必要あり）→（終わった）。列と並びはサーバーの lane、merge、rank を写すだけ。
// 札を普通に押すと、構造の図と同じ Scope の欄を開く（iss-00587 D-07）。札は詳しい画面への普通のリンクのまま。
import * as api from "../core/api.js";
import { boardColumns, boardCounts, boardOptions, groupByParent, KINDS, pullRequestNotice, withParam } from "./_shared/logic.js";
import { createScopePanel } from "./_shared/panel.js";

const byNumber = (a, b) => a.number - b.number;
import { card, emptyState, esc, icon, legend, newTabLink, stateIcon, stateMark } from "./_shared/parts.js";

let dialogScope = null; // the cleanup dialog stays open across the 5-second refresh

// The panel's aside lives beside the page (outside .sd-page) and survives the 5-second redraw (D-07).
const B = {
  root: null,
  page: null, // the element the board is drawn into
  pn: null,
  ctx: null,
  byId: new Map(),
  sel: null, // the selected Scope ID
  doc: null, // its scopes/<ID> JSON
  docState: "loading",
  docRevision: null,
  token: 0, // the latest read; an older answer is dropped (F-04)
};
const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;

function mount(root) {
  root.innerHTML = `<div class="sd-board-page"></div><aside class="sd-board-panel" aria-hidden="true" aria-label="Scope の欄"></aside>`;
  B.root = root;
  B.page = root.firstElementChild;
  B.pn = createScopePanel(root.querySelector("aside"), { onSelect: select, onClose: () => select(null) });
  root.addEventListener("click", onCardClick);
  document.addEventListener("keydown", onKey);
  window.addEventListener("resize", placePanel);
}

function unmount() {
  B.root?.removeEventListener("click", onCardClick);
  document.removeEventListener("keydown", onKey);
  window.removeEventListener("resize", placePanel);
  B.token++; // an answer that arrives after leaving the screen is dropped
  B.pn?.destroy();
  Object.assign(B, { root: null, page: null, pn: null, ctx: null, sel: null, doc: null, docState: "loading", docRevision: null });
}

// A plain left click on a card selects it; a modified or middle click keeps the ordinary link (R-01). The shell
// leaves a prevented click alone. Clicks inside the panel are the panel's own.
function onCardClick(event) {
  if (event.defaultPrevented || !plainClick(event) || B.pn?.element.contains(event.target)) return;
  const anchor = event.target.closest("a.sd-card[data-id]");
  if (!anchor || anchor.closest("dialog") || !B.byId.has(anchor.dataset.id)) return;
  event.preventDefault();
  select(anchor.dataset.id);
}

function onKey(event) {
  if (event.key !== "Escape" || !B.sel || B.root?.querySelector("dialog[open]")) return;
  select(null);
}

// The panel sits under the bands above the board, at the top of the board's own area.
function placePanel() {
  if (B.root) B.root.style.setProperty("--pn-top", `${B.root.offsetTop + 10}px`);
}

function markSelected() {
  for (const el of B.page.querySelectorAll(".sd-card[aria-current]")) el.removeAttribute("aria-current");
  if (B.sel) for (const el of B.page.querySelectorAll(`.sd-card[data-id="${CSS.escape(B.sel)}"]`)) el.setAttribute("aria-current", "true");
}

function drawPanel() {
  if (!B.pn) return;
  const scope = B.sel ? B.byId.get(B.sel) : null;
  if (!scope) {
    B.pn.hide();
    delete B.root.dataset.panel;
  } else {
    placePanel();
    B.pn.show({ ctx: B.ctx, scope, doc: B.doc, docState: B.docState, byId: B.byId });
    B.root.dataset.panel = "open";
  }
  markSelected();
}

function select(id) {
  B.token++;
  B.sel = id && B.byId.has(id) ? id : null;
  B.doc = null;
  B.docState = "loading";
  drawPanel();
  if (B.sel) load(B.sel, { keep: false });
}

// Read the selected Scope's detail; on a new revision the panel keeps the last answer while it reads again (R-08).
async function load(id, { keep }) {
  const token = keep ? ++B.token : B.token;
  const revision = B.ctx?.data?.revision ?? null;
  B.docRevision = revision;
  let doc = null;
  try {
    doc = await api.scope(B.ctx.repository, id, B.ctx.baseline);
  } catch {
    doc = null;
  }
  if (token !== B.token || B.sel !== id) return;
  if (!doc) {
    if (keep && B.doc) return;
    B.docState = "failed"; // F-01
  } else {
    B.doc = doc;
    B.docState = "ok";
  }
  drawPanel();
}

function columnBody(column, ctx, byId, group) {
  const list = (items) => {
    if (!items.length) return `<p class="sd-col__empty">ない</p>`;
    if (!group) return items.map((item) => card(item, ctx)).join("");
    return groupByParent(items)
      .map(({ parent, items: members }) => {
        const head = parent && byId.get(parent);
        const label = head
          ? `${stateMark(head, byId, { label: false })}<span class="ds-docid">${esc(head.id)}</span><span>${esc(head.title)}</span>`
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
        ? `<a data-nav href="${esc(ctx.href(scope.path))}">${stateMark(scope, byId, { label: false })}<span class="ds-docid">${esc(scope.id)}</span></a><div class="sd-muted">${esc(scope.title)}</div>`
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
  if (B.root !== root || !B.pn || !root.contains(B.pn.element)) mount(root);
  B.ctx = ctx;
  const data = ctx.data;
  B.byId = new Map((data?.scopes || []).map((item) => [item.id, item]));
  renderPage(B.page, ctx);
  if (B.sel && !B.byId.has(B.sel)) select(null); // F-02
  else if (B.sel && B.docRevision !== (data?.revision ?? null)) load(B.sel, { keep: true });
  drawPanel();
}

function renderPage(root, ctx) {
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
  const scrollTop = B.root.scrollTop;
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
      ? `<div class="sd-callout" data-tone="unknown" data-code="unknown">${stateIcon("unknown", false)}<div><p class="sd-callout__title">不明 ${unknown.length}件：記録の食い違いを直すまで、どの列にも入れない</p><p>${unknown
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
  B.root.scrollTop = scrollTop;
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
  styles: ["/assets/views/_shared/parts.css", "/assets/views/_shared/scope_tabs.css", "/assets/views/_shared/panel.css", "/assets/views/board.css"],
  render,
  dispose() {
    dialogScope = null;
    unmount();
  },
};
