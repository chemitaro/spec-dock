package spec

// 計画（Issue）。型 specdock/v1。

goal: "指揮の線の点と波紋を合成スレッドだけで動かし、線ごとの小さな SVG に分け、図を動かす間・画面の外・裏で止めて、同じ台本の TaskDuration を今の5分の1以下にする"

steps: {
	"S-01": {title: "T-01 を tests/js/dashboard_graph_command_motion.mjs（新）・tests/unit/presentation/test_dashboard_graph_command_motion.py（新）に先に書いて落ちることを確かめ、D-01（新しい views/graph/command_motion.js の MOTION・boxOf・phaseDelay・phaseOffset・svgOpen・bodyHtml・endsHtml・rippleHtml）を入れて通す。今のファイルは変えない", realizes: ["R-01", "R-02", "R-05"], status: "done", session: "impl-sol"}
	"S-02": {title: "T-02・T-03 を先に書いて（今の iss-00616・iss-00617 の CSS と画面のテストのうち、層の中の HTML と点・波紋の CSS を固定している期待を、この設計に合わせて直すことを含む）落ちることを確かめ、D-02（layersHtml）、D-03（createMotion）、D-04（graph.js・allgraph.js のつなぎと specdockCmdAudit の motion）、D-05（graph.css）を入れて通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02"], status: "done", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（直したテストの期待が、層の中の HTML と点・波紋の CSS の変更だけによることを確かめる。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-02", "R-05"], status: "done", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-06 の測りと実機の確かめ（T-04）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。受入の数に届かないか、写しで見た目の違いがあれば、実装担当に返す", realizes: ["R-01", "R-02", "R-03", "R-05"], status: "done", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "描き方の純粋な計算（node）：boxOf が C と L の道と点の半径のすべての点を pad だけ内側に含む整数の四角で、点がなければ null。phaseDelay(0..3) が 0・−0.15・−0.1・−0.05、phaseOffset が 0・−2・−4・−6。どの時刻 t（0.01 刻みで 0〜0.4）でも、keyframes（0〜25% で見える）と遅れから見える枚数がちょうど1枚で、見える枚のずらしが時刻とともに −2 ずつ進む（周期で 0 に戻る）。bodyHtml：flow は本体1（glow だけ）と cl-ph 4枚（data-ph、animation-delay、stroke-dashoffset、g の data-id・data-parent・data-child・data-state）、wait・done は本体1に glow と cl-line、どれも viewBox と left・top・width・height が同じ数。endsHtml：flow の stubs が 4枚に、点は本体に1つ、stubs のない flow は切り替えの絵なし。rippleHtml の中心と data-agent。属性の値のエスケープ。--cl-len を書かない", verifies: ["R-01", "R-02", "R-05"]}
	"T-02": {title: "CSS の静的な検査：sd-cmd-flow がなく、flow の点の規則にアニメーションがない、.cl-ph の sd-cmd-phase .2s steps(1, end) infinite と keyframes が opacity だけ（0% 1、25% 0、100% 0）、.cr > i の縁 1.5px・丸・sd-cmd-ripple 2.4s ease-out、.cr の 15.5px と負の余白、.cr .cr-b の 1.2s、止める規則（is-still・is-off の paused）、減らす設定（.cl-ph のアニメーションなし・opacity 0、data-ph 0 だけ 1、.cr > i の 1.4倍と .6、.cr-b なし）、.cl-svg の absolute と overflow visible、層の z-index と pointer-events は今のまま、禁じたもの（<animate・animateMotion・canvas・blur(）がない、色は札と変数だけ", verifies: ["R-01", "R-03", "R-05"]}
	"T-03": {title: "画面（偽の DOM と偽の orca、両方の画面）：組があるとき .gx-cmd・.gx-cmd-top・.gx-band-cr が SVG でなく、中の SVG が線ごと（flow は 5つ）で、世界と同じ大きさの SVG がない。組がないとき世界の HTML が今と同じ。指揮の選びで同じ data-id のすべての g.cl に is-cmd-hl、ほかに is-cmd-off、層に has-cmd-sel。図を動かす操作（ドラッグ・ホイール）の後に .gx-view に is-still が付き、続けて動かすと最後から 0.3秒の後に外れる。visibilitychange で裏なら付き、表で外れる。偽の IntersectionObserver で、重ならないと知らされた .cl-ph・.cr に is-off、重なると外れる、描き直しで新しい要素を見張り古いものをやめる、画面を離れると見張りをやめる。IntersectionObserver がないときもエラーなく描ける。specdockCmdAudit の motion の数え", verifies: ["R-02", "R-03", "R-04", "R-05", "F-01", "F-02"]}
	"T-04": {title: "実機（D-06）：同じ台本の TaskDuration（直す前と後、動きありと減らす設定、横断と単体）が受入の数以下、ドラッグの間の長いタスクの数と最長とコマの数（前と後）、specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0・spotDrift ≤ 0.4、両方の画面の 1440 × 明・暗の線・点・波紋の写し（前と後）と、0.05秒ずらしの写しで点の向き、ブラウザーのエラー0", verifies: ["R-01", "R-02", "R-03", "R-05"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_command_motion.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_marks_js.py tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`。
	最後に `make lint`、`uv run pytest`（全体）。実機は D-06。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと点と波紋が今の CSS アニメーションに戻る。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の測りと写し、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が S-01 の節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-03 の終わりまで（S-04 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00646/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、command_motion.js の純粋な計算と node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で node のテストで確かめられる（依頼書：テストで確かめられる計算は Codex GPT-6.1 Sol / medium）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、impl-claude が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、層の HTML、止める仕組み、両方の画面、CSS、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面は Claude Opus 5.5 / medium（依頼書）"}
		owner:         {task: "測りと実機の確かめ（S-04）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。試しのサーバーと headless Chrome がこの worktree にある"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
