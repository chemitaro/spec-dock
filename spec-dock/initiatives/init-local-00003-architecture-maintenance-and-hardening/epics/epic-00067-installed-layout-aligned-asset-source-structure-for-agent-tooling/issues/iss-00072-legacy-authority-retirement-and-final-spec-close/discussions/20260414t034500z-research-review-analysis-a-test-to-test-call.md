# Review Analysis A: test から別の test を直接呼ぶ構造

- Source PR: `https://github.com/chemitaro/spec-dock/pull/73`
- Review source: Copilot inline comment on `tests/presentation_runtime/test_runtime_sync_s07.py`
- Analyst mode: main analysis + consultant second opinion

## Finding

`test_issue_71_runtime_bundle_sync_force_degraded_path()` が別の public test である `self.test_sync_force_placeholder_and_deps_error_regression()` を直接呼んでいる。review は、test 間直接呼び出しは setup/tearDown 契約を曖昧にし、失敗帰属も悪くなるため、private helper 抽出へ寄せるべきだと指摘している。

## Evidence

- `tests/presentation_runtime/test_runtime_sync_s07.py` では次の構造になっている。
  - `test_issue_71_runtime_bundle_sync_force_degraded_path()`
  - `self.test_sync_force_placeholder_and_deps_error_regression()`
- 同 test class に明示的な `setUp` / `tearDown` は現時点では確認できない。

## Assessment

- Validity: `一部妥当`
- Response priority: `推奨`
- Why:
  - 現時点で hook 迂回による即時不具合が起きているとまでは言えない
  - ただし test from test は将来の保守性と失敗診断性を悪化させる
  - 同じ assertion 群を再利用したい意図自体は妥当なので、構造だけ直すのがよい

## Options

### Option 1: 現状維持

- Pros:
  - 変更不要
  - 現在の振る舞いは維持できる
- Cons:
  - smell が残る
  - 将来 `setUp` / `tearDown` 追加時に静かに壊れうる
  - 失敗時の責務が読みにくい

### Option 2: private helper を抽出して両 test から呼ぶ

- Pros:
  - issue traceability を残せる
  - assertion の再利用を維持できる
  - test から test を呼ぶ構造を解消できる
- Cons:
  - 軽微なリファクタが必要

### Option 3: public test を 1 本に統合する

- Pros:
  - 構造は単純になる
- Cons:
  - issue-71 向けの独立した回帰名義が弱くなる
  - 既存の test naming / traceability を崩しやすい

## Best Response

`Option 2` を採用するのが最善。

- `_assert_sync_force_degraded_path_regression()` のような private helper に assertion 群を移す
- `test_sync_force_placeholder_and_deps_error_regression()` と `test_issue_71_runtime_bundle_sync_force_degraded_path()` の両方からその helper を呼ぶ

## Decision

- Classification: `対応した方がよい`
- Action requirement: `should fix in this PR if touching nearby tests again; otherwise acceptable as follow-up hygiene`

## Notes

consultant 評価でも、本件は blocker ではないが hygiene 改善として取り込む価値が高い、という結論で一致した。
