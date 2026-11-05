// The small marks' HTML for fixed inputs (iss-00544 T-06). Run by tests/unit/infra/test_dashboard_shell_polish.py:
//   node dashboard_marks_dump.mjs <assets/dashboard directory>
// Prints one JSON object; the test compares it with tests/fixtures/issue544/marks-golden.json, written from the
// code before the marks' values moved to core/ui.js, so the move changes no HTML.
// iss-00574 rewrote it once for the new state shapes (ready, doing, blocked, unknown; done is unchanged); every other
// mark is still the same HTML.
import { pathToFileURL } from "node:url";
import path from "node:path";

const [assets] = process.argv.slice(2);
const load = (rel) => import(pathToFileURL(path.join(assets, rel)).href);
const ui = await load("core/ui.js");
const parts = await load("views/_shared/parts.js");
const logic = await load("views/_shared/logic.js");
const marks = await load("views/graph/marks.js");

const STATES = ["ready", "doing", "blocked", "unknown", "done"];
// Each module's icons as they were: the shell's, plus the ones the module drew itself.
const CORE = ["search", "chevronDown", "layers", "table", "history", "bell", "folder", "globe", "external", "info", "check", "zap"];
const PART_ICONS = [...CORE, "branch", "merge", "prClosed", "chevronRight", "chevronLeft", "x", "box", "down", "arrowRight", "arrowDown", "file", "book", "target", "calendar", "question"];
const MARK_ICONS = [...CORE, "chevronRight", "x", "plus", "minus", "fit", "branch", "merge", "prClosed", "checkCircle", "box", "sparkle", "arrowRight", "target", "down", "tree", "nest", "link"];
const PRS = [
  { number: 3, state: "open", is_draft: false, checks: "success", mergeable: "mergeable" },
  { number: 4, state: "open", is_draft: true, checks: "pending", mergeable: null },
  { number: 5, state: "open", is_draft: false, checks: "failure", mergeable: "conflicting" },
  { number: 6, state: "open", is_draft: false, checks: "none", mergeable: "unknown" },
  { number: 7, state: "merged", is_draft: false, checks: null, mergeable: null },
  { number: 8, state: "closed", is_draft: false, checks: null, mergeable: null },
];
const LEVELS = ["light", "standard", "strict", "critical", null, "other"];
const CHANGES = [
  { kinds: ["new"] },
  { kinds: ["state"], state_before: "ready" },
  { kinds: ["state", "pr"], state_before: "doing", pr_before: "draft" },
  { kinds: ["pr"], pr_before: "none" },
];
const counts = { done: 3, doing: 1, ready: 2, blocked: 1, unknown: 0 };
const out = {
  ui: {
    stateIcon: STATES.map((s) => [ui.stateIcon(s), ui.stateIcon(s, false)]),
    chip: STATES.map((s) => ui.chip(s)),
    ic: CORE.map((n) => ui.ic(n, "x")),
  },
  parts: {
    icon: PART_ICONS.map((n) => parts.icon(n)),
    kindLabel: ["initiative", "epic", "issue", "x", null].map((k) => parts.kindLabel(k)),
    assuranceMark: LEVELS.map((l) => parts.assuranceMark(l)),
    prMark: PRS.map((p) => [parts.prMark(p), parts.prMark(p, { words: true })]),
    downMark: [0, 1, 5].map((n) => parts.downMark(n)),
    progressBar: [parts.progressBar(counts), parts.progressBar({}, "40px")],
    stateCountList: [parts.stateCountList(counts), parts.stateCountList(counts, { done: false })],
    legend: parts.legend(),
    changeBadge: CHANGES.map((c) => parts.changeBadge({ change: c, state: "blocked" })),
  },
  logic: {
    changeWords: CHANGES.map((c) => logic.changeWords(c, { state: "blocked" })),
    prWords: PRS.map((p) => logic.prWords(p)),
    KIND_LABEL: logic.KIND_LABEL,
    STATE_WORDS: logic.STATE_WORDS,
    PR_STATE_WORDS: logic.PR_STATE_WORDS,
    LANES: logic.LANES,
    DONE_LANE: logic.DONE_LANE,
    KINDS: logic.KINDS,
  },
  marks: {
    ic: MARK_ICONS.map((n) => marks.ic(n, "y")),
    KIND: marks.KIND,
    asMark: LEVELS.map((l) => marks.asMark(l)),
    AS_LEVELS: marks.AS_LEVELS,
    prMark: PRS.map((p) => [marks.prMark(p), marks.prMark(p, true)]),
    sbar: [marks.sbar(counts, 7, 64), marks.sbar(counts, 0, 64)],
    counts: marks.counts(counts),
    frac: marks.frac(counts, 7),
    dnMark: [0, 3].map((n) => marks.dnMark(n)),
    stageMark: [marks.stageMark(0, 3), marks.stageMark(2, 3)],
    wtMark: [marks.wtMark(null), marks.wtMark("u/iss-00002")],
    changeText: CHANGES.map((c) => marks.changeText(c)),
    chgMark: CHANGES.map((c) => marks.chgMark(c)),
  },
};
process.stdout.write(JSON.stringify(out, null, 1));
