package spec

goal: "詳しい画面で、CUE と Markdown の文書、報告、ADR をその場で描いて読め、検査の結果と計画の進み具合が出て、上の帯が前面の `serve` の起動し直しを促す。"

steps: {
	"S-01": {title: "文書の読み取りと覚え（dashboard_documents.py）と script_safe の公開", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-03"], status: "done", session: "std"}
	"S-02": {title: "文書の道と Scope の API の details を足す（dashboard_http.py、dashboard_site.py）", realizes: ["R-01", "R-02", "R-03", "R-04", "F-02", "F-03"], status: "done", after: ["S-01"], session: "std"}
	"S-03": {title: "詳しい画面の「文書」のタブ、検査の結果、進み具合（scope.js、scope.css）", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-02"], status: "done", after: ["S-02"], session: "std"}
	"S-04": {title: "起動し直しの知らせ（app.js、topbar.js）", realizes: ["R-05"], status: "done", session: "std"}
	"S-05": {title: "reference_cli.md と static-inventory.json を直す", realizes: ["R-01", "R-03"], status: "done", after: ["S-02"], session: "std"}
	"S-06": {title: "ヘッドレス Chrome で PC 幅と 390px、明るい・暗いを写し、report.md と artifacts に残す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05"], status: "doing", after: ["S-03", "S-04"], session: "std"}
}

tests: {
	"T-01": {title: "CUE の Scope の文書の道が、/ds/ と /vendor/ だけを読む描いたページを、sandbox の CSP で返す", verifies: ["R-01", "F-02"]}
	"T-02": {title: "Scope の API の details.check が、誤り・警告・誤りなしを返す", verifies: ["R-02"]}
	"T-03": {title: "Markdown の Scope の要件・設計・計画、報告、ADR を wrap_page で包んで返し、許さない道・リンク・../ を断る", verifies: ["R-03", "F-02", "F-03"]}
	"T-04": {title: "progress が todo・doing・done・dropped を数え、dropped を全体から除く", verifies: ["R-04"]}
	"T-05": {title: "cue がない・時間切れのとき、文書の道が次の1手のページを 503 で返し、Scope の API は status failed を返して、ほかの details は続く", verifies: ["F-01"]}
	"T-06": {title: "ファイルが変わらなければ cue を動かさず、変われば描き直す", verifies: ["R-01", "R-04"]}
	"T-07": {title: "画面の資産の静的な検査：scope.js が sandbox の枠、検査の結果、進み具合を描き、topbar.js が restart_required の知らせを出す", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02"]}
	"T-08": {title: "ヘッドレス Chrome の写し（PC 幅と 390px、明るい・暗い）で、文書の枠、検査の結果、進み具合、起動し直しの知らせが見える", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05"]}
}

verification: "`make lint` と `uv run pytest`（全体）と CI。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。画面は一時の状態の置き場で立てたサーバーをヘッドレス Chrome で写す（利用者の常駐と `~/.local/state/spec-dock/` は使わない）。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`（書き込みはないので、データの戻しは要らない）。"
exit: "PR がマージできる状態で、ゲートが同じコミットで通り、report.md に証拠と写しがある。"

execution: {
	sessions: std: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-06", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
