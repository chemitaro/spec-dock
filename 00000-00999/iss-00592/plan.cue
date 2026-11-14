package spec

// 計画（Issue）。型 specdock/v1。

goal: "構造の図の箱と枠、ボードの札、横の欄の見出しに orca-web の稼働の印を出し、横の欄に「Orca で開く」を置き、配る文書に連携の設定を書く。本物の orca-web に対する写しで確かめる"

steps: {
	"S-01": {title: "node のテスト（T-01）を先に書いて落ちることを確かめ、views/_shared/orca_logic.js（slotWorktree、marksKey、openTarget、themeOf）を D-01 のとおりに作る", realizes: ["R-01", "R-02", "R-04", "F-01", "F-02", "F-03", "F-04"], status: "todo", session: "impl-sol"}
	"S-02": {title: "偽の DOM と偽の部品の node のテスト（T-02）を先に書いて落ちることを確かめ、views/_shared/orca_marks.js（paintOrcaMarks、createOpenButton）と置き場の CSS を D-02、D-04 の createOpenButton のとおりに作る", realizes: ["R-01", "R-02", "R-04", "F-01", "F-02", "F-03", "F-04"], status: "todo", after: ["S-01"], session: "impl-sol"}
	"S-03": {title: "テスト（T-03）を先に書き、構造の図（boxHtml、frameHtml、render、知らせ、onClick・onTap）とボード（card の orca、renderPage の後の描き、onCardClick）に D-03 のとおりに組み込む", realizes: ["R-01", "R-02", "R-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "テスト（T-04）を先に書き、横の欄（作り直さない見出しの行、.pn-hl と表紙の比べ、印、createOpenButton、明暗の見張り、preferTab、refreshOrca）を D-04 のとおりに作る。make lint と uv run pytest（全体）を通す", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-02", "F-03"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "隔離した venv の試しの SpecDock と試しの orca-web で、直す前（開始のコミット）と後の写し（構造の図・ボード・横の欄、1440・1000・390、明暗）、orca-web を止めたときの写し、iframe の読み込みの回数、埋め込みの画面を確かめ、report.md の材料（写しと記録）を Workbench に残す。max と open-button の data-width を写しで決め、変えたらコミットする", realizes: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-03"], status: "todo", after: ["S-04"], session: "impl"}
	"S-06": {title: "配る文書に orca_web の節と前提と見え方を D-05 のとおりに書き、static-inventory.json の sha256 を合わせ、T-05 を通す。report.md に S-05 の写しと記録をまとめる", realizes: ["R-05"], status: "todo", after: ["S-05"], session: "owner"}
}

tests: {
	"T-01": {title: "orca_logic.js（node）：slotWorktree は orca が null・status が ok でない（off、loading、unreachable、orca-unreachable、orca-starting）・forScope が空で null、1つでそのもの、2つで mergedWorktree。marksKey は null で空、同じ形で同じ値、経過の表記・状態・overflow が違えば違う値。openTarget は ok・worktree あり・embed でないときだけ worktreeId と key（ScopeID|id|明暗）、ほかは null と空（status が ok でない、embed、forScope 空、id が空や文字列でない）。themeOf は data-theme の light・dark、ほかは matchMedia", verifies: ["R-01", "R-02", "R-04", "F-01", "F-02", "F-03", "F-04"]}
	"T-02": {title: "orca_marks.js（node、偽の root・置き場・document と、呼び出しを数える偽の buildMarks・renderAgentMarks）：worktree のある置き場だけに renderAgentMarks（size sm、置き場の max、同じ now、onSelect なし）、ない置き場は空。同じ要約で2回目は renderAgentMarks を呼ばない（置き場の子が同じ）。経過の表記が変われば描き直す。status が ok でなくなると空にする。新しく作った置き場には最初の呼び出しで描く。ある置き場の renderAgentMarks の例外でほかの置き場は描かれ、その置き場は空。marks() が null で全部空。createOpenButton：置ける入力で script を1つ（src が <origin>/embed/open-button.js、data-worktree・data-theme・data-size sm）、同じ入力で作り直さない、明暗・worktree・Scope が変われば置き直す、置けない入力で空、reset で覚えを捨てる。HTML の文字列で script を作らない（静的な目印）", verifies: ["R-01", "R-02", "R-04", "F-01", "F-02", "F-03", "F-04"]}
	"T-03": {title: "構造の図とボード（node の HTML の部品と静的な目印）：boxHtml の .gx-marks の末尾と frameHtml の .gx-fh の末尾に置き場（data-orca-scope が esc を通った ID、data-orca-max）、HTML が要約によらない。card は orca が真のときだけ置き場を持ち、下の段を必ず出す。orca がないとき今と同じ HTML。graph.js と board.js が render の後と subscribe の知らせで paintOrcaMarks を呼び、dispose で外し、.sd-orca の中の押しで preferTab(\"agents\") を呼ぶ。SIZE の値が変わっていない。SpecDock の CSS に .orca-mark の色の指定がない", verifies: ["R-01", "R-02", "R-03"]}
	"T-04": {title: "横の欄（node の偽の DOM か静的な目印）：build() の見出しの行に .pn-hl、.pn-orca、閉じるがあり、draw() の2回目で .pn-hl と表紙の HTML が同じなら書き換えない。build() の走り直しで createOpenButton を作り直す。hide() で reset。preferTab は TAB_KEYS にあるキーだけを選ぶ（ないキーで userTab が変わらない）。embed のときボタンを置かない。明暗の見張りを destroy で外す", verifies: ["R-01", "R-02", "R-03", "R-04", "F-03"]}
	"T-05": {title: "配る文書：orca_web の節の書き方と既定の値、ORCA_WEB_READ_ORIGINS、届かないときの見え方の言葉がある。実際の Tailscale の IP（100.64.0.0/10）がない。static-inventory.json の検査（今のテスト）が通る（Python）", verifies: ["R-05"]}
	"T-06": {title: "実機の確かめ（S-05）：report.md に、試しの版とポート、写し（構造の図・ボード・横の欄、1440・1000・390、明暗、直す前と後）、orca-web を止めたときの写し（印もボタンもなく、図とボードが動く）、同じ Scope を選んだまま 30 秒の iframe の読み込みの回数が1、幅 390px でボタンが出ないこと、埋め込みの画面でボタンが出ないこと、要約の GET が 10 秒に1回であることの記録がある", verifies: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-03"]}
}

verification: """
	S-01〜S-04（実装担当）：各手順で足したテストと、関わる既存のテスト（`tests/unit/infra/test_dashboard_*_js.py`、`test_dashboard_screens_js.py`、`test_dashboard_panel_logic_js.py`、`test_dashboard_scope_tabs_js.py` など）。S-02 と S-04 の終わりに `make lint`、`uv run pytest`（全体）。
	S-05（実装担当）：試しの SpecDock（隔離した venv、一時の状態の置き場、ポート 186xx、`--tailscale`、`config.json` の `orca_web.port` を試しの orca-web のポートに）と、試しの orca-web（orca-web の main のチェックアウトの `dist/` を `PORT=88xx`、`ORCA_WEB_TAILSCALE_IP`、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet のオリジン、`ORCA_WEB_SETTINGS_FILE` と `ORCA_WEB_SENDS_DIR` を試し専用の置き場で `node dist/server/main.js`）。headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じる）で写す。常駐の 47800 と 8791 には触れない。試しの2つは、本人の確かめまで止めずに残す。
	S-06（タスク担当）：T-05 と `make lint`、`uv run pytest`（全体）。
	"""

rollback: "PR を戻す。`config.json` に `\"orca_web\": {\"enabled\": false}` を書けば、版を戻さずに連携だけを止められる（印とボタンは出なくなり、CSP も今に戻る）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に写しと記録がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {}
	checkpoints_note: "なし。S-01・S-02 は純粋な決め方と DOM の部品でテストで閉じ、S-03〜S-05 は1つの実装担当が続けて組み込み、写しで確かめる。最終品質ゲートで開始のコミットから全体を見る"
	final_quality_gate: {
		scope:          "開始のコミット 67abbe6c1 から S-06 の終わりまで（PR の前に origin/main を取り込み直したら、その後の最終のコミットでやり直す）"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "security-baseline"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   ["spec-dock/initiatives/00000-00999/iss-00592/report.md"]
		second_opinion: "none"
		reviewer:       "quality-gate-reviewer opus / medium"
	}
	merge:      "owner"
	merge_note: "coordinated の使い方。タスク担当はマージせず、PR と証拠を統括に報告する。統括がマージする"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		"impl-sol": {task: "実装（S-01、S-02）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。決め方の純粋な関数と、偽の DOM で確かめられる描きの部品で、どれも node のテストで閉じる。本人の指示（依頼書、2026-11-14）で、テストで確かめられる純粋な計算は Codex GPT-6.1 Sol / medium"}
		impl:       {task: "実装（S-03〜S-05）", model: "opus", effort: "medium", rationale: "claude。画面（構造の図、ボード、横の欄）と一体の組み込みと、写しでの確かめ。本人の指示（依頼書）で Claude Opus 5.5 / medium"}
		owner:      {task: "配る文書と report（S-06）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。依頼書の「要件・設計・計画と文書は、あなたが書く」による"}
	}
	reviews: {
		spec: {role: "仕様のレビュー（実装の前。after は最初の手順の前を指す印として S-01）", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-06", model: "opus", effort: "medium"}
	}
}
