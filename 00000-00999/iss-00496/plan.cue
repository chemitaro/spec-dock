package spec

// 計画（Issue）。型 specdock/v1。

goal: "`installation update`（と `--dry-run`）が、写しを外してリンクのない枠ごとに `CLAUDE_SKILL_LINK_MISSING` を出し、置き方を示す。"

steps: {
	"S-01": {title: "警告のテストを先に書く（Red）", realizes: ["R-01"], status: "doing", session: "impl"}
	"S-02": {title: "警告を作る関数と、planned・succeeded・partial の結果への取り付け", realizes: ["R-01"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "葉の help に1文を足す", realizes: ["R-01"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "コードのレビュー、最終品質ゲート、PR", realizes: ["R-01"], status: "todo", after: ["S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "写しがあってリンクのない一時のリポジトリで、`installation update --dry-run --json` の `warnings` に、枠ごとの `CLAUDE_SKILL_LINK_MISSING`（`slot`、`link_target`、`command`）が出る", verifies: ["R-01"]}
	"T-02": {title: "適用（`--yes`）の結果にも同じ警告が出て、テキストの出力では標準エラーに `warning [CLAUDE_SKILL_LINK_MISSING]` の行が出る。示したコマンドを実行すると、リンクが置ける", verifies: ["R-01"]}
	"T-03": {title: "枠がリンク（壊れたリンクを含む）、写しがない、2回目の更新、`uninstall` では、警告が出ない", verifies: ["R-01"]}
	"T-04": {title: "片方の枠だけに写しがあるときは、その枠の1件だけが出る", verifies: ["R-01"]}
	"T-05": {title: "写しを外す途中で止まった `partial` の結果には、実際に外せた写しの枠の警告だけが出る", verifies: ["R-01"]}
}

verification: "`uv run pytest tests/integration/test_issue496_claude_skill_link_warning.py`、`make lint`、`uv run pytest`（全体）。"
rollback:     "PR を戻す。警告を足すだけで、ファイルの扱いは変えないので、戻しても利用者のファイルに影響しない。"
exit:         "T-01〜T-05 が通り、`scope check` に誤りがなく、PR がマージできる状態。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "medium", rationale: "standard の保証レベルで、仕様が決まっていて案内を足すだけ（統括の指定）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-03", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "high"}
	}
}
