package spec

// 計画（Issue）。型 specdock/v1。

goal: "両方の図で、マウスのホイールがカーソルの位置で拡大・縮小し、矢印キーと + - 0 で動かせ、トラックパッドは今のまま。処理は1つのモジュールにある"

steps: {
	"S-01": {title: "T-01・T-02 を tests/js/dashboard_view_input.mjs（新）・tests/unit/presentation/test_dashboard_view_input.py（新）に先に書いて落ちることを確かめ、D-01〜D-03（新しい views/graph/view_input.js の WHEEL・KEYS・wheelKind・wheelAction・keyAction・ownsKey）を入れて通す。今のファイルは変えない", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01"], status: "done", session: "impl-sol"}
	"S-02": {title: "T-03 を先に書いて（両方の画面の今の画面のテストに、マウスのホイール・キー・aria-label の場面を足す）落ちることを確かめ、D-04（view_input.js の bindViewInput と、graph.js・allgraph.js のつなぎ。今の wheel の処理を消す）と D-05（aria-label）を入れて通す", realizes: ["R-01", "R-02", "R-04", "R-05", "R-06", "R-07", "F-02"], status: "done", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（今のテストの期待を変えたら、その理由が wheel・キー・aria-label の変更だけによることを確かめる。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-06"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-06 の実機の確かめ（T-04）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。受入に届かないか、実機の値が見分けの表と食い違えば、実装担当に返すか統括に問う", realizes: ["R-01", "R-02", "R-04", "F-02"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "wheel の見分けと写し（node、表）：D-01 の表の各行の値で wheelKind が表の種類。wheelAction：マウスのホイールの1刻みが 1.15倍・1/1.15倍（deltaY の符号の逆）、wheelDeltaY 240 で 1.15²、360 でも 1.15²（最大 2刻み）、deltaMode 1 は 1刻み、deltaY 0 は act null、ピンチは exp(−deltaY·0.01)、2本指は dx −deltaX・dy −deltaY、Shift は横だけ（deltaX があれば −deltaX、なければ −deltaY、deltaMode 1 は 16倍、2 は page 倍）。続き：pan の 199ms 後の wheel? は pan、200ms 後は wheel?、pan の直後でも deltaMode 1 は wheel、ピンチは pinch。Firefox のチルト（deltaMode 1、deltaY 0、deltaX 3）は pan で dx −48。Firefox の決まり：deltaMode を wheelDeltaY より先に読む（読む順を記録する偽の物）", verifies: ["R-01", "R-02", "R-03", "F-01"]}
	"T-02": {title: "キーの写しと横取りしない場面（node、偽の DOM）：keyAction の4つの向き（← dx +80、→ dx −80、↑ dy +80、↓ dy −80）、Shift で 320、+・= で 1.25、- で 0.8、0 で fit、a・Enter・Escape・Space・Tab は null、Ctrl・Cmd・Alt 付き・isComposing・defaultPrevented は null。ownsKey：body・documentElement・図の面を包む main（tabindex=-1）・target なし・図の面・図の面の中の role=button の div で true、input・textarea・select・button・a[href]・summary・iframe・contenteditable（図の面の中でも）と、図の面の外の div で false、contenteditable=false の中の div（図の面の中）は true", verifies: ["R-04", "R-05"]}
	"T-03": {title: "画面（偽の DOM と偽の orca、両方の画面。今の dashboard_graph_command_screen.mjs・dashboard_allgraph_command_screen.mjs の台本に、wheel の deltaMode・wheelDeltaY・shiftKey とキーの場面を足す）：マウスのホイール（deltaY −100、wheelDeltaY 120）で拡大率が 1.15倍になりカーソルの下の点が動かない、2本指（小さな値）で世界が動き拡大率は同じ、→ で世界の tx が 80 減る、+ で 1.25倍、0 で fit と同じ transform、input にフォーカスがあると → で動かない、フォーカスが図の面を包む main のとき → で動く、画面が隠れている（.gx-view の hidden）と → で動かず preventDefault もされない、どの操作の後も .gx-view に is-still。横断の構造は、→ の後の描き直しで初めの見え方に戻らない（A.moved）。両方の .gx-view の aria-label が D-05 の文。graph.js・allgraph.js に ctrlKey・deltaX・ArrowLeft の写しがない（静的な検査）", verifies: ["R-01", "R-02", "R-04", "R-05", "R-06", "R-07", "F-02"]}
	"T-04": {title: "実機（D-06）：両方の画面で、CDP の mouseWheel の前と後の拡大率とカーソルの下の点のずれ、届いた wheel の値、小さな deltaX・deltaY の mouseWheel で動く量と拡大率が同じこと、矢印キー・Shift+→・+・-・0 の前と後の transform と拡大率、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0、ブラウザーのエラー0、前と後の写し", verifies: ["R-01", "R-02", "R-04", "F-02"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_view_input.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-06。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すとマウスのホイールは動かすに戻り、矢印キーは効かなくなる。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実機の数と写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-03 の終わりまで（S-04 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00655/", "spec-dock/initiatives/00000-00999/epic-00654/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、view_input.js の純粋な関数と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、impl-claude が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、つなぎ、両方の画面、説明、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面のつなぎ込みは Claude Opus 5.5 / medium（依頼書）"}
		owner:         {task: "実機の確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。試しのサーバーと Chrome をこの worktree で動かす"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
