package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"端末での確認の後に状態が変わったとき、確認していない対象やリポジトリに GitHub で書かない",
	"止め方（エラーのコード、終了コード、effects）は撤去の前の従来の処理（`caaeebe45` の `direct_scope_lifecycle.py` と `direct_scope_publish.py`）に合わせ、0.5.0 の公開の契約をほかに変えない（epic-00512 の constraints）",
]
current: """
	`canonical_scope_change.lifecycle_scope` は、`session.selection()` で選択を1回だけ読み、`@current` を解決し、`confirmed_interactively` の後にそのまま PATCH する。確認の入力の間に `work start` で選択が変わっても、古い対象を閉じる（開き直す）。
	`canonical_scope_create.create_scope` は、`open_write_session` の `repository_for_checkout` で `origin` を1回だけ読み、確認の後もラベルの作成、Issue の POST、親への追加、カタログへの公開まで読み直さない。
	"""
target: """
	`scope close`／`scope reopen` は、端末で確認したとき、確認の後に選択を読み直し、変わっていれば何も書かずに止まる。
	`scope create` は、確認の後（ラベルの作成の前）と POST の直前と、POST の後（親への追加とカタログへの公開の前）に `origin` を読み直し、変わっていれば、それより先を書かずに止まる。
	"""

design: {
	"D-01": {
		title: "`scope close`／`reopen` の、確認の後の選択の読み直し"
		text: """
			`lifecycle_scope` で、`confirmed_interactively` が真を返し、かつ `--yes` なしで端末に問うたとき（`namespace.yes` が偽）、`session.selection()` を読み直す。最初の観測と `(status, record, handle)` が違えば、`ValueError("direct selection changed during confirmation")` を投げる（従来の文言のまま）。
			この例外は GitHub の書き込みの前なので、`runtime_dispatch` の既存の変換で `PRECONDITION_FAILED`・failed・終了コード3・effects 空になる（従来と同じ）。選択の記録、GitHub、カタログは変えない。
			比べるのは選択子によらない（`@current` でも ID でも）。従来も、確認の前の観測と違えば止めていた。`--yes` のときは問わないので読み直さない（従来と同じ）。
			`--expect-current` の確かめ（`check_expectations`）は確認の前のまま残す。確認の後の読み直しで、確認の後の変化も止まる。
			比べ方は小さな関数 `selection_unchanged(before, after)` として `canonical_writes.py` に置く。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "`scope create` の、確認の後と POST の前の `origin` の読み直し"
		text: """
			`WriteSession` に `require_same_repository()` を足す。`repository_for_checkout(context.root)` を読み直し、`slug` が `session.repository.slug` と違えば `ValueError("GitHub repository changed during Scope creation")` を投げる（従来の文言のまま）。`origin` が読めない・形が違うときは、`repository_for_checkout` の今の例外（`ValueError` か `GitProcessError`）をそのまま投げる。
			`create_scope` は、確認の後（`--yes` でも）、`ensure_labels` の前に1回、`create_issue` の POST の直前に1回呼ぶ。POST の直前の呼び出しは `session.write` に渡す関数の中ではなく、その前に置く（GitHub の失敗と区別するため）。
			どちらも GitHub への書き込みの前（ラベルの作成の後の POST の前の場合を除く）なので、`runtime_dispatch` の既存の変換で `PRECONDITION_FAILED`・failed・終了コード3になる（従来と同じ）。ラベルを作った後の POST の前に止まったときは、ラベルの作成が effects に残るので、`session.incomplete` で partial・終了コード6・`CANONICAL_WRITE_INCOMPLETE` を返す（今のラベル作成の後の失敗の扱いと同じ形）。
			"""
		satisfies: ["R-02", "F-01"]
	}
	"D-03": {
		title: "`scope create` の、POST の後の `origin` の読み直し"
		text: """
			POST が成功した後、親への追加（`github.sub-issue.add`）の前と、カタログへの公開（`_publish`）の前に `require_same_repository()` を呼ぶ。今の `try` の中なので、`WRITE_FAILURES` に含まれる `ValueError` として捕まり、`session.incomplete(..., code="SCOPE_PUBLICATION_INCOMPLETE")` で返る。
			結果：status partial、終了コード6、エラーのコード `SCOPE_PUBLICATION_INCOMPLETE`、effects は `github-create succeeded`（対象は確認したリポジトリ）と、残りの手順（`github.sub-issue.add`、`scaffold`）の `not_attempted`、`data.result.github_ref` は確認したリポジトリの ref（例 `gh:example/repo#57`）、カタログにディレクトリを作らず changeset も書かない。従来のテストの観測（終了コード6、effects の最初が succeeded、次が not_attempted、公開しない、POST 1回）と同じ。
			次の1手（recovery）は、今の「`scope import github ...` を実行する」の前に「`origin` を確認したリポジトリ（`example/repo`）に戻す」を置く。次の1手の `scope import github` は番号だけを渡し、番号はその時点の `origin` のリポジトリで解釈されるので、`origin` が違うままでは別のリポジトリの同じ番号の Issue を取り込みうるため。この1文は `RepositoryChanged`（`ValueError` の子）が `recovery` として持ち、今の `CanonicalCommandError` の `recovery` と同じく先頭に並べる。
			"""
		satisfies: ["R-02", "F-01"]
	}
}

compatibility: """
	公開のコマンド、引数、エラーのコードの種類、終了コードの意味、JSON の形は変わらない。動きの変化は、epic-00512 の constraints の「誤って書き込みや受け付けに進んでいた操作を止める直し」に当たる。#513 が `migration.md` の 0.5.1 の節に載せる点：
	(1) `scope close`／`scope reopen` を端末で確認したとき、確認の間に直接の選択が変わると、`PRECONDITION_FAILED`（終了コード3、effects 空、GitHub に書かない）で止まる。
	(2) `scope create` で、確認の後や POST の前に `origin` のリポジトリが変わると、Issue を作らずに止まる。GitHub にまだ何も書いていなければ `PRECONDITION_FAILED`（failed、終了コード3、effects 空）。種類のラベルを作った後なら `CANONICAL_WRITE_INCOMPLETE`（partial、終了コード6、effects は `github.label.create succeeded` と `github-create`・`scaffold` の `not_attempted`）。
	(3) `scope create` で、POST の後（親への追加の前、またはカタログへの公開の前）に `origin` のリポジトリが変わると、`SCOPE_PUBLICATION_INCOMPLETE`（partial、終了コード6）で止まり、それより先の親への追加とカタログへの公開をしない。effects は、済んだ手順の `succeeded` と残りの手順の `not_attempted`。`data.result.github_ref` は確認したリポジトリの ref。recovery の先頭は「`origin` を確認したリポジトリに戻す」案内で、その後に今までの `scope import github` の案内が続く。
	"""
risks: [
	"F-01 の、最後の読み直しから GitHub の要求までの短い間は閉じない（Git と GitHub の呼び出しを不可分にする手段がない）",
	"#520 が同じ `lifecycle_scope` の子孫の判定を直す。後にマージするほうが main を取り込む",
	"`scope import github` は確認を問わないので、この Issue では読み直しを足さない（要件の範囲の外）",
]
