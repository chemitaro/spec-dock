package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00547。plan.cue の slice "iss-00549" の covers（R-01〜R-09、F-01〜F-03）を、この Issue で観測できる形にした。
// 番号は Epic と同じ意味で使い、R-10（カタログの検査）と R-11（コマンドの一覧と文書）を足した。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "新しい記録の形と10のコマンドを足すが、既存のコマンドとカタログの形式は変えず、配る前なら PR を戻せば元に戻る"
}

purpose: "人のタスクを、各リポジトリのカタログの `todos/` に1件1つの JSON で置き、`spec-dock todo` の10のコマンドで、チェックアウトの中から登録・一覧・詳しく・更新・完了・延期・取り消し・開き直し・検査・設定の確かめができるようにする（全リポジトリの集約は iss-00550）。"

background: """
	- 親の Epic（epic-00547）の要件・設計・計画は承認済み。この Issue は、その第1波（記録の形と型と設定、CLI の中核）。設計の正本は Epic の design.cue の D-01〜D-13 と D-18 で、この Issue の design.cue は、それを実装の単位に割り、Epic が決めていない細部を決める。
	- 集約（`todo list --all-repositories`、`--repository`、`todo show <REF>`、`mode: all_repositories`）と `dashboard summary` の数は iss-00550、スキルの規則と `docs/todo.md` は iss-00551、版と `migration.md` は iss-00553、画面は iss-00554。
	"""

includes: [
	"記録の形 `specdock.todo/v1` の Python の型と書く前の検査、CUE の型 `#Todo`、`todo check` の2段の検査",
	"カタログの `todos/` の読み書き（ロック、原子的な置き換え、衝突の写しの警告）と ID の採番",
	"サブタスク（1段）と会話の束（`checklist`）、期限・延期・並び・派生の状態、件数の警告",
	"3段の設定（初めの値、利用者の設定、リポジトリの設定）と `todo settings`",
	"Scope との結び付き（関係する Scope、止めている Scope）と `todo list --scope`／`--blocking`",
	"チェックアウトの中の `todo add|list|show|update|done|snooze|cancel|reopen|check|settings`、1件の結果の形と `specdock.todo-list/v1` の `mode: repository`",
	"`todos/` をカタログの検査が Scope と取り違えないことのテスト",
	"コマンドの一覧の文書（`reference_cli.md`、`docs/README.md`、`cli-redesign-guide.html`、README）と、その dogfood の写しと inventory の行",
]
excludes: [
	"`todo list --all-repositories`／`--repository`、`todo show <REF>`、登録簿の読み取り、`dashboard summary` の `todos`（iss-00550）",
	"配布するスキルの規則と `docs/todo.md`、`canonical.md` の更新（iss-00551）",
	"版の番号と `migration.md`（iss-00553）",
	"ダッシュボードの API と画面、`scope_marks`（iss-00554）",
	"利用者の設定のファイルを作るコマンド（SpecDock は読むだけ）",
]

requirements: {
	"R-01": {
		title: "人のタスクは、そのリポジトリのカタログの `todos/<YYYY-MM>/<ID>.json` に1件1つのファイルで置かれ、GitHub に要求を送らない"
		text:  "閉じても動かさず、消さない。どの worktree からも同じカタログが見える。`todo` のコマンドは GitHub への要求も構造のスナップショットの取り直しもしない。"
		acceptance: [
			"main のチェックアウトで `todo add` したタスクが、同じクローンの別の worktree の `todo list --json` に出る",
			"`todo add`、`todo done` などの全コマンドの実行で、テストの `gh` の stub が一度も呼ばれない",
			"`todo done` の後も、記録のファイルが同じ道に残り、書き込みが changeset に残る",
		]
	}
	"R-02": {
		title: "記録は書く前に Python の型で確かめられ、`todo check` は Python の検査と `cue vet` の2段で全部の記録を確かめる"
		acceptance: [
			"形の正しくない記録を、`todo check` がファイル、欄、理由、出どころ（`python` か `cue`）つきで示し、終了コード7で止まる",
			"`cue` が PATH にないときも、`todo check` が警告 `TODO_CUE_SKIPPED` を出して Python の検査で結果を決める",
			"`tests/fixtures/todo/{valid,invalid}/` の同じ見本で、ファイルごとの通る・通らないが Python の検査と `cue vet` で一致するテストがある",
		]
	}
	"R-03": {
		title: "タスクは ID、題名、種類、状態、期限、依頼者、経緯、Scope との結び付きを持ち、エージェントの登録には必須の欄がある"
		text:  "ID は `t-` と Crockford の base32 の小文字4文字で、そのカタログの中で重ならない。エージェント（`--by agent`）は `role`、`body`、`reply_to`、`effort`（`decide` は `options` 2つ以上と `recommendation`）が必須。人（既定）は題名だけで登録できる。"
		acceptance: [
			"エージェントとして必須の欄を欠いた `todo add` が、`details.missing` に欄の名前を並べた `TODO_INVALID`（終了コード2）で、何も書かずに止まる",
			"人として `todo add --title T` だけで登録でき、`kind: todo`、空の `scopes`、`links`、`tags`、`subtasks` と既定の期限が入る",
			"`todo done --choice K --note N --record R` が `resolution` と `history` の `done` を記録に残す",
			"生成した ID が `^t-[0-9a-hjkmnp-tv-z]{4}$` に合い、既存の ID（閉じたものも）と重ならない",
		]
	}
	"R-04": {
		title: "タスクは1段のサブタスクを持ち、全部が閉じたとき親を閉じてよいことが示される"
		acceptance: [
			"`todo add --parent t-xxxx --title S` で `t-xxxx.1`、`t-xxxx.2` が親のファイルの中に足され、`todo done t-xxxx.2` で1つずつ閉じられる",
			"孫（`--parent t-xxxx.1`）は `TODO_NESTING_TOO_DEEP`（終了コード2）で断られる",
			"全部のサブタスクが閉じたとき、`todo show` と最後の `todo done` の結果に `parent_closable: true` が出る",
			"開いたサブタスクのある親の `todo done` は `TODO_SUBTASKS_OPEN`（終了コード3）で止まり、`--include-subtasks` で一緒に閉じられる",
		]
	}
	"R-05": {
		title: "1回の会話で終わらない複数の項目を、`checklist` の親と `--item` のサブタスクとして1回で登録でき、残りが示される"
		acceptance: [
			"`todo add --kind checklist --by agent … --item A --item B` が、1つのファイルに親と2つのサブタスクを書き、既定の期限を付ける",
			"`todo show <親>` の `derived.open_subtasks` と、テキストの出力の「残り n 件」に、開いたサブタスクが並ぶ",
		]
	}
	"R-06": {
		title: "期限を持ち、指定しなければ既定の期限が付き、期限切れ・延期・並びが一覧に出る"
		acceptance: [
			"期限を指定しない `todo add` に、`created_at` の4時間後の `due` が付く",
			"期限を過ぎた開いたタスクが、`todo list --json` の `derived.overdue: true` で、並びの先頭に出る",
			"`todo snooze --until` したタスクは、その時刻まで既定の `todo list` から隠れ、過ぎれば `effective_status: open` で戻る",
			"`--due` の `30m`、`4h`、`2d`、`YYYY-MM-DD`、時間帯つきの ISO 8601 を受け、過去の時刻を `TODO_INVALID` で断る",
		]
	}
	"R-07": {
		title: "件数の目安を超えると警告し、登録は成功する"
		acceptance: [
			"開いている、エージェントが登録した、`checklist` でない親のタスクが目安を超える `todo add` が、警告 `TODO_LIMIT_EXCEEDED`（`kind: repository`）を出して終了コード0で登録する",
			"1つの親の開いたサブタスクが目安を超える `todo add --parent` が、`kind: subtasks` の同じ警告を出して登録する",
			"人が登録したもの、束、サブタスクは、リポジトリの数に入らない",
		]
	}
	"R-08": {
		title: "目安の件数と既定の期限が、初めの値 < 利用者の設定 < リポジトリの設定 の順で決まり、効いている値と出どころを示せる"
		acceptance: [
			"`$XDG_CONFIG_HOME/spec-dock/config.json` の `todo.parent_limit` を変えると、警告の境目が変わる",
			"`<catalog>/todos/settings.json` にある値は、利用者の設定より優先される",
			"どちらかのファイルが壊れていても、`todo` のコマンドはほかの段の値で動き、警告 `TODO_SETTINGS_INVALID` を出す",
			"`todo settings --json` が、鍵ごとの `value` と `source`（`default`、`user`、`repository`）と、段ごとの `path`、`state` を返す",
		]
	}
	"R-09": {
		title: "タスクに関係する Scope と止めている Scope を結び付けられ、Scope の判定は変わらない"
		acceptance: [
			"`todo list --scope <ID>` が、`related` か `blocks` にその ID を持つタスクだけを返し、`--blocking` は止めているものだけを返す",
			"Scope の ID の入力は0埋めしなくてよく（`iss-531` は `iss-00531`）、形の違う ID は `TODO_INVALID` で断られ、スナップショットにない ID は警告 `TODO_SCOPE_UNKNOWN` で書かれる",
			"人のタスクがあっても `dependency check` と `work start` の判定が変わらず、`evaluate_readiness` のコードが `todos` を参照しない",
		]
	}
	"R-10": {
		title: "カタログの検査が `todos/` を Scope や置き場の誤りと取り違えない"
		acceptance: [
			"`todos/2026-11/t-7k3m.json` と `todos/settings.json` のあるカタログで、`workspace validate` に誤りと置き場の警告が出ず、`scope list` の数が変わらない",
			"`workspace validate` と `scope check` が `cue` で `todos/` を調べない",
		]
	}
	"R-11": {
		title: "公開のコマンドが71になり、ヘルプと配布する文書がそれを示す"
		acceptance: [
			"`LEAF_PATHS` に `todo` の10の葉があり、各葉の `--help` に働き、読むもの、書くもの、前提、JSON の形が出る",
			"`reference_cli.md` に10のコマンドと契約 `specdock.todo/v1`、`specdock.todo-list/v1`（`mode: repository`）があり、コマンドの数を縛るテストと文書が71を示す",
			"変えた配布の文書の inventory の sha256 と `known_old_sha256` が更新され、dogfood の写しが同じ中身になる",
		]
	}
}

failures: {
	"F-01": {
		title: "書く前の検査に通らないとき、ロックが取れないとき、読んだ記録が壊れているときは、何も書かずに止まる"
		text:  "入力の誤りは `TODO_INVALID`（2）、壊れた記録や版の違う記録の書き換えは `TODO_RECORD_INVALID`／`TODO_SCHEMA_UNSUPPORTED`（3）、ロックは `CANONICAL_LOCK_BUSY`。changeset も書かない。"
	}
	"F-02": {
		title: "別の PC との衝突の写し（`*.conflict-*`）と、年月の違う同じ ID を、記録として読まずに示す"
		text:  "`todo list`、`todo show`、`todo check` は衝突の写しを警告 `TODO_CONFLICT_COPY` で示す。同じ ID の2つのファイルは `todo check` が `TODO_ID_DUPLICATE`（誤り）で示し、その ID を指すコマンドは `TODO_ID_AMBIGUOUS`（3）で止まる。"
	}
	"F-03": {
		title: "カタログのリンクがない、または正しくないチェックアウトでは、`todo` のコマンドが `CANONICAL_NOT_LINKED`（次の1手 `spec-dock canonical link`）で何も書かずに止まる"
	}
}

constraints: [
	"Epic の design.cue の D-01〜D-13、D-18 に従う。食い違いは統括に知らせ、仮の判断は report.md と PR に書く",
	"カタログの形式（format 1）、`workspace.json` の版、構造のスナップショット、`evaluate_readiness`、ほかのコマンドの契約を変えない",
	"版の番号と `migration.md` を変えない（iss-00553）。ダッシュボードの画面（`assets/dashboard/`）と `dashboard summary` を触らない",
	"テストは一時のディレクトリと `XDG_CONFIG_HOME`／`XDG_STATE_HOME` と `gh` の stub で閉じ、利用者の設定のファイルを作らない",
]

decisions: [
	"2026-11-04：集約の引数（`--all-repositories`、`--repository`）と `todo show <REF>` は、この Issue では引数として足さない（iss-00550 が足す）。この Issue の `todo show` は ID だけを受ける",
	"2026-11-04：`cue vet` は、全部の記録をカタログからの相対の道を鍵にした1つの JSON にまとめ、標準入力から `#Records`（`[string]: #Todo`）で確かめる。Epic D-05 のファイルを並べる呼び方は、`cue` v0.17.1 が最初に誤ったファイルの誤りしか出さず、位置がファイルを指さないこともあるため、ファイルごとの対応が取れないことを試して確かめた（統括に知らせる）",
]

questions: []
