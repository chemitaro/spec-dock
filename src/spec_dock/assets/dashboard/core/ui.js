// Shared small parts for the shell and the screens (iss-00529). Screens may import these. The one home of the marks'
// values (iss-00544): every icon shape, the state, kind and pull request words and the assurance steps; the
// screens' parts draw with these. The state marks (iss-00574 D-03): ready = a ring with a play triangle, doing =
// the progress ring, blocked = a filled circle with a pause, unknown = a ring with "?", done = a grey check; every
// shape fits one circle. The colors are the state tokens of app.css (`--sd-<state>`).

export const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

export const ICONS = {
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  chevronDown: '<path d="m6 9 6 6 6-6"/>',
  layers: '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
  table: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M3 15h18M9 4v16"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
  bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8M10 20a2 2 0 0 0 4 0"/>',
  folder: '<path d="M3 6a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  external: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  zap: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  // the screens' icons (iss-00531 parts.js, iss-00532 marks.js)
  branch: '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 8v8M18 10c0 4-6 3-11.5 6.5"/>',
  merge: '<circle cx="6" cy="5.5" r="2"/><circle cx="6" cy="18.5" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 7.5v9M6 7.5c0 3.5 4 4.5 10 4.5"/>',
  prClosed: '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><path d="M6 8v8M15 5l5 5M20 5l-5 5M17.5 13v3"/><circle cx="17.5" cy="18" r="2"/>',
  chevronRight: '<path d="m9 6 6 6-6 6"/>',
  chevronLeft: '<path d="m15 6-6 6 6 6"/>',
  x: '<path d="M6 6l12 12M18 6 6 18"/>',
  box: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
  down: '<rect x="2.5" y="7.5" width="8" height="9" rx="1.5"/><path d="M10.5 12h10M16.5 8l4 4-4 4"/>',
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  arrowDown: '<path d="M12 5v14M6 13l6 6 6-6"/>',
  file: '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/>',
  book: '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v16H5.5A1.5 1.5 0 0 0 4 20.5zM4 20.5A1.5 1.5 0 0 0 5.5 22H20"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  question: '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.3M12 16.6v.1"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  fit: '<path d="M4 9V5a1 1 0 0 1 1-1h4M15 4h4a1 1 0 0 1 1 1v4M20 15v4a1 1 0 0 1-1 1h-4M9 20H5a1 1 0 0 1-1-1v-4"/><rect x="8" y="8" width="8" height="8" rx="1"/>',
  checkCircle: '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 5-5.5"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
  tree: '<path d="M5 4v14a2 2 0 0 0 2 2h3M5 9h5M14 7h6M14 18h6"/><rect x="10" y="5" width="4" height="4" rx="1"/><rect x="10" y="16" width="4" height="4" rx="1"/>',
  nest: '<rect x="3" y="4" width="18" height="16" rx="2"/><rect x="6" y="9" width="5" height="4" rx="1"/><rect x="13" y="9" width="5" height="4" rx="1"/>',
  // a person (iss-00554): the human tasks' mark and tab
  person: '<circle cx="12" cy="8" r="3.6"/><path d="M4.8 20.2c.6-3.9 3.6-6.2 7.2-6.2s6.6 2.3 7.2 6.2"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  alert: '<path d="M10.3 3.9 2.6 17.4A2 2 0 0 0 4.3 20.4h15.4a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9.5v4.2M12 17v.1"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
};

export const ic = (name, cls = "") =>
  `<svg class="ds-icon${cls ? " " + cls : ""}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONS[name] || ""}</svg>`;

// The progress ring of a Scope in progress (iss-00574 D-03): one segment per plan step (dropped ones left out), the
// done ones thick in the state color, the rest thin in the track color; past 12 steps one arc of the done part; with
// no steps the outline only. `live` adds the one overlay that blinks (`.sd-nx`): the next segment, the next part of
// the arc, the center dot when every step is done, or a thick ring over the outline.
const RING = 8.6;
const GAP = 0.32;
const TAU = Math.PI * 2;
const point = (a) => `${(12 + RING * Math.sin(a)).toFixed(2)} ${(12 - RING * Math.cos(a)).toFixed(2)}`;
const arc = (a0, a1, cls, width, color = "currentColor") =>
  `<path class="${cls}" d="M${point(a0)}A${RING} ${RING} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${point(a1)}" fill="none" stroke="${color}" stroke-width="${width}"/>`;
const ring = (cls, width, color = "currentColor") =>
  `<circle class="${cls}" cx="12" cy="12" r="${RING}" fill="none" stroke="${color}" stroke-width="${width}"/>`;
const TRACK = "var(--sd-track)";
const CENTER = '<circle class="sd-nx" cx="12" cy="12" r="3" fill="currentColor"/>';

export function progressRing(progress, { live = false } = {}) {
  const total = Math.max(0, Math.floor(progress?.total || 0));
  const done = Math.min(Math.max(0, Math.floor(progress?.done || 0)), total);
  if (!total) return ring("o", 2.4) + (live ? ring("sd-nx", 3.2) : "");
  if (total <= 12) {
    let out = "";
    let next = "";
    for (let i = 0; i < total; i++) {
      const a0 = (i / total) * TAU + GAP / 2;
      const a1 = ((i + 1) / total) * TAU - GAP / 2;
      out += i < done ? arc(a0, a1, "f", 3.2) : arc(a0, a1, "t", 2, TRACK);
      if (live && i === done) next = arc(a0, a1, "sd-nx f", 3.2);
    }
    return out + next + (live && done === total ? CENTER : "");
  }
  const end = (done / total) * TAU;
  let out = ring("t", 2, TRACK);
  if (done === total) out += ring("f", 3.2);
  else if (done) out += arc(0, end, "f", 3.2);
  if (live) out += done === total ? CENTER : arc(end, ((done + 1) / total) * TAU, "sd-nx f", 3.2);
  return out;
}

export const STATES = {
  ready: { label: "着手できる", shape: '<circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M10.1 8.3 16 12l-5.9 3.7z" fill="currentColor" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>' },
  doing: { label: "作業中", shape: progressRing(null) },
  blocked: { label: "止められている", shape: '<circle cx="12" cy="12" r="9.6" fill="currentColor"/><path class="on" d="M9.6 8.6v6.8"/><path class="on" d="M14.4 8.6v6.8"/>' },
  unknown: { label: "不明", shape: '<circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M9.8 9.7a2.3 2.3 0 1 1 3.2 2.1c-.6.3-1 .8-1 1.4v.3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16.5" r="1.25" fill="currentColor"/>' },
  done: { label: "終わった", shape: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path class="on" d="m7.6 12.3 3 3 5.8-6.2"/>' },
};

// The five states in words, from STATES.
export const STATE_WORDS = Object.fromEntries(Object.entries(STATES).map(([state, item]) => [state, item.label]));

export const KIND_LABEL = { initiative: "Initiative", epic: "Epic", issue: "Issue" };

// Assurance steps (Epic R-15): 1 to 4 bars.
export const ASSURANCE_LEVELS = { light: 1, standard: 2, strict: 3, critical: 4 };

export const PR_STATE_WORDS = { open: "開いている", draft: "下書き", merged: "マージ済み", closed: "閉じた" };

// A state mark. For doing, `opts.progress` ({done, total}) draws the progress ring and `opts.live` its blinking
// overlay; `opts.unit` names what is counted in the words ("手順" for an Issue's plan steps, "配下" for the Issues below).
export function stateIcon(state, label = true, opts = {}) {
  const { progress = null, live = false, unit = "手順" } = opts;
  const doing = state === "doing";
  const shape = doing ? progressRing(progress, { live }) : STATES[state]?.shape ?? "";
  const name = STATES[state]?.label ?? state;
  const words = doing && progress?.total ? `${name}（${unit} ${progress.done}／${progress.total} 終わった）` : name;
  const a11y = label ? `role="img" aria-label="${esc(words)}"` : 'aria-hidden="true"';
  return `<svg class="st-ico" data-st="${state}"${doing && live ? ' data-live="1"' : ""} viewBox="0 0 24 24" ${a11y}>${shape}</svg>`;
}

export const chip = (state, opts = {}) => `<span class="chip" data-st="${state}">${stateIcon(state, false, opts)}${esc(STATES[state]?.label ?? state)}</span>`;

// --- Progress and motion of a Scope in progress (iss-00574 D-03, D-04) ------------------------------------------

export const LIVE_MS = 30 * 60 * 1000;

const lookup = (byId) => (typeof byId === "function" ? byId : (id) => byId?.get?.(id));

function below(scope, get) {
  const seen = new Set([scope.id]);
  const out = [];
  const walk = (item) => {
    for (const id of item.children || []) {
      const child = get(id);
      if (!child || seen.has(child.id)) continue;
      seen.add(child.id);
      out.push(child);
      walk(child);
    }
  };
  walk(scope);
  return out;
}

const time = (text) => {
  const value = text ? Date.parse(text) : NaN;
  return Number.isFinite(value) ? value : null;
};

// {done, total} of a Scope in progress: an Issue's plan steps, an Epic's or Initiative's Issues below it; else null.
export function scopeProgress(scope, byId) {
  if (scope?.state !== "doing") return null;
  if (scope.kind === "issue") {
    const p = scope.progress;
    return p && p.total ? { done: p.done || 0, total: p.total } : null;
  }
  const issues = below(scope, lookup(byId)).filter((item) => item.kind === "issue");
  return issues.length ? { done: issues.filter((item) => item.state === "done").length, total: issues.length } : null;
}

// The last move in milliseconds: an Issue's `active_at` or plan time, a parent's also every Scope below; null if unknown.
export function movedAt(scope, byId) {
  if (!scope) return null;
  const items = scope.kind === "issue" ? [scope] : [scope, ...below(scope, lookup(byId))];
  let latest = null;
  for (const item of items) {
    for (const value of [time(item.active_at), time(item.progress?.modified_at)]) {
      if (value != null && (latest == null || value > latest)) latest = value;
    }
  }
  return latest;
}

export const isLive = (moved, now) => moved != null && now - moved <= LIVE_MS;

export function idleWords(ms) {
  const minutes = Math.floor(ms / 60000);
  if (minutes < 1) return "1分以内動きなし";
  if (minutes < 60) return `${minutes}分動きなし`;
  const hours = Math.floor(minutes / 60);
  return hours < 48 ? `${hours}時間動きなし` : `${Math.floor(hours / 24)}日動きなし`;
}

// "N分動きなし" for a Scope in progress that has not moved for 30 minutes; "" otherwise (and when the time is unknown).
export function idleText(scope, byId, now = Date.now()) {
  if (scope?.state !== "doing") return "";
  const moved = movedAt(scope, byId);
  return moved == null || isLive(moved, now) ? "" : idleWords(now - moved);
}

// A Scope's state mark. Only the graph's boxes, its side panel and the detail cover pass `motion: true`; lists never do.
export function stateMark(scope, byId, { now = Date.now(), motion = false, label = true } = {}) {
  const state = scope?.state ?? "unknown";
  if (state !== "doing") return stateIcon(state, label);
  const live = motion && isLive(movedAt(scope, byId), now);
  return stateIcon("doing", label, { progress: scopeProgress(scope, byId), live, unit: scope.kind === "issue" ? "手順" : "配下" });
}

export function stateChip(scope, byId, { now = Date.now(), motion = false } = {}) {
  const state = scope?.state ?? "unknown";
  if (state !== "doing") return chip(state);
  const live = motion && isLive(movedAt(scope, byId), now);
  return chip("doing", { progress: scopeProgress(scope, byId), live, unit: scope.kind === "issue" ? "手順" : "配下" });
}

export function ago(seconds) {
  if (seconds == null) return "—";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 1) return "1分以内";
  if (minutes < 60) return `${minutes}分前`;
  const hours = Math.floor(minutes / 60);
  return hours < 48 ? `${hours}時間前` : `${Math.floor(hours / 24)}日前`;
}

// The human tasks' mark on boxes and cards (iss-00554 D-06): "人 n" for the tasks blocking the Scope itself; with
// `descendants`, the count includes the tasks blocking any Scope below it and says so. Nothing when there are none.
export function humanWords(count, { descendants = false } = {}) {
  return descendants ? `人のタスク ${count}件が止めている（配下を含む）` : `人のタスク ${count}件が止めている`;
}

export function humanMark(count, { descendants = false, cls = "hm" } = {}) {
  if (!count) return "";
  const words = humanWords(count, { descendants });
  return `<span class="${cls}" data-under="${descendants ? 1 : 0}" role="img" title="${esc(words)}" aria-label="${esc(words)}">${ic("person")}人 ${esc(count)}${descendants ? "<small>配下も</small>" : ""}</span>`;
}

// Which count a Scope shows: an Issue its own blockers, an Epic or Initiative the ones of its whole subtree.
export function humanCount(scope) {
  const marks = scope?.todos;
  if (!marks) return { count: 0, descendants: false };
  return scope.kind === "issue" ? { count: marks.blocking || 0, descendants: false } : { count: marks.blocking_with_descendants || 0, descendants: true };
}
