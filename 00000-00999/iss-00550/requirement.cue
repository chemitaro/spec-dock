package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 親は epic-00547。plan.cue の slice "iss-00550" の covers（R-10、R-11、F-03）を、この Issue で観測できる形にした。
// R-10、R-11、F-03 は Epic と同じ意味。R-20（契約と文書）と R-21（iss-00549 のゲートの P2 の2件）は、この Issue で足した番号。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "公開の一覧の JSON の契約と dashboard summary の項目を足すが、既存の項目は変えず、配る前なら PR を戻せば元に戻る"
}

purpose: "このPCの登録簿にある全リポジトリの人のタスクを、チェックアウトもサーバーもなしに1回の `todo list --all-repositories` で集めて版つきの JSON（`specdock.todo-list/v1` の `mode: all_repositories`）で返し、`todo show <REF>` で横断の名前から1件を読めるようにし、`dashboard summary`（とサーバーの summary の API）に人のタスクの数（`todos`）を出す。"

background: """
	- 親の Epic（epic-00547）の要件・設計・計画は承認済み。この Issue は、その第2波（集約と要約）。設計の正本は Epic の design.cue の D-13〜D-15 で、この Issue の design.cue は、それを実装の単位に割り、Epic が決めていない細部を決める。
	- 前の iss-00549（PR #558、マージ済み）が、記録の形、`todo_store`、`todo_model`、`todo_document`、チェックアウトの中の10のコマンドを作った。この Issue は、それを使い、別に書かない。
	- iss-00549 の最終品質ゲートの情報だけの P2 の2件（`gh` の stub のテストが `update`、`snooze`、`cancel`、`reopen` を実行していない。Scope の判定が変わらないことの文字の確かめが `canonical_work.py` を読んでいない）も、この Issue で直す。
	"""

includes: [
	"`todo list --all-repositories`／`--repository R`（登録簿の全カタログを読み、リポジトリごとの失敗を閉じ込める）と `specdock.todo-list/v1` の `mode: all_repositories`（`hidden`、`duplicate`、`unreadable`）",
	"`todo show <REF>`（`owner/name/t-xxxx`、`host/owner/name/t-xxxx`）を登録簿から読む",
	"`dashboard summary` の `todos`（`status`、`open`、`blocking`、`overdue`、`problem`）と、サーバーの `/api/v1/r/<repo>/summary` が同じ数を返すこと",
	"`reference_cli.md` の契約とコマンドの説明、ヘルプの文、その dogfood の写しと inventory の行",
	"iss-00549 のゲートの P2 の2件のテストの穴",
]
excludes: [
	"ダッシュボードの画面（`assets/dashboard/`）、`/api/v1/todos` などの API、`structure` の印、`scope_marks`、revision（iss-00554）",
	"配布するスキルの規則と `docs/todo.md`、`canonical.md`（iss-00551）",
	"版の番号と `migration.md`（iss-00553）",
	"ほかのリポジトリのタスクへの書き込み（書くコマンドは今までどおり、そのチェックアウトのカタログだけ）",
]

requirements: {
	"R-10": {
		title: "全リポジトリの人のタスクを、チェックアウトもサーバーもなしに、1回の CLI で集めて版つきの JSON で返せる"
		text:  "`todo list --all-repositories` は、このPCの登録簿の全行のカタログの `todos/` を読み、リポジトリの名前つきで、D-08 の並びで返す。`--repository R` はそのリポジトリだけに絞る（`--all-repositories` を含む）。`todo show <REF>` は横断の名前から1件を返す。どれも GitHub とサーバーに要求を送らない。"
		acceptance: [
			"登録簿にある2つのリポジトリのタスクが、チェックアウトの外で実行した1回の `todo list --all-repositories --json` に、`mode: all_repositories`、`repositories` の2行、`items` の `ref`／`repository` つきで並ぶ",
			"`--repository owner/name` が、そのリポジトリの行とタスクだけを返す",
			"ダッシュボードで隠したリポジトリも `hidden: true` で返り、`repository` の分からない行は `repository: null`、`ref: null` で返る",
			"同じリポジトリの2つのクローンの行は、`main_checkout` の道の順で最初の行だけを読み、2つ目は `status: duplicate` になる",
			"`todo show owner/name/t-xxxx` が、チェックアウトの外でそのタスクの1件の結果を返す",
			"これらのコマンドの実行で、テストの `gh` の stub が呼ばれない",
		]
	}
	"R-11": {
		title: "`dashboard summary` と、サーバーの summary の API に、人のタスクの数が出る"
		text:  "`specdock.dashboard-summary/v1` に `todos: {status, open, blocking, overdue, problem}` を足す（版は変えない）。数はそのリポジトリの親のタスク（サブタスクは数えない）で、開いている＝閉じていない（延期中を含む）、止めている、期限切れ。"
		acceptance: [
			"`dashboard summary --json` の `data.result.todos` に、開いている数、止めている数、期限切れの数がある",
			"チェックアウトの中では、そのチェックアウトのリンクが正しければ、登録簿に載っていないカタログ（`--no-schedule`）の数も出る",
			"サーバーの `/api/v1/r/<repo>/summary` が、同じリポジトリの `dashboard summary <repo>` と同じ `todos` を返す",
		]
	}
	"R-20": {
		title: "新しい契約と引数が、配布する文書とヘルプに書かれている"
		acceptance: [
			"`reference_cli.md` に、`todo list --all-repositories`／`--repository`、`todo show <REF>`、`mode: all_repositories` の形、`dashboard summary` の `todos` がある",
			"dogfood の写しが提供側と同じで、`static-inventory.json` の行の sha256 が中身と合い、前の sha256 が `known_old_sha256` にある",
		]
	}
	"R-21": {
		title: "iss-00549 のゲートの P2 の2件のテストの穴が埋まる"
		acceptance: [
			"`gh` の stub が呼ばれないことを確かめるテストが、`update`、`snooze`、`cancel`、`reopen` も実行する",
			"Scope の判定が人のタスクを読まないことの文字の確かめが、`application/canonical_work.py` を読む",
		]
	}
}

failures: {
	"F-03": {
		title: "カタログが読めないリポジトリは、理由と次の1手（`canonical link`）を示し、ほかのリポジトリの分を返す"
		text:  "集約では `status: unreadable` と `problem` にして警告 `TODO_REPOSITORY_UNREADABLE` を出し、全体は成功する。`todo show <REF>` では `TODO_REPOSITORY_UNREADABLE`（終了コード3）で止まる。`dashboard summary` では `todos.status: unavailable` にし、要約そのものは成功する。登録簿そのものが読めない集約は `TODO_REGISTRY_UNREADABLE`（終了コード3）で止まる。"
	}
}

constraints: [
	"Epic D-13〜D-15 の契約の形を変えない。`specdock.todo-list/v1` と `specdock.dashboard-summary/v1` は、項目を足すだけで版を変えない",
	"`todo` のコマンドと `dashboard summary` は GitHub にもサーバーにも要求を送らない",
	"読むだけのコマンドはロックを取らず、何も書かない",
	"利用者の設定のファイル（`~/.config/spec-dock/`）を作らない。テストは一時のディレクトリと環境変数で閉じる",
]

decisions: [
	"2026-11-04：`--repository R` に登録簿にないリポジトリを渡したときは、止めずに警告 `TODO_REPOSITORY_UNKNOWN` を出して、ほかを返す（集約の失敗を閉じ込める決まりに合わせる。仮の判断）",
	"2026-11-04：同じリポジトリの2つ目のクローンの行には、警告 `TODO_REPOSITORY_DUPLICATE` も出す（仮の判断）",
]

questions: []
