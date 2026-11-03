// The structure graph's small marks (iss-00532 D-04): PR, CI, mergeability, assurance steps, stage, "waits after",
// progress bars and the icons only the graph uses. The five state shapes are the shell's (core/ui.js STATES and
// stateIcon), shared with the board and the detail screen (#531).
import { esc, ic as coreIcon, STATES, stateIcon } from "../../core/ui.js";

export const GRAPH_ICONS = {
  chevronRight: '<path d="m9 6 6 6-6 6"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  fit: '<path d="M4 9V5a1 1 0 0 1 1-1h4M15 4h4a1 1 0 0 1 1 1v4M20 15v4a1 1 0 0 1-1 1h-4M9 20H5a1 1 0 0 1-1-1v-4"/><rect x="8" y="8" width="8" height="8" rx="1"/>',
  branch: '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 8v8M18 10c0 4-6 3-11.5 6.5"/>',
  merge: '<circle cx="6" cy="5.5" r="2"/><circle cx="6" cy="18.5" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 7.5v9M6 7.5c0 3.5 4 4.5 10 4.5"/>',
  prClosed: '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><path d="M6 8v8M15 5l5 5M20 5l-5 5M17.5 13v3"/><circle cx="17.5" cy="18" r="2"/>',
  checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 5-5.5"/>',
  box: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  down: '<rect x="2.5" y="7.5" width="8" height="9" rx="1.5"/><path d="M10.5 12h10M16.5 8l4 4-4 4"/>',
  tree: '<path d="M5 4v14a2 2 0 0 0 2 2h3M5 9h5M14 7h6M14 18h6"/><rect x="10" y="5" width="4" height="4" rx="1"/><rect x="10" y="16" width="4" height="4" rx="1"/>',
  nest: '<rect x="3" y="4" width="18" height="16" rx="2"/><rect x="6" y="9" width="5" height="4" rx="1"/><rect x="13" y="9" width="5" height="4" rx="1"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
};

export const ic = (name, cls = "") =>
  GRAPH_ICONS[name]
    ? `<svg class="ds-icon${cls ? " " + cls : ""}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${GRAPH_ICONS[name]}</svg>`
    : coreIcon(name, cls);

export { STATES, stateIcon, esc };

export const KIND = { initiative: "Initiative", epic: "Epic", issue: "Issue" };

// Assurance steps (Epic R-15): 1 to 4 bars; the API gives null until its reader exists, then nothing is drawn.
const AS = { light: 1, standard: 2, strict: 3, critical: 4 };
export function asMark(level) {
  const n = AS[level];
  if (!n) return "";
  return `<span class="as" data-lv="${n}" role="img" aria-label="保証 ${esc(level)}" title="保証レベル ${esc(level)}">${[1, 2, 3, 4]
    .map((i) => `<i class="${i <= n ? "f" : ""}"></i>`)
    .join("")}</span>`;
}
export const AS_LEVELS = Object.keys(AS);

const PRW = { open: "開いている", draft: "下書き", merged: "マージ済み", closed: "閉じた" };
const CIW = { success: "成功", failure: "失敗", running: "実行中" };

/** The structure API's pull request as the marks read it: phase, CI and mergeability. */
export function prView(pr) {
  if (!pr) return null;
  const st = pr.state === "open" ? (pr.is_draft ? "draft" : "open") : pr.state;
  const ci = { success: "success", failure: "failure", pending: "running" }[pr.checks] || null;
  const mg = { mergeable: "ok", conflicting: "conflict" }[pr.mergeable] || null;
  return { no: pr.number, st, ci, mg, url: pr.url };
}

const prIcon = (st) => (st === "merged" ? "merge" : st === "closed" ? "prClosed" : "branch");

export function prMark(pr, words = false) {
  const p = prView(pr);
  if (!p) return "";
  const t = `PR #${p.no} ${PRW[p.st]}${p.ci ? `・CI ${CIW[p.ci]}` : ""}${p.st === "open" && p.mg ? `・${p.mg === "ok" ? "マージできる" : "衝突"}` : ""}`;
  const ci = p.ci ? `<span class="ci" data-ci="${p.ci}"></span>` : "";
  const mg = p.st === "open" && p.mg ? `<span class="mg" data-mg="${p.mg}">${ic(p.mg === "ok" ? "check" : "zap")}</span>` : "";
  if (!words) return `<span class="pr" data-pr="${p.st}" role="img" aria-label="${esc(t)}" title="${esc(t)}">${ic(prIcon(p.st))}${ci}${mg}</span>`;
  return (
    `<span class="pr" data-pr="${p.st}">${ic(prIcon(p.st))}#${p.no} ${PRW[p.st]}</span>` +
    (p.ci ? `<span>${ci} CI ${CIW[p.ci]}</span>` : "") +
    (p.st === "open" && p.mg ? `<span>${mg}${p.mg === "ok" ? "マージできる" : "衝突している"}</span>` : "")
  );
}

export const BAR_ORDER = ["done", "doing", "ready", "blocked", "unknown"];
const COUNT_ORDER = ["blocked", "ready", "doing", "unknown"];

export function sbar(cnt, total, w) {
  if (!total) return `<span class="sbar" style="width:${w}px"></span>`;
  return `<span class="sbar" style="width:${w}px" role="img" aria-label="終わった ${cnt.done}／${total}">${BAR_ORDER.map((s) =>
    cnt[s] ? `<i data-st="${s}" style="width:${((cnt[s] / total) * 100).toFixed(2)}%"></i>` : "",
  ).join("")}</span>`;
}
export const counts = (cnt) =>
  `<span class="cnts">${COUNT_ORDER.filter((s) => cnt[s])
    .map((s) => `<span class="cnt" data-st="${s}" title="${STATES[s].label} ${cnt[s]}">${stateIcon(s, false)}${cnt[s]}</span>`)
    .join("")}</span>`;
export const frac = (cnt, total) => `<span class="frac">${cnt.done}<small>／${total}</small></span>`;

export const dnMark = (n) =>
  n ? `<span class="dn" title="後に続く ${n}件（これを直接・間接に待っている開いた Scope）" role="img" aria-label="後に続く ${n}件">${ic("down")}${n}</span>` : "";

export const stageMark = (stage, of) =>
  stage ? `<span class="stg" title="段${stage}（同じ親の中で ${of}段のうち ${stage}段目に進める）">${stage}</span>` : "";

export const wtMark = (branch) =>
  branch ? `<span class="wt" title="worktree：${esc(branch)}" role="img" aria-label="worktree ${esc(branch)}">${ic("folder")}</span>` : "";

const CHANGE = { new: "新しく作られた", state: "状態が変わった", pr: "PR が変わった" };
/** "Changed since you last looked" in words (Epic R-29). */
export function changeText(change) {
  if (!change) return "";
  return change.kinds
    .map((k) =>
      k === "state" && change.state_before
        ? `${CHANGE.state}（前は${STATES[change.state_before]?.label ?? change.state_before}）`
        : CHANGE[k] || k,
    )
    .join("・");
}
export const chgMark = (change) => (change ? `<span class="chg" title="前回から変化：${esc(changeText(change))}"></span>` : "");
