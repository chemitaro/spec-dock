package spec

// 要件（Epic）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "SpecDock の画面に、別のサービス orca-web から読んだエージェントの稼働を重ねて示し、orca-web の「Orca で開く」のボタンを埋め込む。SpecDock 自身は見るだけのままで、誤りは表示の誤りか、埋め込みの不具合にとどまり、版を戻せば回復できる。"
}

// 目的と背景（任意）。
purpose:    "SpecDock のダッシュボード（epic-00427）に、Orca のエージェントの稼働状況と連携の状態を重ねて示し、各エージェントのセッションを Orca のアプリで開くボタンを置く（ダッシュボードの第2段階）。"
background: """
	2026-11-03 の利用者の決定（epic-00427 の `.workbench/architecture-synthesis-20261103.md` と requirement.cue の decisions）：

	- ダッシュボードは3つの段階で進める。第1段階（epic-00427）は SpecDock の資源だけを見る。第2段階（この Epic）は Orca と連携して、エージェントの稼働と連携の状態を示す。第3段階（epic-00526）は、Orca のエージェントとのチャット（ログの表示と送信）を埋め込む。
	- Orca を外から操作する機能は、SpecDock の中に作らず、独立したサービス **orca-web**（仮の名前。新しいリポジトリ、Tailscale の中だけで配る）に作る。orca-web は、堅実な核（Orca の状態を読む口と、「Orca で開く」の操作）と、試験的な部分（チャット）を持つ。SpecDock と company-os（nestboard）は、orca-web の画面と部品を埋め込んで使う。
	- 「Orca で開く」のボタンは orca-web が配る小さな部品で、押した端末に合わせて振る舞う。ホストの Mac ならホストの Orca、Orca でつないだクライアントの PC ならそのクライアントの Orca、iPhone なら iPhone の Orca のアプリを開く。端末の見分けは、ブラウザーから orca-web へ直接届く要求で行う（2026-10-25 の試作 `worktrees/orca/orca-link-url-trial`）。
	- この Epic で SpecDock は見るだけのまま（`GET` だけ）で、Orca の状態は orca-web の読む口から取る。Orca の CLI を直接呼ばない。Scope と worktree の対応は SpecDock が決める。

	要件は、この Epic を始めるときに、orca-web の核の契約に合わせて具体化する。orca-web の開発そのものは、orca-web のリポジトリで管理する。
	"""

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

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
decisions: [
	"2026-11-03（epic-00427 のデザインの決定から）：構造の図とボードに、作業中の worktree の最後の更新の時刻は出さない。代わりに、この段階で、Orca のエージェントが作業を終えてから何もしていない待ち時間を、数え上げ（例「12分」）で箱に示す。要件にするときに、待ち時間の起点（エージェントの完了の時刻）を orca-web の読む口から取れるかを確かめる",
]
// questions: ["..."]
