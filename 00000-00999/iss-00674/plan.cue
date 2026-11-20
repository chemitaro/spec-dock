package spec

// 計画（Issue）。型 specdock/v1。

goal: "ダッシュボードの5か所で、種類が orca-web の部品の名前で出て、名前を引けないときは今の文字が出る。"

steps: {
	"S-01": {title: "`agents_logic.js` に `agentTypeLabel` を足し、node のテスト（T-01）で確かめる", realizes: ["R-01", "R-02", "F-01"], status: "todo", session: "impl"}
	"S-02": {title: "5か所が `agentTypeLabel` を通し、呼ぶ側が部品を渡す。各所のテスト（T-02）を足す", realizes: ["R-01", "R-02", "F-01"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "`make lint` と全体の `uv run pytest` を通す", realizes: ["R-02"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "orca-web の iss-00066 の後の常駐の orca-web で、実際の Antigravity のエージェントの名前を確かめて report.md に残す（T-03）", realizes: ["R-01"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {
		title: "名前の関数の node のテスト（`tests/unit/infra/test_dashboard_agents_logic_js.py` に足す）"
		verifies: ["R-01", "R-02", "F-01"]
		text: """
			合成の部品で：知る種類（表に `antigravity` のある部品で `antigravity` → 『Antigravity』、`claude` → 『Claude』）、
			知らない種類（表に `antigravity` のない部品で `antigravity` → `antigravity`、`iconKey` が `other` → 生の文字列）、
			種類なし（null・undefined・空の文字列・数 → fallback）、部品なし（null → 生の文字列）、表なし（`AGENT_ICONS` か `iconKey` がない部品 → 生の文字列）、
			`iconKey` が例外を投げる・表にない鍵を返す・`label` が空・`toString` のような継承の鍵 → 生の文字列。純粋さのテストがそのまま通ること。
			"""
	}
	"T-02": {
		title: "5か所が名前を出し、部品なしで今の文字を出すテスト"
		verifies: ["R-01", "R-02", "F-01"]
		text: """
			表に `antigravity` のある合成の部品と null の部品の両方で：`agentFrame` の title（`test_dashboard_agents_logic_js.py`）、
			エージェントのタブの選びの文字（`test_dashboard_agents_tab_js.py` の `world.marks`）、
			`countTitle` の部分の種類（`tests/js/dashboard_graph_unscoped.mjs` か直接の node のテスト）、
			指揮の帯のエージェントの詳細の欄の見出しと worktree の詳細の欄の一覧（`command_view.js` を今のテストの偽の DOM で読む所。実装担当が今のテストから選ぶ）、
			`layersHtml(model, marks)` の数の札の title。部品を渡さない今のテストは変えずに通ること。
			"""
	}
	"T-03": {
		title: "実データでの確かめ（S-04）"
		verifies: ["R-01"]
		text: "常駐の orca-web が iss-00066 を入れた版で立て直された後、ダッシュボードの5か所の見える所（タブの選び、指揮の帯の詳細の欄など）で Antigravity のエージェントが『Antigravity』と出ることを、版（spec-dock のコミット、orca-web のコミット）つきで report.md に残す。"
	}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/infra/test_dashboard_agents_logic_js.py`、S-02 の後は
	`uv run pytest tests/unit/infra/ tests/unit/presentation/ -k "dashboard"`。最後に `make lint`、`uv run pytest`（全体）。
	"""

rollback: "PR を戻す。種類は今どおり生の文字列で出る。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実データの確かめ（T-03）と移行の案内の文がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（変更が小さい画面の JS で、最終品質ゲートでまとめて見る）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 83b8ee95f（report.md に記録）から S-03 の終わりまで。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00674/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		impl:  {task: "実装（S-01〜S-03、画面の JS とテスト、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面の JS は Claude Opus 5.5 / medium（依頼書、方針のフロントエンドの行）"}
		owner: {task: "実データの確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。統括の知らせと、この PC の常駐の orca-web が要る"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high、standard なので2人目なし）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
