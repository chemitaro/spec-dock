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
			例外の文言とその扱い（`ValueError`、unlock の前なら failed・終了コード3、unlock の後なら partial・終了コード6、`WORKTREE_REMOVE_FAILED`）は変えない。
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

compatibility: "公開の契約は変わらない。止まる場合は、既存のエラー（`WORKTREE_REMOVE_FAILED`）、終了コード、effects のまま。今まで消していた「判定の後にできた無視されたファイル」を消さずに止まることだけが、動きの変化（誤って進んでいた操作を止める直し）。`migration.md` の 0.5.1 の節に書くなら「`worktree remove` は、判定の後にできた無視されたファイルがあると、`--discard-ignored` なしでは消さずに止まる（コード、終了コード、JSON は変わらない）」。"
risks: [
	"F-01 の残りの時間は閉じない（D-02）",
	"`_remove_captured_worktree` は canonical のほかからは呼ばれない（従来モードは撤去済み）が、引数は既定値付きで足し、呼び出し元の今の動きを変えない",
]
