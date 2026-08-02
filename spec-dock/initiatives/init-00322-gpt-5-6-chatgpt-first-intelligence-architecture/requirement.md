# init-00322 GPT 56 ChatGPT First Intelligence Architecture — 要件定義

## 1. 文書の役割とInitiative identity

この文書は、SpecDockのPlanning、Review、Architecture-Aware Execution Brief、Repair、Issue Execution、per-Issue Delivery、Epic Completion、global cutoverを、ChatGPT Delegation-Firstな構造で提供するInitiativeの戦略目的、cross-Epic制約、必須能力、成功条件を定義する。

- Initiative ID: `init-00322`
- filesystem path: `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture`
- GitHub Issue: `#322`
- repository title: `GPT 56 ChatGPT First Intelligence Architecture`
- program label: `ChatGPT 5.6 Pro Delegation-First Workflow vNext`

### 1.1 Authority

- Humanの明示承認とSpecDockのpromotion条件を満たしたcanonical `requirement.md`、`design.md`、`plan.md`がScope authorityである。
- accepted ADRは、Human adoptionと`report.md` dispositionに基づくarchitecture authorityである。
- Interview、Discussion、Research、self-review、raw ChatGPT outputはevidenceであり、単独ではcanonical authorityを持たない。
- Architecture-Aware Execution BriefとRepair Batchは、Source HEAD固定のfrozen subordinate contractであり、canonical三文書を変更できない。
- Candidate ZIPはPlanning Review・Human Approval・materializationの入力であり、Human承認前はnon-canonicalである。

## 2. Goal、Why now、利用価値

### 2.1 Goal

SpecDockの高度認知処理をChatGPTへ、Workflow制御とGit transactionをCodex Mainへ、bounded repository mutationをExecutorへ、構造的・決定的処理をSpecDock Runtimeへ分離し、Human Gateを維持したまま、GoalからPlanning、実装、Review、個別PR、Human merge、Epic Completionまでを一貫して自動化する。

### 2.2 Why now

GPT-5.5前提の現行Workflowは、段階的authoring、ChatGPT evidence、Codex rewrite、複数local reviewer、manual fallback、receipt／ledgerへ同じ意味を複製している。GPT-5.6 Proの横断分析能力を利用できる現状では、これらの重複はHuman介入、Codex quota、context圧迫、変更surfaceを増やす。

Initiative Planningのdogfoodingでは、Initiativeが技術工程別Epicへ過剰分割され、そのEpicが内部component別Issueへ過剰分割される問題も確認された。分割誤りは後続のRequirement、Design、Planを論理的に整えても価値の低い実装とPRを生むため、Slicing Contractとdecomposition-quality ReviewをPlanningの中心契約にする。

### 2.3 利用価値

- HumanはGoal、Portfolio、material変更、PR merge判断へ集中できる。
- ChatGPTは複数文書、Artifact、code、tests、configurationを横断してPlanning、Review、実装前分析、Repair設計を行う。
- Mainはauthority、Workflow、candidate adoption、Git transaction、Human Gateへ集中できる。
- Executorは承認済みPlan、Execution Brief、Repair Batchに基づく実装とverificationへ集中できる。
- Initiative Planningは全Epic BundleとIssue境界まで先読みし、過剰Epic・過剰Issueを実装前に除去できる。
- 各implementation Issueは1 branch／1 PR／Human mergeで独立完了できる。

## 3. Scope、Non-goals、横断原則

### 3.1 Scope

- Human、ChatGPT、Main、Executor、Runtimeのauthority再定義。
- Initiative／Epic／IssueのIntegrated Planning Bundle。
- Initiative Planningによる全Epic Bundle、Issue Boundary Map、dependency、Portfolio Consolidation。
- Universal Planning CandidateによるInitiative／Epic／Issue Planningのpre-canonical Review、Human Gate、canonical adoption。ZIPを標準transport、Git-bound Reviewを正式fallbackとする。
- Planning、Checkpoint、Issue Delivery、Epic DeliveryのFormal ReviewとTargeted Review。
- `decomposition-quality`および`repository-conventions` Perspective。
- Architecture-Aware Execution Brief、Repair Batch、Executor中心のIssue Execution。
- per-Issue PR、Human Merge Gate、merged HEAD確認、Issue finish。
- multi-Issue Epic coordination、default branch上のEpic Delivery Review、Epic finish。
- `spec-dock-chatgpt`の薄いOracle／GitHub連携。
- provider／installed／dogfood parity、legacy removal、global cutover。
- 代表的な実利用条件によるvalidation。SpecDock自身ではdogfoodをその一例として利用する。

### 3.2 Non-goals

- 既存Scope文書の一括変換、closed Scopeの書換え。
- 自動merge、Human Merge Gateの削除。
- Candidate段階でのEpic／Issue Node作成。
- Draft Node、Candidate DB、Planning receipt DB、semantic parserの追加。
- tracked repository contentをChatGPTへ自動添付してGitHubと二重SSOTにすること。
- Issue数、Epic数、Brief長を固定すること。
- Foundation、QA、Metrics、Dogfood、Inventory、Docs等を、それだけで独立Epic／Issueにすること。
- DDD、イベント駆動、特定frameworkをExecution Briefの必須前提にすること。
- Issue詳細三文書、Milestone、テストケース、file-level変更をInitiative Planningで確定すること。

### 3.3 Slicing Contract

- InitiativeとEpicは、まず一つとして成立するか検討する。
- 独立したCapability、Acceptance、Risk、Rollback、Dependency、Human Decision Boundaryがmaterialに必要な場合だけ分割する。
- Epicは「完了後、誰が何を新しく完了できるか」を表す。
- Issueは必要最小限の独立merge可能なvertical sliceとする。
- IssueはOutcomeに必要なcode、tests、docs、configuration、packaging、migration、real-use validationを含む。
- Issue内部の複雑性はMilestone、Execution Unit、Architecture-Aware Execution Briefで管理する。
- implementation Issueは原則1 branch／1 PR／Human merge／merged HEAD確認／finishとする。
- Planning返却前にConsolidation Reviewを行い、境界を維持するmaterialな理由がなければ隣接Epic／Issueを統合する。

## 4. 必須能力

| ID | 能力要件 |
|---|---|
| REQ-001 | 全WorkflowでHuman、ChatGPT、Main、Executor、Runtimeの責務を一貫して分離し、Goal、Portfolio、material変更、mergeのHuman Gateを維持する。 |
| REQ-002 | Initiative／Epic／IssueのRequirement、Design、Planをfresh ChatGPT sessionで相互整合した完全Bundleとして生成し、返却前セルフレビューを行う。 |
| REQ-003 | Initiative PlanningがThin Initiative Bundleだけで終了せず、全Candidate Epicの完全BundleとIssue Boundary Mapまで生成し、Issue投影を用いてEpic Portfolioを再検証する。 |
| REQ-004 | Initiative PlanningはSlicing Contract、Portfolio Consolidation、`decomposition-quality` Review、Human Portfolio Approvalを経て、承認後にのみEpic／Issue Nodeとdependencyをmaterializeする。 |
| REQ-005 | Initiative／Epic／IssueのPlanning成果物をcanonical adoption前のimmutable Planning Candidateとして扱う。`archive-candidate`はexact ZIP SHAとsource repository／branch／HEADへbindする標準transport、`git-bound`はrepository／branch／reviewed HEAD／target paths／必要なBASEまたはmerge-baseへbindする正式fallbackとする。 |
| REQ-006 | Planning Candidate packageはScopeごとに最小化する。Initiative CandidateはInitiative Bundle、全Epic Bundle、Issue Boundary Maps、dependency、ADR、materialization contractを含む。Epic CandidateはEpic三文書、Issue Boundary Map、関連ADR、source baselineを含む。Issue CandidateはIssue三文書とsource baselineを含む。archive modeではMANIFEST／CHECKSUMSとZIP SHAでReview unitを識別する。 |
| REQ-007 | Red Teamはreview-onlyであり、Candidate、canonical file、patch、replacement、revised ZIPを生成しない。Semantic RevisionはChatGPT Blue Teamが完全な新Candidateを生成する。Mechanical Revisionは意味判断不要かつ変更path／field／literal／meaning invariant／diff budgetが事前に閉じる場合だけMain／Codex／deterministic scriptが実行できる。どちらも旧identityを上書きせず新Candidate identityとfresh Reviewを必要とする。 |
| REQ-008 | Formal Review PASS後、Candidate ZIPを安全展開し、Humanが展開済み内容とexact ZIP SHAを確認する。Approvalは`HUMAN-REVIEW.md`のexact signed recordとして、E1-I1〜E1-I3のmandatory four-item matrix 12／12 PASS、violations 0、Human identity／timestamp、stable M-019 evidence locatorを明示しなければならない。Generic SHA acknowledgementだけではApprovalを成立させない。Human feedback時は新ZIPとfresh Reviewへ戻る。 |
| REQ-009 | Human承認後かつ破壊的操作前に、source HEAD／`SOURCE-BASELINE.json`、canonical三文書／`report.md`のGit blob、destination ownership、Workbench source backup、Candidate replacement stagingをfail closedで確認するC0 preflightを完了する。C0 PASS後にのみ、active pointer preflight、17 edge除去、旧7 Epic retirement、3 Epic／7 Issue作成、9 dependency登録、baseline-bound canonical replacement、Epic Bundle／ADR配置、report disposition append、validate／sync／parity、1 commit／pushを順に実行する。 |
| REQ-010 | ChatGPT連携をCore Runtimeから分離した薄いapplication boundaryとし、Formal処理をGitHub exact repository／branch／HEADへfail closedでbindする。 |
| REQ-011 | Git-tracked repository contentはGitHubをSSOTとし、Operator ContextとGitHub外資料だけを明示補足する。Oracle障害時も同じtask／result contractを維持する。 |
| REQ-012 | Formal ReviewをPlanning、Checkpoint、Delivery Protocolとして提供し、Targeted Reviewをadvisoryとして分離する。Planning Reviewはexact HEAD snapshot、Checkpoint／Delivery Reviewは明示されたsemantic BASEからcurrent HEADまで、PR-style Reviewはmerge-baseからPR HEADまでを評価し、各delta-bounded Reviewはmutation frontierとContract Ownerの現在契約全体の双方を検証する。BASE／ancestryを解決できない場合は`insufficient-evidence`とする。 |
| REQ-013 | Planning Reviewはspecification、architecture、executability、decomposition-quality、適用時repository-conventionsを評価し、Portfolio全体とIssue SeedsをReview対象にする。 |
| REQ-014 | Formal ReviewはP0／P1をblocking、P2／P3だけをnon-blockingとし、必要証拠を確認できない場合のPASSを禁止する。 |
| REQ-015 | Architecture-Aware Execution Briefを、非機械的Execution Unitの目的、現状、適用Concern、Evidence、テスト戦略、実装戦略を具体化するSource HEAD固定契約として提供する。 |
| REQ-016 | Formal blockerでmutationが必要な場合、ChatGPTがRepair Batchを生成し、Mainの採用後にfreezeしてExecutorへ渡す。 |
| REQ-017 | maintained official pathのwrite-capable roleをcustom `executor`一つへ統合する。read-only roleのclosed allowlistはbuilt-in `explorer`、custom `researcher`、`consultant`、`deep-consultant`の4 roleだけとし、その他のnamed sub-agent roleを禁止する。provider authorityは`src/spec_dock/assets/install_root/.codex/agents/`、dogfood projectionは`.codex/agents/`、installed projectionは`<install-root>/.codex/agents/`とし、built-in `explorer`にはoverride fileを置かない。Issue Gradeをmodel／reasoningの自動routingへ使用しない。Executorはbounded implementation／verification、Mainはdiff確認／commit／push／Review、Humanはmergeを所有する。 |
| REQ-018 | Issue ExecutionをExecution Unit、Execution Brief、Checkpoint、Repair Batch、Final Completion Summary、Issue Delivery Reviewで制御する。 |
| REQ-019 | implementation Issueは原則1 dedicated branch／1 PRとし、required CI／Review、Human merge、reviewed HEAD確認後にIssue finishする。 |
| REQ-020 | 複数Issue Epicはdependencyとmerge状態を管理し、全Issueがdefault branchへmergeされた後、default branch上でEpic Delivery Reviewを行う。 |
| REQ-021 | Epic Delivery ReviewのP0／P1に実装修正が必要な場合だけJIT bounded Issueと個別PRを追加し、事前のFinal QA Issueやaggregate Epic PRをdefaultにしない。 |
| REQ-022 | Node、Git、GitHub、Oracle session、Workbench、Candidate ZIP、Execution Brief、Repair Batch、`report.md`のauthorityを分離し、新しい意味的state DBを作らない。 |
| REQ-023 | provider、installed、dogfoodのSkill、Agent、Workflow、Template、Scriptを同一責務へ揃え、旧surfaceとstale参照を除去する。 |
| REQ-024 | 新規・open・active Scopeの次操作をvNextへcutoverし、既存文書は一括移行せず、不足契約だけを通常のPlanning gapとして局所refreshする。 |
| REQ-025 | vNext cutover後、最低4週間かつ5件以上の代表Workflow実行のうち遅い方まで、Planning、Review、Candidate ZIP、Execution Brief、Repair、per-Issue Delivery、Epic Completion、cutoverを実証する。評価は複数module／layer、独自または非標準framework、API／compatibility／data、CLI／build／deployment／documentation、Brief省略が妥当なmechanical changeを含む。 |
| REQ-026 | 直近3件以上の旧Workflowをbaselineとし、Human介入、Main context、旧認知route、Human Gate、semantic state、asset parity、Workflow reliability、changeability、Brief Evidence、implementation convergence、Codex resource、architecture neutrality、wall-clockを分離して測定する。最低評価floorまたはtargetを満たさない場合はE3-I3とInitiativeを完了せず、継続計測、bounded follow-up、Human-approved evaluation restart／extension、rollback、またはHuman中止判断へrouteする。品質悪化を伴う削減を成功としない。 |
| REQ-027 | Human mergeされたE3-I2 PRだけをofficial global cutover activation eventとし、E3-I3をpost-cutover evidence、final release decision、release notes、closure handoffのownerとする。cutover、release decision、Epic finish、Initiative closureを別gateとして定義し、存在しないpost-cutover EvidenceでE3-I2 ReviewをPASSさせない。 |
| REQ-028 | Human承認後のnew Portfolio materializationは、3 Epic／7 Issue semantic keyを一時Workbench ledgerで管理し、Runtimeの`pre_github_fail`、`post_github_remote_only_fail`、`post_github_local_write_fail`、`post_github_body_and_cleanup_fail`、`post_github_local_write_success_cleanup_fail`、post-sync failureへoutcome-specificにbindする。既存remote Issueは`--github-issue`で再利用し、valid local Nodeは再生成せず、dependency／Bundle placement／validate／sync／parityからidempotentに再開できなければならない。partial local cleanupまたはfull unwindはHuman-approved、path-bounded、evidence-preservingとし、manual `.meta.json` authoringとblind create retryを禁止する。 |
| REQ-029 | Existing Initiative canonical `requirement.md`／`design.md`／`plan.md`は、`absent | source-baseline-exact | replacement-exact | unexpected-mismatch`へ分類し、reviewed source blobと一致する`source-baseline-exact`だけをHuman-approved Candidate bytesへpath-bounded atomic replaceできる。各fileはledgerにより部分成功から再開でき、verified source backupからHuman-approved rollbackできなければならない。`report.md`は最終parity後にCandidate SHA marker付きblockを一度だけidempotent appendし、Initiative三文書、全Epic Bundle／ADR、binding substitution、report appendをfinal parityへ含める。 |
| REQ-030 | 旧Portfolio退役前のC0で、`NODE-MATERIALIZATION-MAP.json`に定義した3 Epic／7 Issueのexact title、slug、parent、direct-argv command inputを、exact source Runtimeの`resolve_input_title_and_slug`へside-effectなしで通し、全10件がbyte-exact PASSしなければmaterializationを開始しない。invalid Candidate inputはmaterialization中に修正せず、新Candidate versionへ戻す。 |
| REQ-031 | `new epic`が生成するRuntime scaffoldをexact source template Git blobとobserved bindingからrenderして`runtime-scaffold-exact`を確認し、Node identity placeholderだけを決定的にbindしたCandidate Epic三文書へ、fixed-order atomic replace、actual-byte resume、verified scaffold rollbackで`replacement-exact`へ遷移する。Runtime-created`report.md`、`.meta.json`、rules linksは上書きしない。 |
| REQ-032 | 全Initiative／Epic Artifactはsource Runtimeのtyped filename contractに従い、filename-derived ID／typeとfront matterを一致させる。各fileは`ARTIFACT-MATERIALIZATION-MAP.json`でcanonical destinationまたは`package-only-non-authoritative`、source state、replacement identity、placement order、resume／rollback、final parity、report adoption dispositionを宣言する。Epic-local ADRはCandidate内では`proposed`／`candidate`を維持し、Humanがexact Candidate ZIP SHAと4 ADRのadoptionを明示承認した場合だけ、`EPIC-ADR-ADOPTION.md`のclosed render contractで`accepted`／`accepted`／accepted authority fields／`mirror_eligible: true`を持つcanonical bytesへ遷移する。 |
| REQ-033 | Initiative `report.md`はpre-commit materialization dispositionだけをCandidate SHA marker付きで一度appendし、observed commit SHA、push result、remote HEADを未来値として記録しない。publication evidenceはGit commit object、push result、remote ref、Candidate-SHA-bound Workbench ledgerをauthorityとし、同materializationでreportを二度変更しない。 |
| REQ-034 | Planningは各ScopeのLifecycle活動として実施する。Initiative／Epic PlanningはHuman Portfolio Approval前の現在工程で完了し、Issue Planningは各Issue開始時にJIT実施する。E1-I1〜E1-I3は再利用可能なWorkflow capabilityを実装するものであり、それぞれIssue-localにcurrent Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionを禁止する。 |
| REQ-035 | Human Portfolio Approvalの一次事実は`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`に従うexact source recordとしてCandidate-SHA-bound Workbenchへ保存し、source record SHAとclosed field renderにより`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t231721z-03-disc-human-portfolio-approval-and-m019-evidence.md`へcanonical化する。`report.md`のM-019 referenceはこのcanonical pathとsource record SHAへ解決しなければならない。 |
| REQ-036 | E3-I3はM-001〜M-016をoperationalに評価し、M-017 materialization、M-018 publication、M-019 signed Human Gate／canonical parity／implementation Evidenceをimmutable referenceとして検証し、`FINAL-METRIC-PACKAGE-CONTRACT.md`に従うM-001〜M-019 complete decision packageをfinal Issue Delivery Review、Human merge、Epic Delivery Review、Epic finish、Initiative closureへ渡す。M-017〜M-019を再生成または弱い要約で代替しない。 |
| REQ-037 | Planning SkillはScope／authority stage／必要Evidenceに基づき`archive-candidate`または`git-bound` Review modeを選択する。pre-canonical semantic iterationはarchiveをdefaultとし、実path、CI、merge-base、GitHub inline review、non-deterministic materializationがmaterialな場合だけGit-boundを選ぶ。 |
| REQ-038 | canonical後のmechanical correctionはlocal bounded edit、commit／push、Git-bound Reviewを使用できる。canonical後のsemantic correctionはcurrent canonical stateから新Planning Candidateを作成し、Candidate Reviewへ戻す。 |
| REQ-039 | archive Candidate Review PASS後、source HEAD不変、closed binding、Candidate-to-canonical byte／semantic parity、Candidate外変更0、validate／sync PASS、commit diff一致を証明できる場合だけ二度目の完全Semantic Reviewを省略できる。いずれかを証明できなければnew Candidateまたはfresh Git-bound Reviewへ戻る。 |
| REQ-040 | Implementation、Checkpoint、Issue Delivery、PR-style、Epic Delivery ReviewはGit history、CI、semantic BASE、merge-base、default-branch integrated stateを対象とするためGit-boundを原則必須とし、Planning Candidate ZIP PASSで代替しない。 |
| REQ-041 | SkillはReview mode／Revision lane／Human Gateを判断し、wrapper／scriptはfile attachment、identity、source binding、safe extraction、hash／parity、Oracle invocation、result retrieval等の決定的処理だけを所有する。Runtime／wrapperへsemantic materiality classifierを実装しない。 |
| REQ-042 | Issue Planningはfresh Formal Review PASS後にpositiveなHuman Issue Plan Adoption and Implementation-Start Authorizationを取得する。archive pathではHuman authorizationをexact logical Candidate filename／ZIP SHAへbindし、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publicationを完了する。git-bound pathではHuman authorizationをexact reviewed HEAD／exact target pathsへbindし、exact reviewed-content canonical／commit parity、required validation／planning publicationを完了する。各modeの全条件を満たした後だけ`execution-ready`へ遷移し、Review PASSだけ、Human Gateだけ、parityだけ、validation／publication未完了ではExecutorを開始しない。 `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 |
| REQ-043 | archive Candidate identityはlogical filename、version、internal root、MANIFEST candidate ID、ZIP SHA、source bindingで構成し、transport filenameはclosed`(<positive integer>)`suffixだけをaliasとして許可する。Human approvalとcanonical Evidenceはlogical filename／observed transport filename／ZIP SHAを保持する。 |
| REQ-044 | unresolved-placeholder validationは`PLACEHOLDER-ORACLE-MAP.json`に列挙したdynamic file／tokenだけを機械的に検査し、map外static fileはexact Candidate hashで検証する。static literal examplesをsemantic classifierで判定しない。 |

## 5. 非機能要件

### NFR-001 変更容易性

- Prompt、model label、Oracle UI、Review field、Concern catalog等の可変部分を薄いadapter、prompt resource、Protocol contractへ局所化する。
- RuntimeへPlanning文書、Review JSON、Candidate ZIP、Execution Brief、Repair Batchの意味parserを追加しない。
- 階層別Depth Contractを使い、InitiativeではPortfolio、EpicではIssue境界、Issueでは実装計画、Execution Briefではcurrent codeを深掘りする。

### NFR-002 Git・side effect・情報安全性

- ChatGPT、`spec-dock-chatgpt`、Executor、Reviewer、Candidate ZIP処理はcommit、push、stash、force、mergeを行わない。
- Mainだけがdiffとverificationを確認して明示的commit／pushを行い、Humanだけがmergeする。
- Prompt resource、Operator Context、GitHub外file、Oracle／Human Relay request／response、Workbench、Candidate ZIP、Artifact、Architecture-Aware Execution Brief、Repair Batch、`report.md` evidenceへ、secret、token、cookie、credential、private key、`.env`、production dump、private customer dataを含めない。必要な外部情報は、Humanが明示承認した最小のredacted subsetとして渡し、復元可能なcredential fragmentを残さない。
- Process invocationはdirect argvをdefaultとし、`/bin/sh -c`／`/bin/zsh -lc`、pipe、redirect、heredoc、command substitution、shell variable展開、Prompt／pathのcommand string補間を通常経路で使用しない。対象toolが本質的にshell semanticsを要求しdirect-argv代替がない場合だけ、Human-approved Epic Design、固定command template、untrusted input拒否または安全なencoding、injection regression test、明示的rollback mechanism／trigger、tested rollback evidenceをすべて伴う明示例外とする。いずれかが欠ける例外はgateをPASSしない。
- Candidate ZIPはsafe extractionを通し、absolute／`..`／backslash ambiguity／NUL path、symlink／hardlink／device／FIFO／socket／その他special entry、duplicate／case-fold／Unicode-normalization collision、encrypted entry、nested archive、executable／unexpected binary／non-UTF-8 payload、file count／expanded size／compression ratio超過、CRC failureを拒否する。許容path集合は`MANIFEST.json.files ∪ MANIFEST.json.control_files`と完全一致し、全size／SHAが一致しなければならない。`CHECKSUMS.sha256`はpayloadと`MANIFEST.json`をhashし、自身だけをself-hash-exemptとし、外部ZIP SHAがZIP全体をbindする。exact ZIPを完全検査できない場合は`insufficient-evidence`とし、別入力へfallbackしてFormal PASSを生成しない。

### NFR-003 信頼性・回復性

- transport failure、Review FAIL、planning-gap、insufficient-evidence、Human rejectionを区別する。
- Candidate ZIPの各versionをimmutableとし、ReviewとHuman Approvalをexact ZIP SHAへbindする。
- Oracle session、Workbench ZIP、checksumsを用いて中断・再開できる。
- Canonical replacementはsource backup、replacement staging、per-file ledger、atomic replace、actual-byte reclassificationにより部分成功から再開できる。unexpected mismatchはfail closedとし、Human-approved rollbackまたはblocked stateへrouteする。

### NFR-004 分析品質と資源効率

- ChatGPTの横断分析による理解、Evidence、テスト戦略、実装収束を第一級指標とする。
- Codex token／tool call／探索／failure cycle削減を第二級指標とする。
- raw ChatGPT transcriptをMainへ常時戻さない。
- Initiative-level評価は、cutover後の最低4週間かつ5件以上の代表Workflow実行のうち遅い方まで継続し、直近3件以上の旧Workflow baselineと比較する。
- E1／E2は各Workflow完了時にevidenceを記録する。E3-I2はpre-cutover baseline completeness、parity、replay、rollback readinessを所有し、Human mergeでofficial cutoverをactivateする。E3-I3はpost-cutover weekly aggregation、final decision package、release decisionを所有する。評価floorまたはtarget未達時はrelease、Epic finish、Initiative closureを禁止する。

### NFR-005 保守性・可読性

- canonical仕様書と主要Artifactは日本語ファーストとする。
- 旧案と現行DecisionをCurrent Snapshotへ混在させない。
- Planning PromptのSlicing Contractを一箇所に定義し、Scope別Promptへ重複コピーしない。

### NFR-006 互換性

- Initiative ID、filesystem path、Node metadata、canonical file名、dependency commandを安定interfaceとする。
- closed／finished Scopeをhistorical artifactとして不変に保つ。
- GitHub上のCodex PR Reviewを初期cutoverで廃止しない。

### NFR-007 汎用性

- SpecDock自身のdogfoodを一般的なEpic定義へ混入させず、Representative Real-Use Validationの一例として扱う。
- Architecture-Aware Execution Briefは特定architecture、framework、domain、language、product typeを前提にしない。

### NFR-008 認知資源配分とWorkflow単純性

- CodexはPlanning文書の横断分析、無関係file selection、semantic rewriteを標準責務にせず、Workflow制御、deterministic validation、Git transactionへ集中する。
- archive／GitのReview modeを別々の巨大Workflowとして実装せず、一つのPlanning Candidate lifecycleへ正規化する。
- Scope packageは必要最小限とし、Issue CandidateへInitiative materialization contractを持ち込まない。
- mode／lane選択、Candidate generation、Review、adoptionの各stepをEvidenceとして記録し、silent fallbackを禁止する。

## 6. 受入条件

| ID | 受入条件 |
|---|---|
| AC-001 | Initiative三文書、全Epic三文書、Issue Boundary Mapsが相互に整合し、REQ-001〜REQ-044を3 Epicへtraceできる。 |
| AC-002 | Thin Initiative BundleがEpic内部の実装詳細を複製せず、cross-Epic Goal、constraints、Capability Map、Portfolio Gateを所有する。 |
| AC-003 | 各Epic BundleがActor Outcome、Scope、Architecture、Issue Seeds、dependency、per-Issue PR boundary、Epic Delivery Reviewを定義する。 |
| AC-004 | Issue Seedごとにmerge後Outcome、end-to-end責務、独立PR理由、dependency、acceptance evidence、Milestoneではない理由が明示される。 |
| AC-005 | Planning生成前にSlicing Contractが適用され、返却前にConsolidation Reviewが行われる。 |
| AC-006 | Planning ReviewがInitiative Bundleだけでなく全Epic BundleとIssue Boundary Mapsを`decomposition-quality`で評価する。 |
| AC-007 | Candidate ZIPがcomplete、self-describing、immutable per version、non-canonicalであり、ZIP SHAで識別できる。exact ZIPのpath／entry type／encryption／binary／resource limit／CRC／manifest／checksumをfail closedで完全検査できない場合はFormal Review PASSを生成しない。 |
| AC-008 | fresh ReviewerがZIPを変更せずfinding／verdictを返し、P0／P1時にPlannerが完全な新ZIPを再生成する。 |
| AC-009 | PASSしたZIPがsafe extractionされ、Humanが展開内容とexact SHAを確認し、E1-I1〜E1-I3の12-cell M-019 matrix、violations 0、approver／timestamp、stable canonical evidence locatorを含むexact signed approval recordを作成する。 |
| AC-010 | Human承認前にEpic／Issue Node、GitHub Issue、dependencyを作成しない。 |
| AC-011 | Human承認後、C0でcanonical source blob／destination ownership／source backup／replacement stagingを検証してから、active pointer preflight、17 edge除去、旧7 Epic retirement、3 Epic／7 Issue materialization、9 dependency、canonical三文書置換、Epic Bundle／ADR配置、report append、validate／sync／parityを順に完了し、一つの明示commit／pushへ到達できる。 |
| AC-012 | ChatGPT連携がexact GitHub repository／branch／HEADへfail closedでbindされる。 |
| AC-013 | Planning Reviewはexact HEAD snapshot、Checkpoint／Issue Delivery／Epic Deliveryは明示semantic BASEからreviewed HEAD、PR-style Reviewはmerge-baseからPR HEADを用い、mutation frontierとContract Owner全体を評価する。P0／P1、P2／P3、BASE／ancestryを含む証拠不足を意図したsemanticsで扱う。 |
| AC-014 | Targeted ReviewがadvisoryでありFormal Gateやmutationを発生させない。 |
| AC-015 | Architecture-Aware Execution Briefが非機械的UnitでEvidence、Applicable Concerns、tests、implementation、stop conditionsを具体化する。 |
| AC-016 | Repair BatchがSource HEADへbindされ、上位Planを変更せずbounded repairをExecutorへ渡す。 |
| AC-017 | Issue Executionがwrite role=`executor`、read-only closed set=`explorer`,`researcher`,`consultant`,`deep-consultant`をprovider／installed／dogfoodでexact-set検証し、missing／extra／renamed／write-capable／Grade-routed entryを拒否する。Execution Brief、Checkpoint、Repair、Issue Delivery Review、dedicated PR、Human merge、Issue finishを一つのvertical IssueでE2E処理できる。 |
| AC-018 | 各implementation Issueが個別PRを持ち、Human mergeとreviewed HEAD確認後にfinishする。 |
| AC-019 | Epic Completionが全Issue merge後のdefault branch上でEpic Delivery Reviewを行い、aggregate Epic PRを作らない。 |
| AC-020 | Epic Reviewで実装修正が必要な場合だけJIT bounded Issueを作成する。 |
| AC-021 | provider／installed／dogfood parityが確認され、旧必須surfaceとstale referenceが残らない。 |
| AC-022 | 既存open Scopeが文書一括migrationなしでvNextへ入り、不足契約だけ局所refreshできる。 |
| AC-023 | cutover後の最低4週間かつ5件以上の代表Workflow実行を完了し、複数module／layer、独自／非標準framework、API／compatibility／data、CLI／build／deployment／documentation、mechanical skipのtask shapeを含む。 |
| AC-024 | 直近3件以上の旧Workflow baselineに対し、5件中4件以上で予定外Human介入0、raw transcript必須読込0、handoff中央値30%以上削減、maintained Workflowで旧local cognitive route必須invocation 0、Human Gate violation 0、新規semantic state DB 0、provider／installed／dogfood parity 100%を確認する。Brief品質とimplementation convergenceはbaselineより改善し、非適用Concern捏造0とする。 |
| AC-025 | Prompt／Operator Context／Human Relay／GitHub外file／Workbench／Artifact／Execution Brief／Repair Batch／report evidenceへのsensitive data混入0を検証し、process launchがdirect argvをdefaultとすること、shell例外がHuman-approved Design、固定template、input validation／encoding、injection regression evidence、明示的rollback mechanism／trigger、tested rollback evidenceをすべて持つことを確認する。欠落時はPASSしない。 |
| AC-026 | E3-I2のHuman mergeがofficial cutoverをactivateし、E3-I3がpost-cutover dedicated branch／draft PR、4週間／5件Evidence、final Review、Human release decisionを所有する。E3-I3 merge後にEpic Review／finish、Initiative closureを順番に行い、未達時はcontinue／follow-up／rollback／terminationへfail closedでrouteする。 |
| AC-027 | observed Runtime create outcomesとpost-sync failureをfailure injectionで再現し、各semantic keyについてremote-only時の`--github-issue`再利用、valid local Nodeのno-rerun、partial localのdoctor-first／bounded cleanup、sync resume、exact 9 dependency、partial Bundle placement resume、Human-approved full unwind、3 Epic／7 Issue count、candidate-to-canonical parityを重複GitHub Issue／Nodeなしで証明する。 |
| AC-028 | 現行Initiative三文書がsource-baseline-exactの状態から、requirement→design→planの固定順でatomic replaceされ、任意の部分成功prefixからreplacement-exactをskipしsource-baseline-exactだけを継続できる。unexpected mismatchで停止し、Human-approved rollbackはverified source backupを使ってbaseline-exactへ戻せる。最終`report.md` dispositionは同一Candidate SHA markerを一度だけ持ち、全canonical file／ADR／binding／report parityを満たす。 |
| AC-029 | exact source Runtime validatorを用いたC0 fixtureで全10 Node title／slug／parentがPASSし、invalid input時にold edge、old Node、GitHub Issue、canonical fileのmutationが0である。 |
| AC-030 | 各新Epicについてsource template renderとactual Runtime scaffoldが一致し、Candidate templateの許可placeholderだけをbindして9 canonical Epic documentsがself-identifyingなfront matter、heading、canonical pathを持つ`replacement-exact`へ到達する。partial prefix resumeとverified scaffold rollbackを実証する。 |
| AC-031 | source Runtime parser／duplicate scannerで全Candidate Artifactのfilename-derived ID／type、front matter、timestamp slotがvalidかつuniqueであり、全canonical Artifactがdisposition mapどおり配置され、package-only Artifactがcanonical pathへ存在しない。4 Epic-local ADRはHuman approval前のproposal templateから、approved SHA／Human identity／approval time／bound Epic identityだけをclosed renderし、canonical bytesが`accepted`、`authority: accepted`、accepted authority fields、`mirror_eligible: true`を持ち、source Runtimeのaccepted ADR collectionで4／4検出される。 |
| AC-032 | `report.md`のCandidate-SHA pre-commit dispositionがfinal pre-commit parity後に一度だけ存在し、その後のcommit／push／remote verificationはGit／remote ref／Workbench ledgerで観測され、report再変更なしにpublication terminal stateを証明できる。 |
| AC-033 | E1-I1〜E1-I3が`Implement ... Workflow` identity、implementation-centered outcome、Issue-local mandatory four-item Non-goal matrixを持ち、current Portfolio replanning 0、downstream Issue三文書の先行作成0、Human approval bypass 0、Planning-only completion 0である。各IssueのJIT PlanningはそのIssue Lifecycle内で実施される。 |
| AC-034 | signed Human approval source recordのSHA、exact Candidate SHA、12／12 PASS matrix、violations 0、Human identity／timestampが`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`のclosed renderでcanonical Human approval Evidence Artifactへmaterializeされ、`report.md`のM-019 locatorがそのpathとsource-record SHAへ解決する。 |
| AC-035 | E3-I3 local Requirement／Design／Plan／Issue Boundary Map、All-Issue Map、Materialization Mapが、operational M-001〜M-016とimmutable M-017〜M-019 referenceを区別しつつ、final Review／Human merge／Epic Review／Initiative closureのterminal packageをM-001〜M-019へ統一する。 |
| AC-036 | Initiative／Epic／Issueの3 ScopeでPlanning Candidateを生成でき、Initiativeは完全Portfolio、EpicはEpic三文書＋Issue Boundary Map、IssueはIssue三文書という最小package contractを満たす。 |
| AC-037 | `archive-candidate` Reviewがexact ZIP SHA＋source HEADへ、`git-bound` Reviewがreviewed HEAD＋target paths＋必要なBASE／merge-baseへbindされ、両modeのPASSを相互に誤継承しない。 |
| AC-038 | Semantic finding fixtureはChatGPT Blue Teamの完全新Candidateへrouteされ、Mechanical fixtureはclosed path／field／literal／meaning invariant／diff budgetを事前宣言したlocal deterministic revisionへrouteされる。どちらもnew identityとfresh Reviewを持つ。 |
| AC-039 | archive PASSからcanonical adoptionしたfixtureでsource HEAD不変、closed binding、Candidate外変更0、byte／semantic parity、validate／sync、commit diff一致を証明する。parityを崩すfixtureでは二度目のReview省略を拒否し、new CandidateまたはGit-bound Reviewへfail closedで戻る。 |
| AC-040 | Checkpoint／Issue Delivery／PR／Epic Delivery ReviewがGit-bound rangeとCI／default-branch Evidenceを使用し、Planning Candidate ZIPだけからPASSを生成しない。Planning Skillがmode／laneを選び、wrapperがsemantic判断せず決定的入力処理だけを行うことをtestで確認する。 |
| AC-041 | archive Issue Candidateとgit-bound Issue Planningの双方で、Review PASSのみの`execution-ready`遷移を拒否する。archive modeはexact logical filename／ZIP SHAへのHuman authorization、canonical adoption、candidate-to-canonical parity、required validation／planning publicationを、git-bound modeはexact reviewed HEAD／exact target pathsへのHuman authorization、exact reviewed-content canonical／commit parity、required validation／planning publicationをすべて満たした後だけExecutor開始を許可する。wrong SHA／HEAD／target paths、source drift、semantic adoption diff、parity failure、validation／publication failureのnegative fixtureはすべてfail closedになる。 E1-I1 producerとE2-I1 consumerの双方で`PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 各10／10 PASS、合計20／20、violations 0をacceptance evidenceとする。 |
| AC-042 | transport filenameがlogical filenameまたはclosed`(N)`aliasであり、normalized logical filename、ZIP SHA、internal root、MANIFEST identityが一致する場合だけFormal inspectionを継続する。Human signed recordとcanonical Evidenceがlogical／transport filenameとSHAを保持する。 |
| AC-043 | Placeholder Oracle fixtureが、dynamic fileのundeclared token／remaining token／map外dynamic outputを拒否し、static ADR 13のliteral examplesをexact hash一致時に受理する。 |

## 7. 成功指標と評価契約

### 7.1 Evaluation floor、sample、ownership

- 評価期間は、vNext cutover後の**最低4週間かつ5件以上の代表Workflow実行**のうち遅い方までとする。
- baselineは、利用可能な直近の旧Workflow実行を最低3件採取する。Execution Brief比較は同等または再現可能なUnitで`Briefなし／generic Brief／Architecture-Aware Brief`を比較する。
- 代表Workflowは、複数module／layer、独自または非標準framework、API／compatibilityまたはdata／persistence、CLI／build／deployment／documentation、Brief省略が妥当なmechanical changeを含む。
- E1とE2のMainが各実行終了時にWorkflow log、handoff、Review result、failure cycle、wall-clock、Human interventionを`report.md`または対応Evidenceへ記録する。E3-I3のMaintainer／Mainが週次集計、baseline比較、最終decision packageを所有する。
- evaluation floor未達、required task shape不足、target未達、Evidence不足の場合、E3-I3、Epic 3、Initiativeはfinishしない。継続計測、bounded follow-up Issue、rollback、またはHumanによる明示的な継続／中止判断へrouteする。

### 7.2 Metrics

| ID | 指標 | Baseline | Target | Owner／collection point | Failure／continuation routing |
|---|---|---|---|---|---|
| M-001 | Unplanned Human Intervention | 旧Workflow代表3件以上 | 5件中4件以上で予定外介入0 | E1／E2 Mainが各run終了時に分類、E3-I3集計 | 未達なら原因別follow-upまたはWorkflow再設計。closure禁止 |
| M-002 | Main Context Protection | 旧runのsub-agent／reviewer payload | raw transcript必須読込0、handoff中央値30%以上削減 | MainがtokenまたはUTF-8 byte／文字数をrun終了時記録 | 未達ならPrompt／handoff圧縮を改善し再計測 |
| M-003 | Codex Cognitive Route Proxy | local reviewer、manual planner、Writer、Analyzer invocation | maintained Workflowで必須invocation 0 | Agent／Skill invocation log | allowlist外依存を除去するbounded Issueへroute |
| M-004 | Human Gate Integrity | 旧運用手順 | 自動merge0、未承認分割0、無承認material変更0 | PR／Runtime event audit | 1件でも発生したらrelease blocker |
| M-005 | Minimal State | 旧receipt／ledger／registry件数 | 新規semantic state DB 0 | repository inventory／search | 新stateを除去またはHuman-approved architecture revision |
| M-006 | Asset Parity | provider／installed／dogfood差分 | 100% parity | parity test／smoke | E3-I2 cutover Reviewまでに差分0とし、E3-I3 final Reviewでも再確認する |
| M-007 | Workflow Reliability | vNext baselineなし | 各代表Workflowが完走または明確にfail closed | E2E report、CI、Oracle／GitHub evidence | silent／ambiguous failureはrelease blocker |
| M-008 | Changeability Drill | vNext baselineなし | Prompt、model label、Review／Brief fieldをRuntime migrationなしで局所変更可能 | E3-I3 changeability drill | migration必要ならboundary再設計 |
| M-009 | Brief Evidence Quality | Briefなし／generic Brief | accepted sampleでmaterial Evidence omission、unsupported assumption、wrong Concern selection 0 | Brief review rubric、Checkpoint finding分類 | finding発生時はPrompt／retrieval修正後に再評価 |
| M-010 | Implementation Convergence | Briefなしbaseline | first Checkpoint PASS率を改善、またはfailure cycle／手戻りを減少。品質非劣化 | Executor log、Review result | どちらも改善せず遅延増なら継続採用をHuman判断 |
| M-011 | Codex Resource Shift | Briefなし／Git-first Planning baseline | tokenが取れる場合は削減。取れない場合はsemantic file selection、tool call、探索command、handoff量、failure cycleの一つ以上を改善 | 各Planning runがScope、Review mode、Revision lane、Codex token／proxy、attachment count、handoff量を記録 | 改善なしでも品質効果、総遅延、mode／lane選択妥当性を含む継続判断を記録 |
| M-012 | General Applicability | architecture別baselineなし | required task shapesで適用Concernが妥当、非適用Concern捏造0 | model smoke、Human／Review classification | task-shape欠落または捏造時は評価継続 |
| M-013 | Total Delivery Efficiency | Briefなし／Git-first Planning baseline | ChatGPT latency、Candidate packaging、Review、adoptionを含む総時間と品質／resource tradeoffを記録 | wall-clock、Oracle session、Review mode／Revision lane log、Executor timing | 総合悪化またはmode固定化が不合理な場合はSkill policy調整／Human continuation／rollback decision |
| M-014 | Over-decomposition Prevention | current 7-Epic／component-sliced planning | approved PortfolioでHumanの「細かすぎる」再分割要求0 | Initiative／Epic Planning report | finding時はPortfolioへ戻りConsolidation |
| M-015 | Vertical Issue Quality | current candidate baseline | materializeされたIssueの100%が独立PR Outcomeとend-to-end responsibilityを持つ | Issue Boundary Review、PR audit | horizontal／low-value Issueはmaterializeしない |
| M-016 | Security and Invocation Safety | source contract | sensitive-data exposure 0、unsafe shell interpolation 0、未承認shell exception 0、rollback mechanism／trigger／tested evidence欠落0 | fixture scan、process-spawn test、relay／artifact audit、rollback drill | 1件でもcutover／release blocker、credential rotation／incident response／rollbackへroute |
| M-017 | Materialization Identity Integrity | v7 blocking findings | invalid Node input 0、Runtime scaffold mismatch 0、unresolved binding placeholder 0、Artifact ID／type collision 0、Epic ADR adoption／mirror state mismatch 0 | C0 pure-validator fixture、scaffold render parity、Artifact parser／duplicate scan、accepted ADR collector exact-set test | 1件でもmaterialization blocker、新Candidateへ戻す |
| M-018 | Publication Evidence Integrity | v7 contradictory requirement | future publication claim 0、pre-commit report marker 1、local commit＝remote HEAD | report marker check、Git commit／push／remote-ref audit、Workbench ledger | mismatch時はcompletion禁止、reportを推測更新しない |
| M-019 | Planning Capability Role Clarity | Candidate v8 Human Gate ambiguity | E1-I1〜E1-I3の100%がimplementation outcomeとmandatory four-item Non-goal matrixを持ち、current Portfolio replanning 0、downstream planning代行／pre-authoring 0、Human approval bypass 0、Planning-only completion 0 | E1-I2がCandidate authoring時に収集し、Humanがexact signed approval recordで3 handoffs／12 cellsをPASS・violations 0として署名する。`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`でcanonical evidenceへrenderし、M3／M4 parity、E1 implementation／dogfood evidence、E3-I3 immutable reference、Initiative Final Completion Summaryで再検証 | 署名record、canonical locator、12／12 PASS、source-record SHAのいずれかが欠けたらHuman Approval／materialization／release／Initiative closure禁止。Portfolio Planningへ戻す |

## 8. 主要リスク

| ID | リスク | 緩和策 |
|---|---|---|
| R-001 | モデルが整理しやすい技術レイヤーで過剰分割する。 | Slicing Contract、Issue Projection、Consolidation Review、decomposition-quality P1。 |
| R-002 | Initiative PlanningがEpic／Issue実装詳細まで先取りして陳腐化する。 | 階層別Depth Contract、Issue詳細JIT。 |
| R-003 | Candidate ZIP解析が不安定。 | live smoke、manifest／marker、`insufficient-evidence`、non-formal diagnostic、新しい完全ZIPとfresh Formal Review。 |
| R-004 | Candidate ZIPとcanonical文書のauthorityを混同する。 | non-canonical manifest、Human SHA approval、materialization parity。 |
| R-005 | ZIP展開でsecurity incidentが起きる。 | safe extraction、allowlist、size／ratio limit、path validation。 |
| R-006 | Epic／Issue Nodeを承認前に作り過剰分割を固定する。 | Human approval後だけmaterialize。 |
| R-007 | ChatGPTがGitHub branch／HEADを誤認する。 | exact binding、local preflight、fail closed。 |
| R-008 | Brief／RepairがPlanの裏口になる。 | authority hierarchy、freeze、planning-gap routing。 |
| R-009 | per-Issue PR固定費が増える。 | Minimum Sufficient Decomposition、Milestone内部化。 |
| R-010 | Issueが巨大化する。 | independent review／rollback boundaryで必要な場合だけ分割。 |
| R-011 | Global cutoverで旧surfaceが残る。 | parity、global search、existing Scope replay。 |
| R-012 | 品質を犠牲にCodex削減を追う。 | 品質指標を第一級、資源／時間を分離評価。 |
| R-013 | 少数・短期間・偏ったtask shapeだけで成功判定する。 | 4週間／5件floor、3件baseline、required task shapes、E3-I3 release／closure gate。 |
| R-014 | reviewed Candidate versionを同じfilename／versionで上書きしReview／Approval identityを誤る。 | monotonic version、new filename／MANIFEST／SHA、旧version immutable。 |
| R-015 | Prompt／Artifactへcredentialが混入、またはPrompt／pathのshell interpolationでcommand injectionが起きる。 | global sensitive-data policy、direct argv、redaction、explicit shell exception、injection tests、rollback mechanism／trigger／tested evidence。 |
| R-016 | cutoverを成立させるmerge前にpost-cutover Evidenceを要求し、release lifecycleが循環する。 | E3-I2 cutover activationとE3-I3 evaluation／releaseを別Issue／PR／Human gateへ分離する。 |
| R-017 | GitHub Issue作成後のcreate failureまたはpost-sync failureでremote-only／partial local／valid local stateが残り、blind retryがduplicate Issue／Nodeを作る。 | semantic-key materialization ledger、observed outcome classification、`--github-issue` link-existing、doctor-first inspection、bounded cleanup、sync resume、exact dependency／Bundle parity、Human-approved unwind。 |
| R-018 | Existing canonical三文書がCandidate bytesと異なることをgeneric mismatchとして扱い、旧Portfolio退役後に置換不能となる、または部分置換でmixed stateが残る。 | C0 source preflight、four-state classification、verified source backup、replacement staging、atomic per-file replace、ledger resume、Human-approved rollback／blocked state、report marker、final parity。 |
| R-019 | approved Node title／slugがRuntime入力契約に違反し、旧Portfolio退役後の最初のcreateで停止する。 | exact Runtime-valid title／slug map、C0 pure validation、explicit slug、invalid input時のno-mutation hard stop。 |
| R-020 | Runtime-created Epic scaffoldをabsentと誤認し、Candidate Bundle placementで必ずmismatch停止する。 | source template blob binding、runtime-scaffold-exact state、atomic render replacement、resume／rollback。 |
| R-021 | Artifact filename-derived ID／typeがfront matterと不一致、duplicate timestamp slot、ADR misclassificationが発生する。 | exact source parser／duplicate scanner、typed filename normalization、file-level disposition／parity。 |
| R-022 | Humanが承認したArtifactのcanonical／package-only disposition、またはEpic-local ADRのproposal→accepted transitionが曖昧で、Human approval、canonical authority、mirror eligibilityが不一致になる。 | `ARTIFACT-MATERIALIZATION-MAP.json`、`EPIC-ADR-ADOPTION.md`、closed approval render、accepted ADR collector exact-set、report adoption disposition、package-only exclusion。 |
| R-023 | pre-commit reportに未来のcommit／push成功を要求し、one-commit contractと矛盾する。 | pre-commit report model、Git／remote ref publication authority、no second report mutation。 |
| R-024 | Planning Workflow実装Issueが「他IssueをPlanningするIssue」と誤解され、上位Portfolioを実装中に再設計する。 | `Implement ... Workflow` title、Lifecycle／capability境界、明示Non-goals、ADR 17、Human Gate regression Review。 |
| R-025 | HumanへM-019の質問を表示しただけでgeneric Candidate SHA approvalを記録し、3 handoffの12-cell PASSを署名済み一次事実として保持できない。 | exact approval source record、source-record SHA、canonical Human approval evidence Artifact、report locator、M-019 final trace。 |
| R-026 | E3-I3のlocal handoffがM-001〜M-016で終端し、M-017 materialization、M-018 publication、M-019 Human-Gate Evidenceがrelease／Epic／Initiative closureから脱落する。 | `FINAL-METRIC-PACKAGE-CONTRACT.md`、immutable references、M-001〜M-019 terminal package、local／upper contract parity。 |
| R-027 | Skillがsemantic変更をMechanical Revisionと誤分類し、意味変更を狭いdiffとしてReviewへ流す。 | closed mechanical eligibility、predeclared diff budget、meaning invariant、ambiguity時Semantic lane、fresh Review。 |
| R-028 | ZIP PASS後のcanonical adoptionでCandidate外変更、source drift、unclosed bindingが混入し、reviewed identityとGit stateが乖離する。 | source HEAD recheck、Candidate-to-canonical parity、Candidate-external diff 0、validate／sync、parity失敗時new Candidate／Git-bound Review。 |
| R-029 | Issue Planning Review PASSをHuman adoption／canonical parityと誤認し、未採用または未検証PlanからExecutorを開始する。 | positive Human Issue Plan Adoption and Implementation-Start Authorization、archiveではexact logical filename／ZIP SHA、git-boundではexact reviewed HEAD／exact target paths、adoption／commit parity、required validation／planning publication、Review-PASS-only／validation-failure negative fixture。 回帰testは`PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 全10分類をproducer／consumer別に検証する。 |
| R-030 | upload transportのduplicate-avoidance suffixを別CandidateまたはEvidence不足と誤認する、あるいは曖昧なrenameを許容する。 | MANIFEST logical filename、closed `(N)` alias、exact ZIP SHA／root／candidate ID検証、logical／observed filenameのReview／Human evidence記録。 |
| R-031 | static文書内のliteral placeholder例を未解決dynamic tokenとして拒否する、またはdynamic fileの未宣言tokenを見逃す。 | `PLACEHOLDER-ORACLE-MAP.json`によるclosed dynamic file／token set、static exact-hash policy、positive／negative fixtures。 |

## 9. Capability Epic Portfolio

本Initiativeは、次の3つの独立Capability Epicへ分ける。

1. **ChatGPT Planning and Advisory Review**
2. **Analysis Guided Issue Execution and Per Issue Delivery**
3. **Multi Issue Epic Completion and Global Cutover**

詳細Requirement、Design、Plan、Issue Boundary Mapは各Epic Bundleに定義する。Initiative文書はEpic内部の詳細を重複保持しない。

## 10. Initiative Completion

- 3 EpicがHuman merge／Epic finish済み。
- REQ-001〜REQ-044、AC-001〜AC-043の証拠が揃う。
- old 7-Epic planning structureとその未承認Issue候補がsupersededとして処理される。
- E3-I2 Human mergeによるcutover activation、E3-I3 Human mergeによるrelease decision、Evaluation floor、required task-shape diversity、baseline、M-001〜M-019 decision evidence、existing Scope replay、parity、rollback evidenceがある。M-019はexact signed Human approval record、canonical Human approval Evidence Artifact、canonical materialization parity、E1 implementation／dogfood evidence、E3-I3 immutable reference、Initiative Final Completion Summaryへtraceされる。
- Initiative Final Completion SummaryがHuman承認される。
