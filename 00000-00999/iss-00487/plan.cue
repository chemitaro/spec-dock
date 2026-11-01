package spec

// 計画（Issue）。型 specdock/v1。作業しながら status を更新する。

goal: "3つの積み残しを直し、CUE の仕様で回した試しを記録して、マージできる PR で止める。"

steps: {
	"S-01": {title: "CUE の仕様を書き、`scope check` と `scope render` で確かめる", realizes: ["R-05"], status: "done", session: "impl"}
	"S-02": {title: "ガイドの相互リンクを直す（配布と dogfood の写し、目録のハッシュ）", realizes: ["R-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "`cue.md` の表を単独で縛るテストを足す", realizes: ["R-02"], status: "done", after: ["S-01"], session: "impl"}
	"S-04": {title: "葉の `--help` に共通の引数を出す", realizes: ["R-03", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-05": {title: "`cue.md` の共通の引数の説明を実態に合わせる", realizes: ["R-04"], status: "done", after: ["S-04"], session: "impl"}
	"S-06": {title: "コードのレビュー、最終品質ゲート、PR、CI", realizes: ["F-02"], status: "done", after: ["S-02", "S-03", "S-05"], session: "impl"}
	"S-07": {title: "`report.md` に結果と試しの記録を書く", realizes: ["R-05"], status: "done", after: ["S-06"], session: "impl"}
}

tests: {
	"T-01": {title: "2つのガイドの CUE の節が `cue.md` と `explanation.md` へリンクし、写しと目録が合う", verifies: ["R-01"]}
	"T-02": {title: "`cue.md` の表のコードが、検査のコードと一対一に合い、止まるコードの終了コードが合う", verifies: ["R-02"]}
	"T-03": {title: "葉ごとに、help の共通の引数が、解析の受け付ける集合と等しい", verifies: ["R-03", "F-01"]}
	"T-04": {title: "`scope create issue --help` に `--json`、`--offline`、`--timeout`、`--yes`、`--dry-run` が出る", verifies: ["R-03"]}
	"T-05": {title: "`cue.md` が葉の help に共通の引数が出ると書く", verifies: ["R-04"]}
	"T-06": {title: "`make lint` と `uv run pytest`（全体）が通る", verifies: ["F-02"]}
}

verification: "`spec-dock scope check iss-00487`、`spec-dock scope render iss-00487`、`make lint`、`uv run pytest`。"
rollback:     "PR を戻す。データの移行はない。"
exit:         "PR がマージできる状態で、CI が通り、`report.md` に試しの記録がある。`work finish` はマージの後に統括が行う。"

execution: {
	sessions: impl: {
		task:      "仕様化、実装、PR の作成"
		model:     "opus"
		effort:    "medium"
		rationale: "epic-00425/plan.md の「モデルと推論」I-7。小さな直しで light"
	}
	reviews: {
		spec: {role: "仕様のレビュー（spec-review）", after: "S-01", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー（code-review）", after: "S-05", model: "sonnet", effort: "high"}
		gate: {role: "最終品質ゲート（final-quality-gate、1人）", after: "S-06", model: "opus", effort: "high"}
	}
}
