package spec

// 計画（Issue）。型 specdock/v1。

goal: "線の多い Epic の構造の図で、列の間の極端に広い隙間をなくす（router.js の広げの見積もりの修正）"

steps: {
	"S-01": {title: "再現と原因の確かめ（node で taikyohiyou の構造を配置し、回ごとの広げを数える）", realizes: ["R-01"], status: "done", session: "impl"}
	"S-02": {title: "列の間を測る検査と、線の多い合成の構造のテストを書き、修正の前に落ちることを確かめる", realizes: ["R-01", "R-02"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "広げの要求を通り道ごとに見積もる", realizes: ["R-01", "R-02", "F-01"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "動かない線分と動く線分の前後を、入る余地で決める", realizes: ["R-03", "F-02"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "線の検査と速さのテストを、合成の構造を加えて通す", realizes: ["R-03", "R-04"], status: "todo", after: ["S-04"], session: "impl"}
	"S-06": {title: "実データ（taikyohiyou_project と spec-dock）の 1440、1000、390 の写しと数字を、直す前と後で report.md に残す", realizes: ["R-01"], status: "todo", after: ["S-05"], session: "impl"}
}

tests: {
	"T-01": {title: "線の多い合成の構造の、すべての表し方で、列の間が上限 max(44, 8n + 12) + 32 以下である（修正の前は落ちる）", verifies: ["R-01", "R-02"]}
	"T-02": {title: "代表の構造と合成の構造のすべての組み合わせで、線の検査の違反が0である（動かない線分の押されが残らない）", verifies: ["R-03", "F-02"]}
	"T-03": {title: "250件の生成の構造の配線が、どれも1000ms 未満である", verifies: ["R-04"]}
}

verification: """
	`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py`、`make lint`、`uv run pytest`（全体）。
	実データは、`.workbench/iss-00578/` に写した構造の文書を、`spec-dock dashboard serve --port 18578 --offline` と
	headless Chrome で 1440、1000、390 の幅で写し、node の測りで列の間の幅を数える。
	"""

rollback: "PR を戻す（router.js とテストだけの変更）。"

exit: "PR がマージできる状態で、CI が通り、report.md に直す前と後の数字と写しがある。"

execution: {
	sessions: {
		spec: {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "high", rationale: "統括が policy の bug-fix で選んだ（原因の分からない配置の不具合の診断と修正）"}
		impl: {task: "実装", model: "opus", effort: "high", rationale: "同じセッションで実装する（統括の指定）"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "medium"}
		code: {role: "コードのレビュー", after: "S-05", model: "sonnet", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "high"}
	}
}
