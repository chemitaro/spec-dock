package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00427。plan.cue の slice `iss-00529`（covers: R-01〜R-05、R-08、R-09、R-21、R-22、R-27、R-29、F-01、F-02、F-04、F-07〜F-09、F-12）を、この Issue の番号に書き直した。
// Epic の番号は「Epic R-01」のように書く。この Issue の番号は R-01 などである。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
assurance: {
	level:  "standard"
	reason: "手元と Tailscale に待ち受けるサーバーを作り、全リポジトリの仕様と資料を配る。見せる範囲、資料のスクリプトの切り離し、枠の決まりを誤ると、仕様が意図しない相手に見える。版を戻せば回復できる。"
}

purpose: "利用者ごとに1つのダッシュボードのサーバー（`spec-dock dashboard serve`）を作り、登録簿の、隠していない全リポジトリの画面と API と資料を、見るだけで配る。あわせて、表示を止めて戻すコマンド（`dashboard hide`／`show`／`list`）、在りかの記録、「見た」の記録、埋め込みの約束、画面の骨組み（上の帯、画面の差し込み口、自動の更新）を作る。中の画面（構造の図、ボード、時間の軸、詳しい画面、横断の概況）は、#531 と #532 が差し込み口に足す。"

background: """
	- 親の Epic（epic-00427）の設計 D-02（サーバー）、D-03（道筋と API）、D-06（在りかの記録）、D-09（資料の切り離しと枠の決まり）、D-12 のサーバーの側、D-13（`hide`／`show`／`list`）、D-15（埋め込みの約束）、D-18（「見た」の記録）を、この Issue が作る。D-01 のうち `serve`、`hide`、`show`、`list` もこの Issue。`dashboard service` は #530、今のダッシュボードの撤去は #533。
	- 状態のモデル、要約、スナップショットの読みは #528 でマージ済み（`runtime/domain/dashboard_model.py`、`dashboard_snapshot.py`、`application/dashboard_summary.py`、`infra/dashboard_files.py`、`presentation/dashboard_summary.py`）。PR の状態は #537 の `pull_requests_by_scope` を経てモデルが持つ。この Issue は判定を別に書かず、これを使う。
	- #527 の試作（`iss-00527/report.md` の提案 P-1〜P-6、`iss-00527/artifacts/20261103t151442z--embed-lab.py`）で、PC の Chrome では D-09 と D-15 のとおりに動くことを確かめた。P-1（親は `load` のたびに `hello`、SpecDock は `ready` の後に `navigated` を1回）は Epic の D-15 に入った。P-3（資料の道も同じ `frame-ancestors`）と P-4（CORS は `/ds/` と `/vendor/` だけ、API には付けない）を、この Issue のテストで確かめる。P-5、P-6 は #532。
	- 見た目は、利用者が採った試作 d2（`epic-00427/artifacts/20261103t150110z--dashboard-design-d2.html`。`ds.css` の「D：ビジネス」のトークン）に従う。
	"""

includes: [
	"`spec-dock dashboard serve [--port N] [--tailscale]`（前面。Ctrl-C か SIGTERM で止まる）と、HTTP のサーバー、道筋、API、資料の配信",
	"`spec-dock dashboard hide [REPOSITORY]`、`show [REPOSITORY]`、`list`（公開のコマンドが 54 → 58）と、コマンドの数を縛るテストと文書",
	"状態の置き場の3つのファイルの書き手：在りかの記録 `dashboard/server.json`、隠す印 `dashboard/repositories.json`、「見た」の記録 `dashboard/seen.json`。二重起動を防ぐロック `dashboard/server.lock`",
	"画面の骨組み（上の帯、リポジトリの切り替え、画面の切り替えの枠、取得の時刻、変化の数、古さ・読めない表示、`?embed=1`、postMessage、5秒ごとの自動の更新、「見た」の送信）と、5つの画面の差し込み口（空の枠）",
	"画面の静的な資源を `src/spec_dock/assets/dashboard/` に置き、wheel に入れる（配布資産の `static-inventory.json` には入れない）",
]
excludes: [
	"構造の図、ボード、時間の軸、詳しい画面、横断の概況の中身（#531、#532）。検索（Epic R-17）の中身も #531",
	"`dashboard service`（常駐）と、版の更新の後の起動し直し（#530、Epic D-14）",
	"今の Markdown と PlantUML のダッシュボードの撤去（#533）",
	"文書の描画（段階2、#535）。資料の HTML が CDN から図の部品を読もうとすることを止めること（Epic R-24 の画面の側は #531）",
	"版の番号と `migration.md`（#534）",
	"GitHub への要求。サーバーとこの Issue のコマンドは、GitHub にもほかのネットワークにも要求を送らない（Tailscale の住所は手元の `tailscale` のコマンドで得る）",
]

requirements: {
	"R-01": {
		title: "1つのサーバーが、登録簿の隠していない全リポジトリを配る"
		text: """
			`spec-dock dashboard serve` は前面で動き、Ctrl-C か SIGTERM で止まる。登録簿（`<state_root>/canonical-registry.json`）の、`repository` が分かり、隠していない全リポジトリを、`/r/<host>/<owner>/<name>/` の道で配る。登録簿と隠す印のファイルが変わったら、起動し直さずに読み直す。すでにサーバーが動いていれば、その URL を示して終わる（終了コード0）。（Epic R-01、D-01、D-02）
			"""
		acceptance: [
			"見本の登録簿の2つのリポジトリについて、`dashboard serve` の後に各リポジトリの画面の道と API が応える",
			"動いている間に登録簿へ3つ目のリポジトリを足すと、起動し直さずに `/api/v1/repositories` に現れる",
			"2つ目の `dashboard serve` は、動いているサーバーの URL を示して終了コード0で終わる",
		]
	}
	"R-02": {
		title: "既定では 127.0.0.1 だけに待ち受け、`--tailscale` で Tailscale の IPv4 にも待ち受ける"
		text: """
			既定の番号は 47800（`--port` で変える。0 は空いた番号）。既定では `127.0.0.1` だけに待ち受ける。`--tailscale` のときは、手元の `tailscale ip -4` で得た住所にも待ち受ける。`0.0.0.0` には待ち受けない。Tailscale の設定を変えない。起動のときに、URL と、見せるリポジトリの一覧を示す。`Host` の見出しが、待ち受けの名前（`127.0.0.1`、`localhost`、Tailscale の IP、このPCの MagicDNS の名前）と番号の組でなければ 421 で断る。（Epic R-02、D-02）
			"""
		acceptance: [
			"指定しないときは 127.0.0.1 にだけ待ち受け、起動の出力に URL と見せるリポジトリの一覧が出る",
			"`--tailscale` で、見本の `tailscale` が返す住所にも待ち受け、在りかの記録の `urls.tailscale` にその URL が入る",
			"待ち受けの名前でない `Host` の要求が 421 で断られる",
		]
	}
	"R-03": {
		title: "1つの画面は1つのリポジトリを扱い、上の帯で切り替えられ、1つの失敗がほかを止めない"
		text: "リポジトリの画面と API は、そのリポジトリのモデルだけを返す。上の帯のリポジトリの切り替えで、表示中のほかのリポジトリへ移れる。1つのリポジトリの読み取りの失敗（スナップショットがない、読めない、知らない版、`repository` が分からない登録の行、同じリポジトリのクローンが2つある）は、そのリポジトリの画面と API にだけ理由と次の1手を返し、ほかのリポジトリの表示を止めない。（Epic R-03、F-12、D-02）"
		acceptance: [
			"2つのリポジトリの構造の API が、それぞれのリポジトリの Scope だけを返す",
			"1つのリポジトリのスナップショットを壊しても、ほかのリポジトリの API と画面が応える",
			"PC のブラウザーで、上の帯のリポジトリの切り替えから、ほかのリポジトリの画面へ移れる",
		]
	}
	"R-04": {
		title: "サーバーは見るだけで、書くのは「見た」の記録だけ"
		text: "受け付けるのは `GET` と `HEAD` と、「見た」の口の `POST` だけ（ほかは 405）。サーバーは GitHub にもほかのネットワークにも要求を送らず、カタログ、リポジトリ、登録簿を書かない。状態の置き場に書くのは、在りかの記録（起動と停止）と「見た」の記録だけ。（Epic R-04）"
		acceptance: [
			"`PUT`、`DELETE`、`PATCH`、「見た」の口でない `POST` が 405 で断られる",
			"画面と API と資料をひととおり読んでも、カタログと登録簿のファイルが変わらず、GitHub への要求がない",
		]
	}
	"R-05": {
		title: "HTML の資料を配り、資料のスクリプトを画面とデータから切り離す"
		text: """
			カタログの Scope のディレクトリの中の通常のファイルを `/r/<host>/<owner>/<name>/files/<ID>/<道>` から配る。リンク、`..`、ディレクトリ、Scope のディレクトリの外は断る。この道のすべての応答に、形式によらず `Content-Security-Policy: sandbox allow-scripts allow-popups; frame-ancestors <埋め込みの許可>`（`allow-same-origin` なし）と `X-Content-Type-Options: nosniff` を付ける。資料が相対の道で読むデザインシステム（`../../../design-system/…`）は、サーバーが `/ds/` の中身を返す。API には CORS の見出しを付けず、`/ds/` と `/vendor/` の静的なファイルにだけ `Access-Control-Allow-Origin: *` を付ける。（Epic R-05、F-09、D-09、#527 の P-3、P-4）
			"""
		acceptance: [
			"資料の応答のすべて（HTML、SVG、ほかの形式、404 を除く）に、sandbox と `allow-same-origin` のない CSP、埋め込みと同じ `frame-ancestors`、`nosniff` が付く",
			"`/ds/` と `/vendor/` には `Access-Control-Allow-Origin: *` が付き、API と画面には付かない",
			"リンク、`..`、Scope のディレクトリの外の資料は配られない",
			"PC のブラウザーで、サーバーから開いた資料のスクリプトが、画面の DOM と API の JSON を読めない",
		]
	}
	"R-06": {
		title: "画面は API だけを読み、5秒ごとの印の確かめで、開いたまま新しくなる"
		text: """
			画面の道（`/`、`/r/<host>/<owner>/<name>/`、`…/graph`、`…/board`、`…/timeline`、`…/scopes/<ID>`）は、同じ骨組みの HTML を返す。画面は `GET /api/v1/repositories` と、リポジトリごとの `GET /api/v1/r/<host>/<owner>/<name>/{summary|structure|scopes/<ID>|revision}` だけを読む。`revision` は、スナップショットのファイルの時刻と大きさ、カタログの `state.json` の時刻と大きさ、古さと PR の確かさから作る短い印で、「見た」の記録の時刻を含めない。画面は5秒ごとに `revision` を読み、変わったときだけ全体を読み直して、再読み込みなしで描き直す。応答の JSON は `schema: "specdock.dashboard/v1"` を持つ。（Epic R-07、R-08、D-03）
			"""
		acceptance: [
			"スナップショットを書き換えると `revision` が変わり、「見た」を記録しても変わらない",
			"PC のブラウザーで画面を開いたままスナップショットを書き換えると、10秒以内に、再読み込みなしで取得の時刻が新しくなる",
		]
	}
	"R-07": {
		title: "サーバーの在りかを、状態の置き場の記録で知らせる"
		text: "サーバーは待ち受けを始めた後に `<state_root>/dashboard/server.json`（`schema: \"specdock.dashboard-server/v1\"`、`urls.local`、`urls.tailscale`（なければ null）、`pid`、`version`、`started_at`）を原子的に書き、止まるときに消す（自分の `pid` の記録だけ）。二重起動は `<state_root>/dashboard/server.lock` の排他のロックで防ぐ。`dashboard summary` の `server` は、この記録を読む。（Epic R-22、D-06）"
		acceptance: [
			"起動の後に記録が書かれ、その `urls.local` から `/api/v1/repositories` が応え、SIGTERM で止めると記録が消える",
			"サーバーが動いている間の `dashboard summary` の `server` に `urls.local` が出る",
		]
	}
	"R-08": {
		title: "リポジトリの表示を、`hide` で止め、`show` で戻し、`list` で示す"
		text: """
			`spec-dock dashboard hide [REPOSITORY]` は印を `<state_root>/dashboard/repositories.json`（`schema: \"specdock.dashboard-repositories/v1\"`、`repositories: {<host/owner/name>: {hidden_at}}`）にロックつきで原子的に書き、`show` は消す。チェックアウトの中では REPOSITORY を省ける。隠したリポジトリは、`/api/v1/repositories`、横断の概況、起動のときの一覧に出ず、その道と API と資料には、データを含まない案内（`spec-dock dashboard show <リポジトリ>`）を 404 で返す。隠しても同期は止まらない（登録簿と `CatalogSyncState` を変えない）。`spec-dock dashboard list` は、登録簿の各行の、リポジトリ、表示中か隠しているか、配れるか、サーバーの URL を示す。（Epic R-27、D-13）
			"""
		acceptance: [
			"`dashboard hide` の後、動いているサーバーの一覧からそのリポジトリが消え、その道が戻すコマンドの案内だけを 404 で返し、登録簿が変わらない。`dashboard show` で戻る",
			"`dashboard list` が、各行の表示中か隠しているかと、`repository` が分からない行を示す",
		]
	}
	"R-09": {
		title: "「見た」の記録を、画面自身からの要求だけで書き、変化の印の比べる元を保つ"
		text: """
			`POST /api/v1/r/<host>/<owner>/<name>/seen` は、中身を受け取らず、そのときのモデルから記録（`seen_id`、`seen_at`、各 Scope の `{state, pr}`）を作り、`<state_root>/dashboard/seen.json`（`schema: \"specdock.dashboard-seen/v1\"`）に、リポジトリごとに直近の5件をロックつきで原子的に残す。`Origin` がサーバー自身の起点（R-02 の名前と待ち受けの番号の組）と完全に一致し、`X-SpecDock-Dashboard: 1` があり、`Content-Type` が `application/json` の要求だけを受け、ほかは 403。CORS の見出しは返さない。

			構造の API は、`?baseline=<seen_id>` の記録と比べた変化（#528 の `compare_seen`）と、最新の `seen_id` を返す。`baseline` がないか残っていなければ、最新の記録と比べる。記録がなければ変化はない。画面は、ページとして開いたときに最新の `seen_id` を比べる元に覚えてから、1回だけ `seen` を送る。同じリポジトリの中で画面を移るとき（埋め込みの `navigate` を含む）は、1つのページの中で道だけを変え、比べる元を引き継ぎ、`seen` を送り直さない。横断の概況からは送らない。（Epic R-04、R-29、D-18）
			"""
		acceptance: [
			"見本で、前回見た後に状態が変わった Scope、新しい Scope、PR が変わった Scope に変化の印が付き、`seen` を送った後に同じ `baseline` で読むと印が残り、`baseline` なしで読むと消える",
			"ほかの起点、`X-SpecDock-Dashboard` のない要求、`application/json` でない要求が 403 で断られ、記録が増えない",
			"6回記録すると、そのリポジトリの記録が直近の5件だけになる",
		]
	}
	"R-10": {
		title: "ほかのダッシュボードが、`?embed=1` の画面を iframe に入れ、postMessage でつながる"
		text: """
			どの画面の URL も `?embed=1` を付けると、SpecDock の題名とリポジトリの切り替えを消した表示になり、画面の切り替えは残る。画面の中のリンクは `embed=1` を引き継ぎ、外へのリンクは `target=_blank` で開く。通常の画面は `frame-ancestors 'self'`、`?embed=1` の画面と資料は `frame-ancestors 'self' http://127.0.0.1:* http://localhost:*`（Tailscale で待ち受けるときは `http://<Tailscale の IP>:*` も）にし、`X-Frame-Options` は付けない。

			知らせの約束 `specdock.embed/v1`：形は `{source: \"specdock\"|\"host\", v: 1, type, …}`。親は枠の `load` のたびに `hello` を送る。SpecDock は、`event.source` が親の窓で、起点が埋め込みの許可に合う `hello` を受けたら、その起点を覚え、`ready {repository, path, title, capabilities}` を返し、続けて今の画面の `navigated {path, title, scope}` を1回送る。その後は画面を移るたびに `navigated`。親からの `navigate {path}`（枠を作り直さずに同じページの中で移る）と `theme {scheme}` を受ける。覚えた起点でない知らせは捨て、送るときは覚えた起点を `targetOrigin` にし `*` を使わない。`hello` の前は何も送らない。高さの知らせは作らない。（Epic R-22、D-09、D-15、#527 の P-1）
			"""
		acceptance: [
			"`?embed=1` の画面と資料の応答に埋め込みの許可の `frame-ancestors` が、通常の画面に `frame-ancestors 'self'` が付き、`X-Frame-Options` がない",
			"PC のブラウザーで、在りかの記録の基点と `/r/<host>/<owner>/<name>/scopes/<ID>?embed=1` を、別の番号の起点の試しの親の iframe に入れると、題名とリポジトリの切り替えのない画面が出て、`hello` に `ready` と `navigated` が返り、親の `navigate` で画面が移る",
			"PC のブラウザーで、許していない起点と、親でない窓からの `hello` を無視する",
		]
	}
	"R-11": {
		title: "上の帯に、取得の時刻、古さ、読めないこと、構造の異常と次の1手を示し、読めないときは最後に読めたモデルで続ける"
		text: """
			上の帯に、構造を取得した時刻（何分前か）、前回からの変化の数を、いつも示す。スナップショットが30分を超えて古い、ない、読めない、知らない版、構造の異常がある、PR の状態が分からない、のときは、帯の下に、理由と次の1手（`spec-dock canonical status`、`spec-dock canonical link` など）を書いた知らせを出す。サーバーは、リポジトリごとに最後に読めたモデルを覚え、読めない（壊れている、書き込みの途中）ときは、そのモデルで表示を続け、読めないことを示す。ないときと知らない版のときも画面は開き、構造がないことを示す。（Epic R-09、F-01、F-02、F-03、F-04、D-12）
			"""
		acceptance: [
			"見本で、30分を超えて古いスナップショット、ないとき、壊れたとき、知らない版、異常があるときに、構造の API がそれぞれの知らせ（理由と次の1手）を返す",
			"一度読めたスナップショットを壊すと、構造の API が前のモデルの Scope を返し、読めないことの知らせを付ける",
			"PC のブラウザーで、上の帯に取得の時刻と変化の数が出て、古いときに知らせの帯が出る",
		]
	}
	"R-12": {
		title: "要約の JSON を、サーバーからも CLI と同じ内容で返す"
		text: "`GET /api/v1/r/<host>/<owner>/<name>/summary` は、#528 の `summary_document` で作った `specdock.dashboard-summary/v1` を返す。`hidden` は false、`server` は在りかの記録の `urls.local`。スナップショットがない、読めない、知らない版のときは、CLI と同じコードの誤り（503）を返す。（Epic R-21）"
		acceptance: ["同じスナップショットで、サーバーの要約と `dashboard summary` の要約が、`server` を含めて一致する"]
	}
	"R-13": {
		title: "画面の骨組みと、画面のモジュールの差し込み口を分ける"
		text: """
			画面は、組み立ての道具を使わない素の HTML、CSS、JavaScript のモジュールで、`src/spec_dock/assets/dashboard/` に置き、wheel に入れる。骨組み（上の帯、道の解釈、API の読み、自動の更新、「見た」の送信、埋め込みの受け渡し）と、5つの画面（`graph`、`board`、`timeline`、`scope`、`overview`）のモジュールを、ファイルで分ける。#531 と #532 は、骨組みのファイルを変えずに、画面のファイル（`views/<名前>.js` と任意の CSS）を書き換えるだけで画面を足せる。この Issue の画面のファイルは、決まった形の空の枠にする。見た目は試作 d2 のトークンと上の帯に従い、明るい表示と暗い表示に従い、幅 390px で横にはみ出さない。（Epic D-07）
			"""
		acceptance: [
			"wheel に `spec_dock/assets/dashboard/` の骨組みと5つの画面のファイルが入り、サーバーがそれを `/assets/` から配る",
			"画面のモジュールの形（`export default {id, title, render(root, ctx), dispose?}`）が文書に書かれ、5つの空の枠がその形を持つ",
			"PC のブラウザーで、各画面の道を開くと、上の帯と空の枠が出て、幅 390px で横にはみ出さない",
		]
	}
}

failures: {
	"F-01": {
		title: "スナップショットがない"
		text:  "画面は開き、構造がないことと、次の1手（`spec-dock canonical link`、`spec-dock canonical status`）を示す。要約の API は `DASHBOARD_SNAPSHOT_MISSING`（503）を返す。（Epic F-01）"
	}
	"F-02": {
		title: "スナップショットが30分を超えて古い"
		text:  "古い内容で表示を続け、古いことと取得の時刻を示す。（Epic F-02）"
	}
	"F-03": {
		title: "スナップショットが読めない（壊れている、書き込みの途中）"
		text:  "最後に読めたモデルで表示を続け、読めないことを示す。一度も読めていなければ、構造がないことと次の1手を示す。（Epic F-04）"
	}
	"F-04": {
		title: "待ち受けの番号が使われている"
		text:  "起動せずに `DASHBOARD_PORT_IN_USE`（終了コード3）で止まり、`--port` で別の番号を指定する方法を示す。在りかの記録を書かない。（Epic F-07）"
	}
	"F-05": {
		title: "Tailscale の住所が得られない"
		text:  "`--tailscale` のときは、起動せずに `DASHBOARD_TAILSCALE_UNAVAILABLE`（終了コード3）で理由を示す。指定しないときは `tailscale` を動かさない。（Epic F-08）"
	}
	"F-06": {
		title: "HTML の資料の中のスクリプトが、画面とデータに触ろうとする"
		text:  "資料は固有でない起点（sandbox）で動くので、画面の DOM、どのリポジトリの API の JSON、「見た」の口にも触れられない。（Epic F-09）"
		impact: "資料のスクリプトが、ダッシュボードの表示を偽ったり、データを読み取ったりする"
	}
	"F-07": {
		title: "1つのリポジトリが読めない（登録の行のリポジトリが分からない、同じリポジトリのクローンが2つある）"
		text:  "`repository` が分からない行は、`dashboard list` に「リポジトリが分からない」と出し、配らない。同じリポジトリのクローンが2つあるときは、構造（リポジトリごとのスナップショット）は配り、カタログの資料は選べないので、資料の道は `DASHBOARD_REPOSITORY_AMBIGUOUS`（409）で、どちらかの登録を外す次の1手を返し、帯にも示す。ほかのリポジトリは続ける。登録簿が読めないときは、最後に読めた登録簿で続ける。（Epic F-12）"
	}
	"F-08": {
		title: "スナップショットが知らない版"
		text:  "読まずに、版が違うことと、SpecDock の更新を示す。最後に読めたモデルは使わない。（Epic F-03、D-12）"
	}
	"F-09": {
		title: "待ち受けの名前でない `Host`、ほかの起点からの「見た」"
		text:  "`Host` が違えば 421、「見た」の口の守り（R-09）に合わなければ 403 で断り、何も書かない。（Epic D-02、D-18）"
	}
}

constraints: [
	"新しい実行時の依存を足さない（`http.server.ThreadingHTTPServer` と標準ライブラリ）",
	"テストは一時のディレクトリの状態の置き場（`XDG_STATE_HOME`）で閉じ、番号0で起動して止める。利用者の `~/.local/state/spec-dock/` を使わない",
	"判定（状態、変化、要約）は #528 のモデルを使い、別に書かない",
	"`static-inventory.json` は、この Issue で変えた配布文書の行の sha256 と known_old_sha256 だけを変える（統括の決定）。版の番号と `migration.md` は変えない",
]

decisions: [
	"2026-11-04（作業者の判断）：同じリポジトリのクローンが2つ登録されているときも、構造はリポジトリごとのスナップショットなので配り、カタログを選べない資料の道だけを 409 で断る（F-07）",
	"2026-11-04（作業者の判断）：リポジトリを切り替えるときは、ページとして読み込み直す（別のリポジトリへ移ったときの「見た」は、読み込みのときの1回になる）。同じリポジトリの中の移動だけを1つのページの中で行う",
	"2026-11-04（作業者の判断）：横断の概況（`/`）は #531 の画面で、この Issue では差し込み口に、表示中のリポジトリへのリンクだけの仮の中身を置く（hide/show をブラウザーで確かめるため）",
	"2026-11-04（作業者の判断）：資料の `../../../design-system/` の写しは、`/r/<host>/<owner>/design-system/<道>` が `/ds/` のファイルに当たるときだけ返す（`design-system` という名前のリポジトリの道とぶつかるときは、ファイルがあれば `/ds/` を優先する）",
]
