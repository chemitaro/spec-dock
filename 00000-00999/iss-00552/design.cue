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
			- `resolve_config(user, repository_layers, key)` → `ConfigVisibility(visible, source)`。利用者の段が `invalid` か、リポジトリの段のどれかが `invalid` か、2つ以上のクローンの値が食い違えば `(False, "invalid")`。ほかは、初めの値 `(True, "default")` に、利用者の `visible`、利用者の `repositories[key]`、リポジトリの `visible` の順に重ねる（後が勝つ）。
			- `Visibility(mark, config)`：`hidden = mark or not config.visible`、`hidden_by` は `mark` なら `"mark"`、設定が隠せばその `source`。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01", "F-02"]
	}
	"D-02": {
		title: "設定の読み取り（`infra/user_config.py`、`infra/dashboard_files.py`）"
		text: """
			- `read_user_dashboard(environ)`：`user_config_path` の同じファイルを `read_optional` で読み、D-01 に渡す。
			- `read_repository_dashboard(catalog)`：`<catalog>/dashboard.json` を読む（リンクやディレクトリは `invalid`）。
			- `read_visibility(state_root, repository, catalogs=None)`：印（`read_hidden` の今の読み方）と設定から `Visibility` を返す。`catalogs` が None なら登録簿のそのリポジトリの行のカタログを使う（登録簿が読めなければリポジトリの段なし）。要約と `todo list` が使う。
			どれも読むだけで、ファイルを作らない（F-03）。
			"""
		satisfies: ["R-01", "R-02", "R-06", "F-03"]
	}
	"D-03": {
		title: "サーバーの一覧（`application/dashboard_site.py`）"
		text: """
			`_Listing` の signature に、利用者の設定のファイルと、登録簿の各カタログの `dashboard.json` の (mtime, size) を足す。変われば一覧を読み直す（R-05）。各リポジトリの `Visibility` を `_Listing.visibility` に持ち、`repositories()`／`lookup()` は `hidden` で決める。印の読めないときの今の扱い（最後に読めた印、初めから読めなければ全部隠す）は変えない。`RegistryRow` に `mark`、`config_visible`、`config_source`、`hidden_by` を足し、`config_problems()` が読めない段（`{layer, path, reason}`）を返す。
			"""
		satisfies: ["R-03", "R-05", "F-01", "F-02"]
	}
	"D-04": {
		title: "`dashboard list`／`hide`／`show` の結果（`application/dashboard_commands.py`、`presentation/dashboard_summary.py`）"
		text: """
			- `list`：各行に `mark`、`config {visible, source}`、`hidden_by` を足し、data に `config_problems` を足す。文字の行は `<鍵> hidden by=mark,user config=user …`／`<鍵> shown config=default …`。読めない設定は `config problem: <layer> <path>: <reason>` の行。
			- `hide`／`show`：印を書いた後に `read_visibility` で最終の値を読み、`hidden`（最終）、`hidden_by`、`config` を返す。`show` で設定が隠していれば警告 `DASHBOARD_HIDDEN_BY_CONFIG`（`details {repository, hidden_by, config_problems}`）。
			- `serve` の起動の知らせの「出るものがない」ときの案内に、設定のファイルを足す。
			"""
		satisfies: ["R-03", "R-04"]
	}
	"D-05": {
		title: "要約と `todo list` の `hidden`"
		text:  "`dashboard_summary`、`todo_aggregate`、`todo_list` の `read_hidden` を `read_visibility(...).hidden` に替える（カタログが分かるところは渡す）。"
		satisfies: ["R-06"]
	}
	"D-06": {
		title: "文書とヘルプ"
		text:  "`reference_cli.md`：ダッシュボードの契約に「出すリポジトリの決まり（`specdock.dashboard-settings/v1`、優先、印、壊れたとき）」を足し、設定の3段の行に `dashboard` の節を足し、`dashboard list` と `todo-list` の `hidden` の説明を直す。`cli/catalog.py` の `dashboard list`／`show` の説明。inventory の sha256 と `known_old_sha256`、dogfood の写し。"
		satisfies: ["R-07"]
	}
}

compatibility: "印の形と書き手は変えない。設定のファイルがなければ表示は前と同じ。契約の変更：`dashboard list` の行に `mark`、`config`、`hidden_by`、data に `config_problems` が増える。`dashboard show` の `hidden` が、設定が隠すときに true になる（前は常に false）。`dashboard hide`／`show` の data に `hidden_by` と `config` が増える。`todo list` と `dashboard summary` の `hidden` が設定も含む最終の値になる。利用者の設定の `dashboard` の節が壊れていると全リポジトリが隠れる。"
risks: [
	"利用者が設定のファイルを編集の途中で壊すと、一時的に全リポジトリが隠れる（安全側。`dashboard list` で理由が見える）",
	"各要求で各カタログの `dashboard.json` を stat する（登録簿は数件なので小さい）",
]
