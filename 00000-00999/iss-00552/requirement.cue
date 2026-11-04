package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "ダッシュボードに出すリポジトリを決める設定を、利用者の状態からリポジトリの設定のファイルへ広げる。表示の範囲の誤りは tailnet に見せる範囲の誤りになる"
}

purpose: "利用者が、ダッシュボードに出すリポジトリを、`dashboard hide`／`show` のコマンドだけでなく、設定のファイルで決められる（管理が分かりやすい）。"
background: "2026-11-04 の利用者の要望。今は、利用者ごとの隠す印（`<state_root>/dashboard/repositories.json`、`dashboard hide`／`show` だけが書く）だけで決まる。設定の仕組みは #549（PR #558）で入った3段（初めの値 < 利用者の設定 `$XDG_CONFIG_HOME/spec-dock/config.json`（`specdock.config/v1`）< リポジトリの設定）で、ダッシュボードの表示もこれに乗せる。表示の範囲の誤りは、tailnet に見せる範囲の誤りになる。"

includes: [
	"利用者の設定 `config.json` の `dashboard` の節（全体の既定と、リポジトリごとの値）",
	"リポジトリの設定：カタログの根の `dashboard.json`（`specdock.dashboard-settings/v1`）",
	"設定と隠す印を合わせた最終の表示を、サーバー、`dashboard list`、`hide`／`show`、`dashboard summary`、`todo list` の `hidden` で同じ規則で使う",
	"`reference_cli.md`、ヘルプ、配布資産の inventory と dogfood の写し",
]
excludes: [
	"設定のファイルを書くコマンド（SpecDock は設定のファイルを作らず、書かない）",
	"画面の資源（`assets/dashboard/`）の変更",
	"版の番号と `migration.md`（次の版のリリースの Issue が行う）",
]

requirements: {
	"R-01": {
		title: "利用者の設定で、全体の既定とリポジトリごとに、出すかどうかを決められる"
		text:  "`config.json` の `dashboard` の節に `visible`（全体の既定）と `repositories: {\"<host/owner/name>\": {visible}}`（リポジトリごと）を書ける。リポジトリごとの値が全体の既定に勝つ。`visible: false` を全体に書き、出すものだけ `true` にする使い方ができる。"
		acceptance: [
			"`dashboard.visible: false` だけを書くと、どのリポジトリもサーバーに出ず、`dashboard list` で `hidden: true`、出どころ `user` になる",
			"そのうえで `repositories.\"github.com/o/n\".visible: true` を書くと、そのリポジトリだけが出る",
			"リポジトリの鍵は `owner/name` と大文字も受け、`github.com/owner/name` の小文字にそろえて比べる",
		]
	}
	"R-02": {
		title: "リポジトリの設定（カタログの `dashboard.json`）で決められ、利用者の設定より優先する"
		text:  "カタログの根の `dashboard.json`（`{\"schema\": \"specdock.dashboard-settings/v1\", \"visible\": bool}`）が、そのリポジトリの値を決める。3段の規則（初めの値 true < 利用者の設定 < リポジトリの設定、後の段が勝つ）のまま、リポジトリの `visible: true` は利用者の `visible: false` も上書きする（統括と利用者の判断、2026-11-04）。"
		acceptance: [
			"利用者の設定が `visible: false` でも、カタログの `dashboard.json` が `visible: true` なら出て、出どころが `repository` になる",
			"カタログの `dashboard.json` が `visible: false` なら、利用者の設定が `true` でも隠れる",
		]
	}
	"R-03": {
		title: "隠す印は設定にかかわらず常に隠し、今の印の状態は変わらない"
		text:  "最終の表示は「設定が出す」かつ「隠す印がない」とき。`dashboard hide` の印（`repositories.json`）の形と意味は変えない。`dashboard show` は印を消すだけで、設定が隠していれば結果の `hidden` が true になり、`hidden_by` と警告 `DASHBOARD_HIDDEN_BY_CONFIG` で、直す場所を示す。"
		acceptance: [
			"設定がなく印だけがある利用者で、表示が前と同じ（印のリポジトリだけが隠れる）",
			"設定が出すリポジトリに `dashboard hide` すると隠れ、`hidden_by` が `[\"mark\"]`",
			"設定が隠すリポジトリに `dashboard show` すると、印は消えるが `hidden: true`、`hidden_by` に設定の出どころ、警告 `DASHBOARD_HIDDEN_BY_CONFIG` が出る",
		]
	}
	"R-04": {
		title: "`dashboard list` が、最終の表示と、印・設定の値と出どころを示す"
		text:  "各行に `hidden`（最終）、`served`、`mark`（印の有無）、`config {visible, source}`（`source` は `default`、`user`、`repository`、`invalid`）、`hidden_by`（`mark` と、設定が隠すときはその出どころ）を足す。読めない設定は `config_problems` に並べる。文字の出力は `hidden by=mark,user config=user` のように示す。"
		acceptance: [
			"JSON の各行に `mark`、`config.visible`、`config.source`、`hidden_by` があり、上の受け入れの条件の出どころと一致する",
			"文字の出力に、隠れた理由（`by=`）と設定の出どころ（`config=`）が出る",
		]
	}
	"R-05": {
		title: "動いているサーバーが、設定の変更を起動し直さずに反映する"
		text:  "サーバーは、登録簿と印に加えて、利用者の設定のファイルと各カタログの `dashboard.json` が変われば、一覧を読み直す。"
		acceptance: [
			"サーバーが動いている間に利用者の設定や `dashboard.json` を書き換えると、次の要求から出るリポジトリが変わる",
		]
	}
	"R-06": {
		title: "`dashboard summary` と `todo list` の `hidden` も、同じ最終の値になる"
		acceptance: [
			"設定が隠すリポジトリで、`dashboard summary` の `hidden` と `todo list --all-repositories` の行の `hidden` が true",
		]
	}
	"R-07": {
		title: "文書とヘルプが、設定の置き場、形、優先、壊れたときの扱いを示す"
		acceptance: [
			"`reference_cli.md` の設定とダッシュボードの節、`dashboard list`／`show` のヘルプが新しい契約を示し、inventory の sha256 と dogfood の写しが合う",
		]
	}
}

failures: {
	"F-01": {
		title: "利用者の設定のファイルが壊れていれば、全リポジトリを隠す"
		text:  "読めない、JSON でない、`schema` が違う、`dashboard` の節の形や値が違うときは、その段を飛ばさずに、すべてのリポジトリを隠す（出どころ `invalid`）。`config_problems` に道と理由を示す。`todo` の節の誤りは、ダッシュボードに影響しない。"
		impact: "見せるつもりのないリポジトリが tailnet に見える"
		recovery: "`dashboard list` の `config_problems` の道のファイルを直す。サーバーは起動し直さずに戻る"
	}
	"F-02": {
		title: "リポジトリの `dashboard.json` が壊れているか、2つのクローンで食い違えば、そのリポジトリを隠す"
		impact: "そのリポジトリだけが見えなくなる"
		recovery: "`config_problems` の道のファイルを直すか、食い違いを解く"
	}
	"F-03": {
		title: "SpecDock は設定のファイルを作らず、書かない"
		text:  "`dashboard hide`／`show` も、印（`repositories.json`）だけを書く。"
	}
}

constraints: [
	"#549 の3段の設定の仕組み（`specdock.config/v1`、初めの値 < 利用者 < リポジトリ）に乗せ、別の仕組みを作らない",
	"隠す印（`specdock.dashboard-repositories/v1`）の形と書き手は変えない",
	"GitHub に要求を送らない。テストは一時のディレクトリで閉じる",
]
decisions: [
	"2026-11-04 統括：案A＋B＋C＋D。リポジトリの設定が最も優先（利用者の判断）で、リポジトリの `visible: true` が利用者の `visible: false` を上書きしてよい。隠す印は常に隠す。壊れた設定は隠す側に倒す",
	"リポジトリの設定は、`todos/settings.json` と並ぶカタログの根の `dashboard.json`。カタログの走査はディレクトリだけを見るので、Scope の検査に影響しない",
]
