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
	reason: "版の番号と、上げるときの文書だけを変える。動きの変更は #493・#494・#495 で済んでいて、戻すときは 0.4.1 を入れ直せばよい。"
}

// 目的と背景（任意）。
// purpose:    "この Issue が実現する価値"
// background: "解く問題と、関係者"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "版が 0.4.2 になる"
		text:  "`pyproject.toml`、`uv.lock`、配布する版のファイル `system/spec-dock-version` とその dogfood の写しが 0.4.2 になる。"
	}
	"R-02": {
		title: "上げるときの文書が 0.4.2 の変更を説明する"
		text:  "`migration.md` に「## 0.4.2 への更新」の節があり、#493（OS 由来の不要ファイルを同期しない、`canonical status` の `changes.junk_files`、`canonical remove` の `CANONICAL_IGNORED_FILES_PRESENT`）と #494（CI の見本の費用の注記と `canonical.md` の節）の要点、`installation update` で配布資産を上げることを述べる。"
	}
	"R-03": {
		title: "0.4.1 の配布資産を持つリポジトリが `installation update` で上がる"
		text:  "`static-inventory.json` が今のバイトのハッシュと、0.4.1 のバイトを既知の古い版として持つ。"
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
