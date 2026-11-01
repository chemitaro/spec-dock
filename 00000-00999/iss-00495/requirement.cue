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
	reason: "一度きりの移行の道具の直しで、戻すとき（export-legacy）にだけ効く"
}

// 目的と背景（任意）。
purpose:    "I-12（#439）の切り替えで見つけた `scripts/migrate-to-canonical/migrate.py` の穴を、撤去（0.5.0、I-13）までの戻し（`export-legacy`）に備えて直すか、README に書く。"
background: "`migrate.py` は仕様のツリーの中のリンクだけを書き換え、ツリーの外（`content/`、`docs/` など）から仕様を指すリンクを書き換えない。I-12 では input-devices 17、housing-lifecycle 316、taikyohiyou 4 件が切れ、手で直した（input-devices#20、housing-lifecycle#240、taikyohiyou#2228）。戻すときも同じで、`export-legacy` はツリーの外のリンクを入れ子に戻さない。ほかに、Scope が0件のリポジトリで `verify` が `no commit with schema-3 metadata was found`（exit 2）で終わること、1時間に500件の書き込みの上限で表示なしに最大1時間待つこと、往復で前から切れたリンクの書き方が変わることがあった。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "戻すときにツリーの外のリンクが切れない"
		text:  "`export-legacy` が、ツリーの外から平らな置き場を指すリンクを入れ子のパスに戻すか、戻すべきリンクの一覧を示す。少なくとも README の「戻し方」に、この手順を書く。"
	}
	"R-02": {
		title: "小さな穴を README に書くか直す"
		text:  "Scope が0件の `verify`、500件の上限の待ち（表示を出す）、前から切れたリンクの扱いを、直すか README に書く。"
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
