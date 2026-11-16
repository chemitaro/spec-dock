package spec

// 計画（Issue）。型 specdock/v1。

goal: "『横断の構造』で、リポジトリの枠の中の親の図と子の枠を見える幅で横に並べて折り返し、最初の表示を『幅に合わせる』にして、読める大きさで縦に読み進められるようにする"

steps: {
	"S-01": {title: "D-01・D-02 の node のテスト（T-01・T-02：同じ行に入る子と入らない子、行の幅、重なりなし、graph でない親、9つの入れ子、帯で子孫も下がる）を先に書いて落ちることを確かめ、compose.js を直して通す。今の check_no_overlap の『子は親の図の下』の確かめは、R-01 に合わせて『子は親の図の四角と重ならない』に替える", realizes: ["R-01", "R-02", "F-01"], status: "todo", session: "impl-sol"}
	"S-02": {title: "D-03 の偽の DOM のテスト（T-03：PC の最初の倍率と位置、狭い世界で 1、スマホで 0.74、拡大して範囲を変えても戻らない、『収める』のテストは変えずに通る）を先に書いて落ちることを確かめ、initialView を直して通す。make lint と全体の uv run pytest を通す", realizes: ["R-03"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "D-04 の実機の確かめ（T-04）：開始と候補の世界の寸法の比べ、最初の表示の倍率、写し、線の検査の比べを取り、report.md と artifacts に残し、本人が見る試しの URL を tailnet で立てる", realizes: ["R-01", "R-03", "R-04"], status: "todo", after: ["S-02"], session: "owner"}
}

tests: {
	"T-01": {title: "compose の並び（node）：合成で、親の図（graph、幅 a）と狭い子（幅 b、c）で a + gap + b ≤ bodyWidth なら子 b は図と同じ y で x = 図の右 + gap、入らない子は次の行（y = 行の下 + gap）。2つ以上が並ぶ行は bodyWidth の中。図が bodyWidth より広い親では子はすべて図の下の行（F-01）。graph でない親（all の empty・quiet・loading は1行の下に pad、next の高さ0は見出しの直後）。この PC の登録の形の9つで入れ子と外の2つと order が iss-00614 と同じ、子は親の中で親の図・兄弟と重ならない", verifies: ["R-01", "F-01"]}
	"T-02": {title: "compose の帯（node）：帯を渡さないときと全部0の出力が同じ。図の右に子が並ぶ親に h を渡すと、band の四角、body の y、子と孫のすべての y1・y2 が h 増え、枠の高さが h 増え、重なりがない", verifies: ["R-02"]}
	"T-03": {title: "allgraph の最初の表示（偽の DOM）：図の領域 1440 幅・世界がそれより広い構造で、最初の transform が scale = (1440 − 16) ÷ 世界の幅、translate x = 8、y = 道具の帯の下 + 8、世界の右端が図の領域の中。狭い世界で scale 1・x 8。画面が 640 以下で scale 0.74・x 4。拡大してから範囲を変えても scale が最初の値に戻らない。『収める』のテスト（test_fit_holds_…）が変えずに通る", verifies: ["R-03"]}
	"T-04": {title: "実機（この PC の9つの登録の写し）：node で開始と候補の世界の寸法と『収める』の倍率（1440・1000・390 × 3範囲）、Chrome で 1440・1000・390 × 明・暗 × 3範囲の写し、最初の表示の倍率と横のはみ出しなし（1440・1000）、ブラウザーのエラー0、横のスクロールなし、帯と見出しの重なり0、倍率 100% の edgeAudit をリポジトリごとに単体の構造の図と比べて新しい違反0", verifies: ["R-01", "R-03", "R-04"]}
}

verification: """
	節目：実装担当が各手順の後に `uv run pytest tests/unit/presentation/test_dashboard_allgraph_compose.py tests/unit/presentation/test_dashboard_allgraph_screen.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-04（T-04）。
	"""

rollback: "PR を戻す（dashboard の静的な資産2つとテストだけ）。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に測りと写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が T-01・T-02 の合格と HEAD を確かめてから impl-claude を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミットから S-02 の終わりまで（S-03 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00629/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、compose.js の並びと node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない純粋な計算で node のテストで確かめられる（方針の「テストで確かめられる実装」× standard、依頼書の指定で Sol）。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02、initialView と偽の DOM のテスト、全体の検証）", model: "opus", effort: "medium", rationale: "claude。画面の動きを含む（依頼書の指定：画面は Claude Opus 5.5 / medium）"}
		owner:         {task: "実機の確かめと試しの URL（S-03）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-02", model: "opus", effort: "medium"}
	}
}
