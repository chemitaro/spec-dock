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
	reason: "配布資産の雛形の置き方だけを変える"
}

// 目的と背景（任意）。
purpose:    "配布する雛形 `spec-dock/templates/cue/{epic,initiative,issue}/.workbench/README.md` が、利用側のルートの `.gitignore` の `.workbench/` に隠されて、コミットから漏れないようにする。"
background: "I-12 の準備で、input-devices、company-os、housing-lifecycle の `installation update` が置いたこの3つのファイルが、ルートの `.gitignore` の `.workbench/` で無視され、`git add -f` で足す必要があった（spec-dock のリポジトリでも同じ扱い）。コミットされないと、ほかのクローンの `scope create` の雛形が欠ける。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "雛形がルートの `.workbench/` の無視に隠されない"
		text:  "雛形の置き場を無視されない名前に変える、`spec-dock/.gitignore` に `!` の行を足す、または `installation update` が無視されたファイルを警告する、のどれかで、利用側のコミットから漏れなくなる。"
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
