---
種別: 設計書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-30"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 1. 設計目標

D5では新しい distribution architectureを作らない。verified baseline `e8b885fcb98e63e6c2e5f32245f8d65345157d1f` 上で、Issue 368〜371が完成させた current architectureを唯一の production authorityとして固定し、残存する dead CLI writer seam、package/projection driftの可能性、macOS CI gap、recovery wording driftを最小変更で閉じる。

Design の中心は次の四点である。

1. **authority cutover**: CLI が current public flowの adapterに留まり、managed distribution file mutationを `managed_distribution.py` 以外に持たない。
2. **recovery classification**: `.distribution-retry.json` を pathnameだけで legacy扱いせず、schema/purposeによって current forward guardとlegacy migration inputを区別する。
3. **surface parity**: checked-in source、provider asset、wheel、sdist、installed/fresh consumerを同じ content contractへ束縛する。
4. **same-candidate evidence**: Linux/macOS、package、tests、docs、Full Regression verifierを同じ candidate SHAへ結び付ける。

## 2. Authority と参照文書

本 Design は次を authorityとして組み合わせる。

- 親 Epic `epic-00365` Requirement/Design/Plan
- accepted ADR `artifacts/20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md`
- completed `iss-00368`〜`iss-00371` Requirement/Design/Plan/Report
- exact baseline source `e8b885fcb98e63e6c2e5f32245f8d65345157d1f`

矛盾がある場合、現在の executable implementationの事実確認には exact baseline sourceを用い、product semanticsは後続 completed Issue の accepted contractを優先する。historical wordingだけを理由に current schema-2 forward guardを legacy writer として削除してはならない。

## 3. Current baseline

### 3.1 Public control flow

`src/spec_dock/cli.py` は package assetを解決し、target admission/root-operation coordinationを行い、typed serviceへ dispatchして public output/exitを組み立てる。current sourceで確認できる distribution service entrypointは次である。

| public route | current authority entrypoint | intent/意味 |
|---|---|---|
| fresh `init`、fresh-state `init --force` / `update` | `execute_fresh_distribution()` | fresh provisioning |
| recognized `update` / `init --force` | `execute_recognized_distribution()` | recognized reconciliation |
| `uninstall` default / `--keep-specs` | `execute_deprovision_distribution()` | managed distribution deprovision |
| `uninstall --remove-specs` | `execute_explicit_spec_history_purge_distribution()` | explicit spec-history purge |

これらは literal に一つの generic public functionではない。single ownership contractは、全 entrypointが `src/spec_dock/managed_distribution.py` 内で同じ assessment/action/kernel/journal/result modelを共有し、CLI側に第二 writer authorityを持たないことを意味する。

### 3.2 `managed_distribution.py` current responsibility

current moduleは少なくとも次を所有する。

- physical provider asset/manifestからの distribution contract
- read-only workspace assessment
- blocker-free executable mutation plan
- root/parent/target identity binding
- no-follow / no-replace / descriptor-bound filesystem mutation
- staging/quarantine/GC ownership
- forward guardとoperation journal
- fresh/recognized/deprovision/purgeのrecovery authority
- typed `DistributionProcessResult`

`_rename_distribution_no_replace()` はこの current kernel内で多数の live pathから使用される。Linuxでは `renameat2(..., RENAME_NOREPLACE)`、Darwinでは `renameatx_np(..., RENAME_EXCL)` を解決し、それ以外は required no-replace support不足として fail closedする。したがって symbol名の存在を legacy absence conditionにしてはならない。

### 3.3 Current recovery metadata model

current sourceでは以下の三 pathnameが protocol boundaryに存在する。

| pathname | current classification | writer authority |
|---|---|---|
| `spec-dock/.distribution-retry.json` schema 2 | current forward guard。purposeは `recognized-journal-forward-only` / `fresh-journal-forward-only` / `deprovision-journal-forward-only` / `purge-journal-forward-only` | current `OperationJournalStore` / managed distribution flow が書く |
| `spec-dock/.distribution-retry.json` schema 1 `distribution-rerun` | legacy distribution retry payload。exact same-root/same-operation等の accepted conditionを満たす場合だけ一方向移行 | legacy inputとして読む。current codeは同 pathnameを schema 2 guardへ安全に置換し得る |
| `spec-dock/.distribution-journal.json` | current operation journal | current managed distribution flow が書く |
| `spec-dock/.uninstall-retry.json` | legacy uninstall evidence。root/mode/plan/checkpointを証明できないため自動変換しない | current production writerなし。read/manual/fail-closed only |

この分類が Issue 372 の structural test/doc wordingの基準である。`prepare_legacy_guard()` という method名は historical namingを含むが、current live flowから呼ばれ schema-2 forward guardを作るため、名前だけで dead/legacyと判断しない。

### 3.4 Baseline residual D5-owned seam

`src/spec_dock/cli.py` には current public service dispatchから到達しない旧 writer/helper subgraphが残る。exact source scanで少なくとも次を確認している。

- `_write_atomic_regular_file()`
- `_write_active_pathfile()`
- `_write_spec_dock_version()`
- `_write_distribution_retry_marker()`
- `_remove_distribution_retry_marker()`
- `_install_repo_root_shortcut()`
- 上記 subgraphが使用する `_rename_distribution_no_replace`、`_swap_regular_distribution_target_if_bound`、`_remove_distribution_target_if_bound` direct imports
- old marker helperだけが必要とする `DistributionStageOwnership`

このうち `_write_active_pathfile()`、`_write_spec_dock_version()`、`_write_distribution_retry_marker()`、`_remove_distribution_retry_marker()`、`_install_repo_root_shortcut()` は baseline source内に定義以外の callがないことを確認している。`_write_atomic_regular_file()` の callもこの旧 local helper群からのみである。

`tests/cli_runtime/test_distribution_cutover.py` は baselineで `cli._write_atomic_regular_file` と `cli._rename_distribution_no_replace` を直接 monkeypatch/testする旧 test seamを持つ。一方、同 test suiteと `tests/unit/infra/test_managed_distribution.py` は current `managed_distribution._rename_distribution_no_replace` を通した journal/quarantine/identity raceを広く検証している。

D5は前者を除去し、後者を保持する。

### 3.5 Baseline already-removed predecessor seams

current sourceでは `_UninstallAction`、旧 uninstall plan/apply/tree mutation等の Issue 371 denylistは production sourceから除去済みである。これらを D5で再実装しない。D5 structural testは「再導入されない」ことを確認するだけである。

### 3.6 Package/build baseline

`pyproject.toml` は setuptools package dataとして `assets/**/*` と required dotfile/hidden subtreeを明示収録し、legacy/generated assetsを excludeする。`setup.py` の custom `build_py` は source assetに存在しない stale build output、legacy patterns、generated Python cacheを pruneし、custom `sdist` は non-distributable README/cacheを除外する。

`tests/unit/infra/test_init_update.py` は既存の Issue 69 build harnessを current infrastructureとして持ち、clean build contextから wheel/sdistを作り、isolated install、inventory、checkout fallback absenceを検証できる。

`tests/integration/test_epic_00343_distribution.py` には current testsとして以下が存在する。

- `test_tc_346_s01_001_candidate_wheel_receipt`
- `test_tc_346_s01_002_candidate_wheel_inventory`
- `test_tc_346_s01_003_isolated_wheel_origin_rejects_checkout_fallback`
- `test_tc_346_s01_004_fresh_consumer_installed_shell_and_generic_import`
- `test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider`
- `test_tc_360_s80_wheel_and_sdist_fresh_and_updated_consumers_match_provider`

D5はこの harnessを再利用し、新しい packaging frameworkを導入しない。

### 3.7 Dogfooding/provider baseline

repository `AGENTS.md` に従い checked-in `spec-dock/` workspaceは canonical dogfooding surfaceである。一方、installer runtimeは `src/spec_dock/assets/install_root`、`src/spec_dock/assets/spec_dock`、`src/spec_dock/assets/managed_distribution.json` を package resourceとして使用する。

既存 fast test `test_checked_in_dogfooding_mirror_docs_match_provider_assets` と workflow projection testsが、checked-in dogfoodとprovider asset copyの一致を固定している。D5で docsを変更する場合、dogfoodだけ/provider assetだけを更新して parityを壊してはならない。

### 3.8 CI/test baseline

`tests/conftest.py` の current policyは次である。

- `tests/cli_runtime/`、`tests/integration/`、`tests/unit/infra/test_init_update.py::` 等は heavy prefixで `full_regression`。
- ordinary `uv run pytest` は heavy nodesを policy skipする fast lane。
- heavy focused runは `--run-full-regression --full-regression-shard` を使用する。
- global `--run-full-regression` は ledger completeness/signature guardを有効化する。

`.github/workflows/provider-ci.yml` は pull requestで Ubuntu/Python 3.11、`make lint` と ordinary `uv run pytest` のみを実行する。macOS jobはない。

`.github/workflows/provider-full-regression.yml` は `main` push / workflow dispatchの Ubuntu jobで Issue 368 `verify-full-regression.py --shards 4` を実行し evidenceを uploadする。これは post-merge/current global regression laneであり、PRのfocused Linux/macOS parity laneとは別責務である。

Full Regression ledgerには historical counts/timingsが記録されているが、current verifierの合否は ancestor-bound ledgerと approved failure signatureの一致であり、特定 failure件数や特定秒数をD5 acceptance constantにしない。

### 3.9 Documentation baseline

`README.md`、`spec-dock/docs/README.md`、`spec-dock/docs/migration.md` は current forward recoveryを概ね説明しているが、`.distribution-retry.json` について「legacy schema 1 payload」と「current schema 2 forward guard」が同じ pathnameを共有するため、文章上の legacy/current distinctionを schema/purposeで明確化する必要がある。

`spec-dock/docs/migration.md` と `src/spec_dock/assets/spec_dock/docs/migration.md` は baselineで同一 blobである。docs update後もこの projection parityを保持する。

## 4. Target architecture

### 4.1 Control-flow boundary

```text
public CLI
  ├─ parse / target resolution / operation lock-admission coordination
  ├─ package resource resolution
  ├─ dispatch
  │    ├─ execute_fresh_distribution
  │    ├─ execute_recognized_distribution
  │    ├─ execute_deprovision_distribution
  │    └─ execute_explicit_spec_history_purge_distribution
  └─ typed result -> text/JSON/exit

managed_distribution.py
  ├─ contract / assessment
  ├─ executable plan
  ├─ descriptor-bound filesystem kernel
  ├─ forward guard + journal
  ├─ recovery / migration readers
  └─ DistributionProcessResult
```

Targetでは CLIから `_rename_distribution_no_replace`、`_swap_regular_distribution_target_if_bound`、`_remove_distribution_target_if_bound` 等を使って managed distribution fileを書く edgeがない。filesystem primitiveそのものを public API化したり別 moduleへ移す必要もない。

### 4.2 Structural absence rule

Structural absenceは単純 grepだけに依存しない。

1. ASTで `cli.py` の forbidden direct importを検査する。
2. top-level function definition/call referenceを確認し、dead writer helperが sourceから消えていることを確認する。
3. runtime spyで public commandが current typed serviceを選ぶことを確認する。
4. current migration reader/guard writerの allowlistを schema/roleで検査する。
5. `managed_distribution.py` 内の kernel primitiveは allowlistではなく current implementation componentとして普通に testする。

禁止対象は roleで決める。future renameで同じ CLI-owned writerを復活させても testが検出できるよう、private symbol名の denylistと「CLI内で managed recovery pathnameを書かない」「CLIから filesystem kernel private helperを直接 importしない」の構造条件を併用する。

### 4.3 Recovery state machine boundary

D5は state machineを変更しない。targetは current semanticsの固定である。

- current guard: schema 2 + intent-specific forward-only purpose
- journal: root / intent / authority / contract / plan / protocol / action pre/postconditionに束縛
- schema 1 distribution retry: accepted exact conditionだけ一方向変換
- legacy uninstall marker: auto-convert/write/deleteしない manual evidence
- lower/different authority: current evidenceを読むことはできても mutate/checkpoint authorityを得ない
- mismatch: `DistributionProcessResult` の existing recovery/manual/error mappingへ投影し、CLIは journal payloadを直接解釈しない

D5 cleanupで dead CLI schema-1 marker writerを削除しても、`managed_distribution.py` の current schema-2 guard writerとschema-1 migration readerを削除しない。

### 4.4 Public compatibility boundary

D5は current command grammarを characterisationとして扱う。

- `init [path]`
- `init --force [path]`
- `update [path]`
- `uninstall [path]`
- `uninstall [path] --keep-specs`
- `uninstall [path] --remove-specs`
- destructive applyの existing `--apply`
- existing `--json`

exact parser ordering/optional syntaxはcurrent tests/helpを authorityとし、Design内の例を parser変更の根拠にしない。

JSONは schema version 1、single object、typed action/status/error/retry projectionを維持する。purge/deprovisionのcross-intent mismatchで retry commandを捏造しない。text outputも existing testsが固定する essentialsを維持する。

## 5. Package/parity model

### 5.1 Surfaces

D5 parityは次の六 surfaceを一つの candidateから比較する。

1. **provider source**: `src/spec_dock/assets/**`
2. **checked-in dogfooding**: mapped `spec-dock/**` と repo-root projected managed assets
3. **wheel**: candidate wheelの `spec_dock/assets/**`
4. **sdist**: candidate sdistの `src/spec_dock/assets/**`
5. **installed package**: isolated environmentにinstallした package resource
6. **fresh consumer**: installed candidate commandで生成した target tree

### 5.2 Comparison identity

surfaceごとに意味のある次の identityを比較する。

```text
relative_path
entry_kind
regular_bytes_sha256
required_mode / executable_bit
symlink_target (symlink surface only)
managed_manifest/protocol payload where packaged
```

ZIP/TAR metadataそのものの完全一致は要件ではない。consumer behaviorに必要な file identity/mode/link semanticsを比較する。

### 5.3 Negative package contract

`setup.py` の stale-prune mechanismを維持し、seeded stale build outputが wheel/sdistへ流入しないことを testする。少なくとも既存 exclude patternsと generated `__pycache__` / `*.pyc` / `*.pyo` の absenceを維持する。

provider-only `.github/workflows/provider-ci.yml` / `provider-full-regression.yml` は consumer install_rootへ配送しない。consumerに配送される `.github/workflows/ci.yml` とは別 surfaceである。

### 5.4 Packaged behavior parity

inventoryだけでなく、isolated installed candidateから public distribution flowを実行する。existing wheel/sdist fresh/update consumer harnessを拡張し、少なくとも次を packaged runtimeから確認する。

- fresh initが provider expected treeを生成する
- recognized updateが provider expected treeへ収束する
- keep/deprovisionが accepted preservation boundaryを維持する
- explicit purge routeが accepted explicit authorityなしに発火しない
- checkout source pathが `sys.path` fallbackにならない

full destructive matrixを package testに重複実装する必要はない。deep race/recovery matrixは `managed_distribution` / cutover testsの責務とし、package testは「packaged runtimeが同じ owner routeを実行する」ことを証明する。

## 6. Linux/macOS parity design

### 6.1 Current platform kernel

current no-replace primitiveは Linux `renameat2(RENAME_NOREPLACE)` と Darwin `renameatx_np(RENAME_EXCL)` を使用する。required symbol/capabilityを解決できない場合は `DistributionApplyError` で fail closedする。

D5はこの platform abstractionを generic fallbackへ変更しない。

### 6.2 CI topology

`.github/workflows/provider-ci.yml` に provider-only focused distribution jobを追加する。`pull_request` event の candidate SHA `C` は `github.event.pull_request.head.sha` と定義し、focused jobは `actions/checkout` の `ref` に `C` を明示する。`ubuntu-latest` と `macos-latest` の両 runnerで `git rev-parse HEAD == C` を検証する。

推奨責務分離は次である。

- existing ordinary provider job: default PR merge ref checkoutのまま lint + ordinary fast lane
- D5 focused distribution matrix: Linux/macOS、`ref: ${{ github.event.pull_request.head.sha }}`、same focused commands、checked-out HEAD verification
- post-merge `provider-full-regression.yml`: current global verifier、Ubuntuのまま

D5 focused jobを `continue-on-error` にしない。default checkoutの merge ref `github.sha` を `C` と記録しない。OS別に違う test selectionを使わず、platform capability自体を検証する部分以外は同一 command setを使う。

### 6.3 Focused platform coverage

両OSで少なくとも次の current behaviorを通す。

- no-replace publication
- symlink/hardlink/special-file blocker
- root/visible-parent rebind blocker
- guard/journal publish and forward resume
- quarantine/staging identity preservation
- cross-intent recovery write-zero
- public fresh/recognized/deprovision/purge routing
- candidate wheel/sdist build + isolated fresh consumerの代表 parity nodes

unit fault injectionでしか再現できない raceは host-independent regressionとして同じ suiteに含めてよい。実 syscallの capabilityは両 hostで最低一つの real mutation testを通す。

## 7. Test architecture

### 7.1 Fast lane

`tests/unit/infra/test_managed_distribution.py` は heavy prefixではないため ordinary fast laneで実行される。D5の軽量 structural/recovery classification testをここへ追加し、PRの `uv run pytest` でも authority regressionを捕捉できるようにする。

`tests/unit/infra/test_init_update.py` は heavy prefixだが、そのうち repository policyで `REQUIRED_FAST_NODE_IDS` に指定された dogfood/workflow parity nodesは ordinary fast laneに残る。既存 required-fast classificationを壊さない。

### 7.2 Heavy focused lane

次の実在 fileは `--run-full-regression --full-regression-shard` で実行する。

```bash
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
```

package testを狭く回す場合は existing exact node IDsを指定できるが、D5で追加した packaged deprovision/purge coverageを含む final focused gateは file-level selectionか、collection後に確認した exact node IDsで構成する。

### 7.3 Global Full Regression

partial selectionで global ledger completenessを誤作動させない。final global gateは current verifierを authorityとする。

```bash
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --shards 4
```

verifierは current ledger observation SHAが candidateの ancestorであること、approved-no-op failure node/signatureが一致すること、unexpected failure/error/missing/mismatchがないことを検証する。historical `27` や durationを D5 source assertionへコピーしない。

## 8. Documentation parity design

変更候補は current source scanで実在を確認した次である。

- `README.md`
- `spec-dock/docs/README.md`
- `spec-dock/docs/migration.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`

更新ルール:

1. schema 1 `.distribution-retry.json` を「legacy payload」と呼び、pathname自体を deprecated扱いしない。
2. schema 2 `.distribution-retry.json` を current forward guardと明記する。
3. `.distribution-journal.json` と guardのsame-root/intent/authority/contract/plan/protocol forward recoveryを説明する。
4. `.uninstall-retry.json` は migration/manual reader-onlyで、自動変換・自動削除・推測retryしない。
5. old codeへのrollbackではなく compatible current/newer packageによる forward recoveryを説明する。
6. dogfood docs変更は provider projectionへ同じ bytesを反映し、existing mirror testを greenにする。
7. 完了済み Issue 368〜371 を『今後の owner』『compatibility owner』として説明する pre-completion wordingは、current intent/authority behaviorの説明へ置き換える。Issue番号は historical traceが必要な箇所以外では product contractの代用にしない。

accepted ADRそのものを current namingに合わせて改変することは D5 の必須条件ではない。ADRはhistorical accepted decision recordであり、current canonical Issue docs/READMEが後続 completed implementationを正確に説明すればよい。ADRに現在と矛盾する normative claimがあることが判明した場合だけ、owner decisionなしに履歴を書き換えず follow-up decisionが必要かを停止判定する。

## 9. Evidence binding

final candidateを PR head branchの full commit SHA `C` とする。`pull_request` eventでは `github.event.pull_request.head.sha == C` を authorityとし、Implementation Completionで使用する全 evidenceは `C` を明示的または再現可能に参照する。default checkoutの merge ref SHAである `github.sha` は integration CIの識別子であって `C` ではない。

tracked `report.md` は `C` をfreezeするcommitに含め、実装要約、変更境界、実行するverification contractを確定する。`C` のpush後にしか得られないrun ID、check result、artifact digest、Strict result等のfinal receiptは、candidate SHAを変更しないPR本文、GitHub check summary、CI artifactへ記録する。final receiptをtracked reportへ追記してはならない。report訂正が必要ならそのcommitを新candidate `C2` とし、影響するevidenceを `C2` で再取得する。

| evidence | binding |
|---|---|
| source/tests/docs | `git rev-parse HEAD == C` |
| wheel/sdist | clean checkout `C` から build。artifact SHA-256を記録 |
| installed/fresh consumer | 上記 candidate artifactからのみ install。checkout fallbackなし |
| Linux/macOS D5 focused CI | `github.event.pull_request.head.sha == C` を明示 checkoutし、runner内 `git rev-parse HEAD == C` |
| focused tests | CI/local logが `C` checkout上の commandを記録 |
| Full Regression | verifier resultが candidate HEADを記録し current ledger contractをpass |
| Strict review | review input SHA `C` |
| final evidence receipt | PR本文、GitHub check summary、CI artifactが `C` とrun/check/artifact identityを記録し、tracked treeを変更しない |

Strict review remediationで sourceが `C2` に変わった場合、`C` の package/platform/test/review evidenceを final completionへ流用しない。必要 gateを `C2` で再取得する。

## 10. Gate model

### 10.1 Implementation Completion

code/test/CI/docsの planned changeとtracked reportが `C` に含まれ、same candidateで required local/package/platform/Full Regression evidenceが候補を変更しないrecord boundaryに揃った状態。PR mergeを意味しない。

### 10.2 Strict Review Pass

Implementation Completion candidateの exact SHAに対する bounded Strict reviewが passした状態。remediationで SHAが変われば再review対象になる。

### 10.3 Human PR Merge Gate

repository policyに従う human-operated merge判断。testsやStrict reviewの代替ではなく、それらの後に行う delivery gate。

### 10.4 `issue finish`

Issue lifecycle closure。READMEの current contractどおり、commit/push/PR/merge/validate/test/review completionを保証しない。delivery evidenceが揃った後に実行する。

## 11. Stop / interview gates

次の場合、coderは推測で進めない。

- baseline再確認で CLI dead seamが実は public executable routeから到達する: predecessor D1/D2 contract defectとして停止。
- `.uninstall-retry.json` current writerが見つかる: D3/D4 recovery contractと矛盾するため停止。
- macOSで current no-replace contractを満たせず、単なる capability fail-closedでは supported requirementを達成できない: platform support decisionが必要なため停止。
- package parityの解消に canonical dogfood/provider ownership directionの変更が必要: repository-level owner decisionが必要なため停止。
- public parser/JSON/exit semanticsを変えないと安全修正できない: predecessor/product owner decisionへ戻す。

一方、dead helper/test seam、provider-only CI matrix、docs wording、package projection copyの修正は停止理由ではなく D5の通常実装である。

## 12. Requirement traceability

| Requirement | Design component |
|---|---|
| I372-R01 | §3.1, §4.1, §4.4 |
| I372-R02 | §3.1, §3.2, §4.1, §4.2 |
| I372-R03 | §3.4, §4.2, §7 |
| I372-R04 | §3.3, §4.3 |
| I372-R05 | §4.4, §5.4, §7 |
| I372-R06 | §3.6, §3.7, §5 |
| I372-R07 | §6 |
| I372-R08 | §3.8, §7 |
| I372-R09 | §3.9, §8 |
| I372-R10 | §9, §10, §11 |

## 13. 2026-08-30 収束Addendum（D5 production設計は変更しない）

Step 10で観測した`ledger-mismatch`はD5 distribution semanticsの欠陥ではなく、schema 1 Full Regression baselineがsuccessor evidenceを表現できないrepository quality-governance gapである。Issue 372へ例外分岐や新しいdistribution stateを追加しない。

Issue `iss-00382` が`scripts/quality/`にrepository-only pure evaluatorと二つのthin adapterを実装し、human mergeされた状態をIssue 372再開条件とする。Issue 368 artifact verifierはhistorical evidenceであり、Issue 372 final gateのcanonical fallbackにしない。

再開後のIssue 372はM1〜M5 implementationを再設計せず、merged authorityを含む新candidateを形成して§9〜§10のsame-candidate evidenceを取り直す。追加production changeが必要と判明した場合は本Addendumで正当化せず、既存stop/interview gateへ戻す。
