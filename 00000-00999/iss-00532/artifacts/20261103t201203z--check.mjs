// iss-00532: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <state_dir> <repo_root> <out_dir>
// サーバー（spec-dock dashboard serve --port 18532、XDG_STATE_HOME=<state_dir>）は先に立てておく。
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { launch, sleep } from "./cdp.mjs";

const [STATE, REPO, OUT] = process.argv.slice(2);
const S = "http://127.0.0.1:18532";
const SD = `${S}/r/github.com/chemitaro/spec-dock/`;
const GEN = `${S}/r/github.com/o/generated/`;
const SAMPLE = `${S}/r/github.com/o/sample/`;
const R = { audit: [], sizes: [], errors: {} };
const b = await launch();
const auditJs = "window.specdockEdgeAudit()";
const clean = (a) => !!a && ["boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed", "missing"].every((k) => a[k] === 0) && a.drift <= 0.5;
// the center of the first matching element that is fully inside the graph area and below the bar
const visible = (sel) => `(() => { const v = document.querySelector('.gx-view').getBoundingClientRect(); const bar = Math.max(...[...document.querySelectorAll('.gx-next, .gx-tools, .gx-crumbs:not([hidden])')].map(e => e.getBoundingClientRect().bottom)); const e = [...document.querySelectorAll(${JSON.stringify(sel)})].find(e => { const r = e.getBoundingClientRect(); return r.top > bar + 4 && r.bottom < v.bottom - 60 && r.left > v.left + 4 && r.right < v.right - 4 && r.width > 8; }); if (!e) return null; const r = e.getBoundingClientRect(); return {id: e.dataset.id || e.closest('[data-id]')?.dataset.id, x: r.x + r.width / 2, y: r.y + Math.min(r.height / 2, 14)}; })()`;
const rectOf = (sel) => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.x + r.width / 2, y: r.y + r.height / 2}; })()`;
// the topmost box below the bar: its top must be under the bar's bottom (#527 P-6)
const barGap = `(() => { const v = document.querySelector('.gx-view').getBoundingClientRect(); const bars = [...document.querySelectorAll('.gx-next, .gx-crumbs:not([hidden])' + (innerWidth > 640 ? ', .gx-tools' : ''))].map(e => e.getBoundingClientRect().bottom); const bar = Math.max(...bars); const tops = [...document.querySelectorAll('.gx-box, .gx-frame, .gx-clean')].map(e => e.getBoundingClientRect().top); return {bar: Math.round(bar), top: Math.round(Math.min(...tops)), ok: Math.min(...tops) >= bar}; })()`;
try {
  // 1. 4通り（PC と 390px、明るい・暗い）：横のはみ出し、JS のエラー、線の検査、画面の写し
  for (const mobile of [false, true]) for (const dark of [false, true]) {
    const tag = `${mobile ? "390" : "pc"}-${dark ? "dark" : "light"}`;
    const p = await b.page({ mobile, dark });
    for (const [name, url] of [["graph", SD], ["timeline", `${SD}timeline`]]) {
      await p.go(url); await sleep(700);
      const size = await p.ev(`({sw: document.documentElement.scrollWidth, bw: document.body.scrollWidth, w: innerWidth, theme: getComputedStyle(document.body).backgroundColor})`);
      R.sizes.push({ tag, name, ...size, ok: size.sw <= size.w && size.bw <= size.w });
      if (name === "graph") { const a = await p.ev(auditJs); R.audit.push({ tag, repo: "spec-dock", opts: "home", ...a, ok: clean(a) }); R[`bar-${tag}`] = await p.ev(barGap); }
      await p.shot(join(OUT, `${tag}-${name}.png`));
    }
    R.errors[tag] = p.errors.filter((e) => !e.includes("favicon"));
  }

  // 2. 表し方の組み合わせ（PC）：spec-dock と 250件の見本で、DOM の矩形に対する edgeAudit
  const pc = await b.page();
  for (const [repo, url] of [["spec-dock", SD], ["generated", GEN]]) {
    for (const mode of ["nest", "tree"]) for (const showDone of [false, true]) for (const deps of ["wait", "all"]) {
      await pc.ev(`localStorage.setItem('specdock.graph.v1', JSON.stringify({mode: '${mode}', showDone: ${showDone}, deps: '${deps}', fold: true}))`).catch(() => {});
      const ms = await pc.go(url, "document.querySelector('.gx-edges')", 15000); await sleep(400);
      const a = await pc.ev(auditJs);
      R.audit.push({ tag: "pc-light", repo, opts: `${mode}/${showDone ? "done" : "open"}/${deps}`, loadMs: ms, ...a, ok: clean(a) });
    }
  }
  await pc.ev(`localStorage.removeItem('specdock.graph.v1')`);

  // 3. 速さ（R-13）：250件の見本で、開いてから図と線が出るまで、終わったものも出したとき
  const perf = await b.page();
  const t0 = Date.now(); await perf.go(GEN, "document.querySelector('.gx-edges path')", 15000); R.perfHomeMs = Date.now() - t0;
  R.perfDoneMs = await perf.ev(`(async () => { const t = performance.now(); document.querySelector('[data-act=done]').click(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); return Math.round(performance.now() - t); })()`);
  R.perfDoneAudit = await perf.ev(auditJs);
  R.errors.perf = perf.errors.filter((e) => !e.includes("favicon"));

  // 4. 操作（PC）：状態の印、選ぶ、要点、後の操作が勝つ、ダブルクリック、絞り込み、凡例、Esc
  const p = await b.page();
  await p.go(SD); await p.ev(`localStorage.clear()`); await p.go(SD); await sleep(700);
  await p.ev(`document.querySelector('[data-hl=ready]').click()`); await sleep(100);
  R.hl = await p.ev(`({pressed: document.querySelector('[data-hl=ready]').getAttribute('aria-pressed'), hl: document.querySelectorAll('.gx-box.is-hl').length, dim: document.querySelectorAll('.gx-box.is-dim').length, boxes: document.querySelectorAll('.gx-box').length})`);
  await p.ev(`document.querySelector('[data-act=fit]').click()`); await sleep(200);
  const c = (await p.ev(visible(".gx-box[data-st=blocked]"))) || { x: 0, y: 0 };
  const blocked = c.id;
  await p.mouse("mousePressed", c.x, c.y); await p.mouse("mouseReleased", c.x, c.y); await sleep(600);
  R.select = await p.ev(`({id: '${blocked}', sel: [...document.querySelectorAll('.is-sel')].map(e => e.dataset.id), hlAfter: document.querySelectorAll('.gx-box.is-hl').length, pressed: document.querySelector('[data-hl=ready]').getAttribute('aria-pressed'),
    p1: document.querySelectorAll('.gx-edges g.e.is-p1').length, p2: document.querySelectorAll('.gx-edges g.e.is-p2').length, off: document.querySelectorAll('.gx-edges g.e.is-off').length,
    poff: document.querySelectorAll('.gx-box.is-poff').length, roots: [...document.querySelectorAll('.is-root')].map(e => e.dataset.id),
    selShadow: getComputedStyle(document.querySelector('.gx-box.is-sel')).boxShadow.slice(0, 40),
    panelOpen: document.querySelector('.panel').classList.contains('is-open'), panelRight: Math.round(document.querySelector('.panel').getBoundingClientRect().right), w: innerWidth,
    panel: document.querySelector('.panel .pn-title')?.textContent, why: document.querySelector('.panel .pn-why')?.textContent, path: location.pathname})`);
  await p.shot(join(OUT, "pc-select.png"));
  await p.ev(`document.querySelector('[data-hl=doing]').click()`); await sleep(150);
  R.hlAfterSelect = await p.ev(`({sel: document.querySelectorAll('.is-sel').length, hl: document.querySelectorAll('.gx-box.is-hl').length, panelOpen: document.querySelector('.panel').classList.contains('is-open')})`);
  await p.ev(`document.querySelector('[data-hl=doing]').click()`); await sleep(100);
  R.hlOff = await p.ev(`document.querySelectorAll('.gx-box.is-hl, .gx-box.is-dim').length`);
  // legend
  await p.ev(`document.querySelector('[data-act=legend]').click()`); await sleep(100);
  R.legend = await p.ev(`({open: document.querySelector('.legend').dataset.open, items: document.querySelectorAll('.legend li').length, states: [...document.querySelectorAll('.legend .lg-grp:first-child li')].map(l => l.textContent)})`);
  await p.shot(join(OUT, "pc-legend.png"));
  await p.ev(`document.querySelector('[data-act=legend]').click()`);
  // focus on an Epic from the panel, then back
  const fh = await p.ev(visible(".gx-frame.gx-epic:not(.is-compact) > .gx-fh"));
  await p.mouse("mousePressed", fh.x, fh.y); await p.mouse("mouseReleased", fh.x, fh.y); await sleep(500);
  await p.ev(`document.querySelector('.panel [data-act=focus]').click()`); await sleep(700);
  R.focus = await p.ev(`({search: location.search, crumbs: document.querySelector('.gx-crumbs')?.textContent, frames: [...document.querySelectorAll('.gx-frame')].map(e => e.dataset.id), boxes: document.querySelectorAll('.gx-box').length, bar: ${barGap}})`);
  R.focusAudit = await p.ev(auditJs);
  await p.shot(join(OUT, "pc-focus.png"));
  await p.ev(`document.querySelector('[data-act=unfocus]').click()`); await sleep(600);
  R.unfocus = await p.ev(`({search: location.search, frames: document.querySelectorAll('.gx-frame').length})`);
  // fit: no box under the bar
  await p.ev(`document.querySelector('[data-act=fit]').click()`); await sleep(200);
  R.fitBar = await p.ev(barGap);
  // tree
  await p.ev(`document.querySelector('[data-act=mode]').click()`); await sleep(600);
  R.tree = await p.ev(`({mode: document.querySelector('.gx-world').dataset.mode, frames: document.querySelectorAll('.gx-frame').length, boxes: document.querySelectorAll('.gx-box').length, trunks: document.querySelectorAll('.gx-tree path').length, fold: !!document.querySelector('[data-act=fold]')})`);
  R.treeAudit = await p.ev(auditJs);
  await p.shot(join(OUT, "pc-tree.png"));
  await p.ev(`document.querySelector('[data-act=mode]').click()`); await sleep(500);
  // deps: all / none
  const d = await b.page(); await d.go(SD); await sleep(600); await d.ev(`localStorage.removeItem('specdock.graph.v1')`); await d.go(SD); await sleep(600);
  await d.ev(`document.querySelector('[data-act=done]').click()`); await sleep(500);
  await d.ev(`document.querySelector('[data-deps=all]').click()`); await sleep(700);
  R.depsAll = await d.ev(`({lines: document.querySelectorAll('.gx-edges g.lines g.e').length, done: document.querySelectorAll('.gx-edges g.lines g.e.is-done').length, dash: document.querySelector('.gx-edges g.e.is-done .ln') ? getComputedStyle(document.querySelector('.gx-edges g.e.is-done .ln')).strokeDasharray : null, done2: document.querySelector('[data-act=done]').getAttribute('aria-pressed'), deps: document.querySelector('[data-deps=all]').getAttribute('aria-pressed')})`);
  await d.shot(join(OUT, "pc-done-all.png"));
  await d.ev(`document.querySelector('[data-deps=none]').click()`); await sleep(300);
  R.depsNone = await d.ev(`(async () => { document.querySelector('[data-deps=none]').click(); await new Promise(r => setTimeout(r, 300)); return document.querySelectorAll('.gx-edges g.e').length })()`);
  await d.ev(`localStorage.removeItem('specdock.graph.v1')`);
  // cleanup group
  await p.ev(`document.querySelector('.gx-clean') && document.querySelector('.gx-clean').scrollIntoView()`);
  await p.ev(`document.querySelector('[data-act=fit]').click()`); await sleep(200);
  const cl = await p.ev(visible(".gx-clean"));
  if (cl) { await p.mouse("mousePressed", cl.x, cl.y); await p.mouse("mouseReleased", cl.x, cl.y); await sleep(300); }
  R.cleanupFound = !!cl;
  R.cleanup = await p.ev(`({items: [...document.querySelectorAll('.panel .pn-clean li')].map(l => l.textContent.slice(0, 60))})`);
  // double click opens the detail screen
  await p.ev(`document.querySelector('[data-act=close]')?.click()`);
  const bc = await p.ev(visible(".gx-box"));
  await p.go(SD); await sleep(600);
  const bc2 = await p.ev(visible(".gx-box"));
  Object.assign(bc, bc2);
  await p.mouse("mousePressed", bc.x, bc.y, 1); await p.mouse("mouseReleased", bc.x, bc.y, 1);
  await p.mouse("mousePressed", bc.x, bc.y, 2); await p.mouse("mouseReleased", bc.x, bc.y, 2);
  await sleep(500);
  R.dblclick = await p.ev(`({path: location.pathname, view: document.querySelector('main').dataset.view})`);
  await p.go(SD); await sleep(500);
  // keyboard: Enter selects, Esc clears
  await p.ev(`document.querySelector('.gx-box').focus()`);
  await b.cmd("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 }, p.sessionId);
  await sleep(300);
  const selKey = await p.ev(`document.querySelectorAll('.is-sel').length`);
  await b.cmd("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 }, p.sessionId);
  await sleep(200);
  R.keyboard = { selectedByEnter: selKey, afterEscape: await p.ev(`document.querySelectorAll('.is-sel').length`) };
  // wheel zoom with ctrl
  const z0 = await p.ev(`document.querySelector('.zoomval').textContent`);
  await b.cmd("Input.dispatchMouseEvent", { type: "mouseWheel", x: 700, y: 500, deltaX: 0, deltaY: -100, modifiers: 2 }, p.sessionId); await sleep(150);
  R.wheel = { before: z0, after: await p.ev(`document.querySelector('.zoomval').textContent`), pageZoom: await p.ev("visualViewport.scale") };
  R.evalErrors = { pc: p.evalErrors };
  R.errors.pcOps = p.errors.filter((e) => !e.includes("favicon"));

  // 5. 390px：1回目のタップで選んで要点を下から、2回目のタップで詳しい画面、2本指のつまみ、gesturestart
  const m = await b.page({ mobile: true });
  await m.go(SD); await sleep(700);
  const mb = await m.ev(`(() => { const v = document.querySelector('.gx-view').getBoundingClientRect(); const e = [...document.querySelectorAll('.gx-box')].find(e => { const r = e.getBoundingClientRect(); return r.top > v.top + 80 && r.bottom < v.bottom - 200 && r.left > 0 && r.right < innerWidth; }); const r = e.getBoundingClientRect(); return {id: e.dataset.id, x: r.x + r.width / 2, y: r.y + r.height / 2}; })()`);
  await m.touch("touchStart", [[mb.x, mb.y]]); await m.touch("touchEnd", []); await sleep(600);
  R.tap1 = await m.ev(`({path: location.pathname, sel: [...document.querySelectorAll('.is-sel')].map(e => e.dataset.id), panelOpen: document.querySelector('.panel').classList.contains('is-open'), panelTop: Math.round(document.querySelector('.panel').getBoundingClientRect().top), panelBottom: Math.round(document.querySelector('.panel').getBoundingClientRect().bottom), h: innerHeight})`);
  await m.shot(join(OUT, "390-tap1.png"));
  const mb2 = await m.ev(rectOf(`.gx-box[data-id="${mb.id}"]`));
  await m.touch("touchStart", [[mb2.x, mb2.y]]); await m.touch("touchEnd", []); await sleep(700);
  R.tap2 = await m.ev(`({path: location.pathname, view: document.querySelector('main').dataset.view})`);
  await m.go(SD); await sleep(700);
  const before = await m.ev(`({t: document.querySelector('.gx-world').style.transform, vv: visualViewport.scale})`);
  await m.touch("touchStart", [[150, 400], [240, 400]]);
  for (let i = 1; i <= 8; i++) { await m.touch("touchMove", [[150 - i * 10, 400], [240 + i * 10, 400]]); await sleep(16); }
  await m.touch("touchEnd", []); await sleep(200);
  R.pinch = { before, after: await m.ev(`({t: document.querySelector('.gx-world').style.transform, vv: visualViewport.scale, zoom: document.querySelector('.zoomval').textContent})`) };
  R.gesture = await m.ev(`(() => { const e = new Event('gesturestart', {cancelable: true}); document.dispatchEvent(e); const f = new Event('gesturechange', {cancelable: true}); document.dispatchEvent(f); return {gesturestart: e.defaultPrevented, gesturechange: f.defaultPrevented, touchAction: getComputedStyle(document.querySelector('.gx-view')).touchAction}; })()`);
  // drag pans and does not select
  const t1 = await m.ev(`document.querySelector('.gx-world').style.transform`);
  await m.touch("touchStart", [[200, 500]]); for (let i = 1; i <= 6; i++) { await m.touch("touchMove", [[200 - i * 12, 500 - i * 8]]); await sleep(16); } await m.touch("touchEnd", []); await sleep(200);
  R.drag = { moved: t1 !== (await m.ev(`document.querySelector('.gx-world').style.transform`)), sel: await m.ev(`document.querySelectorAll('.is-sel').length`) };
  R.evalErrors.mobile = m.evalErrors;
  R.errors.mobileOps = m.errors.filter((e) => !e.includes("favicon"));

  // 6. 変化の印（R-29）と時間の軸（R-16）
  const s = await b.page();
  await s.go(SAMPLE); await sleep(800); // records "seen"
  execFileSync(join(REPO, ".venv/bin/python"), [join(OUT, "..", "setup.py"), STATE, REPO, "change"]);
  await sleep(300);
  await s.go(SAMPLE); await sleep(900);
  R.changes = await s.ev(`({marked: [...document.querySelectorAll('.gx-box .chg, .gx-frame .chg')].map(e => e.closest('[data-id]').dataset.id + ':' + e.title), count: document.querySelector('.changes')?.getAttribute('aria-label')})`);
  await s.shot(join(OUT, "pc-changes.png"));
  await s.go(`${SD}timeline`); await sleep(800);
  R.timeline = await s.ev(`({metrics: [...document.querySelectorAll('.ds-metric')].map(m => m.textContent), events: [...document.querySelectorAll('.feed .ev')].slice(0, 8).map(e => e.textContent), times: [...document.querySelectorAll('.feed .ev')].length})`);
  await s.ev(`(() => { const r = document.querySelector('.tl-hov').getBoundingClientRect(); const e = new PointerEvent('pointermove', {clientX: r.x + r.width * 0.5, clientY: r.y + 20, bubbles: true}); document.querySelector('.tl-hov').dispatchEvent(e); })()`); await sleep(150);
  R.timelineTip = await s.ev(`document.querySelector('.chart-tip').textContent`);
  await s.ev(`document.querySelector('[data-kind=issue]').click()`); await sleep(300);
  R.timelineNoIssue = await s.ev(`[...document.querySelectorAll('.ds-metric')].map(m => m.textContent)`);
  await s.ev(`document.querySelector('[data-kind=issue]').click()`); await sleep(200);
  await s.shot(join(OUT, "pc-timeline.png"));
  const ev0 = await s.ev(rectOf(".feed a.ev"));
  await s.mouse("mousePressed", ev0.x, ev0.y); await s.mouse("mouseReleased", ev0.x, ev0.y); await sleep(500);
  R.timelineClick = await s.ev(`location.pathname`);
  R.evalErrors.sample = s.evalErrors;
  R.errors.sample = s.errors.filter((e) => !e.includes("favicon"));
} finally {
  await b.close();
}
R.summary = {
  auditAllClean: R.audit.every((a) => a.ok),
  auditRuns: R.audit.length,
  sizesOk: R.sizes.every((x) => x.ok),
  jsErrors: Object.values(R.errors).reduce((n, l) => n + l.length, 0),
};
writeFileSync(join(OUT, "result.json"), JSON.stringify(R, null, 2));
console.log(JSON.stringify(R.summary));
