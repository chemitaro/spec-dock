// Small HTML parts shared by the board, the detail screen and the overview (iss-00531 D-05). Every user text
// goes through esc(). State shapes come from the shell's core/ui.js (doing = half circle, ready = triangle,
// blocked = octagon, unknown = diamond, done = grey check), so #531 and #532 draw the same marks.
import { ASSURANCE_LEVELS, KIND_LABEL, PR_STATE_WORDS, STATES, chip, esc, humanCount, humanMark, ic, idleText, stateChip, stateIcon, stateMark } from "../../core/ui.js";
import {
  CHECK_WORDS,
  MERGEABLE_WORDS,
  STATE_ORDER,
  changeWords,
  prPhase,
  prWords,
  withoutEmbed,
} from "./logic.js";

export { chip, esc, humanCount, humanMark, idleText, stateChip, stateIcon, stateMark, STATES };

// Every Scope of a structure by its ID, made once per structure (iss-00574): a parent's ring counts the Issues below it.
const SCOPE_MAPS = new WeakMap();
export function scopesOf(data) {
  if (!data?.scopes) return new Map();
  let found = SCOPE_MAPS.get(data);
  if (!found) {
    found = new Map(data.scopes.map((item) => [item.id, item]));
    SCOPE_MAPS.set(data, found);
  }
  return found;
}


// Kept as the screens' name for the shell's icons.
export const icon = ic;

export const kindLabel = (kind) => KIND_LABEL[kind] ?? kind ?? "";

export function assuranceMark(level) {
  const n = ASSURANCE_LEVELS[level];
  if (!n) return "";
  const bars = [1, 2, 3, 4].map((i) => `<i class="${i <= n ? "f" : ""}"></i>`).join("");
  return `<span class="sd-as" data-lv="${n}" role="img" aria-label="保証レベル ${esc(level)}" title="保証レベル ${esc(level)}">${bars}</span>`;
}

const prIconName = (phase) => (phase === "merged" ? "merge" : phase === "closed" ? "prClosed" : "branch");

// The PR mark: state, CI and mergeability with icons; `words` adds the text (board cards, detail header).
export function prMark(pr, { words = false } = {}) {
  if (!pr) return "";
  const phase = prPhase(pr);
  const title = prWords(pr);
  const ci = pr.checks && pr.checks !== "none" ? `<span class="sd-ci" data-ci="${esc(pr.checks)}"></span>` : "";
  const merge =
    pr.state === "open" && !pr.is_draft && pr.mergeable
      ? `<span class="sd-mg" data-mg="${esc(pr.mergeable)}">${icon(pr.mergeable === "mergeable" ? "check" : pr.mergeable === "conflicting" ? "zap" : "question")}</span>`
      : "";
  if (!words) {
    return `<span class="sd-pr" data-pr="${esc(phase)}" role="img" aria-label="${esc(title)}" title="${esc(title)}">${icon(prIconName(phase))}${ci}${merge}</span>`;
  }
  const parts = [`<span class="sd-pr" data-pr="${esc(phase)}">${icon(prIconName(phase))}#${esc(pr.number)} ${esc(PR_STATE_WORDS[phase] ?? phase)}</span>`];
  if (pr.checks) parts.push(`<span class="sd-prw">${ci}${esc(CHECK_WORDS[pr.checks] ?? pr.checks)}</span>`);
  if (pr.state === "open" && !pr.is_draft && pr.mergeable) parts.push(`<span class="sd-prw">${merge}${esc(MERGEABLE_WORDS[pr.mergeable] ?? pr.mergeable)}</span>`);
  return parts.join("");
}

export function mergeBadge(scope) {
  if (scope.merge === "needs_fix") return `<span class="sd-badge" data-tone="danger">${icon("zap")}マージ待ち・直す必要あり</span>`;
  if (scope.merge === "mergeable") return `<span class="sd-badge" data-tone="ok">${icon("check")}マージ待ち・マージできる</span>`;
  return "";
}

export function downMark(count) {
  if (!count) return "";
  return `<span class="sd-dn" title="後に続く ${count}件（これを直接・間接に待っている開いた Scope）" role="img" aria-label="後に続く ${count}件">${icon("down")}${count}</span>`;
}

export function changeBadge(scope) {
  const words = changeWords(scope.change, scope);
  if (!words) return "";
  return `<span class="sd-badge sd-chg" data-tone="accent" title="前回見たときからの変化">${ic("bell")}${esc(words)}</span>`;
}

// A progress bar of child states (done first), with the done fraction.
export function progressBar(counts, width = "100%") {
  const total = STATE_ORDER.reduce((sum, state) => sum + (counts[state] || 0), 0);
  const order = ["done", "doing", "ready", "blocked", "unknown"];
  const bars = total
    ? order.map((state) => (counts[state] ? `<i data-st="${state}" style="width:${((counts[state] / total) * 100).toFixed(2)}%"></i>` : "")).join("")
    : "";
  return `<span class="sd-bar" style="width:${width}" role="img" aria-label="終わった ${counts.done || 0}／${total}">${bars}</span>`;
}

export function stateCountList(counts, { done = true } = {}) {
  return `<span class="sd-cnts">${STATE_ORDER.filter((state) => done || state !== "done")
    .map((state) => `<span class="sd-cnt" data-st="${state}" title="${STATES[state].label} ${counts[state] || 0}">${stateIcon(state, false)}<span class="vh">${STATES[state].label}</span>${counts[state] || 0}</span>`)
    .join("")}</span>`;
}

// A card on the board and on the detail tabs: an ordinary link to the detail screen (opens in a new tab too).
export function card(scope, ctx, { parent = null } = {}) {
  const meta = [];
  if (scope.pr) meta.push(prMark(scope.pr, { words: true }));
  if (scope.kind !== "issue" && scope.children?.length) meta.push(`<span>${esc(scope.children.length)}件の配下</span>`);
  const human = humanCount(scope); // iss-00554 D-06: tasks of a person blocking it (and its subtree for a parent)
  if (human.count) meta.push(humanMark(human.count, { descendants: human.descendants, cls: "sd-hm" }));
  if (scope.downstream) meta.push(downMark(scope.downstream));
  const parentLine = parent ? `<p class="sd-card__parent">${stateMark(parent, scopesOf(ctx.data), { label: false })}<span>${esc(parent.id)}</span><span>${esc(parent.title)}</span></p>` : "";
  return (
    `<a class="sd-card" data-nav data-st="${esc(scope.state)}" data-id="${esc(scope.id)}" href="${esc(ctx.href(scope.path))}">` +
    (scope.change ? `<span class="sd-card__chg" aria-hidden="true"></span>` : "") +
    `<span class="sd-card__r1">${stateMark(scope, scopesOf(ctx.data))}<span class="ds-docid">${esc(scope.id)}</span><span class="sd-no">#${esc(scope.number)}</span>` +
    (scope.kind !== "issue" ? `<span class="sd-badge">${esc(kindLabel(scope.kind))}</span>` : "") +
    `${changeBadge(scope)}</span>` +
    `<span class="sd-card__ttl">${esc(scope.title)}</span>` +
    `<span class="sd-card__why">${esc(scope.reason?.text ?? "")}</span>` +
    (meta.length ? `<span class="sd-card__meta">${meta.join("")}</span>` : "") +
    parentLine +
    `</a>`
  );
}

// Escape hatch when embedded (Epic F-13): the same screen as an ordinary page in a new tab.
export function newTabLink(ctx) {
  if (!ctx.embed) return "";
  const path = withoutEmbed(ctx.route.path);
  return `<a class="sd-newtab" href="${esc(path)}" target="_blank" rel="noopener">${ic("external")}新しいタブで開く</a>`;
}

export function legend() {
  const states = Object.entries(STATES)
    .map(([state, item]) => `<li>${stateIcon(state, false)}<span>${esc(item.label)}</span></li>`)
    .join("");
  const marks = [
    [`<span class="sd-pr" data-pr="open">${icon("branch")}</span>`, "PR が開いている"],
    [`<span class="sd-pr" data-pr="draft">${icon("branch")}</span>`, "下書きの PR"],
    [`<span class="sd-pr" data-pr="merged">${icon("merge")}</span>`, "マージ済み"],
    [`<span class="sd-ci" data-ci="success"></span><span class="sd-ci" data-ci="failure"></span><span class="sd-ci" data-ci="pending"></span>`, "CI の成功・失敗・実行中"],
    [`<span class="sd-mg" data-mg="mergeable">${icon("check")}</span><span class="sd-mg" data-mg="conflicting">${icon("zap")}</span>`, "マージできる・衝突"],
    [downMark(1).replace(/1<\/span>$/, "N</span>"), "後に続く N件"],
    [`<span class="sd-legend__chg"></span>`, "前回見たときから変わった"],
    [humanMark(1, { cls: "sd-hm" }).replace(/1件/g, "N件").replace(/人 1/, "人 N"), "人のタスク N件が止めている（Epic と Initiative は配下も含む）"],
  ]
    .map(([mark, label]) => `<li>${mark}<span>${label}</span></li>`)
    .join("");
  return `<details class="sd-legend"><summary>${ic("info")}凡例</summary><ul>${states}</ul><ul>${marks}</ul></details>`;
}

export function emptyState(text) {
  return `<div class="sd-empty">${ic("info")}<p>${esc(text)}</p></div>`;
}
