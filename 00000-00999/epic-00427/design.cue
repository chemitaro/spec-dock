package spec

// 設計（Epic）。型 specdock/v1。
// コードの場所は 2026-11-03 の main（0.5.1、24f291f9c）で確かめた。

goals: [
	"構造（スナップショット）と内容（カタログ）を合わせて見せる、見るだけのダッシュボードを、標準ライブラリだけの手元のサーバーで配る",
	"状態の判定を、`dependency check` と同じ領域の関数（`evaluate_all`）から作り、画面と要約の JSON と CLI で食い違わないようにする",
	"段階1（構造の画面）を先に出して使い始め、段階2（文書の画面）を後から足す",
	"今の Markdown と PlantUML のダッシュボードを、段階1の版で撤去する",
]

current: """
	- 構造のスナップショット（C10）は `runtime/infra/github_snapshot.py` の `SnapshotStore` が `${XDG_STATE_HOME:-~/.local/state}/spec-dock/github/<host>/<owner>/<name>/snapshot.json` に書く（版1。`runtime/domain/canonical_structure.py` の `StructureSnapshot`。`issues` の各要素は番号、ID、種類、題名、状態、ラベル、担当者、`in_progress`、親、子、`blocked_by`、`blocking`、作成と完了の時刻を持つ。ほかに `external`、`anomalies`、`fetched_at`）。`SnapshotStore.load()` はネットワークに触れず、例外を出さない。
	- 着手の判定は `runtime/domain/canonical_readiness.py` の `evaluate_readiness`／`evaluate_all`（READY、BLOCKED、DOING、DONE、UNKNOWN と、待っているもの `blockers`）。`dependency check` と `work start` が使う。
	- カタログの Scope の場所は `canonical_layout.scope_relative`、Artifact の一覧は `canonical_scope_read.catalog_artifacts`、CUE か Markdown かは `scope_check.scope_format`。
	- 描画は `scope_render.render_scope_html`（CUE だけ。`cue` の実行ファイルが要る）。デザインシステムは配布資産 `spec-dock/design-system/`、図の部品は `src/spec_dock/assets/vendor/`（`infra/diagram_vendor.py` が読むが、まだ誰も呼ばない）。Markdown を HTML にする道は、`presentation/spec_page.wrap_page` の薄いページ（ブラウザーの `ds.js` と marked が描く）だけ。
	- このPCの worktree ごとの選択は `canonical_work.canonical_worktree_rows` で読める。
	- 今のダッシュボードは、定期の同期（`canonical_sync._refresh_dashboards`）が、main のチェックアウトの `spec-dock/` に5つのファイルを書く（`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py`）。`canonical status` の `dashboard` の項目と、`canonical remove` の削除の手順がある。
	- HTTP のサーバーのコードはない。実行時の依存は標準ライブラリだけ（3.10 では `tomli`）。公開のコマンドは53。
	"""

target: """
	- `spec-dock dashboard serve` が、そのリポジトリのダッシュボードを手元で配る。`spec-dock dashboard summary --json` が、同じ要約を CLI から返す。
	- 段階1の版（0.6.0 の予定）で、4つの画面と詳しい画面、要約、在りかの記録が動き、今の5つのファイルの生成が消える。
	- 段階2の版（0.7.0 の予定）で、詳しい画面に、CUE と Markdown の文書、報告と ADR、計画の進み具合が出る。
	"""

design: {
	"D-01": {
		title: "コマンド：`dashboard serve` と `dashboard summary`"
		text: """
			公開のコマンドを2つ足す（53 → 55）。`runtime/cli/catalog.py` の `LEAF_PATHS`、`LEAF_ARGUMENTS`、`HELP_EFFECTS` と、`commands/canonical_dispatch.py` の `CANONICAL_HANDLERS` に足し、コマンドの数を縛るテストと文書（`reference_cli.md` の C54・C55、README、`cli-redesign-guide.html`）を直す。

			- `spec-dock dashboard serve [--port N] [--tailscale] [--project ROOT]`：前面で動き、Ctrl-C か SIGTERM で止まる。起動のときに、開く URL を標準出力に書く（`--json` のときは1行の JSON）。止まるまで終わらない、唯一のコマンドになる。
			- `spec-dock dashboard summary [--json] [--project ROOT]`：R-21 の要約を返す。サーバーが動いていなくても動き、ネットワークに触れない。スナップショットがないときは `DASHBOARD_SNAPSHOT_MISSING`（終了コード3）で、次の1手を示す。
			- 名前は既存の `canonical status` の `dashboard` の項目と重なるが、その項目は D-09 で消える。
			"""
		satisfies: ["R-01", "R-21"]
	}
	"D-02": {
		title: "サーバー：標準ライブラリの HTTP、待ち受け、番号"
		text: """
			`http.server.ThreadingHTTPServer` で作る（新しい依存を足さない）。新しい層の置き場は `runtime/infra/dashboard_server.py`（HTTP）と `runtime/application/dashboard_*.py`（応答の組み立て）。

			- 待ち受け：既定は `127.0.0.1` だけ。`--tailscale` のときは、`tailscale ip -4` の住所にも待ち受ける。住所が得られなければ、起動せずに `DASHBOARD_TAILSCALE_UNAVAILABLE`（終了コード3）で止まる（F-08）。起動のときに、同じ tailnet の端末が仕様を読めることを示す。
			- 番号：既定の番号は、リポジトリ（`host/owner/name`）から決まる、47800〜48799 の中の決まった値にする。リポジトリごとに URL が変わらず、複数のリポジトリを同時に動かせる（R-03）。使われていれば、起動せずに `DASHBOARD_PORT_IN_USE`（終了コード3）で止まり、`--port` を示す（F-07）。
			- 受け付けるのは `GET` と `HEAD` だけ。書き込みの口はない（R-04）。`Host` の見出しが待ち受けの住所（`127.0.0.1:<番号>`、`localhost:<番号>`、Tailscale の住所と名前）でなければ 421 で断る（DNS の付け替えで、ほかのサイトから読まれるのを防ぐ）。
			- 1つのサーバーは、起動のときのチェックアウトの1つのリポジトリだけを扱う（R-03）。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04"]
	}
	"D-03": {
		title: "データの口：版を持つ JSON の API"
		text: """
			画面は、サーバーの JSON の API だけを読む。どれも、スナップショット（`SnapshotStore.load()`）とカタログとこのPCの worktree をその場で読み、GitHub に問い合わせない（R-04、R-07）。

			- `GET /api/v1/summary`：R-21 の要約（D-05）。`dashboard summary --json` の `data` と同じもの。
			- `GET /api/v1/structure`：画面が描くための全体のモデル（D-04 の各 Scope の状態、親子、依存、段、作成と完了の時刻、異常、取得の時刻と古さ）。
			- `GET /api/v1/scopes/<ID>`：詳しい画面の追加の中身（Artifact の一覧、このPCの worktree とブランチ、文書があるか）。段階2で文書の口（D-11）を足す。
			- `GET /api/v1/revision`：スナップショットの `fetched_at` とファイルの時刻、カタログの `state.json` の時刻から作る短い印。画面は5秒ごとにこれを読み、変わったときだけ全体を読み直す（R-08）。
			- 応答の JSON は `schema: "specdock.dashboard/v1"` を持つ。
			"""
		satisfies: ["R-04", "R-07", "R-08"]
	}
	"D-04": {
		title: "状態のモデル：`evaluate_all` からの5つの状態"
		text: """
			新しい領域の部品 `runtime/domain/dashboard_model.py` に、スナップショットから画面のモデルを作る純粋な関数を置く。

			- Issue：`evaluate_all` の DONE、DOING、BLOCKED、READY、UNKNOWN を、終わった、作業中、止められている、着手できる、不明にそのまま写す。判定を別に書かないので、`dependency check` と一致する（R-10）。
			- Epic と Initiative：閉じていれば終わった。自分か子孫に `in_progress` があれば作業中。自分の `evaluate_readiness` が BLOCKED なら止められている。異常があれば不明。それ以外は着手できる。配下の進み具合（終わった数と全体の数）を別に持つ。
			- 終わったものを隠すときに残す印：開いた子孫を持つ閉じた Scope（R-12）。
			- 配下の実行の順番：直下の子を、子孫どうしの依存も子の間の依存に数えて、トポロジカルな段（1、2、…）に分ける。外への依存は別に持つ（R-18）。循環は異常として不明に回す。
			- 片付けの候補：配下がすべて閉じたのに開いている Epic と Initiative、閉じたのに開いた配下がある親（R-20）。
			- 時間の軸：`created_at` と `closed_at` から、週ごとの作成と完了の累計と、最近の動きを作る（R-16）。
			- 取得の時刻と古さ：`fetched_at` から30分を超えたかを決める。異常は `anomalies` をそのまま渡す（R-09）。
			"""
		satisfies: ["R-09", "R-10", "R-12", "R-16", "R-18", "R-20"]
	}
	"D-05": {
		title: "要約の JSON の契約（`specdock.dashboard-summary/v1`）"
		text: """
			D-04 のモデルから作る。項目：`schema`（契約の版）、`repository`、`fetched_at`、`stale`、`counts`（種類ごと・状態ごとの数）、`completion_ratio`、`in_progress`・`ready`・`blocked`・`cleanup` の一覧（各要素は `id`、`number`、`title`、`state`、`reason`）、`anomaly_count`、`paths`（各 Scope の詳しい画面のパス。D-07 の形）、`server`（D-06 の在りかの記録があり、そのサーバーが応えるときだけ、その基点の URL。なければ null）。

			項目を足すのは版を変えずにできる。消すか意味を変えるときは版を上げる。配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-21"]
	}
	"D-06": {
		title: "在りかの記録"
		text: """
			サーバーは起動の後に、ユーザーごとの状態の置き場に `dashboard/<host>/<owner>/<name>.json`（`schema: "specdock.dashboard-endpoint/v1"`、`repository`、`checkout`、`urls`（手元と Tailscale）、`pid`、`started_at`、`version`）を原子的に書き、止まるときに消す。強制的に止められて残った記録は、`pid` が生きていないか、基点の `/api/v1/revision` が応えなければ、読む側が古いと見なす。

			統合ダッシュボードは、この置き場の `*.json` を読んで基点を知り、D-07 のパスと合わせて個別の画面へリンクする（R-22）。置き場の場所と形は、配布する `reference_cli.md` に契約として書く。
			"""
		satisfies: ["R-22"]
	}
	"D-07": {
		title: "画面の作り：パッケージに同梱する静的な画面と URL の契約"
		text: """
			画面は、組み立ての道具を使わない素の HTML、CSS、JavaScript のモジュールで書き、`src/spec_dock/assets/dashboard/` に置いて wheel に同梱する（`assets/**/*` で入る）。配布資産（`static-inventory.json`）には入れない（利用者のリポジトリに写さない）。サーバーが `/`、`/assets/…` で配る。図の部品とデザインシステムも、サーバーが `/vendor/…`（`diagram_vendor`）と `/ds/…` から配り、CDN に頼らない（R-24）。

			- URL の形：`/`（ホーム）、`/board`、`/list`、`/graph`、`/timeline`、`/scopes/<ID>`（詳しい画面）。表示の切り替え（終わったものを含める、種類、範囲、表し方、依存の線、タブ）は問い合わせの文字列に持つ。サーバーは、どの画面のパスにも同じ画面を返し、画面がパスを読んで描く。`/scopes/<ID>` の形は変えない契約にする（R-17）。
			- 明るい表示と暗い表示は `prefers-color-scheme` に従う。幅 390px で横にはみ出さない（R-06）。
			- 状態の札は、色、記号、言葉の3つで示し、凡例を置く（R-11）。
			- 速さ：250件の構造で、ホームは2秒以内、すべての構造の図は3秒以内（R-13、R-15、F-11）。モックの配置の計算（248件で約0.1秒）を基にする。
			"""
		satisfies: ["R-06", "R-11", "R-13", "R-17", "R-24"]
	}
	"D-08": {
		title: "4つの画面と詳しい画面"
		text: """
			モック（`artifacts/20261025t220347z--dashboard-mock.html`）の画面と操作を基にし、データは D-03 の API から読む。

			- 状態のボード（R-13）、一覧と概況（R-14）、検索（R-17）。
			- 構造の図（R-15）：入れ子と木の2つの表し方、範囲の絞り込み、依存の線の3つの切り替え、段の表示、折り返し、拡大・縮小・移動（指の操作を含む）、前後の強調と要点、ダブルクリックでの移動。配置の計算は画面の側で行う。
			- 時間の軸（R-16）：週ごとの累計の図と、最近の動き。
			- 詳しい画面（R-18）：見出し、状態の理由、依存、配下、配下の実行の順番、作業中の場所、Artifact、写せるコマンド。写せるコマンドは、状態に合わせて画面が組み立てる（例：着手できる Issue に `spec-dock work start <ID>`）。
			- 文書の欄（段階1）：文書があるかないかと、HTML の Artifact へのリンクだけ。カタログがなければ、そのことと `spec-dock canonical link` を示す（F-05）。
			- 終わったものの切り替え（R-12）。
			"""
		satisfies: ["R-12", "R-13", "R-14", "R-15", "R-16", "R-17", "R-18"]
	}
	"D-09": {
		title: "HTML の資料を、画面から切り離して配る"
		text: """
			カタログの HTML の資料（Artifact、`explanation.html`）は `/files/<ID>/…` から配る。応答に `Content-Security-Policy: sandbox allow-scripts allow-popups`（`allow-same-origin` なし）を付け、資料を固有でない起点（opaque origin）で動かす。資料のスクリプトは、ダッシュボードの画面の DOM と、API の JSON（同じ起点からしか読めない。CORS の見出しを付けない）に触れられない。画面から開くときも、`sandbox` の属性を付けた `iframe` か新しいタブで開く。

			- 配るのは、その Scope のディレクトリの中の通常のファイルだけ。リンクと `..` を断る（`catalog_artifacts` と同じ守り）。
			- 資料が読む `../../../design-system/` などの相対の道は、サーバーがデザインシステムの場所に写す。
			"""
		satisfies: ["R-05"]
	}
	"D-10": {
		title: "今の Markdown と PlantUML のダッシュボードの撤去"
		text: """
			段階1の版で、次を消す：`application/canonical_dashboard.py`、`domain/canonical_dashboard.py`、`presentation/markdown.py`、`presentation/puml.py`、`canonical_sync._refresh_dashboards` とその呼び出し、`canonical status` の `dashboard` の項目（`canonical_status_sync.dashboard_item` と `CANONICAL_DASHBOARD_*`）、`canonical remove` の `canonical.dashboard.remove` の手順、`CatalogSyncState.dashboard`、`.gitignore` の5つの名前（`asset_layout.py` と配布する `spec-dock/.gitignore`）、文書の記述（`canonical.md`、`reference_cli.md`、`cli-redesign-guide.html`）、それを確かめるテストと fixture。

			- 契約の変更：`canonical status` の JSON から `dashboard` の項目が消える。`canonical remove` は5つのファイルを消さない。`migration.md` に書き、利用者のリポジトリに残った5つのファイルは手で消してよいと示す（`.gitignore` から外れるので、`git status` に出る）。
			- `canonical_state.json` の古い `dashboard` の欄は、読むときに無視する（書かなくなる）。
			"""
		satisfies: ["R-23"]
	}
	"D-11": {
		title: "段階2：文書の描画（CUE、Markdown、報告、ADR、計画の進み具合）"
		text: """
			- CUE の Scope：`GET /scopes/<ID>/doc` が `render_scope_html` を `design_system_base="/ds/"`、`vendor_base="/vendor/"` で呼び、D-09 と同じ切り離しで返す。前もって作ったファイルは使わない（R-19）。`scope check` の結果（`check_scope_documents`）の誤りと警告を、詳しい画面に示す。
			- 描画の失敗（`cue` がない、評価の誤り）：その Scope の文書の欄に、検査の結果と次の1手（`cue` を入れる、`spec-dock scope check <ID>`）を示し、ほかの表示は続ける（F-10）。
			- Markdown の文書：`requirement.md`、`design.md`、`plan.md`、`report.md`、ADR を、`spec_page.wrap_page` の薄いページ（`ds.js` と marked がブラウザーで描く）に包んで返す（R-25）。`wrap_page` と、中の `_script_safe` を公開の関数にする。
			- 計画の進み具合：CUE の Issue の評価（`check_scope_documents` の `evaluation`）の `steps` の `status` を数え、`dropped` を除いた全体の数と、終わった数、作業中の手順を API に足す（R-26）。評価は時間がかかる（`cue` を動かす）ので、Scope ごとに、3つの CUE のファイルの時刻で結果を覚えておく。
			"""
		satisfies: ["R-19", "R-25", "R-26"]
	}
	"D-12": {
		title: "読めないとき、古いとき、ないときの扱い"
		text: """
			- スナップショットがない（F-01）：画面は開き、構造がないことと次の1手（`spec-dock canonical link`、定期の同期の確かめ `spec-dock canonical status`）を示す。`dashboard summary` は `DASHBOARD_SNAPSHOT_MISSING` で失敗する。
			- 30分を超えて古い（F-02）：表示を続け、古いことと取得の時刻を示す。
			- 知らない版（F-03）、読めない（F-04）：`SnapshotStore.load()` は両方を「ない」と返すので、区別のために、ダッシュボードはファイルを自分で読み、`version` を見て知らない版を見分ける（読めないなら「読めない」）。サーバーは、最後に読めたモデルを覚えておき、読めないときはそれで表示を続ける。
			- 構造の異常（F-06）：その Scope を不明として示し、ほかの表示は続ける（D-04）。
			"""
		satisfies: ["R-09"]
	}
}

compatibility: """
	- 段階1の版（0.6.0）：公開のコマンドが2つ増える（55）。`canonical status` の JSON から `dashboard` の項目が消え、`canonical remove` は5つのファイルを消さない（D-10）。ほかのコマンドの契約は変えない。`migration.md` に「0.6.0 への更新」を書く。
	- 段階2の版（0.7.0）：API と画面を足すだけで、ほかの契約は変えない。
	- 要約の JSON（`specdock.dashboard-summary/v1`）、在りかの記録（`specdock.dashboard-endpoint/v1`）、`/scopes/<ID>` の URL は、統合ダッシュボードのための公開の契約にする。
	- 戻すときは、パッケージを前の版に戻す。5つのファイルの生成も前の版で戻る。
	"""

risks: [
	"Tailscale で待ち受けると、同じ tailnet のすべての端末がそのリポジトリの仕様を読める。既定では待ち受けず、起動のときにはっきり示す",
	"HTML の資料の切り離し（D-09）が、ブラウザーによって効かないおそれ。iPhone の Safari と PC のブラウザーで、資料のスクリプトが API を読めないことを確かめる",
	"画面のコードが大きくなる（モックで約 2,500 行）。組み立ての道具なしで、モジュールに分けて保つ。画面の振る舞いのテストは、領域のモデル（D-04）の単体のテストと、API の結合のテストを主にし、画面はブラウザーでの手の確かめで補う",
	"第2段階（Orca の連携）と第3段階（操作）で、サーバーに口が増える。この Epic では、API を `/api/v1/` の下にまとめ、データの組み立て（application）と HTTP（infra）を分けておく。第3段階で書き込みの口を足すときは、`GET` だけの前提（D-02）を改め、偽の要求を防ぐ合言葉と、Tailscale での待ち受けのときの利用者の確かめを、その Epic で設計する",
	"`dashboard serve` は止まるまで終わらない初めてのコマンドで、テストの道具（全部のコマンドを1回ずつ動かすテスト）が待ち続けるおそれ。テストでは、番号0で起動して止める口を設ける",
]
