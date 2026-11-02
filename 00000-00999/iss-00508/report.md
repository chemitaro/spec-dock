---
種別: レポート（Issue）
ID: "iss-00508"
関連GitHub: ["#508"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `spec-dock worktree remove` は、無視されたものが「正しい `spec-dock/initiatives` のリンクだけ」かの判定を、`_remove_captured_worktree` の各確かめ（最初の判定、最初の `verify_target`、unlock の前の確かめ、unlock の後で `git worktree remove` の直前の確かめ）で毎回行うようになった。判定の後（unlock の後を含む）にできた無視されたファイルがあれば、`--discard-ignored` なしでは何も消さずに止まる。
- 実装：`direct_worktrees._remove_captured_worktree` にキーワード引数 `ignored_allowed`（無視されたものの一覧を受け取り、消してよいかを返す）を足した。`canonical_worktrees.remove_worktree` は `discard_ignored` を書き換えるのをやめ、`_only_ignored_is_the_link` を一覧を受け取る形にして渡す。bare の main の拒否の順序（`GIT_FAILED`・終了コード5）を変えないため、canonical の先行の一覧取得の1回は残した（結果は判断に使わない）。
- テスト：`tests/cli_runtime/test_issue508_worktree_remove_ignored.py`（T-01〜T-03。T-01 は撤去の前のテスト `test_issue413_worktree_remove.py::test_remove_preserves_ignored_content_created_after_unlock` を手本にした）。`test_issue432_branch_followups.py` の `_remove_captured_worktree` の差し替え関数を、キーワード引数を受け取る形にした。

### requirement.cue を直した理由

- 統括が書いた R-01 に、R-02（ロックのない worktree でも、最初の判定の後に増えた無視されたファイルを消さない。原因が同じで、同じ直しで直る）と、R-03（リンクだけのときの今の動きと公開の契約を変えない）、F-01（最後の確かめと Git の削除の間の残りの時間）を足した。Epic の constraints の「契約を変えない」を受け入れの条件として観測できるようにするためと、判定と削除の間の時間の扱いを設計に書くため（依頼の手がかり）。
- 仕様のレビューの1回目の P2（止まるときのコードを一律 `WORKTREE_REMOVE_FAILED` と書いていた、bare の main の終了コード5の順序）を受けて、R-03 の止まり方を `PRECONDITION_FAILED`／`WORKTREE_REMOVE_FAILED`／`GIT_FAILED` に分けて書いた。

### 判定と削除の間の時間（design D-02）

- 守る：最初の判定から、最後の `verify_target`（unlock の後、`git worktree remove` の直前）までに増えた無視されたファイル。
- 守らない：最後の確かめから Git が消すまでの、Git の呼び出し1回分の間。Git にファイルの集まりを固定して消させる手段がないため。消したくないファイルがある worktree は、ロックしたままにしておけば `--unlock` なしでは消えない。

### 契約の変化（0.5.1 の migration.md に載せる候補）

- コマンド、引数、エラーのコード、終了コード、JSON の形は変わらない。
- 動きの変化（誤って進んでいた操作を止める直し）：`worktree remove` は、リンクだけの判定の後にできた無視されたファイルがあると、`--discard-ignored` なしでは消さずに止まる（今までは終了コード0で消していた）。書き込みの前なら `PRECONDITION_FAILED`・終了コード3・effects 空、unlock の後なら `WORKTREE_REMOVE_FAILED`・partial・終了コード6（unlock succeeded、remove not_attempted）。
- epic-00512 の constraints の例外の一覧には #508 がないので、統括に Epic 側で足すことを頼む。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：1回目 pass（P0/P1 0、P2 2、P3 2。P2・P3 は仕様に反映）、2回目 pass（指摘なし）。記録：`.workbench/spec-review/iss-00508/round-{1,2}.json`。
- テスト先行：新しいテストの2件（T-01、T-02）が直す前に失敗し、直した後に通ることを確かめた。
- コードのレビュー（code-reviewer opus/high、axis both、範囲 `809a9c67f..726bcf9b5`）：pass、指摘なし。記録：`.workbench/code-review/iss-00508/round-1.json`。
- `make lint` pass、`uv run pytest`（全体、`726bcf9b5`）3231 passed、7 skipped。
- 最終品質ゲート：（下に追記）

## Residual Risks / Follow-ups

- F-01 の残りの時間（最後の確かめと `git worktree remove` の間）は閉じない（D-02）。
- try の中で `_only_ignored_is_the_link` の `observe_link` が OSError を出す極めて狭い競合では、`WORKTREE_REMOVE_FAILED`・終了コード5 の経路になる（コードのレビューの限界の記述。実害を示せないので直していない）。
- 版の更新と `migration.md` の 0.5.1 の節は #513 で行う。
