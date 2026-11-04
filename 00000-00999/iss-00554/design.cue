package spec

// 設計（Issue）。型 specdock/v1。
// コードの場所は 2026-11-04 の main（0534cfe29）で確かめた。

goals: [
	"#549・#550 の読み取りの部品をそのまま使い、ダッシュボードの API と画面を足す（数え方と並びを二重に書かない）",
	"人のタスクが読めなくても、構造の画面は今までどおり描く",
	"見るだけ（書く口を作らない）",
]

current: """
	- `todo list --all-repositories` は `application/todo_aggregate._list_all` の中で、登録簿の行ごとに `read_catalog` し、`repository_row`、`list_item`、`order`、`matches` で `specdock.todo-list/v1` を作る。行ごとの閉じ込めもここにある。
	- サーバーの summary の `todos` は `registry_summary_todos`（登録簿から `catalog_for` でカタログを選び、`tally` で数える）。
	- `DashboardSite.view` の `revision` は、スナップショットと同期の状態のファイルの時刻などから作り、`todos/` を見ない。
	- 画面の道は `/`、`/r/<repo>/{graph,board,timeline,scopes/<ID>}`。上の帯のタブは3つで、リポジトリのない道（横断の概況）にはタブがない。
	- 詳しい画面のタブは `views/_shared/logic.js` の `TABS`（概要、依存、配下、文書、Artifact）。カードは `views/_shared/parts.js` の `card`、構造の図の箱と枠は `views/graph.js` の `boxHtml`／`frameHtml`、印は `views/graph/marks.js`。
	"""

target: """
	- サーバーに人のタスクの API が4つ増え、`structure` と `scopes/<ID>` に印と一覧、`revision` に `todos/` の時刻が入る。
	- 画面に `views/todos.js`（一覧と1件）が増え、構造の図・ボード・詳しい画面・横断の概況に印と数が出る。
	"""

design: {
	"D-01": {
		title: "集約の読み取りを、CLI とサーバーで共有する"
		text: """
			- `application/todo_aggregate.py` の `_list_all` から、行ごとの読み取りと閉じ込めの本体を `collect(rows, *, state_root, filters, now, user_layer, read=read_catalog) -> Collected(rows, items, warnings)` として切り出す（`rows` は `select_catalogs` の結果を絞ったもの。`read` は読み取りを差し替える口で、サーバーが覚えた読み取りを渡す）。`_list_all` は `collect` を呼ぶだけにし、CLI の出力と警告は1文字も変えない（既存の #550 のテストで縛る）。
			- 1つのリポジトリの一覧も `collect` に1行を渡して作る（`mode` は `repository`）。
			- 新しく書くのは、サーバーの側の、表示中のリポジトリの選び方と覚え（D-02）だけ。
			"""
		satisfies: ["R-01", "R-03", "R-08"]
	}
	"D-02": {
		title: "`application/dashboard_todos.py`：サーバーの人のタスクの読み取り"
		text: """
			- `DashboardTodos(state_root, now)`：スレッドの鍵つきで、カタログの道ごとに `(署名, CatalogRead)` を覚える。署名は `todos/` と、その下の年月のディレクトリと `settings.json` の `(st_mtime_ns, st_size)` の組（ない物は None）。記録の書き込みは年月のディレクトリの中の置き換え（rename）なので、ディレクトリの時刻が変わる。署名が同じなら `read_catalog` を呼ばない。利用者の設定のファイル（`user_config_path()`）の署名も覚えの鍵に入れ、件数の目安の古さを防ぐ（仕様のレビューの P3）。
			- カタログの選び方：`SiteRepository` ごとに登録簿を読み、`catalog_for(registry, repository)` の行を使う（2つのクローンでも最初の行。D-14 と同じ）。登録簿が読めない・行がないときは、一覧ではそのリポジトリの行を契約どおりの `status: unreadable` にし、`problem.code` を `TODO_REGISTRY_UNREADABLE`／`TODO_REPOSITORY_UNKNOWN` にする（`unavailable` は `structure` の要約だけで使う）。一覧の API は、読めない行があっても 200 で返す（仕様のレビューの P2）。
			- 提供する読み取り：
			  - `list_document(sites, status)`：表示中の全リポジトリの `specdock.todo-list/v1`（`mode: all_repositories`、`hidden: false`）。
			  - `repository_document(site, status)`：1つの一覧（`mode: repository`）。
			  - `one(site, todo_id)`：`show_from_store` の1件。
			  - `annotations(site, model)`：D-03 の印と一覧と要約。
			  - `signature(site)`：`revision` に入れる署名。ファイルの署名に加え、覚えた記録から今の時刻で決まる組（期限切れ・期限が近い・延期明けのタスクの ID）を入れ、書き込みがなくても期限が過ぎれば `revision` が変わるようにする（仕様のレビューの P2）。
			- `status` の問い合わせは `open|snoozed|done|cancelled|all`（既定 `open`）。ほかの値は 400 `DASHBOARD_TODO_FILTER_INVALID`。
			- ユーザーの設定（件数の目安）は `read_user_todo_settings()` で読む（読むだけ）。
			"""
		satisfies: ["R-01", "R-03", "R-07", "R-08", "F-01"]
	}
	"D-03": {
		title: "Scope の印（`scope_marks`）と、`structure`・`scopes/<ID>` に足す項目"
		text: """
			- `domain/todo_model.scope_marks(records, parents) -> dict[str, {blocking, blocking_with_descendants, related}]`：`records` は形の正しい親の記録、`parents` は Scope の ID から親の ID（スナップショットの親子）。閉じていない（延期中を含む）タスクだけを数える。`blocking` は `scopes.blocks` に直接その ID を持つ数、`related` は `scopes.related` に持つ数、`blocking_with_descendants` は自分と配下の全 Scope のどれかを止めるタスクを、タスクの ID で重ねずに数えた数。`parents` にない ID は数えない。親子が輪になっていても止まる。
			- `presentation/dashboard_api.py`：`scope_item` に `todos: {blocking, blocking_with_descendants, related}`（ない Scope は全部0）。`structure_document` の上に `todos: {status, open, blocking, overdue, problem}`（`tally` と同じ数え方。D-15 の `todos` と同じ形）。`scope_document` に `todos: {status, problem, blocking: [...], related: [...], descendants: [...]}`。一覧の1件は `{ref, repository, id, title, kind, due, overdue, due_soon, effective_status, blocks, related}`。`descendants` は配下の Scope を止めている（自分は止めていない）タスクで、`blocks` で、どの配下かが分かる。並びは `order`。
			- 印の形は画面のためで、契約にしない（Epic の compatibility）。
			"""
		satisfies: ["R-04", "R-05", "R-06", "F-01"]
	}
	"D-04": {
		title: "`dashboard_http.py`：道と API"
		text: """
			- 画面の道：`/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>` に画面の殻を返す。
			- API：
			  - `GET /api/v1/todos[?status=]`：`list_document`（表示中のリポジトリだけ。隠したものは入れない）。
			  - `GET /api/v1/todos/revision`：表示中の全リポジトリの `signature` と登録簿・隠す印の署名を合わせた16桁の値 `{schema, revision}`。
			  - `GET /api/v1/r/<repo>/todos[?status=]`、`GET /api/v1/r/<repo>/todos/<ID>`：1件は `normalize_id` を通し、`TODO_NOT_FOUND` と形の違う ID は 404、`TODO_RECORD_INVALID`／`TODO_SCHEMA_UNSUPPORTED`／重なった ID は 409、1件の要求でカタログが読めないときは 503（`code` と `next_steps` つきの `specdock.dashboard/v1` の誤り）。
			  - 知らない・隠したリポジトリは、今の `/api/v1/r/...` と同じ 404。1つのリポジトリの例外は、今と同じくその応答だけの 500。
			- `structure` と `scopes/<ID>` は `annotations` を渡す。人のタスクの読み取りが例外を出しても、印を0、`todos.status` を `unavailable` にして構造を返す（F-01）。
			- `DashboardSite._revision` に、`DashboardTodos.signature(site)` を足す（`DashboardSite` が `DashboardTodos` を持ち、`DashboardHttp` は `site.todos` を使う）。
			"""
		satisfies: ["R-01", "R-03", "R-07", "R-08", "F-01", "F-02"]
	}
	"D-05": {
		title: "画面：`views/todos.js`、`views/todos.css`、`views/todos/logic.js`"
		text: """
			- `core/route.js`：`/todos` を `{view: "todos", repository: null}`、`/r/<repo>/todos` を `view: "todos"`、`/r/<repo>/todos/<ID>` を `view: "todos", todo: <ID>` にする。`todoPath(repository, id)` を足す。
			- `core/topbar.js`：リポジトリの道のタブに「人のタスク」（4つ目）を足す。リポジトリのない道（横断の概況、全リポジトリの人のタスク）には「横断の概況」と「人のタスク」の2つのタブを出す。`app.js` は題名と、リンクの横取りで `/todos` を画面として扱うことだけを足す。
			- `views/todos/logic.js`（DOM に触れない純粋な関数。node で試す）：組の決め方（期限切れ、期限が近い、止めている、あとで、延期中、閉じた。サーバーの `derived` から決め、サーバーの並びを保つ）、絞り込み（`repo`、`tag`、`kind`、`closed`）の読み書き、期限と経過の言葉、安全な Markdown（全部を先にエスケープしてから、段落、箇条、コードの塊、行の中のコード、太字、`http(s)` のリンクだけを描く）。
			- 一覧：見出し、絞り込み（リポジトリの選択、種類の切り替え、タグの選択、「延期中と閉じたものも」の切り替え。どれも URL の問い合わせ）、組ごとの見出しと件数、カード（種類、題名、リポジトリ、期限の言葉、止めている Scope の ID、サブタスクの残り、タグ）。期限切れのカードは danger の左の帯、記号、「期限切れ（n時間超過）」。読めないリポジトリ、形の正しくない記録・衝突の写しは知らせの枠で、次の1手（`spec-dock canonical link`、`spec-dock todo check`）を出す。
			- 1件：Epic の D-16 の項目（題名、種類、状態、期限、依頼者、本文、選択肢と推奨、答える場所、サブタスクと残り、止めている・関係する Scope へのリンク、経緯、答えと原文の記録、タグ、リンク）。写せるコマンドや完了のボタンは置かない。
			- 更新：リポジトリの道は殻の5秒ごとの `revision` で描き直され、`ctx.data.revision` が変われば読み直す。`/todos` は自分で5秒ごとに `/api/v1/todos/revision` を見て、変われば読み直す（隠れたタブでは見ない）。
			- 見た目は `ds.css` の色の名前と `_shared/parts.css` の部品（`sd-page`、`sd-badge`、`sd-callout`、`sd-card` の形）にそろえ、`views/todos.css` は `[data-view="todos"]` の下に閉じる。390px で横にはみ出さない。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-07", "R-08"]
	}
	"D-06": {
		title: "既存の画面への印"
		text: """
			- `core/ui.js`：人の印の形（`ICONS.person`）と `humanMark(n, {descendants})` の言葉を1か所に置く。「人 n」、配下を含むときは「人 n」に小さく「配下も」を添え、`title`／`aria-label` を「人のタスク n件が止めている（配下を含む）」にする。
			- 構造の図（`views/graph.js`、`graph/marks.js`）：Issue の箱は `todos.blocking`、Epic と Initiative の枠と木の枠は `todos.blocking_with_descendants`。印は `gx-marks`／`gx-fm` の「後に続く」の前に置き、行は折り返さない（#556 の幅を変えない）。選んだときの横の板に「人のタスク」の行（数と、詳しい画面のタブへのリンク）。
			- ボード（`views/_shared/parts.js` の `card`）：Issue は `blocking`、Epic と Initiative は `blocking_with_descendants` の印を `sd-card__meta` に足す。
			- Scope の詳しい画面（`views/scope.js`、`_shared/logic.js` の `TABS`）：「人のタスク」のタブ（件数つき）。止めているもの、（親なら）配下を止めているもの、関係するものの3つの表に、題名、期限（期限切れの印）、種類、どの Scope を止めるかを出し、1件の画面へリンクする。読めないときは知らせの枠。
			- 横断の概況（`views/overview.js`）：札の印の列に「人のタスク 開 n」「期限切れ m」の印（期限切れが1件以上なら danger）。`structure.todos` を使い、`unavailable` なら「人のタスクが読めない」の印。札から全リポジトリの人のタスクの画面への絞り込みのリンクは置かない（札そのものがリンクで、入れ子のリンクになるため。上の帯から入る）。
			"""
		satisfies: ["R-04", "R-05", "R-06", "F-01"]
	}
}

compatibility: """
	- 足すだけ。`structure` と `scopes/<ID>` の項目の追加は契約に入らない。`revision` の値は変わる（中身の意味は変わらない）。
	- 公開の契約に足すもの（次の版の移行の注記に書く）：API の `GET /api/v1/todos`、`GET /api/v1/r/<repo>/todos`（中身は `specdock.todo-list/v1`）、`GET /api/v1/r/<repo>/todos/<ID>`（CLI の1件の形）と、画面の道 `/todos`、`/r/<repo>/todos`、`/r/<repo>/todos/<ID>`。`/api/v1/todos/revision` は画面のための道で、契約にしない。
	- CLI の出力は変わらない（`collect` への切り出しは中身を変えない）。
	"""

risks: [
	"年月のディレクトリの時刻だけでは、同じ秒の同じ大きさの書き換えを見逃すおそれ。`st_mtime_ns` を使うので、ほとんど起きない。起きても次の書き込みで直る",
	"上の帯のタブが4つになり、390px の下のタブが詰まる。写しで確かめ、詰まれば言葉を短くする",
	"安全な Markdown の小さな関数は、表や入れ子の箇条を描かない。本文はエージェントが短く書く前提で、描けないものは文字のまま出る",
]
