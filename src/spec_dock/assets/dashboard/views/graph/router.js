// Orthogonal routing of the dependency lines (iss-00532 D-02), moved from the adopted prototype d2's ROUTER
// (epic-00427/artifacts/20261103t150110z--dashboard-design-d2.html). Pure computation: no DOM, so the same code
// runs in the page and in the node check of the tests.
//
// Input G = { obs: [{x1, y1, x2, y2, p1, p2, key, lane?}], frames: [{x1, y1, x2, y2, cls}], edges: [{a, z}], bounds, fineEntries? }
//   obs    rectangles a line must not cross (boxes, frame headings, folded groups); p1-p2 is where lines may leave or
//          enter on the side. `lane: "v"` marks a rectangle that blocks only vertical runs (a tree's parent line).
//   edges  leave the right side of obs[a] and enter the left side of obs[z].
// Steps (a small form of libavoid's ideas): 1. ports spread on each side, 2. a sparse orthogonal visibility grid of
// the obstacles inflated by M0, 3. A* with the direction in the state and penalties for bends, frame crossings,
// sharing and crossing earlier lines, 4. nudging: overlapping segments of one direction are ordered to cross less
// and spread S apart in their channel; a channel that is too narrow is returned as `widen`, 5. drawing: corners of
// radius R and a cut in the lower line at each crossing.
export const C = { M0: 4, M: 10, S: 8, PORT: 10, R: 7, AH: 7, BEND: 40, FRAME: 30, SHARE: 0.6, CROSS: 12, MINSEG: 2 };
const EPS = 0.01;
const uniq = a => { a.sort((p, q) => p - q); const o = []; for (const v of a) if (!o.length || v - o[o.length - 1] > EPS) o.push(v); return o; };
const lb = (arr, v) => { let lo = 0, hi = arr.length; while (lo < hi) { const m = (lo + hi) >> 1; if (arr[m] < v - EPS) lo = m + 1; else hi = m; } return lo; };

/* 1. 出入りの位置：出口（右の辺）は 2S の格子の上、入口（左の辺）はそれから S ずらした格子の上に置く。
   どの出口の線分も、どの入口の線分と S 以上離れるので、寄せでは動かない端の線分どうしが重ならない */
const PORT_GRID = 2 * C.S;
function slots(o, offset) {
  const out = [];
  for (let y = Math.ceil((o.p1 - offset) / PORT_GRID) * PORT_GRID + offset; y <= o.p2 + EPS; y += PORT_GRID) out.push(y);
  return out;
}
/* 線の多い入口の辺（iss-00578）：2S の格子に入りきらない入口は、S おきに置く。ただし、出口の格子の高さには、
   左で向かい合う障害物（その高さで、辺のすぐ左にある障害物）がその高さに出口を持つときは置かない（どちらも寄せで
   動かない端の線分なので、重なると解けない）。入口を S おきにすると、線の多い箱が 2S おきの分まで高くならず、
   その行のほかの列に、間の広い横の線の帯ができない */
const sidesOf = G => {
  const sides = new Map();
  const add = (k, it) => { if (!sides.has(k)) sides.set(k, []); sides.get(k).push(it); };
  G.edges.forEach(e => { add(e.a + "R", { e, end: 0 }); add(e.z + "L", { e, end: 1 }); });
  return sides;
};
function facing(G, Z, y) {
  let best = -1;
  G.obs.forEach((o, i) => { if (!o.lane && o !== Z && o.x2 <= Z.x1 + EPS && o.y1 - EPS <= y && y <= o.y2 + EPS && (best < 0 || o.x2 > G.obs[best].x2)) best = i; });
  return best;
}
function entrySlots(G, Z, k, exits) {
  const coarse = slots(Z, C.S);
  if (coarse.length >= k || !G.fineEntries) return coarse;
  const fine = [];
  for (let y = Math.ceil((Z.p1 - EPS) / C.S) * C.S; y <= Z.p2 + EPS; y += C.S) {
    if (Math.round(y / C.S) % 2 !== 0) { fine.push(y); continue; }   // 入口の格子
    const f = facing(G, Z, y);
    if (f < 0 || !(exits.get(f) || []).some(v => Math.abs(v - y) < C.S - 0.5)) fine.push(y);
  }
  return fine.length > coarse.length ? fine : coarse;
}
const mid = o => (o.p1 + o.p2) / 2;
// 1つの辺の線を、向こうの端の高さの順に並べ、枠から中央に近い k 個の続いた枠を選ぶ（足りなければ辺に詰める）
function place(G, o, list, end, free) {
  const oth = it => G.obs[it.end ? it.e.a : it.e.z];
  list.sort((p, q) => mid(oth(p)) - mid(oth(q)) || oth(p).x1 - oth(q).x1);
  const k = list.length;
  if (free.length >= k) {
    let best = 0;
    for (let s = 0; s + k <= free.length; s++) if (Math.abs((free[s] + free[s + k - 1]) / 2 - mid(o)) < Math.abs((free[best] + free[best + k - 1]) / 2 - mid(o))) best = s;
    return free.slice(best, best + k);
  }
  // 枠が足りない（配置が箱を高くするまでの間）：辺に詰めて並べる（検査が数える）
  const sp = k > 1 ? Math.max(0, o.p2 - o.p1) / (k - 1) : 0;
  return list.map((_, i) => (k > 1 ? o.p1 + i * sp : mid(o)));
}
// 出口の高さ（障害物の番号ごと）
function exitPorts(G, sides) {
  const exits = new Map();
  sides.forEach((list, key) => {
    if (!key.endsWith("R")) return;
    const i = parseInt(key, 10);
    exits.set(i, place(G, G.obs[i], list, 0, slots(G.obs[i], 0)));
  });
  return exits;
}
function assignPorts(G) {
  const sides = sidesOf(G), exits = exitPorts(G, sides);
  // 出口を先に置き、入口は、向かいの出口の高さを知って置く
  sides.forEach((list, key) => {
    const i = parseInt(key, 10), o = G.obs[i], end = key.endsWith("L") ? 1 : 0;
    const ys = end ? place(G, o, list, 1, entrySlots(G, o, list.length, exits)) : exits.get(i);
    list.forEach((it, j) => { it.e[end ? "y2" : "y1"] = ys[j]; it.e[end ? "k2" : "k1"] = list.length; });
  });
  // まっすぐ届く線：入口の辺にその線だけなら、入口を出口の高さにそろえて、段差のない1本にする
  G.edges.forEach(e => {
    const Z = G.obs[e.z];
    if (e.k2 === 1 && e.y1 >= Z.p1 && e.y1 <= Z.p2) e.y2 = e.y1;
  });
}

/** 1つの辺に k 本の線を出し入れするのに要る、出入りの範囲の長さ（2S の格子） */
export const portSpan = k => (k - 1) * PORT_GRID + PORT_GRID;

/**
 * 出入りの位置が足りない辺ごとに、箱（または枠の見出し）をどれだけ高くすればよいか（px）。キーは障害物の番号。
 * 出口の辺は 2S の格子、入口の辺は entrySlots の枠（線が多ければ S おき）で数える（iss-00578）。
 */
export function portNeed(G) {
  const sides = sidesOf(G), exits = exitPorts(G, sides), need = new Map();
  sides.forEach((list, key) => {
    const i = parseInt(key, 10), o = G.obs[i], k = list.length;
    if (k < 2 || o.lane) return;
    let extra;
    if (key.endsWith("R")) extra = portSpan(k) - (o.p2 - o.p1);
    else {
      const have = entrySlots(G, o, k, exits).length;
      if (have >= k) return;
      const per = Math.max(have, 1) / Math.max(C.S, o.p2 - o.p1);   // 1px あたりの枠の数
      extra = Math.min(portSpan(k) - (o.p2 - o.p1), (k - have) / per);
    }
    if (extra > 0.5) need.set(i, Math.max(need.get(i) || 0, Math.ceil(extra)));
  });
  return need;
}

/* 2. 疎な直交の格子（可視グラフ） */
function buildGrid(G) {
  const B = G.bounds, M0 = C.M0;
  const inf = G.obs.map(o => ({ lane: o.lane, x1: Math.max(B.x1, o.x1 - M0), y1: Math.max(B.y1, o.y1 - M0), x2: Math.min(B.x2, o.x2 + M0), y2: Math.min(B.y2, o.y2 + M0) }));
  const xs = [B.x1, B.x2], ys = [B.y1, B.y2];
  inf.forEach(q => { xs.push(q.x1, q.x2); ys.push(q.y1, q.y2); });
  G.edges.forEach(e => ys.push(e.y1, e.y2));
  const X = uniq(xs), Y = uniq(ys), nx = X.length, ny = Y.length, N = nx * ny;
  const vb = new Uint8Array(N), hb = new Uint8Array(N), vl = new Uint8Array(N), fid = new Int16Array(N);
  const rx = inf.map(q => [lb(X, q.x1), lb(X, q.x2)]);
  for (let j = 0; j < ny; j++) {
    const y = Y[j], ym = j < ny - 1 ? (y + Y[j + 1]) / 2 : NaN, row = j * nx;
    for (let t = 0; t < inf.length; t++) {
      const q = inf[t], a = rx[t][0], b = rx[t][1];
      if (!q.lane && q.y1 + EPS < y && y < q.y2 - EPS) { for (let i = a + 1; i < b; i++) vb[row + i] = 1; for (let i = a; i < b; i++) hb[row + i] = 1; }
      if (q.lane !== "h" && q.y1 < ym && ym < q.y2) for (let i = a + 1; i < b; i++) vl[row + i] = 1;
    }
  }
  // 各点がどの枠の中か（いちばん内側）。枠を出入りする線に罰則を付けるため
  G.frames.map((f, k) => [f, k]).sort((p, q) => (q[0].x2 - q[0].x1) * (q[0].y2 - q[0].y1) - (p[0].x2 - p[0].x1) * (p[0].y2 - p[0].y1)).forEach(([f, k]) => {
    const a = lb(X, f.x1), b = lb(X, f.x2 + 2 * EPS) - 1, c = lb(Y, f.y1), d = lb(Y, f.y2 + 2 * EPS) - 1;
    for (let j = c; j <= d; j++) for (let i = a; i <= b; i++) fid[j * nx + i] = k + 1;
  });
  return { B, X, Y, nx, ny, N, vb, hb, vl, fid, uh: new Uint16Array(N), uv: new Uint16Array(N), ph: new Uint8Array(N), pv: new Uint8Array(N) };
}

/* 3. A*（向きを状態に持ち、曲がりに罰則） */
function heap() {
  let k = [], v = [];
  return {
    get size() { return k.length; },
    push(key, val) { k.push(key); v.push(val); let i = k.length - 1; while (i > 0) { const p = (i - 1) >> 1; if (k[p] <= k[i]) break; [k[p], k[i]] = [k[i], k[p]]; [v[p], v[i]] = [v[i], v[p]]; i = p; } },
    pop() {
      const top = v[0], lk = k.pop(), lv = v.pop();
      if (k.length) { k[0] = lk; v[0] = lv; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < k.length && k[l] < k[m]) m = l; if (r < k.length && k[r] < k[m]) m = r; if (m === i) break; [k[m], k[i]] = [k[i], k[m]]; [v[m], v[i]] = [v[i], v[m]]; i = m; } }
      return top;
    }
  };
}
function routeOne(g, G, e) {
  const A = G.obs[e.a], Z = G.obs[e.z], { X, Y, nx, ny } = g;
  const s = lb(Y, e.y1) * nx + lb(X, Math.min(g.B.x2, A.x2 + C.M0));
  const t = lb(Y, e.y2) * nx + lb(X, Math.max(g.B.x1, Z.x1 - C.M0));
  const NS = g.N * 4;
  if (!g.gs) { g.gs = new Float64Array(NS); g.pr = new Int32Array(NS); g.st = new Uint32Array(NS); g.cl = new Uint32Array(NS); g.run = 0; }
  const run = ++g.run, GV = st => (g.st[st] === run ? g.gs[st] : Infinity);
  const tx = X[t % nx], ty = Y[(t / nx) | 0];
  const H = v => Math.abs(X[v % nx] - tx) + Math.abs(Y[(v / nx) | 0] - ty);
  const hp = heap(); const s0 = s * 4;
  g.st[s0] = run; g.gs[s0] = 0; g.pr[s0] = -1; hp.push(H(s), s0);
  let best = -1;
  while (hp.size) {
    const st = hp.pop(); if (g.cl[st] === run) continue; g.cl[st] = run;
    const v = st >> 2, d = st & 3;
    if (v === t) { best = st; break; }
    const i = v % nx, j = (v / nx) | 0, gv = g.gs[st];
    for (let nd = 0; nd < 4; nd++) {
      if (nd === (d ^ 1)) continue;   // 逆戻りはしない（0 東, 1 西, 2 南, 3 北）
      let w, len, li;
      if (nd === 0) { if (i >= nx - 1 || g.hb[v]) continue; w = v + 1; len = X[i + 1] - X[i]; li = v; }
      else if (nd === 1) { if (i === 0 || g.hb[v - 1]) continue; w = v - 1; len = X[i] - X[i - 1]; li = v - 1; }
      else if (nd === 2) { if (j >= ny - 1 || g.vl[v]) continue; w = v + nx; len = Y[j + 1] - Y[j]; li = v; }
      else { if (j === 0 || g.vl[v - nx]) continue; w = v - nx; len = Y[j] - Y[j - 1]; li = v - nx; }
      if (g.vb[w] && w !== t) continue;
      let c = len + (nd !== d ? C.BEND : 0) + (g.fid[v] !== g.fid[w] ? C.FRAME : 0);
      c += C.SHARE * len * (nd < 2 ? g.uh[li] : g.uv[li]);
      if (nd < 2 ? g.pv[w] : g.ph[w]) c += C.CROSS;
      if (w === t) c += nd === 0 ? 0 : nd === 1 ? 1e6 : C.BEND;   // 終点の辺へは東向きに入る
      const ns = w * 4 + nd, ng = gv + c;
      if (ng < GV(ns)) { g.st[ns] = run; g.gs[ns] = ng; g.pr[ns] = st; hp.push(ng + H(w), ns); }
    }
  }
  const P = [{ x: A.x2, y: e.y1 }];
  if (best < 0) {   // 見つからないとき（検査で数える）
    const mx = (A.x2 + Z.x1) / 2; P.push({ x: mx, y: e.y1 }, { x: mx, y: e.y2 }, { x: Z.x1, y: e.y2 });
    return { pts: simplify(P), failed: true };
  }
  const vs = []; for (let st = best; st >= 0; st = g.pr[st]) vs.push(st >> 2);
  vs.reverse();
  for (let q = 0; q < vs.length; q++) {
    const v = vs[q]; P.push({ x: X[v % nx], y: Y[(v / nx) | 0] });
    if (q) { const u = vs[q - 1]; if (Math.abs(u - v) === 1) { g.uh[Math.min(u, v)]++; g.ph[u] = g.ph[v] = 1; } else { g.uv[Math.min(u, v)]++; g.pv[u] = g.pv[v] = 1; } }
  }
  P.push({ x: Z.x1, y: e.y2 });
  return { pts: simplify(P), failed: false };
}
const SNAP = 0.5;
function simplify(P) {
  const a = [];
  for (const p of P) a.push({ x: p.x, y: p.y });
  // 0.5px より小さいずれで続く点は、同じ縦（横）の線にそろえる。端の点（出入りの位置）は動かさない
  for (const c of ["x", "y"]) {
    for (let i = 0; i < a.length - 1;) {
      let j = i;
      while (j + 1 < a.length && Math.abs(a[j + 1][c] - a[i][c]) < SNAP) j++;
      if (j > i) { const ref = j === a.length - 1 ? a[j][c] : a[i][c]; for (let k = i; k <= j; k++) if (k > 0 && k < a.length - 1) a[k][c] = ref; }
      i = j + 1;
    }
  }
  const b = [];
  for (const p of a) { const l = b[b.length - 1]; if (l && Math.abs(l.x - p.x) < EPS && Math.abs(l.y - p.y) < EPS) continue; b.push(p); }
  a.length = 0; a.push(...b);
  // 一直線の中の点を消す。行って戻る折り返しを消すと、その前後がまた一直線になるので、変わらなくなるまで繰り返す
  for (let changed = true; changed;) {
    changed = false;
    for (let k = a.length - 2; k >= 1; k--) {
      const p = a[k - 1], q = a[k], r = a[k + 1];
      if ((Math.abs(p.x - q.x) < EPS && Math.abs(q.x - r.x) < EPS) || (Math.abs(p.y - q.y) < EPS && Math.abs(q.y - r.y) < EPS)) { a.splice(k, 1); changed = true; }
    }
  }
  return a;
}

/* 4. nudging：重なる線分を車線に分ける */
function segs(routes, V) {
  const out = [], oc = V ? "x" : "y", pc = V ? "y" : "x";
  routes.forEach((rt, ri) => {
    const P = rt.pts, n = P.length;
    for (let k = 0; k < n - 1; k++) {
      const p = P[k], q = P[k + 1], isV = Math.abs(p.x - q.x) < EPS;
      if (isV !== V) continue;
      const pos = p[oc], lowP = p[pc] <= q[pc];
      const nP = k > 0 ? Math.sign(P[k - 1][oc] - pos) : 0, nQ = k + 2 < n ? Math.sign(P[k + 2][oc] - pos) : 0;
      out.push({ ri, k, pos, a: Math.min(p[pc], q[pc]), b: Math.max(p[pc], q[pc]), da: lowP ? nP : nQ, db: lowP ? nQ : nP,
        fars: [k > 0 ? P[k - 1][oc] : null, k + 2 < n ? P[k + 2][oc] : null], movable: k > 0 && k < n - 2 });
    }
  });
  return out;
}
function range(sg, G, V) {
  let lo = V ? G.bounds.x1 : G.bounds.y1, hi = V ? G.bounds.x2 : G.bounds.y2, lob = -1, hib = -1;
  G.obs.forEach((o, i) => {
    if ((o.lane === "v" && !V) || (o.lane === "h" && V)) return;   // 一方の向きだけを塞ぐ障害物は、もう一方の線分を縛らない
    const q1 = (V ? o.y1 : o.x1) - C.M0, q2 = (V ? o.y2 : o.x2) + C.M0;
    if (!(q1 < sg.b - EPS && q2 > sg.a + EPS)) return;
    const r1 = (V ? o.x1 : o.y1) - C.M0, r2 = (V ? o.x2 : o.y2) + C.M0;
    if (r2 <= sg.pos + EPS) { if (r2 > lo) { lo = r2; lob = i; } }
    else if (r1 >= sg.pos - EPS) { if (r1 < hi) { hi = r1; hib = i; } }
  });
  for (const f of sg.fars) {
    if (f == null) continue;
    if (f < sg.pos - EPS) { if (f + C.MINSEG > lo) { lo = f + C.MINSEG; lob = -2; } }
    else if (f > sg.pos + EPS) { if (f - C.MINSEG < hi) { hi = f - C.MINSEG; hib = -2; } }
  }
  const pad = C.M - C.M0;
  return { lo, hi, lob, hib, dlo: lob === -2 ? lo : Math.min(lo + pad, Math.max(lo, sg.pos)), dhi: hib === -2 ? hi : Math.max(hi - pad, Math.min(hi, sg.pos)), dlo0: lob === -2 ? lo : lo + pad, dhi0: hib === -2 ? hi : hi - pad };
}
function crossCount(A, B) {   // A を B の手前（左・上）に置いたときの交差の数
  let c = 0;
  if (A.da > 0 && A.a > B.a + 0.5 && A.a < B.b - 0.5) c++;
  if (A.db > 0 && A.b > B.a + 0.5 && A.b < B.b - 0.5) c++;
  if (B.da < 0 && B.a > A.a + 0.5 && B.a < A.b - 0.5) c++;
  if (B.db < 0 && B.b > A.a + 0.5 && B.b < A.b - 0.5) c++;
  // A の端から奥へ向かう線分と、B の端から手前へ向かう線分が同じ高さ（位置）にあると、A を手前に置けば2つが重なる（直交ではない重なり）
  const fwd = [[A.a, A.da], [A.b, A.db]].filter(([, d]) => d > 0), back = [[B.a, B.da], [B.b, B.db]].filter(([, d]) => d < 0);
  for (const [p] of fwd) for (const [q] of back) if (Math.abs(p - q) < C.S - 0.5) c += 10;
  return c;
}
/* 通り道ごとの不足（iss-00578）：束は、箱の上下の空きを通る範囲の広い線分を介して、別々の列の間の線分をまとめる
   ことがある。束の詰めの超えは、別の通り道の鎖を含むので、広げの量にしない。並びの順に、線分ごとに、自分の通り道
   （動ける範囲 lo〜hi）の中にある手前の線分だけの鎖を数え直し、望む上端を超えた分を、その線分の両側の障害物の間の
   不足とする（-1 は図の端。端も広げられる。-2 は線の自分の曲がりで、広げても足りない） */
function lacking(ord, conf, V, crowded, x, nb) {
  const need = new Map(), chain = new Map();
  const ask = (sg, amount) => {
    if (!sg.movable || sg.lob < -1 || sg.hib < -1 || amount <= 0.5) return;
    const key = `${sg.lob}|${sg.hib}`;
    if (!need.has(key) || need.get(key).amount < amount) need.set(key, { axis: V ? "x" : "y", oa: sg.lob, ob: sg.hib, amount });
  };
  // 寄せの後に、重なる2本が車線の間隔より近く残れば（範囲の端に止められた）、その通り道の不足とする
  ord.forEach(sg => { for (const t of nb.get(sg)) if (t.ri !== sg.ri && Math.min(sg.b, t.b) - Math.max(sg.a, t.a) > 0.5) { const d = Math.abs(x.get(sg) - x.get(t)); if (d < C.S - 0.5) ask(sg, C.S - d); } });
  if (!crowded) return [...need.values()];
  ord.forEach((sg, i) => {
    let req = sg.movable ? sg.dlo0 : sg.pos;
    for (let t = 0; t < i; t++) {
      const p = ord[t];
      if (!conf(p, sg)) continue;
      const inside = p.movable
        ? p.lo >= sg.lo - EPS && (p.hi <= sg.hi + EPS || chain.get(p) <= sg.hi + EPS)
        : p.pos >= sg.lo - EPS && p.pos <= sg.hi + EPS;
      if (inside) req = Math.max(req, chain.get(p) + C.S);
    }
    chain.set(sg, req);
    ask(sg, req - sg.dhi0);
  });
  return [...need.values()];
}
function nudgePass(G, routes, V, widen) {
  const L = segs(routes, V), oc = V ? "x" : "y";
  L.forEach(sg => Object.assign(sg, sg.movable ? range(sg, G, V) : { lo: sg.pos, hi: sg.pos, dlo: sg.pos, dhi: sg.pos, dlo0: sg.pos, dhi0: sg.pos, lob: -2, hib: -2 }));
  // 端どうしが近く、片方の端が奥へ、もう片方の端が手前へ曲がる2本も、並べ方で重なりが決まるので同じ束に入れる
  const ends = sg => [[sg.a, sg.da], [sg.b, sg.db]];
  const near = (p, q) => ends(p).some(([u, du]) => du !== 0 && ends(q).some(([w, dw]) => dw === -du && Math.abs(u - w) < C.S - 0.5));
  const conf = (p, q) => p.ri !== q.ri && (Math.min(p.b, q.b) - Math.max(p.a, q.a) > -1 || near(p, q)) && p.lo < q.hi + C.S && q.lo < p.hi + C.S;
  const par = L.map((_, i) => i), find = i => (par[i] === i ? i : (par[i] = find(par[i])));
  for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++) if (conf(L[i], L[j])) par[find(i)] = find(j);
  const groups = new Map(); L.forEach((sg, i) => { const r = find(i); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(sg); });
  groups.forEach(gr => {
    if (!gr.some(sg => sg.movable)) return;
    const cmp = (A, B) => {
      // 動かない線分との前後は、動く線分が入れる側（片方だけなら）にする（iss-00578）
      if (A.movable !== B.movable) {
        const m = A.movable ? A : B, f = A.movable ? B : A;
        const before = m.dlo0 + C.S <= f.pos + 0.5, after = f.pos + C.S <= m.dhi0 + 0.5;
        if (before !== after) return (before ? -1 : 1) * (A.movable ? 1 : -1);
      }
      if (!A.movable || !B.movable) return A.pos - B.pos || A.ri - B.ri;
      const ab = crossCount(A, B), ba = crossCount(B, A);
      return ab !== ba ? ab - ba : (A.pos - B.pos || A.ri - B.ri);
    };
    // 並びの順：重なる組ごとに「交差の少ないほうの前後」を決め、その前後関係で並べる（閉路は位置の小さいものから切る）
    const m = gr.length, after = gr.map(() => []), indeg = new Array(m).fill(0), nb = new Map(gr.map(sg => [sg, []]));
    for (let i = 0; i < m; i++) for (let j = i + 1; j < m; j++) {
      if (!conf(gr[i], gr[j])) continue;
      nb.get(gr[i]).push(gr[j]); nb.get(gr[j]).push(gr[i]);
      if (cmp(gr[i], gr[j]) <= 0) { after[i].push(j); indeg[j]++; } else { after[j].push(i); indeg[i]++; }
    }
    const ord = [], used = new Array(m).fill(false), byPos = (i, j) => gr[i].pos - gr[j].pos || gr[i].ri - gr[j].ri;
    while (ord.length < m) {
      let cand = []; for (let i = 0; i < m; i++) if (!used[i] && indeg[i] === 0) cand.push(i);
      if (!cand.length) for (let i = 0; i < m; i++) if (!used[i]) cand.push(i);
      cand.sort(byPos); const i = cand[0]; used[i] = true; ord.push(gr[i]);
      after[i].forEach(j => indeg[j]--);
    }
    // 詰める：手前から、望む範囲の下端と、手前の重なる線分 + S のうち大きいほう
    // 並びの順は通り道の範囲を見ないので、範囲の広い線分が、別の通り道の鎖に押されたまま、狭い線分や動かない線分の
    // 手前に並ぶことがある（iss-00578）。押されて自分の上端（動かない線分は自分の位置）を超える線分があれば、それを
    // 押している鎖を手前へたどり、それより奥へ逃げられる線分（範囲がそれより奥まであり、それの奥に入る余地がある）を、
    // それのすぐ奥へ回して詰め直す（12回まで。押されの合計が減らなければ、その前の並びに戻してやめる）
    let x = new Map(), over = 0, prev = null;
    const by = new Map(), at = new Map();
    for (let tries = 0; ; tries++) {
      over = 0; let move = null, total = 0;
      ord.forEach((sg, i) => at.set(sg, i));
      ord.forEach((sg, i) => {
        let req = sg.dlo0, push = null;
        for (const t of nb.get(sg)) if (at.get(t) < i && x.get(t) + C.S > req) { req = x.get(t) + C.S; push = t; }
        by.set(sg, push);
        const cap = sg.movable ? sg.dhi0 : sg.pos, top = sg.movable ? sg.hi : sg.pos;
        over = Math.max(over, req - cap);
        if (req > cap + 0.5) total += req - cap;
        x.set(sg, sg.movable ? req : sg.pos);
        if (move || tries >= 12 || req <= cap + 0.5) return;
        const base = sg.movable ? sg.dlo0 : sg.pos;
        for (let p = push; p && !move; p = by.get(p)) if (p.movable && p.hi > top + EPS && base + C.S <= p.dhi0 + 0.5) move = { sg, p };
      });
      if (prev && total >= prev.total - 0.5) { ord.splice(0, ord.length, ...prev.ord); x = prev.x; over = prev.over; break; }
      if (!move) break;
      prev = { ord: ord.slice(), x: new Map(x), over, total };
      const rest = ord.filter(t => t !== move.p), k = rest.indexOf(move.sg) + 1;
      ord.splice(0, ord.length, ...rest.slice(0, k), move.p, ...rest.slice(k));
    }
    // 中央へ寄せる：余りの半分だけ奥へ動かし、奥から順に間隔と上端を守る
    let slack = Infinity; ord.forEach(sg => { if (sg.movable) slack = Math.min(slack, sg.dhi0 - x.get(sg)); });
    const sh = slack > 0 && isFinite(slack) ? slack / 2 : 0;
    for (let i = ord.length - 1; i >= 0; i--) {
      const sg = ord[i]; if (!sg.movable) continue;
      let v = x.get(sg) + sh; v = Math.min(v, Math.max(sg.dhi0, sg.lo));
      for (let t = i + 1; t < ord.length; t++) if (conf(ord[t], sg)) v = Math.min(v, x.get(ord[t]) - C.S);
      v = Math.max(v, sg.lo); v = Math.min(v, sg.hi);
      x.set(sg, v);
    }
    ord.forEach(sg => { if (!sg.movable) return; const P = routes[sg.ri].pts, v = x.get(sg); P[sg.k][oc] = v; P[sg.k + 1][oc] = v; });
    widen.push(...lacking(ord, conf, V, over > 0.5, x, nb));
  });
}
export function route(G) {
  return routeOnce(G);
}

function routeOnce(G) {
  assignPorts(G);
  const g = buildGrid(G);
  const order = G.edges.map((e, i) => i).sort((i, j) => {
    const d = k => { const e = G.edges[k]; return Math.abs(G.obs[e.z].x1 - G.obs[e.a].x2) + Math.abs(e.y2 - e.y1); };
    return d(i) - d(j);
  });
  const routes = new Array(G.edges.length);
  order.forEach(i => { routes[i] = Object.assign(routeOne(g, G, G.edges[i]), { ei: i }); });
  let widen = [];
  // Four passes (the prototype had three): with every stage on one row (iss-00556), a long line can keep a 2px jog
  // of its own after three passes, which pins its run next to another line's.
  for (let round = 0; round < 4; round++) {
    widen = [];
    nudgePass(G, routes, true, widen); routes.forEach(rt => (rt.pts = simplify(rt.pts)));
    nudgePass(G, routes, false, widen); routes.forEach(rt => (rt.pts = simplify(rt.pts)));
  }
  return { routes, widen, grid: { nx: g.nx, ny: g.ny } };
}

/* 5. 描画：角を丸め、交差では下の線を背景色で切る */
const f1 = v => Math.round(v * 10) / 10;
function pathD(P) {
  const n = P.length, len = k => Math.abs(P[k + 1].x - P[k].x) + Math.abs(P[k + 1].y - P[k].y);
  const room = k => (k === 0 ? len(k) : k === n - 2 ? len(k) - C.AH - 1 : len(k) / 2);
  let d = `M${f1(P[0].x)} ${f1(P[0].y)}`;
  for (let k = 1; k < n - 1; k++) {
    const a = P[k - 1], b = P[k], c = P[k + 1];
    const r = Math.max(0, Math.min(C.R, room(k - 1), room(k)));
    const ux = Math.sign(b.x - a.x), uy = Math.sign(b.y - a.y), vx = Math.sign(c.x - b.x), vy = Math.sign(c.y - b.y);
    d += ` L${f1(b.x - ux * r)} ${f1(b.y - uy * r)}` + (r > 0 ? ` A${f1(r)} ${f1(r)} 0 0 ${ux * vy - uy * vx > 0 ? 1 : 0} ${f1(b.x + vx * r)} ${f1(b.y + vy * r)}` : "");
  }
  const z = P[n - 1]; d += ` L${f1(z.x - C.AH + 1)} ${f1(z.y)}`;
  return d;
}
const WID = c => (/is-p1/.test(c) ? 3 : /is-p2/.test(c) ? 2 : /is-done/.test(c) ? 1.2 : 1.6);
const RANK = c => (/is-p1/.test(c) ? 3 : /is-p2/.test(c) ? 2 : /is-off/.test(c) ? 0 : 1);
export function svg(G, routes, classes) {
  const ord = routes.map((rt, i) => i).sort((i, j) => RANK(classes[i]) - RANK(classes[j]));
  let lines = "", cuts = "", tops = "";
  ord.forEach(i => {
    const P = routes[i].pts, z = P[P.length - 1];
    lines += `<g class="e ${classes[i]}"><path class="ln" d="${pathD(P)}"/><path class="ah" d="M${f1(z.x)} ${f1(z.y)} l${-C.AH} ${-C.AH / 2 - .5} v${C.AH + 1}z"/></g>`;
  });
  // 交差：強調の強いほう、同じなら水平の線を上にする
  const segL = [];
  routes.forEach((rt, i) => { const P = rt.pts; for (let k = 0; k < P.length - 1; k++) { const p = P[k], q = P[k + 1]; segL.push({ i, V: Math.abs(p.x - q.x) < EPS, x1: Math.min(p.x, q.x), x2: Math.max(p.x, q.x), y1: Math.min(p.y, q.y), y2: Math.max(p.y, q.y) }); } });
  const bg = (x, y) => { let best = null; G.frames.forEach(f => { if (x > f.x1 && x < f.x2 && y > f.y1 && y < f.y2 && (!best || (f.x2 - f.x1) * (f.y2 - f.y1) < (best.x2 - best.x1) * (best.y2 - best.y1))) best = f; }); return best ? best.cls : "view"; };
  segL.forEach(h => { if (h.V) return; segL.forEach(v => {
    if (!v.V || v.i === h.i) return;
    const cx = v.x1, cy = h.y1;
    if (!(cx > h.x1 + C.R && cx < h.x2 - C.R && cy > v.y1 + C.R && cy < v.y2 - C.R)) return;
    const hUp = RANK(classes[h.i]) > RANK(classes[v.i]) || (RANK(classes[h.i]) === RANK(classes[v.i]));
    const up = hUp ? h : v, lo = hUp ? v : h, wu = WID(classes[up.i]), wl = WID(classes[lo.i]), gap = 2.5;
    const along = wu / 2 + gap, across = wl / 2 + 1;
    cuts += lo.V ? `<rect class="cut is-${bg(cx, cy)}" x="${f1(cx - across)}" y="${f1(cy - along)}" width="${f1(across * 2)}" height="${f1(along * 2)}"/>`
                 : `<rect class="cut is-${bg(cx, cy)}" x="${f1(cx - along)}" y="${f1(cy - across)}" width="${f1(along * 2)}" height="${f1(across * 2)}"/>`;
    const L2 = along + 1;
    tops += `<g class="e ${classes[up.i]}"><path class="ln" d="${up.V ? `M${f1(cx)} ${f1(cy - L2)}V${f1(cy + L2)}` : `M${f1(cx - L2)} ${f1(cy)}H${f1(cx + L2)}`}" style="stroke-dasharray:none"/></g>`;
  }); });
  return `<g class="lines">${lines}</g><g class="cuts">${cuts}</g><g class="tops">${tops}</g>`;
}

/* 機械の検査：(1) 始点・終点以外の箱の矩形（余白 margin）と交わる線分、(2) 自分の始点・終点の箱の内側に入る線分、
   (3) 別の線の、同じ向きで間隔 lane 未満かつ範囲が重なる線分の組、(4) 斜めの線分 */
export function audit(routes, obs, o = {}) {
  const m = o.margin == null ? 3 : o.margin, lane = o.lane == null ? C.S : o.lane;
  const all = []; let diagonal = 0;
  routes.forEach((rt, ri) => { const P = rt.pts; for (let k = 0; k < P.length - 1; k++) {
    const p = P[k], q = P[k + 1], V = Math.abs(p.x - q.x) < EPS, Hh = Math.abs(p.y - q.y) < EPS;
    if (!V && !Hh) diagonal++;
    all.push({ ri, k, V, x1: Math.min(p.x, q.x), x2: Math.max(p.x, q.x), y1: Math.min(p.y, q.y), y2: Math.max(p.y, q.y) });
  } });
  let boxHits = 0, ownHits = 0, overlaps = 0; const list = [];
  let trunkOverlaps = 0;
  all.forEach(s => obs.forEach(b => {
    if (b.lane) {   // 一方の向きだけを塞ぐ障害物（木の親子の線）：それに沿う同じ向きの線分だけを数える
      const along = b.lane === "v"
        ? s.V && s.x1 > b.x1 - m && s.x1 < b.x2 + m && Math.min(s.y2, b.y2) - Math.max(s.y1, b.y1) > 0.5
        : !s.V && s.y1 > b.y1 - m && s.y1 < b.y2 + m && Math.min(s.x2, b.x2) - Math.max(s.x1, b.x1) > 0.5;
      if (along) { trunkOverlaps++; if (list.length < 20) list.push(`trunk r${s.ri}#${s.k} ${b.key}`); }
      return;
    }
    const own = b.key === routes[s.ri].ka || b.key === routes[s.ri].kz, mm = own ? -0.5 : m;
    if (s.x2 > b.x1 - mm && s.x1 < b.x2 + mm && s.y2 > b.y1 - mm && s.y1 < b.y2 + mm) { if (own) ownHits++; else boxHits++; if (list.length < 20) list.push(`${own ? "own" : "box"} r${s.ri}#${s.k} ${b.key}`); }
  }));
  for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) {
    const s = all[i], t = all[j]; if (s.ri === t.ri || s.V !== t.V) continue;
    const dist = s.V ? Math.abs(s.x1 - t.x1) : Math.abs(s.y1 - t.y1);
    const ov = s.V ? Math.min(s.y2, t.y2) - Math.max(s.y1, t.y1) : Math.min(s.x2, t.x2) - Math.max(s.x1, t.x1);
    if (dist < lane - 0.5 && ov > 0.5) { overlaps++; if (list.length < 40) list.push(`lane r${s.ri}#${s.k}~r${t.ri}#${t.k} d=${dist.toFixed(1)} ov=${ov.toFixed(1)}`); }
  }
  // (5) 同じ箱の同じ辺で、出入りの位置が間隔 lane 未満の組
  let portShare = 0; const ends = [];
  routes.forEach(rt => { const P = rt.pts; ends.push([rt.ka + "R", P[0].y], [rt.kz + "L", P[P.length - 1].y]); });
  for (let i = 0; i < ends.length; i++) for (let j = i + 1; j < ends.length; j++) if (ends[i][0] === ends[j][0] && Math.abs(ends[i][1] - ends[j][1]) < lane - 0.5) portShare++;
  return { segments: all.length, boxHits, ownHits, overlaps, diagonal, portShare, trunkOverlaps, failed: routes.filter(r => r.failed).length, list };
}
