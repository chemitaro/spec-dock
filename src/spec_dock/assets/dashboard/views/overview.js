// 横断の概況（`/`。iss-00531 D-08；Epic D-16、R-09、R-22）。表示中のリポジトリごとの札。札は各リポジトリの
// 構造の JSON から作り、「見た」は送らない（概況を開いても見たにしない。Epic R-29）。
import * as api from "../core/api.js";
import { ago } from "../core/ui.js";
import { boardCounts, byRank, overviewWarnings, stateCounts } from "./_shared/logic.js";
import { emptyState, esc, icon, legend, newTabLink, stateCountList, stateIcon, stateMark } from "./_shared/parts.js";

const REFRESH_MS = 60000;
const PER_SECTION = 3;

const results = new Map(); // repository -> {structure, failure, loadedAt}
let timer = null;
let mounted = null; // {root, ctx}
let loading = null;

async function load(repositories) {
  await Promise.all(
    repositories.map(async (item) => {
      try {
        const structure = await api.structure(item.repository, null);
        results.set(item.repository, { structure, failure: null, loadedAt: performance.now() });
      } catch (error) {
        results.set(item.repository, { structure: null, failure: error.message, loadedAt: performance.now() });
      }
      if (mounted) draw(mounted.root, mounted.ctx); // draw each card as soon as it arrives
    }),
  );
}

function refresh(ctx) {
  if (loading) return loading;
  loading = load(ctx.repositories).finally(() => {
    loading = null;
  });
  return loading;
}

// Each Issue in progress shows its progress ring (iss-00574 R-03; still: a list never moves).
function section(state, label, items, iconHtml, byId = null) {
  const list = items.length
    ? items
        .slice(0, PER_SECTION)
        .map((item) => `<li>${byId ? stateMark(item, byId, { label: false }) : ""}<small>#${esc(item.number)}</small>${esc(item.title)}</li>`)
        .join("") + (items.length > PER_SECTION ? `<li class="sd-none">ほか ${items.length - PER_SECTION}件</li>` : "")
    : `<li class="sd-none">ない</li>`;
  return `<div class="sd-ov__sec" data-st="${state}"><h3>${iconHtml}${label}<b>${items.length}</b></h3><ul>${list}</ul></div>`;
}

// The card's human tasks (iss-00554 D-06; Epic R-13): open and overdue, the counts of `dashboard summary`.
function todoFlags(structure) {
  const todos = structure?.todos;
  if (!todos) return "";
  if (todos.status !== "ok") {
    return `<span class="sd-badge" data-tone="warning" data-todos="unavailable" title="${esc(todos.problem?.message ?? "")}">${icon("person")}人のタスクが読めない</span>`;
  }
  return (
    `<span class="sd-badge" data-tone="${todos.open ? "accent" : ""}" data-todos="open">${icon("person")}人のタスク ${esc(todos.open)}</span>` +
    `<span class="sd-badge" data-tone="${todos.overdue ? "danger" : ""}" data-todos="overdue">${icon(todos.overdue ? "alert" : "clock")}期限切れ ${esc(todos.overdue)}</span>`
  );
}

function repoCard(item, ctx) {
  const result = results.get(item.repository);
  const name = item.owner + "/" + item.name; // escaped where it is written
  const href = ctx.href(item.path);
  if (!result) {
    return `<a class="sd-ov" data-repo="${esc(item.repository)}" href="${esc(href)}" aria-busy="true"><div class="sd-ov__head"><span class="sd-ov__icon">${icon("folder")}</span><p class="sd-ov__name">${esc(name)}</p></div><p class="sd-muted">読み込んでいます…</p></a>`;
  }
  const { structure, failure } = result;
  const warnings = overviewWarnings(structure, failure);
  const band = warnings.length
    ? `<div class="sd-ov__warn">${warnings
        .map(
          (warning) =>
            `<p data-level="${warning.level}">${icon(warning.level === "info" ? "info" : "zap")}<span>${esc(warning.text)}${warning.next.length ? `<span class="sd-ov__next">次の1手：${warning.next.map((step) => `<code>${esc(step)}</code>`).join("、")}</span>` : ""}</span></p>`,
        )
        .join("")}</div>`
    : "";
  const scopes = structure?.scopes || [];
  const snapshot = structure?.snapshot;
  const age = snapshot?.age_seconds == null ? null : snapshot.age_seconds + (performance.now() - result.loadedAt) / 1000;
  const stale = snapshot && (snapshot.stale || snapshot.status !== "ok");
  const status = snapshot?.fetched_at
    ? `<span class="sd-ov__time"${stale ? ' data-state="stale"' : ""} title="GitHub から構造を取得した時刻：${esc(snapshot.fetched_at)}">${esc(ago(age))}に取得</span>`
    : `<span class="sd-ov__time" data-state="stale">取得なし</span>`;
  let body = "";
  if (scopes.length) {
    const issues = scopes.filter((scope) => scope.kind === "issue");
    const lane = (name) => issues.filter((scope) => scope.lane === name).sort(byRank);
    const counts = stateCounts(issues.filter((scope) => scope.lane !== "awaiting_merge"));
    const board = boardCounts(scopes);
    const cleanup = (structure.cleanup || []).length;
    const changes = structure.changes_count || 0;
    body =
      `<div class="sd-ov__next">${section("merge", "マージ待ち", lane("awaiting_merge"), icon("branch"))}${section("doing", "作業中", lane("doing"), stateIcon("doing", false), new Map(scopes.map((scope) => [scope.id, scope])))}${section("ready", "着手できる", lane("ready"), stateIcon("ready", false))}</div>` +
      `<div class="sd-ov__counts">${stateCountList(counts, { done: false })}<span class="sd-cnt" data-st="merge" title="マージ待ち ${board.merge}">${icon("branch")}<span class="vh">マージ待ち</span>${board.merge}</span><span class="sd-ov__frac">${board.done}<small>／${board.total} 終わった</small></span></div>` +
      `<div class="sd-ov__flags"><span class="sd-badge" data-tone="${board.blocked ? "blocked" : ""}">${stateIcon("blocked", false)}止められている ${board.blocked}</span><span class="sd-badge" data-tone="${cleanup ? "warning" : ""}">${icon("box")}片付けの候補 ${cleanup}</span><span class="sd-badge" data-tone="${changes ? "accent" : ""}" data-changes="${changes}">${icon("bell")}変化 ${changes}</span>${todoFlags(structure)}</div>`;
  }
  return (
    `<a class="sd-ov" data-repo="${esc(item.repository)}" href="${esc(href)}"${warnings.some((warning) => warning.level !== "info") ? ' data-warn="1"' : ""}>` +
    band +
    `<div class="sd-ov__head"><span class="sd-ov__icon">${icon("folder")}</span><p class="sd-ov__name">${esc(name)}</p>${status}</div>` +
    body +
    `</a>`
  );
}

function draw(root, ctx) {
  const repositories = ctx.repositories || [];
  const cards = repositories.map((item) => repoCard(item, ctx)).join("");
  root.innerHTML =
    `<div class="sd-page">${newTabLink(ctx)}` +
    `<div class="sd-page-head"><h1>横断の概況</h1><p>このPCで表示しているリポジトリ ${repositories.length}件。札を押すと、そのリポジトリの構造の図へ。</p></div>` +
    `<div class="sd-ctl">${legend()}</div>` +
    (repositories.length ? `<div class="sd-ov-grid">${cards}</div>` : emptyState("表示しているリポジトリがありません。`spec-dock dashboard list` で確かめてください。")) +
    `</div>`;
}

function render(root, ctx) {
  const first = mounted === null;
  mounted = { root, ctx };
  draw(root, ctx);
  if (first) {
    refresh(ctx);
    timer = setInterval(() => {
      if (!document.hidden && mounted) refresh(mounted.ctx);
    }, REFRESH_MS);
  }
}

export default {
  id: "overview",
  title: "横断の概況",
  icon: "globe",
  styles: ["/assets/views/_shared/parts.css", "/assets/views/overview.css"],
  render,
  dispose() {
    clearInterval(timer);
    timer = null;
    mounted = null;
  },
};
