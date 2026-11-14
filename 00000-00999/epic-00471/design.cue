package spec

// 設計（Epic）。型 specdock/v1。

goals: [
	"SpecDock のサーバーは見るだけのまま、画面が orca-web を直接読む",
	"orca-web の場所は1か所（サーバーの設定の読み）で決め、CSP と画面の両方が同じ値を使う",
	"Scope と worktree の対応は、DOM を触らない純粋な関数にし、node のテストで確かめる",
	"要約の読みは画面全体で1つにし、構造の図、ボード、横の欄、後のエージェントのタブ（epic-00526）が同じ結果を使う",
	"印とボタンは orca-web の部品をそのまま使い、SpecDock の描き直しで作り直さない",
]

current: """
	- 構造の API（`presentation/dashboard_api.py` の `scope_item`）の Scope の項目は `branch`（この PC の最初の worktree のブランチ）だけを持つ。`application/dashboard_scope_details.py` の `read_structure_facts` が `git worktree list` を1回読み、`branch_names_scope` で Scope を名指すブランチを探す。
	- Scope の JSON の `details.worktrees` は `{status, items[{path, branch}]}`。
	- 画面の CSP は `application/dashboard_http.py` の `_SHELL_CSP` の固定の文字列で、`_html` が `frame-ancestors` を足す。
	- 利用者の設定は `infra/user_config.py` の `read_user_dashboard` が `dashboard` の節を読み、`application/dashboard_site.py` がファイルの変化で読み直す。
	- 構造の図の箱は `views/graph.js` の `boxHtml`・`frameHtml`（印の並び `.gx-marks`、`views/graph/marks.js`）、ボードの札は `views/_shared/parts.js` の `card`、横の欄は `views/_shared/panel.js` の `createScopePanel`（見出しは描くたびに `innerHTML` で作り直す）。
	"""

target: """
	- サーバー：設定の新しい節 `orca_web` を読み、Host の名前とポートから orca-web のオリジンを決めて、画面の CSP とリポジトリの一覧の API に入れる。構造の API が worktree の記録を返す。
	- 画面：新しい `core/orca.js` がオリジンを受け、orca-web の部品を import し、要約を1つの輪で読み、状態と対応を持って、描く側に知らせる。対応の計算は新しい `core/orca_match.js`（純粋）。
	- 構造の図、ボード、横の欄は、印の置き場（空の要素）を HTML に持ち、`core/orca.js` の知らせと自分の描き直しのたびに、その置き場に orca-web の `renderAgentMarks` で描く。横の欄は、見出しの外に作り直さない置き場を持ち、そこに `open-button.js` を置く。
	"""

design: {
	"D-01": {
		title:     "設定の節 orca_web と、orca-web のオリジンの決め方"
		satisfies: ["R-01", "F-04"]
		text: """
			`config.json` の最上位に任意の節 `orca_web: {enabled?: bool, port?: int}` を足す。既定は `enabled: true`、`port: 8791`。`port` は 1〜65535 の整数（bool は整数として扱わない）。
			読みは `infra/user_config.py` に `read_user_orca_web(path)` を足し、`domain/` に純粋な `parse_orca_web(payload)` を置く（`dashboard` の節の読みとは別。この節の誤りは `dashboard` と `todo` に影響しない）。
			節が壊れている（形や値の誤り）ときは `enabled: false` と同じに扱い（隠す側でなく、連携しない側に倒す）、`problem` に理由を持つ。ファイルがない、節がないときは既定。
			`dashboard_site.py` は、今の `config.json` の変化の見張り（signature）で、この節も読み直す。

			オリジン：要求の Host（`_host_allowed` を通ったもの）のホスト名と `port` から `http://<ホスト名>:<port>`。IPv6 のホスト名は今の Host の許しにないので扱わない。
			`port` がダッシュボード自身のポートと同じときは誤りとして `enabled: false`（自分を orca-web と取り違えない）。

			結果の形（サーバーの内部と API で同じ）：`{enabled: bool, origin: string | null, port: int, problem: string | null}`。`enabled` が false なら `origin` は null。
			"""
	}
	"D-02": {
		title:     "画面の CSP とリポジトリの一覧の API"
		satisfies: ["R-01", "R-02", "F-04", "F-06"]
		text: """
			`dashboard_http.py` の `_html` は、要求ごとに D-01 の結果を作り、`enabled` なら `_SHELL_CSP` の `script-src`、`style-src`、`connect-src`、`frame-src` の値の末尾に `origin` を1つ足した文字列を使う（関数 `shell_csp(origin | None)`。None なら今と同じ文字列）。
			`frame-ancestors` と、JSON・/files/ の CSP は変えない。
			リポジトリの一覧の API（`/api/v1/repositories`）の `server` に `orca_web`（D-01 の形）を足す。画面はこの値だけで orca-web の場所を知る（画面の側で `location.hostname` から作り直さない。CSP と食い違わないため）。
			埋め込みの画面（`embed`）でも CSP と値は同じ。埋め込みかどうかは画面の側（`ctx.embed`）が知り、D-06 で「Orca で開く」を置かない。
			`problem` があれば、`server.orca_web.problem` に入れ、`spec-dock dashboard list` の `config_problems`（層は user、パスは `config.json`）にも1行で出す。画面での見え方は epic-00526 のエージェントのタブが受け持つ（この Epic の画面では、連携を切ったときと同じく印を出さないだけ）。
			"""
	}
	"D-03": {
		title:     "構造の API の worktree の記録"
		satisfies: ["R-03", "F-05"]
		text: """
			`read_structure_facts` は今の `git worktree list` の1回の読みから、Scope ごとに、名指すブランチの worktree のすべてを `[{path, branch}]`（一覧の順）で返す。今の `branch` は、その最初のブランチのまま。
			構造の文書（`structure_document`）の上に `worktrees: {status: "ok" | "unreadable", paths: [<クローンのすべての worktree のパス>]}` を、各 Scope の項目に `worktrees: [{path, branch}]` を足す。
			`git worktree list` が失敗、時間切れ、カタログがないときは `status: "unreadable"`、`paths: []`、各 Scope の `worktrees: []`。`API_SCHEMA` は変えない（項目の追加だけ）。
			パスは `git worktree list --porcelain` が返す文字列のまま（正規化しない）。
			"""
	}
	"D-04": {
		title:     "対応の計算：core/orca_match.js（純粋）"
		satisfies: ["R-04", "F-02", "F-05"]
		text: """
			DOM と時刻を触らない関数だけを置き、node のテストで確かめる。

			- `matchWorktrees(structure, summary)` → `{status, byScope: Map<ScopeID, OrcaWorktree[]>}`。
			  - `structure.worktrees.status` が ok でない → `status: "no-records"`、空の Map（F-05）。
			  - `summary` が null、`schema` が `orca-web.worktree-summary/v1` でない、`worktrees` が並びでない → `status: "invalid"`、空の Map（F-02）。
			  - パスの比べ方：両方の末尾の `/` を除いた文字列の完全一致（大文字と小文字を区別する）。
			  - 段1：各要約の worktree を、Scope の worktree の記録の `path` と比べる。一致すればその Scope。
			  - 手がかり：要約の worktree のうち、パスが `structure.worktrees.paths` のどれかと一致したものの `project.id`（null でない）の集合。
			  - 段2：段1で対応しなかった要約の worktree で、`project.id` が手がかりの集合にあり、`branch` が null でなく、ある Scope の記録の `branch` と完全一致すれば、その Scope。
			  - 1つの要約の worktree は最初に一致した1つの Scope にだけ入る。Scope の中の並びは、SpecDock の記録の順（同じ記録の中は要約の順）。
			  - `issue`、`project.name`、`id` は比べない。
			- `mergedWorktree(list)` → orca-web の `renderAgentMarks` に渡せる1つの worktree の形（`agents` を連ね、`counts` を足し合わせ、`id`、`path`、`branch` は最初のもの）。1つならそのまま返す。
			- `orcaStatus({config, read, summary})` → `"off" | "loading" | "unreachable" | "orca-unreachable" | "orca-starting" | "ok"`。config が無効なら off。まだ一度も読んでいなければ loading。最後の読みか import が失敗、または形が違えば unreachable。`connection.state` が `unreachable` なら orca-unreachable、`starting` なら orca-starting。connected なら ok（`stale` は問わない）。
			"""
	}
	"D-05": {
		title:     "要約の読みと知らせ：core/orca.js"
		satisfies: ["R-01", "R-05", "R-08", "F-01", "F-03", "F-04"]
		text: """
			シェル（`app.js`）が、リポジトリの一覧の API の `server.orca_web` を受けて1回だけ作る。画面（構造の図、ボード、後のタブ）はこれを `ctx.orca` で受ける。

			- 無効なら何も読まず、import もしない。`status()` は off。
			- 有効なら `<origin>/embed/agent-marks.css` を `<link>` で1回足し、`import("<origin>/embed/agent-marks.js")` で部品を読み、`watchWorktreeSummary(origin, {onDocument, onError})` を1つだけ動かす（既定の 10 秒。画面が見えない間は部品が読まない）。
			- import に失敗したら unreachable にし、10 秒後に `?r=<試しの番号>` を付けた URL で import し直す（F-01）。成功するまで続け、成功したら読みの輪を始める。
			- `onDocument` で最後の要約を持ち、`onError` で最後の読みを失敗にする（前の要約は捨て、印を消す。F-01）。
			- 公開する口：`status()`（D-04 の状態）、`summary()`（ok のときだけ最後の要約、ほかは null）、`marks()`（読んだ部品の `renderAgentMarks` など。読めていなければ null）、`origin`、`subscribe(fn)`（要約か状態が変わるたびに呼ぶ。戻り値で外す）、`forScope(structure, scopeId)`（D-04 の `matchWorktrees` の結果を、同じ要約と同じ構造の間は覚えておき、その Scope の worktree の並びを返す。ok でなければ空の並び）。
			- SpecDock の画面の JavaScript は、orca-web に GET の要約の読みと、部品の import と CSS のほかの要求を送らない。
			"""
	}
	"D-06": {
		title:     "印の置き場と描き方（構造の図、ボード、横の欄の見出し）"
		satisfies: ["R-05", "R-06", "R-08", "F-01", "F-03"]
		text: """
			- 置き場：構造の図の Issue の箱の `.gx-marks` の先頭、Epic・Initiative の枠の見出し（`.gx-fh`）の末尾と箱の `.gx-marks` の先頭、ボードの札の印の行、横の欄の見出しの状態の行（`.pn-head`）に、空の `<span class="sd-orca" data-orca-scope="<ID>"></span>` を置く。置き場は Scope の ID だけで決まり、HTML の文字列は要約によらない（描き直しの比べで同じ文字列になる）。
			- 描き方：新しい関数 `paintOrcaMarks(root, ctx, structure)`（`views/_shared/orca_marks.js`）が、root の中の置き場ごとに `ctx.orca.forScope(structure, id)` を求め、worktree があれば `mergedWorktree` を `renderAgentMarks(slot, worktree, {size: "sm", max: 4})` に渡す（`onSelect` は渡さない）。なければ置き場を空にする。
			- 呼ぶとき：各画面の描き直しの直後と、`ctx.orca.subscribe` の知らせのとき。要約が同じなら描き直しても同じ印になり、描き直しの間に置き場を空にしない（R-08）。
			- 構造の図の箱の大きさは変えない。印が箱の幅に収まらないときは、orca-web の `max` の「+N」で詰める（Issue の箱は max 3、枠の見出しは max 4。値は Issue の担当が写しで確かめて決めてよい）。
			- 経過（R-06）は部品が `elapsedFrom` から描く。SpecDock は時刻を渡さない（`now` は部品の既定）。経過を進めるための時計は SpecDock に置かず、要約の読み直し（10 秒）と描き直しで進む。
			"""
	}
	"D-07": {
		title:     "横の欄の「Orca で開く」"
		satisfies: ["R-07", "R-08", "F-01", "F-03", "F-06"]
		text: """
			`createScopePanel` の `build()` が、見出し（`.pn-top`）の外の、作り直さない置き場 `.pn-orca` を作る（見出しの帯の右上に CSS で重ねる。位置は Issue の担当が写しで決める）。
			描くたびに、ねらい `key = <ScopeID>|<要約の worktree の id>|<明暗>` を求める（worktree は D-05 の `forScope` の最初のもの。明暗は `document.documentElement.dataset.theme`、なければ `prefers-color-scheme`）。
			ねらいが前と同じなら何もしない。違えば置き場を空にし、worktree があり、status が ok で、埋め込みの画面でなければ、`<script src="<origin>/embed/open-button.js" data-worktree="<id>" data-theme="<明暗>" data-size="sm">` を `document.createElement` で作って置き場に足す（`innerHTML` ではスクリプトが動かないため）。
			status が ok でなくなったら置き場を空にする。幅 390px 以下の扱いは部品に任せる。
			"""
	}
	"D-08": {
		title:     "配る文書"
		satisfies: ["R-09"]
		text: "ダッシュボードの設定を説明している配る文書（`docs/reference_cli.md` の設定の3段の節と、`docs/migration.md` の版ごとの節）に、`orca_web` の節（既定、書き方、壊れたとき）、orca-web の `ORCA_WEB_READ_ORIGINS` が SpecDock のオリジンを許す前提、届かないときの見え方を足す。どの文書に書くかは Issue の担当が今の文書の構成で決める。"
	}
}

compatibility: """
	- 構造の API とリポジトリの一覧の API は項目を足すだけで、`API_SCHEMA` は変えない。
	- 設定がなければ連携は既定で有効になり、画面の CSP に `http://<Host の名前>:8791` が足される。orca-web が動いていない PC では、読みが失敗して印が出ないだけ（F-01）で、図とボードは今と同じ。
	- `config.json` の `dashboard` と `todo` の節の読みは変えない。
	"""

risks: [
	"orca-web の部品の契約（関数の名前、要約の形）が orca-web の側で変わると、印が出なくなる。部品の import の失敗と形の違いは F-01・F-02 で印を消す側に倒すので、図とボードは壊れない",
	"ブラウザーが失敗した module の import を覚えることがある。D-05 の試し直しで、問い合わせの文字列を変える",
	"`localhost` や MagicDNS の名前で SpecDock を開くと、orca-web の Host の許し（127.0.0.1、localhost、Tailscale の IP）か CORS の許す先（ORCA_WEB_READ_ORIGINS）にないため読めない。届かないときと同じ見え方になる。配る文書に書く",
	"構造の図の箱は狭いので、印が多いと見づらい。`max` の値は Issue の担当が実データの写しで決める",
]
