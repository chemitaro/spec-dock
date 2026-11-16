package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "native lock のテストの揺れを、テストの隔離で直す"

steps: {
	"S-01": {title: "D-02 の回帰テストを足し、直す前のコードで落ちることを確かめる（Red）", realizes: ["R-01"], status: "todo", session: "impl-sol"}
	"S-02": {title: "D-01 の環境の設定を足し、`tests/integration/test_issue413_native_lock.py` をすべて通す（Green）", realizes: ["R-01", "R-02", "F-01"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "そのファイルを単独で50回、`make lint`、全体の `uv run pytest` を2回走らせ、結果を返す", realizes: ["R-02"], status: "todo", after: ["S-02"], session: "impl-sol"}
}

tests: {
	"T-01": {title: "`_environment()` の環境で `maintenance.auto` が false、`gc.auto` が 0、commit が `maintenance run` を起こさない", verifies: ["R-01", "F-01"]}
	"T-02": {title: "単独で50回続けて通り、全体の pytest が2回とも失敗0", verifies: ["R-02"]}
}

verification: """
	節目：`uv run pytest tests/integration/test_issue413_native_lock.py`。
	揺れ：`for i in $(seq 1 50); do uv run pytest -q tests/integration/test_issue413_native_lock.py || echo FAIL $i; done`。
	最後に `make lint`、`uv run pytest`（全体）を2回。
	"""

rollback: "PR を戻す（テストファイル1つだけ）"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に50回と全体2回の結果がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": "なし（変更はテストファイル1つで、最終品質ゲートで足りる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 7f7dd2b1d から S-03 の終わりまで。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00624/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が依頼書で選んだ（タスク担当 × standard）"}
		"impl-sol": {task: "実装（S-01〜S-03）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。テストだけの直しで、テストで確かめられる（依頼書が Sol を指定）。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
