// The command lines' drawing shared by the structure graph (graph.js, iss-00616 D-04) and the cross-repository
// structure (allgraph.js, iss-00617 D-04): the three layers' HTML, the band's marks, the chosen agent's classes, the
// band agent's chat in the panel, and the check of the headings above the lines. The screens' own state stays in the
// screens; these parts take what they draw from their arguments.
import { esc, ic } from "./marks.js";
import { bandMarkHtml, bodyHtml, endsHtml, rippleHtml } from "./command_motion.js";
import { AGENT_SANDBOX, agentFrame } from "../_shared/agents_logic.js";
import { currentTheme } from "../_shared/agents_tab.js";
import { SHEET_GRAB } from "../_shared/panel.js";
import { openWorktreeButton } from "../_shared/orca_marks.js";
import { UNSCOPED, countTitle } from "./unscoped.js";

export const LAYERS = ["gx-cmd", "gx-cmd-top", "gx-band"];

/** A worktree of the summary with only one of its agents (the band's marks draw one agent each). */
export const soloWorktree = (wt, id) => ({ ...wt, agents: (Array.isArray(wt?.agents) ? wt.agents : []).filter((a) => a?.id === id) });

/** The agent of the summary with this id and its worktree, or null. */
export function findAgent(summary, id) {
  for (const worktree of Array.isArray(summary?.worktrees) ? summary.worktrees : []) {
    if (!worktree || !Array.isArray(worktree.agents)) continue;
    const agent = worktree.agents.find((a) => a?.id === id);
    if (agent) return { agent, worktree };
  }
  return null;
}

/** The component's order of a worktree's agents (orderAgents), or null for the summary's order. */
export function orderOf(module) {
  return (wt) => {
    try {
      const list = typeof module?.orderAgents === "function" && Array.isArray(wt?.agents) ? module.orderAgents(wt.agents) : null;
      return Array.isArray(list) ? list : null;
    } catch {
      return null; // the summary's order
    }
  };
}

export function element(html) {
  const holder = document.createElement("div");
  holder.innerHTML = html;
  return holder.children[0];
}

export function removeLayers(world) {
  for (const el of world.querySelectorAll(LAYERS.map((c) => `.${c}`).join(", "))) el.remove();
}

// A ripple centred in a band item: its parent is placed in the band (iss-00616 D-03).
export const inBand = (model, r) => !!model.band?.items.some((it) => r.x >= it.x && r.x <= it.x + it.w && r.y >= it.y && r.y <= it.y + it.h);

/**
 * The three layers' HTML of a commandModel (iss-00616 D-04, iss-00646 D-02, iss-00648 D-04): the lines' bodies and
 * glows (.gx-cmd), the arrowheads at the children's ends, the rings of the children's marks in the boxes and frames and
 * the ripples outside the band (.gx-cmd-top), the band's items, buttons, and the rings of the band children's marks and
 * the ripples in it (.gx-band, "" without a band). Each layer is a box of SVGs of each line's own bounding box and HTML
 * rings (command_motion.js), never one SVG as big as the world. A row with a lead has its text at the row's left
 * (iss-00617: "ほかの場所").
 */
export function layersHtml(model) {
  const lines = model.links.map(bodyHtml).join("");
  const ends = model.links.map(endsHtml).join("") + model.ripples.filter((r) => !inBand(model, r)).map(rippleHtml).join("");
  let band = "";
  if (model.band) {
    const leads = (model.band.rows || [])
      .filter((r) => r.lead)
      .map((r) => `<span class="gx-band-lead" style="left:${r.left}px;top:${r.top}px"${r.leadTitle ? ` title="${esc(r.leadTitle)}"` : ""}>${esc(r.lead)}</span>`);
    const items = model.band.items.map(itemHtml);
    // a band parent's ripples and the band children's rings over its items (the items are opaque and the band lies over
    // .gx-cmd-top)
    const rings = model.links.map(bandMarkHtml).join("") + model.ripples.filter((r) => inBand(model, r)).map(rippleHtml).join("");
    const over = rings ? `<div class="gx-band-cr" aria-hidden="true">${rings}</div>` : "";
    band = `<div class="gx-band">${leads.join("")}${items.join("")}${over}</div>`;
  }
  return {
    cmd: `<div class="gx-cmd" aria-hidden="true">${lines}</div>`,
    top: `<div class="gx-cmd-top" aria-hidden="true">${ends}</div>`,
    band,
  };
}

const BADGES = { primary: UNSCOPED.primary, unlinked: UNSCOPED.unlinked };

/**
 * One item of the band (iss-00668 D-07): its label is a button opening the worktree's panel, then its badge and count,
 * then its agents at the model's slots (wrapped lines too); "+N" is its label alone; an idle item is faint.
 */
function itemHtml(it) {
  const style = `left:${it.x}px;top:${it.y}px;width:${it.w}px;height:${it.h}px`;
  const cls = `gx-band-item${it.idle ? " is-idle" : ""}${it.kind === "fold" ? " is-fold" : ""}`;
  if (it.kind === "fold") {
    const title = `エージェントのいない worktree ${(it.folded || []).length}件`; // the Issue's English words only (constraints)
    return `<div class="${cls}" style="${style}"><button type="button" class="gx-band-lab gx-band-fold" data-cmd-fold="${esc(it.key)}" style="width:${it.labelWidth}px" title="${esc(title)}" aria-label="${esc(title)}">${esc(it.label)}</button></div>`;
  }
  const lab = `<button type="button" class="gx-band-lab" data-cmd-wt="${esc(it.key)}" style="width:${it.labelWidth}px" title="${esc(it.label)}">${esc(it.label)}</button>`;
  const b = BADGES[it.badge];
  const badge = b ? `<span class="gx-band-badge" data-badge="${esc(it.badge)}" style="width:${it.badgeWidth}px" title="${esc(b.title)}" aria-label="${esc(b.title)}">${esc(b.text)}</span>` : "";
  const ct = countTitle(it);
  const count = ct ? `<span class="gx-band-count" style="width:${it.countWidth}px" title="${esc(ct)}" aria-label="${esc(ct)}">${esc(String(it.count))}</span>` : "";
  const agents = it.agents
    .map((a) => `<button type="button" class="gx-band-agent" style="left:${a.x - it.x - 1}px;top:${a.y - it.y}px" data-cmd-agent="${esc(a.id)}" data-cmd-item="${esc(it.key)}" aria-pressed="false" aria-label="${esc(`${it.label}：${a.id}`)}"><span class="gx-band-slot"></span></button>`)
    .join("");
  return `<div class="${cls}" style="${style}">${lab}${badge}${count}${agents}</div>`;
}

/**
 * The stopping of the lines' motion (iss-00646 D-03), one per screen: while the graph moves and quiet ms after it, and
 * while the page is at the back, the graph area has is-still; the pictures and ripples off the graph area have is-off
 * (an IntersectionObserver of the area, none without one: F-01). Only classes change; graph.css pauses the animations.
 * @returns {{moved(): void, watch(world: Element | null): void, stop(): void, state(): object}}
 */
export function createMotion(view, { quiet = 300 } = {}) {
  let timer = null;
  let io = null;
  let phases = 0;
  let ripples = 0;
  let world = null;
  const back = () => document.visibilityState === "hidden";
  const still = (on) => view?.classList.toggle("is-still", on);
  const clearTimer = () => {
    if (timer !== null) clearTimeout(timer);
    timer = null;
  };
  const onVisible = () => {
    if (back()) still(true);
    else if (timer === null) still(false);
  };
  document.addEventListener("visibilitychange", onVisible);
  const unwatch = () => {
    io?.disconnect();
    io = null;
    world = null;
    phases = 0;
    ripples = 0;
  };
  return {
    moved() {
      still(true);
      clearTimer();
      timer = setTimeout(() => {
        timer = null;
        if (!back()) still(false);
      }, quiet);
    },
    watch(next) {
      unwatch();
      if (!next) {
        // F-02: no layer, no still mark nor its clock (the back keeps its mark)
        clearTimer();
        if (!back()) still(false);
        return;
      }
      world = next;
      if (typeof IntersectionObserver !== "function") return; // F-01: no watching; the motion runs everywhere
      io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) e.target.classList.toggle("is-off", !e.isIntersecting);
        },
        { root: view, threshold: 0 },
      );
      for (const el of next.querySelectorAll(".cl-ph, .cr")) {
        io.observe(el);
        if (el.classList.contains("cr")) ripples++;
        else phases++;
      }
    },
    stop() {
      unwatch();
      clearTimer();
      document.removeEventListener("visibilitychange", onVisible);
      still(false);
    },
    state() {
      return { phases, ripples, off: world ? world.querySelectorAll(".cl-ph.is-off, .cr.is-off").length : 0, still: !!view?.classList.contains("is-still") };
    },
  };
}

/** The band's marks, each drawn by the component (one agent each); a mark is drawn again only when it changes. */
export function paintBandMarks(band, model, module, cache) {
  if (!band || !module || !model?.band) return;
  const now = Date.now();
  const at = new Map();
  for (const it of model.band.items) for (const a of it.agents) at.set(`${it.key}\n${a.id}`, { it, a });
  for (const button of band.querySelectorAll("[data-cmd-agent]")) {
    const hit = at.get(`${button.dataset.cmdItem}\n${button.dataset.cmdAgent}`);
    const slot = button.querySelector(".gx-band-slot");
    if (!hit || !slot) continue;
    const doc = soloWorktree(hit.it.worktree, hit.a.id);
    try {
      const built = module.buildMarks(doc, { now, max: 1 });
      const key = JSON.stringify(built ?? null);
      if (cache.get(slot) === key) continue;
      module.renderAgentMarks(slot, doc, { size: "sm", max: 1, now });
      cache.set(slot, key);
      const label = built?.marks?.[0]?.label;
      button.setAttribute("aria-label", `${hit.it.label}：${typeof label === "string" && label ? label : hit.a.id}`);
    } catch {
      slot.replaceChildren();
      cache.set(slot, "");
    }
  }
}

/** The chosen agent's lines stand out, the others fade; only classes change, no line is drawn again (iss-00616 R-06). */
export function paintCmdSel(w, model, sel) {
  if (!w) return;
  const links = new Map((model?.links || []).map((l) => [l.id, l]));
  const parents = new Set();
  if (sel) for (const l of links.values()) if (l.child === sel) parents.add(l.parent);
  for (const svg of w.querySelectorAll(".gx-cmd, .gx-cmd-top, .gx-band-cr")) svg.classList.toggle("has-cmd-sel", !!sel);
  for (const g of w.querySelectorAll(".gx-cmd .cl, .gx-cmd-top .cl, .gx-band-cr .cl")) {
    const l = links.get(g.dataset.id);
    const on = !!sel && !!l && (l.parent === sel || l.child === sel);
    g.classList.toggle("is-cmd-hl", on);
    g.classList.toggle("is-cmd-off", !!sel && !on);
  }
  for (const g of w.querySelectorAll(".gx-cmd-top .cr, .gx-band-cr .cr")) {
    const on = !!sel && (g.dataset.agent === sel || parents.has(g.dataset.agent));
    g.classList.toggle("is-cmd-hl", on);
    g.classList.toggle("is-cmd-off", !!sel && !on);
  }
  for (const b of w.querySelectorAll("[data-cmd-agent]")) b.setAttribute("aria-pressed", String(!!sel && b.dataset.cmdAgent === sel));
}

/**
 * The band agent's heading and chat (orca-web's /embed/agent, as the agents' tab frames it). A panel that already shows
 * the same agent in the same theme is left alone, so the chat is not loaded again (iss-00616 D-04).
 * hide() is called before the panel is drawn again (the screen's Scope panel steps aside).
 * The chat's body takes the agents tab's data-tab, so panel.css lays it out as a column the frame fills (iss-00650).
 * @returns false when the agent is gone from the summary
 */
export function renderAgentPanel(panel, { id, summary, model, orca, hide }) {
  const found = findAgent(summary, id);
  if (!found) return false;
  const theme = currentTheme();
  if (panel.dataset.cmdAgent === id && panel.dataset.theme === theme && panel.classList.contains("is-open")) return true;
  hide?.();
  const { agent, worktree } = found;
  const item = model?.band?.items.find((it) => it.agents.some((a) => a.id === id));
  const label = item?.label ?? (typeof worktree.branch === "string" && worktree.branch ? worktree.branch : "ブランチ不明");
  const type = typeof agent.agentType === "string" && agent.agentType ? agent.agentType : "種類不明";
  const frame = typeof agent.detail === "string" ? agentFrame(orca?.origin, { detail: agent.detail, agentType: agent.agentType ?? null, branch: worktree.branch ?? null }, theme) : null;
  panel.dataset.st = "unknown";
  delete panel.dataset.cmdWt; // iss-00668: a worktree's panel gives way to the chat
  delete panel.dataset.cmdWtSig;
  panel.dataset.cmdAgent = id;
  panel.dataset.theme = theme;
  panel.innerHTML =
    `${SHEET_GRAB}<div class="pn-head"><b><span class="gx-band-slot pn-cmd-mark"></span>${esc(type)} · ${esc(label)}</b><button type="button" class="iconbtn" data-act="close" aria-label="閉じる">${ic("x")}</button></div>` +
    `<div class="pn-body"${frame ? ' data-tab="agents"' : ""}>${frame ? `<iframe class="sd-agent" src="${esc(frame.src)}" sandbox="${AGENT_SANDBOX}" referrerpolicy="no-referrer" title="${esc(frame.title)}"></iframe>` : `<p class="pn-cmd-none">チャットを開けません。</p>`}</div>`;
  const slot = panel.querySelector(".pn-cmd-mark");
  const module = orca?.marks?.();
  try {
    if (slot && module) module.renderAgentMarks(slot, soloWorktree(worktree, id), { size: "sm", max: 1, now: Date.now() });
  } catch {
    slot?.replaceChildren();
  }
  panel.classList.add("is-open");
  panel.setAttribute("aria-hidden", "false");
  return true;
}

/** The band agent's chat or a band item's worktree leaves the panel when it closes (the panel's content is theirs). */
export function clearAgentPanel(panel) {
  if (!panel?.dataset.cmdAgent && !panel?.dataset.cmdWt) return;
  panel.innerHTML = "";
  delete panel.dataset.cmdAgent;
  delete panel.dataset.cmdWt;
  delete panel.dataset.cmdWtSig;
  delete panel.dataset.theme;
}

/**
 * A band item's worktree in the panel (iss-00668 D-07, R-04, R-05): its badge and label, its branch, its path and its
 * agents (each opens its chat, data-wt-agent: the panel itself carries data-cmd-agent while it shows a chat), and orca-web's "open in Orca" when the summary has the worktree; "+N"
 * lists its folded worktrees. A panel that shows the same in the same theme is left alone (its button is not loaded
 * again). hide() is called before the panel is drawn again (the screen's Scope panel steps aside).
 */
export function renderWorktreePanel(panel, { item, orca, embed = false, hide }) {
  if (!item) return false;
  const theme = currentTheme();
  const worktreeId = typeof item.worktree?.id === "string" ? item.worktree.id : null;
  const open = !!worktreeId && orca?.status?.() === "ok" && !embed;
  const sig = JSON.stringify([item.key, item.label, item.badge, item.path, item.worktree?.branch ?? null, item.agents.map((a) => [a.id, a.agentType ?? null]), item.folded ?? null, open ? worktreeId : null, theme]);
  if (panel.dataset.cmdWt === item.key && panel.dataset.cmdWtSig === sig && panel.classList.contains("is-open")) return true;
  hide?.();
  delete panel.dataset.cmdAgent;
  panel.dataset.st = "unknown";
  panel.dataset.cmdWt = item.key;
  panel.dataset.cmdWtSig = sig;
  panel.dataset.theme = theme;
  const close = `<button type="button" class="iconbtn" data-act="close" aria-label="閉じる">${ic("x")}</button>`;
  if (item.kind === "fold") {
    const list = (item.folded || []).map((f) => `<li><b>${esc(f.label)}</b><small>${esc(f.path ?? "")}</small></li>`).join("");
    panel.innerHTML =
      `${SHEET_GRAB}<div class="pn-head"><b>${esc(item.label)} · エージェントのいない worktree</b>${close}</div>` +
      `<div class="pn-body"><ul class="pn-wt-list">${list}</ul></div>`;
  } else {
    const b = BADGES[item.badge];
    const badge = b ? `<span class="gx-band-badge" data-badge="${esc(item.badge)}" title="${esc(b.title)}">${esc(b.text)}</span> ` : "";
    const branch = typeof item.worktree?.branch === "string" && item.worktree.branch ? item.worktree.branch : item.label;
    const agents = item.agents
      .map((a) => {
        const type = typeof a.agentType === "string" && a.agentType ? a.agentType : "種類不明";
        return `<li><button type="button" class="pn-wt-agent" data-wt-agent="${esc(a.id)}"><span class="gx-band-slot"></span>${esc(type)}</button></li>`;
      })
      .join("");
    panel.innerHTML =
      `${SHEET_GRAB}<div class="pn-head"><b>${badge}${esc(item.label)}</b>${close}</div>` +
      `<div class="pn-body"><dl class="pn-wt"><dt>ブランチ</dt><dd>${esc(branch)}</dd><dt>パス</dt><dd class="pn-wt-path">${esc(item.path ?? "")}</dd>` +
      `<dt>エージェント</dt><dd>${agents ? `<ul class="pn-wt-agents">${agents}</ul>` : "なし"}</dd></dl>` +
      `<div class="pn-wt-open"></div></div>`;
    const module = orca?.marks?.();
    const slots = panel.querySelectorAll(".pn-wt-agent .gx-band-slot");
    item.agents.forEach((a, i) => {
      const slot = slots[i];
      try {
        if (slot && module && item.worktree) module.renderAgentMarks(slot, soloWorktree(item.worktree, a.id), { size: "sm", max: 1, now: Date.now() });
      } catch {
        slot?.replaceChildren();
      }
    });
    const slot = panel.querySelector(".pn-wt-open");
    if (slot) openWorktreeButton(slot, { orca, worktreeId, theme, embed, doc: document });
  }
  panel.classList.add("is-open");
  panel.setAttribute("aria-hidden", "false");
  return true;
}

// The headings' parts drawn over the lines (iss-00617 D-06): the frames' heading and meta rows' children but the row of
// agents, and the repository frames' heading children.
const HEAD_PARTS = ":is(.gx-ini, .gx-epic) > .gx-fh > :not(.gx-agents), :is(.gx-ini, .gx-epic) > .gx-fm > *, .ax-head > *";
const clear = (c) => !c || c === "transparent" || /^rgba\([^)]*,\s*0\)$/.test(c.replace(/\s+/g, " "));

/**
 * The check of the headings over the lines (iss-00617 D-05 heads): the frames that make a stacking context (z-index not
 * auto), the heading and meta rows (and the repositories' headings) not at z-index 2, and the heading parts with no
 * background of their own.
 */
export function headsAudit(world) {
  if (!world) return 0;
  let bad = 0;
  for (const f of world.querySelectorAll(".gx-frame")) if (getComputedStyle(f).zIndex !== "auto") bad++;
  for (const row of world.querySelectorAll(":is(.gx-ini, .gx-epic) > :is(.gx-fh, .gx-fm), .ax-head")) if (getComputedStyle(row).zIndex !== "2") bad++;
  for (const el of world.querySelectorAll(HEAD_PARTS)) if (clear(getComputedStyle(el).backgroundColor)) bad++;
  return bad;
}
