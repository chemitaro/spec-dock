package spec

// 計画（Issue）。型 specdock/v1。

goal: "重複キーの宣言を拒み、消えた版3の worktree を unavailable にする"

steps: {
	"S-01": {title: "重複キーと消えた宣言のテストを先に書く（Red）", realizes: ["R-01", "R-02"], status: "todo", session: "impl"}
	"S-02": {title: "project_context.py を直す（Green）", realizes: ["R-01", "R-02"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "レビュー、最終品質ゲート、PR", realizes: ["R-01", "R-02"], status: "todo", after: ["S-02"], session: "impl"}
}

tests: {
	"T-01": {title: "`read_workspace_declaration` が重複キーの宣言（最後が4でも）を ValueError で拒み、`declares_schema_4` が偽になる", verifies: ["R-01"]}
	"T-02": {title: "重複キーの版4の宣言で、`workspace sync` などが PRECONDITION_FAILED（終了コード3）で止まり、`workspace doctor --raw` は観測を返す", verifies: ["R-01"]}
	"T-03": {title: "版3の兄弟の宣言が2回目の読み取りの前に消えても、`resolve_observed_context` が ValueError になり、`workspace sync` の行が unavailable になる", verifies: ["R-02"]}
}

verification: "`make lint` と `uv run pytest`（全体）。"
rollback:     "PR を `git revert` する。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "sonnet", effort: "medium", rationale: "Epic 00512 の plan.cue の session light"}
}
