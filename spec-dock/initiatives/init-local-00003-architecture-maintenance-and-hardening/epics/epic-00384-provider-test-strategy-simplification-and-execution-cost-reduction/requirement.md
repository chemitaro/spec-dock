---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-08-31"
親: ["init-local-00003"]
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

詳細: [Requirement Guide](../../../../docs/authoring/requirement.md)

## 目的

SpecDock provider のテストを、並列実行で待ち時間だけを隠す仕組みから、必要な契約を最小の実行量で証明する仕組みへ置き換える。開発者が通常使う回帰確認は、shard や `pytest-xdist` を使わない単一の `pytest` process で10分以内に完了し、同じ candidate・OS で同じ契約を重複実行しない状態を成果とする。

テストだけを削るのではなく、テスト件数を生んでいる install / update / uninstall / spec-history purge の product contract も見直す。安全上必要な不変条件は残し、利用者価値を持たない自動復旧、歴史的互換性、状態の組合せは product contract から縮小してからテストを廃止する。

## 背景

Issue #372 は distribution hard cutover と parity を対象とし、Full Regression を4 shardで実行する仕組みを導入している。この仕組みは証拠を分割して壁時計を短縮するが、テスト実行量そのものは減らさない。最新 branch の実測では、2,708 tests の GitHub Full Regression が約99分の壁時計と約5.51 shard-process-hoursを使った。別のローカル実測でも約27分の壁時計に対して約87.65 shard-process-minutesを使っている。利用者からは、別時点の逐次実行が約4時間、並列実行中は約10分にわたりCPUがほぼ100%になるとの観測がある。

通常の PR gate も `1567 passed, 1141 skipped in 650.55s` であり、すでに目標の10分を超える。Full Regression はこの1,567 fast testsを再度実行する。distribution parity は Ubuntu 上で通常 gate と同じ575件の `test_managed_distribution.py` を再実行し、さらに Linux / macOS で cutover と package parity を繰り返す。

テスト量は production design と分離できない。`src/spec_dock/managed_distribution.py` は22,332行、41 classes、454 functions / methodsを持ち、provider Python sourceのおよそ44%を占める。対応する4つの主要 test filesだけで約35,000行ある。単純なローカルツールという product goal に対し、per-path identity、journal、retry marker、crash checkpoint、historical compatibility、deprovision、spec-history purge の組合せが永続的な契約になっていることが、テスト肥大化の主因候補である。

本 Epic は親 Initiative の architecture hardening 方針を維持しつつ、「安全であること」と「すべての歴史的・異常状態を自動回復すること」を分離する。Issue #372 の candidate を直接変更せず、独立した product / test architecture outcome として扱う。

## 観測可能な要件

### R0. merge-point releasability

- production code、public CLI、workflowのいずれかを変更するchild Issueは、そのIssueだけを依存済み`main`へmergeした直後にreleasableな状態を残す。
- behavior変更に必要なpublic adapter、docs、successor tests、built-artifact smoke、old contract / test removal receiptを同じbehavior-owning Issueで完了し、tests-onlyの後続Issueへ延期しない。
- 影響を受けないaccepted public lifecycle commandは全てGREENを維持する。後続Issueが未mergeであることを理由にbroken、skip、approved failure、quarantineを許可しない。
- production contractを削除する前に、exact successor proofまたはaccepted retirement authorityを同じPRで成立させる。
- Epic branchへ全implementationを蓄積して最後に一括mergeする運用を採らない。各child PRを依存順に`main`へ統合し、各merge pointを検証する。

### R1. 一つの実行時間予算

- 開発者向け canonical regression command は、単一の `pytest` processで全ての merge-required contractを実行する。
- 同一条件で連続5回計測した各回が、dependency installとlintを除く test bodyで600秒以内となる。
- CIのreference measurementはdependency install完了後、fresh workspace、network accessなし、Linux 2 vCPU hard quota、8 GiB memoryを基本とする。GitHub-hosted runnerがhard quotaを保証できない場合は2 vCPU containerまたはdedicated runnerでreferenceを取得する。
- canonical commandは内部でshard、`pytest-xdist`、並列test workerを起動しない。テストが起動するCLI subprocessも、1 test内で明示的に必要なものを除き直列とする。
- 計測はwall secondsだけでなく、user + system CPU seconds、subprocess数、temp workspace作成数、同一nodeの重複実行数を残す。
- child processを含む `user + system CPU seconds / wall seconds` を平均論理core使用数として扱い、canonical local regressionの5回すべてで1.1以下とする。これにより、短い起動overlapを許しつつ、複数coreを長時間使い切る設計を禁止する。

### R2. 重複実行ゼロ

- steady stateでは、同じcandidate・OS・契約について、authoritative lane間で同じtest nodeを複数回実行しない。
- CI migration中のshadow laneだけは、non-required、owner、expiry、retirement Issueを持ち、duplicateをcandidate SHA付きで明示計測する場合に限り一時重複を許可する。required-check切替完了後はshadow / old laneを撤去し、最終acceptanceでduplicate 0へ戻す。
- platform固有の差分を確認するtestだけを各OSで実行し、OS非依存のdomain / service contractをLinuxとmacOSの双方で繰り返さない。
- wheelとsdistはcandidateごとに一度だけbuild・hash固定し、その同じartifactを必要なsmokeで再利用する。

### R3. 契約追跡可能性

- 残すすべてのtest familyは、現在のpublic behaviorまたはsecurity invariant、責務を持つlayer、実行lane、代表する失敗を一つ以上持つ。
- historical Issue / Step 名だけを根拠とするtestは、durable invariantへ改名・統合するか、対応契約とともに削除する。
- test削除は、同じ invariant をより低い層で証明するtest、または product contract の廃止記録に結び付ける。

### R3A. baseline-bound inventory and removal receipt

- production route、test node、workflow、ledger、selectorを削除する前に、full baseline SHAへ束縛したnode inventoryを作成する。
- inventoryは全collected nodeについて、durable contract、owner layer、current lane、target lane、cost evidence、keep / move / consolidate / delete-after-retirement、owner Issueを持つ。
- delete対象はretired production contractのaccepted authority、またはexact successor nodeを持つ。
- removal receiptはold node / route、successorまたはretirement authority、owner Issue、verification commandを持つ。repository内receiptには自己参照になるresult SHAを書かず、merge parent SHA、inventory before / after digest、change manifest digest、verification result digestを保存する。
- baseline SHA変更後に旧inventoryを黙って再利用しない。
- baseline inventoryを`S0`へ束縛し、各削除PRはmerge parent SHA、node inventory before / after digest、change manifest digest、verification result digestのdelta receiptを作る。out-of-band authorityはresult commit上のGitHub Actions check run `Provider Receipt Binding`とし、result SHA、repository内receipt digest、check_run_id、content-addressed artifact_id、retention_daysを記録する。次IssueはGitHub APIで取得・digest照合し、check / artifact消失、期限切れ、SHA / digest不一致ならfail closedにする。rebase後はrepository内receiptとbindingを再生成する。
- 次のIssueはlatest inventory headだけをconsumeする。並行PRはmerge順確定後にrebaseし、node set、owner、receiptを再照合する。

### R4. layerごとの証明責務

- domain testは純粋な状態遷移・validation・propertyを網羅し、filesystem、Git、package build、CLI processを起動しない。
- filesystem / application contract testは、最小synthetic workspaceと注入可能なfaultを使い、OS境界の代表ケースだけを扱う。
- CLI testはargument / exit code / JSON・text mappingと、代表的なhappy path・fail-closed pathに限定する。
- package / platform testはbuilt artifactのprovenanceと、init・update・uninstallの最小end-to-end smokeだけを扱う。

### R5. distribution product contractの簡素化

- `spec-dock/initiatives/**` とnested Artifactsをdurable user dataとし、init / update / tooling uninstall / retry / cleanupの変更対象にしない。
- `spec-dock/active/**`、`spec-dock/.agent/**`、dashboard、tree / deps図、ADR mirrorなどの再生成可能なprojectionをprovider file inventoryやhistorical identityの管理対象にしない。
- provider-owned repo-local contentは `spec-dock/{docs,templates,system,scripts}` の4 fixed rootsとし、updateではcandidateを全てstage・validateした後、root内部を保存せずroot単位で全量置換する。`scripts` は最後に置換する。
- disposable root内部のuser editは保存しないことをpublic contractにする。inner fileごとのmodified / unknown / historical identityを判定しない。
- root allowlistはcodeに固定し、root / parent binding、symlink、unexpected typeをdestructive step直前に検証する。shared parentやallowlist外pathへ削除authorityを広げない。
- 4 root全体のatomic transaction、自動rollback、per-file checkpoint resume、cross-intent recoveryをpublic contractにしない。partial failure後は外部installerから同じdesired versionを再実行して収束させる。
- small installation record / ready markerは1つだけとし、schema、version、candidate digest、fixed skill slot versionを持つ。per-file stateや任意pathを持たない。
- 通常uninstallはprovider toolingだけを削除し、user-owned spec historyを常に保持する。spec history purgeは通常uninstallから分離する。

### R5A. managed skill contract

- `.agents/skills` 親全体を置換・探索・削除しない。
- managed skillを `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` の2 fixed slotsに限定する。
- 各slot rootへowner / slot / schema versionの小さなmarkerを置き、valid markerがあるexact slotだけをroot単位でupdate / uninstallする。
- marker欠落・不正・別ownerのslotは上書きも削除もせず、書込み前にblockする。unrelated skillsは常に保持する。
- retired skillはcodeに固定された有限のexact-slot allowlistとvalid old markerでだけ削除し、prefix match、arbitrary manifest path、per-file historical digestを削除authorityに使わない。
- marker導入前のcurrent 2 skill rootsは期限付きone-shot migrationでのみ認識し、移行終了後は旧identityとtestsを削除する。

### R5B. Product decision status

accepted ADR `20260831t005139z-adr` により、次を確定した。

1. user historyは常にuser-ownedであり、tooling lifecycleからpurge authorityを除外する。
2. repo-local runtime layoutは4 disposable rootsを維持し、immutable version payload / activation pointerではなくroot replacementを使う。
3. automatic rollback / arbitrary checkpoint resumeを廃止し、external rerun convergenceをfailure contractにする。
4. `.agents/skills` はfixed slot marker方式で管理する。

次のdecision-only child Issuesを、影響する実装Issueの作成・開始前にacceptedにする。未回答を実装者が推測しない。

1. `iss-00388`: legacy direct-update window、markerless migration sunset、`.gitignore` collision / customization、`init --force`。
2. `iss-00389`: `--remove-specs` removal / deprecation / independent purge、confirmation、JSON / text / exit、sunset。
3. `iss-00390`: `.github/workflows/ci.yml` ownership、wheel / sdist / macOS trigger、artifact build count / digest / reuse。

全test inventory作成後、active approved failureのうちcurrent authorityからexpected behaviorを決定できないnodeは、個別のdecision gateへ戻す。

### R5C. lifecycle format and cross-version compatibility

- canonical lifecycle stateは`absent`、`legacy-ready`、`tooling-absent-preserved-data`、`ready-v2(installed_version=A, candidate_digest=D)`、`updating-v2(desired_version=B, desired_digest=D)`、`uninstalling-v2(delete_plan_digest=P)`、`legacy-recovery-active`、`blocked`とする。serialized enum / fixture keyは`ready-v2` / `updating-v2` / `uninstalling-v2`に統一する。`fresh`、`current-supported`、`legacy-supported`、`legacy-expired`、`unknown`はsupport classificationという別axisとし、各classificationからcanonical lifecycle stateへの一意なmappingを持つ。
- package世代は現行`P0`、uninstall-first bridge`P1`、new install/update writer`P2`、legacy sunset後`P3`として扱う。`cutover_path × package_generation × lifecycle_state × public_operation × execution_mode`の全cellにallow / fail-closed / N/A、mutation authority、evidence、diagnostic、recovery owner、implementation owner、sunset / removal ownerを持つ。`cutover_path`はsplit / combinedで、combinedではP1をunpublished / N/Aにする。`public_operation`はinstall、`init --force`、update、uninstall、purge、retry、現存legacy aliasを含み、`execution_mode`はinspect / dry-run / applyを操作から分離する。
- `P1`はlegacy install/update writerを維持しつつ、legacy stateとfuture `InstallationRecordV2`を読むtooling-only uninstall / purge dual-readerを提供する。同一operationにold/new writerを併存させない。
- C5でexact record path、serialized schema / version、`InstallationRecordV2`と`SkillSlotMarkerV1`のcanonical fixture、invalid / unknown / future cases、root / slot completenessを`LifecycleCompatibilityContractV1`として固定する。C5 readerがfixtureをconsumeし、C6 writerはその既存contractへのconformanceを証明する。
- D1はP0が満たすpolicyと、成立しない場合にformat / release sequenceを再審議するauthorityだけを決める。C5内部でcontract / fixtureを先にfreezeし、そのexact fixtureへimmutable P0 artifact / version / digestのmutation-zero probeを実行する。probe failure時はproduction mutationへ進まず親へ戻し、probe success後だけbridgeを実装する。
- `updating-v2`では同じdesired version / digestのexternal updateだけを許可し、uninstall、purge、別version update、old engine fallbackをblockする。
- tooling-only uninstall後のuser data / generated projectionを保持したworkspaceから、accepted install routeで再installできる。
- active legacy recovery stateは、accepted bounded recovery-only adapterまたはlast-compatible package pinのどちらかで扱う。未決状態を新journalへ推測変換しない。
- bridge sunsetをEpic内で行うかfollow-upへ渡すかを`iss-00388`で確定し、期限なしのdual-readerをsteady stateへ残さない。
- C6は最初のdestructive stepより前に唯一のauthoritative fixed recordを`state=updating-v2`、`desired_version`、`desired_digest`へatomic replaceする。以後の全faultで`ready-v2` authorityはなく、物理的に残るlegacy markerはnon-authoritative metadataであり、全readerは`InstallationRecordV2`を優先する。全root / current slot配置とretired slot処理後だけ`ready-v2`へatomic replaceする。
- C5 tooling uninstallは最初のdelete前に同じfixed recordを`state=uninstalling-v2`、exact `delete_plan_digest`へatomic replaceし、recordを最後に削除する。途中停止後は同じdelete planのuninstall rerunだけを許可し、install、update、purge、別plan uninstallをblockする。4 roots、current 2 slots、recordの各delete境界をfault acceptanceに含める。
- D2がindependent purgeを残す場合、tooling installation recordとは別のfixed `PurgeOperationRecordV1`、target evidence digest、monotonic partial-failure state、same-plan rerun authority、最後にrecordを消す順序をC5で実装する。purgeをretireする場合はこのcontractをN/Aとする。

### R6. failureを成功扱いしない

- canonical required testはzero unexpected failuresかつzero approved active failuresでGREENになる。
- 26件のactive failure signatureを成功として受理するledgerは、各nodeを「修正」「現行契約外として削除」「有効なsuccessorへ置換」のいずれかで処理した後に撤去する。
- active failureはexact nodeごとにfix / contract retirement / successor replacementを決定し、family単位のblanket approval、`approved-no-op`、無期限quarantineをsteady stateへ残さない。
- distribution以外のcurrent contractをEpic #384の都合だけでretireしない。
- quarantineが一時的に必要な場合はowner、reason、expiry、successorを必須とし、merge-required GREENの定義には含めない。
- cutover後のrolling 20 canonical runsでflake retryなし・unexpected failureなしを確認する。

### R7. 実行量の可視化

- CI summaryはlaneごとのwall time、CPU time、node count、artifact build count、workspace copy bytes、duplicate node countをcandidate SHAに束縛して表示する。
- `artifact_build_count` はcandidate artifactを生成するbuild command invocation数とし、targetを1とする。一つのinvocationがaccepted policyに応じてwheel / sdistを生成してよいが、各output digestを個別に固定する。
- budget超過はtest failureとして扱い、timing weight更新やworker追加だけで回避できない。
- CPUはpytest root processと全descendantのuser / system CPU secondsの総和を`process_tree_cpu_seconds`とし、`process_tree_cpu_seconds / wall_seconds`を平均論理core使用数とする。

### R7A. additive required-check migration

- 新canonical gateは既存required checkを変更・削除せず、non-required shadowとして追加する。
- shadowの連続GREENとfailure-detection canaryを確認後、GitHub ruleset / branch protectionのauthority、owner、変更前required contextsをreceipt化する。C7のfailure-detection canaryはnew check自身が意図どおりREDになることだけを証明し、merge blockを要求しない。
- unrelated effective required contextsを`U`とし、external required-checkは`U + old`から`U + old + new`、`U + new`の順に移す。対象branch / ruleset scope、複数rulesetのeffective state、human review requirementを集合差分で維持する。
- C8のrequired-set enforcement canaryはnewをrequiredへ追加した`U + old + new`でoldと`U`を全てGREENにし、newだけを意図的にREDにしてmerge blockを証明する。merge queueがactiveならmerge-group eventでも同じcanaryを行う。
- old workflow / ledger / shard machineryは、new checkだけがrequiredであることを再取得してから別PRで削除する。
- required-check defect時はold workflowがrepositoryに残る間だけold contextへrollbackできる。workflow不存在のcontextをrequiredへ戻さない。

## スコープ

対象:

- provider test portfolio全体のinventory、重複・cost・contract ownershipの確定
- `managed_distribution.py` が公開しているper-file reconciliation / journal / recovery契約を4 root replacementへ縮小
- fixed skill slot marker、tooling-only uninstall、有限one-shot migration
- unit、service contract、CLI smoke、package / platform smokeへの再配置
- Full Regression ledger、timing weights、4-shard runnerの段階的撤去
- Provider CI / Provider Full Regressionの実行graph、artifact reuse、budget gate
- obsolete test、duplicate test、historical-step testの安全な削除

対象外:

- Issue #372 candidateへの横入り修正
- test時間短縮だけを目的としたworker数の増加、CI machineの大型化、恒久的なtiming-weight tuning
- Product判断なしでfail-closed path protectionを弱めること
- user-owned spec historyの自動削除範囲を黙って拡大すること
- このEpicの調査段階で全実装Issueを開始すること

## 失敗・境界条件

- production contractを残したままtestだけを削ると、path substitution、partial update、drift、destructive deleteの退行を見逃す。契約縮小とtest削除は同じIssueまたは明示的な依存で結ぶ。
- 逆に、すべてのcurrent testを安全要件とみなすと、歴史的実装詳細が永久にproduct contractとなる。public behavior / invariantへ追跡できないtestは保持理由を満たさない。
- filesystem挙動にはLinux / macOS差がある。pure/domainを両OSで繰り返すのではなく、差が生じるsyscall境界を選んでplatform smokeを残す。
- cold dependency install、GitHub runnerのnoisy-neighbor、network downloadをtest bodyと混同しない。artifact buildとtest実行を別計測する。
- wall timeだけを満たしてprocess-hoursが増える変更は失敗とする。
- R5Bの未決事項はProduct判断であり、影響する下位Issueが推測で決めない。

## 受け入れ条件

- [x] 4 disposable roots、fixed skill slots、user history保護、external rerun convergenceをaccepted ADR `20260831t005139z-adr` に記録している。
- [ ] R5Bの残るProduct判断を、影響する実装Issueの開始前にaccepted decisionとして記録している。
- [ ] production-changing child PRごとに、依存済み`main`上のaccepted public lifecycle command matrixがzero failure、zero policy skipであり、後続Issueなしでもreleasableである。
- [ ] 各production-changing child PRのexact successor node IDsがmerge時点のauthoritative required command / contextでcollection・executionされ、collected count = executed count、policy skip 0である。
- [ ] baseline SHAへ束縛したinventoryが全collected nodeを100%包含する。
- [ ] 削除した全test node、production route、workflow machineryにremoval receiptがある。
- [ ] 全test familyのcontract / layer / lane / cost / keep-move-consolidate-delete判定が追跡できる。
- [ ] canonical local regressionを単一pytest processで連続5回実行し、各回600秒以内、zero failures、zero policy skipsである。
- [ ] 上記5回のchild-inclusive平均論理core使用数が各1.1以下であり、同時pytest worker数が1である。
- [ ] canonical PR test bodyのcritical pathが同一runner classの連続5 successful runsで各600秒以内である。
- [ ] 同一candidate・OSにおけるduplicate test node数が0で、candidate artifact build invocation数が1、accepted wheel / sdist outputの各digestが一意である。
- [ ] platform不適用nodeはcollection後のpolicy skipではなくlane ownershipによって対象外となる。
- [ ] install/update cutover前に旧per-file update testsを削除せず、tooling-only uninstall cutover前に旧deprovision / purge testsを削除していない。
- [ ] uninstall-first bridge merge時にlegacy install / update、tooling-only uninstall、accepted purge surface、post-uninstall reinstallが統合GREENである。
- [ ] install/update cutover merge時にnew writerとnew uninstallが統合GREENであり、old package / writerはnew workspaceをmutation前にfail closedにする。
- [ ] `updating-v2` recordを最初のdestructive step前に永続化し、record前後、各root delete / rename間、ready遷移前、stale staging mismatch、ready write failureのfaultをsame-digest rerun contractで検出する。
- [ ] default pathでshard runnerを使用せず、test worker concurrencyが1である。
- [ ] fixed 2-vCPU Linux referenceで同じbudgetを満たし、seeded fault pack（user data誤書込み、allowlist外削除、symlink follow、root間failure、skill marker mismatch、artifact欠落）を100%検出する。
- [ ] cutover後のrolling 20 canonical runsでflake 0、retry 0である。
- [ ] platform固有smokeがLinuxとmacOSでGREENになり、各OSのtest bodyが600秒以内である。
- [ ] active approved failureが0になり、`full-regression-ledger.json`、timing weights、baseline evaluator、4-shard verifierを削除またはmerge判定外の一時migration toolingへ退役させている。
- [ ] obsolete / duplicate testsの削除前後で、残すdurable invariantsのtraceabilityとnegative-path proofが維持されている。
- [ ] budget summaryがcandidate SHA、wall / CPU time、node / subprocess / workspace / duplicate countsを報告する。
- [ ] required-check transition receiptが`old required`、`old + new required`、`new required only`、old workflow removalの順序とhuman review gate維持を証明する。
- [ ] human PR merge gateを維持し、Issue #372のcandidate / canonical docs / acceptance evidenceを変更していない。

## 制約・前提

- 現時点の計測はlatest concurrent branch `iss-00372-distribution-hard-cutover-and-parity` の `7af12c54...`、実装candidate `bc156009...`、GitHub candidate `53f309a4...` を区別して記録する。
- user-reported「約4時間」「CPUほぼ100%」は重要な問題入力だが、同一SHA・同一machineで今回再測定した数値ではない。
- 10分budgetはtest bodyの目標であり、初回dependency downloadなど外部network時間は別表示する。ただしartifactをlaneごとに再buildする時間は重複costとして対象に含める。
- destructive operationは既定でfail closedとし、path ownershipを証明できない対象を削除しない。
- 既存のhuman PR merge gateを維持する。
- accepted ADR `20260831t005139z-adr` の範囲は確定済みとし、R5Bの未決事項だけを実装上の既成事実にしない。
