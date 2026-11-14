// Pure decisions for mark slots and the Orca open button (iss-00592 D-01).
import { mergedWorktree } from "../../core/orca_match.js";

export function slotWorktree(orca, structure, scopeId) {
  if (!orca || orca.status() !== "ok") return null;
  return mergedWorktree(orca.forScope(structure, scopeId));
}

export function marksKey(built) {
  return built === null ? "" : JSON.stringify(built);
}

export function openTarget({ orca, structure, scopeId, embed, theme }) {
  const empty = { key: "", worktreeId: null };
  if (!orca || orca.status() !== "ok" || embed) return empty;
  const worktreeId = orca.forScope(structure, scopeId)[0]?.id;
  if (typeof worktreeId !== "string" || worktreeId === "") return empty;
  return { key: `${scopeId}|${worktreeId}|${theme}`, worktreeId };
}

export function themeOf(doc, matchMedia) {
  const theme = doc.documentElement.dataset.theme;
  if (theme === "light" || theme === "dark") return theme;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
