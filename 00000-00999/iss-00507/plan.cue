package spec

// 計画（Issue）。型 specdock/v1。

goal: "canonical の `scope delete` と `artifact create` が、途中の失敗で、起きたとおりの effects と status を返す。"

steps: {
	"S-01": {title: "3つの場面の失敗を注入するテストを書き、今のコードで落ちることを確かめる（Red）", realizes: ["R-01", "R-02"], status: "done", session: "impl"}
	"S-02": {title: "`canonical_scope_change.py` の `selection.clear` の記録と `attempted` の判定を直す（Green）", realizes: ["R-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "`canonical_artifact_write.py` で `artifacts/` を作った後の失敗を partial にし、既存のテストのコメントを直す（Green）", realizes: ["R-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、report.md、PR", realizes: ["R-01", "R-02"], status: "done", after: ["S-02", "S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "`--clear-active` の削除で、記録を消した後の記述子の close に OSError を注入すると、終了コード6、`selection.clear succeeded`、`scope.delete not_attempted`、記録はなく Scope のディレクトリは残る（手本 `test_issue413_scope_delete.py::test_confirmed_direct_clear_survives_a_later_descriptor_cleanup_failure`）", verifies: ["R-01"]}
	"T-02": {title: "Scope のディレクトリの最初の unlink を効かせた後に OSError を注入すると、終了コード6、`scope.delete unknown`、`remaining_paths` にそのディレクトリ、控えは残る", verifies: ["R-01"]}
	"T-03": {title: "Scope の `artifact create` で `artifacts/` の mkdir を効かせた後に OSError を注入すると、終了コード6、`partial`、`ARTIFACT_PUBLICATION_INCOMPLETE`、effects が `artifact.directory unknown` と `artifact not_attempted`、空の `artifacts/` が残り、変更の記録はない（手本 `test_issue413_artifact.py::test_uncertain_artifact_directory_creation_reports_partial_and_preserves_it_without_publication`）", verifies: ["R-02"]}
	"T-05": {title: "`artifacts/` を作った後、publication の stage の作成に OSError を注入すると、終了コード6、`partial`、effects が `artifact.directory succeeded` と `artifact failed`、空の `artifacts/` が残る", verifies: ["R-02"]}
	"T-04": {title: "既存の `test_issue440_g2_scope_delete.py`、`test_issue440_g3_artifact.py`、`uv run pytest` の全体が通る", verifies: ["R-01", "R-02"]}
}

verification: "`uv run pytest tests/cli_runtime/test_issue440_g2_scope_delete.py tests/cli_runtime/test_issue440_g3_artifact.py`、`make lint`、`uv run pytest`（全体）。"
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
