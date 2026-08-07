---
url: https://chatgpt.com/c/6a7509b4-8640-83ee-a26d-60c5d59d8479
title: "マットポコック氏のスキル"
date: 2026-08-07T11:33:37.672Z
lang: ja
---

#### ChatGPT said:

Worked for 8m 27s

# 結論

提案されている構成は、現在の方向性としてかなり良いです。

ただし、設計上は「SpecDockのコアだけを残す」というより、次の二層を残すと整理するのが正確です。

```
SpecDock Storage Core
  ├── Initiative / Epic / Issue
  ├── ディレクトリ階層
  ├── GitHub Issueとの対応
  ├── 依存関係DAG
  ├── Artifact
  ├── validate / sync
  └── 可視化・検索用projection

SpecDock Authoring Kit
  ├── requirement.mdテンプレート
  ├── design.mdテンプレート
  ├── plan.mdテンプレート
  ├── 各文書の役割
  ├── 書き方・品質基準
  └── Initiative / Epic / Issueごとの記述ガイド
```

その外側に、交換可能な認知的ワークフローを置きます。

```
Matt Pocock Skills
  ├── Grilling
  ├── Domain Modeling
  ├── TDD
  ├── Debugging
  ├── Code Review
  └── Implementation discipline

ChatGPT-Use Strict
  ├── 高認知負荷の分析
  ├── Requirement / Design / Plan作成
  ├── EpicからIssueへの分解
  └── Fresh review

Codex / Goal
  ├── ローカル実装
  ├── テスト
  ├──修正
  ├──コミット
  └──Issue完了
```

つまり最終形は、

> **SpecDockは、文書形式とローカル作業グラフの権威。**  
> **Matt Skillsは、考え方と実装方法の権威。**  
> **ChatGPT-Use Strictは、高認知負荷作業を外部化する手段。**  
> **Codex Goalは、実装を完遂する実行コンテナ。**

です。

そして、**`to-spec`と`to-tickets`をインストールしないという判断は適切**です。ただし、それに伴って`ask-matt`、`setup-matt-pocock-skills`、`triage`、`wayfinder`などにも注意が必要です。

* * *

# 1\. この構成が優れている理由

現在のSpecDockが重くなった理由は、文書管理や依存関係管理ではありません。

次のような、モデル能力に依存する認知的・運用的ポリシーをSpecDock自身が所有したことが主因です。

*   Requirement → Reviewer → Design → Reviewer → Plan → Reviewer
    
*   Assurance Grade
    
*   Specialistの必須／任意判定
    
*   Evidence Adoption Ledger
    
*   Candidate ZIP
    
*   Planning Review Result
    
*   Human Decision
    
*   Oracle / Browser invocation
    
*   Manual fallback
    
*   PR Observation
    
*   Reviewer修復ループ
    
*   Issue Executionのステップ状態機械
    

現在の`workflow_spec_authoring.md`は、Requirement・Design・Planごとのfresh reviewer pass、Grade、Evidence Adoption Ledger、Specialist evidenceなどを実行準備条件として要求しています。これを残したままSkillだけMatt Skillsへ変えても、実質的には重いワークフローが残ります。

一方で、現在の高性能モデルでは、ゴール、関連文脈、制約、成功条件を明確にすれば、細かい手順を逐一列挙しなくても適切な進め方を推論できる領域が広がっています。OpenAIの現行モデルガイダンスでも、GPT-5.6はユーザーの意図と期待する作業水準を以前より推論しやすく、重複した指示やTool説明を減らした方がよい場合があるとされています。ただし、ドメイン文脈、ハード制約、成功条件は引き続き明示すべきです。[![](https://www.google.com/s2/favicons?domain=https://developers.openai.com&sz=128)OpenAI Developers](https://developers.openai.com/api/docs/guides/latest-model?utm_source=chatgpt.com)

したがって、これからのSpecDockは、

```
モデルに手順を守らせる
```

のではなく、

```
モデルに正しい情報と保存先を提供し、
構造を壊す操作だけ決定的に防ぐ
```

方向へ移るべきです。

* * *

# 2\. `to-spec`と`to-tickets`を入れない判断は正しい

## `to-spec`が合わない理由

Matt Pocock氏の`to-spec`は、現在の会話を一つのSpecに統合し、設定されたIssue trackerへ公開するSkillです。

その出力は概ね、

*   Problem Statement
    
*   Solution
    
*   User Stories
    
*   Implementation Decisions
    
*   Testing Decisions
    
*   Out of Scope
    

という一文書構造です。

一方、SpecDockは、

```
requirement.md
design.md
plan.md
```

を分離し、それぞれ異なる責務を持たせています。

この二つをAdapterで無理に変換すると、

```
Mattの単一Spec
    ↓
Requirement部分を抽出
Design部分を抽出
Plan部分を抽出
文書間整合性を再確認
```

という新たな独自ワークフローが必要になります。

これは、まさに避けようとしている保守負担の再発です。

したがって、

> **SpecDockの仕様書は、ChatGPT-Use StrictまたはCodexが、SpecDockのテンプレートと作成ガイドに従って直接作る**

方が自然です。

* * *

## `to-tickets`が合わない理由

Matt Pocock氏の`to-tickets`は、Tracer BulletとしてTicketを分割し、設定されたTrackerへIssueを作成し、blocking edgeを登録します。

標準GitHub設定では、

*   GitHub Issueの作成
    
*   GitHub native dependencies
    
*   `ready-for-agent`ラベル
    

などを利用します。

しかしSpecDockでは、

```
Issue identity
  → ローカルのIssue node

親子関係
  → ディレクトリ階層

依存関係
  → .meta.json.depends_on

仕様
  → ローカルのrequirement/design/plan
```

が正本です。

`to-tickets`をそのまま使うと、

```
GitHub側のIssue・依存関係
SpecDock側のIssue・依存関係
```

という二重正本が生まれます。

そのため、これもインストールしない方がよいです。

EpicからIssueへの分割は、

```
ChatGPT-Use Strict
または
Codexの高性能モデル
```

に、

*   親EpicのRequirement / Design / Plan
    
*   SpecDockのIssueテンプレート
    
*   Issue分割ガイド
    
*   既存Issue
    
*   依存関係
    

を読ませて行わせ、CodexがSpecDock CLIでIssueと依存関係を作成すれば十分です。

* * *

# 3\. ただし、`ask-matt`もそのままでは入れない方がよい

ここは見落としやすい点です。

現在の`ask-matt`は、Matt Skillsの標準メインフローとして、

```
grill-with-docs
    ↓
to-spec
    ↓
to-tickets
    ↓
Ticketごとにimplement
```

を明示的に案内します。

したがって、`to-spec`と`to-tickets`をインストールしないのに`ask-matt`だけ入れると、

*   存在しないSkillを推奨する
    
*   SpecDockと競合するフローを推奨する
    
*   ユーザーが意図しないGitHub中心フローへ誘導する
    

可能性があります。

## 推奨

次のいずれかです。

### 推奨案：`ask-matt`をインストールしない

必要なSkillを明示的に呼び分けます。

```
仕様の曖昧さ
  → spec-dock-grill-with-docs

仕様書作成
  → chatgpt-use-strict

実装
  → /goal + implement

不具合
  → diagnosing-bugs

レビュー
  → code-review
```

これが最も単純です。

### 代替案：短いProject Routerを作る

例えば`project-flow`というProject-local Skillを作ります。

Markdown

```
- Clarification and design discussion:
  use spec-dock-grill-with-docs

- Requirement, design, and implementation-plan authoring:
  use chatgpt-use-strict with SpecDock templates and authoring guides

- Epic decomposition:
  use chatgpt-use-strict, then create SpecDock Issue nodes and dependencies

- Implementation:
  use Codex goal and implement

- Bug diagnosis:
  use diagnosing-bugs

- Review:
  use code-review against the local SpecDock documents
```

ただし、このRouterも長くしないことが重要です。

* * *

# 4\. `setup-matt-pocock-skills`も原則として使わない方がよい

`setup-matt-pocock-skills`は、

*   Issue tracker
    
*   Triage labels
    
*   `CONTEXT.md`
    
*   ADR配置
    
*   `AGENTS.md` / `CLAUDE.md`
    

を設定します。任意Trackerも設定できますが、SpecDockでは既に文書配置、Issue管理、依存関係管理が存在するため、Setup Skillに再構成させる必要性は低いです。

特にCodexとClaude Codeを併用する場合、どのInstructions fileへ書くかもSetup Skill側の判断になります。

## 推奨

次のファイルは手動で固定します。

```
AGENTS.md
docs/agents/issue-tracker.md
docs/agents/domain.md
```

### `docs/agents/issue-tracker.md`

Markdown

```
# Issue tracker: SpecDock

SpecDock is the canonical local work graph and specification store.

GitHub Issues are linked collaboration and lifecycle records.
Their body is not the canonical specification.

Use SpecDock for:

- Initiative / Epic / Issue identity
- hierarchy
- local specifications
- artifacts
- dependencies
- readiness

Use the SpecDock CLI for structural mutations.
Read and edit Markdown documents directly.
```

Mattの`code-review`は、関連IssueやSpecを探すとき、`docs/agents/issue-tracker.md`の取得方法を参照します。そのため、このファイルで「GitHub Issue本文ではなくSpecDockのローカル文書を読む」と定義すれば、Spec軸Reviewをローカル仕様書へ向けられます。

* * *

# 5\. 推奨するMatt Skillsの導入構成

## そのまま導入してよいもの

Skill

用途

`grilling`

意思決定のヒアリング

`domain-modeling`

用語整理、CONTEXT.md、ADR

`tdd`

Red → Green

`codebase-design`

Deep Module、Seam、Interfaceの設計語彙

`code-review`

Standards / Specの二軸レビュー

`diagnosing-bugs`

再現・仮説・計測・修正

`resolving-merge-conflicts`

意図に基づく競合解消

`writing-for-agents`

Skill・AGENTS・Agent向け文書

`wait-what`

説明の修復

`wizard`

人間にしかできない外部操作

* * *

## 条件付きで導入するもの

Skill

方針

`implement`

導入してよい。SpecDockの計画書を入力として使う

`research`

出力先をScope-local Artifactへ指定する

`prototype`

Prototype結果への参照をScope Artifactへ残す

`handoff`

一時的なSession移送に使う。Canonical記録にはしない

`improve-codebase-architecture`

必要に応じて導入

`implement`は現在かなり薄く、SpecまたはTicketに書かれた作業を実装し、TDD、定期的な型検査・テスト、最終Code Review、Commitまで行う内容です。SpecDockの`plan.md`を入力にすれば、そのまま利用できます。

* * *

## インストールしない方がよいもの

Skill

理由

`to-spec`

SpecDock文書モデルと競合

`to-tickets`

Issue・依存関係の正本が競合

`ask-matt`

`to-spec` / `to-tickets`を含む標準フローへ誘導

`setup-matt-pocock-skills`

SpecDock既存構成を再定義し得る

`triage`

GitHub label state machineとの競合

`wayfinder`

Map、child issue、label、native dependency前提が強い

`wayfinder`は特に、MapをTracker上のIssueとして持ち、Decision Ticketをchild Issueとし、Assignee、Label、native blockingを利用する設計です。SpecDock向けAdapterなしで導入すると、Trackerの正本が曖昧になります。

* * *

# 6\. `grill-with-docs`は、そのままではなく薄いSpecDock版を作る

この判断が最も重要です。

現在の`grill-with-docs`自体は、実質的に次の一行です。

```
Run a grilling session, using domain-modeling.
```

したがって、上流の`grill-with-docs`を直接インストールするより、

*   `grilling`
    
*   `domain-modeling`
    

だけを上流からインストールし、Project-localに、

```
spec-dock-grill-with-docs
```

を作る方がよいです。

## 推奨する内容

Markdown

```
---
name: spec-dock-grill-with-docs
description: >
  Grill the user about the active or explicit SpecDock scope,
  recording durable analysis in a scope-local SpecDock Artifact
  while maintaining shared domain language and ADRs.
disable-model-invocation: true
---

1. Resolve the explicit SpecDock Scope.
   If none was supplied, use the active Initiative, Epic, or Issue.

2. Create one scope-local Artifact using the SpecDock CLI.
   Use the exact returned path.

3. Run the upstream `grilling` discipline with `domain-modeling`.

4. Keep the Artifact updated with:
   - purpose
   - discovered facts
   - resolved decisions
   - alternatives considered
   - unresolved questions
   - possible canonical-document targets

5. Update CONTEXT.md only for shared domain terminology.

6. Create an ADR only when the domain-modeling ADR criteria are met.

7. Do not automatically rewrite requirement.md, design.md, or plan.md.
   Specification authoring is a separate ChatGPT-Use Strict or Codex task.

8. Finish when the user confirms shared understanding.
```

## Artifact例

Markdown

```
---
kind: grilling
scope_id: iss-00123
source_skill: spec-dock-grill-with-docs
status: completed
---

# Refresh token design discussion

## 目的

Refresh token rotationの境界を確定する。

## 確認した事実

- Access tokenの有効期限は15分。
- Redisは既に利用されている。
- 現在revoke APIは存在しない。

## 確定した判断

### D-001 Refresh tokenをローテーションする

- 採用案: refreshごとに新しいtokenを発行する
- 不採用案: 同じtokenを有効期限まで再利用する
- 理由: token漏洩時の再利用期間を限定する

## 未解決事項

- 複数端末を同じtoken familyとして扱うか

## 仕様書への反映候補

- requirement.md: 再利用済みtokenを拒否する
- design.md: token familyとrotation
- plan.md: persistence、rotation、reuse detection
```

ここでは、旧SpecDockのEvidence Adoption LedgerやReviewer Gateは不要です。

Artifactは単に、

> **仕様書作成の材料となる、Scope-localな長期記憶**

です。

* * *

# 7\. ChatGPT-Use Strictは、内蔵ChatGPT-first Workflowの完全な代替になり得る

ご説明のChatGPT-Use Strictには、

*   現在の開発BranchをGitHubへPush
    
*   正確なRepository / Branch / HEADを確認
    
*   ChatGPTがGitHub上の現在状態を参照
    
*   高認知負荷の分析や仕様書作成を実行
    
*   ChatGPTはRepositoryへ直接Mutationしない
    
*   Codexが結果を受け取りローカルへ反映
    

という境界があります。

この境界は、現在のSpecDockに内蔵されたChatGPT-first Planning Runtimeよりはるかに汎用的です。

## 残すべきStrictness

ChatGPT-Use Strictの「Strict」は、次に使うべきです。

*   正確なRepository
    
*   正確なBranch
    
*   正確なHEAD
    
*   Default branchへのfallback禁止
    
*   対象Scopeの明示
    
*   Canonical文書Pathの明示
    
*   Template / Authoring Guideの明示
    
*   SecretやPrivate local fileの除外
    
*   出力ファイルの完全性
    
*   ChatGPTによるRepository mutation禁止
    

## 取り除いてよいStrictness

次はSpecDock Coreへ戻さない方がよいです。

*   Candidate ZIP必須
    
*   Fresh Review必須
    
*   Human Decision JSON必須
    
*   Archive mode / Git-bound mode
    
*   Evidence Ledger必須
    
*   Phase promotion必須
    
*   Grade別Reviewer必須
    
*   Manual fallback state machine
    

つまり、

> **入力と対象の正確性は厳密にする。**  
> **作業プロセスは柔軟にする。**

という構造です。

* * *

# 8\. ChatGPT-Use Strictによる仕様書作成フロー

推奨フローは次です。

```
1. Codexが対象Scopeを解決
2. BranchをPushし、exact HEADを確認
3. ChatGPT-Use Strictを起動
4. ChatGPTがSpecDockのテンプレートと作成ガイドを読む
5. 完全なrequirement.md / design.md / plan.mdを返す
6. CodexがCanonical pathへ書く
7. spec-dock validate
8. git diffで確認
9. 必要ならfresh ChatGPT review
10. Commit
```

## ChatGPTへ渡す情報

本文プロンプトへ全ルールをコピーする必要はありません。

次のPathを明示します。

```
Target:
- active Issue: iss-00123
- requirement: <path>
- design: <path>
- plan: <path>

Authoring contract:
- requirement template: <path>
- design template: <path>
- plan template: <path>
- requirement guide: <path>
- design guide: <path>
- plan guide: <path>

Context:
- parent Epic documents
- parent Initiative documents
- relevant artifacts
- relevant ADRs
- relevant source files
```

テンプレートや作成ガイドの内容をChatGPT-Use Strict Skillへ複製してはいけません。

Skillは、

```
指定されたPathの現在版を読む
```

だけにします。

これにより、SpecDockのテンプレートを更新してもSkillを更新する必要がありません。

* * *

# 9\. EpicからIssueへの分割もChatGPT-Use Strictへ逃がせる

`to-tickets`をインストールしなくても問題ありません。

ChatGPT-Use Strictへ、

> このEpicのRequirement、Design、Plan、既存Issue、依存関係を読み、SpecDockのIssueテンプレートとIssue分割ガイドに従って、必要なIssue群と依存関係を提案してください

と依頼します。

出力例です。

Markdown

```
## Proposed Issues

### I1 — Persist refresh token families

Outcome:
- Refresh token familyを永続化できる

Blocked by:
- None

### I2 — Rotate refresh tokens

Outcome:
- Refreshごとに新しいtokenを発行する

Blocked by:
- I1

### I3 — Detect token reuse

Outcome:
- 利用済みtokenの再利用を検出する

Blocked by:
- I2
```

Codexがこの結果を使い、

Bash

```
spec-dock new issue ...
spec-dock deps add ...
```

を実行します。

重要なのは、ChatGPTにCLIコマンドを実行させないことです。

```
ChatGPT
  → 意味のあるIssue分割を作る

Codex
  → Issue nodeと依存関係を実際に作る

SpecDock
  → DAGと構造を検証する
```

という分離です。

最初から複雑なbatch-create runtimeを作る必要はありません。繰り返し操作が本当に負担になった段階でだけ追加すべきです。

* * *

# 10\. SpecDockの文書は残すが、現在の文書をそのまま残してはいけない

ここが最も重要な注意点です。

「Requirement / Design / Planのテンプレートと丁寧な作成ガイドを残す」ことには賛成です。

しかし、現在のSpecDock文書には、

*   Reviewer Gate
    
*   Grade
    
*   Evidence Adoption Ledger
    
*   Specialist使用
    
*   Manual fallback
    
*   Promotion
    
*   Readiness
    
*   Execution handoff
    

が大量に含まれています。

これらを残すと、ワークフローコードを削除しても、モデルは文書から旧ワークフローを再現しようとします。

## 残すべきもの

### Requirement Guide

*   目的
    
*   現在の問題
    
*   Actor
    
*   観測可能な成果
    
*   Scope / Out of Scope
    
*   Acceptance Criteria
    
*   Edge Cases
    
*   制約
    
*   親Scopeから継承する条件
    

### Design Guide

*   Contextと境界
    
*   Module / Interface
    
*   Domain model
    
*   Data flow
    
*   API / Event / Schema
    
*   Error handling
    
*   Security
    
*   Migration
    
*   Observability
    
*   Alternatives
    
*   Decision rationale
    
*   Diagramの選び方
    

### Plan Guide

*   ゴール
    
*   実装順序
    
*   変更対象
    
*   Test seam
    
*   検証コマンド
    
*   Migration / Rollback
    
*   Completion criteria
    
*   不明点が判明した場合の扱い
    

## 削除すべきもの

*   Requirement reviewer passの必須化
    
*   Design reviewer passの必須化
    
*   Plan reviewer passの必須化
    
*   Grade別の義務
    
*   Specialist使用証跡
    
*   Evidence Adoption Ledger
    
*   Delegated Draft Evidence
    
*   Reviewer Gate Status
    
*   Human approval schema
    
*   Phase promotion state
    
*   ChatGPT-first fallback規則
    

* * *

# 11\. 「テンプレート」と「作成ガイド」を分離する

丁寧な仕様書作成方法を残すことと、巨大なテンプレートを残すことは同じではありません。

最適なのは、

```
Template
  → 実際の文書に残る骨格

Authoring Guide
  → モデルが必要時に読む詳細説明
```

です。

## Template

テンプレートには、必要な見出しと最低限の説明だけを置きます。

Markdown

```
# Requirement

## 目的

## 背景

## 観測可能な成果

## Scope

## Out of Scope

## Acceptance Criteria

## Edge Cases

## 制約

## Open Questions
```

## Authoring Guide

作成ガイドには、

*   良い記述と悪い記述
    
*   RequirementとDesignの境界
    
*   Acceptance Criteriaの粒度
    
*   IssueとEpicの違い
    
*   Optional section
    
*   Diagram catalog
    
*   典型的な漏れ
    
*   具体例
    

を詳しく置きます。

Matt Pocock氏の`writing-for-agents`も、全情報を一つの文書へ詰め込まず、常に必要なStepsを上位に置き、条件付きReferenceをContext Pointerの背後へ移すProgressive Disclosureを重視しています。

つまり、

> **作成ガイドは丁寧にする。**  
> **テンプレートは過剰にしない。**

のがよいです。

* * *

# 12\. 実装は`/goal + implement`でよい

この部分も提案どおりです。

OpenAIは現在、CodexのGoal機能を、長時間作業で追跡する永続的なObjectiveとして位置付けています。[![](https://www.google.com/s2/favicons?domain=https://developers.openai.com&sz=128)OpenAI Developers](https://developers.openai.com/?utm_source=chatgpt.com)

したがって、実装時は、

```
SpecDockのactive Issue
    ↓
Requirement / Design / Plan
    ↓
Codex Goal
    ↓
Matt implement / tdd / code-review
```

という構成でよいです。

## 推奨するGoal

細かな手順を列挙する必要はありません。

```
Complete the active SpecDock Issue iss-00123.

Use its requirement.md, design.md, and plan.md as the authoritative
description of the work.

Work autonomously until the acceptance criteria and completion criteria
are satisfied. Use the installed TDD, debugging, and code-review
disciplines where appropriate.

Run the relevant tests and static checks, keep the specifications
consistent with the implemented behavior, and commit the completed work.
```

このGoalには、

*   対象
    
*   正本
    
*   成功条件
    
*   利用できる認知的Skill
    
*   最終成果
    

だけがあります。

旧`issue-execution`のような、

*   一ステップごとのGate
    
*   Worker delegation rule
    
*   Reviewer state
    
*   Evidence ledger
    
*   Parent implementation exception
    

は不要です。

* * *

# 13\. `issue start`と`issue finish`は残してよい

これらは重いワークフローというより、便利なライフサイクルPrimitiveです。

```
issue start
  → active Issueを設定し、必要ならBranchへ移動

issue finish
  → GitHub Issueをcloseし、activeを解除
```

これ自体が、

*   どう実装するか
    
*   何回Reviewするか
    
*   どのモデルを使うか
    

を決めなければ、Coreに残して問題ありません。

推奨フローは単純です。

```
spec-dock issue start iss-00123

/goal
  Complete the active Issue according to its plan

Codex:
  implementation
  tests
  review
  commit

spec-dock issue finish
```

依存関係により未着手Issueを止める機能も、構造的不変条件として残せます。

* * *

# 14\. 最小のSpecDock連携Skillを一つだけ残す

SpecDock自身が配布するSkillは、一つで十分です。

```
spec-dock
```

これはModel-invokedな永続化Skillです。

Markdown

```
---
name: spec-dock
description: >
  Use the repository's local SpecDock whenever work needs specifications,
  Initiative/Epic/Issue nodes, scope-local analysis artifacts,
  dependencies, active scope, or GitHub Issue linkage.
---

SpecDock is the local specification and work-graph backend.
It does not define the development workflow.

Resolve the explicit Scope first; otherwise use the active Scope.

Read and edit canonical Markdown documents in the resolved node.

Store durable scope-specific analysis in the node's `artifacts/`
directory, creating the Artifact through the SpecDock CLI.

Use the SpecDock CLI for structural changes:

- node creation and lifecycle
- hierarchy
- dependency edges
- GitHub Issue linkage
- validation and projections

Follow the workflow of the invoking skill.
Do not impose a separate SpecDock planning, review, or implementation flow.

Discover exact commands from the local CLI help.
```

これで、

*   `research`
    
*   `code-review`
    
*   `implement`
    
*   ChatGPT-Use Strictの結果反映
    
*   通常のCodex作業
    

のすべてがSpecDockを発見できます。

* * *

# 15\. 推奨する最終ワークフロー

## 新しいInitiative / Epic / Issueを検討する

```
1. Scopeを作成またはactiveにする
2. spec-dock-grill-with-docs
3. 分析をScope-local Artifactへ残す
4. 必要な用語をCONTEXT.mdへ反映
5. 必要な判断をADRへ反映
```

## 仕様書を作る

```
1. ChatGPT-Use Strictを起動
2. Exact repo / branch / HEADを確認
3. SpecDockテンプレート・作成ガイド・親文書・Artifactを参照
4. Requirement / Design / Planを作成
5. CodexがCanonical pathへ反映
6. validate
7. 必要に応じてfresh ChatGPT review
8. Commit
```

## EpicをIssueへ分割する

```
1. ChatGPT-Use StrictでEpicを分析
2. Issue候補と依存関係を返す
3. CodexがSpecDock Issue nodeを作成
4. Codexがdepends_onを登録
5. 各IssueのRequirementを作成
6. validate / sync
```

## Issueを実装する

```
1. issue start
2. /goalでIssue完了を指定
3. implement / tdd / diagnosing-bugs / code-review
4. Tests・静的解析
5. 必要なら仕様書を更新
6. Commit
7. issue finish
```

* * *

# 16\. 移行時に残すもの・削除するもの

## 残す

```
spec-dock/initiatives/
spec-dock/templates/
spec-dock/docs/authoring/
spec-dock/scripts/spec-dock
Issue/Epic/Initiative metadata
artifacts/
depends_on
active
validate
sync
PlantUML / JSON projections
GitHub linkage
issue start / finish
new / import / delete
```

## 削除する

```
spec-dock-chatgpt
ChatGPT Planning create/review/revise/apply
Oracle adapter
Candidate ZIP
PlanningReviewResult
PlanningHumanDecision
Assurance
Grade
guidance issue-planning
guidance issue-execution
Reviewer Gate
Evidence Adoption Ledgerの必須化
Planning manual fallback Skills
Issue Execution Skill
Epic Execution Skill
PR observation
PR merge-preparer
Named reviewer orchestration
```

## 書き換える

```
workflow_spec_authoring.md
phase_requirement.md
phase_design.md
phase_plan.md
workflow_issue.md
workflow_epic.md
workflow_initiative.md
requirement/design/plan templates
report.md template
```

書き換え後は「いつ何を呼ぶか」ではなく、

> **その文書が何を表し、どのような品質で書かれるべきか**

だけを説明します。

* * *

# 17\. この設計で残る課題

## Matt SkillsはCodexでは自動更新ではない

Matt Pocock氏側ではSkillsが更新されますが、Codex向けの`skills.sh`方式はRepositoryへファイルをコピーする方式です。更新は`npx skills update`などで明示的に取得します。Claude Codeのmanaged pluginとは異なり、上流変更が無条件に自動反映されるわけではありません。

これはむしろ安全です。

推奨は、

```
Upstream-maintained
Locally-pinned
Periodically-updated
```

です。

* * *

## Matt Skillsは正式な業界標準ではない

有力で、コミュニティから注目され、実践的なToolkitではありますが、標準化団体が管理する仕様ではありません。

したがって、SpecDock CoreをMatt固有のSkill名や出力形式へ結合してはいけません。

```
SpecDock Core
  → resolve scope
  → create artifact
  → create node
  → add dependency
  → validate

Matt Skills
  → それらを利用する一つのClient
```

という依存方向を守るべきです。

* * *

## `/goal`でもモデルが必ず完遂する保証はない

Goalは長時間作業を安定させますが、仕様の誤読、不要変更、早期完了を完全には防げません。

ただし対策は旧Workflowを復活させることではありません。

優先順位は次です。

1.  Requirement / Design / Planを改善する
    
2.  Completion criteriaを明確にする
    
3.  Testsを追加する
    
4.  Goalを明確にする
    
5.  Code Reviewを利用する
    
6.  それでも繰り返し壊れる構造だけCore guardrailにする
    

一度の失敗を理由に新しいGateを追加すると、再びSpecDockが重くなります。

* * *

# 18\. Guardrailを追加する判断基準

今後SpecDockへ新しい制約を追加するのは、次の条件をすべて満たす場合だけにするとよいです。

1.  複数のモデルまたは複数回の実行で同じ失敗が再発した
    
2.  失敗がデータ破損、誤った依存関係、Scope混同など構造的な問題である
    
3.  決定的コードで安価に防げる
    
4.  文書改善やTool UX改善だけでは十分に防げない
    
5.  特定Workflowに依存せず、他のSkillにも普遍的に有効である
    

例えば、

```
循環依存を禁止する
```

はCore guardrailとして妥当です。

一方、

```
Designの前に必ずReviewerを3体呼ぶ
```

はCore guardrailにすべきではありません。

* * *

# 最終評価

提案された構成は、次の修正を加えれば、現時点で最も良い塩梅です。

1.  **`to-spec`と`to-tickets`はインストールしない**
    
2.  **`ask-matt`、`setup-matt-pocock-skills`、`triage`、`wayfinder`も初期導入から外す**
    
3.  **上流`grill-with-docs`ではなく、`grilling + domain-modeling`を利用する薄い`spec-dock-grill-with-docs`を作る**
    
4.  **SpecDockにはStorage CoreとAuthoring Kitを残す**
    
5.  **現在の丁寧な文書をそのまま残さず、Authoring semanticsだけ残してWorkflow gateを削る**
    
6.  **ChatGPT-Use Strictへ仕様作成・分割・高負荷Reviewを逃がす**
    
7.  **実装は`/goal + implement + tdd + code-review`へ移す**
    
8.  **SpecDock Coreは文書・Issue・依存関係・構造検証だけを管理する**
    
9.  **Matt Skillsは上流追従、ローカルではVersionを固定する**
    
10.  **新しいGuardrailは実測された構造的失敗にだけ追加する**
    

最終的には、SpecDockを、

> **開発方法を規定するWorkflow Engine**

から、

> **高性能なモデルが自由に考え、正しく記録し、次のモデルが容易に再開できるローカル仕様・作業グラフ**

へ変えることになります。

この形なら、SpecDockが持っている独自価値は残り、モデルの進歩を妨げる運用的負債だけを切り離せます。

![](https://www.google.com/s2/favicons?domain=https://developers.openai.com&sz=32)

Sources

  

Today 5:12 PM

#### You said:

うん、この構成でかなりスペックドックシンプルにできると思います。一方で、仕様書の作成から実装までの自動化という理念は失われますが、これは現在のモデルの性能としてもやっぱり自動化には耐えられない、ボロが出る、大量のスロップが生成するという現実がありました。うん、なので一旦この自動化に関しては、今後のモデルの進化に委ねるとした上で、うん、この、仕様書の作成、基本的にChatGPTに丸ごと全部作成を依頼するというのが、今見出しているいい感じのところだと思うので、今後のChatGPTの最先端フロンティアモデルの発展に期待をしたいと思います。その上で、かなりこのスペックドックはストレージコアとオーソレングキットだけ残してシンプルにします。で、今回例としてマットポコのスキルを例としていますが、今後この外部側のインテリジェンスはいくらでも切り替え可能なものにしていきたいと思っています。うん。なので、これスキルですね。スキルはこれ実質二つ作るのかなと思っています。うん。あ、まあそうですね。スキル、スペックドック、Grill with Docs。これはスキルとして作る。あと、スペックドックスキルですね。これはスペックドック自体の使用方法だとか概要をモデルに学習させるためのスキル。うん。これだけを残して、あとは綺麗さっぱり整理したいと思います。あとこのスペックドックGrill with Docsですが、これはローカル側にこのスキルを作成するとよいか、それともスペックドック側にこのスキルを作成するとよいか、どちらがよいと思いますか?ここをですね、うん。というのも、この仕様書の作成、ユーザーとのディスカッションですね。モデルが調査して、Grill with Docsのスペックドックに対応したスキル、これはスキルにするか、なんか別の形でもよい、Grill with Docsを使用しつつ、それとは別にスペックドックの知識を与えながらという形でもよいのかもしれませんが、ここがですね、まだ十分に詰めきれていないと思います。うん。モデルが調査し、ユーザーと対話し、要件を具体化しするところですね。そして仕様書を作る。ここはChatGPT側に委ねるところではありますが、ここがまだ具体化できていないと思いました。うん。それは、MatpocのスキルのGrill with Docsが作成するファイルを指定しているといった都合がありますが、これはスペックドックのスキルを読み込ませて、この指示を書き換えることができるのか、できないのであれば、うん、Grill with Docsはインストールせずに、独自のスペックドック Grill with Docsのスキルを作成するか、ここをちょっと具体化してほしいです。ベストプラクティスを提案してください。また、重要なのは今後インテリジェンス部分は切り替え可能にする、簡単に切り替え可能にするというところです。

Show moreShow less

  

#### ChatGPT said:

Worked for 6m 59s

# 結論

最も適切な構成は次です。

1.  **`spec-dock` Skill**  
    SpecDock Coreの利用方法、Scope解決、仕様書・Artifact・Issue・依存関係の保存方法をモデルへ教える、安定したModel-invoked Skill。
    
2.  **`spec-dock-grill-with-docs` Skill**  
    SpecDock上の現在Scopeを対象として、外部の`grilling`と`domain-modeling`を組み合わせ、対話・調査結果をScope-local Artifactへ保存する、明示起動型の薄いIntegration Skill。
    

そして配置は、次のように分けるのが最善です。

```
ユーザー環境・外部配布
  ├── grilling
  ├── domain-modeling
  ├── tdd
  ├── code-review
  ├── diagnosing-bugs
  └── chatgpt-use-strict

各SpecDock導入リポジトリ
  └── .agents/skills/
      ├── spec-dock/
      └── spec-dock-grill-with-docs/
```

**`spec-dock-grill-with-docs`のソースはSpecDock側で管理し、導入先リポジトリへRepo Skillとして配布する**のがよいです。ただし、SpecDock Coreそのものではなく、`integrations/matt-pocock/`のような**任意のIntegration Layer**として分離します。

上流の`grill-with-docs`はインストールしません。代わりに上流の、

*   `grilling`
    
*   `domain-modeling`
    

だけを利用します。

この構成なら、Matt Pocock氏の認知ロジックの改善を受け取りながら、SpecDock固有の保存規則はSpecDock側で確実に維持できます。

* * *

# 1\. 既存の`grill-with-docs`と`spec-dock`を同時に読み込ませるだけでは不十分

まず重要な点として、現在のMatt Pocock氏の`grill-with-docs`は、実は非常に短いSkillです。

```
Run a /grilling session, using the /domain-modeling skill.
```

つまり、`grill-with-docs`自身が複雑な質問ロジックやファイル保存処理を持っているわけではありません。質問ロジックは`grilling`が、`CONTEXT.md`やADRの更新は`domain-modeling`が担当します。

`grilling`は、意思決定をDesign Treeとして扱い、現在回答可能なFrontierをラウンド単位でユーザーに質問します。コードやRepositoryから調査できるFactはモデルが調査し、ユーザーにはDecisionだけを確認する設計です。

`domain-modeling`は、共有用語を`CONTEXT.md`へ、長期的で戻しにくい設計判断をADRへ記録します。

したがって、競合の中心は、

```
Grillingの質問方法
```

ではなく、

```
Grillingで得たScope固有の分析を、
どこへどの形式で永続化するか
```

です。

ここだけをSpecDock側で補えばよいわけです。

* * *

## Skill同士の「上書き」は信頼できない

Codexは複数のSkillを明示的または暗黙的に起動できますが、Skill同士を自動的にマージしたり、一方が他方を上書きしたりする正式な仕組みではありません。特に同じ`name`を持つSkillが複数存在しても、Codexはそれらをマージせず、両方をSkill selectorへ表示する場合があります。[![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=128)ChatGPT Learn](https://learn.chatgpt.com/codex/build-skills)

したがって、

```
上流 grill-with-docs
+
SpecDock Skill
```

を同時に読み込ませ、

> SpecDock Skillの方が保存規則を上書きしてくれるだろう

と期待するのは不安定です。

モデルが両方の指示をうまく統合する場合もありますが、次のような揺れが残ります。

*   Scope-local Artifactを作らず`CONTEXT.md`だけ更新する
    
*   Artifactを作るがフォーマットを守らない
    
*   Requirement / Design / PlanまでGrilling中に変更する
    
*   Active ScopeではなくRepository rootへ保存する
    
*   上流SkillとSpecDock Skillのどちらを優先するかが実行ごとに変わる
    

よって、**明示的な一つの入口Skillで合成する**方がよいです。

* * *

# 2\. 最善案は「上流SkillのFork」ではなく「薄いComposition Skill」

推奨する`spec-dock-grill-with-docs`は、Matt Pocock氏の`grill-with-docs`をコピーして大幅改変するSkillではありません。

構造は次です。

```
spec-dock-grill-with-docs
        │
        ├── SpecDock Scopeを解決
        ├── Scope-local Artifactを作成
        ├── grillingを利用
        ├── domain-modelingを利用
        └── Artifactへ結果を記録
```

つまり、

```
SpecDock固有部分
  = Scopeと永続化

Matt Skills固有部分
  = 質問、調査、Domain Modeling
```

を分けます。

Matt Pocock氏の設計でも、User-invoked SkillはOrchestrationを担当し、Model-invoked Skillは再利用可能なDisciplineを担当します。`grill-with-docs`も、User-invokedな薄い入口からModel-invokedな`grilling`と`domain-modeling`を利用する構造です。

したがって、SpecDock版も同じ構造にするのが自然です。

* * *

# 3\. Skillの配置先：ユーザーグローバルではなくRepo-local

Codexは、次のScopeからSkillを読み込みます。

*   Repository Scope：`$REPO_ROOT/.agents/skills`
    
*   User Scope：`$HOME/.agents/skills`
    
*   Admin Scope
    
*   System Scope
    

Repository固有のSkillはRepo内に、複数Repositoryで利用する個人SkillはUser Scopeに置くことが公式に推奨されています。[![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=128)ChatGPT Learn](https://learn.chatgpt.com/codex/build-skills)

したがって、配置は次が適切です。

Skill

所有者

Installation Scope

`grilling`

Matt Pocock / 外部

UserまたはPlugin

`domain-modeling`

Matt Pocock / 外部

UserまたはPlugin

`tdd`

Matt Pocock / 外部

UserまたはPlugin

`code-review`

Matt Pocock / 外部

UserまたはPlugin

`chatgpt-use-strict`

ユーザー個人

User

`spec-dock`

SpecDock

Repository

`spec-dock-grill-with-docs`

SpecDock Integration

Repository

`chatgpt-use`は、現在、ユーザー環境固有のOracle wrapper、Browser mode、ChatGPT Project URL、Local Oracle checkout、Model selection、Session recoveryなどを扱っています。そのため、SpecDockへ同梱するのではなく、Operator-ownedなUser Skillとして維持するのが正しいです。

SKILL

一方、`spec-dock-grill-with-docs`は、

*   SpecDockのActive Scope
    
*   Artifactの作成方法
    
*   Artifact format
    
*   Authoring Kitの位置
    
*   SpecDock CLI
    

に依存します。

したがって、User-globalにすると、異なるSpecDock versionやSpecDockを使わないRepositoryでも誤起動する可能性があります。**SpecDockのversionと一緒にRepositoryへ配布するべきSkill**です。

* * *

# 4\. ソースコード上は「Core」ではなく「Optional Integration」に置く

インストール先はRepository Scopeですが、SpecDockソース内での置き場所は分離すべきです。

推奨構造です。

```
spec-dock/
├── core/
│   ├── nodes
│   ├── dependencies
│   ├── artifacts
│   ├── validation
│   └── projections
│
├── authoring-kit/
│   ├── templates
│   ├── requirement-guide.md
│   ├── design-guide.md
│   └── plan-guide.md
│
├── skills/
│   └── spec-dock/
│
└── integrations/
    └── matt-pocock/
        └── skills/
            └── spec-dock-grill-with-docs/
```

これにより、CoreはMatt Skillsを知りません。

```
Core
  × grillingを知らない
  × domain-modelingを知らない
  × ChatGPTを知らない
  × Oracleを知らない
```

Optional Integrationだけが、

```
この環境ではgrillingとdomain-modelingを使う
```

と知っています。

初期段階では同じGitHub Repository内に置いて構いません。Artifact formatやCLIがまだ変わる段階では、同じRepositoryの方が整合を取りやすいからです。

ただし、次の境界を設けます。

*   CoreからIntegrationへのImportは禁止
    
*   Core testsとIntegration testsを分離
    
*   Integrationは任意インストール
    
*   Coreのmetadata schemaにMatt固有項目を追加しない
    
*   Integrationを削除しても既存SpecDock dataはそのまま利用できる
    

Core contractが安定した後、必要なら`spec-dock-matt-skills`という別RepositoryやPluginへ移動できます。

* * *

# 5\. 二つのSpecDock Skillの正確な責務

## 5.1 `spec-dock`

これはModel-invokedなPersistence / Repository Skillです。

### 担当すること

*   Explicit ScopeまたはActive Scopeの解決
    
*   Initiative / Epic / Issueの文書読込み
    
*   親Scopeの文書読込み
    
*   Scope-local Artifactの作成
    
*   Canonical文書の編集場所の解決
    
*   Issue node作成
    
*   Dependency追加・削除
    
*   GitHub Issue linkage
    
*   `validate`とprojection
    
*   Authoring Kitへの案内
    

### 担当しないこと

*   Grilling
    
*   仕様作成フロー
    
*   Requirement → Design → Planの順序強制
    
*   Reviewer起動
    
*   TDD
    
*   実装
    
*   ChatGPT呼出し
    
*   Human approval
    
*   PR delivery
    

### Skill本文のイメージ

Markdown

```
---
name: spec-dock
description: >
  Use this repository's local SpecDock when work needs to read or update
  specifications, scope artifacts, Initiative/Epic/Issue nodes,
  dependencies, active scope, or GitHub Issue linkage.
---

SpecDock is the repository's local specification and work-graph backend.
It does not define the development workflow.

Resolve the explicit Scope first. Otherwise use the active Scope.
Stop only when the Scope is genuinely ambiguous.

Read and edit canonical Markdown documents in the resolved node.

Create durable scope-specific analysis through the SpecDock Artifact command,
then write only to the returned path and follow the scope-local artifact rules.

Use the SpecDock CLI for structural mutations:

- node creation and lifecycle
- hierarchy
- dependency edges
- GitHub Issue linkage
- validation and projections

Follow the workflow of the invoking skill.
Do not impose a separate SpecDock planning, review, or implementation process.

Read the current Authoring Kit and CLI help instead of relying on copied rules.
```

* * *

## 5.2 `spec-dock-grill-with-docs`

これはUser-invokedなDiscovery / Clarification Skillです。

### 担当すること

*   Scopeを確定する
    
*   Interview Artifactを一つ作る
    
*   Repository、親仕様、既存Artifactを調査する
    
*   `grilling`でユーザーと対話する
    
*   `domain-modeling`で用語とADR候補を整理する
    
*   調査結果とDecisionをArtifactへ保存する
    
*   ChatGPTによる仕様作成へ渡せるAuthoring Briefを作る
    

### 担当しないこと

*   Requirement / Design / Planの完成
    
*   ChatGPT-Use Strictの自動起動
    
*   Issue分割
    
*   Implementation
    
*   Reviewer Gate
    
*   Canonical文書の自動変更
    

### Skill本文のイメージ

Markdown

```
---
name: spec-dock-grill-with-docs
description: >
  Explicitly investigate and clarify an active or named SpecDock scope
  through a grilling session, preserving the findings as a scope-local
  SpecDock Artifact and maintaining shared domain language where needed.
disable-model-invocation: true
---

1. Resolve the explicit SpecDock Scope.
   If none was supplied, use the active Initiative, Epic, or Issue.

2. Read:
   - the Scope's canonical documents;
   - parent-scope documents;
   - relevant existing Artifacts;
   - relevant source code and tests;
   - the configured domain glossary and ADRs.

3. Create one scope-local `interview` or `analysis` Artifact through
   the SpecDock CLI. Use the exact returned path and current artifact rules.

4. Run the installed `grilling` discipline with `domain-modeling`.

5. Keep the Artifact current with compact summaries of:
   - discovered facts;
   - resolved decisions;
   - alternatives considered;
   - rejected alternatives and rationale;
   - unresolved questions;
   - implications for requirement, design, and plan.

6. Update shared domain documentation only when a shared term is resolved.
   Create an ADR only when the domain-modeling ADR criteria are met.

7. Do not author or rewrite canonical requirement, design, or plan files.
   End with an authoring-ready brief for the next intelligence provider.

8. Finish when the user confirms shared understanding and the Artifact
   contains all resolved decisions and remaining open questions.
```

`spec-dock-grill-with-docs`は明示起動だけにした方がよいです。Codexでは`agents/openai.yaml`の`allow_implicit_invocation: false`によって暗黙起動を止め、明示的な`$skill`起動だけを許可できます。[![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=128)ChatGPT Learn](https://learn.chatgpt.com/codex/build-skills)

* * *

# 6\. Artifact formatはSkillへコピーしない

ユーザーが懸念している、

> SpecDockのArtifact formatを守ってほしい

という要件は重要です。

ただし、Artifact formatを`spec-dock-grill-with-docs/SKILL.md`へ全文コピーするのは避けるべきです。

そうすると、

```
Artifact format変更
    ↓
Core更新
    ↓
Docs更新
    ↓
Skill更新
    ↓
Integration更新
```

が必要になります。

代わりにSkillは、

```
SpecDock CLIでArtifactを作る
返されたPathを使う
Scope-local artifacts/rules.mdを読む
```

だけにします。

Bash

```
spec-dock new artifact interview \
  --issue iss-00123 \
  --title "Clarify refresh token behavior" \
  --format json
```

概念的な返却値です。

JSON

```
{
  "scope_id": "iss-00123",
  "kind": "interview",
  "path": "spec-dock/.../artifacts/20260807t100000z-interview-clarify-refresh-token-behavior.md",
  "rules_path": "spec-dock/.../artifacts/rules.md"
}
```

モデルは、

1.  `path`へ書く
    
2.  `rules_path`を読む
    

だけです。

これはMatt Pocock氏の`writing-for-agents`が推奨するProgressive Disclosureや、環境から容易に取得できる情報を文書へ重複コピーしないという考え方とも一致します。

* * *

# 7\. Artifactの内容はIntelligence-neutralにする

CoreのArtifact schemaに、

YAML

```
matt_skill: grill-with-docs
matt_version: ...
grilling_round: ...
```

を必須項目として入れてはいけません。

外部インテリジェンスを交換可能にするなら、ArtifactはCapability中心にします。

YAML

```
---
schema_version: 1
scope_id: iss-00123
kind: interview
status: complete
created_at: 2026-08-07T10:00:00+09:00
source:
  type: agent-skill
  workflow: grilling
---
```

Coreが要求するのは、例えば次だけです。

*   `scope_id`
    
*   `kind`
    
*   `status`
    
*   `created_at`
    

`source`は任意のProvenanceです。

本文もベンダー非依存にします。

Markdown

```
# Refresh token clarification

## Goal

## Facts established

## Decisions resolved

## Alternatives considered

## Rejected alternatives

## Open questions

## Authoring brief

### Requirement implications

### Design implications

### Plan implications
```

この構造なら、将来の外部インテリジェンスが、

*   Matt Skills
    
*   ChatGPT
    
*   Claude
    
*   DeepSeek
    
*   独自Agent
    
*   人間との会議
    

のどれであっても、同じArtifactへ記録できます。

* * *

# 8\. `CONTEXT.md`とScope-local Artifactは別の役割

`domain-modeling`は、`CONTEXT.md`を実装仕様や議事録ではなく、共有語彙のGlossaryとして扱います。ADRも、戻しにくく、背景なしでは意外で、実際のトレードオフが存在する判断だけに限定します。

したがって、Grilling結果を全部`CONTEXT.md`へ書いてはいけません。

```
Scope-local Artifact
  ├── 質問した論点
  ├── 調査したFact
  ├── 選択肢
  ├── Decision
  └── 未解決事項

CONTEXT.md
  └── 将来の全作業で共有すべき確定用語

ADR
  └── 長寿命で重要な設計判断
```

実際のContext文書をSpecDock配下へ置きたい場合は、Repository rootの`CONTEXT-MAP.md`から、SpecDock内または各Bounded Context内の`CONTEXT.md`へ参照させる方法が使えます。`domain-modeling`は、rootの`CONTEXT-MAP.md`によるMulti-context構成を想定しています。

* * *

# 9\. Grillingと仕様書作成を一つのSkillへまとめない

ここも重要です。

推奨フローは二段階です。

```
Discovery
  spec-dock-grill-with-docs
          ↓
  Scope-local Interview Artifact
          ↓
Authoring
  chatgpt-use-strict
          ↓
  requirement.md
  design.md
  plan.md
```

## Discoveryの完了条件

*   Repositoryから調査できるFactは調査済み
    
*   ユーザー判断が必要なDecisionは回答済み、または未解決として明示
    
*   Scope / Out of Scopeが理解されている
    
*   主要なAlternativeが整理されている
    
*   Requirement / Design / Planへの影響が整理されている
    
*   ユーザーがShared Understandingを確認した
    

## Authoringの入力

ChatGPT-Use Strictへ渡すのは、

*   対象Scope
    
*   Exact repository / branch / HEAD
    
*   親Initiative / Epic文書
    
*   Scope-local Interview Artifact
    
*   関連Research Artifact
    
*   Requirement / Design / Planテンプレート
    
*   Authoring Guide
    
*   関連コード・テスト
    

です。

## なぜ自動連結しないのか

`spec-dock-grill-with-docs`から`chatgpt-use-strict`を自動起動すると、次の結合が生まれます。

*   ChatGPT availability
    
*   Oracle wrapper
    
*   Browser session
    
*   User固有Project URL
    
*   Model selection
    
*   Prompt attachment方式
    

現在の`chatgpt-use`は、これらをOperator-ownedなローカル環境として扱い、回答をAdvisoryとしてRepository factsとテストで検証する設計です。

SKILL +1

したがって、Discovery SkillはArtifact生成で終え、Authoring Providerの選択は次の明示的な操作に残すべきです。

* * *

# 10\. 外部インテリジェンスを交換可能にするための安定契約

交換可能性を実現するために、SpecDockが定義するのはSkill名ではなく、次の入出力だけです。

## Discovery Input

```
- target scope
- parent chain
- canonical documents
- existing artifacts
- code and tests
- domain glossary
- ADRs
```

## Discovery Output

```
- scope-local interview/analysis artifact
- established facts
- resolved decisions
- open questions
- authoring brief
```

## Authoring Input

```
- target scope
- discovery artifacts
- parent specifications
- templates
- authoring guides
- relevant implementation context
```

## Authoring Output

```
- requirement.md
- design.md
- plan.md
- explicit information-insufficient result when authoring cannot complete
```

## Structural Mutation

```
- create node
- add dependency
- link GitHub Issue
- validate
```

これらをSpecDock CLIとファイル構造で表現します。

Coreは、

```
grilling
ChatGPT
Claude
Matt
Oracle
```

という語を知りません。

* * *

# 11\. Skill名も外部Provider名へ結合しない

Skill名を、

```
spec-dock-matt-grill-with-docs
```

にする必要はありません。

```
spec-dock-grill-with-docs
```

でよいです。

「Grilling」は実行するCapabilityを表しており、Providerを表していません。

現在はMatt Pocock氏の`grilling`と`domain-modeling`を使用しますが、将来別の実装へ切り替えても、ユーザーから見たCapabilityが同じならSkill名を維持できます。

ただし、Artifactの任意Provenanceには、

YAML

```
source:
  workflow: grilling
  implementation: mattpocock-skills
```

と記録しても構いません。

* * *

# 12\. Codex上の具体的なSkill Scope

推奨配置をまとめると次です。

```
$HOME/.agents/skills/
├── grilling/
├── domain-modeling/
├── tdd/
├── code-review/
├── diagnosing-bugs/
└── chatgpt-use-strict/
```

```
$REPO_ROOT/.agents/skills/
├── spec-dock/
└── spec-dock-grill-with-docs/
```

CodexはSkillの`name`と`description`を最初に読み、Taskと一致したときだけ完全な`SKILL.md`を読み込むProgressive Disclosureを採用しています。そのため、`spec-dock`のDescriptionには「仕様書、Artifact、Issue、Epic、Dependency、Active Scope」のようなTriggerを明確に含めるべきです。[![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=128)ChatGPT Learn](https://learn.chatgpt.com/codex/build-skills)

`spec-dock-grill-with-docs`は明示的に起動するため、暗黙起動を無効にします。

YAML

```
interface:
  display_name: "SpecDock Grill With Docs"
  short_description: "Clarify a SpecDock scope and preserve the findings"

policy:
  allow_implicit_invocation: false
```

`spec-dock`は通常、暗黙起動を有効にしてよいです。

YAML

```
interface:
  display_name: "SpecDock"
  short_description: "Use local specs, artifacts, work nodes, and dependencies"

policy:
  allow_implicit_invocation: true
```

* * *

# 13\. 同名Overrideは絶対に使わない

上流の`grill-with-docs`と同じ`name`でRepo-local Skillを作る方法は避けるべきです。

Codexの現在の公式仕様では、同名SkillはOverrideやMergeされず、両方がSkill selectorに現れる可能性があります。[![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=128)ChatGPT Learn](https://learn.chatgpt.com/codex/build-skills)

したがって、

```
grill-with-docs
```

をProject側で上書きするのではなく、

```
spec-dock-grill-with-docs
```

という一意な名前を使います。

そして上流`grill-with-docs`はインストールしません。

インストールするのは、

```
grilling
domain-modeling
```

だけです。

* * *

# 14\. 最小限のCompatibility Test

このIntegrationを重くしないため、Prompt本文のSnapshot testを大量に作る必要はありません。

次のContract testだけで十分です。

## Test 1：Scope解決

*   Explicit Issueが指定されたらそのIssueを使う
    
*   指定がなければActive Scopeを使う
    
*   複数候補で曖昧なら停止する
    

## Test 2：Artifact

*   CLI経由で一つだけArtifactを作る
    
*   返されたPathへ書く
    
*   Artifact rulesを守る
    
*   Scope外へ書かない
    

## Test 3：Canonical文書

*   Grilling中にRequirement / Design / Planを変更しない
    

## Test 4：Domain knowledge

*   Scope固有DecisionはArtifact
    
*   共有用語だけCONTEXT
    
*   ADR基準を満たす判断だけADR
    

## Test 5：Provider absence

*   `grilling`または`domain-modeling`が利用できなければ、明確に停止する
    
*   不完全なArtifactを完成扱いしない
    

これならMatt Skillsの内部プロンプトが更新されても、SpecDock Integrationは壊れません。

* * *

# 15\. 導入順序

## 第1段階

SpecDock Coreを簡素化します。

*   Storage Core
    
*   Authoring Kit
    
*   `spec-dock` Skill
    
*   既存Workflow Skills削除
    
*   ChatGPT-first Runtime削除
    
*   PR / Reviewer orchestration削除
    

## 第2段階

外部Matt Skillsとして次だけを導入します。

*   `grilling`
    
*   `domain-modeling`
    
*   `tdd`
    
*   `code-review`
    
*   `diagnosing-bugs`
    
*   必要な補助Skill
    

## 第3段階

Optional Integrationとして、

```
spec-dock-grill-with-docs
```

を追加します。

## 第4段階

ChatGPT-Use Strictとの接続を、Skill-to-Skillの自動呼出しではなく、ArtifactとAuthoring Kitによる文書契約として検証します。

* * *

# 最終提案

ユーザーの考えている「二つのSpecDock Skill」という整理は正しいです。

ただし、所有境界は次にしてください。

## SpecDock Coreが所有

```
spec-dock
```

*   常設
    
*   Repo-local
    
*   Intelligence-neutral
    
*   Storage / Graph / Authoring Kitの利用方法
    
*   Model-invoked
    

## SpecDock Optional Integrationが所有

```
spec-dock-grill-with-docs
```

*   任意
    
*   Repo-local
    
*   Explicit invocation
    
*   Scope-local Artifactへの永続化
    
*   外部`grilling`と`domain-modeling`をComposition
    
*   Canonical仕様書は作らない
    

## ユーザーまたは外部Providerが所有

```
grilling
domain-modeling
chatgpt-use-strict
```

*   User Scope
    
*   独立更新
    
*   SpecDock Coreから参照されない
    
*   容易に交換可能
    

したがって、質問への直接的な回答は次です。

> **上流の`grill-with-docs`と`spec-dock`を同時に読み込ませ、SpecDock Skillが上流Skillを上書きする構成にはしない。**
> 
> **上流`grill-with-docs`は導入せず、上流の`grilling`と`domain-modeling`を利用する独自の`spec-dock-grill-with-docs`を作る。**
> 
> **そのSkillはSpecDockのOptional Integrationとして管理し、導入先RepositoryへRepo-local Skillとして配置する。**
> 
> **Grilling結果はScope-local Artifactで終了し、Requirement / Design / Planの作成はChatGPT-Use Strictなどの交換可能な別Providerへ委ねる。**

この構造が、SpecDockの簡素さ、Matt Skillsの更新追随性、ChatGPTによる高品質Authoring、将来の外部インテリジェンス交換可能性を同時に満たします。

![](https://www.google.com/s2/favicons?domain=https://learn.chatgpt.com&sz=32)

Sources

  

#### You said:

OKです。ありがとうございました。これはスペックドック側で解釈できる、スペック側で利用できるイニシアティブとして実施しようと思っています。うん。で、それかエピックで進めるか、どちらですね。ま、これエピックで一つのエピック、複数イシューで進められるのではないかと思っています。どうでしょうか。複数エピックになるのであれば、うん、イニシアティブ、専用のイニシアティブを立てる必要があると思います。なので、このスペックドック確認して、十分に理解してもらった上で、うん。この計画書ですね。要件定義書、設計書、計画書、作成してほしいです。イニシアティブ単位で作るか、うん、イニシアティブと複数エピックか、どこかのエピックに属する、そうですね、どこかのイニシアティブに属する単独エピック、それに複数のイシューか、どのような構成が良いでしょうか、分析をしてください。ただ、これまでですね、あまりこう肥大化しすぎないようにしてほしいです。肥大化しすぎることによる大量のスロップの生成が問題だと、課題だと認識しています。必要に応じてイニシアティブを活用してください。単独エピックで収まれば単独エピック、単独エピックで収まらないのであれば、イニシアティブの作成を検討してください。

Show moreShow less

  

#### ChatGPT said:

Worked for 15m 31s

Analyzed

Python

````
from pathlib import Path
from textwrap import dedent
import zipfile

out_dir = Path("/mnt/data/spec-dock-core-simplification-epic-draft")
out_dir.mkdir(parents=True, exist_ok=True)

title = "SpecDock Core Simplification and External Intelligence Boundary"
parent = "init-local-00003"
date = "2026-08-07"

readme = dedent(f"""\
# {title} — Epic materialization guide

## Recommended hierarchy

This change should be created as **one Epic with four Issues** under the existing
`{parent} Architecture Maintenance and Hardening` Initiative.

A new Initiative is not recommended because the existing Initiative is explicitly
open-ended and already owns architecture contracts, source-of-truth boundaries,
runtime/scaffold/docs parity, and structural hardening.

Do not place this Epic under `init-00322 GPT 56 ChatGPT First Intelligence Architecture`.
That Initiative exists to automate Planning, Review, Execution, and Delivery through a
ChatGPT-first workflow. This Epic deliberately replaces that product-owned workflow with
a lightweight storage core, an authoring kit, and replaceable external intelligence.

## Proposed Epic

- Title: `{title}`
- Parent: `{parent}`
- Suggested slug: `spec-dock-core-simplification-and-external-intelligence-boundary`

Create the real Epic through SpecDock so the GitHub Issue number and canonical Epic ID
are assigned correctly:

```bash
./spec-dock/scripts/spec-dock new epic \\
  --initiative {parent} \\
  --title "{title}"
````

After creation:

1.  Replace `<EPIC_ID>` and `<GITHUB_ISSUE_NUMBER_OR_URL>` in the three draft documents.
    
2.  Copy `requirement.md`, `design.md`, and `plan.md` into the returned Epic directory.
    
3.  Add this Epic to the parent Initiative plan as the current architecture-simplification Epic.
    
4.  Create the four Issues listed in `plan.md` through the SpecDock CLI.
    
5.  Register the dependency edges from `plan.md`.
    
6.  Run `validate` and `sync`.
    

## Baseline used for this draft

*   Repository: `chemitaro/spec-dock`
    
*   Branch: `main`
    
*   Reviewed HEAD: `ecdac90d157ac3bc3680bca833d7bdf88e46de45`
    
*   Date reviewed: `{date}`
    

## Scope discipline

This bundle intentionally avoids:

*   a new Initiative;
    
*   multiple Epics;
    
*   a separate planning-only Issue;
    
*   a separate final-quality Issue;
    
*   detailed file-by-file implementation steps at Epic level.
    

The four Issues are the minimum coherent slices:

1.  Storage Core runtime reduction.
    
2.  Authoring Kit simplification.
    
3.  Two-skill integration boundary.
    
4.  Distribution cutover, migration, and legacy retirement.  
    """)
    

## requirement = dedent(f"""\\

## 種別: 要件定義書（Epic）  
ID: "<EPIC\_ID>"  
タイトル: "{title}"  
関連GitHub: \["<GITHUB\_ISSUE\_NUMBER\_OR\_URL>"\]  
状態: "draft"  
作成者: "ChatGPT"  
最終更新: "{date}"  
親: \["{parent}"\]

# <EPIC\_ID> {title} — 要件定義（何を、なぜ行うか）

## 1\. 目的

### Initiativeとの紐づき

`{parent} Architecture Maintenance and Hardening` が扱う構造健全性、source-of-truth、  
runtime/scaffold/docs parity、運用可能性の改善として、SpecDockを次の二つへ縮退する。

1.  **Storage Core**
    
    *   Initiative / Epic / Issueのローカル階層
        
    *   GitHub Issue linkage
        
    *   Scope-local Artifact
        
    *   direct dependency DAG
        
    *   active scope
        
    *   validate / sync / projection
        
    *   deterministicな構造操作
        
2.  **Authoring Kit**
    
    *   Initiative / Epic / Issueの`requirement.md`
        
    *   `design.md`
        
    *   `plan.md`
        
    *   Artifact rules
        
    *   各文書の役割、品質基準、書き方を説明するガイド
        

### このEpicが提供する能力

*   SpecDockが開発ワークフローを所有せず、任意の高性能モデルや外部Skillから利用できる。
    
*   仕様書、分析記録、Issue階層、依存関係は引き続きローカルGit管理下に残る。
    
*   外部インテリジェンスを変更しても、SpecDockのデータ構造と文書を再設計せずに済む。
    
*   SpecDock自身が配布するAgent Skillは、Storage Coreを利用する`spec-dock`と、  
    明示的な対話用`spec-dock-grill-with-docs`の二つに限定される。
    
*   ChatGPT-Use Strict、Matt Pocock Skills、Codex GoalなどはOperator-ownedな外部能力として利用できる。
    

## 2\. 背景

現在のSpecDockは、ローカル仕様書と依存グラフに加えて、次の認知・運用ワークフローまで  
製品内部で所有している。

*   Initiative / Epic / Issue Planning Skill
    
*   Issue / Epic Execution Skill
    
*   Clarification workflow
    
*   Assurance gradeとresource allocation
    
*   phase promotionとfresh reviewer gate
    
*   delegated authoringとEvidence Adoption Ledger
    
*   ChatGPT-first Candidate / Review / Revision / Human Decision / Apply
    
*   `spec-dock-chatgpt`
    
*   PR creation / observation / merge preparation
    
*   named sub-agent roleとhost adapter
    
*   workflow guidance / runbook
    

これらはモデル能力、ハーネス、外部UI、レビュー方法の変化を直接受けるため、  
Storage Coreよりも高い頻度で更新が必要になる。結果として、仕様書管理と依存関係管理を  
維持するためにも、大量のworkflow docs、Skill、runtime、test、projectionを同時に  
保守しなければならない。

一方、実運用では、仕様書作成から実装までを完全自動化すると、過剰分割、過剰な証跡、  
大量の低価値文書、形式的に整っていても価値の低い実装が生成される問題が確認された。  
現時点では、高認知負荷の仕様作成をChatGPTのfrontier modelへ明示的に委任し、  
Codexがローカルで反映・実装する構成の方が実用的である。

## 3\. 基本原則

### E-RQ-001 Storage Coreを製品境界とする

SpecDock Coreは次だけを所有する。

*   node identityとdirectory hierarchy
    
*   GitHub Issue linkage
    
*   canonical local documents
    
*   Scope-local Artifact
    
*   dependency storageとDAG validation
    
*   readiness projection
    
*   active scopeとIssue lifecycle primitive
    
*   validate / sync / update / uninstall
    
*   optionalなworkbench / worktree utility
    

Coreはモデル、Prompt、Reviewer、Oracle、ChatGPT Project、特定Skill名を知らない。

### E-RQ-002 Authoring Kitを保持する

Initiative / Epic / Issueの`requirement.md`、`design.md`、`plan.md`について、  
次を丁寧に説明するテンプレートとガイドを残す。

*   各文書が答える問い
    
*   Scopeごとの責務
    
*   文書間の境界
    
*   受け入れ条件とEdge caseの書き方
    
*   設計境界、契約、図表の選び方
    
*   実装順序、テスト、検証、rollbackの書き方
    
*   Artifactからcanonical documentへ整理する考え方
    

テンプレートは実文書に残る最小scaffoldとし、詳細説明はAuthoring Guideへ置く。

### E-RQ-003 Workflow gateをAuthoring Kitから除去する

次を仕様書作成の必須条件またはCore authorityとして扱わない。

*   fresh reviewer pass
    
*   phase promotion
    
*   Assurance grade
    
*   specialist使用義務
    
*   Evidence Adoption Ledger
    
*   delegated draft evidence
    
*   Human Decision JSON
    
*   Candidate ZIP
    
*   manual fallback state machine
    
*   PR readiness / merge-prepared state
    

既存文書の履歴は保持するが、新しいテンプレートとガイドから旧workflow authorityを除去する。

### E-RQ-004 構造の厳密さだけを維持する

モデルがMarkdownを直接編集できる一方、次の構造変更はSpecDock CLIだけが行う。

*   node作成、close、delete
    
*   hierarchy
    
*   dependency add / remove
    
*   GitHub Issue linkage
    
*   generated projection
    

Coreは自己依存、循環依存、不正なancestor / descendant dependency、重複identity、  
Scope外pathへの構造変更を拒否する。

### E-RQ-005 Agent Skillを二つに限定する

SpecDockがmanaged assetとして配布するSkillは次の二つだけとする。

1.  `spec-dock`
    
    *   Model-invoked
        
    *   Scope、canonical documents、Artifact、node、dependency、CLIの利用方法を提供する
        
    *   開発ワークフローを規定しない
        
2.  `spec-dock-grill-with-docs`
    
    *   User-invoked
        
    *   explicit / active Scopeを解決する
        
    *   Scope-local Artifactを作る
        
    *   外部の`grilling`と`domain-modeling`能力を利用する
        
    *   Fact、Decision、Alternative、Open Question、Authoring BriefをArtifactへ残す
        
    *   canonical `requirement.md` / `design.md` / `plan.md`を自動作成しない
        

`spec-dock-grill-with-docs`は明示起動専用とし、外部能力が存在しない場合は明確に停止する。  
外部Skill本体はSpecDockへ同梱しない。

### E-RQ-006 外部インテリジェンスを交換可能にする

SpecDockは次を外部から利用できるが、依存しない。

*   ChatGPT-Use Strict
    
*   Matt Pocock Skills
    
*   Codex Goal
    
*   将来の別Agent / model / skill set
    

外部能力との契約は、Scope、local documents、Artifact、CLI、Git repositoryだけで表す。  
外部Provider固有の設定、model名、browser session、wrapper pathをSpecDock Coreへ保存しない。

### E-RQ-007 `to-spec`と`to-tickets`を採用しない

Matt Pocock Skillsを利用する場合も、次はSpecDock標準フローへ導入しない。

*   `to-spec`
    
*   `to-tickets`
    
*   それらを前提とする`ask-matt`
    
*   GitHub label state machineを持つ`triage`
    
*   tracker固有前提の強い`wayfinder`
    

仕様書はSpecDock Authoring Kitを参照して作成し、Issueと依存関係はSpecDock CLIで作成する。

### E-RQ-008 Product-owned ChatGPT workflowを撤去する

次をSpecDockから削除する。

*   `spec-dock-chatgpt`
    
*   ChatGPT Planning create / review / revise / apply
    
*   Candidate / Review / Human Decision contract
    
*   Oracle-specific runtime boundary
    
*   ChatGPT-first planning Skills
    
*   ChatGPT-specific workflow docsとtests
    

Operator-ownedなChatGPT-Use StrictはSpecDock外で維持し、必要な場合だけ利用する。

### E-RQ-009 既存データを保持する

Cutover時に次を自動変換・削除しない。

*   `spec-dock/initiatives/**`
    
*   canonical requirement / design / plan / report
    
*   historical artifacts / discussions
    
*   accepted ADR
    
*   `.meta.json.depends_on`
    
*   GitHub linkage
    
*   Workbenchのunmanaged content
    

旧workflow固有の既存記録はhistorical evidenceとして残せるが、新Coreはその状態を  
readiness authorityとして解釈しない。

### E-RQ-010 Managed assetを確実に整理する

`init`は新しい最小構成だけを導入し、`update`は旧SpecDockが管理していた次のassetを  
安全にpruneする。

*   planning / execution / clarification / authoring Skills
    
*   PR observation / creation / merge Skills
    
*   host adapterとnamed agent role
    
*   product-owned ChatGPT runtime
    
*   workflow / assurance / delegated authoring command surface
    
*   stale docs、templates、tests、native shims
    

User-owned fileとunmanaged Skillは削除しない。

### E-RQ-011 外部自動化を製品要件にしない

本Epicでは、仕様作成から実装完了までの完全自動化を提供しない。

代表的な利用例は次とする。

1.  `spec-dock-grill-with-docs`で論点を明確化しArtifactへ保存する。
    
2.  ChatGPT-Use Strict等で仕様書を作成する。
    
3.  Codexがlocal canonical documentsへ反映する。
    
4.  `/goal`と外部実装SkillでIssueを完了する。
    
5.  SpecDockは文書、Issue、依存関係、状態を保持する。
    

### E-RQ-012 変更容易性を成功条件に含める

新しい外部インテリジェンスを導入するとき、SpecDock Coreのruntime、metadata schema、  
Authoring Kitを変更せず、Repo-local SkillまたはOperator-owned Skillだけで接続できること。

## 4\. エピック受け入れ条件

### E-AC-001 Fresh install

*   `spec-dock init`後、Storage Core、Authoring Kit、`spec-dock`、  
    `spec-dock-grill-with-docs`だけがSpecDock managed Skillとして存在する。
    
*   Planning / Execution / PR / ChatGPT workflow Skillは導入されない。
    
*   `validate`が成功する。
    

### E-AC-002 Core command surface

*   node、artifact、dependency、active、issue lifecycle、sync、validate、update、uninstallの  
    必要な操作が利用できる。
    
*   `assurance`、`authoring`、`delegated-authoring`、`workflow/guidance`、  
    `spec-dock-chatgpt`は公開command surfaceに存在しない。
    

### E-AC-003 Local document authority

*   Initiative / Epic / Issueの仕様書はローカルnode directoryに存在する。
    
*   GitHub Issue本文はcanonical specificationとして要求されない。
    
*   外部Agentがcurrent local documentsを直接参照できる。
    

### E-AC-004 Dependency graph

*   Issue / Epic dependencyを登録・削除・照会できる。
    
*   cycleとinvalid edgeは保存前に拒否される。
    
*   `sync`がmachine-readable graphと人間向け可視化を生成する。
    

### E-AC-005 Authoring Kit

*   Requirement / Design / Planのテンプレートとガイドから旧workflow gateが除去されている。
    
*   各文書の役割と品質基準は、特定modelやSkillに依存せず理解できる。
    
*   Templateは詳細説明を過剰に複製しない。
    

### E-AC-006 Skill boundary

*   `spec-dock`はStorage Coreの利用方法だけを提供し、別workflowを開始しない。
    
*   `spec-dock-grill-with-docs`はScope-local Artifactを作成し、対話結果を保存する。
    
*   Grilling中にcanonical Requirement / Design / Planを自動変更しない。
    
*   外部Skill不在はCore利用を妨げない。
    

### E-AC-007 Existing consumer update

*   `spec-dock update`が既存node、文書、Artifact、dependency、Workbench contentを保持する。
    
*   旧managed workflow assetだけをpruneする。
    
*   更新後に`validate`と`sync`が成功する。
    

### E-AC-008 External intelligence smoke

次の手動smokeが成立する。

1.  `spec-dock-grill-with-docs`でScope Artifactを作成する。
    
2.  Operator-owned ChatGPT-Use StrictでAuthoring Kitを参照し、三文書を作成する。
    
3.  Codexが文書を反映し、`validate`を通す。
    
4.  Codex GoalからIssueのPlanに沿って実装できる。
    

このsmokeを外部Providerの自動E2E testとして製品へ固定しない。

### E-AC-009 Legacy retirement

*   `init-00322`のChatGPT-first automation方針はsupersededとして扱われる。
    
*   Historical local documentsは保持する。
    
*   Openなlegacy implementation Issueは重複実装を防ぐため整理される。
    
*   新しいSpecDock READMEとguideがStorage Core + Authoring Kitを主要製品境界として説明する。
    

## 5\. スコープ

### 必須

*   Runtime command registryとdomain/application/infraの縮退
    
*   Installer managed assetの縮退
    
*   Authoring Kitの再構成
    
*   二つのSpecDock Skill
    
*   update / uninstall時のobsolete cleanup
    
*   provider / dogfood / installed consumerの整合
    
*   testsとmigration / cutover docs
    
*   旧ChatGPT-first / workflow surfaceのretirement
    

### 禁止

*   新しいworkflow engineを別名で再実装する
    
*   Matt Pocock SkillsまたはChatGPT-Use StrictをSpecDock Coreへvendorする
    
*   外部SkillのPromptやversionをCore schemaへ埋め込む
    
*   既存node treeを一括書換えする
    
*   GitHub Issue本文を仕様の正本へ変更する
    
*   自動化を維持するための新しいstate DB、receipt DB、review DBを作る
    

### 対象外

*   ChatGPT-Use Strict Skillそのものの実装
    
*   Matt Pocock Skillsの配布・更新機構
    
*   `to-spec` / `to-tickets`互換Adapter
    
*   完全自律Runner
    
*   Web UI
    
*   新しいdocument profileへの全面移行
    
*   既存historical documentsの内容修正
    

## 6\. 非機能要件

### 軽量性

*   Coreの公開概念とmanaged Skill数を減らす。
    
*   Model-facing instructionはProgressive Disclosureを使い、CLI helpとAuthoring Guideを  
    source of truthとする。
    
*   旧workflow語彙を新Skillやtemplateへ複製しない。
    

### 信頼性

*   Markdown編集の自由度を高めても、node graphとdependency graphの構造安全性は維持する。
    
*   `update`はmanaged assetだけを変更し、user dataを保持する。
    
*   Partial cleanup時は対象pathと残存assetを診断できる。
    

### 互換性

*   Data compatibilityを優先する。
    
*   Workflow compatibilityは提供しない。
    
*   旧command / Skill aliasを恒久的に残さない。
    
*   Rollbackは旧workflowへのruntime fallbackではなく、Git revertまたは旧releaseへの  
    明示的なversion rollbackとする。
    

### セキュリティ

*   External providerのcredential、cookie、browser profile、private wrapper pathを  
    SpecDockへ取り込まない。
    
*   Artifactとdocument pathはRepository境界外へescapeできない。
    
*   External outputはRepository factsとtestsで検証してから採用する。
    

## 7\. 依存と影響範囲

### 主な影響領域

*   `src/spec_dock/cli.py`
    
*   `src/spec_dock/assets/install_root/.agents/`
    
*   `src/spec_dock/assets/install_root/.codex/`
    
*   `src/spec_dock/assets/install_root/.github/`
    
*   `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
    
*   `src/spec_dock/assets/spec_dock/docs/`
    
*   `src/spec_dock/assets/spec_dock/templates/`
    
*   dogfooding projectionである`.agents/`、`.codex/`、`spec-dock/`
    
*   installer / runtime / parity / consumer tests
    

### 外部依存

*   Coreには新しい外部dependencyを追加しない。
    
*   `spec-dock-grill-with-docs`利用時だけ、外部の`grilling`と`domain-modeling`が必要。
    
*   ChatGPT-Use StrictはOperator-owned optional dependency。
    

## 8\. 後続Issue seed

*   **Reduce Runtime to Storage Core**
    
    *   workflow / assurance / ChatGPT / delegated authoring surfaceを削除し、  
        deterministic core commandだけを残す。
        
*   **Simplify Authoring Kit and Document Contracts**
    
    *   Requirement / Design / Plan templatesとauthoring docsから旧workflow gateを除去し、  
        intelligence-neutralな品質基準へ再構成する。
        
*   **Replace Managed Workflow Skills with SpecDock Skills**
    
    *   `spec-dock`と`spec-dock-grill-with-docs`を実装し、他のmanaged Skillとagent roleを削除する。
        
*   **Cut Over Distribution and Retire Legacy Workflow Surfaces**
    
    *   init/update/uninstall、obsolete cleanup、docs、tests、dogfood、legacy initiative retirement、  
        release cutoverを完了する。
        

## 9\. 未確定事項

なし。

本EpicはStorage Core + Authoring Kitへのhard cutoverを採用する。  
旧workflowと新境界の恒久的なdual modeは提供しない。  
""")

## design = dedent(f"""\\

## 種別: 設計書（Epic）  
ID: "<EPIC\_ID>"  
タイトル: "{title}"  
関連GitHub: \["<GITHUB\_ISSUE\_NUMBER\_OR\_URL>"\]  
状態: "draft"  
作成者: "ChatGPT"  
最終更新: "{date}"  
依存: \["requirement.md"\]  
親: \["{parent}"\]

# <EPIC\_ID> {title} — 設計（どう実現するか）

## 1\. 設計判断

### D-001 単独Epicとして実施する

本変更はSpecDock自身のarchitecture boundaryを縮小する一つのcoherent contractである。  
既存の`{parent}`はopen-endedなarchitecture initiativeであり、新規Initiativeを作らない。

`init-00322 GPT 56 ChatGPT First Intelligence Architecture`は本変更の親にしない。  
同InitiativeはPlanningからDeliveryまでの自動化を目標とし、本Epicの「製品所有workflowを撤去する」  
方向と矛盾するため、cutover時のsupersede対象とする。

### D-002 Storage CoreとAuthoring Kitを別の責務として残す

```
External Intelligence
  ├── ChatGPT-Use Strict
  ├── Matt Pocock Skills
  ├── Codex Goal
  └── future providers
          │
          ▼
Repo-local Skills
  ├── spec-dock
  └── spec-dock-grill-with-docs
          │
          ▼
SpecDock
  ├── Storage Core
  └── Authoring Kit
```

Storage Coreはstateとinvariantを、Authoring Kitは文書の意味と品質基準を所有する。  
外部インテリジェンスは交換可能なClientであり、Coreのdependencyではない。

### D-003 認知的自由と構造的安全を分離する

*   Markdown:
    
    *   Agentが直接読取り・編集できる。
        
*   Structure:
    
    *   node、hierarchy、dependency、GitHub linkage、projectionはCLIだけが変更する。
        
*   Workflow:
    
    *   SpecDockは規定しない。
        
*   Validation:
    
    *   ファイル構造とgraph invariantだけを決定的に検証する。
        

## 2\. 対象アーキテクチャ

### 2.1 Storage Core

#### Node graph

*   Initiative
    
*   Epic
    
*   Issue
    
*   stable ID
    
*   parent chain
    
*   GitHub Issue linkage
    

#### Knowledge storage

*   canonical `requirement.md`
    
*   canonical `design.md`
    
*   canonical `plan.md`
    
*   optional `report.md`
    
*   Scope-local `artifacts/`
    
*   accepted ADR
    
*   optional Workbench
    

#### Work graph

*   `.meta.json.depends_on`
    
*   add / remove / check
    
*   cycle validation
    
*   ready / blocked / indeterminate projection
    
*   `index*.json`
    
*   `tree*.json`
    
*   dependency JSON / PlantUML
    
*   dashboard
    

#### Lifecycle and utility

*   `new`
    
*   `import`
    
*   `close`
    
*   `delete`
    
*   `active`
    
*   `issue start`
    
*   `issue finish`
    
*   `worktree`
    
*   `workbench`
    
*   `sync`
    
*   `validate`
    
*   `doctor`
    
*   `update`
    
*   `uninstall`
    

WorktreeとWorkbenchはworkflowではなく、isolation / staging primitiveとして残す。

### 2.2 削除するRuntime surface

Runtime registryから次を削除する。

*   `assurance`
    
*   `authoring`
    
*   `delegated_authoring`
    
*   `workflow` / `guidance`
    
*   product-owned ChatGPT planning / review / revise / apply
    
*   workflow state / runbook / context routing
    
*   reviewer / specialist / grade interpretation
    

対応するdomain、application、infra、presentation、parser、wrapper、testsも削除する。  
Core側にdeprecated aliasやautomatic fallbackを残さない。

### 2.3 Authoring Kit

推奨ディレクトリ概念:

```
spec-dock/
├── templates/
│   ├── initiative/
│   ├── epic/
│   └── issue/
└── docs/
    ├── authoring/
    │   ├── overview.md
    │   ├── requirement.md
    │   ├── design.md
    │   ├── plan.md
    │   ├── scope-layering.md
    │   └── artifacts.md
    └── reference/
```

既存pathを大きく変更する必要はない。重要なのは、文書の意味をworkflow gateから分離すること。

#### Canonical authority

*   `requirement.md`: 何を、なぜ、どの条件で達成するか
    
*   `design.md`: どの境界、契約、構造で実現するか
    
*   `plan.md`: どの順序、検証、完了条件で実装するか
    

#### Evidence

*   `artifacts/`: 分析、調査、Interview、Review、Alternative、外部出力
    
*   `report.md`: 任意の簡潔な実行・結果記録。必須state machineにしない
    
*   Workbench: disposable staging
    

#### Template方針

Templateには完成文書に残る見出しと短い説明だけを置く。  
詳細な例、判断基準、optional section、diagram catalogはAuthoring Guideへ置く。

削除する語彙:

*   grade
    
*   reviewer gate
    
*   promotion
    
*   EAL
    
*   delegated evidence
    
*   fallback evidence
    
*   merge-prepared
    
*   execution-ready state machine
    

## 3\. Skill設計

### 3.1 `spec-dock`

#### Invocation

*   Model-invoked
    
*   Repository Scope
    
*   SpecDock managed Skill
    

#### 責務

*   explicit / active Scopeの解決
    
*   parent chain、canonical docs、Artifact、dependencyの案内
    
*   Markdownは直接編集可能であることを伝える
    
*   structure mutationはCLIへ誘導する
    
*   Authoring KitとCLI helpへのcontext pointerを提供する
    
*   invoking workflowを優先する
    

#### 非責務

*   Planning / Review / Implementation workflow
    
*   ChatGPT呼出し
    
*   Matt Skillの起動
    
*   reviewer選択
    
*   PR delivery
    

Skill本文にCLI syntax、Artifact schema、template全文を複製せず、current local help / rulesへ誘導する。

### 3.2 `spec-dock-grill-with-docs`

#### Invocation

*   User-invoked
    
*   `allow_implicit_invocation: false`
    
*   Repository Scope
    
*   SpecDock managed integration Skill
    

#### 外部能力

現在の実装は外部の次を利用する。

*   `grilling`
    
*   `domain-modeling`
    

これらをSpecDockへvendorしない。存在しない場合は、不完全な独自代替を実行せず、必要能力が  
利用できないことを明示して停止する。

#### 処理

1.  explicit Scope、なければactive Scopeを解決する。
    
2.  Scope、parent docs、existing artifacts、関連code / tests、CONTEXT / ADRを読む。
    
3.  SpecDock CLIで`interview`または`analysis` Artifactを一つ作る。
    
4.  返されたpathとrulesを使用する。
    
5.  `grilling`と`domain-modeling`でFact / Decisionを解決する。
    
6.  Artifactへ次を簡潔に残す。
    
    *   Goal
        
    *   Facts established
        
    *   Decisions resolved
        
    *   Alternatives considered
        
    *   Rejected alternatives
        
    *   Open questions
        
    *   Authoring brief
        
7.  Shared termだけをCONTEXTへ反映する。
    
8.  ADR基準を満たす判断だけADR化する。
    
9.  canonical Requirement / Design / Planは自動作成しない。
    
10.  Userがshared understandingを確認した時点で完了する。
    

#### Provider neutrality

Skill名とArtifact本文はCapability中心にする。  
Core metadataへMatt固有versionを必須化しない。任意provenanceのみ許可する。

## 4\. 外部Authoring境界

### 4.1 ChatGPT-Use Strict

Operator-owned SkillとしてSpecDock外に置く。

概念フロー:

```
Codex
  ├── Scopeと関連pathを解決
  ├── branchをpush
  └── exact repository / branch / HEADを確定
          │
          ▼
ChatGPT-Use Strict
  ├── GitHubからexact branchを読む
  ├── Authoring Kitを読む
  ├── parent docs / artifacts / code / testsを読む
  └── complete requirement / design / planを返す
          │
          ▼
Codex
  ├── local canonical docsへ反映
  ├── diffとrepository factsで検証
  └── validate / tests / commit
```

SpecDockはwrapper、browser、model、session、attachment、result schemaを所有しない。

### 4.2 External development skills

*   TDD、debugging、code review等はlocal canonical docsを入力として利用できる。
    
*   `to-spec` / `to-tickets`を標準導入しない。
    
*   Issue作成とdependency mutationはCodexがSpecDock CLIで行う。
    

## 5\. Distribution設計

### 5.1 Managed Skill

`_MANAGED_SKILL_NAMES`相当は二つだけにする。

```
spec-dock
spec-dock-grill-with-docs
```

旧managed Skill、host adapter、named Agent role、consumer向けPR workflow assetをobsolete inventoryへ移す。

### 5.2 Installer

*   `init`: 最小assetだけを導入する。
    
*   `update`: managed dataをrefreshし、obsolete managed workflow assetをpruneする。
    
*   `uninstall`: 新しいinventoryとlegacy inventoryの両方を安全に除去できる。
    
*   User-owned `.agents/skills/*`、`.codex/*`、`.github/*`を誤削除しない。
    
*   provider sourceとdogfood projectionの二重管理が必要な範囲を縮小する。
    

### 5.3 Existing workspace

*   node treeとdocumentsはin-placeで保持する。
    
*   `.assurance.json`等の旧workflow metadataはhistorical unmanaged dataとして残すか、  
    明示的なobsolete managed fileだけを削除する。
    
*   既存`report.md`とArtifactを書換えない。
    
*   新Coreは旧gate stateを解釈しない。
    

## 6\. Migration / Cutover

### Hard cutover

Workflow compatibilityを残さない。

1.  New Core / Authoring Kit / Skillsを同一releaseへ揃える。
    
2.  Fresh consumerでinit smokeを行う。
    
3.  Existing consumerでupdate preservation / prune smokeを行う。
    
4.  Dogfood repositoryを新構成へ更新する。
    
5.  旧command、Skill、agent role、docs pointerの残存を検査する。
    
6.  `init-00322`と未完了child workをsupersededとして整理する。
    
7.  Major versionまたは明確なbreaking release noteで公開する。
    

### Rollback

*   Git revert
    
*   旧releaseへの明示的version rollback
    
*   backupからmanaged assetを復元
    

新Core内に旧workflow fallbackを残さない。

## 7\. データフロー

plantuml

```
@startuml
skinparam monochrome true
left to right direction

actor User
component "External Intelligence" as External
component "spec-dock Skill" as Skill
component "spec-dock-grill-with-docs" as Grill
component "Authoring Kit" as Kit
component "Storage Core CLI" as Core
database "Local Spec Graph" as Graph
cloud "GitHub Issues" as GitHub

User --> External
User --> Grill
Grill --> Skill
Grill --> Core : create Artifact
Grill --> Graph : write Artifact
External --> Kit : read templates and guides
External --> Graph : read via GitHub or local handoff
Skill --> Core
Core --> Graph
Core --> GitHub : linkage and lifecycle
@enduml
```

## 8\. 失敗設計

### External Skillがない

*   `spec-dock-grill-with-docs`だけが明確に停止する。
    
*   Storage Coreと`spec-dock` Skillは通常利用できる。
    

### External providerが利用不能

*   SpecDockは影響を受けない。
    
*   Codexまたは別ProviderでAuthoring Kitを使用できる。
    

### Update途中のobsolete cleanup failure

*   User dataを変更しない。
    
*   removed / remaining managed pathsを構造化して返す。
    
*   retry可能なcleanupを案内する。
    

### Historical docsが旧workflow語彙を含む

*   Historical evidenceとして保持する。
    
*   current template / guide / Skillから参照しない。
    
*   一括rewriteしない。
    

## 9\. テスト戦略

### Core

*   node / hierarchy / identity
    
*   dependency DAG
    
*   artifact path safety
    
*   active / issue lifecycle
    
*   sync / projection
    
*   update / uninstall preservation
    

### Removed surface

*   public parser / registryに旧commandがない
    
*   packaged assetsに旧Skill / role / wrapperがない
    
*   current docsに旧workflow entrypointがない
    
*   `rg` / inventory regressionで再混入を検出する
    

### Authoring Kit

*   provider / installed / dogfood parity
    
*   templatesに旧gate語彙がない
    
*   guideがRequirement / Design / Planの役割を説明する
    
*   templateが過剰なpolicy cacheになっていない
    

### Skills

*   `spec-dock`がworkflowを開始しない
    
*   `spec-dock-grill-with-docs`が一つのScope Artifactを使う
    
*   canonical docsを自動変更しない
    
*   external dependency absenceを明確に扱う
    

### Consumer smoke

*   fresh init
    
*   existing update
    
*   uninstall / reinstall
    
*   node + artifact + deps + validate + sync
    
*   manual external intelligence smoke
    

## 10\. 未確定事項

なし。  
""")

## plan = dedent(f"""\\

## 種別: 計画書（Epic）  
ID: "<EPIC\_ID>"  
タイトル: "{title}"  
関連GitHub: \["<GITHUB\_ISSUE\_NUMBER\_OR\_URL>"\]  
状態: "draft"  
作成者: "ChatGPT"  
最終更新: "{date}"  
依存: \["requirement.md", "design.md"\]  
親: \["{parent}"\]

# <EPIC\_ID> {title} — 計画（Issue と実施順序）

## 1\. 計画方針

### Epic classification

*   `multi-issue implementation`
    
*   単独Epic
    
*   Issue数: 4
    
*   専用のfinal-quality Issue: 作らない
    
*   Epic全体のintegration、migration、final verificationは最後のCutover Issueへ含める
    

### 分割原則

*   技術レイヤーではなく、独立して検証可能な契約単位で分割する。
    
*   Planning-only Issue、Review-only Issue、Metrics-only Issueを作らない。
    
*   Core、Authoring Kit、Skill Integrationは責務が異なるため分離する。
    
*   Installer / migration / dogfoodは横断統合であるため最後のIssueにまとめる。
    
*   既存historical nodeや文書の一括変換Issueを作らない。
    

## 2\. Issue一覧

実際のIDはSpecDock CLIとGitHub Issue作成後に確定する。

### I1 Reduce Runtime to Storage Core

#### 目的

SpecDock runtimeから認知・運用workflowを削除し、Storage Coreの決定的操作だけを残す。

#### 成果物

*   target command registry
    
*   retained core domain / application / infra
    
*   removed workflow / assurance / authoring / ChatGPT modules
    
*   core-only CLI help
    
*   focused core regression
    
*   removal inventory
    

#### 主な範囲

*   `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
    
*   runtime parser / registry / wrappers
    
*   dogfood runtime projection
    
*   corresponding tests
    

#### 完了条件

*   node、artifact、deps、active、issue lifecycle、sync、validate、update、uninstallが動作する。
    
*   workflow / assurance / delegated authoring / product ChatGPT commandが存在しない。
    
*   existing node treeとdependency storage formatを変更しない。
    
*   Core testが成功する。
    

#### 依存

*   なし
    

* * *

### I2 Simplify Authoring Kit and Document Contracts

#### 目的

Requirement / Design / Planの丁寧な作成方法を維持しつつ、旧workflow gateと  
provider-specificな義務を除去する。

#### 成果物

*   simplified Initiative / Epic / Issue templates
    
*   authoring overview
    
*   requirement guide
    
*   design guide
    
*   plan guide
    
*   scope layering guide
    
*   artifact guide
    
*   optional report semantics
    
*   old workflow docsの削除または非current化
    
*   template / docs regression
    

#### 主な範囲

*   `src/spec_dock/assets/spec_dock/templates/`
    
*   `src/spec_dock/assets/spec_dock/docs/`
    
*   dogfood template / docs projection
    
*   README / guide
    

#### 完了条件

*   Templateにgrade、reviewer gate、EAL、promotion、fallback、PR readinessが残っていない。
    
*   Guideが各文書の役割、品質、Scope差を説明する。
    
*   Templateは最小scaffoldであり、詳細説明はGuideに集約される。
    
*   Intelligence provider名やmodel名に依存しない。
    

#### 依存

*   なし
    
*   I1と並行可能
    

* * *

### I3 Replace Managed Workflow Skills with SpecDock Skills

#### 目的

現在の多数のmanaged Skill / adapter / roleを、二つのRepo-local Skillへ置き換える。

#### 成果物

*   `spec-dock`
    
*   `spec-dock-grill-with-docs`
    
*   Codex `agents/openai.yaml`
    
*   required external capabilityの明示
    
*   managed Skill inventory縮小
    
*   obsolete Skill / host adapter / named role removal
    
*   integration contract tests
    

#### `spec-dock`の完了条件

*   Scope、canonical docs、Artifact、node、dependencyをモデルへ案内する。
    
*   structure mutationはCLIへ誘導する。
    
*   invoking workflowを優先し、Planning / Review / Implementationを規定しない。
    
*   current Authoring KitとCLI helpをpointerで参照する。
    

#### `spec-dock-grill-with-docs`の完了条件

*   explicit / active Scopeを解決する。
    
*   Scope-local Artifactを一つ作成する。
    
*   外部`grilling` / `domain-modeling`を利用する。
    
*   Fact、Decision、Alternative、Open Question、Authoring Briefを記録する。
    
*   canonical Requirement / Design / Planを自動変更しない。
    
*   missing external capabilityを明確に報告する。
    
*   implicit invocationを無効にする。
    

#### 依存

*   I1
    
*   I2
    

* * *

### I4 Cut Over Distribution and Retire Legacy Workflow Surfaces

#### 目的

Provider、fresh consumer、existing consumer、dogfoodを新境界へ揃え、旧workflowを  
安全にretireする。

#### 成果物

*   installer `init` inventory
    
*   `update` obsolete cleanup
    
*   `uninstall` inventory
    
*   provider / dogfood / installed parity
    
*   fresh consumer smoke
    
*   existing consumer preservation smoke
    
*   release / migration documentation
    
*   legacy command / Skill / role / docs pointer absence checks
    
*   manual external intelligence smoke
    
*   `init-00322` supersede / closure plan
    
*   mergeable delivery
    

#### 完了条件

*   Fresh initがStorage Core、Authoring Kit、二つのSkillだけを導入する。
    
*   Existing updateがnode、docs、Artifact、dependency、Workbench contentを保持する。
    
*   旧managed workflow assetが残らない。
    
*   Full Core regression、lint、validate、syncが成功する。
    
*   次の手動シナリオを確認する。
    
    1.  Scope作成
        
    2.  Artifact作成
        
    3.  dependency登録
        
    4.  `spec-dock-grill-with-docs`
        
    5.  ChatGPT-Use Strict等で三文書作成
        
    6.  Codex GoalでIssue実装
        
*   Historical `init-00322` dataは保持され、current workflowとして参照されない。
    
*   Breaking changeとmigration boundaryがREADME / release noteに明記される。
    

#### 依存

*   I1
    
*   I2
    
*   I3
    

## 3\. 依存グラフ

plantuml

```
@startuml
skinparam monochrome true
left to right direction

rectangle "I1\nReduce Runtime to Storage Core" as I1
rectangle "I2\nSimplify Authoring Kit" as I2
rectangle "I3\nReplace Managed Skills" as I3
rectangle "I4\nCut Over and Retire Legacy" as I4

I1 --> I3 : blocks
I2 --> I3 : blocks
I1 --> I4 : blocks
I2 --> I4 : blocks
I3 --> I4 : blocks
@enduml
```

SpecDock dependency direction:

```
I3 depends_on I1
I3 depends_on I2
I4 depends_on I1
I4 depends_on I2
I4 depends_on I3
```

CLI適用時は、dependentを`--from`、prerequisiteを`--to`にする。

## 4\. 実施順序

### Lane A

1.  I1 Storage Core
    
2.  I3 Skills
    
3.  I4 Cutover
    

### Lane B

1.  I2 Authoring Kit
    
2.  I3との統合
    
3.  I4 Cutover
    

I1とI2は並行可能。I3は両方のstable contractを参照する。I4が唯一の横断統合Issueとなる。

## 5\. Issue handoff共通条件

各Issueは次を継承する。

*   Parent EpicのRequirement / Design / Planを変更せず、必要な変更はEpicへ戻す。
    
*   Existing `spec-dock/initiatives/**` dataを一括変換しない。
    
*   Provider sourceをauthorityとし、dogfood projectionを検証する。
    
*   User-owned external Skillを削除しない。
    
*   External providerをCore dependencyにしない。
    
*   旧workflowを別名で再実装しない。
    
*   変更対象のtestsとcurrent full Core regressionを通す。
    
*   `validate`と`sync`でlocal graph整合性を確認する。
    

## 6\. 品質戦略

### 必須自動検証

*   Ruff / format / mypy
    
*   Core unit / CLI regression
    
*   installer init / update / uninstall
    
*   packaged asset inventory
    
*   provider / dogfood parity
    
*   no-current-reference regression
    
*   fresh consumer
    
*   existing consumer preservation
    

### 手動検証

*   `spec-dock` SkillによるScope / docs / dependency参照
    
*   `spec-dock-grill-with-docs`によるArtifact作成
    
*   external capability absence時の停止
    
*   ChatGPT-Use Strict等によるAuthoring Kit利用
    
*   Codex GoalによるPlanベース実装
    

External browser/model自体をCIへ組み込まない。

## 7\. Migrationとrollout

### Rollout順序

1.  I1 / I2を完成させる。
    
2.  I3を新Core / Kitへ接続する。
    
3.  I4でinstallerとdogfoodをhard cutoverする。
    
4.  Majorまたは明確なbreaking releaseとして配布する。
    
5.  Existing consumerは`update`前に通常のGit backupを持つ。
    
6.  Update後に`validate` / `sync`を実行する。
    
7.  Legacy automation Initiativeとopen workをsupersededとして整理する。
    

### Data preservation

保持:

*   node directories
    
*   `.meta.json`
    
*   dependency edges
    
*   Requirement / Design / Plan / Report
    
*   Artifact / Discussion / ADR
    
*   Workbench unmanaged content
    

削除対象:

*   SpecDock-managed workflow Skill
    
*   SpecDock-managed agent role / host adapter
    
*   SpecDock-managed PR workflow asset
    
*   product-owned ChatGPT runtime
    
*   obsolete workflow docs / templates / scripts
    
*   generated stateは再生成可能な範囲で更新
    

## 8\. 最終完了条件

*   Storage CoreとAuthoring Kitが明確な製品境界としてREADMEに記載されている。
    
*   Managed Skillは二つだけである。
    
*   Runtimeに旧workflow commandがない。
    
*   Existing dataとdependency graphが保持される。
    
*   Fresh / existing consumerの両方でCoreが動作する。
    
*   External intelligenceを交換してもCore変更が不要な契約になっている。
    
*   `init-00322`の旧自動化方針がcurrent routeとして残っていない。
    
*   本Epicの4 Issueが完了し、required CIとレビューを通した一つのmergeable PRまたは  
    明示されたdelivery単位が完成している。
    

## 9\. 未確定事項

なし。  
""")

(out\_dir / "README.md").write\_text(readme, encoding="utf-8")  
(out\_dir / "requirement.md").write\_text(requirement, encoding="utf-8")  
(out\_dir / "design.md").write\_text(design, encoding="utf-8")  
(out\_dir / "plan.md").write\_text(plan, encoding="utf-8")

zip\_path = Path("/mnt/data/spec-dock-core-simplification-epic-draft.zip")  
with zipfile.ZipFile(zip\_path, "w", compression=zipfile.ZIP\_DEFLATED) as zf:  
for path in sorted(out\_dir.iterdir()):  
zf.write(path, arcname=f"{out\_dir.name}/{path.name}")

print(f"Created: {out\_dir}")  
print(f"Created: {zip\_path}")  
print("Files:", \[p.name for p in sorted(out\_dir.iterdir())\])

STDOUT/STDERR

Created: /mnt/data/spec-dock-core-simplification-epic-draft
Created: /mnt/data/spec-dock-core-simplification-epic-draft.zip
Files: \['README.md', 'design.md', 'plan.md', 'requirement.md'\]

# 階層判断

**新規Initiativeは作らず、既存の`init-local-00003 Architecture Maintenance and Hardening`配下に、単独Epicを一つ追加する構成が最適です。**

理由は明確です。`init-local-00003`は、もともとopen-endedなArchitecture Initiativeとして定義されており、source-of-truth、identity、sync、naming、state boundary、runtime / scaffold / docs parityなどの構造的な変更を継続的に受け入れる方針です。今回の変更は、新しい利用者向け機能ではなく、SpecDockの製品境界と責務を縮小・再設計するArchitecture concernなので、このInitiativeの目的に正確に一致します。

一方、`init-00322 GPT 56 ChatGPT First Intelligence Architecture`は、Planning、Review、Execution、per-Issue Delivery、Epic CompletionまでをChatGPT-firstに自動化することを目的としています。今回の方針は、その自動化をSpecDockの製品責務から外し、外部インテリジェンスへ移すものなので、`init-00322`配下には置けません。むしろ、今回のEpicの最終Cutoverで、`init-00322`を**旧自動化方針としてsupersedeする対象**にするのが自然です。

したがって階層は次です。

```
init-local-00003 Architecture Maintenance and Hardening
└── 新規Epic:
    SpecDock Core Simplification and External Intelligence Boundary
    ├── Issue 1: Reduce Runtime to Storage Core
    ├── Issue 2: Simplify Authoring Kit and Document Contracts
    ├── Issue 3: Replace Managed Workflow Skills with SpecDock Skills
    └── Issue 4: Cut Over Distribution and Retire Legacy Workflow Surfaces
```

新しいInitiativeが必要になるのは、将来この方針が複数の独立Epicへ拡大し、たとえば「Storage Core」「Authoring Kit」「外部インテリジェンス接続」「可視化製品」がそれぞれ独立した投資目的を持つようになった場合です。現段階では一つのArchitecture transitionとして閉じており、新規Initiativeは過剰です。

* * *

# Issueを4本に限定した理由

現在のSpecDockは、インストーラーだけでもPlanning、Execution、ChatGPT Authoring、Clarification、ADR、Codex/Copilot Adapter、PR Observation、PR Creation、PR Merge Preparationなど多数のmanaged Skillを配布しています。

Runtimeにも、Core操作に加えて`assurance`、`authoring`、`delegated_authoring`、`workflow`などのコマンド群が登録されています。

このため実装自体は複数Issueに分ける必要があります。しかし、技術レイヤーごとに細分化すると、今回解消したい「過剰なIssue分割」「大量の計画文書」「形式的な最終品質Issue」が再発します。

そこで、独立した責務境界だけで4本に分けました。

## I1 — Reduce Runtime to Storage Core

DeterministicなCore操作を残し、Workflow、Assurance、Delegated Authoring、製品内ChatGPT Runtimeを削除します。

残す主な能力は次です。

*   Initiative / Epic / Issue
    
*   Artifact
    
*   Dependency DAG
    
*   Active Scope
    
*   Issue start / finish
    
*   Workbench / Worktree
    
*   GitHub linkage
    
*   Validate / Sync
    
*   Update / Uninstall
    

## I2 — Simplify Authoring Kit and Document Contracts

要件定義書・設計書・実装計画書のテンプレートと作成ガイドを残しながら、次を除去します。

*   Reviewer Gate
    
*   Grade
    
*   Evidence Adoption Ledger
    
*   Phase Promotion
    
*   Specialist evidence
    
*   Human Decision
    
*   PR readiness
    

現在のEpicテンプレートやAuthoring Workflowには、これらのWorkflow固有項目が多く含まれています。

## I3 — Replace Managed Workflow Skills with SpecDock Skills

Managed Skillを次の二つだけにします。

```
spec-dock
spec-dock-grill-with-docs
```

`spec-dock`はStorage CoreとAuthoring Kitの利用方法を教えるModel-invoked Skillです。

`spec-dock-grill-with-docs`は、外部の`grilling`と`domain-modeling`を利用し、対象ScopeのArtifactへ対話結果を残す明示起動型Skillです。Matt Pocock氏の`grill-with-docs`自体は、現在ほぼ`grilling + domain-modeling`のCompositionだけなので、この置換はForkではなく薄いIntegrationとして成立します。

## I4 — Cut Over Distribution and Retire Legacy Workflow Surfaces

Installer、Update、Uninstall、Dogfood、Migration、README、テスト、旧Initiativeの整理を一つの横断Issueとして完了させます。

別の「最終品質Issue」は作りません。I4がIntegrationとCutoverを兼ねます。

* * *

# 依存関係

I1とI2は並行して進められます。

```
I1 Storage Core ───────┐
                       ├──> I3 Skills ───> I4 Cutover
I2 Authoring Kit ──────┘
```

SpecDock上では次の依存になります。

```
I3 depends_on I1
I3 depends_on I2

I4 depends_on I1
I4 depends_on I2
I4 depends_on I3
```

`deps add`では、dependentが`--from`、prerequisiteが`--to`です。現在のSpecDockは`.meta.json.depends_on`を依存関係の正本とし、自己依存、循環、不正なancestor / descendant依存を保存前に拒否します。このCore機能はそのまま維持する計画です。

* * *

# 作成したEpic文書

現在の`main`を確認した上で、次の4ファイルを作成しました。

*   `README.md`
    
    *   階層判断
        
    *   Materialization手順
        
    *   Baseline
        
    *   過剰分割を避ける方針
        
*   `requirement.md`
    
    *   Storage CoreとAuthoring Kitの製品境界
        
    *   削除対象
        
    *   二つのSkill
        
    *   外部インテリジェンスとの境界
        
    *   Acceptance Criteria
        
    *   Migration方針
        
*   `design.md`
    
    *   Target Architecture
        
    *   残すRuntime surface
        
    *   削除するRuntime surface
        
    *   Authoring Kit設計
        
    *   Skill設計
        
    *   ChatGPT-Use Strictとの境界
        
    *   Distribution / Migration / Test戦略
        
*   `plan.md`
    
    *   4 Issueの具体的な責務
        
    *   依存関係
        
    *   並行Lane
        
    *   共通Handoff条件
        
    *   CutoverとData preservation
        
    *   最終完了条件
        

個別ファイルはこちらです。

*   Materialization Guide
    
*   Epic Requirement
    
*   Epic Design
    
*   Epic Plan
    

まとめたZIPです。

SpecDock Core Simplification Epic Draft

* * *

# Materialization方法

GitHub Issue番号とEpic IDは、実際にSpecDock CLIから作成した時点で確定させるべきなので、文書内では次をplaceholderにしています。

```
<EPIC_ID>
<GITHUB_ISSUE_NUMBER_OR_URL>
```

作成コマンドは次です。

Bash

```
./spec-dock/scripts/spec-dock new epic \
  --initiative init-local-00003 \
  --title "SpecDock Core Simplification and External Intelligence Boundary"
```

生成されたEpic directoryへ3文書を配置し、placeholderを実IDへ置換します。その後、`plan.md`に記載した4 Issueを作成し、依存関係を登録します。

今回の構成では、次を意図的に作っていません。

*   新規Initiative
    
*   複数Epic
    
*   Planning専用Issue
    
*   Review専用Issue
    
*   Metrics専用Issue
    
*   Final Quality専用Issue
    
*   ChatGPT-Use Strict実装Issue
    
*   Matt Skillsのインストーラー実装Issue
    
*   既存文書の一括Migration Issue
    

これにより、SpecDockを大幅に簡素化するEpic自体が、再びSpecDockの過剰なWorkflowとIssue分割を再生産しない構成にしています。

README.mdDocumentOpen file

requirement.mdDocumentOpen file

design.mdDocumentOpen file

1 more

Sources

ChatGPT can make mistakes. Check important info.

  

Pro