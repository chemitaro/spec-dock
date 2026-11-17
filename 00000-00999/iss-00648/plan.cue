package spec

// 計画（Issue）。型 specdock/v1。

goal: "指揮の線を、上の縁から出て上の縁へ入るホップの弧にし、子の端に矢じりと印の縁を描き、Epic の文書を今の決定に合わせる。点・波紋・軽くした描き方は変えない"

steps: {
	"S-01": {title: "D-06：Epic epic-00615 の requirement.cue・design.cue を直し、spec-dock scope check epic-615 を通す（仕様のレビューの前に、タスク担当が書く）", realizes: ["R-06"], status: "done", session: "owner"}
	"S-02": {title: "T-01 を tests/js/dashboard_graph_command.mjs・tests/js/dashboard_allgraph_command.mjs に先に書いて（今の下の端・stubs・boxArc・frameArc・bandArc・曲線の制御点を固定した期待を、この設計に合わせて直すことを含む）落ちることを確かめ、D-01（端）、D-02（hop）、D-03（sameHop）、D-04 のモデルの mark、D-05（top・ceiling、crossModel の ceiling: 4）を views/graph/command.js・views/allgraph/command.js に入れて通す。描き方のファイルは変えない", realizes: ["R-01", "R-02", "R-03", "F-01", "F-02"], status: "done", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "T-02・T-03 を先に書いて（端の層の cl-dot と stubs の期待を直すことを含む）落ちることを確かめ、D-04 の描き方（command_motion.js の ARROW・arrowPath・markRect・endsHtml・bandMarkHtml、command_view.js の layersHtml・paintCmdSel、graph.css）を入れて通す", realizes: ["R-04", "R-05", "F-01"], status: "done", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "make lint と全体の uv run pytest を通す（直したテストの期待が、端・道・弧・端の層の変更だけによることを確かめる。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-05"], status: "done", after: ["S-03"], session: "impl-claude"}
	"S-05": {title: "D-07 の写し・測り・検査（T-04）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。受入に届かないか、写しで崩れがあれば、実装担当に返す", realizes: ["R-02", "R-03", "R-04", "R-05"], status: "done", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "端と道の純粋な計算（node）：箱・木の枠の箱・入れ子の枠の見出し・帯の印・塊・祖先の枠（相手を含む場合を含む）・印の位置が分からない端の from・to が上の縁の上で、印のある端は x が印の中央。stubs がどれも空。道の始めと終わりの制御点が端より上（子が上・下・同じ高さ）。hop：同じ高さでも高さが違っても（差 700px を含む）頂点がちょうど H（±0.5）上、H が dx・dy で増え 18〜56 の間、dx 0 で横に 8px 以上ふくらむ、ceiling で頂点が下がる（HOP.low より下げない）。sameHop：同じ箱の同じ行・違う行、同じ枠の見出し、帯の同じ項目で kind arc、頂点が縁より 18 上、弦 12 以上、縦に重なる印で 12 に離す、上の余白 14px の箱で 11 に下がり crowded 1・boxOverlaps 0、8 も入らないとき 8。依存の線の水平な区間：縁から 10px と 15px 上で 18 のまま edgeOverlaps 0、16px 上で 13 に下がる（18〜14 は頂点との差が 3 未満）、中央の半分の外（脚の位置だけ）の区間は高さを変えず数えない、8〜18 のどれでも 3px 未満になる区間の組（例：9・14・18px 上）で d が上限のまま edgeOverlaps 1。線の mark（印の四角、帯なら band true、塊・祖先の枠・分からない端は null）。top が帯の上へふくらむ弧を含む。top が帯の同じ項目の弧の頂点も含む。crossModel が ceiling 4 を渡し、ほかの場所の帯から下の箱（差 500px 以上を含む）への弧の頂点が 4 − 0.5 以上", verifies: ["R-01", "R-02", "R-03", "F-01", "F-02"]}
	"T-02": {title: "描き方（node）と CSS の静的な検査：arrowPath の先が to、底が to.y − 6 で幅 7。endsHtml に cl-arrow 1つ、cl-dot なし、mark があり band でなければ cl-in が印の四角を 2px 外へ囲み、SVG の四角が矢じりと縁を含む。stubs が空の flow の端の層は止めた絵1枚。bandMarkHtml が帯の子だけに cl-in の SVG を返す。CSS：cl-arrow の塗りと cl-in の線が --sd-cmd、cl-in 1.5px、done で .35、cl-dot の規則がない。iss-00646 の切り替え・波紋・止める規則・禁じたものの検査は今のまま通る", verifies: ["R-04", "R-05"]}
	"T-03": {title: "画面（偽の DOM と偽の orca、両方の画面）：組があるとき、箱の子の線の端の層に cl-arrow と cl-in、帯の子の縁が .gx-band-cr に入る。指揮の選びで .gx-band-cr の g.cl にも is-cmd-hl・is-cmd-off。組がないとき世界の HTML が今と同じ。iss-00646 の止める仕組みのテストが通る", verifies: ["R-04", "R-05", "F-01"]}
	"T-05": {title: "Epic の文書の検査：spec-dock scope check epic-615 が誤りなしで通り、rg で epic-00615 の requirement.cue・design.cue に、今の決まりとしての『下の縁』『印の行に近い縁』『短い線』『端の点』『stubs』（空とする文を除く）『2〜3 秒』『stroke-dashoffset』の文が残らない（decisions の履歴の行を除く）", verifies: ["R-06"]}
	"T-04": {title: "実機（D-07）：両方の画面の 1440・390 × 明・暗 × 全体・いま・これからの、直す前と後の写し（帯 → 箱、同じ箱の親子の 18px の弧と 11px に下がった弧の両方、リポジトリをまたぐ線）。同じ台本の TaskDuration が横断 0.11・単体 0.07 秒以下（前と後）。specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0、spotDrift ≤ 0.4、spotMissing 0、ブラウザーのエラー0", verifies: ["R-02", "R-03", "R-04", "R-05"]}
}

verification: """
	節目：S-02 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_command.py tests/unit/presentation/test_dashboard_allgraph_command.py`、
	S-03 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-07。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと線が下から出る U 字の曲線と箱の下の弧に戻る。API・保存・モデルは変わらない。Epic の文書の直しは Git の外の仕様なので、戻すときは文書を書き戻す。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の写しと測り、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-02 の後は、タスク担当が S-02 の節目のテストの合格を確かめてから S-03 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-04 の終わりまで（S-05 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00648/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）と S-01", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-02、command.js・allgraph/command.js の純粋な計算と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、impl-claude が S-02 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-03〜S-04、端の層の描き方、両方の画面、CSS、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書）"}
		owner:         {task: "写しと測りと実機の確かめ（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。試しのサーバーと headless Chrome がこの worktree にある"}
	}
	// 仕様のレビューは S-02 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
