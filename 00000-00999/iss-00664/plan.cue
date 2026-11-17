package spec

// 計画（Issue）。型 specdock/v1。
// 作業しながら、手順の追加、変更、status の更新を、このファイルに直接書く。

goal: "時間に左右されない横断の構造の動きのテストと、原因の記録"

steps: {
	"S-01": {title: "各マージで単独10回走らせ、計測で落ちる仕組みを確かめる", realizes: ["R-01"], status: "done", session: "impl"}
	"S-02": {title: "ハーネスに run.styled を足し、motion と input の run に付ける", realizes: ["R-02", "F-01"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "単独20回、打ち切り 0ms・1e9ms、make lint、uv run pytest で確かめる", realizes: ["R-02"], status: "doing", after: ["S-02"], session: "impl"}
	"S-04": {title: "1440×900 の Chrome で指揮の線の動きを確かめ、report.md に残す", realizes: ["R-03", "R-01"], status: "todo", after: ["S-02"], session: "impl"}
}

tests: {
	"T-01": {title: "test_the_motion_stills_and_watches_on_the_cross_repository_structure を単独に20回、0回落ちる", verifies: ["R-02"]}
	"T-02": {title: "whenStyled の打ち切りを 0ms と 1e9ms にしても、このテストのファイルが通る（時間に左右されない）", verifies: ["R-02", "F-01"]}
	"T-03": {title: "1440×900 の Chrome で、読み込み・ドラッグ・ホイール・キーの後に is-still が外れ、絵が切り替わる", verifies: ["R-03"]}
	"T-04": {title: "各マージで単独10回の落ちた回数の表が report.md にある", verifies: ["R-01"]}
}

verification: "make lint、uv run pytest（全体、手元の macOS）、T-01〜T-04"
rollback:     "テストの2ファイルの変更を戻す（画面のコードは変えていない）"
exit:         "T-01〜T-04 が合格し、final-quality-gate が同じコミットで合格する"

execution: {
	sessions: {
		spec: {task: "仕様化", model: "claude-opus-5-5", effort: "medium", rationale: "統括の依頼書（iss-00664）の指定"}
		impl: {task: "実装（テストの2ファイル）", model: "claude-opus-5-5", effort: "medium", rationale: "変更が小さく調査と一体のため、方針と同じセッションの例外を使う（依頼書が許す）"}
	}
	reviews: code: {role: "最終品質ゲートのレビュー", after: "S-03", model: "opus", effort: "medium"}
}
