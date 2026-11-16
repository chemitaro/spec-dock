// The structure graph's saved choices (iss-00556 D-05, iss-00603 D-04). Pure: no DOM and no storage, so node tests it.
// Version 3 holds the way of showing, the range of what is shown (all, now, next) in place of version 2's showDone
// and fold, and the legend. Without a version 3 value, version 2 carries over its way of showing and legend, and its
// showDone as the range ("all" when true, else "now"; fold is not used). Without either, version 1 carries over only
// the way of showing and the legend (as from version 1 to 2), so an old showDone does not hide the new defaults.
// The old line choice (iss-00607: the lines are always every line) is not read from any version; a version 3 value
// that still holds it loses it at the next write. Every value is checked; a wrong one falls back to the default. The
// old keys are read, never removed.
export const PREFS_KEY = "specdock.graph.v3";
export const LEGACY_KEYS = ["specdock.graph.v2", "specdock.graph.v1"]; // the newest first

const VALID = {
  mode: (v) => v === "nest" || v === "tree",
  range: (v) => v === "all" || v === "now" || v === "next",
};
const isRecord = (v) => !!v && typeof v === "object" && !Array.isArray(v);

/**
 * @param current  the parsed version 3 value, or null
 * @param legacies the parsed values of LEGACY_KEYS ([version 2, version 1]; null where there is none or it is broken)
 * @param defaults the layout's DEFAULTS
 * @returns {opts: {mode, range}, legend}
 */
export function restorePrefs(current, legacies, defaults) {
  const opts = { mode: defaults.mode, range: defaults.range };
  let legend = false;
  const [v2, v1] = Array.isArray(legacies) ? legacies : [];
  let from = null;
  let keys = [];
  if (isRecord(current)) [from, keys] = [current, ["mode", "range"]];
  else if (isRecord(v2)) {
    [from, keys] = [v2, ["mode"]];
    opts.range = v2.showDone === true ? "all" : "now";
  } else if (isRecord(v1)) [from, keys] = [v1, ["mode"]];
  if (from) {
    for (const key of keys) if (key in from && VALID[key](from[key])) opts[key] = from[key];
    if (typeof from.legend === "boolean") legend = from.legend;
  }
  return { opts, legend };
}
