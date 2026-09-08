---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-08"
親: ["init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 要件定義

本Epicの正本は、本書、[Design](design.md)、[Plan](plan.md)、accepted ADR、[Epic Integration Branch Contract](artifacts/epic-integration-branch-contract.md)、[Rolling-Wave Issue Elaboration Contract](artifacts/rolling-wave-issue-elaboration-contract.md)、[Provider Lifecycle Wire Contract](artifacts/provider-lifecycle-wire-contract.md)、[Post-#387 Regression Baseline Register](artifacts/active-failure-disposition-register.md)である。

## 1. Outcome

Epic #384の目的は、利用者データを保護したままproviderの状態数と重複検証を減らし、低いCPU占有で短時間に全required contractを検証できる製品へ簡素化することである。Issue分割は目的ではなく、その変更を安全に受け入れるための手段である。三つの依存順の実装・検証単位を維持する。各Issueは実装と自身の検証を一体で完了し、人間だけがIssue PRをEpic integration branchへmergeする。各merge後のintegration branchはGREENかつ内部整合でなければならない。三Issue完了後にだけ、同branchをmainへ一度だけ人間がmergeする。

実在するdelivery chainは次で固定する。

| Order | SpecDock ID | GitHub | Outcome |
|---:|---|---:|---|
| predecessor | `iss-00387` | #387 | CLOSED、mainへmerge済み。Current surface residue cleanup。 |
| 1 | `iss-00392` | #392 | Fixed Ownership Provider Lifecycle Hard Cutover。既存nodeをscope縮小して再利用。 |
| 2 | `iss-00395` | #395 | Regression Baseline Terminalization and Product Defect Repair。`iss-00392`へ依存。 |
| 3 | `iss-00396` | #396 | Build Once Provider Gate and Regression Policy Cutover。`iss-00395`へ依存。 |

CLOSEDの`iss-00388`〜`iss-00390`はhistorical superseded nodeのまま保持し、再利用・reopen・dependency先への変更を行わない。

## 2. Identity roles and planning baseline

本書のfront matterにあるSHA `240e561e94b50250a4a6309452a7fd0fb511458a`とtree `181f7eb28da0edff3ca1352edf4cb2ae1f21d433`は、前回replacement packを生成した**authoring-source provenance**である。Current integration tipまたはfreeze identityではない。

2026-09-02の親計画候補 `1429c2f899c6d2086d5bd03c0dcea01f5b168435` は、同一reviewer conversation `required-strict-github-connector-verificati-723` のexecution `required-strict-github-connector-verificati-747` による `review_status=pass`、findings `[]` を受けた。外部freeze receiptとGitHub #384/#392/#395/#396 body projection/readbackも記録済みである。このSHAは過去の合格地点であり、後続編集を自動的に認証しない。

`CURRENT_INTEGRATION_TIP` は各gateでlocal HEAD・upstream・remoteを照合して解決する。`PARENT_FREEZE_SHA` は当該候補のreviewを通過したclean pushed tipをtracked tree外のreceiptへ記録する。既存receiptを後続候補のpassへ流用しない。過去のfailやremediation履歴は[再開時記録](artifacts/20260907t223421z-epic-resumption-and-gpt6-review.md)とReportを参照する。現在のreview方式は[Rolling-Wave Contract §5](artifacts/rolling-wave-issue-elaboration-contract.md)に従う。

- `iss-00387` / GitHub #387はCLOSED/completedである。
- PR #394はbase `main`、head `4f018da3790d7aeeb16410a386e6e586fb2e803d`、merge commit `db13d047e0a9fb2df31b1a5fc44da0673d8fb9cd`で、人間によりmainへmerge済みである。
- Current branchはそのmergeを含むpost-#387 integration baselineである。
- `iss-00395`と`iss-00396`は実在し、metadata dependencyはそれぞれ`iss-00392`、`iss-00395`である。
- Packageとchecked-in dogfoodはtransitional `0.2.3`である。
- Root `full-regression-ledger.json`の`failure_paths`は15行で、14 `active`、1 `resolved/superseded`である。
- Root `full-regression-timing-weights.json`は243 node weightsを持つ。
- Ledger top-levelの27件集計、古いhead SHA、conclusionはIssue #368時点のhistorical metadataであり、current row-count authorityではない。
- Current Provider CI、policy skip、ledger evaluator、4-shard Full Regression、main-push workflowはまだtransitional stateとして存在する。
- Issue #392は2026-09-08に正式start済み。Product implementationは未startである。現在は同Issue branchでユーザー承認済みの親v12修正とIssue詳細化を行う。正式start、内容review、公開freeze、実装許可を区別する。

## 3. Requirements

### E384-RQ-001 — Epic integration branch authority

`codex/epic-00384-provider-test-strategy-planning`をEpic integration branchとして使用する。各implementation Issue branchは、そのIssue start時点の同branch tipから分岐し、PR baseを同branchへ固定する。Issue PRをmainへ向けない。Issue実装をPRなしでintegration branchへdirect pushすること、partial cherry-pick、parallel writer、agent mergeを許可しない。ユーザーが承認した親仕様の編集・commit/pushはこの実装統合禁止とは別に扱う。

### E384-RQ-002 — Ordered human merge and GREEN state

Issue PRは`iss-00392`、`iss-00395`、`iss-00396`の順で、人間だけが一件ずつmergeする。各merge後にbranch-tip identityを固定し、required verificationを再実行し、GREENと内部整合を確認するまで次Issueをstartしない。

### E384-RQ-003 — Rolling-wave elaboration

現在の各Issue R/D/Pはdraft contractであり、実装file、symbol、test code、exact command、step-by-step手順を固定しない。親候補の独立review、external `PARENT_FREEZE_SHA` receipt、GitHub #384/#392/#395/#396 body projection readbackを確認した後、各Issue start直前にcurrent Epic branch tipへ再基準化する。IssueはEpic tipから分岐した専用branchで扱う。作業ディレクトリは新worktreeでも、ユーザーが明示した既存worktreeの再利用でもよい。SpecDockの`issue start`によるbranch/active選択と、Product実装開始許可を区別する。親G0・依存確認とユーザーの開始依頼の後に正式startし、選択されたIssue branchで詳細化する。Stable contractを変更せずimplementation-ready R/D/PとLuna Max handoffを生成し、Rolling-Wave Contract §5の独立reviewでacceptされてからだけProduct実装を開始できる。2026-09-08にユーザーからcommit/push後の#392正式startを依頼された。親G0を満たしてから、このworktreeを再利用して専用Issue branchを選択する。Product実装開始許可は引き続き別gateである。

### E384-RQ-004 — Fixed provider ownership and closed wire

Durable provider mutation authorityは、四つのfixed roots、二つのfixed skill slots、`spec-dock/spec-dock.version`に限定する。Fresh-only seed creationとshared-container bootstrapは別にboundedとする。Public lifecycle record/result/action/text/JSON/exitはwire artifactのclosed inventoryだけを使用する。

### E384-RQ-005 — Legacy migration, seed policy and tooling-only uninstall

Exact clean `0.2.3`だけを`0.2.4`へone-shot migrateする。Strict seven-key recordはimmutable `seed_policy`を保持し、resume identityをoperation/candidate/policyへ固定する。Uninstallはtooling-only、default dry-run、durable `tooling-absent-preserved-data`を保持する。`--remove-specs`はmutation-zero exit 2である。

### E384-RQ-006 — Filesystem safety, recovery and protected data

Candidate validation、descriptor binding、no-follow、hard-link/special-type rejection、same-filesystem persistent stage、native no-replace/exchange、terminal cleanup continuationを維持する。Wire v12のgeneration-bound completion receiptにより、cleanup完了応答前のクラッシュ後も、Consumerを変更せず完了と保存済みcontinuationを再提示できる。Receiptは既存private namespace内のbounded bookkeepingであり、新しいprovider-owned Consumer targetではない。Initiatives、Artifacts、repository workbench、consumer seeds、unknown path、unrelated skills、user dataをpreserveする。Lifecycle operationとevidence workspaceのcleanup authorityを混同しない。準備・初期incomplete recordの通常I/O失敗もWIR-PREP-001のclosed resultとexact recoveryへ含める。元Consumer状態と同世代record/container変更後を区別し、未公開operationをcleanup完了と誤認しない。

### E384-RQ-007 — Post-#387 regression baseline authority

[Post-#387 Regression Baseline Register](artifacts/active-failure-disposition-register.md)がcurrent regression debtの唯一のauthorityである。Current authorityはexact 15 rows、14 active、1 resolvedである。古い27-row conditional register、Issue #387 future-admission model、stale top-level countをcurrent authorityとして使用しない。

### E384-RQ-008 — Issue #392 lifecycle outcome

Issue #392はfixed ownership lifecycle、closed wire、exact migration、tooling-only uninstall、safe recovery、public compatibility、complete dogfood migration、old lifecycle writer removalを一つのobservable Product outcomeとして実装する。Regression terminalizationとfinal provider-gate redesignを所有しない。

### E384-RQ-009 — Issue #392 baseline and gate preservation

Issue #392は14 active rowのnode identity、signature、lifecycleを追加・削除・変更しない。Current test-policy machineryを維持し、Issue merge後もknown baseline以外のunexpected failure 0、current PR gateとexact full-regression pathがGREENでなければならない。既にresolvedのrowは、old lifecycle test removalに必要なpre-decided behavior-preserving successor rebindingだけを許可する。

### E384-RQ-010 — Issue #395 terminalization

Issue #395はregisterの14 active rowsが表すaccepted behaviorを、今確定した原因に対応する修復でnormal passへterminalizeする。Register §6.1の12件はtest harness/observer修正、2件はProduct側の責務境界修正を第一の修復対象とする。Productが正しい場合に旧test前提へ退行させない。Parentで別successorが明示されていないactive rowはfixed-in-placeとする。新しいapproved failure、skip、xfail、silent retirement、row追加、scope外cleanupを認めない。

### E384-RQ-011 — Issue #395 current-gate continuity

Issue #395完了時は、15 rowsすべてresolved、active 0、approved failure 0、unexpected failure 0である。Current ledger、timing、sharder、policy hook、current PR workflow、main-push Full Regressionは整合したままGREENであり、Issue #396のtoolingへ依存しない。

### E384-RQ-012 — Issue #396 build-once provider gate

Issue #396はclean zero-approved-failure baselineだけを入力とし、build-once packaging、same-candidate downstream roles、Linux canonical、sdist smoke、macOS delta、actual-byte evidenceを持つfinal provider gateを実装する。Qualificationのquantitative value、population、aggregation、rejectionおよびescape prohibitionは、直下の`E384-QUAL-001`だけをcurrent normative sourceとし、他のcurrent-authority文書は同contractを参照する。

#### E384-QUAL-001 — Final Provider Qualification Acceptance Contract

1. **Authority and owner.** 本項だけがfinal provider qualificationのquantitative valueとaggregation semanticsを定義する。Issue #396はimplementation/evidenceのsole writerであり、#392と#395はread-only consumerである。Three-Issue pivotはownerを旧#392から#396へ移すだけで、accepted qualification guaranteeを削除または緩和しない。
2. **Candidate binding.** 一つのcandidate qualification campaignは、exact source SHA/tree、candidate manifest digest、wheel/sdist content digestで識別されるexactly one candidateへ束縛する。Candidate artifactのbuild invocationはcandidateごとにexactly oneであり、campaignの全canonical runはその同一artifact bytesをconsumeする。
3. **Environment binding.** Campaignはversioned source-controlled environment contract `specdock-linux-qualification-v1`と、そこから得たexactly one accepted environment fingerprintへ束縛する。親が固定する能力境界はLinux x86_64、qualification allocationは2 vCPU以下・8 GiB RAM以下、standard/general-purpose runner classであり、GPU、larger/custom high-performance tier、sample間のCPU burst/quota変更を認めない。最初の測定前にrunner provider/class、CPU model family、quota、memory limit、OS/image digest、Python/dependency/tool versions、filesystem条件をreferenceへ固定する。現在のmain/CIと同じ標準classを基準にし、能力比較不能や上限を実効制限できない環境はadmission failureとする。#396は具体image/collectorを選ぶが能力境界を選び直さない。Fingerprint drift、異なるenvironment version、異なるcandidateのrunを同一campaignへ混在させない。
4. **Canonical process topology.** Canonical regressionはexactly one pytest root process、exactly one worker、no shardingで実行する。Testが起動したnon-pytest descendantsはCPU measurement対象に含める。Additional pytest process、additional worker、xdistまたはshardはcontract適合にならない。
5. **Performance population.** Campaign ID、candidate identity、environment fingerprintを最初のattempt開始前にfreezeし、そのcandidate/campaignへ事前登録して開始したchronological first exactly five independent final-gate attemptsのLinux canonical観測を五runの母集団とする。各attemptはfresh owner-bound workspaceで同一artifact bytesを一度だけ実行する。五回を一つのattempt内で反復しない。開始後の失敗、取消、中断、identity/raw不足は不合格のmemberとして残し、eligible外として除外・補充しない。同一candidateで失敗後にcampaign IDを取り直して先頭五件を選び直すこと、retry/rerun、成功runだけの選択を禁止する。
6. **Per-run wall predicate.** 五runの各runについて、monotonic elapsed wall timeは`<= 600 seconds`でなければならない。Intervalはpytest root processのspawn直前からroot exitおよび全descendant reap完了までとする。
7. **Per-run CPU predicate.** 五runの各runについて、`child-inclusive total CPU seconds / elapsed wall seconds <= 1.1`でなければならない。Numeratorは同一intervalのpytest root processと全descendantのuser CPU + system CPUであり、denominatorは正のelapsed wall secondsである。
8. **Independent conjunction.** 五runすべてがwall predicateとCPU predicateをそれぞれ独立に満たす。Mean、median、p95、percentile、aggregate-total、rounded display valueまたはrun間相殺を代替判定にしない。
9. **Correctness predicates.** 各canonical runのunexpected failures、approved failures、policy skips、duplicate node executionsはそれぞれexactly zeroである。Skip、approved failure、duplicate executionまたはretry後successをclean pass evidenceへ昇格しない。
10. **Seeded-fault campaign.** Admitted fault catalogueはcandidate freeze時点でversioned、source-controlled、candidate-boundであり、実行前にdenominatorを固定する。全catalogue entryを実行し、detectionは`100 percent`でなければならない。Miss、unexecuted entryまたはpost-observation denominator reductionはqualification rejectionである。
11. **Stability population.** Stability acceptanceは、同じgate contract versionとenvironment versionへ事前登録して開始したlatest exactly twenty chronological final-gate execution attemptsをwindowとする。成功・失敗・取消・中断を問わず開始順で保持し、identity/raw不足の開始済みattemptも欠測の不合格memberとして残す。Candidateは各executionで固定されるが、window membershipをsuccess結果でfilterしない。Windowがtwenty未満ならevidence incompleteである。各attemptの結果とwindow全体のqualification結果を別々に記録し、後者を前者の判定入力に戻さない。
12. **Stability predicates.** Rolling twenty windowの全memberは、それぞれper-attempt final-gate resultがsuccessfulかつacceptedでなければならない。Per-attempt resultは、そのattemptの全roleの成否、candidate/environment/raw evidence、単回に適用するwall/CPU/correctness predicatesを含み、pytest bodyの成否だけには縮小しない。五run全体とrolling twenty全体の集計、campaign単位のseeded-fault evidenceは最終qualification側で評価し、過去/後続attemptの入力待ちを単回resultへ戻さない。Windowのflakesはexactly zero、retriesまたはrerunsはexactly zeroである。Failed、intentional REDまたはnon-accepted memberもwindowに残し、除外、置換または後続successで相殺しない。Retry/rerunを行ったexecutionを除外、置換またはclean passへ昇格しない。履歴不足だけでは正常なattemptの結果を書き換えないため、初期nineteen attemptsを経たtwentieth attemptで初めてwindowを評価できる。古いmemberはchronological latest-twenty境界から自然に外れる場合だけwindow外となり、当該attemptの記録自体は変更しない。
13. **Fail-closed rejection.** Fingerprint drift、missed seeded fault、flake、retry、rerun、rolling twenty window内のfailedまたはnon-accepted per-attempt result、incomplete five-run evidence、incomplete rolling-twenty window、identity mismatchまたはmissing raw evidenceはqualification rejectionである。初期window不足を過去attemptのfailureへ再帰的に変換しないが、不足したwindowをB3/Epic qualification passとして受け入れることもない。
14. **Forbidden escapes.** Additional worker、sharding、policy skip、approved failure、retry、rerunまたはhardware escalationは本contractを満たす手段にならない。Environmentを変更した場合はfingerprint driftとして既存campaignを失効させる。
15. **Platform scope.** Wall/CPU performance predicatesはLinux canonical qualification bodyへだけ適用する。LinuxまたはmacOSの別platform-delta bodyに独立した`<= 600 seconds` predicateを追加しない。Platform role acceptanceはIssue #396のderived implementation contractで別途証明する。
16. **Rolling-wave boundary.** Issue-start elaborationはmeasurement collector、workflow、schema field、test、commandおよびartifact layoutを具体化できるが、本項のvalue、population、window、aggregation、scope、rejectionまたはescape prohibitionを変更できない。
17. **Execution, reuse and gates.** 通常のrequired PR contextはper-attempt resultを判定する。B3/Epic acceptanceはcurrent candidateの五run campaign、candidate-bound seeded-fault全件、rolling twentyのすべてを追加で判定する。同じcanonical観測を五run集計と二十件履歴が参照することは証拠再利用であり、duplicate node executionではない。Candidateのartifactは一度だけbuildし、後続attemptは保存された同じbytesをconsumeする。事前登録した新しいattempt IDによる独立観測は許可するが、同じattempt IDの再実行、GitHubのrun attempt増分、既存記録の置換はretry/rerunとして不合格にする。Intentional required-context REDは五run campaign freeze前に行い二十件履歴には残す。REDの後には二十件の新しい成功attemptが必要であり、この一回限りの導入証拠コストを隠さない。Campaign freeze後の先頭五件内のREDはそのcampaignをrejectする。初期履歴も通常attemptの同じ全role graphから構成し、5×20の入れ子実行を作らない。

### E384-RQ-013 — Consumer-first regression-policy removal

Issue #396だけがold regression policyを削除できる。Replacement consumers/providersを先に成立させ、old consumer 0を証明してから、ledger、243-node timing、sharder、policy skip machinery、old policy hook、quality providers、main-push Full Regressionを同一Issue内で削除する。

### E384-RQ-014 — Compatibility, required context and external evidence

Final gate cutoverはold/new contextsのno-gap coexistence、new required contextのintentional RED block、GREEN recovery、old required context removal、final readbackを人間操作で行う。Workflow/API/artifact/evidenceはactual source/treeとactual bytesへ束縛し、tracked reportへfuture identityまたはpost-merge factを書かない。

### E384-RQ-015 — Dogfood and documentation convergence

Provider sourceを先に変更し、candidate-changing Issueは四roots、二slots、record、markersをcomplete candidateとしてdogfoodへ反映する。Partial projectionをmergeしない。Issue #392がlifecycle guidance、Issue #396がfinal test-policy/provider-gate guidanceを所有する。

### E384-RQ-016 — Rollback and recovery

Rollback unitはIssue PR merge全体である。Dependent Issue start前は直前mergeをhuman revertできる。Dependent work開始後はsuffixを逆順revertするか、owned boundary内でforward-fixする。Stable contract writerの一部だけを戻すpartial rollback、automatic rollback、old writer fallbackを禁止する。

### E384-RQ-017 — Evidence, Issue closure and final main merge

各Issue acceptanceは、Issue PRのhuman merge、integration branch GREEN、acceptance evidence readback後に成立する。三Issue完了後だけEpic PRをmainへ一度human mergeし、final branch treeとmerge treeのequality、final main verification、Issue/Epic closure evidenceを取得する。

### E384-RQ-018 — Historical non-authority and no extra Issue

旧single-Issue HTML、historical research/discussions、single-Issue guide、CLOSED #388〜#390は削除せずhistorical evidenceとして保持するが、current implementation authorityではない。調査、意思決定、文書、test、verification-only Issueを追加しない。

### E384-RQ-019 — Lifecycle/runtime coordination

`spec-dock/system/.runtime/create.lock`をprovider rootと一緒に交換して排他を失わせてはならない。#392は、disposable roots外の同一repository-bound coordinationをlifecycleとrepo-local runtimeの入口で共有し、root交換中に通常commandが利用者データを書かない境界を所有する。単なるlock存在確認や別lockの併用では満たさない。Wrapperから外部installerへのhandoffは二重取得でdeadlockさせず、runtimeの観測開始から書込み完了までの世代整合を保つ。中断後はincomplete stateを通常runtimeへ渡さず外部installerの復旧だけを許す。

`E384-DEC-001` は2026-09-08のユーザー回答「推奨案を採用します」で確定した。初回0.2.3→0.2.4移行だけは、旧SpecDock command・書込みhelperを終了し、新規起動を止めたmaintenance windowで直接外部installerを実行する。移行中断時も停止を維持し、外部installerでreadyを確認してから解除する。旧runtimeの共通排他参加や、process一覧だけによる停止保証を主張しない。以後は[Wire §16](artifacts/provider-lifecycle-wire-contract.md)のrepository-root inodeの共有/排他leaseで保護する。自動process kill、旧runtimeの暗黙patch、新しい一般的schedulerは追加しない。

同じwire節が、module import前のadmission、固定bootstrap、update/uninstall双方のrelease→exec handoff、書込みhelper終了までのlease寿命、busy/unsupported時のmutation-zero、incomplete後の外部復旧を定める。既存create lockは通常create同士の内側の直列化として残せるが、cross-generationのauthorityではない。親判断の解決はreview pass・公開freeze・Issue start・実装開始許可を代替しない。

### E384-DEC-002 — 既存branch checkoutの世代境界（採用済み）

2026-09-08のユーザー回答「オッケーです。それではコミットプッシュした上で最初のイシューをスタートしてください」により採用した。管理下のcheckoutはadmission済みprovider closureを変えない場合だけ許可する。固定したtarget refの事前比較で不同一/判定不能ならcheckout前に、事後driftならactive/sync前に停止する。事後にbranchが変わっていればその事実を報告し、自動rollbackしない。現HEADから新branchを作る通常経路は維持する。Wire §16のclosed admissionと[全体再評価ADR §3 B2](artifacts/20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md)がこの判断を具体化する。

## 4. Parent acceptance coverage

| Requirement | Primary owner | Shared consumers |
|---|---|---|
| E384-RQ-001–003 | Parent Epic | #392, #395, #396 |
| E384-RQ-004–006 | #392 | #395 and #396 read-only |
| E384-RQ-007 | Parent register | all three Issues |
| E384-RQ-008–009 | #392 | Parent gate |
| E384-RQ-010–011 | #395 | #392 output, #396 input |
| E384-RQ-012–014 | #396 | Parent human gate |
| E384-QUAL-001 | Parent owns qualification policy; #396 implements and evidences | #392 and #395 read-only |
| E384-RQ-015 | #392 lifecycle / #396 final policy | #395 protection |
| E384-RQ-016–018 | Parent Epic | all three Issues |
| E384-RQ-019 | #392; legacy admission decision is parent-owned | #395, #396 read-only |

## 5. Final acceptance

Epic acceptance requires all three Issue merges on the integration branch, GREEN evidence after each merge, `E384-QUAL-001` conformance, complete final provider gate, old regression-policy machinery absent, stable contracts unchanged, human review complete, and one final human merge to main. Parent freeze and #392 elaboration additionally require the independent review pass defined in the Rolling-Wave Contract and the post-pass GitHub Issue projection readback. Main must never observe Issue-level intermediate states.

2026-09-08に[準備失敗ADR](artifacts/20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md)の親修正をユーザーが承認した。現在の内容reviewは当該修正を含む候補へ束縛し、Product実装前の公開freezeは別gateにする。

Current parent decision: `owner_decisions_required=[]`。`E384-DEC-001` / `E384-DEC-002` はユーザー採用済み。今回の実測・採否は[全体再評価ADR](artifacts/20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md)を参照する。
