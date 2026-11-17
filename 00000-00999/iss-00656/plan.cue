package spec

// 計画（Issue）。型 specdock/v1。

goal: "Scope の欄の見出しを『パンくずと今の ID』『題名』『（足すときだけ）帯』にし、タブの名前を繰り返す帯をなくして、見出しの高さを直す前の 60% 以下にする"

steps: {
	"S-01": {title: "T-01 を tests/unit/infra/test_dashboard_panel_logic_js.py に先に書いて落ちることを確かめ、D-01（panel_logic.js の headerBand）を入れて通す。ほかのファイルは変えない", realizes: ["R-03", "R-04", "F-01"], status: "done", session: "impl-claude"}
	"S-02": {title: "T-02・T-03 を先に書いて（今の欄・タブ・詳しい画面・CSS のテストのうち、見出しとタブの行の形を固定している期待を、この設計に合わせて直すことを含む）落ちることを確かめ、D-02（panel.js の見出し）、D-03（SCOPE_TABS の open、frameBar、tabOpenLink、欄と詳しい画面のタブの行）、D-07（headOverflows と fitHead）、D-08（hide() で段を保つ。T-05 を先に書く）、D-04（panel.css・scope_tabs.css・scope.css）を入れて通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-08", "R-09", "F-01", "F-02"], status: "done", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（直したテストの期待が、見出しとタブの行の形の変化だけによることを確かめる。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-08"], status: "done", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-06 の測りと実機の確かめ（T-04）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。受入の数に届かないか、写しで崩れがあれば、実装担当に返す", realizes: ["R-01", "R-06", "R-07"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "headerBand の純粋な計算（node）：理由の符号 in_progress・closed・no_waits と、文が空・状態の名前と同じ・前後の空白だけ違う・reason がないときは reason が空で、動きなしもなければ null。waiting（『#12 を待つ』）・descendant_in_progress・parent_closed・inherited_waiting・unknown の符号・pr_mergeable・pr_needs_fix と、知らない符号で文が名前と違うときは reason がその文。作業中で動きなしがあれば、理由が足さなくても {reason: \"\", idle} を返す。merge は needs_fix・mergeable のとき値、ほかは null。マージ待ちで理由が足さない（in_progress など）ときも null でなく、reason が札の言葉（『マージ待ち・直す必要あり』『マージ待ち・マージできる』）", verifies: ["R-03", "R-04", "F-01"]}
	"T-02": {title: "欄（偽の DOM、構造の図と横断の構造）：見出し（.pn-top）の文字に今の ID がちょうど1回、祖先の ID がその前に順に並び（Issue・Epic・Initiative）、祖先のない Scope に『最上位』の印。祖先のボタンで onSelect。題名の title が全文。帯：自分で作業中・終わった・着手できるは帯なしで状態の名前が札の1回だけ、止められている・配下が作業中・PR の理由・分からないは帯があり文が理由、30分を超えて動きのない作業中の Issue は動きなしだけの帯。マージ待ちの Scope に『マージ待ち』の札がなく帯にマージの印（直す必要ありとマージできるで違う）、理由が足さないマージ待ちでも帯が出る。.pn-kicker・.pn-merge・別の行の .pn-idle がない。同じ状態の描き直しで .pn-crumb・.pn-hl・.pn-cover を書き直さない。タブの行の印：説明資料（書かれている）なら説明資料の href と『説明資料を新しいタブで開く』、文書のタブなら選んだ文書の href と名前、ほかのタブ・雛形・読み込み中・読めないときは印なし。タブの切り替え・文書の選び直し・Scope の切り替えで印が変わり、前の印が残らない。送り：偽の DOM で .pn-crumb の scrollWidth を clientWidth より大きくして描く・印を描く・窓の大きさを変えると .pn-head に is-stacked が付き、収まれば外れ、全体の段では付かない、片付けの候補の見出しには付かない。headOverflows の境（差 1px は偽、2px は真）。印を押して開く・Orca で開く・引っぱりの今のテストが通る", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-08", "F-01", "F-02"]}
	"T-03": {title: "タブと詳しい画面と CSS（HTML と偽の DOM と静的な検査）：説明資料のタブの中身に sd-framebar がなく枠が最初、文書のタブの帯に選びがあり印がない、SCOPE_TABS の open（説明資料・文書だけ）と tabOpenLink の HTML（エスケープを含む）、詳しい画面のタブの行に選んだタブの印。CSS：見出しが折り返さず .pn-crumb が flex: 1 1 0・min-width 0・overflow hidden、is-stacked で折り返し .pn-crumb が order 9・100%、閉じるの margin-left: auto の規則が残る（片付けの候補）、欄の題名の2行の切り、帯の1行と省略記号、.pn-tabrow と .pn-tabopen:empty の隠し、スマートフォンの全体の段で祖先のパンくず・最上位の印・.pn-kind・帯を隠し題名を1行にする規則、.sd-framebar__open・.sd-framebar__name・.pn-kicker の規則がない", verifies: ["R-02", "R-03", "R-05", "R-06"]}
	"T-05": {title: "段を保つ（偽の DOM、スマートフォンの幅、横断の構造の画面か panel の部品）：片付けの候補を開いて全面にし、構造の更新・画面の大きさの変化で描き直しても data-snap が full のまま。Scope の欄を閉じてから片付けの候補を開くと half、片付けの候補を全面で閉じるボタンで閉じてから開き直すと half、閉じてから Scope を選ぶと half、全面の片付けの候補の中の Scope を選ぶと full のまま。帯の欄と Scope の欄の今の段のテストが通る", verifies: ["R-09"]}
	"T-04": {title: "実機（D-06）：1440×900 と 1000×800 の見出しの高さと説明資料の枠の高さ（直す前と後、作業中の Issue・止められている Scope・Epic）、1000×800 の1行目が1行で .pn-head がはみ出さない、印4つで1行かパンくずが下の行に送られはみ出さない、片付けの候補の見出しの閉じるが右端、写し（Issue・Epic・Initiative・止められている・エージェントのいる Scope、構造の図と横断の構造とボード、1440・1280・1000 × 明・暗、390×844 の通常と全体の段）、ブラウザーのエラー0", verifies: ["R-01", "R-06", "R-07"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/infra/test_dashboard_panel_logic_js.py`、
	S-02 の後は `uv run pytest tests/unit/infra/test_dashboard_panel_logic_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_agents_tab_js.py tests/unit/infra/test_dashboard_scope_tabs_js.py tests/unit/infra/test_dashboard_state_marks.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`（ほかに欄を描くテストがあれば足す）。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-06。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと欄の見出しとタブの行が今の形に戻る。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の高さの測りと写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから続けさせる。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "実装の開始のコミット（iss-00650 のマージ後の origin/main。report.md に記録）から S-03 の終わりまで（S-04 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00656/", "spec-dock/initiatives/00000-00999/epic-00573/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-claude": {task: "実装（S-01〜S-03、headerBand、欄の見出し、タブの行の印、詳しい画面、CSS、テスト、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面のコード（HTML・CSS・画面の JS）は Claude Opus 5.5 / medium（依頼書）。テストで確かめられる計算は headerBand の数行だけで、見出しの HTML と同じ変更の一部なので、Codex の別のセッションに分けない（分けると起動と引き継ぎの手間が計算の大きさを上回る）"}
		owner:         {task: "測りと実機の確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。試しのサーバーと headless Chrome をこの worktree で動かす"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
