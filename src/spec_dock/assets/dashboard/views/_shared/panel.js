// The Scope panel shared by the structure graph and the board (iss-00587 D-05). It shows the selected Scope's
// header and the same tabs as the detail screen (SCOPE_TABS), keeps the chosen tab and the choices inside a tab in
// itself (never in the page's query), and leaves the tab's contents alone when a redraw yields the same HTML, so the
// explanation frame is not loaded again (R-08). The screens select and fetch; the panel only draws.
// It shows only the tabs that say so (visibleTabs), paints the agents strip after the contents, and redraws itself
// on each orca-web summary (iss-00593 D-04).
import { ancestors, withoutEmbed, withParam } from "./logic.js";
import { esc, icon, idleText, kindLabel, mergeBadge, orcaSlot, stateChip, stateMark } from "./parts.js";
import { themeOf } from "./orca_logic.js";
import { createOpenButton, paintOrcaMarks } from "./orca_marks.js";
import { nextOnTap, pickTab, settleSheet, sheetHeights } from "./panel_logic.js";
import { panelEnv, SCOPE_TABS, TAB_KEYS, visibleTabs } from "./scope_tabs.js";
import { paintAgentList } from "./agents_tab.js";

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;
const PHONE = 640;
const DRAG_START = 6; // px a finger moves before the sheet follows it

// Write the tab strip only when its HTML changed: the summaries redraw the panel every 10 seconds (iss-00593). The
// heading row and the cover keep their own comparison (iss-00592 R-02).
const written = new WeakMap();
function put(element, html) {
  if (written.get(element) === html) return;
  element.innerHTML = html;
  written.set(element, html);
}

export function createScopePanel(aside, { onSelect = () => {}, onClose = () => {}, extraActions = () => "" } = {}) {
  aside.classList.add("sd-pn");
  let parts = null; // the panel's own elements; another drawing in the same aside (the cleanup list) replaces them
  let current = null; // the last state given to show()
  let userTab = null; // the tab the person pressed, kept across Scopes (R-02)
  let params = new Map(); // choices inside a tab (done, doc) for the current Scope
  let shownHtml = null;
  let shownKey = null; // `${id}|${tab}` of the contents in the body
  let snap = "half"; // the phone sheet's height: peek, half or full (D-08)
  let drag = null;
  let skipClick = false; // the click that ends a drag is not a tap
  let shownHl = null; // the heading row's chips and the cover, written only when their HTML changes (iss-00592 R-02)
  let shownCover = null;
  let openButton = null; // orca-web's "open in Orca" in the heading row (D-04)
  let followed = null; // the ctx.orca whose summaries redraw the panel
  let unfollow = null;

  function follow(orca) {
    if (orca === followed) return;
    unfollow?.();
    followed = orca ?? null;
    unfollow = typeof followed?.subscribe === "function" ? followed.subscribe(redraw) : null;
  }

  // The panel's own redraw (the summaries, the frame's move) draws with the shell's current ctx, not the one the
  // screen last gave, and not while a move waits (iss-00593 D-06, FQG-001).
  function redraw() {
    if (!current) return;
    if (current.ctx.current) {
      const ctx = current.ctx.current();
      if (!ctx) return;
      current = { ...current, ctx };
    }
    draw();
  }

  function build() {
    aside.innerHTML =
      `<button type="button" class="pn-grab" aria-label="欄の高さを変える"></button>` +
      `<div class="pn-top"></div><div class="pn-tabs" role="tablist" aria-label="欄のタブ"></div>` +
      `<div class="pn-body" role="tabpanel"></div><div class="pn-foot"></div>`;
    const q = (sel) => aside.querySelector(sel);
    const top = q(".pn-top");
    top.innerHTML =
      `<div class="pn-head"><span class="pn-hl"></span><span class="pn-orca"></span>` +
      `<button type="button" class="iconbtn pn-close" data-pn-act="close" aria-label="閉じる">${icon("x")}</button></div><div class="pn-cover"></div>`;
    parts = { top, hl: q(".pn-hl"), orca: q(".pn-orca"), cover: q(".pn-cover"), tabs: q(".pn-tabs"), body: q(".pn-body"), foot: q(".pn-foot") };
    shownHtml = null;
    shownKey = null;
    shownHl = null;
    shownCover = null;
    openButton = createOpenButton(parts.orca, { doc: document }); // a new slot forgets the last button (D-04)
  }

  // The heading row's chips (and the mark slot), and the cover below it.
  function header(scope, byId) {
    const chain = ancestors(byId, scope);
    const pathHtml = chain.length
      ? `<nav class="pn-path" aria-label="親の道筋">${chain.map((item) => `<button type="button" data-pn-goto="${esc(item.id)}" title="${esc(item.title)}">${esc(item.id)}</button>${icon("chevronRight")}`).join("")}<span>${esc(scope.id)}</span></nav>`
      : `<p class="pn-path">${icon("layers")}最上位</p>`;
    const idle = idleText(scope, byId);
    return {
      hl: `${stateChip(scope, byId, { motion: true })}<span class="pn-merge">${mergeBadge(scope)}</span>${orcaSlot(scope.id, 4)}`,
      cover:
        `<p class="pn-kicker"><span class="ds-docid">${esc(scope.id)}</span><span class="pn-kind">#${esc(scope.number)}・${esc(kindLabel(scope.kind))}</span></p><h2 class="pn-title">${esc(scope.title)}</h2>` +
      `<p class="pn-why" data-st="${esc(scope.state)}">${stateMark(scope, byId, { motion: true, label: false })}<span>${esc(scope.reason?.text ?? "")}</span></p>` +
        (idle ? `<p class="pn-idle">${icon("clock")}${esc(idle)}</p>` : "") +
        pathHtml,
    };
  }

  // orca-web's marks and button for the shown Scope: after each drawing, on the reader's news and on a theme change.
  function refreshOrca() {
    if (!current || !parts || !aside.contains(parts.body)) return;
    const { ctx, scope } = current;
    paintOrcaMarks(parts.top, ctx, ctx.data);
    openButton.update({ orca: ctx.orca, structure: ctx.data, scopeId: scope.id, embed: ctx.embed, theme: themeOf(document, (query) => matchMedia(query)) });
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
    follow(ctx.orca);
    const ready = docState === "ok" && state.doc?.scope?.id === state.scope.id;
    // The structure wins: an older detail never overrides the newer state and reason the structure shows.
    const scope = ready ? { ...state.doc.scope, ...state.scope } : state.scope;
    let tab = userTab;
    let env = null;
    let shown = SCOPE_TABS.filter((item) => !item.visible); // while the detail loads, only the tabs that always show
    // A chosen tab that is not shown while loading (agents) shows the default tab; the choice itself is kept.
    if (!ready && userTab != null && !shown.some((item) => item.key === userTab)) tab = pickTab(userTab, shown.map((item) => item.key), null);
    if (ready) {
      // Which tabs show does not depend on the tab, so a first env picks the tab and a second one carries it.
      const first = panelEnv(ctx, scope, state.doc, byId, { params, tab: userTab });
      shown = visibleTabs(first);
      tab = pickTab(userTab, shown.map((item) => item.key), state.doc.details);
      env = tab === userTab ? first : panelEnv(ctx, scope, state.doc, byId, { params, tab });
    }
    aside.dataset.st = scope.state;
    const head = header(scope, byId);
    if (head.hl !== shownHl) {
      parts.hl.innerHTML = head.hl;
      shownHl = head.hl;
    }
    if (head.cover !== shownCover) {
      parts.cover.innerHTML = head.cover;
      shownCover = head.cover;
    }
    put(parts.tabs, shown.map(({ key, label, count }) => {
      const n = env ? count(env) : null;
      return `<button type="button" role="tab" data-pn-tab="${key}" aria-selected="${tab === key}">${label}${n != null ? `<small>${n}</small>` : ""}</button>`;
    }).join(""));
    const html = body(docState, env, tab);
    const key = `${scope.id}|${tab}`;
    if (parts.body.dataset.dropped) {
      shownHtml = null; // the shell removed the frame before a move: place it again
      delete parts.body.dataset.dropped;
    }
    if (html !== shownHtml) {
      const keep = key === shownKey ? parts.body.scrollTop : 0;
      parts.body.innerHTML = html;
      parts.body.scrollTop = keep;
      shownHtml = html;
    } else if (key !== shownKey) parts.body.scrollTop = 0;
    shownKey = key;
    parts.body.dataset.tab = tab ?? "";
    if (env && tab === "agents") paintAgentList(parts.body, env, { redraw });
    // The detail screen and the new tab carry the panel's agent choice (an id or gone:<id>) like the tabs' links do,
    // so a lost agent does not open the one left by itself on the new page (iss-00593 R-05, FQG attempt 2).
    const detail = withParam(withParam(withoutEmbed(scope.path), "agent", params.get("agent") ?? null), "tab", tab ?? "summary");
    parts.foot.innerHTML =
      `<a class="ds-btn is-primary" data-nav href="${esc(ctx.href(detail))}" aria-label="詳しい画面" title="詳しい画面">${icon("arrowRight")}詳しい画面</a>` +
      `<a class="ds-btn" href="${esc(detail)}" target="_blank" rel="noopener" aria-label="新しいタブで開く" title="新しいタブで開く">${icon("external")}新しいタブで開く</a>` +
      extraActions(scope) +
      (scope.url ? `<a class="ds-btn" href="${esc(scope.url)}" target="_blank" rel="noopener" aria-label="GitHub" title="GitHub">${icon("external")}GitHub</a>` : "");
    aside.classList.add("is-open");
    aside.setAttribute("aria-hidden", "false");
    applySnap();
    refreshOrca();
  }

  // --- The phone sheet (D-08): three heights, moved only by the grab and the header band -------------------
  const isSheet = () => (aside.closest(".app") || document.documentElement).clientWidth <= PHONE;

  function applySnap() {
    if (!isSheet()) {
      aside.style.removeProperty("--pn-h");
      delete aside.dataset.snap;
      return;
    }
    aside.style.setProperty("--pn-h", `${sheetHeights(innerHeight)[snap]}px`);
    aside.dataset.snap = snap;
  }

  function release(event) {
    if (!drag || event.pointerId !== drag.id) return;
    const moved = drag.moved;
    const height = aside.getBoundingClientRect().height;
    const velocity = drag.velocity;
    drag = null;
    aside.classList.remove("is-dragging");
    if (!moved) return;
    skipClick = true;
    setTimeout(() => (skipClick = false), 0);
    const settled = settleSheet({ height, velocity, heights: sheetHeights(innerHeight) });
    if (settled === "closed") {
      snap = "half";
      applySnap();
      onClose();
      return;
    }
    snap = settled;
    applySnap();
  }

  aside.addEventListener("pointerdown", (event) => {
    if (!current || !isSheet() || (event.pointerType === "mouse" && event.button !== 0)) return;
    const t = event.target;
    const grab = t.closest(".pn-grab");
    if (!grab && (!t.closest(".pn-top") || t.closest("button, a"))) return; // the contents and frames scroll freely
    const now = performance.now();
    drag = { id: event.pointerId, y: event.clientY, h: aside.getBoundingClientRect().height, moved: false, last: { y: event.clientY, t: now }, velocity: 0 };
  });
  aside.addEventListener("pointermove", (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    const up = drag.y - event.clientY; // up is positive: the sheet grows
    if (!drag.moved) {
      if (Math.abs(up) < DRAG_START) return;
      drag.moved = true;
      aside.setPointerCapture?.(event.pointerId);
      aside.classList.add("is-dragging");
    }
    const now = performance.now();
    const dt = now - drag.last.t;
    if (dt > 0) drag.velocity = (drag.last.y - event.clientY) / dt;
    drag.last = { y: event.clientY, t: now };
    aside.style.setProperty("--pn-h", `${Math.max(0, Math.min(innerHeight, drag.h + up))}px`);
  });
  aside.addEventListener("pointerup", release);
  aside.addEventListener("pointercancel", (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    drag = null;
    aside.classList.remove("is-dragging");
    applySnap();
  });
  const onResize = () => {
    if (current) applySnap();
  };
  window.addEventListener("resize", onResize);
  // The button follows the page's light and dark (D-04): the system's choice and the shell's data-theme.
  const onTheme = () => refreshOrca();
  const media = globalThis.matchMedia?.("(prefers-color-scheme: dark)") ?? null;
  media?.addEventListener("change", onTheme);
  const themeWatch = typeof MutationObserver === "function" ? new MutationObserver(onTheme) : null;
  themeWatch?.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  aside.addEventListener("click", (event) => {
    if (!current || !parts || !aside.contains(parts.body)) return; // another drawing owns the aside
    const t = event.target;
    if (t.closest(".pn-grab")) {
      if (!skipClick && isSheet()) {
        snap = nextOnTap(snap); // a tap (or Enter) switches between half and full
        applySnap();
      }
      return;
    }
    if (t.closest(".sd-orca")) {
      preferTab("agents"); // a pressed mark in the heading opens the agents' tab (iss-00592 D-03)
      return;
    }
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

  // Choose a tab as if the person pressed it (iss-00592 D-04); a key outside the shared tabs changes nothing.
  function preferTab(key) {
    if (!TAB_KEYS.includes(key)) return;
    userTab = key;
    if (current) draw();
  }

  return {
    element: aside,
    show(state) {
      if (current?.scope?.id !== state.scope.id) {
        params = new Map();
        if (snap === "peek") snap = "half"; // another Scope keeps the height, but not the smallest one
      }
      current = state;
      draw();
    },
    hide() {
      current = null;
      follow(null);
      params = new Map();
      snap = "half"; // the next opening starts at the usual height
      drag = null;
      aside.classList.remove("is-open", "is-dragging");
      aside.setAttribute("aria-hidden", "true");
      openButton?.reset();
    },
    preferTab,
    refreshOrca,
    isOpen: () => current != null,
    snap: () => (isSheet() ? snap : null),
    destroy() {
      follow(null);
      window.removeEventListener("resize", onResize);
      media?.removeEventListener("change", onTheme);
      themeWatch?.disconnect();
    },
  };
}
