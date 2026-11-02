package spec

// 計画（Issue）。型 specdock/v1。

goal: "`scope close`／`reopen`／`create` が、確認の後に変わった選択と `origin` で GitHub に書かない。"

steps: {
	"S-01": {title: "確認の間に選択を変える close／reopen のテストと、origin を変える create のテスト（確認の間、POST の後）を書き、落ちることを確かめる（Red）", realizes: ["R-01", "R-02"], status: "done", session: "impl"}
	"S-02": {title: "`selection_unchanged` と `lifecycle_scope` の読み直しを足す（Green）", realizes: ["R-01", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "`WriteSession.require_same_repository` と `RepositoryChanged` を足し、`create_scope` の確認の後・POST の前・POST の後に呼ぶ（Green）", realizes: ["R-02", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、report.md、PR", realizes: ["R-01", "R-02"], status: "doing", after: ["S-02", "S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "close（open から）と reopen（completed から）で、`--expect-current` の有無の両方について、確認の入力の間に選択を別の Scope に変えると、`PRECONDITION_FAILED`・終了コード3・effects 空で止まり、PATCH がなく、新しい選択の記録が変わらない", verifies: ["R-01", "F-01"]}
	"T-02": {title: "確認の入力の間に選択が変わらなければ、今までどおり PATCH する（既存の `test_scope_close_accepts_a_terminal_confirmation_after_planning`）", verifies: ["R-01"]}
	"T-03": {title: "create の確認の入力の間に `git remote set-url origin` で別のリポジトリにすると、`PRECONDITION_FAILED`・終了コード3で止まり、GitHub への書き込みがなく、カタログが変わらない", verifies: ["R-02", "F-01"]}
	"T-04": {title: "`--yes` の create で、POST の間に origin を別のリポジトリにすると、partial・終了コード6・`SCOPE_PUBLICATION_INCOMPLETE`、effects が `github-create succeeded` と `scaffold not_attempted`、`github_ref` が確認したリポジトリの ref、POST は1回、カタログにディレクトリも changeset もなく、recovery の先頭が origin を戻す案内になる", verifies: ["R-02", "F-01"]}
	"T-05": {title: "親のある create で、POST の後に origin が変わると、`github.sub-issue.add` を試みず `not_attempted` になる", verifies: ["R-02"]}
	"T-07": {title: "`--yes` の create で、種類のラベルを作った後・POST の前に origin を変えると、`CANONICAL_WRITE_INCOMPLETE`・partial・終了コード6、effects が `github.label.create succeeded` と `github-create`・`scaffold` の `not_attempted` で、Issue の POST がない", verifies: ["R-02", "F-01"]}
	"T-08": {title: "親のある create で、親への追加の間に origin を変えると、`github.sub-issue.add succeeded`・`scaffold not_attempted`・`SCOPE_PUBLICATION_INCOMPLETE`・終了コード6で、カタログにディレクトリも changeset もない", verifies: ["R-02", "F-01"]}
	"T-06": {title: "既存の `test_issue440_g2_scope_change.py`、`test_issue440_g2_scope_create.py`、`uv run pytest` の全体が通る", verifies: ["R-01", "R-02"]}
}

verification: "`uv run pytest tests/cli_runtime/test_issue440_g2_scope_change.py tests/cli_runtime/test_issue440_g2_scope_create.py tests/cli_runtime/test_issue506_reread_after_confirmation.py`、`make lint`、`uv run pytest`（全体）。"
rollback:     "PR を閉じるか、マージ後なら `git revert` する。データの形は変えない。"
exit:         "T-01〜T-08 が通り、PR がマージできる状態で、CI が通る。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "medium", rationale: "3 policy §4 standard の実装（epic-00512 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-03", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "high"}
	}
}
