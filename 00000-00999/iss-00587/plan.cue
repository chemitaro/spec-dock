package spec

// 計画（Issue）。型 specdock/v1。

goal: "欄を共有の部品にして、説明資料を最初のタブに埋め込み、詳しい画面と同じタブを欄の中で切り替えられるようにし、ボードと構造の図の両方から開き、スマホでは3段のシートにする"

steps: {
	"S-01": {title: "Scope の JSON の説明資料の項目に skeleton（true、false、null）を足す。テストを先に書いて落ちることを確かめ、実装する（D-01）", realizes: ["R-03", "F-03"], status: "todo", session: "impl-sol"}
	"S-02": {title: "views/_shared/panel_logic.js（explanationState、defaultTab、pickTab、sheetHeights、settleSheet、nextOnTap）を、node のテストを先に書いて実装する（D-02）", realizes: ["R-02", "R-04", "R-07"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "scope.js のタブの中身を views/_shared/scope_tabs.js に移し、env と SCOPE_TABS で描く形にし、説明資料のタブを足す。詳しい画面のタブの選びを pickTab にし、今のテストの期待を直す（D-03、D-04）", realizes: ["R-02", "R-03", "R-04", "R-09", "F-03"], status: "todo", after: ["S-02"], session: "impl-ui"}
	"S-04": {title: "views/_shared/panel.js と panel.css（見出し、タブ、中身、下の帯、欄の中のクリック、描き直しで枠とスクロールを保つ）を作り、構造の図の Scope の欄をそれに置き換える。PC の幅と上の帯のずらし、centerOn を直す（D-05、D-06）", realizes: ["R-01", "R-02", "R-03", "R-05", "R-06", "R-08", "F-01", "F-02", "F-04"], status: "todo", after: ["S-03"], session: "impl-ui"}
	"S-05": {title: "ボードで札を押すと同じ欄を開く。欄の aside を描き直しで保ち、列を欄の左に収める（D-07）", realizes: ["R-01", "R-05", "F-02", "F-04"], status: "todo", after: ["S-04"], session: "impl-ui"}
	"S-06": {title: "スマホのシートを3段のスワイプにする（取っ手と見出しの帯で引きずる、払う、取っ手のタップ、閉じる、段を保つ、resize）（D-08）", realizes: ["R-07", "R-08"], status: "todo", after: ["S-05"], session: "impl-ui"}
	"S-07": {title: "静的なテスト（共有の部品の使い方、esc、外への読み込みなし）を足して直し、make lint と全体の pytest を通す", realizes: ["R-01", "R-02", "R-09"], status: "todo", after: ["S-06"], session: "impl-ui"}
	"S-08": {title: "spec-dock の実データで 1440、1000、390 の直す後の写しを撮り、直す前の写しと並べて report.md に残す。390 のスワイプの3段と全体の読みを確かめる", realizes: ["R-10", "R-01", "R-03", "R-05", "R-06", "R-07"], status: "todo", after: ["S-07"], session: "owner"}
}

tests: {
	"T-01": {title: "dashboard_scope_details の documents の explanation の skeleton が、印ありで true、印なしで false、ないとき null、リンク（シンボリックリンク）で null、ほかの文書には skeleton の鍵がない", verifies: ["R-03", "F-03"]}
	"T-02": {title: "panel_logic.js の explanationState と defaultTab と pickTab が、written・skeleton・missing・unreadable と、wanted のあり・なし・知らないキーで決まった値を返す（node）", verifies: ["R-02", "R-04"]}
	"T-03": {title: "panel_logic.js の settleSheet が、遅い離しで近い段、速い上下の払いで次の段、最小より 48px より下で closed、端の段を超えない値を返し、sheetHeights と nextOnTap が決まった値を返す（node）", verifies: ["R-07"]}
	"T-04": {title: "scope_tabs.js の説明資料のタブが、written で sandbox の iframe（src は href、esc 済み）、skeleton と missing で知らせ（data-code）、unreadable で catalogProblem を返す。欄の env の paramLink が data-pn-param を持ち、ページの env が今と同じ道を作る（node）", verifies: ["R-02", "R-03"]}
	"T-05": {title: "SCOPE_TABS のキーが explanation から始まる決まった並びで、scope.js と panel.js が SCOPE_TABS からタブを作り、タブの中身の関数が scope.js に残っていない（静的）", verifies: ["R-02", "R-09"]}
	"T-06": {title: "board.js と graph.js が createScopePanel を使い、ボードの札のクリックが修飾キーのとき欄を開かない分かれを持つ。新しいファイルが外へ読みに行かず、利用者の文字が esc を通る（静的）", verifies: ["R-01"]}
	"T-07": {title: "実データの写し（1440、1000、390、ボードと構造の図、直す前と後）と、ブラウザーでの測り（欄の幅、帯との重なり、列の右端、iframe の src と sandbox、タブで URL が変わらない、描き直しで iframe が同じ、390 の3段の高さ、全体の枠の高さ、中身のスクロールで高さが変わらない、閉じる）が report.md にある", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "R-10", "F-02"]}
	"T-08": {title: "欄の詳しい JSON が読めないとき（API を 500 にした状態）、見出しと「詳しい内容を読めなかった」が出て、選びを変えた後の古い答えが出ない（ブラウザーでの確かめ、または panel.js の show を node で呼ぶ）", verifies: ["F-01", "F-04"]}
}

verification: """
	節目：S-01 は `uv run pytest tests/unit/application/test_dashboard_scope_details.py`、S-02〜S-07 は `uv run pytest tests/unit/infra/test_dashboard_screens_js.py tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_small_screens.py`
	と、新しく足したテストのファイル。最後に `make lint`、`uv run pytest`（全体）。
	実データ（S-08、タスク担当）：`.workbench/iss-00587/state` に写した状態の置き場で、隔離した venv（`.workbench/iss-00587/venv-after`、作業の木から作った wheel を入れる）の
	`spec-dock dashboard serve --port 18588 --offline --state-root <絶対の道>` を立て、headless Chrome（`--disable-features=MacAppCodeSignClone`、`Browser.close` で閉じる。
	`.workbench/iss-00587/shoot.mjs`）で 1440×900、1000×800、390×844 を写し、測る。直す前は開始のコミットの venv（`venv-before`、ポート 18587）で写した。
	道具の環境の spec-dock と常駐のダッシュボード（47800）には触れない。
	"""

rollback: "PR を戻す（ダッシュボードの画面の資産、dashboard_scope_details.py の項目の追加、テストだけの変更）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に直す前と後の写しと測りがある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"CP-1": {after: "S-04", range: "開始のコミット 928460f48 から S-04 の終わりまで", reviewer: "code-reviewer opus / medium", reason: "共有の部品の形（env、SCOPE_TABS、createScopePanel）と、構造の図への組み込みが要。ボードとスマホのシートを足す前に、ここで形の誤りを止める"}
	}
	final_quality_gate: {
		scope:          "開始のコミット 928460f48 から S-07 の終わりまで（S-08 は記録だけ）"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "security"]
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
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01、S-02）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。サーバーの項目の追加と、DOM のない純粋な計算で、pytest と node のテストで確かめられる。本人の指示（2026-11-13）で Sol を優先する。Sol で失敗や見落としが記録されたときだけ、方針 §1 の4で GPT-6 Astra / high に上げる"}
		"impl-ui":  {task: "実装（S-03〜S-07）", model: "opus", effort: "medium", rationale: "claude。画面と一体の HTML・CSS・画面の JavaScript（欄の部品、構造の図とボードへの組み込み、スワイプ）。本人の指示（2026-11-13）と方針の「実装担当（フロントエンド）× standard」"}
		owner:      {task: "実データの写し（S-08）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。ブラウザーでの確かめは実装ではなく、受け入れの証拠の取得"}
	}
	reviews: {
		spec: {role: "仕様のレビュー", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー（CP-1）", after: "S-04", model: "opus", effort: "medium"}
		gate: {role: "最終品質ゲート", after: "S-07", model: "opus", effort: "medium"}
	}
}
