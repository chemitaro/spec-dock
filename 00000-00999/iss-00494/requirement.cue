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
	reason: "配布する見本と文書だけを変え、動きは変えない"
}

// 目的と背景（任意）。
purpose:    "`canonical check` の CI の見本（`spec-dock/docs/ci/spec-dock-check.yml`）と案内に、ホストの runner の費用と、リポジトリの決まりに合わせて起動の条件と runner を変えてよいことを書く。"
background: "I-12（#439）で、`migrate.py cut` が見本どおり PR と push で `ubuntu-latest` に動く `spec-dock-check.yml` を足した。housing-lifecycle（判断 S72：CI は手動の起動だけ、push の前は pre-push hook）と taikyohiyou（手元の VM の runner への振り分け、費用の見張りが `ci.yml` を名前で参照）では、そのままでは決まりに反するので、手で合わせた。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "見本と案内が費用と合わせ方を述べる"
		text:  "見本の注記と `spec-dock/docs/canonical.md`（または CI の案内）が、ホストの runner の費用、起動の条件と runner を変えてよいこと、push の前の hook で同じ `spec-dock canonical check --json` を回す形を述べる。"
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
