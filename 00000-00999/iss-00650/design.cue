package spec

// 設計（Issue）。型 specdock/v1。

current: "`renderAgentPanel`（views/graph/command_view.js）が `<div class=\"pn-body\">` に iframe を置く。`.sd-pn .pn-body` は block で、`.sd-pn .sd-agent { flex: 1; min-height: 240px; height: auto }` の flex が効かず、iframe は既定の高さになる。"
target:  "枠を出すとき `<div class=\"pn-body\" data-tab=\"agents\">` にする。panel.css の既存の規則（PC：`display: flex; flex-direction: column; gap: 4px; padding: 4px 10px 10px`、狭い画面：`padding: 2px 4px 4px`）と scope_tabs.css の `.sd-agent` の縁・角丸がそのまま効く。"

design: {
	"D-01": {
		title: "帯の欄の本文の属性"
		text: """
			`renderAgentPanel` の本文の開きタグを、`frame` があるとき `<div class="pn-body" data-tab="agents">`、ないとき今の `<div class="pn-body">` にする。CSS は変えない。
			`data-tab` を読む JS は panel.js（Scope の欄を描くとき自分で上書きする）と scope.js（詳しい画面）だけで、帯の欄の本文を読むものはない（タスク担当が grep で確かめた）。Scope の欄に戻るときは panel.js が本文を作り直すので、属性は残らない。
			構造の図（graph.js）と『横断の構造』（allgraph.js）は同じ関数を呼ぶので、1か所で両方が直る。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-03": {
		title: "下からの欄の動きを、欄の中身によらず panel.js で働かせる"
		text: """
			`createScopePanel`（views/_shared/panel.js）の下からの欄の動きの判定を、`current`（Scope の欄の中身）から「aside が開いている（`.is-open`）」に変える。動きの処理は panel.js のこの1か所のまま。
			1. pointerdown：`!current` を `!aside.classList.contains("is-open")` にする。引っぱりの取っ手は、つまみ `.pn-grab` と、見出しの帯 `.pn-top`（Scope の欄）か `.pn-head`（ほかの描き手の見出し）。ボタンとリンクの上では始めない（今と同じ）。
			2. click：つまみ `.pn-grab` のタップ（半分と全面の切り替え）を、「ほかの描き手が aside を持っている」の早い返りより前に置き、aside が開いていれば中身によらず働かせる。ほかの click の扱いは今のまま（ほかの描き手のときは返る）。
			3. resize：`if (current) applySnap()` を、aside が開いていれば `applySnap()` にする。
			4. `hide()`：`snap = "half"` のあとに `applySnap()` を呼ぶ。ほかの描き手は `hide()` のあとに aside を差し替えるので、開いたときの高さが半分になる（今は前の Scope の欄の高さが残る）。Scope の欄では、次の `show()` の `draw()` がまた `applySnap()` を呼ぶので変わらない。
			5. 引いて閉じたとき（`settleSheet` が closed）は、今どおり `onClose()` を呼ぶ。画面（graph.js・allgraph.js）は、閉じるボタン（`data-act="close"`）と同じ処理を1つの関数 `closePanel()`（帯の欄なら `closeAgentPanel()`、片付けの候補なら `cleanup = false` と `renderPanel()`、それ以外は `select(null)`）にまとめ、`onClose` と閉じるボタンの両方からそれを呼ぶ。Scope の欄の閉じる（`data-pn-act="close"`）も `onClose` なので、結果は今と同じ `select(null)`。
			6. つまみの HTML：panel.js が `SHEET_GRAB`（`<button type="button" class="pn-grab" aria-label="欄の高さを変える"></button>`、Scope の欄と同じ）を export し、帯の欄（command_view.js）と片付けの候補の欄（graph.js・allgraph.js）の `<div class="pn-grab"></div>` をそれに替える。Scope の欄の `build()` も同じ定数を使う。CSS は今の `.sd-pn .pn-grab` がそのまま効く（PC では出ない）。
			7. CSS は変えない。`.pn-head` には `touch-action` の規則がないが、pointer の動きは panel.js が見るので、見出しを引いて動かせる（実機で確かめる）。足りなければ、`.sd-pn .pn-top` の `touch-action: none` の規則の範囲に `.sd-pn > .pn-head` を足す（共有の規則の範囲を広げるだけで、帯の欄だけの CSS ではない）。
			"""
		satisfies: ["R-03", "F-02"]
	}
	"D-02": {
		title: "確かめ方（seam）"
		text: """
			- 偽の DOM：`tests/js/dashboard_graph_command_screen.mjs` と `tests/js/dashboard_allgraph_command_screen.mjs` の写しに、本文の `data-tab` を足し、帯を押したあとで `agents`、開けないときに null を確かめる（今のテストの件に足す）。
			- 静的：panel.css の PC と狭い画面の規則が `[data-tab="agents"]` を含むこと（今の test_dashboard_agents_tab_js.py が見ている）。
			- 実機：隔離した venv で立てた構造の図で、1440×900 と 390×844 の iframe と本文の高さを測る（直す前と後）。
			- 下からの欄（D-03）：`tests/js/dashboard_graph_command_screen.mjs` に、幅と高さを走りごとに変える口（`width`・`height`）、aside の矩形の高さを `--pn-h` から返す `hooks.rect`、欄の上での引っぱり（`{sheet: {on, dy}}`：pointerdown → pointermove → pointerup）とつまみのタップ（`{grab: true}`）の手順、写しに `snap`（data-snap）と `pnH`（--pn-h）を足す。幅 390 で、帯の欄・片付けの候補の欄・Scope の欄の3つで、つまみのタップ、上へ引く、下へ引いて閉じるを確かめる。『横断の構造』は帯の欄を下へ引いて閉じる1件。
			- 実機（D-03）：390×844 の Chrome で、CDP の `Input.dispatchTouchEvent` でつまみと見出しを引き、`data-snap` と欄の高さと開閉を、直す前と後、3つの欄で測る。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-02"]
	}
}

risks: ["Scope の欄から帯の欄、帯の欄から Scope の欄へ行き来したときに属性が残る：panel.js が本文の dataset.tab を描くたびに上書きし、帯の欄は innerHTML を作り直すので残らない", "hide() で applySnap() を呼ぶと、閉じた Scope の欄の --pn-h も半分になる：閉じた欄は画面の外にあり、次に開くときは半分から始まる（今の hide() の snap = half と同じ意味）"]
