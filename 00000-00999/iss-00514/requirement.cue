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
	reason: "移行の控えと古い worktree を消す。消すと戻せないので、対象と結果を利用者が確かめてから行う。"
}

// 目的と背景（任意）。
purpose:    "移行のために残した控えと、版3のまま残した worktree を、利用者が決めたとおりに片付ける。"
background: "I-12（#439）と I-13（#440）と、0.4.2・0.5.0 の配布で、控えを残した（`worktrees/i12-prep/backups/`、`worktrees/i12-prep/migrate-to-canonical-state/`、`worktrees/spec-dock-042/backups/`、`worktrees/spec-dock-050/backups/`、`/private/tmp/spec-dock-v0.4.*`・`v0.5.0` の作業の置き場）。spec-dock には、版3のままの worktree が2つある（`local-macos-vm-ci`、`schema1-preserving-migration-20261004`）。0.5.0 では、その中で SpecDock のコマンドが動かない。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "片付けの一覧を示す"
		text:  "0.5.1 を配ってから1〜2週間の通常の利用で問題がないことを確かめた後、対象ごとに、パス、大きさ、作られた時期と理由、消したときに失うものを並べた一覧を利用者に示す。"
		acceptance: ["一覧と、問題がないことの根拠（同期の記録と `canonical status`）が report.md にある"]
	}
	"R-02": {
		title: "許可されたものだけを消す"
		text:  "利用者が許可した対象だけを消し、ほかは残す。版3の worktree は、#463 の再開のしかたと合わせて、main を取り込むか消すかを利用者が決める。worktree は `spec-dock worktree remove` で消す。"
		acceptance: ["消したものと残したものと、利用者の決定が report.md にある"]
	}
}

// 失敗・境界の条件。番号（F-01、…）をキーにする。
// title は必須。impact（起きたときの影響）と recovery（回復のしかた）は strict 以上で必須。
failures: {
	// "F-01": {
	// 	title:    "〜のときは、何も書かずに止まる"
	// 	impact:   "〜"
	// 	recovery: "〜"
	// }
}

// 制約・前提、合意した判断、未解決事項（任意）。
// constraints: ["..."]
// decisions: ["..."]
// questions: ["..."]
