package spec

// 設計（Issue）。型 specdock/v1。
// 正本は Epic（epic-00547）の design.cue の D-13、D-14、D-15。ここでは、それを実装の単位に割り、Epic が決めていない細部を決める。
// Epic の番号は「Epic D-xx」と書く。コードの場所は 2026-11-04 の main（1f5c042cb、#558 のマージの後）で確かめた。

goals: [
	"Epic D-13〜D-15 のとおりに、集約の一覧、`todo show <REF>`、`dashboard summary` の `todos` を作る",
	"集約、`todo show <REF>`、`dashboard summary`、サーバーの summary が、同じ登録簿の選び方（`select_catalogs`）と同じ数え方（`todo_model.tally`）を使う",
	"iss-00549 の `todo_store`、`classify`、`load_record`、`todo_document` を、TodoRepository に縛らない形に少し割って使い回す（別に書かない）",
]

current: """
	- `todo list` と `todo show` は `CANONICAL_HANDLERS` にだけあり、チェックアウトのリンク（`require_linked`）を要る。`specdock.todo-list/v1` は `mode: repository` の1行だけ。`classify` と `load_record` は `TodoRepository` を受ける。
	- `dashboard summary` は、ユーザーごとの状態の置き場（スナップショット、隠す印、サーバーの在りか）だけを読む。サーバーの `/api/v1/r/<repo>/summary` も `summary_document` で作る。
	- 登録簿 `<state_root>/canonical-registry.json` の行は `{catalog, main_checkout, repository, git, registered_at}`。`repository` は `host/owner/name` の鍵か null。
	"""

target: """
	- `todo list --all-repositories`、`todo list --repository R`、`todo show <REF>` が、チェックアウトの外でも動く（`REPOSITORY_INDEPENDENT_HANDLERS`）。
	- `specdock.dashboard-summary/v1` に `todos` がある。
	- `reference_cli.md` に新しい引数と契約がある。
	"""

design: {
	"D-01": {
		title: "登録簿からカタログを選ぶ（`application/todo_aggregate.py` の `select_catalogs`）"
		text: """
			- `select_catalogs(registry) -> tuple[Selected, ...]`：登録簿の行を、`repository` を `GithubRepository.parse` で読み（読めない値は null と同じ）、`(repository の鍵, main_checkout, catalog)` の順に並べる。null の行は `repository: null` のまま、それぞれ読む。同じ鍵の行が2つ以上あれば、`main_checkout` の道の順で最初の行を `read`、ほかを `duplicate`（読まない）にする（Epic D-14）。
			- `catalog_for(state_root, repository) -> Selected | None`：上の選び方で、その鍵の `read` の行を1つ返す。`dashboard summary`（REPOSITORY を渡したとき、リンクが正しくないとき）、`todo show <REF>`、サーバーの summary が使う。
			- 登録簿は `infra/canonical_registry.read_registry` で読む。`RegistryUnreadable` は呼び出し側が扱う（集約と `todo show <REF>` は `TODO_REGISTRY_UNREADABLE`、終了コード3。summary は `todos.status: unavailable`）。登録簿がなければ空。
			"""
		satisfies: ["R-10", "R-11", "F-03"]
	}
	"D-02": {
		title: "1つのカタログを、失敗を閉じ込めて読む（`read_catalog`）"
		text: """
			- `read_catalog(selected, *, user_layer) -> CatalogRead`：`status` は `ok` か `unreadable`。
			- `unreadable` になるのは、カタログが無い・ディレクトリでない・中を読めない（`os.scandir` が `OSError`）、`todos` があってディレクトリでない、`todos/` の読み取り（`TodoStore.read_all`）が `OSError` を出す、ときだけ。`problem` は `{code: "TODO_REPOSITORY_UNREADABLE", message, next_step: "spec-dock --project <main_checkout> canonical link"}`。`todos/` がないのは0件の `ok`。
			- `ok` のときは、iss-00549 の `classify` で、正しい v1 の記録と `invalid_files`、`conflict_copies` に分け、設定を `resolve((user_layer, store.read_settings()))` で決める（利用者の設定は1回だけ読む）。
			- `classify` と `load_record` は、`TodoRepository` ではなく `TodoStore` を受けるように割る（チェックアウトの道の呼び出しも直す。振る舞いは変えない）。
			"""
		satisfies: ["R-10", "F-03"]
	}
	"D-03": {
		title: "数え方（`domain/todo_model.tally`）と、リポジトリの行（`presentation/todo_document.repository_row`）"
		text: """
			- `tally(records, now) -> {open, blocking, overdue, snoozed}`：親のタスクだけ。`open` は閉じていない（`open` か `snoozed`）、`blocking`・`overdue` は `derived` の値、`snoozed` は `effective_status` が `snoozed`。iss-00549 の `todo_list.repository_row` の数え方をここに移し、チェックアウトの一覧、集約、`dashboard summary` が使う。
			- `repository_row(*, repository, catalog, main_checkout, hidden, status, problem, counts, invalid_files, conflict_copies)`：`specdock.todo-list/v1` の `repositories[]` の1行。`counts` は `tally` に `agent_parents {count, limit, source}` を足したもの。`unreadable` と `duplicate` の行は `counts: null`、`invalid_files: []`、`conflict_copies: []`。
			- `hidden` は `read_hidden(state_root, repository)`。`repository` が null なら `false`。
			"""
		satisfies: ["R-10", "R-11"]
	}
	"D-04": {
		title: "集約の一覧（`todo list --all-repositories`／`--repository`）"
		text: """
			- `list_all(namespace, cwd)`：`REPOSITORY_INDEPENDENT_HANDLERS["todo list"]`。`--all-repositories` も `--repository` もなければ `None` を返し、今のチェックアウトの道へ渡す。チェックアウトの中で実行しても、登録簿を読む。
			- `--repository R`（くり返せる）は `GithubRepository.parse` で鍵にし、形が違えば `TODO_REPOSITORY_INVALID`（終了コード2）。登録簿にない鍵は、警告 `TODO_REPOSITORY_UNKNOWN`（`details.repository`、`next_step: spec-dock dashboard list`）を出して、ほかを返す。`repository` が null の行は、`--repository` があるときは入れない。
			- 文書：`todo_list_document(mode="all_repositories")`。`filters` に `repositories`（鍵の配列。チェックアウトの道では空の配列）を足す。`repositories` は D-01 の順の全部の行。`items` は全部の `ok` の行の記録を、絞り込み（`matches`）の後に `order` と同じ並びで1つに並べる（同じ組と同じ時刻の間は、リポジトリの鍵、道の順）。
			- 警告：`TODO_REPOSITORY_UNREADABLE`（行ごと）、`TODO_REPOSITORY_DUPLICATE`（2つ目の行ごと。`details.catalog`、`details.chosen`）、`TODO_RECORD_INVALID` と `TODO_CONFLICT_COPY`（iss-00549 と同じ。`details.repository` を足す）、`TODO_SETTINGS_INVALID`（同じ道は1回だけ）。全体は成功（終了コード0）。
			- テキストの出力：リポジトリの行は、`unreadable`／`duplicate` なら `<repo>: unreadable [code] message`。タスクの行は、ID の代わりに `ref`（null なら ID）を出す。
			"""
		satisfies: ["R-10", "F-03"]
	}
	"D-05": {
		title: "`todo show <REF>`"
		text: """
			- `show_ref(namespace, cwd)`：`REPOSITORY_INDEPENDENT_HANDLERS["todo show"]`。`ID` に `/` がなければ `None`（今のチェックアウトの道）。
			- REF は最後の `/` で分け、前を `GithubRepository.parse`、後を `normalize_id` で読む（サブタスクの ID も受ける）。どちらかが読めなければ `TODO_REPOSITORY_INVALID`／`TODO_INVALID`（終了コード2）。
			- `catalog_for` で行を選ぶ。登録簿にない鍵は `TODO_REPOSITORY_UNKNOWN`（終了コード3、`next_step: spec-dock dashboard list`）、カタログが読めなければ `TODO_REPOSITORY_UNREADABLE`（終了コード3）、登録簿が読めなければ `TODO_REGISTRY_UNREADABLE`（終了コード3）。
			- 読み方と結果は、チェックアウトの `todo show` と同じ（`load_record`、サブタスクの確かめ、衝突の写しの警告、`todo_view`、`parent_closable` のときの `next_step`）。共通の部分を `show_from_store` に割る。
			"""
		satisfies: ["R-10", "F-03"]
	}
	"D-06": {
		title: "`dashboard summary` の `todos`（CLI とサーバー）"
		text: """
			- `presentation/dashboard_summary.summary_document(model, *, hidden, server, todos)` に引数 `todos` を足し、項目 `todos` に入れる。テキストの出力に `todos open=N blocking=N overdue=N`、`unavailable` なら `todos unavailable [code] message` の1行を足す。
			- `application/todo_aggregate.summary_todos(*, catalog, main_checkout, user_layer, now) -> dict` と `registry_summary_todos(state_root, repository, now)`：`read_catalog` の後に `tally` の `open`、`blocking`、`overdue` を返す。`{status: "ok", open, blocking, overdue, problem: null}`、読めなければ `{status: "unavailable", open: null, blocking: null, overdue: null, problem: {code, message, next_step}}`。`problem.code` は `TODO_REPOSITORY_UNREADABLE`、`TODO_REPOSITORY_UNKNOWN`（登録簿にない。`next_step: spec-dock canonical link`）、`TODO_REGISTRY_UNREADABLE`。
			- カタログの選び方（Epic D-15）：REPOSITORY を省いたチェックアウトの道（`summarize_checkout`）では、`require_linked` が通ればそのカタログ（登録簿に載っていなくてよい）、`CanonicalCommandError` なら登録簿（`catalog_for`）。REPOSITORY を渡した道（`summarize_named`）は登録簿だけ。人のタスクが読めなくても要約は成功する。
			- サーバー：`dashboard_http._summary` が `registry_summary_todos(self.site.state_root, repository, self.now())` を渡す。登録簿の選び方が CLI と同じなので、REPOSITORY を渡した `dashboard summary` と同じ数になる。キャッシュは足さない（画面の Issue の D-16）。
			- 時刻は `todo_common.utc_now()`（CLI）と `self.now()`（サーバー）。
			- ヘルプの `_READS_BY_ROOT["dashboard"]`、`_JSON_DATA_BY_ROOT["dashboard"]`、`dashboard summary` の説明に、カタログの `todos/` と登録簿を読むことと `todos` を足す。
			"""
		satisfies: ["R-11", "F-03"]
	}
	"D-07": {
		title: "CLI の引数、ヘルプ、文書"
		text: """
			- `todo list` に `--all-repositories`（旗）と `--repository REPOSITORY`（くり返し）を足す。`todo show` の引数の表示を `ID|REF` にする。葉の数（71）は変えない。
			- 葉の要約、`HELP_EFFECTS` の文、`_help_spec` の対象の文（`todo list`、`todo show`）、`_READS_BY_ROOT["todo"]` に登録簿を足す。
			- `reference_cli.md`（提供側と dogfood の写し）：C54 の説明に `todos`、C63・C64 の引数と説明、人のタスクの契約の節の一覧の説明（`mode: all_repositories`、`hidden`、`status` の3つの値、`filters.repositories`、`--no-schedule` のカタログは集まらないこと）、要約の契約の表に `todos`。`static-inventory.json` の行の sha256 を直し、前の sha256 を `known_old_sha256` に足す。
			"""
		satisfies: ["R-20"]
	}
	"D-08": {
		title: "iss-00549 のテストの穴（P2 の2件）"
		text: """
			- `tests/cli_runtime/test_issue549_todo.py` の `gh` の stub のテストで、`update`、`snooze`、`cancel`、`reopen` も実行し、`world.requests()` の数が変わらないことを確かめる。
			- 文字の確かめの一覧に `application/canonical_work.py` を足す（`work start` の実装の本体。`work_start.py` は残す）。
			- この Issue の新しいコマンド（集約、`show <REF>`、`dashboard summary`）も、`gh` の stub が呼ばれないことを確かめる。
			"""
		satisfies: ["R-21", "R-10"]
	}
}

compatibility: """
	- 公開の契約に項目を足すだけ（版は変えない）：`specdock.todo-list/v1` に `mode: all_repositories`、`repositories[].status` の `unreadable`／`duplicate`、`filters.repositories`。`specdock.dashboard-summary/v1` に `todos`。
	- 新しい引数：`todo list --all-repositories`、`--repository`。`todo show` が `REF` を受ける。コマンドの数（71）は変えない。
	- `dashboard summary` が、ユーザーごとの状態の置き場に加えて、登録簿とカタログの `todos/` も読む（何も書かず、GitHub にもサーバーにも要求を送らない点は同じ）。
	"""

risks: [
	"登録簿は PC ごとで、`canonical link --no-schedule` のカタログは集まらない。文書に書き、そのチェックアウトの中の `todo list` を使うよう示す",
	"サーバーの summary は要求ごとに登録簿とカタログの `todos/` を読む。件数が多くなれば、画面の Issue（iss-00554）が時刻で覚える読み取りを足す",
]
