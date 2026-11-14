// The agents tab (iss-00593 D-02〜D-05): one strip of the Scope's agents over the chosen agent's orca-web frame.
// The choice itself is agents_logic.js; this module gathers its inputs from an env, draws the tab's contents as a
// string that depends only on the Scope, the chosen agent, the theme and the reason (so a redraw leaves the frame
// alone), and paints the strip into its slot afterwards. It never calls orca-web's write endpoints.
import { AGENT_SANDBOX, agentFrame, agentsVisibility, createAgentMemory, forgetGone, memoryFor, noteDrift, noteGone, pickAgent, scopeAgents, stripForm } from "./agents_logic.js";
import { withoutEmbed } from "./logic.js";
import { esc, icon } from "./parts.js";
import { frameBar } from "./scope_tabs.js";

// One memory for the page: the panel and the detail screen show one Scope at a time (D-02). A reload clears it.
export const mem = createAgentMemory();

const states = new WeakMap(); // env -> the inputs and the visibility, decided once per env
const picks = new WeakMap(); // env -> the pickAgent result the contents were drawn with

export function currentTheme() {
  const set = document.documentElement.dataset.theme;
  if (set === "light" || set === "dark") return set;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

// The inputs of the agents tab for one env (D-02). It never keeps a choice: another tab may be showing.
export function agentsState(env) {
  const known = states.get(env);
  if (known) return known;
  const { ctx, scope, byId } = env;
  const orca = ctx.orca;
  const status = orca?.status() ?? "off";
  const problem = ctx.orcaProblem ?? null;
  const embed = ctx.embed === true;
  const records = ctx.data?.worktrees?.status === "ok" ? (byId.get(scope.id)?.worktrees?.length ?? 0) : 0;
  const { agents, invalid, invalidIds } = scopeAgents(orca?.forScope(ctx.data, scope.id) ?? []);
  const wanted = env.param("agent") ?? null;
  memoryFor(mem, scope.id);
  const goneIds = mem.gone;
  if (status === "ok" && wanted && !wanted.startsWith("gone:") && !agents.some((item) => item.id === wanted) && !invalidIds.has(wanted)) {
    noteGone(mem, wanted, { stale: false });
  }
  const state = { ...agentsVisibility({ status, problem, records, agents, invalid, invalidIds, wanted, goneIds, embed }), agents, invalid, invalidIds, wanted, goneIds };
  states.set(env, state);
  return state;
}

// Function declarations: scope_tabs.js reads these while the two modules load each other.
export function agentsVisible(env) {
  return agentsState(env).show;
}

export function agentsCount(env) {
  const state = agentsState(env);
  return state.reason === null ? state.agents.length : null;
}

// One notice. The heading and the lines are HTML whose texts the callers already escaped.
function callout(tone, code, headingHtml, lines = []) {
  const mark = icon(tone === "note" ? "info" : "alert");
  return `<div class="sd-callout" data-tone="${tone}" data-code="${code}">${mark}<div><p class="sd-callout__title">${headingHtml}</p>${lines.map((line) => `<p>${line}</p>`).join("")}</div></div>`;
}

const outside = (scope) => `<a href="${esc(withoutEmbed(scope.path))}" target="_blank" rel="noopener">${icon("external")}SpecDock を新しいタブで開く</a>`;

// The notices of D-05: no frame and no strip.
function notice(env, state) {
  const { ctx, scope } = env;
  switch (state.reason) {
    case "loading":
      return callout("note", "orca-loading", "orca-web を読んでいる");
    case "unreachable":
      return callout("warning", "orca-unreachable", `orca-web（${esc(ctx.orca?.origin ?? "")}）に届かない`, [
        `orca-web が動いているか、orca-web の ORCA_WEB_READ_ORIGINS がこの画面のオリジン（${esc(globalThis.location?.origin ?? "")}）を許しているかを確かめる`,
      ]);
    case "shape":
      return callout("warning", "orca-shape", `orca-web の要約のエージェントの項目の形が違う（${state.invalid}件）。orca-web の版を確かめる`);
    case "orca-unreachable":
      return callout("warning", "orca-orca-unreachable", "orca-web は動いているが、Orca に届いていない（connection.state：unreachable）");
    case "orca-starting":
      return callout("warning", "orca-orca-starting", "orca-web が Orca を読み始めたところ（connection.state：starting）");
    case "config":
      return callout("warning", "orca-config", `設定の orca_web の節を読めない：${esc(ctx.orcaProblem)}`, [
        "直すファイル：<code>config.json</code>（<code>spec-dock dashboard list</code> の <code>config_problems</code> に道が出る）",
        ...(ctx.embed === true ? [outside(scope)] : []),
      ]);
    case "embed":
      return callout("warning", "orca-embed", "埋め込みの画面ではチャットを開けない", [outside(scope)]);
    default:
      return "";
  }
}

// The tab's contents (D-03). Only the Scope, the reason, the chosen agent's frame (id, kind, branch, theme) and the
// gone or choose notice go into the string; the strip is painted into its slot afterwards (paintAgentList).
export function agentsTab(env) {
  const state = agentsState(env);
  if (state.reason !== null) return notice(env, state);
  const pick = pickAgent(state.agents, state.wanted, state.goneIds);
  if (pick.addGone) noteGone(mem, pick.addGone, { stale: pick.addGoneStale });
  if (pick.remember) env.keep("agent", pick.remember);
  picks.set(env, pick);
  const { ctx, scope } = env;
  const selected = pick.selected;
  let main;
  if (selected && mem.drift === selected.id) {
    main = callout("warning", "orca-agent-drift", "チャットの中のリンクで、選んだのと別のエージェントに移ったので閉じた。このタブでは選んだエージェントだけを開く", [
      `<a data-agent-pick="${esc(selected.id)}" ${env.paramLink("agent", selected.id)}>選んだエージェントに戻す</a>`,
    ]);
  } else if (selected) {
    const frame = agentFrame(ctx.orca?.origin, selected, currentTheme());
    main = frame ? `<iframe class="sd-agent" src="${esc(frame.src)}" sandbox="${AGENT_SANDBOX}" referrerpolicy="no-referrer" title="${esc(frame.title)}"></iframe>` : "";
  } else if (pick.gone) {
    main = callout("warning", "orca-agent-gone", "選んでいたエージェントはいなくなった。上から選び直す");
  } else {
    main = callout("note", "orca-agent-choose", "エージェントを選ぶ");
  }
  return `<div class="sd-framebox" data-frame="agents">${frameBar(`<div class="sd-agents" data-orca-agents="${esc(scope.id)}"></div>`, null)}${main}</div>`;
}

function stripHtml(env, state, pick) {
  const form = stripForm(state.agents, pick.selected, pick.gone);
  const inner = (agent) =>
    `<span class="sd-agentpick__mark" data-orca-agent="${esc(agent.id)}"></span><span>${esc(agent.agentType ?? "種類不明")}</span><span class="sd-mono">${esc(agent.branch ?? "ブランチ不明")}</span>`;
  let html =
    form === "label"
      ? `<span class="sd-agentpick" aria-current="true">${inner(state.agents[0])}</span>`
      : state.agents
          .map((agent) => {
            const current = !pick.gone && pick.selected?.id === agent.id ? ' aria-current="true"' : "";
            return `<a class="sd-agentpick" data-agent-pick="${esc(agent.id)}" ${env.paramLink("agent", agent.id)}${current}>${inner(agent)}</a>`;
          })
          .join("");
  if (state.invalid > 0) html += `<span class="sd-muted">形の違う ${state.invalid}件は出していない</span>`;
  return html;
}

function paintMarks(strip, env, state) {
  const marks = env.ctx.orca?.marks?.() ?? null;
  if (!marks) return;
  const byId = new Map(state.agents.map((agent) => [agent.id, agent]));
  for (const slot of strip.querySelectorAll("[data-orca-agent]")) {
    const agent = byId.get(slot.dataset.orcaAgent);
    if (!agent) continue;
    try {
      const doc = { agents: [agent.raw] };
      const key = JSON.stringify(marks.buildMarks(doc, { max: 1 }));
      if (slot.dataset.marks === key) continue;
      marks.renderAgentMarks(slot, doc, { size: "sm", max: 1 });
      slot.dataset.marks = key;
    } catch {
      // a broken part leaves the mark empty; the rest of the strip still draws
    }
  }
}

// The strip, painted after the contents (D-04). It writes only its slot and never touches the frame next to it.
export function paintAgentList(root, env, { redraw } = {}) {
  const strip = root.querySelector("[data-orca-agents]");
  if (!strip) return;
  const state = agentsState(env);
  const pick = picks.get(env) ?? pickAgent(state.agents, state.wanted, state.goneIds);
  const html = stripHtml(env, state, pick);
  if (strip.dataset.strip !== html) {
    strip.innerHTML = html;
    strip.dataset.strip = html;
  }
  paintMarks(strip, env, state);

  // The person's pick forgets the losses of this Scope before the click's own handling redraws (R-05).
  const box = root.querySelector('.sd-framebox[data-frame="agents"]');
  if (box && !box.dataset.pickWatch) {
    box.dataset.pickWatch = "1";
    box.addEventListener(
      "click",
      (event) => {
        const item = event.target?.closest?.("[data-agent-pick]");
        if (item) forgetGone(mem, item.dataset.agentPick);
      },
      true,
    );
  }

  // A second load means a link inside the frame opened another agent's screen: close it (F-08).
  const frame = root.querySelector("iframe.sd-agent");
  const id = pick.selected?.id ?? null;
  if (frame && id !== null && !frame.dataset.loadWatch) {
    frame.dataset.loadWatch = "1";
    let loads = 0;
    frame.addEventListener("load", () => {
      loads += 1;
      if (loads < 2) return;
      noteDrift(mem, id);
      if (redraw) redraw();
      else frame.remove();
    });
  }
}
