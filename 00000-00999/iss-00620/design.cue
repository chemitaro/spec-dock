package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"行の数を決める規則を layout.js の純粋な関数1つにし、配置と画面の両方がそれを使う（node のテストで確かめられる）",
	"印の入力がないときの配置を1つも変えず、iss-00603 の digest の比較で確かめる",
	"印の幅は部品の実寸を測り、行の数が変わったときだけ配置をやり直す",
]

current: """
	- `graph.js` の `boxHtml` は、下の段 `.gx-marks` に `asMark`・片付けの候補・`prMark`・`wtMark`・`hmMark`・`dnMark`・`orcaSlot(s.id, 2)` を並べる（木の枠の箱は `sbar`・`frac`・`counts`・`asMark`・候補・`hmMark`・`dnMark`・`orcaSlot(s.id, 2)`）。
	  `frameHtml` は見出し `.gx-fh` の終わりに `orcaSlot(s.id, 3)`、要約の行 `.gx-fm` に `dnMark`。凡例に「後に続く数」。箱の aria-label に「後に続く n件」。
	- `.gx-marks`・`.gx-fh` は折り返さない flex。置き場 `.sd-orca` は `flex: none; margin-left: auto`（app.css）。部品の `.orca-marks` は `inline-flex; flex-wrap: wrap; gap: 2px; max-width: 100%`。
	- `orca_marks.js` の `paintOrcaMarks` は置き場の `data-orca-max` を数にして `buildMarks`・`renderAgentMarks` の `max` に渡す。部品は `max` を越えると先頭の max−1 個と『+N』を描き、`max` が1以上の整数でなければ 4 とみなす。
	- `layout.js` の箱の高さは `SIZE.boxH + grow`、入れ子の枠の見出しは `SIZE.head + grow`（grow は線の口の数で伸ばす分）。印の行は数えない。
	- 要約が来るたびに `paintOrca` が印だけを描き直し、配置はやり直さない。
	"""

target: """
	- 構造の図から dnMark が消え、置き場は上限なし（`data-orca-max="all"`）。
	- layout.js が箱・枠ごとの印の測った幅（`opts.marks`）から行の数を決め、箱・見出しを伸ばす。
	- graph.js が印を描いた後に測り、今の配置と行の数が違うときだけ配置をやり直す。
	"""

design: {
	"D-01": {
		title: "行の数の規則（layout.js の markRows と rowsOf）"
		text: """
			layout.js に次を足して export する（DOM なし）。

			```js
			export const MARK_ROW = 20; // 稼働の印の行1つ分：部品の sm の高さ 16px と行の間 4px（graph.css）
			export const MARK_INSET = { box: 26 }; // 箱の幅から下の段の幅を引く分：左の縁 4 + 左の余白 11 + 右の余白 10 + 右の縁 1（graph.css .gx-box）
			export const FRAME_TITLE_MIN = 96; // 入れ子の枠の見出しで題名に残す最小の幅（px）
			export function markRows(m, avail, reserve = 0)
			export function rowsOf(node, m)
			```

			`m` は1つの箱・枠の印の測った幅 `{lead, items, gap}`：`lead` は同じ行のほかの印の幅とその行の flex の間（稼働の印の前の間を含む。題名は含まない）、
			`items` は稼働の印1つずつの幅（部品の並び順）、`gap` は稼働の印どうしの横の間（部品の 2px を測った値）。

			`markRows(m, avail, reserve)`：
			1. `m` がない、または `items` が空 → 1。
			2. `one = Σitems + gap × (items.length − 1)`。`lead + reserve + one ≤ avail` → 1（R-04 の2：1行目の右寄せ）。
			3. そうでなければ、`items` を順に `avail` の幅へ詰める（先頭から、次の印が `x + gap + w > avail` なら改行。`avail` より広い印は1つで1行）。その行の数を `k` とする。
			4. `lead > 0 || reserve > 0` なら `1 + k`（R-04 の3：ほかの印・題名の行の次から）、そうでなければ `k`（R-04 の4）。

			`rowsOf(node, m)`：layout の node（`type` が box・tframe・frame）について、
			- box・tframe：`markRows(m, (x2 − x1) − MARK_INSET.box)`。
			- frame（入れ子の枠）：`padX` を `SIZE.pad[kind]` の横（Initiative 16、Epic・Issue 12）として `markRows(m, (x2 − x1) − 2 × padX − 2, FRAME_TITLE_MIN)`（2 は左右の縁）。
			- ほかの type や `m` なし：1。

			配置の中（D-02）も同じ `markRows` を同じ幅で呼ぶので、graph.js が今の layout の node に `rowsOf` を使った値は、その layout の行の数と必ず一致する（T-05）。
			"""
		satisfies: ["R-04", "R-05"]
	}
	"D-02": {
		title: "配置が印の行を高さに入れる（layout.js）"
		text: """
			`layout`・`routeLayout` の options に `marks`（Scope の id → D-01 の `m` の object。省略や `{}` は印なし）を足す。`rangeOpts` は値を変えずに通す。

			- `boxBlock`：`rows = markRows(ctx.opts.marks?.[s.id], SIZE.boxW − MARK_INSET.box)`、`h = SIZE.boxH + grow + (rows − 1) × MARK_ROW`。
			- `tree` の項目（tbox）：`w`（枠の箱は treeFrameW、箱は boxW）で同じく `rows` を求め、`h = SIZE.boxH + grow + (rows − 1) × MARK_ROW`。
			- `frameBlock`：`w` を今のとおり求めた後、`rows = markRows(m, w − 2 × padX − 2, FRAME_TITLE_MIN)`、`head = SIZE.head + grow + (rows − 1) × MARK_ROW`。中身の `y` と枠の `h` は今の式のまま head から決まる。
			- `flatten`：box・tframe・frame の node に、`rows > 1` のときだけ `rows` を足す（1 のときは鍵を足さない。印なしの nodes が今と同じ JSON になる）。

			幅、`SIZE` の既存の値、段・行・包み（pack）の決め方は変えない。伸びた高さは今の包みと線の引き方にそのまま入り、routeLayout の検査と幅の広げ方は伸びた箱で回る（R-05）。
			"""
		satisfies: ["R-05", "F-01"]
	}
	"D-03": {
		title: "印の幅は部品の実寸を測る（graph.js の measureMarks）"
		text: """
			**決めたこと：決まった幅ではなく、描いた部品の実寸を測る。** 理由：

			- 印の幅は、エージェントの種類のロゴ、monitoring の印、スリープの月、経過の文字（now、7m、39m、12h…）で変わり、ほかの印（PR の印、人のタスクの数、進み具合）も箱ごとに違う。
			  決まった幅を最大に取ると、収まる箱も早く折り返して高さが無駄に伸び、平均に取るとはみ出す（本人の写しの不具合そのもの）。
			- 印の大きさは orca-web の部品が決める（R-07 で変えない）。SpecDock に幅の表を写すと、部品が変わったときに黙ってずれる。測れば部品の今の大きさに従う。
			- 測るのは描いた後なので、行の数の規則は D-01 の純粋な関数に分け、そこを node で確かめる。測る部分は小さく保ち、実機で確かめる（T-08）。

			`measureMarks(world)`（graph.js）：`[data-orca-scope]` の置き場ごとに、中に `.orca-mark` が1つ以上あれば、その箱・枠の id（置き場の `data-orca-scope`）に `{lead, items, gap}` を返す。
			- 幅は `getBoundingClientRect().width / V.s`（拡大の分を戻す）を小数第1位で切り上げる（足し合わせて実際より小さくならないように）。
			- `items`：置き場の中の `.orca-mark` ごとの幅（描いた順）。`gap`：部品の `.orca-marks` の `getComputedStyle().columnGap`。
			- `lead`：置き場の親の行（`.gx-marks` か `.gx-fh`）の子のうち、置き場と題名（`.gx-fttl`）を除いたものの幅の和 + その行の `columnGap` ×（子の数 − 1）。
			- 測れない（F-02）：図が隠れている、どれかの幅が0、部品の `.orca-marks` の `flexWrap` が `wrap` でない（部品の CSS がまだ効いていない）→ `null`（配置を変えない）。
			"""
		satisfies: ["R-04", "R-06", "F-02"]
	}
	"D-04": {
		title: "行の数が変わったときだけ配置をやり直す（graph.js の checkRows）"
		text: """
			`V.marks`（最後に測った印、初めは `{}`）を `buildWorld` の routeLayout の options の `marks` に渡す。

			`checkRows()`：`M = measureMarks(V.el.world)`。`null` なら何もしない。今の配置 `V.EG.layout.nodes` の box・tframe・frame ごとに `rowsOf(node, M[node.id])` を求め、
			`node.rows ?? 1` と1つでも違えば、`V.marks = M` にして、`V.sig = null` で `render(V.root, V.ctx)` を呼ぶ（`V.fitted` を保つので拡大・位置は変わらない。選択と横の欄も render のまま保つ）。
			どれも同じなら `V.marks = M` だけを更新し、配置はやり直さない（R-06：経過の文字だけの変化では箱を作り直さない）。

			呼ぶところ：
			- `paintOrca()` の `paintOrcaMarks` の後（要約のたび、描いた後のたび）。
			- `ResizeObserver` で `.gx-world` の置き場（`.sd-orca`）を見て、大きさが変わったら `requestAnimationFrame` で1回にまとめて `checkRows`（部品の CSS や字体があとから効いたとき。R-06 の3つ目）。`buildWorld` のたびに見る要素を付け直し、`dispose` で外す。
			- 揺れの歯止め（F-03）：`checkRows` からのやり直しを数え、要約（`orcaWatch` の知らせ）・大きさの変化・データの変化のたびに0に戻す。2回を越えたらやり直さない。

			やり直しで `render` → `paintOrca` → `checkRows` が再び呼ばれるが、そのときは今の layout の行の数と一致するので止まる（D-01 の一致）。
			"""
		satisfies: ["R-06", "F-02", "F-03"]
	}
	"D-05": {
		title: "画面：dnMark を消し、置き場を上限なしにし、折り返す（graph.js・marks.js・parts.js・orca_marks.js・graph.css）"
		text: """
			- `boxHtml`：`M.dnMark(s.downstream)` を2か所から消し、aria-label の「。後に続く n件」を消す。置き場は `orcaSlot(s.id, "all")`。`n.rows > 1` なら `.gx-marks` に `is-wrap` を足す。
			- `frameHtml`：見出しの置き場を `orcaSlot(s.id, "all")` にし、`n.rows > 1` なら `.gx-fh` に `is-wrap` を足す。要約の行 `.gx-fm` から `M.dnMark` を消す。
			- `renderLegend`：「後に続く数」の `li` を消す（ほかの行と「矢印：…出る線＝後に続く」は残す）。
			- `marks.js`：`dnMark` を消す。`tests/js/dashboard_marks_dump.mjs` と `tests/fixtures/issue544/marks-golden.json` から `dnMark` の項目を消す。
			- `parts.js` の `orcaSlot(id, max)`：`max` は数か `"all"`（`data-orca-max="all"`）。ボード（4）と横の欄（4）は今のまま。
			- `orca_marks.js` の `paintOrcaMarks`：`data-orca-max` が `"all"` のとき、`max = Math.max(1, worktree.agents の数)`（配列でなければ 1）。部品の `max` の意味は変えない（全員が max 以下なので『+N』は出ない）。
			- `graph.css`：`.gx .dn` とそれに関わる規則（`.gx-marks .dn`、`.hm + .dn`、`:is(.hm, .dn) ~ .sd-orca`）を `dn` なしに直す。
			  `.gx :is(.gx-marks, .gx-fh).is-wrap { flex-wrap: wrap; row-gap: 4px; }`、`.gx .is-wrap > .sd-orca { flex-basis: 100%; margin-left: 0; }`、`.gx .sd-orca .orca-marks { row-gap: 4px; }`。
			  1行目の右寄せ（今の `margin-left: auto`）はそのまま。折り返した稼働の印の行は左寄せ（部品の既定）。新しい色を足さない（R-07）。
			- `edgeAudit`：結果に `markOverflow`（稼働の印 `.orca-mark` のどれかが、その箱・枠の内側の右の縁か、箱の下の縁を 0.5px より越える箱・枠の数）を足す。実機の確かめ（T-08）に使う。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-07", "F-01"]
	}
	"D-06": {
		title: "テストの置き場"
		text: """
			- layout（node、`tests/js/dashboard_graph_check.mjs` に `marks` を渡せるようにし、`tests/unit/presentation/test_dashboard_graph_marks_rows.py` を新しく作る）：
			  `markRows` の場合分け（T-01）、`opts.marks` の高さ（T-02）、印なしの一致（T-03）、伸びた箱での audit（T-04）、`rowsOf` と node.rows の一致（T-05）。
			  印の幅は、部品の sm の実寸に近い決まった値（例：ほかの印 60px、稼働の印 36px、間 2px）で作る。
			- 画面（`tests/unit/infra/test_dashboard_orca_views_js.py`・`test_dashboard_orca_marks_js.py`、`tests/unit/presentation/test_dashboard_graph_js.py` などの静的な検査と node の偽の DOM）：dnMark・凡例・aria-label、置き場の `"all"`、`is-wrap`、`checkRows` の呼び方（T-06、T-07）。
			- 既存の `test_the_box_size_does_not_change` は SIZE の値を見るので、そのまま通る（SIZE は変えない）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-05", "R-06"]
	}
	"D-07": {
		title: "実機の確かめ（タスク担当）"
		text: """
			開始のコミットと直した後のコミットを `git archive` から wheel にし、別々の隔離した venv と `.workbench/iss-00620/state-*`（この PC の状態の置き場の写し）で、`spec-dock dashboard serve --tailscale` を別のポートで立てる（常駐の 47800・8791 と道具の環境には触れない）。
			エージェントが1人・3人・6人の箱は、実データにいなければ、試しの orca-web の要約を返す小さなサーバー（`/embed/agent-marks.{js,css}` は orca-web のチェックアウトの部品をそのまま配り、`/api/worktrees/summary` は作った要約）を別のポートで立て、試しのダッシュボードの Orca の設定をそこに向ける。
			headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で 1440・390 × 明暗に写し、`specdockEdgeAudit()` の違反0と `markOverflow` 0、ブラウザーのエラー0を report.md に残す。
			iss-00613 の箱（またはエージェントが2人以上の箱）の前後、構造の図で『後に続く』が消え、ボードには残ることも写す。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"]
	}
}

compatibility: """
	構造の API・保存・設定は変えない。構造の図の部品を使う『横断の構造』（iss-00614）にも同じ変更が入る。
	印の入力がない配置は今と同じなので、orca-web をつないでいない利用者の構造の図は、dnMark が消えること以外は変わらない。
	"""

risks: [
	"部品の CSS や字体が遅れて効くと、初めの配置が1行で描かれ、効いた後に1回やり直す（ResizeObserver で拾う）。",
	"MARK_ROW と MARK_INSET は graph.css の値の写し。CSS を変えるときは一緒に直す（コメントで互いを指す）。実機の `markOverflow` で確かめる。",
	"箱が高くなると線の口の数による伸び（grow）と重なって大きくなるが、どちらも高さを足すだけで、検査は伸びた箱で回る。",
]
