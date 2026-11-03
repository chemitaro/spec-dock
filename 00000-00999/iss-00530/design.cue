package spec

// 設計（Issue）。型 specdock/v1。
// コードの場所は 2026-11-04 の main（8ad7ef252、#531・#532・#533 のマージの後）で確かめた。

goals: [
	"同期の常駐の部品（launchd と systemd の Scheduler）を、ファイルの形だけを差し替えて使い、`launchctl`／`systemctl` の扱いを別に書かない",
	"常駐の動き（ロックの待ち、Tailscale の取り直し、版の確かめ）を `serve` の待ちの輪に集め、時間と版を差し替えて試せるようにする",
	"テストで本物の管理の側を呼ばない守りを、同期と同じ形でダッシュボードの常駐にも掛ける",
]

current: """
	- 同期の常駐：`infra/canonical_scheduling.py` の `Scheduler`（Protocol）、`scheduler_for`、`spec_dock_executable`、`usable_executable`、`write_atomic`、`SchedulerError`、`SchedulerObservation`。launchd は `infra/canonical_scheduler_launchd.LaunchdScheduler(agents_dir, label, uid, runner, sleep)`（`ensure` は plist を書き、変われば `bootout` → `bootstrap`。`remove` は `bootout` と削除）。systemd は `infra/canonical_scheduler_systemd.SystemdScheduler(unit_dir, service, timer, runner)`（timer を `enable --now`）。ファイルの形は `domain/canonical_scheduler.py` の `SchedulerSpec`、`launchd_plist`、`systemd_units`、`systemd_quote`、`state_root_argument`。
	- 環境：`infra/runtime_environment.detect_runtime_environment()` と `detect_service_manager(environment)`（Linux で `systemd_present`、`systemd_user`）。テストの守り：`tests/conftest.py` の `_session_guard`（`scheduler_for`、`spec_dock_executable`、`detect_service_manager` を差し替え、PATH の先に `launchctl`／`systemctl` の偽物を置き、呼ばれたら失敗）。
	- サーバー：`infra/dashboard_server.DashboardServer(state_root, *, port, tailscale, probe, version)` の `start()`（ロックを待たずに取る。取れなければ `DashboardAlreadyRunning`）、`wait`、`request_stop`、`stop`。`application/dashboard_http.DashboardHttp` が `hosts`、`embed_hosts`、`version` を持ち、`_repositories()` が `server: {version, started_at, embed_hosts}` を返す。`infra/dashboard_store` の `write_server_record`、`read_server_record`、`remove_server_record`。`infra/dashboard_files.pid_alive`。
	- コマンド：`application/dashboard_commands.serve`（SIGTERM／SIGINT で `request_stop`、0.5秒ごとの待ちの輪）。`cli/catalog.py` は 58 の leaf。`commands/canonical_dispatch.py` の `REPOSITORY_INDEPENDENT_HANDLERS`。
	"""

target: """
	- `runtime/domain/dashboard_service.py`：ラベル、ファイルの名前、`DashboardServiceSpec`（`SchedulerSpec` を広げる）、plist と systemd の単位の形、記録した引数の読み戻し、終了コード75。
	- `runtime/infra/dashboard_service.py`：`DashboardLaunchdService`（`LaunchdScheduler` を継ぐ）、`DashboardSystemdService`（`SystemdScheduler` を継ぐ）、工場 `dashboard_service_for(kind, *, environment)`、`installed_version()`。
	- `runtime/infra/canonical_scheduler_launchd.py`：plist の中身を作るところを `_payload(spec)` に分ける（振る舞いは変えない）。
	- `runtime/application/dashboard_service.py`：`install`、`status`、`uninstall` の処理。
	- `runtime/infra/dashboard_server.py`：`add_tailscale()`（後から Tailscale の住所に待ち受ける）、`defer_tailscale`、起動の版。
	- `runtime/application/dashboard_commands.py`：`serve` の `--service` と `--state-root`、待ちの輪（ロックの取り直し、Tailscale の取り直し、版の確かめ）。
	- `runtime/application/dashboard_http.py`：`/api/v1/repositories` の `server` に `installed_version`、`restart_required`。
	- `cli/catalog.py`、`commands/canonical_dispatch.py`：3つの leaf（58 → 61）と `serve` の2つの引数。
	"""

design: {
	"D-01": {
		title: "ファイルの形（domain）"
		text: """
			`domain/dashboard_service.py` に置く。

			- 定数：`DASHBOARD_LAUNCHD_LABEL = "io.github.chemitaro.spec-dock.dashboard"`、`DASHBOARD_SYSTEMD_SERVICE = "spec-dock-dashboard.service"`、`SERVICE_LOG = "dashboard/service.log"`（状態の置き場から）、`VERSION_CHANGED_EXIT = 75`、`RESTART_SECONDS = 10`、`LOCK_RETRY_SECONDS = 30`、`TAILSCALE_RETRY_SECONDS = 30`、`VERSION_CHECK_SECONDS = 60`。
			- `DashboardServiceSpec(SchedulerSpec)`：`port: int = 47800`、`tailscale: bool = False`、`tailscale_dir: Path | None = None` を足す。`arguments()` は `(実行ファイル, "dashboard", "serve", "--service", "--port", N, ["--tailscale"], "--state-root", 状態の置き場)`。`log` は `<state_root>/dashboard/service.log`。`search_path(tail)` は git の場所、Tailscale の場所（git と違えば）、末尾。
			- `dashboard_launchd_plist(spec, label)`：`Label`、`ProgramArguments`、`WorkingDirectory`（ホーム）、`RunAtLoad: true`、`KeepAlive: true`、`ThrottleInterval: 10`、`StandardOutPath`／`StandardErrorPath`（`log`）、`EnvironmentVariables.PATH`。
			- `dashboard_systemd_unit(spec)`：`[Unit] Description`、`[Service] Type=simple`、`WorkingDirectory=%h`、`Environment=PATH=…`、`ExecStart=…`（同期と同じ `systemd_quote`）、`Restart=always`、`RestartSec=10`、`StandardOutput=append:<log>`、`StandardError=append:<log>`、`[Install] WantedBy=default.target`。
			- `service_settings(arguments) -> ServiceSettings(port, tailscale, state_root) | None`：記録した引数の読み戻し（`status` が使う）。`dashboard serve --service` の形でなければ None。
			"""
		satisfies: ["R-01", "R-02", "R-07"]
	}
	"D-02": {
		title: "管理の側の部品（infra）"
		text: """
			- `LaunchdScheduler` の `needs_change` と `ensure` が呼ぶ plist の組み立てを `_payload(spec)` に分ける（同期の振る舞いは変えない）。`DashboardLaunchdService(LaunchdScheduler)` は `label` を `DASHBOARD_LAUNCHD_LABEL` にし、`_payload` を `dashboard_launchd_plist` にする。`ensure` は、ファイルが変われば `bootout` → `bootstrap`（KeepAlive のサービスはこれで新しい引数で起動し直す）。`remove` は `bootout` と削除。`observe` は plist があるかと `launchctl print` の結果。
			- `DashboardSystemdService(SystemdScheduler)`：単位は1つ（timer なし）。`_files` は単位だけ、`_active` は `is-active spec-dock-dashboard.service`。`ensure` は書き、`daemon-reload`、`enable --now`、ファイルが変わり既に動いていれば `restart`。`remove` は `disable --now`（入っていて断られたら止まる）、削除、`daemon-reload`。`observe` は単位があるかと `is-active`。
			- 両方に `recorded_arguments()`（plist の `ProgramArguments`、単位の `ExecStart` を `shlex` で分けたもの）を持たせる。
			- 工場 `dashboard_service_for(kind, *, environment)`：`launchd` は `<HOME>/Library/LaunchAgents`、`systemd` は `${XDG_CONFIG_HOME:-<HOME>/.config}/systemd/user`。テストはこの関数を差し替える（conftest の守りに足す）。
			- `installed_version() -> str | None`：`importlib.metadata.version("spec-dock")`。読めなければ None。
			"""
		satisfies: ["R-01", "R-03", "R-05"]
	}
	"D-03": {
		title: "`install`、`status`、`uninstall` の処理（application）"
		text: """
			`application/dashboard_service.py`。どれもチェックアウトなしで動き、版3のチェックアウトの中では `serve` と同じく `CANONICAL_NOT_MIGRATED` で止まる。

			- 管理の種類：`detect_runtime_environment()` の `system` が darwin なら launchd。linux なら `detect_service_manager` で `systemd_present` かつ `systemd_user` が True のとき systemd。どちらでもなければ「入れられない」。
			- `install`：番号を確かめる（1〜65535、既定 47800。外れれば `DASHBOARD_PORT_INVALID`、終了コード2）。入れられなければ `DASHBOARD_SERVICE_UNSUPPORTED`（終了コード3、次の1手 `spec-dock dashboard serve`）。実行ファイルは、登録簿の同期の常駐（`scheduler_for(registry.scheduler)`）の `recorded_executable` が使えればそれ、なければ `spec_dock_executable()`。git の場所は登録簿の最初の行の git、なければ PATH の git、なければ `/usr/bin`。Tailscale の場所は PATH の `tailscale`。`<state_root>/dashboard/` を作り、`ensure`。結果は `scheduler`、`path`、`outcome`（created／updated／unchanged）、`port`、`tailscale`、`state_root`、`url`（`http://127.0.0.1:<N>/`）、`log`。効果は `dashboard.service`（unchanged なら unchanged）。`SchedulerError` は `DASHBOARD_SERVICE_FAILED`（終了コード3、`details.path`、次の1手は `install` のやり直しか `uninstall`）。
			- `status`：書かない。`supported`、`scheduler`、`path`、`installed`、`loaded`、`detail`、記録した `port`／`tailscale`／`state_root`、`server`（記録した状態の置き場（なければ今の置き場）の在りかの記録の `pid` が生きていれば `{pid, urls, version, started_at}`、なければ null）、`running`、`package_version`（`installed_version()`）、`restart_pending`（動いていて版が違う）。入れられない環境では `supported: false` と、ほかは false／null。
			- `uninstall`：入れられない環境では `removed: false` で成功。`remove` の後、記録した状態の置き場（なければ今の置き場）の `dashboard/service.log` を消す。結果は `removed`、`path`、`log_removed`。効果は `dashboard.service`（removed なら succeeded、でなければ unchanged）。`SchedulerError` は `DASHBOARD_SERVICE_FAILED`。
			"""
		satisfies: ["R-01", "R-02", "R-03", "F-01", "F-02", "F-03"]
	}
	"D-04": {
		title: "`serve --service` の待ちの輪"
		text: """
			`dashboard_commands.serve` に `--service`（`argparse.SUPPRESS`）と `--state-root`（絶対の道。`resolve_state_root(override=…)`）を足す。時間と版の部品（`clock`、`version_reader`、間隔）は引数で差し替えられるようにする。

			1. シグナル（SIGTERM、SIGINT）の扱いを先に入れる（待ちの間にも止まれるように）。
			2. 起動：`DashboardServer(root, port, tailscale, defer_tailscale=service)` の `start()`。`DashboardAlreadyRunning` のとき、前面なら今までどおり `already_running` で終わる。`--service` なら、標準エラーに1回知らせ、止まる合図か `LOCK_RETRY_SECONDS` まで待って取り直す。止まる合図なら `already_running` の結果で終わる（終了コード0）。
			3. 起動の後、0.5秒ごとの輪で：(a) `--service --tailscale` で住所がまだなら、`TAILSCALE_RETRY_SECONDS` ごとに `server.add_tailscale()`。(b) `VERSION_CHECK_SECONDS` ごとに `version_reader()` を読み、起動のときの版（`version_reader()` の最初の値）と違えば、`--service` なら輪を抜けて止め、標準エラーに知らせて `SystemExit(75)`。前面なら1回だけ標準エラーに知らせ、`server.app.installed_version` を新しい版にする（終了しない）。版が None なら比べない。
			4. 止まる：今までどおり `server.stop()`（自分の在りかの記録を消す）。
			- 起動の失敗（`DASHBOARD_PORT_IN_USE` など）は、前面も常駐も今までどおり終了コード3。常駐では管理の側が10秒後に起動し直し、理由は `service.log` に残る（F-04）。
			"""
		satisfies: ["R-04", "R-05", "R-06", "F-04"]
	}
	"D-05": {
		title: "後から Tailscale に待ち受ける（infra）と API の版の項目"
		text: """
			- `DashboardServer(…, defer_tailscale=False)`：True で住所が得られなければ、`DASHBOARD_TAILSCALE_UNAVAILABLE` で止まらずに手元だけで起動する。`tailscale_pending` が True のまま。
			- `add_tailscale() -> bool`：住所を得て、同じ番号で待ち受け、スレッドで動かし、`app.hosts` と `app.embed_hosts` に住所（と MagicDNS の名前）を足し、在りかの記録を `urls.tailscale` つきで書き直す。住所がないか待ち受けに失敗すれば False（次に取り直す）。`DashboardHttp` の `hosts`／`embed_hosts` は tuple の差し替えで足す（読みの途中でも壊れない）。
			- `DashboardHttp` に `installed_version`（既定は `version`）を持たせ、`_repositories()` の `server` に `installed_version` と `restart_required`（`installed_version != version`）を足す。
			"""
		satisfies: ["R-05", "R-06"]
	}
	"D-06": {
		title: "コマンドの一覧、ヘルプ、文書"
		text: """
			`LEAF_PATHS` に `dashboard service install`、`dashboard service status`、`dashboard service uninstall`（58 → 61）。引数は `install` が `--port`、`--tailscale`、ほかはなし。`serve` に `--service`（help は SUPPRESS）と `--state-root`。`HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_help_spec` の Target／Reads／Writes／Does not／JSON、`REPOSITORY_INDEPENDENT_HANDLERS`。

			コマンドの数を縛るテスト（58 → 61）と、`reference_cli.md`（コマンドの表と「ダッシュボードのサーバーの契約」に常駐の節）、`docs/README.md`、README、`cli-redesign-guide.html`（配布と dogfood の写し）を直し、`static-inventory.json` の変えた行の sha256 を更新して前の値を `known_old_sha256` に足す。
			"""
		satisfies: ["R-07"]
	}
}
