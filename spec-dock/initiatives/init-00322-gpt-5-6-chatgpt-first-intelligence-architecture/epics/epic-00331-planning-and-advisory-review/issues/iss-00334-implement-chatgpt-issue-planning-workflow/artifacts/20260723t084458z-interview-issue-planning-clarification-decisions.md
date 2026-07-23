---
種別: interview
ID: "20260723t084458z-interview-issue-planning-clarification-decisions"
タイトル: "iss-00334 Issue Planning Workflow Clarification — 回答済み意思決定"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-23"
親: ["iss-00334", "epic-00331", "init-00322"]
scope: "issue"
scope_id: "iss-00334"
created_at: "2026-07-23T08:44:58Z"
created_by: "GPT-5.6 Pro"
status: "answered"
authority: "user-approved-interview-evidence"
adoption_status: "adopted-for-candidate-authoring"
canonical_status: "non-authoritative"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "347c2f79086730ccd7af99ba836d0c1b758f4a95"
derived_from:
  - "ChatGPTで実施したGrill Me／Grill with Docs形式のIssue-local clarification"
  - "init-00322 current-effective decisions and accepted ADR"
  - "epic-00331 Requirement／Design／Plan"
reflected_to: []
---

# 20260723t084458z-interview-issue-planning-clarification-decisions

## 位置づけ

- このArtifactは、`iss-00334`の仕様具体化でHumanへ提示し、回答済みとなった重要判断を、現在有効な状態へ正規化したInterview recordである。
- 本文はraw conversationや逐次ログではなく、質問、比較した選択肢、推奨、Human回答、採用した意味、仕様への含意を説明可能な形で残す。
- `authority: user-approved-interview-evidence`は、Humanがこのclarificationで意思決定した事実を示す。canonical Requirement／Design／Plan、reviewer pass、`execution-ready`を自己宣言しない。
- parent Initiative／Epicで既に承認済みの判断は、Issue-localで再質問せず継承する。

## Interviewの進行原則

Humanから次の進行原則が明示された。

1. repository、code、tests、docsから確認できる事実は質問しない。
2. parent Initiative／Epic／accepted ADRで確定した判断を再質問しない。
3. 未確定でも、通常の技術判断で合理的に決められるものはMain／Analystが決定する。
4. Requirement、Design、Plan、Scope、Acceptance Criteria、Human Gate等を変えるHuman value judgmentだけを一問ずつ質問する。
5. 質問が袋小路化しないよう、未確定事項を「Human判断が必要／不要」に分類する。
6. interview回答、research、decision synthesisをIssue-local Artifactとして逐次保存する。
7. canonical三文書とCandidate ZIPは、clarification完了後の明示許可まで生成しない。

## source-grounded context

### 確認済み上位契約

- `spec-dock-issue-planning`を公開Human interfaceとして維持する。
- `spec-dock-chatgpt`をCore CLIから分離したthin Oracle adapterとする。
- Planning Candidateは`archive-candidate`と`git-bound`を正式支援する。
- SkillがReview mode、Revision lane、Human Gate、semantic判断を所有する。
- script／wrapperはidentity、source binding、safe extraction、hash、parity、Oracle invocation等の決定的処理だけを所有する。
- Review PASS、Human Gate、parity、validation、Planning publicationの論理積だけがIssue execution startを許可する。
- `PA-NF-01`〜`PA-NF-10`をlocal normative fixtureとして実装する。
- 新しいsemantic state DBやaccepted HEAD registryを作らない。
- provider／installed／dogfood parity、sensitive-data exclusion、direct argv、one Issue／one branch／one PR／Human mergeを維持する。

## Interview Decision 1 — official operator entrypoint

### 質問

Issue Planning Workflowのofficial product surfaceを、Skill-only、Skill-primary＋first-class deterministic CLI、CLI-primaryのどれにするか。

### 比較した選択肢

- Option A: Skill-only official surface
- Option B: Skill-primary＋first-class deterministic CLI
- Option C: CLI-primary＋Skill wrapper

### 推奨

Option B。

### ユーザー回答

- Option Bを採用する。
- ユーザーが明示的に起動するinterfaceはSkillとする。
- WorkflowはSkillへ記述する。
- AgentがCLIを実行してOracleをラップしたChatGPT Planningを利用する。
- CLIが入力情報、出力形式、禁止事項を機械的にPromptへ合成する。

### 採用した意味

```text
Human
→ spec-dock-issue-planning Skill
→ Agent / Main
→ spec-dock-chatgpt CLI
→ Oracle
→ ChatGPT
```

- SkillはWorkflowとsemantic decisionを所有する。
- CLIはsupported deterministic product surfaceである。
- CLIはReview mode、Revision lane、Human adoptionを自己判断しない。

### 仕様への影響

- Requirement: Actor Journey、official surface、authority boundary
- Design: Skill／CLI／Oracle／Runtime component boundary
- Plan: SkillとCLIのcontract／parity tests

## Interview Decision 2 — CLIの処理粒度

### 質問

一つのend-to-end command、phase-separated deterministic commands、両者併設のどれにするか。

### 比較した選択肢

- Option A: one-shot end-to-end command
- Option B: phase-separated deterministic commands
- Option C: phase commands＋convenience orchestrator

### 推奨

Option B。

### ユーザー回答

- Option Bを採用する。
- Initiativeで具体化済みのcommand hierarchyとphase boundaryを、そのまま取り入れる。

### 採用した意味

Issue Planning walking skeletonのChatGPT-facing operationsは、少なくとも次とする。

```text
spec-dock-chatgpt planning create <target>
spec-dock-chatgpt planning revise <target>
spec-dock-chatgpt review planning <target>
```

- Human Gateを越えて自動完走するone-shot commandを作らない。
- Skillが各phaseを順番に実行する。
- adoption、parity、validation、publication、readinessの決定的処理はCore Runtime側へ分離する。

### 仕様への影響

- Requirement: phase-separated authority chain
- Design: application command boundary、resume／retry boundary
- Plan: phase別TDDとnegative fixture

## Interview Decision 3 — Human Issue Plan Authorizationの一次操作面

### 質問

Skill対話、Human作成file、GitHub commentのどれをHuman authorizationの一次操作とするか。

### 比較した選択肢

- Option A: Skill対話で明示承認し、Mainがsource recordへcapture
- Option B: Humanがapproval fileを直接編集
- Option C: GitHub Issue commentを一次recordとする

### 推奨

Option A。

### ユーザー回答

- Option Aを採用する。

### 採用した意味

```text
Skillがexact reviewed identityを表示
→ Humanが対話上で明示承認
→ Mainが回答を構造化source recordへcapture
→ source record SHAを計算
→ Runtimeがschema／identity／hashを検証
→ canonical approval evidenceをclosed render
```

Humanが承認する内容:

1. Issue Planning Bundleの採用
2. Implementation-Start Authorization

- Review PASSはHuman approvalを代替しない。
- genericな`OK`を任意の過去Candidateへ再利用しない。
- Runtimeへ自然言語approval classifierを実装しない。

### 仕様への影響

- Requirement: positive Human Gate
- Design: source record、canonical evidence、identity binding
- Plan: wrong identity／missing field／tampered record tests

## Interview Decision 4 — Planning publication

### 質問

local Planning commit、commit＋push＋remote verification、Planning専用PRのどれをpublication完了とするか。

### 比較した選択肢

- Option A: local Planning commitまで
- Option B: Planning commit＋push＋remote-ref verification
- Option C: Planning専用PR＋Human merge

### 推奨

Option B。

### ユーザー回答

- Option Bを採用する。

### 採用した意味

Planning publication完了条件:

```text
canonical requirement.md / design.md / plan.md
+ canonical Human authorization evidence
+ dedicated Planning commit
+ named Issue branchへのpush
+ local publication commit == remote branch HEAD
+ canonical bytes == commit tree bytes
```

- Planning専用PRは作らない。
- 同じIssue branchにPlanning commitとimplementation commitsを積む。
- 最終的にone Delivery PRを作り、Humanがmergeする。

### 仕様への影響

- Requirement: publication success criteria
- Design: local／remote identity、git-bound reviewed／publication HEAD
- Plan: fake remote、push failure、divergence、no-force recovery tests

## Interview Decision 5 — Review transportの再確認を行わない

### 発端

未承認Bundleをgit-bound Reviewする際の配置pathを選択肢として質問した。

### ユーザー回答

- Reviewは二系統に対応する。
- 適切なInitiative／Epic／Issue directoryへ、適切なcanonical filenameで配置し、commit／pushしたbranchをChatGPTへ共有してReviewする方法を支援する。
- ChatGPTが生成したcomplete ZIPを、そのままfresh Reviewerへ渡す方法も支援する。
- この判断はInitiativeで議論・決定済みである。
- Initiative／Epicで確定した事項をIssue-localで再質問しない。

### 採用した意味

- `archive-candidate`と`git-bound`のdual transportを上位ADRどおり継承する。
- git-boundでは対象Scopeのcanonical pathとfilenameを使用する。
- archiveではexact immutable ZIPをformal Review identityとする。
- transport間のsilent fallbackを行わない。
- この論点は今後再質問しない。

### 仕様への影響

- Requirement／Design／Planに上位contractを完全投影する。
- mode selection rationaleはSkillが所有する。

## Interview Decision 6 — Prompt Markdown resourceの構成

### 質問

operationごとのcomplete template、provider-managed closed fragments、public custom template overrideのどれにするか。

### 比較した選択肢

- Option A: operationごとのcomplete Markdown template
- Option B: provider-managed closed fragment composition
- Option C: public custom template override

### 推奨

Option B。

### ユーザー回答

- Option Bを採用する。

### 採用した意味

- Prompt本文はPython sourceへ長文埋込みしない。
- operation-specific Markdownとshared Markdown fragmentsを固定順序で合成する。
- fragment inventoryはprovider-managed closed setとする。
- recursive include、arbitrary conditional、expression evaluation、public template override、raw prompt overrideを許可しない。
- Operator固有情報は`--context`、`--context-file`、`--file`だけで渡す。
- resource identityとrendered Prompt hashを追跡する。

### 仕様への影響

- Requirement: maintainability、reproducibility、fail-closed
- Design: prompt-set manifest、resource loader、renderer
- Plan: resource parity、unknown／missing／duplicate fragment tests

## Interview Decision 7 — real Issue dogfood target

### 質問

適格条件だけを固定してJIT選定、今exact Issueを固定、dogfood専用Issueを新設のどれにするか。

### 比較した選択肢

- Option A: eligibility contractを今固定し、feature-complete直前にexact IssueをJIT選定
- Option B: clarification時点でexact Issueを固定
- Option C: dogfood専用Issueを新設

### 推奨

Option A。

### ユーザー回答

- Option Aを採用する。

### 採用した意味

今はeligible criteriaだけを仕様化する。

```text
- openな実Issue
- 既存Issue Nodeまたはapproved Seedへbind可能
- iss-00334／00335／00336のdependency chain外
- current Portfolio replanning不要
- vNext Planning refreshが必要
- bounded／rollback可能
- dogfood publicationが他作業を妨げない
```

feature-complete直前にMainが最新repositoryを再調査し、Humanがexact Issueを選ぶ。

- dogfood専用Issueを新設しない。
- downstream Issueの三文書をE1-I1で先行作成しない。
- automated testsでは両Review modeと全negative fixtureを固定検証する。

### 仕様への影響

- Requirement: real-use validation
- Design: target eligibility selector
- Plan: late-binding Human Gateとdogfood evidence format

## 追加のユーザー指示 — 未確定事項の扱い

Humanは、未確定事項を次のように分類するよう指示した。

### Human interviewが不要

- repository調査で判明する事実
- parent契約から導出できる事項
-通常の技術判断で合理的に決められる実装詳細
- file／module／schemaの具体化で、Human value judgmentを伴わないもの

これらはAnalyst／Mainが調査し、研究またはdiscussion Artifactへ結論を記録する。

### Human interviewが必要

- Human authorityの位置
- public product surface
- Scope／Outcome／Non-goalの変更
-不可逆なtrade-off
- parent契約を変える必要がある判断
- exact dogfood Issue選定
- exact reviewed identityへのPlan adoption／implementation-start authorization
- Candidate ZIP生成許可

## 追加確認の要否

### 現時点

- 追加の即時Human質問: なし
- repository調査とIssue-local design concretizationを継続する
- materialな新trade-offが発見された場合だけ、一問に絞って追加Interviewを作る

### 後で必須となるHuman Gate

1. feature-complete直前のexact dogfood Issue選定
2. dogfood対象Issueのexact reviewed identityへのHuman Issue Plan Authorization
3. clarification完了時のCandidate ZIP生成許可

### 条件付きHuman Gate

- direct argvで実装不能なshell exception
- byte-exact rollback不能
- Seedに対応するIssue Node新設
- E1-I1外のlegacy removal
- parent Initiative／Epic／ADR契約変更

## 採用判断

- adoption_status: `adopted-for-candidate-authoring`
- adoption target候補:
  - `iss-00334/requirement.md`
  - `iss-00334/design.md`
  - `iss-00334/plan.md`
  - supporting research／discussion artifacts
- canonical adoption:
  - 未実施。Candidate生成、fresh Planning Review、Human Gateを経るまでcanonical authorityとしない。

## Requirement／Design／Planへの含意

### Requirement

- Skill-primary＋first-class deterministic CLI
- dual Review transport／dual Revision lane
- positive Human Gate
- Planning publication
- Prompt closed fragments
- real Issue dogfood late binding
- mandatory four non-goals

### Design

- actor／component responsibility
- command phase boundary
- Prompt resource architecture
- Candidate／Review／approval／publication identity
- source record／canonical approval evidence
- readiness verifier
- additive migration／E1-I3 cutover boundary

### Plan

- vertical walking skeleton
- phase別TDD
- PA-NF-01〜PA-NF-10
- provider／installed／dogfood parity
- feature-complete後のeligible Issue再調査
- one Issue branch／one Delivery PR／Human merge
