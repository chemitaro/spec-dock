package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の線が箱・枠の見出しや別の線に重ならない（配置の見込みと実寸の一致、router の寄せの直し）"

steps: {
	"S-01": {title: "D-06 の回帰の入力を tests/fixtures/issue627/ に作る（題名を伏せる）。直す前の router で、その入力の違反が0でないことを node で確かめる", realizes: ["R-03"], status: "done", session: "owner"}
	"S-02": {title: "T-01・T-02 を tests/unit/presentation/test_dashboard_graph_route_fix.py（と tests/js の検査の口）に先に書いて落ちることを確かめ、router.js に D-04・D-05 を入れて通す。既存の構造の図のテストを通す", realizes: ["R-03", "R-05"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "T-03〜T-05 を tests/unit/presentation/test_dashboard_graph_fit.py（と tests/js の検査の口）に先に書いて落ちることを確かめ、D-01（graph.css）・D-02（layout.js の heads と compactHeight）・D-03（measure.js、graph.js と allgraph.js の測り直し）を入れて通す", realizes: ["R-01", "R-02", "F-01", "F-02"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に dashboard の資産はないので、変われば直す）", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-03"], session: "impl-claude"}
	"S-05": {title: "D-07 の実機の確かめ（R-04 の表、R-01 の見出しの差、R-02 のはみ出し、直す前と後の写し）と R-05 の 240 組の比べを report.md に残し、試しの URL を立てる", realizes: ["R-01", "R-02", "R-04", "R-05"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "tests/fixtures/issue627/ の6つの入力で、routeLayout の audit の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・failed）が0", verifies: ["R-03"]}
	"T-02": {title: "route(G) に直接渡す小さな入力：入口の辺のすぐ左で向かい合う箱が同じ高さに出口を持つとき、その線だけの入口が向かいの出口と S − 0.5 未満にならず、audit の違反0。向かいがないときは今どおり入口を出口の高さにそろえる", verifies: ["R-03"]}
	"T-03": {title: "layout の heads：縮めた Epic・Initiative に base より高い heads を渡すと高さが heads + grow になり node に fit がある、base 以下や渡さないときは今の JSON と同じ、縮めていない枠と箱は heads で変わらない。compactHeight の値（Epic 67、Initiative 78、エージェントの行1つで +20）", verifies: ["R-02"]}
	"T-04": {title: "measure.js の headsDiffer（純粋）：fit のない node と heads なし・base 以下で false、base より高い needs で true、fit と同じ needs で false、行の数で base が変わる", verifies: ["R-02", "F-02"]}
	"T-05": {title: "静的な検査：graph.css の D-01 の規則、graph.js と allgraph.js の checkRows が compactNeeds と headsDiffer を使い rowsRedo の2回の歯止めを共有し、routeLayout に heads を渡す。compactNeeds は隠れた図・未適用の CSS で null（F-01）", verifies: ["R-01", "R-02", "F-01", "F-02"]}
	"T-06": {title: "実機：R-04 の組の edgeAudit の違反0、R-01 の見出しの差 0.5px 以内、R-02 のはみ出し0、日本語の題名が切れない（1440・390 × 明暗の写し）", verifies: ["R-01", "R-02", "R-04"]}
	"T-07": {title: "240 組の node の比べ（直す前と後）で違反の増えた組0", verifies: ["R-05"]}
}

verification: """
	節目：S-02 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_route_fix.py tests/unit/presentation/test_dashboard_graph_js.py`、S-03 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_route_fix.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_fit.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/presentation/test_dashboard_allgraph_screen.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-07、比べは `.workbench/iss-00627/tools/sweep.mjs`。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の表と写し、240 組の比べ、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-02 の後は、タスク担当がテストの合格と 240 組の比べを確かめてから S-03 に進む。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 5c0ebb916 から S-04 の終わりまで（S-05 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "ui-behavior"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00627/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-02、router.js とその node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。寄せと入口の高さは DOM のない純粋な計算で node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-03〜S-04、CSS・layout の heads・測り直し）", model: "opus", effort: "medium", rationale: "画面は Claude Opus 5.5 / medium（依頼書）。タスク担当のこのセッションが同じ値なので、別のセッションを起こさずに行う"}
		owner:         {task: "回帰の入力（S-01）、実機の写しと比べ（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機が要る"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
