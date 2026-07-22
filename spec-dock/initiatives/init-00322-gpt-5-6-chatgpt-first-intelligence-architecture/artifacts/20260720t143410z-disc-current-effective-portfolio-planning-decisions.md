---
種別: disc
ID: "20260720t143410z-disc"
タイトル: "init-00322 Portfolio Planning — Current Effective Decision Snapshot"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "current-effective discussion snapshot"
derived_from:
  - "Initiative Planning dogfooding through 2026-07-21"
  - "ADR 10〜22"
  - "Independent Formal Reviews of Candidate v1 through v10"
  - "Candidate v8 Human Gate clarification"
  - "Candidate v13 Independent Red-Team Formal Review"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
artifact_type: "disc"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t143410z-disc-current-effective-portfolio-planning-decisions.md"
---

# init-00322 Portfolio Planning — Current Effective Decision Snapshot

1. 今回のScopeは複数の独立Capabilityを束ねるためInitiativeを維持する。
2. Initiative文書は薄いStrategy／Capability Portfolioとし、詳細Designの主戦場をEpicへ移す。
3. Initiative Planning Workflowは全Epic BundleとIssue Boundary Mapまで作成し、Issue投影でEpic境界を逆検証する。
4. Issue完全三文書とExecution Unit詳細はJITで作る。
5. EpicはOutcome単位、IssueはMinimum Sufficientなvertical sliceとする。
6. implementation Issueはper-Issue branch／PR／Human mergeをdefaultとする。
7. DogfoodはSpecDock自身を開発するときのRepresentative Real-Use Validationであり、Epicの種類ではない。
8. Candidate一式はimmutable ZIPへまとめ、Planner／fresh Reviewer／Human Approval／materializationで同じSHAを使う。
9. ReviewerとHumanはZIPを直接修正せず、feedbackをPlannerへ戻して新versionを作る。
10. Human承認後だけ、旧Portfolioをdeterministicにretireし、新Epic／Issue Nodeをmaterializeする。
11. Candidate ZIPの許容pathは`files ∪ control_files`で、CHECKSUMS自身だけをself-hash-exemptとする。
12. Issue Seedには具体的なacceptance evidenceを必須とする。
13. Epic 2は実装開始から専用PR／Human merge／Issue finishまでを一つのvertical Issue Seedとする。
14. 主要write-capable sub-agentはcustom Executor一つ。read-only specialistは限定し、Issue Gradeでmodel／reasoningを自動routingしない。
15. Epic 1はplanning-specific legacy surfaceを所有し、Epic 3はremaining shared／execution／delivery surfaceを所有する。
16. Current 7-Epic／component-sliced structureは、Human承認後にreverse-topological、no-force、stop-on-failure contractでretireする。
17. 新Portfolioは3 Capability Epic、合計7 Issue Boundaryを持つ。

18. Candidate revisionはversion NからN+1へ単調増加し、新filename、新MANIFEST identity、新SHAを持つ。旧versionを上書きしない。
19. Initiative closureにはcutover後4週間かつ5件以上、旧Workflow baseline 3件以上、required task-shape coverage、明示targetとfailure routingを必要とする。
20. Prompt、Operator Context、Human Relay、GitHub外file、Workbench、Artifact、Execution Brief、Repair Batch、report evidenceへsensitive dataを含めず、process invocationはdirect argvをdefaultとする。shell例外はHuman approval、固定template、安全なinput handling、injection regression、rollback mechanism／trigger／tested evidenceをすべて必要とする。
21. E3-I2 Human mergeだけをofficial global cutover activationとし、E3-I3をpost-cutover evaluation、release decision、closure evidenceのownerとする。cutover、release、Epic finish、Initiative closureを別gateとして扱う。
22. E3-I3はQA-only Issueではなく、cutover後にしか存在しないEvidence、Human release decision、rollback／continuation boundaryを持つ独立operational Issueである。
23. legacy retirementとnew Portfolio materializationは別authorityへ分離する。
24. new materializationは3 Epic／7 Issue semantic keyのWorkbench ledgerを持ち、Runtime create outcomeごとにremote-only、partial local、valid local、cleanup failure、post-sync failureを区別する。
25. remote Issueまたはvalid local Node binding後のblind create retryを禁止し、link-existing、doctor-first inspection、bounded cleanup、sync resume、exact dependency／Bundle parity、Human-approved unwindでidempotentに継続する。
26. legacy retirement前のC0で、current HEAD／source Git blobs、canonical destination ownership、verified source backup、Candidate replacement staging、future path ownershipをfail closedに検証する。
27. Existing Initiative三文書は`source-baseline-exact → replacement-exact`だけを許可し、`absent`／`unexpected-mismatch`で停止する。new Epic三文書はvalid Node作成後に必ず存在するため、exact Runtime template renderへ一致する`runtime-scaffold-exact → replacement-exact`だけを許可し、`absent`／`unexpected-mismatch`で停止する。
28. Canonical replacementはrequirement→design→planの固定順、path-bounded atomic replace、per-file ledgerで実施し、partial prefixからactual bytesに基づきresumeする。
29. Human-approved canonical rollbackはverified Workbench source backupだけを使う。old Portfolioを自動復元せず、必要に応じてblocked migration stateへrouteする。
30. `report.md`は全parity後にexact Candidate SHA marker付きdispositionを一度だけappendし、final parityはInitiative三文書、全Epic Bundle／ADR、binding substitution、report dispositionを被覆する。


## Candidate v8で追加されたCurrent Effective Decisions

31. 全10 Nodeのtitle／slug／parentはsource Runtimeのpure validatorでC0検証し、旧Portfolio退役前に全件PASSしなければならない。
32. Node titleはASCII英数字tokenとsingle spaceだけを使用し、slugはkebab-caseを明示する。materialization中のtitle修正は禁止する。
33. Runtime-created Epic三文書は`runtime-scaffold-exact → replacement-exact`で置換し、absent前提を使用しない。
34. Epic canonical三文書はNode binding front matter templateを持ち、actual ID／GitHub Issue／path／actor／dateだけを決定的にrenderする。
35. Artifact identityはfilename-derived ID／typeをauthorityとし、front matterを一致させる。全Artifactはcanonical destinationまたはpackage-only dispositionを持つ。
36. Initiative `report.md`はpre-commit dispositionだけを保持する。commit／push／remote verificationはGit／remote refとWorkbench ledgerをauthorityとし、同じmaterialization commit後にreportを再変更しない。
37. ADR 16を、Node input、Epic scaffold、Artifact disposition、publication evidenceの統合authorityとして採用する。

## Candidate v9で追加されたCurrent Effective Decisions

38. PlanningはScope lifecycle activityであり、Initiative／Epic Planningは現在工程、Issue Planningは各Issue開始時のJITで行う。
39. Planning関連のimplementation Issueは他IssueのPlanningを代行せず、再利用可能なSpecDock Workflow capabilityを実装する。
40. E1-I1〜E1-I3は`Implement ... Workflow` title、implementation-centered Outcome、明示Non-goalsを持つ。
41. 現在のapproved Portfolio再設計、downstream Issue三文書の先行作成、Planning-only completionを禁止する。
42. representative Planning runは主成果ではなくAcceptance Evidenceとして扱う。
43. ADR 17をPlanning lifecycleとcapability implementationのauthorityとして採用する。


## Candidate v10で追加されたCurrent Effective Decisions

44. E1-I1〜E1-I3はそれぞれIssue-localに、current Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionを禁止する。
45. M-019はE1-I2／Human Portfolio Approvalがprimary ownerとなり、canonical materialization parityとInitiative Final Completion Summaryで再検証する。Initiative closureはM-001〜M-019のcomplete evidenceを必要とする。
46. Front matterを宣言するArtifactはbyte 0から`---`で開始する。leading LFを許可しない。
47. Epic-local ADRはCandidate内ではproposal／candidateを維持し、exact Human Portfolio Approval後だけ`EPIC-ADR-ADOPTION.md`のclosed renderでaccepted／mirror-eligible canonical authorityへ遷移する。
48. Human approval text、Artifact map、report disposition、source accepted-ADR collectorの4者が4 Epic-local ADRのadoptionについて一致しなければmaterializationをPASSしない。
49. ADR 18をEpic-local ADR adoption lifecycleのauthorityとして採用する。

## Candidate v11で追加されたCurrent Effective Decisions

50. Human Portfolio Approvalはgeneric SHA approvalではなく、E1-I1〜E1-I3の4禁止事項を12／12 PASS、violations 0として記録するexact signed recordである。
51. signed approval recordはCandidate-SHA-bound Workbenchでhashされ、`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`により固定canonical Discussionへrenderされる。`report.md`のM-019 locatorはcanonical pathとsource-record SHAへ解決する。
52. E3-I3はM-001〜M-016をoperationalに評価し、M-017 materialization、M-018 publication、M-019 Human-Gate／canonical parity／implementation Evidenceをimmutable referenceとして検証する。
53. E3-I3 final Issue Delivery Review、Human merge、default-branch Epic Review、Epic finish、Initiative closureはM-001〜M-019 complete packageを必要とし、M-001〜M-016-only packageをterminalにしない。
54. ADR 19をsigned Human Gate Evidenceとcomplete metric closureのauthorityとして採用する。


## Candidate v12で追加されたCurrent Effective Decisions

55. Initiative、Epic、IssueのPlanning成果物を共通のimmutable Planning Candidateとして扱う。
56. ZIPはpre-canonical Planningの標準transport、Git-bound Reviewはactual repository path／CI／merge-base／multi-Human inline review等が必要な場合の正式fallbackとする。
57. Initiative Candidateは完全Portfolio、Epic CandidateはEpic三文書＋Issue Boundary Map、Issue CandidateはIssue三文書を基本とし、Scopeごとにpackageを最小化する。
58. archive-candidate Formal identityはZIP SHA＋source HEAD、git-bound Formal identityはreviewed HEAD＋target paths＋必要なBASE／merge-baseであり、PASSを相互に誤継承しない。
59. Planning Candidate RevisionをSemantic RevisionとMechanical Revisionへ分ける。SemanticはChatGPT Blue Team、Mechanicalは閉じた決定的操作としてMain／Codex／scriptが担当できる。
60. Mechanical Revisionは対象path／field、old／new literal、meaning invariant、diff budgetを編集前に列挙できる場合だけ許可し、曖昧ならSemantic Revisionへ戻す。
61. どちらのRevision laneでもCandidate bytes変更はnew version／filename／root／MANIFEST／SHAとfresh Red-Team Reviewを必要とする。
62. Red Teamはreview-onlyであり、Candidate、canonical file、patch、revised ZIPを生成しない。
63. archive PASSからcanonical adoption後、source HEAD不変、closed binding、Candidate外diff 0、byte／semantic parity、validate／sync PASSを証明できる場合だけ二度目の完全Semantic Reviewを省略できる。
64. Checkpoint、Issue Delivery、PR、Epic Delivery ReviewはGit-boundを維持し、Planning Candidate ZIP PASSで代替しない。
65. Review modeとRevision laneはSkillが判断し、wrapper／scriptはidentity、attachment、safe extraction、hash／parity、Oracle invocation等の決定的処理だけを担う。
66. ADR 20をUniversal Planning Candidate、dual Review transport、dual Revision laneのauthorityとして採用する。


## Candidate v13で追加されたCurrent Effective Decisions

67. Planning Review PASSはHuman decisionの入力であり、単独では`execution-ready`を成立させない。
68. Issue Planningはexact reviewed identityへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization、mode-specific canonical／commit parity、required validation／planning publication後だけ`execution-ready`へ遷移する。archive／git-boundの両modeでpositive gateを必要とする。
69. logical Candidate filenameはMANIFEST authority、transport filenameはobservational metadataとし、closed`(<positive integer>)`suffixだけをaliasとして許可する。
70. Human approval source recordとcanonical Evidenceはlogical filename、observed transport filename、ZIP SHAを保持する。
71. unresolved-placeholder検査は`PLACEHOLDER-ORACLE-MAP.json`のdynamic file／tokenだけに適用し、map外static fileはexact hashで検証する。
72. ADR 21をScope-specific Planning Adoption Gateのauthority、ADR 22をCandidate identity／transport alias／Placeholder Oracleのauthorityとして採用する。

## Candidate v14で追加されたCurrent Effective Decisions

73. archive-candidateとgit-bound Issue PlanningはReview transportだけが異なり、いずれも`fresh Review PASS → exact-identity Human Issue Plan Adoption and Implementation-Start Authorization → canonical／commit parity → validation → execution-ready`の同一authority chainを必要とする。
74. `fresh Git-bound Planning Review PASS`を、Human authorization／parity／validationから独立したpre-start alternativeとして扱わない。Epic 2のIssue Boundary Mapを含む全consumer-facing handoffはRequirement／Design／Planと同じ正のgateを持つ。
75. Planning Review PASSのみ、Human Gateのみ、parityのみ、wrong identity、source drift、validation failureのいずれからもExecutorを開始せず、archive／git-bound両modeのnegative fixtureでこれを証明する。

## Candidate v15で追加されたCurrent Effective Decisions

76. Planning Adoption Gateはpackage-wide invariantであり、central contractだけでなく全normative local Requirement／Design／Plan／Issue handoffへ完全に投影する。
77. archive-candidate modeは`fresh Review PASS → exact logical filename／ZIP SHAへbindされたHuman authorization → deterministic canonical adoption → candidate-to-canonical parity → required validation／planning publication → execution-ready`を必要とする。
78. git-bound modeは`fresh Review PASS on exact reviewed HEAD／exact target paths → 同identityへbindされたHuman authorization → exact reviewed-content canonical／commit parity → required validation／planning publication → execution-ready`を必要とする。
79. Review PASSのみ、Human Gateのみ、parityのみ、wrong Candidate SHA／reviewed HEAD／target paths、source drift、semantic adoption mutation、validation／planning-publication failureではExecutorを開始しない。
80. local handoffが上位contractを短縮してterminal sequenceを定義することを禁止し、全consumer／producer acceptance evidenceへpositive／negative fixtureを要求する。
## Candidate v16で追加されたCurrent Effective Decisions

81. Planning Adoption negative fixtureをclosed set `PA-NF-01`〜`PA-NF-10`として固定する: `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failure。
82. 全named producer／consumer Requirement／Design／Plan／Issue handoff／Human Review／Materialization acceptanceは、10 IDと意味をlocal normative contractとして明示し、central contract参照やgeneric `negative fixtures`だけで省略しない。
83. E1-I1 producerとE2-I1 consumerはそれぞれ10／10 PASS、合計20／20、violations 0をacceptance evidenceとする。
84. 10分類のいずれかが未実装・未検証・failureである場合、`execution-ready`／Executor start、Human approval、materialization completionを許可しない。

