# init-00322 GPT 56 ChatGPT First Intelligence Architecture — 計画

## 1. 計画の役割

この計画は、Initiativeを3つの独立Capability Epicへ分け、Initiative Planning時点で各Epic BundleとIssue Boundary Mapまで具体化し、Candidate ZIPによるReview／Human Approval後にEpic／Issue NodeをmaterializeするProgram Planを定義する。

Initiative PlanはEpic内部の詳細を複製せず、Epic Portfolio、dependency、Portfolio Gate、materialization、Initiative completionを所有する。

## 2. 開始条件

- HumanがInitiative Goalと本Candidate Planningの作成を指示している。
- Source branchの現行Initiative三文書と既存Epic構造を確認している。
- ADR 10〜22をcurrent decisionとしてCandidateへ含める。
- Candidate ZIPのOracle／ChatGPT ZIP handlingはFormal Review前にlive smokeする。exact ZIPを安全かつ完全に検査できない場合は`insufficient-evidence`としてFormal Reviewを停止する。Git-tracked packや個別attachmentはnon-formal diagnosticに限り、同じReview identityの代替にはしない。

## 3. Initiative Planning Completion Gate

Initiative Planningは次が揃うまで完了しない。

1. Thin Initiative Requirement／Design／Plan。
2. 3 EpicのRequirement／Design／Plan。
3. 3 EpicのIssue Boundary MapとIssue Seeds。
4. Epic／Issue dependency graph。
5. ADR set。
6. Portfolio Consolidation rationale。
7. immutable Candidate ZIPとchecksums。
8. fresh Planning Review（`decomposition-quality`必須）。
9. P0／P1解消済みfinal Candidate ZIP。
10. Humanによるexact ZIP SHAのPortfolio Approval。
11. 承認後の旧7 Epic deterministic retirementと3 Epic／7 Issue Node materializationとdependency登録。
12. candidate-to-canonical parity、validate／sync、commit／push。

## 4. Epic Portfolio

| # | Epic | Outcome | Issue Seeds | 依存 |
|---:|---|---|---:|---|
| 1 | **ChatGPT Planning and Advisory Review** | Main／HumanがIssue Planning、Initiative／Epic Portfolio Planning、Planning Review、Targeted Review、Human-approved materializationを完了できる。 | 3 | なし |
| 2 | **Analysis Guided Issue Execution and Per Issue Delivery** | Mainが承認済みIssue PlanからExecution Brief、single custom Executor、Checkpoint、Repair、個別PR、Human merge、Issue finishまでを一つのvertical Issueで完了できる。 | 1 | Epic 1 |
| 3 | **Multi Issue Epic Completion and Global Cutover** | Main／Maintainerが複数Issue Epicをfinishし、Human mergeでofficial cutoverをactivateし、別Issueでpost-cutover evaluation／release decision／closureを完了できる。 | 3 | Epic 2 |

3 Epicは、独立Actor Outcome、Acceptance Boundary、Risk／Rollback Boundaryを持つため分離する。Foundation、Review、QA、Metrics、Dogfoodを独立Epicにしない。

## 5. Epic Dependency Graph

```text
Epic 1 Planning and Review
        |
        v
Epic 2 Analysis Guided Issue Execution and Per Issue Delivery
        |
        v
Epic 3 Epic Completion and Global Cutover
```

Epic 2はEpic 1のPlanning／Review capabilityを利用する。Epic 3はEpic 2の個別PR／Issue finish capabilityを前提とする。

## 6. Issue Portfolio Summary

Epic 1の3 IssueはPlanning活動を別Issue化したものではない。すべてSpecDockへ再利用可能なPlanning／Review Workflow capabilityを実装するIssueであり、各Issue自身のJIT Planningは通常どおりIssue開始時に行う。


### Epic 1

```text
E1-I1 ──> E1-I2 ──> E1-I3
   └────────────────> E1-I3
```

E1-I2はE1-I1へ依存する。E1-I3はE1-I1およびE1-I2へ依存する。

### Epic 2

```text
E2-I1 Analysis Guided Issue Execution and Per Issue Delivery
```

### Epic 3

```text
E3-I1 Multi Issue Epic Coordination and Finish
   |
   v
E3-I2 Official Global Cutover and Rollback Activation
   |
   v
E3-I3 Post Cutover Evaluation Release Decision and Initiative Closure
```

Issue詳細三文書はNode開始直前にJIT生成する。Issue BoundaryはPortfolio Approval時点でHuman承認済みとする。

## 7. Universal Planning Candidate Workflow

```text
Planning output
→ immutable Scope Candidate
→ Skill selects archive-candidate or git-bound Review
→ fresh Red-Team Review bound to exact mode identity
→ P0/P1: Skill selects Semantic or Mechanical Revision lane
→ complete new Candidate identity or bounded Git correction
→ fresh Review
→ PASS
→ Scope-specific Human Gate
→ deterministic canonical adoption／parity
→ explicit commit／push
```

archive Candidateはversion Nを上書き・再利用しない。Reviewerはどのmodeでも修正しない。Semantic RevisionはChatGPTがcomplete Candidate N+1を作り、Mechanical Revisionはclosed deterministic diffだけをMain／Codex／scriptが作る。Candidate bytes変更は常にnew identityとfresh Reviewを必要とする。Git-bound Reviewはrepository／branch／reviewed HEAD／target paths／BASEまたはmerge-baseへbindする。




### Issue Planning execution-ready gate

Issue Planningのterminal sequenceは`PLANNING-ADOPTION-GATE.md`をauthorityとする。

```text
archive-candidate:
fresh Review PASS on exact logical Candidate filename／ZIP SHA
→ Human Issue Plan Adoption and Implementation-Start Authorization bound to exact logical Candidate filename／ZIP SHA
→ deterministic canonical adoption
→ candidate-to-canonical parity
→ required validation／planning publication
→ execution-ready

git-bound:
fresh Review PASS on exact reviewed HEAD／exact target paths
→ Human Issue Plan Adoption and Implementation-Start Authorization bound to exact reviewed HEAD／exact target paths
→ exact reviewed-content canonical／commit parity
→ required validation／planning publication
→ execution-ready
```

Review PASSのみ、Human Gateのみ、parityのみ、wrong Candidate SHA／reviewed HEAD／target paths、source drift、semantic adoption mutation、validation／planning-publication failureでは`execution-ready`を設定しない。E1-I1は両modeのpositive／negative fixtureを実装し、E2-I1はEvidence欠落時にExecutor開始を拒否する。

### Candidate identity and placeholder verification

- logical filenameはMANIFEST authority、observed transport filenameはrecorded metadata。closed`(N)`aliasだけを許可する。
- Human approval source recordとcanonical Evidenceはlogical／transport filenameとZIP SHAを保存する。
- placeholder final parityは`PLACEHOLDER-ORACLE-MAP.json`のdynamic filesだけを検査し、static exact-hash Artifactのliteral examplesをscanしない。

### Closed Planning Adoption negative-fixture acceptance

The execution plan requires the following ten independent rejection fixtures in every named producer／consumer handoff and acceptance surface.

| ID | Required rejected condition | Expected result |
|---|---|---|
| `PA-NF-01` | archive Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-02` | git-bound Review PASSだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-03` | Human Gateだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-04` | parityだけで`execution-ready`／Executor startを要求する | reject |
| `PA-NF-05` | wrong logical Candidate filenameまたはwrong Candidate SHAでadoption／startを要求する | reject |
| `PA-NF-06` | wrong reviewed HEADまたはwrong exact target pathsでadoption／startを要求する | reject |
| `PA-NF-07` | source drift後にreview identityを再確立せずadoption／startを要求する | reject |
| `PA-NF-08` | adoption中にsemantic mutationが発生した内容からstartを要求する | reject |
| `PA-NF-09` | parity failure後に`execution-ready`／Executor startを要求する | reject |
| `PA-NF-10` | validationまたはplanning-publication failure後に`execution-ready`／Executor startを要求する | reject |

Both E1-I1 producer and E2-I1 consumer acceptance must prove every row independently; central-reference-only or generic `negative fixtures` wording is non-conforming.

## 8. Materialization Plan

Human Approval後にだけ実行する。

1. exact Candidate SHA、fresh Review PASS、Human approval、repository／branch／HEAD、clean treeを確認する。
2. C0でsource blobs、existing canonical ownership、future destinations、all payload hashes、all 10 Node title／slug／parent、source Runtime template／Artifact parser blobs、Artifact filename／ID／type、backup／stagingを検証する。FAILならmutation 0。
3. active pointerをpreflightし、Candidate legacy evidenceをArtifact mapに従い必要なら先行配置する。
4. observed 17 edgesをchecked removeし、old 7 Epicをreverse-topological `delete --recursive --yes`でretireする。partial failureはlegacy contractへ従う。
5. exact 3 Epic／7 Issueを`NODE-MATERIALIZATION-MAP.json`のdirect argvでcreate／bindする。remote-onlyは`--github-issue`、valid local Nodeはno-rerun、post-sync failureはsync resume。
6. all three Epic Runtime scaffoldsをexact source template renderへ照合する。`runtime-scaffold-exact`でなければdependency登録へ進まない。
7. exact 9 direct dependenciesをmissing-edge-onlyで登録する。
8. existing Initiative requirement→design→planをsource-baseline-exactからatomic replaceする。
9. new Epic requirement→design→planをbound Candidate templateへrenderし、runtime-scaffold-exactからatomic replaceする。Runtime report／meta／rulesを保持する。
10. `ARTIFACT-MATERIALIZATION-MAP.json`の全canonical Artifactを配置する。Epic-local ADRは`EPIC-ADR-ADOPTION.md`に従いHuman approval fieldsとbound Epic identityだけをrenderしてaccepted canonical bytesへ遷移し、package-only entryを除外する。
11. doctor／validate／sync／repository convention、3／7／9、old absence、binding、all canonical docs／ADRs／Artifacts、Placeholder Oracle dynamic token violations 0／remaining token 0 and static exact-hash parityを検証する。
12. final pre-commit parity後にCandidate-SHA report dispositionを一度appendし、marker parityを再検証する。
13. one explicit commitを作成してpushし、remote ref＝local commitを確認する。observed publication evidenceはGit／remote ref／Workbench ledgerへ記録し、reportを再変更しない。

途中失敗はactual stateでresumeする。partial cleanup、canonical／scaffold rollback、new Portfolio unwindはHuman approvalを必要とする。blind create、duplicate Issue、manual `.meta.json`、unconditional overwrite、ad hoc reset、mixed Portfolio commitを禁止する。

## 9. Epic Delivery Policy

- 各EpicのIssueは個別branch／PR／Human mergeをdefaultとする。
- dependent Issueは原則、依存IssueのHuman mergeとdefault branch refresh後に開始する。
- 独立vertical Issueだけをparallel実行する。
- 全Issue merge後、default branch上でEpic Delivery Reviewを行う。
- Epic Reviewでmutationが必要な場合だけJIT bounded Issueを追加する。
- aggregate Epic PRと事前Final QA Issueをdefaultにしない。

## 10. Current Structure Replacement

現在の7 Epic構造は、本PortfolioがFormal ReviewをPASSしHuman承認された後にsupersedeする。

```text
旧 Foundation／Planning／Review
→ Epic 1 Planning and Advisory Review

旧 Issue Execution／Issue-level Delivery
→ Epic 2 Analysis Guided Issue Execution and Per Issue Delivery

旧 Epic Delivery／Cutover／Final Dogfood
→ Epic 3 Epic Completion and Global Cutover
```

旧Planning Bundleは履歴として保持し、現行authorityへ混在させない。

## 11. Initiative Milestones

| Milestone | Outcome | Gate |
|---|---|---|
| P0 Candidate Authoring | Initiative＋全Epic Bundle＋Issue Boundary Maps＋ADRを含むCandidate ZIP | manifest／checksum／internal self-review |
| P1 Formal Portfolio Review | exact archive-candidate Review。本Initiative CandidateはZIP SHA＋source HEADへbindする | P0／P1なし |
| P2 Human Portfolio Approval | Humanが展開済みfile、exact ZIP SHA、3 Epic／7 Issue、ADR 10〜22、4 Epic-local ADRのadoptionを承認し、`HUMAN-REVIEW.md`のsigned recordへ3 handoffs／12 cells PASS・violations 0、approver／timestamp、canonical evidence locatorを記録 | exact signed approval record SHA／M-019 PASS／stable evidence locator |
| P3 Portfolio Materialization | C0 source preflight、旧7 Epic retirement、3 Epic／7 Issue Node、dependencies、baseline-bound canonical replacement、Epic Bundle／ADR placement、report disposition | backup／resume／rollback／parity／validate／sync／commit／push |
| E1 Planning Capability | Epic 1の全Issue個別merge | Epic 1 Delivery Review／finish |
| E2 Issue Delivery Capability | Epic 2の全Issue個別merge | Epic 2 Delivery Review／finish |
| E3 Cutover Activation | E3-I2 reviewed PRのHuman merge | official route activation／rollback readiness／merged HEAD verification |
| E3 Post Cutover Evaluation and Release | E3-I3の4週間／5件floor、final Review、Human merge | release decision package publication／E3-I3 finish |
| E3 Epic Completion | E3-I3 merge後のdefault branch Epic Review | Epic finish |
| I0 Initiative Closure | 全REQ／AC、M-001〜M-019、Initiative Final Completion Summary | Human closure decision |

## 12. Initiative-level Verification

- Planning Reviewはexact HEAD snapshot、Checkpoint／Deliveryは明示semantic BASEからreviewed HEAD、PR-styleはmerge-baseからPR HEADを用い、BASE／ancestry不明時は`insufficient-evidence`となること。
- Initiative／Epic／Issue Planning CandidateがScope別最小packageを持ち、pre-canonical semantic iterationではarchive-candidate、必要時だけgit-bound fallbackを選べること。
- Semantic／Mechanical Revision classifierがclosed eligibilityへ従い、ambiguityをMechanicalへ流さず、両laneのCandidate変更がnew identity／fresh Reviewを持つこと。
- archive PASSからcanonical adoptionしたfixtureがsource HEAD、closed binding、Candidate外diff 0、byte／semantic parity、validate／syncを満たすときだけ二度目のSemantic Reviewを省略し、drift fixtureではnew Candidate／Git Reviewへ戻ること。
- Checkpoint／Issue Delivery／PR／Epic DeliveryがGit-bound Evidenceを使用し、Planning ZIP PASSだけで代替しないこと。
- Skillがmode／laneを判断し、wrapperがsemantic materialityを判断しないこと。
- 各delta-bounded Reviewがmutation frontierとContract Ownerの現在契約全体を評価すること。
- Agent role exact setがwrite=`executor`、read-only=`explorer`,`researcher`,`consultant`,`deep-consultant`で、provider／installed／dogfood parityとallowlist外role拒否を検証すること。
- exact Candidate ZIP安全検査が全unsafe-entry class、CRC、manifest/control contractをfail closedで扱い、代替入力からFormal PASSを生成しないこと。
- 17 edge removal、recursive delete、active pointer、recovery、old-node absenceをobserved graph fixtureで検証すること。
- Runtime create failure injectionでremote-only、partial／complete local write、lock cleanup failure、post-sync failureを再現し、link-existing、no-rerun、bounded cleanup、sync resume、exact 9 dependency、partial Bundle placement resume、Human-approved unwindをduplicate remote／local bindingなしで検証すること。
- Requirement／Design／Plan／Epic Bundle traceability。
- Epic数、Issue数に固定数biasがないこと。
- 全Issueがvertical outcomeと独立PR理由を持つこと。
- E1-I1〜E1-I3のIssue-local handoffがmandatory four-item Non-goal matrixを持ち、current Portfolio replanning、downstream pre-authoring、Human approval bypass、Planning-only completionが0であること。Humanはexact signed approval recordで3 handoffs／12 cells PASS・violations 0を記録し、source-record SHAとcanonical Evidence locatorをM-019として保持する。canonical materialization parity、implementation diff、dogfood classification、E3-I3 immutable reference、Initiative closureで再検証すること。
- Initiative／Epic／Issue Candidate package shape、archive-candidate／git-bound Review mode、Semantic／Mechanical Revision lane、Human Gate、safe adoption smoke。
- Planning Candidate archive Review、Git-bound fallback、Targeted Review、Execution Brief、Repair、Issue Delivery、Epic CompletionのE2E。
- provider／installed／dogfood parity。
- old surface search、existing Scope replay、rollback。
- quality／resource／latency評価。
- Prompt／Operator Context／Human Relay／GitHub外file／Workbench／Artifact／Execution Brief／Repair Batch／report evidenceのsensitive-data fixtureが0 exposureであること。
- process launchがdirect argvをdefaultとし、shell例外がHuman-approved Design、固定template、input validation／encoding、injection regression test、明示的rollback mechanism／trigger、tested rollback evidenceをすべて持つこと。欠落時はPASSしない。
- exact source Runtime pure validatorが全10 Node title／slug／parentをPASSし、invalid fixtureでC0 mutation 0となること。
- all new Epic source template rendersがRuntime scaffoldと一致し、bound Candidate templatesが9 canonical documentsへreplacement-exactとなり、front matter／heading／meta identityが一致すること。
- exact source Artifact parser／duplicate scannerが全Artifactのfilename-derived ID／type、front matter、timestamp slotをPASSし、canonical／package-only dispositionとfinal parityが一致すること。4 Epic-local ADRはHuman approval前のproposal templateからaccepted canonical bytesへclosed renderされ、accepted fieldsと`mirror_eligible: true`を持ちsource Runtime collectorで4／4検出されること。
- pre-commit report disposition後のcommit／push／remote verificationがGit／remote ref／Workbench ledgerだけで証明され、reportへ未来値または第二publication mutationがないこと。

## 13. Cutover、Evaluation、Release Decision

1. E1／E2の各代表run終了時にoperational metrics M-001〜M-016のraw evidenceを発生元の`report.md`、CI／GitHub evidence、Oracle session、accepted Artifactへ記録する。M-017はPortfolio materialization ledger／canonical parity、M-018はcommit／push／remote-ref publication ledger、M-019はexact signed Human approval record／canonical approval Evidence Artifact／Epic 1 implementation evidenceとして別ownerが生成・保持する。
2. E3-I2が旧Workflow 3件以上のbaseline completeness、parity、existing Scope replay、known-good HEAD、rollback mechanism／trigger／drill、security closureをpre-cutoverに確定する。
3. E3-I2 Issue Delivery Review PASS後、Humanがdedicated PRをmergeする。そのmergeだけがofficial global cutoverをactivateする。
4. Mainがmerged HEAD、official route、rollback readinessを確認しE3-I2をfinishする。
5. E3-I3をpost-cutover default branchから開始し、一つのdedicated branch／draft PRでweekly report／Artifactを管理する。
6. cutover後4週間かつ5件以上の代表Workflow実行のうち遅い方まで測定する。multi-module／layer、非標準framework、API／data、CLI／build／documentation、mechanical skipを最低1件ずつ含める。1 runが複数shapeを満たしてもよいが、全shapeのevidenceを明示する。
7. E3-I3が週次集計とfinal decision packageを作成し、Human intervention 4／5、handoff中央値30%以上削減、旧認知route 0、Human Gate violation 0、semantic state DB 0、parity 100%、Brief Evidence finding 0、shell exception rollback evidence欠落0等のM-001〜M-016を判定する。さらにM-017 materialization Evidence、M-018 publication Evidence、M-019 signed Human approval／canonical parity／implementation Evidenceのimmutable locatorとidentityを検証し、`FINAL-METRIC-PACKAGE-CONTRACT.md`どおりM-001〜M-019 complete decision packageへ取り込む。E3-I3はM-017〜M-019の過去事実を再生成しない。
8. release-blocking target、sample floor、duration floor、task-shape coverage、Evidenceのどれかが未達ならE3-I3 final Review／Human mergeへ進めない。継続計測、bounded follow-up Issue、Human-approved evaluation restart／extension、rollback Issue／PR、またはInitiative中止を選ぶ。
9. E3-I3 final Issue Delivery Review PASS後、Human mergeでfinal decision package／release notesを公開し、reviewed HEAD確認後にE3-I3をfinishする。
10. E3-I3 merge後のdefault branch Epic Delivery Review PASSでEpic 3をfinishし、Initiative Final Completion SummaryとHuman decisionでInitiativeをcloseする。

## 14. Completion

Initiativeは、3 EpicがHuman merge後にfinishし、REQ-001〜REQ-044とAC-001〜AC-043のevidence、E3-I2 cutover activation、E3-I3 release decision、rollback、4週間／5件evaluation floor、required task-shape diversity、M-001〜M-019 complete decision package、Initiative Final Completion Summaryが揃った後に完了する。M-019はHuman Portfolio Approval時のfour-item Non-goal matrix、materialization後のcanonical handoff parity、実装後のOutcome／dogfood evidence分類をfinal summaryで再検証する。
