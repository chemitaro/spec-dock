// The structure graph's small marks (iss-00532 D-04): PR, CI, mergeability, assurance steps, stage, "waits after",
// progress bars. The values (state shapes and words, icons, kinds, assurance steps) are the shell's core/ui.js,
// shared with the board and the detail screen (#531, iss-00544).
import { ASSURANCE_LEVELS, esc, ic, KIND_LABEL, PR_STATE_WORDS, STATES, stateIcon } from "../../core/ui.js";

export { STATES, stateIcon, esc, ic };

export const KIND = KIND_LABEL;

// Assurance steps (Epic R-15): 1 to 4 bars; nothing is drawn when the API gives null.
const AS = ASSURANCE_LEVELS;
export function asMark(level) {
  const n = AS[level];
  if (!n) return "";
  return `<span class="as" data-lv="${n}" role="img" aria-label="保証 ${esc(level)}" title="保証レベル ${esc(level)}">${[1, 2, 3, 4]
    .map((i) => `<i class="${i <= n ? "f" : ""}"></i>`)
    .join("")}</span>`;
}
export const AS_LEVELS = Object.keys(AS);

const PRW = PR_STATE_WORDS;
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
