package spec

// 計画（Issue）。型 specdock/v1。

goal: "状態の色と形を改め、作業中の印に進み具合と稼働を入れ、テスト駆動で実装し、PC のヘッドレスの Chrome で確かめ、マージできる PR にする。"

steps: {
	"S-01": {title: "仕様（requirement・design・plan・explanation）を書き、`scope check` と仕様のレビューを通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "F-01", "F-02"], status: "done", session: "impl"}
	"S-02": {title: "`dashboard_progress.py` の読み取りと覚える仕組み、API の `progress`、`revision` の `plan.cue` を、テスト先行で入れる", realizes: ["R-06", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "状態の色の札と付け替え（`app.css`、`parts.css`、`graph.css`、`todos.css`、`todos.js`、`scope.js`、`overview.js`、`board.js`）を、コントラストのテスト先行で入れる", realizes: ["R-01", "R-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "`core/ui.js` の形、`progressRing`、`stateMark` と時刻の関数を、node のテスト先行で入れ、印の見本の golden を新しい形で書き直す", realizes: ["R-01", "R-03", "R-04", "R-05", "F-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "画面に組み込む（構造の図、要点、詳しい画面は動かす。ボード、概況、検索、人のタスクは動かさない）。点滅の CSS と `app.js` の30分の境目", realizes: ["R-03", "R-04", "R-05"], status: "done", after: ["S-03", "S-04"], session: "impl"}
	"S-06": {title: "PC のヘッドレスの Chrome で写しを撮り、artifacts と report.md に残す", realizes: ["R-02", "R-05", "R-07"], status: "doing", after: ["S-02", "S-05"], session: "impl"}
	"S-07": {title: "コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、PR と CI", realizes: ["R-01", "R-06"], status: "todo", after: ["S-06"], session: "impl"}
}

tests: {
	"T-01": {title: "`read_plan_progress`：作業中の Issue の数と `modified_at`、2回目は `cue` を走らせない、詳しい画面の API の後も捨てない、書き換えたものだけ読み直す、見なかった分を捨てる", verifies: ["R-06"]}
	"T-02": {title: "`read_plan_progress`：読めない・`cue` がない・例外・締め切りの後・カタログがないときの None と、覚える／覚えないの区別", verifies: ["F-01"]}
	"T-03": {title: "構造の API と詳しい画面の API の `progress`（作業中の Issue だけ、同じ値）と、`plan.cue` の書き換えで `revision` が変わる（HTTP の層）", verifies: ["R-06"]}
	"T-04": {title: "CSS の値から、明るい・暗いの状態の色の地との差（3:1）と札の文字の差（4.5:1）を計算する。`[data-st]` が札だけを使い、止められている・人が止めているに `--ds-danger` がない", verifies: ["R-01", "R-02"]}
	"T-05": {title: "node：5つの形が丸に収まり、輪の区切り・弧・外枠、live の重ね、`aria-label` の数、Epic の配下の割合", verifies: ["R-01", "R-03", "R-04"]}
	"T-06": {title: "node：`movedAt`（`modified_at` を含む、配下を含む、読めない時刻）、done = total と外枠だけの live の重ね、29分と31分の `isLive`、`idleWords`、`motion: false` で点滅の要素がない", verifies: ["R-05", "F-02"]}
	"T-07": {title: "静的：`prefers-reduced-motion` で重ねだけが消える、一覧の画面が `motion: true` を渡さない、各画面の作業中の印が `stateMark` で描かれる、`app.js` が `liveUntil` で描き直す", verifies: ["R-03", "R-05"]}
	"T-08": {title: "ヘッドレスの Chrome：4通りの写し、29分と31分の箱、要点の「動きなし」、縮めた動きのエミュレーション、ブラウザーの記録のエラー0件", verifies: ["R-02", "R-03", "R-05", "R-07"]}
}

verification: "`spec-dock scope check iss-00574`、`make lint`、`uv run pytest`（全体）、PC のヘッドレスの Chrome（一時の状態の置き場、`--disable-features=MacAppCodeSignClone`、`Browser.close`）。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（状態の置き場とカタログに書かないので、戻すだけでよい）。"
exit: "PR が CI を通り、マージできる状態で、report.md に写しと検証とゲートの結果がある。"

execution: {
	sessions: {
		spec: {task: "仕様化（統括が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括の依頼：policy §4 standard の実装"}
		impl: {task: "実装", model: "opus", effort: "medium", rationale: "統括の依頼：policy §4 standard の実装"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-06", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-07", model: "opus", effort: "high"}
	}
}
