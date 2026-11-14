// The Scope panel shared by the structure graph and the board (iss-00587 D-05). It shows the selected Scope's
// header and the same tabs as the detail screen (SCOPE_TABS), keeps the chosen tab and the choices inside a tab in
// itself (never in the page's query), and leaves the tab's contents alone when a redraw yields the same HTML, so the
// explanation frame is not loaded again (R-08). The screens select and fetch; the panel only draws.
import { ancestors, withoutEmbed, withParam } from "./logic.js";
import { esc, icon, idleText, kindLabel, mergeBadge, stateChip, stateMark } from "./parts.js";
import { pickTab } from "./panel_logic.js";
import { panelEnv, SCOPE_TABS, TAB_KEYS } from "./scope_tabs.js";

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;

export function createScopePanel(aside, { onSelect = () => {}, onClose = () => {}, extraActions = () => "" } = {}) {
  aside.classList.add("sd-pn");
  let parts = null; // the panel's own elements; another drawing in the same aside (the cleanup list) replaces them
  let current = null; // the last state given to show()
  let userTab = null; // the tab the person pressed, kept across Scopes (R-02)
  let params = new Map(); // choices inside a tab (done, doc) for the current Scope
  let shownHtml = null;
  let shownKey = null; // `${id}|${tab}` of the contents in the body

  function build() {
    aside.innerHTML =
      `<button type="button" class="pn-grab" aria-label="欄の高さを変える"></button>` +
      `<div class="pn-top"></div><div class="pn-tabs" role="tablist" aria-label="欄のタブ"></div>` +
      `<div class="pn-body" role="tabpanel"></div><div class="pn-foot"></div>`;
    const q = (sel) => aside.querySelector(sel);
    parts = { top: q(".pn-top"), tabs: q(".pn-tabs"), body: q(".pn-body"), foot: q(".pn-foot") };
    shownHtml = null;
    shownKey = null;
  }

  function header(scope, byId) {
    const chain = ancestors(byId, scope);
    const pathHtml = chain.length
      ? `<nav class="pn-path" aria-label="親の道筋">${chain.map((item) => `<button type="button" data-pn-goto="${esc(item.id)}" title="${esc(item.title)}">${esc(item.id)}</button>${icon("chevronRight")}`).join("")}<span>${esc(scope.id)}</span></nav>`
      : `<p class="pn-path">${icon("layers")}最上位</p>`;
    const idle = idleText(scope, byId);
    return (
      `<div class="pn-head">${stateChip(scope, byId, { motion: true })}${mergeBadge(scope)}<button type="button" class="iconbtn pn-close" data-pn-act="close" aria-label="閉じる">${icon("x")}</button></div>` +
      `<div class="pn-cover"><p class="pn-kicker"><span class="ds-docid">${esc(scope.id)}</span>#${esc(scope.number)}・${esc(kindLabel(scope.kind))}</p><h2 class="pn-title">${esc(scope.title)}</h2>` +
      `<p class="pn-why" data-st="${esc(scope.state)}">${stateMark(scope, byId, { motion: true, label: false })}<span>${esc(scope.reason?.text ?? "")}</span></p>` +
      (idle ? `<p class="pn-idle">${icon("clock")}${esc(idle)}</p>` : "") +
      `${pathHtml}</div>`
    );
  }

  // F-01: the header comes from the structure; the contents say the detail could not be read.
  function body(docState, env, tab) {
    if (env) return SCOPE_TABS.find((item) => item.key === tab).render(env);
    if (docState === "failed") {
      return `<div class="sd-callout" data-tone="warning" data-code="panel-doc-failed">${icon("alert")}<div><p class="sd-callout__title">詳しい内容を読めなかった（次の更新で読み直す）</p></div></div>`;
    }
    return `<p class="pn-loading">${icon("clock")}読み込み中…</p>`;
  }

  function draw() {
    const state = current;
    if (!parts || !aside.contains(parts.body)) build();
    const { ctx, docState, byId } = state;
    const ready = docState === "ok" && state.doc?.scope?.id === state.scope.id;
    // The structure wins: an older detail never overrides the newer state and reason the structure shows.
    const scope = ready ? { ...state.doc.scope, ...state.scope } : state.scope;
    const tab = ready ? pickTab(userTab, TAB_KEYS, state.doc.details) : userTab;
    const env = ready ? panelEnv(ctx, scope, state.doc, byId, { params, tab }) : null;
    aside.dataset.st = scope.state;
    parts.top.innerHTML = header(scope, byId);
    parts.tabs.innerHTML = SCOPE_TABS.map(({ key, label, count }) => {
      const n = env ? count(env) : null;
      return `<button type="button" role="tab" data-pn-tab="${key}" aria-selected="${tab === key}">${label}${n != null ? `<small>${n}</small>` : ""}</button>`;
    }).join("");
    const html = body(docState, env, tab);
    const key = `${scope.id}|${tab}`;
    if (html !== shownHtml) {
      const keep = key === shownKey ? parts.body.scrollTop : 0;
      parts.body.innerHTML = html;
      parts.body.scrollTop = keep;
      shownHtml = html;
    } else if (key !== shownKey) parts.body.scrollTop = 0;
    shownKey = key;
    parts.body.dataset.tab = tab ?? "";
    const detail = withParam(withoutEmbed(scope.path), "tab", tab ?? "summary");
    parts.foot.innerHTML =
      `<a class="ds-btn is-primary" data-nav href="${esc(ctx.href(detail))}">${icon("arrowRight")}詳しい画面</a>` +
      `<a class="ds-btn" href="${esc(detail)}" target="_blank" rel="noopener">${icon("external")}新しいタブで開く</a>` +
      extraActions(scope) +
      (scope.url ? `<a class="ds-btn" href="${esc(scope.url)}" target="_blank" rel="noopener">${icon("external")}GitHub</a>` : "");
    aside.classList.add("is-open");
    aside.setAttribute("aria-hidden", "false");
  }

  aside.addEventListener("click", (event) => {
    if (!current || !parts || !aside.contains(parts.body)) return; // another drawing owns the aside
    const t = event.target;
    const act = t.closest("[data-pn-act]");
    if (act) {
      if (act.dataset.pnAct === "close") onClose();
      return;
    }
    const tabButton = t.closest("[data-pn-tab]");
    if (tabButton) {
      userTab = tabButton.dataset.pnTab;
      draw();
      return;
    }
    const goto = t.closest("[data-pn-goto]");
    if (goto) {
      onSelect(goto.dataset.pnGoto);
      return;
    }
    if (!plainClick(event)) return; // a modified click opens the link's ordinary page (a new tab)
    const choice = t.closest("a[data-pn-param]");
    if (choice) {
      event.preventDefault();
      const value = choice.dataset.pnValue;
      if (value) params.set(choice.dataset.pnParam, value);
      else params.delete(choice.dataset.pnParam);
      draw();
      return;
    }
    const other = t.closest("a[data-id]");
    if (other && current.byId?.has(other.dataset.id)) {
      event.preventDefault(); // the shell leaves a prevented click alone
      onSelect(other.dataset.id);
    }
  });

  return {
    element: aside,
    show(state) {
      if (current?.scope?.id !== state.scope.id) params = new Map();
      current = state;
      draw();
    },
    hide() {
      current = null;
      params = new Map();
      aside.classList.remove("is-open");
      aside.setAttribute("aria-hidden", "true");
    },
    isOpen: () => current != null,
    snap: () => "half",
  };
}
