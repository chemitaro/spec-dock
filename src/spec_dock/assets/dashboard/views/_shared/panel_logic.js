// Pure tab and sheet decisions shared by the Scope page and panel (iss-00587).
export function explanationState(details) {
  if (!details || details.catalog !== "ok") return "unreadable";
  const document = details.documents?.find((item) => item.key === "explanation");
  if (!document || document.exists === false) return "missing";
  return document.skeleton === true ? "skeleton" : "written";
}

export function defaultTab(details) {
  return explanationState(details) === "written" ? "explanation" : "summary";
}

export function pickTab(wanted, keys, details) {
  return keys.includes(wanted) ? wanted : defaultTab(details);
}

export function sheetHeights(viewHeight) {
  return {peek: 120, half: Math.round(viewHeight * 0.58), full: viewHeight};
}

export function settleSheet({height, velocity, heights}) {
  if (height < heights.peek - 48) return "closed";
  const snaps = ["peek", "half", "full"];
  if (velocity >= 0.5) return snaps.find((snap) => heights[snap] > height) ?? "full";
  if (velocity <= -0.5) return [...snaps].reverse().find((snap) => heights[snap] < height) ?? "peek";
  return snaps.reduce((nearest, snap) =>
    Math.abs(heights[snap] - height) < Math.abs(heights[nearest] - height) ? snap : nearest);
}

export function nextOnTap(snap) {
  return snap === "full" ? "half" : "full";
}

// Header band contents: only reasons that add to the state name, idle time, and merge state (iss-00656 D-01).
const PLAIN_REASONS = new Set(["closed", "in_progress", "no_waits"]);
const MERGE_WORDS = {needs_fix: "マージ待ち・直す必要あり", mergeable: "マージ待ち・マージできる"};

export function headerBand(scope, {idle = "", label = ""} = {}) {
  const text = String(scope?.reason?.text ?? "").trim();
  const plain = !text || text === label || PLAIN_REASONS.has(scope?.reason?.code);
  const merge = Object.hasOwn(MERGE_WORDS, scope?.merge) ? scope.merge : null;
  const reason = plain ? (merge ? MERGE_WORDS[merge] : "") : text;
  if (!reason && !idle && !merge) return null;
  return {reason, idle, merge};
}
