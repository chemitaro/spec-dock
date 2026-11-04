// Shared small parts for the shell and the screens (iss-00529). Screens may import these; the shapes and
// labels follow the adopted design d2 (Epic D-07): doing = half circle, ready = triangle, blocked = octagon,
// unknown = diamond, done = grey check. The one home of the marks' values (iss-00544): every icon shape, the
// state, kind and pull request words and the assurance steps; the screens' parts draw with these.

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

export const STATES = {
  ready: { label: "着手できる", shape: '<path d="M7 4.2 20.2 12 7 19.8z" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>' },
  doing: { label: "作業中", shape: '<circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M12 6.2a5.8 5.8 0 0 1 0 11.6z" fill="currentColor"/>' },
  blocked: { label: "止められている", shape: '<path d="M8.1 2.6h7.8l5.5 5.5v7.8l-5.5 5.5H8.1l-5.5-5.5V8.1z" fill="currentColor"/><path class="on" d="M7.6 12h8.8"/>' },
  unknown: { label: "不明", shape: '<path d="M12 1.8 22.2 12 12 22.2 1.8 12z" fill="currentColor"/><path class="on" style="stroke-width:2.2" d="M9.9 9.7a2.2 2.2 0 1 1 3.1 2c-.6.3-1 .8-1 1.4v.3M12 16.4v.1"/>' },
  done: { label: "終わった", shape: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path class="on" d="m7.6 12.3 3 3 5.8-6.2"/>' },
};

// The five states in words, from STATES.
export const STATE_WORDS = Object.fromEntries(Object.entries(STATES).map(([state, item]) => [state, item.label]));

export const KIND_LABEL = { initiative: "Initiative", epic: "Epic", issue: "Issue" };

// Assurance steps (Epic R-15): 1 to 4 bars.
export const ASSURANCE_LEVELS = { light: 1, standard: 2, strict: 3, critical: 4 };

export const PR_STATE_WORDS = { open: "開いている", draft: "下書き", merged: "マージ済み", closed: "閉じた" };

export const stateIcon = (state, label = true) =>
  `<svg class="st-ico" data-st="${state}" viewBox="0 0 24 24" ${label ? `role="img" aria-label="${STATES[state]?.label ?? state}"` : 'aria-hidden="true"'}>${STATES[state]?.shape ?? ""}</svg>`;

export const chip = (state) => `<span class="chip" data-st="${state}">${stateIcon(state, false)}${esc(STATES[state]?.label ?? state)}</span>`;

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
