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
	"D-02": {
		title: "確かめ方（seam）"
		text: """
			- 偽の DOM：`tests/js/dashboard_graph_command_screen.mjs` と `tests/js/dashboard_allgraph_command_screen.mjs` の写しに、本文の `data-tab` を足し、帯を押したあとで `agents`、開けないときに null を確かめる（今のテストの件に足す）。
			- 静的：panel.css の PC と狭い画面の規則が `[data-tab="agents"]` を含むこと（今の test_dashboard_agents_tab_js.py が見ている）。
			- 実機：隔離した venv で立てた構造の図で、1440×900 と 390×844 の iframe と本文の高さを測る（直す前と後）。
			"""
		satisfies: ["R-01", "R-02"]
	}
}

risks: ["Scope の欄から帯の欄、帯の欄から Scope の欄へ行き来したときに属性が残る：panel.js が本文の dataset.tab を描くたびに上書きし、帯の欄は innerHTML を作り直すので残らない"]
