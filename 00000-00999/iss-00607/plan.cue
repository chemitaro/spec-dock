package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の依存の線の切り替えをなくし、常にすべての線で描く（layout.js・prefs.js・graph.js とテスト）"

steps: {
	"S-01": {title: "D-04 のうち layout と restorePrefs のテストを書き換える（deps wait・none を渡しても deps なしと同じ、全体・いまが iss-00603 の digest の deps all の組と同じ、restorePrefs の返り値に deps がない、prefs.js に deps の字がない）。直す前のコードで落ちることを確かめる（Red）", realizes: ["R-02", "R-04", "F-01"], status: "todo", session: "impl-sol"}
	"S-02": {title: "layout.js に D-01、prefs.js に D-02（restorePrefs と注釈）を実装し、dashboard_graph_check.mjs の組み合わせから deps をなくして、すべての組み合わせで edgeAudit の違反0を通す（Green）", realizes: ["R-02", "R-04", "F-01"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "toolbar のテスト（帯に deps の group がない、保存が3つの鍵、版3の deps none でも線が出る）を先に書いて落ちることを確かめ、graph.js に D-03 と savePrefs（D-02）を実装する", realizes: ["R-01", "R-03", "R-04", "F-01"], status: "todo", after: ["S-02"], session: "impl-ui"}
	"S-04": {title: "make lint と全体の pytest を通す", realizes: ["R-01", "R-02", "R-04"], status: "todo", after: ["S-03"], session: "impl-ui"}
	"S-05": {title: "spec-dock と housing-lifecycle の実データで、直す前と後の道具の帯と線を 1440・390、明暗で写し、edgeAudit の違反0と帯の大きさを report.md に残し、tailnet の試しの URL を立てる", realizes: ["R-05"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "全体・いまの layout（4つの構造 × 入れ子・木 × 幅 既定・374 × 配線の前後、deps なし）が layout-before.json の deps all の digest と同じ", verifies: ["R-02"]}
	"T-02": {title: "small・context の構造で、deps wait・none を渡した layout の nodes・groups・edges が deps なしと同じで、終わった依存の組が is-done（done 真）で出る（全体・いま）。これからの既存の線のテストが通る", verifies: ["R-02", "F-01"]}
	"T-03": {title: "restorePrefs：版3（deps wait を含む）、版2（deps none を含む）、版1、壊れた値、なしで、opts が {mode, range} だけ。prefs.js と graph.js に `deps` の字がない", verifies: ["R-04", "F-01"]}
	"T-04": {title: "dashboard_graph_check.mjs のすべての組み合わせ（deps なし）で edgeAudit の違反0", verifies: ["R-02"]}
	"T-05": {title: "toolbar：入れ子・木 × 全体・いま・これからで、帯に data-act=deps・aria-label「依存の線」・3つの文字がなく、縮小〜見せる範囲が今の順で残る。凡例の HTML が直す前と同じ文を持つ", verifies: ["R-01", "R-03"]}
	"T-06": {title: "toolbar：範囲と表し方と凡例を押したあと `specdock.graph.v3` の値が {mode, range, legend} の3つの鍵だけ。版3に deps none を保存した状態で描いた世界に依存の線（is-done を含む）がある", verifies: ["R-04", "F-01"]}
	"T-07": {title: "選んだ箱の線の強調の既存のテストが通る（全体の pytest）", verifies: ["R-03"]}
	"T-08": {title: "実データ（spec-dock、housing-lifecycle）× 1440・390 × 明暗の直す前と後の写し、390px の帯の高さ（後が短い）、edgeAudit の違反0、ブラウザーのエラー0が report.md にある。graph.css に差分がない", verifies: ["R-05"]}
}

verification: """
	節目：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py`。最後に `make lint`、`uv run pytest`（全体）。
	実データ：この PC の状態の置き場を `.workbench/iss-00607/state` に写し、隔離した venv（開始のコミットと最後のコミットの wheel）で
	`spec-dock dashboard serve --port <空いた番号> --offline --state-root <絶対の道> --tailscale` を立て、headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で写す。
	常駐のダッシュボード（47800）と道具の環境には触れない。
	"""

rollback: "PR を戻す（ダッシュボードの静的な資産とテストだけ）。deps のない版3は前のコードで deps の既定（all）として読まれる。"

exit: "PR がマージできる状態で CI が通り、最終品質ゲートの closure.md があり、report.md に実データの写しと試しの URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {}
	checkpoints_note: "なし。変更は deps の分かれ道を消すだけで小さく、S-02 の終わりに担当が節目のテストを通し、最終品質ゲートで開始のコミットから全体を見る"
	final_quality_gate: {
		scope:          "開始のコミット bf21a961a から S-04 の終わりまで（S-05 は記録だけ）。PR の直前に origin/main を取り込んだら、その最後のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00607/"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "統括がマージする（依頼書）。タスク担当はマージしない"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01〜S-02）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。layout.js・prefs.js は DOM のない純粋な計算で node のテストで確かめられる（方針の「テストで確かめられる実装」× standard）。本人の指示で Sol を使う。chat-scratch の symlink の拒否や確認の画面で止まったら、待たずに止め、Claude Opus 5.5 / medium に切り替える（統括が了承済み、逸脱として report.md に書く）"}
		"impl-ui":  {task: "実装（S-03〜S-04）", model: "opus", effort: "medium", rationale: "claude。道具の帯はフロントエンドの実装（依頼書、方針 × standard）"}
		owner:      {task: "実データの写しと試しの URL（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
