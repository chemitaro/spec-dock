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
	reason: "親を閉じるときの子孫の判定を1つ緩めるだけ。誤って閉じても scope reopen で戻せる。"
}

// 目的と背景（任意）。
purpose:    "親の Scope を `scope close --reason completed`（と `work finish`）で閉じるとき、不採用（not planned）で閉じた子孫があっても止めない。開いている子孫と、状態が分からない子孫があるときだけ止める。"
background: "2026-11-02 に epic-00424 を閉じようとしたところ、子の I-6（#433。中身を I-5 に移したので、計画どおり不採用で閉じた）のために `DESCENDANT_NOT_COMPLETED` で止まった。判定は `src/spec_dock/runtime/application/scope_completion_plan.py:81` と `canonical_work.py:848` にあり、子孫が `completed` 以外ならすべて止める。不採用の子孫は、わざとやめた仕事なので、親の完了を止める理由がない。利用者は、この判定を直し、0.5.1 の後に epic-00424 を閉じると決めた。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "不採用の子孫は、親の完了を止めない"
		text:  "子孫が `completed` か `not-planned` で閉じていれば、親を `completed` で閉じられる。開いている子孫、または状態が分からない子孫があれば、今までどおり `DESCENDANT_NOT_COMPLETED` で止まる。`scope close` と `work finish` の両方で同じ判定にする。"
	}
	"R-02": {
		title: "判定の変更を文書とテストに書く"
		text:  "`reference_cli.md` などの `scope close` の説明と、`DESCENDANT_NOT_COMPLETED` の意味を直す。不採用の子孫があるとき閉じられること、開いている子孫があるとき止まることをテストで確かめる。"
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
