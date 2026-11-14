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
