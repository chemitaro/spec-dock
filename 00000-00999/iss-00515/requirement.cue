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
	reason: "Linux の環境で確かめるだけで、製品は変えない。見つかった不具合は別の Issue にする。"
}

// 目的と背景（任意）。
purpose:    "Linux で、canonical モードの定期の同期と、Codex のサンドボックスの中の操作が動くことを確かめる。"
background: "epic-00424 の設計の「未確認の事項」に残った2件。systemd のユーザーのタイマーが動くことは確かめたが、そこからの GitHub への push の認証は確かめていない。Linux の Codex のサンドボックス（Landlock）の中で、ディレクトリへの `flock` が効くかも確かめていない。今の利用者の環境は macOS だけなので、急がない。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "systemd のタイマーから push できる"
		text:  "systemd の動く Linux で `canonical link` が登録したユーザーのタイマーから、`spec-dock canonical sync` が GitHub に push できる（認証の設定のしかたを含めて記録する）。"
	}
	"R-02": {
		title: "Codex のサンドボックスの中でカタログの排他が効く"
		text:  "Linux の Codex のサンドボックス（Landlock）の中で、カタログのディレクトリへの `flock` が効き、仕様の読み書きができる。効かなければ、`canonical status` が示す1行の設定で回避できるかを確かめる。"
	}
	"R-03": {
		title: "Codex の1行の設定が、実際の Codex のセッションで効く"
		text:  "`canonical status` が示す Codex の1行（`writable_roots = [\"<カタログ>\"]`）を `~/.codex/config.toml` に足すと、main のチェックアウトの外の worktree で動く実際の Codex のセッションが、カタログの仕様を読み書きできる（macOS と Linux）。epic-00424 の AC-07 で、表示と文書は確かめたが、実際のセッションでは確かめていない（`iss-00436/report.md` の「未確認」）。設定の形が権限のプロファイルに移っていれば、`canonical status` の案内の直しを別の Issue にする。"
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
