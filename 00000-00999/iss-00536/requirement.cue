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
	reason: "版の番号と文書だけを変え、配るのは通常の PR。戻すときは 0.6.0 を入れ直し、配る PR を git revert すればよい。"
}

// 目的と背景（任意）。
purpose:    "SpecDock 0.8.0（文書の描画 #535 と人のタスクの画面 #554）を出し、epic-00547 の iss-00555（画面の版のリリース）も兼ねる。"
background: "0.7.0 の後に #535・#554 が main に入った。リリースは1つにまとめる（統括の決定）。手順は #553（0.7.0）と同じ。マージの後のタグ、導入、配布は統括が行う。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "版が 0.8.0 になる"
		text:  "`pyproject.toml`、`uv.lock`、`system/spec-dock-version`（提供側と dogfood の写し）が 0.8.0 になる。"
	}
	"R-02": {
		title: "migration.md が 0.8.0 の変更を説明する"
		text:  "提供側と dogfood の `migration.md`（バイト一致）に「## 0.8.0 への更新」の節がある。文書の描画（#535）、人のタスクの画面（#554）、常駐の自動の起動し直しを述べ、#567 は main にマージ済みのときだけ書く。"
	}
	"R-03": {
		title: "0.7.0 の配布資産を持つリポジトリが installation update で上がる"
		text:  "`static-inventory.json` が変わった配布資産（`reference_cli.md`、`migration.md`、版のファイル）の今のハッシュと、0.7.0 のバイトを既知の古い版として持つ。"
	}
	"R-04": {
		title: "タグ・導入・配布は統括が行う"
		text:  "マージの後のタグ、パッケージの導入、5つのリポジトリへの配布は、この Issue の PR では行わない。"
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
