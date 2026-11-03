// Shared small parts for the shell and the screens (iss-00529). Screens may import these; the shapes and
// labels follow the adopted design d2 (Epic D-07): doing = half circle, ready = triangle, blocked = octagon,
// unknown = diamond, done = grey check.

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
