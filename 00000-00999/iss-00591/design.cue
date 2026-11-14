package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"orca-web の場所は、サーバーの1か所（設定の読みと要求の Host）で決め、CSP と画面の両方が同じ値を使う",
	"Scope と worktree の対応と状態は、DOM と時刻を触らない純粋な関数にし、node のテストで確かめる",
	"要約の読みは画面全体で1つにし、iss-00592 の印と epic-00526 のタブが同じ結果を使えるようにする",
	"今の構造の API、一覧の API、CSP、設定の読みは、項目を足すだけで、連携を切れば今と同じになる",
]

current: """
	- 設定：`infra/user_config.py` の `read_user_dashboard` が `domain/dashboard_visibility.py` の `parse_user_dashboard` で `dashboard` の節を読む。`application/dashboard_site.py` の `DashboardSite._refresh_listing` が、`config.json` の署名（`_signature`）が変わったときだけ読み直し、`_Listing` に持つ。`config_problems()` は `_Listing.problems`。
	- CSP：`application/dashboard_http.py` の `_SHELL_CSP`（固定）と `_html`。一覧の API は `_repositories()`（要求を受けない）。`DashboardHttp.port` はダッシュボード自身のポート。`_host_allowed` が Host を確かめる。
	- 構造：`read_structure_facts` が `_branches` で `git worktree list` を1回読み、Scope ごとに最初のブランチを返す。`structure_document` と `scope_item` が JSON を作る。revision は `DashboardSite._revision` の材料の sha256。
	- 画面：`app.js` の `boot` が一覧の API を読み、`state.server` に持ち、`module.render(root, ctx)` に ctx を渡す。`core/` に orca-web のものはない。
	"""

target: """
	- サーバー：`domain/orca_web.py` の純粋な `parse_orca_web` と `orca_web_origin`。`DashboardSite` が `_Listing` に `orca_web` の設定を持ち、`orca_web()` で返す。`DashboardHttp` が要求の Host から origin を決め、`_html` の CSP と一覧の API の `server.orca_web` に使う。構造の API が worktree の記録を返し、revision に worktree の署名が入る。
	- 画面：`core/orca_match.js`（純粋）と `core/orca.js`（読みの輪）。`app.js` が `createOrca(state.server?.orca_web)` を1回作り、ctx に `orca` を足す。
	"""

design: {
	"D-01": {
		title:     "設定の節 orca_web の読み（domain/orca_web.py、infra、DashboardSite）"
		satisfies: ["R-01", "F-02"]
		text: """
			`domain/orca_web.py`（新規、純粋）：

			- `OrcaWebSettings(enabled: bool, port: int, problem: str | None, section_problem: bool)`（frozen dataclass）。既定 `OrcaWebSettings(True, 8791, None, False)`。
			- `parse_orca_web(payload: bytes | None, *, read_error: str | None = None) -> OrcaWebSettings`：
			  - `read_error` がある → `(False, 8791, read_error, False)`。`payload` が None（ファイルがない）→ 既定。
			  - JSON でない、最上位が dict でない、`schema` が `specdock.config/v1` でない → `(False, 8791, <理由>, False)`（ファイルの誤り。今の `dashboard` の読みと同じ判定。共通の `_document` があれば使う）。
			  - `orca_web` の鍵がない → 既定。値が dict でない、知らない鍵がある、`enabled` が bool でない、`port` が int でない（bool は不可）か 1〜65535 の外 → `(False, 8791, "orca_web.<鍵> …", True)`。
			  - それ以外 → `(enabled, port, None, False)`（`enabled` の既定 true、`port` の既定 8791）。
			- `orca_web_origin(settings, host_name: str, own_port: int) -> dict`：結果の形 `{enabled, origin, port, problem}`。`settings.enabled` が false → `{False, None, port, problem}`。`port == own_port` → `{False, None, port, "orca_web.port must differ from the dashboard's own port <own_port>"}`。それ以外 → `{True, f"http://{host_name}:{port}", port, None}`。`host_name` は小文字にしたもの。

			`infra/user_config.py` に `read_user_orca_web(path: Path | None = None) -> OrcaWebSettings`（`read_optional` と `parse_orca_web`）。
			`DashboardSite._refresh_listing` は、今 `read_user_dashboard` を呼ぶ同じ所で `read_user_orca_web(self.user_config)` を呼び、`_Listing.orca_web` に持つ（今の署名で読み直すので、起動し直さずに効く）。`DashboardSite.orca_web() -> OrcaWebSettings` を足す。
			`section_problem` が true のときだけ、`problems` に `ConfigProblem("user", <config.json のパス>, settings.problem)` を足す（今の並べ方の規則のまま。リポジトリの出し入れの `Visibility` には入れない）。ファイルの誤りは今の `dashboard` の行が出るので足さない。
			"""
	}
	"D-02": {
		title:     "画面の CSP と一覧の API（dashboard_http.py）"
		satisfies: ["R-01", "R-02", "F-02"]
		text: """
			- `shell_csp(origin: str | None) -> str`（モジュールの関数）：None なら `_SHELL_CSP` と同じ文字列。文字列なら、`script-src 'self'`、`style-src 'self' 'unsafe-inline'`、`connect-src 'self'`、`frame-src 'self'` の4つの指示の値の末尾に ` <origin>` を足したもの。ほかの指示と順は変えない。
			- `DashboardHttp._orca(request) -> dict`：`_host_allowed` を通った要求の Host のホスト名（`rpartition(":")` の前、小文字）と `self.site.orca_web()` と `self.port` から `orca_web_origin` を返す。
			- `_html(status, body, embed=…, orca_origin=None)`：CSP を `f"{shell_csp(orca_origin)}; frame-ancestors {ancestors}"` にする。画面の HTML を返す呼び出し（`_shell`、`_repository_page` の画面と、隠したリポジトリの画面）は、`self._orca(request)["origin"]` を渡す。ほかの `_html` の呼び出しと、`_json`、`_material` は変えない。要求を受け取っていない関数には、要求か origin を引数で渡す（形は実装担当が決めてよい）。
			- `_repositories(request)` の `server` に `"orca_web": self._orca(request)` を足す。
			- 埋め込み（`embed=1`）でも同じ CSP と値。
			"""
	}
	"D-03": {
		title:     "構造の API の worktree の記録と、revision の worktree の署名"
		satisfies: ["R-03", "F-03"]
		text: """
			- `read_structure_facts` は今の `git worktree list` の1回の読みから、Scope ごとの `worktrees: [{path, branch}]`（名指すブランチのすべて、一覧の順）と、クローンのすべての worktree のパスを作る。戻り値の形は、今の `{ID: {"assurance", "branch"}}` を壊さない形にする（例：`StructureFacts(readings, worktrees_status, paths, by_scope)` の dataclass か、読みの dict に `"worktrees"` を足し、文書の上の値を別の戻り値にする。形は実装担当が決めてよい）。`branch` は今のまま（最初の worktree のブランチ）。
			- `structure_document` の上に `"worktrees": {"status": "ok" | "unreadable", "paths": [...]}`、`scope_item` に `"worktrees": [{"path", "branch"}]` を足す。カタログがない、`git worktree list` が失敗・時間切れ → `status: "unreadable"`、`paths: []`、各 Scope の `worktrees: []`。`model` がない文書にも上の `worktrees` を置く（`unreadable`）。パスは `GitWorktreeRecord.path` の `str()` のまま。ブランチのない（detached）worktree もパスの一覧には入れる。
			- revision：`infra/` に `worktree_signature(checkout: Path | None) -> tuple | None` を足す。`checkout / ".git"` が dir でなければ None。dir なら `HEAD` と、`worktrees/` の dir そのものと、その下の各項目の `HEAD` と `gitdir` の `(名前, mtime_ns, size)` を名前の順に並べた tuple（読めない項目は None の値）。`DashboardSite._revision` の `parts` にこれを足す（`site.checkout`）。`git` を呼ばない。
			"""
	}
	"D-04": {
		title:     "対応と状態の計算：core/orca_match.js（純粋）"
		satisfies: ["R-04", "R-05", "F-01", "F-03"]
		text: """
			`src/spec_dock/assets/dashboard/core/orca_match.js`（新規）。DOM、時刻、fetch を触らない ES Module。

			- `SUMMARY_SCHEMA = "orca-web.worktree-summary/v1"`。
			- `normPath(value)`：文字列なら末尾の `/` をすべて除いたもの（`/` だけなら `/`）、ほかは null。
			- `summaryValid(summary)`：object で、`schema` が `SUMMARY_SCHEMA`、`worktrees` が並び。
			- `matchWorktrees(structure, summary) -> {status: "ok" | "no-records" | "invalid", byScope: Map<string, object[]>}`：
			  - `structure?.worktrees?.status !== "ok"` → `no-records`、空の Map（F-03）。次に `summaryValid` でない → `invalid`、空の Map（F-01）。
			  - 記録：`structure.scopes` の各項目の `worktrees`（並びでなければ空）の `{path, branch}`。パスの表 `normPath(path) → 最初の ScopeID`、ブランチの表 `branch → 最初の ScopeID`（Scope の番号の順 = `structure.scopes` の順）。
			  - 段1：要約の worktree（object でないものは飛ばす）の `normPath(path)` がパスの表にあれば、その Scope。
			  - 手がかり：`normPath(path)` が `structure.worktrees.paths` の `normPath` の集合にある要約の worktree の、文字列の `project.id` の集合。
			  - 段2：段1で対応しなかったもので、`project.id` が文字列で手がかりにあり、`branch` が文字列でブランチの表にあれば、その Scope。
			  - 1つの要約の worktree は1つの Scope にだけ入る。Scope の中の並びは、SpecDock の記録の順（その Scope の `worktrees` の並びで先に一致した記録のもの）、同じ記録に一致したものは要約の順。
			  - `issue`、`project.name`、`id` は比べない。親の Scope を子から合算しない。
			- `mergedWorktree(list)`：0件 → null、1件 → そのもの。2件以上 → 最初の `id`、`path`、`branch`、`project` と、`agents` を連ねた並び、`counts` の各数（数でない値は 0）を足したもの。
			- `orcaStatus({enabled, read, summary})`：`enabled` が false → `off`。`read` が `"none"` → `loading`。`read` が `"failed"` か、`summaryValid(summary)` でない → `unreachable`。`summary.connection?.state` が `unreachable` → `orca-unreachable`、`starting` → `orca-starting`、`connected` → `ok`。それ以外の値 → `unreachable`。`stale` は見ない。
			"""
	}
	"D-05": {
		title:     "要約の読みと知らせ：core/orca.js と、シェルの組み込み"
		satisfies: ["R-01", "R-05", "F-01", "F-02"]
		text: """
			`src/spec_dock/assets/dashboard/core/orca.js`（新規）。`createOrca(config, deps = {})` を公開する。`config` は一覧の API の `server.orca_web`（ない、または `enabled` が true でない、または `origin` が文字列でない → 無効）。
			`deps` はテストのための差し替え：`importModule(url)`（既定 `(u) => import(u)`）、`addStylesheet(href)`（既定は `<link rel="stylesheet">` を `document.head` に足す）、`setTimer`、`clearTimer`（既定 `setTimeout`、`clearTimeout`）、`retryMs`（既定 10000）。

			- 無効：何もしない。`status()` は `off`、`summary()` は null、`marks()` は null、`forScope()` は `[]`、`subscribe` は何もしない外しの関数を返す。
			- 有効：`addStylesheet(<origin>/embed/agent-marks.css)` を1回。`importModule(<origin>/embed/agent-marks.js)`（2回目からは `?r=<試しの番号>` を付ける）。失敗 → read を failed にし、知らせ、`retryMs` 後に試し直す（成功するまで）。成功 → 部品を持ち、`watchWorktreeSummary(origin, {onDocument, onError})` を1つだけ動かす。
			- `onDocument(doc)`：最後の要約を doc にし、read を ok にする（形が違っても持ち、`orcaStatus` が unreachable を返す）。`onError`：最後の要約を null、read を failed にする。どちらも状態か要約が変わったら知らせる（同じ doc の参照では知らせない。読むたびに新しい doc なので、読めるたびに知らせる）。
			- 口：`status()`（D-04 の `orcaStatus`）、`summary()`（status が ok のときだけ最後の要約、ほかは null）、`marks()`（読めた部品のモジュール、なければ null）、`origin`（有効なら origin、無効なら null）、`subscribe(fn)`（戻り値で外す。知らせの中の例外は飲み込み、ほかの購読者を止めない）、`forScope(structure, scopeId)`（status が ok でなければ `[]`。ok なら `matchWorktrees(structure, summary)` の結果を、同じ structure と同じ要約の参照の間は覚え、`byScope.get(scopeId) ?? []`）、`stop()`（輪と試し直しを止める。テストと後の画面のため）。
			- orca-web に送る要求は、CSS の読み込み、部品の import（とその部品が import するファイル）、要約の GET だけ。

			シェル：`app.js` の `boot` は一覧の API を読んだ後に `state.orca = createOrca(listing.server?.orca_web)` を1回だけ作る（一覧の読みに失敗したら `createOrca(null)`）。`checkServer` の読み直しでは作り直さない（設定の変化は次に開いた画面から効く）。`module.render` の ctx に `orca: state.orca` を足す。画面（views/）はまだ使わない。
			"""
	}
	"D-06": {
		title:     "実データの確かめ（タスク担当）"
		satisfies: ["R-06"]
		text: """
			最後の実装のコミットから wheel を作り、`.workbench/iss-00591/venv` の隔離した venv に入れ、状態の置き場の写し（`.workbench/iss-00591/state`、道具の環境の状態の置き場から登録簿とスナップショットを写す）で、別のポート（18591）と `--tailscale` で `spec-dock dashboard serve` を立てる。
			確かめの式 `.workbench/iss-00591/match.mjs`（node）：試しのサーバーの `/api/v1/repositories` と spec-dock の構造の API と、常駐の orca-web の `/api/worktrees/summary` を node から読み（Origin を付けない読みは CORS の対象外）、配る `core/orca_match.js` を import して `matchWorktrees` を走らせ、対応した Scope と worktree の id と path の末尾の名前を出す。
			ブラウザーの確かめ：headless Chrome で試しの画面を開き、CSP にオリジンが入ること、部品の CSS と import と要約の読みの要求が出て、要約の読みが CORS で拒まれること（CDP のネットワークとコンソールの記録。拒まれた読みは `onError` に入り、状態は unreachable になる）、構造の図とボードが描かれ、ページの例外がないことを確かめる（写しは要らない）。
			記録は report.md に残す（ユーザー名を含む絶対パスと実際の IP は書かない）。
			"""
	}
}

compatibility: """
	- 構造の API とリポジトリの一覧の API は項目を足すだけで、`API_SCHEMA` は変えない。
	- 設定がなければ連携は既定で有効になり、画面の CSP に `http://<Host の名前>:8791` が足される。orca-web が動いていない PC では、画面の読みが失敗して状態が unreachable になるだけで、画面はまだ何も描かない。
	- `config.json` の `dashboard` と `todo` の節の読みとリポジトリの出し入れは変えない。
	- 構造の revision の材料が増えるので、更新の後に一度だけ画面が構造を読み直す。
	"""

risks: [
	"orca-web の部品の契約（関数の名前、要約の形）が orca-web の側で変わると、状態が unreachable になる。図とボードは壊れない",
	"ブラウザーが失敗した module の import を覚えることがある。問い合わせの文字列を変えて試し直す",
	"`localhost` や MagicDNS の名前で SpecDock を開くと、orca-web の Host の許しか CORS の許す先にないため読めない（iss-00592 の配る文書に書く）",
	"`.git` が dir でない main のチェックアウト（別の場所の git dir）では worktree の署名が None で、worktree の変化だけでは revision が変わらない。ほかの変化か再読み込みで追いつく",
]
