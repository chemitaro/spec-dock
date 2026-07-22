---
種別: ADR（Architecture Decision Record）
ID: "20260720t141001z-13-adr"
タイトル: "Immutable Candidate ZIPをPlanning Review・Human Approval・Materializationの境界として利用する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
関連:
  - "20260720t080853z-10-adr-outcome-oriented-vertical-slicing-and-per-issue-merge-boundaries"
  - "20260720t080853z-11-adr-prompt-embedded-slicing-contract-and-decomposition-quality-review"
  - "20260720t112401z-12-adr-initiative-planning-orchestrates-epic-planning-through-issue-boundaries"
authority: "accepted"
accepted_authority: "human"
accepted_at: "2026-07-20"
accepted_by: "Human"
mirror_eligible: true
derived_from:
  - "Initiative Planning candidate transport and review discussion through 2026-07-20"
  - "Oracle browser attachment and ZIP bundle capability research"
  - "Human decision: adopt the ZIP-based Planner／Reviewer／Human approval workflow"
  - "Independent Formal Review of Candidate v3: monotonic immutable version contract required"
  - "Independent Formal Review of Candidate v5: outcome-aware materialization recovery required"
reflected_to:
  - "spec-dock-initiative-planning"
  - "spec-dock/docs/workflow_planning.md"
  - "spec-dock/docs/workflow_initiative.md"
  - "spec-dock/docs/workflow_review.md"
  - "spec-dock-chatgpt planning create"
  - "spec-dock-chatgpt planning revise"
  - "spec-dock-chatgpt review planning"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260720t141001z-13-adr-immutable-candidate-zip-as-planning-review-and-approval-boundary.md"
---

# Immutable Candidate ZIPをPlanning Review・Human Approval・Materializationの境界として利用する

## 位置づけ

このADRは、Initiative Planningが生成するThin Initiative Bundle、全Candidate Epic Bundle、Issue Boundary Map、ADR、Review用資料を、Node作成前にどのように保持し、ChatGPT Planner、fresh ChatGPT Reviewer、Human、Codex Main Orchestratorの間で受け渡すかを定める。

候補文書をWorkbench上の個別file群だけで管理すると、ChatGPTへ渡すfile選択と再添付が複雑になる。一方、候補文書を承認前に正式Nodeへ配置したり、Git管理されたCandidate treeを標準化したりすると、未承認構造、temporary branch lifecycle、authority混同、Node churnを増やす。

本Decisionは、**一つのimmutable Candidate ZIPをReview対象・Human承認対象・Materialization sourceとして扱う**ことで、候補一式のidentity、integrity、受け渡し、Review、Human Gate、canonical配置を単純化する。

## ADR 化基準

- hard to reverse: yes。Initiative Planning、Oracle file attachment、Planning Review、Human Gate、Node materialization、Workbench、Git transaction、candidate authorityへ横断的に影響する。
- surprising without context: yes。Git管理されていないZIPをPlanning Reviewの正式入力にしつつ、Human承認後までcanonical authorityを成立させないため、durabilityとauthorityを分けて理解する必要がある。
- real tradeoff: yes。GitHub inline reviewとcandidate commit履歴を標準経路から外す代わりに、Codex操作量、temporary path管理、branch lifecycle、添付選択、Review対象の曖昧さを削減する。

## 結論（Decision）

### 1. Candidate ZIPを一つのreviewable unitとする

Initiative Planningのcandidate outputは、次を一つのZIPへまとめる。

```text
portfolio-candidate.zip
├── CANDIDATE.md
├── PORTFOLIO.md
├── MANIFEST.json
├── CHECKSUMS.sha256
├── initiative/
│   ├── requirement.md
│   ├── design.md
│   └── plan.md
├── epics/
│   ├── <semantic-epic-key>/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   ├── plan.md
│   │   └── artifacts/
│   └── ...
├── issue-boundary-maps/
├── artifacts/
└── reviews/
```

ZIPは次を満たす。

```text
- complete: Human Approvalに必要な全候補文書を含む
- self-describing: CANDIDATE／PORTFOLIO／MANIFESTを含む
- immutable per version: 一度Reviewへ渡したZIPは書き換えない
- content-addressed: ZIP全体のSHA-256で候補を識別する
- non-canonical: Review・Human承認前は正式仕様・Node authorityを持たない
```

### 2. WorkbenchはCandidate ZIPの保存場所とする

標準保存先はInitiative Workbenchとする。

```text
<initiative>/.workbench/initiative-planning/<run-id>/
├── portfolio-candidate-v4.zip
├── portfolio-candidate-v5.zip
├── review-vN.md
├── review-vN+1.md
└── human-review/
```

`vN`と`vN+1`は異なるimmutable fileであり、旧versionを削除・上書きしてcurrent versionへ見せかけない。

WorkbenchはGit管理されないが、候補ZIPのprimary working copy、Oracle session artifactはbackup、ZIP自体はportable snapshotとして機能する。

Candidate ZIPの内容を、Review前にcanonical Initiative／Epic／Issue pathへ展開しない。Draft Epic Node、Provisional Node、Candidate Registry、Planning DBを作らない。

### 3. PlannerとReviewerの責務を分離する

ChatGPT Plannerがcomplete Candidate ZIPを生成・改訂する。

fresh ChatGPT Reviewerは、Candidate ZIPを変更せず、findingとverdictだけを返す。

```text
Planner
→ Candidate version N（例: `candidate-v4.zip`）／MANIFEST version N／ZIP SHA N

fresh Reviewer
→ review-vN.md bound to filename／version／SHA N

P0／P1あり
→ Plannerへcandidate-vN.zip＋review-vN findings
→ Candidate version N+1（例: `candidate-v5.zip`）／new MANIFEST identity／new ZIP SHA N+1
→ fresh Reviewer
```

version Nのbytes、filename、MANIFEST identity、Review resultを上書きしない。

ReviewerがZIP内部のfileを直接修正したり、silent changeを含むrevised ZIPを返したりすることを標準にしない。Authoring authorityとReview authorityを混ぜない。

### 4. Reviewはexact ZIP SHAへbindする

各Review結果は、最低限次へbindする。

```text
- candidate ZIP filename
- candidate ZIP SHA-256
- MANIFEST SHA-256
- Review protocol
- Reviewer session reference
- verdict
- findings
```

P0／P1がある場合はFAIL。P2／P3だけならPASSし、候補文書を変更しない。

修正版は同じZIPを書き換えず、単調増加する新version、新filename、新MANIFEST identity、新しいSHAを持つcomplete Candidate ZIPとして生成する。Review／Human Approval／materializationはこのidentity tupleへbindする。

### 5. Oracle／ChatGPTへのZIP添付

既にCandidate ZIPが存在する場合、Oracle Browser ModeへそのZIPをraw attachmentとして一つだけ渡す。

```text
--file <candidate.zip>
--browser-attachments always
```

既存ZIPを`--browser-bundle-files --browser-bundle-format zip`へ再投入してnested ZIPを作らない。bundle flagsは、複数の元fileしか存在しない場合にOracle側で一つのZIPへまとめる用途へ限定する。

OracleがZIPを実attachmentとしてuploadできることと、ChatGPTがZIP内部の全fileを安定して展開・横断Reviewできることは分けて扱う。正式導入前に、path列挙、marker読取、cross-file矛盾検出、revised ZIP生成・downloadを含むlive smokeを必須とする。

exact ZIPを安全かつ完全に解析できない場合、Formal Reviewは`insufficient-evidence`で終了する。Git-tracked Candidate Packや個別file attachmentはnon-formal diagnosticにだけ利用でき、同一Formal Review identityの代替入力としてPASSを生成できない。診断後は完全な新Candidate ZIPと新SHAを生成し、fresh Formal Reviewを開始する。

### 6. Humanは展開済みfileとexact ZIP SHAを承認する

Formal Planning Review PASS後、Codex Mainはfinal Candidate ZIPをHuman Review専用Workbench directoryへ安全に展開する。

```text
<initiative>/.workbench/initiative-planning/<run-id>/human-review/<candidate-sha>/
```

Humanはbinary ZIPそのものではなく、展開済みのInitiative Bundle、Epic Bundles、Issue Boundary Maps、ADR、dependency、Review結果を確認する。

Human Approvalは次へbindする。

```text
Approved Candidate ZIP SHA-256
Approved Portfolio／Epic／Issue boundaries
Approved per-Issue PR boundaries
Approved ADR set
```

Humanが変更を求めた場合、Workbench上の展開fileを直接編集して承認しない。Human feedbackをPlannerへ渡し、新しいCandidate ZIP、fresh Review、再確認を行う。

### 7. Safe extractionを必須とする

ChatGPTまたは外部toolが生成したZIPを、無検証で展開しない。

少なくとも次を検査する。

```text
- absolute path禁止
- `..` path traversal禁止
- backslash path ambiguity禁止
- NUL path禁止
- symlink禁止
- hard link禁止
- device／FIFO／socket／その他special entry禁止
- duplicate path禁止
- case-fold collision禁止
- Unicode-normalization collision禁止
- encrypted entry禁止
- nested archive禁止
- executable payload禁止
- unexpected binary／non-UTF-8 text payload禁止
- file数上限
- expanded size上限
- per-entry／total compression ratio上限
- allowlisted extension
- CRC failure禁止
- 許容path集合を`MANIFEST.json.files ∪ MANIFEST.json.control_files`へ限定し、集合外fileを禁止
- manifestのsize／file SHA-256一致
- ZIP全体SHA-256一致
```

上記のどれかを検査できない場合も安全と推定せず`insufficient-evidence`とする。

Planning Candidateのdefault allowlistは、Markdown、JSON、YAML、text、PlantUML等のreviewable text formatとする。Candidate ZIPだけでなく、Prompt resource、Operator Context、GitHub外file、Human Relay package、Workbench、Artifact、Execution Brief、Repair Batch、report evidenceへsecret、token、cookie、credential、private key、`.env`、production dump、private customer dataを含めない。必要な情報はHuman-approved redacted subsetに限定する。Process launchはdirect argvをdefaultとし、shell例外はHuman-approved Design、固定template、input validation／encoding、injection regression evidence、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。欠落時はReview／Approval／release gateをPASSしない。

### 8. Human承認後にのみNodeをmaterializeする

Humanがexact Candidate ZIP SHAを承認した後、Main OrchestratorはRuntimeのsupported commandでEpic／Issue Nodeとdependencyを作成する。

```text
Human approves exact ZIP SHA
→ Runtime creates Epic／Issue Nodes
→ candidate semantic keyとNode ID／pathをbinding
→ approved ZIPをsafe extract
→ canonical pathへcopy
→ approved binding placeholderだけ置換
→ validate／sync
→ candidate-to-canonical parity確認
→ commit／push
```

手動directory作成、`.meta.json`手書き、承認前GitHub Issue作成、Draft Node typeの追加は行わない。

### 9. 許可するmaterialization時変換を限定する

Candidate Bundleの意味内容をMainやCodexが再執筆しない。

許可されるのは、Candidate生成時に明示されたbinding placeholderの決定的置換だけとする。以下のtokenはこのstatic ADR内ではsyntaxのliteral examplesであり、dynamic render対象ではない。実際のdynamic targetは`PLACEHOLDER-ORACLE-MAP.json`だけが列挙する。

```text
{{INITIATIVE_ID}}
{{INITIATIVE_PATH}}
{{EPIC_ID}}
{{EPIC_PATH}}
{{ISSUE_ID}}
{{ISSUE_PATH}}
```

placeholder置換後のexpected fileとcanonical fileをbyte-levelまたはnormalized text-levelで比較する。binding以外の差分がある場合はmaterializationを完了しない。

### 10. Gitはcanonical publication boundaryとする

Candidate ZIP自体を標準経路でGit管理しない。

Human承認後のNode作成、canonical file配置、dependency登録、validate、sync、parity確認がすべて成功した場合だけ、Mainが一つの明示的commitを作成してpushする。

```text
Candidate ZIP:
Review／Approval boundary

Canonical materialization commit:
repository publication boundary
```

Candidate ZIPをdefault branchへmergeしない。

### 11. 代替file setはnon-formal diagnosticに限定する

Git-tracked Candidate Packや個別file attachmentは、ZIP transport／inspection failureの診断、Human inline comment、長期非同期collaborationに利用できる。ただし、exact ZIPと同一のFormal Review identityを持たず、Formal PASSやHuman ZIP-SHA Approvalを生成できない。

診断結果を反映した完全な新Candidate ZIPを生成し、外部SHAを確定してからfresh Formal Reviewへ戻る。Git-tracked candidateを正式Node、approved ZIP、canonical authorityとみなさない。

### 12. Materialization完了までCandidate ZIPを保持する

次がすべて成功するまで、承認済みCandidate ZIPをWorkbenchから削除しない。

```text
- Epic／Issue Node作成
- dependency登録
- binding placeholder置換
- canonical file配置
- validate／sync
- candidate-to-canonical parity
- commit／push
```

成功後はWorkbenchから削除できる。最終証跡はcanonical文書、Node metadata、Git commit、verified remote ref、GitHub Issue／dependency、Oracle session、Review result、Candidate-SHA-bound Workbench ledger、`report.md`のpre-commit materialization dispositionに残る。

## 背景（Context）

Initiative PlanningはThin Initiative Bundleだけでなく、全Epic Bundle、Issue Boundary Map、ADR、dependency、Consolidation Reviewを生成する。これらはHuman承認前には正式Nodeを持たないが、ChatGPT PlannerとReviewerが完全なPortfolioを横断的に扱い、Humanが具体的なEpic／Issue境界を確認する必要がある。

Workbench上の個別file群はGitHub Connectorから参照できず、毎回Codexが添付対象を選ぶと、希少なCodex token、tool call、contextを消費する。全fileを一つのZIPへまとめれば、Planner／Reviewer／Human／Materializerの受け渡しを一つのimmutable unitへ集約できる。

一方、候補文書をGit管理する方式はReviewabilityに優れるが、temporary branch、candidate path、commit、cleanup、authority説明が増える。候補Nodeを先に作る方式は、過剰分割や不採用構造を正式repository modelへ固定する。

ZIP-first方式は、Candidate identityをSHAで固定し、ReviewとHuman Approvalを同じbyte列へbindし、承認後だけ正式Nodeへmaterializeできる。

## 選択肢（Options considered）

### Option A — Workbench個別file群＋毎回添付

- repositoryを汚さない。
- 添付選択、版管理、添付漏れ、複数session handoffが複雑。
- 棄却。

### Option B — Git-tracked Candidate Packを標準とする

- ChatGPT／Human／GitHub diffに強い。
- branch lifecycle、candidate commit、cleanup、authority説明、Codex操作量が増える。
- non-formal diagnosticへ限定し、Formal Reviewには使用しない。

### Option C — 承認前にEpic／Issue Nodeを作る

- 最終pathでReviewできる。
- 未承認分割、Node churn、ID churn、Draft stateを製品化する。
- 棄却。

### Option D — Candidate BundleをInitiative Artifactへ保存する

- Git管理可能。
- materialization後に候補三文書とcanonical文書が重複し、authorityが曖昧。
- 棄却。

### Option E — Immutable Candidate ZIPをWorkbenchで受け渡す

- Planner／Reviewer／Human／Materializerが同じ一fileとSHAを扱える。
- Git candidate lifecycleが不要。
- safe extractionとZIP解析smokeが必要。
- 採用。

## 判断理由（Rationale）

1. 一つのZIPとSHAにより、Review対象とHuman承認対象を明確に固定できる。
2. Codexが関連fileを意味的に選択・要約する必要がない。
3. Candidateを正式Nodeやcanonical pathへ早期昇格させずに済む。
4. PlannerとReviewerの責務分離を維持できる。
5. Revisionはcomplete ZIP regenerationとなり、partial patchやsilent changeを防げる。
6. Humanは展開済みfileを直接確認でき、binaryだけを承認する必要がない。
7. Node creationとcanonical placementをHuman承認後へ遅延できる。
8. Git commitを正式publication boundaryとして維持できる。
9. Git-tracked candidateはdiagnostic／collaboration surfaceとして残せるが、Formal Review identityを持たない。
10. 新しいCandidate DB、Draft Node、Registry、Importerを作らずに実現できる。

## 影響（Consequences）

### Positive

- Planner／Reviewer間の受け渡しが一fileになる。
- Review対象の版をSHAで固定できる。
- Codexのfile selection、packing、semantic summary負荷を減らせる。
- Human Approvalとmaterialization sourceを一致させられる。
- 未承認Epic／Issueを正式Nodeへ作らずに済む。
- candidate branch／directory cleanupを標準経路から除去できる。
- Review FAIL時は、findingと元ZIPだけで完全Revisionを依頼できる。

### Negative／Cost

- ChatGPTがZIPを安定して展開・横断Review・再生成できるかlive smokeが必要。
- Human確認前に安全なZIP展開処理が必要。
- GitHub inline diff／commentを標準で利用できない。
- Candidate ZIPのsize、file数、expanded sizeを管理する必要がある。
- long-running／multi-human reviewではGit-tracked diagnostic surfaceを利用できるが、承認対象には新しいexact ZIPが必要になる。
- SHA、manifest、review result、Human approvalのbindingを明示する運用が必要になる。

### Non-circular integrity contract

- `MANIFEST.json.files[]`はpayload fileをpath、size、SHA-256付きで宣言する。
- `MANIFEST.json.control_files[]`は`MANIFEST.json`と`CHECKSUMS.sha256`だけを宣言する。
- ZIP entry集合は`files ∪ control_files`と完全一致しなければならない。
- `CHECKSUMS.sha256`は全payload fileと`MANIFEST.json`をhashする。循環を避けるため`CHECKSUMS.sha256`自身だけをself-hash-exemptとする。
- 外部のZIP SHA-256が`CHECKSUMS.sha256`自身を含むZIP全体をbindする。

### Risks and mitigations

- Risk: ChatGPTがZIP内の一部fileを読まない。
  - Mitigation: MANIFEST、marker smoke、path inventory、Evidence Used、Review completeness check。
- Risk: Reviewerが直接修正してsilent changeを入れる。
  - Mitigation: Reviewerはfindingのみ、Plannerがcomplete ZIPを再生成。
- Risk: Humanが展開fileを直接編集する。
  - Mitigation: feedbackをPlannerへ戻し、新ZIP＋fresh Review。
- Risk: zip-slip／zip bomb。
  - Mitigation: strict safe extraction、allowlist、size／ratio上限、manifest verification。
- Risk: Candidate ZIP消失。
  - Mitigation: Workbench primary、Oracle session backup、portable ZIP、materialization完了まで保持。
- Risk: Human承認後に別ZIPをmaterializeする。
  - Mitigation: exact SHA approval、pre-materialization SHA verification、parity check。
- Risk: binding substitutionが意味内容を変える。
  - Mitigation: placeholder allowlist、expected-final hash／diff verification。

## 運用上の必須変更

- `spec-dock-initiative-planning`へCandidate ZIP生成、versioning、Review loop、Human approval、materialization handoffを追加する。
- `workflow_planning.md`へCandidate ZIP contract、Planner／Reviewer責務、P0／P1 revision loopを追加する。
- `workflow_initiative.md`へHuman Approval by ZIP SHA、safe extraction、Node materializationを追加する。
- `workflow_review.md`へZIP-bound Review result、Reviewer non-mutation、fresh Reviewを追加する。
- Oracle ZIP attachment／downloadのlive smokeを実装前gateにする。
- Mainにsafe extraction、manifest／checksum verification、binding parity verificationを要求する。
- `report.md`へapproved Candidate SHA、Review result、pre-commit materialization dispositionを短く記録する。observed commit／push／remote HEADはGit object、remote ref、Candidate-SHA-bound Workbench ledgerをauthorityとし、同materializationでreportを二度変更しない。

## 検証シナリオ

1. Candidate ZIPをOracleへ一fileとしてuploadし、全pathとmarkerをChatGPTが正しく列挙する。
2. ChatGPTが複数Epic文書を横断して矛盾と過剰分割を検出する。
3. Reviewerはfindingのみ返し、ZIP内部fileを変更しない。
4. Plannerがfindingを受けてcomplete v2 ZIPを生成し、v1と異なるSHAを持つ。
5. P2／P3だけのReviewではZIPを変更せずHuman Gateへ進む。
6. Human Review用safe extractionがpath traversal、symlink、duplicate path、zip bombを拒否する。
7. Humanが承認したSHA以外のZIPをmaterializeしようとすると停止する。
8. RuntimeがNodeを作成し、placeholderだけを置換し、candidate-to-canonical parityがPASSする。
9. canonical commit／push成功前にCandidate ZIPが削除されない。
10. ZIP解析smokeがFAILした場合、Formal Reviewは`insufficient-evidence`となり、non-formal diagnostic後に新しい完全ZIPとfresh Reviewへ戻る。

## 参照（References）

- ADR 10: Outcome-Oriented Vertical Slicing and Per-Issue Merge Boundaries。
- ADR 11: Prompt-Embedded Slicing Contract and Decomposition Quality Review。
- ADR 12: Initiative PlanningでEpic PlanningをオーケストレーションしIssue境界まで確定する。
- Oracle: browser attachment、ZIP bundle、browser session artifact機能。
- Local `chatgpt-use`: long prompt／複数fileを`--file`で添付し、fresh modelへstandalone contextを渡す運用。


## Canonical replacement clarification

Human approval of an exact Candidate ZIP authorizes only the baseline-bound transition defined by ADR 15. Existing canonical file differences are not silently overwritten: source Git blobs and path ownership must match the reviewed baseline, verified backups and replacement staging must exist before destructive mutation, and partial replacement must resume or rollback through the canonical replacement ledger.
