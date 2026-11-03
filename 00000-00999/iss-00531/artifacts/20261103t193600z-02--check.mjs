// iss-00531: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <state_dir> <server_port> <out_dir>
// ボード、詳しい画面、横断の概況、検索を、PC の幅と 390px、明るい表示と暗い表示で開き、JavaScript のエラーを集める。
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [STATE, PORT, OUT] = process.argv.slice(2);
const S = `http://127.0.0.1:${PORT}`;
const R_ = '/r/github.com/o/r';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const DEBUG = 19531;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const dir = mkdtempSync(join(tmpdir(), 'iss531-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${DEBUG}`, `--user-data-dir=${dir}`,
  '--disable-features=MacAppCodeSignClone', '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
let ws, id = 0; const pend = new Map(); const listeners = [];
async function connect() {
  for (let i = 0; i < 60; i++) { try { const j = await (await fetch(`http://127.0.0.1:${DEBUG}/json/version`)).json(); ws = new WebSocket(j.webSocketDebuggerUrl); break; } catch { await sleep(200); } }
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } else listeners.forEach((f) => f(d)); });
}
const cmd = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
const errors = [];
async function newPage({ mobile = false, dark = false, label = '' } = {}) {
  const { targetId } = await cmd('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cmd('Target.attachToTarget', { targetId, flatten: true });
  await cmd('Page.enable', {}, sessionId);
  await cmd('Runtime.enable', {}, sessionId);
  await cmd('Log.enable', {}, sessionId);
  listeners.push((d) => {
    if (d.sessionId !== sessionId) return;
    if (d.method === 'Runtime.exceptionThrown') errors.push(`${label} exception: ${d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text}`);
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errors.push(`${label} console.error: ${d.params.args.map((a) => a.value ?? a.description).join(' ')}`);
    if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error' && !String(d.params.entry.url).endsWith('/favicon.ico')) errors.push(`${label} log: ${d.params.entry.text} ${d.params.entry.url || ''}`);
  });
  await cmd('Emulation.setDeviceMetricsOverride', mobile ? { width: 390, height: 844, deviceScaleFactor: 3, mobile: true } : { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
  await cmd('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: dark ? 'dark' : 'light' }] }, sessionId);
  const ev = async (expr) => { const r = await cmd('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sessionId); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails)); return r.result.value; };
  const go = async (url, wait = 1500) => { await cmd('Page.navigate', { url }, sessionId); await sleep(wait); };
  const shot = async (name, full = false) => {
    const params = { format: 'png' };
    if (full) {
      const size = await ev(`(() => { const m = document.getElementById('view'); return {w: innerWidth, h: Math.ceil(Math.min(6000, m.scrollHeight + m.getBoundingClientRect().top))}; })()`);
      await cmd('Emulation.setDeviceMetricsOverride', { width: size.w, height: size.h, deviceScaleFactor: mobile ? 2 : 1, mobile }, sessionId);
      await ev(`document.body.style.height = 'auto'`);
      await sleep(300);
    }
    const r = await cmd('Page.captureScreenshot', params, sessionId);
    writeFileSync(join(OUT, name), Buffer.from(r.data, 'base64'));
    if (full) {
      await cmd('Emulation.setDeviceMetricsOverride', mobile ? { width: 390, height: 844, deviceScaleFactor: 3, mobile: true } : { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
      await ev(`document.body.style.height = ''`);
    }
  };
  const fits = () => ev(`(() => { const m = document.getElementById('view'); const over = [...m.querySelectorAll('*')].filter((e) => { const b = e.getBoundingClientRect(); return b.width && b.right > innerWidth + 1 && !e.closest('.sd-tabs, .sd-table-wrap, dialog:not([open])'); }).slice(0, 3).map((e) => e.className || e.tagName);
    return {doc: document.documentElement.scrollWidth, main: m.scrollWidth, width: innerWidth, ok: document.documentElement.scrollWidth <= innerWidth && m.scrollWidth <= m.clientWidth, over}; })()`);
  return { ev, go, shot, fits, sessionId };
}
const seenCount = () => { try { return JSON.parse(readFileSync(join(STATE, 'spec-dock/dashboard/seen.json'), 'utf8')).repositories['github.com/o/r'].records.length; } catch { return 0; } };
const R = {};
try {
  await connect();
  // 1. 横断の概況（PC、明るい）：札、警告の帯、変化の数、「見た」が増えない
  const seenBefore = seenCount();
  let pg = await newPage({ label: 'pc-light' });
  await pg.go(`${S}/`, 2500);
  R.overview = await pg.ev(`[...document.querySelectorAll('.sd-ov')].map((c) => ({repo: c.dataset.repo, warn: [...c.querySelectorAll('.sd-ov__warn p')].map((p) => p.dataset.level + ':' + p.textContent.slice(0, 48)),
    merge: c.querySelector('.sd-ov__sec[data-st="merge"] li')?.textContent, changes: c.querySelector('[data-changes]')?.dataset.changes, time: c.querySelector('.sd-ov__time')?.textContent, href: c.getAttribute('href')}))`);
  R.overviewLegend = await pg.ev(`!!document.querySelector('.sd-legend')`);
  R.overviewSearchHidden = await pg.ev(`document.querySelector('#search-slot').children.length === 0`);
  R.overviewSeen = { before: seenBefore, after: seenCount() };
  await pg.shot('01-overview-pc.png', true);
  // 2. ボード（PC）：列の順、マージ待ちの段、推奨順、後に続く、不明の帯、閉じた親の帯、片付けの候補
  const t0 = Date.now();
  await pg.go(`${S}${R_}/board`, 1800);
  R.board = await pg.ev(`({lanes: [...document.querySelectorAll('.sd-col')].map((c) => c.dataset.lane + ':' + c.querySelector('.sd-col__head b').textContent),
    ready: [...document.querySelectorAll('.sd-col[data-lane="ready"] .sd-card')].map((c) => c.dataset.id + (c.querySelector('.sd-dn') ? '(' + c.querySelector('.sd-dn').textContent + ')' : '')),
    doing: [...document.querySelectorAll('.sd-col[data-lane="doing"] .sd-card')].map((c) => c.dataset.id),
    mergeable: [...document.querySelectorAll('.sd-col[data-lane="awaiting_merge"] .sd-col__sub[data-mg="ok"] ~ .sd-card')].map((c) => c.dataset.id),
    subs: [...document.querySelectorAll('.sd-col__sub')].map((s) => s.dataset.mg + ':' + s.querySelector('b').textContent),
    unknown: document.querySelector('[data-code="unknown"]')?.textContent.slice(0, 60), kept: document.querySelector('[data-code="kept-parents"]')?.textContent.slice(0, 70),
    changeBadges: [...document.querySelectorAll('.sd-card .sd-chg')].map((b) => b.closest('.sd-card').dataset.id + ':' + b.textContent),
    metrics: [...document.querySelectorAll('.sd-metric')].map((m) => m.dataset.st + '=' + m.querySelector('.sd-metric__value').textContent),
    cleanup: document.querySelector('.sd-cleanup b')?.textContent, scriptTitle: !!document.querySelector('script:not([src])')})`);
  await pg.shot('02-board-pc.png', true);
  await pg.ev(`document.querySelector('[data-act="cleanup"]').click()`); await sleep(300);
  R.cleanupDialog = await pg.ev(`({open: document.getElementById('sd-cleanup').open, rows: [...document.querySelectorAll('#sd-cleanup tbody tr')].map((r) => r.cells[0].textContent.trim().slice(0, 12) + ' | ' + r.cells[1].textContent)})`);
  await pg.shot('03-board-cleanup-pc.png');
  await pg.ev(`document.querySelector('[data-act="close-cleanup"]').click()`); await sleep(200);
  R.cleanupClosed = await pg.ev(`!document.getElementById('sd-cleanup').open`);
  // 表示の切り替えと URL
  await pg.ev(`window.__marker = 1; [...document.querySelectorAll('.sd-seg a')].find((a) => a.textContent === 'Epic').click()`); await sleep(500);
  R.kind = await pg.ev(`({url: location.pathname + location.search, marker: window.__marker === 1, cards: [...document.querySelectorAll('.sd-card')].map((c) => c.dataset.id)})`);
  await pg.go(`${S}${R_}/board?group=1&done=1`, 1500);
  R.toggles = await pg.ev(`({lanes: [...document.querySelectorAll('.sd-col')].map((c) => c.dataset.lane), groups: [...document.querySelectorAll('.sd-col[data-lane="ready"] .sd-col__grp')].map((g) => g.textContent.slice(0, 30)), checked: [...document.querySelectorAll('.sd-toggle')].map((t) => t.getAttribute('aria-checked')), kept: !!document.querySelector('[data-code="kept-parents"]')})`);
  await pg.ev(`document.querySelector('.sd-legend summary').click()`); await sleep(150);
  R.legend = await pg.ev(`[...document.querySelectorAll('.sd-legend li')].map((l) => l.textContent).join(' / ')`);
  // 3. 250件の構造でボードが2秒以内
  const pb = await newPage({ label: 'pc-big' });
  await pb.go('about:blank', 100);
  await cmd('Page.navigate', { url: `${S}/r/github.com/o/big/board` }, pb.sessionId);
  const started = Date.now();
  let ms = null;
  for (let i = 0; i < 100; i++) { await sleep(50); const n = await pb.ev(`document.querySelectorAll('.sd-card').length`).catch(() => 0); if (n > 0) { ms = await pb.ev(`Math.round(performance.now())`); break; } }
  R.bigBoard = { msFromNavigation: ms, wallMs: Date.now() - started, cards: await pb.ev(`document.querySelectorAll('.sd-card').length`), scopes: await pb.ev(`fetch('/api/v1/r/github.com/o/big/structure').then((r) => r.json()).then((d) => d.scopes.length)`) };
  // 4. 詳しい画面：見出しとタブ
  await pg.go(`${S}${R_}/scopes/iss-00007`, 1800);
  R.header = await pg.ev(`({kicker: document.querySelector('.sd-cover__kicker').textContent, title: document.querySelector('.sd-cover__title').textContent, tags: document.querySelector('.sd-cover__tags').textContent,
    side: [...document.querySelectorAll('.sd-cover__side dt')].map((dt) => dt.textContent + '=' + dt.nextElementSibling.textContent.trim().slice(0, 40)), tabs: [...document.querySelectorAll('.sd-tab')].map((t) => t.textContent + (t.getAttribute('aria-selected') === 'true' ? '*' : '')), legend: !!document.querySelector('.sd-legend')})`);
  R.summary = await pg.ev(`[...document.querySelectorAll('.sd-kv dt')].map((dt) => dt.textContent + '=' + dt.nextElementSibling.textContent.trim().slice(0, 50))`);
  await pg.shot('04-scope-summary-pc.png', true);
  await pg.go(`${S}${R_}/scopes/iss-00013?tab=deps`, 1500);
  R.deps = await pg.ev(`({rows: [...document.querySelectorAll('.sd-table tbody tr')].map((r) => [...r.cells].map((c) => c.textContent.trim()).join(' | ')), state: document.querySelector('.sd-cover__tags .chip').textContent})`);
  await pg.shot('05-scope-deps-pc.png', true);
  await pg.go(`${S}${R_}/scopes/iss-00022?tab=deps`, 1500);
  R.deepRoots = await pg.ev(`[...document.querySelectorAll('[data-code="deep-roots"] li')].map((l) => l.textContent.trim())`);
  await pg.go(`${S}${R_}/scopes/epic-00002?tab=children`, 1500);
  R.children = await pg.ev(`({stages: [...document.querySelectorAll('.sd-stage')].map((s) => s.dataset.stage + ':' + [...s.querySelectorAll('.sd-card')].map((c) => c.dataset.id).join(',')), done: document.querySelector('.sd-tabpanel').textContent.match(/終わった \\d+件を隠している/)?.[0]})`);
  await pg.shot('06-scope-children-pc.png', true);
  await pg.go(`${S}${R_}/scopes/iss-00003?tab=docs`, 1500);
  R.docs = await pg.ev(`[...document.querySelectorAll('.sd-doc')].map((d) => d.querySelector('.sd-doc__title').textContent + ':' + d.dataset.has + (d.querySelector('a') ? '(link ' + d.querySelector('a').getAttribute('href') + ')' : ''))`);
  R.assurance = await pg.ev(`[...document.querySelectorAll('.sd-cover__side dt')].find((dt) => dt.textContent === '保証レベル').nextElementSibling.textContent`);
  await pg.go(`${S}${R_}/scopes/iss-00003?tab=artifacts`, 1500);
  R.artifacts = await pg.ev(`[...document.querySelectorAll('.sd-table tbody tr')].map((r) => r.cells[0].textContent + ' -> ' + r.querySelector('a').getAttribute('href') + ' target=' + r.querySelector('a').target)`);
  await pg.shot('07-scope-artifacts-pc.png');
  await pg.go(`${S}${R_}/scopes/iss-00005?tab=docs`, 1500);
  R.noCatalog = await pg.ev(`({callout: document.querySelector('[data-code^="catalog-"]')?.textContent, code: document.querySelector('[data-code^="catalog-"]')?.dataset.code})`);
  await pg.shot('08-scope-no-catalog-pc.png');
  await pg.go(`${S}${R_}/scopes/iss-00099`, 1500);
  R.unknownScope = await pg.ev(`document.querySelector('.sd-empty')?.textContent`);
  // タブの URL を新しいタブで開く
  const pt = await newPage({ label: 'pc-newtab' });
  await pt.go(`${S}${R_}/scopes/epic-00002?tab=children`, 1800);
  R.newTab = await pt.ev(`({selected: document.querySelector('.sd-tab[aria-selected="true"]').textContent, stages: document.querySelectorAll('.sd-stage').length})`);
  // タブの切り替えは履歴に積まれ、戻るで戻る
  await pt.ev(`[...document.querySelectorAll('.sd-tab')].find((t) => t.textContent.startsWith('依存')).click()`); await sleep(600);
  const afterClick = await pt.ev(`location.search`);
  await pt.ev(`history.back()`); await sleep(800);
  R.tabHistory = { afterClick, afterBack: await pt.ev(`location.search + ' ' + document.querySelector('.sd-tab[aria-selected="true"]').textContent`) };
  // 5. 検索：ホーム（#532 の構造の図）でも出る、0埋めなしの ID、Enter で詳しい画面へ
  await pg.go(`${S}${R_}/`, 1800);
  R.searchOnGraph = await pg.ev(`!!document.querySelector('#search-slot .sd-search input')`);
  await pg.ev(`(() => { const i = document.querySelector('.sd-search input'); i.focus(); i.value = 'iss-8'; i.dispatchEvent(new Event('input')); })()`); await sleep(200);
  R.searchResults = await pg.ev(`[...document.querySelectorAll('.sd-search__list [role=option]')].map((o) => o.textContent)`);
  await pg.shot('09-search-pc.png');
  // 上の帯の5秒ごとの描き直しの後も、欄と入力とフォーカスが残る
  await sleep(6500);
  R.searchAfterRefresh = await pg.ev(`(() => { const i = document.querySelector('#search-slot .sd-search input'); return {present: !!i, value: i?.value, focused: document.activeElement === i, listOpen: !document.querySelector('.sd-search__list').hidden}; })()`);
  // 矢印で2件目を選び、描き直しの後も選択が残る
  await pg.ev(`(() => { const i = document.querySelector('.sd-search input'); i.value = 'issue'; i.dispatchEvent(new Event('input')); i.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown', bubbles: true})); })()`); await sleep(200);
  const chosen = await pg.ev(`document.querySelector('.sd-search__list [aria-selected="true"]').textContent`);
  await sleep(6000);
  R.searchKeepChoice = { chosen, afterRefresh: await pg.ev(`document.querySelector('.sd-search__list [aria-selected="true"]')?.textContent`) };
  // 外を押すと候補が閉じ、描き直しの後も閉じたまま（値は残る）
  await pg.ev(`document.querySelector('#view').click()`); await sleep(200);
  const closedNow = await pg.ev(`document.querySelector('.sd-search__list').hidden`);
  await sleep(6000);
  R.searchOutside = { closedNow, closedAfterRefresh: await pg.ev(`document.querySelector('.sd-search__list').hidden`), value: await pg.ev(`document.querySelector('.sd-search input').value`) };
  await pg.ev(`(() => { const i = document.querySelector('.sd-search input'); i.focus(); i.value = 'iss-8'; i.dispatchEvent(new Event('input')); })()`); await sleep(200);
  await pg.ev(`document.querySelector('.sd-search input').dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true}))`); await sleep(800);
  R.searchEnter = await pg.ev(`({path: location.pathname, value: document.querySelector('.sd-search input').value})`);
  await pg.ev(`(() => { const i = document.querySelector('.sd-search input'); i.focus(); i.value = 'failing'; i.dispatchEvent(new Event('input')); })()`); await sleep(200);
  R.searchTitle = await pg.ev(`[...document.querySelectorAll('.sd-search__list [role=option]')].map((o) => o.textContent)`);
  await pg.ev(`document.querySelector('.sd-search input').dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))`);
  // 6. 埋め込みの逃げ道
  await pg.go(`${S}${R_}/board?embed=1&kind=issue`, 1500);
  R.embedBoard = await pg.ev(`document.querySelector('.sd-newtab')?.getAttribute('href') + ' target=' + document.querySelector('.sd-newtab')?.target + ' cardHref=' + document.querySelector('.sd-card')?.getAttribute('href')`);
  await pg.go(`${S}${R_}/scopes/iss-00007?embed=1`, 1500);
  R.embedScope = await pg.ev(`document.querySelector('.sd-newtab')?.getAttribute('href')`);
  await pg.go(`${S}/?embed=1`, 2000);
  R.embedOverview = await pg.ev(`document.querySelector('.sd-newtab')?.getAttribute('href')`);
  await pg.go(`${S}${R_}/board`, 1500);
  R.noEmbedLink = await pg.ev(`!document.querySelector('.sd-newtab')`);
  // PR が分からないリポジトリ（o/s）
  await pg.go(`${S}/r/github.com/o/s/board`, 1500);
  R.prUnknownBoard = await pg.ev(`({band: document.querySelector('[data-code="pr-unknown"]')?.textContent.slice(0, 30), mergeCol: document.querySelector('[data-pr-unknown]')?.textContent.slice(0, 30)})`);
  await pg.go(`${S}/r/github.com/o/s/scopes/iss-00002`, 1500);
  R.prUnknownScope = await pg.ev(`[...document.querySelectorAll('.sd-cover__side dt')].find((dt) => dt.textContent === 'PR').nextElementSibling.textContent`);
  // スナップショットがない（o/m）
  await pg.go(`${S}/r/github.com/o/m/board`, 1500);
  R.missingBoard = await pg.ev(`({empty: document.querySelector('.sd-empty')?.textContent, notices: [...document.querySelectorAll('.notice')].map((n) => n.dataset.code)})`);
  // 7. 幅と明るさ：PC と 390px、明るい表示と暗い表示
  R.fits = {};
  const pages = [['overview', '/'], ['board', `${R_}/board`], ['board-done', `${R_}/board?done=1&group=1`], ['scope', `${R_}/scopes/iss-00013`], ['deps', `${R_}/scopes/iss-00013?tab=deps`], ['children', `${R_}/scopes/epic-00002?tab=children&done=1`], ['docs', `${R_}/scopes/iss-00003?tab=docs`], ['artifacts', `${R_}/scopes/iss-00003?tab=artifacts`]];
  for (const [mobile, dark] of [[false, false], [false, true], [true, false], [true, true]]) {
    const label = `${mobile ? 'phone' : 'pc'}-${dark ? 'dark' : 'light'}`;
    const p = await newPage({ mobile, dark, label });
    for (const [name, path] of pages) {
      await p.go(`${S}${path}`, name === 'overview' ? 2500 : 1500);
      R.fits[`${label}:${name}`] = await p.fits();
      if ((mobile || dark) && ['overview', 'board', 'scope', 'children'].includes(name)) await p.shot(`10-${label}-${name}.png`, true);
    }
    if (mobile) {
      await p.go(`${S}${R_}/board`, 1500);
      await p.ev(`document.querySelector('.sd-search__open').click()`); await sleep(200);
      await p.ev(`(() => { const i = document.querySelector('.sd-search input'); i.value = '13'; i.dispatchEvent(new Event('input')); })()`); await sleep(200);
      R[`search-${label}`] = await p.ev(`({fieldVisible: getComputedStyle(document.querySelector('.sd-search__field')).display, results: document.querySelectorAll('.sd-search__list [role=option]').length, fit: document.documentElement.scrollWidth <= innerWidth})`);
      await p.shot(`11-${label}-search.png`);
      await p.ev(`document.querySelector('[data-act="cleanup"]').click()`); await sleep(300);
      await p.shot(`12-${label}-cleanup.png`);
    }
  }
  R.overviewSeenAtEnd = seenCount();
} catch (error) {
  R.failure = String(error.stack || error);
} finally {
  R.errors = errors;
  writeFileSync(join(OUT, 'result.json'), JSON.stringify(R, null, 2));
  try { await cmd('Browser.close'); } catch {}
  await sleep(500);
  rmSync(dir, { recursive: true, force: true });
  process.exit(0);
}
