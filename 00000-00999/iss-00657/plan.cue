package spec

// 計画（Issue）。型 specdock/v1。

goal: "指揮の線の点を、組の間 24px の大小2つの点の組にし、0.1秒ごとに 2px（20px/秒）で流し、波紋を 3.6秒にして、iss-00646 の重さの受入を保つ"

steps: {
	"S-01": {title: "iss-00648 のマージの後の origin/main から始め（開始のコミットを report.md に書く）、D-01 の前提（端の層の stubs が空、本体だけが切り替えの絵を持つ）を読み直す。T-01 を先に直して落ちることを確かめ、D-01（MOTION、dotsHtml、bodyHtml）を入れて通す", realizes: ["R-01", "R-02", "R-04", "F-01"], status: "todo", session: "impl-sol"}
	"S-02": {title: "T-02・T-03 を先に直して落ちることを確かめ、D-02（graph.css の点・組・切り替え・波紋・注記）を入れて通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05"], status: "todo", after: ["S-01"], session: "impl-claude"}
	"S-03": {title: "make lint と全体の uv run pytest を通す（直したテストの期待が、数と点の線の数の変更だけによることを確かめる。static-inventory.json に載る資産の sha256 が変われば直す）", realizes: ["R-04"], status: "todo", after: ["S-02"], session: "impl-claude"}
	"S-04": {title: "D-04 の測り・連続の写し・線の検査（T-04）を report.md に残し、本人が見る試しの URL（tailnet）を立てたままにする。受入に届かないか、写しで向きが読めなければ、数を見直すか統括に問う", realizes: ["R-01", "R-02", "R-04", "R-05"], status: "todo", after: ["S-03"], session: "owner"}
	"S-05": {title: "D-05（Epic epic-00615 の R-05・D-04・decisions）を書き換え、spec-dock scope check epic-00615 と iss-00657 を通す", realizes: ["R-02"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "描き方の純粋な計算（node）：MOTION が {phases: 12, step: 2, tick: 0.1, gap: 24, tail: 6, pad: 4} で phases·step = gap。phaseDelay(0..11) が 0・−1.1・−1.0・…・−0.1、phaseOffset が 0・−2・…・−22。0.01秒刻みの 0〜2.4秒のどの時刻も見える絵がちょうど1枚で、そのずらしが 0.1秒ごとに −2 ずつ進み 1.2秒で 0 に戻る。dotsHtml が cl-line cl-hd（ずらし off）と cl-line cl-tl（ずらし off+6）の2本で −0 を書かない。bodyHtml の flow が止めた SVG 1（glow だけ）と cl-ph 12枚（data-ph 0..11、animation-delay、各々に頭と尾）、wait・done は今のまま。属性のエスケープ。今の boxOf・endsHtml・rippleHtml の検査は保つ", verifies: ["R-01", "R-02", "R-04", "F-01"]}
	"T-02": {title: "CSS の静的な検査：flow の点の 0.1 23.9 と wait の 0.1 7.9、.cl-hd の太さ 3.5、.cl-tl の太さ 2 と opacity .45、選んだ線の 4.5 と 3（.cl-line の 3 の規則より後）、.cl-ph の sd-cmd-phase 1.2s steps(1, end) infinite、keyframes が opacity だけ（0% 1、8.334% 0、100% 0）、sd-cmd-ripple 3.6s ease-out と .cr-b の 1.8s、減らす設定（data-ph 0 だけ）、止める規則と層の規則は今のまま。MOTION（node で読む）と CSS の写しの数（1周の秒 = phases·tick、dasharray の和 = gap、keyframes の割合 ≈ 100/phases）が合う", verifies: ["R-01", "R-02", "R-03", "R-05"]}
	"T-03": {title: "画面（偽の DOM と偽の orca、両方の画面）：流れる線1本で本体の層の SVG が 13 で、切り替えの各々に cl-hd と cl-tl があり、specdockCmdAudit の motion.phases が 12。指揮の選び・止める仕組み・見張りの今の期待がそのまま通る", verifies: ["R-04"]}
	"T-04": {title: "実機（D-04）：同じ台本の TaskDuration（前と後、動きありと減らす設定、横断と単体、交互に3回）で後が横断 0.11秒以下・単体 0.07秒以下。1440×900 の 0.1秒ごとの連続の写し（前と後、明・暗、減らす設定）で組が子へ 2px ずつ進み、止まった1枚で向きが読める。specdockEdgeAudit の違反0、specdockCmdAudit の boxOverlaps・edgeOverlaps・heads 0・spotDrift ≤ 0.4、ブラウザーのエラー0", verifies: ["R-01", "R-02", "R-04", "R-05"]}
}

verification: """
	節目：S-01 の後は `uv run pytest tests/unit/presentation/test_dashboard_graph_command_motion.py`、
	S-02 の後は `uv run pytest tests/unit/presentation/ tests/unit/infra/test_dashboard_orca_views_js.py tests/unit/infra/test_dashboard_screens_js.py tests/unit/infra/test_dashboard_allgraph_route.py`。
	最後に `make lint`、`uv run pytest`（全体）。PR の直前に origin/main を取り込み直し、最後のコミットで両方をやり直す。実機は D-04。
	"""

rollback: "PR を戻す（dashboard の静的な資産とテストだけ）。戻すと点が iss-00646 の 8px・4枚・40px/秒と 2.4秒の波紋に戻る。API・保存・モデルは変わらない。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に動きの数の表（前と後）、TaskDuration（前と後、両方の画面）、連続の写し、線の検査、試しの URL がある。マージは統括が行う。"

gates: {
	checkpoints: {
		"CP-1": "なし（S-01 の後は、タスク担当が節目のテストの合格を確かめてから S-02 の担当を起動する。レビューは最終品質ゲートでまとめる）"
	}
	final_quality_gate: {
		scope:          "開始のコミット（report.md に記録）から S-03 の終わりまで（S-04 で直しが出れば、その直しまで）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "e2e-user-flow"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00657/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:          {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol":    {task: "実装（S-01、command_motion.js の数と点の線、node のテスト）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。DOM のない計算で node のテストで確かめられる（依頼書）。chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに止め、impl-claude が S-01 から引き継ぐ（統括が了承済み、逸脱として report.md に書く）"}
		"impl-claude": {task: "実装（S-02〜S-03、CSS と画面のテスト、全体の確かめ）", model: "opus", effort: "medium", rationale: "claude。画面（SVG の形、CSS）は Claude Opus 5.5 / medium（依頼書）"}
		owner:         {task: "測り・実機の確かめ・Epic の文書（S-04〜S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。試しのサーバーと headless Chrome がこの worktree にある"}
	}
	// 仕様のレビューは S-01 の前に行う（report.md のレビュー記録。spec-reviewer opus / high）。
	reviews: {
		gate: {role: "最終品質ゲート", after: "S-03", model: "opus", effort: "medium"}
	}
}
