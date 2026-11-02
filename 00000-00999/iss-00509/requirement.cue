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
	reason: "配布するスキルの補助スクリプトだけを直す。失敗しても Artifact は作り直せる。"
}

// 目的と背景（任意）。
purpose:    "`spec-dock-grill-with-docs` の `finalize-artifact.py` が、版4の `spec-dock/initiatives` のリンクを通る Artifact のパスを受け付ける。"
background: "I-13（#440）で見つかった（`iss-00440/report.md` の後続の候補 7）。版4では `spec-dock/initiatives` がカタログへのリンクなので、今は「unsafe directory component 'initiatives'」で拒む。今のテストは実ディレクトリに写した配置で確かめている。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "リンクを通る Artifact を仕上げられる"
		text:  "`spec-dock/initiatives` がカタログへのリンクのとき、そのリンクだけは安全な経路として扱い、ほかのリンクは今までどおり拒む。"
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
