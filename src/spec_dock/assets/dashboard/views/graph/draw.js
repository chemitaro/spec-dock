// The structure graph's parts as HTML (iss-00614 D-02): boxes, frames, folded groups, the tree's lines, the class of a
// dependency line, the state chips, the range buttons and the legend. Shared by the structure graph (views/graph.js)
// and the cross-repository structure (views/allgraph.js), which draws one graph per repository frame.
//
// Pure: the functions read no module state. The drawing context `V` is {data (the structure JSON), ix (index of its
// Scopes), desc (descendants(ix)), cleanup (Map id → cleanup candidate), range (the layout's range), path and sel
// (the selection, for the lines' classes)}; graph.js passes its own state.
import * as M from "./marks.js";
import { orcaSlot } from "../_shared/parts.js";

const { esc, ic, stateIcon, STATES } = M;

// The ranges of what is shown (iss-00603 D-05): value, label, icon and the short meaning in the title.
export const RANGES = [
  ["all", "全体", "layers", "終わったものも、片付けの候補も出す"],
  ["now", "いま", "clock", "開いている親の中の終わったものを灰色で出し、片付けの候補は畳む"],
  ["next", "これから", "sparkle", "着手できる・作業中・止められている・不明だけを出す"],
];

// The board's lane order (Epic R-13): blocked, ready, doing, awaiting merge (needs fix, mergeable), unknown.
export const HL = [
  ["blocked", "blocked", "止められている"],
  ["ready", "ready", "着手できる"],
  ["doing", "doing", "作業中"],
  ["fix", "merge", "直す必要あり"],
  ["ok", "merge", "マージできる"],
  ["unknown", "unknown", "不明"],
];

export function descendants(ix) {
  const memo = new Map();
  const walk = (id, seen = new Set()) => {
    if (memo.has(id)) return memo.get(id);
    seen.add(id);
    const out = [];
    for (const k of ix.kids.get(id) || []) {
      if (seen.has(k.id)) continue;
      out.push(k, ...walk(k.id, seen));
    }
    memo.set(id, out);
    return out;
  };
  return (id) => walk(id);
}

export const cleanupMap = (data) => new Map((data.cleanup || []).map((c) => [c.id, c]));

export function tally(V, id) {
  const cnt = { done: 0, doing: 0, ready: 0, blocked: 0, unknown: 0 };
  const list = V.desc(id);
  for (const d of list) cnt[d.state] = (cnt[d.state] || 0) + 1;
  return { cnt, total: list.length };
}

function maxOpenStage(V, parentId) {
  const kids = parentId ? V.ix.kids.get(parentId) || [] : V.data.scopes.filter((s) => !s.parent_id);
  return Math.max(1, ...kids.filter((k) => k.state !== "done").map((k) => k.stage?.open || 1));
}

// The cleanup candidate's mark (iss-00603 D-06): on frames in all and now, on boxes in all only, never in next.
const clnMark = (s, cleanup) =>
  cleanup.has(s.id) ? `<span class="cln" title="片付けの候補：${esc(cleanup.get(s.id).text)}" role="img" aria-label="片付けの候補">${ic("box")}</span>` : "";

export function boxHtml(V, s, n) {
  const { cleanup, range } = V;
  const of = s.state !== "done" ? maxOpenStage(V, s.parent_id) : 1;
  const stg = of >= 2 ? M.stageMark(s.stage?.open, of) : "";
  const human = M.humanCount(s);
  const label = `${s.id} ${s.title}。${STATES[s.state]?.label ?? s.state}（${s.reason?.text ?? ""}）${s.downstream ? `。後に続く ${s.downstream}件` : ""}${human.count ? `。人のタスク ${human.count}件が止めている${human.descendants ? "（配下を含む）" : ""}` : ""}`;
  const frame = n.type === "tframe";
  const cln = range === "all" ? clnMark(s, cleanup) : "";
  let marks;
  if (frame) {
    const { cnt, total } = tally(V, s.id);
    marks = `<div class="gx-marks">${M.sbar(cnt, total, 64)}${M.frac(cnt, total)}${M.counts(cnt)}${M.asMark(s.assurance)}${cln}${M.wtMark(s.state === "doing" ? s.branch : null)}${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  } else {
    marks = `<div class="gx-marks">${M.asMark(s.assurance)}${cln}${M.prMark(s.pr)}${M.wtMark(s.state === "doing" ? s.branch : null)}${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  }
  return (
    `<div class="gx-box${frame ? " is-frame" : ""}" data-id="${esc(s.id)}" data-st="${s.state}" role="button" tabindex="0" aria-label="${esc(label)}" style="${pos(n)}">` +
    M.chgMark(s.change) +
    `<span class="rt" title="大もとの待ち先：ここが進めば、選んだ箱へ続く待ちがほどける" role="img" aria-label="大もとの待ち先">${ic("target")}大もと</span>` +
    `<div class="gx-r1">${M.stateMark(s, V.ix.byId, { motion: true })}<span class="gx-id">${esc(s.id)}</span><span class="gx-no">#${s.number}</span>${stg}</div>` +
    `<div class="gx-ttl${frame ? " is-one" : ""}" title="${esc(s.title)}">${esc(s.title)}</div>` +
    marks +
    `<div class="gx-agents">${orcaSlot(s.id, "all")}</div>` +
    `</div>`
  );
}

export function frameHtml(V, s, n) {
  const { cleanup, range } = V;
  const { cnt, total } = tally(V, s.id);
  const ini = s.kind === "initiative";
  const head =
    `<div class="gx-fh" data-id="${esc(s.id)}" role="button" tabindex="0" aria-label="${esc(`${s.id} ${s.title}。${STATES[s.state]?.label ?? s.state}`)}">${M.stateMark(s, V.ix.byId, { motion: true })}` +
    (ini ? `<span class="gx-kicker">Initiative</span>` : "") +
    `<span class="ds-docid">${esc(s.id)}</span><span class="gx-fttl" title="${esc(s.title)}">${esc(s.title)}</span>${M.wtMark(s.state === "doing" ? s.branch : null)}<div class="gx-agents">${orcaSlot(s.id, "all")}</div></div>`;
  const meta =
    `<div class="gx-fm">${M.sbar(cnt, total, ini ? 150 : 84)}${M.frac(cnt, total)}${M.counts(cnt)}${M.asMark(s.assurance)}` +
    (range === "next" ? "" : clnMark(s, cleanup)) +
    `${M.hmMark(s)}${M.dnMark(s.downstream)}</div>`;
  return (
    `<section class="gx-frame ${ini ? "gx-ini" : "gx-epic"}${n.compact ? " is-compact" : ""}" data-id="${esc(s.id)}" data-st="${s.state}" style="${pos(n)}">` +
    M.chgMark(s.change) +
    `<span class="rt" title="大もとの待ち先" role="img" aria-label="大もとの待ち先">${ic("target")}大もと</span>` +
    head +
    meta +
    `</section>`
  );
}

export function chipHtml(V, g) {
  const names = g.ids.map((id) => `${id} ${V.ix.byId.get(id)?.title ?? ""}`).join("、");
  return (
    `<button type="button" class="gx-clean" data-clean="${esc(g.key)}" data-ids="${esc(g.ids.join(" "))}" style="${pos(g)}" title="片付けの候補：${esc(names)}" aria-label="片付けの候補 ${g.ids.length}件（押すと一覧）">` +
    `${ic("box")}<b>${g.ids.length}</b><span>片付けの候補</span></button>`
  );
}

export const pos = (r) => `left:${r.x1}px;top:${r.y1}px;width:${r.x2 - r.x1}px;height:${r.y2 - r.y1}px`;

// The tree's parent lines of a layout (its trunks), as the paths of one svg.
export function treeSvgPaths(trunks) {
  return trunks
    .map((t) =>
      t.lane === "v"
        ? `<path d="M${(t.x1 + t.x2) / 2} ${t.y1}V${t.y2}"/>`
        : `<path d="M${t.x1} ${(t.y1 + t.y2) / 2}H${t.x2}"/>`,
    )
    .join("");
}

export function edgeClass(V, e) {
  const base = e.done ? "is-done" : "is-wait";
  const P = V.path;
  if (!P) return base;
  let lv = 9;
  for (const [b, n] of e.pairs) {
    if ((n === V.sel && P.upDirect.has(b)) || (b === V.sel && P.downDirect.has(n))) lv = Math.min(lv, 1);
    else if (P.related.has(b) && P.related.has(n)) lv = Math.min(lv, 2);
  }
  return `${base}${lv === 1 ? " is-p1" : lv === 2 ? " is-p2" : " is-off"}`;
}

// The open Issues of each state chip, counted into `n` ({key: count}, the keys of HL).
export function hlCounts(scopes, n = Object.fromEntries(HL.map(([key]) => [key, 0]))) {
  for (const s of scopes) {
    if (s.kind !== "issue" || s.state === "done") continue;
    if (s.merge === "mergeable") n.ok++;
    else if (s.merge === "needs_fix") n.fix++;
    else if (s.lane in n) n[s.lane]++;
  }
  return n;
}

// The state chips above the graph (they only highlight): `pressed(key)` tells the pressed one.
export function chipsHtml(n, pressed) {
  const chipBtn = ([key, st, label], extra) =>
    `<button type="button" class="nx" data-st="${st}" data-hl="${key}" aria-pressed="${pressed(key)}" title="${label}の Issue を図の中で目立たせる">${extra || stateIcon(st, false)}<span class="lab">${label}</span><b>${n[key]}</b></button>`;
  return (
    chipBtn(HL[0]) +
    chipBtn(HL[1]) +
    chipBtn(HL[2]) +
    `<span class="nx-grp" role="group" aria-label="マージ待ち"><span class="nx-grp__lab">${ic("branch")}<span class="lab">マージ待ち</span></span>${chipBtn(HL[3], ic("zap"))}${chipBtn(HL[4], ic("check"))}</span>` +
    (n.unknown ? chipBtn(HL[5]) : "")
  );
}

// The toolbar's zoom group and its range group.
export const zoomHtml = (s) =>
  `<span class="tool-group"><button type="button" class="tool is-icon" data-act="zout" aria-label="縮小">${ic("minus")}</button><button type="button" class="tool zoomval" data-act="z100" title="100% に戻す">${Math.round(s * 100)}%</button><button type="button" class="tool is-icon" data-act="zin" aria-label="拡大">${ic("plus")}</button></span>`;
export const rangesHtml = (range) =>
  `<span class="tool-group" role="group" aria-label="見せる範囲">` +
  RANGES.map(([v, label, icon, title]) => `<button type="button" class="tool" data-act="range" data-range="${v}" aria-pressed="${range === v}" title="見せる範囲：${label}（${title}）">${ic(icon)}<span class="lab">${label}</span></button>`).join("") +
  `</span>`;

// iss-00616 D-05: cmd adds the command lines' rows to "そのほか" (the structure graph with Orca); off by default, so the
// shared legend of the cross-repository structure stays as it is.
export function renderLegend(el, open, { cmd = false } = {}) {
  const li = (a, b, wide) => `<li${wide ? ' class="wide"' : ""}><span>${a}</span>${b}</li>`;
  el.dataset.open = String(open);
  el.innerHTML =
    `<button type="button" class="legend__head" data-act="legend" aria-expanded="${open}">${ic("info")}凡例${ic("chevronRight")}</button><div class="legend__body">` +
    `<div class="lg-grp"><h4>状態</h4><ul>${["blocked", "ready", "doing", "unknown", "done"].map((s) => li(s === "doing" ? stateIcon(s, false, { progress: { done: 3, total: 8 } }) : stateIcon(s, false), s === "doing" ? "作業中（区切り＝計画の手順、緑＝終わった。30分以内に動いたら次が点滅）" : STATES[s].label, s === "doing")).join("")}${li('<span class="sbar" style="width:26px"><i data-st="done" style="width:60%"></i><i data-st="doing" style="width:20%"></i><i data-st="ready" style="width:20%"></i></span>', "配下の内訳")}</ul></div>` +
    `<div class="lg-grp"><h4>PR と CI</h4><ul>${li(`<span class="pr" data-pr="open">${ic("branch")}</span>`, "開いている")}${li(`<span class="pr" data-pr="draft">${ic("branch")}</span>`, "下書き")}${li(`<span class="pr" data-pr="merged">${ic("merge")}</span>`, "マージ済み")}${li(`<span class="pr" data-pr="closed">${ic("prClosed")}</span>`, "閉じた")}` +
    `${li('<span class="ci" data-ci="success"></span>', "CI 成功")}${li('<span class="ci" data-ci="failure"></span>', "CI 失敗")}${li('<span class="ci" data-ci="running"></span>', "CI 実行中")}${li(`<span class="mg" data-mg="ok">${ic("check")}</span>`, "マージできる")}${li(`<span class="mg" data-mg="conflict">${ic("zap")}</span>`, "衝突")}</ul></div>` +
    `<div class="lg-grp"><h4>保証</h4><ul>${M.AS_LEVELS.map((l) => li(M.asMark(l), l)).join("")}</ul></div>` +
    `<div class="lg-grp"><h4>そのほか</h4><ul>${li('<span class="lg-chg"></span>', "前回から変化")}${li(`<span class="wt">${ic("folder")}</span>`, "worktree あり")}${li('<span class="stg">2</span>', "進める段")}${li(`<span class="dn">${ic("down")}3</span>`, "後に続く数")}${li(`<span class="hm">${ic("person")}人 2</span>`, "人のタスクが止めている数（枠は配下も）")}${li(`<span class="cln">${ic("box")}</span>`, "片付けの候補（全体では箱と枠に印、いまでは畳んで1つに、これからでは出さない）", 1)}${li('<span class="lg-line"></span>', "待っている依存", 1)}${li('<span class="lg-line is-done"></span>', "終わった依存", 1)}${li('<span class="lg-tree"></span>', "親子（木）", 1)}${cmd ? li('<span class="lg-cmd"></span>', "指揮（親 → 子）", 1) + li('<span class="lg-cr"></span>', "指揮している親（波紋）") : ""}</ul></div>` +
    `<div class="lg-grp"><h4>箱を選んだとき</h4><ul>${li('<span class="lg-box is-sel"></span>', "選んだ箱（1つだけ）")}${li('<span class="lg-line is-p1"></span>', "直接の依存", 1)}${li('<span class="lg-line is-p2"></span>', "間接（2段目より先）", 1)}${li('<span class="lg-line is-off"></span><span class="lg-box is-off"></span>', "関係ない")}${li(`<span class="rt lg-rt">${ic("target")}大もと</span>`, "大もとの待ち先")}${li(ic("arrowRight"), "矢印：選んだ箱へ入る線＝待ち先、出る線＝後に続く", 1)}</ul></div>` +
    `</div>`;
}
