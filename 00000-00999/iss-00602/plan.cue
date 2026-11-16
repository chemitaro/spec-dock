package spec

// 計画（Issue）。型 specdock/v1。

goal: "iss-00601 が調べたエージェントのタブと構造の図の印の押しの5つの小さな点を、それぞれ再現するテストを先に書いてから直す。"

steps: {
	"S-01": {title: "テスト（T-01〜T-05）を先に書いて、直す前の main で落ちる（各点を再現する）ことを確かめ、D-01（onTap の順）、D-02（fromLast と keep）、D-03（lastChoice と欄の足）、D-04（捕捉の聞き手の修飾キー）、D-05（scopeAgents）を作る。今のテストの、直した動きを前提にしない目印（iss-00593 の D-04 の修飾キーによらない forgetGone など）を新しい約束に合わせる。関わるテストと make lint を通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02", "F-03"], status: "done", session: "impl"}
	"S-02": {title: "配る文書（D-06）の reference_cli.md と static-inventory.json の sha256 を直し、テスト（T-06）を足す。make lint と uv run pytest（全体）を通す", realizes: ["R-06"], status: "done", after: ["S-01"], session: "owner"}
	"S-03": {title: "試しの orca-web と試しの SpecDock の組で、5点の直しの動き（T-07）を、直す前（main）と後で、1440・1000・390 の幅と明暗の写しとともに確かめ、report.md に残す。本人が見る URL を報告し、本人の確かめまで残す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01"], status: "done", after: ["S-02"], session: "owner"}
	"S-04": {title: "最終品質ゲートの P1（FQG-00602-01）の直し：T-03 の footChoice と欄の足の場面のテストを先に書いて落ちることを確かめ、D-03 の footChoice と panel.js の足を直す。関わるテストと make lint を通す", realizes: ["R-02", "F-01"], status: "doing", after: ["S-03"], session: "impl_fix"}
	"S-05": {title: "配る文書（D-06）の「選び」の文を直し（欄の選びもいなくなっていれば gone:<id>）、static-inventory.json と T-06 を合わせる。実機で、欄の Map に A がある場面（T-07 の 2'）で足のリンクが gone:<id> になり、A が戻っても新しいタブで A が開かないことを確かめ、report.md に残す", realizes: ["R-02", "R-06", "F-01"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "onTap の順（静的な目印、test_dashboard_orca_views_js.py）：onTap の中で、closest(\".sd-orca\") の判定が isPhone() && V.sel === id の判定より前にあり、その節の中で select(id) が preferTab(\"agents\") より前で、節が return で終わる。直す前の graph.js でこの目印が落ちる", verifies: ["R-03"]}
	"T-02": {title: "覚えからの選びの keep（node、偽の env、test_dashboard_agents_tab_js.py）：agent のない欄の env（Map が空）と詳しい画面の env（pageEnv と偽の replaceParam）のそれぞれで、覚えの last A が agents（A と B）にいるとき、agentsTab が keep を (\"agent\", \"A\") で1回呼び、iframe が A（直す前は keep を呼ばずに落ちる）。詳しい画面では keep の後の同じ env の param が A を返し、paramLink の A のリンクの道が今の route と同じ agent を持つ。1人（A だけ）でも (\"agent\", \"A\")。問い合わせか Map に agent=A があれば keep を呼ばない。last の A が覚えの gone にある、または agents にいなければ keep は (\"agent\", \"gone:A\") で iframe がない（F-01）。理由が shape のとき keep を呼ばない（F-03）", verifies: ["R-01", "F-01", "F-03"]}
	"T-03": {title: "lastChoice と欄の足（node、test_dashboard_agents_logic_js.py と test_dashboard_orca_views_js.py の PANEL_DOM）：lastChoice が、別の Scope の覚え → null、同じ Scope の last A → \"A\"、last A が gone → \"gone:A\"、last がなく gone に X と Y（この順）→ \"gone:X\"、何もない → null。欄の偽の DOM で、欄の Map が空で覚えが同じ Scope の last A のとき、概要のタブでも足の「詳しい画面」と「新しいタブで開く」の href に agent=A（直す前は agent がなく落ちる）。A が gone なら agent=gone%3AA。覚えが別の Scope なら agent がない。欄の Map に agent=B があれば B。footChoice が、mapped null → lastChoice と同じ、mapped gone:X → gone:X、mapped A で同じ Scope の覚えの gone に A → gone:A、覚えが別の Scope なら A、gone にない A → A。欄の偽の DOM で、エージェントのタブで A を選び（Map に A）、概要のタブに替えた後の要約で A がいなくなると、足の2つのリンクが agent=gone%3AA（直す前は agent=A で落ちる）", verifies: ["R-02", "F-01", "F-02"]}
	"T-04": {title: "帯の捕捉の聞き手の修飾キー（node、偽の root、test_dashboard_agents_tab_js.py）：覚えに gone と picked と last と drift を入れた状態で、button 0 で修飾キーなしの押しは forgetGone が効き（gone が空、picked と last がその id、drift が null）、metaKey・ctrlKey・shiftKey・altKey のそれぞれと button 1 の押しでは gone・picked・last・drift が変わらない（直す前は変わって落ちる）。どの押しでも preventDefault を呼ばない", verifies: ["R-04"]}
	"T-05": {title: "scopeAgents の並びでない agents（node、test_dashboard_agents_logic_js.py と test_dashboard_agents_tab_js.py）：agents がオブジェクト・null・欠け・文字の worktree のそれぞれで invalid 1、agents 空、invalidIds 空（直す前は invalid 0 で落ちる）。並びの worktree（使える2人）と並びでない worktree が混ざると agents 2、invalid 1。並びでない worktree だけの要約で wanted が A のとき、agentsVisibility の理由が shape、agentsState の後で覚えの gone に A がなく、agentsTab が keep を呼ばず orca-shape の知らせを返す。直った要約（A がいる）で同じ env の作り直しが A を開く", verifies: ["R-05", "F-03"]}
	"T-06": {title: "配る文書（Python、test_issue593_agents_docs.py）：reference_cli.md のエージェントのタブの節に、欄の足のリンクが選びか覚え（gone:<id> を含む）を持つこと、最後に開いた相手を問い合わせに書くこと、修飾キーつきの押しが元の画面の覚えを変えないこと、orca-shape の意味に agents が並びでない worktree があること。実際の Tailscale の IP と利用者の絶対パスがない（今のテスト）。static-inventory.json の sha256 が合う（今のテスト）", verifies: ["R-06"]}
	"T-07": {title: "実機の確かめ（S-03 と S-05、headless Chrome と CDP）：report.md に、試しの組の版とポート、直す前（main の wheel）と後の比べで、(1) 欄の開き直し→足の詳しい画面→帯の今の相手の押しで iframe の読み込みの回数と入力欄の書きかけ、(2) A がいなくなり B だけの要約（CDP の Fetch の差し替え）で概要のタブの欄の足の「新しいタブで開く」の道と、その道をエージェントのタブで開いたときに B が自動で開かないこと、(2') 欄の Map に人の選び A があるまま概要のタブで A がいなくなったとき足のリンクが gone:A を持ち、A が戻った後にその道を新しいタブで開いても A が開かないこと（S-05）、(3) 390px で選んだ箱の印の2回目の押しの後の道と欄のタブ、印の外の押しで詳しい画面、(4) 帯の別の相手の Cmd の押しの後で、元のページで欄を開き直したときの相手、(5) agents をオブジェクトに差し替えた要約で orca-shape の知らせと、外して同じ相手に戻ること、の記録と、1440・1000・390 の幅と明暗の写しがある", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01"]}
}

verification: """
	テストの基準：開始のコミット `16f0cf122`（main）の `uv run pytest -q` は 3912 passed / 7 skipped / 0 failed（iss-00601 の report.md、同じコミットの別の worktree で 2026-11-15 に計った値）。これを基準とし、実装担当は全体の基準を取り直さない。
	S-01（実装担当 impl）：T-01〜T-05 を先に書き、直す前に落ちることを記録する。関わる今のテスト（`tests/unit/infra/test_dashboard_agents_logic_js.py`、`test_dashboard_agents_tab_js.py`、`test_dashboard_orca_views_js.py`、`test_dashboard_scope_tabs_js.py`、`test_dashboard_panel_logic_js.py`、`test_dashboard_agents_boundary.py`、`test_dashboard_screens_js.py`）と `make lint`。
	S-02（タスク担当）：T-06、`make lint`、`uv run pytest`（全体）。
	S-03（タスク担当）：試しの組（下）と headless Chrome（CDP）。記録と写しは worktree の `.workbench/iss-00602/`、要るものを report.md に写す。
	試しの組（統括の依頼書）：
	- 試しの SpecDock：S-02 の HEAD から作った wheel（と、比べのための main `16f0cf122` の wheel）を隔離した venv に入れ、一時の状態の置き場（`XDG_CONFIG_HOME` も一時の置き場にし、そこの `spec-dock/config.json` の `orca_web.port` を試しの orca-web に向ける）、別のポート、`--tailscale` で `dashboard serve`。登録簿は道具の環境の状態の置き場の写し（サーバーの記録とログを除く）。
	- 試しの orca-web：orca-web の main のチェックアウトの `dist/` を別のポートで、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet のオリジン、`ORCA_WEB_SETTINGS_FILE` を試し専用の置き場、`sendEnabled` は false。orca-web のファイルは変えない。
	- 2人以上のエージェントがいる worktree が実データになければ、CDP の Fetch で要約の応答を差し替える。送信はしない（入力欄に書くだけで送らない）。
	- 常駐のダッシュボード（47800）と常駐の orca-web（8791）の設定は変えず、止めない。
	- 本人が見る試しの URL（tailnet）を報告に書き、本人の確かめまで止めずに残す。止め方を report.md と報告に書く。
	"""

rollback: "PR を戻す。版を戻さずにエージェントのタブを消すときは、`config.json` に `\"orca_web\": {\"enabled\": false}` を書く（タブも印も消える）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に実機の確かめ（T-07）の記録がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"C-1": {
			last_step: "S-01"
			range:     "開始のコミット `16f0cf122` から S-01 の HEAD まで"
			reviewer:  "code-reviewer Opus 5.5 / medium（方針の strict の行）"
			reason:    "S-01 は別の提供元（Codex）の実装担当が、選びの直し（違う相手が開く道を閉じる部分）を作る。文書と実機の確かめの前に確かめる"
		}
	}
	final_quality_gate: {
		scope:          "開始のコミット `16f0cf122` から S-05 の終わりまで（attempt 1 は S-02 の終わり `80d5aba3f`）（S-03 は report.md の記録だけ。仕様は Git で扱わない）。PR の前に origin/main を取り込んだら、その最終のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "integration-boundaries", "compatibility-regression"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "chatgpt"
		reviewer:       "quality-gate-reviewer Opus 5.5 / high（主）、2人目 ChatGPT GPT-6 / Extra High（chatgpt-final-quality-gate-strict。取れないとき GPT-6 Astra / high）"
	}
	merge:      "owner"
	merge_note: "coordinated の使い方。タスク担当はマージせず、PR と証拠を統括に報告する。統括がマージする"
}

execution: {
	sessions: {
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の「タスク担当 × strict」から選んだ（依頼書 task_a02f6618c98b）"}
		impl:  {task: "実装（S-01）", model: "GPT-6.1 Sol", effort: "medium", rationale: "codex。5点の直しは、純粋な関数と node の偽の env・偽の DOM・静的な目印のテストで確かめられる（D-01 の onTap も3行の並べ替えで、静的な目印と実機で確かめる）。本人の指示（依頼書：テストで確かめられる部分は Codex GPT-6.1 Sol / medium をなるべく使う）と方針の「実装担当（テストで確かめられる実装）× strict」。Codex が chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに worker-stop し、HEAD と未コミットを確かめて Claude Opus 5.5 / high に切り替える（統括が了承済み。逸脱として report.md に書く）"}
		impl_fix: {task: "最終品質ゲートの P1 の直し（S-04）", model: "Opus 5.5", effort: "high", rationale: "claude。impl（Codex GPT-6.1 Sol）は Orca の chat-scratch の symlink の拒否で動かず、計画の取り決め（統括の了承済み）で Claude Opus 5.5 / high に切り替えた。同じ扱い"}
		owner: {task: "配る文書（S-02、S-05）と実機の確かめ（S-03、S-05）", model: "Opus 5.5", effort: "high", rationale: "タスク担当（このセッション）。文書はタスク担当が書く（依頼書と方針 §2 の注）。S-03 は試しの組の起動と写しの取得で、実装ではない"}
	}
	reviews: {
		spec:       {role: "仕様のレビュー（実装の前。after は最初の手順の前を指す印として S-01）。spec-reviewer Opus 5.5 / high と、2人目 ChatGPT GPT-6 / Extra High（chatgpt-spec-review-strict）", after: "S-01", model: "Opus 5.5", effort: "high"}
		checkpoint: {role: "区切りのレビュー C-1", after: "S-01", model: "Opus 5.5", effort: "medium"}
		gate:       {role: "最終品質ゲート（主。2人目は ChatGPT GPT-6 / Extra High）", after: "S-05", model: "Opus 5.5", effort: "high"}
	}
}
