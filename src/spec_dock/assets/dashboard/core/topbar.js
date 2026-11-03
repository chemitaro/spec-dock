// The top band (Epic D-07, R-03, R-09, R-17): brand and repository switcher (hidden when embedded), the three
// screen tabs, a search slot (#531 fills it), the change count and the fetch time; notices go below the band.
import { ago, esc, ic } from "./ui.js";
import { repositoryPath, withEmbed } from "./route.js";

export const TABS = [
  ["graph", "構造の図", "layers"],
  ["board", "ボード", "table"],
  ["timeline", "時間の軸", "history"],
];

export function renderTop(target, mobileTabs, state) {
  const { route, repositories, data } = state;
  const repo = route.repository;
  const current = route.view;
  const tabs = repo
    ? TABS.map(
        ([view, label, icon]) =>
          `<a class="tab" role="tab" data-nav href="${esc(withEmbed(repositoryPath(repo, view), route.embed))}" aria-selected="${current === view}">${ic(icon)}<span>${label}</span></a>`,
      ).join("")
    : "";
  const items = (repositories || [])
    .map(
      (item) =>
        `<li><a role="menuitem" href="${esc(item.path)}"${item.repository === repo ? ' aria-current="page"' : ""}>${ic("folder")}<span>${esc(item.owner)}/${esc(item.name)}</span></a></li>`,
    )
    .join("");
  const name = repo ? repo.split("/").slice(1).join("/") : "すべてのリポジトリ";
  const snapshot = data?.snapshot;
  const stale = snapshot && (snapshot.stale || snapshot.status !== "ok");
  const changes = data?.changes_count || 0;
  target.innerHTML =
    `<span class="brand embed-hide"><a href="/" class="brand__link" aria-label="横断の概況"><span class="brand__mark">S</span><span class="brand__name">SpecDock</span></a></span>` +
    `<div class="repo embed-hide">` +
    `<button type="button" class="repo-btn" id="repo-btn" aria-haspopup="menu" aria-expanded="false">${ic(repo ? "folder" : "globe")}<span>${esc(name)}</span>${ic("chevronDown")}</button>` +
    `<ul class="repo-menu" id="repo-menu" role="menu" hidden><li><a role="menuitem" href="/">${ic("globe")}<span>すべてのリポジトリ</span></a></li>${items}</ul>` +
    `</div>` +
    (tabs ? `<nav class="tabs" role="tablist" aria-label="画面の切り替え">${tabs}</nav>` : "") +
    `<div class="top__right">` +
    `<div class="search-slot" id="search-slot"></div>` +
    (repo
      ? `<span class="iconbtn changes" title="前回見たときからの変化" aria-label="前回から変化 ${changes}件">${ic("bell")}${changes ? `<span class="num">${changes}</span>` : ""}</span>`
      : "") +
    (repo
      ? `<span class="status"${stale ? ' data-state="stale"' : ""} title="GitHub から構造を取得した時刻${snapshot?.fetched_at ? `：${esc(snapshot.fetched_at)}` : ""}"><span>${snapshot?.fetched_at ? esc(ago(snapshot.age_seconds)) : "取得なし"}<span class="status__w">に取得</span></span></span>`
      : "") +
    `</div>`;
  mobileTabs.innerHTML = tabs;
  mobileTabs.hidden = !tabs;
  const button = target.querySelector("#repo-btn");
  const menu = target.querySelector("#repo-menu");
  button.addEventListener("click", () => {
    const open = menu.hidden;
    menu.hidden = !open;
    button.setAttribute("aria-expanded", String(open));
  });
}

// One listener for the page: a click outside the switcher closes its menu.
document.addEventListener("click", (event) => {
  const menu = document.getElementById("repo-menu");
  if (menu && !menu.hidden && !event.target.closest(".repo")) {
    menu.hidden = true;
    document.getElementById("repo-btn")?.setAttribute("aria-expanded", "false");
  }
});

export function renderNotices(target, data, error) {
  const notices = [...(data?.notices || [])];
  if (error) notices.unshift({ code: "LOAD_FAILED", level: "error", text: error, next_steps: ["spec-dock dashboard list"] });
  target.innerHTML = notices
    .map(
      (item) =>
        `<div class="notice" data-level="${esc(item.level)}" data-code="${esc(item.code)}">${ic(item.level === "info" ? "info" : "zap")}<p>${esc(item.text)}${
          item.next_steps?.length ? ` <span class="notice__next">次の1手：${item.next_steps.map((step) => `<code>${esc(step)}</code>`).join("、")}</span>` : ""
        }</p></div>`,
    )
    .join("");
  target.hidden = notices.length === 0;
}
