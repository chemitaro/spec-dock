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
	reason: "利用者の無視されたファイルを、許可なしに消しうる（データの失われ）。"
}

// 目的と背景（任意）。
purpose:    "`worktree remove --unlock` が、unlock の後にできた無視されたファイルを、`--discard-ignored` なしで消さない。"
background: "I-13（#440）で見つかった（`iss-00440/report.md` の後続の候補 6）。unlock の前に「無視されたものはリンクだけ」と判定して `discard_ignored` を真にするため、unlock の後にできたファイルも消しうる。撤去の前のコードも同じ。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "無視されたものの判定を unlock の後に行う"
		text:  "unlock の後に、無視されたものがリンクだけかを判定する。ほかのものがあれば、`--discard-ignored` なしでは何も消さずに止まる。"
		acceptance: ["unlock の後に無視されたファイルを作るテストで、`--discard-ignored` なしの `worktree remove --unlock` がそのファイルを残して止まることが観測できる（元のテスト `test_issue413_worktree_remove.py::test_remove_preserves_ignored_content_created_after_unlock`）"]
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
