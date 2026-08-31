---
種別: 要件定義書（Issue）
ID: "iss-00390"
タイトル: "Retained Workflow Ownership And Artifact Platform Validation Policy"
関連GitHub: ["#390"]
状態: "draft"
最終更新: "2026-08-31"
親: ["epic-00384", "init-local-00003"]
---

# iss-00390 Retained Workflow Ownership And Artifact Platform Validation Policy — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

retained `.github/workflows/ci.yml`のownershipと、wheel / sdist / Linux / macOS validationのtrigger、artifact build / reuse contractをProduct policyとして確定する。同一candidateの重複testと重複buildを除く後続CI cutoverが、保証範囲を推測せず設計できる状態を成果とする。

## 背景

current `install_root`は2 managed skillsと`.github/workflows/ci.yml`を配布する。provider PR CIはordinary laneに加えてLinux / macOS parityでtest familyを再実行し、post-merge Full Regressionは4 shardを起動する。accepted ADRはworkflow ownership、artifact / platform triggerを未決としている。

## 観測可能な要件

- shipped `.github/workflows/ci.yml`をinit-once consumer-owned seed、provider-owned reusable projection、distribution対象外の一つに分類する。
- update / uninstallがworkflowへ持つmutation / delete authorityを明示する。
- wheel、sdist、Linux smoke、macOS smokeをPR / main / release / manualのどこで実行するか定義する。
- platform-independent nodeをmacOSで再実行せず、OS固有boundaryだけをowner laneへ割り当てる。
- exact same candidate artifact bytesを必要lane間で再利用し、source SHA / digest mismatchをfailureとする。
- `artifact_build_count`の計数単位とtargetを定義する。
- GitHub ruleset / branch protection / merge queueのauthority、required context名、変更ownerを定義する。
- shadow acceptance、old + new required、new-only required、old workflow removalの順序とrollbackを定義する。
- unrelated effective required contextsを`U`として、`U + old -> U + old + new -> U + new`の集合契約、ruleset scope、merge queue canaryを定義する。

## スコープ

対象:

- retained workflow ownershipとlifecycle authority
- wheel / sdist / Linux / macOS triggerと保証範囲
- artifact build invocation、digest、source SHA、retention、cross-job reuse
- public deprecation window
- 後続install/update IssueとCI Issueへ分けたremoval / change receipt
- external required-check transition receiptとhuman review gate ownership

対象外:

- workflow YAML、reporter、artifact builderの実装
- test nodeの具体的選定
- human PR merge gateの撤去
- worker追加やmachine大型化によるbudget回避

## 失敗・境界条件

- workflow ownershipが曖昧なままupdateするとconsumer customizationを破壊し得る。
- lane triggerが曖昧だと同じnode / artifact buildを複数laneで繰り返す。
- artifact digest / source SHAが束縛されないと別candidateのevidenceを混在できる。
- GitHub-hosted runnerが2 vCPU hard quotaを保証しない場合、reference measurementを別container / runnerへ分離する必要がある。
- repository workflowとexternal required contextsを同時変更できると仮定すると、gate空白または永続pendingを作り得る。

## 受け入れ条件

- [ ] `.github/workflows/ci.yml`のownership、mutation authority、delete authorityが一つに確定している。
- [ ] wheel、sdist、Linux、macOSのtriggerと保証範囲が確定している。
- [ ] platform-independent nodeをmacOSで再実行しないlane ownershipが明示されている。
- [ ] candidate artifactのbuild invocation計数単位とtargetが確定している。
- [ ] artifact outputごとのdigest、source SHA、retention、cross-job reuse ownerが確定している。
- [ ] missing artifact、digest mismatch、source SHA mismatchがfailする契約である。
- [ ] public deprecation windowが必要な場合はversionまたはdateで確定している。
- [ ] human PR merge gateを維持する。
- [ ] required contextのstable name、external authority、変更ownerが確定している。
- [ ] shadow GREEN / failure canary、old + new required、new-only required、old workflow removalのtransitionとrollbackが確定している。
- [ ] canaryは`U`とoldをGREEN、新だけをREDにし、merge queueがactiveならmerge-groupでもblockを証明する。
- [ ] workflowをuninstall delete対象へ含める場合はparent ADR改定とC5 behavior / tests追加が必要であり、それまではpreserveする。
- [ ] accepted decisionがEpic Requirement / Design / Planへ反映されている。

## 制約・前提

- 本Issueはdecision-onlyでありworkflowやproduction codeを変更しない。
- canonical regressionのsingle process / worker 1 / 600秒budgetを緩和しない。
- artifact trigger未決をtest authorやCI implementerが推測しない。
- Issue #372を変更しない。
