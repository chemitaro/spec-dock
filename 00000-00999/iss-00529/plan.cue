package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "ダッシュボードのサーバー、API、資料の配信、`hide`／`show`／`list`、在りかと「見た」の記録、埋め込みの約束、画面の骨組みを作り、PR をマージできる状態で止める。"

steps: {
	"S-01": {title: "状態の置き場の書き手（在りかの記録、隠す印、「見た」の記録）を作る", realizes: ["R-07", "R-08", "R-09"], status: "done", session: "impl"}
	"S-02": {title: "リポジトリの一覧とリポジトリごとの読み（最後に読めたモデル、revision、知らせ）を作る", realizes: ["R-01", "R-03", "R-06", "R-11"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "道筋、見出し、API、資料、「見た」の口を作る", realizes: ["R-04", "R-05", "R-06", "R-09", "R-10", "R-12"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "受け口（待ち受け、Host の検査、ロック、在りかの記録、止め方）と `dashboard serve` を作る", realizes: ["R-01", "R-02", "R-07"], status: "done", after: ["S-03"], session: "impl"}
	"S-05": {title: "`dashboard hide`／`show`／`list` を作り、コマンドの数を縛るテストと文書を直す", realizes: ["R-08"], status: "done", after: ["S-01"], session: "impl"}
	"S-06": {title: "画面の骨組みと5つの差し込み口を作り、wheel に入ることを確かめる", realizes: ["R-03", "R-10", "R-11", "R-13"], status: "done", after: ["S-03"], session: "impl"}
	"S-07": {title: "PC のブラウザーで、骨組み、自動の更新、埋め込み、資料の切り離し、hide/show を確かめて report.md に書く", realizes: ["R-03", "R-05", "R-06", "R-10", "R-11", "R-13"], status: "done", after: ["S-04", "S-05", "S-06"], session: "impl"}
	"S-08": {title: "コードのレビュー、最終品質ゲート、PR、CI", realizes: ["R-01", "R-13"], status: "doing", after: ["S-07"], session: "impl"}
}

tests: {
	"T-01": {title: "在りかの記録、隠す印、「見た」の記録の書きと読み（直近5件、読めないファイル、自分の pid だけ消す）", verifies: ["R-07", "R-08", "R-09"]}
	"T-02": {title: "リポジトリの一覧：隠す印、分からない行、2つのクローン、登録簿の読み直しと読めないとき", verifies: ["R-01", "R-03", "R-08", "F-07"]}
	"T-03": {title: "リポジトリごとの読み：ない、古い、壊れた（最後に読めたモデル）、知らない版、異常、PR が分からない、の知らせ", verifies: ["R-11", "F-01", "F-02", "F-03", "F-08"]}
	"T-04": {title: "revision がスナップショットの変化で変わり、「見た」で変わらない", verifies: ["R-06"]}
	"T-05": {title: "道筋：画面の HTML、隠した案内、知らないリポジトリ、405、道の部品の検査", verifies: ["R-04", "R-06", "R-08"]}
	"T-06": {title: "見出し：通常と `?embed=1` の `frame-ancestors`、資料の sandbox と同じ `frame-ancestors`、`/ds/` と `/vendor/` だけの CORS、`X-Frame-Options` なし", verifies: ["R-05", "R-10", "F-06"]}
	"T-07": {title: "資料：通常のファイル、リンク、`..`、ディレクトリ、外、デザインシステムの写し、2つのクローンの 409", verifies: ["R-05", "F-07"]}
	"T-08": {title: "「見た」の口：守り（Origin、見出し、種類）、記録、baseline での変化の印の保ち方", verifies: ["R-09", "F-09"]}
	"T-09": {title: "要約の API が `dashboard summary` と一致し、ないときは同じコード", verifies: ["R-12", "F-01"]}
	"T-10": {title: "受け口：番号0で起動、2つのリポジトリが応え、登録の追加が現れ、Host の 421、在りかの記録、止めると消える、二重起動", verifies: ["R-01", "R-02", "R-03", "R-07", "F-09"]}
	"T-11": {title: "使われている番号と Tailscale の住所がないときに、起動せずに止まる。`--tailscale` で見本の住所に待ち受ける", verifies: ["R-02", "F-04", "F-05"]}
	"T-12": {title: "`dashboard serve` を子のプロセスで起動し、SIGTERM で終了コード0、2つ目は already_running", verifies: ["R-01", "R-07"]}
	"T-13": {title: "`dashboard hide`／`show`／`list` を、チェックアウトの中と外で動かす。隠した後の一覧と案内、登録簿が変わらない", verifies: ["R-08"]}
	"T-14": {title: "公開のコマンドが58で、一覧、ヘルプ、文書が合う", verifies: ["R-01", "R-08"]}
	"T-15": {title: "wheel に画面の資源が入り、5つの差し込み口が決まった形を持つ。骨組みが `seen` の見出しと `embed` の約束の印を持つ", verifies: ["R-13", "R-10"]}
	"T-16": {title: "PC のブラウザー（ヘッドレスの Chrome）：骨組み、切り替え、自動の更新、埋め込みの受け渡し、資料の切り離し、hide/show、幅 390px（report.md）", verifies: ["R-03", "R-05", "R-06", "R-10", "R-11", "R-13"]}
	"T-17": {title: "画面と API と資料を読んでも、カタログと登録簿が変わらず、ネットワークへの要求がない", verifies: ["R-04"]}
}

verification: "`uv run pytest`（全体）と `make lint`。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。PC のブラウザーでの確かめ（一時のディレクトリの状態の置き場で立てたサーバー）。PR の CI。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`。状態の置き場の `dashboard/` の4つのファイルは、消してよい（隠す印と「見た」の記録が消えるだけ）。"
exit: "PR がマージできる状態で、CI とゲートが通り、report.md に証拠を書いた。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-08", model: "opus", effort: "high"}
	}
}
