// The pure choice of the agents tab (iss-00593 D-01): which agents a Scope offers, whether the tab shows and why,
// which agent is chosen, and the frame's address. It knows no page, no ctx and no network, so node tests read it.

// The least the orca-web agent screen needs (D-03): its own scripts and origin (the send guard and the conversation
// API are same-origin only), and new tabs for the PR and CI links that leave the sandbox behind.
export const AGENT_SANDBOX = "allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox";

const DETAIL = "/embed/agent?id=";
const WAITING = new Set(["loading", "unreachable", "orca-unreachable", "orca-starting"]);
const GONE = "gone:";

const text = (value) => (typeof value === "string" ? value : null);
const filled = (value) => typeof value === "string" && value !== "";

// The agents of a Scope's matched worktrees, in worktree order then summary order. An entry is used only when its
// detail is exactly the address of its own id, so the strip, the title, the choice and the frame name one agent.
export function scopeAgents(worktrees) {
  const agents = [];
  const invalidIds = new Set();
  let invalid = 0;
  const seen = new Set();
  for (const worktree of Array.isArray(worktrees) ? worktrees : []) {
    if (!worktree || typeof worktree !== "object" || !Array.isArray(worktree.agents)) continue;
    for (const raw of worktree.agents) {
      const id = raw && typeof raw === "object" && filled(raw.id) ? raw.id : null;
      if (id !== null) {
        if (seen.has(id)) continue; // the first entry of an id wins; later ones are dropped, not counted
        seen.add(id);
      }
      if (id === null || raw.detail !== DETAIL + encodeURIComponent(id)) {
        invalid++;
        if (id !== null) invalidIds.add(id);
        continue;
      }
      agents.push({ id, agentType: text(raw.agentType), branch: text(worktree.branch), worktreeId: worktree.id, detail: raw.detail, raw });
    }
  }
  return { agents, invalid, invalidIds };
}

// Whether the tab shows, and the reason it shows a notice instead of a frame (R-01, R-06; D-01). Top to bottom.
export function agentsVisibility({ status, problem = null, records = 0, agents = [], invalid = 0, invalidIds, wanted = null, goneIds, embed = false }) {
  const gone = goneIds ?? new Set();
  const broken = invalidIds ?? new Set();
  const hidden = { show: false, reason: null };
  if (status === "off" && !problem) return hidden;
  if (!records) return hidden;
  if (!problem && !WAITING.has(status)) {
    if (status !== "ok") return hidden;
    if (!agents.length && !wanted && !gone.size && !(invalid > 0)) return hidden;
  }
  if (problem) return { show: true, reason: "config" };
  if (embed) return { show: true, reason: "embed" };
  if (status !== "ok") return { show: true, reason: status };
  // No usable agent but some entries out of shape: never read as a loss, whatever the choice says (FQG attempt 1).
  const noneUsable = !agents.length && invalid > 0;
  if (noneUsable || (wanted && broken.has(wanted))) return { show: true, reason: "shape" };
  return { show: true, reason: null };
}

// The chosen agent (Epic D-02), only when the reason is null. A choice never moves to another agent by itself.
export function pickAgent(agents, wanted, goneIds) {
  const gone = goneIds ?? new Set();
  const result = (selected, isGone, remember = null, addGone = null, addGoneStale = false) => ({ selected, gone: isGone, remember, addGone, addGoneStale });
  if (wanted && wanted.startsWith(GONE)) return result(null, true, null, wanted.slice(GONE.length), true);
  // A lost id read back (a back move, or a loss noted while another tab showed) is written as gone:<id> too, so a
  // reload does not open it again.
  if (wanted && gone.has(wanted)) return result(null, true, GONE + wanted);
  if (wanted) {
    const selected = agents.find((item) => item.id === wanted);
    return selected ? result(selected, false) : result(null, true, GONE + wanted, wanted, false);
  }
  if (gone.size) return result(null, true);
  if (agents.length === 1) return result(agents[0], false, agents[0].id);
  return result(null, false);
}

// A fixed heading for the one chosen agent; otherwise pressable items (also when only one is left after a loss).
export function stripForm(agents, selected, gone) {
  return agents.length === 1 && !gone && selected != null && selected.id === agents[0].id ? "label" : "switch";
}

// The frame's address and title (R-03). The detail is used as given: the id is never encoded again.
export function agentFrame(origin, agent, theme) {
  if (typeof origin !== "string" || !agent || (theme !== "light" && theme !== "dark")) return null;
  return {
    src: origin + agent.detail + "&theme=" + theme,
    title: "エージェント：" + (agent.agentType ?? "種類不明") + "・" + (agent.branch ?? "ブランチ不明"),
  };
}

// What the screen remembers about one Scope until another Scope is shown (R-05, F-08): the ids that went away, the
// id the person picked last, the id whose frame moved to another agent's screen, and the id whose frame was placed
// last (the choice of an env that has none, such as a panel opened again; FQG attempt 1).
export function createAgentMemory() {
  return { scopeId: null, gone: new Set(), picked: null, drift: null, last: null };
}

export function memoryFor(mem, scopeId) {
  if (mem.scopeId !== scopeId) {
    mem.scopeId = scopeId;
    mem.gone = new Set();
    mem.picked = null;
    mem.drift = null;
    mem.last = null;
  }
  return mem;
}

// A stale gone:<id> read back from the query or the panel's Map does not undo the person's newer pick of that id.
export function noteGone(mem, id, { stale = false } = {}) {
  if (stale && id === mem.picked) return mem;
  mem.gone.add(id);
  if (id === mem.picked) mem.picked = null;
  return mem;
}

export function forgetGone(mem, id) {
  mem.gone = new Set();
  mem.drift = null;
  mem.picked = id;
  mem.last = id;
  return mem;
}

export function noteDrift(mem, id) {
  mem.drift = id;
  return mem;
}

export function noteShown(mem, id) {
  mem.last = id;
  return mem;
}
