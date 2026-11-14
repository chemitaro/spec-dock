package spec

// 計画（Issue）。型 specdock/v1。

goal: "ダッシュボードが orca-web の場所を知り、要約を1つの輪で読み、SpecDock の worktree の記録と突き合わせて Scope ごとの worktree を決められるようにする（印はまだ描かない）"

steps: {
	"S-01": {title: "テスト（T-01〜T-03）を先に書いて落ちることを確かめ、domain/orca_web.py、infra の read_user_orca_web、DashboardSite の orca_web と config_problems、dashboard_http.py の shell_csp・_orca・CSP・一覧の API の server.orca_web を D-01、D-02 のとおりに作る", realizes: ["R-01", "R-02", "F-02"], status: "todo", session: "impl"}
	"S-02": {title: "テスト（T-04、T-05）を先に書いて落ちることを確かめ、構造の API の worktree の記録（文書の上の worktrees と、Scope の項目の worktrees）と、revision の worktree の署名を D-03 のとおりに作る", realizes: ["R-03", "F-03"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "node のテスト（T-06〜T-08）を先に書いて落ちることを確かめ、core/orca_match.js を D-04 のとおりに作る", realizes: ["R-04", "R-05", "F-01", "F-03"], status: "todo", after: ["S-02"], session: "impl"}
	"S-04": {title: "node のテスト（T-09、T-10）を先に書いて落ちることを確かめ、core/orca.js と app.js の組み込みを D-05 のとおりに作る。make lint と uv run pytest（全体）を通す", realizes: ["R-01", "R-05", "F-01", "F-02"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "隔離した venv と別のポートの試しのサーバーで、常駐の orca-web の実データの対応と、画面のオリジンからの読みが拒まれることを確かめ、report.md に残す（D-06）", realizes: ["R-06"], status: "todo", after: ["S-04"], session: "owner"}
}

tests: {
	"T-01": {title: "parse_orca_web：ファイルなし・節なし → 既定（true、8791）。enabled false、port 9001 を読む。節が dict でない・知らない鍵・enabled が bool でない・port が bool・0・65536・文字列 → 無効で section_problem。JSON でない・schema が違う・read_error → 無効で section_problem でない。orca_web_origin：Host の名前の小文字と port から origin、無効なら origin null、port が自分のポートなら無効と理由（Python、domain）", verifies: ["R-01", "F-02"]}
	"T-02": {title: "DashboardSite：config.json を書き換えると起動し直さずに orca_web() が変わる。節の誤りは config_problems に user の1行で出て、リポジトリの出し入れ（visibility、repositories()）は変わらない。ファイルが JSON でないとき config_problems の行は今の1行だけ（Python、application）", verifies: ["R-01", "F-02"]}
	"T-03": {title: "HTTP：設定なしで Host 127.0.0.1:<port> の画面の CSP の4つの指示の末尾に http://127.0.0.1:8791 があり、ほかの指示は今のまま。許した別の Host（192.0.2.10）ではその名前。enabled false で _SHELL_CSP と同じ文字列。JSON の口と /files/ の CSP は変わらない。一覧の API の server.orca_web が D-01 の形。port の書き換えが次の要求で効く。許していない Host は 421（Python、application か cli_runtime）", verifies: ["R-01", "R-02", "F-02"]}
	"T-04": {title: "構造の API：差し替えた worktree の一覧（main、カタログ、chemitaro/iss-00591 と iss-00591-2 の2つ、detached）で、iss-00591 の項目の worktrees が2件（一覧の順）、branch が最初のもの、文書の上の worktrees が ok で全パス（detached も含む）。一覧の失敗・カタログなしで unreadable、paths 空、各 worktrees 空、ほかの項目は今と同じ（Python）", verifies: ["R-03", "F-03"]}
	"T-05": {title: "worktree_signature：一時の git のクローンで、linked worktree を足す・ブランチを切り替える・消すたびに値が変わり、何もしなければ同じ。.git が dir でなければ None。DashboardSite の revision が worktree を足すと変わる（Python、本物の git を一時のディレクトリで使う）", verifies: ["R-03"]}
	"T-06": {title: "matchWorktrees：パスの一致（末尾の / の有無）、同じ project.id のブランチの一致、別の project.id の同じブランチは対応しない、手がかりなし（paths に一致がない）では段2をしない、issue だけの一致は対応しない、Epic は子の worktree を合算しない、1つの要約の worktree は1つの Scope、Scope の中の並び（記録の順、同じ記録は要約の順）、path・branch・project が null の worktree（node）", verifies: ["R-04"]}
	"T-07": {title: "matchWorktrees と orcaStatus の失敗：structure の worktrees.status が unreadable → no-records と空。summary が null・schema が違う・worktrees が並びでない → invalid と空。orcaStatus の off・loading・unreachable（failed、形の違い、知らない state）・orca-unreachable・orca-starting・ok（stale true でも ok）（node）", verifies: ["R-05", "F-01", "F-03"]}
	"T-08": {title: "mergedWorktree：0件 null、1件そのもの、2件で agents の連結と counts の和と最初の id・path・branch（node）", verifies: ["R-04"]}
	"T-09": {title: "createOrca（差し替えた importModule・addStylesheet・タイマーと、偽の部品の watchWorktreeSummary）：無効な config（null、enabled false、origin なし）で importModule も addStylesheet も呼ばれず status off。有効で CSS と import が1回、watch が1つ、onDocument で ok と知らせ、forScope が対応の並びを返し、同じ structure と要約で matchWorktrees の結果を覚える。onError で unreachable、summary null、forScope 空。import の失敗で unreachable、次の import の URL が ?r=1、成功で watch が始まる。subscribe の外し、購読者の例外がほかを止めない、stop で輪とタイマーが止まる（node）", verifies: ["R-05", "F-01", "F-02"]}
	"T-10": {title: "app.js が createOrca を一覧の API の server.orca_web で1回だけ作り、render の ctx に orca を渡し、checkServer で作り直さないこと（静的な目印のテスト）。core/orca.js と core/orca_match.js が画面の資産として配られる（/assets/core/… が 200）（Python）", verifies: ["R-05"]}
	"T-11": {title: "実データの確かめ（S-05）：report.md に、試しの版とポート、要約の worktree の数、node の上の本物の部品での core/orca.js の状態 ok、対応した Scope と worktree の数と ID（iss-00591 の worktree が iss-00591 に対応する）、画面のオリジンからの部品の import が 403 で拒まれ ?r=1 で試し直され、図とボードが描かれたことの記録がある", verifies: ["R-06"]}
}

verification: """
	S-01〜S-04（実装担当）：各手順で足したテストと、関わる既存のテスト（`tests/unit/application/test_dashboard_*`、`tests/cli_runtime/test_issue529_dashboard_server.py`、`tests/unit/infra/test_dashboard_*_js.py` など）。S-04 の終わりに `make lint`、`uv run pytest`（全体）。
	S-05（タスク担当）：D-06 の試しのサーバーと `match.mjs`、headless Chrome の確かめ。
	"""

rollback: "PR を戻す。`config.json` に `\"orca_web\": {\"enabled\": false}` を書けば、版を戻さずに連携だけを止められる（CSP も今に戻る）。"

exit: "PR がマージできる状態で、CI が通り、最終品質ゲートの closure.md があり、report.md に実データの対応の記録がある。マージは統括が行う。"

// 関門（coding-task / specify の ## 関門）
gates: {
	checkpoints: {}
	checkpoints_note: "なし。4つの実装の手順を1つの実装担当が続けて行い、どれもテストで閉じた変更（サーバーの項目の追加と、画面の純粋な計算と読みの部品）で、画面の描きを含まない。最終品質ゲートで開始のコミットから全体を見る"
	final_quality_gate: {
		scope:          "開始のコミット 89f51588a から S-04 の終わりまで（S-05 は記録だけ）"
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
		spec:  {task: "仕様化（起動した側が選んだ値の記録）", model: "opus", effort: "medium", rationale: "統括が方針の「タスク担当 × standard」から選んだ（依頼書）"}
		impl:  {task: "実装（S-01〜S-04）", model: "gpt-6.1-sol", effort: "medium", rationale: "codex。サーバーの設定・CSP・API と、対応の純粋な計算と読みの部品で、どれもテストで確かめられる。本人の指示（依頼書、2026-11-14）で Codex GPT-6.1 Sol / medium。失敗や見落としが記録されたときだけ方針 §1 の4で GPT-6 Astra / high。画面の描きはこの Issue にないので Claude の手順は切り出さない"}
		owner: {task: "実データの確かめ（S-05）", model: "opus", effort: "medium", rationale: "タスク担当（このセッション）。常駐の orca-web を読むだけの受け入れの証拠の取得で、実装ではない"}
	}
	reviews: {
		spec: {role: "仕様のレビュー（実装の前。after は最初の手順の前を指す印として S-01）", after: "S-01", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート", after: "S-04", model: "opus", effort: "medium"}
	}
}
