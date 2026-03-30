# S13 canonical guidance test expectation realignment analysis

## 問題

S12 で `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` を GitHub-mandatory create contract に揃えた一方、wrapper/init-update 系の canonical guidance tests は initiative 配下 epic create guidance に `--no-github` が残る前提を保持していた。

失敗として観測されたのは次の 4 件。

- `tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs`
- `tests.test_init_update.TestInitUpdate.test_current_guidance_documents_match_discussion_numbering_contract`
- `tests.test_init_update.TestInitUpdate.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set`
- `tests.test_init_update.TestInitUpdate.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set`

## あるべき状態

- canonical guidance tests は、現在の shipped docs contract を正本として検証する。
- `docs/rules/initiative/epics.md` は S12 corrective 後の create command
  - `./spec-dock/scripts/spec-dock new epic --initiative <id> --title "<title>"`
  を期待する。
- `--no-github` は create 成功経路の guidance として期待しない。

## ギャップ

- docs 正本は current contract に更新済み。
- テスト期待値だけが旧 contract を保持しており、docs corrective を regression と誤判定している。

## 修正案

### 案A: docs を旧期待値へ戻す

- 長所:
  - failing tests は即座に通る。
- 短所:
  - S12 corrective と矛盾する。
  - stale `--no-github` guidance を再導入し、current runtime contract と不整合になる。

### 案B: failing tests の期待値だけ current docs contract へ更新する

- 長所:
  - S12 corrective の意図を維持できる。
  - runtime contract は不変で、変更面積が最小。
  - failing surface が docs-facing assertions に限定されているので修正境界が明確。
- 短所:
  - issue docs の MUST NOT にある「test expectation realignment を再度変更しない」を限定的に緩める必要がある。

### 案C: docs と tests の両方に compatibility wording を追加する

- 長所:
  - 旧/新どちらの wording にも一定の寛容さを持たせられる。
- 短所:
  - 契約が曖昧になる。
  - reject contract と usage guidance の境界がぼやける。

## 推奨

案Bを採る。

理由:

- 問題は runtime ではなく docs-facing test oracle の stale expectation に閉じている。
- S12 corrective は already-approved の narrow rules/docs-authority fix なので、ここで docs を戻すのは contract regression になる。
- したがって、issue docs では「S12 で是正した current guidance を読む canonical tests の期待値 realignment」を S13 の narrow corrective として追加し、tests だけを最小更新するのが最も整合的。

## 実施境界

- 許可する:
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/test_init_update.py`
  - `iss-00038` の requirement/design/plan/report
- 許可しない:
  - runtime code 変更
  - S12 対象 docs の contract rollback
  - 新しい guidance contract の追加
