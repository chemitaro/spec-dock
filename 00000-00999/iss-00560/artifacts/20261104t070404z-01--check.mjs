// iss-00560: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <out_dir>
// サーバー（spec-dock dashboard serve --port 18560 --state-root <一時> --offline）は先に立てておく。
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { launch, sleep } from "./cdp.mjs";

const [OUT] = process.argv.slice(2);
const SD = "http://127.0.0.1:18560/r/github.com/chemitaro/spec-dock/";
const CHAIN = ["epic-00425", "epic-00427", "epic-00471", "epic-00526"];
const R = { runs: [] };
// 図の中の座標（倍率に依らない style の left/top）で、つながりの4つの Epic と配置の署名を読む
const facts = `(() => {
  const a = window.specdockEdgeAudit ? window.specdockEdgeAudit() : null;
  const at = (id) => { const e = document.querySelector('.gx-world [data-id="' + id + '"]:is(.gx-frame, .gx-box)'); return e ? [parseFloat(e.style.left), parseFloat(e.style.top), parseFloat(e.style.left) + parseFloat(e.style.width)] : null; };
  const chain = ${JSON.stringify(CHAIN)}.map((id) => [id, at(id)]);
  const items = [...document.querySelectorAll('.gx-world .gx-frame, .gx-world .gx-box')];
  const sig = items.map((e) => e.dataset.id + ':' + e.style.left + ',' + e.style.top).join('|');
  const tops = new Set([...document.querySelectorAll('.gx-world > .gx-frame, .gx-world > .gx-box')].filter((e) => !e.parentElement.closest('.gx-frame')).map((e) => e.style.top));
  const w = document.querySelector('.gx-world');
  return { audit: a, chain, sameRow: new Set(chain.map((c) => c[1] && c[1][1])).size === 1, leftToRight: chain.every((c, i) => i === 0 || (c[1] && chain[i - 1][1] && chain[i - 1][1][2] < c[1][0])),
    sig, sigLen: sig.length, worldW: parseFloat(w.style.width), worldH: parseFloat(w.style.height), zoom: document.querySelector('.zoomval')?.textContent,
    scrollW: document.documentElement.scrollWidth, innerW: innerWidth };
})()`;
const KEYS = ["boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed", "missing"];
const clean = (f) => f.audit && KEYS.every((k) => !f.audit[k]);
const b = await launch(19560);
try {
  // PC（1440×900）
  const p = await b.page({ width: 1440, height: 900 });
  await p.go(SD + "board", "document.querySelector('.sd-cols, .sd-empty')");
  await p.ev(`localStorage.removeItem('specdock.graph.v2')`);
  await p.go(SD, "document.querySelector('.gx-edges')"); await sleep(1500);
  const pc = await p.ev(facts);
  R.runs.push({ tag: "pc-1440", ...pc, sig: undefined });
  await p.shot(join(OUT, "pc-graph.png"));
  // 拡大・縮小、100%、「全体」では並べ直さない
  const zooms = [];
  for (const act of ["zin", "zout", "zout", "z100", "fit"]) {
    await p.ev(`document.querySelector('[data-act="${act}"]').click()`); await sleep(400);
    const f = await p.ev(facts);
    zooms.push({ act, zoom: f.zoom, same: f.sig === pc.sig });
  }
  R.zoomKeepsLayout = zooms;
  await p.shot(join(OUT, "pc-graph-fit.png"));
  // 高さだけ変えても並べ直さない
  await p.resize(1440, 700); await sleep(800);
  R.heightKeepsLayout = (await p.ev(facts)).sig === pc.sig;
  // 幅を変えると並べ直す
  await p.resize(1000, 900); await sleep(1500);
  const narrow = await p.ev(facts);
  R.runs.push({ tag: "pc-1000", ...narrow, sig: undefined });
  R.widthRelayouts = narrow.sig !== pc.sig;
  await p.ev(`document.querySelector('[data-act="fit"]').click()`); await sleep(500);
  await p.shot(join(OUT, "pc-1000-graph-fit.png"));
  await p.resize(1440, 900); await sleep(1500);
  R.widthBackSameLayout = (await p.ev(facts)).sig === pc.sig;
  R.errors = { pc: p.errors.filter((e) => !e.includes("favicon")), pcEval: p.evalErrors };
  // 390px
  const m = await b.page({ mobile: true });
  await m.go(SD, "document.querySelector('.gx-edges')"); await sleep(1500);
  const ph = await m.ev(facts);
  R.runs.push({ tag: "390", ...ph, sig: undefined });
  await m.shot(join(OUT, "390-graph.png"));
  await m.ev(`document.querySelector('[data-act="fit"]').click()`); await sleep(600);
  await m.shot(join(OUT, "390-graph-fit.png"));
  R.errors.m = m.errors.filter((e) => !e.includes("favicon"));
  R.errors.mEval = m.evalErrors;
} finally {
  await b.close();
}
R.ok = R.runs.every((r) => clean(r) && r.sameRow && r.leftToRight && r.scrollW <= r.innerW) && R.zoomKeepsLayout.every((z) => z.same) && R.heightKeepsLayout && R.widthRelayouts && R.widthBackSameLayout && Object.values(R.errors).every((e) => !e.length);
writeFileSync(join(OUT, "result.json"), JSON.stringify(R, null, 1));
console.log(JSON.stringify(R, null, 1).slice(0, 5000));
