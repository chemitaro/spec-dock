package spec

// 要件（Epic）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "strict"
	reason: "ダッシュボードから、メッセージの送信などの書き込みの操作をできるようにする。Tailscale を通して同じ tailnet の端末から操作が届くので、偽の要求や誤った相手への送信が、エージェントの作業とリポジトリに及ぶ。送った操作は取り消せないことがある。"
}

// 目的と背景（任意）。
purpose:    "Orca のエージェントとのチャット（セッションのログの表示と、メッセージの送信）を、SpecDock のダッシュボードと company-os のダッシュボードの中で使えるようにする（ダッシュボードの第3段階）。"
background: "2026-11-03 の利用者の決定：チャットは SpecDock の中に作らず、独立したサービス orca-web（epic-00471 の背景を参照）の試験的な部分として作る。この Epic は、SpecDock のダッシュボードで worktree とその中のセッション（Codex、Claude Code、OpenCode など）を選び、orca-web のチャットの画面を埋め込む側を受け持つ。埋め込みの方法（iframe か別のやり方か）は、この Epic で分析して決める。書き込み（送信）は orca-web の中で完結させ、SpecDock は見るだけのままにするかも、この Epic で決める。要件は、第2段階が終わる前に、利用者との聞き取りで具体化する。"

// 対象と対象外（任意）。
// includes: ["..."]
excludes: [
	"第1段階（epic-00427）と第2段階（epic-00471）の表示の機能",
]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	// "R-01": {
	// 	title: "利用者が〜できる"
	// 	text:  "詳しい説明"
	// 	acceptance: ["〜が観測できる"]
	// }
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
