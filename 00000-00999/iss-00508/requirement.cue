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
	reason: "利用者の無視されたファイルを、許可なしに消しうる（データの失われ）。"
}

// 目的と背景（任意）。
purpose:    "`worktree remove --unlock` が、unlock の後にできた無視されたファイルを、`--discard-ignored` なしで消さない。"
background: "I-13（#440）で見つかった（`iss-00440/report.md` の後続の候補 6）。unlock の前に「無視されたものはリンクだけ」と判定して `discard_ignored` を真にするため、unlock の後にできたファイルも消しうる。撤去の前のコードも同じ。"

// 対象と対象外（任意）。
// includes: ["..."]
// excludes: ["..."]

// 観測できる要件。番号（R-01、R-02、…）をキーにする。
// title は必須。acceptance（観測できる受け入れの条件）は standard 以上で必須。
requirements: {
	"R-01": {
		title: "無視されたものの判定を unlock の後に行う"
		text:  "unlock の後に、無視されたものがリンクだけかを判定する。ほかのものがあれば、`--discard-ignored` なしでは何も消さずに止まる。"
		acceptance: ["unlock の後に無視されたファイルを作るテストで、`--discard-ignored` なしの `worktree remove --unlock` がそのファイルを残して止まることが観測できる（元のテスト `test_issue413_worktree_remove.py::test_remove_preserves_ignored_content_created_after_unlock`）"]
	}
	"R-02": {
		title: "ロックのない worktree でも、最初の判定の後に増えた無視されたファイルを消さない"
		text:  "ロックのない worktree の `worktree remove`（`--discard-ignored` なし）でも、最初の判定の後、削除の直前の確かめまでに無視されたファイルが増えたら、何も消さずに止まる。原因は R-01 と同じ（最初の判定で `discard_ignored` を真にして、後の確かめを飛ばす）。"
		acceptance: ["最初の判定の後に無視されたファイルを作るテストで、`--discard-ignored` なしの `worktree remove` が `git worktree remove` を呼ばずに、そのファイルを残して止まることが観測できる"]
	}
	"R-03": {
		title: "リンクだけのときの今の動きと公開の契約を変えない"
		text:  "無視されたものが正しい `spec-dock/initiatives` のリンクだけなら、今までどおり `--discard-ignored` なしで消せる。`--discard-ignored` を付けたときの動きも変えない。止まるときのエラーのコード、終了コード、effects、JSON の形は、既存の止まり方のままにする：書き込みの前（最初の判定と、try の外の最初の確かめ）で止まれば `PRECONDITION_FAILED`・failed・終了コード3・effects 空、unlock の後で止まれば `WORKTREE_REMOVE_FAILED`・partial・終了コード6（unlock succeeded、remove not_attempted）。bare の main を対象にしたときの拒否（Git の失敗、`GIT_FAILED`・終了コード5）も変えない。"
		acceptance: ["リンクだけの worktree が、ロックあり（`--unlock`）とロックなしの両方で `--discard-ignored` なしに消えることが観測できる", "既存の `tests/cli_runtime/test_issue440_g3_worktree_remove.py` が変えずに通る"]
	}
}

// 失敗・境界の条件。番号（F-01、…）をキーにする。
// title は必須。impact（起きたときの影響）と recovery（回復のしかた）は strict 以上で必須。
failures: {
	"F-01": {
		title:    "最後の確かめと `git worktree remove` の間に、無視されたファイルが増える"
		text:     "SpecDock の確かめと Git の削除は1つの不可分の操作ではないので、最後の確かめの後、Git が消すまでの短い間に作られたファイルは守れない。この Issue は、確かめを削除の直前（unlock の後）に置き、間を Git の呼び出し1回に縮める。"
		impact:   "その短い間にできた無視されたファイルが消えうる"
		recovery: "防げない残りとして design.cue の risks に書く。消すべきでないファイルがある worktree は、ロックしたままにしておけば `--unlock` なしでは消えない"
	}
}

// 制約・前提、合意した判断、未解決事項（任意）。
// constraints: ["..."]
// decisions: ["..."]
// questions: ["..."]
