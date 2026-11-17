package spec

// 計画（Issue）。型 specdock/v1。

goal: "帯の欄のチャットの枠を、欄の本文の高さいっぱいに広げる"

steps: {
	"S-01": {title: "T-01 を先に足して落ちるのを確かめ、D-01（command_view.js の本文の属性）を入れて通す。make lint と全体の uv run pytest を通す（static-inventory.json に載る sha256 が変われば直す）", realizes: ["R-01", "R-02", "F-01"], status: "todo", session: "owner"}
	"S-02": {title: "T-02 の実機の確かめ（直す前と後の写しと数）を report.md に残し、本人が見る試しの URL を立てたままにする", realizes: ["R-01", "R-02"], status: "todo", after: ["S-01"], session: "owner"}
}

tests: {
	"T-01": {title: "偽の DOM：構造の図と『横断の構造』で帯の印を押すと、欄の本文の data-tab が agents（iframe あり）、チャットを開けないとき data-tab なし。今の指揮の画面のテスト（同じ iframe を保つ）が通る", verifies: ["R-01", "R-02", "F-01"]}
	"T-02": {title: "実機：1440×900 と 390×844（明）で、帯の印を押したときの iframe の高さと本文の高さ（直す前と後）、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps 0、ブラウザーのエラー0", verifies: ["R-01", "R-02"]}
}

verification: "S-01 の後に `uv run pytest tests/unit/presentation/test_dashboard_graph_command_screen.py tests/unit/presentation/test_dashboard_allgraph_command_screen.py tests/unit/infra/test_dashboard_agents_tab_js.py`、最後に `make lint`、`uv run pytest`（全体）。実機は T-02。"
rollback:     "PR を戻す（command_view.js の1行とテスト）。"
exit:         "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の数と試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {"CP-1": "なし（変更が1行で、レビューは最終品質ゲートでまとめる）"}
	final_quality_gate: {
		scope:          "開始のコミット 92e26aff7 から S-01 の終わりまで。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00650/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が依頼書で Opus 5.5 / medium を選んだ"}
		owner: {task: "実装と実機（S-01〜S-02）", model: "opus", effort: "medium", rationale: "同じセッションの例外：light で手順が2つ以下、変更は画面の JS の1行（依頼書が許す例外）。値は依頼書が画面のコードに指定する Claude Opus 5.5 / medium と同じ"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", model: "opus", effort: "medium"}
		gate: {role: "最終品質ゲート", after: "S-01", model: "opus", effort: "medium"}
	}
}
