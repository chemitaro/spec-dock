package spec

// 計画（Issue）。型 specdock/v1。

goal: "『これから』でも両方の画面で指揮の線・弧・行・帯を『いま』と同じ規則で出し、子の数の札をやめる"

steps: {
	"S-01": {title: "T-01・T-02 を先に書いて今の実装で落ちることを確かめ、D-02（allgraph/command.js の crossPlace）・D-03（unscoped.js・command.js・command_view.js・graph.css の子の数）を入れて通す。iss-00668 の『これから』の node のテストの期待をこの決定に合わせて直し、直したテストの名前を控える", realizes: ["R-01", "R-02", "R-03", "F-01", "F-02"], status: "done", session: "impl"}
	"S-02": {title: "T-03 を先に書いて落ちることを確かめ、D-01（graph.js の paintCommand）と allgraph.js の crossPlace・unscopedItems の呼び方を直して通す。iss-00668・iss-00617 の『これから』の画面のテストの期待を直し、直したテストの名前を控える", realizes: ["R-01", "R-02", "R-03", "R-04"], status: "done", after: ["S-01"], session: "impl"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に載る資産の sha256 が変われば直す）。直したテストの一覧を report.md に書く", realizes: ["R-04"], status: "done", after: ["S-02"], session: "impl"}
	"S-04": {title: "D-05 の実機の確かめ（T-04）を report.md に残し、移行の案内の文を書く。写しで直しが要れば実装担当に返す", realizes: ["R-01", "R-02", "R-03", "R-04"], status: "done", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "横断の居場所（node、tests/js/dashboard_allgraph_command.mjs と pytest の包み）：実データの形の合成の入力（3つのリポジトリ、main の統括 → 別のリポジトリの worktree の子、同じ worktree の親子、Unscoped の行）で、range next・now・all のどれでも crossPlace の pairs が全部残り、places が帯・印・枠に決まる。next で Scope のないリポジトリは帯に組の親の端があるとき keep され、子だけなら keep されず子の端が『ほかの場所』にある。『ほかの場所』の行が next でも作られる。crossModel の links・arcs が next でも 0 より多い。F-02 の unknown のときの見送りは今のまま", verifies: ["R-01", "R-03", "R-04", "F-02"]}
	"T-02": {title: "行の項目（node、tests/js/dashboard_graph_unscoped.mjs と pytest の包み）：unscopedItems に range がなく、どの項目にも count・countParts がなく、指揮していない Unlinked・薄い項目・+N・線の端の印なしの項目が出る。itemWidth に数の足しがない。組も要約もないとき行だけ（F-01）", verifies: ["R-02", "F-01"]}
	"T-03": {title: "画面（偽の DOM と偽の orca）：構造の図と『横断の構造』の『これから』で .gx-cmd に線があり、同じ組の入力で specdockCmdAudit の links・arcs・motion・heads が『いま』と同じ（『これから』で隠れた Scope の worktree の子は祖先の枠の縁に落ち、その分は本数で確かめる）。動きを減らす設定で止まった表示。.gx-band-count がどの範囲にもない。CSS の静的な検査で .gx-band-count の規則がない。全体・いまの今のテストはそのまま通る", verifies: ["R-01", "R-02", "R-03", "R-04"]}
	"T-04": {title: "実機（D-05）：/graph と /r/github.com/chemitaro/spec-dock/ の『これから』『いま』『全体』の specdockCmdAudit（links・arcs・boxOverlaps・edgeOverlaps・heads・motion）と specdockEdgeAudit、ブラウザーのエラー0、横のスクロールなし。1440・390 × 明・暗の写しで、/graph の既定の『これから』に線が出ている", verifies: ["R-01", "R-02", "R-03", "R-04"]}
}

verification: """
	S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_allgraph_command.py tests/unit/presentation/test_dashboard_graph_unscoped.py tests/unit/presentation/test_dashboard_graph_command.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/ -k dashboard`。最後に `make lint`、`uv run pytest`（全体）。実機は D-05。
	"""

rollback: "PR を戻す（ダッシュボードの静的な資産とテストだけ）。戻すと『これから』は線なし・子の数つきに戻る。保存・API は変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に診断・直したテストの一覧・実機の写しと数・移行の案内の文がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後に、タスク担当が S-01 の節目のテストの合格を確かめる。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-03 の終わりまで（S-04 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00676/"]
		second_opinion: "chatgpt-final-quality-gate-strict（依頼書：2人目は ChatGPT Use の系列を先に使う。取れなければ方針どおり quality-gate-reviewer の2人目）"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		impl:  {task: "実装（S-01〜S-03、画面の JS・CSS とテスト）", model: "claude-opus-5-5", effort: "medium", rationale: "claude。画面の JS と偽の DOM の画面のテストなので Claude Opus 5.5 / medium（依頼書の推し、方針のフロントエンドの行）"}
		owner: {task: "実機の写しと数え、移行の案内（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場の写しと常駐の orca-web の要約が要る"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
