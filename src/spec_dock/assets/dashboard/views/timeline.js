// The time axis (iss-00532; Epic R-16, D-08): cumulative created and closed Scopes per week for the chosen kinds,
// and the recent Scope and pull request events. The model counts (#528 weekly_totals, recent_events); this screen
// adds the chosen kinds up (timeline/series.js) and draws.
import { esc, ic, stateIcon } from "../core/ui.js";
import { emptyText } from "./graph.js";
import { groupEvents, mergeWeeks } from "./timeline/series.js";

const KINDS = [
  ["initiative", "Initiative"],
  ["epic", "Epic"],
  ["issue", "Issue"],
];
const PREFS = "specdock.timeline.v1";
const EVENT = {
  created: ["sparkle", "が作られた"],
  closed: ["check", "が終わった"],
  pr_opened: ["branch", "の PR が開いた"],
  pr_merged: ["merge", "の PR がマージされた"],
};

const T = { kinds: new Set(KINDS.map(([k]) => k)), root: null, ctx: null, weeks: [], resize: null, change: null };

const icon = (name) => ic(name);

function loadPrefs() {
  try {
    const saved = JSON.parse(localStorage.getItem(PREFS) || "null");
    if (Array.isArray(saved) && saved.length) T.kinds = new Set(saved.filter((k) => KINDS.some(([name]) => name === k)));
  } catch {
    // keep every kind
  }
}

function savePrefs() {
  try {
    localStorage.setItem(PREFS, JSON.stringify([...T.kinds]));
  } catch {
    // ignore
  }
}

const day = (iso) => {
  const d = new Date(`${iso}T00:00:00`);
  return `${d.getMonth() + 1}月${d.getDate()}日`;
};
const time = (iso) => new Date(iso).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" });

function chartSvg(weeks, W) {
  const H = Math.round(Math.min(300, Math.max(200, W * 0.42)));
  const L = 38;
  const R = 70;
  const top = 14;
  const B = 26;
  const iw = W - L - R;
  const ih = H - top - B;
  const max = Math.max(1, ...weeks.map((w) => w.created));
  const step = max > 200 ? 100 : max > 60 ? 20 : max > 20 ? 5 : 2;
  const ymax = Math.ceil(max / step) * step;
  const X = (i) => L + (weeks.length > 1 ? (i / (weeks.length - 1)) * iw : iw / 2);
  const Y = (v) => top + ih - (v / ymax) * ih;
  let g = "";
  for (let v = 0; v <= ymax; v += step) g += `<line class="grid" x1="${L}" x2="${L + iw}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${L - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`;
  let month = -1;
  weeks.forEach((w, i) => {
    const m = Number(w.week_start.slice(5, 7));
    if (m !== month) {
      month = m;
      g += `<line class="axis" x1="${X(i)}" x2="${X(i)}" y1="${top + ih}" y2="${top + ih + 4}"/><text x="${X(i)}" y="${H - 6}" text-anchor="middle">${m}月</text>`;
    }
  });
  const line = (k) => weeks.map((w, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(w[k]).toFixed(1)}`).join("");
  const area =
    weeks.map((w, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(w.created).toFixed(1)}`).join("") +
    weeks
      .slice()
      .reverse()
      .map((w, j) => `L${X(weeks.length - 1 - j).toFixed(1)} ${Y(w.closed).toFixed(1)}`)
      .join("") +
    "Z";
  const last = weeks[weeks.length - 1];
  const lx = X(weeks.length - 1);
  return (
    `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="週ごとの作成と完了の累計。最新の週は作成 ${last.created}、完了 ${last.closed}">` +
    `<line class="axis" x1="${L}" x2="${L + iw}" y1="${top + ih}" y2="${top + ih}"/>${g}` +
    `<path class="tl-area" d="${area}"/>` +
    `<path class="tl-line is-created" d="${line("created")}"/>` +
    `<path class="tl-line is-closed" d="${line("closed")}"/>` +
    `<circle class="tl-dot is-created" cx="${lx}" cy="${Y(last.created)}" r="3.5"/><circle class="tl-dot is-closed" cx="${lx}" cy="${Y(last.closed)}" r="3.5"/>` +
    `<text class="lbl" x="${lx + 8}" y="${Y(last.created) + 4}">作成 ${last.created}</text>` +
    `<text class="lbl" x="${lx + 8}" y="${Math.max(Y(last.closed) + 4, Y(last.created) + 20)}">完了 ${last.closed}</text>` +
    `<line class="axis tl-hair" x1="0" x2="0" y1="${top}" y2="${top + ih}"/>` +
    `<rect class="tl-hov" x="${L}" y="${top}" width="${iw}" height="${ih}" fill="transparent"/></svg>`
  );
}

function drawChart() {
  const el = T.root?.querySelector(".chart");
  if (!el) return;
  const weeks = T.weeks;
  if (!weeks.length) {
    el.innerHTML = `<p class="tl-none">数える Scope がありません。</p>`;
    return;
  }
  const W = Math.max(280, Math.floor(el.clientWidth));
  el.innerHTML = chartSvg(weeks, W) + `<div class="chart-tip" role="status"></div>`;
  const svg = el.querySelector("svg");
  const hov = el.querySelector(".tl-hov");
  const hair = el.querySelector(".tl-hair");
  const tip = el.querySelector(".chart-tip");
  const L = 38;
  const iw = W - L - 70;
  const show = (e) => {
    const b = svg.getBoundingClientRect();
    const sc = W / b.width;
    const x = (e.clientX - b.left) * sc;
    const i = weeks.length > 1 ? Math.max(0, Math.min(weeks.length - 1, Math.round(((x - L) / iw) * (weeks.length - 1)))) : 0;
    const X = L + (weeks.length > 1 ? (i / (weeks.length - 1)) * iw : iw / 2);
    hair.setAttribute("x1", X);
    hair.setAttribute("x2", X);
    hair.style.opacity = 1;
    const w = weeks[i];
    tip.innerHTML = `${day(w.week_start)}の週<br>作成 ${w.created}・完了 ${w.closed}・開いている ${w.created - w.closed}`;
    tip.style.left = `${Math.max(70, Math.min(b.width - 70, X / sc))}px`;
    tip.style.top = "40px";
    tip.style.opacity = 1;
  };
  hov.addEventListener("pointermove", show);
  hov.addEventListener("pointerdown", show);
  hov.addEventListener("pointerleave", () => {
    hair.style.opacity = 0;
    tip.style.opacity = 0;
  });
}

function feedHtml(data, ctx) {
  const groups = groupEvents(data.timeline?.events || [], data.scopes);
  if (!groups.length) return `<p class="tl-none">まだ動きがありません。</p>`;
  return `<ul class="feed">${groups
    .map(
      (g) =>
        `<li class="feed__day">${day(g.day)}</li>` +
        g.items
          .map((e) => {
            const [name, words] = EVENT[e.kind] || ["info", ""];
            const pr = e.kind.startsWith("pr_") ? `（#${e.number}）` : "";
            const body = `<span class="ev__ic" data-k="${esc(e.kind)}">${icon(name)}</span><span class="ev__txt"><b>${esc(e.scope_id)}</b>${words}${pr}<small>${esc(e.scope?.title ?? "")}</small></span><span class="ev__time">${esc(time(e.at))}</span>`;
            return e.scope ? `<li><a class="ev" data-nav href="${esc(ctx.href(e.scope.path))}">${body}</a></li>` : `<li><span class="ev">${body}</span></li>`;
          })
          .join(""),
    )
    .join("")}</ul>`;
}

function render(root, ctx) {
  if (T.root !== root) {
    T.root = root;
    loadPrefs();
    T.resize = () => drawChart();
    window.addEventListener("resize", T.resize);
    T.change = (e) => {
      const kind = e.target.dataset?.kind;
      if (!kind) return;
      if (e.target.checked) T.kinds.add(kind);
      else T.kinds.delete(kind);
      savePrefs();
      render(root, T.ctx);
    };
    root.addEventListener("change", T.change); // root is the shell's <main>: removed again in dispose
  }
  T.ctx = ctx;
  const data = ctx.data;
  if (!data || !Array.isArray(data.scopes) || !data.scopes.length) {
    root.innerHTML = `<div class="tl"><p class="gx-empty-text">${esc(emptyText(data))}</p></div>`;
    return;
  }
  const chosen = KINDS.map(([k]) => k).filter((k) => T.kinds.has(k));
  T.weeks = mergeWeeks(data.timeline?.weeks_by_kind || {}, chosen);
  const last = T.weeks[T.weeks.length - 1] || { created: 0, closed: 0 };
  const before = T.weeks[Math.max(0, T.weeks.length - 5)] || { closed: 0 };
  const repo = (ctx.repository || "").split("/").slice(1).join("/");
  const metric = (label, value, iconHtml) =>
    `<div class="ds-metric"><div class="ds-metric__label">${iconHtml}${label}</div><div class="ds-metric__value">${value}</div></div>`;
  root.innerHTML =
    `<div class="tl"><div class="page-head"><h1>時間の軸</h1><p>${esc(repo)}・週ごとの累計と、最近の動き</p></div>` +
    `<div class="ds-metrics">` +
    metric("作られた（累計）", last.created, icon("sparkle")) +
    metric("終わった（累計）", last.closed, stateIcon("done", false)) +
    metric("開いている", last.created - last.closed, ic("layers")) +
    metric("直近4週の完了", last.closed - (T.weeks.length > 4 ? before.closed : 0), ic("history")) +
    `</div>` +
    `<div class="time-grid"><section class="chart-card"><h3>作成と完了の累計（週ごと）</h3><p>2本の線の間の幅が、開いている Scope の数。週は月曜から。</p>` +
    `<div class="tl-kinds" role="group" aria-label="数える種類">${KINDS.map(([k, label]) => `<label><input type="checkbox" data-kind="${k}"${T.kinds.has(k) ? " checked" : ""}>${label}</label>`).join("")}</div>` +
    `<div class="chart-legend"><span><i class="is-created"></i>作られた</span><span><i class="is-closed"></i>終わった</span></div>` +
    `<div class="chart"></div></section>` +
    `<section class="chart-card"><h3>最近の動き</h3><p>新しい順。Scope の作成と完了、PR が開いた・マージされた。</p>${feedHtml(data, ctx)}</section></div></div>`;
  drawChart();
}

function dispose() {
  if (T.resize) window.removeEventListener("resize", T.resize);
  if (T.root && T.change) T.root.removeEventListener("change", T.change);
  T.root = null;
  T.resize = null;
  T.change = null;
}

export default {
  id: "timeline",
  title: "時間の軸",
  icon: "history",
  styles: ["/assets/views/timeline.css"],
  render,
  dispose,
};
