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
	reason: "試作と確かめだけで、製品のコードを出さない。結果は報告に残し、設計を直す材料にする。"
}

// 目的と背景（任意）。
purpose: "製品のコードを出さず、iframe 埋め込みの指の操作、枠の決まり、postMessage の約束を実際のブラウザーで確かめ、Epic 427 の設計を直す材料にする（Epic の F-13）。"
// purpose:    ""
// background: "解く問題と、関係者"

// 対象と対象外（任意）。
excludes: ["製品のコードとテストの変更", "逃げ道（普通のリンク）の実装（#531）", "Epic の文書の直接の修正（提案として report.md に書く）"]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "構造の図の指の操作（つまむ、移動、タップ）が、起点の違う iframe の中で効くかを確かめる"
		text:  "`touch-action: none`、Pointer Events、Safari の `gesturestart` の抑止（D-08）を、PC の Chrome（触る操作の模擬）、PC の Safari、iPhone の Safari で見る。"
	}
	"R-02": {
		title: "`frame-ancestors`、`sandbox` の資料の切り離し、`/ds/` の CORS の決まり（D-09）が、ブラウザーでそのとおりに働くかを確かめる"
		text:  "許した起点の親は埋め込め、許さない起点の親は止められる。`/files/` の資料は固有でない起点で動き、親の DOM と API に触れず、`/ds/` は読める。"
	}
	"R-03": {
		title: "postMessage の始まりの挨拶と戻る履歴（D-15）が、そのとおりに動くかを確かめる"
		text:  "`hello`、`ready`、`navigated`、`navigate`、`theme`。覚えた起点以外の知らせを捨てること、`hello` の前は何も送らないこと、iframe の中の移動が共通の履歴に入り、戻るで戻れること。"
	}
	"R-04": {
		title: "結果と、設計（D-08、D-09、D-15）への直しの提案、iPhone の実機の手順を report.md に書く"
		text:  "iPhone の実機は利用者の確かめ待ちにして、開くだけで確かめられるチェックリストと、Tailscale の IP で待ち受ける起動のしかたを書く。"
	}
}

// 失敗・境界の条件。番号（F-01、…）をキーにする。
// title は必須。impact（起きたときの影響）と recovery（回復のしかた）は strict 以上で必須。
failures: {
	"F-01": {
		title: "試しのサーバーを Tailscale の IP で待ち受けたまま残さない"
		text:  "試しが終わったらサーバーを止める。常駐させない。"
	}
}

// 制約・前提、合意した判断、未解決事項（任意）。
// constraints: ["..."]
// decisions: ["..."]
// questions: ["..."]
