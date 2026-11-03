// The time axis' data (iss-00532 D-06). Pure functions over the structure API's `timeline`: no DOM.
// The model (#528 `weekly_totals`, `recent_events`) counts; these only combine the kinds and group by day.

/**
 * Cumulative created and closed counts per week for the chosen kinds. `weeksByKind[kind]` is the model's list of
 * {week_start, created, closed} for one kind; before a kind's first week it counts 0, after its last week its last
 * value. Returns [{week_start, created, closed}] over the union of the weeks.
 */
export function mergeWeeks(weeksByKind, kinds) {
  const lists = kinds.map((kind) => weeksByKind?.[kind] || []).filter((list) => list.length);
  const weeks = [...new Set(lists.flatMap((list) => list.map((w) => w.week_start)))].sort();
  const at = lists.map(() => -1);
  return weeks.map((week) => {
    let created = 0;
    let closed = 0;
    lists.forEach((list, k) => {
      while (at[k] + 1 < list.length && list[at[k] + 1].week_start <= week) at[k]++;
      if (at[k] >= 0) {
        created += list[at[k]].created;
        closed += list[at[k]].closed;
      }
    });
    return { week_start: week, created, closed };
  });
}

/** The day (YYYY-MM-DD) of an ISO time in a time zone (the browser's when omitted). */
export function dayOf(iso, timeZone) {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date(iso));
  const get = (type) => parts.find((p) => p.type === type).value;
  return `${get("year")}-${get("month")}-${get("day")}`;
}

/**
 * The recent events, newest first as the model gives them, grouped by day, each with its Scope
 * ({id, title, kind, path}, or null when the Scope is not in the structure).
 */
export function groupEvents(events, scopes, timeZone) {
  const byId = new Map((scopes || []).map((s) => [s.id, s]));
  const groups = [];
  for (const event of events || []) {
    const day = dayOf(event.at, timeZone);
    let group = groups[groups.length - 1];
    if (!group || group.day !== day) {
      group = { day, items: [] };
      groups.push(group);
    }
    const scope = byId.get(event.scope_id);
    group.items.push({ ...event, scope: scope ? { id: scope.id, title: scope.title, kind: scope.kind, path: scope.path } : null });
  }
  return groups;
}
