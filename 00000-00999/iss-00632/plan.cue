package spec

// 計画（Issue）。型 specdock/v1。

goal: "横断の構造の同じ種類の知らせを上に1回だけまとめ、縮めた枠の測り直しを実機で確かめる"

steps: {
	"S-01": {title: "T-01・T-02 を tests/js/dashboard_allgraph_notices.mjs と tests/unit/presentation/test_dashboard_allgraph_notices.py に先に書いて落ちることを確かめ、D-01（logic.js の kind・detail）と D-02（views/allgraph/notices.js）を入れて通す", realizes: ["R-01", "R-02", "R-05", "F-01"], status: "done", session: "impl-sol"}
	"S-02": {title: "T-03・T-04 を tests/unit/presentation/test_dashboard_allgraph_screen.py（と tests/js/dashboard_allgraph_screen.mjs）に先に書いて落ちることを確かめ、D-03（allgraph.js・allgraph.css）を入れて通す。既存の知らせの検査を新しい置き場に直す", realizes: ["R-01", "R-02", "R-03", "F-01"], status: "done", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に dashboard の資産があれば sha256 を直す）", realizes: ["R-01", "R-02", "R-03", "R-05"], status: "done", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-04 の実機の確かめ（R-04 の18組、まとめの行、写し）を report.md に残し、試しの URL を立てる", realizes: ["R-03", "R-04"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "overviewWarnings の各種類に D-01 の kind と detail が付き、level と text は今のまま（tests/unit/infra/test_dashboard_screens_js.py の既存の検査も通る）", verifies: ["R-05"]}
	"T-02": {title: "splitNotices（純粋）：種類ごとに1行、名前は一覧の順、detail、同じ name のときだけ owner/name、行の順（error→warning→info、同じ level は SHARED の順）、next が1回、failure と ambiguous は own に残る、warnings が null のリポジトリは数えない、failed のリポジトリは知らせのすべてが own に残りまとめに出ない、知らせがなければ summary が空", verifies: ["R-01", "R-02", "F-01"]}
	"T-03": {title: "画面の node の検査：2つが古く1つが PR 不明のとき .ax-sum が2行で、どの枠の .ax-warn にもその知らせがない。読めなかった枠は理由の1行だけ（枠の高さが1行分）。『これから』で Scope がなく古いだけの枠は出ず、名前はまとめの行にある。Scope が0件でスナップショットが読めない failed の枠には読めない理由の行が残り、まとめの行に名前がない。知らせがなければ .ax-sum は hidden", verifies: ["R-01", "R-02", "F-01"]}
	"T-04": {title: "画面の node の検査（styled）：まとめの行があるとき、最初の表示の ty がまとめの行の下端 + 8 以上（barBottom が .ax-sum を含む）。静的な検査で .ax-sum の pointer-events: none と li の auto・fit-content", verifies: ["R-03"]}
	"T-05": {title: "実機：R-04 の18組の edgeAudit の total の違反0、縮めた枠のはみ出し0、まとめの行の写し（1440・390 × 明暗）", verifies: ["R-03", "R-04"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_allgraph_notices.py tests/unit/infra/test_dashboard_screens_js.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/test_dashboard_allgraph_notices.py tests/unit/presentation/test_dashboard_allgraph_screen.py tests/unit/presentation/test_dashboard_allgraph_compose.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/presentation/test_dashboard_graph_fit.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-04。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の表と写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当がテストの合格を確かめてから S-02 に進む。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 3f5f8d8e9 から S-03 の終わりまで（S-04 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "compatibility-regression"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00632/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、知らせの種類と振り分けの純粋な部品と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない純粋な計算で node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、画面の DOM・CSS と全体の検証）", model: "opus", effort: "medium", rationale: "画面は Claude Opus 5.5 / medium（依頼書）。タスク担当のこのセッションが同じ値なので、別のセッションを起こさずに行う"}
		owner:         {task: "実機の確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機が要る"}
	}
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
