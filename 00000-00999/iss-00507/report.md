---
種別: レポート（Issue）
ID: "iss-00507"
関連GitHub: ["#507"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `scope delete --clear-active`：`remove_observed()` の結果（succeeded／unchanged／conflict の failed）の記録を、`with WorkTargetStore(...)` の中に移した。記録を消した後に記述子の close が OSError を投げても `selection.clear succeeded` が残り、`SCOPE_DELETE_INCOMPLETE`（partial、終了コード6）になる（design D-01）。
- `scope delete`：`TreeRemovalIncomplete` の `applied` が空でも `attempted` が真なら、そのディレクトリを試みたものとして `scope.delete unknown` を返し、変更の記録（`changes.delete`）に入れる。`remaining_paths` に残る（D-02）。
- `artifact create`／`artifact import file`（Scope の Artifact）：`artifacts/` の mkdir を試みたか・成功したかを覚え、その後の失敗を `partial`（終了コード6、`ARTIFACT_PUBLICATION_INCOMPLETE`、recovery あり）で返す。publication が確かめられた場合と結果が分からない場合の effects は今のまま。それ以外は `artifact.directory`（succeeded／unknown、target は `spec-dock/initiatives/<区切り>/<ID>/artifacts`）と `artifact`（not_attempted／failed）の2行。作ったディレクトリは残す。`@root` は変えない（D-03）。
- 変えたファイル：`src/spec_dock/runtime/application/canonical_scope_change.py`、`src/spec_dock/runtime/application/canonical_artifact_write.py`、`tests/cli_runtime/test_issue440_g2_scope_delete.py`（2件）、`tests/cli_runtime/test_issue440_g3_artifact.py`（2件と、`@root` のテストのコメント）。配布資産と dogfood の `spec-dock/` は変えていない。

### requirement.cue を直した理由

- 仕様のレビューの1回目の P3：R-02 の本文が `artifact.directory unknown` だけを述べ、mkdir が返った後の失敗で succeeded になることを書いていなかった。本文に「作ったことが確かめられていれば succeeded、mkdir の結果が分からなければ unknown」を足した。受け入れの条件は変えていない。

### 契約の変化（0.5.1 の migration.md に載せる候補）

- `artifact create`／`artifact import file`（Scope の Artifact）：`artifacts/` を新しく作ろうとした後、publication がファイルを作らずに失敗したとき（publication の前の失敗を含む）、0.5.0 は `status: failed`、終了コード5（OSError）か3（ValueError）、`error.code` が `LOCAL_IO_FAILED` など、effects は空か `artifact failed`。0.5.1 は `status: partial`、終了コード6、`error.code: ARTIFACT_PUBLICATION_INCOMPLETE`、`recovery` あり、effects は `artifact.directory`（succeeded か unknown）と `artifact`（not_attempted か failed）。
- `scope delete`：エラーのコード `SCOPE_DELETE_INCOMPLETE` と終了コード6は変わらない。effects の status だけが変わる（記録を消した後の close の失敗で `selection.clear` が not_attempted → succeeded、最初の unlink の後の例外で `scope.delete` が not_attempted → unknown）。
- コマンド、引数、JSON の形は変わらない。

## Verification

| 受け入れ | 確かめたこと | 結果 |
|---|---|---|
| R-01（close の失敗） | `test_issue440_g2_scope_delete.py::test_confirmed_direct_clear_survives_a_later_descriptor_cleanup_failure`（T-01） | 通過 |
| R-01（最初の unlink） | `test_issue440_g2_scope_delete.py::test_first_subtree_unlink_with_unknown_outcome_reports_the_scope_unknown`（T-02） | 通過 |
| R-02 | `test_issue440_g3_artifact.py::test_uncertain_scope_artifact_directory_creation_reports_partial_and_preserves_it_without_publication`（T-03）、`test_failure_after_creating_the_scope_artifact_directory_reports_it_succeeded`（T-05） | 通過 |

- 仕様のレビュー（spec-reviewer opus/high）：1回目 pass（P0/P1 0、P2 1、P3 1。どちらも仕様に反映）。記録：`.workbench/spec-review/iss-00507/round-1.json`、`review-response.md`。
- テスト先行：足した4件が直す前に、今の誤った報告（`selection.clear not_attempted`、`scope.delete not_attempted`、`failed`・終了コード5）で落ち、直した後に通ることを確かめた。
- コードのレビュー（code-reviewer opus/high、axis both、範囲 `3156ac15c..c21a5aef4`）：pass、指摘なし。記録：`.workbench/code-review/iss-00507/round-1.json`。
- 最終品質ゲート（campaign `iss-00507-fqg-1`、`c21a5aef428760af5bddcf3dd7c490cf9ac72852`）：合格（1回目）。レビューの道（quality-gate-reviewer opus/high、1人、観点 functional-correctness・requirements-closure・test-adequacy）は pass、P0〜P3 0、網羅は完全。テストの道は `make lint` 終了コード0（ruff check、ruff format check、mypy pass）、`uv run pytest` 終了コード0（3262 passed、7 skipped、1718秒）。ChatGPT の補助の道はなし（無効）。記録：`.workbench/final-quality-gate/iss-00507-fqg-1/closure.md`。
- PR：https://github.com/chemitaro/spec-dock/pull/521（head `c21a5aef4`）。CI（Provider CI 41446978276、SpecDock check 41446977940、Commit identity 41446977979／41446936042）はすべて success、GitHub は MERGEABLE・CLEAN（2026-11-02T12:58:05Z の観測。外部の CheckRun は観測の対象外）。マージと `spec-dock work finish` は統括が行う。

## Residual Risks / Follow-ups

- `artifact` の effect の failed（canonical）と not_attempted（`@root`）の違いは残した（D-03。0.5.0 からの canonical の値）。
- #506 も `canonical_scope_change.py` を直す。ぶつかったら、後にマージするほうが main を取り込む。
- 版の更新と `migration.md` の 0.5.1 の節は #513 で行う。
