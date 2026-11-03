package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "ダッシュボードのモデルと要約を作り、`spec-dock dashboard summary` を出して、PR をマージできる状態で止める。"

steps: {
	"S-01": {title: "スナップショットの文書の読み（版1・版2、PR の欄）を作る", realizes: ["R-08"], status: "todo", session: "impl"}
	"S-02": {title: "状態、理由、ボードの列、マージ待ちの分け方を作る", realizes: ["R-01", "R-02"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "後に続く数、待ち先の数、推奨順を作る", realizes: ["R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "片付けの候補、残す印、配下の段、依存の道筋を作る", realizes: ["R-04", "R-05"], status: "todo", after: ["S-02"], session: "impl"}
	"S-05": {title: "「見た」の記録の1件と比べ方、時間の軸、古さを作る", realizes: ["R-06", "R-07", "R-09"], status: "todo", after: ["S-02"], session: "impl"}
	"S-06": {title: "要約の JSON を作る", realizes: ["R-10"], status: "todo", after: ["S-03", "S-04"], session: "impl"}
	"S-07": {title: "`dashboard summary` のコマンドとファイルの読みを作り、コマンドの数を縛るテストと文書を直す", realizes: ["R-11"], status: "todo", after: ["S-06"], session: "impl"}
	"S-08": {title: "コードのレビュー、最終品質ゲート、PR、CI", realizes: ["R-10", "R-11"], status: "todo", after: ["S-07"], session: "impl"}
}

tests: {
	"T-01": {title: "見本の構造で5つの状態と理由が決まり、Issue の状態が `evaluate_readiness` と一致する", verifies: ["R-01", "F-05"]}
	"T-02": {title: "マージ待ちの列と「マージできる」「直す必要あり」、下書きと PR が分からないときの扱い", verifies: ["R-02"]}
	"T-03": {title: "後に続く数と待ち先の数と推奨順（着手できるものの先頭、止められているものの順）", verifies: ["R-03"]}
	"T-04": {title: "片付けの候補の2つの種類と残す印", verifies: ["R-04"]}
	"T-05": {title: "配下の段、外への依存、循環、上流と下流、大もとの待ち先", verifies: ["R-05", "F-05"]}
	"T-06": {title: "「見た」の記録との比べ方（状態、新しい、PR、題名だけは数えない、比べる元なし）", verifies: ["R-06"]}
	"T-07": {title: "週ごとの累計と最近の動きの順", verifies: ["R-07"]}
	"T-08": {title: "版1と版2の読み、PR の対応づけ、PR の確かさ（unknown、stale、fresh）", verifies: ["R-08"]}
	"T-09": {title: "取得の時刻の古さ（29分と31分）と異常の数", verifies: ["R-09", "F-02"]}
	"T-10": {title: "要約の JSON の項目と、モデルとの一致", verifies: ["R-10"]}
	"T-11": {title: "`dashboard summary` をチェックアウトの中と外で動かし、GitHub に要求せず、`server` と `hidden` が出る", verifies: ["R-11", "F-06"]}
	"T-12": {title: "スナップショットがない、知らない版、読めないときの失敗のコード", verifies: ["F-01", "F-03", "F-04"]}
	"T-13": {title: "250件の構造でモデルが十分に速く作れる", verifies: ["R-03"]}
	"T-14": {title: "公開のコマンドが54で、一覧、ヘルプ、文書が合う", verifies: ["R-11"]}
}

verification: "`uv run pytest`（全体）と `make lint`。仕様のレビュー（spec-reviewer opus/high）、コードのレビュー（code-reviewer opus/high）、最終品質ゲート（quality-gate-reviewer opus/high、1人）。PR の CI。"
rollback: "マージの前なら PR を閉じる。マージの後なら `git revert`。状態の置き場に書くものはない。"
exit: "PR がマージできる状態で、CI とゲートが通り、report.md に証拠を書いた。`work finish` は統括がマージの後に行う。"

execution: {
	sessions: impl: {task: "仕様化と実装（Orca の worker）", model: "opus", effort: "medium", rationale: "policy §4 standard の実装（epic-00427 の plan.cue の session std）"}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-08", model: "opus", effort: "high"}
	}
}
