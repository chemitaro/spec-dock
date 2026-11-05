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
	reason: "配置の決まりを最上位にも広げるだけ"
}

// 目的と背景（任意）。
purpose:    "構造の図で Initiative も画面の幅に合わせて横に並べ、画面をシンプルでコンパクトに使えるようにする"
background: "Initiative の中の Epic は画面の幅で折り返して横に並ぶ（#560）が、Initiative どうしは、中の Epic が幅いっぱいに広がるため縦に積まれる。利用者の要望（2026-11-05、epic-00573）"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "Initiative が、画面の幅に収まる分だけ横に並ぶ"
		text:  "最上位の Initiative を、画面の幅（倍率100%で見える幅）に収まる分だけ横に並べ、収まらなければ次の行へ折り返す。行の残りの幅に収まる Initiative は、その幅で作り直して同じ行に置く。ただし、下の行に積むより高くなるときは置かない。"
		acceptance: ["Initiative が4つ（それぞれ Epic 1つに Issue 4つ）の構造で、幅1400で、ほかの Initiative と並ぶ Initiative の x が重ならず、同じ行に2つ以上並ぶ", "残りの幅が最小幅（420）に足りない幅1000と、幅374では、Initiative が縦に積まれる"]
	}
	"R-02": {
		title: "並べ方の決まりは #560 と同じ"
		text:  "依存でつながった Initiative はつながりの順に同じ行に左から右へ、つながっていないまとまりは活動順に左から並べ、幅を超えるところでまとまりの境目で折り返す。まとまりの中は割らない。"
		acceptance: ["依存でつながった Initiative の鎖が1行に残る", "つながっていない Initiative は活動順に左から並ぶ"]
	}
	"R-03": {
		title: "幅が変わったときだけ並べ直す"
		text:  "並べ直しは、見えている幅が変わったときだけ行う。線の配線で通路を広げる間は、最初に決めた幅のままにする。"
		acceptance: ["edgeAudit の違反が、代表的な構造のすべての見せ方で0のまま", "配線の広げ直しの前後で、Initiative の幅が変わらない"]
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
constraints: ["編集の範囲は views/graph*、tests/、この Issue の Scope だけ", "版の番号と migration.md は変えない"]
decisions: ["Initiative が1つなら今までと同じ", "依存でつながった Initiative のまとまりの中は、幅を分けず今までの幅を使う"]
// questions: ["..."]
