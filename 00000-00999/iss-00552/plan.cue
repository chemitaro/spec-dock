package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "設定でダッシュボードに出すリポジトリを決められるようにし、レビューとゲートを通して main への PR をマージできる状態にする。"

steps: {
	"S-01": {title: "仕様を書き、仕様のレビューを通す", realizes: ["R-07"], status: "doing", session: "impl"}
	"S-02": {title: "表示の規則（D-01）", realizes: ["R-01", "R-02", "R-03", "F-01", "F-02"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "設定の読み取りと `read_visibility`（D-02）", realizes: ["R-01", "R-02", "F-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "サーバーの一覧（D-03）", realizes: ["R-03", "R-05", "F-01", "F-02"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "`dashboard list`／`hide`／`show` と文字の出力（D-04）", realizes: ["R-03", "R-04"], status: "todo", after: ["S-04"], session: "impl"}
	"S-06": {title: "要約と `todo list` の `hidden`（D-05）", realizes: ["R-06"], status: "todo", after: ["S-03"], session: "impl"}
	"S-07": {title: "文書、ヘルプ、inventory、dogfood の写し（D-06）", realizes: ["R-07"], status: "todo", after: ["S-05"], session: "impl"}
	"S-08": {title: "コードのレビュー、最終品質ゲート、report.md、PR と CI", realizes: ["R-07"], status: "todo", after: ["S-06", "S-07"], session: "impl"}
}

tests: {
	"T-01": {title: "利用者の全体の既定とリポジトリごとの値、鍵のそろえ方", verifies: ["R-01"]}
	"T-02": {title: "リポジトリの `dashboard.json` が利用者の設定に勝つ（true と false の両方）", verifies: ["R-02"]}
	"T-03": {title: "設定がなければ印だけで前と同じ。印は設定が出しても隠す。`show` が設定の隠すときに `hidden: true`、`hidden_by`、`DASHBOARD_HIDDEN_BY_CONFIG`", verifies: ["R-03"]}
	"T-04": {title: "`dashboard list` の JSON の `mark`、`config`、`hidden_by`、`config_problems` と文字の出力", verifies: ["R-04"]}
	"T-05": {title: "同じ `DashboardSite` が、利用者の設定と `dashboard.json` の書き換えを次の読み取りで反映する", verifies: ["R-05"]}
	"T-06": {title: "`dashboard summary` と `todo list --all-repositories` の `hidden` が設定を含む", verifies: ["R-06"]}
	"T-07": {title: "壊れた利用者の設定（JSON でない、schema 違い、値の型違い、鍵の誤り）で全部隠れ、`todo` の節の誤りは影響しない", verifies: ["F-01"]}
	"T-08": {title: "壊れた `dashboard.json` と、2つのクローンの食い違いで、そのリポジトリだけ隠れる", verifies: ["F-02"]}
	"T-09": {title: "`hide`／`show`／`list` が設定のファイルを作らず、書かない", verifies: ["F-03"]}
	"T-10": {title: "ヘルプと `reference_cli.md` の記述、inventory の sha256 と dogfood の写し（既存の配布資産のテスト）", verifies: ["R-07"]}
}

verification: "`make lint` と `uv run pytest`（全体）を通す。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）を通し、結果を report.md に書く。PR の CI の通過を確かめる。"
rollback: "マージの前なら PR を閉じる。マージの後で配る前なら `git revert`。設定のファイルは前の版では読まれないだけで、印は変わらない。"
exit: "S-01〜S-08 が done、PR がマージできる状態で CI が通り、report.md にゲートの合格の証拠と、次の版の移行の注記に要る契約の変更がある。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "epic-00427 の plan.cue の session std（policy §4 standard の実装）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-08", model: "opus", effort: "high"}
	}
}
