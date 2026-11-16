package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の「これから」で、見える子孫のない親を出さない（layout.js の visibility とテスト、実データの写し）"

steps: {
	"S-01": {title: "test_dashboard_graph_range.py に D-02 の合成の構造 `_parents()` と、これから・全体・いま・focus・audit のテストを足し、test_dashboard_graph_toolbar.py に D-03 の知らせのテストを足して、直す前のコードで R-01 のテスト、R-04 の focus 80、D-03 の知らせが落ち、R-02・R-03・R-05・F-02 と focus 70・95 のテストが通ることを確かめる（Red）", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "F-01"], status: "done", session: "impl-sol"}
	"S-02": {title: "layout.js の visibility の next の分岐を D-01 にし、構造の図のテスト（graph_js・graph_range・graph_toolbar）をすべて通す。iss-00603 の digest と `_next()` の期待は変えない（Green）", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "F-01", "F-02"], status: "done", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "make lint と全体の pytest を通す", realizes: ["R-05", "R-06"], status: "done", after: ["S-02"], session: "impl-sol"}
	"S-04": {title: "orca-web・spec-dock・housing-lifecycle の実データで、これからの直す前と後を 1440・390、明暗で写し、edgeAudit の違反0、ブラウザーのエラー0、orca-web の init-00002 が前は出て後は出ないことを report.md に残し、tailnet の試しの URL を立てる（D-04）", realizes: ["R-06"], status: "done", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "`_parents()` のこれから（入れ子・木）：70・71・73（init-00002 の形）、80・81・82（3段）、110・111（子を持つ Issue）が出ない", verifies: ["R-01"]}
	"T-02": {title: "`_parents()` のこれから：子のない開いた Initiative 90 と Epic 91 が出る", verifies: ["R-02"]}
	"T-03": {title: "`_parents()` のこれから：95 が枠（入れ子 frame、木 tframe）、98 が出て、96 が出ない。今の `_next()` の `SHOWN` のテストがそのまま通る", verifies: ["R-03"]}
	"T-04": {title: "`_parents()` のこれからの focus：70 で {70}、80 で {80}、95 で {95, 98}（入れ子・木）", verifies: ["R-04"]}
	"T-05": {title: "今の digest の比較（test_all_and_now_lay_out_as_the_two_old_combinations）がそのまま通り、`_parents()` の全体で 70・71・73・80・81・82・110・111 が nodes に、いまで 70・80・81・110・111 が nodes に、71・73・82 が入れ子では groups、木では nodes に出る", verifies: ["R-05"]}
	"T-06": {title: "`_parents()` の next（入れ子・木、focus）を含む組み合わせで edgeAudit の違反0。モデルの片付けの候補がちょうど 71・73・82・96 で、70・80・81・95・110・111 が候補でないこと（前提）", verifies: ["R-06"]}
	"T-09": {title: "親の循環と無い親の参照を持つ小さな構造で、これから（入れ子・木）の layout が例外なく返る", verifies: ["F-02"]}
	"T-07": {title: "開いた Initiative と候補 a の Epic だけの構造をこれからで描くと、知らせの文が出て、道具の帯と札の帯が残る（test_dashboard_graph_toolbar.py の仕組み）", verifies: ["F-01"]}
	"T-08": {title: "実データ（orca-web、spec-dock、housing-lifecycle）のこれからの直す前と後 × 1440・390 × 明暗の写し、edgeAudit の違反0、ブラウザーのエラー0、orca-web の init-00002 の前後が report.md にある", verifies: ["R-06"]}
}

verification: """
	節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py`。最後に `make lint`、`uv run pytest`（全体）。
	実データ：D-04 のとおり、隔離した venv と `.workbench/iss-00611/state` で別のポートに立てる。常駐のダッシュボード（47800）と道具の環境には触れない。
	"""

rollback: "PR を戻す（layout.js とテストだけ）。保存・API・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実データの前後の写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": "なし（変更は layout.js の1つの分岐とテストだけで、S-02 の後の最終品質ゲートで足りる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 2c7427a97 から S-03 の終わりまで（S-04 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00611/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01〜S-03）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。layout.js の見せる判定は DOM のない純粋な計算で node のテストで確かめられる（方針の「テストで確かめられる実装」× standard）。本人の指示で Sol を使う。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		owner:      {task: "実データの写しと試しの URL（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
