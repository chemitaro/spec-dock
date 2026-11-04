package spec

// 設計（Epic）。型 specdock/v1。
// コードの場所は 2026-11-04 の main（0.6.0、ae8c72456）で確かめた。
// 経緯と材料は `.workbench/README.md`、`.workbench/analysis-human-task-storage-20261104.md`、`.workbench/proposal-round3-20261104.md`。

goals: [
	"人のタスクを、各リポジトリのカタログの `todos/` に1件1つの JSON のファイルで置き、GitHub に触れずに CLI だけで登録・一覧・完了できるようにする",
	"書く前の Python の検査と、`cue vet` による型の検査の2段で、カタログに正しい形の記録だけが残るようにし、2つの型を同じ見本で縛る",
	"件数の目安と既定の期限を、初めの値 < 利用者の設定 < リポジトリの設定 の3段で決め、効いている値と出どころを示せるようにする",
	"登録簿から全リポジトリのタスクを集め、版つきの JSON（`specdock.todo-list/v1`）で外部の道具にも渡し、`dashboard summary` とダッシュボードの画面が同じ数え方を使うようにする",
	"人のタスクは印だけを示し、Scope の状態、`dependency check`、`work start` の判定（`evaluate_readiness`）を変えない",
	"CLI と記録の形を epic-00427 から切り離して先に出し、画面だけを epic-00427 の後に足す",
]

current: """
	- カタログ（`spec-dock/canonical` の worktree）は、どの worktree からも `spec-dock/initiatives/` で見え、定期の同期が保存と push をする。Scope のディレクトリは `<catalog>/<区切り>/<ID>/` だけで、`runtime/infra/catalog_tree.py` の `CatalogTree.misplaced()` は、ID の形の名前（`init-`、`epic-`、`iss-` で始まる）と区切りの形の名前だけを調べる。`todos` という名前は、どちらにも当たらない。
	- カタログに書くコマンドは、`application/canonical_catalog.catalog_changes`（`infra/catalog_lock.CatalogLock` の flock を最大10秒待ち、`CANONICAL_LOCK_BUSY`。形式の版を書く前に確かめ、同期のための changeset を残す）の中で、`infra/file_publication.publish_file`（記号のリンクを断り、一時のファイルから置き換える。`expected` で書く直前の中身の食い違いを断る）を使って書く（`canonical_artifact_write.py`）。リンクと形の確かめは `canonical_catalog.require_linked`（`CANONICAL_NOT_LINKED`）。
	- 同期は、`*.conflict-<PC>-<時刻>` の写しを残し（`domain/canonical_sync_rules.conflict_copy_name`）、20件を超える削除と、秘密情報らしい中身と、10MB を超えるファイルを保留にする。`workspace validate` は衝突の写しを `CANONICAL_CONFLICT_COPY` の警告として示す。
	- `cue` は `infra/cue_tool.py`（`locate_cue`、`CueTool.export`、`parse_cue_errors`）で呼ぶ。Scope の型は `src/spec_dock/cue/v1/*.cue`（`package spec`）で、`infra/cue_schemas.schema_directory` が `specdock/v<N>` だけを `cue/v<N>/` に写す。
	- 登録簿 `<state_root>/canonical-registry.json`（`infra/canonical_registry.read_registry`）に、このPCで `canonical link` した全カタログが載る（`catalog`、`main_checkout`、`repository`。`repository` は null のことがあり、同じリポジトリの2つのクローンは2行になる）。ただし `canonical link --no-schedule` でリンクしたカタログは、登録簿に載らない（定期の同期の対象でもない）。
	- 利用者の設定のファイルはない（`workspace.json` は契約のファイル）。`XDG_CONFIG_HOME` は、常駐の設定のファイルの置き場を決めるのにだけ使っている（`infra/canonical_scheduling.py`、`infra/dashboard_service.py`）。
	- `dashboard summary` と、サーバーの `/api/v1/r/<repo>/summary` は、どちらも `presentation/dashboard_summary.summary_document` で `specdock.dashboard-summary/v1` を作る（項目を足すのは版を変えずにできる）。今はユーザーごとの状態の置き場のファイルだけを読む。
	- ダッシュボードのサーバー（`application/dashboard_http.py`、`dashboard_site.py`）は、画面の道 `/`、`/r/<repo>/{graph,board,timeline,scopes/<ID>}` と、API `/api/v1/repositories`、`/api/v1/r/<repo>/{summary,structure,scopes/<ID>,revision}` を持つ。画面は `src/spec_dock/assets/dashboard/`（`views/{overview,graph,board,timeline,scope}.js`）。`revision` は、スナップショットとカタログの同期の状態のファイルの時刻から作る。
	- 公開のコマンドは61（`runtime/cli/catalog.py` の `LEAF_PATHS`）。チェックアウトがなくても動くコマンドは `commands/canonical_dispatch.REPOSITORY_INDEPENDENT_HANDLERS` に置く（`dashboard summary REPOSITORY` の `summarize_named`）。
	"""

target: """
	- `spec-dock todo add|list|show|update|done|snooze|cancel|reopen|check|settings` の10のコマンドが、そのリポジトリのカタログの `todos/` だけを読み書きする（GitHub に要求を送らない）。`todo list --all-repositories` は登録簿の全カタログを集める。
	- `dashboard summary` の要約に、人のタスクの数（`todos`）が足される。
	- 画面の版（epic-00427 の後）で、ダッシュボードに、全リポジトリと、リポジトリごとの人のタスクの画面、1件の詳しい画面があり、構造の図・ボード・Scope の詳しい画面・横断の概況に、人が止めている印と数が出る。
	- 配布するスキルに、エージェントが人のタスクを登録・完了する規則がある。spec-dock 自身で使い始めている。
	"""

design: {
	"D-01": {
		title: "置き場：カタログの `todos/` と、1件1つのファイル"
		text: """
			- 記録：`<catalog>/todos/<YYYY-MM>/<ID>.json`。`YYYY-MM` は作った時刻（UTC）の年月。どの worktree からも `spec-dock/initiatives/todos/…` で見え、ふつうのファイルとして定期の同期が保存と push をする。新しい同期の手順は足さない。
			- 閉じても、状態を変えるだけで、ファイルを動かさず、消さない（動かすと削除と追加になり、20件を超えると同期の保留に触れる）。v1 には記録を消すコマンドを作らない。
			- リポジトリの設定：`<catalog>/todos/settings.json`（D-10）。
			- Scope に結び付くタスクも、Scope のディレクトリには置かず、ID で結び付ける（D-11）。Scope の削除や `work finish` と絡まず、探す場所が1つで済む。
			- 記録のファイルは `todos/<YYYY-MM>/` の中の、名前が `^t-[0-9a-hjkmnp-tv-z]{4}\\.json$` のものだけ。ほかのファイルは記録として読まない。その扱い：
			  - `todos/settings.json`：リポジトリの設定（D-10）。記録でないファイルとして警告しない。
			  - `.` で始まる名前（`publish_file` の一時のファイルなど）と、OS が置くファイル（`canonical_sync_rules.is_os_junk`）：黙って飛ばす。
			  - 衝突の写し（`*.conflict-*`）：`todo list`、`todo show`、`todo check` が警告 `TODO_CONFLICT_COPY` を出す（D-06）。
			  - そのほか（手で置いたもの、名前の形が違うもの）：`todo check` だけが警告 `TODO_FILE_UNKNOWN` を出す。
			  - どれも、そのリポジトリのほかの記録の読み取りを止めない（D-14）。
			- GitHub には書かず、問い合わせもしない。Scope の ID の確かめも、保存したスナップショット（`SnapshotStore.load()`、ネットワークに触れない）だけで行う（D-11）。
			- 層：`runtime/infra/todo_store.py`（道の組み立て、全記録の読み取り、ID の一覧、書き込み）。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "記録の形（`specdock.todo/v1`）"
		text: """
			1件の JSON。鍵は snake_case、時刻は UTC の `YYYY-MM-DDTHH:MM:SSZ`。

			| 欄 | 必須 | 中身 |
			|---|---|---|
			| `schema` | ○ | `"specdock.todo/v1"` |
			| `id` | ○ | `t-` と4文字（D-03） |
			| `title` | ○ | 1行の、空白だけでない文字列（200文字まで） |
			| `kind` | ○ | `decide`、`check`、`operate`、`act`、`todo`、`checklist`。`todo` は人が登録したものだけ |
			| `status` | ○ | `open`、`snoozed`、`done`、`cancelled` |
			| `created_at`、`updated_at` | ○ | 時刻 |
			| `origin` | ○ | `{by: "agent"\\|"human", role}`。`role` はエージェントのとき必須（例「iss-00531 の担当」「spec-dock の統括」）。session ID や端末の handle は書かない |
			| `body` | エージェントは○ | Markdown。背景と問い、手順。操作のコマンドは書いてよいが、秘密の値は書かない |
			| `options` | エージェントの `decide` は○ | `[{key, text}]`、2つ以上、`key` は重ならない |
			| `recommendation` | エージェントの `decide` は○ | `{key, reason}`。`key` は `options` のどれか |
			| `reply_to` | エージェントは○ | 答える場所（例「Orca の iss-00531 の担当」「統括のチャット」「このタスクを done にすれば足りる」） |
			| `effort` | エージェントは○ | 人がかかる時間の見込み。`^[1-9][0-9]*(m\\|h\\|d)$` |
			| `due` | ○ | 期限（D-08）。登録のときに必ず決まる |
			| `snooze_until` | `snoozed` のとき○ | 時刻 |
			| `scopes` | ○ | `{related: [ID], blocks: [ID]}`（D-11）。空でよい |
			| `links`、`tags` | ○ | 文字列の配列。空でよい |
			| `subtasks` | ○ | D-07。空でよい |
			| `resolution` | `done`、`cancelled` のとき○、ほかは null | `{at, by, role, choice, note, record}`。`choice` は `options` の `key`、`record` は本人の発言の原文の記録へのパスか URL。`cancelled` は `note`（理由）が必須 |
			| `history` | ○ | `[{at, by, role, action, target, note, fields}]`。`action` は `added`、`updated`、`done`、`snoozed`、`cancelled`、`reopened`、`subtask_added`、`subtask_done`、`subtask_cancelled`、`subtask_reopened`、`subtask_updated`。CLI が足すだけで、消さない |

			- 人が登録するもの（`origin.by: human`）は、`title` のほかに入力が要らない（ほかの必須の欄は CLI が初めの値で埋める）。
			- 型は開いている：v1 にない欄があっても誤りにせず、書き換えるときに残す（後の版で足した欄を、前の版の CLI が消さないため）。`schema` が `specdock.todo/v1` でない記録は、読まずに `TODO_SCHEMA_UNSUPPORTED` と示し、書き換えを断る。
			- 秘密情報らしい中身は、今の同期の保留（`SECRET_PATTERNS`）が保存を止める。CLI では検査しない（スキルの規則で書かせない。D-17）。
			- 層：`runtime/domain/todo_record.py`（dataclass、読み取り、形の検査、状態の移り変わり）。
			"""
		satisfies: ["R-03", "R-04"]
	}
	"D-03": {
		title: "ID の採番と、横断の名前"
		text: """
			- 形：`t-` と、Crockford の base32 の小文字の4文字（`0123456789abcdefghjkmnpqrstvwxyz`。`i`、`l`、`o`、`u` を除く。約100万通り）。`secrets` で作り、カタログのロックの中で `todos/*/t-*.json` の全部の名前（閉じたものも含む）と重ならないことを確かめる。20回続けて重なれば `TODO_ID_EXHAUSTED`（終了コード3）で止まる（実際には起きない数）。
			- 入力は大文字と小文字を区別しない（`T-7K3M` は `t-7k3m`）。
			- 別の PC がオフラインで同じ ID を作ったときは、同じ年月なら同じ道になり、同期が衝突の写しを残す（F-02、D-06）。年月が違えば2つのファイルになり、`todo check` が `TODO_ID_DUPLICATE`（誤り）で示し、その ID を指すコマンドは `TODO_ID_AMBIGUOUS`（終了コード3）で止まって、2つの道を示す。
			- 横断の名前（`ref`）：`<owner>/<name>/t-xxxx`（github.com 以外は `<host>/<owner>/<name>/t-xxxx`）。登録簿の `repository` が分からないカタログでは `ref` は null。
			- サブタスクの ID は親の ID に `.1`、`.2`…（D-07）。
			- 層：`runtime/domain/todo_record.py`（形と作り方。乱数の源は引数で渡し、テストで固定する）。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "書く前の検査（Python の型）と、何も書かずに止まること"
		text: """
			- すべての書くコマンドは、(1) リンクとカタログの確かめ（D-12）、(2) 入力の読み取り、(3) カタログのロックの中で今のファイルを読み、変えた後の記録を作り、(4) `todo_record.validate` で形を確かめ、(5) 通ったときだけ書く。どこで止まっても、何も書かない（F-01）。
			- `validate` は、型（D-02 の全部の欄と値の形）、欄の間の決まり（`status` と `resolution`・`snooze_until` の組、エージェントの必須の欄、`decide` の `options` と `recommendation`、`kind: todo` は人だけ、サブタスクの ID が親の ID で始まる、`scopes` の ID の形）を調べ、問題ごとに `{field, message}` を返す。
			- 入力の誤りは `TODO_INVALID`（終了コード2）。`details.problems` に欄の名前と理由を並べ、エージェントの必須の欄が欠けたときは `details.missing` に欄の名前（例 `body`、`reply_to`、`effort`）を並べる（R-03 の受け入れ）。
			- 読んだファイルが壊れている、または形に合わないときは、書き換えを断り（`TODO_RECORD_INVALID`、終了コード3）、`todo check` で直す場所を示す。
			- 層：検査は `domain/todo_record.py`、組み立ては `application/todo_commands.py`。
			"""
		satisfies: ["R-02", "R-03", "F-01"]
	}
	"D-05": {
		title: "CUE の型（`#Todo`）と `todo check`"
		text: """
			- 型の定義：`src/spec_dock/cue/todo/v1/todo.cue`（`package todo`、`#Todo` と `#Subtask`、開いた構造 `...`）。D-02 の形と欄の間の決まりを、D-04 と同じに書く。パッケージのデータ（`cue/**/*.cue`）として wheel に入る。Scope の型（`cue/v1/`、`package spec`）とは別のディレクトリなので、Scope の評価に混ざらない（`schema_directory` は `specdock/v<N>` だけを写す。`shipped_schemas()` に `todo` が出ないことをテストで確かめる）。置き場は `infra/cue_schemas.todo_schema_path()` で返す。
			- `infra/cue_tool.CueTool` に `vet(files, *, schema, expression, cwd, timeout)` を足す：全部の記録を `{カタログからの相対の道: 記録}` の1つの JSON にまとめて標準入力で渡し、`cue vet -c -d '#Records' <todo.cue> -`（`#Records: [string]: #Todo`）で確かめる。誤りは、誤りの道の先頭の鍵でファイルに対応づける（2026-11-04 改め。cue v0.17.1 では複数のデータファイルを渡すと最初に誤ったファイルの誤りしか出ず、欄の間の規則の誤りは位置が JSON のファイルを指さないため。#549 の確かめ）。
			- `spec-dock todo check [--json]`：そのリポジトリの `todos/` の全部を調べる。
			  1. Python の検査（いつも）：各記録の `validate`、名前と `id` と年月の一致、ID の重なり（`TODO_ID_DUPLICATE`）、`settings.json` の形（D-10）、衝突の写し（`TODO_CONFLICT_COPY`、警告）、記録でないファイル（`TODO_FILE_UNKNOWN`、警告）、`schema` の版が違う記録（`TODO_SCHEMA_UNSUPPORTED`、誤り）。
			  2. `cue vet`（`cue` v0.17.1 以上があるとき）：全部の記録を `#Todo` で一度に確かめる。`cue` がない、古いときは、警告 `TODO_CUE_SKIPPED`（`next_step` に入れ方）を出し、Python の検査だけで結果を決める（R-02）。`cue` が時間切れか失敗したときは、警告 `TODO_CUE_FAILED` で同じく扱う。
			  3. 誤りがあれば終了コード7（`TODO_CHECK_FAILED`）。誤りごとに、ファイル、欄、理由、出どころ（`python` か `cue`）を示す。警告だけなら成功。
			- 2つの型を縛るテスト：`tests/fixtures/todo/{valid,invalid}/*.json` の同じ見本を、Python の検査と `cue vet` の両方にかけ、ファイルごとの通る・通らないが一致することを確かめる（`cue` がない CI でも Python の側は動き、`cue` の側は `cue` があるときに動く。Provider CI に `cue` があることを実装の Issue で確かめる）。
			- `workspace validate` と `scope check` は `todos/` を調べない（D-18）。
			- 層：`application/todo_check.py`、`infra/cue_tool.py`、`infra/cue_schemas.py`、`presentation/todo_document.py`（結果の形）。
			"""
		satisfies: ["R-02"]
	}
	"D-06": {
		title: "ロックと原子的な書き込み、別の PC との衝突"
		text: """
			- 書き込みは `catalog_changes(catalog, command="todo <動詞>", origin="command")` の中で行う。カタログのロック（flock、最大10秒、`CANONICAL_LOCK_BUSY`）は同期とも共有なので、同期の保存の途中に書かない。ロックの中ではネットワークに触れない。changeset に書いたファイルの道を残す。
			- 1つのコマンドの書き込みは1つのファイルだけ（親とサブタスクは同じファイル。D-07）。新しいファイルは `publish_file(path, payload)`、書き換えは、ロックの中で読んだ中身の `read_regular_file` の写しを `expected` に渡す `publish_file` で、一時のファイルから置き換える（読んだ後に変わっていれば断る）。年月のディレクトリがなければ `create_missing_parents` で作る。ダッシュボードの「見た」の記録（epic-00427 D-18）と同じく、ロックと置き換えで書くが、ロックは同期と共有するカタログのロックを使う（ユーザーごとの状態の置き場のロックではない）。
			- 読む側（`todo list`、`todo show`、ダッシュボード）はロックを取らない。置き換えで書くので、読めば必ず前か後の完全なファイルになる。
			- 別の PC で同じタスクを同時に変えたとき（F-02）：同期が `t-xxxx.conflict-<PC>-<時刻>.json` を残す。この写しは記録の名前の形に合わないので記録として読まない。`todo list`、`todo show`、`todo check` は、`todos/` の中の衝突の写しを `TODO_CONFLICT_COPY` の警告として、元のファイルと写しの道を示し、次の1手（中身を元のファイルに統合してから写しを消す。AGENTS.md の規則と同じ）を示す。`workspace validate` も今までどおり `CANONICAL_CONFLICT_COPY` を示す。CLI は自動で統合しない。
			- 層：`application/todo_commands.py`（ロックと順番）、`infra/todo_store.py`（読み書き）。
			"""
		satisfies: ["R-01", "F-01", "F-02"]
	}
	"D-07": {
		title: "サブタスクと、会話の束（`checklist`）"
		text: """
			- 形：親の記録の `subtasks: [{id, title, status, created_at, updated_at, resolution}]`。`status` は `open`、`done`、`cancelled`（延期はない）。期限は持たず、親の期限に従う。ID は親の ID に `.<番号>`。番号はそのファイルの最大の番号に1を足し、取り消したものの番号も使い直さない。経緯は親の `history` に `target` をサブタスクの ID にして残す。
			- 足す：`todo add --parent <親の ID> --title T`。孫（`--parent t-7k3m.1`）は `TODO_NESTING_TOO_DEEP`（終了コード2）で断る。閉じた親に足すときは `TODO_PARENT_CLOSED`（終了コード3）で断り、先に `todo reopen` を示す。
			- 閉じる・開き直す・直す：`todo done|cancel|reopen|update t-7k3m.2`。
			- 親は自動で閉じない。サブタスクがあり、全部が閉じたとき、`todo show` と、最後のサブタスクを閉じた `todo done` の結果に `parent_closable: true` と、親を閉じる次の1手（`spec-dock todo done <親>`）を出す（R-04）。
			- 開いたサブタスクのある親を `todo done`／`todo cancel` すると、何も書かずに `TODO_SUBTASKS_OPEN`（終了コード3）で止まり、開いたサブタスクを示す。`--include-subtasks` を付けると、開いたサブタスクを同じ状態（`done` か `cancelled`）で一緒に閉じる。
			- 会話の束（R-05）：`todo add --kind checklist --by agent --role R --title T --body … --reply-to … --effort … --item <題名> --item <題名> …` で、親と、`--item` ごとのサブタスクを1回で書く。既定の期限が付く（D-08）。`todo show <親>` の結果に、開いたサブタスクの一覧（`open_subtasks`）と、テキストの出力の「残り n 件：…」を出す。
			- 1つの親のサブタスクの数の目安は D-09。
			"""
		satisfies: ["R-04", "R-05"]
	}
	"D-08": {
		title: "期限、延期、期限切れ、並び"
		text: """
			- `--due` の書き方：`30m`、`4h`、`2d`（今からの時間）、`YYYY-MM-DD`（その日の、このPCの時間帯での 23:59:59）、時間帯つきの ISO 8601。UTC に直して書く。過去の時刻は `TODO_INVALID`。
			- 既定：`--due` がなければ、`created_at` に設定の `default_due`（初めの値 `4h`。D-10）を足す。束（`checklist`）も同じ。
			- 延期：`todo snooze <ID> --until <時刻> [--due <時刻>]`。`status` を `snoozed`、`snooze_until` を書く。親だけ（サブタスクは延期しない）。期限は `--due` がなければ変えない。
			- 読む側が決める派生の状態（`domain/todo_model.py` の純粋な関数。今の時刻は引数）：
			  - `effective_status`：`snoozed` で `snooze_until` を過ぎていれば `open`、ほかは `status` のまま。ファイルは書き換えない（読むだけのコマンドで書かないため）。
			  - `overdue`：`effective_status` が `open` で、`due` が今より前。
			  - `due_soon`：`overdue` でなく、`due` が今から24時間以内。
			  - `blocking`：閉じていなくて、`scopes.blocks` が空でない。
			- 「開いている」は、閉じていない（`open` か `snoozed`）こと。件数の目安（D-09）と要約の数（D-15）は、これを数える。
			- 並び（CLI の `todo list` と画面で同じ。`todo_model.order`）：期限切れ（期限の古い順）、期限の近いもの、止めているもの、あとで（期限の順）、延期中、閉じたもの（閉じた時刻の新しい順）。同じ組の中は、期限、作った時刻、ID の順。
			"""
		satisfies: ["R-06"]
	}
	"D-09": {
		title: "件数の警告"
		text: """
			- 数え方（`todo_model.count_limits`）：
			  - リポジトリ：開いている親のタスクのうち、`origin.by` が `agent` で、`kind` が `checklist` でないもの。人が登録したもの、束、サブタスクは数えない。
			  - サブタスク：1つの親の、開いたサブタスクの数。
			- `todo add`（サブタスクを足すときを含む）と `todo reopen` の書き込みの後に数え、目安（`parent_limit`、初めの値20。`subtask_limit`、初めの値30。D-10）を超えていれば、警告 `TODO_LIMIT_EXCEEDED`（`details`：`kind` は `repository` か `subtasks`、`count`、`limit`、`source`（効いている値の出どころ）、`next_step`）を出す。登録は成功する（終了コード0）。
			- `todo list` の結果の `repositories[].counts` にも、同じ数と目安を出す。
			"""
		satisfies: ["R-07"]
	}
	"D-10": {
		title: "3段の設定と、効いている値の表示"
		text: """
			- 鍵：`parent_limit`（1〜10000 の整数、初めの値20）、`subtask_limit`（1〜10000 の整数、初めの値30）、`default_due`（`^[1-9][0-9]*(m|h|d)$`、30日まで、初めの値 `"4h"`）。
			- 段（後のものが優先。鍵ごとに決める）：
			  1. 初めの値（`domain/todo_settings.py` の定数）。
			  2. 利用者の設定：`$XDG_CONFIG_HOME/spec-dock/config.json`（`XDG_CONFIG_HOME` が絶対の道のとき）、ほかは `~/.config/spec-dock/config.json`。SpecDock 全体の設定のファイルで、形は `{"schema": "specdock.config/v1", "todo": {<鍵>: <値>}}`。ほかの機能は、後で `todo` と並ぶ節を足す（知らない節は無視する）。
			  3. リポジトリの設定：`<catalog>/todos/settings.json`。形は `{"schema": "specdock.todo-settings/v1", <鍵>: <値>}`。そのリポジトリの全 worktree と PC で共通（同期される）。
			- どちらのファイルもなければ、初めの値を使う。ファイルが読めない、JSON でない、`schema` が違う、値の形が違うときは、そのファイル（段）を丸ごと飛ばし、警告 `TODO_SETTINGS_INVALID`（`details`：`path`、`layer`、`reason`）を出す。どの `todo` のコマンドも止まらない（R-08）。知らない鍵は無視する。
			- 書くコマンドは作らない（利用者とエージェントがファイルを書く。リポジトリの設定はカタログのふつうのファイルなので、同期が保存する）。書き方と見本は、配布する文書（D-17）に書く。
			- 表示：`spec-dock todo settings [--json]`。鍵ごとに `value` と `source`（`default`、`user`、`repository`）、段ごとに `path`、`state`（`missing`、`ok`、`invalid`、`not_applicable`）、`reason` を返す。schema 4 のチェックアウトの中では、ほかの `todo` のコマンドと同じく `require_linked` を通してリポジトリの段を読み、リンクがない・正しくないときは `CANONICAL_NOT_LINKED`（次の1手 `spec-dock canonical link`）で止まる（F-03）。チェックアウトの外では、リポジトリがないので、リポジトリの段を `not_applicable` にして、初めの値と利用者の設定を示す。`todo add` の件数の警告も、`source` を示す。
			- 層：`domain/todo_settings.py`（重ね方と値の検査）、`infra/user_config.py`（利用者の設定の道と読み取り。読むだけで、作らない）、`infra/todo_store.py`（リポジトリの設定の読み取り）、`application/todo_settings.py`。
			"""
		satisfies: ["R-08"]
	}
	"D-11": {
		title: "Scope との結び付き（印だけ）"
		text: """
			- 記録の `scopes.related`（関係する Scope）と `scopes.blocks`（このタスクが終わるまで進められない Scope）に、カノニカルの Scope の ID（`init-`、`epic-`、`iss-` と5桁）を並べる。どちらも空なら、リポジトリに付く。入力は0埋めしなくてよい（`iss-531` は `iss-00531`）。
			- CLI：`todo add --scope ID… --blocks ID…`、`todo update --add-scope/--remove-scope/--add-blocks/--remove-blocks ID`。
			- 確かめ：ID の形は `TODO_INVALID` で断る。あるかどうかは、保存したスナップショット（ネットワークに触れない）で確かめ、ないときや、スナップショットがないときは、警告 `TODO_SCOPE_UNKNOWN` を出して書く（GitHub に問い合わせないため）。
			- `todo list --scope ID`：`related` か `blocks` にその ID を持つタスク。`--blocking`：止めているものだけ。
			- `evaluate_readiness`、`dependency check`、`work start`、Scope の状態は、人のタスクを読まない（コードの中で `todos` を参照しないことをテストで確かめる。R-09 の受け入れ）。
			- 親への集計（画面と API。D-16）：Scope ごとに、`blocks` に直接その ID を持つ開いたタスクの数（`blocking`）を数える。Epic と Initiative には、自分と配下の全 Scope（スナップショットの親子）を止めている開いたタスクを、重ねずに数えた数（`blocking_with_descendants`）も出す。関係する数（`related`）も数える。純粋な関数 `domain/todo_model.scope_marks(todos, parents)` に置き、画面の Issue が使う。
			"""
		satisfies: ["R-09", "R-13"]
	}
	"D-12": {
		title: "`todo` のコマンドの家族"
		text: """
			公開のコマンドを10足す（61 → 71）。`runtime/cli/catalog.py` の `LEAF_PATHS`、`LEAF_ARGUMENTS`、`HELP_EFFECTS` などと、`commands/canonical_dispatch.py` に足し、コマンドの数を縛るテストと文書（`reference_cli.md`、README、`cli-redesign-guide.html`）を直す。名前の `todo` は暫定の決定（2026-11-04）のとおり。

			| コマンド | 働き |
			|---|---|
			| `todo add --title T [--kind K] [--by agent\\|human] [--role R] [--body TEXT\\|--body-file F] [--option KEY=TEXT]… [--recommend KEY --reason TEXT] [--reply-to TEXT] [--effort 10m] [--due WHEN] [--scope ID]… [--blocks ID]… [--link URL]… [--tag T]… [--parent ID] [--item TITLE]…` | 登録。`--by` の既定は `human`、`--kind` の既定は人なら `todo`（エージェントは必須）。`--parent` でサブタスク、`--item` で束のサブタスク（D-07） |
			| `todo list [--status open\\|snoozed\\|done\\|cancelled\\|all] [--scope ID] [--kind K] [--tag T] [--blocking] [--overdue] [--all-repositories] [--repository R]…` | 一覧（`specdock.todo-list/v1`。D-13）。`--status` の既定は `open`（`effective_status` が `open` のもの。延期中は隠す）。`--repository` は登録簿のリポジトリで絞る（`--all-repositories` を含意） |
			| `todo show ID\\|REF` | 1件（サブタスク、`parent_closable`、`open_subtasks`、衝突の写し）。`REF`（`owner/name/t-xxxx`）なら登録簿から読む |
			| `todo update ID [--title] [--body\\|--body-file] [--kind] [--due] [--reply-to] [--effort] [--option]… [--recommend --reason] [--add-/--remove-scope] [--add-/--remove-blocks] [--add-/--remove-tag] [--add-/--remove-link] [--note]` | 欄を直す。`history` に `updated` と変えた欄の名前を残す |
			| `todo done ID [--choice KEY] [--note TEXT] [--record PATH\\|URL] [--by] [--role] [--include-subtasks]` | 完了。`resolution` と `history` を書く |
			| `todo snooze ID --until WHEN [--due WHEN] [--note]` | 延期（D-08） |
			| `todo cancel ID --reason TEXT [--include-subtasks]` | 取り消し |
			| `todo reopen ID [--due WHEN] [--note]` | 開き直す。`resolution` を null にし（前の答えは `history` に残る）、`status` を `open` にする |
			| `todo check` | 検査（D-05） |
			| `todo settings` | 効いている値と出どころ（D-10） |

			- 書くコマンドは、そのチェックアウト（か `--project`）のリポジトリのカタログだけに書く。ほかのリポジトリのタスクを書くときは、そのリポジトリのチェックアウトで実行する。書くコマンドの `--by`／`--role` は、`history` と `resolution` の `by`／`role` になる。
			- チェックアウトのいる道（`canonical_dispatch.CANONICAL_HANDLERS`）：`add`、`update`、`done`、`snooze`、`cancel`、`reopen`、`check`、`list`（`--all-repositories`／`--repository` なし）、`show ID`。チェックアウトがなくても動く道（`REPOSITORY_INDEPENDENT_HANDLERS`）：`list --all-repositories`／`--repository`、`show REF`、`settings`（いつもこの道で受け、チェックアウトの中なら `require_linked` を通してリポジトリの段を読む。リンクが正しくなければ F-03 のとおり止まる。D-10）。
			- リンクとカタログの確かめ（F-03）：チェックアウトのいるコマンドは `require_linked` を通し、リンクがない、正しくない、カタログが読めないときは、何も書かずに今の `CANONICAL_NOT_LINKED`（次の1手 `spec-dock canonical link`）で止まる。書くコマンドは `catalog_changes` の中で形式の版も確かめる（`CANONICAL_FORMAT_UNSUPPORTED`）。
			- GitHub：どの `todo` のコマンドも、構造のスナップショットの取り直しも GitHub への要求もしない（`--offline` と同じ動き。R-01 の受け入れを、`gh` の stub が呼ばれないテストで確かめる）。
			- 見つからない ID は `TODO_NOT_FOUND`、閉じたものの延期などの許されない移り変わりは `TODO_STATE_INVALID`（どちらも終了コード3）。終了コードは今の決まり（入力の誤り2、前提の不足3、検査の失敗7）に従う。`--dry-run` は、書く前の検査までを行い、書く予定の記録を返す。
			- テキストの出力は人向けの短い行（ID、印、期限をこのPCの時刻で、題名）。JSON は今の封筒（`FamilyData("todo", …)`）の `data.result` に D-13 の形を入れる。
			- 層：`cli/catalog.py`、`commands/canonical_dispatch.py`、`application/todo_commands.py`（書くコマンド）、`application/todo_list.py`（`list`、`show`、集約）、`application/todo_check.py`、`application/todo_settings.py`、`presentation/todo_document.py`（JSON とテキスト）。
			"""
		satisfies: ["R-01", "R-03", "R-04", "R-06", "R-09", "F-03"]
	}
	"D-13": {
		title: "JSON の契約（`specdock.todo/v1` と `specdock.todo-list/v1`）"
		text: """
			- `specdock.todo/v1`：記録のファイルそのもの（D-02）。CLI の1件の結果（`add`、`show`、`update`、`done`、`snooze`、`cancel`、`reopen`）の `data.result` は `{todo: <記録>, derived: {effective_status, overdue, due_soon, blocking, parent_closable, open_subtasks: [{id, title}], subtask_counts: {open, total}}, ref, repository, path, warnings_detail}`。`path` はカタログからの相対の道。
			- `specdock.todo-list/v1`（`todo list` の `data.result`）：
			  - `schema`、`generated_at`、`mode`（`repository` か `all_repositories`）、`filters`（受け取った絞り込み）。
			  - `repositories`：`[{repository, catalog, main_checkout, hidden, status, problem, counts: {open, blocking, overdue, snoozed, agent_parents: {count, limit, source}}, invalid_files, conflict_copies}]`。`status` は `ok`（記録を読めた。形の正しくないファイルや衝突の写しがあっても `ok` で、`invalid_files` と `conflict_copies` にその道を並べる）、`unreadable`（カタログか `todos/` のディレクトリそのものが読めない。`problem` に `code`、`message`、`next_step`。そのリポジトリの `items` はない）、`duplicate`（同じリポジトリの2つ目のクローン。D-14）。`hidden` はダッシュボードで隠しているか（D-14）。
			  - `items`：D-08 の並びで `[{ref, repository, path, derived, todo}]`（`derived` と `todo` は1件の結果と同じ）。
			  - チェックアウトの中の `todo list`（`mode: repository`）も同じ形で、`repositories` は、そのチェックアウトのカタログの1行（`hidden` はダッシュボードの印を読んだ値、`main_checkout` はそのクローンの main のチェックアウト）。`mode: repository` の形は記録の形と CLI の中核の Issue が作り、`mode: all_repositories`（登録簿、`duplicate`）は集約の Issue が足す。
			- 版の決まり（`specdock.dashboard-summary/v1` と同じ）：項目を足すのは版を変えずにできる。消すか意味を変えるときは版を上げる。外部の道具（個人のタスク管理、Company OS の nestboard）は、`schema` を見て読む。配布する `reference_cli.md` に契約として書く。
			- 層：`presentation/todo_document.py`（`todo_view`、`todo_list_document`）。ダッシュボードの API（D-16）も、同じ関数で作る。
			"""
		satisfies: ["R-10"]
	}
	"D-14": {
		title: "全リポジトリの集約（登録簿を読む）"
		text: """
			- `todo list --all-repositories` は、`read_registry(state_root)` の全部の行のカタログの `todos/` を、その場で読む（各カタログの worktree を直接読む。チェックアウトもサーバーもいらない。GitHub に問い合わせない）。読むのは記録と `settings.json` だけで、ロックは取らない。
			- リポジトリごとの失敗を閉じ込める：カタログがない、カタログか `todos/` のディレクトリが読めない、ときだけ、そのリポジトリを `status: unreadable` と `problem`（`next_step` は `main_checkout` での `spec-dock canonical link`）にし、ほかのリポジトリの分を返す。全体は成功（終了コード0）で、警告 `TODO_REPOSITORY_UNREADABLE` を出す（R-10、F-03）。`todos/` がまだないのは失敗ではなく、0件の `ok`。
			- ファイル単位の問題はリポジトリの失敗にしない（D-01）：形の正しくない記録や版の違う記録は `invalid_files` に、衝突の写しは `conflict_copies` に道を並べ（警告 `TODO_RECORD_INVALID`、`TODO_CONFLICT_COPY`。次の1手 `spec-dock todo check`）、そのリポジトリのほかの記録は `items` に返す。一時のファイルと OS のファイルは黙って飛ばす。
			- 登録簿そのものが読めないときは `TODO_REGISTRY_UNREADABLE`（終了コード3）。登録簿が空なら、空の一覧。
			- `repository` が null の行は、`repository: null`、`ref: null` で並べる。同じ `repository` の行が2つあれば（クローンが2つ）、`main_checkout` の道の順で最初の行を読み、2つ目は `status: duplicate` として読まない（ダッシュボードの `DASHBOARD_REPOSITORY_AMBIGUOUS` と違い、CLI では読めるほうを返す）。
			- ダッシュボードで隠したリポジトリ（`dashboard hide`）も、CLI の集約には入れ、`hidden: true` を付ける（外部の道具が全部を読めるようにする）。画面は隠したものを出さない（D-16）。
			- 件数の目安は、リポジトリごとに、そのリポジトリの設定と利用者の設定で決める。
			- `todo show <owner>/<name>/t-xxxx` も、同じ読み方で1件を返す。
			- 集まるのは、このPCの登録簿に載ったリポジトリだけ（登録簿は PC ごとにあり、`canonical link --no-schedule` でリンクしたカタログは載らない）。文書に書き、`--no-schedule` のリポジトリでは、そのチェックアウトの中の `todo list` を使うよう示す。
			- 層：`application/todo_list.py`（登録簿の行ごとの読み取りと閉じ込め）、`infra/todo_store.py`。
			"""
		satisfies: ["R-10", "F-03"]
	}
	"D-15": {
		title: "`dashboard summary` の拡張"
		text: """
			- `specdock.dashboard-summary/v1` に項目 `todos` を足す（版は変えない。epic-00427 D-05 の決まり）：`{status: "ok"|"unavailable", open, blocking, overdue, problem}`。数は D-08 の定義（開いている＝閉じていない、止めている、期限切れ）で、そのリポジトリの親のタスクを数える（サブタスクは数えない）。
			- カタログの見つけ方：`REPOSITORY` を省いてチェックアウトの中で実行したときは、そのチェックアウトのリンクが正しければ、そのカタログを読む（`--no-schedule` のリンクでも数が出る）。リンクが正しくないとき、または `REPOSITORY` を渡したときは、登録簿から、そのリポジトリの行のカタログを選ぶ（D-14 と同じ選び方）。どちらでもカタログが見つからない、読めないときは、`status: "unavailable"`、数は null、`problem` に理由と次の1手を書き、要約そのものは今までどおり成功する（人のタスクが読めなくても、構造の要約は返す）。
			- `dashboard summary` は、今のユーザーごとの状態の置き場のファイルに加えて、カタログの `todos/` も読む（手元のファイルだけで、GitHub にもサーバーにも要求を送らない点は変えない）。`HELP_EFFECTS` と `reference_cli.md` を直す。
			- サーバーの `/api/v1/r/<repo>/summary` も同じ `summary_document` で作るので、同じ数を返す。
			- 層：`application/dashboard_summary.py`（カタログを選んで読む）、`application/todo_list.py`（数えるための読み取りを共有）、`domain/todo_model.py`（数え方）、`presentation/dashboard_summary.py`（`todos` の項目とテキストの1行）。
			"""
		satisfies: ["R-11"]
	}
	"D-16": {
		title: "ダッシュボード：API と画面（見るだけ。epic-00427 の後）"
		text: """
			epic-00427 の画面の作り（D-07）と見た目の決まり（案D、`ds.css`）、見るだけ（R-04）、埋め込み（`?embed=1`）に従う。書く口（登録、完了、延期）は作らない。

			- API（`application/dashboard_http.py`、組み立ては `application/dashboard_todos.py`）：
			  - `GET /api/v1/todos`：表示中（隠していない）の全リポジトリの `specdock.todo-list/v1`（D-13 と同じ関数。`--all-repositories` と同じ閉じ込め）。
			  - `GET /api/v1/r/<repo>/todos`：1つのリポジトリの一覧。`GET /api/v1/r/<repo>/todos/<ID>`：1件（D-13 の1件の形）。
			  - `structure` と `scopes/<ID>` の応答に、Scope ごとの印（D-11 の `blocking`、`blocking_with_descendants`、`related`）と、詳しい画面のための止めている・関係するタスクの一覧（`ref`、`id`、`title`、`due`、`overdue`、`kind`）を足す（画面のための形で、契約にしない）。
			  - `revision` に、`todos/` と年月のディレクトリと `settings.json` の時刻を足し、CLI で書いたタスクが5秒ごとの更新で画面に出るようにする。横断の画面は全リポジトリの `revision` を合わせる。
			  - サーバーは、リポジトリごとに `todos/` の時刻で読み取りを覚え、変わったときだけ読み直す。1つのリポジトリの失敗は、そのリポジトリの分にだけ返す。
			- 画面（`src/spec_dock/assets/dashboard/views/todos.{js,css}` と、既存の view の小さな変更）：
			  - 全リポジトリの人のタスク `/todos`（横断の概況と同じ層。R-03 の例外）、リポジトリごと `/r/<repo>/todos`、1件 `/r/<repo>/todos/<ID>`。上の帯から入れる。道は `?embed=1` を引き継ぐ。
			  - 並び：D-08 の並び（期限切れ、期限の近いもの、止めているもの、あとで）。延期中と閉じたものは切り替えで出す。リポジトリ、タグ、種類で絞る（絞り込みは URL に持つ）。
			  - 期限切れは、先頭に、色（danger）、記号、言葉（「期限切れ」と経過の時間）の3つで示す（epic-00427 R-11 の決まり）。
			  - 1件の画面：題名、種類、状態、期限、依頼者、本文（Markdown を安全に描く。今の詳しい画面と同じ道具）、選択肢と推奨、答える場所、サブタスクと残りの数、止めている・関係する Scope へのリンク、経緯、閉じたときの答えと原文の記録。写せるコマンドや、完了のボタンは置かない。
			  - 構造の図の箱とボードのカード：止めている開いたタスクがあれば「人 n」の印。Epic と Initiative の枠とカードは `blocking_with_descendants` を「人 n（配下を含む）」の形で出す（R-13）。
			  - Scope の詳しい画面：「人のタスク」のタブに、止めているもの、関係するものを、題名と期限つきで並べ、1件の画面へリンクする。
			  - 横断の概況の札：開いている数と期限切れの数（D-15 の `todos`）。読めないときは「人のタスクが読めない」の印。
			- 速さ：250件の構造と100件のタスクで、今の画面の速さの目安（epic-00427 D-07）を崩さない。
			- 層：`application/dashboard_todos.py`、`application/dashboard_http.py`、`application/dashboard_site.py`（revision）、`presentation/dashboard_api.py`（印）、`domain/todo_model.py`（`scope_marks`）、`assets/dashboard/`。
			"""
		satisfies: ["R-12", "R-13"]
	}
	"D-17": {
		title: "配布するスキルの規則と文書"
		text: """
			- 提供側の `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md` に「人のタスク」の節を足し、`src/spec_dock/assets/static-inventory.json` の同じ項目を直す。中身（R-05、R-14）：
			  1. 会話の中で答えが返るものは登録しない（Claude Code や Codex の複数の質問も同じ）。
			  2. 答えを待ったままターンを終えるとき、人しかできない操作をすぐにしてもらえないとき、数日かかる確かめ、期限のある行為は、`todo add --by agent --role <役割> --kind <種類>`（背景と問い、`--reply-to`、`--effort`、`decide` は選択肢と推奨）で登録してから、止まらない作業を続ける。止める Scope があれば `--blocks` を付ける。
			  3. 1回の会話で全部の答えが返らない2つ以上の項目は、あらかじめ `--kind checklist` と `--item` で束にし、答えを受けるたびにサブタスクを閉じ、返事の終わりに `todo show <親>` の残りを示す。
			  4. PR のマージ待ちは登録しない（ダッシュボードの表示を使う。意図して登録するのは妨げない）。作業者から統括への問いは Orca で行い、統括が答えられず人に上げるときだけ、統括が `decide` で登録する。
			  5. 答えを受けた担当が `todo done --record <原文の記録>` で閉じる。
			  6. 統括は、始めるときに `todo list` を読み、答えが出たのに閉じていないものを閉じる。
			  7. 秘密の値を書かない（操作のコマンドは書いてよい）。Claude Code の隔離セッション（`--worktree`）では、仕様と同じく読むだけにし、登録は統括に頼む。
			- 配布する文書：`src/spec_dock/assets/spec_dock/docs/todo.md`（人のタスクの使い方、記録の形、設定の3段と見本、集約、外部の道具の読み方）を足し、`reference_cli.md`（10のコマンドと2つの契約、`dashboard summary` の `todos`）、`canonical.md`（`todos/` がカタログにあること、エラーと次の1手）、`migration.md`（D-19）を直す。
			- dogfooding：spec-dock の main のチェックアウトで、版を入れた後に `installation update` でスキルを入れ替え、統括と作業者が使い始める（リリースの Issue）。
			- 層：配布の資産だけ（コードは変えない）。
			"""
		satisfies: ["R-05", "R-14"]
	}
	"D-18": {
		title: "カタログの検査が `todos/` を Scope と取り違えないこと"
		text: """
			- `CatalogTree.directories()` は区切りの形のディレクトリの中だけを見て、`misplaced()` は ID の形の名前と区切りの形の名前だけを示すので、`todos/` と `todos/<YYYY-MM>/` は Scope にも、置き場の誤り（`SCOPE_DIRECTORY_MISPLACED`）にもならない。`scope list`、`scope check`、`scope show`、`workspace validate`、`workspace doctor`、`work finish` の検査も、Scope のディレクトリだけを読む。これを変えない。
			- 確かめるテストを足す：`todos/2026-11/t-7k3m.json` と `todos/settings.json` のあるカタログで、`workspace validate` に誤りと置き場の警告が出ず、`scope list` の数が変わらないこと。年月の名前 `2026-11` を、区切りの形（`00000-00999`）と取り違えないこと（`todos/` の下なので、カタログの直下の検査に入らない）。
			- `workspace validate` の `.meta.json` の探索と衝突の写しの警告（`CANONICAL_CONFLICT_COPY`）は、`todos/` の中も今までどおり見る（衝突の写しを示すのは望ましい）。
			- `workspace validate` は `todo check` を呼ばない（`cue` を呼ばない今の決まりを保つ）。人のタスクの検査は `todo check` に分ける。
			- 層：コードは変えず、`tests/` に確かめを足す（記録の形と CLI の中核の Issue）。
			"""
		satisfies: ["R-01"]
	}
	"D-19": {
		title: "移行と、新しい版での最初の使い方"
		text: """
			- パッケージを新しい版に上げるだけで、`todo` のコマンドが使える。カタログの形式の版（format 1）、`workspace.json` の版（4）、構造のスナップショットは変えない。`todos/` は最初の `todo add` が作る（それまでは `todo list` が空を返し、`todo check` が「記録がない」で成功する）。
			- スキルの規則は静的な資産なので、各リポジトリで `installation update` をしたときに入れ替わる（パッケージの更新とは別。今の決まりどおり）。
			- 前の版の SpecDock が別の PC で同じカタログを同期しても、`todos/` はふつうのファイルとして保存と push がされ、検査にも引っかからない（前の版の `CatalogTree` も ID と区切りの形の名前だけを調べる。0.5.x と 0.6.0 で確かめる）。前の版では `todo` のコマンドがないだけ。
			- 利用者の設定のファイルは SpecDock が作らない。なくても初めの値で動く。
			- `migration.md` に、この版への更新（コマンドが10増える、`dashboard summary` に `todos` が足される、`todos/` の置き場、設定の3段、スキルの入れ替えに `installation update` がいること）を書く。画面の版では、画面が足されることだけを書く。
			- Company OS の受付簿の移し替えは、この Epic の外（しばらく使って良ければ Company OS の側で移す）。
			"""
		satisfies: ["R-01", "R-08"]
	}
}

compatibility: """
	- CLI と記録の形の版（次の minor の版。版の番号はリリースのときに統括が決める）：公開のコマンドが10増える（71）。`specdock.dashboard-summary/v1` に `todos` が足される（版は変えない）。カタログに `todos/` ができる。ほかのコマンドの契約、カタログの形式、構造のスナップショット、`evaluate_readiness` は変えない。
	- 画面の版（epic-00427 の完了の後）：API と画面を足すだけ。
	- 公開の契約にするもの：記録の形（`specdock.todo/v1`）、一覧（`specdock.todo-list/v1`）、利用者の設定（`specdock.config/v1` の `todo` の節）、リポジトリの設定（`specdock.todo-settings/v1`）、`dashboard summary` の `todos`、API の `/api/v1/todos` と `/api/v1/r/<repo>/todos[/<ID>]`。画面の印の形（`structure` の中の項目）は契約にしない。
	- 戻すとき：パッケージを前の版に戻すと `todo` のコマンドがなくなるが、`todos/` のファイルはカタログに残り、ほかのコマンドには影響しない（もう一度上げれば、そのまま読める）。
	"""

risks: [
	"エージェントが `--by agent` を付けずに登録すると、必須の欄の検査をすり抜ける（`--by` の既定は人）。スキルの規則で必ず付けさせ、dogfooding で漏れを見る。漏れが多ければ、環境変数からエージェントを見分ける案を後で判断する",
	"既定の期限が4時間なので、夜に登録したものは朝には期限切れで並ぶ。期限切れが多すぎて目立たなくなるなら、設定で変える（利用者の設定の `default_due`）",
	"`cue vet` の誤りの文と位置が、`cue` の版で変わるおそれ。結果の判定は終了コードとファイルの対応だけにし、文はそのまま示す",
	"2つの PC がオフラインで同じ ID を、違う年月に作ると、ID が重なる（約100万通りなので、ごくまれ）。`todo check` が示し、ID を指すコマンドは止まる。直し方（片方の ID を手で変える）を文書に書く",
	"登録簿は PC ごとなので、別の PC では、その PC で `canonical link` したリポジトリだけが集まる。今は1台で使うので困らない",
	"画面の Issue は epic-00427 の完了（段階2の 0.7.0 を含む）を待つので、画面が出るのは CLI よりかなり後になる。それまでは CLI と `dashboard summary` で見る",
	"人のタスクの本文に秘密情報を書くと、同期が保留にし、カタログの保存が止まる。スキルの規則で書かせない。保留になったら、今の同期の手順（`canonical status`）で直す",
]
