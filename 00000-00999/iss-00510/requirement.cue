package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "light"
	reason: "宣言の読み取りの境界の扱いを直す。今の利用者のリポジトリには該当する宣言がない。"
}

// 目的と背景（任意）。
purpose:    "曖昧な宣言と、観測の間に消えた worktree を、はっきりした結果で扱う。"
background: "I-13（#440）で見つかった（`iss-00440/report.md` の後続の候補 8、12）。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "重複キーの宣言を曖昧として扱う"
		text:  "`{\"schema_version\":99,\"schema_version\":4}` のような重複キーの宣言を、版4として受け付けない（撤去の前と同じく今は受け付ける）。扱い（`PRECONDITION_FAILED` にするか）は設計で決める。"
	}
	"R-02": {
		title: "観測の間に消えた版3の worktree を unavailable にする"
		text:  "`resolve_observed_context` が版3の兄弟の宣言を2回読む間にそれが消えても、AssertionError で落ちずに unavailable の行にする。"
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
