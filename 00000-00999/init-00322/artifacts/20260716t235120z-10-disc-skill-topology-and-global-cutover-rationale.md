---
種別: disc
ID: "20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale"
タイトル: "Skill／Agent TopologyとGlobal CutoverのDecision Rationale"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md"
  - "artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md"
  - "artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md"
authority: "synthesized"
derived_from:
  - "artifacts/20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md"
  - "artifacts/20260716t235120z-12-research-oracle-thin-adapter-and-github-binding.md"
  - "artifacts/20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
---

# 20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale Skill／Agent TopologyとGlobal CutoverのDecision Rationale

## 位置づけ

- この文書は、複数Interview・Research・ADRを横断し、採用判断へ至った説明可能なrationale、tradeoff、設計含意を整理する。
- Current Effective Decision Snapshotとaccepted ADRを上書きしない。本文は決定に至った論点構造を後続Agentへ伝えるevidence surfaceである。
- 生ログや非公開の内部chain-of-thoughtを再現せず、会話上で明示された分析、比較、反証、ユーザー承認だけを要約する。

## 対象論点

- 公開Workflow Skill、共有Reference、専用CLIの三層
- 削除する旧authoring／manual／Reviewer／custom agent
- 残すExecutor／Explorer／Researcher／Consultant
- Model／Reasoning policy
- 全Scope workflow cutoverとdocument migrationなし
- このsynthesisが必要な理由:
  - Skill数削減だけを目的と誤解すると、独立ユーザー目的のあるTargeted Reviewまで削除したり、一つの巨大Skillへ統合したりする危険がある。

## derived question sheets／research

- `interview`／`research`:
  - artifacts/20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md
  - artifacts/20260716t235120z-12-research-oracle-thin-adapter-and-github-binding.md
  - artifacts/20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact.md
- Current decision:
  - `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md`
- Related ADR:
  - artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md
  - artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md
  - artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md

## synthesis

- 合意済みのこと:
  - Initiative／Epic／Issue Planning Skillは3つ維持する
  - Formal ReviewとRepair Batchは親Workflow operationであり独立Skillにしない
  - Targeted Reviewだけは独立ユーザー目的を持つため公開Skillにする
  - `spec-dock-chatgpt`がOracle invocationの決定的leaf operationを所有する
  - custom Explorerを削除しbuilt-in Explorerを無改変で使う
  - 既存Scope文書を変換せず全Scopeの次操作からvNextへcutoverする
- 未合意／未確定のこと:
  - exact model labelとreasoning enum
  - provider／installed／dogfoodの全file inventory
  - Oracle version／configのlive compatibility
- source-groundedに解決できたこと:
  - 現行repositoryには旧authoring Skill、manual Planning Skill、local Reviewer、custom Explorer、Repository Analyst、doc-writerが存在する
  - Workbench導入済みのため新しい一時state layerは不要
  - 既存canonical document形式はvNextと互換である

## 選択肢／tradeoff

- Option A: 旧Skill／Agentを補助fallbackとして残す:
  - Pros:
    - 移行時の安心感
  - Cons:
    - 二重Workflowと二重authorityが残る
    - 初期contextと保守surfaceが増える
  - Disposition:
    - Rejected
- Option B: 最小Topologyへ一括cutover:
  - Pros:
    - 責務が明確
    - Codex default改善を利用
    - mirror負債を減らす
    - 文書migration不要
  - Cons:
    - 一度に多くの旧参照を削除する必要
    - live smokeが重要
  - Disposition:
    - Accepted
- Option C: 一つの汎用Skillへ統合:
  - Pros:
    - Skill数が最小
  - Cons:
    - mode分岐が巨大化
    - authority layerを誤りやすい
  - Disposition:
    - Rejected

## reflection proposal

- canonical docs／workflow／template／skill guidanceへ反映すべき候補:
  - `workflow_planning.md`、`workflow_chatgpt_delegation.md`、`workflow_review.md`、`workflow_repair_batch.md`を新設
  - 旧`workflow_spec_authoring.md`を置換
  - Main／Executor／ExplorerはSpecDockからmodelを固定しない
  - Researcher／Consultant／Deep Consultantだけrole profileを定義する
  - global searchとparity testでlegacy surfaceを除去する
- まだproposalに留める理由:
  - exact file path、Prompt本文、JSON field、Oracle config key等は各Epic Planningとlive smokeで決めるため。
  - 本文は実装authorityではなく、canonical文書とADRの解釈を助ける。

## adoption target／採用先候補

- `requirement.md`:
  - REQ-023〜REQ-026、NFR-001／004／006、AC-015〜AC-018
- `design.md`:
  - Skill／Agent topology、Oracle boundary、Cutover設計
- `plan.md`:
  - Epic 1、Epic 2、Epic 3、Epic 4、Epic 6、Epic 7
- `ADR`:
  - Thin Oracle Adapter、Global Cutover、Minimal Persistent State
- `report.md`:
  - 削除／残存surfaceとparity結果の最終要約

## ADR triage

- ADR candidateか:
  - yes
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADRとして残す理由:
  - Actor authority、SSOT、Review gate、Repair／Delivery境界、cutoverは将来のSkill／Runtime変更で再び誤って戻されやすいため。
- 対応するaccepted ADR:
  - artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md
  - artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md
  - artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md

## 推奨案

- 現時点の推奨案:
  - 独立ユーザー目的のあるWorkflow Skillだけを残し、内部operationは共有Reference＋`spec-dock-chatgpt` CLIへ集約したうえで全Scopeを一括cutoverする。
- 理由:
  - Current Effective Decision Snapshot、canonical三文書、accepted ADRが同じ方向を示しており、旧案を再導入する根拠がない。

## 推奨反映先

- `requirement.md`:
  - REQ-023〜REQ-026、NFR-001／004／006、AC-015〜AC-018
- `design.md`:
  - Skill／Agent topology、Oracle boundary、Cutover設計
- `plan.md`:
  - Epic 1、Epic 2、Epic 3、Epic 4、Epic 6、Epic 7
- `ADR`:
  - Thin Oracle Adapter、Global Cutover、Minimal Persistent State
- `report.md`:
  - 削除／残存surfaceとparity結果の最終要約

## 未採用／deferred理由

- 未採用:
  - 旧`spec-dock-chatgpt-authoring`を内部Leaf Skillとして残す
  - manual Planning fallbackを残す
  - Formal Review／Repair Batchごとの独立Skill
  - Custom Explorer／Repository Analyst／Docs Writer
  - 新規Scopeだけへの段階導入
- deferred:
  - model labelとOracle config keyは実装時点のsupported valueへ合わせる
  - closed historical artifactは書き換えない

## 次アクション

- Epic 1で完全asset inventoryを作る
- Epic 6でprovider／installed／dogfood parityとlegacy searchを実施する
- Epic 7でend-to-end dogfood後にglobal cutoverを確定する
- 追加で作るdiscussion docs:
  - なし。本pack内のInterview、Research、Decision Snapshot、ADR、self-reviewで必要な説明面を構成する。
