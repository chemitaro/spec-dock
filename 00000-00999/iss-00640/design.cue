package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"CSS の数行だけで直し、DOM・JavaScript・スマホの並びを変えない",
	"幅の境目（px の値）を決め打ちせず、flex の折り返しに任せて、札と道具が入るかで1行か2行かが決まるようにする",
]

current: """
	- 帯は `.gx-bar`（flex、wrap、space-between、gap 8px 16px）> `.gx-left`（縦の列：構造の図は道筋 `.gx-crumbs` と札 `.gx-next`、横断の構造は札 `.gx-next` とまとめの行 `.ax-sum`）と `.gx-tools`（margin-left: auto）。
	- 横断の構造では `.gx-left` の高さが札 + まとめの行なので、道具の列が1行目に入らないと、`.gx-left` 全体の下（まとめの行の下）に折り返す。
	- `.ax-sum` は `width: 0; min-width: 100%`（iss-00632）で、札の列の幅に収まる。
	- 最初の表示と『収める』の上端は `barBottom()`（`.gx-next`・`.ax-sum`・PC の `.gx-tools` の下端の最大）+ 8。
	- スマホ（`@container app (max-width: 640px)`）では `.gx-bar` が `display: contents`、`.gx-left` が上の絶対配置、`.gx-tools` が右下の縦の列。
	"""

target: """
	- PC（`@container app (min-width: 641px)`）の横断の構造では `.gx-left` が `display: contents` になり、`.gx-next`・`.ax-sum` が `.gx-bar` の flex の項目になる。
	- `.ax-sum` は `order: 1; flex-basis: 100%` で、札（order 0）と道具（order 0、DOM で後）の後の、自分だけの行に並ぶ。
	- 札と道具は同じ行に入れば1行、入らなければ道具が次の行に折り返し、`margin-left: auto` で右寄せになる。
	"""

design: {
	"D-01": {
		title: "横断の構造の PC の帯の並び（allgraph.css）"
		text: """
			allgraph.css に次を足す（新しい色・トークンなし）：

			```css
			@container app (min-width: 641px) {
			  .gx[data-screen="allgraph"] .gx-left { display: contents; }
			  .gx[data-screen="allgraph"] .ax-sum { order: 1; flex-basis: 100%; }
			}
			```

			- 641 は allgraph.js・graph.js の `PHONE = 640`（`isPhone` は app の幅 ≤ 640）と、graph.css のスマホの `@container app (max-width: 640px)` の補い。スマホの規則には触れない。
			- `.gx-left` の `pointer-events: none`（iss-00632）は `display: contents` で箱がなくなっても、子へ引き継がれる値として残る。`.gx-next` は auto、`.ax-sum` は none、その `li` は auto のまま（帯の空きは図に届く）。
			- `.ax-sum` の `width: 0; min-width: 100%` は残す。flex の項目としては `flex-basis: 100%` と min-width 100% で帯の幅になり、スマホでは今と同じく札の列の幅になる。
			- 行の間は `.gx-bar` の row-gap 8px（`.gx-left` の gap 8px と同じ）。
			"""
		satisfies: ["R-01", "R-04", "F-01"]
	}
	"D-02": {
		title: "構造の図は変えない"
		text: "graph.css・graph.js は変えない。構造の図の `.gx-left` は札（と道筋）だけで、道具の列は札の列の次の行に右寄せで出るので、既に R-02 の形になっている。"
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "最初の表示と『収める』の追従（変えない、検査を足す）"
		text: """
			allgraph.js の `barBottom()` は、`.gx-next`・`.ax-sum`・PC の `.gx-tools` の下端の最大を取るので、並びが変わってもそのまま追従する（`display: contents` の `.gx-left` の子も `offsetParent` を持つ）。
			JavaScript は変えず、node の検査の写し（`tests/js/dashboard_allgraph_screen.mjs` の `hooks.rect`）で、札・道具・まとめの行の下端を別々に与えられるようにし、
			最初の表示の ty と『収める』の上端が最大の下端 + 8 になることを確かめる。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "実機の確かめ"
		text: """
			開始のコミットの wheel（直す前）と直した後の wheel を、それぞれ隔離した venv と、この PC の状態の置き場の写しで `spec-dock dashboard serve --offline` に立て
			（直した後は `--tailscale`、試しの orca-web の中継つき）、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close`）で測る。
			1000・1280・1440・390 × 横断の構造・構造の図で、帯・札・道具・まとめの行の矩形と最初の表示の ty、写し（明）。
			横断の構造の 1000・1280・1440・390 × これから・いま・全体 × 明暗（24組）で edgeAudit の total の違反と横のスクロール。
			常駐のダッシュボード（47800）と orca-web（8791）の設定、道具の環境には触れない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04"]
	}
}

compatibility: "DOM・API・保存は変わらない。スマホの並びは変わらない。PC の横断の構造では、まとめの行が札の列の幅から帯の幅に広がる（省略が減る）。"

risks: [
	"帯の右で Scope の欄が開くと、帯が狭くなり2行の形になる（F-01 の決まった形）。",
	"`display: contents` の要素に付けた見た目（背景・枠）は描かれない。`.gx-left` には見た目がないので影響しない。",
]
