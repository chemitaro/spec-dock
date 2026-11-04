// iss-00556: PC の Chrome（ヘッドレス、CDP）での確かめ。使い方: node check.mjs <out_dir>
// サーバー（spec-dock dashboard serve --port 18556、--state-root <一時>）は先に立てておく。
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { launch, sleep } from "./cdp.mjs";

const [OUT] = process.argv.slice(2);
const SD = "http://127.0.0.1:18556/r/github.com/chemitaro/spec-dock/";
const R = { runs: [], prefs: {} };
const facts = `(async () => {
  const a = window.specdockEdgeAudit ? window.specdockEdgeAudit() : null;
  const doc = await (await fetch('/api/v1/r/github.com/chemitaro/spec-dock/structure')).json().catch(() => null);
  const st = new Map((doc?.scopes || []).map((s) => [s.id, s]));
  const boxes = [...document.querySelectorAll('.gx-box, .gx-frame')].map((e) => e.dataset.id);
  const parentOf = (id) => st.get(id)?.parent_id ? st.get(st.get(id).parent_id) : null;
  const shownDone = boxes.filter((id) => st.get(id)?.state === 'done');
  return {
    audit: a, opts: JSON.parse(localStorage.getItem('specdock.graph.v2') || 'null'),
    pressed: [...document.querySelectorAll('.gx-tools [aria-pressed="true"]')].map((b) => b.dataset.act + (b.dataset.deps ? ':' + b.dataset.deps : '')),
    boxes: boxes.length, doneShown: shownDone.length,
    doneUnderDone: shownDone.filter((id) => parentOf(id)?.state === 'done' && !st.get(id)?.keep_visible),
    doneLines: document.querySelectorAll('.gx-edges .is-done').length, waitLines: document.querySelectorAll('.gx-edges .is-wait').length,
    roots: [...document.querySelectorAll('.gx-world > .gx-frame')].map((e) => [e.dataset.id, Math.round(e.getBoundingClientRect().top)]).sort((x, y) => x[1] - y[1]).map((x) => x[0]),
  };
})()`;
const b = await launch(19556);
try {
  for (const mobile of [false, true]) {
    const tag = mobile ? "390" : "pc";
    const p = await b.page({ mobile });
    // 前の版に「終わったものも」と「待っている線」を保存した利用者（R-05）
    await p.go(SD + "board", "document.querySelector('.sd-cols, .sd-empty')");
    await p.ev(`localStorage.removeItem('specdock.graph.v2'); localStorage.setItem('specdock.graph.v1', JSON.stringify({mode: 'nest', showDone: true, deps: 'wait', fold: true, legend: false}))`);
    await p.go(SD, "document.querySelector('.gx-edges')"); await sleep(1200);
    const f = await p.ev(facts);
    R.runs.push({ tag, view: "home", ...f, errors: p.errors.filter((e) => !e.includes("favicon")) });
    await p.shot(join(OUT, `${tag}-graph.png`));
    if (!mobile) {
      await p.ev(`document.querySelector('[data-act="fit"]')?.click()`); await sleep(600);
      await p.shot(join(OUT, `pc-graph-fit.png`));
      for (const [name, act] of [["wait", `[data-act="deps"][data-deps="wait"]`], ["tree", `[data-act="mode"]`]]) {
        await p.ev(`document.querySelector('${act}').click()`); await sleep(1500);
        R.runs.push({ tag, view: name, ...(await p.ev(facts)) });
      }
      await p.shot(join(OUT, `pc-graph-tree-wait.png`));
    }
  }
} finally {
  await b.close();
}
const KEYS = ["boxHits", "ownHits", "overlaps", "diagonal", "portShare", "trunkOverlaps", "failed", "missing"];
R.ok = R.runs.every((r) => r.audit && KEYS.every((k) => !r.audit[k]) && !r.doneUnderDone.length && !(r.errors || []).length);
writeFileSync(join(OUT, "result.json"), JSON.stringify(R, null, 1));
console.log(JSON.stringify(R, null, 1).slice(0, 4000));
