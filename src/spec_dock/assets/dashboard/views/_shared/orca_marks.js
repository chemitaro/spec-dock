// DOM adapters for the shared orca-web components (iss-00592 D-02 / D-04).
import { marksKey, openTarget, slotWorktree } from "./orca_logic.js";

const painted = new WeakMap();
// iss-00621 D-01: slot -> the agent ids in the order the component drew its marks (buildMarks' order, never sorted)
const shown = new WeakMap();

export function paintOrcaMarks(root, ctx, structure) {
  const now = Date.now();
  const module = ctx.orca?.marks();
  for (const slot of root.querySelectorAll("[data-orca-scope]")) {
    try {
      const worktree = slotWorktree(ctx.orca, structure, slot.dataset.orcaScope);
      // iss-00620: "all" (the structure graph) draws every agent, so the component never folds them into "+N"
      const max = slot.dataset.orcaMax === "all" ? Math.max(1, Array.isArray(worktree?.agents) ? worktree.agents.length : 0) : Number(slot.dataset.orcaMax);
      const built = worktree && module ? module.buildMarks(worktree, { now, max }) : null;
      const key = marksKey(built);
      if (painted.get(slot) === key) continue;
      if (key === "") {
        slot.replaceChildren();
        shown.set(slot, []);
      } else {
        module.renderAgentMarks(slot, worktree, { size: "sm", max, now });
        // A result without a marks list records nothing to match, so a press only opens the tab (F-01).
        shown.set(slot, Array.isArray(built.marks) ? built.marks.map((m) => m?.id ?? null) : []);
      }
      painted.set(slot, key);
    } catch {
      slot.replaceChildren();
      shown.delete(slot); // F-02: an old order never names another agent
      painted.set(slot, "");
    }
  }
}

// The agent of a pressed mark in a slot (iss-00621 D-01): the mark's data-agent-id, or else its place among the
// slot's marks in the recorded order. null for "+N", a mark outside the slot, or a record that does not match (F-01).
export function markAgentAt(slot, target) {
  const mark = target?.closest?.(".orca-mark");
  if (!mark || !slot?.contains?.(mark) || mark.classList.contains("orca-mark--more")) return null;
  const tagged = mark.getAttribute("data-agent-id");
  if (typeof tagged === "string" && tagged !== "") return tagged;
  const marks = [...slot.querySelectorAll(".orca-mark:not(.orca-mark--more)")];
  const ids = shown.get(slot);
  const i = marks.indexOf(mark);
  if (!ids || ids.length !== marks.length || i < 0) return null;
  return ids[i];
}

// A copy of a slot's recorded agent ids, or null when it has none (for iss-00616's mark positions).
export function markIds(slot) {
  const ids = shown.get(slot);
  return ids ? [...ids] : null;
}

export function createOpenButton(slot, { doc }) {
  let previous;
  return {
    update(input) {
      const { key, worktreeId } = openTarget(input);
      if (previous === key) return;
      slot.replaceChildren();
      if (worktreeId !== null) {
        const script = doc.createElement("script");
        script.src = `${input.orca.origin}/embed/open-button.js`;
        script.dataset.worktree = worktreeId;
        script.dataset.theme = input.theme;
        script.dataset.size = "sm";
        slot.append(script);
      }
      previous = key;
    },
    reset() {
      previous = undefined;
      slot.replaceChildren();
    },
  };
}

// Follow the shell's one reader (iss-00592 D-03): one subscription at a time, moved when the reader changes.
export function createOrcaWatch(onNews) {
  let reader = null;
  let off = null;
  const stop = () => {
    off?.();
    off = null;
    reader = null;
  };
  return {
    follow(orca) {
      if (orca === reader) return;
      stop();
      reader = orca ?? null;
      off = reader?.subscribe(onNews) ?? null;
    },
    stop,
  };
}
