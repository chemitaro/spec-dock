# init-00322 GPT 56 ChatGPT First Intelligence Architecture — 設計

## 1. 設計目的

本設計は、`ChatGPT 5.6 Pro Delegation-First Workflow vNext`のcross-Epic architecture charterを定義する。Initiative文書は能力Portfolio、authority、共通制約、Review／Approval／Deliveryの境界を所有し、Epic固有の詳細ArchitectureとIssue境界は各Epic Bundleへ委譲する。

## 2. System Context

```text
Human
  ├─ Goal / Portfolio Approval / Material Change / Merge
  v
Codex Main Orchestrator
  ├─ deterministic anchors
  ├─ ChatGPT task orchestration
  ├─ candidate adoption
  ├─ explicit Git transaction
  └─ Human Gate
       |
       +--> spec-dock-chatgpt / Oracle / ChatGPT
       |      ├─ Planning Bundle
       |      ├─ Formal / Targeted Review
       |      ├─ Candidate ZIP revision
       |      ├─ Architecture-Aware Execution Brief
       |      └─ Repair Batch
       |
       +--> Executor
       |      └─ bounded implementation / verification
       |
       +--> SpecDock Runtime
              └─ Node / dependency / validate / sync / deterministic files
```

ChatGPTはrepositoryを読み完全な分析成果物を生成するが、filesystem、Git、Nodeを変更しない。ExecutorとRuntimeはlocal working treeまで、Mainは明示的commit／push／PRまで、HumanはPortfolio承認とmergeを所有する。

## 3. AuthorityとSSOT

| 情報 | SSOT |
|---|---|
| Initiative／Epic／IssueのGoal・Requirement・Design・Plan | Human承認済みcanonical三文書 |
| architecture decision | accepted ADR＋`report.md` disposition |
| Planning candidate | immutable Candidate ZIP＋ZIP SHA |
| Planning Review result | Reviewer output bound to ZIP SHA |
| Human Portfolio Approval | exact ZIP SHAへの明示承認 |
| Node／dependency／active | SpecDock Runtime metadata |
| tracked repository | GitHub exact branch／HEAD |
| local mutation | working tree／Git diff |
| ChatGPT run | Oracle session |
| Execution Unit guidance | accepted Architecture-Aware Execution Brief |
| bounded repair | accepted Repair Batch |
| completion／handoff | `report.md` |
| temporary drafts／safe extracted Human view | Workbench |

Candidate ZIPはGit管理されなくてもReview／Approval identityを持つが、Human承認とcanonical materializationまではproduct authorityを持たない。

## 4. Hierarchical Depth Contract

### Initiativeで深掘りする

- strategy Goal、Why now、cross-Epic constraints。
- Capability Portfolio、Epic boundary、Epic dependency。
- Slicing Contract、per-Issue PR default、Initiative completion。
- cross-Epic ADR、compatibility、cutover。

### Initiativeで固定しない

- Epic内部interfaceの詳細、file／class、Issue Milestone、test case、exact implementation sequence。

### Epicで深掘りする

- Actor Outcome、Scope／Non-scope、Architecture boundary。
- cross-Issue interface、error／state／compatibility boundary。
- actual Issue Seeds、dependency、per-Issue PR boundary、Epic Delivery Review。

### Epicで固定しない

- Issueの完全三文書、Milestone、Execution Unit、具体的test case、file-level change。

### Issue／Execution Unit

- Issue PlanningはRequirement、detailed Design、Execution Units、verification、Exit ContractをJITで定義する。
- Architecture-Aware Execution Briefはexact HEAD上の具体的tests／implementation strategyをJITで定義する。

## 5. Initiative Planning Orchestration

```text
Human Goal
→ Thin Initiative Bundle
→ Candidate Epic Portfolio
→ Epic Planning × N
→ Issue Boundary Projection × N
→ Portfolio Consolidation
→ Candidate ZIP
→ fresh Planning Review
→ Planner Revision loop if P0/P1
→ safe extraction
→ Human approves exact ZIP SHA
→ Epic／Issue Node materialization
→ canonical placement／validate／sync
→ explicit commit／push
```

Initiative PlanningはEpic Seedだけで完了しない。全Epic BundleとIssue Boundary Mapを作り、Issue投影でEpic境界を逆検証する。ただしInitiative文書へEpic詳細を転記しない。

## 6. Universal Planning Candidate Architecture

### 6.1 Scope-specific Candidate structure

```text
Initiative Candidate
├── Initiative Bundle
├── all Epic Bundles
├── all Issue Boundary Maps
├── dependencies／ADRs／materialization contracts
├── SOURCE-BASELINE.json
├── MANIFEST.json
└── CHECKSUMS.sha256

Epic Candidate
├── requirement.md
├── design.md
├── plan.md
├── issue-boundary-map.md
├── relevant artifacts／ADRs
├── SOURCE-BASELINE.json
├── MANIFEST.json
└── CHECKSUMS.sha256

Issue Candidate
├── requirement.md
├── design.md
├── plan.md
├── SOURCE-BASELINE.json
├── MANIFEST.json
└── CHECKSUMS.sha256
```

### 6.2 Candidate lifecycle and immutable identity

```text
Planner → Candidate version N（例: `candidate-v4.zip`）／MANIFEST version N／ZIP SHA N
fresh Reviewer → findings／verdict bound to filename＋version＋ZIP SHA N
P0/P1 → Planner creates Candidate version N+1（例: `candidate-v5.zip`）／new MANIFEST identity／new ZIP SHA N+1
P2/P3 only → no document mutation
PASS → safe extraction → Human review of the exact reviewed ZIP SHA
```

version `N`のZIP bytes、filename、MANIFEST identity、Review resultを上書きしない。Revisionは必ず単調増加する新version、新filename、新external SHAを持ち、完全なZIPとしてfresh independent Reviewを受ける。ReviewerはZIPを修正しない。Humanも展開fileを直接編集して承認しない。

### 6.3 Dual Review transport

Planning Review Requestは二つのmodeへ正規化する。

```text
archive-candidate:
  scope_id
  repository／branch／source_head
  logical_candidate_filename／observed_transport_filename／version／zip_sha256／internal_root

git-bound:
  scope_id
  repository／branch／reviewed_head
  target_paths
  semantic_base | merge_base（protocolに応じて必須）
```

Selection policy:

- Initiative pre-canonical: archive-candidate default。
- Epic／Issue pre-canonical semantic iteration: lightweight archive-candidate default。
- actual repository path、CI、GitHub inline comments、compliance candidate commit、non-deterministic materializationが必要: git-bound fallback。
- canonical mechanical correction: git-boundを優先。
- canonical semantic correction: current canonical stateからnew archive Candidateを作る。
- Checkpoint／Issue Delivery／PR／Epic Delivery: git-bound必須。

archive modeとgit modeは異なるFormal identityであり、一方のPASSを他方へ自動継承しない。archive modeのobserved transport filenameは`CANDIDATE-IDENTITY-AND-TRANSPORT.md`のclosed`(N)`aliasだけをlogical filenameへnormalizeできる。normalized name、ZIP SHA、internal root、MANIFEST candidate IDのいずれかが不一致なら`insufficient-evidence`とする。

### 6.4 Dual Revision lanes

```text
Semantic Revision
- Requirement／Architecture／slice／dependency／authority／Acceptance Criteria／Gate／Workflow change
- ChatGPT Blue Team
- complete Candidate replacement

Mechanical Revision
- typo／front matter delimiter／exact path／closed placeholder／literal count／link／manifest／checksum
- Main／Codex／deterministic script
- closed file／field／old-new literal／meaning invariant／diff budget required
```

Mechanical eligibilityの一つでも曖昧ならSemantic Revisionへrouteする。どちらのlaneでもCandidate bytesが変わればnew version、new filename、new root／MANIFEST identity、new SHA、fresh Red-Team Reviewを必須とする。Reviewerはrevision laneに関係なく修正しない。

### 6.5 Candidate-to-canonical parity

archive Candidate PASSをcanonical stateへ採用した後、二度目の完全Semantic Reviewを省略できるのは次をすべて満たす場合だけである。

1. source HEADがReview時と同じ。
2. dynamic renderは`PLACEHOLDER-ORACLE-MAP.json`のclosed file／token allowlist内。map外static fileはexact Candidate hashで検証し、literal placeholder examplesをscanしない。
3. rendered Candidateとcanonical fileのbyte／semantic parityがある。
4. Candidate外file変更が0。
5. validate／sync／link／repository conventionがPASS。
6. commit diffがadoption contractと完全一致。

条件未達、source drift、validation対応による意味変更、Candidate外変更、parity不成立ではnew Candidateまたはfresh Git-bound Reviewへ戻る。

### 6.6 Scope-specific positive Human Gate

Review PASS is evidence for a Human decision, not execution authority. Initiative uses Human Portfolio Approval, Epic uses Human Issue-Slice Approval, and Issue uses Human Issue Plan Adoption and Implementation-Start Authorization.

Issue archive path:

```text
fresh Review PASS on exact logical Candidate filename／ZIP SHA
→ Human approves exact logical Candidate filename／ZIP SHA
→ deterministic canonical adoption
→ candidate-to-canonical parity
→ required validation／planning publication
→ execution-ready
```

Issue git-bound path:

```text
fresh Review PASS on exact reviewed HEAD／exact target paths
→ Human approves exact reviewed HEAD／exact target paths
→ reviewed content is adopted without semantic mutation
→ exact reviewed-content canonical／commit parity
→ required validation／planning publication
→ execution-ready
```

Archive or Git Review PASS alone, Human Gate alone, parity alone, wrong reviewed identity, source drift, semantic adoption mutation, or validation／publication failure is rejected. The full contract and negative fixtures are defined in `PLANNING-ADOPTION-GATE.md` and ADR 21.

### 6.7 Closed Planning Adoption negative-fixture matrix

This table is a package-wide architecture invariant and is normative in this local Design. Any shorter terminal sequence is invalid.

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

### 6.8 Safe extraction and exact-ZIP Formal Review identity

- absolute path、`..` traversal、backslash path ambiguity、NUL pathを拒否する。
- symlink、hardlink、device、FIFO、socket、その他special entryを拒否する。
- duplicate path、case-fold collision、Unicode-normalization collisionを拒否する。
- encrypted entry、nested archive、executable payload、unexpected binary payload、non-UTF-8 text payloadを拒否する。
- allowlisted text extension、file count、expanded size、per-entry／total compression ratioを検査し、CRC failureを拒否する。
- `MANIFEST.json.files[]`をpayload、`control_files[]`を`MANIFEST.json`／`CHECKSUMS.sha256`として扱い、ZIP entry集合が両者の和と完全一致し、全size／SHAが一致することを確認する。
- `CHECKSUMS.sha256`はpayloadと`MANIFEST.json`をhashし、自身だけをself-hash-exemptとする。外部ZIP SHAでZIP全体を照合する。
- observed transport filenameはlogical filenameまたはclosed`(<positive integer>)`aliasだけを許可し、normalized logical filename、ZIP SHA、internal root、MANIFEST candidate IDが一致しなければ`insufficient-evidence`とする。
- exact ZIPを安全かつ完全に検査できない場合は`insufficient-evidence`とする。Git-tracked packや個別attachmentはdiagnostic inputにしか使えず、同じFormal Review identityでPASSを生成できない。Formal Reviewには新しい完全ZIPと新しいSHAが必要である。


### 6.9 Initiative Portfolio Materialization

Human approval後のmaterializationは次のauthorityへ分離する。

- `NODE-MATERIALIZATION-MAP.json`／`NODE-MATERIALIZATION-PREFLIGHT.md`: exact 10 Node inputとC0 pure validation。
- `LEGACY-PORTFOLIO-RETIREMENT.md`: old 7 Epic／17 edge retirement。
- `NEW-PORTFOLIO-MATERIALIZATION-RECOVERY.md`: phase order、Runtime outcome、ledger、resume／unwind。
- `MATERIALIZATION-MAP.md`: semantic key、Runtime-valid title／slug、creation order、exact 9 dependency。
- `CANONICAL-BUNDLE-REPLACEMENT.md`／`CANONICAL-REPLACEMENT-MAP.json`: existing Initiative three-document replacement。
- `EPIC-SCAFFOLD-REPLACEMENT.md`／`EPIC-SCAFFOLD-REPLACEMENT-MAP.json`: exact Runtime scaffoldからbound Epic canonical docsへのreplacement。
- `ARTIFACT-MATERIALIZATION-MAP.json`: 全Artifactのcanonical／package-only disposition。
- `EPIC-ADR-ADOPTION.md`: Human approval後の4 Epic-local ADR proposal→accepted canonical render。
- `REPORT-MATERIALIZATION-DISPOSITION-TEMPLATE.md`／`PUBLICATION-EVIDENCE-CONTRACT.md`: pre-commit reportとGit publication evidence。

```text
C0 source／Candidate／Node input／template／Artifact／destination preflight
→ M0 legacy retirement
→ M1 3 Epic／7 Issue creation／binding
→ M1b Runtime Epic scaffold exact verification
→ M2 exact 9 dependency registration
→ M3a existing Initiative canonical replacement
→ M3b bound Epic canonical replacement
→ M3c canonical Artifact placement／Epic-local ADR accepted render
→ M4 doctor／validate／sync／full parity／pre-commit report disposition
→ M5 one explicit commit／push／remote-ref verification
```

C0は全破壊的操作より前に、exact source Runtimeのtitle／slug validatorで全10 Node inputをside-effectなしで検証する。approved inputがinvalidならmaterialization中に修正せず、新Candidate versionへ戻る。

Existing Initiative三文書は`source-baseline-exact → replacement-exact`、new Epic三文書は`runtime-scaffold-exact → replacement-exact`だけを許可する。New Epic Candidate docsはreviewable binding front matterを持ち、actual ID／GitHub Issue／canonical path／actor／dateだけをrenderする。Runtime-created report／meta／rulesは保持する。

全Artifactはfilename-derived ID／typeとfront matterを一致させ、file-level disposition mapへ従う。package-only self-reviewはcanonical pathへcopyしない。Epic-local ADRはCandidate bytes上のproposalをそのままcopyせず、Human approvalのexact Candidate SHA、approver、approval time、bound Epic identityだけを`EPIC-ADR-ADOPTION.md`のclosed field transitionでrenderし、accepted canonical bytesとして配置する。

Initiative reportはpre-commit dispositionだけを一度appendする。observed commit／push／remote evidenceはGit／remote ref／Workbench ledgerをauthorityとし、reportを二度変更しない。

### 6.10 Candidate version identity

Candidate identityは次のtupleで一意にする。

```text
(candidate version, logical archive filename declared by MANIFEST, internal root, MANIFEST candidate.id, external ZIP SHA-256)
```

どれか一つでも変わる場合は新versionとして扱う。外部transport filenameはidentityそのものではなく観測metadataとし、`<logical-stem>(<positive integer>).zip`だけをclosed aliasとして許可する。normalized name、SHA、internal root、MANIFEST identityが一つでも不一致なら`insufficient-evidence`とする。過去versionを削除または置換してcurrent versionへ見せかけない。Workbench、Oracle session、Review Markdown、Human approval記録は対応するversionとSHAを明示する。Historical exampleを残す場合はcurrent operational instructionと区別する。

## 7. Slicing and Decomposition Architecture

### 7.1 Minimum Sufficient Decomposition

```text
Initiative → まず1 Epic
Epic       → まず1 Issue
```

独立Capability、Acceptance、Risk、Rollback、Dependency、Human Decisionのmaterial boundaryがある場合だけ分割する。固定数heuristicをproduct ruleにしない。

### 7.2 Vertical Issue contract

Issue Seedは次を持つ。

- Actor／Beneficiary。
- merge後のObservable Outcome。
- end-to-endで含む責務。
- separate PR／Review／rollbackが必要な理由。
- dependency。
- acceptance evidence。
- なぜMilestoneではなくIssueなのか。

Foundation、schema、backend、tests、docs、QA、Metrics、Dogfood、Inventory等を単独Issueへしない。必要な活動はOutcomeを届けるIssueへ含める。

### 7.3 Planning lifecycleとPlanning capability implementation

```text
Initiative／Epic Planning
→ Human Portfolio Approval前の現在工程で完了

Issue Planning
→ 各Issue開始時にそのIssue自身へJIT実施

Planning-related implementation Issue
→ 上記Lifecycleを実行可能にするSpecDock Workflow capabilityを実装
```

Planning関連Issueのtitleは`Implement ... Workflow`とし、主要成果をcode／Skill／Prompt／adapter／tests／docs／projectionとして定義する。実Planning runはsubordinate acceptance evidenceであり、Issueの主成果物ではない。

Planning関連IssueはそれぞれIssue-localに、current Portfolio replanning、downstream Issue Requirement／Design／Plan pre-authoring、Human approval bypass、Planning-only completionの4項目を禁止する。materialなboundary gapは下位Issue内で修正せず上位Planningへescalateする。

M-019のprimary ownerはE1-I2／Human Portfolio Approval gateである。Humanは`HUMAN-REVIEW.md`のexact signed recordでE1-I1〜E1-I3の12-cell matrixをPASS・violations 0として署名し、source-record SHAを固定する。`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`はそのrecordを`spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t231721z-03-disc-human-portfolio-approval-and-m019-evidence.md`へclosed renderする。M3／M4はcanonical Epic 1 Plan／Issue Boundary Mapへのfour-item matrix伝播を再検証し、Initiative Final Completion Summaryはimplementation diff、dogfood classification、signed Human Gate evidenceを再参照してM-019をcloseする。E3-I3はこのpre-cutover evidenceをimmutable referenceとしてfinal decision packageへ含めるが、M-019を再生成しない。

### 7.4 Decomposition Review

Initiative Planning Reviewは全BundleとIssue Boundary Mapsを入力に、`decomposition-quality`を必須適用する。

P1例:

- Epic完了時に利用可能な能力がない。
- horizontal Issue群がend-to-end outcomeを分断する。
- current consumerのないfoundation／registryを作る。
- QA／Metrics／Dogfood／Inventoryだけの必須Issue。
- IssueがPR固定費に見合うOutcomeを持たない。
- Issueが巨大すぎてreview／rollback不能。

## 8. Skill and Wrapper Responsibility

Skill owns:

- Scope-specific Candidate shape。
- archive／Git Review mode selection。
- Semantic／Mechanical Revision lane selection。
- Human Gate and adoption decision。
- Git-first fallback justification。

Wrapper／script owns:

- exact repository／branch／HEAD binding。
- Candidate／target file attachment。
- ZIP SHA、safe extraction、manifest／checksum、parity。
- Oracle invocation and result retrieval。
- direct argv and sensitive-data exclusion。

Wrapper／Runtimeへsemantic materiality classifierを実装しない。判断不能時はSkillがSemantic laneまたはHuman clarificationへfail closedでrouteする。

## 9. Review Architecture

Formal Protocolとtemporal window:

| Protocol | Normative review range |
|---|---|
| Planning Review | 指定されたexact HEADのsnapshot。BASEを持たない。 |
| Checkpoint Review | 明示したsemantic BASE SHAからcurrent synchronized HEADまで。BASE ancestryをfail closedで検証する。 |
| Issue Delivery Review | Issue実装開始または最後に承認したIssue delivery baselineのsemantic BASEからcurrent HEADまで。 |
| Epic Delivery Review | 対象Epicの最初のincluded Issue変更前に定めたsemantic BASEから、review対象default-branch HEADまで。 |
| PR-style Review | target base branchとPR HEADのmerge-baseからPR HEADまで。 |
| Targeted Review | snapshotまたは明示BASEを使用できるがadvisoryである。 |

全delta-bounded Reviewは、BASE..HEADで特定したmutation frontierだけでなく、reviewed HEADにおけるContract Ownerの現在契約全体の充足を評価する。BASE、merge-base、ancestry、reviewed HEADを解決できない場合は`insufficient-evidence`でありPASSしない。

Planning ReviewはInitiative Bundleだけでなく、全Epic Bundles、Issue Boundary Maps、dependency、Consolidation rationaleを評価する。P0／P1はFAIL、P2／P3のみはPASS、証拠不足ではPASSしない。

## 10. `spec-dock-chatgpt` Boundary

SpecDockはlogical capability familyとして次を提供する。

```text
planning create / revise
review planning / checkpoint / delivery / targeted
execution-brief generate
repair-batch generate
```

Exact command／flag、module／file path、Prompt本文、field名はEpic Planningで確定する。

Formal callはnamed branch、clean tree、upstream、local HEAD＝remote HEAD、target、BASE ancestryをpreflightし、失敗時にGit操作しない。ChatGPTが`@GitHub`でexact repository／branch／HEADを確認できなければ継続しない。

### 10.1 Sensitive data boundary

Prompt resource、Operator Context、GitHub外file、Oracle／Human Relay package、Workbench、Candidate ZIP、Artifact、Execution Brief、Repair Batch、report evidenceへsecret、token、cookie、credential、private key、`.env`、production dump、private customer dataを含めない。必要な外部情報はHumanが明示承認した最小redacted subsetとし、preflight／fixture testで検出・拒否・redactionを検証する。

### 10.2 Process invocation boundary

Oracle、backend、helper、review、artifact processing等のprocess launchはdirect argvをdefaultとする。通常経路でshell wrapper、pipe、redirect、heredoc、command substitution、shell variable expansion、Prompt／path interpolationを使わない。direct-argv代替がなくshell semanticsが本質的に必要な例外は、Human-approved Epic Design、固定command template、untrusted input拒否／safe encoding、injection payload regression test、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。いずれかが欠ける場合はPlanning、Issue Delivery、cutover、releaseの各gateをPASSしない。

## 11. Architecture-Aware Execution Brief、Agent Topology、Repair

Agent role IDのclosed setは次である。

```text
write-capable:
- executor

read-only:
- explorer        # Codex built-in。override fileを置かない
- researcher
- consultant
- deep-consultant
```

Authority／projection path:

```text
provider authority:
src/spec_dock/assets/install_root/.codex/agents/
  executor.toml
  researcher.toml
  consultant.toml
  deep-consultant.toml

installed projection:
<install-root>/.codex/agents/（provider relative file setのexact projection）

dogfood projection:
.codex/agents/
  executor.toml
  researcher.toml
  consultant.toml
  deep-consultant.toml
```

built-in `explorer`にはprovider／installed／dogfoodのどこにも`explorer.toml`を置かない。上記以外のrole IDはmaintained official pathで禁止する。現在の`dev-coder`、`code-reviewer`、`spec-reviewer`、`qa-reviewer`、`doc-writer`、`repo-analyst`、`spark-worker`、`utility-worker`、`spec-manager`、`system-architect`その他allowlist外roleはcutover時に除去またはofficial pathから切り離す。exact-set testはmissing、extra、renamed、write-capable権限、provider／installed／dogfood差分、Issue Grade routingをすべてfailさせる。

- Issue Gradeをmodel／reasoning自動routingへ使わず、Mainが必要な委任でだけ明示overrideする。
- Execution Briefは実装前のproactive contract。
- Repair BatchはFormal blocker後のreactive contract。
- どちらもSource HEAD固定、Main adoption後freeze、Issue Artifactとして保存、上位Plan変更不可、実施結果追記なし。
- ChatGPTが関連Artifactとrepository evidenceを意味的に探索し、Codex／wrapperはdeterministic anchorsだけを提示する。

## 12. Issue Delivery and Epic Completion

### Issue default

```text
Issue Planning
→ Execution Units
→ optional Execution Brief
→ Executor
→ Checkpoint／Repair
→ Issue Delivery Review
→ dedicated PR
→ CI／ChatGPT Review／GitHub Codex Review
→ Human merge
→ reviewed HEAD確認
→ issue finish
```

### Epic default

```text
all Issue PRs merged to default branch
→ Epic Delivery Review on default branch
→ PASS: epic finish
→ P0/P1 requiring mutation: create JIT bounded Issue／PR
```

aggregate Epic PR、事前Final QA Issueをdefaultにしない。

## 13. Capability Map

| Epic | Actor Outcome | 依存 |
|---|---|---|
| ChatGPT Planning and Advisory Review | Human／MainがGoalまたはSeedからreviewed Planning Bundle、Portfolio、Node materialization、Targeted Reviewを完了できる。 | なし |
| Analysis Guided Issue Execution and Per Issue Delivery | Mainが承認済みIssue Planから実装、Review、個別PR、Human merge、Issue finishまで完了できる。 | Epic 1 |
| Multi Issue Epic Completion and Global Cutover | Main／Maintainerが複数Issue Epicをfinishし、Human mergeでvNextをcutoverし、別Issueでpost-cutover evaluation／release decision／closureを完了できる。 | Epic 2 |

## 14. Cutover、Evaluation、Release Architecture

E1／E2は各代表Workflowの終了時に、planned／unplanned Human intervention、handoff量、Agent／Skill invocation、Review result、failure cycle、wall-clock、Brief Evidence findingを発生元の`report.md`、CI／GitHub evidence、Oracle session、accepted Artifactへ記録する。

### 14.1 E3-I2 cutover activation

E3-I2はpre-cutover baseline completeness、remaining legacy removal、provider／installed／dogfood parity、existing Scope replay、known-good HEAD、rollback mechanism／trigger／drill、security closureを所有する。reviewed E3-I2 PRのHuman mergeだけがofficial global cutoverをactivateする。E3-I2 Reviewはpost-cutover evidenceを要求しない。

### 14.2 E3-I3 post-cutover evaluation and release

E3-I3はcutover後default branchから一つのdedicated branch／draft PRを作り、次を所有する。

```text
minimum duration: cutover後4週間
minimum representative runs: 5
baseline: 旧Workflow 3件以上
required task shapes: multi-module/layer, non-standard framework, API/data, CLI/build/docs, mechanical skip
persistence: E3-I3 report／Artifacts with source evidence references
```

E3-I3は週次集計でM-001〜M-016をoperationalに評価し、M-017 materialization、M-018 publication、M-019 signed Human Gate／canonical parity／implementation Evidenceのimmutable locatorとidentityを検証する。`FINAL-METRIC-PACKAGE-CONTRACT.md`に従うM-001〜M-019 complete decision packageが揃うまでfinal Review／Human merge／release／Epic finish／Initiative closureへ進まない。floor、task-shape、Evidence、release-blocking target、immutable referenceのいずれかが未達なら、継続計測、bounded follow-up、Human-approved evaluation restart／extension、rollback、またはInitiative中止へrouteする。

### 14.3 Authority event distinction

```text
E3-I2 Human merge = official cutover activation
E3-I3 Human merge = release decision package publication
Epic Delivery Review PASS = Epic finish authorization
Initiative Final Completion Summary + Human decision = Initiative closure
```
### 14.4 Signed Human Gate and complete metric package

```text
Human signed approval record
→ canonical M-019 evidence Artifact
→ M3／M4 canonical parity
→ Epic 1 implementation／dogfood evidence
→ E3-I3 immutable M-019 reference
→ Initiative Final Completion Summary
```

E3-I3 operationally evaluates M-001〜M-016. It resolves M-017 from the materialization ledger／canonical parity, M-018 from Git publication evidence, and M-019 from the canonical Human approval evidence Artifact plus implementation evidence. The final package is M-001〜M-019 and follows `FINAL-METRIC-PACKAGE-CONTRACT.md`.


## 15. Cutover and Compatibility

- vNextはdocument schema migrationではなくWorkflow／Actorのglobal cutover。
- existing Scopeは次操作からvNextへ入り、不足契約だけPlanning gapとしてrefreshする。
- provider／installed／dogfood parityを維持する。
- old 7-Epic planning structureと未承認slice候補は、新Portfolio承認後に`LEGACY-PORTFOLIO-RETIREMENT.md`のreverse-topological、no-force、stop-on-failure contractでretireする。
- Epic 1はplanning-specific legacy surfaceを所有し、Epic 3はremaining shared／execution／delivery surfaceを所有する。Epic 3はEpic 1のsurfaceをverification-onlyとして扱う。
- Candidate ZIPが承認される前に既存Nodeを削除しない。
- cutover activation、post-cutover evaluation、release decision、Epic finish、Initiative closureを一つのIssue／gateへ短絡しない。

## 16. Cross-Cutting ADR

本Initiativeは少なくとも次のDecisionを採用する。

- Outcome-Oriented Vertical Slicing and Per-Issue Merge Boundaries。
- Prompt-Embedded Slicing Contract and Decomposition Quality Review。
- Initiative Planning Orchestrates Epic Planning through Issue Boundaries。
- Immutable Candidate ZIP as Planning Review and Approval Boundary。
- Planning Workflow Capability Implementation Is Not Downstream Planning。
- Separate Official Cutover Activation from Post-Cutover Evaluation and Release Closure。
- 各Epic固有ADRはEpic Bundle内で定義する。

- ADR 20: Universal Planning Candidate、dual Review transport、dual Revision lanes。
