---
種別: 実装報告書（Issue）
ID: "iss-00360"
タイトル: "Cut Over Distribution and Retire Legacy Workflow Surfaces"
関連GitHub: ["#360"]
最終更新: "2026-08-13"
親: ["epic-00356", "init-local-00003"]
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

## Outcome

Issue 360のRequirement / Design / Planを、Issue 357〜359の実装handoff、IC-1 / IC-2、現行installer、ChatGPT-Use-Strictのexact-main authoring分析に基づいて具体化した。Requirement / Design / Planはすべてfresh review passでapprovedであり、planning commit / pushとformal `issue start`を完了した。ChatGPT-SpecReview-Strict round 1はexact upstream SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証した上で、Requirement / Designに残ったformal start前のhistorical statusをP1として検出した。現在地の同期修正後、fresh exact-upstream re-reviewを行う。実装、PR、Issue close、IC-3判定は未実施である。

## Verification

* Current branch: `iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`
* Initial planning baseline HEAD: `27b8682cb6e5262c980f3b04c7f01459a87685e9`
* Integrated main baseline: `a6ded0d9a838b40cdcd741fa473cd264b801f245`
* Issue 359 final head: `948d0cf0dedb84ca34e51a4adc0995820aa011f6`
* Initial approved planning commit: `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Current branch upstream: `origin/iss-00360-cut-over-distribution-and-retire-legacy-workflow-surfaces`
* Push verification at planning commit: local `HEAD` = upstream = `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* `origin/main` merge: fast-forward success、Issue 360文書差分を保持
* `active set iss-00360`: success
* Initial `issue start iss-00360`: dependency `iss-00359`未完了でblocked
* Post-merge dependency check: `ready=true`、blockers=0
* Post-merge `issue start iss-00360`: 未コミットIssue 360文書を保護するcheckout safetyで停止。active selection unchanged
* Approved planning docs / IC evidence commit: success、対象7 pathだけ、commit `3147c80bbbd6a8d4f76685ed5228d1d4495f1aef`
* Issue 360 branch first push / same-name upstream setup: success
* Formal `issue start iss-00360`: success。Issue checkoutはcurrent Issue 360 branch、auto-sync success
* Post-start active context: Initiative `init-local-00003`、Epic `epic-00356`、Issue `iss-00360`
* Post-start dependency: `ready=true`、blockers 0、authority `github`、effective status `open`
* Post-start validation: `spec-dock: ok (validate) nodes=221`
* ChatGPT-Use-Strict: GitHub connectorで`chemitaro/spec-dock` `main` = `a6ded0d9a838b40cdcd741fa473cd264b801f245`を検証し、session `required-strict-github-connector-verificati-65`、resolved model `5.5Pro`でR/D/P authoring案を取得。main orchestratorがrepository factsとIC evidenceへ照合して正本候補へ統合
* Requirement fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし）
* Design fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.98）
* Plan fresh spec review: round 1 / round 2 fail、round 3 pass（P0/P1なし、confidence 0.99）
* ChatGPT-SpecReview-Strict pre-submit attempt: session `required-strict-github-connector-verificati-66`はrate-limit dialogで停止。`promptSubmitted=false`、conversation IDなし、leaseなしでreview未成立
* ChatGPT-SpecReview-Strict round 1: session `required-strict-github-connector-verificati-67`、GitHub connectorでcurrent branch exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証、resolved model `GPT-5.5` verified。Lifecycle current-state矛盾1件をP1として`fail`
* IC-1 fresh verification: Storage Core `4 passed`、S09 Authoring Kit `23 passed`、Fresh node / Artifact `3 passed`
* IC-2 fresh verification: Issue 359 static / collision `11 passed`、finalizer `9 passed`、route / zero-write `7 passed`

## Residual Risks / Follow-ups

* Issue 359 final headとmain mergeへR/D/Pを再照合した。実装開始前にはCurrent branch HEADとTarget二skillのexact inventoryをもう一度lockする。
* Formal `issue start`はapproved planning commit / push後に成功し、active Issueは`iss-00360`である。
* Epic-local ArtifactとReportにIC-1 / IC-2 pass evidenceを記録し、Requirement / Design / Plan review、commit / push、formal startを完了した。残るplanning blockerはlifecycle current-state同期修正のcommit / pushと、そのclean exact-upstream HEADでのStrict re-reviewである。
* Historical digestは実際の過去package bytesから再現できるものだけをS10でlockする。再現不能なcandidateは推測登録せずpreserve-and-blockする。

## Notes

### Planning route

初期authoringでは利用者指示によりCodexが直接作成した。その後、利用者がChatGPT-Use-StrictとChatGPT-SpecReview-Strictの利用を明示したため、GitHub exact-mainをauthorityとするStrict routeへ切り替えた。通常の`planning create / apply`、`adoption_published`は使用していない。

ChatGPT-Use-Strictの出力はadvisory evidenceとして扱い、main orchestratorが現行source、test、Issue 357〜359 handoff、IC-1 / IC-2へ照合してcanonical候補へ統合した。最終authorityはrepository内のR/D/Pとfresh reviewer gateであり、Strict outputの自己主張ではない。

### Evidence inputs

* Epic 00356の承認済みRequirement / Design / Plan / Report
* Issue 357の360 handoff keep inventoryとStorage Core実装report
* Issue 358のTarget Authoring Kit、obsolete candidate、21-path preservation fixture、report
* Issue 359の二skill contract、18 managed + 3 legacy skill inventory、branch implementation / PR report
* Issue 360のevidence-only draft Requirement / Design / Plan
* `src/spec_dock/cli.py`の現行init / update / uninstall、exact obsolete path、bootstrap-only、collision-aware additive skill behavior
* provider / dogfood asset treeとinstaller test inventory

### Evidence Adoption Ledger

| ID | adoption_status | Source / role | Claim | Canonical target | Rationale / evidence | Blocking / next action |
|---|---|---|---|---|---|---|
| EAL-360-001 | adopted | ChatGPT-Use-Strict authoring evidence | Current physical authority、historical identity、deep module、operation × provenance、forward recovery、parityをR/D/Pへ具体化できる | Requirement / Design / Plan | GitHub connectorで`chemitaro/spec-dock` main SHA `a6ded0d9…`を確認し、session `required-strict-github-connector-verificati-65`の提案をlocal source / tests / IC evidenceへ照合した | no。canonical authorityはR/D/Pとfresh reviewer |
| EAL-360-002 | adopted | `implementation-planner` read-only draft | Plan round 1の5 P1をstep-local vertical TDD、Closure Index、delegation/review/commit gate、S90/S99/H10へ再構成する | Plan §4〜§9 | Canonical editなしのdraftをmain orchestratorがapproved R/Dとworkflow policyへ照合して統合した | no。Plan round 3 passでadoption closure確認済み |
| EAL-360-003 | adopted | fresh `spec-reviewer` findings | Requirement / Design / PlanのP0/P1をphaseごとに検出し、修正範囲を限定する | R/D/P/report | Requirement round 3、Design round 3、Plan round 3のpassをraw authorityではなくreview evidenceとして採用した | no。Strict final reviewを別途実施 |

Unresolved `blocked` / `stale` / `unreviewed` adoption entryはない。EAL-360-002のpromotion gateはPlan round 3 passでclosedした。Git / lifecycle / Strict gateはadoptionとは別に未完了である。

### Delegated Draft Evidence

| Draft | created_by_role | Scope / source | Allowed output | Diff guard | Adoption | Reviewer |
|---|---|---|---|---|---|---|
| Issue 360 Plan restructuring draft | `implementation-planner` | Issue 360 approved Requirement / Design、draft Plan / report、`phase_plan_issue.md`、`workflow_issue.md`、Plan round 1 findings | Chat response内のread-only section draft。Canonical、implementation、Artifactへのwrite禁止 | Workerはfile / Artifact変更なし。Main orchestrator統合後の`git diff --check` pass、`spec-dock validate` pass | EAL-360-002でadopted。Authority自己主張、promotion、readiness claimは不採用 | fresh Plan round 3 pass |

### Grade Specialist Evidence Gate

| Grade | Specialist | Availability / route | Output | Integration decision | Gate |
|---|---|---|---|---|---|
| strict | `implementation-planner` | available / used | 5件のP1を閉じるstep構造、Closure Index、concrete RED、delegation / reviewer / commit、S90 / S99 / H10 draft | main orchestratorがapproved R/Dと現行workflowへ照合しcanonical Planへ統合 | closed。fresh `spec-reviewer` round 3 pass |

### Spec Interpretation / Decision Ledger

| ID | Status | Type | Options considered | Disposition | Decision / evidence | Canonical promotion / follow-up |
|---|---|---|---|---|---|---|
| D-360-001 | resolved | authority | Current全量manifest / physical provider tree + historical-only manifest | adopted | Current catalogは物理provider treeから導出し、JSONへ全量複製しない。Provider-private manifestはhistorical identityとobsolete policyだけを持つ | Design §2、§4、Plan S10 / S30 |
| D-360-002 | resolved | safety | path / marker自己申告 / trusted manifest + target identity | adopted | Exact path、workspace marker、consumer manifestの自己申告だけではownershipを認めない。Known target identity、またはknown manifest bytes + provider-private target identityの一致だけを証拠にする | Requirement I360-RQ-009、Design §4.2 / §6、Plan S10 / S30 |
| D-360-003 | resolved | product boundary | CI削除 / cognitive CI維持 / deterministic Storage Core CI維持 | adopted | `.github/workflows/ci.yml`はcognitive workflowではなくdeterministic Storage Core CIとしてTargetへ維持し、Current reusable collision policyを適用する | Requirement I360-RQ-002 / 009、Design §4 / §6、Plan S40B |
| D-360-004 | resolved | migration safety | Freshでもobsolete prune / provenance別prune | adopted | Genuine Freshではobsolete pruneをせず、update / uninstallもunknown / modified assetをpreserve-and-blockする | Requirement I360-RQ-007〜009、Design §6 / §7、Plan S45 / S55 / S70 |
| D-360-005 | resolved | recovery | 全体atomic rollback / phase markerによるforward recovery | adopted | Portable atomic rollbackを主張せず、full preflight、apply-time identity再検証、phase marker、same-package forward retry、post-verifyを採用する | Requirement I360-RQ-012 / 013、Design §6.3 / §8、Plan S30 / S60 / S70 |
| D-360-006 | resolved | compatibility | marker統合 / operation別marker維持 | adopted | Init / updateは新`.distribution-retry.json`、uninstallは既存`.uninstall-retry.json`を維持する。両marker / invalid markerはblockし、暗黙移行しない | Design §8.1、Plan S35 / S60 / S65 / S70 |
| D-360-007 | resolved | package authority | fallback / marker単独 / provider asset + recognized version anchors | adopted | `.gitignore`は必須provider assetだけをsourceとし、version markerはcanonical exact allowlist、version固有anchor、downgrade拒否を一体で検証する | Design §4.1 / §7.3、Plan §3.1 / S10 / S35 / S40B |
| D-360-008 | resolved | recovery | adversarial完全防御 / detected raceのfail-closed境界 | adopted | Operation全体のatomicityではなく、通常process / handled filesystem failureを保証する。Same-UID hostile tampering等は検知時fail-closedとforward recoveryの境界にする | Design §6.3 / §8、Plan S30 / S60 |
| D-360-009 | resolved | lifecycle | gate統合 / 独立gate | adopted | IC-1 / IC-2、dependency readiness、formal `issue start`、R/D/P review、Strict reviewを別gateとして扱う | Requirement I360-RQ-001、Plan §2 / S00 |
| D-360-010 | resolved | downstream | Issue 360内でIC-3を自己承認 / Epic ownerへhandoff | deferred | IC-3 pass、未承認final Issue候補、Epic completionはIssue 360自身で自己承認しない。Planningをblockしない理由は、IC-3が実装・検証後にだけ判定できるEpic-owned downstream gateだからである | Plan H10でEpic ownerへread-only handoffし、Issue 360 closure時に再判定する |

### Spec Authoring Gate / Planning gate ledger

| Phase | Canonical artifact | Reviewer | Status | Evidence / next action |
|---|---|---|---|---|
| Requirement | `requirement.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし。IC-1 / IC-2、Design promotion、formal start、implementation handoffは非承認 |
| Design | `design.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし、confidence 0.98。Plan phaseへ昇格 |
| Plan | `plan.md` | fresh `spec-reviewer` | pass | round 3でP0/P1なし、confidence 0.99。Approved、Git/lifecycle/Strict gateへ進む |

### Reviewer Gate Status

| Gate | Reviewer | Freshness | State | Risk acceptance | Promotion decision |
|---|---|---|---|---|---|
| Requirement | `spec-reviewer` | fresh round 3 | passed | none | Requirement approved |
| Design | `spec-reviewer` | fresh round 3 | passed | none | Design approved |
| Plan | `spec-reviewer` | fresh round 3 | passed | none | Plan approved。Git/lifecycle/Strict gateへ進む |
| ChatGPT-SpecReview-Strict | ChatGPT browser-only exact-upstream review | fresh round 1 | failed | none | `e7520e6a…`でlifecycle current-state矛盾をP1検出。Requirement / Design同期修正をcommit / push後、fresh exact-SHA re-review |

### ChatGPT-SpecReview-Strict round 1

Pre-submit session `required-strict-github-connector-verificati-66`はChatGPTのrate-limit dialog再表示で停止した。Recovery診断では`promptSubmitted=false`、conversation IDなし、leaseなしであり、review結果として数えない。共有Pro sessionのterminal完了後、new-submission gateを満たすことを確認してfresh reviewを開始した。

Session `required-strict-github-connector-verificati-67`はGitHub connectorで`chemitaro/spec-dock`、current Issue 360 branch、exact SHA `e7520e6a433c0b6345b4f52f1172c32f56fad9d3`を検証し、requested `gpt-5.5-pro`、resolved label `GPT-5.5`、model verification `yes`で完了した。Requirement / Designにformal start前のcheckout-safety停止とreview未完了が現在形で残る一方、Report / Planはformal startとphase reviewの成功を記録しているため、S00の現在地が一意でないというP1を1件検出し、`review_status=fail`となった。

Findingはrepository factsと一致したため採用し、Requirement I360-RQ-001とDesign §1を最新lifecycle evidenceへ同期した。Product scope、migration contract、acceptance criteria、implementation stepは変更していない。修正commitを同名upstreamへpushし、別のfresh Strict conversationでexact-SHA re-reviewするまでimplementation blockを維持する。

### Design review round 1

Fresh reviewerは次のP1を検出し、Design / Plan / Decision Ledgerへ反映した。

* Preflight後も各mutationでrootからno-follow再bindし、device / inode / `ctime_ns` / type / link count / content identityを再検証する。差異時はpathname cleanupを行わない。
* Consumer-side manifestの自己申告を信頼せず、manifest自身のknown historical identityとprovider-private target path + target identityの両方を必須にした。
* Init / update用`.distribution-retry.json`と既存uninstall用`.uninstall-retry.json`を統合せず、dual / invalid markerをblockする一意なmigration契約へ決定した。
* `.gitignore`を必須provider assetとして単一distribution planへ含め、hard-coded fallbackを削除する方針を固定した。
* Provider / dogfood / testのAdd / Modify / Delete / Read-only treeとshared-symbol dependency deltaを追加した。

P2のrecognized / unrecognized `init --force`とmarker matrix、AC別verification trace、Decision Ledgerも同時に追加した。

### Design review round 2

別のfresh reviewerはround 1の5件が解消済みであることを確認したうえで、次の追加findingを検出した。

* `spec-dock.version`を「valid」とする構文、known-version admission、version固有anchor、実行中version、downgrade、retry例外を明文化した。
* Decision Ledgerの`Status`を解決状態、`Disposition`をadopted / rejected / deferredとして分離し、IC-3 deferredの非blocking理由とrevisit条件を記録した。
* Dependency diagramにTitle / Question / Scope / Excluded / Update triggerとedge labelを追加した。

Round 2のP1 / P2を反映済みとした。

### Design review round 3

別のfresh reviewerが最新Design / Reportをapproved RequirementとDesign phase基準へ再照合した。Round 2のversion admission predicate、Decision Ledger分離、dependency diagram metadata / edge意味はいずれも解消済みで、新規P0 / P1なし、confidence 0.98の`pass`と判定した。このpassによりDesignを`approved`へ昇格し、Plan reviewへ進む。

### Plan review round 1

Fresh reviewerはproduct scope / migration設計を概ね反映済みとしつつ、実装開始可能なcommand queueとして次のP1を検出した。

* S20〜S70のhorizontalなRED / layer batchingを、一つのobservable behaviorごとにRED / GREEN / review / commitを閉じるvertical sliceへ分解する。
* 全ACとfilesystem / marker / package / scope riskを追跡する`Spec-Locked Closure Index`を置く。
* 各implementation stepへdepends / unblocks、source、target、allowed / forbidden、delegated role、verification、stop、report、review / re-review、commit / cleanを固定する。
* S90をdocs impact、S99をqa / issue-wide code / specの三者final gateとし、IC-3 input handoffをその後のH10へ分離する。
* Repository root rebindとcross-root retry marker replayをzero-writeで拒否するnegative closureを追加する。

`implementation-planner`のread-only draftを上記findingへ限定して採用し、Plan §4〜§9をS00 / S10 / S20 / S25 / S30 / S35 / S40A / S40B / S45 / S50 / S55 / S60 / S65 / S70 / S80 / S85 / S90 / S95 / S99 / H10へ再構成した。Fresh round 2はpendingである。

### Plan review round 2

別のfresh reviewerはround 1の5件すべてが解消済みであることを確認した。新規P1として、Requirement / Designが要求するdiagnostic sanitationがrequired Closure Indexとstep-local negative testへ固定されていない点を検出した。

`C360-RISK-DIAGNOSTIC-SANITATION`をrequired closureとして追加し、S25 classifier diagnosticとS60 fault / retry diagnosticへcredential風文字列、source bytes、repository外absolute pathの非包含test、owner、verification command、report destinationを固定した。Fresh round 3を待つ。

### Plan review round 3

別のfresh reviewerがapproved Requirement / Designと最新Plan / Reportを再照合した。Diagnostic sanitationはrequired Closure Index、S25 / S60のstep-local negative test、verification command、report destination、S95 / S99まで追跡可能であり、round 1の5件にも回帰なし、新規P0 / P1なし、confidence 0.99の`pass`と判定した。このpassによりPlanを`approved`へ昇格した。

### Requirement review round 1

Fresh reviewerは次のP1を検出し、Requirementへ反映した。

* Planning selection、IC-1 / IC-2 handoff approval、Runtime dependency readinessを分離した。
* Storage Coreの決定論的な`.github/workflows/ci.yml`をTargetへ維持した。
* Obsolete pruneをexact pathではなくoperation × provenanceで判定し、ownership未証明時は全mutation前に停止する契約へ修正した。
* Root `README.md`、installed migration guide、retained scripts / system / template / Workbench MarkdownをCurrent docs auditへ追加した。

### Requirement review round 2

Fresh reviewerは、retained `.github/workflows/ci.yml`が利用者所有の同名workflowと衝突した場合の挙動をP1として検出した。Current target全般をmissing、byte-identical、proven historical、ownership unknownへ分類し、最後のclassは既存bytesを保持して全mutation前に停止する契約とacceptanceを追加した。

### Requirement review round 3

別のfresh reviewerがRequirementを親Epic、Issue 357〜359 handoff、installer / asset現物と再照合し、P0 / P1なしの`pass`と判定した。このpassはRequirement単体の品質gateであり、IC-1 / IC-2の充足、Design promotion、formal `issue start`、実装着手を承認しない。

### Lifecycle state

初回`issue start`はdependency readinessを満たさず実行開始を拒否した。利用者が指定したfallbackに従い、`active set iss-00360`でIssue 360を選択し、ユーザーがIssue 359 branchからIssue 360 branchを作成した。Issue 359 merge後はdependency `ready=true`となったが、再試行はdirty worktree safetyで停止した。IC-1 / IC-2とR/D/P reviewを閉じ、planning commitを同名upstreamへpushした後、formal `issue start iss-00360`を再実行してIssue checkout / auto-syncを含めsuccessした。Post-startもactive Issue、dependency、validation、local / upstream SHAを実測している。
