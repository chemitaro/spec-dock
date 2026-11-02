package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"利用者の無視されたファイルを、`--discard-ignored` の許可なしに消さない",
	"0.5.0 の公開の契約（コマンド、引数、エラーのコード、終了コード、JSON の形）を変えない（epic-00512 の constraints）",
]
current: """
	`canonical_worktrees.remove_worktree` は、unlock の前に1回だけ `_only_ignored_is_the_link` で「無視されたものは正しいリンクだけ」と判定し、真なら `discard_ignored=True` にした名前空間を `direct_worktrees._remove_captured_worktree` に渡す。
	`_remove_captured_worktree` の `verify_target` は、`discard_ignored` が真だと無視されたものの確かめを飛ばす。そのため、判定の後（unlock の後を含む）にできた無視されたファイルも `git worktree remove` が消す（Git は無視されたファイルを「きれい」と見て消す）。
	"""
target: "無視されたものの判定は、`_remove_captured_worktree` の各 `verify_target`（最初の確かめ、unlock の前の確かめ、unlock の後の確かめ）で毎回行う。リンクだけなら続け、ほかのものがあれば、今までと同じ例外で止まる。"

design: {
	"D-01": {
		title: "無視されたものを許す判定を、名前空間の真偽から、毎回呼ぶ判定に変える"
		text: """
			`_remove_captured_worktree` に、キーワード引数 `ignored_allowed: Callable[[bytes], bool] | None = None` を足す。`git ls-files --others --ignored --exclude-standard --directory -z` の出力を受け取り、`--discard-ignored` なしで消してよいかを返す。
			`namespace.discard_ignored` が偽のとき、無視されたものがあれば、`ignored_allowed` が与えられていて真を返す場合だけ続ける。最初の判定（今の「ignored worktree content requires --discard-ignored ...」）と `verify_target` の判定（今の「ignored worktree content changed before removal」）の両方で、同じ判定を使う。
			`verify_target(locked=False)` は unlock の後、`git worktree remove` の直前に呼ばれるので、判定は unlock の後に行われる。
			`canonical_worktrees.remove_worktree` は `discard_ignored` を書き換えず、`_only_ignored_is_the_link` を出力を受け取る形にして `ignored_allowed` に渡す。リンクが正しいかの確かめ（`resolve_layout` と `link_state`）も、毎回行う。
			canonical が `_remove_captured_worktree` の前に行っていた `git ls-files --others --ignored ...` の1回は残す。bare の main を対象にしたとき、この呼び出しが Git の失敗（`GIT_FAILED`・終了コード5）で止まる今の順序を変えないためで、結果は `discard_ignored` の判断には使わない（既存のテスト `test_remove_rejects_the_bare_main_of_a_clone_from_a_valid_linked_project` が固定している）。
			例外の文言とその扱いは変えない：try の外（最初の判定と最初の `verify_target`）の `ValueError` は `PRECONDITION_FAILED`・failed・終了コード3・effects 空、try の中（unlock の前の確かめ、unlock の後の確かめ）は `WORKTREE_REMOVE_FAILED`、unlock が成功していれば partial・終了コード6。
			既存のテスト `test_issue432_branch_followups.py::test_remove_runs_the_legacy_step_on_the_checked_record` は `_remove_captured_worktree` を位置引数5つの関数に差し替えているので、キーワード引数を受け取れるように直す（テストの差し替えの形の直しで、確かめる中身は変えない）。
			"""
		satisfies: ["R-01", "R-02", "R-03"]
	}
	"D-02": {
		title: "判定と削除の間の時間の扱い"
		text: """
			守る範囲：最初の判定から、最後の `verify_target`（unlock の後、`git worktree remove` の直前）までに増えた無視されたファイル。
			守らない範囲：最後の `verify_target` が返ってから、Git が実際にファイルを消すまでの短い間（Git の呼び出し1回分）。Git にファイルの集まりを固定して消させる手段がないため、ロックやファイルの記述子で閉じることはしない。未追跡のファイルは Git 自身が `worktree remove` を拒むので、この残りは無視されたファイルだけに関わる。
			"""
		satisfies: ["F-01"]
	}
}

compatibility: "公開のコマンド、引数、エラーのコード、終了コード、JSON の形は変わらない。動きの変化は、epic-00512 の constraints の「誤って書き込みや受け付けに進んでいた操作を止める直し」に当たる：今まで終了コード0で消していた「判定の後にできた無視されたファイル」がある場面で、`--discard-ignored` なしでは消さずに止まる（書き込みの前なら `PRECONDITION_FAILED`・終了コード3、unlock の後なら `WORKTREE_REMOVE_FAILED`・partial・終了コード6）。#513 は `migration.md` の 0.5.1 の節にこの1点を載せる。Epic の constraints の例外の一覧には #508 がないので、統括に報告して Epic 側で足してもらう。"
risks: [
	"F-01 の残りの時間は閉じない（D-02）",
	"`_remove_captured_worktree` は canonical のほかからは呼ばれない（従来モードは撤去済み）が、引数は既定値付きで足し、呼び出し元の今の動きを変えない",
]
