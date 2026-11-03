// iss-00529: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <state_dir> <server_port> <parent_port> <repo_root>
import { spawn, execFileSync } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [STATE, PORT, PPORT, REPO] = process.argv.slice(2);
const S = `http://127.0.0.1:${PORT}`, SL = `http://localhost:${PORT}`, P = `http://127.0.0.1:${PPORT}`;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const dir = mkdtempSync(join(tmpdir(), 'iss529-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=19529', `--user-data-dir=${dir}`,
  '--disable-features=MacAppCodeSignClone', '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
let ws, id = 0; const pend = new Map(); const listeners = [];
async function connect() {
  for (let i = 0; i < 60; i++) { try { const j = await (await fetch('http://127.0.0.1:19529/json/version')).json(); ws = new WebSocket(j.webSocketDebuggerUrl); break; } catch { await sleep(200); } }
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } else listeners.forEach(f => f(d)); });
}
const cmd = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
async function newPage({ mobile = false, dark = false } = {}) {
  const { targetId } = await cmd('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cmd('Target.attachToTarget', { targetId, flatten: true });
  await cmd('Page.enable', {}, sessionId);
  const frames = [];
  listeners.push(d => { if (d.method === 'Target.attachedToTarget' && d.sessionId === sessionId) frames.push(d.params.sessionId); });
  await cmd('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sessionId);
  await cmd('Emulation.setDeviceMetricsOverride', mobile ? { width: 390, height: 844, deviceScaleFactor: 3, mobile: true } : { width: 1366, height: 860, deviceScaleFactor: 1, mobile: false }, sessionId);
  if (dark) await cmd('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'dark' }] }, sessionId);
  const ev = async (expr, sid = sessionId) => { const r = await cmd('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sid); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails)); return r.result.value; };
  const go = async (url, wait = 1500) => { await cmd('Page.navigate', { url }, sessionId); await sleep(wait); };
  const shot = async name => { const r = await cmd('Page.captureScreenshot', { format: 'png' }, sessionId); writeFileSync(join(REPO, '.workbench/browser', name), Buffer.from(r.data, 'base64')); };
  return { ev, go, shot, frames, sessionId };
}
const cli = (...args) => execFileSync(join(REPO, '.venv/bin/spec-dock'), args, { env: { ...process.env, XDG_STATE_HOME: STATE } }).toString();
const R = {};
try {
  await connect();
  // 1. 骨組み（PC）：上の帯、空の枠、知らせ、取得の時刻
  let pg = await newPage();
  await pg.go(`${S}/r/github.com/o/r/board`);
  R.shell = await pg.ev(`({title: document.title, brand: !!document.querySelector('.brand__name') && getComputedStyle(document.querySelector('.brand')).display !== 'none',
    tabs: [...document.querySelectorAll('.top .tab')].map(t => t.textContent + (t.getAttribute('aria-selected')==='true'?'*':'')),
    status: document.querySelector('.status')?.textContent, changes: document.querySelector('.changes')?.getAttribute('aria-label'),
    slot: document.querySelector('[data-slot]')?.dataset.slot, slotText: document.querySelector('.slot__count')?.textContent,
    notices: [...document.querySelectorAll('.notice')].map(n => n.dataset.code)})`);
  await pg.shot('01-board-pc.png');
  // 2. 同じリポジトリの中の移動（1ページの中、seen を送り直さない）
  await pg.ev(`window.__marker = 1; document.querySelector('.top .tab').click()`); await sleep(600);
  R.inPage = await pg.ev(`({path: location.pathname, marker: window.__marker === 1, slot: document.querySelector('[data-slot]')?.dataset.slot})`);
  R.seenAfterInPage = JSON.parse(execFileSync('cat', [join(STATE, 'spec-dock/dashboard/seen.json')]).toString()).repositories['github.com/o/r'].records.length;
  // 3. 自動の更新：スナップショットを書き換えると、再読み込みなしで新しくなる
  execFileSync(join(REPO, '.venv/bin/python'), [join(REPO, '.workbench/browser/setup.py'), STATE, 'change']);
  await sleep(7000);
  R.refresh = await pg.ev(`({marker: window.__marker === 1, slotText: document.querySelector('.slot__count')?.textContent, changes: document.querySelector('.changes')?.getAttribute('aria-label'), status: document.querySelector('.status')?.textContent, notices: [...document.querySelectorAll('.notice')].map(n => n.dataset.code)})`);
  // 4. リポジトリの切り替え（上の帯）
  await pg.ev(`document.getElementById('repo-btn').click()`); await sleep(200);
  R.menu = await pg.ev(`[...document.querySelectorAll('#repo-menu a')].map(a => a.textContent)`);
  await pg.ev(`[...document.querySelectorAll('#repo-menu a')].find(a => a.textContent === 'o/s').click()`); await sleep(1500);
  R.switched = await pg.ev(`({path: location.pathname, marker: window.__marker === 1, notices: [...document.querySelectorAll('.notice')].map(n => n.dataset.code + ':' + n.textContent.slice(0, 40))})`);
  await pg.shot('02-stale-notice-pc.png');
  // 5. 資料の切り離し（トップで開く、と枠に入れる）
  await pg.go(`${S}/r/github.com/o/r/files/iss-00002/explanation.html`, 2500);
  R.materialTop = JSON.parse(await pg.ev(`document.getElementById('o').textContent`));
  await pg.go(`${S}/r/github.com/o/r/`);
  await pg.ev(`(() => { const f = document.createElement('iframe'); f.id = 'mat'; f.src = '/r/github.com/o/r/files/iss-00002/explanation.html'; document.body.append(f); })()`); await sleep(2500);
  R.materialFramed = await pg.ev(`(() => { try { return document.getElementById('mat').contentDocument ? 'PARENT CAN READ' : 'opaque (contentDocument null)'; } catch (e) { return 'BLOCKED ' + e.name } })()`);
  // 6. 埋め込み：別の起点の親の iframe（親 127.0.0.1:${PPORT}、子 localhost:${PORT}）
  const pe = await newPage();
  await pe.go(`${P}/?src=/r/github.com/o/r/scopes/iss-00002?embed=1`, 2500);
  R.embedHandshake = await pe.ev(`window.__log.filter(x => x.k !== 'load').map(x => (x.k === 'sent' ? '>' : '<') + x.type + (x.path ? ' ' + x.path : '') + (x.scope ? ' scope=' + x.scope : ''))`);
  const child = pe.frames[pe.frames.length - 1];
  R.embedChild = await pe.ev(`({brandHidden: getComputedStyle(document.querySelector('.brand')).display, repoHidden: getComputedStyle(document.querySelector('.repo')).display, tabs: document.querySelectorAll('.top .tab').length, tabHref: document.querySelector('.top .tab')?.getAttribute('href'), embed: document.documentElement.dataset.embed})`, child);
  await pe.shot('03-embed.png');
  await pe.ev(`send('navigate', {path: '/r/github.com/o/r/board?embed=1'})`); await sleep(800);
  R.embedNavigate = await pe.ev(`({last: window.__log.filter(x => x.k === 'recv').slice(-1)[0], parentUrl: location.search})`);
  R.embedChildAfter = await pe.ev(`({path: location.pathname + location.search, slot: document.querySelector('[data-slot]')?.dataset.slot})`, child);
  await pe.ev(`send('theme', {scheme: 'dark'})`); await sleep(300);
  R.embedTheme = await pe.ev(`document.documentElement.dataset.theme`, child);
  const before = await pe.ev(`window.__log.filter(x => x.k === 'recv').length`);
  await pe.ev(`rogue()`); await sleep(800);
  // 許していない起点からの hello（親の窓から、偽の起点）を子の中で起こす
  await pe.ev(`window.dispatchEvent(new MessageEvent('message', {data: {source: 'host', v: 1, type: 'hello'}, origin: 'http://evil.example:1', source: window.parent}))`, child); await sleep(300);
  R.embedRogue = { recvBefore: before, recvAfter: await pe.ev(`window.__log.filter(x => x.k === 'recv').length`) };
  // 7. hello の前は何も送らない／許していない起点の hello を受けない（親が hello を送らない）
  const pn = await newPage();
  await pn.go(`${P}/?nohello=1&src=/r/github.com/o/r/?embed=1`, 2500);
  const c2 = pn.frames[pn.frames.length - 1];
  await pn.ev(`window.dispatchEvent(new MessageEvent('message', {data: {source: 'host', v: 1, type: 'hello'}, origin: 'http://evil.example:1', source: window.parent}))`, c2); await sleep(400);
  R.noHello = { recvWithoutHello: await pn.ev(`window.__log.filter(x => x.k === 'recv').length`) };
  await pn.ev(`hello()`); await sleep(400);
  R.noHello.recvAfterHello = await pn.ev(`window.__log.filter(x => x.k === 'recv').map(x => x.type)`);
  // 8. 枠の決まり：?embed=1 のない画面は別の起点の枠に出ない
  await pn.go(`${P}/?src=/r/github.com/o/r/`, 2000);
  R.strictFrame = { recv: await pn.ev(`window.__log.filter(x => x.k === 'recv').length`), frameSessions: pn.frames.length };
  // 9. hide/show
  cli('dashboard', 'hide', 'o/s');
  await pg.go(`${S}/`);
  R.hideOverview = await pg.ev(`[...document.querySelectorAll('.slot__list a')].map(a => a.textContent)`);
  await pg.go(`${S}/r/github.com/o/s/`);
  R.hiddenPage = await pg.ev(`document.body.innerText`);
  cli('dashboard', 'show', 'o/s');
  await pg.go(`${S}/`);
  R.showOverview = await pg.ev(`[...document.querySelectorAll('.slot__list a')].map(a => a.textContent)`);
  // 10. スマートフォンの幅 390px（暗い表示）
  const pm = await newPage({ mobile: true, dark: true });
  for (const path of ['/', '/r/github.com/o/r/', '/r/github.com/o/r/board', '/r/github.com/o/r/timeline', '/r/github.com/o/r/scopes/iss-00002', '/r/github.com/o/s/']) {
    await pm.go(SL + path, 1200);
    R['phone ' + path] = await pm.ev(`({scrollWidth: document.documentElement.scrollWidth, innerWidth, mtabs: getComputedStyle(document.getElementById('mtabs')).display, bg: getComputedStyle(document.body).backgroundColor})`);
  }
  await pm.go(SL + '/r/github.com/o/s/board', 1200);
  await pm.shot('04-phone-dark.png');
} catch (e) { R.error = String(e.stack || e); }
finally {
  try { await cmd('Browser.close'); } catch {}
  await sleep(500); try { chrome.kill(); } catch {}
  rmSync(dir, { recursive: true, force: true });
}
console.log(JSON.stringify(R, null, 1));
