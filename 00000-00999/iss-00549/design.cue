package spec

// 設計（Issue）。型 specdock/v1。
// 正本は Epic（epic-00547）の design.cue の D-01〜D-13 と D-18。ここでは、それを実装の単位に割り、Epic が決めていない細部を決める。
// Epic の番号は「Epic D-xx」と書く。コードの場所は 2026-11-04 の main（0.6.0、ae8c72456）で確かめた。

goals: [
	"Epic D-01〜D-12 と D-18 のとおりに、記録の形、2段の検査、置き場、ロック、ID、サブタスク、期限、件数、設定、Scope との結び付き、10のコマンドを作る",
	"記録を読むすべての道（書くコマンド、一覧、検査）が同じ `todo_record.validate` と `todo_model` の純粋な関数を使い、CUE の型と同じ見本で縛られる",
	"集約（iss-00550）と画面（iss-00554）が、この Issue の `todo_store`、`todo_model`、`todo_document` をそのまま使えるようにする",
]

current: """
	- `todo` のコマンド、`todos/` の記録、利用者の設定のファイルはない。公開のコマンドは61。
	- カタログへの書き込みは `canonical_catalog.catalog_changes`（ロック、形式の版、changeset）と `file_publication.publish_file`（`expected` で書き換え、なしで新規）。`require_linked` がリンクを確かめる。
	- `cue` は `infra/cue_tool.CueTool.export` だけ。型は `src/spec_dock/cue/v1/`（`package spec`）。
	- `render_text` は、専用の分岐がない `FamilyData` を JSON の字下げで出す。
	"""

target: """
	- `spec-dock todo add|list|show|update|done|snooze|cancel|reopen|check|settings`（71の葉）。`settings` はチェックアウトの外でも動く。
	- `src/spec_dock/cue/todo/v1/todo.cue` の `#Todo` と `#Records`、`tests/fixtures/todo/{valid,invalid}/*.json`。
	- `reference_cli.md` に10のコマンドと2つの契約（`mode: repository`）。
	"""

design: {
	"D-01": {
		title: "記録の形と書く前の検査（`domain/todo_record.py`）"
		text: """
			Epic D-02、D-03、D-04 のとおり。細部：

			- 記録は JSON の `dict` のまま扱う（型は開いているので、知らない欄を読み、書き換えるときに残す）。新しい記録は、Epic D-02 の全部の欄を必ず書き、値がないものは `null`（`body`、`recommendation`、`reply_to`、`effort`、`snooze_until`、`resolution`）か空の配列（`options`、`links`、`tags`、`subtasks`、`history` を除く）にする。
			- `validate(record) -> tuple[Problem, ...]`（`Problem(field, message)`、`field` はドットでつないだ道。例 `subtasks.1.status`）。調べること：
			  - `schema` が `specdock.todo/v1`（違えば検査を進めず、呼び出し側が `TODO_SCHEMA_UNSUPPORTED` にする）。
			  - `id`：`^t-[0-9a-hjkmnp-tv-z]{4}$`。`title`：文字列、空白だけでない、改行なし、200文字まで（サブタスクも同じ）。
			  - `kind`、`status` の値。`kind: todo` は `origin.by: human` だけ。
			  - 時刻（`created_at`、`updated_at`、`due`、`snooze_until`、`resolution.at`、`history[].at`、サブタスクの時刻）：`YYYY-MM-DDTHH:MM:SSZ` で、暦として正しい。
			  - `origin`：`by` は `agent` か `human`、`role` は文字列か null。エージェントは `role`、`body`、`reply_to` が空白だけでない文字列、`effort` が `^[1-9][0-9]*(m|h|d)$`。`decide` のエージェントは `options` が2つ以上で `recommendation` が null でない。
			  - `options`：`{key, text}` の配列。`key` は `^[A-Za-z0-9][A-Za-z0-9_.-]*$` で重ならない、`text` は空白だけでない。`recommendation`：null か `{key, reason}`、`key` は `options` のどれか、`reason` は空白だけでない。
			  - `status: snoozed` なら `snooze_until` が時刻。`done`、`cancelled` なら `resolution` が `{at, by, role, choice, note, record}`（`choice` は null か `options` の `key`、`cancelled` は `note` が空白だけでない）。`open`、`snoozed` なら `resolution` は null。
			  - `scopes`：`{related, blocks}`、各要素は `^(init|epic|iss)-([0-9]{5}|[1-9][0-9]{5,})$`（`domain/ids.CANONICAL_ID_RE` と同じ）。`links`、`tags`：空白だけでない文字列の配列。
			  - `subtasks`：`{id, title, status, created_at, updated_at, resolution}`。`id` は `<親の id>.<1以上の数>` で重ならない。`status` は `open`、`done`、`cancelled`。閉じたものは `resolution` があり、開いたものは null。
			  - `history`：`{at, by, role, action, target, note, fields}`。`action` は Epic D-02 の11の値。`fields` は文字列の配列。
			- エージェントの必須の欄が欠けたときは、`Problem` に加えて欄の名前を `missing` に集める（`todo add` の `details.missing`。Epic R-03 の受け入れ）。
			- ID：`new_id(taken, choose)`。`choose` は乱数の源（既定 `secrets.choice`、テストで固定）。20回続けて重なれば `TODO_ID_EXHAUSTED`。入力の ID は小文字にして受ける（サブタスクの `.n` も）。
			- 状態の移り変わり（関数 `transition(record, action, …) -> record` が新しい `dict` を返す）：
			  - `done`、`cancel`：`open`／`snoozed` から。閉じた記録には `TODO_STATE_INVALID`。開いたサブタスクがあれば `TODO_SUBTASKS_OPEN`、`--include-subtasks` なら同じ状態で閉じ、サブタスクごとに `subtask_done`／`subtask_cancelled` の経緯を足す。
			  - `snooze`：`open`／`snoozed` の親から（延期し直してよい）。サブタスクは `TODO_INVALID`。
			  - `reopen`：`done`／`cancelled` から。`resolution` と `snooze_until` を null にし、`status` を `open` に。期限は `--due` があれば書き換える。サブタスクの開き直しは、親が閉じていれば `TODO_PARENT_CLOSED`。
			  - `update`：どの状態でも欄を直せる。`history` の `updated` の `fields` に、変えた欄の名前を並べる。変わらなければ書かない（結果は `unchanged`）。
			  - 状態を変えるたびに `updated_at` を今にし、`snoozed` から出るときは `snooze_until` を null にする。
			"""
		satisfies: ["R-03", "R-04", "F-01"]
	}
	"D-02": {
		title: "期限、派生の状態、並び、件数（`domain/todo_model.py`）"
		text: """
			Epic D-08、D-09 のとおりの純粋な関数。今の時刻は引数で渡す。

			- `parse_when(text, now, tz)`：`<数>m|h|d`（1以上、30日まで）は今からの時間、`YYYY-MM-DD` は `tz` での 23:59:59、時間帯つきの ISO 8601（`Z` か `+09:00`）はそのまま。UTC の `YYYY-MM-DDTHH:MM:SSZ` に直す。読めない、時間帯がない、今より前なら `TODO_INVALID`。`tz` はこの PC の時間帯（`datetime.now().astimezone().tzinfo`）。
			- `derived(record, now)`：`effective_status`、`overdue`、`due_soon`（24時間以内）、`blocking`、`parent_closable`（サブタスクがあり、全部閉じていて、親が閉じていない）、`open_subtasks: [{id, title}]`、`subtask_counts: {open, total}`。
			- `order(records, now)`：期限切れ（期限の古い順）、期限の近いもの、止めているもの、あとで（期限の順）、延期中、閉じたもの（閉じた時刻の新しい順）。組の中は期限、作った時刻、ID の順。
			- `count_limits(records)`：リポジトリの数（閉じていない、`origin.by: agent`、`kind` が `checklist` でない親）と、親ごとの開いたサブタスクの数。
			- `matches(record, filters, now)`：`--status`（既定 `open` は `effective_status` が `open`。`all` は全部）、`--scope`（`related` か `blocks`）、`--kind`、`--tag`、`--blocking`、`--overdue`。
			"""
		satisfies: ["R-06", "R-07", "R-09"]
	}
	"D-03": {
		title: "置き場と読み書き（`infra/todo_store.py`）"
		text: """
			Epic D-01、D-06 のとおり。

			- `TodoStore(catalog)`：`todos/`、`todos/settings.json`、`todos/<YYYY-MM>/<ID>.json` の道。
			- `scan()`：`todos/` の下の、`^[0-9]{4}-(0[1-9]|1[0-2])$` の名前のディレクトリの中のファイルを分ける。記録（`^t-[0-9a-hjkmnp-tv-z]{4}\\.json$`）、衝突の写し（名前に `.conflict-` を含む。`todos/` の直下の `settings.conflict-*.json` も）、黙って飛ばすもの（`.` で始まる、`is_os_junk`）、知らないもの（そのほか。`todos/` の直下の `settings.json` 以外のファイルと、年月の形でないディレクトリも）。`todos/` がなければ全部が空。
			- `read_all()`：各記録を `read_regular_file` で読み、JSON の object なら `(path, snapshot, record)`、読めない・JSON でない・object でないものは `invalid` に理由つきで分ける。1つの失敗がほかを止めない。ロックは取らない。
			- `find(todo_id)`：ID（サブタスクなら親の ID）の記録の道。2つの年月にあれば `TODO_ID_AMBIGUOUS`（`details.paths`）、なければ `TODO_NOT_FOUND`。
			- `write_new(path, record)`：`create_missing_parents` で年月のディレクトリを作り、`publish_file(path, payload)`。`write_replace(path, record, expected)`：ロックの中で読んだ `FileSnapshot` を `expected` に渡す。一時のファイルの名前は `.<ID>.json.<乱数>.tmp`（`.` で始まるので記録として読まれない）。中身は `json.dumps(record, ensure_ascii=False, indent=2) + "\\n"`、鍵の順は記録の順のまま。
			"""
		satisfies: ["R-01", "F-01", "F-02"]
	}
	"D-04": {
		title: "書くコマンドの順番（`application/todo_commands.py`）"
		text: """
			Epic D-04、D-06、D-07 のとおり。`add`、`update`、`done`、`snooze`、`cancel`、`reopen` は、どれも次の順で動く。

			1. `todo_common.open_repository(context, namespace)`：`require_linked`（F-03）、リポジトリ（`repository_for_checkout`。読めなければ null）、設定（D-06）、構造のスナップショット（`SnapshotStore(...).load()`、ネットワークに触れない）。
			2. 入力の読み取りと確かめ（`TODO_INVALID`。`--body-file` の読み取り、`--due` の解釈、Scope の ID の形と0埋め、`--option KEY=TEXT`）。
			3. `catalog_changes(catalog, command="todo <動詞>", origin="command", timeout=CATALOG_LOCK_TIMEOUT)` の中で、対象の記録を読み直し（新規なら全部の ID を読んで採番）、壊れていれば `TODO_RECORD_INVALID`、版が違えば `TODO_SCHEMA_UNSUPPORTED`、移り変わりを作り、`validate` に通す。通らなければ `TODO_INVALID`（`details.problems`、`details.missing`）。
			4. `--dry-run` なら書かずに、書く予定の記録を `planned` で返す（ロックの外に出てから）。
			5. 1つのファイルだけを書き、`changes.add(相対の道)`。`publish_file` が途中で失敗したら、`TODO_WRITE_INCOMPLETE`（`partial`、終了コード6、効果は `unknown` か `succeeded`）。
			6. 書いた後に件数を数え（D-02）、`add`（サブタスクを含む）と `reopen` で目安を超えれば警告 `TODO_LIMIT_EXCEEDED`。Scope の ID がスナップショットになければ警告 `TODO_SCOPE_UNKNOWN`（スナップショットがなければ `details.reason: snapshot_missing`）。
			- `--by`（`agent`／`human`、既定 `human`）と `--role` は、`add` では `origin` に、すべての書くコマンドでは `history` と `resolution` の `by`／`role` になる。
			- `add`：`--parent` があればサブタスク（`--title` だけを使い、ほかの記録の欄の引数があれば `TODO_INVALID`）。`--item` は束（`--kind checklist` のときだけ）。`--kind` の既定は人なら `todo`、エージェントは必須。
			- 結果は D-07 の1件の形。`done` で最後のサブタスクを閉じたときは `parent_closable: true` と次の1手 `spec-dock todo done <親>`。
			- 時刻は `todo_common.utc_now()`（テストで差し替える）。
			"""
		satisfies: ["R-01", "R-03", "R-04", "R-05", "R-06", "R-07", "R-09", "F-01", "F-03"]
	}
	"D-05": {
		title: "読むコマンド（`application/todo_list.py`）"
		text: """
			- `todo list`：`open_repository` の後、`read_all` と `scan`、`validate` に通った記録だけを `matches` で絞り、`order` で並べ、D-07 の `specdock.todo-list/v1`（`mode: repository`）を返す。形の正しくない記録と版の違う記録は `invalid_files` に道を並べ、警告 `TODO_RECORD_INVALID`（次の1手 `spec-dock todo check`）。衝突の写しは `conflict_copies` と警告 `TODO_CONFLICT_COPY`（元のファイルと写しの道、次の1手：中身を元のファイルに統合してから写しを消す）。
			- `todo show ID`：その ID（サブタスクの ID なら親）の記録。形が正しくなければ `TODO_RECORD_INVALID`（3）。その記録の衝突の写しがあれば `TODO_CONFLICT_COPY`。テキストの出力に「残り n 件：…」。
			- 読むコマンドはロックを取らず、何も書かない。
			"""
		satisfies: ["R-01", "R-04", "R-05", "R-06", "R-09", "F-02"]
	}
	"D-06": {
		title: "3段の設定（`domain/todo_settings.py`、`infra/user_config.py`、`application/todo_settings.py`）"
		text: """
			Epic D-10 のとおり。

			- `domain/todo_settings.py`：`DEFAULTS = {parent_limit: 20, subtask_limit: 30, default_due: "4h"}`、`check_values(mapping) -> reason | None`（知らない鍵は無視、整数は bool を除く1〜10000、`default_due` は30日まで）、`resolve(layers) -> Effective`（鍵ごとの `value` と `source`）。
			- `infra/user_config.py`：`user_config_path(environ)`（`XDG_CONFIG_HOME` が絶対の道ならそこ、ほかは `~/.config`）の `spec-dock/config.json` を読むだけ。なければ `missing`、読めない・JSON でない・`schema` が `specdock.config/v1` でない・`todo` が object でない・値が違えば `invalid` と理由。`todo` の節がなければ値なしの `ok`。
			- リポジトリの段：`todos/settings.json` を `TodoStore` が読み、`schema` が `specdock.todo-settings/v1` のもの。同じ規則。
			- `invalid` の段は丸ごと飛ばし、警告 `TODO_SETTINGS_INVALID`（`path`、`layer`、`reason`）をすべての `todo` のコマンドで出す。
			- `todo settings`（チェックアウトがなくても動く道）：`resolve_context` が成り立たなければ（Git の worktree でない、宣言がない）チェックアウトの外として、リポジトリの段を `not_applicable` にする。版3の宣言は今までどおり `CANONICAL_NOT_MIGRATED`。版4のチェックアウトの中では `require_linked` を通す（F-03）。結果は `{values: {<鍵>: {value, source}}, layers: [{layer, path, state, reason}]}`。
			"""
		satisfies: ["R-08", "F-03"]
	}
	"D-07": {
		title: "JSON の形とテキスト（`presentation/todo_document.py`）"
		text: """
			Epic D-13 のとおり。

			- `todo_view(record, *, now, repository, path) -> {todo, derived, ref, repository, path, warnings_detail}`。`ref` は `<owner>/<name>/t-xxxx`（github.com 以外は `<host>/<owner>/<name>/t-xxxx`）、リポジトリが分からなければ null。`path` は `todos/<YYYY-MM>/<ID>.json`（カタログからの相対）。`warnings_detail` は、その結果の警告の `{code, message, details}` の写し。
			- `todo_list_document(...)`：`schema`、`generated_at`、`mode: "repository"`、`filters`、`repositories`（1行。`repository`、`catalog`、`main_checkout`、`hidden`（`read_hidden`。リポジトリが分からなければ false）、`status: "ok"`、`problem: null`、`counts: {open, blocking, overdue, snoozed, agent_parents: {count, limit, source}}`、`invalid_files`、`conflict_copies`）、`items: [{ref, repository, path, derived, todo}]`。
			- テキスト：一覧は1件1行（ID、印（`!期限切れ`、`期限間近`、`止める`、`延期中`、`済`、`取消`）、期限をこの PC の時刻で、題名）、`show` は欄を数行とサブタスクと「残り n 件：…」、`check` は要約の1行と誤りごとの1行、`settings` は鍵ごとの1行。`render_text` に `todo ` の分岐を足す。
			- `FamilyData("todo", …)` の `data.result` に入れる。
			"""
		satisfies: ["R-05", "R-06", "R-09", "R-11"]
	}
	"D-08": {
		title: "CUE の型と `todo check`（`cue/todo/v1/todo.cue`、`infra/cue_tool.py`、`infra/cue_schemas.py`、`application/todo_check.py`）"
		text: """
			Epic D-05 のとおり。ただし `cue vet` の呼び方を変える（requirement.cue の decisions）。

			- `cue/todo/v1/todo.cue`：`package todo`。`#Todo`、`#Subtask`、`#Resolution`、`#History` と `#Records: [string]: #Todo`。D-01 の規則を同じに書き、すべての構造を `...` で開く。欄の間の規則は `if` と内側の `_` の欄（例 `_recommendation_known`）で書く。
			- `infra/cue_schemas.todo_schema_path()`：パッケージの `cue/todo/v1/todo.cue`。`shipped_schemas()` は `specdock/v<N>` だけなので `todo` が出ない（テストで確かめる）。
			- `CueTool.vet(schema_file, data, *, expression, cwd, timeout)`：`cue vet -c -d <expression> <schema_file> json: -` に、`data`（JSON の文字列）を標準入力で渡す。終了コードと標準エラーを返す。
			- `todo check`：Python の検査の後に `cue vet`。Python の検査のコード：誤りは、読めない・JSON の object でない・`validate` に通らない記録（`TODO_RECORD_INVALID`、欄ごと）、名前と `id` と年月（`created_at` の年月）が合わない記録（`TODO_RECORD_MISPLACED`）、年月の違う同じ ID（`TODO_ID_DUPLICATE`）、版の違う記録（`TODO_SCHEMA_UNSUPPORTED`）。警告は、衝突の写し（`TODO_CONFLICT_COPY`）、記録でないファイル（`TODO_FILE_UNKNOWN`）、壊れた設定（`TODO_SETTINGS_INVALID`。ほかのコマンドと同じく止めない）。`cue` があれば、版の合う object の記録全部を `{<カタログからの相対の道>: 記録}` の1つの JSON にして `#Records` で確かめる。誤りの道の先頭の鍵をファイルに対応づけ、`source: cue` の誤り（`TODO_CUE_INVALID`）にする。`cue` がない・古ければ警告 `TODO_CUE_SKIPPED`（`next_step` に入れ方）、時間切れか失敗（終了コード1でない、または誤りの道がどのファイルにも対応しない）なら警告 `TODO_CUE_FAILED`。
			- 誤りがあれば `failed`、終了コード7、`TODO_CHECK_FAILED`。結果は `{valid, checked_files, errors: [{code, file, field, message, source}], warnings, cue: {status, version}}`。記録がなければ「記録がない」で成功。
			- 見本：`tests/fixtures/todo/valid/*.json` と `invalid/*.json`。1つのテストが、全部を Python の検査と `cue vet` の両方にかけ、ファイルごとの通る・通らないが一致し、`valid` は通り `invalid` は通らないことを確かめる（`cue` は CI にある。ない PC では `tests/support/cue.py` のとおりテストが失敗して入れ方を示す）。
			"""
		satisfies: ["R-02"]
	}
	"D-09": {
		title: "Scope との結び付き（印だけ）"
		text: """
			Epic D-11 のうち、この Issue の分（`scope_marks` と画面は iss-00554）。

			- `todo add --scope ID… --blocks ID…`、`todo update --add-scope/--remove-scope/--add-blocks/--remove-blocks ID`。`parse_scope_id` で確かめて `scope_id` で0埋めの形にする。形が違えば `TODO_INVALID`。重ねて足さない。
			- あるかどうかはスナップショットの `find` で確かめ、ないとき、スナップショットがないときは警告 `TODO_SCOPE_UNKNOWN` で書く。
			- `evaluate_readiness`、`dependency`、`work start` のコードは変えない。テストで、`runtime/domain/canonical_readiness.py` と readiness を組み立てる application のモジュールの中に `todo` の参照がないことと、タスクがあっても `dependency check` の結果が同じことを確かめる。
			"""
		satisfies: ["R-09"]
	}
	"D-10": {
		title: "コマンドの家族の登録とヘルプ（`cli/catalog.py`、`commands/canonical_dispatch.py`）"
		text: """
			Epic D-12 のうち、集約の引数を除いたもの。

			- `LEAF_PATHS` に `todo add`、`todo list`、`todo show`、`todo update`、`todo done`、`todo snooze`、`todo cancel`、`todo reopen`、`todo check`、`todo settings` を足す（71）。`MUTATING_LEAF_PATHS` に書く6つを足す（`--yes` を受けるが確かめは求めない）。
			- `LEAF_ARGUMENTS`：Epic D-12 の表のとおり（`--all-repositories`、`--repository`、`REF` を除く）。繰り返す引数は `action="append"`。書くコマンドに `--by {agent,human}` と `--role`。
			- `HELP_EFFECTS`、`HELP_PRECONDITIONS`、`_READS_BY_ROOT["todo"]`、`_DOES_NOT_BY_ROOT["todo"]`、`_JSON_DATA_BY_ROOT["todo"]`、例。
			- `CANONICAL_HANDLERS` に `settings` 以外の9つ、`REPOSITORY_INDEPENDENT_HANDLERS` に `todo settings`（いつもこの道で答え、None を返さない）。
			- エラーは `CanonicalCommandError`（コード、終了コード、`details`、次の1手）で投げ、今の `dispatch` が描く。
			"""
		satisfies: ["R-11", "F-03"]
	}
	"D-11": {
		title: "カタログの検査が `todos/` を取り違えないことの確かめ"
		text:  "Epic D-18 のとおり。コードは変えず、`tests/cli_runtime/` に、`todos/2026-11/t-7k3m.json` と `todos/settings.json` のあるカタログで `workspace validate` と `scope list` と `scope check` を確かめるテストを足す。"
		satisfies: ["R-10"]
	}
	"D-12": {
		title: "文書と inventory"
		text: """
			- 提供側の `src/spec_dock/assets/spec_dock/docs/reference_cli.md`：C62〜C71 の10の行、`specdock.todo/v1` と `specdock.todo-list/v1`（`mode: repository`。`mode: all_repositories` は iss-00550 が足すと書く）の節、エラーのコードと終了コード、設定の3段の形。冒頭の「公開61 leaf」を71に。
			- `docs/README.md` の「全61 leaf」、`cli-redesign-guide.html` の「全61コマンド」と表（10の行）、リポジトリの `README.md`（数を書いていれば）を直す。コマンドの数を縛るテスト（61 → 71）を直す。
			- `static-inventory.json` の変えた行の `sha256` を新しい中身で計り直し、前の値を `known_old_sha256` に足す。dogfood の写し（`spec-dock/docs/…`）に同じ中身を写す。
			- `canonical.md`、`docs/todo.md`、スキルは iss-00551、`migration.md` は iss-00553 なので変えない。
			"""
		satisfies: ["R-11"]
	}
}

compatibility: """
	- 足すだけ：公開のコマンドが10増える（61 → 71）。カタログに `todos/` ができる（最初の `todo add` が作る）。利用者の設定のファイル `$XDG_CONFIG_HOME/spec-dock/config.json` を読む（作らない）。
	- 公開の契約：`specdock.todo/v1`（記録）、`specdock.todo-list/v1`（`mode: repository`）、`specdock.config/v1` の `todo` の節、`specdock.todo-settings/v1`。
	- 変えない：カタログの形式、`workspace.json` の版、構造のスナップショット、`evaluate_readiness`、ほかのコマンドの契約、`dashboard summary`。
	"""

risks: [
	"CUE と Python の規則が細部で食い違う（例：暦として正しくない時刻、改行の扱い）。見本を増やして同じテストで縛り、食い違えばテストが落ちる",
	"`cue vet` の誤りの道の形が `cue` の版で変わるおそれ。対応づけは先頭の引用した鍵だけにし、対応しないときは `TODO_CUE_FAILED` の警告にして Python の結果で決める",
	"`--by` の既定が人なので、エージェントが付け忘れると必須の欄の検査をすり抜ける（Epic のリスク。スキルは iss-00551）",
]
