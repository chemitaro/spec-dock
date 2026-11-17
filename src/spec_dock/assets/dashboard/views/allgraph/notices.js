// The cross-repository structure's notices (iss-00632 D-02): the warnings of overviewWarnings whose text is fixed by
// their kind are gathered once per kind for the page, naming the repositories they apply to; the rest (a reason a
// repository could not be read, the two clones' text) stay in their repository's frame. Every warning of a repository
// the screen cannot draw (failed) is its reason and stays in its frame. Pure computation: no DOM.

/** The kinds the page's summary takes, in its order within a level, with the row's heading. */
export const SHARED = {
  "snapshot-missing": "構造のスナップショットがありません",
  "snapshot-unsupported": "構造のスナップショットが知らない版です（SpecDock を更新してください）",
  "snapshot-unreadable": "構造のスナップショットが読めません",
  stale: "構造が更新されていません",
  anomalies: "構造の異常があります",
  "pr-unknown": "PR の状態が分かりません",
};
const LEVELS = ["error", "warning", "info"];
const KINDS = Object.keys(SHARED);

/**
 * @param repos [{repository, owner, name, failed, warnings}] in the list's order (warnings: overviewWarnings' result,
 *              or null while loading, not counted; failed: every warning stays in the frame)
 * @returns {summary: [{kind, level, text, next, repos: [{repository, label, detail?}]}],
 *           own: Map(repository → the warnings kept in its frame)}
 */
export function splitNotices(repos) {
  const names = new Map();
  for (const r of repos) {
    const name = r.name || r.repository;
    names.set(name, (names.get(name) || 0) + 1);
  }
  const label = (r) => {
    const name = r.name || r.repository;
    return names.get(name) > 1 && r.owner ? `${r.owner}/${name}` : name;
  };
  const rows = new Map();
  const own = new Map();
  for (const r of repos) {
    if (!Array.isArray(r.warnings)) continue;
    const kept = [];
    for (const w of r.warnings) {
      if (r.failed || !(w.kind in SHARED)) {
        kept.push(w);
        continue;
      }
      let row = rows.get(w.kind);
      if (!row) {
        row = { kind: w.kind, level: w.level, text: SHARED[w.kind], next: w.next || [], repos: [] };
        rows.set(w.kind, row);
      }
      row.repos.push({ repository: r.repository, label: label(r), ...(w.detail ? { detail: w.detail } : {}) });
    }
    own.set(r.repository, kept);
  }
  const rank = (row) => [LEVELS.indexOf(row.level), KINDS.indexOf(row.kind)];
  const summary = [...rows.values()].sort((a, b) => {
    const [la, ka] = rank(a);
    const [lb, kb] = rank(b);
    return la - lb || ka - kb;
  });
  return { summary, own };
}
