package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図と『横断の構造』の帯を Unscoped の行にし、主のチェックアウトと紐づかない worktree を git の一覧から並べ、見方ごとに出し分ける"

steps: {
	"S-01": {title: "T-01 を tests/unit/application/test_dashboard_structure_facts.py と構造の API のテストに先に書いて落ちることを確かめ、D-01（worktree_items・StructureFacts.items・dashboard_http の items）を入れて通す", realizes: ["R-01", "F-03"], status: "todo", session: "impl-sol"}
	"S-02": {title: "T-02・T-03 を tests/js/dashboard_graph_unscoped.mjs（新）・tests/unit/presentation/test_dashboard_graph_unscoped.py（新）と今の dashboard_graph_command.mjs・dashboard_allgraph_command.mjs に先に書いて落ちることを確かめ、D-02（views/graph/unscoped.js）・D-03（command.js の bandLabel・itemWidth）・D-04（allgraph/command.js の crossPlace・bandShape・crossModel）を入れて通す。今のテストの期待は、札「main のチェックアウト」の変更と、幅の印・数の足しの分だけ直す", realizes: ["R-02", "R-03", "R-04", "R-06", "R-07", "R-09", "F-01", "F-02", "F-04"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "T-04 を先に書いて落ちることを確かめ、D-05（graph.js）・D-06（allgraph.js）・D-07（command_view.js・orca_marks.js）・D-08（graph.css）を入れて通す。今の画面のテスト・golden の期待は、行がいつも出ること・札の変更・『これから』の線がなくなることの分だけ直し、理由を report.md に書く", realizes: ["R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "make lint と全体の uv run pytest を通す（static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-08"], status: "todo", after: ["S-03"], session: "impl-claude"}
	"S-05": {title: "D-09 の実機の確かめ（T-05）と重さの比べを report.md に残し、移行の案内の文を書き、本人が見る試しの URL を立てたままにする。写しで直しが要れば実装担当に返す", realizes: ["R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "サーバー（pytest）：worktree_items が main・linked・detached（branch None・head）・locked・bare・prunable・仕様の置き場（catalog と同じパス、末尾の / の違いも）を含む行から、bare・prunable・置き場を除き、git の順で main を最初の行だけ真にする、最初の行が bare なら main がない、read_structure_facts が lister を1回だけ呼び items を作る、読めないとき items が空で status が unreadable、構造の API の JSON の worktrees に status・paths（今のまま）・items がある", verifies: ["R-01", "F-03"]}
	"T-02": {title: "行の項目（node）：Primary がいつも先頭（エージェントなし・要約なし・組なしでも）、Scope に紐づく行は出ない、Unlinked に同じパスの要約の worktree の全部のエージェントが orderOf の並びで重なる、末尾の / の違いと同じパスの2つ（最初）、線の端の重ね（当たる項目に足す・当たらなければ印なしの今の項目）、items のない構造で今の bandItems と同じ項目に main の Primary、要約がないとき git だけ、idle の Unlinked が1つなら薄く・2つ以上で +N（folded の中身）、childCount と count（子の重複を数えない、0 は null、項目ごとの合計、countParts と countTitle の内訳）、1つの worktree の全部のエージェント（線の端でないものも）が1つの項目に orderOf の並びで入る、range next で Primary と count のある Unlinked だけ、並び、key が線の端の bandKeys と同じ、commanding、detached の札", verifies: ["R-02", "R-03", "R-04", "R-06", "R-09", "F-01", "F-02", "F-03", "F-04"]}
	"T-03": {title: "帯の模型と横断（node）：itemWidth が印と数の分だけ広がる、5つ以上のエージェントで折り返し（列は4まで、項目の高さ、slot の位置、行の高さが最大の項目、bandRowHeight）、折り返した印の線の端が項目の上の縁で slot の中心の x、同じ項目の親子の弧、bandShape の h が高さに合う、fold の幅、bandLabel の main がブランチ名、組が0でも rows があれば commandModel が band を返す、crossPlace が各リポジトリの行を unscopedItems で作る・pairs が0でも行を返す・next で pairs と places が空、keep が next で commanding・全体いまで今どおり、bandShape の幅に Unscoped の頭の文字、crossModel の行の lead", verifies: ["R-02", "R-04", "R-06", "R-07", "R-09"]}
	"T-04": {title: "画面（偽の DOM と偽の orca）：構造の図と『横断の構造』で、組も要約もないとき行と Primary が出る、Unlinked と薄い項目と +N、項目の押しで詳細の欄（ブランチ・パス・エージェント・『Orca で開く』の script、埋め込みや orca なしで出ない）、+N の押しで一覧、もう一度・閉じる・Esc で閉じる、エージェントの印の押しで今と同じチャットと aria-pressed、『これから』で .gx-cmd に線がなく数の札が出る（title・aria-label の英語）、全体・いまで線が今と同じ、折り返した項目のボタンが模型の位置にある、同じ入力で描き直さない、印の title・aria-label、CSS の静的な検査（.gx-band-badge・.gx-band-count・.is-idle・色は変数だけ）", verifies: ["R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-09"]}
	"T-05": {title: "実機（D-09）：spec-dock の構造の図と『横断の構造』の 1440・390 × 明・暗で (a) 統括が誰も指揮していないとき main が Primary、(b) work start していない worktree のエージェントが Unlinked、(c) エージェントのいない古い worktree が薄く +N に畳まれる、(d) 『これから』で指揮している worktree だけが数つき、(e) 1つの worktree に複数のエージェント（指揮の親子を含む）がいると1つの項目に並び、親子が弧で結ばれる（試しのエージェントは統括に頼む）、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0、ブラウザーのエラー0、横のスクロールなし、iss-00646 の台本の数が開始のコミットと比べて悪くならない", verifies: ["R-02", "R-03", "R-04", "R-06", "R-07", "R-08", "R-09"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/application/test_dashboard_structure_facts.py` と構造の API のテスト、
	S-02 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_unscoped.py tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_allgraph_command.py tests/unit/presentation/test_dashboard_allgraph_compose.py`、
	S-03 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/ -k "dashboard"`。最後に `make lint`、`uv run pytest`（全体）。実機は D-09。
	"""

rollback: "PR を戻す（ダッシュボードの静的な資産、構造の API の items、テスト）。戻すと帯は今の指揮の帯に戻る。API の items を読むのはこの画面だけで、保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと数え、移行の案内の文、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-02 の後に、タスク担当が S-01・S-02 の節目のテストの合格を確かめてから S-03 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-04 の終わりまで（S-05 は記録。写しで直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00668/", "spec-dock/initiatives/00000-00999/epic-00667/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01〜S-02、サーバーの items と、行の項目・帯の模型・横断の純粋な計算と、pytest・node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。テストで確かめられる計算とサーバー（依頼書：Codex GPT-6.1 Sol / medium。方針の表は GPT-6.2 Sol だが依頼書の指定を優先）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、impl-claude が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-03〜S-04、両方の画面の描画と押し、詳細の欄、CSS、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書、方針のフロントエンドの行）"}
		owner:         {task: "実機の写しと数え、重さの比べ、移行の案内（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機、統括が用意する試しのエージェントが要る"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high、standard なので2人目なし）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
