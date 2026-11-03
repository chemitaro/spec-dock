package spec

// 設計（Issue）。型 specdock/v1。
// コードの場所は 2026-11-04 の main（17f674d67、#528 と #537 のマージの後）で確かめた。

goals: [
	"HTTP の受け口（infra）を薄くし、道筋と応答の組み立て（application）を、ソケットなしで試せる純粋に近い関数にする",
	"判定は #528 のモデルと要約をそのまま呼び、サーバーの側では、読みの切り離し、最後に読めたモデル、「見た」の比べる元だけを足す",
	"画面の骨組みと、5つの画面のモジュールをファイルで分け、#531 と #532 が骨組みに触らずに画面を足せるようにする",
]

current: """
	- モデル：`runtime/domain/dashboard_model.py` の `build_model(snapshot, *, now)`、`seen_scopes`、`compare_seen`、`upstream`、`downstream_ids`、`root_waits`、`child_stages`、`weekly_totals`、`recent_events`。要約：`presentation/dashboard_summary.summary_document(model, *, hidden, server)`、`scope_path`。
	- ファイルの読み：`infra/dashboard_files.py` の `read_snapshot_file`（ok／missing／unreadable／unsupported）、`read_hidden`、`read_server_url`、`pid_alive`、定数 `DASHBOARD_DIRECTORY`、`REPOSITORIES_FILE`、`SERVER_FILE` と2つの schema。書き手はない。
	- 登録簿：`infra/canonical_registry.read_registry(root)` → `SyncRegistry(catalogs=(RegistryEntry(catalog, main_checkout, repository, git, registered_at), …))`。`repository` は `github.com/<owner>/<name>` か null。
	- 原子的な書きとロック：`infra/canonical_state.write_json_atomic(directory, name, payload)`、`directory_lock(directory, timeout)`、`file_lock(path, timeout, error)`、`catalog_state_dir(root, catalog)` と `STATE_FILE`。
	- 配る部品：デザインシステム `src/spec_dock/assets/spec_dock/design-system/`（`ds.css`、`ds.js`、`vendor/marked.umd.js`）、図の部品 `infra/diagram_vendor.read_diagram_vendor_file(path)`。Scope の場所 `domain/canonical_layout.scope_relative(ID)`。
	- コマンド：`cli/catalog.py`（54 の leaf。`dashboard summary` がある）、`commands/canonical_dispatch.py`（`CANONICAL_HANDLERS`、`REPOSITORY_INDEPENDENT_HANDLERS`）、テキストの出力 `presentation/envelope.render_text`。
	"""

target: """
	- `runtime/infra/dashboard_store.py`：在りかの記録、隠す印、「見た」の記録の書き手（ロックつき、原子的）。
	- `runtime/infra/dashboard_network.py`：Tailscale の住所と MagicDNS の名前を手元の `tailscale` のコマンドで得る（差し替えられる）。
	- `runtime/application/dashboard_site.py`：リポジトリの一覧（登録簿と隠す印の読み直し）と、リポジトリごとの読み（最後に読めたモデル、`revision`）。
	- `runtime/application/dashboard_http.py`：道筋、応答の見出し（CSP、CORS、nosniff）、API の JSON、資料、「見た」の口。`Request` → `Response` の関数。
	- `runtime/presentation/dashboard_api.py`：構造、Scope、リポジトリの一覧、知らせの JSON。
	- `runtime/infra/dashboard_server.py`：`ThreadingHTTPServer` の受け口、待ち受け、ロック、在りかの記録、止め方。
	- `runtime/application/dashboard_commands.py`：`serve`、`hide`、`show`、`list` の処理。公開のコマンドは58。
	- `src/spec_dock/assets/dashboard/`：`index.html`、`app.css`、`app.js` と `core/*.js`（骨組み）、`views/index.js`（差し込み口の表）、`views/{graph,board,timeline,scope,overview}.js`（空の枠）。
	"""

design: {
	"D-01": {
		title: "コマンド：`dashboard serve`、`hide`、`show`、`list`"
		text: """
			`cli/catalog.py` の `LEAF_PATHS`、`LEAF_ARGUMENTS`、`HELP_EFFECTS`、`HELP_PRECONDITIONS` と、`canonical_dispatch.py` の2つの表に足す（54 → 58）。コマンドの数を縛るテストと文書（`reference_cli.md`、`docs/README.md`、README、`cli-redesign-guide.html` の配布と dogfood の写し）を直し、`static-inventory.json` の該当行を更新する。

			| コマンド | 引数 | 働き |
			|---|---|---|
			| `dashboard serve` | `--port N`（既定 47800、0 は空いた番号）、`--tailscale` | 前面で動く。起動の出力（標準エラー）に URL と見せるリポジトリの一覧。止まると結果（`urls`、`repositories`、`stopped`）を返す。すでに動いていれば `already_running: true` と URL で終わる |
			| `dashboard hide` | `[REPOSITORY]` | 印を書く。`repository`、`hidden: true`、`changed`、`registered` |
			| `dashboard show` | `[REPOSITORY]` | 印を消す。`hidden: false` |
			| `dashboard list` | なし | `repositories[]`（`repository`（null あり）、`catalog`、`main_checkout`、`hidden`、`served`、`path`、`problem`）と `server` |

			REPOSITORY は `owner/name` か `github.com/owner/name`。省くと、チェックアウトの `origin` から決める（`dashboard summary` と同じ `summarize_named`／`summarize_checkout` の形）。`list` と `serve` はリポジトリによらない（REPOSITORY_INDEPENDENT_HANDLERS で常に処理する）。
			"""
		satisfies: ["R-01", "R-08"]
	}
	"D-02": {
		title: "受け口：待ち受け、`Host` の検査、ロック、在りかの記録、止め方"
		text: """
			`DashboardServer(state_root, *, port, tailscale, network)` が、`127.0.0.1` と（`--tailscale` のとき）Tailscale の IP の2つの `ThreadingHTTPServer` を同じ番号で作り（番号0なら1つ目が得た番号を2つ目に使う）、それぞれをスレッドで動かす。受け口の `BaseHTTPRequestHandler` は、要求を `Request(method, path, query, headers, body)` にして `DashboardHttp.handle` に渡し、`Response(status, headers, body)` を書くだけにする。

			- 起動の順：(1) `<state_root>/dashboard/server.lock` を待たずに取る（取れなければ、`server.json` の URL を読んで `already_running` で終わる）。(2) `--tailscale` なら住所を得る（得られなければ `DASHBOARD_TAILSCALE_UNAVAILABLE`、終了コード3）。(3) 待ち受け（`EADDRINUSE` なら `DASHBOARD_PORT_IN_USE`、終了コード3。`--port` を案内）。(4) `server.json` を原子的に書く。(5) SIGTERM と SIGINT で止まるまで待つ。(6) `server.json` を、自分の `pid` のときだけ消し、ロックを放す。
			- `Host` の検査：受け付ける名前は、`127.0.0.1`、`localhost`、Tailscale の IP、MagicDNS の名前（`tailscale status --json` の `Self.DNSName`。得られなければ足さない）で、番号は待ち受けの番号。違えば 421。
			- テストのために、`DashboardServer.start()`／`stop()` と、実際の番号を返す口を持つ。ネットワークの部品（`TailscaleProbe`）は差し替えられる。
			"""
		satisfies: ["R-01", "R-02", "R-07", "F-04", "F-05", "F-09"]
	}
	"D-03": {
		title: "リポジトリの一覧と、リポジトリごとの読み"
		text: """
			`DashboardSite(state_root, *, now)` が持つ：

			- リポジトリの一覧：登録簿と `repositories.json` を、ファイルの時刻と大きさが変わったときだけ読み直す。登録簿が読めないときは、最後に読めたものを使う。`repository` が分からない行は `problem: "repository_unknown"` で配らない。同じ `repository` が2行あるときは `problem: "ambiguous"` を付け（構造は配り、資料は 409）、カタログは決めない。
			- リポジトリごとの読み `RepositoryReader`：スナップショットのファイルの `stat`（`mtime_ns`、大きさ）が前と同じなら前の解析を使い、違えば `read_snapshot_file` で読む。`ok` なら解析を「最後に読めたもの」として覚える。`unreadable` のときは、最後に読めたものがあればそれを使い、`status: "unreadable"` を付ける。`missing` と `unsupported` は、最後に読めたものを使わない。モデルは要求ごとに `build_model(parsed.snapshot, now=now())` で作る（古さと PR の確かさが時間で変わるため）。
			- 例外の閉じ込め：リポジトリごとの読みとモデルの組み立ての例外は、そのリポジトリの応答（500 と理由）にだけ返す。
			- `revision`：スナップショットの `stat`、カタログの `state.json` の `stat`、読みの状態、古さ（`stale`）、PR の確かさを並べた文字列の sha256 の先頭16桁。「見た」の記録は含めない。
			"""
		satisfies: ["R-01", "R-03", "R-06", "R-11", "F-01", "F-02", "F-03", "F-07", "F-08"]
	}
	"D-04": {
		title: "道筋と応答の見出し"
		text: """
			`DashboardHttp.handle(request) -> Response` が道を分ける。方法は `GET`／`HEAD`（すべて）と `POST`（「見た」の口だけ）。ほかは 405。

			| 道 | 応答 |
			|---|---|
			| `/`、`/r/<h>/<o>/<n>/`、`…/graph`、`…/board`、`…/timeline`、`…/scopes/<ID>` | 骨組みの `index.html`。隠したリポジトリは案内の HTML（404）、知らないリポジトリは 404 |
			| `/assets/<道>` | `assets/dashboard/` のファイル |
			| `/ds/<道>`、`/r/<h>/<o>/design-system/<道>` | デザインシステムのファイル。`Access-Control-Allow-Origin: *` |
			| `/vendor/<道>` | 図の部品。`Access-Control-Allow-Origin: *` |
			| `/r/<h>/<o>/<n>/files/<ID>/<道>` | 資料（D-05） |
			| `/api/v1/repositories` | 表示中のリポジトリ |
			| `/api/v1/r/<h>/<o>/<n>/{summary,structure,scopes/<ID>,revision}` | D-06 |
			| `POST /api/v1/r/<h>/<o>/<n>/seen` | D-07 |

			見出し：すべてに `X-Content-Type-Options: nosniff`、`Cache-Control: no-store`（`/assets/`、`/ds/`、`/vendor/` は `no-cache`）、`Referrer-Policy: no-referrer`。画面の HTML は `Content-Security-Policy: frame-ancestors 'self'`、`?embed=1` なら `frame-ancestors <埋め込みの許可>`。埋め込みの許可は `'self' http://127.0.0.1:* http://localhost:*` と、Tailscale で待ち受けるときの `http://<IP>:*`。`X-Frame-Options` は付けない。API には CORS の見出しを付けない。道の部品は、`%` の解き、空、`.`、`..`、`\\`、NUL を断る。
			"""
		satisfies: ["R-04", "R-05", "R-06", "R-10", "R-13"]
	}
	"D-05": {
		title: "資料の配信と切り離し"
		text: """
			`files/<ID>/<道>`：`<ID>` は `scope_relative` が受ける正確な ID。カタログ（登録簿の `catalog`）から `<区切り>/<ID>/` の各部品を `lstat` でたどり、リンクとディレクトリを断り、終わりが通常のファイルのときだけ返す。種類は拡張子から（知らなければ `application/octet-stream`）。成功も失敗も、この道のすべての応答に `Content-Security-Policy: sandbox allow-scripts allow-popups; frame-ancestors <埋め込みの許可>` と `nosniff` を付ける（#527 の P-3）。隠したリポジトリは案内の 404、同じリポジトリのクローンが2つなら 409。
			"""
		satisfies: ["R-05", "F-06", "F-07"]
	}
	"D-06": {
		title: "API の JSON（`specdock.dashboard/v1`）"
		text: """
			- `repositories`：`{schema, repositories: [{repository, host, owner, name, path, api, problem}], unknown_count, server: {version, started_at, embed_hosts}}`。隠したものを除く。`embed_hosts` は埋め込みの許可の名前（`127.0.0.1`、`localhost`、Tailscale の IP）。
			- `structure?baseline=<seen_id>`：`{schema, repository, revision, snapshot: {status, fetched_at, age_seconds, stale, detail}, notices: [{code, level, text, next_steps}], pull_requests: {status, fetched_at, error}, anomalies, scopes: [{id, number, kind, title, parent_id, children, state, reason{code,text,numbers}, lane, merge, downstream, waits, keep_visible, created_at, closed_at, url, path, pr, change}], cleanup, timeline: {weeks, events}, seen: {latest_id, baseline_id}, changes_count}`。`status` は `ok`、`unreadable`（最後に読めたモデル）、`missing`、`unsupported`。データがないときは `scopes: []`。形は画面のためで、公開の契約にしない（#531、#532 が項目を足してよい）。
			- `scopes/<ID>`：構造の1件と、`upstream`、`downstream`、`root_waits`、`child_stages`。知らない ID は 404。
			- `summary`：`summary_document(model, hidden=False, server=<urls.local>)`。データがないときは CLI と同じコードで 503。
			- `revision`：`{schema, repository, revision}`。
			- 知らせのコード：`SNAPSHOT_STALE`、`SNAPSHOT_MISSING`、`SNAPSHOT_UNREADABLE`、`SNAPSHOT_UNSUPPORTED`、`STRUCTURE_ANOMALIES`、`PULL_REQUESTS_UNKNOWN`、`PULL_REQUESTS_STALE`、`REPOSITORY_AMBIGUOUS`。`text` は日本語の短い文、`next_steps` はコマンドの文字列。
			"""
		satisfies: ["R-03", "R-06", "R-11", "R-12", "F-01", "F-02", "F-03", "F-08"]
	}
	"D-07": {
		title: "「見た」の口と記録"
		text: """
			`POST …/seen` の守り：`Origin` が `http://<受け付ける名前>:<番号>` のどれかと完全に一致し、`X-SpecDock-Dashboard: 1`、`Content-Type` の主な部分が `application/json`。違えば 403（CORS の見出しなし）。中身は読まずに捨てる（最大 64 KiB まで）。データのないリポジトリは 409。

			記録：`dashboard_store.append_seen(state_root, repository, scopes)` が `directory_lock(<state_root>/dashboard)` の中で `seen.json` を読み直し、`{seen_id: secrets.token_hex(8), seen_at, scopes: {ID: {state, pr}}}` を足し、直近の5件にして原子的に書く。形は `{schema: "specdock.dashboard-seen/v1", repositories: {<key>: {records: [...]}}}`（古い順）。読めない `seen.json` は、記録がないものとして扱い、次の書きで作り直す（「見た」の記録は失っても印が出ないだけのため）。

			比べ方：構造の API は `baseline` の記録（なければ最新）の `scopes` を `SeenScope` に戻し、`compare_seen` に渡す。
			"""
		satisfies: ["R-09", "F-09"]
	}
	"D-08": {
		title: "隠す印と在りかの記録の書き手"
		text: """
			- `hide_repository`／`show_repository(state_root, repository, *, now)`：`directory_lock(<state_root>/dashboard)` の中で `repositories.json` を読み直し、鍵を足すか消し、変わったときだけ原子的に書く。読めない `repositories.json` は上書きせずに `DASHBOARD_STATE_UNREADABLE`（終了コード3）で止まる（隠す印を黙って失わないため）。
			- `write_server_record`／`remove_server_record(state_root, pid)`：`server.json` を原子的に書き、消すときは中の `pid` が自分のときだけ消す。
			- 読みは #528 の `dashboard_files`（`read_hidden`、`read_server_url`）をそのまま使い、書き手と同じ定数を使う。
			"""
		satisfies: ["R-07", "R-08"]
	}
	"D-09": {
		title: "画面の骨組みと差し込み口"
		text: """
			`assets/dashboard/` の作り：

			- `index.html`：上の帯、知らせの帯、画面の領域（`<main id="view">`）だけの骨組み。`/assets/app.css` と `/assets/app.js`（module）を読む。
			- `app.js`：起動、道の解釈（`core/route.js`）、API の読み（`core/api.js`。`fetch` は同じ起点だけ）、上の帯（`core/topbar.js`）、自動の更新（5秒ごとの `revision`）、「見た」の送信（ページの読み込みのとき1回）、埋め込みの受け渡し（`core/embed.js`）。
			- `views/index.js`：差し込み口の表 `VIEWS = {graph, board, timeline, scope, overview}`。各画面は `export default {id, title, icon, styles?: [CSS の道], render(root, ctx), dispose?()}`。`ctx` は `{repository, route, data（構造の JSON）, scope（詳しい画面の JSON）, embed, navigate(path), href(path)}`。骨組みは、データが変わるたびに `render` を呼び直す。#531 と #532 は `views/<名前>.js`（と CSS）を書き換えるだけで画面を足す。
			- 画面の内の移動は `pushState`。`a[data-nav]` と同じリポジトリの道の `<a>` を骨組みが受けて、1つのページの中で移る。外へのリンクは `target=_blank`。
			- 見た目：d2 のトークン（`--ds-*`）を `app.css` に写し、`prefers-color-scheme` と `data-theme` で暗い表示にする。高さは `100dvh`。幅 640px 以下で、上の帯の画面の切り替えを下の段に移す。
			- 上の帯：（埋め込みでないとき）SpecDock の印とリポジトリの切り替え、画面の切り替え（構造の図、ボード、時間の軸）、検索の枠（中身は #531）、変化の数、取得の時刻（何分前、古いときは警告の色）。帯の下に `notices` の知らせを並べる。
			"""
		satisfies: ["R-03", "R-06", "R-09", "R-10", "R-11", "R-13"]
	}
	"D-10": {
		title: "埋め込みの受け渡し（`core/embed.js`）"
		text: """
			`?embed=1` のとき：`document.documentElement.dataset.embed = "1"` で題名とリポジトリの切り替えを隠し、骨組みの作るリンクに `embed=1` を付ける。`message` を受け、`event.source === window.parent` で、`data.source === "host"`、`data.v === 1` のものだけを見る。`hello` は、起点が `^http://(127\\.0\\.0\\.1|localhost|<サーバーの返す Tailscale の IP>):\\d+$` に合うときに受け、起点を覚えて `ready` と `navigated` を返す（何度来ても、そのたびに返す。受け入れる起点は最初のものに固定する）。`navigate {path}` は同じリポジトリなら1つのページの中で、違うリポジトリなら読み込み直しで移る。`theme {scheme}` は `data-theme` を変える。送るときは覚えた起点を `targetOrigin` にし、`hello` の前は送らない。Tailscale の IP は `/api/v1/repositories` の `server.embed_hosts` で受け取る（読み終える前の `hello` は、読み終えてから判定する）。
			"""
		satisfies: ["R-10"]
	}
}

compatibility: """
	- 公開のコマンドが4つ増える（54 → 58）：`dashboard serve`、`dashboard hide`、`dashboard show`、`dashboard list`。ほかのコマンドの契約は変えない。
	- 状態の置き場に、`dashboard/server.json`（`specdock.dashboard-server/v1`）、`dashboard/repositories.json`（`specdock.dashboard-repositories/v1`）、`dashboard/seen.json`（`specdock.dashboard-seen/v1`）、`dashboard/server.lock` を作る。リポジトリ、カタログ、登録簿には書かない。
	- 公開の契約にするもの：画面の道 `/r/<host>/<owner>/<name>/scopes/<ID>` と `?embed=1`、postMessage の約束 `specdock.embed/v1`、`frame-ancestors` の決まり、在りかの記録、要約の API。構造の API の形と表示の切り替えの問い合わせは契約にしない。配布する `reference_cli.md` に書く。
	- 0.6.0 の移行の注記（#534）に要るもの：上の4つのコマンドと4つのファイル、既定の番号 47800、`--tailscale` の待ち受け。
	"""

risks: [
	"`--tailscale` で待ち受けると、隠していない全リポジトリの仕様と資料が、同じ tailnet の端末から読める。既定では待ち受けず、起動のときに見せる一覧を示し、`hide` で外せる",
	"`dashboard serve` は止まるまで終わらない。全部のコマンドを1回ずつ動かすテストは `help` だけを動かす。サーバーのテストは番号0で起動し、`stop()` か SIGTERM で止める",
	"画面の振る舞い（埋め込み、自動の更新、「見た」の送信）は Python のテストでは見えない。API の結合のテストを主にし、PC のブラウザー（ヘッドレスの Chrome）での確かめを report.md に残す。iPhone の Safari は #534 で利用者に頼む",
	"`/r/<h>/<o>/design-system/` の写しは、`design-system` という名前のリポジトリの道と重なる。`/ds/` にファイルがあるときだけ写す",
]
