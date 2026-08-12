---
種別: disc
ID: "20260812t134618z-disc"
タイトル: "PR Repair Unit PR363-U002 Additive Skill Ownership"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-12"
親: ["iss-00359"]
template: "disc"
authority: "evidence"
derived_from: []
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# 20260812t134618z-disc PR Repair Unit PR363-U002 Additive Skill Ownership

## Repair Contract

- `source_batch`: `report.md#11`
- `unit_id`: `PR363-U002`
- `root_cause_family`: `additive-skill-ownership`
- `covered_ids`: `PR363-P1-002`
- `source_links`: PR #363 review thread `PRRT_kwDOQ99OK86YlhKP`
- `failure_class`: `review_feedback:additive-skill-ownership`
- `decided_priority`: `P1`
- `merge_blocking`: `yes`
- `disposition`: `fix-now`

## Validity Analysis

`install_root`全file mappingは対象pathの既存content ownershipを区別せず`copy2`する。新skillと同名のuser-owned fileが存在するとinit / updateが成功しつつ内容を破壊する。指摘はvalid。

## Need-To-Fix Decision

Issue 359が新たにclaimする二skill treeだけにcollision-aware adoptionを導入し、既存非同一fileを上書きしない。

## Root Cause

additive materializationをgeneric managed copyへ載せる際、first-adoption時の既存content conflictをpreflight contractに含めなかった。

## Options Considered

1. unconditional copyを維持: user content lossのため棄却。
2. materializationを#360まで延期: 安全だがIssue 359のinstall intentを満たさないため棄却。
3. 二skill tree限定でmissing / byte-identicalだけを許可し、非同一existing fileを全copy前にfail-closed: 採用。
4. durable ownership manifestを新設: #360 migration責務へ拡張するため棄却。

## Recommended Design

Current mappingは維持し、二skill配下のmapped fileについて、init / update preflightでexisting regular fileのbytesをprovider assetと比較する。missingはinstall、identicalは安全なadoption、non-identicalは明示errorで処理全体をcopy前停止する。managed / legacy inventoryは変更しない。

## Implementation Plan

1. pre-existing sentinelがinit / updateで保持され、commandがfailするpublic behavior testをREDにする。
2. `src/spec_dock/cli.py`へ二skill tree限定content-conflict preflightとapply直前recheckを追加する。
3. provider / dogfoodの全新assetを保護対象としてtestする。

## Validation Plan

init / update collision test、exact-match update regression、focused installer suite、全体lint / pytest。

## Out of Scope

Target inventory cutover、ownership manifest、旧skill prune、consumer migration、publication、uninstall policyの確定。

## Implementation Result

`src/spec_dock/cli.py`へ二skill tree限定のcontent collision preflightとdescriptor-relative no-follow / no-replace materializationを追加した。init / updateはmissing targetをmaterializeし、byte-identical targetをread-only adoptし、非同一existing targetまたはpreflight後のpath差し替えを外部へ書かずfailする。

## Validation Result

四つのmapped assetに対するinit collision test、updateの全copy前停止test、final preflight後のsymlink差し替えtest、byte-identical hard-linkのread-only adoption testを含むIssue 359 focused contract 20件、ordinary suite 1647件、lintがpassした。包括的な最終品質ゲートはP0=0 / P1=0でpass。PR latest-head再観測はpending。

## Commit Evidence

pending

## Re-observation Result

pending

## Residual Risk / Follow-up

durable ownershipとuninstall migrationは#360。Issue 359は非同一existing fileを破壊しないfirst-adoption boundaryだけを所有する。
