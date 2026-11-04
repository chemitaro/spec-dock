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
	reason: "版を出して配る作業で、問題があればパッケージを前の版に戻し、配布の PR を戻せば元に戻る"
}

// 目的と背景（任意）。
purpose:    "SpecDock 0.7.0（人のタスクの CLI `spec-dock todo`）を出し、5つのリポジトリで人のタスクの運用を始められるようにする。"
background: "epic-00547 の #549（CLI）・#550（集約）・#551（スキルと文書）と、#556（構造の図の既定）が main に入った。手順は #534（0.6.0）と同じ。マージの後のタグ、導入、配布、dogfooding の確かめは統括が行う。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "版が 0.7.0 になる"
		text:  "`pyproject.toml`、`uv.lock`、版のファイル `system/spec-dock-version` とその dogfood の写しが 0.7.0 になる。"
	}
	"R-02": {
		title: "上げるときの文書が 0.7.0 の変更を説明する"
		text:  "`migration.md`（提供側と dogfood の写しはバイト一致）に「## 0.7.0 への更新」の節があり、`todo` の10のコマンド（公開 61 → 71）、記録の置き場（カタログの `todos/`）、集約、`dashboard summary` の `todos`、設定の3段、`todo check` と `cue`、`TODO_*` のコード、スキルの入れ替えに `installation update` が要ること、ダッシュボードの表示の設定（#552）、構造の図の既定の変更と保存のキーの `v2`、最初の1手、戻し方を述べる。"
	}
	"R-03": {
		title: "0.6.0 の配布資産を持つリポジトリが `installation update` で上がる"
		text:  "`static-inventory.json` が、変わった配布資産の今のハッシュと、0.6.0 のバイトを既知の古い版として持つ。新しい `docs/todo.md` は補われる。"
	}
	"R-04": {
		title: "配布と dogfooding はマージの後に統括が行う"
		text:  "タグ、パッケージの導入、5つのリポジトリへの配布、利用者の PC での人のタスクの確かめは、この Issue の PR では行わない。"
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
