package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の稼働の印をすべて、ほかの印の下の専用の行に収める（折り返して箱を伸ばす）。『後に続く』は今のまま"

steps: {
	"S-01": {title: "tests/js/dashboard_graph_check.mjs に layout の options の marks を通す口を足し、test_dashboard_graph_marks_rows.py に T-01〜T-05 を書いて、直す前のコードで markRows・nodeMarkRows・高さのテストが落ち、印なしの一致（T-03）と既存の digest のテストが通ることを確かめる（Red）", realizes: ["R-04", "R-05"], status: "todo", session: "impl-sol"}
	"S-02": {title: "layout.js に D-01（MARK_ROW・MARK_INSET・markRows・nodeMarkRows。既存の rowsOf は変えない）と D-02（box・tbox・frame の高さ、flatten の rows）を入れ、S-01 のテストと構造の図の既存のテスト（graph_js・graph_range・graph_toolbar・small_screens）を通す（Green）", realizes: ["R-04", "R-05", "F-01"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "画面の静的・偽の DOM のテスト（T-06・T-07）を先に直して落ちることを確かめ、D-05（置き場の all・.gx-agents・CSS・edgeAudit の markOverflow）と D-03・D-04（measureMarks・checkRows・ResizeObserver・歯止め）を入れて通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-06", "R-07", "F-01", "F-02", "F-03"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "static-inventory.json の sha256 を直し（変われば）、make lint と全体の uv run pytest を通す", realizes: ["R-05", "R-07"], status: "todo", after: ["S-03"], session: "impl-claude"}
	"S-05": {title: "D-07 の実機の写し（エージェント1人・3人・6人の箱、iss-00613 の箱の前後、構造の図とボードの『後に続く』、1440・390 × 明暗）、edgeAudit の違反0・markOverflow 0・ブラウザーのエラー0を report.md に残し、試しの URL を立てる", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "markRows：m なし・items 空で 1、印が1つで 2、avail にちょうど入る並びで 2、1px 越える並びで 3、avail より広い印は1つで1行、gap を数える", verifies: ["R-04"]}
	"T-02": {title: "options.marks を渡した layout：稼働の印が1人（エージェントの行1つ）・3人（1つ）・6人（2つ、印 36px・間 2px・中の幅 152px で4つと2つ）の箱の高さが 108・108・128（入れ子・木）、エージェントの行が1つの入れ子の枠の見出しが MARK_ROW 高く中身が下がる、幅は変わらない、印のない node には rows の鍵がない", verifies: ["R-05"]}
	"T-03": {title: "marks なし・{}・全部1行の marks の layout が、marks なしの今の layout と同じ JSON。iss-00603 の digest の比較（test_all_and_now_lay_out_as_the_two_old_combinations）がそのまま通る", verifies: ["R-05", "F-01"]}
	"T-04": {title: "稼働の印が1人・3人・6人の箱と2行の枠を含む小さな構造と context の構造で、入れ子・木 × 全体・いま・これから・focus の routeLayout の audit の違反0", verifies: ["R-05"]}
	"T-05": {title: "layout の box・tframe・frame の node ごとに、nodeMarkRows(node, marks[id]) が node.rows ?? 1 と一致する", verifies: ["R-04", "R-06"]}
	"T-06": {title: "画面の静的な検査：boxHtml・frameHtml の dnMark と aria-label の「後に続く」と renderLegend の「後に続く数」が今のまま。置き場が orcaSlot(s.id, \"all\") で、.gx-marks・.gx-fh の中になく、その下の .gx-agents にある。ボードの card は downMark と orcaSlot(scope.id, 4) のまま。paintOrca の後と ResizeObserver から checkRows を呼び、checkRows は nodeMarkRows で比べて違うときだけ render し、V.rowsRedo が2のときは render しない（checkRows からの render と ResizeObserver では0に戻さない）", verifies: ["R-01", "R-02", "R-03", "R-06"]}
	"T-07": {title: "偽の DOM で paintOrcaMarks：data-orca-max=\"all\" の置き場はエージェント6人に max 6 を渡し、4 の置き場は max 4 のまま。agents が配列でない worktree は max 1。parts.orcaSlot(id, \"all\") の HTML", verifies: ["R-03", "F-01"]}
	"T-08": {title: "実機：エージェント1人・3人・6人の箱と iss-00613 の箱（前後）の写し 1440・390 × 明暗、edgeAudit の違反0・markOverflow 0・ブラウザーのエラー0、『後に続く』が構造の図とボードに残る、経過の文字だけの要約で箱が作り直されない（要素の同一性）、エージェントが1人の箱でも稼働の印がエージェントの行にあり、ほかの印の行に混ざらない、エージェントのいない箱の高さが今のまま", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "F-02", "F-03"]}
}

verification: """
	節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_marks_rows.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_orca_marks_js.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-07。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": "なし（S-02 の後は、タスク担当がテストの合格を確かめてから S-03 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット d9bb6164d から S-04 の終わりまで（S-05 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "ui-behavior"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00620/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01〜S-02、layout.js とその node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。行の数と高さは DOM のない純粋な計算で node のテストで確かめられる（方針の「テストで確かめられる実装」× standard）。本人の指示で Sol を使う。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-03〜S-04、画面・CSS・測ってやり直す仕組み）", model: "opus", effort: "medium", rationale: "claude。画面は実機の DOM と見た目の判断を含む（依頼書の指定：画面は Claude Opus 5.5 / medium）"}
		owner:         {task: "実機の写しと試しの URL（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
