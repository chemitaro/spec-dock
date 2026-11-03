package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"5つのファイルの生成と、それに付いた状態・表示・削除の手順を、提供側のソースと配布物から消す。",
	"Epic の D-10 が挙げた契約の変更（`canonical status` の `dashboard`、`canonical remove` の5つのファイル）だけを起こし、ほかのコマンドの契約は変えない。",
]
current: "定期の同期の手順7（`refresh_structures`）が、リポジトリごとに `ensure_fresh` の後で `_refresh_dashboards` を呼び、`application/canonical_dashboard.refresh_dashboard` が `domain/canonical_dashboard`（入力の組み立て）、`presentation/markdown`、`presentation/puml` で5つのファイルを書き、`state.json` の `dashboard` に `input_hash`、`written_at`、`error` を残す。`canonical status` の `SyncView.dashboard_item` がそれを示し、`canonical remove` が5つのファイルを消す。"
target:  "手順7は `ensure_fresh` だけを行い、`RepositoryResult.dashboards_written` は常に0。`state.json` に `dashboard` を書かず、読むときは無視する。`canonical status` と `canonical remove` は5つのファイルに触れない。"

design: {
	"D-01": {
		title: "生成のモジュールの削除"
		text: """
			`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py` を消す。`presentation/markdown.py` は `puml._issue_ready_board_state` だけを使い、ほかに使う側はない（`rg` で確かめた）。`spec_page.py` の Markdown の扱いは別物で残す。
			"""
		satisfies: ["R-01", "R-04"]
	}
	"D-02": {
		title: "定期の同期の手順7"
		text: """
			`canonical_sync.refresh_structures` から、スナップショットのパスの計算と `_refresh_dashboards` の呼び出しを消し、`_refresh_dashboards` を消す。`RepositoryResult` は `dashboards_written: int = 0` の欄と `to_json` の項目を残し、作る側はその値を渡さない（常に0）。docstring は「後の版で消す予定の、常に0の項目」と書く。`_record` の `dashboard=latest.dashboard` を消す。
			"""
		satisfies: ["R-01", "R-04"]
	}
	"D-03": {
		title: "`canonical status` の `dashboard` の項目の削除"
		text: """
			`CanonicalStatusData.dashboard`、`canonical_status.py` の `dashboard=view.dashboard_item()`、`SyncView.dashboard_item` を消す。`canonical_errors.py` の `CANONICAL_DASHBOARD_OCCUPIED`、`CANONICAL_DASHBOARD_FAILED`、`DASHBOARD_OCCUPIED_NEXT_STEP`、`DASHBOARD_FAILED_NEXT_STEP`、`DASHBOARD_MISSING_NEXT_STEP` を消す。`catalog.py` の `canonical status` の `json_data` から `dashboard` を外す。
			"""
		satisfies: ["R-02", "R-04"]
	}
	"D-04": {
		title: "`canonical remove` の手順の削除"
		text: """
			`canonical_remove._plan` の5つのファイルの手順と import を消し、モジュールの docstring と `catalog.py` の `writes` から「the dashboard files of the main checkout」を外す。残ったファイルは利用者のものとして残る（F-02）。
			"""
		satisfies: ["R-03", "F-02"]
	}
	"D-05": {
		title: "`state.json` の古い `dashboard` の欄"
		text: """
			`CatalogSyncState` から `dashboard` の欄を消し、`to_json` は `dashboard` を書かない。`from_json` は `payload` の `dashboard` を読まない（形を確かめない）。`STATE_VERSION` は変えない：前の版は `dashboard` がなければ `None` として読むので、版を戻しても読める。
			"""
		satisfies: ["R-04", "F-01"]
	}
	"D-06": {
		title: "配布資産、文書、inventory、dogfood の写し"
		text: """
			- 配布する `spec-dock/.gitignore` から5行を消す。`asset_layout.LEGACY_WORKBENCH_IGNORE`（未使用）を消す。
			- `canonical.md`：`canonical status` の項目の一覧から `dashboard` を外し、節「構造のスナップショットとダッシュボード」を「構造のスナップショット」にして5つのファイルの段落を消し、表から `CANONICAL_DASHBOARD_*` の2行を消す。
			- `catalog.py`：`canonical sync` の `writes` から5つのファイルを外し、`json_data` の `dashboards_written` に「always 0; kept for compatibility」を添える。
			- `static-inventory.json`：`spec-dock/.gitignore` と `spec-dock/docs/canonical.md` の行の sha256 を新しくし、前の sha256 を `known_old_sha256` に足す（ほかの行は変えない）。5つのファイルは配布資産でないので `retired` に足さない。
			- dogfood の `spec-dock/.gitignore` と `spec-dock/docs/canonical.md` を提供側と同じにする。
			"""
		satisfies: ["R-05"]
	}
	"D-07": {
		title: "テストと fixture"
		text: """
			- 消す：`tests/cli_runtime/test_issue438_canonical_dashboard.py`、`tests/unit/application/test_canonical_dashboard_golden.py`、`tests/unit/domain/test_canonical_dashboard.py`、`tests/unit/presentation/test_dashboard_board_state.py`、`tests/unit/presentation/test_deps_raw_puml.py`、そのための fixture（`tests/fixtures/issue438/` などテストからだけ読まれるもの）。
			- 直す：`test_issue429_canonical_status.py` の項目の一覧、`test_issue430_canonical_sync.py` の `dashboards_written`（0 になる）、`test_issue430_legacy_and_public.py` の `dashboard` の往復、`tests/unit/domain/test_canonical_sync_state.py` の往復の見本（`dashboard` の欄は読んで捨て、書かない）。
			- 足す：`tests/cli_runtime/test_issue533_dashboard_removal.py`（R-01〜R-03、F-01、F-02、R-04 の import と `src` の検索、R-05 の配布資産）と、wheel のテストの一覧に4つのモジュール。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04", "R-05", "F-01", "F-02"]
	}
}

compatibility: "0.6.0 の移行の注記に要る契約の変更：`canonical status` の JSON から `dashboard` の項目が消え、`CANONICAL_DASHBOARD_OCCUPIED`／`CANONICAL_DASHBOARD_FAILED` の警告が出なくなる。`canonical remove` は5つのファイルを消さない。`canonical sync` の `dashboards_written` は常に0（後の版で消す予定）。`state.json` に `dashboard` を書かない（前の版に戻しても読める）。配布する `spec-dock/.gitignore` から5つの名前が外れるので、`installation update` の後、利用者のリポジトリに残った5つのファイルが `git status` に出る。消してよい。"
risks: [
	"第3波のほかの Issue が `canonical.md` や inventory の同じ行を変えると衝突する。PR の前に `origin/main` を取り込み、sha256 を合わせた後の中身で計り直す。",
	"同期の手順7からスナップショットのパスの計算を消すとき、`ensure_fresh` の失敗の扱い（probe の値）を変えない。既存の `test_issue430_canonical_sync.py` で確かめる。",
]
