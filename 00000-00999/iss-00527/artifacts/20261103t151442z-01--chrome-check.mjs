// iss-00527: PC の Chrome（ヘッドレス、CDP）での確かめ。embed-lab.py を先に起動しておく。
// 使い方: node chrome-check.mjs  （結果を JSON で標準出力へ）
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const P = 'http://127.0.0.1:18527', C = 'http://localhost:18528', CS = 'http://127.0.0.1:18528';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const dir = mkdtempSync(join(tmpdir(), 'iss527-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=19527', `--user-data-dir=${dir}`,
  '--disable-features=MacAppCodeSignClone', '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
let ws, id = 0; const pend = new Map(); const sessions = {};
async function connect() {
  for (let i = 0; i < 50; i++) { try { const j = await (await fetch('http://127.0.0.1:19527/json/version')).json(); ws = new WebSocket(j.webSocketDebuggerUrl); break; } catch { await sleep(200); } }
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } });
}
const cmd = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
async function newPage(mobile) {
  const { targetId } = await cmd('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cmd('Target.attachToTarget', { targetId, flatten: true });
  const s = m => (p) => cmd(m, p, sessionId);
  await cmd('Page.enable', {}, sessionId);
  if (mobile) {
    await cmd('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 3, mobile: true }, sessionId);
    await cmd('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 }, sessionId);
    await cmd('Emulation.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' }, sessionId);
  }
  const ev = async expr => { const r = await cmd('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }, sessionId); return r.result.value; };
  const go = async url => { await cmd('Page.navigate', { url }, sessionId); await sleep(1200); };
  const touch = (type, pts) => cmd('Input.dispatchTouchEvent', { type, touchPoints: pts.map((p, i) => ({ x: p[0], y: p[1], id: i + 1 })) }, sessionId);
  return { sessionId, ev, go, touch, cmd: (m, p) => cmd(m, p, sessionId), targetId };
}
const log = pg => pg.ev('JSON.stringify(window.__log)').then(JSON.parse);
const lastG = async pg => { const l = (await log(pg)).filter(x => x.k === 'recv' && x.type === 'debug'); return l.length ? l[l.length - 1].g : null; };
const dbgs = async pg => (await log(pg)).filter(x => x.k === 'recv' && x.type === 'debug').map(x => x.m);
const types = async pg => (await log(pg)).filter(x => ['recv', 'sent'].includes(x.k)).map(x => (x.k === 'sent' ? '>' : '<') + x.type);

const R = {};
try {
  await connect();
  // ---- 1. frame-ancestors：許した親は埋め込める、許さない（'self' のみ）は止まる
  let pg = await newPage(false);
  await pg.go(`${P}/?childhost=localhost`);
  R.allowedEmbed = { sequence: await types(pg), debug: (await dbgs(pg)).slice(0, 3) };
  await pg.go(`${P}/?childhost=localhost&src=/embed-strict`);
  const lg = await log(pg);
  R.blockedEmbed = { iframeLoadEvent: lg.some(x => x.k === 'iframe-load'), childMessages: lg.filter(x => x.k === 'recv').length };
  // iframe が止められたときの子のドキュメント（Chrome はエラーページ）
  R.blockedEmbed.note = '子は何も送らない（debug も来ない）。親から見ると load は発火するが中身は拒否のエラーページ';

  // ---- 2. postMessage の約束
  await pg.go(`${P}/?childhost=localhost&rogue=1`);
  await sleep(2200);
  const s1 = await types(pg);
  R.handshake = { sequence: s1, rogueDropped: (await dbgs(pg)).filter(m => m.startsWith('drop')), hellosAccepted: (await dbgs(pg)).filter(m => m.startsWith('hello-accepted')) };
  await pg.ev(`__send('theme',{scheme:'dark'})`); await pg.ev(`__send('navigate',{path:'/embed?page=2&embed=1'})`); await sleep(400);
  const l2 = await log(pg);
  R.themeNavigate = { debug: (await dbgs(pg)).filter(m => /theme|navigate/.test(m)), navigated: l2.filter(x => x.type === 'navigated').map(x => x.path), parentUrlAfter: await pg.ev('location.search') };
  // hello の前は何も送らない
  await pg.go(`${P}/?childhost=localhost&autohello=0`);
  R.beforeHello = { sequence: await types(pg), debugBeforeHello: (await dbgs(pg)).length };
  // 許さない起点からの hello：ALLOW に無い起点を装うことはできないので、親が 127.0.0.1 / localhost 以外のとき（Tailscale の IP）は iPhone の手順で確かめる
  R.originCheckNote = 'ALLOW の正規表現は 127.0.0.1 / localhost / Tailscale の IP。外の起点は実機（iPhone の手順）では確かめにくいので、正規表現の単体の確かめで代える';
  const re = /^http:\/\/(127\.0\.0\.1|localhost|100\.85\.74\.8):\d+$/;
  R.originRegex = Object.fromEntries(['http://127.0.0.1:1', 'http://localhost:9', 'http://100.85.74.8:80', 'http://evil.example:1', 'http://127.0.0.1.evil.example:1', 'https://localhost:1'].map(o => [o, re.test(o)]));

  // ---- 3. 履歴（D-15）：iframe の中の通常のリンクと pushState、戻る
  await pg.go(`${P}/?childhost=localhost`);
  const frameOf = async () => (await pg.cmd('Page.getFrameTree')).frameTree;
  async function clickIn(sel) { // 子の画面のボタンの位置は iframe の位置 + 要素の位置。ここでは座標を固定で押す
    return sel;
  }
  // 子のリンクを押す：iframe の左上（親の bar 約 40px の下）に子の bar がある
  const hist0 = await pg.cmd('Page.getNavigationHistory');
  // 通常のリンク（全画面遷移）
  await pg.ev(`(()=>{const r=document.getElementById('f').getBoundingClientRect();window.__fr=[r.left,r.top]})()`);
  const [fx, fy] = await pg.ev('window.__fr');
  // リンクは子の bar の 4 番目付近。ヘッドレスの既定 1280 幅では 1 行に収まる位置を探すため、ボタンを順に押すのではなく子の debug の g を見ながら確かめる
  // → 位置を子に聞く方式：子の DOM の位置を debug で返させる代わりに、親から postMessage navigate を使い、リンクは Input.dispatchMouseEvent で押す
  await pg.ev(`document.getElementById('f').contentWindow.postMessage({source:'host',v:1,type:'navigate',path:'/embed?page=2&embed=1'},'${C}')`);
  await sleep(300);
  const h1 = await pg.cmd('Page.getNavigationHistory');
  R.history = { entriesBefore: hist0.entries.length, entriesAfterPushState: h1.entries.length, topUrlUnchanged: h1.entries.at(-1).url };
  // 親の戻る（top の history.back）
  await pg.ev('history.back()'); await sleep(600);
  const dd = await dbgs(pg);
  R.history.afterTopBack = { popstateSeen: dd.filter(m => m.startsWith('popstate')), loads: dd.filter(m => m.startsWith('loaded')) };

  // 全画面遷移（通常のリンク）を直接起こす：子の中で location 遷移を実行させるため、子を直接開いてリンクを押す
  await pg.go(`${P}/?childhost=localhost`);
  await sleep(300);
  // 座標でリンクを押す：子の bar（flex）の「通常のリンク」は 4 番目。+ - 全体 の後。固定座標は不安定なので、子の g.r0 は使わず、Tab とキー操作ではなく Input.dispatchMouseEvent を数点試す
  async function clickAt(x, y) { for (const t of ['mousePressed', 'mouseReleased']) await pg.cmd('Input.dispatchMouseEvent', { type: t, x, y, button: 'left', clickCount: 1 }); await sleep(500); }
  const before = (await pg.ev('window.__loads'));
  for (const x of [200, 250, 300, 340]) { await clickAt(fx + x, fy + 18); if ((await pg.ev('window.__loads')) > before) break; }
  R.fullNavigation = { loadsBefore: before, loadsAfter: await pg.ev('window.__loads'), hellosSent: await pg.ev('window.__hellos'), sequence: await types(pg) };
  const hist2 = await pg.cmd('Page.getNavigationHistory');
  R.fullNavigation.historyEntries = hist2.entries.length;
  await pg.ev('history.back()'); await sleep(900);
  R.fullNavigation.afterBack = { loads: await pg.ev('window.__loads'), hellos: await pg.ev('window.__hellos'), navigatedPaths: (await log(pg)).filter(x => x.type === 'navigated').map(x => x.path) };
  // 親が hello を再送しない場合（autohello=0）、全画面遷移の後 SpecDock は沈黙する
  await pg.go(`${P}/?childhost=localhost&autohello=0`);
  await pg.ev('window.__hello()'); await sleep(300);
  const b2 = await pg.ev('window.__loads');
  for (const x of [200, 250, 300, 340]) { await clickAt(fx + x, fy + 18); if ((await pg.ev('window.__loads')) > b2) break; }
  const n0 = (await types(pg)).length; await sleep(500);
  R.fullNavigationNoRehello = { loadsAdded: (await pg.ev('window.__loads')) - b2, navigatedAfterNav: (await log(pg)).filter(x => x.type === 'navigated').length };

  // ---- 4. 資料の切り離し（子の中の iframe：親 → 子 → 資料 の入れ子）
  pg = await newPage(false);
  await pg.go(`${P}/?childhost=localhost&src=${encodeURIComponent('/embed?embed=1&autodoc=1')}`);
  await sleep(1800);
  const fd = (await dbgs(pg)).find(m => m.startsWith('file '));
  R.sandboxFile = fd ? JSON.parse(fd.slice(5)).results : 'no result (frame-ancestors chain blocked?)';
  // 資料を親の直下に置いた場合（独立の確かめ）
  await pg.go(`${CS}/r/h/o/n/files/iss-1/doc.html`);
  R.sandboxFileTopLevel = { origin: await pg.ev('String(self.origin)'), note: 'トップで開くと CSP の sandbox は文書にも効く（opaque origin = null）' };
  // SVG（スクリプトを含む）：トップで開いたとき sandbox が効いてスクリプトが走らないか
  await pg.go(`${CS}/r/h/o/n/files/x/a.svg`);
  R.svgTopLevel = { origin: await pg.ev('String(self.origin)') };

  // ---- 5. 指の操作（iPhone の幅、触る操作の模擬）
  pg = await newPage(true);
  await pg.go(`${P}/?childhost=localhost`);
  await sleep(800);
  const gA = await lastG(pg);
  const [ox, oy] = await pg.ev(`(()=>{const r=document.getElementById('f').getBoundingClientRect();return [r.left,r.top]})()`);
  const node = [ox + gA.r0[0], oy + gA.r0[1]];
  async function tap(x, y) { await pg.touch('touchStart', [[x, y]]); await sleep(40); await pg.touch('touchEnd', []); await sleep(250); }
  await tap(...node);
  R.touch = { afterTap1: { sel: (await lastG(pg)).selected, taps: (await lastG(pg)).taps } };
  await tap(...node);
  const g2 = await lastG(pg);
  R.touch.afterTap2 = { navs: g2.navs, navigatedMsgs: (await log(pg)).filter(x => x.type === 'navigated').map(x => x.path).slice(-2) };
  // ドラッグ
  const g3a = await lastG(pg);
  await pg.touch('touchStart', [[ox + 200, oy + 500]]);
  for (let i = 1; i <= 8; i++) { await pg.touch('touchMove', [[ox + 200 + i * 10, oy + 500 + i * 6]]); await sleep(16); }
  await pg.touch('touchEnd', []); await sleep(300);
  const g3 = await lastG(pg);
  R.touch.drag = { dx: g3.tx - g3a.tx, dy: g3.ty - g3a.ty, drags: g3.drags };
  // 2本指のつまみ（広げる）
  await pg.touch('touchStart', [[ox + 150, oy + 500], [ox + 250, oy + 500]]);
  for (let i = 1; i <= 10; i++) { await pg.touch('touchMove', [[ox + 150 - i * 8, oy + 500], [ox + 250 + i * 8, oy + 500]]); await sleep(16); }
  await pg.touch('touchEnd', []); await sleep(300);
  const g4 = await lastG(pg);
  R.touch.pinch = { scaleBefore: g3.scale, scaleAfter: g4.scale, pinches: g4.pinches, ptrMax: g4.ptrMax, visualViewportScale: g4.vv };
  R.touch.note = 'Chrome の模擬は Pointer Events の touch を出す。Safari の gesturestart は出ないので、iPhone の実機で確かめる（gs カウンター）';
  const meta = await pg.ev('({w: innerWidth, vv: visualViewport.scale, ua: navigator.userAgent.slice(0,40)})');
  R.touch.viewport = meta;
} catch (e) { R.error = String(e.stack || e); }
finally {
  try { await cmd('Browser.close'); } catch {}
  await sleep(500); try { chrome.kill('SIGKILL'); } catch {}
  rmSync(dir, { recursive: true, force: true });
}
console.log(JSON.stringify(R, null, 1));
