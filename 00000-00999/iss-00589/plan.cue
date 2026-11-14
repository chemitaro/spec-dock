package spec

// 計画（Issue）。型 specdock/v1。

goal: "文書と説明資料のタブを「1行の帯 ＋ 残りの高さを使う枠」にし、選べる文書を仕様と報告にして、埋め込んだ文書を読む面積を最大にする"

steps: {
	"S-01": {title: "node のテスト（T-01〜T-03）を先に書いて落ちることを確かめ、scope_tabs.js の docsTab・documentEntries・checkResults・explanationTab と DOC_INFO を D-01〜D-03、D-05、D-06 のとおりに直す。test_dashboard_documents.py の目印を新しい形に合わせる", realizes: ["R-01", "R-02", "R-03", "R-05", "F-01", "F-02"], status: "todo", session: "impl-ui"}
	"S-02": {title: "scope_tabs.css・panel.css・scope.css を D-02、D-04 のとおりに直し（帯、セグメント、誤りの帯、枠の伸び、使わない規則の削除）、静的なテスト（T-04）を足す。make lint と uv run pytest（全体）を通す", realizes: ["R-02", "R-03", "R-04", "R-05"], status: "todo", after: ["S-01"], session: "impl-ui"}
	"S-03": {title: "実データで直した後の写しと測りを撮り、直す前と並べて report.md に残す。--tailscale のサーバーを立てて URL を残す（D-07）", realizes: ["R-06", "R-02", "R-03", "R-04", "R-05"], status: "todo", after: ["S-02"], session: "owner"}
}

tests: {
	"T-01": {title: "CUE の Scope の docsTab が、仕様・報告の2つのセグメント（説明資料なし、.sd-doc なし、plan-progress なし）を返し、wanted がないとき仕様を選び、右端のリンクの href が選んだ view で target=_blank。report がないとき報告が aria-disabled。欄の env では項目が data-pn-param=\"doc\" を持つ（node）", verifies: ["R-01", "R-02", "R-03"]}
	"T-02": {title: "checkResults が、誤り 0 件（警告だけを含む）で帯を出さず、誤りがあるとき check-invalid の details（件数と spec-dock scope check <ID>、一覧）を返し、failed で render-failed を返して枠を出さない。Markdown の Scope で要件・設計・計画・報告が並ぶ。catalog が ok でないとき catalogProblem（node）", verifies: ["R-01", "R-03", "F-01"]}
	"T-03": {title: "explanationTab の written が .sd-framebox と .sd-framebar（新しいタブのリンク）と iframe.sd-explain（src、sandbox は今のまま）を返し、docsTab と explanationTab が同じ入力で同じ文字列を返す（node）", verifies: ["R-05", "F-02"]}
	"T-04": {title: "panel.css が docs と explanation の .pn-body を flex の列にし、枠が flex: 1 で伸び、scope.css の枠が flex: none で高さが 100dvh から決まり、使わなくなった .sd-doc の規則がなく、新しい色（#、rgb(、hsl(）を足していない（静的）", verifies: ["R-04", "R-05"]}
	"T-05": {title: "実データの写し（1440、1000、390 の全体の段、欄と詳しい画面、文書と説明資料、直す前と後）と、枠の高さの測り（上端、高さ、見える高さ、欄に対する割合、中身のスクロールの有無、帯の高さ、セグメントの項目）と、差し込んだ誤りの帯の閉じた高さ（1000、390）が report.md にある", verifies: ["R-02", "R-03", "R-04", "R-05", "R-06"]}
}

verification: """
	S-01、S-02：`uv run pytest tests/unit/infra/test_dashboard_scope_tabs_js.py tests/unit/application/test_dashboard_documents.py tests/unit/infra/test_dashboard_screens_js.py` と、足したテスト。最後に `make lint`、`uv run pytest`（全体）。
	S-03（タスク担当）：`.workbench/iss-00589/shoot.mjs` を、直す前の venv（ポート 18589）と直した後の venv（ポート 18590、--tailscale）で走らせる（D-07）。
	"""

rollback: "PR を戻す（ダッシュボードの画面の資産とテストだけの変更）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の写しと測りと tailnet の URL がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {}
	checkpoints_note: "なし。変えるのは1つのタブの部品と見た目だけで、2手順を同じ実装担当が続けて行う。最終品質ゲートで開始のコミットから全体を見る"
	final_quality_gate: {
		scope:          "開始のコミット 7e50ac583 から S-02 の終わりまで（S-03 は記録だけ）"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "security-baseline"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "coordinated の使い方。タスク担当はマージせず、PR と証拠を統括に報告する。統括がマージする"
}

execution: {
	sessions: {
		spec:      {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-ui": {task: "実装（S-01、S-02）", model: "opus", effort: "medium", rationale: "claude。画面と一体の HTML・CSS・画面の JavaScript。本人の指示（依頼書、2026-11-14）。データの形・純粋な計算・API の変更はなく（Scope の JSON は変えない）、文書の選びの並びも同じ描き方の関数の中の数行なので、Codex の手順は切り出さない"}
		owner:     {task: "実データの写しと測り（S-03）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。ブラウザーでの確かめは実装ではなく、受け入れの証拠の取得"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-02", model: "opus", effort: "medium"}
	}
}
