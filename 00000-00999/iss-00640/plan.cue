package spec

// 計画（Issue）。型 specdock/v1。

goal: "1000 前後の幅で、上の帯の道具の列が、状態の札の次の行の右寄せに決まって並ぶようにする"

steps: {
	"S-01": {title: "T-01・T-02 を tests/js/dashboard_allgraph_screen.mjs と tests/unit/presentation/test_dashboard_allgraph_screen.py に先に書いて落ちることを確かめ（T-02 は検査の写しの変更だけで既に通ることを確かめる）、D-01（allgraph.css）を入れて通す", realizes: ["R-01", "R-03", "F-01"], status: "todo", session: "owner"}
	"S-02": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に dashboard の資産があれば sha256 を直す）", realizes: ["R-01", "R-03"], status: "todo", after: ["S-01"], session: "owner"}
	"S-03": {title: "D-04 の実機の確かめ（帯の寸法、欄を開いた形とまとめなしの形、写し、24組の edgeAudit）を report.md に残し、試しの URL を立てる", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01"], status: "todo", after: ["S-02"], session: "owner"}
}

tests: {
	"T-01": {title: "静的な検査：allgraph.css の `@container app not (max-width: 640px)` の中に `.gx[data-screen=\"allgraph\"] .gx-left { display: contents }` と `.ax-sum { order: 1; flex-basis: 100% }` があり、境目の 640 が allgraph.js の PHONE と graph.css のスマホの規則と同じ。graph.css の `.gx-bar`・`.gx-tools`・スマホの帯の規則が今のまま", verifies: ["R-01", "R-02", "R-04"]}
	"T-02": {title: "画面の node の検査（styled）：札・道具・まとめの行の下端を別々の値（道具 > まとめ、まとめ > 道具、まとめなし）にしたとき、最初の表示の ty と『収める』の上端が最大の下端 + 8", verifies: ["R-03", "F-01"]}
	"T-03": {title: "実機：1000・1280・1440・390 × 横断の構造・構造の図の帯の矩形（R-01・R-02 の位置、390 は直す前と同じ）、最初の表示の ty、写し。欄を開いた 1440 とまとめなしの 1000・1440 の帯（F-01）。横断の構造の24組で edgeAudit の total の違反0と横のスクロールなし", verifies: ["R-01", "R-02", "R-03", "R-04", "F-01"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_allgraph_screen.py tests/unit/presentation/test_dashboard_graph_toolbar.py tests/unit/presentation/test_dashboard_graph_fit.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-04。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の表と写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（変更が CSS の数行とテストなので、レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 0ef2dfeae から S-02 の終わりまで（S-03 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "compatibility-regression"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00640/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		owner: {task: "実装と実機の確かめ（S-01〜S-03）", model: "opus", effort: "medium", rationale: "変更は画面の CSS（依頼書：画面は Claude Opus 5.5 / medium）。テストで確かめられる計算の変更はない（barBottom は変えず、検査の写しを足すだけ）ので Codex の実装担当は起こさない。タスク担当のこのセッションが同じ値なので別のセッションを起こさない"}
	}
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-02", model: "opus", effort: "medium"}
	}
}
