package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"表示を決める規則を1か所（domain）に置き、サーバー、`dashboard list`、`hide`／`show`、要約、`todo list` が同じ答えを使う",
	"#549 の設定の3段と隠す印の扱い（読めなければ隠す）に合わせる",
]
current: "表示は隠す印（`repositories.json`）だけで決まる。`DashboardSite` が印と登録簿の変化で一覧を読み直し、`read_hidden` が要約と `todo list` の `hidden` を返す。"
target:  "表示は「設定の値（初めの値 true < 利用者 < リポジトリ）が出す」かつ「印がない」で決まり、その理由が `dashboard list` で見える。"

design: {
	"D-01": {
		title: "表示の規則（`domain/dashboard_visibility.py`）"
		text: """
			純粋な部品。

			- `parse_user_dashboard(path, payload, read_error)`：利用者の設定のファイルの `dashboard` の節を読む。ファイルがない → `missing`。読めない／JSON でない／`schema` が `specdock.config/v1` でない／`dashboard` が object でない／`visible` が bool でない／`repositories` が object でない、その値が `{visible: bool}` でない、鍵が `GithubRepository.parse` できない → `invalid`（理由つき）。節がなければ `ok` で値なし。知らない鍵は無視する。鍵は `GithubRepository.parse(...).key` にそろえる（同じ鍵に2つの書き方があり値が違えば `invalid`）。
			- `parse_repository_dashboard(path, payload, read_error)`：カタログの `dashboard.json`。ない → `missing`。`schema` が `specdock.dashboard-settings/v1` で `visible` が bool（なくてもよい）なら `ok`。ほかは `invalid`。
			- `resolve_config(user, repository_layers, key)` → `ConfigVisibility(visible, source, problems)`。利用者の段が `invalid` か、リポジトリの段のどれかが `invalid` なら `(False, "invalid")`。2つ以上のクローン（同じリポジトリの登録簿の行）では、各クローンの値（`visible` の bool、またはファイルがない・`visible` を書かないときの「なし」）を比べ、1種類でなければ食い違いとして `(False, "invalid")` にし、`problems` に `{layer: "repository", path: <各カタログの dashboard.json を「, 」でつないだもの>, reason: "clones disagree: …"}` を足す。ほかは、初めの値 `(True, "default")` に、利用者の `visible`、利用者の `repositories[key]`、リポジトリの `visible` の順に重ねる（後が勝つ）。
			- `Visibility(mark, config)`：`hidden = mark or not config.visible`、`hidden_by` は `mark` なら `"mark"`、設定が隠せばその `source`。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01", "F-02"]
	}
	"D-02": {
		title: "設定の読み取り（`infra/user_config.py`、`infra/dashboard_files.py`）"
		text: """
			- `read_user_dashboard(environ)`：`user_config_path` の同じファイルを `read_optional` で読み、D-01 に渡す。
			- `read_repository_dashboard(catalog)`：`<catalog>/dashboard.json` を読む（リンクやディレクトリは `invalid`）。
			- `read_visibility(state_root, repository, fallback_catalog=None)`（`application/dashboard_site.py`）：新しく作った `DashboardSite` の答え（D-03）をそのまま返す。印、登録簿、各クローンのカタログの読み方がサーバーの最初の読み取りと同じになる（印が初めから読めなければ全部隠す、登録簿が読めなければ登録なし）。登録簿にないリポジトリ（`canonical link --no-schedule` のチェックアウト）では、`fallback_catalog` をリポジトリの段にする。要約と `todo list` が使う。
			どれも読むだけで、ファイルを作らない（F-03）。
			"""
		satisfies: ["R-01", "R-02", "F-03"]
	}
	"D-03": {
		title: "サーバーの一覧（`application/dashboard_site.py`）"
		text: """
			`_Listing` の signature に、利用者の設定のファイルと、登録簿の各カタログの `dashboard.json` の (mtime, size) を足す。変われば一覧を読み直す（R-05）。各リポジトリの `Visibility` を `_Listing.visibility` に持ち、`repositories()`／`lookup()` は `hidden` で決める。印の読めないときの今の扱い（最後に読めた印、初めから読めなければ全部隠す）は変えない。`RegistryRow` に `mark`、`config_visible`、`config_source`、`hidden_by` を足し、`config_problems()` が読めない段と食い違い（`{layer, path, reason}`）を返す。`visibility(key, fallback_catalog)` が1つのリポジトリの `Visibility` を返す（D-02 の `read_visibility` が使う）。
			"""
		satisfies: ["R-03", "R-05", "R-06", "F-01", "F-02"]
	}
	"D-04": {
		title: "`dashboard list`／`hide`／`show` の結果（`application/dashboard_commands.py`、`presentation/dashboard_summary.py`）"
		text: """
			- `list`：各行に `mark`、`config {visible, source}`、`hidden_by` を足し、data に `config_problems` を足す。文字の行は `<鍵> hidden by=mark,user config=user …`／`<鍵> shown config=default …`。読めない設定は `config problem: <layer> <path>: <reason>` の行。
			- `hide`／`show`：印を書いた後に `read_visibility` で最終の値を読み、`hidden`（最終）、`hidden_by`、`config` を返す。`show` で設定が隠していれば警告 `DASHBOARD_HIDDEN_BY_CONFIG`（`details {repository, hidden_by, config_problems}`）。
			- `serve` の起動の知らせの「出るものがない」ときの案内に、設定のファイルを足す。
			- 直接のURL（`application/dashboard_http.py`）：隠れたリポジトリの応答（`DASHBOARD_REPOSITORY_HIDDEN` の JSON と `_hidden_page`）の次の1手を `hidden_by` で変える。印だけなら今の `spec-dock dashboard show <slug>`。設定が隠すなら `spec-dock dashboard list`（出どころと `config_problems` を見る）と、設定のファイルを直す案内。両方なら両方。
			"""
		satisfies: ["R-03", "R-04"]
	}
	"D-05": {
		title: "要約と `todo list` の `hidden`"
		text:  "`dashboard_summary`、`todo_aggregate`、`todo_list` の `read_hidden` を `read_visibility(...).hidden` に替える（チェックアウトのカタログを `fallback_catalog` に渡す）。登録簿の行ごとの `todo list` の行（2つ目のクローンの `duplicate` の行も）は、リポジトリの鍵で同じ答えを使う。"
		satisfies: ["R-06"]
	}
	"D-06": {
		title: "文書とヘルプ"
		text:  "`reference_cli.md`：ダッシュボードの契約に「出すリポジトリの決まり（`specdock.dashboard-settings/v1`、優先、印、壊れたとき）」を足し、設定の3段の行に `dashboard` の節を足し、`dashboard list` と `todo-list` の `hidden` の説明を直す。`cli/catalog.py` の `dashboard list`／`hide`／`show`／`summary` と `todo` の葉の説明と読む物（利用者の設定のファイルと各カタログの `dashboard.json`）。inventory の sha256 と `known_old_sha256`、dogfood の写し。"
		satisfies: ["R-07"]
	}
}

compatibility: "印の形と書き手は変えない。設定のファイルがなければ表示は前と同じ。契約の変更：`dashboard list` の行に `mark`、`config`、`hidden_by`、data に `config_problems` が増える。`dashboard show` の `hidden` が、設定が隠すときに true になる（前は常に false）。`dashboard hide`／`show` の data に `hidden_by` と `config` が増える。`todo list` と `dashboard summary` の `hidden` が設定も含む最終の値になる。利用者の設定のファイル（`dashboard` の節を書かず `todo` だけを使う利用者も）が読めない、JSON でない、`schema` が違う、または `dashboard` の節が壊れていると、全リポジトリが隠れる（前は `todo` の段を飛ばす警告だけだった）。隠れたリポジトリの直接のURLの次の1手が、出どころで変わる。"
risks: [
	"利用者が設定のファイルを編集の途中で壊すと、一時的に全リポジトリが隠れる（安全側。`dashboard list` で理由が見える）",
	"各要求で各カタログの `dashboard.json` を stat する（登録簿は数件なので小さい）",
]
