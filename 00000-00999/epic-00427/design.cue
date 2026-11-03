package spec

// 設計（Epic）。型 specdock/v1。
// コードの場所は 2026-11-03 の main（0.5.1、24f291f9c）で確かめた。
// 構成の判断の経緯は `.workbench/architecture-synthesis-20261103.md`（分析役2人の独立の分析と、統括の判断）。

goals: [
	"構造（スナップショット）と内容（カタログ）を合わせて見せる、見るだけのダッシュボードを、利用者ごとに1つの、標準ライブラリだけの手元のサーバーで、全リポジトリに配る",
	"状態の判定を、`dependency check` と同じ領域の関数（`evaluate_all`）から作り、画面と要約の JSON と CLI で食い違わないようにする",
	"company-os などのほかのダッシュボードが、SpecDock の画面を作り直さずに埋め込めるようにする",
	"段階1（構造の画面）を先に出して使い始め、段階2（文書の画面）を後から足す。第2・第3段階（orca-web との連携）が口を足せる形にしておく",
	"今の Markdown と PlantUML のダッシュボードを、段階1の版で撤去する",
]

current: """
	- 構造のスナップショット（C10）は `runtime/infra/github_snapshot.py` の `SnapshotStore` が `${XDG_STATE_HOME:-~/.local/state}/spec-dock/github/<host>/<owner>/<name>/snapshot.json` に書く（版1。`runtime/domain/canonical_structure.py` の `StructureSnapshot`）。`SnapshotStore.load()` はネットワークに触れず、例外を出さない（読めない、知らない版のときも「ない」を返す）。
	- 登録簿 `<state_root>/canonical-registry.json`（`runtime/infra/canonical_registry.py`、`RegistryEntry(catalog, main_checkout, repository, …)`）に、このPCで `canonical link` した全カタログが載る。`repository` は null のことがあり、同じリポジトリの2つのクローンは2行になる。
	- 定期の同期は、`runtime/infra/canonical_scheduling.py` の `Scheduler`（`ensure`、`remove`、`observe`、`kick`。launchd、systemd、loop の3つ）で入る。
	- 着手の判定は `runtime/domain/canonical_readiness.py` の `evaluate_readiness`／`evaluate_all`。`dependency check` と `work start` が使う。
	- カタログの Scope の場所は `canonical_layout.scope_relative`、Artifact の一覧は `canonical_scope_read.catalog_artifacts`、CUE か Markdown かは `scope_check.scope_format`。このPCの worktree ごとの選択は `canonical_work.canonical_worktree_rows`。
	- 描画は `scope_render.render_scope_html`（CUE だけ。`cue` の実行ファイルが要る）。デザインシステムは配布資産 `spec-dock/design-system/`、図の部品は `src/spec_dock/assets/vendor/`（`infra/diagram_vendor.py`）。Markdown を包む道は `presentation/spec_page.wrap_page`。
	- 今のダッシュボードは、定期の同期（`canonical_sync._refresh_dashboards`）が main のチェックアウトの `spec-dock/` に5つのファイルを書く。
	- HTTP のサーバーのコードはない。実行時の依存は標準ライブラリだけ（3.10 では `tomli`）。公開のコマンドは53。
	- 「paused」と「resume」の語は、カタログの同期の停止に使われている（`CANONICAL_PAUSED`、`canonical resume`）。
	"""

target: """
	- `spec-dock dashboard serve` か、明示して入れた常駐（`dashboard service install`）の1つのサーバーが、登録簿の、隠していない全リポジトリを `/r/<host>/<owner>/<name>/` で配る。`dashboard hide`／`show` で表示を止めて戻す。`dashboard summary` が要約を CLI から返す。
	- 段階1の版（0.6.0 の予定）で、3つの画面（構造の図、ボード、時間の軸。ホームは構造の図）と詳しい画面、横断の概況、埋め込みの表示、要約、在りかの記録が動き、今の5つのファイルの生成が消える。
	- 段階2の版（0.7.0 の予定）で、詳しい画面に、CUE と Markdown の文書、報告と ADR、計画の進み具合が出る。
	"""

design: {
	"D-01": {
		title: "コマンド：`dashboard` の家族"
		text: """
			公開のコマンドを足す（53 → 61）。`runtime/cli/catalog.py` の `LEAF_PATHS`、`LEAF_ARGUMENTS`、`HELP_EFFECTS` と、`commands/canonical_dispatch.py` の `CANONICAL_HANDLERS` に足し、コマンドの数を縛るテストと文書（`reference_cli.md`、README、`cli-redesign-guide.html`）を直す。

			| コマンド | 働き |
			|---|---|
			| `dashboard serve [--port N] [--tailscale] [--json]` | 前面で動き、Ctrl-C か SIGTERM で止まる。起動のときに URL と見せるリポジトリの一覧を書く。すでに動いていれば、その URL を示して終わる（終了コード0）。常駐から起動されたときは D-14 の決まりに従う |
			| `dashboard service install [--port N] [--tailscale]` | 常駐を入れる（D-14） |
			| `dashboard service status` | 常駐が入っているか、動いているか、URL |
			| `dashboard service uninstall` | 常駐を外す |
			| `dashboard hide [REPOSITORY]` | 表示から外す（D-13）。チェックアウトの中では省ける |
			| `dashboard show [REPOSITORY]` | 表示に戻す |
			| `dashboard list [--json]` | 登録したリポジトリと、表示中か隠しているか、サーバーの URL |
			| `dashboard summary [REPOSITORY] [--json]` | R-21 の要約。サーバーが動いていなくても、隠したリポジトリでも動き、GitHub にもサーバーにも要求を送らない（在りかの記録の `pid` が生きているかだけを見る）。スナップショットがないときは `DASHBOARD_SNAPSHOT_MISSING`（終了コード3） |

			`REPOSITORY` は `owner/name` か `host/owner/name`。同じリポジトリのクローンが2つ登録されているときは、main のチェックアウトの道で選ばせる（`DASHBOARD_REPOSITORY_AMBIGUOUS`、終了コード3）。`repository` が分からない登録の行は、一覧に「リポジトリが分からない」と出し、配らない。
			"""
		satisfies: ["R-01", "R-21", "R-27", "R-28"]
	}
	"D-02": {
		title: "サーバー：標準ライブラリの HTTP、待ち受け、番号、二重起動"
		text: """
			`http.server.ThreadingHTTPServer` で作る（新しい依存を足さない）。HTTP は `runtime/infra/dashboard_server.py`、応答の組み立ては `runtime/application/dashboard_*.py` に置く（第2段階で orca-web の口を足すときも、組み立ての側だけを足す）。

			- 待ち受け：既定は `127.0.0.1` だけ。`--tailscale` のときは `tailscale ip -4` の住所にも待ち受ける。`0.0.0.0` には待ち受けない。前面の `serve --tailscale` で住所が得られなければ、起動せずに `DASHBOARD_TAILSCALE_UNAVAILABLE`（終了コード3）で止まる（F-08）。常駐では手元で先に始め、30秒ごとに住所を取り直して足す（R-28）。
			- 番号：既定は 47800 の1つ（`--port` で変える）。使われていれば、起動せずに `DASHBOARD_PORT_IN_USE`（終了コード3）で止まる（F-07）。
			- 二重起動：`<state_root>/dashboard/server.lock` の排他のロックで防ぐ。2つ目の `serve` は、動いているサーバーの URL を示して終わる。
			- 受け付けるのは `GET` と `HEAD` と、「見た」の口（D-18）の `POST` だけ（R-04）。`Host` の見出しが、待ち受けの住所と番号（`127.0.0.1`、`localhost`、Tailscale の IP、このPCの MagicDNS の名前）でなければ 421 で断る。
			- リポジトリの切り離し：リポジトリごとのモデルの組み立てを例外で閉じ込め、失敗はそのリポジトリの画面と API にだけ返す（R-03、F-12）。
			- 新しい登録：登録簿の時刻が変わったら読み直す（R-01）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04"]
	}
	"D-03": {
		title: "道筋とデータの口"
		text: """
			画面は、サーバーの JSON の API だけを読む。どれも、スナップショット、カタログ、このPCの worktree をその場で読み、GitHub に問い合わせない（R-04、R-07）。

			- 画面の道筋：`/`（横断の概況、D-16）、`/r/<host>/<owner>/<name>/`（ホーム＝構造の図）、`…/graph`、`…/board`、`…/timeline`、`…/scopes/<ID>`。表示の切り替えは問い合わせの文字列に持つ（固めない）。`/r/…/scopes/<ID>` の形と `?embed=1` は、変えない契約にする（R-17、R-22）。画面の中のリンクは相対の道で作り、前置きが変わっても動くようにする。
			- 共有の部品：`/assets/…`（画面）、`/ds/…`（デザインシステム）、`/vendor/…`（図の部品）。全リポジトリで共有する。
			- API：`GET /api/v1/repositories`（表示中のリポジトリと、各要約への道）。リポジトリごとに `GET /api/v1/r/<host>/<owner>/<name>/{summary|structure|scopes/<ID>|revision}` と、`POST /api/v1/r/<host>/<owner>/<name>/seen`（D-18）。
			- 自動の更新：画面は5秒ごとにそのリポジトリの `revision`（スナップショットの `fetched_at` とファイルの時刻、カタログの `state.json` の時刻から作る短い印。「見た」の記録の時刻は含めない）を読み、変わったときだけ全体を読み直す（R-08）。
			- 応答の JSON は `schema: "specdock.dashboard/v1"` を持つ。`structure` の形は画面のためのもので、公開の契約にしない。
			"""
		satisfies: ["R-04", "R-07", "R-08", "R-17"]
	}
	"D-04": {
		title: "状態のモデル：`evaluate_readiness` からの5つの状態と、ボードの分け方"
		text: """
			新しい領域の部品 `runtime/domain/dashboard_model.py` に、スナップショットから画面のモデルを作る純粋な関数を置く。

			- 状態（R-10）：どの種類も `evaluate_all` の結果を写す。DONE → 終わった、UNKNOWN → 不明、DOING → 作業中、BLOCKED → 止められている、READY → 着手できる。Epic と Initiative は、DONE と UNKNOWN でなく、子孫のどれかに `in_progress` があれば作業中にする（この1つだけを足す）。止められている理由は `blockers` の `role`（`ancestor` の閉じた親、`prerequisite`、`external`）から作る。判定を別に書かないので、`dependency check` と一致する。
			- ボードの分け方（R-13）：作業中で、下書きでない開いた PR（D-19）を持つ Issue をマージ待ちの列に、ほかの作業中を作業中の列に置く。マージ待ちは、CI が失敗したか衝突のあるものを「直す必要あり」、それ以外（CI が成功、実行中、なし、マージの可否が分からない）を「マージできる」に分ける（R-13）。状態そのものは変えない。
			- 推奨順（R-31）：開いた Scope ごとに、それを直接か間接に待っている開いた Scope の数（後に続く数）と、まだ終わっていない待ち先の数を求め、R-31 の決まりで並べる順番を返す。図と画面は、この順番をそのまま使う。
			- 終わったものを隠すときに残す印：開いた子孫を持つ閉じた Scope（R-12）。
			- 配下の実行の順番：直下の子を、子孫どうしの依存も子の間の依存に数えて、トポロジカルな段（1、2、…）に分ける。外への依存は別に持つ（R-18）。循環は異常として不明に回す。
			- 片付けの候補：配下がすべて閉じたのに開いている Epic と Initiative、閉じたのに開いた配下がある親（R-14、R-20）。
			- 前回からの変化（R-29）：比べる元（D-18 の `baseline`。画面を開いたときに最新だった「見た」の記録）の各 Scope の状態と PR の状態と、今のモデルを比べ、状態が変わった、新しい、PR が変わった（開いた、マージ待ちになった、CI が失敗に変わった、マージされた、閉じた）を印にする。題名、親子、依存だけの変化は数えない。
			- 時間の軸：`created_at` と `closed_at` から、週ごとの作成と完了の累計を作り、最近の動きに Scope の作成と完了、PR の開いた時刻とマージの時刻を並べる（R-16）。
			- 取得の時刻と古さ：`fetched_at` から30分を超えたかを決める。異常は `anomalies` をそのまま渡す（R-09）。
			"""
		satisfies: ["R-09", "R-10", "R-12", "R-13", "R-14", "R-16", "R-18", "R-20", "R-29", "R-31"]
	}
	"D-05": {
		title: "要約の JSON の契約（`specdock.dashboard-summary/v1`）"
		text: """
			D-04 のモデルから作る。項目：`schema`、`repository`、`fetched_at`、`stale`、`counts`（種類ごと・状態ごとの数）、`completion_ratio`、`awaiting_merge`・`in_progress`・`ready`・`blocked`・`cleanup` の一覧（各要素は `id`、`number`、`title`、`state`、`reason`）、`anomaly_count`、`paths`（各 Scope の詳しい画面の道。`/r/<host>/<owner>/<name>/scopes/<ID>`）、`hidden`（隠しているか）、`server`（在りかの記録があり、その `pid` が生きているときだけ、その基点の URL。なければ null。応えるかは確かめない）。

			項目を足すのは版を変えずにできる。消すか意味を変えるときは版を上げる。配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-21"]
	}
	"D-06": {
		title: "在りかの記録（`specdock.dashboard-server/v1`）"
		text: """
			サーバーは起動の後に `<state_root>/dashboard/server.json`（`schema`、`urls.local`、`urls.tailscale`（なければ null）、`pid`、`version`、`started_at`）を原子的に書き、止まるときに消す。強制的に止められて残った記録は、`pid` が生きていないか、`/api/v1/repositories` が応えなければ、読む側が古いと見なす。リポジトリごとの記録は作らない。

			統合ダッシュボードは、この記録で基点を知り、自分のページの住所（手元か Tailscale か）に合う URL を選び、D-03 の道と合わせて埋め込む（R-22）。置き場と形は、配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-22"]
	}
	"D-07": {
		title: "画面の作り：パッケージに同梱する静的な画面"
		text: """
			画面は、組み立ての道具を使わない素の HTML、CSS、JavaScript のモジュールで書き、`src/spec_dock/assets/dashboard/` に置いて wheel に同梱する（`assets/**/*` で入る）。配布資産（`static-inventory.json`）には入れない。図の部品とデザインシステムもサーバーが配り、CDN に頼らない（R-24）。

			- ホームは構造の図（R-15）。上の帯に、リポジトリの切り替え（R-03）、3つの画面の切り替え、今のリポジトリの検索、取得の時刻（R-17）を置く。PC では本体を幅いっぱいにし、選んだものの要点を右の欄に、スマートフォンでは下から出す。見た目の決まり（色、文字、余白、部品）は、2026-11-03 に利用者が選んだ案D（説明資料のデザインシステム `ds.css` を使う）と、それを直した試作（`artifacts/20261103t150110z--dashboard-design-d2.html`。要点は同じ名前の `.md`）に従う。状態の色と記号は、作業中＝accent の半円、着手できる＝ok の三角、止められている＝danger の八角形と斜線、不明＝warn のひし形、終わった＝灰色の印。
			- 明るい表示と暗い表示は `prefers-color-scheme` に従う。幅 390px で横にはみ出さない。高さは `100vh` でなく `100dvh` か親の高さで決める（iframe の中でも崩れないため）（R-06）。
			- 状態の札は、色、記号、言葉の3つで示し、凡例を置く（R-11）。
			- 画面の状態は URL だけに持つ（埋め込まれたときに、ブラウザーの保存の領域が分けられても困らないため）。
			- 速さ：250件の構造で、ボードは2秒以内、ホームの構造の図は PC で2秒・iPhone で4秒以内、すべての構造の図は PC で3秒以内（R-13、R-15、F-11）。モックの配置の計算（248件で約0.1秒）を基にする。
			"""
		satisfies: ["R-03", "R-06", "R-11", "R-13", "R-24"]
	}
	"D-08": {
		title: "3つの画面と詳しい画面"
		text: """
			データは D-03 の API から読む。見た目は、利用者が選んだデザイン案に従う。

			- 構造の図（R-15、ホーム）：依存の線は、配置の後に、箱と枠の見出しを障害物にした直交の経路を求め、同じ通り道の線分を車線に分けて引く（方法は試作で選んだものを #532 が持ち込む）。車線が足りないときは配置の隙間を広げて引き直す。線が箱を通らず、同じ向きで重ならないことを、テストで機械的に確かめる。上の状態の印で目立たせる、片付けの候補を畳む、選んだ箱の上流と下流をすべて強調する（直接と2段目より先を分ける）。入れ子と木の2つの表し方、範囲の絞り込み、依存の線の3つの切り替え、段の表示、折り返し、拡大・縮小・移動、前後の強調と要点、PC のダブルクリックとスマートフォンの2回目のタップでの移動。箱には、状態、ID と番号、題名、保証レベル、PR の印、作業中のブランチ、変化の印。Epic の枠には、進み具合の帯、状態ごとの数、保証レベル。配置の計算は画面の側で行う。指の操作は、図の領域に `touch-action: none` を付け、Pointer Events で2本指の拡大縮小とドラッグを自分で処理し、Safari の `gesturestart` を止めてページ全体の拡大と競合させない。拡大・縮小と「全体を収める」のボタンも置く。
			- 状態のボード（R-13、R-14、R-31）：左から、止められている、着手できる、作業中、マージ待ち（マージできる／直す必要あり）、（終わった）の列。列の中は推奨順。種類の絞り込み、親ごとのまとめ、上の数の帯と片付けの候補の印。一覧の画面は作らない。
			- 時間の軸（R-16）：週ごとの累計の図と、Scope と PR の最近の動き。
			- 詳しい画面（R-18）：見出しと、概要、依存、配下、文書、Artifact のタブ。GitHub の Issue と PR へのリンク。写せるコマンドは置かない。
			- 文書のタブ（段階1）：文書があるかないかだけ。カタログがなければ、そのことと `spec-dock canonical link` を示す（F-05）。
			- 終わったものの切り替え（R-12）。
			"""
		satisfies: ["R-12", "R-13", "R-14", "R-15", "R-16", "R-17", "R-18", "R-31"]
	}
	"D-09": {
		title: "HTML の資料の切り離しと、枠の決まり"
		text: """
			- 資料：カタログの資料（Artifact、`explanation.html` など）は `/r/<host>/<owner>/<name>/files/<ID>/…` から配り、この道から返すすべての応答に、形式によらず `Content-Security-Policy: sandbox allow-scripts allow-popups`（`allow-same-origin` なし）と `X-Content-Type-Options: nosniff` を付ける（SVG のようにスクリプトを含められるほかの形式も切り離すため）。資料は固有でない起点で動き、ダッシュボードの画面の DOM と、どのリポジトリの API の JSON にも触れられない（API には CORS の見出しを付けない）。1つの起点に全リポジトリが載るので、この切り離しは欠かせない（R-05、F-09）。配るのは、その Scope のディレクトリの中の通常のファイルだけで、リンクと `..` を断る。
			- 共有の部品：固有でない起点の資料がデザインシステムと図の部品を読めるよう、`/ds/` と `/vendor/` の静的なファイルにだけ `Access-Control-Allow-Origin: *` を付ける（データを含まないため）。資料が読む `../../../design-system/` などの相対の道は、サーバーが `/ds/` に写す。
			- 枠の決まり：通常の画面は `Content-Security-Policy: frame-ancestors 'self'`。`?embed=1` の画面と、そこから開く資料は、段階1では `frame-ancestors 'self' http://127.0.0.1:* http://localhost:* http://<Tailscale の IP>:*` にする（見るだけなので、設定なしで company-os に埋め込めるようにする）。`X-Frame-Options` は付けない。書き込みを足す段階で、正確な起点の設定に絞る。
			"""
		satisfies: ["R-05", "R-22"]
	}
	"D-10": {
		title: "今の Markdown と PlantUML のダッシュボードの撤去"
		text: """
			段階1の版で、次を消す：`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py`、`canonical_sync._refresh_dashboards` とその呼び出し、`canonical status` の `dashboard` の項目（`canonical_status_sync.dashboard_item` と `CANONICAL_DASHBOARD_*`）、`canonical remove` の `canonical.dashboard.remove` の手順、`CatalogSyncState.dashboard`、`.gitignore` の5つの名前（`asset_layout.py` と配布する `spec-dock/.gitignore`）、文書の記述（`canonical.md`、`reference_cli.md`、`cli-redesign-guide.html`）、それを確かめるテストと fixture。

			- 契約の変更：`canonical status` の JSON から `dashboard` の項目が消える。`canonical remove` は5つのファイルを消さない。`migration.md` に書き、利用者のリポジトリに残った5つのファイルは消してよいと示す（`.gitignore` から外れるので、`git status` に出る）。
			- `state.json` の古い `dashboard` の欄は、読むときに無視する（書かなくなる）。
			"""
		satisfies: ["R-23"]
	}
	"D-11": {
		title: "段階2：文書の描画（CUE、Markdown、報告、ADR、計画の進み具合）"
		text: """
			- CUE の Scope：`GET /r/…/scopes/<ID>/doc` が `render_scope_html` を `design_system_base="/ds/"`、`vendor_base="/vendor/"` で呼び、D-09 と同じ切り離しで返す。前もって作ったファイルは使わない（R-19）。`scope check` の結果（`check_scope_documents`）の誤りと警告を、詳しい画面に示す。
			- 描画の失敗（`cue` がない、評価の誤り）：その Scope の文書の欄に、検査の結果と次の1手（`cue` を入れる、`spec-dock scope check <ID>`）を示し、ほかの表示は続ける（F-10）。
			- Markdown の文書：`requirement.md`、`design.md`、`plan.md`、`report.md`、ADR を、`spec_page.wrap_page` の薄いページに包んで返す（R-25）。`wrap_page` と中の `_script_safe` を公開の関数にする。
			- 計画の進み具合：CUE の Issue の評価の `steps` の `status` を数え、`dropped` を除いた全体の数、終わった数、作業中の手順を API に足す（R-26）。評価は `cue` を動かすので、Scope ごとに3つの CUE のファイルの時刻で結果を覚えておく。
			"""
		satisfies: ["R-19", "R-25", "R-26"]
	}
	"D-12": {
		title: "読めないとき、古いとき、ないときの扱い"
		text: """
			- スナップショットがない（F-01）：そのリポジトリの画面は開き、構造がないことと次の1手（`spec-dock canonical link`、`spec-dock canonical status`）を示す。`dashboard summary` は `DASHBOARD_SNAPSHOT_MISSING` で失敗する。
			- 30分を超えて古い（F-02）：表示を続け、古いことと取得の時刻を示す。
			- 知らない版（F-03）、読めない（F-04）：`SnapshotStore.load()` は両方を「ない」と返すので、ダッシュボードはファイルを自分で読み、`version` を見て知らない版を見分ける（読めないなら「読めない」）。サーバーは、リポジトリごとに最後に読めたモデルを覚えておき、読めないときはそれで表示を続ける。
			- 構造の異常（F-06）：その Scope を不明として示し、ほかの表示は続ける（D-04）。
			"""
		satisfies: ["R-09"]
	}
	"D-13": {
		title: "表示を止めて戻す（`hide`／`show`）"
		text: """
			印は `<state_root>/dashboard/repositories.json`（`schema: "specdock.dashboard-repositories/v1"`、鍵は `host/owner/name`、値は `hidden_at`）に、ロックつきで原子的に書く。書くのは `dashboard hide`／`show` だけ。リポジトリ、カタログ、登録簿、`CatalogSyncState` には置かない（表示はこのPCの利用者の好みで、同期の契約を巻き込まないため）。

			- サーバーは、隠したリポジトリのモデルを組み立てず、`/api/v1/repositories`、横断の概況、起動のときの見せる一覧から外す。直接の URL には、データを含まない案内（`spec-dock dashboard show <リポジトリ>`）を 404 で返す。
			- 隠しても同期は止まらない。同期も止めたいときは `canonical remove` で、別の話であることを文書に書く。
			- サーバーは `repositories.json` の時刻が変わったら読み直す。
			"""
		satisfies: ["R-27"]
	}
	"D-14": {
		title: "常駐（`dashboard service`）"
		text: """
			`runtime/infra/canonical_scheduling.py` の `Scheduler` の部品を使い、同期とは別のラベル（launchd の `…spec-dock.dashboard`、systemd のユーザーの単位 `spec-dock-dashboard.service`）で、常に動くサービス（launchd の `KeepAlive`、systemd の `Restart=always` と `RestartSec=10`）として入れる。`canonical link` や `installation update` からは入れない（言い直した約束3）。

			- 起動の引数：常駐は `dashboard serve --service` で動く（利用者向けの印でない内部の引数）。
			- 実行ファイル：同期と同じ Python とコンソールを記録する（macOS のフルディスクアクセスの許可を同期と共有するため）。
			- 設定：`--port` と `--tailscale` は、常駐の起動の引数に書く。変えるときは `install` をやり直す。
			- 前面の `serve` との共存：`--service` で起動したとき、前面の `serve` がロックを持っていれば、終わらずに30秒ごとにロックを取り直して待つ（launchd と systemd が起動と終了を繰り返さないように）。前面の `serve` が止まれば、常駐がそのまま引き継ぐ。
			- 版の更新：サーバーは60秒ごとに `importlib.metadata.version("spec-dock")` を見て、起動のときと違えば終了コード75で終了する。launchd の `KeepAlive` と systemd の `Restart=always` が、新しい版で起動し直す。前面の `serve` は、画面の帯で起動し直しを促す（終了しない）。
			- `status`：設定のファイルがあるか、動いているか、URL、記録した版。`uninstall`：常駐を止めて設定のファイルを消し、何も残さない。
			- systemd のない Linux では、常駐を入れずに `serve` を案内する（同期の loop の代わりは作らない）。
			"""
		satisfies: ["R-28"]
	}
	"D-15": {
		title: "埋め込みの表示と postMessage の約束（`specdock.embed/v1`）"
		text: """
			- `?embed=1`：SpecDock の題名とリポジトリの切り替えを消し、画面の切り替えと検索を残す。画面の中のリンクは `embed=1` を引き継ぐ。GitHub などの外へのリンクは `target=_blank` で開く。
			- 知らせの形：`{source: "specdock", v: 1, type, …}`（親から送るものは `source: "host"`）。始まりは親から：親は枠が読み込まれたら `hello {v}` を送る。SpecDock は、`frame-ancestors` で許した起点（D-09）からの `hello` を受けたら、その起点を覚え、`ready {repository, path, title, capabilities}` を返す。その後、SpecDock から親へ `navigated {path, title, scope}`（画面を移るたび）。親から SpecDock へ `navigate {path}`（枠を作り直さずに移る）、`theme {scheme: "light"|"dark"|"auto"}`。`hello` の前は、SpecDock は何も送らない。
			- 起点の確かめ：SpecDock は、覚えた起点からの知らせだけを受け、`event.source` が親の窓であることも確かめる。送るときは、覚えた起点を `targetOrigin` にし、`*` を使わない。
			- 履歴：画面の移動を履歴に積むのは SpecDock の側（iframe の中の移動は、もとから共通の履歴に入る）。親は `navigated` を受けて自分の URL を `replaceState` で合わせるだけにする。
			- 高さ：親が枠の高さを決め、SpecDock は中でスクロールする。高さの知らせは作らない。
			- 足すのは版を変えずにでき、消すか意味を変えるときは版を上げる。配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-22"]
	}
	"D-16": {
		title: "横断の概況（`/`）"
		text: "表示中の全リポジトリについて、リポジトリごとの札を並べる。札には、一番大きく、マージ待ち、作業中、着手できる Issue の題名を数件ずつ出し、その下に状態ごとの数、止められている数、片付けの候補の数、前回からの変化の数、取得の時刻と古さ、読めないときの印を出す。古い、ない、読めない、異常があるときは、札の上に警告の帯を出し、経過の時間と理由を書く（R-09）。札を押すと、そのリポジトリのホームへ移る。横断の概況を開いても「見た」にしない（D-18）。`?embed=1` で埋め込める。統合ダッシュボードは、JSON から画面を作らずにこれを埋め込める（R-22）。"
		satisfies: ["R-09", "R-22"]
	}
	"D-17": {
		title: "（2026-11-03 に取り下げ）写せるコマンド"
		text: "利用者の決定で、画面からコマンドを写す機能を置かないことにした。詳しい画面には GitHub の Issue と PR へのリンクだけを置く（R-18）。Tailscale の住所でクリップボードが使えない問題は、起きなくなった。番号は、経緯を残すために残す。"
		satisfies: ["R-18"]
	}
	"D-18": {
		title: "「見た」の記録（`specdock.dashboard-seen/v1`）"
		text: """
			- 置き場：`<state_root>/dashboard/seen.json`。リポジトリ（`host/owner/name`）ごとに、`seen_at` と、そのときの各 Scope の状態と PR の状態（`{ID: {state, pr}}`）を持つ。ロックつきで原子的に書く。端末に関わらず共通（R-29）。
			- 口：`POST /api/v1/r/<host>/<owner>/<name>/seen`。そのリポジトリの画面（構造の図、ボード、時間の軸、詳しい画面）を開き、データを読み終えたときに、画面が1回送る。中身は空で、サーバーがそのときのモデルから記録を作る（画面から状態を受け取らない）。横断の概況からは送らない。
			- 守り：`Origin` の見出しが、サーバー自身の起点（D-02 が `Host` で受け付ける名前（`127.0.0.1`、`localhost`、Tailscale の IP、MagicDNS の名前）と待ち受けの番号の組み合わせ）のどれかと完全に一致し、`X-SpecDock-Dashboard: 1` の見出しがあり、`Content-Type` が `application/json` の要求だけを受け、ほかは 403 で断る（ほかの起点からは事前の確かめ（preflight）が要る形にし、CORS の見出しは返さない）。Cookie は使わない。偽の要求でできるのは変化の印を消すことだけで、GitHub、カタログ、リポジトリには触れない。
			- 印が見ている間に消えないための比べる元：記録にはそれぞれ印（`seen_id`）を付け、リポジトリごとに直近の5件を残す。画面は開いたときに最新の `seen_id` を受け取り、それを比べる元（`baseline`）として覚えてから `seen` を送る。自動の更新で読み直すときは `?baseline=<seen_id>` を付け、サーバーはその記録と比べる。同じリポジトリの中で画面を移るとき（図からボード、詳しい画面へ、埋め込みの `navigate` を含む）は、画面は1つのページの中で道筋だけを変え、`baseline` を引き継ぎ、`seen` を送り直さない（`seen` は、そのリポジトリの画面をページとして読み込んだときか、別のリポジトリから移ってきたときに1回だけ送る）。そのため、開いている間は、どの画面でも開いたときの変化の印が残り、新しく起きた変化も足される。比べる元が残っていなければ最新の記録と比べる。印は、次に画面を開いたときに消える（R-29）。
			- 前回の記録がないリポジトリは、変化の印を出さず、最初に開いたときに記録を作る。
			"""
		satisfies: ["R-04", "R-29"]
	}
	"D-19": {
		title: "PR の状態の取得（構造のスナップショットの版2）"
		text: """
			定期の同期が構造を取るときに、同じ周期で PR を取る（`runtime/infra/github_structure.py`）。

			- 取るもの：そのリポジトリの開いている PR（最大100件）と、最近更新された閉じた PR（最大50件）を、GraphQL の1回の問い合わせ（ページを足すときだけ増える）で、`number`、`state`、`isDraft`、`headRefName`、`mergeable`（MERGEABLE、CONFLICTING、UNKNOWN）、`statusCheckRollup.state`（SUCCESS、FAILURE、PENDING、ERROR、なし）、`createdAt`、`mergedAt`、`closedAt`、`url` を取る。
			- 持ち方：構造のスナップショット（C10）の版を2に上げ、`pull_requests: {番号: {...}}` を足す。版1を読む前の版の SpecDock は版2を知らない版として扱い、取り直す（`SnapshotStore._read` はもともと知らない版を「ない」と扱う）。
			- Scope との対応：PR の `headRefName` を、`canonical_structure.branch_names_scope` で Scope に対応づける（`iss-00528`、`chemitaro/iss-00528` など）。同じ Scope に複数の PR があれば、開いているものを先に、新しいものを先に選ぶ。
			- 失敗：PR の問い合わせだけが失敗したときは、構造の取得を続け、`pull_requests` を前回の値のまま残し、`pull_requests_error` に理由と時刻を書く。ダッシュボードは「PR の状態が分からない」を示す（R-30）。
			- 費用：問い合わせはリポジトリごとに1回増える。GitHub の制限（1時間に5000点）の中で、今の構造の取得と同じ間隔に収める。
			"""
		satisfies: ["R-07", "R-30"]
	}
}

compatibility: """
	- 段階1の版（0.6.0）：公開のコマンドが8つ増える（61）。`canonical status` の JSON から `dashboard` の項目が消え、`canonical remove` は5つのファイルを消さない（D-10）。構造のスナップショットが版2になる（D-19。ユーザーごとの状態の置き場の中の、SpecDock だけが読むファイル）。ほかのコマンドの契約は変えない。`migration.md` に「0.6.0 への更新」を書く。
	- 段階2の版（0.7.0）：API と画面を足すだけで、ほかの契約は変えない。
	- 公開の契約にするもの：要約の JSON（`specdock.dashboard-summary/v1`）、「見た」の記録の置き場（`specdock.dashboard-seen/v1`。読むのは SpecDock だけだが形を固める）、在りかの記録（`specdock.dashboard-server/v1`）、画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>` と `?embed=1`、postMessage の約束（`specdock.embed/v1`）、`frame-ancestors` の決まり。画面の中の JSON（`structure`）と、表示の切り替えの問い合わせは契約にしない。
	- 戻すときは、パッケージを前の版に戻し、常駐を入れていれば `dashboard service uninstall` を先に行う。5つのファイルの生成も前の版で戻る。
	"""

risks: [
	"1つのサーバーで Tailscale に待ち受けると、隠していない全リポジトリの仕様が、同じ tailnet のすべての端末から読める。既定では待ち受けず、起動のときに見せる一覧を示し、`hide` で外せる",
	"iPhone の Safari で、起点の違う iframe の中の構造の図を、指でつまむ操作と移動で動かせるかは、資料では確かめきれなかった。最初の Issue で試作し、実機で確かめる（だめなら、埋め込みでは普通のリンクを主にする）",
	"HTML の資料の切り離し（D-09）が、ブラウザーによって効かないおそれ。iPhone の Safari と PC のブラウザーで、資料のスクリプトが API を読めないことを確かめる",
	"同じホストの別の番号のサービスは、すべて同じ site になり、Cookie も SameSite も防壁にならない。第3段階で書き込みを足すときは Cookie を使わず、起点の完全一致と起動ごとの合言葉で守る（http の Tailscale の住所では Fetch Metadata の見出しが付かないので頼れない）。書き込みは orca-web の側で完結させる案が有力（epic-00526）",
	"常駐の Python のプロセスが1つ落ちると全リポジトリの表示が止まる。常駐は自動で起動し直し、リポジトリごとの失敗は閉じ込める",
	"画面のコードが大きくなる（モックで約 2,500 行）。組み立ての道具なしで、モジュールに分けて保つ。画面の振る舞いのテストは、領域のモデル（D-04）の単体のテストと、API の結合のテストを主にし、画面はブラウザーでの確かめで補う",
	"`dashboard serve` は止まるまで終わらない初めてのコマンドで、全部のコマンドを1回ずつ動かすテストが待ち続けるおそれ。テストでは、番号0で起動して止める口を設ける",
	"Mac が眠っている間は、どの構成でも iPhone から開けない。眠らせない設定は OS の側の話で、SpecDock の範囲の外",
]
