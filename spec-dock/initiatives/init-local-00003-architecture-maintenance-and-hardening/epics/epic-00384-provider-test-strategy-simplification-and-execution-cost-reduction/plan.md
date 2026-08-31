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

本Planはaccepted ADR `20260831t005139z-adr` を実装境界のauthorityとする。未決Product判断はdecision-only Issueで受理し、影響するproduction / CI Issueをその前に開始しない。Issue #372のcandidate、canonical docs、acceptance evidenceは変更しない。

すべてのproduction-changing child Issueは、依存済み`main`へ単独mergeした直後にreleasableでなければならない。Epic branchへimplementationを蓄積して最後に一括mergeしない。behavior変更、public adapter、docs、successor tests、built-artifact smoke、old route / test receiptを同じbehavior-owning Issueで完了する。

## Issue granularity assessment

- **Result**: `PROPOSED_ISSUE_CANDIDATES`
- **Decision basis**:
  - decision、inventory、external required-check transition、closeoutはruntimeを変更せず、独立した受入境界を持つsafe-transition / evidence scopeである。
  - 現行distribution engineはinstall / update / deprovision / purgeでmanifest、journal、admission、retry marker、result modelを共有する。install-first splitではnew workspaceをold uninstallが理解できないため、uninstall-first dual-reader bridgeを先にmergeする。
  - bridgeはlegacy writerを維持したままlegacy / future workspaceを読む。install / update cutoverはbridge merge後にnew writerを公開し、各merge pointで全public lifecycleをGREENにする。
  - 包括的tests-only Issueはbehaviorからproofを分離するため廃止する。testsはbehavior ownerへ移し、distribution外failureはinventoryからcontract ownerへfan-outする。
  - CI repository changeとGitHub external required-check changeは原子的でない。shadow追加、required set切替、old machinery撤去を別境界にする。
- **Current adoption**:
  - decision-only candidates D1〜D3は`iss-00388`、`iss-00389`、`iss-00390`として作成済みだがdecision未受理である。
  - C4〜C10、conditional C11、`FIX-<contract>`はproposalであり、creation gate通過後にactual `iss-xxxxx`を付与する。
- **Assumptions / unresolved evidence**:
  - 2,708 nodesと26 active failuresはhistorical observationであり、C4がexact baselineを再取得する。
  - dual-reader bridge、legacy recovery policy、bridge sunset、purge eligibility、external required-check authorityはProduct / Policy decisionが必要である。
  - bridgeを受理できない場合、C5とC6は一つのproduction vertical Issueへ統合する。
  - 10分budget、CPU比1.1、rolling 20はtargetであり、達成証拠ではない。

## Revised child Issue graph

| Label | Actual ID | 種別 | タイトル |
|---|---|---|---|
| D1 | `iss-00388` / #388 | Decision-only safe-transition | Legacy Direct Update Window And Gitignore Seed Policy |
| D2 | `iss-00389` / #389 | Decision-only safe-transition | Tooling Uninstall Spec History Purge And Public CLI Compatibility |
| D3 | `iss-00390` / #390 | Decision-only safe-transition | Retained Workflow Ownership And Artifact Platform Validation Policy |
| C4 | proposal | Evidence safe-transition | Receipt Binding Bootstrap And Rolling Test Contract Inventory |
| C5 | proposal | Production vertical | Lifecycle Compatibility Guard And Tooling-Uninstall Bridge |
| C6 | proposal | Production vertical | Install And Update Cutover To Disposable Roots And Fixed Slots |
| C5C6 | conditional proposal | Combined production vertical | Lifecycle Guard, Uninstall, Install And Update Atomic Cutover |
| FIX-* | conditional proposals | Production / test vertical | Behavior-Owned Active Failure Repair Or Contract Retirement |
| DEC-* | conditional proposals | Decision-only safe-transition | Behavior-Owned Expected-Behavior Decision |
| C7 | proposal | CI safe-transition | Canonical Portfolio And Shadow Provider Contract Gate |
| C8 | proposal | External-state safe-transition | Required Check Set Cutover |
| C9 | proposal | CI safe-transition | Legacy Provider CI And Full Regression Retirement |
| C10 | proposal | Closeout evidence | Fixed-Runner Budget And Stability Closeout |
| C11 | conditional proposal | Production vertical | Legacy Lifecycle Bridge Sunset |

固定10件を守ることは目的ではない。`FIX-*`の件数はC4 inventoryが示すdurable contract ownershipで決まり、C11はD1がEpic内sunsetを選んだ場合だけ作成する。

## Direct dependencies

```text
D2 ─┐
D3 ─┴─> D1 final compatibility matrix reconciliation
D1 + D3 ─> C4 Receipt Binding Bootstrap + Rolling Inventory

D1 ─┐
D2 ─┼─> C5 Tooling-Only Uninstall / Purge Bridge
D3 ─┤
C4 ─┘

D1 ─┐
D3 ─┼─> C6 Install / Update Cutover
C4 ─┤
C5 ─┘

C4 ─> DEC-<contract>*（expected behavior未決時）
C4 + matching DEC-* ─> FIX/RETIRE-<contract>*

D3 ─┐
C4 ─┼─> C7 Shadow Provider Contract Gate
accepted production-cutover path terminal（C5 then C6、またはC5C6） ─┤
all active failure dispositions terminal ─┘

C7 ─> C8 Required Check Set Cutover
C8 ─> C9 Legacy CI Retirement
C9 ─> C10 Final Closeout

D1 + C9 + accepted production-cutover path terminal ─> C11 Legacy Sunset（D1がEpic内sunsetを選んだ場合）
C11 ─> C10（作成された場合）
```

D2 / D3の調査とD1のdraft、C4のbaseline collectionは並行可能だが、acceptanceはD2 / D3 acceptance、D1 reconciliation、C4 finalizationの順にする。production writerはC5、C6を直列にするか、fallback時はC5C6だけを作成する。`FIX-*`はfile ownershipが重ならず、各contractが独立acceptanceを持つ場合だけ並行できる。

## Parent acceptance coverage

| Epic acceptance | Revised owner |
|---|---|
| legacy window / recovery / downgrade / `.gitignore` / `init --force` | D1 |
| tooling-only uninstall / purge eligibility / public CLI | D2 |
| workflow ownership / artifact-platform trigger / required-check authority | D3 |
| receipt binding bootstrap / full node inventory / rolling receipt head | C4 |
| uninstall-first compatibility bridge / post-uninstall reinstall | C5 |
| 4 roots + 2 slots + `InstallationRecordV2` / new writer | C6 |
| active failure fix / retirement / successor | matching `FIX-*`、C5またはC6 |
| expected behaviorを決定できないactive failure | matching `DEC-*` |
| behavior test ownership / removal receipt | each behavior-owning production Issue |
| single-process gate / build once / metrics / lane ownership | C7 |
| external required-check transition / human gate | C8 |
| ledger / timing / shard / old workflow retirement | C9 |
| five reference runs / seeded faults / rolling 20 | C10 |
| finite legacy reader / recovery adapter removal | C11 when D1 requires Epic-local sunset |

## D1 — `iss-00388` decision-only

### Observable outcome

legacy direct-update window、markerless slot migration、`.gitignore`、`init --force`に加え、package / workspace compatibility、active legacy recovery、bridge sunsetをaccepted decisionにする。

### Required decisions

- `P0` / `P1` / `P2` / `P3`と全canonical state、全public operation、inspect / dry-run / apply execution modeのallow / fail-closed / N/A matrix。retryとlegacy aliasも明示する。
- active legacy journalをbounded recovery-only adapterで扱うか、last-compatible packageへpinするか。
- `P0`がnew guardを検出してmutation前に停止する条件。
- legacy reader / fixtures / testsをEpic内で削除するか、期限付きfollow-upへ渡すか。
- finite tree evidence、version / date sunset、unknown preserve-and-block。

production code、tests、assets、workflowは変更しない。

### Acceptance dependency

D2 / D3のaccepted decisionsを正式inputとして取り込み、単一compatibility matrix digestを作る。全cell coverage 100%、multiple authority 0、D1 / D2 / D3 conflict 0になるまでD1をacceptしない。

## D2 — `iss-00389` decision-only

### Observable outcome

normal uninstall、独立purge、deprecated `--remove-specs`、confirmation、public resultに加え、tooling uninstall後のpurge eligibilityを一意なcontractにする。

### Required decisions

- installation record削除後に独立purge targetを証明するevidence。
- deprecated aliasのparser error / non-mutating deprecation / independent confirmation。
- cleanup-pendingのsuccess / warning / partial failure / failure semantics。
- `tooling-absent-preserved-data`からのreinstall authority。
- legacy / new workspaceでのdry-run / apply、text / JSON、exit、retry guidance。

production code、tests、assets、workflowは変更しない。

## D3 — `iss-00390` decision-only

### Observable outcome

shipped workflow ownership、artifact / platform triggerに加え、GitHub ruleset / branch protection / merge queueのauthority、required context名、変更owner、shadow acceptanceをaccepted policyにする。

### Required decisions

- current external required contextsとhuman review requirementのauthority / owner。
- new workflow / job / contextのstable name。
- required化前の連続GREEN数、C7 failure-detection canary、C8 required-set enforcement canary、retention。
- old + new required、new-only required、old workflow removalのtransition receipt。
- wheel / sdist / Linux / macOS trigger、artifact digest、reuse、retention。

workflow YAML、reporter、artifact builderは変更しない。

## C4 proposal — Receipt Binding Bootstrap And Rolling Test Contract Inventory

### Observable outcome

exact baseline SHAの全collected nodeをdurable contract、owner layer、current / target lane、cost、disposition、owner Issueへ100% mappingし、後続PRが更新できるrolling inventory headを作る。

### Creation / start gate

- exact baseline SHAを固定する。node collection / cost計測はD1〜D3と並行開始できるが、C4 completionはD1 / D3 acceptance後とする。
- historical 2,708 / 26 countsをauthorityとして再利用しない。

### Acceptance

- collected node setとinventory node setが一致し、missing disposition / unknown ownerが0。
- active failure nodeをdurable behavior ownerへ割り当て、判断不能nodeだけ個別decision candidateにする。
- production route / manifest / journal symbolのconsumer graphを記録し、C5で削除候補となるsymbolがlegacy install / updateから非参照かを判定する。
- existing required contextsとhuman review gateを変更しないadditive non-required workflow/check producerをC4がbootstrapする。必要なGitHub token / App権限、workflow event、stable check name、artifact permissionを明示する。
- `InventoryHeadV1`とrepository内`RemovalReceiptDeltaV1`がparent SHA、inventory before / after digest、change manifest digest、verification result digestを持つ。result SHAはGitHub Actions check run `Provider Receipt Binding`のcheck_run_id、content-addressed artifact_id、retention_daysでreceipt digestへ束縛し、次IssueがGitHub APIで取得・照合できない場合はfail closedにする。
- bindingにはartifact server IDとartifact content digestを含める。PR headでproducerを実証し、main pushでactual merged commitへ再bindingする。C4自身のrepository receipt / actual merged SHA / artifactを最初のend-to-end acceptanceとする。
- rollbackはnon-required producerだけを別PRで撤去し、既存required contexts、ruleset、review requirementを変更しない。producerがGREENでactual main bindingを生成するまでC4をcompleteにしない。
- rebase後の再生成、parallel PRのmerge-order再照合、latest head consumptionを検証する。

production codeとbehavior testsは変更しない。binding producerのadditive workflow / scriptとinventory artifactsだけを変更するsafe-transitionとする。

## C5 proposal — Lifecycle Compatibility Guard And Tooling-Uninstall Bridge

### Observable outcome

legacy install / update writerを維持したまま、exact lifecycle compatibility contract、legacy update / `init --force` admission guard、tooling-only uninstall / accepted purge surfaceを一つのvertical compatibility bridgeとしてcutoverする。

### Creation / start gate

- D1、D2、D3がaccepted。
- C4 latest inventory headがcomplete。
- D1統合matrix digestを取得し、全cell coverage 100%、multiple authority 0、D1 / D2 / D3 conflict 0を確認する。
- D1がP0 policyと成立しない場合のformat / release sequence再審議authorityをacceptedにしている。C5開始前に未作成のcanonical fixtureを要求しない。
- C4 production symbol graphで削除候補journal / manifest symbolsがlegacy install / updateから非参照である。分離不能ならC5 / C6をcombined vertical Issueへ置換する。
- bridgeをProduct contractとして受理。拒否された場合はC5 / C6をcombined vertical Issueへ置換する。

### Stable contract

- `LifecycleCompatibilityContractV1`、`InstallationRecordV2`、`SkillSlotMarkerV1`、`LifecycleStateReaderV1`、`ToolingDeletePlanV1`、conditional `PurgeOperationRecordV1`、`PurgeAuthorityV1`、`LifecyclePublicResultV1`。
- C5がexact record / marker path、serialized schema / version、canonical ready-v2 / updating-v2 / slot fixtures、invalid / unknown / future cases、root / slot completenessを固定する。C6はfixture producerではなくconformance ownerである。
- dual-reader / single-writer。old/new uninstall writerをruntime toggleで併存させない。
- legacy-readyとfuture ready-v2をread-only分類する。
- ready-v2はuninstall / dry-runを許可し、P1 legacy update / init-forceはC5が追加するadmission guardでfail closedにする。
- updating-v2、unknown roots、foreign / invalid slots、active unresolved recoveryではdestructive actionをblockする。

### Vertical acceptance

- C5内部の順序を`contract / fixture freeze -> immutable P0 probe -> production bridge`に固定する。probe failureならtarget mutationを開始せず親へ戻し、format / release sequenceを再設計する。
- legacy install / updateが引き続きGREEN。
- new tooling-only uninstall、accepted purge、confirmation、JSON / text / exitがGREEN。
- tooling-only uninstall後にuser data / generated projectionがbyte-identicalで残り、accepted legacy install routeで再installできる。
- C5が固定したcanonical ready-v2 / updating-v2 fixtureをnew uninstallとP1 admission guardが処理する。C6は同じfixtureへconformする。
- exact P0 artifactがC5-frozen canonical new fixturesをmutation-zeroでblockする。不能ならdecisionで上書きしない。
- exact successor node IDsをcurrent authoritative required command / contextで実行し、collected = executed、policy skip 0、affected package / platform smoke GREENを証明する。
- successor tests成立後に限り、legacy install / updateから非参照とC4が証明したold deprovision / purge専用routes、journals、testsだけをreceipt付きで削除する。shared symbolはC6またはcombined Issueまで残す。
- built artifactでinstall → tooling uninstall → reinstallの代表lifecycleを通す。
- exact tooling-uninstall allowlistは4 roots、valid owned 2 slots、fixed installation recordだけとする。shipped workflowは常にpreserveする。D3がdeleteを選ぶ場合はparent ADRを改定し、C5 scope / testsへ明示追加するまで開始しない。
- 最初のtooling delete前にrecordを`uninstalling-v2(delete_plan_digest=P)`へatomic replaceし、4 roots、current 2 slotsの後にrecordを最後に削除する。valid owned slotはbounded tombstoneへatomic renameしてからcleanupする。各root delete前後、scripts後、slot tombstone rename / cleanup前後、record delete failureを注入し、same-plan rerun convergenceとforeign tombstone blockを証明する。
- D2がindependent purgeを残す場合は別fixed `PurgeOperationRecordV1`で各target delete境界、record last、same-plan rerun、別plan blockを証明する。retireの場合はN/A receiptを残す。

### Recovery / rollback

- destructive defectではapplyを停止し、read-only diagnosticへ戻す。
- C6前はlegacy install / update writerを維持する。
- C6後のrollback baseとしてready-v2をuninstallできるがupdateしない。
- old engineへのautomatic fallbackを行わない。

## C6 proposal — Install And Update Cutover To Disposable Roots And Fixed Slots

### Observable outcome

C5 bridge上でfresh / init / update writerを4 disposable roots、2 fixed skill slots、`InstallationRecordV2`へcutoverし、new writerが公開する全workspaceをmerge済みuninstallが理解する。

### Creation / start gate

- D1、D3がaccepted。
- C4 latest inventory headがcomplete。
- C5がmerge済みで、C5-owned canonical ready-v2 / updating-v2 fixturesに対するuninstall / admission proofがGREEN。
- C5-owned `LifecycleCompatibilityContractV1`が固定され、C6 writerが変更せずconformできる。

### Vertical acceptance

- fresh、legacy one-shot migration、ready-v2 update、tooling-only uninstall、accepted purge、post-uninstall reinstallが一つのpublic lifecycle matrixでGREEN。
- 4 roots / 2 slotsを完全stage・validateし、全配置後だけready recordをatomic replaceする。
- root間failure後はsame desired version / digestのexternal rerunだけで収束する。
- 最初のdestructive step前にfixed recordをupdating-v2 / desired version / digestへatomic replaceし、全配置後だけready-v2へ遷移する。
- updating record成功後の全faultでauthoritative recordはupdating-v2のまま、ready-v2 authorityはabsent、許可mutationはsame desired version / digest updateだけである。物理的に残るlegacy ready markerはnon-authoritativeで、全readerがfixed recordを優先する。
- user data、generated projections、unknown paths、shared skill parent、unrelated skillsがbyte-identical。
- `P0` / `P1` updateはready-v2 / updating-v2をmutation前にfail closedにする。
- successor tests、package smoke成立後にold per-file update、historical manifest、update journal / checkpoint、対応testsをreceipt付きで削除する。
- exact successor node IDsをcurrent authoritative required command / contextで実行し、collected = executed、policy skip 0、affected package / platform smoke GREENを証明する。
- updating record前後、最初のroot削除前、各root delete前 / delete後・rename前 / rename後、root間、各current slot delete前 / delete後・rename前 / rename後、2 slots間、finite retired slot削除の各境界、全slot後 / ready前、stale staging mismatch、ready write failureをfault acceptanceに含める。
- 各fault後のsame-version / same-digest rerun convergenceと、invalid / foreign / markerless slotのbyte-identical preserve-and-blockを証明する。C5のskill delete proofはtooling uninstallによるvalid owned current 2 slots削除に限定し、C6 updateのcurrent slot replacement / retired slot deletionはC6が所有する。

### Recovery / rollback

- stage failureはtarget mutation 0。
- updating-v2はsame desired external rerun以外をblock。
- defect時はnew apply routeを停止し、C5 uninstall / diagnosticを維持する。
- old update engineへautomatic fallbackしない。

## C5C6 conditional proposal — Combined Lifecycle Cutover

C4 consumer graphでC5削除候補がlegacy install / updateと分離不能、またはuninstall-first bridgeをProduct contractとして受理できない場合だけ作成する。fallback decision時はC5 / C6を作成・開始せず、actual combined Issue ID、dependencies、owned symbols / nodesをlatest inventory headへ記録する。

### Creation / start gate

- D1 / D2 / D3、C4、統合matrix digestがcomplete。
- combined理由、C5 / C6 terminal disposition=`replaced-before-start`、actual Issue IDをparentへ記録する。
- C5とC6のstable contracts、fault sets、behavior tests、built-artifact smoke、receipt obligationsを一つも省略せず同じIssueへ移す。

### Vertical acceptance

- legacy workspaceからnew reader / writer / uninstallへ一度にcutoverし、中間のpublic package generationを公開しない。
- fresh、legacy migration、ready / updating / uninstalling、tooling uninstall、conditional purge、post-uninstall reinstallを同一matrixでGREENにする。
- exact successor nodesをcurrent required gateでcollected = executed、policy skip 0、package / platform smoke GREENにし、old route / testsを二層receipt付きで同じPRから削除する。
- 単独merge後に後続C5 / C6なしでreleasableである。

C7のdependencyは具体的なC5 / C6名ではなく、`accepted production-cutover path terminal`、すなわち`C5 then C6 complete`または`C5C6 complete`の一方だけとする。

## DEC-<contract> / FIX-<contract> conditional proposals

C4 inventoryが確認したactive failureを、durable contract ownerごとの最小decision / vertical Issueへfan-outする。expected behaviorがcurrent authorityから決まらない場合は先に`DEC-<contract>`を作り、accepted authorityを`FIX/RETIRE-<contract>`へ渡す。

各candidateは次を持つ。

- 一つのobservable public behaviorまたはsecurity invariant。
- production fix、public adapter、docs、successor testsを同じIssueで完了する。
- exact old node、fix / retirement / successor、focused command、repository内parent/digest receiptとout-of-band result SHA binding。
- matching Issue単独merge後にzero failure / zero policy skip。
- actual Issue ID、dependency、owned node set、terminal dispositionをlatest inventory headへ記録する。
- exact successor nodeをmerge時点のauthoritative required command / contextで実行し、collected = executed、policy skip 0を証明する。

current authorityからexpected behaviorを決定できないnodeは、実装Issueを作らず個別`DEC-*`へ戻す。C7開始前にbaseline上の全active failure nodeが`fixed and GREEN`、`retired by accepted authority`、`replaced by exact successor and GREEN`のいずれかへterminal化し、`active_failure_count = 0`でなければならない。unrelated contractを一つのfailure cleanup Issueへ集約しない。

## C7 proposal — Canonical Portfolio And Shadow Provider Contract Gate

### Observable outcome

candidate build once、Linux canonical single-process portfolio、macOS platform delta、metrics、duplicate detectorをnon-required shadow gateとして追加し、old required gateを維持したままsuccessor gateを証明する。

### Creation / start gate

- D3 accepted。
- accepted production-cutover pathと全`DEC-*` / `FIX-*`がterminal。
- C4 latest inventory headでzero unresolved ownerかつ`active_failure_count = 0`。

### Acceptance

- new contextはstable nameを持ち、old workflow / contextsを変更しない。
- exact candidate artifactを一度buildし、source SHAと各output digestを固定する。
- Linuxはsingle pytest process / worker 1、macOSはaccepted deltaだけを同じartifact bytesで実行する。
- process-tree wall / CPU、node、subprocess、workspace、copy bytes、build count、duplicate countを報告する。
- shadowはnon-required、owner、expiry、C9 retirement ownerを持つ。
- D3で決めた連続GREENとfailure-detection canaryを満たす。意図的故障でnew check自身がREDになることだけを証明し、non-required shadowによるmerge blockは要求しない。
- selector omission時は全correctness portfolioをsingle processで実行し、shard / approved failureへ戻さない。
- C5 / C6 / FIXで既にauthoritative実行済みのnodeだけを非重複laneへ移す。未実行successor proofや新behavior testをC7で初めて有効化しない。

## C8 proposal — Required Check Set Cutover

### Observable outcome

unrelated effective required contextsを`U`として、GitHub external stateを`U + old`から`U + old + new`、`U + new`へ移し、human review requirementを維持する。

### Creation / start gate

- C7 shadow acceptance complete。
- current ruleset / branch protection / merge queue、required contexts、review requirement、ownerをlive取得する。
- resolved ownerが各transitionを実行できる権限を持つことを確認する。

### Acceptance

- before / afterのeffective required set全体、対象branch / ruleset scope、review requirementをreceipt化し、`U`を集合差分でpreserveする。
- oldと`U`を残したままnew contextをrequiredへ追加する。
- required-set enforcement canary PRで`U`とoldを全てGREEN、新だけを意図的にREDにしhuman mergeがblockされ、GREEN復帰後に進める。
- merge queueがactiveならmerge-group eventでもcontext生成と同じblockを確認する。
- old contextをrequired setから外し、`U + new`だけがeffective required setでreview gateも残ることを確認する。
- `RequiredCheckTransitionReceiptV1`を保存する。
- C8 receiptは`U + old -> U + old + new -> U + new`までのappend-only chain headとして保存し、C9がold workflow removalとpost-removal live stateを追記し、C10がfinalizeするowner分担を記録する。

### Rollback

C9前はold workflowがrepositoryに残るため、new defect時にold contextをrequiredへ再追加できる。new contextを外すのはold context復旧確認後だけとする。

## C9 proposal — Legacy Provider CI And Full Regression Retirement

### Observable outcome

new check名を維持したまま、old Provider CI duplicate lanes、post-merge Full Regression、ledger、timing weights、baseline evaluator、policy skip、4-shard verifierを撤去する。

### Creation / start gate

- C8 receiptがnew-only requiredとhuman review gateを証明する。
- old contextsがexternal required setに含まれないことをlive再取得する。

### Acceptance

- C9 result candidate SHAをmerge前に固定し、そのexact result treeをbaseにexact inverse patchまたはC9全体revertを適用したrestoration branchを作る。
- restoration bundleはworkflow、scripts、selectors、policy configuration、ledgerを含むold contextの全transitive dependencyとdigestを持ち、C9 result treeへclean applyできる。
- old workflowがbase branchから消えた状態のPR eventでold contextをnon-required生成してGREENにし、merge queue active時はmerge-groupでも生成する。
- removal PR自体がnew required gateでGREEN。
- authoritative lane間duplicate 0、artifact build invocation 1、policy skip 0。
- removed workflow / node / selector / ledgerごとにsuccessorまたはretirement receiptがある。
- old workflow不存在のままold contextをrequiredへ戻さない。
- C8の`RequiredCheckTransitionReceiptV1` chainへexact old workflow removal、post-removal live effective required set、ruleset scope、human review、merge queue resultを追記する。
- C9 repository receiptにresult tree SHAを保存する。post-merge `main`のactual commit / tree SHAを`Provider Receipt Binding`で照合し、prevalidated treeと異なる場合はactual merged tree上でrestoration bundleとreceiptを再生成・再canaryしてからC9をcompleteにする。

### Rollback

旧contextへ戻す必要がある場合は、上記C9 exact result tree起点のrestoration branchを使う。new checkが全面RED / pendingでも、restoration PRのold checkをnon-requiredでPR / merge-group上に起動し、`U + old + new`へ追加、oldと`U`のGREENを確認してから`U + old`へ戻す。その後human reviewを維持したままrestoration PRをmergeする。required testが0になる瞬間を作らない。

## C10 proposal — Fixed-Runner Budget And Stability Closeout

### Observable outcome

同一final candidateでfixed Linux reference 5 runs、PR critical path 5 runs、seeded fault pack、Linux / macOS smoke、rolling 20 canonical runsを完了し、Epic acceptanceをevidenceで閉じる。

### Creation / start gate

- C9 complete。
- C11を作成するdecisionの場合はC11 complete。
- hard 2-vCPU / 8 GiB reference、same runner class、rolling trigger / retention、series reset条件が確定。

### Evidence acceptance

```text
pytest_process_count = 1
worker_count = 1
wall_seconds <= 600
process_tree_cpu_seconds / wall_seconds <= 1.1
unexpected_failures = 0
approved_active_failures = 0
policy_skips = 0
duplicate_nodes_same_candidate_os = 0
artifact_build_count = 1
```

final candidateはcommit SHA、artifact digest、node inventory digest、runner classの組で定義する。一つでも変わればseriesをresetする。一回でもthreshold超過、failure、skip、duplicate、retryがあればEpicをcloseせず、matching behavior owner、C7またはC9へ戻す。

- local canonical command 5 runsとPR critical-path 5 runsを別seriesとして全回記録する。
- rolling 20のtrigger、candidate tuple、reset条件、全20 resultを記録する。
- seeded fault packの各faultとowner nodeを列挙し、100% detectionを確認する。
- Linux / macOS各accepted smokeのtest bodyが600秒以内である。
- latest final `InventoryHeadV1`を再生成し、全node / removal receipt coverage 100%、active failure 0を確認する。
- C8 / C9の`RequiredCheckTransitionReceiptV1` chainをfinal live effective required set、ruleset scope、human review requirement、merge queue behaviorへ再照合してfinalizeする。
- C11をEpic外へ送る場合はactual follow-up Issue ID、owner、expiryをclose gateで再確認する。

## C11 conditional proposal — Legacy Lifecycle Bridge Sunset

D1がEpic内sunsetを選んだ場合だけ作成し、C9とaccepted production-cutover pathの完了後に開始する。

### Observable outcome

finite legacy reader / recovery-only adapterと対応testsを削除し、P3 new-only lifecycleをGREENにする。

### Acceptance

- legacy-readyはactionable diagnostic付きでmutation前にfail closed。
- ready-v2のinstall / update / uninstall / accepted purgeがGREEN。
- removed adapter、fixtures、testsにreceiptがある。
- unknown / foreign stateのpreserve-and-blockを維持する。
- exact successor node setを固定し、current new required contextでcollected = executed、policy skip 0を証明する。
- P3 built-artifact lifecycle smoke、public diagnostic / docs update、unaffected lifecycle command GREENを同じPRで完了する。
- repository内receiptとout-of-band result bindingをlatest inventory chainへ追加し、後続Issueなしでreleasableであることをmerge pointで証明する。

### Creation gate

- C9 complete、accepted production-cutover path terminal、latest inventory head取得済み。
- new contextがcurrent ruleset scopeでrequiredであること、human review requirement、merge queue behaviorをlive取得する。
- C11-owned successor node setとremoval targetsをlatest inventory headへ固定する。

D1がsunsetをEpic後へ送る場合、Requirementはfinite bridgeが残ったままclose可能であることと、owner follow-up / expiryを明示する。

## Test ownership

| Test family | Behavior owner |
|---|---|
| legacy admission / recovery / downgrade / post-uninstall reinstall | C5、decisionはD1 |
| tooling-only uninstall / delete plan / purge / confirmation / public result | C5、decisionはD2 |
| root staging / replacement / ready / updating / same-version rerun | C6 |
| fixed skill write lifecycle | C6 |
| tooling uninstallによるvalid owned current fixed skill delete lifecycle | C5 |
| updateによるcurrent slot replacement / finite retired slot deletionと全slot fault境界 | C6 |
| `.gitignore` / `init --force` | C6、decisionはD1 |
| shipped workflow asset ownership | decisionはD3。既定はpreserve、update mutationを選ぶ場合はC6、uninstall deleteを選ぶ場合はADR改定後のC5 |
| distribution外active failure | matching `FIX-*` |
| built artifact init → update → uninstall lifecycle | C6を主ownerとしC5 contractも同じsmokeで通す |
| macOS固有filesystem / mode / executable | behavior-owning Issueでnode作成、lane assignmentはC7 |
| user data誤書込み / allowlist外削除 / marker mismatch / destructive recovery faults | C5 |
| root間failure / same-digest rerun / staging-record mismatch | C6 |
| artifact欠落 / digest mismatch / selector / duplicate / metrics | C7 |
| ledger / timing / shard / policy skip meta-tests | C9 |

旧testを削除する各PRは、old node ID、durable contract、exact successorまたはaccepted retirement authority、owner Issue、focused command、parent SHA、inventory / manifest / verification digestsをrepository内receiptへ持ち、result SHAをout-of-band immutable bindingでそのreceiptへ結ぶ。

## Sequence gates

### Gate 1 — Decisions and rolling inventory

D2 / D3を先にacceptし、D1が単一compatibility matrixへreconcileしてdigest、coverage 100%、multiple authority 0、conflict 0を確定する。C4は並行してbaseline collectionを行えるが、D1 / D3後にnon-required receipt binding producerとactual-main bootstrap receiptを完成し、latest inventory headを確定する。

### Gate 2 — Uninstall-first bridge

C5 / C6分離がacceptedならC5を単独mergeし、legacy install / update、新uninstall / purge、post-uninstall reinstallを統合GREENにする。fallbackならC5C6だけをGate 3までのcombined production verticalとしてmergeする。

### Gate 3 — Install / update writer cutover

C5 / C6分離時はC6を単独mergeし、P2 lifecycleとP0 / P1 fail-closed downgrade matrixをGREENにする。fallback時はC5C6 completionをaccepted production-cutover terminalとする。

### Gate 4 — Behavior-owned failure repairs

必要な`DEC-*`をacceptした後、`FIX/RETIRE-*`をcontract ownerごとにmergeし、baseline上の全nodeをterminal dispositionへ移してactive approved failureを0にする。各merge後のmainをGREENに保つ。

### Gate 5 — Additive shadow gate

C7でnew gateをnon-required shadowとして追加し、old required gateを維持する。

### Gate 6 — External required-check cutover

C8でold + new requiredを経てnew-only requiredへ移す。old workflowは残す。

### Gate 7 — Old machinery retirement

C9でold workflow / ledger / shard / policy skipを撤去する。

### Gate 8 — Optional legacy sunset

D1がEpic内sunsetを要求した場合だけC11をmergeする。

### Gate 9 — Final evidence

C10でsame-candidate 5-run referenceとrolling 20 acceptanceを完了する。

## Epic verification

1. child PRごとにmerge parent上のpublic lifecycle matrixを実行し、後続Issueなしでもreleasableであることを確認する。
2. canonical regressionをworker 1で連続5回実行する。
3. root processと全descendantのwall / user / system CPU、subprocess、temp workspace、copied bytesを記録する。
4. local / Linux / macOS laneのexecuted node集合を比較し、steady-state same OS duplicate 0を確認する。
5. artifact receiptのsource SHA / digest / build countを確認する。
6. P0 / P1 / P2 compatibility matrix、legacy / current、root-inner drift、symlink、rebind、permission、root間stopをowner layerで検証する。
7. init、update、tooling-only uninstall、accepted purge、post-uninstall reinstallをbuilt artifactで通す。
8. user data、generated projections、unknown paths、unrelated skillsがbyte-identicalであることを確認する。
9. plain zero-failure / zero policy skip / zero approved failureを確認する。
10. baselineから削除した全production route / test / workflow machineryのrolling removal receiptを確認する。
11. required-check transition receiptとlive external stateを照合する。
12. SpecDock validation、lint、provider / dogfood parityを確認する。

## Exit / handoff

- Requirementの全受け入れ条件を同一final candidateのevidenceで満たす。
- 各production-changing child Issueを依存順に`main`へmergeし、各merge pointのreleasabilityを証明する。
- tooling uninstallのdelete authorityは4 disposable roots、valid owned fixed skill slots、fixed installation recordだけに限定する。shipped workflowはparent ADR改定とC5 acceptance追加なしに削除しない。
- canonical regressionがsingle process / 10分以内 / zero failure / zero policy skipである。
- duplicate nodes、approved failure ledger、4-shard runner、timing weightsが残っていない。
- distribution contractとtest ownershipをcode / test name / CI commandから理解できる。
- proposal labelはIssue作成時にactual `iss-xxxxx` IDへ置換する。
- C10 evidenceが揃う前にEpicをcloseしない。
- agentは各Issueをmerge-ready PRまで進めるが、mergeは人間が行う。
- Issue #372のdocs、branch、candidate、acceptance evidenceを変更しない。
