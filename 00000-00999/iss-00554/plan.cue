package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "人のタスクの API と画面、既存の画面の印を、#549・#550 の部品の上にテスト駆動で作り、PC のヘッドレス Chrome の写しを残し、レビューとゲートを通して main への PR をマージできる状態にする。"

steps: {
	"S-01": {title: "仕様を書き、仕様のレビューを通す", realizes: ["R-01", "R-04"], status: "doing", session: "impl"}
	"S-02": {title: "`scope_marks` と、`todo_aggregate.collect` への切り出し", realizes: ["R-01", "R-04"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "`dashboard_todos.py`（覚えと選び方）、`revision`、API の道", realizes: ["R-01", "R-03", "R-07", "R-08", "F-02"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "`structure`・`scopes/<ID>` の印と一覧と要約", realizes: ["R-04", "R-05", "R-06", "F-01"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "画面：道、上の帯、`views/todos.js` と logic と css", realizes: ["R-01", "R-02", "R-03", "R-07"], status: "todo", after: ["S-03"], session: "impl"}
	"S-06": {title: "既存の画面の印：構造の図、ボード、詳しい画面のタブ、横断の概況", realizes: ["R-04", "R-05", "R-06"], status: "todo", after: ["S-04", "S-05"], session: "impl"}
	"S-07": {title: "一時の状態の置き場でサーバーを立て、ヘッドレス Chrome で PC 幅と 390px、明るい・暗いの写しを残す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"], status: "todo", after: ["S-06"], session: "impl"}
	"S-08": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-01", "R-08"], status: "todo", after: ["S-07"], session: "impl"}
}

tests: {
	"T-01": {title: "`scope_marks` が、直接・配下を含む（重ねない）・関係する数を、閉じていないタスクだけで数え、知らない ID と輪で止まらない", verifies: ["R-04"]}
	"T-02": {title: "`collect` への切り出しの後も `todo list --all-repositories` の出力が変わらない（#550 のテストがそのまま通る）", verifies: ["R-01"]}
	"T-03": {title: "`/api/v1/todos` が表示中の2つのリポジトリのタスクを `ref` と `repository` つきで D-08 の並びで返し、隠したリポジトリを入れず、`status` で絞れ、知らない値は 400", verifies: ["R-01", "R-02"]}
	"T-04": {title: "`/api/v1/r/<repo>/todos` と `/todos/<ID>` が CLI と同じ形を返し、ない ID・形の違う ID は 404、壊れた記録は 409、読めないカタログは 503", verifies: ["R-03", "F-02"]}
	"T-05": {title: "1つのリポジトリの `todos` がファイルのとき、`/api/v1/todos` はその行を `unreadable` にし、ほかを返す。壊れた記録・衝突の写しは `invalid_files`／`conflict_copies` になる", verifies: ["R-08"]}
	"T-06": {title: "タスクを足すとリポジトリの `revision` と `/api/v1/todos/revision` が変わり、変わらない間は `read_catalog` を呼ばない", verifies: ["R-07"]}
	"T-07": {title: "`structure` の Scope の `todos` の印と上の `todos` の要約（`dashboard summary` と同じ数）、`scopes/<ID>` の止めている・配下・関係する一覧。人のタスクの読み取りが例外でも構造は 200 で `unavailable`", verifies: ["R-04", "R-05", "R-06", "F-01"]}
	"T-08": {title: "画面の道 `/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>` が殻を返し、全部の API と画面を開いてもカタログと状態の置き場が変わらない", verifies: ["R-03", "R-08"]}
	"T-09": {title: "node で、組の決め方、絞り込みの読み書き、期限の言葉、安全な Markdown（`<script>` とリンクの `javascript:` を描かない）、道の読み取り、人の印の言葉、カードと箱の印を確かめる", verifies: ["R-01", "R-02", "R-03", "R-04"]}
	"T-10": {title: "静的な検査：画面がサーバーの外を読まない、利用者の文字が esc を通る、書く口（POST、完了のボタン、写せるコマンド）がない、css が `[data-view=\"todos\"]` の下に閉じる", verifies: ["R-08", "R-03"]}
	"T-11": {title: "ヘッドレス Chrome で、全リポジトリ・リポジトリごと・1件・構造の図・ボード・詳しい画面のタブ・横断の概況を PC 幅と 390px、明るい・暗いで写し、期限切れの印、人の印、横にはみ出さないことを見る", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"]}
}

verification: "`make lint` と `uv run pytest`（全体）を通す。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通し、結果を report.md に書く。写しは artifacts と report.md に残す。PR の CI（Provider CI）の通過を確かめる。iPhone の Safari の確かめは統括が利用者に頼む。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。API と画面を足しただけで、CLI とカタログに影響しない。"
exit: "S-01〜S-08 が done、PR がマージできる状態で CI が通り、report.md にゲートの合格の証拠と写しと、次の版の移行の注記に要る契約の変更がある。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "epic-00547 の plan.cue の session std（policy の standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-08", model: "opus", effort: "high"}
	}
}
