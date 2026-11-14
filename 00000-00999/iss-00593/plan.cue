package spec

// 計画（Issue）。型 specdock/v1。

goal: "横の欄と詳しい画面の「エージェント」のタブで、その Scope の worktree のエージェントを選び、orca-web の詳細とチャットを使えるようにする。SpecDock は相手の選びだけを受け持ち、書き込みに関わらない。"

steps: {
	"S-01": {title: "node のテスト（T-01〜T-03）を先に書いて落ちることを確かめ、views/_shared/agents_logic.js（scopeAgents、agentsVisibility、pickAgent、stripForm、agentFrame、覚えの関数、AGENT_SANDBOX）を D-01 のとおりに作る。関わるテストと make lint を通す", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-07", "F-01", "F-02", "F-04", "F-05", "F-07", "F-08"], status: "done", session: "impl_ui"}
	"S-02": {title: "テスト（T-04〜T-06）を先に書いて落ちることを確かめ、agents_tab.js、scope_tabs.js（agents の行、visibleTabs、keep、frameBar の export）、panel.js、scope.js（3つの部分と dispose）、app.js（orcaProblem、replaceParam、明暗）、CSS を D-02〜D-06 のとおりに作る。今のタブのテスト（TAB_KEYS など）を新しい並びに合わせる", realizes: ["R-01", "R-02", "R-03", "R-05", "R-06", "R-07", "F-01", "F-03", "F-05", "F-06", "F-07", "F-08"], status: "done", after: ["S-01"], session: "impl_ui"}
	"S-03": {title: "テスト（T-07、T-08）を先に書いて落ちることを確かめ、書き込みに関わらないことの静的なテスト（D-07）と配る文書（D-08）と static-inventory.json を作る。make lint と uv run pytest（全体）を通す", realizes: ["R-04", "R-08"], status: "done", after: ["S-02"], session: "impl_ui"}
	"S-04": {title: "試しの orca-web と試しの SpecDock の組で、写し（1440・1000・390、明暗、直す前と後）、sandbox の値での読み・送信・Orca で開く・新しいタブ、確かめ専用の宛先への送信とネットワークの記録、60 秒の本文の残り、Scope を変えたとき・いなくなったとき・iframe の中で移ったとき、届かないとき・埋め込みのときを確かめ、report.md に残す（T-09）", realizes: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "F-01", "F-02", "F-03", "F-05", "F-06", "F-08"], status: "done", after: ["S-03"], session: "owner"}
}

tests: {
	"T-01": {title: "agentsVisibility の表（node）：off で problem なし → 出さない。off で problem あり・records 1 → 出す、理由 config。records 0 → どの status でも出さない。loading・unreachable・orca-unreachable・orca-starting で records 1 → 出す、理由はその status。ok・agents 2 → 出す、理由 null。ok・agents 0・wanted なし → 出さない。ok・agents 0・wanted あり（id と gone:id）→ 出す。ok・agents 0・wanted なし・goneIds が空でない → 出す。ok・agents 0・invalid 1 → wanted や goneIds の有無によらず出す、理由 shape。ok・agents 1・invalid 1 → 理由 null。ok・wanted が invalidIds にある → 出す、理由 shape。embed 真・ok・agents 1 → 出す、理由 embed。embed 真・problem あり → 理由 config。知らない status → 出さない", verifies: ["R-01", "F-04", "F-05", "F-07"]}
	"T-02": {title: "pickAgent の表と scopeAgents（node）：wanted なし・1人 → その人と remember その id。wanted なし・2人 → 選ばない、gone false。wanted が id にある → その人、remember null（人数が増えても同じ）。wanted があり agents にない（残り1人を含む）→ selected null、gone true、remember gone:<id>。wanted が gone:<id> → 同じ id が agents に戻っても selected null、gone true、remember null、addGone その id。wanted が goneIds にある（同じ id が agents に戻った、またはほかのタブの間に覚えに足された）→ gone true、selected null、remember gone:<id>、addGone null。wanted なし・goneIds が空でない・1人 → 自動で選ばず gone true。wanted があり agents にない → addGone その id。stripForm：1人で選ばれていれば label、1人で gone か選びなしなら switch、2人以上は switch。覚えの関数：memoryFor が別の Scope で gone・picked・drift・last を捨てる、noteShown が last を書き、forgetGone が last も選んだ id にする、noteGone の stale が picked と同じ id を足さず stale でなければ足して picked を消す、forgetGone が gone と drift を捨て picked を覚える、noteDrift。scopeAgents：返り値が {agents, invalid, invalidIds}、worktree の順と agents の順、detail が /embed/agent?id= と encodeURIComponent(id) と完全に同じ項目だけ（id が A で detail が B を指す、別の道、& を含む、文字列でない、id がない項目を除いて invalid に数える。: や _ を含む本物の形の id は通る）、同じ id は最初だけ（invalid に数えない）、branch と agentType の null、並びでない入力は空", verifies: ["R-02", "R-05", "F-02"]}
	"T-03": {title: "agentFrame と AGENT_SANDBOX（node）：src が origin と detail をそのまま連ね &theme=<明暗> で終わる（id を符号にし直さない）、theme が light・dark でなければ null、origin がなければ null、title が種類とブランチ（null なら「種類不明」「ブランチ不明」）を持つ、同じ入力で同じ値。AGENT_SANDBOX が D-01 の値で、allow-forms と allow-top-navigation を含まない", verifies: ["R-03", "R-04", "R-07"]}
	"T-04": {title: "agentsTab の HTML（node、差し替えた ctx.orca と構造）：drift の Scope と id で iframe がなく orca-agent-drift の知らせと data-agent-pick の戻すリンク、shape の知らせに件数。1人で iframe の文字列が D-03 の形（sandbox、referrerpolicy、title、theme）で、keep が agent=<id> で1回呼ばれる。同じ選びのまま、ほかのエージェントを足す・消す・並べ替える・印の mark を変えると中身の文字列が同じ。明暗・選んだ相手のブランチ・種類を変えると文字列が変わる。gone・選ぶの知らせに iframe がない。理由ごとの知らせの data-code と言葉（unreachable に origin、config に problem と config.json、embed に withoutEmbed のリンク）。中身に /api/ の道と postMessage がない。sendEnabled に当たる入力がなく、送れるかで文字列が変わらない", verifies: ["R-03", "R-05", "R-06", "R-07", "F-01", "F-05", "F-06", "F-07", "F-08"]}
	"T-05": {title: "タブの並びと env（node）：TAB_KEYS が explanation、agents、summary、… の8つ。visibleTabs が条件で agents を出し入れし、ほかの7つはいつも残る。count が理由 null のとき人数、ほかは null。agentsState が同じ env で1回だけ決める。pageEnv の keep が ctx.replaceParam を呼び、以後の param と paramLink が新しい問い合わせを使う。panelEnv の keep が params の Map を書き換え、ページの道を変えない。agentsState が scopeAgents の返り値を分けて受け（agents が並び）、ふつうの要約で visible・count・render が人数と選びを正しく返す（つないだ正常系）。選んだ相手の項目だけ形が違うと理由 shape で覚えにも選びにも足さず、直った要約で同じ相手に戻る。agentsState と visible・count は keep を呼ばず、render（agentsTab）だけが呼ぶ。agentsState が、状態 ok で wanted が agents にないとき keep を呼ばずに覚えに足し、その後同じ id が戻っても render が gone を返す。worktree の記録が ok でないときと全部が形違いのときは覚えに足さない。選びのない env（欄を閉じて開き直す、agent のない道）で mem.last を選びとして使い、last がいなくなって別の1人だけ残っても自動で開かず gone になる。いなくなった覚え：gone を見た Scope で覚え、同じ Scope の別の env（欄から詳しい画面、欄の閉じと開き直し、戻る操作で wanted が前の id か null）でも gone のまま、別の Scope の agentsState で捨てる、forgetGone の後は選んだ id が開く。paintAgentList が stripForm の label で span、switch で data-agent-pick と paramLink の a を描き（gone で残り1人でも a で aria-current なし）、押しの捕捉で forgetGone を呼び既定の動きを止めない、aria-current、esc、帯の文字列が同じなら置き場を書き換えない、buildMarks が同じなら renderAgentMarks を呼ばない、marks が null や例外でも帯を描く、形の違う N件の注、iframe の load の2回目で同じ聞き手の中で noteDrift と redraw を呼び1回目では呼ばない、redraw がなければ iframe を外す、聞き手を二重に付けない（偽の root と部品）", verifies: ["R-01", "R-02", "R-05", "R-07", "F-08"]}
	"T-06": {title: "画面の組み込み（静的な目印と node）：panel.js が visibleTabs のキーを pickTab に渡し、agents のとき paintAgentList を redraw つきで呼び、ctx.orca を購読し hide と destroy で外す。scope.js が .sd-scope-top・.sd-tabs-row・.sd-tabpanel の3つと data-scope を持ち、同じ Scope で中身の文字列が同じなら .sd-tabpanel を書き換えず、別の Scope で全体を書き換え、中身の後に帯を redraw つきで描き、dispose で購読を外す。app.js の ctx に orcaProblem・replaceParam・current があり、replaceParam が history.replaceState を使い描き直さず、呼んだ描きの route が今の state.route と違えば書かない、navigate が Scope か agent の違う移りでだけ詳しい内容を待つ前に iframe.sd-agent を外して覚えた中身を捨て（次の描きで置き直す）、Scope も agent も変わらない移り（ボードの絞り込み、focus、今のタブや今の相手の押し）では外さない、同じ Scope の問い合わせだけの移りは今の詳しい内容で先に描く、知らせの描き直しが ctx.current() を使い移動の待ちの間は描かない（FQG-001 の道の再現：人が B を押した待ちの間に B が消えて A だけの知らせが来ても A の iframe を置かない）、prefers-color-scheme の change と setTheme で render を呼ぶ。panel.css・scope.css・scope_tabs.css の .sd-agent と [data-tab=\"agents\"] の規則と、.sd-scope-top の display: contents。新しい色の値（# や rgb の直書き）を足していない", verifies: ["R-03", "R-05", "R-06", "R-07", "F-03"]}
	"T-07": {title: "書き込みに関わらないこと（Python、tests/unit/infra/test_dashboard_agents_boundary.py）：D-07 の glob（core/orca*.js、views/_shared/orca_*.js、views/_shared/agents_*.js）で集めた画面のファイル（agents_logic.js・agents_tab.js・core/orca.js があること）に書き込みの口の道と postMessage がない、ダッシュボードの .js の postMessage が core/embed.js の window.parent への1か所だけ、AGENT_SANDBOX の値", verifies: ["R-04"]}
	"T-08": {title: "配る文書（Python）：reference_cli.md にエージェントのタブの節があり、出す条件、sendEnabled、sandbox の値、iframe の中の移りの残るリスク（または orca-web の iss-00037 で移りがなくなったこと）と、知らせの10の data-code（orca-loading、orca-unreachable、orca-shape、orca-orca-unreachable、orca-orca-starting、orca-config、orca-embed、orca-agent-gone、orca-agent-choose、orca-agent-drift）のそれぞれの説明を含み、実際の Tailscale の IP（100.64.0.0/10）と利用者の絶対パスを含まない。static-inventory.json の sha256 が合う（今の inventory のテスト）", verifies: ["R-08"]}
	"T-09": {title: "実機の確かめ（S-04、headless Chrome と CDP）：report.md に、試しの組の版とポート、直す前と後の写し（横の欄と詳しい画面、1440・1000・390、明暗）、iframe の下端と二重のスクロールのなさの計測、sandbox の値での会話の読み・送信・Orca で開く・PR のリンクの新しいタブ、確かめ専用の宛先への1回の送信と送信の口の要求の frameId がすべて iframe であることと親の frame の orca-web への要求が要約の GET と /embed/ の下の静的な部品の読み込みだけであること、iframe の中の親か子のリンクで移った知らせと戻すことと、移った先の load と送る欄の有効化（GET /api/send/status の応答）の順の記録（確かめ専用の宛先のエージェントに親か子がなければ、CDP でその iframe の中の文書を別の /embed/agent?id= に移して代わりにする）、60 秒の本文の残りと iframe の読み込みの回数、Scope を変えたときの iframe の消え、要約の差し替え（CDP の Fetch）でのいなくなった知らせ・残り1人の押せる項目と押して開くこと・戻る操作と欄から詳しい画面と欄の開き直しで知らせが残ること・同じ id の戻り・相手のブランチの変化・ほかの相手の増減、試しの orca-web を止めたときと起動し直したとき、埋め込みのとき、試しの sendEnabled を false にしたときの orca-web の知らせの記録がある", verifies: ["R-01", "R-02", "R-03", "R-04", "R-05", "R-06", "R-07", "F-01", "F-02", "F-03", "F-05", "F-06", "F-08"]}
}

verification: """
	S-01（実装担当 impl_ui）：T-01〜T-03 と、関わる既存のテスト（`tests/unit/infra/test_dashboard_orca_match_js.py` など）、`make lint`。
	S-02、S-03（同じ実装担当 impl_ui）：T-04〜T-08 と、関わる既存のテスト（`tests/unit/infra/test_dashboard_scope_tabs_js.py`、`test_dashboard_panel_logic_js.py`、`test_dashboard_screens_js.py`、`test_dashboard_shell_polish.py`、`tests/cli_runtime/test_issue529_dashboard_server.py` など）。S-03 の終わりに `make lint`、`uv run pytest`（全体）。
	S-04（タスク担当）：試しの組（下）と headless Chrome（CDP）。記録と写しは worktree の `.workbench/iss-00593/`、要るものを report.md に写す。
	試しの組（統括の決定）：
	- 試しの SpecDock：S-03 の HEAD の `git archive` から作った wheel を隔離した venv に入れ、一時の状態の置き場（`XDG_CONFIG_HOME` も一時の置き場にし、そこの `spec-dock/config.json` に `{"schema": "specdock.config/v1", "orca_web": {"enabled": true, "port": <試しの orca-web のポート>}}`）、別のポート（186xx）、`--tailscale` で `dashboard serve`。登録簿は道具の環境の状態の置き場の写し（サーバーの記録とログを除く）。
	- 試しの orca-web：orca-web の main のチェックアウトの `dist/` を、別のポート（88xx）、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet の2つのオリジン、`ORCA_WEB_TAILSCALE_IP`、`ORCA_WEB_SETTINGS_FILE` と `ORCA_WEB_SENDS_DIR` を `.workbench/iss-00593/orca-web/` の試し専用の置き場にして起動する。試しの設定のファイルにだけ `"sendEnabled": true` を書く。orca-web のファイルは変えない。
	- 送る宛先：統括が用意した spec-dock の worktree `iss-00593-send-test`（ブランチ `chemitaro/iss-00593-send-test`）のエージェントだけ（その Scope のタブ、つまり iss-00593 のタブに、この worktree のエージェントと並んで出る）。送る前に帯と iframe の title のブランチが `chemitaro/iss-00593-send-test` であることを確かめる。業務中のエージェント（ブランチ `chemitaro/iss-00593` のこの worktree のもの、統括、ほかの worker）には送らない。本文は害のない短い1文。
	- 本人が見る試しの URL（tailnet）を報告に書き、本人の確かめまで止めずに残す。止め方（2つのプロセスの pid への SIGTERM と、試しの置き場の片付け）を report.md と報告に書く。
	"""

rollback: "PR を戻す。版を戻さずに止めるときは、`config.json` に `\"orca_web\": {\"enabled\": false}` を書く（タブも印も消え、orca-web に何も要求しない）。送信だけを止めるときは、orca-web の設定の `sendEnabled` を false にする。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に実機の確かめ（T-09）の記録がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {
		"C-1": {
			last_step: "S-01"
			range:     "開始のコミットから S-01 の HEAD まで"
			reviewer:  "code-reviewer opus / medium（方針の strict の行）"
			reason:    "相手の選びの決め方（出す条件、自動の選び、いなくなった印、iframe の道と sandbox）は、この Issue の失敗の条件の中心で、S-02 の画面がそのまま頼る。画面を作る前に、別の実装担当の作ったものを確かめる"
		}
	}
	final_quality_gate: {
		scope:          "開始のコミットから S-03 の終わりまで（S-04 は report.md の記録だけ。仕様は Git で扱わない）。PR の前に origin/main を取り込んだら、その最終のコミットでやり直す"
		perspectives:   ["functional-correctness", "requirements-closure", "test-adequacy", "security-baseline", "integration-boundaries", "compatibility-regression"]
		test_commands:  ["make lint", "uv run pytest"]
		record_paths:   []
		second_opinion: "chatgpt"
		reviewer:       "quality-gate-reviewer opus / high（主）、2人目 ChatGPT GPT-6 / Extra High（chatgpt-final-quality-gate-strict。取れないとき GPT-6 Astra / high）"
	}
	merge:      "owner"
	merge_note: "coordinated の使い方。タスク担当はマージせず、PR と証拠を統括に報告する。統括がマージする"
}

execution: {
	sessions: {
		spec:       {task: "仕様化（起動した側が選んだ値の記録）", model: "Opus 5.5", effort: "high", rationale: "統括が方針の「タスク担当 × strict」から選んだ（依頼書 task_94e69dff49b1）"}
		impl_ui:    {task: "実装（S-01、S-02、S-03）", model: "Opus 5.5", effort: "high", rationale: "claude。横の欄と詳しい画面の描き、iframe を残す描き直し、CSS の高さで、画面と一体。本人の指示（依頼書）と方針の「フロントエンドの設計と実装 × strict」で Opus 5.5 / high。S-01 は初め Codex GPT-6.1 Sol / medium（impl_logic）に割り当てたが、2026-11-14 に Codex の構造化のセッションが実行基盤の拒否（Orca の chat-scratch の書き込み先がシンボリックリンクの下にある）で何もできずに止まり（dispatch ctx_fdfd94981884）、方針 §1 の5で統括に返した。統括の了承（msg_cea1846a58b7、iss-00593 に限る）で、S-01〜S-03 をこの1つのセッションにまとめる。区切りのレビュー C-1 は S-01 の後のまま"}
		owner:      {task: "実機の確かめ（S-04）", model: "Opus 5.5", effort: "high", rationale: "タスク担当（このセッション）。試しの組の起動と、送信の確かめと写しの受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec:      {role: "仕様のレビュー（実装の前。after は最初の手順の前を指す印として S-01）。spec-reviewer と、2人目 ChatGPT GPT-6 / Extra High（chatgpt-spec-review-strict）", after: "S-01", model: "Opus 5.5", effort: "high"}
		checkpoint: {role: "区切りのレビュー C-1", after: "S-01", model: "Opus 5.5", effort: "medium"}
		gate:      {role: "最終品質ゲート（主。2人目は ChatGPT GPT-6 / Extra High）", after: "S-03", model: "Opus 5.5", effort: "high"}
	}
}
