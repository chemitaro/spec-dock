package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"端と道の形だけを `command.js` の純粋な計算で変え、描き方（iss-00646）の仕組みはそのまま使う",
	"どの端も『上の縁・上向き』の1種類にし、場合分けを減らす",
]

current: "端は下（箱の中の短い線つき）か相手に向いた縁、道は両端の向きの三次ベジェ、同じ箱・枠・項目は下・右・見出しの下・上の弧。子の端に点。"

target: "端はすべて上の縁・上向き、道は上にふくらむホップの三次ベジェ、同じ箱・枠・項目は上の縁の小さなホップ。子の端に下向きの矢じりと印の縁。"

design: {
	"D-01": {
		title: "端：すべて上の縁、上向き（`commandModel` の `fixedEnd`・`faceOf`）"
		text: """
			`fixedEnd(ref)` の返す端 `{kind, p, n, spot, …}` を次にする。`n` はどれも `UP = {x: 0, y: −1}`。`stubs` はどれも `[]`（返す線の `stubs` も `[]`。描き方の `endsHtml` は空の `stubs` をすでに扱う）。
			- `mark`（箱・木の枠の箱・入れ子の枠）：`p = {x: spot.x + spot.w/2, y: node.y1}`、`spot` は今の `markSpots` の四角。
			- `band`：`p = {x: slot の中央, y: item.y}`、`spot` は今の帯の印の四角。
			- 印の位置が分からない `mark`（F-01）：`p = node の上の縁の中央`、`spot: null`、`unknown: true`。
			- `group`・`frame`（印のない端）：`faceOf` をやめ、`p = 上の縁の中央`（`SIDES.top.at(rect)`）、`side: "top"`、`n: UP`。枠が相手を中に含む場合（今の `inside`）も同じ。同じ縁から出る線を `SPREAD`（10px）ずつずらす今の仕組みは、そのまま（`along: "x"`）。
			`DOWN` と、`faceOf` の `left`・`right`・`bottom`・`inside` の選び分けは使わなくなる（消す）。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "道：ホップの三次ベジェ（`hop(P, C, ceiling)`）"
		text: """
			定数 `HOP = { min: 18, kx: 0.15, ky: 0.1, max: 56, side: 40, chord: 12, room: 3, low: 8 }`（`export`）。
			`hop(P, C, ceiling = −Infinity)`（`export`、純粋）：
			1. `dx = |C.x − P.x|`、`dy = |C.y − P.y|`、`H = clamp(HOP.kx·dx + HOP.ky·dy, HOP.min, HOP.max)`。
			2. `top = min(P.y, C.y) − H`。`top < ceiling` なら `top = ceiling`（F-02。ただし `min(P.y, C.y) − top` が `HOP.low` より小さくはしない）。
			3. 制御点の縦の長さ：`h1 = P.y − top`、`h2 = C.y − top`、`kP = λ·h1`、`kC = λ·h2`。λ は、道の頂点（t を 1/96 刻みで取った点の y の最小）がちょうど `top` になる値を、[0, 4/3] の二分探索（40回）で求める。各 t の y は λ について単調に減り、λ = 0 で頂点は `min(P.y, C.y)`（`top` より下）、λ = 4/3 で `top` 以上の高さに届く（同じ高さの端ではちょうど `top`）ので、解は1つに決まる。こうして、高さの差が大きくても頂点が `top` を越えない（`ceiling` も越えない）。
			4. 横のふくらみ：`dx < HOP.side` なら `b = min(HOP.side − dx, 0.5·min(kP, kC))`（λ を決めた後の値）、`s = C.x ≥ P.x ? 1 : −1`。でなければ `b = 0`。横のふくらみは頂点の高さを変えない（制御点の x だけを動かす）。
			5. `c1 = {x: P.x + s·b, y: P.y − kP}`、`c2 = {x: C.x + s·b, y: C.y − kC}`、道は `M P C c1 c2 C`、`len` は今の `roundLen(bezierLength(…))`。返すのは `{d, len, peak}`（`peak` は手順3の頂点の y、四捨五入 0.1）。
			違う箱・枠・項目の線（`kind: "curve"`）は `hop(a.p, b.p, ceiling)` で描く。今の `k = min(140, max(24, 0.45·L))` の曲線はやめる。
			"""
		satisfies: ["R-01", "R-02", "F-02"]
	}
	"D-03": {
		title: "同じ箱・同じ枠・帯の同じ項目の弧：上の縁の小さなホップ（`sameHop`）"
		text: """
			`boxArc`・`frameArc`・`bandArc` を1つの `sameHop(a, b, self)`（`self` は箱・枠のノード、または帯の項目）に置き換える。
			1. 端は `a.p`、`b.p`（どちらも `self` の上の縁、D-01）。`|b.p.x − a.p.x| < HOP.chord` なら、今の `widen` と同じ考え方で、2点の中点を中心に `HOP.chord` 離し（`self` の左右の縁の内側に収め）、親を左に置く順序は今の `widen` に従う。
			2. 上の余白 `room`：`self` の上の縁から上へ、`[lo, hi]`（2つの端の x の範囲）に重なる、最も近いほかのノード・塊・帯の項目の下の縁まで、`self` を含む枠の内側の上の縁（`y1 + 1`）まで、世界の範囲（`boundsOf` か `{0, 0, width, height}`。ただし帯の項目には世界の上の縁を使わない）までの最小。今の `roomOf` に `top` の向きを足し、`bottom`・`right` を消す。`self` を含む枠は障害に数えない（今と同じ）。
			3. 高さ `d = min(HOP.min, room − HOP.room)`。`d < HOP.min` なら `audit.crowded++`。`d < HOP.low` なら `d = HOP.low`。
			4. 道は、両端を上向きに `4d/3` の制御点で結ぶ三次ベジェ（今の `arcOut(e1, e2, UP, d)`）。
			5. 検査：ふくらみの四角（`bulgeBox(e1, e2, UP, d)`）が `self` を除く障害と重なれば `boxOverlaps++`、依存の線の水平な区間と重なれば `edgeOverlaps++`（今の `overlapsBox`・`overlapsRoute`）。`audit.arcs` と `audit.links` を数える（今と同じ）。
			返す線は今と同じ `{kind: "arc", d, len, stubs: [], bulge: d, from, to}` に、D-04 の `mark` と `peak`（`self` の上の縁の y − d。両端を同じ高さで 4d/3 の制御点で結ぶ三次ベジェの頂点は、ちょうど縁から d 上）を足したもの。`ARC_D`・`FRAME_ARC_D`・`CHORD`・`ARC_MIN` は `HOP` に置き換える。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "子の端の矢じりと、受けた印の縁"
		text: """
			`commandModel` の各線に `mark` を足す：子の端に印の四角があれば `{x, y, w, h, band}`（`band` は子が帯の印のとき true）、なければ null（F-01、塊・祖先の枠）。
			`command_motion.js`：
			- `ARROW = { len: 6, half: 3.5 }`、`arrowPath(to)`（`export`、純粋）：先を `to` に置いた下向きの三角 `M (to.x − half) (to.y − len) L to.x to.y L (to.x + half) (to.y − len) Z`。
			- `markRect(m)`（`export`、純粋）：印の四角を 2px 外へ広げた角丸の四角 `<rect class="cl-in" x y width height rx="4">`。
			- `endsHtml(link)`：`stubs` のほか、`cl-dot` の代わりに `<path class="cl-arrow" d="…"/>` を描き、`mark` があり `band` でなければ `cl-in` を同じ SVG に描く。SVG の四角（`boxOf`）は、矢じりの3点と縁の四角を含める。切り替えの絵は今のとおり `stubs` だけに付ける（`stubs` は空なので、端の層は止めた絵1枚になる）。
			- `bandMarkHtml(link)`（`export`）：`mark.band` のとき、`cl-in` だけを持つ線ごとの SVG（`<g class="cl" data-id data-state>`）。
			`command_view.js` の `layersHtml`：帯の印の縁を、波紋と同じ帯の入れ物（`.gx-band-cr`）に入れる（入れ物は、波紋か縁があるときに作る）。`paintCmdSel` の線の選択子に `.gx-band-cr .cl` を足す。
			`graph.css`：`.gx .cl-arrow { fill: var(--sd-cmd); stroke: none; }`、`.gx .cl-in { fill: none; stroke: var(--sd-cmd); stroke-width: 1.5; }`、`.gx .cl[data-state="done"] :is(.cl-arrow, .cl-in) { opacity: .35; }`。`.cl-dot` の規則を消す。`.gx-band-cr` の中の `.cl-svg` も今の `.cl-svg` の規則（absolute、overflow visible）に従う。押したときの薄め（`.has-cmd-sel .cl.is-cmd-off`）は今の規則で縁にも効く。
			"""
		satisfies: ["R-04", "F-01"]
	}
	"D-05": {
		title: "世界の上の縁と、横断の構造の天井"
		text: """
			`commandModel` の `top` を `min(帯があれば band.top − 16 、なければ 0, 0, すべての線（`curve` と `arc`）の peak − 6)` にする（構造の図の『収める』と世界の大きさが、帯の上へふくらむ弧を含む）。今の `top` の使い方（`graph.js` の `V.cmd.top`）は変えない。
			`commandModel` に引数 `ceiling`（既定 −Infinity）を足し、`hop` と `sameHop` の高さの上限に使う（`sameHop` は `room` を `self.y1 − ceiling` 以下にする）。`allgraph/command.js` の `crossModel` は `ceiling: 4` を渡す（横断の構造の世界は y が 0 から始まり、`top` を使わないため。F-02）。
			"""
		satisfies: ["R-02", "F-02"]
	}
	"D-06": {
		title: "Epic epic-00615 の文書の直し"
		text: """
			requirement.cue：F-05（印の位置が分からない端を上の縁の中央に）、R-04 の text と acceptance の端（『印の位置から出て』『箱の中の部分（印から箱の縁までの短い線）』『印の行に近い縁の外へ…違う行なら右の縁の外』『枠の見出しの統括の印の下から下へ出て』）を、上の縁のホップ（iss-00648）に書き換える。R-05 と制約の『stroke-dashoffset（点の流れ）』を、止めた絵4枚の opacity の切り替え（40px/秒、iss-00646）と HTML の輪の波紋に書き換える。decisions に、この Issue と iss-00646 の決定で置き換えたことを1行ずつ足す（前の決定の行は消さない）。
			design.cue：D-03 の線の描き方（箱の中の短い線をやめ、矢じりと印の縁、帯の印の縁は帯の層）、D-02 の端と道（下・内側の下の縁・`stubs`・制御点の長さ）、D-04 の動き（『端から端まで2〜3秒』『stroke-dashoffset』『世界の中の SVG の層』）、D-10 の弧（縁の選び・弦 40px・下や右の縁）を、iss-00646 と iss-00648 の設計を指す短い文に書き換える。番号と `satisfies` は変えない。
			直した後に `spec-dock scope check epic-615` を通す。
			"""
		satisfies: ["R-06"]
	}
	"D-07": {
		title: "確かめ（実機と測り）"
		text: """
			試しのサーバー：直す前は基準のコミット `92e26aff7` を隔離した venv（ポート 18649、ローカルだけ）、直した後はこの worktree を editable で隔離した venv（18648、`--tailscale`）。同じ状態の置き場の写しと、常駐の orca-web を GET で読むだけの中継（18848）。headless Chrome は `--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じる。
			写し：今の Run の実データ（帯の統括 → Issue の箱のタスク担当、同じ箱のタスク担当 → 実装担当、横断の構造のリポジトリをまたぐ線）で、構造の図と横断の構造を 1440・390、明暗、『全体・いま・これから』で、直す前と後を並べる。足りない場面は、統括に試しのエージェントを頼む。
			測り：iss-00646 の台本（1440×900、deviceScaleFactor 2、読み込みの15秒後から10秒の TaskDuration）で、前と後を交互に3回ずつ、動きありと減らす設定。
			検査：両方の画面で `specdockEdgeAudit()`、`specdockCmdAudit()`（`boxOverlaps`・`edgeOverlaps`・`heads`・`spotDrift`・`spotMissing`・`crowded`）、ブラウザーのエラー。
			"""
		satisfies: ["R-02", "R-03", "R-04", "R-05"]
	}
}

compatibility: "表示だけの変更。モデルの線の形（`from`・`to`・`d`・`stubs`）は変わるが、使うのは dashboard の中だけ。`specdockCmdAudit()` の項目は同じ。"

risks: [
	"帯から下の箱への線は、帯の上へ出てから帯の項目の後ろを通って降りる（帯の層は線の上）。写しで見え方を確かめ、本人の確かめを受ける。",
	"違う箱の間の弧は、上にある箱の後ろを通る（今の曲線と同じ）。頂点の高さの上限 56px は写しで確かめる。",
	"箱の上の余白が 14px の場所では、同じ箱の弧が 11px に下がる（`crowded`）。",
]
