package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"canonical の `scope delete` と `artifact create` が、途中の失敗で、実際に起きたことを effects と status に出す",
	"0.5.0 の公開の契約は、epic-00512 の constraints が認めた直し（#507 の `failed` を `partial` にすること）のほかは変えない",
]
current: """
	`canonical_scope_change.py` の `scope delete` は、`with WorkTargetStore(...) as store:` の中で `remove_observed()` を呼び、`selection.clear` の effect を `with` を出た後に足す。`__exit__` の `os.close` が OSError を投げると、記録は消えているのに effect が足されず、`session.incomplete` が残りの手順として `selection.clear not_attempted` と報告する。
	同じ処理は、`remove_tree` が投げた `TreeRemovalIncomplete` の `applied` が空なら `scope.delete` の effect を足さない。最初の unlink（または rmdir）が効いた後に例外になると `applied` は空で `attempted` が真なので、Scope のディレクトリは途中まで消えているのに `scope.delete not_attempted` と報告する。
	`canonical_artifact_write.py` の `artifact create`／`artifact import file` は、`artifacts/` の `os.mkdir` と `os.fsync` の後の失敗（publication の前）を、`failed`（OSError なら終了コード5、`LOCAL_IO_FAILED`、effects 空）で返す。作ったディレクトリのことは報告しない。
	"""
target: "上の3つの場面で、`selection.clear succeeded`、`scope.delete unknown`、`partial`（終了コード6、`ARTIFACT_PUBLICATION_INCOMPLETE`、`artifact.directory` が succeeded か unknown）を返す。作ったディレクトリと控えは残す。"

design: {
	"D-01": {
		title: "`selection.clear` の結果を、記述子を閉じる前に記録する"
		text: """
			`scope delete` の `--clear-active` の処理で、`remove_observed()` の結果の判定（`conflict` なら `selection.clear failed` を足して止まる。`removed` なら succeeded、`already_absent` なら unchanged を足す）を、`with WorkTargetStore(...)` の中に移す。
			これで、`__exit__` の close が OSError を投げても、確かめた削除は `selection.clear succeeded` として残り、OSError は今までどおり `SCOPE_DELETE_INCOMPLETE`（partial、終了コード6）の原因になる。残りの手順（`scope.delete` など）は not_attempted のまま。
			`SelectionRemovalUnknown` の扱い（`selection.clear unknown`）は変えない。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "Scope のディレクトリの削除を試みたかを、`attempted` でも判定する"
		text: """
			`TreeRemovalIncomplete` を受けたとき、`error.applied` が空でなくても、`error.attempted` が真でも、そのディレクトリを試みたものとして扱う：`changes.delete(relative)` を記録し、`scope.delete unknown` を足す。どちらも偽（確かめの段階で止まった）なら、今までどおり effect を足さず、残りの手順として not_attempted になる。
			`remove_tree` の `attempted` は、各項目の確かめの前に偽に戻り、`os.unlink`／`os.rmdir` を呼ぶ直前に真になるので、確かめで止まった場合を試みたとは扱わない。
			`changed_paths` には足さず、`remaining_paths` に残す（`scope.delete unknown` の今の扱いと同じ）。
			"""
		satisfies: ["R-01"]
	}
	"D-03": {
		title: "`artifacts/` を作った後の失敗を partial で返す"
		text: """
			`_publish_scope_artifact` で、`os.mkdir("artifacts", dir_fd=...)` を呼ぶ前に `directory_attempted` を真にし、成功したら `created_directory` を真にする。`FileExistsError` なら `directory_attempted` を偽に戻す（前からあったディレクトリは作っていない）。
			`LOCAL_FAILURES` を受けたとき、`directory_attempted` が真なら partial（終了コード6、`ARTIFACT_PUBLICATION_INCOMPLETE`、今と同じ recovery）にし、effects の先頭に `artifact.directory`（`created_directory` なら succeeded、でなければ unknown。target は `spec-dock/initiatives/<区切り>/<ID>/artifacts`）を置く。続けて `artifact` の effect を、publication を試みていなければ not_attempted、試みていれば今と同じ判定（succeeded／unknown／failed）で置く。
			作ったディレクトリは消さない。`data.result` は今と同じ（`artifact` は publication が確かめられたときだけ、`changed` はその真偽）。`artifacts/` が前からあった場合と、ディレクトリを作る前の失敗（カタログのロックなど）の扱いは変えない。
			`@root` の `direct_artifact.mutate_artifact` は、もとからこの形で返すので変えない。
			"""
		satisfies: ["R-02"]
	}
}

compatibility: """
	変わる契約（#513 が `migration.md` の 0.5.1 の節に載せる）：
	- `artifact create` と `artifact import file`（Scope の Artifact）で、`artifacts/` を作った後、publication を始める前か publication が確かめられずに失敗したとき：今は `status: failed`、終了コード5（OSError）か3（ValueError）、`error.code` が `LOCAL_IO_FAILED` などで、effects は空か `artifact failed`。0.5.1 では `status: partial`、終了コード6、`error.code: ARTIFACT_PUBLICATION_INCOMPLETE`、`recovery` あり、effects は `artifact.directory`（succeeded か unknown）と `artifact`（not_attempted か failed か unknown）。
	- `scope delete`：エラーのコードと終了コード（`SCOPE_DELETE_INCOMPLETE`、6）は変わらない。effects の status だけが、起きたことに合わせて変わる（記録を消した後の close の失敗で `selection.clear` が not_attempted から succeeded に、最初の unlink の後の例外で `scope.delete` が not_attempted から unknown に）。
	コマンド、引数、JSON の形は変わらない。`artifact.directory` は `@root` の Artifact が今も返す effect の種類。
	"""
risks: [
	"#506 も `canonical_scope_change.py` を直す。ぶつかったら、後にマージするほうが main を取り込む",
	"`artifact create` の failed を partial にするのは、`artifacts/` を新しく作った場合だけ。前からある場合は変わらない",
]
