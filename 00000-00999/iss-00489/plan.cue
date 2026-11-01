package spec

// 計画（Issue）。型 specdock/v1。作業しながら status を更新する。

goal: "5つの提案を実装し、マージできる PR で止める。"

steps: {
	"S-01": {title: "CUE の仕様を書き、`scope check` と仕様のレビューを通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02"], status: "done", session: "impl"}
	"S-02": {title: "選言の誤りをまとめる（テスト先行）", realizes: ["R-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "`CUE_INVALID` の `hint` を日本語にする（テスト先行）", realizes: ["R-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "Issue の雛形の手順の例、写し、目録、置き換えのテスト", realizes: ["R-03"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "警告 `SPEC_NO_TESTS`（テスト先行）", realizes: ["R-04"], status: "done", after: ["S-01"], session: "impl"}
	"S-06": {title: "`scope render --design-system inline`（テスト先行）とブラウザーでの確かめ", realizes: ["R-05", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-07": {title: "`cue.md`、`reference_cli.md`、`canonical.md`、写し、目録", realizes: ["R-04", "R-05"], status: "done", after: ["S-05", "S-06"], session: "impl"}
	"S-08": {title: "コードのレビュー、最終品質ゲート、PR、CI、`report.md`", realizes: ["F-02"], status: "doing", after: ["S-02", "S-03", "S-04", "S-07"], session: "impl"}
}

tests: {
	"T-01": {title: "`status: \"doin\"` で `CUE_INVALID` が1件、out of bound を含み、`cue_related` に衝突の行がある", verifies: ["R-01"]}
	"T-02": {title: "リポジトリの型の既定値つき列挙の項目でも1件になる", verifies: ["R-01"]}
	"T-03": {title: "必須の項目がない誤りの件数と中身が今と同じ（`cue_related` がない）", verifies: ["R-01", "F-02"]}
	"T-04": {title: "どの `CUE_INVALID` の `hint` も日本語で、英語の文がない（評価、型だけの場所、`schema`、項目のない文法の誤り）", verifies: ["R-02"]}
	"T-05": {title: "雛形の例の並び、例の行が型 `#Step` に合うこと、写しと目録のハッシュ", verifies: ["R-03"]}
	"T-06": {title: "今の版の雛形を持つ利用側の `installation update` が新しい版に置き換える", verifies: ["R-03"]}
	"T-07": {title: "light の Issue でテストがないと警告 `SPEC_NO_TESTS`、ほかの場合は出ない", verifies: ["R-04"]}
	"T-08": {title: "`cue.md` の表のコードが検査のコードと一対一に合う（`SPEC_NO_TESTS` を含む）", verifies: ["R-04"]}
	"T-09": {title: "既定の `scope render` と `render_scope_html` の HTML が今と同じ", verifies: ["R-05", "F-02"]}
	"T-10": {title: "`--design-system inline` の HTML が3つのファイルを埋め込み、`file:` の道筋を持たない", verifies: ["R-05"]}
	"T-11": {title: "デザインシステムのない場所でも、埋め込んだ HTML の本文がブラウザーで描かれる（手で確かめる）", verifies: ["R-05"]}
	"T-12": {title: "`--design-system inline` でデザインシステムがなければ `DESIGN_SYSTEM_MISSING` で止まり、HTML を出さない", verifies: ["F-01"]}
	"T-13": {title: "`make lint` と `uv run pytest`（全体）が通る", verifies: ["F-02"]}
}

verification: "`spec-dock scope check iss-00489`、`spec-dock scope render iss-00489`、`make lint`、`uv run pytest`。"
rollback:     "PR を戻す。データの移行はない。雛形は `known_old_sha256` で戻せる。"
exit:         "PR がマージできる状態で、CI が通り、`report.md` に結果がある。`work finish` はマージの後に統括が行う。"

execution: {
	sessions: impl: {
		task:      "仕様化、実装、PR の作成"
		model:     "opus"
		effort:    "medium"
		rationale: "epic-00425/plan.md の「モデルと推論」。standard の Issue（I-4〜I-7 と同じ）"
	}
	reviews: {
		spec: {role: "仕様のレビュー（spec-review）", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー（code-review）", after: "S-07", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート（final-quality-gate、1人）", after: "S-08", model: "opus", effort: "high"}
	}
}
