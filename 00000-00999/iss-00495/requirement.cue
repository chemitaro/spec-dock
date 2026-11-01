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
		title: "戻すときにツリーの外のリンクを手で戻す手順が分かる"
		text:  "README の「戻し方」に、`migrate.py` が仕様のツリーの外（`content/`、`docs/` など）から仕様を指すリンクを書き換えないこと、切り替えでは切り替え前のコミットの `.meta.json` から新旧のパスの対応を作って手で直したこと（input-devices 17件 #20、housing-lifecycle 316件 #240、taikyohiyou 4件 #2228）、`export-legacy` で戻すときもツリーの外のリンクは入れ子に戻らず同じように手で戻す必要があることを書く。"
		acceptance: ["README の「戻し方」の節に、ツリーの外のリンクが書き換えられないことと、手で戻す手順が書かれている"]
	}
	"R-02": {
		title: "小さな穴を README に書く"
		text:  "Scope が0件の `verify` が `no commit with schema-3 metadata was found`（exit 2）で終わること（比べるものがないだけで異常ではない）、書き込みは1時間に500件（`WRITES_PER_HOUR`）までで、達すると表示なしに最大1時間待つこと（止まったのではない）、往復で前から切れたリンクの書き方が変わることがあることを、README の共通の決まりか本番の節に書く。"
		acceptance: ["README に3つの穴がそれぞれ書かれ、テストが要る語の存在を確かめる"]
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
constraints: ["コードは直さない（道具は 0.5.0 の撤去で消すため）。編集は README、`tests/`、この Scope のディレクトリだけ"]
decisions: ["利用者の決定（2026-11-01）：R-01 の元の案「`export-legacy` が戻すか一覧を示す」は、コードを直さない範囲（README だけ）に合わせて「README に手で戻す手順を書く」に直した。理由は report.md"]
// questions: ["..."]
