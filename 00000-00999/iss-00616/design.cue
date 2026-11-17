package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"Epic D-02〜D-05・D-07・D-10 を、今の main（iss-00620・iss-00621・iss-00627・iss-00043 の後）の実際の名前と寸法に合わせて作る",
	"線の端は、配置の矩形・測った印の幅・描いた並びの記録だけから決め、描くたびに DOM の位置を測らない",
	"組がないとき、構造の図の世界の HTML を今と同じにし、『横断の構造』は何も変えない",
]

current: """
	- `views/graph.js`：`buildWorld` が世界に木の線 → 枠 → 箱 → 塊 → 依存の線の SVG を innerHTML で置く（z-index：木 0、枠 1、箱と塊 2、依存の線 5）。`paintOrca()` が `paintOrcaMarks` → 欄 → `checkRows()`（印の幅を測って `V.marks` に置き、行の数が違えば配置をやり直す）。`onTap` が印の押しで `select(id)` と `V.pn.openAgent(markAgentAt(slot, target))`。
	- `views/graph/layout.js`：`markRows(m, avail)` が印を左から詰めて行の数を返す。`nodeMarkRows`、`MARK_ROW = 20`、`MARK_INSET = {box: 26}`、`SIZE.pad`（epic [9, 12, 12]、initiative [16, 16, 16]）、`compactHeight`。ノードは `{type: box|tframe|frame, id, x1, y1, x2, y2, rows?, fit?, compact?, kind?}`、塊は `{key, ids, x1, y1, x2, y2}`。
	- `views/_shared/orca_marks.js`：`markIds(slot)` が置き場の描いた順の id の写し（なければ null）。
	- `core/orca_match.js`：`matchWorktrees(structure, summary)` → `{status, byScope: Map<Scope id, worktree[]>}`、`normPath`、`summaryValid`。
	- orca-web の部品（`ctx.orca.marks()`）：`orderAgents(agents)`、`buildMarks(worktree, {now, max})` → `{marks: [{id, mark, workingMode, typeLabel, label, detail, …}], overflow}`、`renderAgentMarks(container, worktree, {size, max, now})`。
	- `graph.css`：`.gx-box` は block で中身が上から流れる（padding 7 10 8 11、縁 1、左の縁 4）。`.gx-agents { display: flex; margin-top: 4px; }`、印の高さ 16px（部品の sm）。
	- `draw.js` の `renderLegend(el, open)` は構造の図と『横断の構造』が共有する。
	"""

target: """
	- 新しい `views/graph/command.js`（純粋な計算）と、`layout.js` の `markSpots` と共有の詰め `packMarks`。
	- `graph.js` に指揮の層・端の層・帯の描画、指揮の選び、帯のエージェントの詳細の欄、`window.specdockCmdAudit`。
	- `graph.css` に層・帯・線・波紋・減らす設定、箱の印の行を底に寄せる規則。`app.css` に指揮の色の札。
	- `draw.js` の `renderLegend` に、既定では出ない「指揮（親 → 子）」の行の口。
	"""

design: {
	"D-01": {
		title: "組と居場所（command.js：commandPairs、placeAgents）"
		text: """
			`views/graph/command.js` は DOM・ネットワーク・時計に触れない（`layout.js` と同じ流儀）。`core/orca_match.js` から `matchWorktrees`・`normPath`・`summaryValid` を読む。

			1. `commandPairs(summary)` → `[{parent: AgentRef, child: AgentRef}]`。`AgentRef = {id, mark, workingMode, agentType, detail, worktree}`（`worktree` は要約の worktree の object そのもの）。
			   - 要約が `summaryValid` でなければ空。全 worktree の全エージェントを id で引く表（最初の1つ。id が文字列でないものは入れない）。
			   - 各エージェントの `parent` が object で、`parent.id` が文字列で、自分の id でなく、表にあれば、（親, 子）の組。同じ（親, 子）は1組。並びは子の id、次に親の id の順。輪でも各組を1回ずつ数えるだけなので止まる（F-02）。
			2. `ownWorktrees(structure, summary)` → `Set<worktree>`：構造の `worktrees.status` が ok でなければ null。`structure.worktrees.paths` にパスがある worktree と、それらと同じ `project.id` の worktree（`matchWorktrees` と同じ判定）。
			3. `placeAgents(pairs, {structure, summary, layout, ix})` → `{pairs, places: Map<agent id, Place>, own}`。null を返すとき（F-01）：`own` が null。
			   - 両端ともほかのリポジトリ（`own` にない）の組を落とす（R-01）。
			   - worktree → Scope：`matchWorktrees(structure, summary).byScope` を逆に引く Map（worktree の object → Scope の id。最初の Scope）。
			   - `Place` は次のどれか：`{kind: "mark", node: <layout の node>, scope}`（Scope が `layout.nodes` にある）、`{kind: "group", group}`（Scope、またはその祖先が `layout.groups` の `ids` に入る。layout の `pairs` の holder と同じ：塊の members とその子孫）、`{kind: "frame", node}`（`ix.ancestors(scope)` をたどって最初に `layout.nodes` にある祖先）、`{kind: "band", key}`（どれにも当たらない、Scope に対応しない worktree、ほかのリポジトリ）。
			4. 帯の項目 `bandItems(pairs, places, own, orderOf)` → `[{key, label, own, main, agents: [AgentRef]}]`：`band` に決まった端だけを、worktree ごと（`key` は worktree の `id`、同じ id の worktree が2つあれば `id` と `path`）にまとめる。
			   - 札：このリポジトリで `main === true` なら「main のチェックアウト」、このリポジトリのほかはブランチ名（`branch` が文字列でなければ「ブランチ不明」）、ほかのリポジトリは「<project.name> · <branch>」（`project.name` がなければ「ほかのリポジトリ」、`branch` がなければ「ブランチ不明」）（R-02、F-03）。
			   - 項目の並び：このリポジトリの main → このリポジトリのほか（札の順）→ ほかのリポジトリ（札の順）。
			   - 項目の中の並び：`orderOf(worktree)`（描く側が部品の `orderAgents` を渡す。なければ要約の順）の id の順から、帯に出すものだけを取り出した順。

			node のテスト（T-01）：Epic D-02 の場合のすべて（5組の合成、別のリポジトリの統括、同じ worktree の親子2組、両端ともほかのリポジトリ、Epic の worktree の統括 → 枠の中の Issue、隠れた Issue（祖先の枠）、畳んだ塊、親が見えない、形の違う親、自分を指す、輪、`main` が null、`branch` が null、`project` が null、構造の worktree の一覧が読めない、要約が無効）。
			"""
		satisfies: ["R-01", "R-02", "F-01", "F-02", "F-03"]
	}
	"D-02": {
		title: "印の位置（layout.js：packMarks、markSpots）と、印の行を箱の底に寄せる CSS"
		text: """
			- `packMarks(m, avail)` → `[{row, x}] | null`：今の `markRows` の詰め（左から、`x + gap + w > avail` で次の行、最初の印はどの幅でも置く）を関数に分けたもの。`markRows` は `1 + (最後の row + 1)`（印がなければ 1）を `packMarks` から返す（結果は今と同じ。今の T-01 の表がそのまま通る）。
			- 定数（`MARK_ROW`・`MARK_INSET` と同じ所に置き、`graph.css` のコメントと互いを指す）：`MARK_H = 16`（部品の sm の高さ）、`MARK_LEFT = {box: 15}`（箱の左の縁 4 + 左の余白 11）、`MARK_BOTTOM = {box: 9}`（箱の下の縁 1 + 下の余白 8）、`FRAME_TITLE = 22`（枠の見出しの題名の行）、`FRAME_GAP = 4`（`.gx-agents` の margin-top）。
			- `markSpots(node, m)` → `[{id, x, y, w, h}] | null`（世界の座標）。`m = {items, gap, ids}`。`ids` の数と `items` の数が違う、どちらかがない、`packMarks` の行の数が `(node.rows ?? 1) − 1` と違う、なら null（F-04）。
			  - Issue の箱・木の枠の箱（`box`・`tframe`）：`avail = (x2 − x1) − MARK_INSET.box`。行の数 k。印 i は `x = x1 + MARK_LEFT.box + x_i`、`y = y2 − MARK_BOTTOM.box − MARK_H − (k − 1 − row_i) × MARK_ROW`、`w = items[i]`、`h = MARK_H`。
			  - 入れ子の枠（`frame`）：`padT, padX = SIZE.pad[kind]`、`avail = (x2 − x1) − 2·padX − 2`（`nodeMarkRows` と同じ）。題名の行の高さ `t = FRAME_TITLE + (compact ? max(0, (node.fit ?? base) − base) : 0)`、`base = compactHeight(kind, node.rows ?? 1)`。印 i は `x = x1 + 1 + padX + x_i`、`y = y1 + padT + t + FRAME_GAP + row_i × MARK_ROW`。
			- CSS（統括の了承、2026-11-17）：`.gx .gx-box { display: flex; flex-direction: column; }` と `.gx .gx-box > .gx-agents { margin-top: auto; }`と `padding-top: 4px;`（箱の中では、印の行の上の 4px を margin ではなく padding で持ち、余りを `margin-top: auto` が吸う。中身の項目の並びは今のまま。`MARK_ROW` の 4 は行の間の `row-gap` のまま）。木の枠の箱も同じ要素なので同じ規則。印の行の下の縁が、箱の下の内側の縁（`y2 − 9`）にそろう。
			- 実機の検査（`specdockCmdAudit().spotDrift`）：描いた各 `.orca-mark` について、箱・枠の要素までの `offsetLeft`・`offsetTop` の和（拡大の影響を受けない）に、その要素の配置の左上を足した位置と、`markSpots` の矩形の左上との差の最大（px）。1 以下が合格（R-03）。

			node のテスト（T-02）：`packMarks` の場合（今の `markRows` の表）、箱の1行・2行、木の枠の箱、Epic・Initiative の入れ子の枠、縮めた Epic の題名2行（`fit`）、F-04 の4つ。
			"""
		satisfies: ["R-03", "F-04"]
	}
	"D-03": {
		title: "端・曲線・弧・波紋・帯の寸法（command.js：commandModel）"
		text: """
			`commandModel({pairs, places, items, layout, spotsOf, routes})` → `{band, links, ripples, audit, top, width}`。`spotsOf(node)` は描く側が `markSpots(node, {…V.marks[id], ids: markIds(slot)})` を渡す。`routes` は `V.EG.routes`（依存の線の道の点の列）。

			- 帯の寸法（定数 `BAND`）：`{top: −16, h: 28, left: SIZE.margin, pad: 6, gap: 10, labelGap: 6, slot: 52}`。帯は世界の座標の負の側の1行（y が −16 から 12。配置の上の余白 24 の上の 12px に重ねる。decisions）。項目 j の幅 `pad + labelWidth(label) + labelGap + slot × n + pad`、左から `gap` ずつ空けて並べる（折り返さない）。`labelWidth(text)`：ASCII の文字 6.6px、ほかの文字 11.5px の和を切り上げ、24〜200 に収める。各エージェントの矩形はその項目の中の `slot` 幅の枠、高さは項目と同じ。`top` は帯があれば `BAND.top`、なければ 0。`width` は配置の幅と、帯の右の端 + `SIZE.margin` の大きいほう。
			- 端の点と出る向き（Epic D-02 の3）：
			  - `mark`（箱・木の枠の箱）：印の下の辺の中央から真下に箱の下の縁（`y2`）までの短い線を `stubs` に入れ、端は `(印の中央の x, y2)`、向きは下。
			  - `mark`（入れ子の枠）：端は印の下の辺の中央、向きは下（`stubs` なし。枠は指揮の層より下）。
			  - 帯：端はそのエージェントの枠の下の縁の中央 `(cx, BAND.top + BAND.h)`、向きは下（帯から出る線は制御点を下に置く）。
			  - `group`・`frame`（印がない端）：相手の端の点へ向かう向きのうち、縦横の大きいほうの縁（上・下・左・右）の中央、向きはその縁の外向き。ただし `frame` の枠が相手の端の点を中に含むときは、枠の内側の下の縁の中央で、向きは上。同じ縁から出る線は、その縁に沿って 10px ずつずらす（線の id の順）。
			  - 印の位置が分からない（`spotsOf` が null、id が記録にない）`mark` の端は、その箱は下の縁の中央・枠は上の縁の中央、向きは外（F-04）。
			- 道（`kind: "curve"`）：両端 P、C と向き dP、dC、距離 L から `k = clamp(0.45 × L, 24, 140)`、`d = M P C (P + dP·k) (C + dC·k) C`。
			- 同じ居場所（両端が同じ node の `mark`、または帯の同じ項目）：Epic D-10 の弧（`kind: "arc"`）。
			  - 縁：同じ行なら、箱は下の縁、入れ子の枠は上の縁、帯の項目は下の縁。違う行なら右の縁（帯の項目は1行なので、いつも下の縁で、もう一方の縁はない）。
			  - 両端、弦 40px への広げ（縁の長さの内に限る）、ふくらみ `d = min(16, room − 3)`（`room` は縁から外へ、弧の幅の範囲で向かい合う、いちばん近い自分以外の node・塊・帯の項目の縁、自分を入れる祖先の枠の内側の縁、帯なら配置のいちばん上の node までの距離）、`d < 8` なら もう一方の縁、そこでも `d < 8` なら初めの縁で `d = 8` にして `crowded` に数える、依存の線の、その縁と平行な区間が弧の外接の四角に入ればもう一方の縁、どちらでも入れば初めの縁で `edgeOverlaps` に数える、は Epic D-10 のとおり。
			  - 道は、両端から縁の外へ直角に制御点 `4d/3`（三次ベジェのふくらみの頂が d になる）。箱の印から縁までの短い線（下の縁なら真下、右の縁なら印の右の辺の中央から横）は `stubs`。
			- 両端が同じ塊・同じ祖先の枠（どちらにも印がない）なら、線を作らない。
			- `links[]`：`{id: "<親>><子>", parent, child, state, kind, d, stubs: [d], from, to}`。`state` は子の `mark` が working なら `flow`、done なら `done`、ほか（waiting・blocked・sleeping・unknown と知らない値）は `wait`。
			- `ripples[]`：組の親ごとに1つ（同じ親は1つ）、親の印の中央（帯ならその枠の中央）。印の位置が分からない親には付けない。
			- `audit = {links, arcs, boxOverlaps, edgeOverlaps, crowded}`。`boxOverlaps` は、弧のふくらみの外接の四角が、自分以外の node（自分を入れる祖先の枠を除く）・塊・帯の項目と重なる（面積が 0 より大きい）数。
			- 鍵 `commandKey(...)`：要約の object、`V.EG` の object、使った `V.marks` と各置き場の `markIds` の JSON、`BAND` が同じなら同じ文字列。描く側は鍵が同じなら何もしない（R-08）。

			node のテスト（T-03）：帯の寸法（項目1つ・3つ、札の長さの上限）、曲線の端と向き（箱の印・枠の見出しの印・帯・塊・枠の縁・枠が相手を含む）、同じ縁から出る線のずらし、同じ行・違う行・帯の弧（弦 40px 以上、`d` の値、浅くする、向きを変える、`crowded`）、依存の線と平行な区間で向きを変える、合成の入力の `boxOverlaps`・`edgeOverlaps` が 0、`state`、`ripples` の数、同じ居場所の塊・祖先の枠で線なし、F-04 の端。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-07", "R-08", "F-04"]
	}
	"D-04": {
		title: "構造の図への描画（graph.js）"
		text: """
			- `paintCommand()` を `paintOrca()` の最後（`checkRows()` の後）に呼ぶ。`checkRows()` が配置をやり直したときは、その中の描き直しの `paintOrca()` が先に描き、外の呼び出しは鍵が同じなので何もしない。
			- 入力：`ctx.orca.status() === "ok"` と `ctx.orca.summary()`、`V.data`、`V.EG.layout`・`V.EG.routes`、`V.ix`、`V.marks`、各置き場の `markIds`（`[data-orca-scope="<id>"]` の要素から）。`orderOf` は部品の `orderAgents` があればそれ、なければ要約の順。
			- 組がない（F-01 を含む）なら、`.gx-cmd`・`.gx-cmd-top`・`.gx-band` を世界から取り除き、帯の高さを 0 に戻す。世界の innerHTML（`buildWorld`）は変えない。
			- 世界の中の並びと重なり：`<svg class="gx-cmd" aria-hidden="true">` を最後の枠の後（箱の前）に、`<svg class="gx-cmd-top" aria-hidden="true">` を最後の塊の後（依存の線の SVG の前）に、`<div class="gx-band">` を世界の最後に差し込む。z-index：`.gx-cmd` 1（枠と同じ値で DOM の順が後）、`.gx-cmd-top` 3、`.gx-band` 4（依存の線 5 より下。帯は負の y にあり依存の線と重ならない）。両 SVG は `position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none`、幅と高さは配置の幅と高さ。
			- 線：各 link を `<g class="cl" data-id data-parent data-child data-state>` にし、中に下地の光の `<path class="cl-glow">` と本体の `<path class="cl-line">`（同じ d）。端の層には stubs（同じ `data-state` の `<path class="cl-stub">`）、端の点（子の端に小さな円 `cl-dot`）、波紋（`<g class="cr">` に円 `cr-a`・`cr-b` を2つ）。
			- 帯：`.gx-band` は `left: 0; top: 0` の入れ物で、各項目 `<div class="gx-band-item" style="left;top;width;height">` に札 `<span class="gx-band-lab" style="width:<labelWidth>px" title="<札>">` と、各エージェントの `<button type="button" class="gx-band-agent" data-cmd-agent="<id>" aria-pressed="false" aria-label="<札>：<部品の label>">` の中の置き場（`<span class="gx-band-slot">`）。置き場には `renderAgentMarks(slot, {…worktree, agents: [そのエージェント]}, {size: "sm", max: 1, now})` で描く。ボタンの幅は `BAND.slot`、印は中央に置く。
			- 世界の大きさ・初めの見え方・『収める』：`V.cmd = {top, width}` を持ち、`initialView`・`fitScale`・`fit` は、外接の四角を `y: top〜L.height`、幅 `max(L.width, width)` で計算する（帯がなければ今と同じ値）。帯の出入りでは `V.tx`・`V.ty`・`V.s` を変えない（R-08）。
			- 指揮の選び `V.cmdSel`（エージェントの id）と、帯のエージェントの詳細の欄 `V.agentPanel`（エージェントの id）：
			  - `onTap`：押した要素が `[data-cmd-agent]` の中なら、同じ id が選ばれていれば両方を解き、違えば `V.sel` を解いて（`select(null)` と同じ）`V.cmdSel` と `V.agentPanel` をその id にする。箱・枠の見出しの印（`.sd-orca`）の押しでは、今の処理の後に `V.cmdSel = markAgentAt(slot, target)`（null なら解く）。印でない箱の押し・空いたところの押しでは `V.cmdSel` を解く。
			  - `onKey`：Esc で `V.agentPanel` を閉じ（なければ今の順）、`V.cmdSel` を解く。`[data-cmd-agent]` の上の Enter・Space は `preventDefault` して、`onTap` と同じ処理。
			  - `select(null)`・欄の閉じる・`V.cleanup` の一覧を開く、で `V.cmdSel` と `V.agentPanel` を解く。
			  - 目立たせ：`.gx-cmd` と `.gx-cmd-top` に `has-cmd-sel`、`V.cmdSel` が親か子の `g.cl` に `is-cmd-hl`、ほかに `is-cmd-off`。帯のボタンの `aria-pressed`。クラスを付け替えるだけで、線の要素は作り直さない。
			  - 消えたら：`paintCommand` で `V.cmdSel` が要約にいなければ解き、`V.agentPanel` なら欄も閉じる。
			- 詳細の欄（`renderPanel` の `V.cleanup` の前）：`V.pn.hide()` の後、aside に `pn-grab`、見出し（そのエージェントの印・種類・札、閉じるボタン `data-act="close"`）、`pn-body` に `agentFrame(ctx.orca.origin, {detail, agentType, branch}, currentTheme())` の iframe（`sandbox="${AGENT_SANDBOX}"`、`referrerpolicy="no-referrer"`）。枠が作れなければ「チャットを開けません」の一文。ページの URL は変えない。
			- `window.specdockCmdAudit()`：`{...audit, spotDrift, spotMissing, layers: [世界の子の class の並び], pointer: [両 SVG の pointer-events]}`。`dispose` で消す（`specdockEdgeAudit` と同じ扱い）。
			"""
		satisfies: ["R-02", "R-03", "R-06", "R-07", "R-08", "F-01"]
	}
	"D-05": {
		title: "色の札、線と波紋の CSS、減らす設定、凡例"
		text: """
			- `app.css` の3か所（`:root`、`@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) … }` の中、`:root[data-theme="dark"]`）に：明 `--sd-cmd: #8a8100; --sd-cmd-glow: rgb(255 236 64 / 45%);`、暗 `--sd-cmd: #fff04d; --sd-cmd-glow: rgb(255 240 77 / 22%);`。
			  計算（タスク担当、2026-11-17）：#8a8100 は色相 56.1°（`--sd-blocked` 明 #a86e00 の 39.3° より 16.8° 黄の側）、`--ds-bg-2` #f6f7f9 と 3.75:1、`--ds-surface` #ffffff と 4.02:1。#fff04d は 54.9°（暗 #ffc93c の 43.4° より 11.5°）、暗の `--ds-bg-2` #15181e と 15.1:1。
			- `graph.css`（色は札と今のデザインシステムの変数だけ）：
			  - `.cl-glow`：`stroke: var(--sd-cmd-glow); stroke-width: 6; stroke-linecap: round; fill: none`。`.cl-line`・`.cl-stub`：`stroke: var(--sd-cmd); stroke-width: 2; fill: none; stroke-linecap: round`。
			  - `flow`：`stroke-dasharray: 0.1 8`（丸い点）と `animation: sd-cmd-flow .15s linear infinite`、`@keyframes sd-cmd-flow { to { stroke-dashoffset: -8.1; } }`（一定の速さ、約 54px/s。写しで本人の確かめを受けて ±50% の内で直してよい）。点は親から子へ流れる（道は親から子へ描く）。
			  - `wait`：同じ点線で `animation: none`。`done`：実線で `opacity: .35`、`animation: none`、下地の光なし。
			  - 波紋：`.cr circle { fill: none; stroke: var(--sd-cmd); transform-box: fill-box; transform-origin: center; animation: sd-cmd-ripple 2.4s ease-out infinite; }`、`.cr-b { animation-delay: 1.2s; }`、`@keyframes sd-cmd-ripple { from { transform: scale(.4); opacity: .9; } to { transform: scale(2.2); opacity: 0; } }`。端の点 `.cl-dot { fill: var(--sd-cmd); }`。
			  - 目立たせ：`.has-cmd-sel .cl.is-cmd-off, .has-cmd-sel .cr.is-cmd-off { opacity: .15; }`、`.cl.is-cmd-hl .cl-line { stroke-width: 3; }`。
			  - 帯：`.gx-band-item` は `position: absolute; display: flex; align-items: center; box-sizing: border-box; padding: 0 6px; border: 1px solid var(--ds-border); border-radius: 999px; background: var(--ds-surface); box-shadow: var(--ds-shadow-s); white-space: nowrap`、`.gx-band-lab` は決まった幅と `overflow: hidden; text-overflow: ellipsis; font-size: 11.5px; color: var(--ds-text-2)`、`.gx-band-agent` は幅 `52px`、高さ 100%、`display: flex; justify-content: center; align-items: center; background: none; border: 0; padding: 0; cursor: pointer`、`[aria-pressed="true"]` で `box-shadow: inset 0 -2px 0 var(--sd-cmd)`。フォーカスの輪は今の `:focus-visible` の規則。
			  - `@media (prefers-reduced-motion: reduce)`：`.gx .cl-line, .gx .cl-stub { animation: none; }`、`.gx .cr circle { animation: none; transform: scale(1.4); opacity: .6; }`、`.gx .cr-b { display: none; }`（R-04）。
			  - `.gx .gx-box { display: flex; flex-direction: column; }`、`.gx .gx-box > .gx-agents { margin-top: auto; padding-top: 4px; }`（D-02）。`.gx .gx-agents { display: flex; margin-top: 4px; }` の行は今の静的な検査が固定しているので残し、箱の中だけ上の規則で上書きする。
			- 凡例（`draw.js`）：`renderLegend(el, open, {cmd = false} = {})`。`cmd` が true のときだけ、『そのほか』に `li('<span class="lg-cmd"></span>', "指揮（親 → 子）", 1)` と `li('<span class="lg-cr"></span>', "指揮している親（波紋）")` を足す。`graph.js` は `{cmd: V.ctx?.orca?.status?.() !== "off"}` を渡す。`allgraph.js` は今のまま（既定 false）。`.lg-cmd`（26×0 の点線の見本、`border-top: 2px dotted var(--sd-cmd)`）と `.lg-cr`（10px の円の輪 `border: 1.5px solid var(--sd-cmd)`）は `graph.css` に置く。
			"""
		satisfies: ["R-04", "R-05", "R-06"]
	}
	"D-06": {
		title: "確かめのしかた（Epic D-07）"
		text: """
			- 純粋な計算（T-01〜T-03）：`tests/js/dashboard_graph_command.mjs`（新）を `tests/unit/presentation/test_dashboard_graph_command.py`（新）が今の流儀（`test_dashboard_graph_js.py` の `_run` と同じ形）で呼ぶ。合成の値だけを使い、実際のパス・IP・セッションの id を書かない。
			- CSS と HTML の静的な検査（T-04）：`app.css` の3か所の札、テストの中で色相とコントラストを計算、`graph.css` の規則（層の z-index と pointer-events、点の流れの keyframes、減らす設定、`.gx-box` の flex と `.gx-agents` の `margin-top: auto`、禁じたもの（`<animate`・`animateMotion`・`canvas`・`blur(`）がない）、`renderLegend` の既定の HTML が今と同じ。
			- 画面（T-05）：`tests/js/fake_dom.mjs` の偽の DOM と偽の orca（`summary()` と `orderAgents` を足す。今の呼び手は変わらない）で `graph.js` を描き、層の有無と順、組がないときの世界の HTML、`routeLayout` の呼び数（要約だけの更新で増えない）、同じ入力で同じ要素、帯の押し（`onTap`・Enter）で欄の iframe と `aria-pressed`、Esc・閉じるで解ける、消えたエージェントで解ける、凡例の行の有無を確かめる。偽の DOM で足りない処理（ポインター、offset）は、画面の関数を直接呼ぶか、実機（T-06）で確かめる。
			- 実機（T-06）：iss-00621 の実機の確かめと同じ組み立て（この worktree の wheel を隔離した venv に入れ、この PC の状態の置き場の写しと試しの設定で `spec-dock dashboard serve --offline --tailscale --port <空いたポート>`、GET だけを中継する試しの orca の口）。常駐のダッシュボード（47800）と orca-web（8791）の設定、道具の環境には触れない。headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じる）で、spec-dock の構造の図を 1440・1000・390 × 明・暗、『全体・いま・これから』で写し、`specdockEdgeAudit()` の違反 0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps` 0・`spotDrift` ≤ 1、ブラウザーのエラー 0、横のスクロールなし、減らす設定の写し、帯の押しのチャット、題名が1行の箱の印の行の前後の写し（統括の求め）を数えて report.md に残す。実データは、今の Run の統括（main のチェックアウト → 帯）とタスク担当・実装担当（同じ worktree の弧）。Epic の枠の印からの線が要れば、統括に試しのエージェントを頼む。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08"]
	}
}

compatibility: """
	組がないとき（Orca につながっていない、親の項目がない古い orca-web、組がない要約）、構造の図の世界の HTML は今のまま。凡例の行は Orca との連携が有効な画面にだけ出る。
	箱の印の行が箱の底に寄るのは、エージェントがいる箱だけの見え方の変化（統括の了承）。『横断の構造』は、共有の `.gx-box` の CSS が同じに効くので印の行が底に寄るほかは変わらない（線と帯は iss-00617）。
	PR を戻すと、線・帯・色の札・凡例の行がなくなり、印の行は今の位置に戻る。API・保存（localStorage）・モデルは変わらない。
	"""

risks: [
	"`.gx-box` を flex にすると、題名の line-clamp や印の行の高さが変わりうる。今の golden・`markOverflow`・iss-00627 の `drift` の検査と、実機の写しで確かめる（『横断の構造』の箱も同じ規則が効く）",
	"部品の印の幅は経過の文字で変わる。`V.marks` は描くたびに測り直されるので、`markSpots` は最後に測った幅を使う。測りの前の一瞬は F-04 の縁に置かれ、次の描き直しで印に結び直す",
	"帯は世界の負の y にあるので、要約が初めの見え方の後に届くと、帯の上の一部が道具の帯の下に隠れうる（BAND.top −16 × 倍率。見えている配置の上の余白に大半が収まる）。『収める』で全体が見える",
	"『横断の構造』は `draw.js` と `graph.css` を共有する。今のテスト（`test_dashboard_allgraph_screen.py` など）がそのまま通ることを確かめる",
]
