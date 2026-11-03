package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00427。plan.cue の slice `iss-00530`（covers: R-28）を、この Issue の番号に書き直した。
// Epic の番号は「Epic R-28」のように書く。この Issue の番号は R-01 などである。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
assurance: {
	level:  "standard"
	reason: "利用者の PC に常駐の設定（launchd、systemd）を入れ外しする。誤ると常駐が残るか、同期を巻き込む。uninstall と版を戻すことで回復できる。"
}

purpose: "利用者が明示して入れたときだけ、ログインのときにダッシュボードのサーバーを起動する常駐（`spec-dock dashboard service install`／`status`／`uninstall`）を作る。常駐は前面の `dashboard serve` と共存し、SpecDock のパッケージを更新したら新しい版で起動し直す。"

background: """
	- 親の Epic（epic-00427）の R-28（言い直した約束3：常駐は利用者が明示して入れたときだけ）と、設計 D-14（常駐）、D-01 の `dashboard service` の3つのコマンド、D-02 の「常駐では手元で先に始め、30秒ごとに Tailscale の住所を取り直して足す」を、この Issue が作る。
	- 前面のサーバー `dashboard serve`、在りかの記録 `<state_root>/dashboard/server.json`、二重起動を防ぐロック `server.lock` は #529 でマージ済み（`runtime/infra/dashboard_server.py`、`runtime/application/dashboard_commands.py`）。この Issue はそれを常駐から動かす。
	- 定期の同期の常駐は `runtime/infra/canonical_scheduling.py` の `Scheduler` と、launchd（`canonical_scheduler_launchd.py`）、systemd（`canonical_scheduler_systemd.py`）の部品で入る。ダッシュボードの常駐は同じ部品を、別のラベルと別の形のファイル（常に動くサービス）で使う。
	"""

includes: [
	"`spec-dock dashboard service install [--port N] [--tailscale]`、`dashboard service status`、`dashboard service uninstall`（公開のコマンドが 58 → 61）と、コマンドの数を縛るテストと文書",
	"`dashboard serve` の常駐のための引数 `--service`（利用者向けでない）と `--state-root`、常駐のときの動き（ロックの待ち、Tailscale の住所の取り直し、版の更新での終了）",
	"前面の `serve` が版の更新を知ったときの知らせ（標準エラーへの1回の知らせと、`/api/v1/repositories` の `server` の項目）",
	"launchd の LaunchAgent（`io.github.chemitaro.spec-dock.dashboard`）と systemd のユーザーの単位（`spec-dock-dashboard.service`）のファイルの形",
]
excludes: [
	"画面の帯での起動し直しの促し（画面の資源 `assets/dashboard/` は触らない。API の項目だけを足し、画面は後の Issue が読む）",
	"`canonical link` や `installation update` から常駐を入れること（言い直した約束3で、しない）",
	"systemd のない Linux での常駐の代わり（同期の loop にあたるもの）を作ること",
	"版の番号と `migration.md`（#534）",
	"テストで本物の launchd と systemd に登録すること、利用者の launchd の登録を変えること",
]

requirements: {
	"R-01": {
		title: "利用者が `dashboard service install` で、ダッシュボードの常駐を入れられる"
		text: """
			macOS では `~/Library/LaunchAgents/io.github.chemitaro.spec-dock.dashboard.plist` を書いて `launchctl bootstrap` し、Linux（systemd のユーザーの管理がある）では `~/.config/systemd/user/spec-dock-dashboard.service`（`XDG_CONFIG_HOME` に従う）を書いて `systemctl --user enable --now` する。常駐は `spec-dock dashboard serve --service --port N [--tailscale] --state-root <状態の置き場>` を、常に動くサービス（launchd の `KeepAlive`、systemd の `Restart=always`、`RestartSec=10`）として動かす。同期の常駐（`…canonical-sync`）とはラベルもファイルも分け、同期の常駐のファイルに触らない。

			実行ファイルは、同期の常駐が記録したものが使えればそれを、なければ今の `spec-dock` を記録する。同じ設定でもう一度入れると何もしない（`unchanged`）。`--port` か `--tailscale` を変えて入れ直すと、ファイルを書き直して起動し直す（`updated`）。
			"""
		acceptance: [
			"`dashboard service install` の後、launchd では決まったラベルの plist（`KeepAlive`、`RunAtLoad`、引数 `dashboard serve --service --port 47800 --state-root …`）、systemd では `Restart=always` の単位ができ、`bootstrap` か `enable --now` が1回呼ばれる（テストは差し替えた部品で見る）",
			"同じ引数で2回目を実行すると結果が `unchanged` で、ファイルも登録も変わらない。`--port 47801` で入れ直すと `updated` になり、起動し直す",
			"同期の常駐のファイル（`io.github.chemitaro.spec-dock.canonical-sync.plist`、`spec-dock-canonical-sync.{service,timer}`）が変わらない",
		]
	}
	"R-02": {
		title: "利用者が `dashboard service status` で、入っているか、動いているか、URL、版を見られる"
		text: "`status` は何も書かない。設定のファイルがあるか（`installed`）、管理の側に読み込まれているか（`loaded`）、在りかの記録の `pid` が生きているか（`running`）、URL（`urls.local`、`urls.tailscale`）、設定の番号と Tailscale の有無と状態の置き場、動いているサーバーの版と、今入っているパッケージの版、版が違うか（`restart_pending`）を返す。常駐を入れられない環境では `supported: false` を返す（止まらない）。"
		acceptance: [
			"入れる前は `installed: false`、入れた後は `installed: true` と設定の番号、在りかの記録があり `pid` が生きていれば `running: true` と URL を返す",
			"在りかの記録の版と今のパッケージの版が違えば `restart_pending: true` を返す",
		]
	}
	"R-03": {
		title: "利用者が `dashboard service uninstall` で、常駐を何も残さずに外せる"
		text: "常駐を止め（launchd の `bootout`、systemd の `disable --now`）、設定のファイルと常駐の記録（launchd の `<state_root>/dashboard/service.log`。systemd の出力は journal）を消す。入っていなければ何もせずに成功する（`removed: false`）。同期の常駐には触らない。systemd のユーザーの管理が一時的に応えない Linux でも、単位のファイルがあれば `status` に見え、`uninstall` で外す（外せなければ F-02 で止まる）。"
		acceptance: [
			"`uninstall` の後、設定のファイルと `service.log` が残らず、`bootout` か `disable --now` が呼ばれる",
			"2回目の `uninstall` は `removed: false` で成功する",
			"systemd の単位があり、ユーザーの管理が判定できないとき、`status` は `installed: true`、`uninstall` は単位を消す",
		]
	}
	"R-04": {
		title: "常駐は前面の `serve` と共存し、前面が止まれば引き継ぐ"
		text: "`--service` で起動したサーバーは、前面の `serve` が `server.lock` を持っていれば、終わらずに30秒ごとにロックを取り直して待つ（launchd と systemd が起動と終了を繰り返さないように）。前面が止まれば、次の取り直しで自分が起動する。待っている間に SIGTERM を受ければ、待ちをやめて終了コード0で終わる。前面の `serve` は今までどおり、常駐が動いていればその URL を示して終わる。"
		acceptance: [
			"ロックを持つ別のサーバーがあるとき、`--service` のサーバーは終わらずに待ち、そのサーバーが止まると起動して在りかの記録を書く（待つ間隔を短くしたテスト）",
			"待っている間の SIGTERM で、終了コード0で終わる",
		]
	}
	"R-05": {
		title: "パッケージを更新すると、常駐のサーバーが新しい版で動く"
		text: "サーバーは起動のときの版（`importlib.metadata.version(\"spec-dock\")`）を覚え、60秒ごとに読み直す。`--service` のときは、版が違えば止まって（在りかの記録を消して）終了コード75で終わり、launchd の `KeepAlive` と systemd の `Restart=always` が新しい版で起動し直す。前面の `serve` は終了せず、標準エラーに1回だけ起動し直しを促し、`/api/v1/repositories` の `server` に `installed_version` と `restart_required: true` を出す。版が読めないときは変わっていないと見なす。"
		acceptance: [
			"`--service` のサーバーで、版を返す部品の値を変えると、在りかの記録を消して終了コード75で終わる",
			"前面のサーバーでは終了せず、API の `server.restart_required` が `true`、`installed_version` が新しい版になる",
		]
	}
	"R-06": {
		title: "常駐は Tailscale の住所が得られなくても手元で先に始め、得られたら足す"
		text: "`--service --tailscale` のときに `tailscale ip -4` で住所が得られなければ、`127.0.0.1` だけで起動し、30秒ごとに住所を取り直す。得られたら同じ番号でその住所にも待ち受け、`Host` の検査と埋め込みの許す住所に足し、在りかの記録の `urls.tailscale` を書き直す。前面の `serve --tailscale` は今までどおり `DASHBOARD_TAILSCALE_UNAVAILABLE` で止まる。"
		acceptance: [
			"住所を返さない部品で `--service --tailscale` を起動すると、手元で応え、在りかの記録の `urls.tailscale` が null。部品が住所を返すようにすると、次の取り直しで `urls.tailscale` が入り、その `Host` の要求に応える",
		]
	}
	"R-07": {
		title: "公開のコマンドが61になり、一覧、ヘルプ、補完、文書が合う"
		text: "`cli/catalog.py`、`canonical_dispatch.py`、コマンドの数を縛るテスト、`reference_cli.md`、`docs/README.md`、README、`cli-redesign-guide.html`（配布と dogfood の写し）を直し、`static-inventory.json` の該当行の sha256 を更新する。`reference_cli.md` に、常駐のファイルの形、`--service` の動き、終了コード75、`status` の JSON を契約として書く。"
		acceptance: [
			"`len(LEAF_PATHS) == 61` で、`help dashboard service install` などがヘルプを出し、文書のコマンドの数が61",
			"`static-inventory.json` の変えた行の sha256 がファイルと一致し、前の値が `known_old_sha256` にある",
		]
	}
}

failures: {
	"F-01": {
		title: "常駐を入れられない環境（systemd のユーザーの管理がない Linux）では、`install` は何も書かずに止まり、`serve` を案内する"
		text:  "`DASHBOARD_SERVICE_UNSUPPORTED`（終了コード3）。次の1手は `spec-dock dashboard serve`。`uninstall` は書くものがないので成功し、`status` は `supported: false` を返す。"
	}
	"F-02": {
		title: "`launchctl` か `systemctl` が失敗したら、`DASHBOARD_SERVICE_FAILED`（終了コード3）で止まり、出力と次の1手を示す"
		text:  "`install` の途中で失敗したときは、書いた設定のファイルの道を示し、同じ `install` のやり直しか `uninstall` を案内する。`uninstall` の `bootout` が断られたときは、設定のファイルを消さずに止まり、やり直せるようにする。"
	}
	"F-03": {
		title: "番号が 1〜65535 でなければ、`install` は何も書かずに `DASHBOARD_PORT_INVALID`（終了コード2）で止まる"
		text:  "常駐の URL が決まらないので、番号0（空いた番号）は常駐では使わない。"
	}
	"F-05": {
		title: "`install` と `uninstall` に `--dry-run` を付けると、何もせずに使い方の誤り（終了コード2）で止まる"
		text:  "常駐の入れ外しは、計画だけの形を持たない（`canonical sync` などと同じく、共通の `--dry-run` を受け付けない leaf にする）。`--yes` も受け付けない（`dashboard serve`、`hide`、`show` と同じく、利用者が実行すること自体が明示の操作）。"
	}
	"F-04": {
		title: "常駐の起動で番号が使われていれば、サーバーは終了コード3で終わり、理由を常駐の記録に書く"
		text:  "管理の側が10秒ごとに起動し直す。`status` は `running: false` を示し、`service.log` に `DASHBOARD_PORT_IN_USE` が残る。"
	}
}

constraints: [
	"テストは本物の launchd と systemd に登録しない。`launchctl` と `systemctl` は差し替えた実行の部品で見る。tests/conftest.py の守り（本物の管理のコマンドを呼べば失敗）に、ダッシュボードの常駐の工場も加える",
	"利用者の環境（`~/Library/LaunchAgents`、`~/.config/systemd/user`、`~/.local/state/spec-dock/`）をテストで変えない",
	"画面の資源（`src/spec_dock/assets/dashboard/`）は触らない（#531、#532、#544 の担当）",
	"判定、API の道筋、在りかの記録の形は #529 のものを使い、別に書かない。足すのは `/api/v1/repositories` の `server` の項目（`installed_version`、`restart_required`）だけ",
]

decisions: [
	"2026-11-04（作業者）：`install` は、別の状態の置き場（別の `XDG_STATE_HOME`）で入れた常駐があっても書き直す。常駐は利用者ごとに1つで、利用者が明示して実行したため。`status` は記録した状態の置き場を示す",
	"2026-11-04（作業者）：常駐の記録（標準出力と標準エラー）は `<state_root>/dashboard/service.log` に書き、`uninstall` で消す（何も残さない）",
	"2026-11-04（作業者）：常駐の PATH は、同期と同じ形（git の場所、Tailscale の場所、決まった末尾）にする。Tailscale の場所は入れるときに `tailscale` を探して記録する（macOS のアプリの中の実行ファイルは `dashboard_network` が直接探す）",
	"2026-11-04（作業者）：終了コード75は CLI の結果の封筒（0〜7）の外なので、`serve --service` は封筒を書かずに `SystemExit(75)` で終わる。常駐の管理の側だけが読む",
	"2026-11-04（作業者）：systemd の単位の出力は journal に任せる（`StandardOutput=append:` の道は引用符を解かないため、空白を含む状態の置き場で壊れる）。`service.log` は launchd だけ",
	"2026-11-04（仕様のレビューの P2 の扱い）：画面の帯での起動し直しの促し（Epic D-14）は、この Issue が API の `server.installed_version`／`restart_required` を足し、画面は後の Issue（#544 か後続）が読む。担当の割り当ては統括に知らせる。Epic R-28 の受け入れ「ログインし直すとサーバーが動く」は、本物の launchd を使うので、この Issue のテストでは確かめず、#534 の配布の後に利用者の PC で確かめる",
	"2026-11-04（作業者）：`--service` は利用者向けのヘルプに出さない（`argparse.SUPPRESS`）。`--state-root` は `canonical sync` と同じく見える引数にする",
]
