package spec

// 計画（Issue）。型 specdock/v1。

goal: "木の表示の『全体』の線の違反を0にし、入れ子の表示の結果を変えない（router.js の木の詰め直しと、layout.js の落ち着きの判定）"

steps: {
	"S-01": {title: "T-01〜T-03 を tests/unit/presentation/test_dashboard_graph_tree_route.py（と tests/js/dashboard_graph_route_fix.mjs の mode・marks・problems・maxWiden）に先に書いて落ちることを確かめ、router.js に D-01、layout.js に D-02 を入れて通す。既存の構造の図のテストを通す", realizes: ["R-01", "R-02", "R-03", "F-01", "F-02"], status: "todo", session: "impl-sol"}
	"S-02": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に dashboard の資産はないので、変われば直す）", realizes: ["R-04"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "D-04 の比べ（240 組と固定した入力の 60 組、稼働の印あり）と実機の確かめ（taikyohiyou の木の『全体』の edgeAudit と前後の写し）を report.md に残し、試しの URL を立てる", realizes: ["R-03", "R-04", "R-05"], status: "todo", after: ["S-02"], session: "owner"}
}

tests: {
	"T-01": {title: "固定した入力の product・business の木の『全体』（稼働の印なし）で、routeLayout の audit の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・failed）が0で、返す problems が audit の違反の数と一致", verifies: ["R-02", "R-03"]}
	"T-02": {title: "route(G) に直接渡す木の小さな入力（親の線、40 個の箱の列、箱 i → i + 5、通り道 120px）で、overlaps 0、広げの要求の最大が S 以下", verifies: ["R-01"]}
	"T-03": {title: "静的な検査：router.js の packFree の呼び出しが !G.nested の条件の中、layout.js の settled が problems を含む", verifies: ["R-01", "R-02"]}
	"T-04": {title: "比べ：240 組と固定した入力の 60 組で違反の増えた組0、入れ子の組の経路が同じ。木の 30 組と固定した入力の木（稼働の印あり）で違反0", verifies: ["R-03", "R-04"]}
	"T-05": {title: "実機：taikyohiyou_project の木の『全体』1440 の明暗で edgeAudit の違反0、前後の写し", verifies: ["R-03", "R-05"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_tree_route.py tests/unit/presentation/test_dashboard_graph_route_fix.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_fit.py`。
	最後に `make lint`、`uv run pytest`（全体）。比べは `.workbench/iss-00633/tools/sweep.py`、実機は D-04。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に原因、比べ、実機の表と前後の写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当がテストの合格と比べを確かめてから S-02 に進む。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 3f5f8d8e9 から S-02 の終わりまで（S-03 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "compatibility-regression"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00633/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01〜S-02、router.js・layout.js とその node のテスト、lint と全体のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。寄せと落ち着きの判定は DOM のない純粋な計算で、node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		owner:      {task: "比べ、実機の確かめと写し（S-03）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機が要る"}
	}
	reviews: {
		spec: {role: "仕様のレビュー（S-01 の前）", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-02", model: "opus", effort: "medium"}
	}
}
