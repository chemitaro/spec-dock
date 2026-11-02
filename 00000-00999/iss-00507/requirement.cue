package spec

// 要件（Issue）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。
// 文章の項目には Markdown を書いてよい。型にない項目は、必要に応じて足してよい。

// 型の版。消さない。
schema: "specdock/v1"

// 保証レベル（light、standard、strict、critical）と、その理由。
// 失敗したときの影響と回復の難しさで選ぶ（工数や作業の難しさでは選ばない）。
// 具体化や作業の途中で、上げても下げてもよい。正本はここだけで、ほかの場所に写さない。
assurance: {
	level:  "standard"
	reason: "途中の失敗で、結果の effects が実際の状態と食い違うと、利用者とエージェントが回復の手を誤る。"
}

// 目的と背景（任意）。
purpose:    "canonical の `scope delete` と `artifact create` が、途中で失敗したときに、実際に起きたことを effects と status で正しく返す。"
background: "I-13（#440）で見つかった（`iss-00440/report.md` の後続の候補 4、5）。従来モードの処理は正しく返していて、そのテストは撤去で消えた。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "`scope delete` が、消えた記録と途中まで消えたディレクトリを正しく報告する"
		text:  "`WorkTargetStore.remove_observed()` が removed を返した後に記述子の close が失敗しても `selection.clear` を succeeded と報告する。Scope のディレクトリの最初の unlink が効いた後の例外では、`scope.delete` を not_attempted にしない（`TreeRemovalIncomplete.attempted` を見る）。"
		acceptance: ["close の失敗を注入したテストで `selection.clear` が succeeded になることが観測できる（元のテスト `test_issue413_scope_delete.py::test_confirmed_direct_clear_survives_a_later_descriptor_cleanup_failure`）", "最初の unlink の後の例外で、`scope.delete` が試みた状態として報告されることがテストで観測できる"]
	}
	"R-02": {
		title: "`artifact create` が、ディレクトリを作った後の失敗を partial で返す"
		text:  "`artifacts/` を作った後の失敗は、`partial` で返し（`artifact.directory` は、作ったことが確かめられていれば succeeded、mkdir の結果が分からなければ unknown）、作ったディレクトリを残す。今は `failed`（終了コード5、effects 空）になる。"
		acceptance: ["失敗を注入したテストで `partial` と `artifact.directory unknown` が観測できる（元のテスト `test_issue413_artifact.py::test_uncertain_artifact_directory_creation_reports_partial_and_preserves_it_without_publication`）"]
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
