---
種別: 要件定義書（Epic）
ID: "<EPIC_ID>"
タイトル: "SpecDock Core Simplification and External Intelligence Boundary"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft"
作成者: "ChatGPT"
最終更新: "2026-08-07"
親: ["init-local-00003"]
---

# <EPIC_ID> SpecDock Core Simplification and External Intelligence Boundary — 要件定義（何を、なぜ行うか）

## 1. 目的

### Initiativeとの紐づき

`init-local-00003 Architecture Maintenance and Hardening` が扱う構造健全性、source-of-truth、
runtime/scaffold/docs parity、運用可能性の改善として、SpecDockを次の二つへ縮退する。

1. **Storage Core**
   - Initiative / Epic / Issueのローカル階層
   - GitHub Issue linkage
   - Scope-local Artifact
   - direct dependency DAG
   - active scope
   - validate / sync / projection
   - deterministicな構造操作

2. **Authoring Kit**
   - Initiative / Epic / Issueの`requirement.md`
   - `design.md`
   - `plan.md`
   - Artifact rules
   - 各文書の役割、品質基準、書き方を説明するガイド

### このEpicが提供する能力

- SpecDockが開発ワークフローを所有せず、任意の高性能モデルや外部Skillから利用できる。
- 仕様書、分析記録、Issue階層、依存関係は引き続きローカルGit管理下に残る。
- 外部インテリジェンスを変更しても、SpecDockのデータ構造と文書を再設計せずに済む。
- SpecDock自身が配布するAgent Skillは、Storage Coreを利用する`spec-dock`と、
  明示的な対話用`spec-dock-grill-with-docs`の二つに限定される。
- ChatGPT-Use Strict、Matt Pocock Skills、Codex GoalなどはOperator-ownedな外部能力として利用できる。

## 2. 背景

現在のSpecDockは、ローカル仕様書と依存グラフに加えて、次の認知・運用ワークフローまで
製品内部で所有している。

- Initiative / Epic / Issue Planning Skill
- Issue / Epic Execution Skill
- Clarification workflow
- Assurance gradeとresource allocation
- phase promotionとfresh reviewer gate
- delegated authoringとEvidence Adoption Ledger
- ChatGPT-first Candidate / Review / Revision / Human Decision / Apply
- `spec-dock-chatgpt`
- PR creation / observation / merge preparation
- named sub-agent roleとhost adapter
- workflow guidance / runbook

これらはモデル能力、ハーネス、外部UI、レビュー方法の変化を直接受けるため、
Storage Coreよりも高い頻度で更新が必要になる。結果として、仕様書管理と依存関係管理を
維持するためにも、大量のworkflow docs、Skill、runtime、test、projectionを同時に
保守しなければならない。

一方、実運用では、仕様書作成から実装までを完全自動化すると、過剰分割、過剰な証跡、
大量の低価値文書、形式的に整っていても価値の低い実装が生成される問題が確認された。
現時点では、高認知負荷の仕様作成をChatGPTのfrontier modelへ明示的に委任し、
Codexがローカルで反映・実装する構成の方が実用的である。

## 3. 基本原則

### E-RQ-001 Storage Coreを製品境界とする

SpecDock Coreは次だけを所有する。

- node identityとdirectory hierarchy
- GitHub Issue linkage
- canonical local documents
- Scope-local Artifact
- dependency storageとDAG validation
- readiness projection
- active scopeとIssue lifecycle primitive
- validate / sync / update / uninstall
- optionalなworkbench / worktree utility

Coreはモデル、Prompt、Reviewer、Oracle、ChatGPT Project、特定Skill名を知らない。

### E-RQ-002 Authoring Kitを保持する

Initiative / Epic / Issueの`requirement.md`、`design.md`、`plan.md`について、
次を丁寧に説明するテンプレートとガイドを残す。

- 各文書が答える問い
- Scopeごとの責務
- 文書間の境界
- 受け入れ条件とEdge caseの書き方
- 設計境界、契約、図表の選び方
- 実装順序、テスト、検証、rollbackの書き方
- Artifactからcanonical documentへ整理する考え方

テンプレートは実文書に残る最小scaffoldとし、詳細説明はAuthoring Guideへ置く。

### E-RQ-003 Workflow gateをAuthoring Kitから除去する

次を仕様書作成の必須条件またはCore authorityとして扱わない。

- fresh reviewer pass
- phase promotion
- Assurance grade
- specialist使用義務
- Evidence Adoption Ledger
- delegated draft evidence
- Human Decision JSON
- Candidate ZIP
- manual fallback state machine
- PR readiness / merge-prepared state

既存文書の履歴は保持するが、新しいテンプレートとガイドから旧workflow authorityを除去する。

### E-RQ-004 構造の厳密さだけを維持する

モデルがMarkdownを直接編集できる一方、次の構造変更はSpecDock CLIだけが行う。

- node作成、close、delete
- hierarchy
- dependency add / remove
- GitHub Issue linkage
- generated projection

Coreは自己依存、循環依存、不正なancestor / descendant dependency、重複identity、
Scope外pathへの構造変更を拒否する。

### E-RQ-005 Agent Skillを二つに限定する

SpecDockがmanaged assetとして配布するSkillは次の二つだけとする。

1. `spec-dock`
   - Model-invoked
   - Scope、canonical documents、Artifact、node、dependency、CLIの利用方法を提供する
   - 開発ワークフローを規定しない

2. `spec-dock-grill-with-docs`
   - User-invoked
   - explicit / active Scopeを解決する
   - Scope-local Artifactを作る
   - 外部の`grilling`と`domain-modeling`能力を利用する
   - Fact、Decision、Alternative、Open Question、Authoring BriefをArtifactへ残す
   - canonical `requirement.md` / `design.md` / `plan.md`を自動作成しない

`spec-dock-grill-with-docs`は明示起動専用とし、外部能力が存在しない場合は明確に停止する。
外部Skill本体はSpecDockへ同梱しない。

### E-RQ-006 外部インテリジェンスを交換可能にする

SpecDockは次を外部から利用できるが、依存しない。

- ChatGPT-Use Strict
- Matt Pocock Skills
- Codex Goal
- 将来の別Agent / model / skill set

外部能力との契約は、Scope、local documents、Artifact、CLI、Git repositoryだけで表す。
外部Provider固有の設定、model名、browser session、wrapper pathをSpecDock Coreへ保存しない。

### E-RQ-007 `to-spec`と`to-tickets`を採用しない

Matt Pocock Skillsを利用する場合も、次はSpecDock標準フローへ導入しない。

- `to-spec`
- `to-tickets`
- それらを前提とする`ask-matt`
- GitHub label state machineを持つ`triage`
- tracker固有前提の強い`wayfinder`

仕様書はSpecDock Authoring Kitを参照して作成し、Issueと依存関係はSpecDock CLIで作成する。

### E-RQ-008 Product-owned ChatGPT workflowを撤去する

次をSpecDockから削除する。

- `spec-dock-chatgpt`
- ChatGPT Planning create / review / revise / apply
- Candidate / Review / Human Decision contract
- Oracle-specific runtime boundary
- ChatGPT-first planning Skills
- ChatGPT-specific workflow docsとtests

Operator-ownedなChatGPT-Use StrictはSpecDock外で維持し、必要な場合だけ利用する。

### E-RQ-009 既存データを保持する

Cutover時に次を自動変換・削除しない。

- `spec-dock/initiatives/**`
- canonical requirement / design / plan / report
- historical artifacts / discussions
- accepted ADR
- `.meta.json.depends_on`
- GitHub linkage
- Workbenchのunmanaged content

旧workflow固有の既存記録はhistorical evidenceとして残せるが、新Coreはその状態を
readiness authorityとして解釈しない。

### E-RQ-010 Managed assetを確実に整理する

`init`は新しい最小構成だけを導入し、`update`は旧SpecDockが管理していた次のassetを
安全にpruneする。

- planning / execution / clarification / authoring Skills
- PR observation / creation / merge Skills
- host adapterとnamed agent role
- product-owned ChatGPT runtime
- workflow / assurance / delegated authoring command surface
- stale docs、templates、tests、native shims

User-owned fileとunmanaged Skillは削除しない。

### E-RQ-011 外部自動化を製品要件にしない

本Epicでは、仕様作成から実装完了までの完全自動化を提供しない。

代表的な利用例は次とする。

1. `spec-dock-grill-with-docs`で論点を明確化しArtifactへ保存する。
2. ChatGPT-Use Strict等で仕様書を作成する。
3. Codexがlocal canonical documentsへ反映する。
4. `/goal`と外部実装SkillでIssueを完了する。
5. SpecDockは文書、Issue、依存関係、状態を保持する。

### E-RQ-012 変更容易性を成功条件に含める

新しい外部インテリジェンスを導入するとき、SpecDock Coreのruntime、metadata schema、
Authoring Kitを変更せず、Repo-local SkillまたはOperator-owned Skillだけで接続できること。

## 4. エピック受け入れ条件

### E-AC-001 Fresh install

- `spec-dock init`後、Storage Core、Authoring Kit、`spec-dock`、
  `spec-dock-grill-with-docs`だけがSpecDock managed Skillとして存在する。
- Planning / Execution / PR / ChatGPT workflow Skillは導入されない。
- `validate`が成功する。

### E-AC-002 Core command surface

- node、artifact、dependency、active、issue lifecycle、sync、validate、update、uninstallの
  必要な操作が利用できる。
- `assurance`、`authoring`、`delegated-authoring`、`workflow/guidance`、
  `spec-dock-chatgpt`は公開command surfaceに存在しない。

### E-AC-003 Local document authority

- Initiative / Epic / Issueの仕様書はローカルnode directoryに存在する。
- GitHub Issue本文はcanonical specificationとして要求されない。
- 外部Agentがcurrent local documentsを直接参照できる。

### E-AC-004 Dependency graph

- Issue / Epic dependencyを登録・削除・照会できる。
- cycleとinvalid edgeは保存前に拒否される。
- `sync`がmachine-readable graphと人間向け可視化を生成する。

### E-AC-005 Authoring Kit

- Requirement / Design / Planのテンプレートとガイドから旧workflow gateが除去されている。
- 各文書の役割と品質基準は、特定modelやSkillに依存せず理解できる。
- Templateは詳細説明を過剰に複製しない。

### E-AC-006 Skill boundary

- `spec-dock`はStorage Coreの利用方法だけを提供し、別workflowを開始しない。
- `spec-dock-grill-with-docs`はScope-local Artifactを作成し、対話結果を保存する。
- Grilling中にcanonical Requirement / Design / Planを自動変更しない。
- 外部Skill不在はCore利用を妨げない。

### E-AC-007 Existing consumer update

- `spec-dock update`が既存node、文書、Artifact、dependency、Workbench contentを保持する。
- 旧managed workflow assetだけをpruneする。
- 更新後に`validate`と`sync`が成功する。

### E-AC-008 External intelligence smoke

次の手動smokeが成立する。

1. `spec-dock-grill-with-docs`でScope Artifactを作成する。
2. Operator-owned ChatGPT-Use StrictでAuthoring Kitを参照し、三文書を作成する。
3. Codexが文書を反映し、`validate`を通す。
4. Codex GoalからIssueのPlanに沿って実装できる。

このsmokeを外部Providerの自動E2E testとして製品へ固定しない。

### E-AC-009 Legacy retirement

- `init-00322`のChatGPT-first automation方針はsupersededとして扱われる。
- Historical local documentsは保持する。
- Openなlegacy implementation Issueは重複実装を防ぐため整理される。
- 新しいSpecDock READMEとguideがStorage Core + Authoring Kitを主要製品境界として説明する。

## 5. スコープ

### 必須

- Runtime command registryとdomain/application/infraの縮退
- Installer managed assetの縮退
- Authoring Kitの再構成
- 二つのSpecDock Skill
- update / uninstall時のobsolete cleanup
- provider / dogfood / installed consumerの整合
- testsとmigration / cutover docs
- 旧ChatGPT-first / workflow surfaceのretirement

### 禁止

- 新しいworkflow engineを別名で再実装する
- Matt Pocock SkillsまたはChatGPT-Use StrictをSpecDock Coreへvendorする
- 外部SkillのPromptやversionをCore schemaへ埋め込む
- 既存node treeを一括書換えする
- GitHub Issue本文を仕様の正本へ変更する
- 自動化を維持するための新しいstate DB、receipt DB、review DBを作る

### 対象外

- ChatGPT-Use Strict Skillそのものの実装
- Matt Pocock Skillsの配布・更新機構
- `to-spec` / `to-tickets`互換Adapter
- 完全自律Runner
- Web UI
- 新しいdocument profileへの全面移行
- 既存historical documentsの内容修正

## 6. 非機能要件

### 軽量性

- Coreの公開概念とmanaged Skill数を減らす。
- Model-facing instructionはProgressive Disclosureを使い、CLI helpとAuthoring Guideを
  source of truthとする。
- 旧workflow語彙を新Skillやtemplateへ複製しない。

### 信頼性

- Markdown編集の自由度を高めても、node graphとdependency graphの構造安全性は維持する。
- `update`はmanaged assetだけを変更し、user dataを保持する。
- Partial cleanup時は対象pathと残存assetを診断できる。

### 互換性

- Data compatibilityを優先する。
- Workflow compatibilityは提供しない。
- 旧command / Skill aliasを恒久的に残さない。
- Rollbackは旧workflowへのruntime fallbackではなく、Git revertまたは旧releaseへの
  明示的なversion rollbackとする。

### セキュリティ

- External providerのcredential、cookie、browser profile、private wrapper pathを
  SpecDockへ取り込まない。
- Artifactとdocument pathはRepository境界外へescapeできない。
- External outputはRepository factsとtestsで検証してから採用する。

## 7. 依存と影響範囲

### 主な影響領域

- `src/spec_dock/cli.py`
- `src/spec_dock/assets/install_root/.agents/`
- `src/spec_dock/assets/install_root/.codex/`
- `src/spec_dock/assets/install_root/.github/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- `src/spec_dock/assets/spec_dock/docs/`
- `src/spec_dock/assets/spec_dock/templates/`
- dogfooding projectionである`.agents/`、`.codex/`、`spec-dock/`
- installer / runtime / parity / consumer tests

### 外部依存

- Coreには新しい外部dependencyを追加しない。
- `spec-dock-grill-with-docs`利用時だけ、外部の`grilling`と`domain-modeling`が必要。
- ChatGPT-Use StrictはOperator-owned optional dependency。

## 8. 後続Issue seed

- **Reduce Runtime to Storage Core**
  - workflow / assurance / ChatGPT / delegated authoring surfaceを削除し、
    deterministic core commandだけを残す。

- **Simplify Authoring Kit and Document Contracts**
  - Requirement / Design / Plan templatesとauthoring docsから旧workflow gateを除去し、
    intelligence-neutralな品質基準へ再構成する。

- **Replace Managed Workflow Skills with SpecDock Skills**
  - `spec-dock`と`spec-dock-grill-with-docs`を実装し、他のmanaged Skillとagent roleを削除する。

- **Cut Over Distribution and Retire Legacy Workflow Surfaces**
  - init/update/uninstall、obsolete cleanup、docs、tests、dogfood、legacy initiative retirement、
    release cutoverを完了する。

## 9. 未確定事項

なし。

本EpicはStorage Core + Authoring Kitへのhard cutoverを採用する。
旧workflowと新境界の恒久的なdual modeは提供しない。
