package spec

// 計画（Issue）。型 specdock/v1。

goal: "第3波の手直し5件を、テスト駆動で入れ、PC のヘッドレスの Chrome で確かめ、マージできる PR にする。"

steps: {
	"S-01": {title: "骨組みの格子の行を明示し、graph と timeline の回避を消す", realizes: ["R-01"], status: "todo", session: "impl"}
	"S-02": {title: "`read_structure_facts` と覚える仕組みを足し、構造の API と詳しい画面に渡す", realizes: ["R-02", "R-03", "F-01", "F-02"], status: "todo", session: "impl"}
	"S-03": {title: "印の値を `core/ui.js` に寄せ、worktree の印を作業中の箱に限る", realizes: ["R-04"], status: "todo", session: "impl"}
	"S-04": {title: "骨組みが「見た」をモデルがあるときだけ送る", realizes: ["R-05"], status: "todo", session: "impl"}
	"S-05": {title: "経路の引き直しを問題の最も少ない回を返す形にし、代表のデータを足す", realizes: ["R-06"], status: "todo", session: "impl"}
	"S-06": {title: "PC のヘッドレスの Chrome で5画面を確かめ、手元の私的な構造で線の検査をやり直し、report.md に書く", realizes: ["R-01", "R-05", "R-06"], status: "todo", after: ["S-01", "S-02", "S-03", "S-04", "S-05"], session: "impl"}
}

tests: {
	"T-01": {title: "`app.css` が4つの行を明示し、`graph.css`・`timeline.css` に `grid-row` がない（静的）。5画面の `<main>` の高さ（ヘッドレスの Chrome、report.md に記録）", verifies: ["R-01"]}
	"T-02": {title: "CUE・Markdown の Scope と worktree のあるカタログで、構造の API の `assurance` と `branch`、詳しい画面の `scope` の同じ項目", verifies: ["R-02"]}
	"T-03": {title: "2回目の要求は `cue` を走らせず、`git worktree list` は要求ごとに1回。1つのファイルを書き換えるとその Scope だけ読み直す。見なかった Scope の分を捨てる", verifies: ["R-03"]}
	"T-04": {title: "読み取りの例外、`git worktree list` の失敗、`cue` がない、カタログがない・決まらないときに、構造の API が 200 でその項目だけ `null`", verifies: ["F-01"]}
	"T-05": {title: "締め切りの後の Scope と、締め切りをまたいで読めなかった Scope は `null` で覚えず、次の要求で読む（時計を差し替える）", verifies: ["F-02"]}
	"T-06": {title: "`parts.js`・`logic.js`・`marks.js`・`timeline.js` に値の表の定義がなく、印の関数の HTML が直す前と同じ（node）。箱の worktree の印は作業中だけ（静的とブラウザー）", verifies: ["R-04"]}
	"T-07": {title: "`app.js` が `snapshot.fetched_at` のあるときだけ `markSeen` を呼ぶ（静的）。スナップショットのないリポジトリでエラー0件・`POST` なし（ヘッドレスの Chrome、report.md に記録）", verifies: ["R-05"]}
	"T-08": {title: "線の検査の代表のデータ（spec-dock、種 532・15・18）のすべての表し方で問題0件。種 532 が1秒以内", verifies: ["R-06"]}
}

verification: "`spec-dock scope check iss-00544`、`make lint`、`uv run pytest`（全体）、PC のヘッドレスの Chrome（一時の状態の置き場、`--disable-features=MacAppCodeSignClone`、`Browser.close`）。手元の私的な構造の線の検査は `.workbench` の手順で行い、テストには入れない。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（状態の置き場とカタログに書かないので、戻すだけでよい）。"
exit: "PR が CI を通り、マージできる状態で、report.md に検証とゲートの結果がある。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-06", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
