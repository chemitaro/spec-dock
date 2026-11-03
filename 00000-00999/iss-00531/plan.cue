package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "状態のボード、Scope の詳しい画面、横断の概況、検索を、骨組みの差し込み口に入れ、PR をマージできる状態で止める。"

steps: {
	"S-01": {title: "要件、設計、計画、説明資料を書き、仕様のレビューを通す", realizes: ["R-01", "R-07", "R-12"], status: "doing", session: "impl"}
	"S-02": {title: "構造と Scope の JSON に `rank`、`in_progress`、`dependencies` を足す", realizes: ["R-01", "R-02", "R-07", "R-08", "R-12"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "詳しい画面の読み取り（カタログ、文書、Artifact、保証レベル、worktree）を作り、`dashboard_http.py` の1か所でつなぐ", realizes: ["R-07", "R-08", "R-09"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "共有の部品（`views/_shared/parts.js`、`parts.css`）と検索（`search.js`、`app.js` の1行）を作る", realizes: ["R-04", "R-05", "R-10", "R-11", "R-14", "R-15"], status: "todo", after: ["S-01"], session: "impl"}
	"S-05": {title: "状態のボード（`views/board.js`）を作る", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-14", "R-15"], status: "todo", after: ["S-02", "S-04"], session: "impl"}
	"S-06": {title: "Scope の詳しい画面（`views/scope.js`）を作る", realizes: ["R-07", "R-08", "R-09", "R-11", "R-14", "R-15"], status: "todo", after: ["S-03", "S-04"], session: "impl"}
	"S-07": {title: "横断の概況（`views/overview.js`）を作る", realizes: ["R-12", "R-13", "R-14", "R-15"], status: "todo", after: ["S-02", "S-04"], session: "impl"}
	"S-08": {title: "PC のヘッドレスの Chrome で、PC の幅と 390px、明るい表示と暗い表示、JavaScript のエラーなしを確かめ、report.md と Artifact に残す", realizes: ["R-01", "R-02", "R-03", "R-05", "R-10", "R-11", "R-12", "R-13", "R-14", "R-15"], status: "todo", after: ["S-05", "S-06", "S-07"], session: "impl"}
	"S-09": {title: "コードのレビュー、最終品質ゲート、PR、CI", realizes: ["R-01", "R-15"], status: "todo", after: ["S-08"], session: "impl"}
}

tests: {
	"T-01": {title: "構造の JSON の `rank` がモデルの推奨順と一致する（マージできる → 直す必要あり → 作業中 → 着手できる（後に続く数の多い順）→ 止められている（待ち先の少ない順））", verifies: ["R-01", "R-02", "R-12"]}
	"T-02": {title: "Scope の JSON の `dependencies`：自分の依存、祖先から引き継いだ依存（宣言した祖先）、Scope でない Issue、待たれているもの", verifies: ["R-07", "R-08"]}
	"T-03": {title: "詳しい画面の読み取り：カタログ ok／ない／2つのクローン／Scope のディレクトリがない、文書のありなし（`.cue` と昔の `.md`、リンクは数えない）、Artifact の一覧（隠しファイルとリンクを除く、名前の逃がし、打ち切り）", verifies: ["R-08", "R-09"]}
	"T-04": {title: "詳しい画面の読み取り：保証レベル（読めた、読めない、`cue` の時間切れ）と worktree（Scope を名指すブランチだけ、git の失敗）が、その欄だけ「読めない」になる", verifies: ["R-07", "F-03"]}
	"T-05": {title: "API：`scopes/<ID>` が `dependencies` と `details` を返し、知らない ID は読み取りを走らせずに 404。カタログもリポジトリも書かれない", verifies: ["R-07", "R-09", "F-02"]}
	"T-06": {title: "画面の資源：3つの画面が差し込み口の形（`id`、`title`、`icon`、`styles`、`render`）を持ち、`views/_shared/` の部品を読み、外の URL を読まず、`innerHTML` に入れる利用者の文字を `esc` で逃がす。`app.js` の追加が `mountSearch` の1行だけ", verifies: ["R-15", "F-04"]}
	"T-07": {title: "JavaScript の単体（`node` があるとき）：ボードの列の振り分けと並び、問い合わせの文字列の切り替え、検索の一致（ID、0埋めなし、番号、`#番号`、題名）、変化と PR の印の言葉、概況の警告の帯の理由", verifies: ["R-01", "R-02", "R-05", "R-06", "R-10", "R-13"]}
	"T-08": {title: "ヘッドレスの Chrome：ボードの列と順、片付けの候補の一覧、種類と親と終わったものの切り替えと URL、詳しい画面の見出しと5つのタブと段、カタログのない Scope、検索から詳しい画面へ、概況の札と古いときの警告の帯、埋め込みの逃げ道、PC と 390px と暗い表示ではみ出さずエラーなし、概況で `seen` が増えない（report.md）", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09", "R-10", "R-11", "R-12", "R-13", "R-14", "R-15", "F-01"]}
}

verification: "`make lint` と `uv run pytest`（全体）。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。PC のヘッドレスの Chrome での確かめ（一時のディレクトリの状態の置き場で立てたサーバー）。PR の CI。iPhone の Safari の確かめは #534 で利用者に頼む。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`。画面と JSON の項目を足すだけで、状態の置き場とカタログには何も書かない。"
exit: "PR がマージできる状態で、CI とゲートが通り、report.md に証拠を書いた。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-08", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-09", model: "opus", effort: "high"}
	}
}
