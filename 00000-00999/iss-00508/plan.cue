package spec

// 計画（Issue）。型 specdock/v1。

goal: "`worktree remove` が、判定の後にできた無視されたファイルを、`--discard-ignored` なしで消さない。"

steps: {
	"S-01": {title: "unlock の後と、ロックなしの判定の後に無視されたファイルを作るテストを書き、落ちることを確かめる（Red）", realizes: ["R-01", "R-02"], status: "done", session: "impl"}
	"S-02": {title: "`_remove_captured_worktree` に `ignored_allowed` を足し、canonical の `remove_worktree` から渡す（Green）", realizes: ["R-01", "R-02", "R-03", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "リンクだけの worktree の削除（ロックあり・なし）のテストを足し、`test_issue432_branch_followups.py` の差し替え関数をキーワード引数を受け取る形に直し、既存のテストを通す", realizes: ["R-03"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、report.md、PR", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "unlock の後に無視されたファイルを作ると、`--unlock` の削除が unlock succeeded・remove not_attempted・終了コード6で止まり、ファイルが残る", verifies: ["R-01"]}
	"T-02": {title: "ロックなしで、最初の判定の後（`verify_target` の前）に無視されたファイルを作ると、`git worktree remove` を呼ばずに `PRECONDITION_FAILED`・終了コード3・effects 空で止まり、ファイルが残る", verifies: ["R-02"]}
	"T-03": {title: "リンクだけの worktree は、ロックあり（`--unlock`）とロックなしの両方で `--discard-ignored` なしに消え、カタログは変わらない", verifies: ["R-03"]}
	"T-04": {title: "既存の `test_issue440_g3_worktree_remove.py`（bare の main の終了コード5を含む）、`test_issue432_branch_followups.py` の `PRECONDITION_FAILED` の固定、`uv run pytest` の全体が通る", verifies: ["R-03", "F-01"]}
}

verification: "`uv run pytest tests/cli_runtime/test_issue440_g3_worktree_remove.py`、`make lint`、`uv run pytest`（全体）。"
rollback:     "PR を閉じるか、マージ後なら `git revert` する。データの形は変えない。"
exit:         "T-01〜T-04 が通り、PR がマージできる状態で、CI が通る。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "medium", rationale: "3 policy §4 standard の実装（epic-00512 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-03", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "high"}
	}
}
