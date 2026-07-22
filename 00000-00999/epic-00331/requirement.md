---
種別: 要件定義書（Epic）
ID: "epic-00331"
タイトル: "ChatGPT Planning and Advisory Review"
関連GitHub: ["chemitaro/spec-dock#331"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
親: ["init-00322"]
candidate_semantic_key: "planning-and-advisory-review"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/requirement.md"
---

# epic-00331 ChatGPT Planning and Advisory Review — 要件定義（何を、なぜ行うか）

## 1. Epic Outcome

MainとHumanが、Goalまたは既存Scope Seedから、review済みのPlanning Bundle、適切なEpic／Issue境界、Human-approved Node materializationを完了できる。Humanは任意対象へのTargeted Reviewも利用できる。

## 2. Actor

- Primary: Codex Main Orchestrator、Human。
- Cognitive service: ChatGPT Planner／Reviewer。
- Deterministic service: SpecDock Runtime。

## 3. Scope

- 必要最小限の`spec-dock-chatgpt` thin adapter、exact GitHub binding、Oracle／Human Relay。
- ChatGPT Issue Planning Workflow implementation walking skeleton。これは各IssueのJIT Planningを可能にする製品機能であり、後続IssueのPlanningを代行する独立Planning作業ではない。
- Initiative／Epic／Issue Planning Candidate、Scope別package、archive-candidate／git-bound Review、Human Gate／canonical adoption。
- Epic Planningのstandalone利用。
- Planning Review、decomposition-quality、repository-conventions。
- Targeted Review。
- planning-specificな旧authoring／manual Planning／local planning reviewer routeのactivation切替と除去。その他のshared／execution／delivery legacy surfaceはEpic 3が所有する。
- provider／installed／dogfood parityとreal-use validation。

## 4. Non-scope

- Issue implementation、Execution Brief、Repair Batch。
- per-Issue PR Delivery、Epic Completion。
- 全legacy execution／delivery surfaceのglobal removal。
- exact file／class／Prompt fieldをEpic Requirementで固定すること。

## 5. Requirements

| ID | Requirement |
|---|---|
| E1-REQ-001 | SpecDockへ、既存Issue NodeまたはSeedを入力としてcomplete Issue Planning BundleをJIT生成・セルフレビューする再利用可能Workflowを実装する。archive modeではfresh Planning Review PASS、exact logical Candidate filename／ZIP SHAへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publicationを完了する。git-bound modeではfresh Planning Review PASS on exact reviewed HEAD／exact target paths、同identityへbindされたHuman authorization、exact reviewed-content canonical／commit parity、required validation／planning publicationを完了する。各modeの全条件後だけ`execution-ready`へ昇格する。 |
| E1-REQ-002 | ChatGPT Issue Planning Workflowの実装に必要なthin adapter、target resolution、Git preflight、Oracle invocation、output retrieval、placement、Review integration、tests、docs、projectionを一つのvertical implementation Issueで提供する。 |
| E1-REQ-003 | SpecDockへ、Initiative PlanningがThin Initiative Bundle、全Epic Bundle、Issue Boundary Maps、dependency、ADRを一つのCandidate ZIPへ生成・Review・Human approval・materializeできる再利用可能Portfolio Planning Workflowを実装する。 |
| E1-REQ-004 | exact Candidate ZIPを全unsafe-entry class、CRC、manifest／checksumまでfail closedで検査してfresh Planning Reviewerへ渡し、exact source HEAD snapshot上でdecomposition-qualityを含むPortfolio Reviewを実施する。exact ZIPを完全検査できない場合は`insufficient-evidence`とし、代替file setからFormal PASSを生成しない。 |
| E1-REQ-005 | P0／P1時にPlannerが、旧versionを上書きせず、単調増加する新version、新filename、新MANIFEST identity、新ZIP SHAを持つcomplete revised ZIPを生成する。P2／P3のみでは候補を変更しない。 |
| E1-REQ-006 | Review PASS後にsafe extractionし、Humanがexact ZIP SHAとPortfolioを承認できる。 |
| E1-REQ-007 | Human承認後、RuntimeでEpic／Issue Nodesとdependenciesを作成し、approved Bundleをcontent-preservingにmaterializeする。 |
| E1-REQ-008 | standalone Epic PlanningがEpic Bundleとvertical Issue Seedsを生成し、Human Issue-slice approvalへ進める。 |
| E1-REQ-009 | Targeted Reviewが対象とPerspectiveを受けadvisory結果だけを返す。 |
| E1-REQ-010 | Planning PromptへSlicing Contract、階層別Depth Contract、Consolidation Self-Reviewを合成する。 |
| E1-REQ-011 | Planning Reviewがspecification、architecture、executability、decomposition-quality、適用時repository-conventionsを評価する。 |
| E1-REQ-012 | `spec-dock-chatgpt-authoring`、manual Planning Skills、local planning reviewer等のplanning-specific legacy surfaceを新Workflowへ置換・除去し、Epic 3のremaining global cutoverとmutation ownershipを重複させない。 |
| E1-REQ-013 | shipped surfaceのprovider／installed／dogfood parityを維持する。 |
| E1-REQ-014 | Planning／Review／Oracle／Human RelayのPrompt、Operator Context、GitHub外file、Workbench、Candidate ZIP、Artifactへsensitive dataを含めず、process launchをdirect argvのdefault contractで実行する。shell例外はHuman-approved Design、固定template、untrusted input拒否／safe encoding、injection regression evidence、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。 |
| E1-REQ-015 | 各代表Planning／Review run終了時にplanned／unplanned Human intervention、Main handoff量、Agent／Skill invocation、Review result、wall-clock、failure modeを記録し、E3-I3のInitiative-level評価へhandoffする。 |
| E1-REQ-016 | Portfolio materializationは3 Epic／7 Issue semantic keyを一時ledgerで管理し、Runtime create outcome、remote Issue、local Node、post-sync、dependency、Bundle placementをidempotentに再開する。remote binding後のblind `--create-github-issue`、valid local Nodeの再生成、manual `.meta.json` authoringを禁止し、partial cleanup／full unwindはHuman-approvedとする。 |
| E1-REQ-017 | `NODE-MATERIALIZATION-MAP.json`の全10 title／slug／parentを旧Portfolio退役前にexact source Runtime pure validatorでside-effectなし検証し、invalid inputでmaterializationを開始しない。 |
| E1-REQ-018 | 新Epic canonical三文書はexact Runtime scaffold、Node binding placeholder render、fixed-order atomic replacement、resume／rollbackを経てself-identifyingなcanonical authorityとなり、Runtime report／meta／rulesを保持する。 |
| E1-REQ-019 | 全Candidate Artifactをsource Runtime filename identityへ正規化し、canonical／package-only disposition、placement／resume／rollback／parityをfile単位で固定する。4 Epic-local ADRはproposal templateとしてReviewし、Human Portfolio Approval時だけclosed renderでaccepted canonical authorityへ遷移させる。 |
| E1-REQ-020 | Initiative reportはpre-commit dispositionだけを保持し、commit／push／remote evidenceをGit／remote ref／Workbench ledgerへ分離する。 |
| E1-REQ-021 | E1-I1〜E1-I3はPlanning／Review Workflowの実装Issueであり、それぞれIssue-localにcurrent Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionを禁止する。materialなPortfolio gapは上位Planningへescalateする。 |
| E1-REQ-022 | Issue Planning、Epic Planning、Initiative Planningへ共通のPlanning Candidate lifecycleを提供し、Scopeごとに最小packageを生成する。Issue CandidateはIssue三文書、Epic CandidateはEpic三文書＋Issue Boundary Map、Initiative Candidateは完全Portfolioを基本形とする。 |
| E1-REQ-023 | Planning Skillが`archive-candidate`と`git-bound` Review modeを選択する。pre-canonical semantic iterationはarchiveをdefaultとし、CI／path-based tooling／multi-Human inline review／non-deterministic materialization等のmaterial理由がある場合だけGit-bound fallbackを選ぶ。 |
| E1-REQ-024 | Planning Candidate RevisionをSemanticとMechanicalへ分ける。SemanticはChatGPT Blue Teamのcomplete Candidate replacement、Mechanicalはclosed path／field／literal／meaning invariant／diff budgetを持つdeterministic local revisionとする。両laneともnew identityとfresh Reviewを必要とする。 |
| E1-REQ-025 | archive Candidate PASSからcanonical adoptionした後、source HEAD不変、closed binding、Candidate外変更0、byte／semantic parity、validate／sync PASSを証明できる場合だけ二度目の完全Semantic Reviewを省略する。証明不能時はnew Candidateまたはfresh Git-bound Reviewへ戻る。 |
| E1-REQ-026 | wrapper／scriptはidentity、attachment、source binding、safe extraction、hash／parity、Oracle invocation、result retrievalを所有し、Review mode／Revision lane／Human Gateのsemantic判断はSkillへ残す。 |
| E1-REQ-027 | Issue Planning Review PASSだけを`execution-ready`とみなさない。archive modeはexact logical filename／ZIP SHAへのHuman approval、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publicationを正のgateとする。git-bound modeはexact reviewed HEAD／exact target pathsへのHuman approval、exact reviewed-content canonical／commit parity、required validation／planning publicationを正のgateとする。wrong identity、source drift、semantic adoption diff、parity failure、validation／publication failureをfail closedで拒否する。 `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E1-I1 producerは10／10 PASS、violations 0を必要とする。 |
| E1-REQ-028 | Candidate Reviewはlogical filenameとobserved transport filenameを分離し、closed`(N)`transport aliasだけをcontent identityと照合して許可する。Human approval Evidenceへlogical／transport filenameとSHAを保存する。 |
| E1-REQ-029 | placeholder verificationは`PLACEHOLDER-ORACLE-MAP.json`のdynamic file／tokenだけを対象とし、static exact-hash documentのliteral examplesを未解決bindingとみなさない。 |

## 6. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| E1-AC-001 | 一つの実Issueで、archive modeはPlanning Candidate生成→fresh Review PASS→exact logical filename／ZIP SHAへのHuman Issue Plan Adoption Gate→deterministic canonical adoption→candidate-to-canonical parity→required validation／planning publication→execution-readyを、git-bound modeはexact reviewed HEAD／exact target pathsへのfresh Review PASS→同identityへのHuman Gate→exact reviewed-content canonical／commit parity→required validation／planning publication→execution-readyをend-to-endで完了できる。Review PASSだけのexecution-ready fixtureは拒否される。 |
| E1-AC-002 | 一つのInitiative GoalからInitiative Bundle、全Epic Bundle、Issue Boundary Mapsを含むCandidate ZIPを生成できる。 |
| E1-AC-003 | Reviewerがexact ZIPのpath ambiguity、encryption、special entry、collision、nested archive、executable／binary、resource limit、CRC、manifest／checksumsを完全検査し、exact source HEAD snapshotでcross-file矛盾と過剰分割をReviewできる。 |
| E1-AC-004 | HumanがPASS済みZIPをWorkbenchで確認し、exact SHAを承認できる。 |
| E1-AC-005 | 承認前Node作成0、承認後のNode／dependency／canonical file parity 100%。 |
| E1-AC-006 | Targeted Reviewがadvisoryでありrepository mutationを行わない。 |
| E1-AC-007 | planning-specific legacy routeを標準Workflowから除外し、新Workflowだけで代表Planningを完走する。Epic 3はそのabsenceをverificationし、同surfaceを再変更しない。 |
| E1-AC-008 | provider／installed／dogfoodで同じPlanning／Review責務が動作する。 |
| E1-AC-009 | secret／token／cookie／credential／private key／`.env`／production dump／private customer dataのfixtureがPrompt／Relay／Workbench／Artifactへ保存されず、Oracle／backend invocationがdirect argvで行われ、shell例外は明示承認、固定template、安全なinput handling、injection regression、rollback mechanism／trigger、tested rollback evidenceを持つ。欠落時はPlanning／Review gateをPASSしない。 |
| E1-AC-010 | representative Planning runsがHuman intervention、handoff byte／文字数、Agent／Skill invocation、Review result、wall-clockをrun単位で記録し、旧Workflow baselineと比較可能である。 |
| E1-AC-011 | failure injectionが`pre_github_fail`、`post_github_remote_only_fail`、`post_github_local_write_fail`、`post_github_body_and_cleanup_fail`、`post_github_local_write_success_cleanup_fail`、post-sync failureを再現し、link-existing／doctor-first／bounded cleanup／no-rerun／sync resume／exact dependency／Bundle parity／Human-approved unwindをduplicate Issue／Nodeなしで完走する。 |
| E1-AC-012 | exact source title／slug validatorが全10 approved Node inputをPASSし、invalid title／slug fixtureが旧Portfolio／GitHub／filesystem mutation 0でC0 hard stopする。 |
| E1-AC-013 | 3 EpicのRuntime scaffold render parity、9 bound canonical documents、Node identity front matter、partial resume、verified scaffold rollbackを証明する。 |
| E1-AC-014 | exact source Artifact parser／duplicate scannerが全canonical Artifact ID／type／slotをPASSし、全file dispositionとpackage-only exclusionを証明する。4 Epic-local ADRはHuman approval後にaccepted canonical front matterと`mirror_eligible: true`を持ち、accepted ADR exact-setで4／4検出される。 |
| E1-AC-015 | pre-commit report marker、one explicit commit、push、remote-ref verificationが矛盾なく完了し、reportの第二mutationが0である。 |
| E1-AC-016 | E1-I1〜E1-I3の主要成果が実装済みcode／Skill／Prompt／adapter／tests／docs／projectionであり、Issue-local mandatory four-item Non-goal matrixによりcurrent Portfolio replanning 0、後続Issue三文書の先行作成0、Human approval bypass 0、Planning-only completion 0である。代表Planning runは実装能力の受入証跡としてのみ扱われる。 |
| E1-AC-017 | Initiative／Epic／Issue Candidateの3 package fixtureがScope別最小構成、source baseline、manifest／checksumsを満たし、Issue CandidateへInitiative materialization contractが混入しない。 |
| E1-AC-018 | archive-candidate／git-bound Review requestが相互排他的なidentityを持ち、Skill selection testがdefault／fallback条件どおりmodeを選び、silent fallbackまたはPASS相互継承を拒否する。 |
| E1-AC-019 | Semantic findingがChatGPT complete revisionへ、Mechanical literal fixtureがclosed deterministic revisionへrouteされ、ambiguous fixtureがMechanical laneを拒否する。全revisionがnew Candidate identity／fresh Reviewを持つ。 |
| E1-AC-020 | archive PASS→canonical adoption parity fixtureとsource-drift／Candidate-external-change negative fixtureが、二度目のReview省略条件とfresh Review条件を正しく分岐する。 |
| E1-AC-021 | Skill／wrapper responsibility testがmode／lane semantic decisionをSkillだけに保持し、wrapperはdirect argv、attachment、hash、parity等の決定的処理だけを実行する。 |
| E1-AC-022 | archive／git-boundの両Issue Planning fixtureで、Review PASSのみ、Human Gateのみ、parityのみ、wrong Candidate SHA／reviewed HEAD／target paths、source drift、semantic adoption change、parity failure、validation／planning-publication failureからの`execution-ready`遷移を拒否する。archiveではpositive Human Gate＋canonical adoption＋candidate-to-canonical parity＋required validation／planning publication、git-boundではpositive Human Gate＋exact reviewed-content canonical／commit parity＋required validation／planning publicationの全条件後だけ許可する。 `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E1-I1 producerは10／10 PASS、violations 0を必要とする。 |
| E1-AC-023 | upload名にclosed`(N)`suffixが付いてもlogical filenameへ機械正規化し、SHA／root／MANIFEST一致時だけReview継続できる。fuzzy rename／different extension／hash mismatchは`insufficient-evidence`となり、Human approval Evidenceは両filenameを保持する。 |
| E1-AC-024 | Placeholder Oracleがdynamic undeclared／remaining tokenを拒否し、static ADR 13のliteral placeholder examplesをexact hash一致時に受理する。 |

## 7. Risks

- ZIP semantic handlingが不安定: live smoke、`insufficient-evidence`、non-formal diagnostic、新しい完全ZIPとfresh Formal Review。
- Initiative Planningが詳細化しすぎる: Depth Contractとdecomposition-quality Review。
- Materializationで本文が変わる: placeholder allowlistとparity check。
- Prompt／Relayからのcredential leakageまたはshell injection: sensitive-data preflight、redaction、direct argv、exception review、injection tests、rollback drill。
- Planning Workflow実装IssueがPlanning活動そのものと誤解される: `Implement ... Workflow` title、明示Non-goals、implementation-centered acceptance evidence、ADR 17。
- Issue Planning walking skeletonがgeneric foundationへ膨張: 最初の実Issue完走をDoDとし、未使用surfaceを作らない。
- Review mode／Revision lane誤分類: closed selection matrix、ambiguity時Semantic lane、mandatory fresh Review。
- ZIP PASSとcanonical Git stateの乖離: closed binding、Candidate-to-canonical parity、Candidate外diff 0、drift時Git-bound re-review。
