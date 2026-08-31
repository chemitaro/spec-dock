---
種別: 実装計画書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

`critical`。

spec-history purgeを廃止してProduct surfaceは縮小するが、root allowlist、binding、marker、uninstall順序の欠陥はuser dataやshared contentを不可逆に削除し得る。public CLI、legacy migration、package artifact、required CIを同時にcutoverするため、successor proof、fault injection、artifact-level verification、人間reviewを必須とする。

## 目標

4 roots / 2 slotsのminimal lifecycle、tooling-only uninstall、exact `0.2.3` migration、purge removal、contract-owned test portfolio、build-once single-process provider gateを一つのimplementation-and-verification unitとして完成させる。最終candidateから旧per-file engine、active failure approval、duplicate lanes、4-shard machineryを除き、Requirementの全受入を同じIssueで証明する。

## 順序・依存

Start preconditions:

- Epic Requirement / Design / Planとaccepted ADR `20260831t152024z-adr`がProduct判断を完了している。
- #388〜#390がfuture implementation unitではない。
- base SHA `d8f9d02f...`、2,710 node set、node digest、ordinary gate、26 active failuresが記録済みである。
- effective required contexts / branch protectionがcurrent tokenでは未観測であることを明記し、外部設定を推測変更しない。

Sequence rules:

- successor tests / service proofをold production contract / testsの削除より先に成立させる。
- candidate全体と全target collisionを最初のtarget mutation前に検証する。
- 中間package generationやruntime toggleをmainへ公開しない。
- 内部milestoneはIssueではない。必要なら複数PRを使うが、各main merge pointをreleasableに保つ。
- final acceptanceが揃うまでIssueをopenに保ち、検証Issueを作らない。

## 実装step

### M1. Successor contract freeze

1. 4 roots / 2 slots / consumer seeds / durable data / unknown targetのclassifierをtest-firstで固定する。
2. installation record、skill marker、typed resultのschemaを固定する。
3. exact `0.2.3` recognizer inputsとactive-recovery blockをfixture化する。
4. init / update / uninstall / compatibility aliasesのstate-result tableを固定する。
5. Linux canonical / macOS deltaの排他的node ownershipを定める。

### M2. Minimal lifecycle core

1. no-follow repository / parent bindingとfixed action setを実装する。
2. candidate staging / validationとtree digestを実装する。
3. incomplete / ready recordのatomic replaceを実装する。
4. fixed roots replacement、fixed slot marker、exact tombstone cleanupを実装する。
5. same-operation / same-candidate rerunとcross-intent blockを実装する。
6.各mutation境界へfault injection seamを置く。

### M3. Combined public cutover

1. install / update / uninstall servicesをfinal interfaceへ接続する。
2. `init`、`init --force`、`update`、`uninstall`をnew servicesへ接続する。
3. default dry-run、`--apply`、`--keep-specs`、rejected `--remove-specs`を実装する。
4. text / JSON / exit mappingとmigration / recovery guidanceを更新する。
5. tooling-absent-preserved-dataからのreinstallを実装する。

### M4. Legacy / downgrade proof

1. exact clean `0.2.3` workspaceとmarkerless 2 slotsをbuilt baseline artifactから作る。
2. clean migration、absent slots、exact slots、modified / foreign slotsを検証する。
3. active legacy recoveryとunsupported legacyがwrite 0になることを検証する。
4. final workspaceへ旧`0.2.3`の`init --force`、update、tooling uninstall、`--remove-specs`を実行し、tree mutation 0を証明する。
5. mutationがあればfinal marker / formatを変更して再検証する。

### M5. Old product contract removal

successor proof後に限り、per-file reconciler、historical identity catalog、operation journal、per-action checkpoint、cross-intent recovery、purge service、obsolete exact-file catalog、対応tests / docsを削除する。削除対象、reason、successor / retirement authority、focused verificationをIssue reportの一枚の表へ記録する。

### M6. Failure cohort / portfolio consolidation

1. 26 active nodeをexact nodeごとにfix / current successor / accepted retirementへ分類する。
2. S05 context-pack、S06 active、import S10、delete scrub、credentialed URL、shell structural、sync、workbench familyをcurrent contractへ修正する。
3. approved-no-opを0にしてfailure ledgerを削除する。
4. testをpure/domain、filesystem/service、CLI、built artifact、macOS deltaへ再配置する。
5. path-based fast/full permissionを撤去し、canonical collectionでpolicy skip 0にする。

### M7. Build-once provider gate

1. authoritative candidateからone invocationでwheel / sdistをbuildしdigest manifestを作る。
2. Linux canonical single-process laneを実装する。
3. same wheelをconsumeするmacOS delta laneを実装する。
4. candidate SHA / digest mismatch failure、duplicate node detector、wall / CPU metricsを実装する。
5. effective required contexts、classic protection、merge queueをPR上でread-only取得する。
6. existing context名を再利用する。不可避な場合だけold+new required / intentional RED / new-only requiredを人間ownerと実行する。

### M8. Old CI removal

new gateのGREEN / intentional RED block確認後に、duplicate parity selection、`provider-full-regression.yml`、4-shard verifier、timing weights、failure ledger evaluator、policy skip hooks、関連meta-testsを削除する。main pushでfull regressionやcandidate rebuildを行わない。

### M9. Final acceptance

同じfinal candidateでlocal / fixed Linux 5 runs、seeded fault pack、rolling 20、Linux / macOS artifact smoke、old-package mutation-zero、duplicate 0、required setを確認する。人間merge後、merged treeがverified PR treeと同一であることを確認する。

## 検証

Planning baseline:

- `uv run pytest --run-full-regression --collect-only -qq`: 2,710 nodes
- sorted node-set SHA-256: `f607b007d167231ed27f2a17391b0d8b3aa452d67ce6532565463e193486a04c`
- `uv run pytest -q`: 1,574 passed、1,136 skipped、57.02s
- active ledger focused rerun: 26 failed、14.69s

Final commands / evidenceは実装中にrepository scriptsへ固定する。最低限、次を同じcandidate SHAへ束縛する。

- lint / static analysis
- canonical single-process pytest collection and execution
- focused lifecycle / CLI / fault tests
- built wheel / sdist source / digest verification
- baseline `0.2.3` migration and old-package mutation-zero
- macOS delta node set and Linux intersection 0
- five-run wall / process-tree CPU report
- seeded fault detection report
- rolling-20 flake / retry report
- required contexts before / after、review requirement、merge queue、canary
- SpecDock sync / validateとdogfooding projection inspection

## rollback

- pre-merge: failing candidateをmergeせず、required setを変更した場合はcaptured before stateへ戻す。
- runtime preflight failure: target mutation 0でread-only diagnosticを返す。
- runtime partial failure: same operation / same candidateのexternal rerunだけを許可する。
- destructive defect: apply routeをfail closedにし、old engineへfallbackしない。
- post-merge: human-reviewed Git revertを用いる。user dataをrollback素材として変更しない。

## exit / handoff

- Requirementの全checkboxが同じfinal tree / artifactsで証明されている。
- unexpected failures、approved failures、policy skips、duplicate nodesがすべて0である。
- performance / fault / rolling-20 / artifact / required-context evidenceがIssue reportに記録されている。
- human mergeが完了し、merged treeとverified PR treeが一致する。
- `iss-00392`のReportを完成し、SpecDock `issue finish`可能な状態へ進める。
- follow-up decision / investigation / verification Issueを予約しない。未達なら同じIssueをopenのまま修正する。
