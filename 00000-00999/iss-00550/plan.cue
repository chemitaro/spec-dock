package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "全リポジトリの集約の一覧、`todo show <REF>`、`dashboard summary` の `todos` と、その文書を、テスト駆動で作り、iss-00549 のテストの穴を埋め、レビューとゲートを通して main への PR をマージできる状態にする。"

steps: {
	"S-01": {title: "仕様を書き、仕様のレビューを通す", realizes: ["R-20"], status: "done", session: "impl"}
	"S-02": {title: "`tally` と `repository_row` に数え方と行を移し、`classify`／`load_record` を `TodoStore` で受ける形に割る", realizes: ["R-10", "R-11"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "`select_catalogs`、`read_catalog`、集約の一覧、`todo show <REF>` とディスパッチ", realizes: ["R-10", "F-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "`dashboard summary` とサーバーの summary の `todos`", realizes: ["R-11", "F-03"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "iss-00549 のテストの穴を埋める", realizes: ["R-21"], status: "todo", after: ["S-01"], session: "impl"}
	"S-06": {title: "CLI の引数とヘルプ、`reference_cli.md` と dogfood の写し、inventory", realizes: ["R-20"], status: "todo", after: ["S-03", "S-04"], session: "impl"}
	"S-07": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-10", "R-11", "R-20", "R-21"], status: "todo", after: ["S-05", "S-06"], session: "impl"}
}

tests: {
	"T-01": {title: "登録簿の2つのリポジトリのタスクが、チェックアウトの外の1回の `todo list --all-repositories` に `ref` つきで並び、`--repository` で絞れ、登録簿にない名前は `TODO_REPOSITORY_UNKNOWN` の警告になる", verifies: ["R-10"]}
	"T-02": {title: "隠したリポジトリの `hidden: true`、`repository` が null の行、2つ目のクローンの `duplicate` と警告", verifies: ["R-10"]}
	"T-03": {title: "カタログが無い・`todos` がファイルのリポジトリが `unreadable` と `problem` になり、ほかのリポジトリの分が返る。登録簿が壊れていれば `TODO_REGISTRY_UNREADABLE` で3", verifies: ["F-03", "R-10"]}
	"T-04": {title: "壊れた記録と衝突の写しが、集約でもそのリポジトリの `invalid_files`／`conflict_copies` と警告になり、ほかの記録は返る", verifies: ["R-10"]}
	"T-05": {title: "`todo show owner/name/t-xxxx` がチェックアウトの外で1件を返し、知らないリポジトリ・形の違う REF・見つからない ID が決めたコードで止まる", verifies: ["R-10", "F-03"]}
	"T-06": {title: "`dashboard summary` の `todos` が、開いている（延期中を含む）・止めている・期限切れの数を親のタスクだけで数え、チェックアウトの中では `--no-schedule` のカタログも読み、読めなければ `unavailable` で要約は成功する", verifies: ["R-11", "F-03"]}
	"T-07": {title: "サーバーの `/api/v1/r/<repo>/summary` の `todos` が `dashboard summary <repo>` と同じ", verifies: ["R-11"]}
	"T-08": {title: "集約、`show <REF>`、`dashboard summary`、`update`／`snooze`／`cancel`／`reopen` で `gh` の stub が呼ばれず、`canonical_work.py` が `todo` を参照しない", verifies: ["R-21", "R-10"]}
	"T-09": {title: "ヘルプと `reference_cli.md` と dogfood の写し、inventory の sha256", verifies: ["R-20"]}
}

verification: "`make lint` と `uv run pytest`（全体）を通す。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通し、結果を report.md に書く。PR の CI（Provider CI）の通過を確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。足した項目と引数だけなので、ほかのコマンドとカタログに影響しない。"
exit: "S-01〜S-07 が done、PR がマージできる状態で CI が通り、report.md にゲートの合格の証拠と、次の版の移行の注記に要る契約の変更がある。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "epic-00547 の plan.cue の session std（policy の standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-06", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-07", model: "opus", effort: "high"}
	}
}
