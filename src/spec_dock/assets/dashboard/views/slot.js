// A placeholder for a screen that a later Issue fills (iss-00529). Shows what the slot will hold and how many
// Scopes the structure has, so the shell can be checked end to end.
import { esc, ic } from "../core/ui.js";

export function emptySlot({ id, title, icon, owner, note }) {
  return {
    id,
    title,
    icon,
    styles: [],
    render(root, ctx) {
      const count = ctx.data ? ctx.data.scopes.length : 0;
      const scope = ctx.route.scope ? `<p class="slot__scope"><span class="ds-docid">${esc(ctx.route.scope)}</span></p>` : "";
      root.innerHTML =
        `<section class="slot" data-slot="${esc(id)}" aria-label="${esc(title)}">` +
        `<div class="slot__icon">${ic(icon)}</div>` +
        `<h1 class="slot__title">${esc(title)}</h1>${scope}` +
        `<p class="slot__note">${esc(note)}（${esc(owner)} で作ります）</p>` +
        (ctx.data ? `<p class="slot__count">このリポジトリの Scope：${count}件</p>` : "") +
        `</section>`;
    },
  };
}
