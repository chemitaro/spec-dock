package spec

// 設計（Issue）。型 specdock/v1。

goals: ["曖昧な宣言を版4として受け付けない", "観測の間に消えた worktree を、落ちずに unavailable の行にする"]
current: "`read_workspace_declaration` は `read_guarded_json` の通常の `json.loads` で読むので、重複キーは最後の値が勝ち、`{\"schema_version\":99,\"schema_version\":4}` が版4として受け付けられる。`resolve_observed_context` は版3を `WorkspaceNotMigrated` で見分けた後にもう一度読み、`assert loaded is not None` で消えた宣言を AssertionError にする。"
target:  "重複キーの宣言は `ValueError` で拒む。`resolve_observed_context` は消えた宣言を `ValueError` にし、既存の呼び出し元（`canonical_workspace`、`canonical_work`）の `except (OSError, ValueError, RuntimeError)` が unavailable の行にする。"

design: {
	"D-01": {
		title:     "宣言の読み取りで重複キーを拒む"
		text:      "`project_context.read_workspace_declaration` と版3の再読み取りは、`read_guarded_json_bytes` が返す生のバイトを、重複キーで `ValueError` を出す `object_pairs_hook`（`legacy_reader._unique_object` と同じ規則）付きで読み直す。これで宣言の読み取りの入口がすべて同じ規則になる。`read_guarded_json` 自体は、ほかの JSON の読み取りにも使われるので変えない。\n\n**エラーと終了コード**：新しいコードは作らない。`ValueError` は、版5・文字列の \"4\"・null と同じ経路で、`PRECONDITION_FAILED`（終了コード3）になる。`CANONICAL_NOT_MIGRATED` にはしない（版が決まらないため）。\n\n**`workspace doctor --raw`**：宣言を解釈しない `resolve_git_context` と `legacy_reader` を通るので、変えない。曖昧な宣言は、0.5.0 と同じく観測として返す（AC-440-01 の形を保つ）。`require_migrated` も、重複キーの宣言を読み取れないものとして今までどおり通す。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "観測の間に消えた宣言を unavailable にする"
		text:      "`resolve_observed_context` の版3の再読み取りで、宣言が消えて `None` が返ったとき、または辞書でないとき、`assert` ではなく `ValueError(\"workspace declaration is missing or invalid\")` を出す。呼び出し元は既に `ValueError` を捕まえて `SelectionObservation(\"unavailable\", ..., reason=...)` の行にするので、呼び出し元は変えない。"
		satisfies: ["R-02"]
	}
}

compatibility: "重複キーの宣言を持つ版4のリポジトリは、0.5.0 では受け付けられたが、0.5.1 では `PRECONDITION_FAILED`（終了コード3）になる。`doctor --raw` の観測と、そのほかの JSON は変わらない。#513 が `migration.md` の 0.5.1 の節に書く。"
