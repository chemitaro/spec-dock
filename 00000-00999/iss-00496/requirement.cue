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
	reason: "installation update の結果の案内を変え、Claude Code から skill が見えなくなる事故を防ぐ"
}

// 目的と背景（任意）。
purpose:    "`installation update` が `.claude/skills/spec-dock*` の古い写しを外したのに、`.claude/skills/<name>` → `../../.agents/skills/<name>` のリンクがないとき、Claude Code から skill が見えなくなることを結果で知らせ、次の1手を示す。"
background: "I-12 の準備（2026-11-01）で、4つのリポジトリの `installation update`（0.4.1）が `.claude/skills/spec-dock` と `spec-dock-grill-with-docs` の写しを外した。リンクは Claude Code の側（`sync-project-skills`）が作る決まりで、どのリポジトリにもまだなかったため、手でリンクを置いた（input-devices#18 など）。知らせがないと、Claude Code のセッションが SpecDock の skill を読めないまま動く。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "写しを外してリンクがないとき、警告と次の1手が出る"
		text:  "`installation update`（と `--dry-run`）の結果が、外す写しの名前ごとに、リンクがないことを警告し、置き方（相対リンクのコマンド、または `sync-project-skills`）を示す。リンクがあるときは何も言わない。"
		acceptance: ["写しがあってリンクのない一時のリポジトリで、`installation update --dry-run --json` に警告が出ることがテストで観測できる", "リンクがあるときは警告が出ないことがテストで観測できる"]
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
