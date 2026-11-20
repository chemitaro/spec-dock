package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"種類の名前を引く決まりを、1つの純粋な関数に閉じる",
	"今の関数の呼び方と表示を、部品を渡さないときはそのまま保つ",
]

current: """
	5か所が、それぞれ `agentType`（なければ既定の文字）を、そのまま文字にしている（requirement の background）。
	`agentFrame(origin, agent, theme)` と `countTitle(item)` は純粋な関数で、部品を受け取らない。
	`countTitle` は `command_view.js` の `itemHtml(it)` から、`itemHtml` は `layersHtml(model)` から、`layersHtml` は `views/graph.js` と `views/allgraph.js` の `drawCommand` から呼ばれる。
	"""

target: """
	`views/_shared/agents_logic.js` に足す `agentTypeLabel` を5か所が通し、部品は呼ぶ側（`orca.marks()` を持つ所）から引数で渡す。
	"""

design: {
	"D-01": {
		title: "名前の関数 `agentTypeLabel(marks, agentType, fallback)`"
		text: """
			`src/spec_dock/assets/dashboard/views/_shared/agents_logic.js`（import のない純粋な部品。`test_the_logic_module_is_pure` が守る）に、関数を1つ足して書き出す。
			新しいファイルにしないのは、`agentFrame` が同じファイルの中でこれを呼べ、純粋さのテストの決まり（import なし）を変えずに済むため。
			1. `raw` を、`agentType` が空でない文字列ならそれ、そうでなければ `fallback` とする。
			2. `agentType` が空でない文字列で、`marks` がオブジェクトで、`marks.iconKey` が関数で、`marks.AGENT_ICONS` がオブジェクトのとき、
			   `key = marks.iconKey(agentType)` を求める。`key` が文字列で、`other`・`none` でなく、`AGENT_ICONS` の自分の項目（`Object.prototype.hasOwnProperty`）で、
			   その項目の `label` が空でない文字列なら、`label` を返す。
			3. それ以外（部品が null、書き出しがない、`iconKey` が例外を投げる、を含む）は `raw` を返す。例外は関数の中で受け止め、外へ出さない。
			HTML のエスケープはしない（呼ぶ側が今どおり `esc` する）。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
	"D-02": {
		title: "5か所が関数を通す"
		text: """
			- `agents_tab.js` の `stripHtml`：`agentTypeLabel(env.ctx.orca?.marks?.() ?? null, agent.agentType, "種類不明")`。
			- `agents_logic.js` の `agentFrame(origin, agent, theme, marks = null)`：title の種類を `agentTypeLabel(marks, agent.agentType, "種類不明")` にする。
			  呼ぶ側の `agents_tab.js`（`ctx.orca?.marks?.()`）と `command_view.js` の `renderAgentPanel`（`orca?.marks?.()`）が部品を渡す。
			- `command_view.js` の `renderAgentPanel` の見出しと `renderWorktreePanel` のエージェントの一覧：`agentTypeLabel(orca?.marks?.() ?? null, agentType, "種類不明")`。
			- `unscoped.js` の `countTitle(item, marks = null)`：各部分の種類を `agentTypeLabel(marks, p.agentType, "agent")` にする。
			  `command_view.js` の `itemHtml(it, marks)` と `layersHtml(model, marks = null)` が部品を受け渡し、`views/graph.js`・`views/allgraph.js` の `drawCommand` が `ctx.orca?.marks?.() ?? null` を渡す。
			`agents_tab.js`・`command_view.js` は今の `agents_logic.js` の import に `agentTypeLabel` を足し、`unscoped.js` は `../_shared/agents_logic.js` から import する。
			`agents_logic.js` は import なしのまま（純粋さのテストの決まりを変えない）。
			部品は要約より先に入るので、エージェントが出る最初の描画から名前が引ける。部品が後から変わる場合の描き直しは足さない（今のキャッシュの決まりのまま）。
			"""
		satisfies: ["R-01", "R-02", "F-01"]
	}
}

compatibility: """
	新しい引数はすべて省けて、省けば今の表示。今の orca-web（表に `claude`・`codex` だけ）では Claude・Codex の名前が『Claude』『Codex』になり、ほかは今どおり生の文字列。
	部品の書き出しを読まない古い SpecDock と、新しい orca-web の組み合わせは、今どおり生の文字列。
	"""

risks: [
	"`claude` の表示が『claude』から『Claude』に、`claude-agent-teams` が『Claude』に変わる。部品の表の名前に合わせる意図どおりの変化で、テストが生の文字列を期待していれば、そのテストは R-01 に合わせて直す（変えたテストは report.md に書く）",
]
