package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "`dashboard service install`／`status`／`uninstall` と、`serve --service` の常駐の動き（ロックの待ち、Tailscale の取り直し、版の更新での終了）を作り、PR をマージできる状態で止める。"

steps: {
	"S-01": {title: "ファイルの形（plist、systemd の単位、引数の読み戻し）を domain に作る", realizes: ["R-01", "R-02"], status: "done", session: "impl"}
	"S-02": {title: "launchd と systemd の部品を、ダッシュボードの常駐の形で使えるようにし、工場とテストの守りを足す", realizes: ["R-01", "R-03"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "`install`、`status`、`uninstall` の処理とコマンドの一覧（58 → 61）を作る", realizes: ["R-01", "R-02", "R-03", "R-07"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "`serve --service`：ロックの待ち、Tailscale の取り直し、版の確かめと終了コード75、前面の知らせと API の項目", realizes: ["R-04", "R-05", "R-06"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "文書（`reference_cli.md`、README、`cli-redesign-guide.html`）と `static-inventory.json` を直す", realizes: ["R-07"], status: "done", after: ["S-03", "S-04"], session: "impl"}
	"S-06": {title: "コードのレビュー、最終品質ゲート、report.md、PR、CI", realizes: ["R-01", "R-07"], status: "done", after: ["S-05"], session: "impl"}
}

tests: {
	"T-01": {title: "plist と systemd の単位の形（KeepAlive、Restart=always、引数、PATH、記録の道）と、引数の読み戻し", verifies: ["R-01", "R-02"]}
	"T-02": {title: "launchd の部品：初めて入れる（bootstrap）、同じなら unchanged、変われば bootout → bootstrap、外す（bootout と削除）、同期の plist に触らない", verifies: ["R-01", "R-03"]}
	"T-03": {title: "systemd の部品：enable --now、変われば restart、disable --now と削除と daemon-reload、断られたら止まる", verifies: ["R-01", "R-03", "F-02"]}
	"T-04": {title: "`dashboard service install`／`status`／`uninstall` を差し替えた部品で動かす：結果の JSON、2回目の unchanged、番号を変えた updated、`service.log` が消える、2回目の uninstall", verifies: ["R-01", "R-02", "R-03"]}
	"T-05": {title: "入れられない環境の `install` は何も書かずに `DASHBOARD_SERVICE_UNSUPPORTED`、`status` は `supported: false`、`uninstall` は成功。番号の誤りは `DASHBOARD_PORT_INVALID`、部品の失敗は `DASHBOARD_SERVICE_FAILED`、`--dry-run` は終了コード2。単位があり管理が判定できないときも見えて外せる", verifies: ["F-01", "F-02", "F-03", "F-05", "R-03"]}
	"T-06": {title: "`status` が動いているサーバーの URL と版を示し、版が違えば `restart_pending`", verifies: ["R-02"]}
	"T-07": {title: "`serve --service`：別のサーバーがロックを持つ間は待ち、止まると起動する。待ちの間の SIGTERM で0", verifies: ["R-04"]}
	"T-08": {title: "版の確かめ：`--service` は記録を消して75で終わる。前面は終わらず API の `restart_required`", verifies: ["R-05"]}
	"T-09": {title: "`--service --tailscale`：住所なしで手元で起動し、住所が得られると待ち受けと記録と Host の検査に足す", verifies: ["R-06"]}
	"T-10": {title: "公開のコマンドが61で、ヘルプ、補完、文書、inventory の sha256 が合う", verifies: ["R-07"]}
	"T-11": {title: "子のプロセスで `dashboard serve --service --state-root` を、ロックを持つ別のサーバーがあるときに起動し、終わらずに待ち、SIGTERM で終了コード0（実のプロセスとシグナルでの確かめ）", verifies: ["R-04"]}
}

verification: "`uv run pytest`（全体）と `make lint`。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。PR の CI。本物の launchd と systemd への登録は、テストでも手元の確かめでもしない（利用者の登録を変えないため）。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`。常駐を入れた利用者は、戻す前に `dashboard service uninstall` を行う。"
exit: "PR がマージできる状態で、CI とゲートが通り、report.md に証拠を書いた。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-05", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
