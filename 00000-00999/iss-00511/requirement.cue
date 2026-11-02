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
	reason: "文書とテストの食い違いと不足だけを直す。動きは変えない。"
}

// 目的と背景（任意）。
purpose:    "0.5.0 の撤去の後に残った文書の古い記述を直し、撤去の不在を確かめるテストの不足を埋める。"
background: "I-13（#440）の最終品質ゲートの P2・P3 と書き手の指摘（`iss-00440/report.md` の後続の候補 9〜11、13、14）。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "文書の古い記述を直す"
		text:  "README.md:9 の「現行CLIの全55コマンド」を 53 に直し、それを固定する `tests/unit/infra/test_issue477_authoring_docs.py` も直す。`docs/github-issue-integration.md:7` の local backend とローカル metadata の記述を直す。`pyproject.toml` の package-data に残る、外した `templates/{initiative,epic,issue}/.workbench/README.md` のパターン3行を外す。"
	}
	"R-02": {
		title: "撤去の不在と雛形のバイトを確かめるテストを足す"
		text:  "配布する文書の全体で、外したコマンドと引数（`workspace migrate`、`workbench copy`、`--ci`、`--source local`、`.meta.json` の作成）が案内されていないことを確かめる。作った CUE の `report.md` のバイトを 0.4.2 の出力と比べる。"
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
questions: ["wheel から入れたコンソールで、canonical の `work start`／`work finish` を通す e2e のテストを足すか（本物の定期の実行に触れずに子のプロセスで動かす手段が要る。候補 14）"]
