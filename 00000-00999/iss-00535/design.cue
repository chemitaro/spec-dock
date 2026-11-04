package spec

goals: [
	"描画の入口（`render_scope`）とデザインシステムの薄いページ（`wrap_page`）を、そのまま使う",
	"文書は資料と同じ切り離しで配り、画面は sandbox の枠で示す",
	"`cue` を動かす回数を、ファイルが変わったときだけにする",
]
current: "「文書」のタブは、文書のあるなしと説明資料へのリンクだけ。`server.restart_required` は API にあるが画面に出ない。"
target:  "「文書」のタブで、CUE の仕様、Markdown の文書、報告、ADR を枠の中で読め、検査の結果と計画の進み具合が出る。上の帯が起動し直しを促す。"

design: {
	"D-01": {
		title: "文書の読み取りと覚え（`application/dashboard_documents.py`）"
		text: """
			- `ScopeDocuments`（サーバーの寿命のメモリ。ロックつき）が、`(カタログ, Scope ID)` ごとに、`requirement.cue`・`design.cue`・`plan.cue`・`explanation.html` とリポジトリの型（`<main のチェックアウト>/spec-dock/cue/*.cue`）の `(mtime_ns, size)` と、Scope の種類と題名（構造から来て描画に効く）を鍵に、`render_scope` の結果（HTML、検査の報告、完全か）を1つ覚える。鍵が同じなら `cue` を動かさない。
			- `render_scope` は `design_system_base="/ds/"`、`vendor_base="/vendor/"`、Scope の種類（構造のモデルの `kind`）、題名で呼ぶ。`repository_root` は登録簿の `main_checkout`（`SiteRepository.checkout`）で、なければカタログを指す（リポジトリの型なし）。
			- `CanonicalCommandError`（`CUE_NOT_FOUND`、`CUE_TIMEOUT` など）は覚えず、`failed` の結果（コード、文、次の1手）にする（F-01）。ほかの例外も同じ。
			- `check(…)` は API 用の `details.check`（`status`：`ok`・`invalid`・`failed`・`markdown`、`complete`、`errors`・`warnings` の `{code, message, file}`、`next_steps`）と `details.progress` を返す。
			- `progress(evaluation)`：`steps` の各値の `status`（既定 todo）を数え、`{total, done, doing, todo, dropped, doing_steps: [{id, title}]}`。`total` は dropped を除く。手順がなければ None。
			- `markdown_page(directory, 道)`：許す道（`requirement.md`、`design.md`、`plan.md`、`report.md`、`artifacts/<ADR>`、`discussions/<ADR>`）の通常のファイルだけを、リンクをたどらずに読み、`wrap_page(本文, design_system_base="/ds/", vendor_base="/vendor/")` に包む。
			- `adr_documents(directory)`：`artifacts/` と `discussions/` の直下の通常のファイルで、名前が `.md` で終わり `adr-` を含むもの（名前の順、上限あり）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-03"]
	}
	"D-02": {
		title: "文書の道（`application/dashboard_http.py`）"
		text: """
			- `/r/<host>/<owner>/<name>/scopes/<ID>/doc`：構造にある Scope で、カタログに `requirement.cue` があれば、D-01 の HTML を 200 で返す。評価が通らないときも検査の結果のページを 200 で返す。`failed` なら、コードと次の1手の薄いページを 503 で返す。Markdown の Scope は 404。
			- `/r/<host>/<owner>/<name>/scopes/<ID>/doc/<道>`：D-01 の `markdown_page` を 200、許さない道やないファイルは 404。
			- どちらも `_material`（`sandbox allow-scripts allow-popups; frame-ancestors <埋め込みの許可>`、`nosniff`、`no-store`）で返す。隠したリポジトリは資料と同じ案内の 404、あいまいなカタログは 409、知らないリポジトリや構造にない Scope は 404。
			- Scope の API（`/api/v1/r/…/scopes/<ID>`）は、`details` に `check`、`progress`、`spec`（CUE の仕様のページの道）、文書ごとの `view`（枠で示す道）、`adrs` を足す。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-02", "F-03"]
	}
	"D-03": {
		title: "`wrap_page` と `script_safe` を公開の関数にする（`presentation/spec_page.py`）"
		text:  "`_script_safe` を `script_safe` にし、中の呼び出しを直す。`wrap_page` は中で本文を `script_safe` に通す（`</script` で枠の外に出ない）ので、Markdown の本文はそのまま渡す。"
		satisfies: ["R-03", "F-02"]
	}
	"D-04": {
		title: "詳しい画面の「文書」のタブと進み具合（`views/scope.js`、`views/scope.css`）"
		text: """
			- 「文書」のタブ：上に文書の札（CUE の Scope は「要件・設計・計画」の1枚、Markdown の Scope は3枚、報告、説明資料、ADR）。札を選ぶと問い合わせの `doc` に持ち、下の枠（`<iframe sandbox="allow-scripts allow-popups" referrerpolicy="no-referrer">`）にその文書を示す。既定は CUE の仕様、なければ最初にある文書。各札に「新しいタブで開く」。説明資料は今のとおり新しいタブだけ。
			- 検査の結果：`details.check` の誤りと警告を、数と一覧（コード、文、ファイル）で示す。`failed` なら警告の囲みに理由と次の1手を示し、「要件・設計・計画」の札を選んでいるときは枠を描かない（ほかの札の Markdown の文書は描く。F-01）。
			- 進み具合：`details.progress` があれば、「概要」と「文書」のタブに、帯（終わった、作業中、未着手）と「n／m 終わった」、作業中の手順の一覧を示す。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "F-01", "F-02"]
	}
	"D-05": {
		title: "起動し直しの知らせ（`app.js`、`core/topbar.js`）"
		text:  "`app.js` は起動のときと60秒ごとに `/api/v1/repositories` を読み、`server` を覚える。`renderNotices` は、`server.restart_required` が true なら、先頭に `SERVER_RESTART_REQUIRED` の知らせ（入っている版、次の1手 `spec-dock dashboard serve`）を出す。変わったときだけ知らせの帯を描き直す。"
		satisfies: ["R-05"]
	}
	"D-06": {
		title: "文書（`docs/reference_cli.md`）"
		text:  "ダッシュボードのサーバーの契約の「画面の道」と「資料」に、文書の道（`…/scopes/<ID>/doc`、`…/scopes/<ID>/doc/<道>`）と、その切り離しを足す。`static-inventory.json` の該当の行の sha256 を更新し、前の値を `known_old_sha256` に足す。"
		satisfies: ["R-01", "R-03"]
	}
}

compatibility: "画面の道に `scopes/<ID>/doc` と `scopes/<ID>/doc/<道>` が増える（足すだけ）。`SiteRepository` に任意の `checkout` が増える。`_script_safe` は `script_safe` に名前が変わる（内部の関数）。Scope の API の `details` に項目が増える（契約にしない JSON）。"
risks: [
	"#554 も `views/scope.js` と画面の骨組みに手を入れるので、後にマージするほうが取り込み直す",
	"5秒の自動の更新で構造の版が変わると、詳しい画面が描き直され、文書の枠が読み直される（スクロールが先頭に戻る）",
]
