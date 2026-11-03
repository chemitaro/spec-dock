// iss-00544: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <out_dir>
// サーバー（spec-dock dashboard serve --port 18544、XDG_STATE_HOME=<一時>）は先に立てておく。
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { launch, sleep } from "./cdp.mjs";

const [OUT] = process.argv.slice(2);
const S = "http://127.0.0.1:18544";
const SD = `${S}/r/github.com/chemitaro/spec-dock/`;
const SAMPLE = `${S}/r/github.com/o/sample/`;
const EMPTY = `${S}/r/github.com/o/empty/`;
const SCREENS = [["graph", SD, ".gx-edges"], ["board", `${SD}board`, ".sd-cols, .sd-empty"], ["timeline", `${SD}timeline`, ".tl"], ["scope", `${SD}scopes/epic-00427`, ".sd-tabs, [role=tablist], h1"], ["overview", `${S}/`, ".ov, .sd-empty, [data-view=overview] *"]];
const R = { heights: [], errors: {}, empty: {}, sample: {} };
const geo = `(() => { const m = document.getElementById('view').getBoundingClientRect(); const bands = ['top','mtabs','notices'].map(id => { const e = document.getElementById(id); const r = e.getBoundingClientRect(); return {id, h: Math.round(r.height), display: getComputedStyle(e).display}; }); const above = bands.reduce((s, b) => s + b.h, 0); return {view: document.getElementById('view').dataset.view, mainTop: Math.round(m.top), mainH: Math.round(m.height), inner: innerHeight, above, bands, ok: m.height > 0 && Math.abs(m.height - (innerHeight - above)) <= 1 && Math.abs(m.bottom - innerHeight) <= 1}; })()`;
const b = await launch();
const recordPosts = (p) => b.cmd("Page.addScriptToEvaluateOnNewDocument", { source: "window.__posts = []; const f = window.fetch; window.fetch = (u, o) => { if (o && o.method === 'POST') window.__posts.push(String(u)); return f(u, o); };" }, p.sessionId);
try {
  for (const mobile of [false, true]) {
    const tag = mobile ? "390" : "pc";
    const p = await b.page({ mobile });
    for (const [name, url, until] of SCREENS) {
      await p.go(url, `document.querySelector(${JSON.stringify(until)})`); await sleep(800);
      const g = await p.ev(geo);
      R.heights.push({ tag, name, ...g });
      await p.shot(join(OUT, `${tag}-${name}.png`));
    }
    R.errors[tag] = p.errors.filter((e) => !e.includes("favicon"));
    // スナップショットのないリポジトリ：エラーなし、「見た」を送らない（R-05）
    const e = await b.page({ mobile });
    await recordPosts(e);
    for (const [name, suffix] of [["graph", ""], ["board", "board"], ["timeline", "timeline"]]) {
      await e.go(EMPTY + suffix, "document.querySelector('.gx-empty:not([hidden]), .sd-empty, .tl, .notice')"); await sleep(800);
      R.empty[`${tag}-${name}`] = { posts: await e.ev("window.__posts"), notices: await e.ev("[...document.querySelectorAll('.notice')].map(n => n.textContent.slice(0, 60))"), geo: await e.ev(geo) };
    }
    R.errors[`${tag}-empty`] = e.errors.filter((x) => !x.includes("favicon"));
    if (!mobile) await e.shot(join(OUT, `pc-empty-timeline.png`));
  }
  // スナップショットのあるリポジトリ：「見た」を1回送る。保証レベルと worktree の印（R-02、R-04）
  const s = await b.page();
  await recordPosts(s);
  await s.go(SAMPLE, "document.querySelector('.gx-edges')"); await sleep(800);
  R.sample.posts = await s.ev("window.__posts");
  R.sample.boxes = await s.ev(`[...document.querySelectorAll('.gx-box')].map(e => ({id: e.dataset.id, st: e.dataset.st, as: e.querySelector('.as')?.dataset.lv ?? null, wt: !!e.querySelector('.wt')}))`);
  await s.shot(join(OUT, "pc-sample-graph.png"));
  await s.go(`${SAMPLE}scopes/iss-00002`, "document.querySelector('h1')"); await sleep(800);
  R.sample.detail = await s.ev(`document.getElementById('view').innerText.match(/保証レベル[\\s\\S]{0,30}|ブランチ[\\s\\S]{0,30}/g)`);
  R.errors.sample = s.errors.filter((x) => !x.includes("favicon"));
} finally {
  await b.close();
}
R.ok = R.heights.every((h) => h.ok) && Object.values(R.errors).every((e) => !e.length) && Object.values(R.empty).every((x) => !x.posts?.length) && R.sample.posts?.length === 1;
writeFileSync(join(OUT, "result.json"), JSON.stringify(R, null, 1));
console.log(JSON.stringify({ ok: R.ok, heights: R.heights.map((h) => [h.tag, h.name, h.view, h.mainH, h.inner - h.above, h.ok]), errors: R.errors, empty: Object.fromEntries(Object.entries(R.empty).map(([k, v]) => [k, v.posts])), sample: R.sample }, null, 1));
