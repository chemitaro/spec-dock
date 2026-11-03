// 横断の概況（`/`）。#531 がこのファイルを書き換えて作る（Epic R-22、D-16）。
// この Issue では、表示中のリポジトリへのリンクだけを置く（「見た」は送らない）。
import { esc, ic } from "../core/ui.js";

export default {
  id: "overview",
  title: "横断の概況",
  icon: "globe",
  styles: [],
  render(root, ctx) {
    const items = ctx.repositories
      .map((item) => `<li><a data-repo href="${esc(ctx.href(item.path))}">${ic("folder")}<span>${esc(item.owner)}/${esc(item.name)}</span></a></li>`)
      .join("");
    root.innerHTML =
      `<section class="slot" data-slot="overview" aria-label="横断の概況">` +
      `<div class="slot__icon">${ic("globe")}</div><h1 class="slot__title">横断の概況</h1>` +
      `<p class="slot__note">リポジトリごとの札（#531 で作ります）。表示中のリポジトリ：${ctx.repositories.length}件</p>` +
      `<ul class="slot__list">${items}</ul></section>`;
  },
};
