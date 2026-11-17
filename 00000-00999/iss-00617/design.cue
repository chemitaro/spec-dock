package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"Epic D-06 を、今の main（iss-00614・iss-00629・iss-00632・iss-00616 の後）の実際の名前と寸法に合わせて作る",
	"iss-00616 の純粋な計算（command.js）と描画を写さずに使い、構造の図の出力は変えない",
	"線の端は、各リポジトリの配置の矩形・測った印の幅・描いた並びの記録と、compose の枠の矩形だけから決め、描くたびに DOM の位置を測らない",
	"組がないとき、『横断の構造』の世界の HTML と枠の位置を今と同じにする",
	"見出しの文字を線より上に置くのは CSS の重なりの順と下地だけで行い、線の道は変えない",
]

current: """
	- `views/allgraph.js`：`draw()` が `compose(items(), sizes(N.own), {range, width, bands: {}})` で枠を置き、世界の innerHTML に `section.ax-repo`（見出し `.ax-head`、知らせ `.ax-warn`、本文 `.ax-body`）を並べ、`paintOrca()` が本文ごとに `paintOrcaMarks(body, ctx, structure)` → 欄 → `checkRows()`（本文ごとに印の幅を `r.marks` に測り、行の数が違えばそのリポジトリだけ配置をやり直して `draw()`）。
	  リポジトリの状態は `R`（key → {status, structure, ix, desc, eg: {layout, G, routes, …}, marks, heads, …}）、表示は `A`（tx, ty, s, moved, comp, sel, pn …）。`onTap` は印の押しで `select(repo, id)` と `A.pn.openAgent(markAgentAt(slot, target))`。凡例は `D.renderLegend(A.el.legend, A.legend)`。
	- `views/allgraph/compose.js`：`REPO`（head 40、warn 24、line 28、pad 16、gap 16、minW 360、headW 280、margin 8）、`bodyWidth`、`compose(repos, sizes, {range, width, bands})` → `{frames: Map(key → {key, depth, x1, y1, x2, y2, head, warn, band, body: {kind, x, y, w, h}}), order, width, height}`（座標は世界の座標）。`bands[key]` は帯の高さ（px、なければ0）。
	- `views/graph/command.js`（iss-00616）：`commandPairs`、`ownWorktrees`、`placeAgents`（内部の `placeOf` と `bandKeys`）、`bandLabel`、`bandItems`、`BAND`（top −16、h 28、left 24、border 1、pad 6、gap 10、labelGap 6、slot 52）、`labelWidth`、`commandModel({pairs, places, items, layout, spotsOf, routes})` → `{band: {top, h, items, right}|null, links, ripples, audit, top, width}`、`commandKey`。
	- `views/graph.js`（iss-00616 D-04）：`paintCommand`・`drawCommand`（`.gx-cmd` を最後の枠の後、`.gx-cmd-top` を依存の線の前、`.gx-band` を世界の最後に置く）・`paintBandMarks`・`paintCmdSel`・`pressBandAgent`・`renderAgentPanel`・`cmdAudit`。
	- `graph.css`：`.gx .gx-world > .gx-frame { z-index: 1 }`、`.gx .gx-world > .gx-cmd { z-index: 1 }`、箱と塊 2、`.gx-cmd-top` 3、依存の線 5、帯 6。`allgraph.css`：`.gx .ax-body > .gx-frame { z-index: 1 }`、`.ax-repo`・`.ax-head`・`.ax-body` は z-index なし。
	"""

target: """
	- `graph/command.js`：`placeAgents` の居場所の決め方を `placer` として外に出し（`placeAgents` は今と同じ結果）、`bandKeys` を外に出し、`commandModel` に複数の帯の行（`rows`）と本文ごとの外枠（`boundsOf`）の口を足す（渡さなければ今と同じ結果）。帯の行の幅 `bandRowWidth`。
	- 新しい `allgraph/command.js`（純粋な計算）：worktree とリポジトリの対応、居場所、帯の形、入れ物の枠、世界の座標に移した配置、線の模型。
	- `allgraph/compose.js`：帯の幅（`bands[key]` に `{h, w}`）、入れ物の枠（`keep`）、全体の帯（`other`）の口と、見えている枠を保つ補い `anchorShift`。
	- 新しい `graph/command_view.js`（DOM の部品）：層と帯の HTML、帯の印の描き、指揮の選びの class、帯のエージェントの詳細の欄。`graph.js` と `allgraph.js` が使う。
	- `allgraph.js`：指揮の層・端の層・帯の描画、帯の形のやり直しと補い、指揮の選び、帯のエージェントの詳細の欄、凡例の行、`window.specdockCmdAudit`。
	- `graph.css`・`allgraph.css`：見出しの文字を線より上に置く規則と下地、『ほかの場所』の行の頭の文字。
	"""

design: {
	"D-01": {
		title: "共有の計算の口（graph/command.js）"
		text: """
			構造の図の結果を変えずに、次を足す。

			- `bandKeys(summary)` を export する（今の内部の関数。worktree → 帯の項目の鍵）。
			- `placer({structure, summary, layout, ix})` → `(ref) => Place`：今の `placeAgents` の中の `scopeOf`・`nodes`・`groupOf`・`placeOf` を取り出したもの（mark → group → frame → band の順。band は `{kind: "band", key}`）。`placeAgents` はこれを使い、結果は今と同じ。
			- `bandRowWidth(items, lead)`：帯の行の幅。各項目の幅は今の `bandModel` の式（`2·border + 2·pad + labelWidth(label) + labelGap + slot·エージェントの数`）、項目の間は `BAND.gap`、`lead`（行の頭の文字）があれば `labelWidth(lead) + BAND.labelGap` を先に足す。
			- `commandModel` に任意の引数を足す：
			  - `rows`：`[{key, left, top, lead, items}]`。各行の項目を `left`（`lead` があれば、その幅の後）から左から並べ、`y = top`、高さ `BAND.h`。渡さなければ、今のとおり `[{key: "", left: BAND.left, top: BAND.top, lead: null, items}]`。
			  - 帯の端は、その項目の行の `top + BAND.h`（今の `BAND.top + BAND.h` の一般化）。帯の項目の弧は、その項目の `y` から上へ（今の `BAND.top` の一般化）。
			  - `boundsOf(node)`：弧のふくらみの余白 `roomOf` の外枠（今は `{0, 0, layout.width, layout.height}`）。渡さなければ今のとおり。
			  - 戻りの `band` は、すべての行の項目を並べたもの `{top: いちばん上の行の top, h, items, right: いちばん右の端, rows: [{key, left, top, lead, leadWidth, items}]}`。`top`（初めの見え方の上の縁）は今のとおり `band.top − 16`、`width` は `max(layout.width, right + SIZE.margin)`。
			- 構造の図の今のテスト（T-01〜T-03 of iss-00616）が、そのまま通ること。
			"""
		satisfies: ["R-01", "R-02", "R-04"]
	}
	"D-02": {
		title: "対応・居場所・帯の形（allgraph/command.js、純粋な計算）"
		text: """
			新しい `views/allgraph/command.js`。DOM・時計・通信なし。

			- `repoOfWorktrees(repos, summary)`：`repos` は一覧の API の順の `[{key, structure}]`（読めていないリポジトリは `structure: null`）。
			  戻り `{of: Map<worktree, key>, unknown: boolean}`。各リポジトリのパスの集合（`structure.worktrees.status === "ok"` のときの `paths` の `normPath`）で、まずパスの当たりを、一覧の順の最初のリポジトリに決める。
			  残りの worktree は、各リポジトリでパスの当たった worktree の `project.id` と同じものを、一覧の順の最初のリポジトリに決める。`unknown` は、`structure` がない、または `worktrees.status` が ok でないリポジトリが1つでもあること（F-02）。
			- `crossPlace(pairs, {repos, summary, visible, orderOf})`：`repos` は `[{key, structure, layout, ix, graph}]`（`graph` は、その枠の本文がグラフであること）、`visible` は帯を渡さない `compose` の `order` の集合。
			  1. 各端の worktree のリポジトリ `k`（`of`）。`k` がないとき、`unknown` ならその組を落とし（F-02）、そうでなければ `{kind: "band", key, row: ""}`（『ほかの場所』）。
			  2. `k` があり `graph` なら、そのリポジトリの `placer` で居場所を決め、`repo: k` を付ける。band なら `row: k`。
			  3. `k` があり `graph` でなければ `{kind: "band", key, repo: k, row: k}`。
			  4. 見えない（`visible` にない）リポジトリ `k` の帯の端：その行に組の親の端が1つでもあれば `k` を `keep` に入れる（R-03）。なければ、その行の端を `row: ""` に移す。
			  5. 帯の項目：行ごとに `bandItems` を、その行の端だけの places と、own の集合（その行のリポジトリの worktree の集合。『ほかの場所』は空の集合）で呼ぶ（札：own なら「main のチェックアウト」かブランチ名、『ほかの場所』は「<project.name> · <branch>」）。
			  戻り `{pairs, places, rows: Map<row, items>, keep: Set<key>}`。
			- `bandShape(rows, keep)`：`compose` に渡す形 `{bands: {key: {h: REPO.band, w: bandRowWidth(items) + 2·REPO.pad}}, keep: [...], other: rows.get("") ? {h: REPO.other, w: bandRowWidth(items, "ほかの場所") + 2·REPO.pad} : null}` と、その鍵の文字列（同じ形なら同じ文字列。R-05）。
			- `crossModel({comp, repos, placed, spotsOf, orderOf})`：
			  - 世界の座標に移した配置：`comp.frames` で本文がグラフの各リポジトリ `k` の原点 `(f.body.x, f.body.y)` だけずらした node・塊の写し（`{…n, x1+ox, y1+oy, x2+ox, y2+oy, repo: k, src: n}`）と、依存の線の道（`r.eg.routes` の `pts` をずらしたもの）。`places` の node・group を写しに置き換える。
			  - `spotsOf(写し)`：`markSpots(src, そのリポジトリの測った幅と記録)` の矩形を同じだけずらす（F-03 は `markSpots` の null のまま）。
			  - `boundsOf(写し)`：そのリポジトリの本文の矩形 `{ox, oy, ox + L.width, oy + L.height}`。
			  - 帯の行：帯のある各リポジトリ `k` は `{key: k, left: f.x1 + REPO.pad, top: f.band.y1 + REPO.bandTop, lead: null}`、『ほかの場所』は `{key: "", left: comp.other.x1 + REPO.pad, top: comp.other.y1 + REPO.otherTop, lead: "ほかの場所"}`。
			  - `commandModel({pairs, places, rows, layout: {nodes, groups, width: comp.width, height: comp.height}, spotsOf, routes, boundsOf})`。
			- `crossKey`：同じ入力で同じ文字列（要約、各リポジトリの `eg` と測った幅と記録、`comp`。`commandKey` と同じ流儀の id）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-02", "F-03", "F-04"]
	}
	"D-03": {
		title: "枠の組み立ての口と補い（allgraph/compose.js）"
		text: """
			- `REPO` に足す（allgraph.css の写し。一緒に直す）：`band: 40`（帯の高さ。項目は上から `bandTop: 8` に高さ 28、下に 4。その下に本文の配置の余白 24 が続く）、`other: 56`（全体の帯の高さ。項目は上から `otherTop: 16`（帯の項目の上の弧の余白）に高さ 28、下に 12）。
			- `options.bands[key]`：数（今と同じく高さ）か `{h, w}`。`w` があれば、その枠の幅を `max(今の幅, w)` にする（帯の行が枠からはみ出さない）。
			- `options.keep`：key の配列か Set。そのリポジトリは、`visible` の判定によらず出す（R-03。中身は今の body の表のまま：『これから』で Scope のないものは本文の高さ 0）。その親のリポジトリは、子が出るので今の規則で出る。
			- `options.other`：`{h, w}` か null。あれば、すべての枠を `h` だけ下げ（`REPO.margin + h` から並べる）、戻りに `other: {x1: REPO.margin, y1: REPO.margin, x2: REPO.margin + max(w, 並べた幅), y2: REPO.margin + h}` を、`width` を `max(今の幅, w + 2·REPO.margin)` にする。なければ `other: null`。
			- 3つとも渡さなければ、戻りは今と同じ（`other: null` が足されるだけ）。
			- `anchorShift(prev, next, view)`：`view = {x1, y1, x2, y2}` は世界の座標の見えている範囲（`(-tx)/s` から `(clientWidth − tx)/s`、`(barBottom − ty)/s` から `(clientHeight − ty)/s`）。
			  `prev` で本文がグラフの枠のうち、本文の矩形が `view` と重なるものから、見えている上の端 `max(body.y, view.y1)` がいちばん小さいもの（同じなら `prev.order` の先）を選び、その key の `next` の本文の原点との差 `{dx, dy}` を返す（`next` にない、重なるものがない、なら `{0, 0}`）。
			  `allgraph.js` は、帯の形が変わって組み立て直したとき、`A.moved` なら `A.tx −= dx·A.s`、`A.ty −= dy·A.s`。
			"""
		satisfies: ["R-02", "R-03", "R-05"]
	}
	"D-04": {
		title: "共有の描画の部品（graph/command_view.js）"
		text: """
			`graph.js` の iss-00616 の描画のうち、画面の状態（`V`）に頼らない部分を、新しい `views/graph/command_view.js` に移す。`graph.js` はこれを呼び、出力（HTML の文字列と class）は今と同じ。

			- `layersHtml(model, {width, height})` → `{cmd, top, band}`：今の `drawCommand` の3つの要素の HTML（`.gx-cmd` の `.cl`（`cl-glow`・`cl-line` と `--cl-len`）、`.gx-cmd-top` の stubs（`--cl-len`）・端の点・帯の外の波紋、`.gx-band` の項目・ボタン・帯の中の波紋 `.gx-band-cr`）。
			  `model.band.rows` の行に `lead` があれば、その行の `left`・`top` に `<span class="gx-band-lead">` を置く（『ほかの場所』。構造の図では出ない）。
			- `paintBandMarks(bandEl, model, module, cache)`、`paintCmdSel(world, model, sel)`、`agentPanelHtml(...)`／`renderAgentPanel` の、DOM を受け取って描く部分。`soloWorktree`、`findAgent`、`ripple`、`inBand` も同じ所に置く。
			- `graph.js` の今のテストが固定の行として読む行（`test_dashboard_orca_views_js.py` の `import` の行、`onTap` の行など）は、そのまま残す。
			"""
		satisfies: ["R-04"]
	}
	"D-05": {
		title: "『横断の構造』への描画（allgraph.js）"
		text: """
			- 状態を足す：`A.cmdKey`、`A.cmdModel`、`A.cmdSel`、`A.agentPanel`、`A.shape`（今の帯の形と鍵。初めは形なし）、`A.shapeRedo`（F-05 の数え。要約の知らせと `render` で0に戻す）。
			- `draw()`：`compose(items(), sizes(N.own), {range, width, bands: A.shape.bands, keep: A.shape.keep, other: A.shape.other})`。帯の形が変わった組み立てのときは、組み立ての前の `A.comp` と後で `anchorShift` を求め、`A.moved` なら補う（R-05）。
			  世界の innerHTML の後、`paintOrca()` が今の流れの最後に `paintCommand()` を呼ぶ。`ResizeObserver` の後（`onMarksResize`）も呼ぶ（印の幅だけで端が動く）。
			- `paintCommand()`：要約（`orca.status()` が ok のときだけ）、組（`commandPairs`）。組がない、または `crossPlace` の組がないとき：帯の形があれば形をなくして `draw()`、なければ層を外す（F-01）。
			  組があるとき：`crossPlace`（`visible` は帯を渡さない `compose` の `order`）→ `bandShape`。形の鍵が `A.shape` と違い、`A.shapeRedo < 2` なら、`A.shape` を置き換えて `draw()` して戻る（F-05）。
			  同じなら、`crossKey` が前と違うときだけ `crossModel` で模型を作り、`layersHtml` の3つの要素を世界の最後に置く（`.gx-cmd`、`.gx-cmd-top`、`.gx-band`。z-index で重なるので DOM の順は問わない）。その後 `paintBandMarks` と `paintCmdSel`。
			- 層の大きさは `comp.width`・`comp.height`。世界の大きさは今のとおり `comp` の大きさ（帯は世界の中なので、初めの見え方と『収める』は今の計算のまま帯を含む）。
			- 指揮の選び：帯のボタンの押し（onTap・Enter・Space）で `A.cmdSel`・`A.agentPanel` を置き、Scope の選びを解き、欄に帯のエージェントのチャット（`renderAgentPanel`）。同じものをもう一度・閉じる・Esc・空いたところで解ける。
			  箱・枠の見出しの印の押しは、今の `if (!same) select(hit.repo, hit.id);` と `A.pn?.openAgent(markAgentAt(slot, target));` の2行をそのまま残し、その後に `A.cmdSel = markAgentAt(slot, target)` と `paintCmdSel`（構造の図と同じ）。`select()` は `A.cmdSel` を解く（印の押しはその後に置き直す）。
			  要約から消えたエージェントの選びと欄は解く（iss-00616 R-06 の `dropGone` と同じ）。
			- 凡例：`D.renderLegend(A.el.legend, A.legend, {cmd: !!orca && orca.status?.() !== "off"})`。
			- `dispose()`：層・状態・`window.specdockCmdAudit` を外す。
			- `window.specdockCmdAudit()`：`A.cmdModel.audit`（なければ0）、`spotDrift`（各リポジトリの描いた `.orca-mark` の箱の中の offset ＋ 本文の原点 ＋ node の位置と、`crossModel` の `spotsOf` の矩形の差の最大。帯のボタンの中央と計算の中央の差を含む）、`spotMissing`、`layers`（世界の子の class）、`pointer`（`.gx-cmd`・`.gx-cmd-top` の pointer-events）、
			  `heads`（見出しの文字の重なりの検査：世界の中のすべての `.gx-frame` の z-index が auto でない、その `:is(.gx-fh, .gx-fm)` の z-index が 2 でない、または見出しの文字・札（D-06 の対象）の背景の色が透明、の数。`.ax-head` も同じに数える）。構造の図の `cmdAudit` にも同じ `heads` を足す（ほかの項目は今のまま）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-07", "F-01", "F-05"]
	}
	"D-06": {
		title: "見出しの文字を線より上に置く CSS（graph.css・allgraph.css、両方の画面）"
		text: """
			- `graph.css`：`.gx .gx-world > .gx-frame` の z-index を `auto` にする（重なりの文脈を作らない。位置を持つ z-index auto の要素は、z-index 0 の層に文書の順で描かれるので、木の線（z 0、先）→ 枠 → 指揮の層（z 1）の順は今と同じ）。
			- 枠の地の色の変数：`.gx .gx-ini { --gx-fbg: color-mix(in srgb, var(--ds-surface) 55%, var(--ds-bg-2)) }`、`.gx .gx-epic { --gx-fbg: var(--ds-surface) }`、`.gx .gx-frame[data-st="done"] { --gx-fbg: var(--ds-surface-2) }`（今の背景の値の写し。背景もこの変数で書いてよい）。新しい色の値は足さない。
			- `.gx :is(.gx-ini, .gx-epic) > :is(.gx-fh, .gx-fm) { position: relative; z-index: 2 }`（行ごと上げる。行そのものには背景を付けない）。
			- 下地：`.gx :is(.gx-ini, .gx-epic) > .gx-fh > :not(.gx-agents)` と `.gx :is(.gx-ini, .gx-epic) > .gx-fm > *` に `background-color: var(--gx-fbg)`。自分の地の色を持つ札（`.ds-docid`、`.sbar`、`.hm`、`.dn`、片付けの印など。実装担当が今の CSS から列挙する）は、`background: linear-gradient(<自分の色>, <自分の色>) var(--gx-fbg)` の2層にして、見え方を今と同じにする（暗いテーマの `--ds-accent-soft` は半透明のため）。
			- `allgraph.css`：`.gx .ax-body > .gx-frame` の z-index を `auto`。`.gx .ax-head { z-index: 2 }`、`.gx .ax-head > * { position: relative; background-color: var(--ds-bg-2) }`、`.gx .ax-repo:is([data-depth="1"], [data-depth="3"]) .ax-head > * { background-color: var(--ds-surface-2) }`（今の枠の背景の写し。独自の変数は書かない）。`.ax-link:hover` の背景は今のまま上に効かせる。
			- 『ほかの場所』の行の頭：`.gx .gx-band-lead { position: absolute; height: 28px; line-height: 28px; font-size: 11.5px; font-weight: 700; color: var(--ds-text-2); white-space: nowrap }`（graph.css の帯の規則の所。帯の寸法の写しのコメントに足す）。
			- 帯（z 6）、端の層（z 3）、依存の線（z 5）、箱（z 2）、指揮の層（z 1）は今のまま。見出しの行（z 2）は箱と重ならない。暗くした枠（`is-dim`・`is-poff` の opacity）の見出しの行は、それ自体が z 2 の重なりの文脈になるので、線より上のまま淡くなる。
			- 入れ子の枠の見出しの同じ枠の弧（iss-00616 の `frameArc`、印の下へ 12px）は、要約の行の文字の後ろを通る所が隠れる（risks）。
			"""
		satisfies: ["R-06"]
	}
	"D-07": {
		title: "確かめのしかた"
		text: """
			- 純粋な計算（T-01〜T-03）：`tests/js/dashboard_allgraph_command.mjs`（新）を `tests/unit/presentation/test_dashboard_allgraph_command.py`（新）が今の流儀（`test_dashboard_allgraph_compose.py` と同じ形）で呼ぶ。`compose` の口と `anchorShift` は今の `dashboard_allgraph_compose.mjs` に足す。合成の名前と値だけを使う（実際のパス・IP・セッションの id、本人の環境の名前を書かない）。
			- 構造の図の今のテスト（`test_dashboard_graph_command.py`・`test_dashboard_graph_command_screen.py`・golden）がそのまま通る。変えてよいのは、R-06 の CSS を確かめる期待（`.gx .gx-world > .gx-frame` の z-index）と、新しい `heads` の項目だけ。
			- CSS の静的な検査（T-04）：両方の CSS の R-06 の規則、`allgraph.css` に色の値と独自の変数がない（今の検査）、指揮の規則に `<animate`・`animateMotion`・`canvas`・`blur(` がない（今の検査の範囲に `.gx-band-lead` を足す）。
			- 画面（T-05）：`tests/js/fake_dom.mjs` の偽の DOM と偽の orca で `allgraph.js` を描く（今の `dashboard_allgraph_screen.mjs` の組み立てに、要約の `parent` を足す）。層の有無、帯の位置と枠の高さ、入れ物の枠の出入り、要約だけの更新で `routeLayout` の呼び数が増えない、同じ形で `compose` をやり直さない、補い、帯の押しのチャット、印の押しの選び、凡例の行、組がないときの世界の HTML。
			- 実機（T-06）：iss-00616 の実機と同じ組み立て（この worktree の wheel を隔離した venv に入れ、この PC の状態の置き場の写しと試しの設定で `spec-dock dashboard serve --offline --tailscale --port <空いたポート>`、GET だけを中継する試しの orca の口）。常駐のダッシュボード（47800）と orca-web（8791）の設定、道具の環境には触れない。
			  headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close`）で『横断の構造』を 1440・390 × 明・暗 × 全体・いま・これから で写し、`specdockEdgeAudit().total` の違反、`specdockCmdAudit()`、ブラウザーのエラー、横のスクロールを数える。構造の図でも、見出しの上を線が通る所（init-00423 の見出しなど）を拡大して前後を写し、`heads` 0 を数える。
			  リポジトリをまたぐ線・帯だけの入れ物の枠・『ほかの場所』の帯が今の実データにないときは、統括に試しのエージェント（例：あるリポジトリの main のチェックアウトに親、別のリポジトリの Issue の worktree に子）を頼む。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07"]
	}
}

compatibility: """
	組がないとき（Orca につながっていない、親の項目がない古い orca-web、組がない要約）、『横断の構造』の世界の HTML と枠の位置は今のまま（`compose` に帯の形を渡さない）。
	両方の画面の枠の見出しは、重なりの順と、枠と同じ色の下地だけが変わり、組がないときの見え方は今と同じ。構造の図の線と帯の出力は、共有の部品に移しても今と同じ。
	PR を戻すと、『横断の構造』の線と帯がなくなり、両方の画面で線が見出しの文字の上をまた通る。API・保存（localStorage）・モデルは変わらない。
	"""

risks: [
	"枠の z-index を auto にすると、枠の中の要素（大もとの札 `.rt`、変化の印など）の z-index が世界の重なりの文脈に出る。今の値（`.rt` は 2）で箱や線との順が変わらないことを、写しで確かめる",
	"下地を自分の地の色を持つ札に重ねるとき、列挙の漏れで暗いテーマの札の色が変わりうる。明・暗の写しの見出しの拡大で、前後を比べる",
	"入れ子の枠の見出しの同じ枠の弧は、要約の行の文字の後ろを通る所が隠れる。弧のふくらみは 12px で、行の間のすき間には見える。今の実データにこの組は少ない",
	"帯の形が要約の更新のたびに揺れると（エージェントの出入り）、枠の組み立てが繰り返され、下の枠が動く。補いは見えている枠だけを保ち、組み立ての数え（F-05）で止める",
	"帯の行が長いと、そのリポジトリの枠が広がり、ほかの枠の並び（折り返し）が変わる。帯の項目の札は 200px で切れる（`labelWidth`）ので、広がりはエージェントの数に比例する",
	"`placeAgents` を `placer` に分けるとき、構造の図の居場所が変わりうる。iss-00616 の T-01 がそのまま通ることで確かめる",
]
