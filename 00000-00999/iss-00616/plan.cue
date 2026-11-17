package spec

// 計画（Issue）。型 specdock/v1。

goal: "リポジトリの構造の図に、親の印から子の印への黄色の動く指揮の線、同じ箱の弧、親の端の波紋、すべての Initiative の上の『指揮の帯』を出し、印を押すと線が目立ち、帯のエージェントのチャットが開く"

steps: {
	"S-01": {title: "T-01〜T-03 を tests/js/dashboard_graph_command.mjs と tests/unit/presentation/test_dashboard_graph_command.py に先に書いて落ちることを確かめ、D-01（command.js の commandPairs・ownWorktrees・placeAgents・bandItems）、D-02（layout.js の packMarks・markSpots と定数。markRows は packMarks から）、D-03（commandModel・labelWidth・BAND・commandKey）を入れて通す。今の tests/unit/presentation/test_dashboard_graph_marks_rows.py・test_dashboard_graph_js.py・test_dashboard_graph_fit.py を通す", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-02", "F-03", "F-04"], status: "todo", session: "impl-sol"}
	"S-02": {title: "T-04・T-05 を先に書いて落ちることを確かめ、D-04（graph.js の paintCommand、層と帯、指揮の選び、帯の詳細の欄、初めの見え方と『収める』、specdockCmdAudit）、D-05（app.css の色の札、graph.css、draw.js の renderLegend の口、fake_dom.mjs の偽の orca の足し）、D-02 の CSS（箱の印の行を底に寄せる）を入れて通す", realizes: ["R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "F-01"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（構造の図・『横断の構造』の golden や静的な検査が変われば、変わった理由が D-02 の箱の CSS か D-05 の凡例の口だけであることを確かめて直す。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-02", "R-05"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-06 の実機の確かめ（T-06）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。写しで見た目の直しが要れば、実装担当に返す", realizes: ["R-02", "R-03", "R-04", "R-06", "R-07", "R-08"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "組と居場所と帯の項目（node）：Epic D-02 の合成の5組がそのまま得られる、parent なし・null・要約にいない・自分・文字列でない・object でない・輪で組なし（止まる）、両端ともほかのリポジトリの組を落とす、居場所の mark・frame（隠れた Issue のいちばん近い描かれた祖先）・group（畳んだ塊）・band、構造の worktree の一覧が読めない・要約が無効で null、帯の札（main のチェックアウト、ブランチ名、<project.name> · <branch>、ブランチ不明、ほかのリポジトリ · <branch>、main が null）と項目の並び、項目の中の並びが orderOf の部分の列", verifies: ["R-01", "R-02", "F-01", "F-02", "F-03"]}
	"T-02": {title: "印の位置（node）：packMarks が今の markRows の表と同じ行を出し markRows の結果が変わらない、箱の1行・2行・木の枠の箱・Epic と Initiative の入れ子の枠・縮めた Epic の題名2行（fit）の markSpots の矩形、ids がない・数が違う・行の数が node.rows と違うで null", verifies: ["R-03", "F-04"]}
	"T-03": {title: "端・曲線・弧・帯の寸法（node）：帯の項目の幅と位置（1つ・3つ、札の上限）、top と width、端と向き（箱の印は stubs と下の縁、枠の見出しの印は下、帯は下の縁、塊・枠の縁、枠が相手を含むときの内側の下の縁）、同じ縁のずらし、三次ベジェの制御点、同じ行・違う行・帯の項目の弧（弦 40px 以上、d の値、浅くする、向きを変える、crowded）、依存の線と平行で向きを変える、合成の入力の boxOverlaps と edgeOverlaps が 0、Epic の枠の見出しの統括 → 枠の中の Issue の子の線が枠の上の縁より上へ出ない、state（flow・wait・done）、ripples が親ごとに1つ、同じ塊・同じ祖先の枠で線なし、F-04 の端、commandKey が同じ入力で同じ", verifies: ["R-02", "R-03", "R-04", "R-08", "F-04"]}
	"T-04": {title: "CSS と HTML の静的な検査：app.css の3か所の --sd-cmd と --sd-cmd-glow、テストで計算した色相の差（10° 以上）とコントラスト（3:1 以上）、graph.css の層の z-index と pointer-events: none、点の流れの keyframes（stroke-dashoffset）、波紋（transform・opacity）、減らす設定の規則、.gx-box の flex と .gx-agents の margin-top: auto、<animate・animateMotion・canvas・blur( がない、renderLegend の既定の HTML が今と同じで cmd のときだけ「指揮（親 → 子）」の行", verifies: ["R-03", "R-04", "R-05"]}
	"T-05": {title: "画面（偽の DOM と偽の orca）：組がないとき世界の HTML が今と同じで層と帯がない、組があるとき層の順（枠 → .gx-cmd → 箱 → 塊 → .gx-cmd-top → 依存の線、帯）、要約だけの更新で routeLayout の呼び数が増えない、同じ入力の2回目で .gx-cmd の要素が同じ、帯のボタンの押し（onTap と Enter）で欄に /embed/agent?id= の iframe と aria-pressed、is-cmd-hl・is-cmd-off、もう一度・閉じる・Esc で解ける、そのエージェントが要約から消えると解けて欄が閉じる、箱の印の押しで cmdSel、凡例の行が orca が有効なときだけ、『収める』と初めの見え方が帯の top を含む、帯が出ても V.tx・V.ty・V.s が変わらない", verifies: ["R-02", "R-03", "R-05", "R-06", "R-07", "R-08", "F-01"]}
	"T-06": {title: "実機（D-06）：spec-dock の構造の図の 1440・1000・390 × 明・暗、全体・いま・これから の写し、帯（main のチェックアウトの統括）と線、同じ worktree の弧、点の流れと止まった線と薄い線、波紋、減らす設定、帯の押しのチャット、箱の印の押しの目立たせ、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps 0・spotDrift ≤ 1、ブラウザーのエラー0、横のスクロールなし、題名が1行の箱の印の行の前後", verifies: ["R-01", "R-02", "R-03", "R-04", "R-06", "R-07", "R-08"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_graph_marks_rows.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_fit.py`、
	S-02 の後は、それに `tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py` を足す。最後に `make lint`、`uv run pytest`（全体）。実機は D-06。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと線・帯・色の札・凡例の行がなくなり、箱の印の行は今の位置に戻る。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと数え、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット 3f5f8d8e9 から S-03 の終わりまで（S-04 は記録と、写しから返した直し）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00616/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、command.js と layout.js の純粋な計算と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で、node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium。方針の実装担当の行）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium（impl-claude）が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、画面の描画・選び・欄・CSS・凡例と全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書、方針のフロントエンドの行）"}
		owner:         {task: "実機の写しと数え（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機、統括が用意する試しの送り先が要る"}
	}
	// 仕様のレビューは S-01 の前に、開始のコミット 3f5f8d8e9 で行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
