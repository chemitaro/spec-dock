package spec

// 計画（Issue）。型 specdock/v1。

goal: "『横断の構造』に、リポジトリをまたぐ指揮の線、枠ごとの帯、全体の帯『ほかの場所』、帯だけの入れ物の枠を出し、両方の画面で指揮の線を枠の見出しの文字の下に通す"

steps: {
	"S-01": {title: "T-01〜T-03 を tests/js/dashboard_allgraph_command.mjs（新）・test_dashboard_allgraph_command.py（新）と今の dashboard_allgraph_compose.mjs に先に書いて落ちることを確かめ、D-01（graph/command.js の bandKeys・placer・bandRowWidth・commandModel の rows と boundsOf）、D-02（allgraph/command.js の repoOfWorktrees・crossPlace・bandShape・crossModel・crossKey）、D-03（compose.js の REPO の足し、bands の {h, w}・keep・other、anchorShift）を入れて通す。今の test_dashboard_graph_command.py・test_dashboard_graph_js.py をそのまま通し、test_dashboard_allgraph_compose.py は REPO の完全一致の期待を足したキーを含めて直すほかはそのまま通す", realizes: ["R-01", "R-02", "R-03", "R-05", "F-02", "F-03", "F-04"], status: "todo", session: "impl-sol"}
	"S-02": {title: "T-04・T-05 を先に書いて落ちることを確かめ、D-04（graph/command_view.js に描画を移し、graph.js の出力を変えない）、D-05（allgraph.js の paintCommand・帯の形のやり直しと補い・指揮の選び・帯のチャット・凡例・specdockCmdAudit と、graph.js の cmdAudit の heads）、D-06（graph.css・allgraph.css の見出しの規則と下地、gx-band-lead）を入れて通す。test_dashboard_graph_command_screen.py の枠の z-index の期待は D-06 に合わせて直す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "F-01", "F-05"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（構造の図・『横断の構造』の golden や静的な検査が変われば、変わった理由が D-06 の CSS か D-01・D-04 の口だけであることを確かめて直す。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-04", "R-06", "R-07"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-07 の実機の確かめ（T-06）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。写しで見た目の直しが要れば、実装担当に返す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-06", "R-07"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "対応と居場所と帯の形（node）：パスの当たりが project の当たりより先、一覧の順の最初、unknown（構造なし・worktrees.status が ok でない）、2つのリポジトリをまたぐ組（親は親のリポジトリの帯、子は子のリポジトリの箱の印）、グラフのない枠のリポジトリの端は帯、当たらない worktree は『ほかの場所』（札 <project.name> · <branch>、ほかのリポジトリ · <branch>）、unknown のとき当たらない端の組を落とす、両端とも『ほかの場所』・同じ帯の組を残す、見えないリポジトリの帯に親がいれば keep・子だけなら『ほかの場所』へ、keep した子の枠のために出る親のリポジトリの帯の子の端はその帯に残る、別のリポジトリの同じ id の枠の端を同じ縁のずらしの組にしない、bandShape の高さ・幅・鍵（同じ形で同じ鍵）", verifies: ["R-01", "R-02", "R-03", "F-02", "F-04"]}
	"T-02": {title: "compose の口と補い（node）：bands・keep・other を渡さないとき今の結果と同じ（other: null だけ足す）、帯の高さで本文が下がる、帯の幅で枠が広がる、keep で『これから』の空の枠が見出しと帯だけで出る（その親も出る）、keep を外すと出ない、other ですべての枠が下がり width が広がる、anchorShift が見えている上の端のいちばん上のグラフの枠の原点の差を返す（重なるものがない・next にないで 0）、補いの後の画面の位置が変わらない", verifies: ["R-02", "R-03", "R-05"]}
	"T-03": {title: "世界の座標の模型（node）：rows を渡さない commandModel が今の結果と同じ（iss-00616 の T-03 がそのまま通る）、placer で placeAgents が今と同じ、2つの行の帯の項目の位置（lead の幅の後）と端の y、リポジトリをまたぐ線の始まりと終わりが本文の原点＋配置の座標、同じ箱の弧の spotsOf のずらし、boundsOf で本文の下の余白が弧の d を決める、帯の項目の上の弧が行の top から、合成の入力の boxOverlaps・edgeOverlaps が 0、F-03 の端、crossKey が同じ入力で同じ", verifies: ["R-01", "R-04", "R-07", "F-03"]}
	"T-04": {title: "CSS の静的な検査：graph.css の .gx-world > .gx-frame の z-index auto、--gx-fbg の3つ（今の背景の値の写し）、見出しの行と要約の行の position: relative と z-index 2、見出しの子（.gx-agents を除く）と要約の子の下地、自分の地の色を持つ札の2層の背景、allgraph.css の .ax-body > .gx-frame の z-index auto・.ax-head の z-index 2 と子の下地（深さ1・3は surface-2）、allgraph.css に色の値と独自の変数がない、.gx-band-lead の規則、指揮の規則に <animate・animateMotion・canvas・blur( がない、指揮の層・端の層・帯・箱・依存の線の z-index が今のまま", verifies: ["R-06"]}
	"T-05": {title: "画面（偽の DOM と偽の orca）：組がないとき『横断の構造』の世界の HTML が今と同じで層と帯がない、組があるとき層が1つずつ、帯のあるリポジトリの枠の高さが REPO.band 増え本文が下がる、入れ物の枠の出入り（親がいる・消える）、『ほかの場所』の行の頭の文字、要約だけの更新で routeLayout の呼び数が増えない、同じ形の2回目で compose をやり直さず .gx-cmd の要素が同じ、帯の形の変化で A.moved のとき見えている枠の原点の画面の位置が同じ、F-05 の2回の上限と入力が変わったときの数えの戻り、上限に届いたときに行のない帯の組を描かない、帯の押しで /embed/agent?id= の iframe と aria-pressed とその線の is-cmd-hl、もう一度・閉じる・Esc で解ける、箱の印の押しで select と openAgent と cmdSel、凡例の行、specdockCmdAudit の形と heads、構造の図の出力が今と同じ（今のテストがそのまま通る）", verifies: ["R-02", "R-03", "R-04", "R-05", "R-07", "F-01", "F-05"]}
	"T-06": {title: "実機（D-07）：『横断の構造』の 1440・390 × 明・暗 × 全体・いま・これから の写し、枠ごとの帯（main のチェックアウトの統括）と線、リポジトリをまたぐ線、帯だけの入れ物の枠と『ほかの場所』（要れば統括の試しのエージェント）、帯の押しのチャット、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0・spotDrift ≤ 1、ブラウザーのエラー0、横のスクロールなし、両方の画面の見出しの上を線が通る所の前後の拡大", verifies: ["R-01", "R-02", "R-03", "R-04", "R-06", "R-07"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_allgraph_command.py tests/unit/presentation/test_dashboard_allgraph_compose.py tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_marks_rows.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`。最後に `make lint`、`uv run pytest`（全体）。実機は D-07。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと『横断の構造』の線と帯がなくなり、両方の画面で見出しの重なりの順が今に戻る。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の写しと数え、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-03 の終わりまで（S-04 は記録。写しで直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00617/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、graph/command.js の口、allgraph/command.js、compose.js の純粋な計算と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で、node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium。方針の実装担当の行）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium（impl-claude）が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、共有の描画の部品、allgraph.js の描画と選び、両方の画面の CSS、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書、方針のフロントエンドの行）"}
		owner:         {task: "実機の写しと数え（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。この PC の状態の置き場と実機、統括が用意する試しの送り先が要る"}
	}
	// 仕様のレビューは S-01 の前に、開始のコミットで行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
