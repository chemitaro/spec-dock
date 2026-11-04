package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

// 目標（任意）。
// goal: "..."

// 実装の手順。番号（S-01、…）をキーにし、番号の順に並べる。
// title と realizes（満たす要件・失敗の条件の番号）が必須。
// status は todo（既定）、doing、done、dropped。after は先に済ませる手順の番号。
// 1手順を1行に書き、status は title と realizes のすぐ後に置く。status の位置がそろうので一括で書き換えやすく、
// 同じ手順に status を2つ書く誤りも防げる（同じ値の2つは CUE が黙ってまとめ、違う値なら誤りになる）。
// すべての要件に、それを満たす手順が要る（dropped の手順は数えない）。
// strict 以上では、dropped でない手順のすべてが、いずれかの番号に結び付く。
goal: "人のタスクの規則をスキルに、使い方を文書に書き、テストとレビューとゲートを通して main への PR をマージできる状態にする。"

steps: {
	"S-01": {title: "仕様を書き、仕様のレビューを通す", realizes: ["R-05"], status: "done", session: "impl"}
	"S-02": {title: "確かめるテストを先に書く（Red）", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "スキルの「人のタスク」の節を書く", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "`todo.md` を足し、`README.md`、`canonical.md` を直す", realizes: ["R-04"], status: "todo", after: ["S-02"], session: "impl"}
	"S-05": {title: "写しと `static-inventory.json` を合わせ、テストを通す（Green）", realizes: ["R-05"], status: "todo", after: ["S-03", "S-04"], session: "impl"}
	"S-06": {title: "候補の wheel と隔離した利用者のリポジトリで、規則のとおりの登録・完了を確かめる", realizes: ["R-05"], status: "todo", after: ["S-05"], session: "impl"}
	"S-07": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05"], status: "todo", after: ["S-06"], session: "impl"}
}

// テスト。番号（T-01、…）をキーにする。title と verifies（確かめる要件・失敗の条件の番号）が必須。
// standard 以上では、すべての要件に、strict 以上では、すべての失敗の条件に、確かめるテストが要る。
tests: {
	"T-01": {title: "スキルに登録しない場面・登録する場面・`--blocks`・`--worktree` の規則の語がある", verifies: ["R-01", "F-01"]}
	"T-02": {title: "スキルに `--kind checklist --item`、`todo show <親>`、束にしない場面がある", verifies: ["R-02"]}
	"T-03": {title: "スキルに `todo done --record` と、統括が始めるときに `todo list` を読むことがある", verifies: ["R-03"]}
	"T-04": {title: "`todo.md` が配布され、`README.md` と `canonical.md` から辿れる。`canonical.md` の `TODO_*` が `reference_cli.md` にある", verifies: ["R-04", "F-01"]}
	"T-05": {title: "提供側と写しが一致し、inventory の sha256 が合い、`installation init` で入る", verifies: ["R-05"]}
	"T-06": {title: "候補の wheel と隔離した利用者のリポジトリで、スキルと文書が入り、`todo add --by agent`（束を含む）と `todo done --record` が動く（手で確かめ、report.md に書く）", verifies: ["R-05"]}
}

// 検証のしかた、戻し方、終わりの条件（任意）。critical では、手順があれば rollback が要る。
verification: "`make lint` と `uv run pytest`（全体）を通す。仕様のレビュー（spec-reviewer opus/medium）、コードのレビュー（code-reviewer sonnet/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通し、結果を report.md に書く。PR の CI を確かめる。"
rollback:     "マージの前なら PR を閉じる。マージの後なら `git revert`。文を足すだけで、コードとカタログに影響しない。"
exit:         "S-01〜S-07 が done、PR がマージできる状態で CI が通り、report.md にゲートの合格の証拠と、次の版の移行の注記に要る契約の変更がある。`work finish` は統括がマージの後に行う。"

// 実行の割り当て（任意）。手順の session は、ここのセッションの名前を指す。
// レビューの after は、どの手順の後かを指す。モデルと推論の名前は、どんな文字列でもよい。
execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "sonnet", effort: "medium", rationale: "epic-00547 の plan.cue の session light"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー", after: "S-05", model: "sonnet", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-07", model: "opus", effort: "high"}
	}
}
