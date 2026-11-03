package spec

// 計画（Issue）。型 specdock/v1。

goal: "定期の同期が PR の状態をスナップショットの版2に書き、読む側が Scope ごとの PR を得られるようにし、版の移りと既存の読む側を壊さないことをテストで確かめる。"

steps: {
	"S-01": {title: "領域のモデルと版2の JSON（読み書き、版1の読み、引き継ぎ）を作る", realizes: ["R-02", "R-06"], status: "todo", session: "std"}
	"S-02": {title: "`pull_requests_by_scope` を作る", realizes: ["R-05"], status: "todo", after: ["S-01"], session: "std"}
	"S-03": {title: "PR の GraphQL の問い合わせと、待たないレート制限を作る", realizes: ["R-01", "R-04"], status: "todo", after: ["S-01"], session: "std"}
	"S-04": {title: "`SnapshotStore` と `ensure_fresh(\"cycle\")` に PR の取得、間隔、失敗の記録をつなぐ", realizes: ["R-01", "R-03", "R-04"], status: "todo", after: ["S-03"], session: "std"}
	"S-05": {title: "版の移りと既存の読む側の回帰のテストを足す", realizes: ["R-06"], status: "todo", after: ["S-04"], session: "std"}
	"S-06": {title: "レビュー、最終品質ゲート、report.md、PR", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"], status: "todo", after: ["S-05"], session: "std"}
}

tests: {
	"T-01": {title: "版2の JSON の往復、3つの鍵の形、許さない値の拒否（単体：tests/unit/domain/test_canonical_structure.py）", verifies: ["R-02", "F-04"]}
	"T-02": {title: "CI の写し方（5つと rollup なし）、状態、マージの可否の写し方、形の違う応答の拒否（単体：GraphQL の応答の解釈）", verifies: ["R-01", "R-02", "F-01"]}
	"T-03": {title: "`pull_requests_by_scope` の対応づけと選び方", verifies: ["R-05"]}
	"T-04": {title: "同期の周期で、1回の GraphQL で PR が入り、まだ取っていない値から変わる（gh の stub）", verifies: ["R-01", "R-02"]}
	"T-05": {title: "2分の間隔と、display・decision・refresh で PR を問い合わせないこと", verifies: ["R-03"]}
	"T-06": {title: "PR の問い合わせの失敗とレート制限で、構造は続き、前回の値を残し、待たずに理由を書き、成功で null に戻る", verifies: ["R-04", "F-01", "F-02"]}
	"T-07": {title: "構造の取り直しと書き込みの反映が PR を引き継ぎ、古い PR の結果が新しい結果を上書きしない、スナップショットがないときは試みない", verifies: ["F-03", "F-04"]}
	"T-08": {title: "版1の読み、版2で書き戻し、古い読み手が版2を「ない」とする、古い版の書き戻しを読む、知らない版の拒否", verifies: ["R-06"]}
	"T-09": {title: "版1と版2で、`dependency check` の結果と今のダッシュボードの `input_hash` が一致する", verifies: ["R-06"]}
	"T-10": {title: "開いた PR 100件、閉じた PR 50件の上限が問い合わせにあり、それを超える PR を持たない", verifies: ["R-01", "F-05"]}
}

verification: "`make lint` と `uv run pytest`（全体）と CI。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。配った後に前の版へ戻すと、前の版は版2を「ない」として一度だけ構造を取り直す。"
exit: "PR がマージできる状態で、ゲートの証拠を report.md に書き、統括に PR の URL と契約の変更を報告した。"

execution: {
	sessions: std: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-05", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-05", model: "opus", effort: "high"}
	}
}
