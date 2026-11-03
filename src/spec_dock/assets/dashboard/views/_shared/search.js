// 上の帯の検索（iss-00531 D-09；Epic R-17）。今のリポジトリの Scope を ID、番号、題名で探し、詳しい画面へ移る。
// 骨組みの app.js が render() のたびに mountSearch(slot, …) を呼ぶ。上の帯は描き直されるので、部品はここで
// 1回だけ作り、新しい #search-slot へ移す。骨組みは5秒ごとに上の帯だけを描き直し、そのときは mountSearch を
// 呼ばないので、上の帯を MutationObserver で見張って付け直す（入力の値とフォーカスを保つ）。
import { esc, ic, stateIcon } from "../../core/ui.js";
import { searchScopes } from "./logic.js";

let box = null; // the persistent search element
let current = { data: null, navigate: null, repository: null };
let results = [];
let active = -1;
let hadFocus = false; // survives the blur caused by the top band removing the element
let selection = [0, 0];
let observer = null;

const STYLE = "/assets/views/_shared/search.css";

function build() {
  if (!document.querySelector(`link[href="${STYLE}"]`)) {
    const sheet = document.createElement("link"); // the search shows on every screen, #532's included
    sheet.rel = "stylesheet";
    sheet.href = STYLE;
    document.head.append(sheet);
  }
  const element = document.createElement("div");
  element.className = "sd-search";
  element.innerHTML =
    `<button type="button" class="sd-search__open" aria-label="検索を開く" aria-expanded="false">${ic("search")}</button>` +
    `<div class="sd-search__field">${ic("search")}<input type="search" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="sd-search-list" aria-label="Scope を探す（ID・番号・題名）" placeholder="ID・番号・題名で探す" autocomplete="off" spellcheck="false"></div>` +
    `<ul class="sd-search__list" id="sd-search-list" role="listbox" aria-label="検索の候補" hidden></ul>`;
  const input = element.querySelector("input");
  const opener = element.querySelector(".sd-search__open");
  const list = element.querySelector("ul");
  const remember = () => {
    selection = [input.selectionStart ?? 0, input.selectionEnd ?? 0];
  };
  input.addEventListener("input", () => {
    remember();
    update(element);
  });
  input.addEventListener("keyup", remember);
  input.addEventListener("select", remember);
  input.addEventListener("focus", () => {
    hadFocus = true;
    update(element);
  });
  input.addEventListener("blur", () => {
    // A blur from the user leaves the element in the document; a removal by the redraw does not.
    queueMicrotask(() => {
      if (element.isConnected) hadFocus = false;
    });
  });
  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (!results.length) return;
      event.preventDefault();
      active = (active + (event.key === "ArrowDown" ? 1 : -1) + results.length) % results.length;
      paint(element);
    } else if (event.key === "Enter") {
      const hit = results[active >= 0 ? active : 0];
      if (hit) {
        event.preventDefault();
        go(element, hit);
      }
    } else if (event.key === "Escape") {
      close(element, true);
      input.blur();
    }
  });
  list.addEventListener("mousedown", (event) => event.preventDefault()); // keep the focus on the input
  list.addEventListener("click", (event) => {
    const option = event.target.closest("[data-index]");
    if (option) go(element, results[Number(option.dataset.index)]);
  });
  opener.addEventListener("click", () => {
    const open = !element.classList.contains("is-open");
    element.classList.toggle("is-open", open);
    opener.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
  });
  document.addEventListener("click", (event) => {
    if (!element.contains(event.target)) close(element, false);
  });
  return element;
}

function close(element, clear) {
  const input = element.querySelector("input");
  if (clear) input.value = "";
  results = [];
  active = -1;
  paint(element);
  element.classList.remove("is-open");
  element.querySelector(".sd-search__open").setAttribute("aria-expanded", "false");
}

function go(element, scope) {
  close(element, true);
  current.navigate?.(scope.path);
}

function update(element) {
  const input = element.querySelector("input");
  results = searchScopes(current.data?.scopes || [], input.value);
  active = results.length ? 0 : -1;
  paint(element);
}

function paint(element) {
  const input = element.querySelector("input");
  const list = element.querySelector("ul");
  const query = input.value.trim();
  const open = query.length > 0;
  list.hidden = !open;
  input.setAttribute("aria-expanded", String(open));
  if (!open) {
    list.innerHTML = "";
    input.removeAttribute("aria-activedescendant");
    return;
  }
  list.innerHTML = results.length
    ? results
        .map(
          (item, index) =>
            `<li role="option" id="sd-search-${index}" data-index="${index}" aria-selected="${index === active}">${stateIcon(item.state)}<span class="ds-docid">${esc(item.id)}</span><span class="sd-search__t">${esc(item.title)}</span></li>`,
        )
        .join("")
    : `<li class="sd-search__none" role="presentation">見つからない</li>`;
  if (active >= 0) input.setAttribute("aria-activedescendant", `sd-search-${active}`);
  else input.removeAttribute("aria-activedescendant");
}

function attach(slot) {
  const input = box.querySelector("input");
  const focus = hadFocus;
  slot.replaceChildren(box);
  if (focus) {
    input.focus({ preventScroll: true });
    try {
      input.setSelectionRange(selection[0], selection[1]);
    } catch {
      // type=search may refuse a selection in some browsers; the value is kept either way
    }
  }
  if (input.value.trim()) update(box);
}

// Re-attach after the shell redraws the top band without calling mountSearch (its 5-second refresh).
function watch(header) {
  if (!header || observer?.header === header) return;
  observer?.disconnect();
  observer = new MutationObserver(() => {
    if (!box || box.isConnected || !current.repository) return;
    const slot = header.querySelector("#search-slot");
    if (slot) attach(slot);
  });
  observer.header = header;
  observer.observe(header, { childList: true, subtree: true });
}

export function mountSearch(slot, { route, data, navigate }) {
  if (!slot) return;
  watch(slot.closest("header"));
  if (!route?.repository || !data?.scopes?.length) {
    current = { data: null, navigate: null, repository: null };
    slot.replaceChildren();
    return;
  }
  box = box || build();
  if (current.repository !== route.repository) close(box, true);
  current = { data, navigate, repository: route.repository };
  attach(slot);
}
