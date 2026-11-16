package spec

// 計画（Issue）。型 specdock/v1。

goal: "稼働しているエージェントを、どの置き場でも1人1つの印ですべて出し（折り返し、構造の図の箱はその分だけ高くする）、エージェントのタブの5つの小さな点を直す。"

steps: {
	"S-01": {title: "テスト（T-01〜T-04、T-08〜T-11）を先に書いて落ちることを確かめ、D-01（markMax、paintOrcaMarks の max、orcaSlot(id) と呼ぶ側）、D-03（layout.js の ORCA_ROW と orcaRows）、D-04（markRows、rowsKey）、D-07（fromLast と keep）、D-08（lastChoice と欄の足）、D-09（捕捉の聞き手の修飾キー）、D-10（scopeAgents）を作る。data-orca-max や上限を前提にした今のテストを新しい約束に合わせる。関わるテストと make lint を通す", realizes: ["R-01", "R-03", "R-04", "R-05", "R-07", "R-08", "F-01", "F-02", "F-03", "F-04", "F-05"], status: "todo", session: "impl_logic"}
	"S-02": {title: "テスト（T-05〜T-07）を先に書いて落ちることを確かめ、D-02（.sd-orca と .gx-fh の置き場の CSS）、D-05（graph.js の測り、sig、配置し直しの上限、whenStyled の後の測り、edgeAudit の overflow）、D-06（onTap の順）を作る。make lint と uv run pytest（全体）を通す", realizes: ["R-02", "R-03", "R-06", "F-01", "F-02", "F-03"], status: "todo", after: ["S-01"], session: "impl_ui"}
	"S-03": {title: "配る文書（D-11）の reference_cli.md と static-inventory.json の sha256 を直し、テスト（T-12）を足す。make lint と uv run pytest（全体）を通す", realizes: ["R-09"], status: "todo", after: ["S-02"], session: "owner"}
	"S-04": {title: "試しの orca-web と試しの SpecDock の組で、3人以上のエージェントの worktree（なければ要約の差し替え）の、構造の図の箱・ボードの札・横の欄の見出しの全員の印、折り返し、箱の伸び、edgeAudit（overflow を含む）、5点の直しの動きを、1440・1000・390 の幅と明暗で確かめ、report.md に残す（T-13）。本人が見る URL を報告し、本人の確かめまで残す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "F-01"], status: "todo", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "markMax と paintOrcaMarks（node、偽の置き場と偽の部品）：markMax が agents 3 → 3、8 → 8、0 → 1、並びでない・null・worktree なし → 1。paintOrcaMarks が、3人と8人の worktree で buildMarks と renderAgentMarks の両方に max 3・8 を渡し（置き場に data-orca-max がなくても）、合わせた2つの worktree（2人と3人）で max 5。部品がない・状態が ok でない・例外のとき置き場を空にする（今のまま）。鍵が同じなら描き直さない（今のまま）", verifies: ["R-01", "F-03"]}
	"T-02": {title: "置き場の HTML（node と静的）：orcaSlot(id) が `<span class=\"sd-orca\" data-orca-scope=\"…\"></span>` で data-orca-max を持たず、esc する。graph.js の boxHtml・frameHtml、panel.js の header、parts.js の card が orcaSlot に id だけを渡す。ダッシュボードの .js に data-orca-max と orcaMax が残らない", verifies: ["R-01"]}
	"T-03": {title: "layout の orcaRows（node、dashboard_graph_check.mjs）：入れ子で、ある Issue の箱に3行 → 高さが 88 + 36（ほかの箱と同じ grow の分を除いて）、幅 178。ある枠に2行 → headY2 − y1 が渡さないときより 18 大きく、枠の中の箱がその分下がる。木で、Issue の箱と木の枠の箱に2行 → 高さが 18 大きい。行の数が0・1・負・小数・文字、orcaRows がない・オブジェクトでない → 渡さないときと同じ結果（nodes・groups・edges・width・height）。small・context・packing などの代表の構造で、多くの箱と枠に2〜4行を渡した routeLayout の audit の違反が0（入れ子と木、幅 1400 と 374、showDone と deps の組）。ORCA_ROW が 18 で、SIZE の値が変わらない", verifies: ["R-03"]}
	"T-04": {title: "markRows と rowsKey（node）：[] → 0、[0,0,0] → 1、[0,0,18,18,36] → 3、並びの順によらない、1〜4px の差は同じ行、数でない値を除く。rowsKey が2以上の項目だけを id の順に `id:n` で連ね、同じ中身なら同じ文字列、1以下だけなら \"\"", verifies: ["R-03", "F-01", "F-02"]}
	"T-05": {title: "構造の図の測りと配置し直し（静的な目印）：render の sig に V.orcaKey、buildWorld が routeLayout に orcaRows: V.orcaRows を渡す、paintOrca が paintOrcaMarks と refreshOrca の後で measureOrcaRows と rowsKey を比べ、V.orcaPass < 2 のときだけ render を呼び、終わりに V.orcaPass を戻す。measureOrcaRows が .gx-box の :scope > .gx-marks > .sd-orca と .gx-frame の :scope > .gx-fh > .sd-orca を測り、offsetParent が null の置き場と例外の置き場で前の値を保つ。whenStyled の後に paintOrca。dispose が orcaRows・orcaKey・orcaPass を戻す。edgeAudit の返り値に overflow", verifies: ["R-03", "F-01", "F-02", "F-03"]}
	"T-06": {title: "置き場の CSS（静的）：app.css の .sd-orca が inline-flex・flex: 0 1 auto・min-width: 0・max-width: 100%・margin-left: auto を持ち、.sd-orca:empty の規則が残る。graph.css の .gx .gx-fh .sd-orca の max-width: 50%。SpecDock の CSS に .orca- の選びがない（今のテスト）", verifies: ["R-02"]}
	"T-07": {title: "onTap の順（静的）：onTap の中で、closest(\".sd-orca\") の判定が isPhone() && V.sel === id の判定より前にあり、その中で select(id) が preferTab(\"agents\") より前で return する", verifies: ["R-06"]}
	"T-08": {title: "覚えからの選びの keep（node、偽の env）：agent のない env で、覚えの last A が agents（A と B）にいるとき、agentsTab が keep を (\"agent\", \"A\") で1回呼び、iframe が A。1人（A だけ）でも (\"agent\", \"A\")。問い合わせに agent=A があれば keep を呼ばない。last の A が覚えの gone にあれば keep は (\"agent\", \"gone:A\") で iframe がない。last の A が agents にいなければ keep は gone:A（今のまま）。keep の後の同じ Scope の詳しい画面の env の param が A を返す（pageEnv と偽の replaceParam）", verifies: ["R-04", "F-04"]}
	"T-09": {title: "lastChoice と欄の足（node）：lastChoice が、別の Scope の覚え → null、同じ Scope の last A → \"A\"、last A が gone → \"gone:A\"、last がなく gone に X → \"gone:X\"、何もない → null。欄の偽の DOM（PANEL_DOM）で、欄の Map が空で、覚えが同じ Scope の last A のとき、概要のタブでも足の「詳しい画面」と「新しいタブで開く」の href に agent=A。gone なら agent=gone%3AA。覚えが別の Scope なら agent がない。欄の Map に agent=B があれば B", verifies: ["R-05", "F-04", "F-05"]}
	"T-10": {title: "帯の捕捉の聞き手の修飾キー（node、偽の root）：button 0 で修飾キーなしの押しで forgetGone が効き（覚えの gone が空、picked と last がその id）、metaKey・ctrlKey・shiftKey・altKey のそれぞれと button 1 では覚えの gone・picked・last が変わらない。どの押しでも preventDefault を呼ばない", verifies: ["R-07"]}
	"T-11": {title: "scopeAgents の並びでない agents（node）：agents がオブジェクト・null・欠け・文字の worktree が invalid 1 で agents が空、invalidIds が空。並びの worktree（使える2人）と並びでない worktree が混ざると agents 2、invalid 1。その要約で wanted が A のとき agentsVisibility の理由が shape、agentsState の後で覚えの gone に A がない", verifies: ["R-08"]}
	"T-12": {title: "配る文書（Python）：reference_cli.md の連携の節に、全員の印（まとめない）、折り返し、構造の図の箱と枠の見出しが高くなり幅は変わらないこと、欄の足のリンクが選びか覚え（gone:<id> を含む）を持つこと、修飾キーつきの押しが元の画面の覚えを変えないこと、orca-shape の意味に agents が並びでない worktree があること。実際の Tailscale の IP と利用者の絶対パスがない（今のテスト）。static-inventory.json の sha256 が合う（今のテスト）", verifies: ["R-09"]}
	"T-13": {title: "実機の確かめ（S-04、headless Chrome と CDP）：report.md に、試しの組の版とポート、直す前と後の写し（構造の図・ボード・横の欄、1440・1000・390、明暗）、3人以上の worktree の各置き場の .orca-mark の数と orca-mark--more のなさ、置き場の右端が箱・札・見出しを越えないことの計測、2行以上の箱と枠の高さと specdockEdgeAudit()（overflow を含む）の0、行の数が変わったときの配置し直しの回数（同じ要約の繰り返しで増えない）、5点の直しの動き（欄の開き直し→詳しい画面→帯の今の相手の押しで iframe の読み込みが増えない、概要のタブの足のリンクの agent、390 の選んだ箱の印の2回目の押しでエージェントのタブ、Cmd の押しで元の画面の覚えが変わらない、agents が並びでない要約の差し替えで形の違いの知らせ）がある", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "R-08", "F-01"]}
}

verification: """
	テストの基準：開始のコミット `16f0cf122`（main）の `uv run pytest -q` は 3912 passed / 7 skipped / 0 failed（iss-00601 の report.md、同じコミットの別の worktree で 2026-11-15 に計った値）。これを基準とし、実装担当は全体の基準を取り直さない。
	S-01（実装担当 impl_logic）：T-01〜T-04、T-08〜T-11 と、関わる今のテスト（`tests/unit/infra/test_dashboard_orca_*.py`、`test_dashboard_agents_*.py`、`test_dashboard_scope_tabs_js.py`、`tests/unit/presentation/test_dashboard_graph_js.py`）、`make lint`。
	S-02（実装担当 impl_ui）：T-05〜T-07 と、関わる今のテスト（`test_dashboard_orca_views_js.py`、`test_dashboard_screens_js.py`、`test_dashboard_shell_polish.py`、`test_dashboard_graph_js.py`）。終わりに `make lint`、`uv run pytest`（全体）。
	S-03（タスク担当）：T-12、`make lint`、`uv run pytest`（全体）。
	S-04（タスク担当）：試しの組（下）と headless Chrome（CDP）。記録と写しは worktree の `.workbench/iss-00602/`、要るものを report.md に写す。
	試しの組（統括の依頼書）：
	- 試しの SpecDock：S-03 の HEAD から作った wheel を隔離した venv に入れ、一時の状態の置き場（`XDG_CONFIG_HOME` も一時の置き場にし、そこの `spec-dock/config.json` の `orca_web.port` を試しの orca-web に向ける）、別のポート、`--tailscale` で `dashboard serve`。登録簿は道具の環境の状態の置き場の写し（サーバーの記録とログを除く）。
	- 試しの orca-web：orca-web の main のチェックアウトの `dist/` を別のポートで、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet の2つのオリジン、`ORCA_WEB_SETTINGS_FILE` を試し専用の置き場、`sendEnabled` は false。orca-web のファイルは変えない。
	- 3人以上のエージェントがいる worktree が実データになければ、CDP の Fetch で要約の応答を差し替える（印の数を変える）。送信はしない。
	- 常駐のダッシュボード（47800）と常駐の orca-web（8791）の設定は変えず、止めない。
	- 本人が見る試しの URL（tailnet）を報告に書き、本人の確かめまで止めずに残す。止め方を report.md と報告に書く。
	"""

rollback: "PR を戻す。版を戻さずに印とタブを消すときは、`config.json` に `\"orca_web\": {\"enabled\": false}` を書く（印もタブも消え、構造の図は今の高さに戻る）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に実機の確かめ（T-13）の記録がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"C-1": {
			last_step: "S-01"
			range:     "開始のコミット `16f0cf122` から S-01 の HEAD まで"
			reviewer:  "code-reviewer Opus 5.5 / medium（方針の strict の行）"
			reason:    "S-01 は別の提供元（Codex）の実装担当が、選びの直し（違う相手が開く道を閉じる部分）と配置の入力を作る。S-02 の画面がその上に乗るので、画面を作る前に確かめる"
		}
	}
	final_quality_gate: {
		scope:          "開始のコミット `16f0cf122` から S-03 の終わりまで（S-04 は report.md の記録だけ。仕様は Git で扱わない）。PR の前に origin/main を取り込んだら、その最終のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "integration-boundaries", "compatibility-regression", "performance"]
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
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の「タスク担当 × strict」から選んだ（依頼書 task_a02f6618c98b）"}
		impl_logic: {task: "実装（S-01）", model: "GPT-6.1 Sol", effort: "medium", rationale: "codex。純粋な関数と node のテストで確かめられる部分（選びの直し、配置の入力、置き場の max）。本人の指示（依頼書：テストで確かめられる部分は Codex GPT-6.1 Sol / medium をなるべく使う）と方針の「実装担当（テストで確かめられる実装）× strict」。Codex が chat-scratch の symlink の拒否か確認の画面で止まったら、待たずに worker-stop し、HEAD と未コミットを確かめて impl_ui の値（Claude Opus 5.5 / high）に切り替える（統括が了承済み。逸脱として report.md に書く）"}
		impl_ui:    {task: "実装（S-02）", model: "Opus 5.5", effort: "high", rationale: "claude。画面と一体の部分（描いた印の測り、配置し直しの輪、CSS の折り返し、押しの順）。本人の指示（依頼書）と方針の「実装担当（フロントエンドの設計と実装）× strict」"}
		owner:      {task: "配る文書（S-03）と実機の確かめ（S-04）", model: "Opus 5.5", effort: "high", rationale: "タスク担当（このセッション）。文書はタスク担当が書く（依頼書と方針 §2 の注）。S-04 は試しの組の起動と写しの取得で、実装ではない"}
	}
	reviews: {
		spec:       {role: "仕様のレビュー（実装の前。after は最初の手順の前を指す印として S-01）。spec-reviewer Opus 5.5 / high と、2人目 ChatGPT GPT-6 / Extra High（chatgpt-spec-review-strict）", after: "S-01", model: "Opus 5.5", effort: "high"}
		checkpoint: {role: "区切りのレビュー C-1", after: "S-01", model: "Opus 5.5", effort: "medium"}
		gate:       {role: "最終品質ゲート（主。2人目は ChatGPT GPT-6 / Extra High）", after: "S-03", model: "Opus 5.5", effort: "high"}
	}
}
