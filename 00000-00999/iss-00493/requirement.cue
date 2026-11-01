package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "同期が保存するファイルの規則を変え、すべてのリポジトリのカタログに効く"
}

// 目的と背景（任意）。
purpose:    "macOS の `.DS_Store` などの OS が作る不要なファイルを、カタログの同期が `spec-dock/canonical` に保存しないようにする。"
background: "2026-11-01 の I-12（#439）で、taikyohiyou の `move-local` が移した `spec-dock/initiatives/init-01808-…/.DS_Store` を、定期の同期が保存して GitHub に push した（`d0a643a`。手で消して `4b15af0` で保存し直した）。移行の前は、taikyohiyou のルートの `.gitignore` で無視されていた。カタログの無視の規則はカタログ自身の `.gitignore`（`.runtime/` と `.workbench/` だけ）で、リポジトリの `.gitignore` は効かず、利用者の全体の除外（`~/.config/git/ignore`）にも `.DS_Store` はない（2026-11-01 に確かめた）。Finder で仕様のフォルダーを開くたびに `.DS_Store` ができ、同期で GitHub に push されうる。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "OS の不要なファイルを保存しない"
		text:  "カタログで `.DS_Store`（ほかに `Thumbs.db` など、決めた一覧）ができても、同期はそれを保存せず、push もしない。"
		acceptance: ["カタログに `.DS_Store` を置いて同期を2回実行しても、`spec-dock/canonical` のツリーに `.DS_Store` が入らないことがテストで観測できる"]
	}
	"R-02": {
		title: "すでに保存された不要なファイルの扱いが分かる"
		text:  "`canonical status` か `canonical check` が、カタログのツリーにある OS の不要なファイルを示し、消し方を案内する。"
		acceptance: ["ツリーに `.DS_Store` を持つカタログで、指摘と次の1手が出ることがテストで観測できる"]
	}
	"R-03": {
		title: "OS の不要なファイルを未保存と数えない"
		text:  "保存しない OS の不要なファイルが残っていても、`canonical status` の未保存の数に入らず、`work finish` の保存の確かめを止めない（Finder が Scope のフォルダーに `.DS_Store` を作るたびに、終了が `CANONICAL_SAVE_UNCONFIRMED` で止まらない）。"
		acceptance: [
			"カタログに `.DS_Store` だけがあるとき、`canonical status` の `changes.unsaved` が 0 であることがテストで観測できる",
			"Scope のディレクトリに `.DS_Store` だけがあるとき、`work finish` の保存の確かめが、その場所を未保存と見ないことがテストで観測できる",
		]
	}
	"R-04": {
		title: "すでに保存された不要なファイルの削除は、大量の削除の保留に数えない"
		text:  "R-02 の案内に従って OS の不要なファイルをまとめて消しても、大量の削除の保留（`mass_delete`）にならず、次の同期が削除を保存する。"
		acceptance: ["保存済みの `.DS_Store` を25個消しても保留にならず、削除が保存されることがテストで観測できる"]
	}
}

// 失敗・境界の条件。番号（F-01、…）をキーにする。
// title は必須。impact（起きたときの影響）と recovery（回復のしかた）は strict 以上で必須。
failures: {
	"F-01": {
		title:    "保存しない不要なファイルが残るカタログは、`canonical remove` が何も消さずに止まる"
		text:     "保存しないファイルは未保存と数えないので、`git worktree remove` が失敗する前に、消してしまうファイルとして名指して止まる。"
		impact:   "止まらないと、リンクや登録を消した後で `git worktree remove` が失敗し、中途の状態が残る"
		recovery: "示したファイルを消すかカタログの外へ移し、同じコマンドをもう一度実行する"
	}
}

// 制約・前提、合意した判断、未解決事項（任意）。
constraints: [
	"利用者の5つの既存のカタログ（spec-dock、input-devices、company-os、housing-lifecycle、taikyohiyou_project）でも、パッケージを更新するだけで効く（カタログのファイルを書き換える手順を要さない）",
	"カタログのルートのファイル（形式1の `CANONICAL_ROOT_FILES`）は変えない",
]
decisions: [
	"R-03、R-04、F-01 は、実装担当が設計の中で見つけて足した（同期の規則で除外すると、未保存の数、`work finish`、`canonical remove`、削除の保留に影響が及ぶため）。理由は report.md にある",
]
