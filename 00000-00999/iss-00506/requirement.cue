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
	reason: "端末での確認の後に状態が変わると、違う Issue やリポジトリに GitHub で書く。書いた後に戻すのが難しい。"
}

// 目的と背景（任意）。
purpose:    "`scope close`／`scope reopen`／`scope create` が、確認の後と GitHub に書く前に、直接の選択と `origin` を読み直し、変わっていれば何も書かずに止まる。"
background: "I-13（#440）でテストを canonical に書き直したとき、canonical の処理がこの読み直しをしないことが分かった（`iss-00440/report.md` の後続の候補 1〜3）。従来モードの処理は読み直していて、そのテストは撤去で消えた。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "確認の後に選択が変わったら `scope close`／`reopen` が止まる"
		text:  "`@current` を確認の前に解決したまま PATCH しない。確認の後に直接の選択を読み直し、変わっていれば何も書かずに止まる。"
		acceptance: ["`WriteWorld` で選択を確認の入力の間に変えると、GitHub に PATCH せずに止まることがテストで観測できる（元のテスト `test_issue413_scope_lifecycle.py::test_scope_lifecycle_refuses_a_changed_direct_selection_after_terminal_confirmation`）"]
	}
	"R-02": {
		title: "確認の後と作成の後に `origin` が変わったら `scope create` が止まる"
		text:  "GitHub の作成の前に `origin` を読み直し、変わっていれば POST しない。作成の後にリポジトリが変わっていれば、カタログに公開しない。"
		acceptance: ["確認の入力の間に `git remote set-url origin` を行うと POST しないことがテストで観測できる（元のテスト `test_scope_create_commands_vnext.py::test_github_create_confirmation_rejects_native_origin_change_before_post`）", "作成の間にリポジトリが変わると、カタログに公開しないことがテストで観測できる（元のテスト `test_issue413_scope_publish.py::test_repository_change_during_create_keeps_the_confirmed_old_ref_without_local_publication`）"]
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
