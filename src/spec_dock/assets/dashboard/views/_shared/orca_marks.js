// DOM adapters for the shared orca-web components (iss-00592 D-02 / D-04).
import { marksKey, openTarget, slotWorktree } from "./orca_logic.js";

const painted = new WeakMap();

export function paintOrcaMarks(root, ctx, structure) {
  const now = Date.now();
  const module = ctx.orca?.marks();
  for (const slot of root.querySelectorAll("[data-orca-scope]")) {
    try {
      const max = Number(slot.dataset.orcaMax);
      const worktree = slotWorktree(ctx.orca, structure, slot.dataset.orcaScope);
      const built = worktree && module ? module.buildMarks(worktree, { now, max }) : null;
      const key = marksKey(built);
      if (painted.get(slot) === key) continue;
      if (key === "") slot.replaceChildren();
      else module.renderAgentMarks(slot, worktree, { size: "sm", max, now });
      painted.set(slot, key);
    } catch {
      slot.replaceChildren();
      painted.set(slot, "");
    }
  }
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
