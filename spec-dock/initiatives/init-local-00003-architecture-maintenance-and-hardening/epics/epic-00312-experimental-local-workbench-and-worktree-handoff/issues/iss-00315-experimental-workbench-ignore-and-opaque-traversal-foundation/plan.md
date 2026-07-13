---
種別: 実装計画書（Issue）
ID: "iss-00315"
タイトル: "Experimental Workbench Ignore And Opaque Traversal Foundation"
関連GitHub: ["#315"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00315 Experimental Workbench Ignore And Opaque Traversal Foundation — Issue 実装計画書（Standard / TDD）

## 1. Readinessと実装原則

- `requirement.md`はfresh spec-reviewer pass済み。
- Assurance profileは`standard`。
- 本designのfresh review通過後に本planをreviewし、plan pass前にはproduction codeを変更しない。
- provider sourceを先に変更し、dogfood projectionはinstalled updateで確認する。
- 1 stepだけをactiveにし、Red/characterization → Green → focused regression → fresh review → commit → clean checkの順で閉じる。
- 実装は`dev-coder`、docsは`doc-writer`へ委譲し、親は統合とgate管理を行う。
- W1ではPRを作らず、W5へdeferred delivery evidenceを残す。

## 2. Allowed / forbidden surface

Allowed:

- `src/spec_dock/cli.py`
- `src/spec_dock/assets/spec_dock/.gitignore`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{infra,application,domain}/**`
- 関連する`tests/unit/**`, `tests/cli_runtime/**`, 必要最小限のintegration test
- provider docs/templateとdogfood projection（S90/S06のみ）
- active Issueの`requirement.md`, `design.md`, `plan.md`, `report.md`, `artifacts/**`

Forbidden:

- Issue 316 copy、Issue 317 import、Issue 318 workflow/skill機能の先行実装
- node/artifact schema変更、migration、新dependency
- `.workbench` contentsのGit管理、catalog/TTL/secret scan
- unrelated refactor、全recursive traversalのgeneric framework化

## 3. Closure index

| Closure | 閉じる契約 | Requirement / Design | Evidence |
|---|---|---|---|
| C315-01 | ignore matrix / near-name | AC-315-001 / DES-315-001 | S01 tests |
| C315-02 | node/graph opacity | AC-315-002 / DES-315-002–003 | S02 tests |
| C315-03 | descendant no-access | AC-315-003 / DES-315-002–003 | S02 sentinel |
| C315-04 | independent resolvers | AC-315-004 / DES-315-004 | S03 tests |
| C315-05 | authoring reject/prune | AC-315-005 / DES-315-005 | S04 tests |
| C315-06 | explicit operations unchanged | AC-315-006–007 / DES-315-006 | S05 characterization |
| C315-07 | update preservation/parity | AC-315-008–009 / DES-315-007 | S06 tests/inspection |
| C315-08 | scope and docs closure | RQ-315-010 | S90/S99 review |

## 4. Step plan

### S00 — Inventory, assurance, baseline

Goal: implementation surfaceと既存baselineを固定する。

Tasks:

1. `rg`で`rglob`, `glob`, `walk`, metadata/source traversalを列挙する。
2. 各callsiteを`default-semantic-discovery`、`explicit-user-operation`、`generated-known-tree`へ分類しreportへ記録する。
3. 必須inventoryとして次を本文確認する。
   - `infra/fs_repo.py`
   - `infra/assurance_store.py::_issue_records`
   - `src/spec_dock/cli.py::_resolve_manifest_target_dir`
   - `application/delete_node.py::_matching_target_directories`
   - `application/delegated_authoring.py::_resolve_scope_dir`
   - `application/delegated_authoring.py::_directory_state`
   - `domain/authoring_pack/source_manifest.py`
4. focused baseline testsを実行し、既存failureがないことを記録する。

Verification: relevant existing unit/CLI tests; read-only inventory diff。No production changeなら`approved-no-op`で閉じる。

### S01 — Ignore asset and installer fallback

Behavior: fresh init/update consumerでsupported placementの`.workbench/probe`がignoredとなり、near-nameはreservedにならない。

Red: installer/init fixtureと`git check-ignore` matrixを追加し、provider asset/fallback欠落でfailすることを確認。

Green: provider `.gitignore`とinstaller fallbackを最小変更する。

Verification: focused installer tests、fresh init smoke。Closure: C315-01。

### S02 — Node metadata and graph opacity

Behavior: Workbench内current/legacy metadataとbroken descendantがnode/graph inputにならず、outside malformed metadataは従来どおりfailする。

Red: fake duplicate/malformed metadata、near-name、no-descendant-access sentinelを追加する。

Green: node discoveryをtop-down pruneし、必要なら小さなexact-component predicateを追加する。

Verification: fs repository/domain/CLI focused tests、validate/sync/deps regression。Closure: C315-02, C315-03。

### S03 — Independent resolver parity

Behavior: common node readerを迂回するassurance store、installer recovery、delete fallback、delegated scope resolverがWorkbench metadataを候補にしない。Installerはfallback scanだけでなく、corrupt/stale persisted pathがWorkbench descendantを指す場合も候補から除外する。

Red: 各resolverについてWorkbench内metadataが誤選択されるfixtureを追加する。

Green: 既存責任内でprune/filterする。generic traversal abstractionは必要な共有predicateを超えて作らない。

Verification: focused installer/application/infra unit tests。Closure: C315-04。

### S04 — Authoring source rejection and pruning

Behavior: exact Workbench inputはcontent access前にstable blockerとなり、parent directory inputではWorkbench subtreeをhash/readしない。

Red: file/dir/descendant explicit source、parent selection、near-name、unreadable/broken descendantをtestする。

Green: preflightでexact inputをrejectし、manifest traversalでsubtreeをpruneする。

Verification: authoring-pack domain/application tests、publish未実行確認。Closure: C315-05。

### S05 — Delete and worktree-remove characterization

Behavior: nonempty Workbenchはscope delete/worktree removeをblockせず、既存明示operationと共に削除される。

Method: 既存実装で成立する場合はcharacterization testのみ。成立しない場合だけ最小修正する。Workbench専用confirmation/backupは追加しない。

Verification: delete CLI/runtime testsとworktree remove test/smoke。Closure: C315-06。

### S06 — Update preservation and provider/dogfood parity

Behavior: existing root/scoped sentinel bytes/nested filesがupdate後も同一で、provider changesがconsumer/dogfoodへ配布される。

Red/characterization: update fixtureへsentinelを置き、SHA-256またはbyte equalityを記録する。

Green: 必要ならinstaller managed/unmanaged境界だけを修正し、通常update経路でdogfoodをrefreshする。

Verification: `tests/unit/infra/test_init_update.py` focused lane、fresh temp consumer init/update、provider/dogfood diff。Closure: C315-07。

### S90 — Documentation impact resolution

Owner: `doc-writer`。

Tasks: public docs/templateへの影響をinventoryし、必要なWorkbench ignore/opaque説明だけをprovider authorityへ追加する。Issue 316–318のcommands/workflowは先行記述しない。dogfood projectionを通常update経路で確認する。

Verification: docs diff、template/install test、fresh spec-reviewer。Closure: C315-08。

### S99 — Issue final quality and deferred PR delivery

1. Focused testsを再実行。
2. `uv run pytest tests/unit`と`uv run pytest tests/cli_runtime`を実行。
3. `make lint`を実行し、Ruff/format/mypyのstatic analysis gateを通す。
4. final `code-reviewer`、`qa-reviewer`、`spec-reviewer`をfreshに実行し、P0/P1またはblocking driftを解消する。
5. reportの全closure、commit hash、test evidenceを確定する。
6. W1ではPRを作成せず、`deferred_to: iss-00319`、branch/head、commits、remaining riskをreportへ記録する。
7. `issue finish iss-00315`を実行し、次Issueがreadyになったことを確認する。

## 5. Step completion contract

各S01–S06/S90について以下が全て必要:

- worker summaryとchanged files。
- Redまたはapproved characterization evidence。
- required focused verification pass。
- fresh step reviewer pass（P0/P1なし）。
- requirement/design/planからのclosure mapping。
- focused Japanese Conventional Commit。
- commit後`git status --short` clean（active symlink/generated stateを除く場合は理由を記録）。

失敗時は同step内で修正と再reviewを行い、次stepへ進まない。

## 6. Stop / replan conditions

- Public CLI/schema/migration/security-sensitive changeが必要。
- Workbench outside malformed metadata behaviorを緩和する必要がある。
- explicit operationをsemantic discoveryへ変更しなければ成立しない。
- planned surface外のrecursive resolverが見つかり、複数stepのclosureへ影響する。
- data loss、secret emission、baseline regressionを観測した。

局所callsite追加だけならinventory/reportを更新して同step内で扱う。Requirement/Design contractが変わる場合は停止してcanonical docsとfresh reviewをやり直す。

## 7. Final acceptance

- C315-01–08がreportでpassまたは明示的approved-no-op。
- AC-315-001–009がtest/review evidenceへ追跡可能。
- provider/dogfood authorityとupdate preservationが確認済み。
- Issue 316–318の機能を先行実装していない。
- branchはW5統合用にpush済みで、W1のdeferred delivery recordが完成している。
