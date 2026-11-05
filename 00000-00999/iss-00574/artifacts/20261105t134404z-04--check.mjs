// iss-00574: PC のヘッドレス Chrome（CDP）での確かめ。使い方: node check.mjs <out_dir>
// サーバー（spec-dock dashboard serve --port 18574、一時の --state-root）は先に立てておく。
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { launch, sleep } from "./cdp.mjs";

const [OUT] = process.argv.slice(2);
const HOST = "http://127.0.0.1:18574";
const SD = `${HOST}/r/github.com/o/r/`;
const R = { runs: [] };
const marks = `(() => {
  const live = [...document.querySelectorAll('.st-ico[data-live="1"]')];
  const where = (e) => e.closest('[data-id]')?.dataset.id || e.closest('.pn-head, .sd-cover, .panel')?.className || '?';
  const ring = (id) => { const e = document.querySelector('.gx-box[data-id="' + id + '"] .st-ico, .gx-fh[data-id="' + id + '"] .st-ico'); return e ? { f: e.querySelectorAll('.f:not(.sd-nx)').length, t: e.querySelectorAll('.t').length, nx: e.querySelectorAll('.sd-nx').length, label: e.getAttribute('aria-label') } : null; };
  const nx = document.querySelector('.st-ico[data-live="1"] .sd-nx');
  const cs = nx ? getComputedStyle(nx) : null;
  return {
    live: live.map(where), liveCount: live.length,
    rings: Object.fromEntries(['iss-00003', 'iss-00004', 'iss-00008', 'iss-00009', 'iss-00012', 'epic-00002', 'init-00001'].map((id) => [id, ring(id)])),
    anim: cs ? { name: cs.animationName, opacity: cs.opacity } : null,
    idle: [...document.querySelectorAll('.pn-idle, .sd-idle')].map((e) => e.textContent),
    color: (() => { const e = document.querySelector('.gx-box[data-st="doing"] .st-ico, .sd-card[data-st="doing"] .st-ico, .st-ico[data-st="doing"]'); return e ? getComputedStyle(e).color : null; })(),
    overflow: document.documentElement.scrollWidth > innerWidth,
  };
})()`;
const until = "document.querySelector('.gx-box, .sd-cols, .sd-ov, .sd-cover, .td-list, .td-card, .sd-empty')";
const b = await launch(19574);
try {
  for (const dark of [false, true]) {
    for (const mobile of [false, true]) {
      const tag = `${mobile ? "390" : "pc"}-${dark ? "dark" : "light"}`;
      const p = await b.page({ mobile, dark });
      const visit = async (name, url, after) => {
        await p.go(url, until);
        await sleep(1500);
        if (after) {
          const r = await p.ev(after);
          if (r) { await p.mouse("mousePressed", r.x, r.y); await p.mouse("mouseReleased", r.x, r.y); }
          await sleep(900);
        }
        const f = await p.ev(marks);
        R.runs.push({ tag, view: name, ...f });
        await p.shot(join(OUT, `${tag}-${name}.png`));
      };
      await visit("graph", SD);
      await visit("panel", SD, `(() => { const b = document.querySelector('.gx-box[data-id="iss-00004"] .gx-ttl').getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
      if (!mobile) {
        // the boxes' marks, 3 times larger (two shots 1 second apart: the blinking segment differs)
        await p.go(SD, until); await sleep(1500);
        const box = await p.ev(`(() => { const a = document.querySelector('.gx-box[data-id="iss-00003"]').getBoundingClientRect(); const z = document.querySelector('.gx-box[data-id="iss-00009"]').getBoundingClientRect(); return { x: a.x, y: a.y, width: z.right - a.x, height: 40 }; })()`);
        await b.cmd("Page.bringToFront", {}, p.sessionId);
        for (const n of [0, 1]) {
          // fix the blinking phase: 0 ms = faint (opacity .15), 1000 ms = full
          await p.ev(`document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ${n * 1000}; })`);
          await sleep(200);
          const r = await b.cmd("Page.captureScreenshot", { format: "png", clip: { ...box, scale: 3 } }, p.sessionId);
          writeFileSync(join(OUT, `${tag}-zoom-${n}.png`), Buffer.from(r.data, "base64"));
          await sleep(1000);
        }
      }
      await visit("board", SD + "board");
      await visit("overview", HOST + "/");
      await visit("scope-idle", SD + "scopes/iss-00004");
      await visit("scope-live", SD + "scopes/iss-00003");
      await visit("todos", SD + "todos");
      R.runs.push({ tag, view: "errors", errors: p.errors.filter((e) => !e.includes("favicon")), evalErrors: p.evalErrors });
    }
  }
  // 動きを減らす設定（PC・明るい）
  const p = await b.page({});
  await b.cmd("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }, { name: "prefers-color-scheme", value: "light" }] }, p.sessionId);
  await p.go(SD, until); await sleep(1500);
  R.reduced = await p.ev(marks);
  await p.shot(join(OUT, "pc-light-graph-reduced-motion.png"));
  R.reducedErrors = p.errors.filter((e) => !e.includes("favicon"));
} finally {
  await b.close();
}
const g = R.runs.filter((r) => r.view === "graph");
const lists = R.runs.filter((r) => ["board", "overview", "todos"].includes(r.view));
R.ok = {
  graphLive: g.every((r) => ["iss-00003", "iss-00008", "iss-00012"].every((id) => r.live.includes(id)) && !r.live.includes("iss-00004") && !r.live.includes("iss-00009")),
  listsStill: lists.every((r) => r.liveCount === 0),
  idlePanel: R.runs.filter((r) => r.view === "panel").every((r) => r.idle.some((t) => t.includes("2時間動きなし"))),
  idleCover: R.runs.filter((r) => r.view === "scope-idle").every((r) => r.idle.some((t) => t.includes("2時間動きなし"))),
  coverLive: R.runs.filter((r) => r.view === "scope-live").every((r) => r.liveCount >= 1 && r.idle.length === 0),
  reduced: R.reduced?.anim?.name === "none" && R.reduced?.anim?.opacity === "0",
  noErrors: R.runs.filter((r) => r.view === "errors").every((r) => !r.errors.length) && !R.reducedErrors.length,
  noOverflow: R.runs.every((r) => r.view === "errors" || !r.overflow),
};
writeFileSync(join(OUT, "result.json"), JSON.stringify(R, null, 1));
console.log(JSON.stringify(R.ok), JSON.stringify(R.runs.find((r) => r.view === "graph")?.rings));
