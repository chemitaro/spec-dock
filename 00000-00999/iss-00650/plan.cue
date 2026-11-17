package spec

// 計画（Issue）。型 specdock/v1。

goal: "帯の欄のチャットの枠を、欄の本文の高さいっぱいに広げ、狭い画面の下からの欄（帯の欄、片付けの候補の欄）を Scope の欄と同じく指で動かせるようにする"

steps: {
	"S-01": {title: "T-01 を先に足して落ちるのを確かめ、D-01（command_view.js の本文の属性）を入れて通す。make lint と全体の uv run pytest を通す（static-inventory.json に載る sha256 が変われば直す）", realizes: ["R-01", "R-02", "F-01"], status: "done", session: "owner"}
	"S-03": {title: "T-03 を先に足して落ちるのを確かめ、D-03（panel.js の下からの欄の判定、SHEET_GRAB、hide の applySnap、graph.js・allgraph.js の closePanel、command_view.js と片付けの候補のつまみ）を入れて通す。make lint と全体の uv run pytest を通す", realizes: ["R-03", "F-02", "R-02"], status: "done", after: ["S-01"], session: "owner"}
	"S-02": {title: "T-02 と T-04 の実機の確かめ（直す前と後の写しと数）を report.md に残し、本人が見る試しの URL を立てたままにする", realizes: ["R-01", "R-02", "R-03"], status: "done", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "偽の DOM：構造の図と『横断の構造』で帯の印を押すと、欄の本文の data-tab が agents（iframe あり）、チャットを開けないとき data-tab なし。今の指揮の画面のテスト（同じ iframe を保つ）が通る", verifies: ["R-01", "R-02", "F-01"]}
	"T-03": {title: "偽の DOM（幅 390）：構造の図の帯の欄・片付けの候補の欄・Scope の欄で、開いたとき data-snap が half、つまみのタップで full → half、見出しを上へ引いて full、下へ引いて閉じる（帯の欄は data-cmd-agent・強調・aria-pressed が閉じるボタンと同じに解ける）。本文の上で引いても動かない、PC の幅（1440）では動かない。『横断の構造』の帯の欄を下へ引いて閉じる。今の Scope の欄のテストが通る", verifies: ["R-03", "F-02", "R-02"]}
	"T-04": {title: "実機：390×844 の Chrome で、CDP の Input.dispatchTouchEvent で、帯の欄・片付けの候補の欄・Scope の欄を、上へ引いて全面、下へ引いて閉じる、つまみのタップで切り替え（直す前と後の data-snap・欄の高さ・開閉）", verifies: ["R-03"]}
	"T-02": {title: "実機：1440×900 と 390×844（明）で、帯の印を押したときの iframe の高さと本文の高さ（直す前と後）、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps 0、ブラウザーのエラー0", verifies: ["R-01", "R-02"]}
}

verification: "S-01・S-03 の後に `uv run pytest tests/unit/presentation/test_dashboard_graph_command_screen.py tests/unit/presentation/test_dashboard_allgraph_command_screen.py tests/unit/infra/test_dashboard_agents_tab_js.py tests/unit/infra/test_dashboard_scope_tabs_js.py tests/unit/infra/test_dashboard_orca_views_js.py`、最後に `make lint`、`uv run pytest`（全体）。実機は T-02・T-04。"
rollback:     "PR を戻す（dashboard の panel.js・command_view.js・graph.js・allgraph.js とテスト）。"
exit:         "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の数と試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {"CP-1": "なし（変更が1行で、レビューは最終品質ゲートでまとめる）"}
	final_quality_gate: {
		scope:          "開始のコミット 92e26aff7 から S-03 の終わりまで（S-02 は記録）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す。範囲の追加の前のキャンペーン iss-00650（f7655ea8c、合格前に範囲が変わった）は使わず、新しいキャンペーンで行う"
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
		owner: {task: "実装と実機（S-01・S-03・S-02）", model: "opus", effort: "medium", rationale: "同じセッションの例外：light で実装の手順が2つ（S-01・S-03。S-02 は実機の確かめ）、変更は画面の JS の小さな判定の直し（依頼書が許す例外）。値は依頼書が画面のコードに指定する Claude Opus 5.5 / medium と同じ"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", model: "opus", effort: "medium"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
