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
	reason: "版の番号と文書だけを変え、配るのは通常の PR。戻すときは 0.5.0 を入れ直し、配る PR を git revert すればよい。"
}

// 目的と背景（任意）。
purpose:    "SpecDock 0.5.1 を出し、5つのリポジトリの配布資産を 0.5.1 にそろえる。"
background: "epic-00512 の直し（#506〜#511）を、1回のリリースで届ける。手順は #501（0.4.2）と #440（0.5.0）と同じ。配布の PR で、利用者のリポジトリの古い記述（input-devices の `README.md` の `4d25a8b` の固定、company-os の `contract.md` の 0.2.4）も直す。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "版が 0.5.1 になる"
		text:  "`pyproject.toml`、`uv.lock`、版のファイル `system/spec-dock-version` とその dogfood の写しが 0.5.1 になる。"
	}
	"R-02": {
		title: "上げるときの文書が 0.5.1 の変更を説明する"
		text:  "`migration.md` に「## 0.5.1 への更新」の節があり、#506〜#511 の要点と、契約の変更（あれば）を述べる。"
	}
	"R-03": {
		title: "0.5.0 の配布資産を持つリポジトリが `installation update` で上がる"
		text:  "`static-inventory.json` が、変えた配布資産の今のハッシュと、0.5.0 のバイトを既知の古い版として持つ。"
	}
	"R-04": {
		title: "5つのリポジトリが 0.5.1 にそろう（マージの後に統括が行う）"
		text:  "利用者の環境に 0.5.1 を入れ、4つのリポジトリで `installation update` の PR を作り、`canonical check` と検査のワークフローを通す。"
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
