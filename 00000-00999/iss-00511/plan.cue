package spec

// 計画（Issue）。型 specdock/v1。

goal: "0.5.0 の後に残った文書とテストの不足を直し、PR を作る。"

steps: {
	"S-01": {title: "仕様（design/plan）を書き、レビューを通す", realizes: ["R-01", "R-02", "R-03"], status: "doing", session: "light"}
	"S-02": {title: "README の数のテストと文書・package-data を直す（Red → Green）", realizes: ["R-01"], status: "todo", after: ["S-01"], session: "light"}
	"S-03": {title: "撤去の不在のテストと、report.md のバイトのテストを足す", realizes: ["R-02"], status: "todo", after: ["S-02"], session: "light"}
	"S-04": {title: "`canonical check` の重複キーを拒む（Red → Green）", realizes: ["R-03"], status: "todo", after: ["S-01"], session: "light"}
	"S-05": {title: "`static-inventory.json` と dogfood の写しをそろえる", realizes: ["R-01", "R-02"], status: "todo", after: ["S-02", "S-03"], session: "light"}
	"S-06": {title: "コードのレビュー、最終品質ゲート、PR", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-04", "S-05"], session: "light"}
}

tests: {
	"T-01": {title: "README の「全N コマンド」の N が `LEAF_ARGUMENTS` の数と等しい", verifies: ["R-01"]}
	"T-02": {title: "`docs/github-issue-integration.md` に local backend の記述がなく、package-data に外したパターンが無い", verifies: ["R-01"]}
	"T-03": {title: "配布する文書の全体に、撤去した案内が許可の表の外で現れない", verifies: ["R-02"]}
	"T-04": {title: "作った report.md が 0.4.2 の出力とバイトで一致する（3種類）", verifies: ["R-02"]}
	"T-05": {title: "重複したキーの宣言を、`canonical check` が `WORKSPACE_DECLARATION_INVALID`（reason=duplicate-member）の1件にする", verifies: ["R-03"]}
}

verification: "`make lint` と `uv run pytest`（全体）。新しいテストは、直す前に失敗する（Red）ことを確かめる。"
rollback:     "マージの前なら PR を閉じる。"
exit:         "PR が CI を通り、マージできる状態になる。"

execution: {
	sessions: light: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "policy §4 light の実装（epic-00512 の session light）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー", after: "S-05", model: "sonnet", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
