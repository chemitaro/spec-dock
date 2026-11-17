package spec

// 計画（Issue）。型 specdock/v1。

goal: "作業中の Epic・Initiative の枠に worktree の印を出し、どこの稼働の印を押しても押したエージェントのチャットを開き、ボードの札の稼働の印を専用の行に置く"

steps: {
	"S-01": {title: "T-01〜T-03 を tests/unit/infra/test_dashboard_orca_marks_js.py と tests/unit/infra/test_dashboard_orca_views_js.py に先に書いて落ちることを確かめ、D-01（orca_marks.js の記録と markAgentAt）と D-02（panel.js の openAgent）を入れて通す。今の orca の node のテストを通す", realizes: ["R-02", "R-03", "R-04", "F-01", "F-02"], status: "todo", session: "impl-sol"}
	"S-02": {title: "T-04〜T-06 を先に書いて落ちることを確かめ、D-03（graph.js・allgraph.js・board.js・panel.js の押し）、D-04（draw.js の枠の worktree の印と、要れば graph.css）、D-05（parts.js の札の専用の行と parts.css）を入れて通す", realizes: ["R-01", "R-02", "R-05"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（構造の図の golden や静的な検査が変われば、変わった理由が R-01・R-05 の HTML の足しか、R-02 の押しの置き換え（今の `preferTab(\"agents\")` の呼びを固定した検査）だけであることを確かめて直す。static-inventory.json の dashboard の sha256 が要れば直す）", realizes: ["R-01", "R-02", "R-05"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-06 の実機の確かめ（統括が用意する試しの送り先で、T-07 の写しと数え）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする", realizes: ["R-01", "R-02", "R-03", "R-05"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "markAgentAt（偽の DOM）：data-agent-id のある印でその値、ない3つの印でそれぞれ記録の同じ番目、印の子の要素を押しても同じ、+N（--more）・置き場の外・記録なし・数が違う・記録の id が null で null。markIds が記録の写しを返し、記録がなければ null", verifies: ["R-04", "F-01"]}
	"T-02": {title: "paintOrcaMarks の記録：buildMarks の marks[].id の順を記録し（並べ替えない）、同じ key では記録を残し、エージェントが変われば新しい並び、key が空なら空の並び、例外で空にしたら記録なし（markAgentAt が null）", verifies: ["R-03", "R-04", "F-02"]}
	"T-03": {title: "openAgent（run_panel）：別のエージェントを選んでいた欄で openAgent(id) を呼ぶと、エージェントのタブが選ばれ、欄の agent が id になり、その id の枠が描かれる。openAgent(null) は preferTab(\"agents\") と同じで選びを変えない。Scope を変える show の後に呼んだ選びが残る", verifies: ["R-02", "F-01"]}
	"T-04": {title: "枠の HTML：doing で branch のある Epic・Initiative の frameHtml の .gx-fh と、木の表示の枠の boxHtml の .gx-marks に title「worktree：<branch>」の .wt が1つ、.gx-agents の外。doing でない・branch が null なら今と同じ HTML。見出しの aria-label が今と同じ", verifies: ["R-01"]}
	"T-05": {title: "札の HTML と CSS：card(scope, ctx, {orca: true}) の置き場が .sd-card__meta の外の .sd-card__agents の中、card(scope, ctx) が今と同じ。parts.css に .sd-card__agents の :not(:has(.orca-mark)) の display: none", verifies: ["R-05"]}
	"T-06": {title: "画面の押しの静的な検査：graph.js・allgraph.js・board.js・panel.js の印の押しが select の後に openAgent(markAgentAt(...)) を呼び、印の押しで preferTab(\"agents\") を直接呼ばない。スマホの二度目の指の扱いが印の押しの後に残る", verifies: ["R-02"]}
	"T-07": {title: "実機（1440・390 × 明・暗）：作業中の Epic の枠の見出しの worktree の印と稼働の印（見出しの題名の行が1行）、同じ箱・枠に2人以上のときの2つ目の印の押しで、そのエージェントの枠（/embed/agent?id=）が開く（構造の図の箱・枠の見出し、ボードの札、横の欄の見出し、『横断の構造』）、+N の押しで選びが変わらない、ボードの札の専用の行と縁の内、エージェントのいない札の高さ、印の並びが要約の buildMarks と同じ（親子の組を置けるなら上流 → 下流が関係のないものの右）、edgeAudit の違反0、ブラウザーのエラー0", verifies: ["R-01", "R-02", "R-03", "R-05"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_agents_tab_js.py tests/unit/infra/test_dashboard_agents_logic_js.py`、
	S-02 の後は、それに `tests/unit/infra/test_dashboard_screens_js.py tests/unit/presentation/` を足す。最後に `make lint`、`uv run pytest`（全体）。実機は D-06。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと枠の worktree の印とボードの専用の行がなくなり、印を押したときは今どおり前の選びのエージェントが開く。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと数え、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット edfabc759 から S-03 の終わりまで（S-04 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "ui-behavior"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00621/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、orca_marks.js の記録と markAgentAt、panel.js の openAgent と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。対応の求め方と欄の選びは node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium。方針の実装担当の行）。chat-scratch の symlink の拒否で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、画面の押し、枠の worktree の印、札の専用の行、CSS、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書）"}
		owner:         {task: "実機の写しと数え（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機、統括が用意する試しの送り先が要る"}
	}
	// 仕様のレビューは S-01 の前に、開始のコミット edfabc759 で行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
