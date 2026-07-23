---
種別: disc
ID: "20260723t084459z-disc-issue-planning-current-effective-decisions"
タイトル: "iss-00334 ChatGPT Issue Planning Workflow — Current Effective Decision Snapshot"
状態: "current"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-23"
親: ["iss-00334", "epic-00331", "init-00322"]
scope: "issue"
scope_id: "iss-00334"
authority: "user-approved-clarification-synthesis"
adoption_status: "candidate-for-canonical-authoring"
canonical_status: "non-authoritative"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "347c2f79086730ccd7af99ba836d0c1b758f4a95"
derived_from:
  - "20260723t084457z-research-issue-planning-workflow-gap-analysis.md"
  - "20260723t084458z-interview-issue-planning-clarification-decisions.md"
  - "init-00322 accepted ADR 02, 03, 08, 20, 21, 22"
  - "epic-00331 Requirement／Design／Plan and walking-skeleton ADR"
reflected_to: []
---

# 20260723t084459z-disc-issue-planning-current-effective-decisions

## 位置づけ

- このArtifactは、`iss-00334`について現在有効なIssue-local判断を統合したDiscussion Snapshotである。
- sourceから確定した上位契約、Humanが回答した意思決定、通常の技術判断としてsource-groundedに導いた方針を一つの現在形へ整理する。
- 過去の選択肢や途中案を運用規則として併記せず、現在採用する意味を記録する。
- 本文はCandidate authoringの入力であり、canonical Requirement／Design／Plan、accepted ADR、fresh Review PASS、`execution-ready`を代替しない。
- 将来materialな判断が変わる場合は、対応するInterview／Discussion／ADR candidateを追加し、正本Candidateで整合させる。

## authority precedence

判断が衝突する場合の優先順位は次とする。

```text
accepted Initiative ADR / canonical Initiative docs
→ canonical Parent Epic docs / accepted Epic ADR
→ explicit Human answer in this clarification
→ source-grounded Issue-local technical decision
→ non-authoritative research inference
```

- 上位契約をIssue-local convenienceで短縮しない。
- source-grounded technical decisionがHuman intentを推測して変更しない。
- Artifact front matterの自己申告だけでproduct authorityを成立させない。

## Current Effective Decision Set

### I334-D-001 Outcome

E1-I1は、既存Issue Nodeまたはapproved Seedに対応するIssueを入力として、complete Issue Planning BundleをJIT生成し、Formal Review、Human authorization、deterministic adoption／parity、validation、Planning publicationを完了した後だけ実装開始へhandoffできる再利用可能Workflowを実装する。

このIssueの主成果はWorkflow capability、tests、docs、provider／installed／dogfood projectionであり、今回のPlanning run自体ではない。

### I334-D-002 Mandatory non-goals

Requirement／Design／Planの全てで次を明示する。

1. Current Portfolio replanningを行わない。
2. 後続IssueのRequirement／Design／Planを先行作成しない。
3. Human approvalやmerge判断を自動化・代行・迂回しない。
4. Planning文書またはPlanning runだけでIssueを完了しない。

### I334-D-003 Official Human interface

`spec-dock-issue-planning` Skillをofficial Human interfaceとする。

Skillが所有するもの:

- Issue／parent／authority確認
- Review mode選択
- Revision lane選択
- Humanへの質問
- Human Gate
- semantic判断
- CLI operation順序
- Review結果の意味的採否

### I334-D-004 First-class deterministic CLI

`spec-dock-chatgpt`をsupported first-class CLIとし、Core `spec-dock` CLIから分離する。

Issue Planning walking skeletonで提供するChatGPT-facing operation:

```text
spec-dock-chatgpt planning create <target>
spec-dock-chatgpt planning revise <target>
spec-dock-chatgpt review planning <target>
```

CLIはHuman Gateを越えるone-shot orchestration、semantic materiality判定、canonical mutation、commit、push、mergeを所有しない。

### I334-D-005 Actor responsibility

| Actor／Component | Responsibility |
|---|---|
| Human | Plan adoption、implementation-start authorization、merge、materialな例外承認 |
| Planning Skill | Workflow、mode、lane、Human Gate、semantic decision |
| Codex Main | result採否、filesystem mutation、Git transaction、phase orchestration |
| `spec-dock-chatgpt` | target／Git binding、Prompt、Oracle invocation、result retrieval |
| Core Runtime／script | ZIP safety、identity、approval validation、adoption、parity、validation、publication verification、derived readiness |
| Oracle | browser、login、model picker、session、reattach、response／artifact保存 |
| ChatGPT Planner | complete Bundle generation、self-review、Semantic Revision |
| ChatGPT Reviewer | review-only Formal Planning Review |

### I334-D-006 Prompt resource architecture

Prompt本文をPython sourceへ長文埋込みしない。

provider-managed closed resource set:

```text
prompt-set manifest
+ operation-specific Markdown
+ ordered shared Markdown fragments
→ deterministic rendered Prompt
```

manifestに置く情報:

- operation identifier
- ordered fragment names
- required input keys
- operation-specific resource
- output contract kind
- schema version

禁止:

- public custom template override
- raw prompt override
- recursive include
- arbitrary conditional／loop／expression evaluation
- environment variable expansion
- operator-controlled resource path

Operator固有情報は`--context`、`--context-file`、`--file`だけから追加する。

### I334-D-007 Prompt identity

各invocationで次を追跡する。

- prompt-set schema version
- operation resource path／SHA
- ordered fragment path／SHA
- normalized structured input digest
- rendered Prompt SHA-256
- source repository／branch／HEAD

resource検証、required input、placeholder、UTF-8、sensitive-data preflightのいずれかが失敗した場合、Oracleを起動しない。

### I334-D-008 Exact Git／GitHub preflight

Formal ChatGPT operation前に次を機械確認する。

- named branch
- clean working tree
- upstream existence
- local HEAD == remote HEAD
- exact repository
- exact target Scope
- source HEAD

自動commit、push、stash、force bypass、default branch fallback、tracked file自動添付を行わない。

### I334-D-009 Dual Review transports

二つを正式支援する。

#### archive-candidate

- pre-canonical semantic iterationのdefault
- exact immutable ZIP
- logical filename、version、internal root、Candidate ID、source binding、external ZIP SHAへbind

#### git-bound

- actual path、CI、GitHub inline review等がmaterialに必要な場合のformal fallback
- target Scopeのcanonical directory／filenameへcomplete Bundleを配置
- candidate Planning commitをpush
- exact repository／branch／reviewed HEAD／target pathsへbind

silent fallbackを行わない。

### I334-D-010 Issue Candidate package

default packageは単一rootの次の最小構成とする。

```text
requirement.md
design.md
plan.md
SOURCE-BASELINE.json
MANIFEST.json
CHECKSUMS.sha256
```

formal Candidateへ含めないもの:

- `report.md`
- `.meta.json`
- `.assurance.json`
- raw transcript
- Oracle log
- executable／binary
- nested archive
- secret／credential／private data

追加fileはoutput contractとMANIFESTでclosedに宣言されたUTF-8 textだけを許可する。

### I334-D-011 Candidate identity

Candidate identity:

```text
candidate version
logical archive filename
internal root
MANIFEST candidate ID
external ZIP SHA-256
source repository / branch / HEAD
```

versionは単調増加する。旧versionを上書きしない。

observed transport filenameはidentity本体ではなくmetadataとし、`<logical-stem>(<positive integer>).zip`だけをclosed aliasとして許可する。

### I334-D-012 Candidate safe review

exact ZIPについて次をfail closedで検査する。

- absolute／`..`／backslash ambiguity／NUL path
- symlink／hardlink／device／FIFO／socket／special entry
- duplicate／case-fold／Unicode normalization collision
- encrypted entry／nested archive
- executable／unexpected binary／non-UTF-8
- file count／expanded size／compression ratio
- CRC
- MANIFEST files／control_filesとentry集合の完全一致
- size／SHA一致
- CHECKSUMS self-hash exemption contract
- external ZIP SHA

完全検査できない場合は`insufficient-evidence`とし、個別fileや再構成treeからFormal PASSを生成しない。

### I334-D-013 Dual Revision lanes

#### Semantic Revision

Requirement、Architecture、scope、dependency、authority、Acceptance Criteria、Gate、Workflow等の意味変更。ChatGPT Blue Teamがcomplete new Candidateを生成する。

#### Mechanical Revision

path、field、old value、new value、meaning invariant、diff budgetを編集前に列挙できるclosed change。Main／deterministic scriptが実行できる。

どちらでもCandidate bytes変更はnew version／filename／root／MANIFEST／SHAとfresh independent Reviewを必要とする。

### I334-D-014 Planning Review output

Oracle session内に次を生成する。

```text
review-result.json
review-result.md
```

- JSON: protocol-specific structured result、identity、perspectives、verdict、P0〜P3 findings、insufficient-evidence
- Markdown: Human-readable rendering

Runtimeはidentity／schema shape／hashのみ検証し、findingの意味やverdictをsemantic parseしない。Main／Skillが解釈する。

fresh Reviewへ前回finding、Authorの自己弁護、期待verdictを渡さない。

### I334-D-015 Human Issue Plan Authorization

official entrypointはSkill対話とする。

```text
Skillがexact reviewed identityを提示
→ HumanがPlan adoptionとimplementation-start authorizationを明示
→ Mainが構造化source recordへcapture
→ source record SHAを計算
→ Runtimeがschema／identity／hashを検証
→ canonical approval evidenceをclosed render
```

Runtimeへ自然言語approval classifierを実装しない。

### I334-D-016 Approval evidence

#### Workbench source record

machine-readable JSONとして一時保存し、SHA-256をauthority referenceとする。

含む情報:

- schema version
- Issue ID
- Review mode
- exact reviewed identity
- source identity
- displayed approval question digest
- normalized Human answer
- Plan adoption boolean
- implementation-start authorization boolean
- approver
- timestamp

#### Canonical evidence

Issue `artifacts/`へtyped Markdownとしてclosed renderする。

- source record SHA
- exact reviewed identity
- authorization scope
- approver／time
- logical／transport filenameまたはreviewed HEAD／target paths

raw conversation全文は保存しない。

### I334-D-017 Archive positive gate

```text
fresh Review PASS on exact Candidate identity
→ same identityへのHuman authorization
→ deterministic canonical adoption
→ candidate-to-canonical parity
→ required validation
→ Planning publication
→ execution-ready
```

Candidate三文書はbyte-exactをdefaultとする。dynamic bindingは`PLACEHOLDER-ORACLE-MAP.json`でclosedに宣言されたfile／tokenだけを許可する。

### I334-D-018 Git-bound positive gate

```text
complete Bundleをcanonical pathsへ配置
→ candidate Planning commit / push
→ exact reviewed HEAD / target pathsをfresh Review
→ same identityへのHuman authorization
→ approval evidence-only publication commit
→ exact reviewed-content canonical / commit parity
→ required validation
→ remote publication verification
→ execution-ready
```

`reviewed_head`と`publication_head`を分離する。

publication gate:

- publication HEAD parent == reviewed HEAD
- exact target blobsはreviewed HEADと同一
- approval evidence以外のdiffなし
- local publication HEAD == remote branch HEAD

### I334-D-019 Candidate-external diff

許可するCandidate-external publication changeはclosed allowlistのみ。

- Human authorization canonical evidence
- Candidate／Review identityへのdeterministic reference
- publication verificationに必要なfixed metadata

禁止:

- three-document semantic mutation
- unrelated source／test／config／docs変更
- `.assurance.json` mutation
- free-form report mutation
- formatterによるCandidate本文変更

### I334-D-020 Planning publication

```text
canonical three-document Bundle
+ canonical Human authorization evidence
+ dedicated Planning commit
+ named Issue branchへのpush
+ local publication commit == remote branch HEAD
+ canonical bytes == commit tree bytes
```

Planning専用PRは作らない。同じIssue branchでimplementationを続け、one Delivery PRをHumanがmergeする。

### I334-D-021 Derived readiness

新しいpersistent `execution-ready` flag、Planning state DB、accepted HEAD registry、custom Git refを作らない。

Core RuntimeへvNext Planning Adoption readiness verifierを追加し、次を入力として都度導出する。

- Review identity evidence
- Human authorization evidence
- parity evidence
- validation result
- publication local／remote identity

結果:

```text
ready
blocked
stale
insufficient-evidence
```

E1-I1では新Skillがこのverifierを利用する。legacy report-based guidanceのphysical removalはE1-I3へ委譲する。

### I334-D-022 `.assurance.json` boundary

E1-I1は`.assurance.json`をCandidateへ含めず、自動変更せず、readiness markerとして使用しない。

existing valid assuranceがrequired validationに必要な場合は観測する。automatic Standard fallbackを行わない。

### I334-D-023 `report.md` boundary

`report.md`をPlanning receipt、Human approval primary record、Review result authority、Candidate identity store、publication store、readiness flagとして使用しない。

Issue完了時に主要Evidence referenceとFinal Completion Summaryを記録する。legacy report gateはE1-I3 cutoverまで互換面として残す。

### I334-D-024 Source drift

次の各時点でsource bindingを再検証する。

1. Prompt生成前
2. Candidate受領時
3. Formal Review前
4. Human authorization提示前
5. canonical adoption直前
6. Planning publication直前

source HEAD／reviewed HEADが変化した場合、old Candidate／Review／approvalをstaleとし、new Candidateまたはfresh Git-bound Reviewへ戻る。自動rebase、silent refresh、old PASS継承を行わない。

### I334-D-025 Canonical adoption transaction

archive adoption:

```text
destination preflight
→ existing bytes capture
→ full Candidate staging
→ all-file validation
→ requirement atomic replace
→ design atomic replace
→ plan atomic replace
→ final parity
```

verified source backupとpath ownershipを証明できる場合だけ自動rollbackする。証明不能時はEvidenceを保持してblockedとし、Human-approved recoveryへrouteする。

### I334-D-026 Failure／retry／Human Relay

failure classを区別する。

- transient timeout／transport: bounded retry
- recoverable Oracle session: reattach
- browser／login: operator repair後にsame request
- artifact download: Oracle session artifactから再取得
- access denial／unknown: retryしない
- malformed Candidate: rejected
- stale Candidate: new Candidate
- Human rejection: feedback付きnew Candidate
- GitHub exact HEAD確認不能: blocked／information_insufficient
- Oracle UI failure: same Prompt／Context／Result contractでHuman Relay

manual Planningへ自動fallbackしない。

### I334-D-027 PA-NF-01〜PA-NF-10

Issue-local Requirement／Design／Plan／Acceptance Criteriaへ10 IDと意味を省略せず記載する。

| ID | Required rejection |
|---|---|
| PA-NF-01 | archive Review PASS only |
| PA-NF-02 | git-bound Review PASS only |
| PA-NF-03 | Human Gate only |
| PA-NF-04 | parity only |
| PA-NF-05 | wrong logical filename／Candidate SHA |
| PA-NF-06 | wrong reviewed HEAD／exact target paths |
| PA-NF-07 | source drift |
| PA-NF-08 | semantic mutation during adoption |
| PA-NF-09 | parity failure |
| PA-NF-10 | validation／Planning publication failure |

E1-I1 producer acceptanceは10／10 PASS、violations 0を必要とする。

### I334-D-028 Provider／installed／dogfood

provider authority:

- Skill: `src/spec_dock/assets/install_root/.agents/skills/`
- CLI／Runtime／Prompt resources: `src/spec_dock/assets/spec_dock/scripts/`
- docs: `src/spec_dock/assets/spec_dock/docs/`

実装順:

```text
provider
→ unit / CLI tests
→ wheel / sdist
→ fresh init
→ update
→ dogfood projection
→ byte / inventory parity
```

### I334-D-029 Additive migration

E1-I1はreplacement capabilityを追加する。

残すもの:

- `spec-dock-chatgpt-authoring`
- manual Planning Skills
- old authoring commands
- local planning reviewer assets
- legacy docs

E1-I3がreal-use evidence確認後にplanning-specific legacy surfaceをretireする。

### I334-D-030 Real Issue dogfood

eligible criteriaを今固定し、exact Issueはfeature-complete直前に最新repositoryからJIT選定する。

条件:

- openな実Issue
- 既存Issue Nodeまたはapproved Seedへbind可能
- E1-I1／I2／I3 dependency chain外
- current Portfolio replanning不要
- vNext Planning refreshが必要
- bounded／rollback可能
- dogfood publicationが他作業を妨げない

Mainが候補を提示し、Humanがexact targetを選ぶ。dogfood専用Issueを新設しない。

### I334-D-031 Dogfood mode／Evidence

Skillがmaterial reasonに基づきReview modeを選択する。defaultはarchive、actual Git stateが必要な場合だけgit-boundとする。

Issue Artifactへ次を記録する。

- target Issue
- source／reviewed／publication identity
- Review mode／Revision lane
- Human intervention planned／unplanned
- Main handoff size
- Agent／Skill／CLI invocation count
- Review result
- failure cycle
- wall-clock
- Oracle session reference
- Candidate／Review／publication SHA
- PA-NF summary

### I334-D-032 Delivery boundary

```text
one Issue
→ one named branch
→ Planning publication commit
→ implementation / repair commits
→ one Delivery PR
→ required Review
→ Human merge
→ reviewed merged HEAD確認
→ Issue finish
```

Planning専用PR、自動merge、merge前finishを行わない。

### I334-D-033 Clarification artifact workflow

- source-grounded fact／gapは`research`
- Humanへ質問し回答済みの重要判断は`interview`
- 複数判断のcurrent-effective synthesisは`disc`
- hard-to-reverse、surprising、real trade-offの三条件を満たす新判断だけ`adr` candidateへroute
- canonical R／D／Pは明示許可後のCandidateで作成

## Terminology／Ubiquitous Language

| Term | Meaning |
|---|---|
| Planning Candidate | canonical adoption前のimmutable complete Planning Bundle package |
| archive-candidate | exact ZIP SHAへbindしたFormal Planning Review transport |
| git-bound | exact repository／branch／HEAD／target pathsへbindしたFormal Review transport |
| Semantic Revision | Requirement／Architecture／Scope等の意味変更を伴うcomplete Candidate replacement |
| Mechanical Revision | closed path／field／literal／meaning invariant／diff budgetを持つdeterministic change |
| reviewed identity | Formal Reviewが評価したexact Candidate tupleまたはGit HEAD／target paths |
| Human Issue Plan Authorization | Plan adoptionとimplementation-start authorizationを同じreviewed identityへbindするHuman decision |
| reviewed HEAD | git-bound Formal Reviewが評価したcommit |
| publication HEAD | approval evidenceを追加しremote verificationされたPlanning publication commit |
| Planning publication | canonical Bundle＋approval evidenceをcommit／pushしremote identityを検証するphase |
| readiness verifier | vNext positive gateをEvidenceから都度導出するdeterministic Runtime operation |
| Candidate-external diff | Candidate payload外でpublication時に発生するclosed allowlisted change |
| Human Relay | Oracle UI failure時も同じPrompt／Context／Result contractを維持するmanual transport |

## Decision provenance

| Decision group | Source |
|---|---|
| dual transports／lanes／positive gate／Candidate identity | Initiative accepted ADR 20〜22 |
| Skill／CLI／Oracle boundary | Initiative accepted ADR 03＋Human Decision 1／2 |
| minimal persistent state | Initiative accepted ADR 08 |
| Human authorization entrypoint | Human Decision 3 |
| Planning publication | Human Decision 4 |
| Prompt closed fragments | Human Decision 1／6 |
| dogfood target late binding | Human Decision 7 |
| implementation details in D-007, D-010, D-014, D-016, D-021等 | source-grounded Issue-local technical decisions |

## 未検証事項

次は実装設計時にrepositoryで確認する事実であり、現時点でHuman質問を必要としない。

- exact Python entrypoint／module names
- Core Runtime public command names
- Prompt package resource path／package-data config
- Candidate／Review／approval schema field names
- validation command composition
- fake remote publication test harness
- artifact filename parser integration
- compatibility wrapper inventory
- feature-complete時点のeligible dogfood Issue一覧

## deferred／後続Issue

### E1-I2

- Initiative／Epic Portfolio Planning orchestration
- child Node／dependency materialization
- legacy Portfolio retirement
- destructive migration recovery

### E1-I3

- Targeted Review
- planning-specific official route cutover
- `spec-dock-chatgpt-authoring`／manual Planning／local reviewer removal
- legacy docs／Skill cleanup

### Epic 2／3

- Issue execution
- Execution Brief
- Repair Batch
- per-Issue PR Delivery
- Epic completion
- global cutover／release

## Human Gate remaining

### 必須

1. feature-complete直前のexact dogfood Issue選定
2. dogfood Issueのexact reviewed identityへのHuman authorization
3. clarification完了後のCandidate ZIP生成許可

### 条件付き

- shell exception
- byte-exact rollback不能
- Seedに対応するIssue Node新設
- E1-I1外のlegacy removal
- parent contract変更

## ADR triage

現時点でIssue-localな新ADRは作らない。

理由:

-主要な不可逆判断はInitiative accepted ADR 02, 03, 08, 20, 21, 22で既に固定されている。
- Human回答はそのIssue-local具体化であり、別の長期architecture decisionを新設していない。
- Prompt closed fragment composition等は、第二consumerで共通化境界を検証するwalking-skeleton implementation detailである。

実装調査で上位契約を変更するmaterial trade-offが判明した場合だけADR candidateへrouteする。

## Candidate authoringへの反映

### Requirement

- D-001〜D-005
- D-008〜D-013
- D-015〜D-020
- D-021〜D-024
- D-027〜D-032

### Design

- 全Actor responsibility
- Prompt／Candidate／Review／approval／publication／readiness architecture
- transaction／retry／rollback
- provider／installed／dogfood
- migration boundary

### Plan

- vertical walking skeleton tranche
- unit／CLI／integration／projection／dogfood tests
- PA-NF-01〜PA-NF-10
- publication／fake remote
- late-bound dogfood Human Gate
- one Delivery PR

## 次の作業

```text
current implementation inventory
→ component / command map
→ schema candidates
→ detailed test matrix
→ file-impact map
→ unresolved assumption check
→ clarification completion report
→ HumanへCandidate ZIP生成許可を一問だけ確認
```
