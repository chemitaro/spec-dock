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
	reason: "定期の同期と canonical status、canonical remove の契約から、今のダッシュボードの生成を外す。誤ると同期を壊すおそれがあるが、版を戻せば回復できる。"
}

purpose:    "HTML のダッシュボード（epic-00427）に置き換わった、今の Markdown と PlantUML のダッシュボード（`dashboard.md` と4つの PlantUML のファイル）の生成と、それに付いた契約を撤去する（Epic の R-23、D-10）。"
background: "iss-00438 は、定期の同期の手順7で、main のチェックアウトの `spec-dock/` に5つのファイルを書き、`canonical status` の `dashboard` の項目、`canonical remove` の削除の手順、`state.json` の `dashboard` の欄を足した。epic-00427 の段階1（0.6.0）で HTML のダッシュボードと `dashboard summary` が出るので、エージェントと利用者はそちらを読む。"

includes: [
	"5つのファイルを作るコード（`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py`、`canonical_sync._refresh_dashboards` とその呼び出し）の撤去",
	"`canonical status` の `dashboard` の項目と `CANONICAL_DASHBOARD_*`、次の1手の文の撤去",
	"`canonical remove` の `canonical.dashboard.remove` の手順の撤去",
	"`CatalogSyncState.dashboard` の撤去（古い `state.json` の `dashboard` の欄は読むときに無視する）",
	"配布する `spec-dock/.gitignore` と `asset_layout.py` から5つの名前を外す",
	"文書（`canonical.md`）、CLI の説明（`catalog.py`）、配布資産の inventory、dogfood の写し、テストと fixture の追随",
]
excludes: [
	"`migration.md` と版の番号（#534 が書く）",
	"利用者のリポジトリに残った5つのファイルの削除（SpecDock は消さない。利用者が消してよい）",
	"新しい画面（`src/spec_dock/assets/dashboard/`）と `dashboard` のコマンド群",
	"過去の版の fixture（`tests/fixtures/issue440`、`issue497`、`issue501` の古い `.gitignore` と `canonical.md`）",
	"履歴の文書（`docs/discussion-sheets/`）とカタログの仕様",
]

requirements: {
	"R-01": {
		title: "定期の同期が5つのファイルを作らない"
		text:  "`canonical sync`（定期の実行を含む）は、main のチェックアウトの `spec-dock/` に `dashboard.md`、`tree.puml`、`tree-all.puml`、`deps-issues.puml`、`deps-raw.puml` を作らず、すでにあるものを書き換えも削除もしない。構造のスナップショットの更新（手順7の `ensure_fresh`）は今までどおり行う。`repositories[]` の `dashboards_written` は、契約を変えないために項目を残し、常に0を返す（統括の決定 (A)。後の版で消す予定）。"
		acceptance: [
			"偽の GitHub の構造で `canonical sync` を2周しても、main のチェックアウトに5つのファイルがなく、`repositories[]` の各行に `dashboards_written: 0` があり、構造のスナップショットは書かれる",
			"前の版が書いた5つのファイルを置いて同期しても、中身と時刻が変わらず残る",
		]
	}
	"R-02": {
		title: "`canonical status` の JSON から `dashboard` の項目が消える"
		text:  "`canonical status` の `data` は `catalog`、`link`、`exclude`、`access`、`tools`、`sync`、`changes`、`format`、`git`、`snapshot`、`structure` の11項目になる。`CANONICAL_DASHBOARD_OCCUPIED` と `CANONICAL_DASHBOARD_FAILED` の警告を出さない。"
		acceptance: ["`canonical status --json` の `data` の鍵が11項目（と `kind`）で `dashboard` がなく、古い `state.json` に `dashboard.error` があっても `CANONICAL_DASHBOARD_*` の警告が出ない"]
	}
	"R-03": {
		title: "`canonical remove` は5つのファイルを消さない"
		text:  "`canonical remove` の計画と実行に `canonical.dashboard.remove` の手順がなく、main のチェックアウトに残った5つのファイルはそのまま残る。"
		acceptance: ["5つのファイルを置いたチェックアウトで `canonical remove` の計画にも `--yes` の結果にも `canonical.dashboard.remove` がなく、5つのファイルが残る"]
	}
	"R-04": {
		title: "生成のコードが残っていない"
		text:  "5つのファイルを作るモジュールと関数、`CatalogSyncState.dashboard`、`CANONICAL_DASHBOARD_*` の定数、5つの名前の定数が、提供側のソースと配布物に残らない。"
		acceptance: [
			"`spec_dock.runtime.application.canonical_dashboard`、`spec_dock.runtime.domain.canonical_dashboard`、`spec_dock.runtime.presentation.markdown`、`spec_dock.runtime.presentation.puml` を import できず、新しく作った wheel にも入らない",
			"`src/spec_dock/runtime/` と `src/spec_dock/asset_layout.py` と配布する `spec-dock/.gitignore` に `_refresh_dashboards`、`CANONICAL_DASHBOARD_`、`dashboard_item`、`canonical.dashboard.remove`、5つのファイルの名前が現れない（配布する文書は R-05 で確かめる。#534 が `migration.md` に5つの名前を書くので、文書は検索の対象にしない）",
		]
	}
	"R-05": {
		title: "配布資産と文書が撤去に合う"
		text:  "配布する `spec-dock/.gitignore` から5つの名前を外し、`canonical.md` と CLI の説明（`canonical status`、`canonical sync`、`canonical remove`）から5つのファイルの記述を消す。変えた配布資産は inventory の sha256 を新しくし、前の sha256 を `known_old_sha256` に足す。dogfood の写しを提供側と同じにする。"
		acceptance: [
			"配布する `spec-dock/.gitignore` に5つの名前がなく、inventory の行の sha256 が中身と合い、前の中身の sha256 が `known_old_sha256` にある（`installation update` が前の版の `.gitignore` を新しくする）",
			"`canonical.md` と CLI の説明に5つのファイル、`CANONICAL_DASHBOARD_*`、`canonical status` の `dashboard` の項目が現れず、dogfood の `spec-dock/` の写しが提供側と同じ",
		]
	}
}

failures: {
	"F-01": {
		title: "古い `state.json` の `dashboard` の欄（形が壊れていても）で状態が読めなくならない"
		text:  "前の版が書いた `dashboard` の欄は、読むときに中身を見ずに無視し、次に書くときに落とす。欄が辞書でなくても `StateFormatError` にしない。"
	}
	"F-02": {
		title: "利用者のリポジトリに残った5つのファイルを SpecDock は消さない"
		text:  "生成をやめた後も、残ったファイルは利用者のものとして扱い、同期も `canonical remove` も触れない。`.gitignore` から外れるので `git status` に出る。消してよいことは 0.6.0 の `migration.md`（#534）が示す。"
	}
}

constraints: [
	"Epic の設計の「ほかのコマンドの契約は変えない」に従い、`canonical sync` の `dashboards_written` は残して常に0にする（統括の決定 (A)、2026-11-04）。",
	"第3波の #530・#531・#532 と並ぶので、担当の外のファイルを変えない。`reference_cli.md` と `cli-redesign-guide.html` は5つのファイルを記述していないので変えない。",
	"版の番号と `migration.md` は変えない（#534）。",
]
decisions: [
	"`asset_layout.LEGACY_WORKBENCH_IGNORE` は、どこからも使われていない古い `.gitignore` の写しで、5つの名前を含む。名前だけを抜くと写しの意味を失うので、定数ごと消す。",
	"`tests/integration/test_issue413_wheel.py` の「wheel に入らないモジュール」の一覧に4つのモジュールを足し、配布物に残らないことを確かめる。",
]
