package spec

// 計画（Issue）。型 specdock/v1。

goal: "OS の不要なファイルを、すべての既存のカタログで、同期が新しく保存しないようにし、すでに保存されたものを見つけて消せるようにする"

steps: {
	"S-01": {title: "規則 `is_os_junk` と、削除の保留の除外を作る（D-01、D-05）", realizes: ["R-01", "R-04"], status: "todo", session: "impl"}
	"S-02": {title: "同期の保存の候補から、まだツリーにない不要なファイルを外す（D-02）", realizes: ["R-01"], status: "todo", after: ["S-01"], session: "impl"}
	"S-03": {title: "未保存の数と `work finish` の確かめから外し、`canonical status` に `junk_files` を足す（D-03、D-04）", realizes: ["R-02", "R-03"], status: "todo", after: ["S-01"], session: "impl"}
	"S-04": {title: "`canonical remove` が残った不要なファイルで止まる（D-06）", realizes: ["F-01"], status: "todo", after: ["S-03"], session: "impl"}
	"S-05": {title: "配布の文書、`static-inventory.json`、dogfood の写しを直す（D-07）", realizes: ["R-01", "R-02"], status: "todo", after: ["S-02", "S-03"], session: "impl"}
}

tests: {
	"T-01": {title: "`is_os_junk` が一覧の名前（大文字と小文字を問わず、どの深さでも）を真とし、似た名前の仕様のファイルを偽とする（`tests/unit/domain/test_canonical_sync_rules.py`）", verifies: ["R-01"]}
	"T-02": {title: "カタログに `.DS_Store`、`Thumbs.db`、`._x.md` と普通のファイルを置いて同期を2回実行すると、GitHub のツリーに普通のファイルだけが入り、`canonical status` の `unsaved` が 0（`tests/cli_runtime/test_issue430_canonical_sync.py`）", verifies: ["R-01", "R-03"]}
	"T-03": {title: "ツリーに `.DS_Store` があるとき `canonical status` の `changes` が `problem` で `junk_files` と次の1手を示し、消して同期すると削除が保存されて指摘が消える（`tests/cli_runtime/test_issue429_canonical_status.py`）", verifies: ["R-02"]}
	"T-04": {title: "Scope の場所に未追跡の `.DS_Store` だけがあるとき、`_unsaved_places` が未保存と見ない（`tests/cli_runtime/` の work finish のテスト）", verifies: ["R-03"]}
	"T-05": {title: "保存済みの不要なファイルの削除25件は `classify_holds` で保留にならない（単体）。ほかのファイルの削除25件は今までどおり保留になる。同期で、保存済みの `.DS_Store` 25件を消すと保留にならず削除が push される（`tests/cli_runtime/test_issue430_canonical_sync.py`）", verifies: ["R-04"]}
	"T-06": {title: "未追跡の `.DS_Store` が残るカタログで `canonical remove` が `CANONICAL_IGNORED_FILES_PRESENT` でパスを名指し、何も消さない", verifies: ["F-01"]}
	"T-07": {title: "提供側の文書と dogfood の写しが同じで、`static-inventory.json` の sha256 が合う（既存の配布資産のテスト）", verifies: ["R-01", "R-02"]}
}

verification: "TDD で各テストを先に赤にしてから実装する。`make lint` と `uv run pytest`（全体）を通す。コードのレビュー（code-review）と最終品質ゲート（final-quality-gate）を通す。"
rollback:     "PR を戻せば、同期は前の規則（不要なファイルも保存する）に戻る。カタログには何も書かないので、カタログ側の戻しは要らない。"
exit:         "`main` への PR が CI を通り、マージできる状態。`work finish` はマージの後に統括が行う。"

execution: {
	sessions: impl: {task: "仕様化と実装", model: "opus", effort: "high", rationale: "standard の実装で、設計を任されたので1段上げた（統括の依頼）"}
	reviews: {
		spec: {role: "仕様のレビュー（spec-review）", after: "S-01", model: "opus", effort: "high"}
		code: {role: "コードのレビュー（code-review）", after: "S-05", model: "opus", effort: "high"}
		gate: {role: "最終品質ゲート（final-quality-gate）", after: "S-05", model: "opus", effort: "high"}
	}
}
