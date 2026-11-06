package spec

goal: "時間のテスト 2 件を負荷に強くし、ダッシュボードの見た目 4 件を直す"

steps: {
	"S-01": {title: "グラフの時間のテストを CPU 時間の最小にする", realizes: ["R-01", "F-01"], status: "done", session: "impl"}
	"S-02": {title: "bootstrap の timeout のテストに余裕を持たせる", realizes: ["R-02"], status: "done", session: "impl"}
	"S-03": {title: "favicon を配り、ページから指す", realizes: ["R-03"], status: "done", session: "impl"}
	"S-04": {title: "Scope が 0 件の札に一言を出す", realizes: ["R-04"], status: "done", session: "impl"}
	"S-05": {title: "文書の目次の背景を最後までつなぐ", realizes: ["R-05"], status: "done", session: "impl"}
	"S-06": {title: "390px の帯の下の枠の線を隠す", realizes: ["R-06"], status: "done", session: "impl"}
}

tests: {
	"T-01": {title: "負荷（yes を CPU の 4 倍）の下でグラフの時間のテストが通る", verifies: ["R-01", "F-01"]}
	"T-02": {title: "負荷の下で bootstrap のテストが通る", verifies: ["R-02"]}
	"T-03": {title: "`/favicon.ico` が 200 の SVG で、シェルが icon を指す", verifies: ["R-03"]}
	"T-04": {title: "Scope が 0 件の札の文言が、概況の script にある", verifies: ["R-04"]}
	"T-05": {title: "文書の HTML に目次の背景の規則が入る", verifies: ["R-05"]}
	"T-06": {title: "狭い幅の規則が graph.css にある。写し（390px、明るい・暗い）で確かめる", verifies: ["R-06"]}
}

verification: "make lint、uv run pytest（全体）、負荷をかけた状態での 2 テスト、headless Chrome の前後の写し（PC 幅と 390px、明るい・暗い）を report.md に残す。"
exit: "PR がマージできる状態で、最終品質ゲートの合格が report.md にある。"

execution: {
	sessions: {
		spec: {task: "仕様化", model: "sonnet", effort: "medium", rationale: "統括の依頼（policy §4 light）"}
		impl: {task: "実装", model: "sonnet", effort: "medium", rationale: "統括の依頼（policy §4 light）"}
	}
	reviews: code: {role: "コードのレビュー", after: "S-06", model: "sonnet", effort: "high"}
}
