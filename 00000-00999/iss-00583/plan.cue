package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の入れ子の配置で、塊を先に置いて空きに1つの Scope を詰め、最上位も見える幅で折り返す（views/graph/layout.js とテスト）"

steps: {
	"S-01": {title: "塊と空きの詰め込み、塊のない段の不変、背の高い1つ、広げ直しでの固定を確かめるテストを書き、直す前のコードで落ちることを確かめる（Red）", realizes: ["R-01", "R-03", "F-01", "F-02", "F-03"], status: "todo", session: "impl"}
	"S-02": {title: "childrenBlock を塊と1つに分け、packBlock（塊の棚、右の列、塊の下、残りの棚）と入れ物の形、置き場の固定を実装する（Green）", realizes: ["R-01", "R-03", "F-01", "F-02", "F-03"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "最上位の widestRoom と shelved を消し、見える幅で折り返す。iss-00575 のテストの期待を改め、見える幅に収まることを確かめるテストを足す", realizes: ["R-02", "R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "読み順など、塊を先に置く規則で変わるほかのテストの期待を直し、make lint と全体の pytest を通す", realizes: ["R-01", "R-03"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "spec-dock と housing-lifecycle の実データで 1440、1000、390 の写しと数字を、直す前と後で report.md に残す", realizes: ["R-04", "R-01", "R-02"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "epic-00313 に似せた合成の構造で、つながりのない5つが最初の塊の棚の縦の範囲の中の、塊の右か下にあり、Epic の枠が直す前より低い（幅 1440）", verifies: ["R-01"]}
	"T-02": {title: "同じ構造の幅 1000・1440・1920 で、gaps のない layout と routeLayout が採った回の layout の両方で、兄弟の四角が重ならず、どの棚も見える幅の中にある（1つで超える塊を除く）", verifies: ["R-01", "F-01"]}
	"T-03": {title: "背の高い1つの枠は、塊の棚の下の棚に置かれ、塊の棚の高さは塊だけで決まる", verifies: ["F-01"]}
	"T-04": {title: "塊のない段（wide の構造）の座標が直す前と同じ（今の test_groups_without_dependencies_wrap_at_the_width_seen が通る）", verifies: ["F-02"]}
	"T-05": {title: "1つの Scope どうしは、同じ置き場の中で活動順に並ぶ", verifies: ["F-03"]}
	"T-06": {title: "合成の4つの Initiative で、1400×760 と 1920×1080 の、2つ以上が並ぶ行が見える幅に収まり、高さありと高さなしの行が同じ", verifies: ["R-02"]}
	"T-07": {title: "edgeAudit の違反0（代表の構造と合成の構造のすべての表し方、高さあり、幅 1000・1440・1920）、gaps ありで置き場が同じ、幅374・高さ800で Initiative が縦積み、250件が1秒の中", verifies: ["R-03"]}
	"T-08": {title: "実データ（spec-dock、housing-lifecycle）の写しと数字が、直す前と後で report.md にある", verifies: ["R-04"]}
}

verification: """
	節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py`。最後に `make lint`、`uv run pytest`（全体）。
	実データ：`.workbench/iss-00583/state` に写した状態の置き場（この PC の構造のスナップショット）を、`uv run spec-dock dashboard serve --port 18583 --offline --state-root <絶対の道>`
	で配り、headless Chrome（`--disable-features=MacAppCodeSignClone`、`Browser.close` で閉じる）で 1440×900、1000×800、390×844 を写す（`.workbench/iss-00583/shoot.mjs`）。
	node の測り（`.workbench/iss-00583/probe.mjs`）で、全体の幅と見える幅を比べる。
	"""

rollback: "PR を戻す（layout.js とテストだけの変更）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の写しと数字がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": {after: "S-02", range: "開始のコミット 982932e47 から S-02 の終わりまで", reviewer: "code-reviewer opus / medium", reason: "詰め込みの規則と入れ物の形（配線の広げ直しとのつながり）が要。最上位の変更とテストの期待の更新の前に、ここで誤りを止める"}
	}
	final_quality_gate: {
		scope:          "開始のコミット 982932e47 から S-04 の終わりまで（S-05 は記録だけ）"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:            "owner"
	merge_note:       "この Issue では、本人が統括にマージを委任した（2026-11-13、統括の連絡 msg_e2967864b02f）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		impl:  {task: "実装（S-01〜S-04）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。layout.js は DOM のない純粋な計算で、node のテストで確かめられる。本人の指示（2026-11-13）で Sol を優先し、詰め込みの規則も Sol で始める。Sol で失敗や見落としが記録されたときだけ、方針 §1 の4で GPT-6 Astra / high に上げる"}
		owner: {task: "実データの写し（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。ブラウザーでの確かめは実装ではなく、受け入れの証拠の取得。画面の HTML・CSS は変えないので Claude の実装担当は起動しない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー（CP-1）", after: "S-02", model: "opus", effort: "medium"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
