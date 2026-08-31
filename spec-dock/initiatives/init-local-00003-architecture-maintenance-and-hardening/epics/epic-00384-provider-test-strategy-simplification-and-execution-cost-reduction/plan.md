---
種別: 計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md", "artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md"]
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 計画

詳細: [Scope Layering Guide](../../../../docs/authoring/scope-layering.md)

## 目標

現行2,708 testsを4 shardへ分配する運用を最終形とせず、distribution product contractとtest portfolioを同時に縮小する。完了時には、provider-owned contentを4 disposable rootsと2 fixed skill slotsで管理し、merge-required regressionを単一pytest processで10分以内に実行し、active approved failures、duplicate nodes、timing-weight schedulerを持たない。

本Planはaccepted ADR `20260831t005139z-adr` を実装境界のauthorityとする。未決Product判断はdecision-only Issueで受理し、影響するproduction / test / CI Issueをその前に作成・開始しない。Issue #372のcandidate、canonical docs、acceptance evidenceは変更しない。

## Issue granularity assessment

- **Result**: `PROPOSED_ISSUE_CANDIDATES`
- **Decision basis**:
  - 4 disposable rootsと2 fixed skill slotsはcandidate staging、update orchestration、installation record / ready markerを共有するため、一つのinstall/update cutover Issueがend-to-endで所有する。
  - unresolved Product decisionsはproduction implementationから分離する。判断Issueはaccepted authorityを成果とし、codeを変更しない。
  - full node inventory、26 active failure disposition、test portfolio再編、CI / budget cutover、5-run / rolling-20 evidenceは入力、acceptance、failure時の戻り先が異なる。
  - technical layer、file、test / implementationという役割だけでは分割しない。
  - production contractを廃止するIssueより先に、そのcontractを証明するtestを削除しない。
- **Current adoption**:
  - decision-only candidates 1〜3は`iss-00388`、`iss-00389`、`iss-00390`として作成済みだが、decisionは未受理である。
  - candidates 4〜10はproposalであり、Product gates通過後にactual `iss-xxxxx`として作成する。
- **Assumptions / unresolved evidence**:
  - legacy support window、`.gitignore`、purge CLI、workflow ownership、artifact / platform triggerは未決である。
  - 2,708 nodesと26 active failuresはhistorical observationであり、inventory Issueのexact baselineで再計測する。
  - 10分budget、CPU比1.1、rolling 20はtargetであり、達成証拠ではない。

## Child Issue graph

| Label | Actual ID | 種別 | タイトル |
|---|---|---|---|
| E384-01 | `iss-00388` / #388 | Decision-only | Legacy Direct Update Window And Gitignore Seed Policy |
| E384-02 | `iss-00389` / #389 | Decision-only | Tooling Uninstall Spec History Purge And Public CLI Compatibility |
| E384-03 | `iss-00390` / #390 | Decision-only | Retained Workflow Ownership And Artifact Platform Validation Policy |
| E384-04 | proposal | Evidence / planning | Provider Test Contract Inventory And Removal Receipt Baseline |
| E384-05 | proposal | Decision-only | Active Approved Failure Disposition Authority |
| E384-06 | proposal | Production implementation | Install Update Cutover To Disposable Roots And Fixed Skill Slots |
| E384-07 | proposal | Production implementation | Tooling Only Uninstall And Purge Compatibility Cutover |
| E384-08 | proposal | Test implementation | Contract Owned Pytest Portfolio And Zero Failure Cutover |
| E384-09 | proposal | CI implementation | Single Process CI Graph Artifact Reuse And Budget Gate Cutover |
| E384-10 | proposal | Acceptance evidence | Five Run Reference And Rolling 20 Stability Acceptance |

## Parent acceptance coverage

| Epic acceptance | Owner |
|---|---|
| legacy window / `.gitignore` / `init --force` | E384-01 (`iss-00388`) |
| uninstall / purge public contract | E384-02 (`iss-00389`) |
| workflow ownership / artifact-platform trigger | E384-03 (`iss-00390`) |
| full node inventory / removal baseline | E384-04 |
| active approved failure disposition | E384-05 |
| 4 roots + 2 slots + ready marker | E384-06 |
| tooling-only uninstall / purge separation | E384-07 |
| contract-owned tests / zero active failure / zero policy skip | E384-08 |
| single process / worker 1 / duplicate 0 / build 1 / metrics | E384-09 |
| five reference runs / seeded faults / rolling 20 | E384-10 |

## Direct dependencies

```text
E384-01 -> E384-04
E384-02 -> E384-04
E384-03 -> E384-04
E384-04 -> E384-05
E384-01 -> E384-06
E384-03 -> E384-06
E384-04 -> E384-06
E384-02 -> E384-07
E384-04 -> E384-07
E384-06 -> E384-07
E384-04 -> E384-08
E384-05 -> E384-08
E384-06 -> E384-08
E384-07 -> E384-08
E384-03 -> E384-09
E384-08 -> E384-09
E384-09 -> E384-10
```

E384-01〜03は並行して判断できる。E384-05とE384-06もwriterが競合しないため並行可能だが、production writerであるE384-06とE384-07は直列とする。

## E384-01 — `iss-00388` Legacy Direct Update Window And Gitignore Seed Policy

### Outcome

legacy direct-updateの有限window、markerless migration evidence / sunset、`.gitignore` collision、`init --force`、public compatibilityをaccepted decisionにする。

### Gate / implementation handoff

- production codeは変更しない。
- fresh / current-supported / legacy-supported / legacy-expired / unknownを相互排他的に定義する。
- unknownはpreserve-and-blockする。
- E384-06が削除するmanifest section、adapter、fixtures、testsをreceipt化する。

詳細なRequirement / Design / strict Planは`iss-00388`を正本とする。

## E384-02 — `iss-00389` Tooling Uninstall Spec History Purge And Public CLI Compatibility

### Outcome

`--remove-specs`のremove / deprecate / independent purge、confirmation、dry-run / apply、text / JSON / exit、sunsetをaccepted decisionにする。

### Gate / implementation handoff

- normal uninstallからhistory purgeへ到達させない。
- destructive aliasをsilent実行させない。
- unknown ownershipはpreserve-and-blockする。
- E384-07が変更するoption、intent、route、journal、tests、docsをreceipt化する。

詳細なRequirement / Design / critical Planは`iss-00389`を正本とする。

## E384-03 — `iss-00390` Retained Workflow Ownership And Artifact Platform Validation Policy

### Outcome

shipped workflow ownership、update / uninstall authority、wheel / sdist / Linux / macOS trigger、artifact build invocation / digest / reuse / retentionをaccepted decisionにする。

### Gate / implementation handoff

- platform-independent nodesをmacOSで再実行しない。
- exact artifact bytesをlane間で再利用し、missing / digest / source SHA mismatchをfailする。
- human PR merge gateを維持する。
- shipped asset changeはE384-06、provider CI changeはE384-09へ分けてreceipt化する。

詳細なRequirement / Design / strict Planは`iss-00390`を正本とする。

## E384-04 proposal — Provider Test Contract Inventory And Removal Receipt Baseline

### Observable outcome

exact baseline SHAの全collected nodeをcurrent contract、owner layer、current / target lane、cost、disposition、owner Issueへ100% mappingし、testやproduction routeを削除する前のremoval receipt baselineを作る。

### Creation / start gate

- E384-01、E384-02、E384-03がacceptedである。
- exact baseline SHAを固定し、historical 2,708 / 26 countsを再利用しない。

### Implementation plan

1. `pytest --collect-only`相当のexact node set、current lanes、ledger、timing evidenceを取得する。
2. nodeごとにcontract ID、owner layer、current lanes、target lane、keep / move / consolidate / delete-after-retirement、owner Issueを記録する。
3. duplicate groups、active failure nodes、production route / retired authorityを紐づける。
4. JSON / Markdown inventoryとremoval receipt schemaをIssue Artifactsとして保存する。
5. node set equality、duplicate nodeid 0、missing disposition 0、unknown owner 0、ledger count一致を検証する。

production code、tests、workflowは変更しない。baseline SHAが変わればinventoryをstaleとして後続deletionをblockする。

## E384-05 proposal — Active Approved Failure Disposition Authority

### Observable outcome

E384-04で確認したactive failure nodeを一件ずつ`fix`、`contract retirement`、`exact successor replacement`へ分類し、blanket approvalと無期限quarantineを0にする。

### Creation / start gate

- E384-04 inventoryがcompleteである。
- current authorityからexpected behaviorを決定できないnodeはProduct interviewへ戻す。

### Implementation plan

1. 各nodeにowner、canonical authority、exact nodeid、disposition、successor / retirement authority、implementation ownerを付ける。
2. current ledger、inventory、successor nodeをset equalityで照合する。
3. conflicting disposition、unknown owner、approved-no-opを0にする。
4. accepted disposition ArtifactをE384-08へのreceiptとする。

production fixやtest削除は行わない。判断不能nodeが一つでもあればE384-08をblockする。

## E384-06 proposal — Install Update Cutover To Disposable Roots And Fixed Skill Slots

### Observable outcome

fresh / init / updateを4 disposable roots、2 fixed skill slots、one installation record / ready markerへ一括cutoverし、old per-file update authorityと対応testsを同じIssueで退役させる。

### Creation / start gate

- E384-01、E384-03がacceptedである。
- E384-04のbaseline / removal receiptがcompleteである。

### Implementation plan

1. fixed roots / slots、marker schema、ready state、action orderをpure modelとして定義する。
2. root / slot candidateをtargetと同一filesystemへ全量stageし、tree digest、required entrypoint、markerをvalidateする。
3. target root / parent / repository bindingをno-followで検証し、skill collisionを全mutation前にblockする。
4. `docs -> templates -> system -> scripts`とslotsをfixed orderでreplaceし、全配置後にだけready markerをatomic replaceする。
5. E384-01のfinite migration、`.gitignore`、E384-03のworkflow seedを実装する。
6. successor service testsを成立させ、old per-file update route、historical manifest sections、journal / checkpoint / update recovery testsを削除する。
7. provider assetsからdogfooding projectionを更新し、built wheel representative smokeを行う。

### Acceptance / failure

- 4 roots / 2 slotsがcandidate treeと完全一致し、obsolete / local editが残らない。
- Initiatives、Artifacts、`.workbench`、unknown paths、shared skills parent、unrelated skillsがbyte-identicalである。
- staging failureではtarget mutation 0、symlink / rebind / unexpected type / marker mismatchはpre-write blockする。
- root間failure後はexternal same-version rerunで収束し、old engineへfallbackしない。
- ready markerは部分配置をnew versionとして公開しない。

## E384-07 proposal — Tooling Only Uninstall And Purge Compatibility Cutover

### Observable outcome

normal uninstallを4 fixed roots、valid owned exact skill slots、installation recordだけへ限定し、E384-02のaccepted purge compatibilityへcutoverする。

### Creation / start gate

- E384-02がacceptedである。
- E384-04がcompleteである。
- E384-06がaccepted implementation baseにある。

### Implementation plan

1. fixed owned targetsだけからtyped delete planを構築する。
2. 全targetのbinding、type、markerをmutation前に検証する。
3. dry-run / applyを同じresultからrenderし、tooling-only uninstallへCLIを切り替える。
4. purgeを残す場合は独立entrypoint / authorityへ移す。
5. update / retry / uninstallからpurge serviceへの到達不能をnegative testで証明する。
6. old deprovision / purge / cross-intent recovery routes、journals、tests、docsをreceipt付きで削除する。

### Acceptance / failure

- durable user data、generated projections、unknown paths、shared skill parent、unrelated skillsを変更しない。
- valid owner markerのexact slotだけを削除する。
- marker / binding mismatchは該当delete前にblockする。
- deprecated aliasはsilent purgeしない。
- defect時はapplyを停止し、dry-run diagnosticへ戻す。old engineへfallbackしない。

## E384-08 proposal — Contract Owned Pytest Portfolio And Zero Failure Cutover

### Observable outcome

durable contract ownerごとのsmall portfolioへtestを再配置し、active approved failure、policy-injected skip、per-file / journal / historical matrixをsteady stateから除去する。

### Creation / start gate

- E384-04 inventoryとE384-05 dispositionがcompleteである。
- E384-06、E384-07のproduction cutover evidence / receiptsがある。

### Implementation plan

1. fixed roots / slots / marker / orderをpure owner testsへ移す。
2. filesystem service testsをminimal synthetic workspaceとroot / slot fault injectionへ集約する。
3. CLI testsをparser、confirmation、exit、JSON / text mappingと代表pathへ縮小する。
4. package testsをexact built artifactの少数lifecycle smokeへ縮小する。
5. macOS固有nodeをplatform delta setへ分離する。
6. duplicate proofをlowest valid owner layerへ統合する。
7. E384-05のfix / retire / successorを一件ずつ実施する。
8. policy skipを撤去し、不要nodeはlane selectionでcollection対象外にする。
9. old nodeごとにcontract、retired route / successor、command、result SHAをreceipt化する。

### Acceptance / failure

- selected nodesはzero failure、zero active approved failure、zero policy skipである。
- 全nodeがcontract ID、owner layer、laneを持つ。
- seeded fault packの各faultに一つ以上のowner proofがある。
- selector omission時は正しいowner layerへtestを戻し、shard / approved failureを復活させない。

最終600秒budgetはE384-09 / E384-10が所有する。correctness proof削除とperformance達成を同じacceptanceにしない。

## E384-09 proposal — Single Process CI Graph Artifact Reuse And Budget Gate Cutover

### Observable outcome

canonical local / PR gateをone pytest process、worker 1、candidate build invocation 1、Linux canonical + macOS delta、duplicate node 0へcutoverし、Full Regression machineryを退役させる。

### Creation / start gate

- E384-03がacceptedである。
- E384-08がzero-failure portfolioを完成している。
- reference runner、artifact trigger、macOS delta policyが確定している。

### Implementation plan

1. candidate artifactをaccepted commandで一度buildし、source SHAと各output digestをreceiptへ固定する。
2. Linux canonical jobでexact artifactとsingle pytest processを使用する。
3. child-inclusive wall / user / system CPU、node、subprocess、workspace、copy bytesを計測するthin reporterを実装する。
4. same artifact bytesをmacOSへ渡し、accepted deltaだけを実行する。
5. lane node receiptsを比較し、same candidate / OS duplicate、build count、digest mismatchをfailureにする。
6. required checkを新gateへ切り替える。
7. ledger、timing weights、baseline evaluator、policy options、4-shard verifier、duplicate selectors、関連meta-testsを削除する。

### Acceptance / failure

- pytest process count 1、worker 1、shard / xdistなし。
- one-runでfailure 0、policy skip 0、duplicate 0、build invocation 1。
- metricsがcandidate SHA付きで出力され、budget超過はfailureになる。
- artifact missing / digest / source mismatchはtest開始前にfailする。
- selector omission時は全correctness portfolioをsingle processで実行するgateへ戻し、shard / approved failureを再導入しない。
- human PR merge gateを維持する。

## E384-10 proposal — Five Run Reference And Rolling 20 Stability Acceptance

### Observable outcome

同一final candidateでfixed Linux reference 5 runs、seeded fault pack、Linux / macOS smoke、rolling 20 canonical runsを完了し、Epic acceptanceをevidenceで閉じる。

### Creation / start gate

- E384-09がcompleteである。
- hard 2-vCPU / 8 GiB reference、same runner class、rolling trigger / retention、series reset条件が確定している。

### Evidence plan

1. dependency install後、networkなし、同一runner classで5回連続実行する。
2. 各runのcandidate SHA、artifact digest、wall / CPU、process、node、workspace、copy、build、duplicateをreceipt化する。
3. seeded fault expected / observed matrixを100%満たす。
4. accepted Linux / macOS smokeを実行する。
5. 同一series条件でrolling 20 runsのflake 0、retry 0、unexpected failure 0を確認する。
6. child / Epic reportとacceptance checkboxesを更新する。

全5回で次を満たす。

```text
pytest_process_count = 1
worker_count = 1
wall_seconds <= 600
(child_user_seconds + child_system_seconds) / wall_seconds <= 1.1
unexpected_failures = 0
approved_active_failures = 0
policy_skips = 0
duplicate_nodes_same_candidate_os = 0
artifact_build_count = 1
```

一回でもthreshold超過、failure、skip、duplicate、retryがあればEpicをcloseしない。E384-08またはE384-09のownerへ戻し、修正後は該当seriesをresetする。

## Sequence gates

### Gate 1 — Decision acceptance

`iss-00388`、`iss-00389`、`iss-00390`のProduct / Policy choicesをaccepted authorityとして固定する。

### Gate 2 — Inventory

E384-04を作成し、exact baseline SHAの全node inventory、duplicate grouping、removal receipt baselineを完成する。

### Gate 3 — Failure authority and install/update

E384-05はactive failuresを個別処置し、E384-06は4 roots + 2 slotsへcutoverする。両者は並行可能。

### Gate 4 — Uninstall

E384-06後、E384-07でtooling-only uninstallとpurge compatibilityへcutoverする。

### Gate 5 — Test portfolio

E384-05、E384-06、E384-07のauthority / receiptsを入力にE384-08を進める。

### Gate 6 — CI budget cutover

E384-09でsingle-process CI、artifact reuse、budget reportingへcutoverし、Full Regression machineryを撤去する。

### Gate 7 — Final evidence

E384-10でsame-candidate 5-run referenceとrolling 20 acceptanceを完了する。

## Epic verification

1. canonical regressionをworker 1で連続5回実行する。
2. child-inclusive wall / user / system CPU、subprocess、temp workspace、copied bytesを記録する。
3. local / Linux / macOS laneのexecuted node集合を比較し、same OS duplicate 0を確認する。
4. artifact receiptのsource SHA / digest / build countを確認する。
5. fresh / current / accepted legacy、root-inner drift、symlink、parent rebind、permission failure、root間stopをnew owner layerで検証する。
6. init、update、tooling-only uninstallとskill lifecycleをLinux built artifactで通す。
7. user dataとunrelated skillsがbyte-identicalであることを確認する。
8. plain zero-failure / zero policy skipを確認する。
9. baselineから削除した全production route / test / workflow machineryのremoval receiptを確認する。
10. SpecDock validation、lint、provider / dogfood parityを確認する。

performanceは最良値ではなく5回すべてを記録する。wall 600秒超、平均論理core 1.1超、worker追加依存、duplicate node、active approved failureのいずれかがあればEpic acceptance未達とする。

## Exit / handoff

- Requirementの全受け入れ条件を同一final candidateのevidenceで満たす。
- 4 disposable rootsとfixed skill slots以外へprovider delete authorityを持たない。
- canonical regressionがsingle process / 10分以内 / zero failure / zero policy skipである。
- duplicate nodes、approved failure ledger、4-shard runner、timing weightsが残っていない。
- distribution contractとtest ownershipをcode / test name / CI commandから理解できる。
- candidate labelはIssue作成時にactual `iss-xxxxx` IDへ置換する。
- E384-10 evidenceが揃う前にEpicをcloseしない。
- agentは各Issueをmerge-ready PRまで進めるが、mergeは人間が行う。
- Issue #372のdocs、branch、candidate、acceptance evidenceを変更しない。
