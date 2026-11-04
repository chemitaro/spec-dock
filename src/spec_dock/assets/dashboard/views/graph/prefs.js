// The structure graph's saved choices (iss-00556 D-05). Pure: no DOM and no storage, so node tests it.
// Version 2 began when the defaults changed (done Scopes under open parents and every dependency line): from
// version 1 only the way of showing, the folding and the legend carry over, so an old `showDone` or `deps` does not
// hide the new defaults. Every value is checked; a wrong one falls back to the default.
export const PREFS_KEY = "specdock.graph.v2";
export const LEGACY_KEY = "specdock.graph.v1";

const VALID = {
  mode: (v) => v === "nest" || v === "tree",
  showDone: (v) => typeof v === "boolean",
  deps: (v) => v === "all" || v === "wait" || v === "none",
  fold: (v) => typeof v === "boolean",
};
const isRecord = (v) => !!v && typeof v === "object" && !Array.isArray(v);

/**
 * @param current  the parsed version 2 value, or null
 * @param legacy   the parsed version 1 value, or null (used only when there is no version 2 value)
 * @param defaults the layout's DEFAULTS
 * @returns {opts: {mode, showDone, deps, fold}, legend}
 */
export function restorePrefs(current, legacy, defaults) {
  const opts = { mode: defaults.mode, showDone: defaults.showDone, deps: defaults.deps, fold: defaults.fold };
  let legend = false;
  const from = isRecord(current) ? current : isRecord(legacy) ? legacy : null;
  const keys = from === current ? Object.keys(VALID) : ["mode", "fold"];
  if (from) {
    for (const key of keys) if (key in from && VALID[key](from[key])) opts[key] = from[key];
    if (typeof from.legend === "boolean") legend = from.legend;
  }
  return { opts, legend };
}
