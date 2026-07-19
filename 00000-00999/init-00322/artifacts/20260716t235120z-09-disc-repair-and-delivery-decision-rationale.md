---
種別: disc
ID: "20260716t235120z-09-disc-repair-and-delivery-decision-rationale"
タイトル: "Repair Batch・Executor・Delivery LifecycleのDecision Rationale"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md"
  - "artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md"
  - "artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md"
authority: "synthesized"
derived_from:
  - "artifacts/20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries.md"
  - "artifacts/20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
---

# 20260716t235120z-09-disc-repair-and-delivery-decision-rationale Repair Batch・Executor・Delivery LifecycleのDecision Rationale

## 位置づけ

- この文書は、複数Interview・Research・ADRを横断し、採用判断へ至った説明可能なrationale、tradeoff、設計含意を整理する。
- Current Effective Decision Snapshotとaccepted ADRを上書きしない。本文は決定に至った論点構造を後続Agentへ伝えるevidence surfaceである。
- 生ログや非公開の内部chain-of-thoughtを再現せず、会話上で明示された分析、比較、反証、ユーザー承認だけを要約する。

## 対象論点

- Review後のPlan外修正を扱う中間契約
- Repair Batchの生成・採用・freeze
- Executorの意味的裁量とMain-owned Git transaction
- Issue Exit Contract、Delivery Topology、Delivery Owner Issue
- Issue Review／Epic Review／PR Delivery／Human Merge Gate
- このsynthesisが必要な理由:
  - RepairとDeliveryは一つの連続loopを形成する。個別のAgentやPR手順だけを読むと、Plan外修正のauthority、Review freshness、finish条件を誤りやすい。

## derived question sheets／research

- `interview`／`research`:
  - artifacts/20260716t235120z-04-interview-repair-batch-executor-and-git-boundaries.md
  - artifacts/20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics.md
- Current decision:
  - `artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md`
- Related ADR:
  - artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md
  - artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md
  - artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md

## synthesis

- 合意済みのこと:
  - Repair Batchはformal quality gateのaccepted blockerを扱う小規模設計書兼実装計画書
  - ChatGPTが完全Markdownを生成し、Mainが採用し、Executor開始前にfreezeする
  - Executorは契約内で柔軟に変更するがcommit／pushしない
  - Epic PlanがDelivery TopologyとOwnerを、Issue PlanがExit Contractを所有する
  - Issue ReviewとEpic Reviewは異なるContract Ownerのため両方必要
  - merge-preparedはHuman Gateでありfinishではない
- 未合意／未確定のこと:
  - Repair Batch templateの最終最小section
  - PR watcherの再利用方法
  - report.md Final Completion Summaryのexact template
- source-groundedに解決できたこと:
  - 現行Repair Batchは有用なfamily synthesisと同時にPR state ledgerとして肥大化している
  - GitHub／Oracle／Git historyが外部gate結果と実施結果のSSOTを既に持つ
  - 現行運用には単独Issue PRとEpic-wide PRの両方が存在する

## 選択肢／tradeoff

- Option A: finding単位の直接patch:
  - Pros:
    - 速い
    - artifactが増えない
  - Cons:
    - root cause couplingを失う
    - scope creepと再発が起きやすい
  - Disposition:
    - Rejected
- Option B: すべてPlanningへ戻す:
  - Pros:
    - canonical contractが常に更新される
  - Cons:
    - 局所repairにも高コスト
    - PlanningとExecutionの境界が重い
  - Disposition:
    - Rejected
- Option C: Frozen Repair Batch＋Plan-driven Delivery:
  - Pros:
    - bounded repair契約を残せる
    - Executor handoffが明確
    - 複数PR粒度に対応
  - Cons:
    - 新しいartifactとReview loopが必要
    - Mainのrouting判断が必要
  - Disposition:
    - Accepted

## reflection proposal

- canonical docs／workflow／template／skill guidanceへ反映すべき候補:
  - `workflow_repair_batch.md`を共通referenceとして作る
  - Issue ExecutionはExecution Tranche／Checkpoint／Repair／Exit Contractを所有する
  - PR Deliveryは一つの簡素なSkillとしてmerge-preparedまで所有する
  - Delivery Owner Issueはbounded integration repairを所有する
- まだproposalに留める理由:
  - exact file path、Prompt本文、JSON field、Oracle config key等は各Epic Planningとlive smokeで決めるため。
  - 本文は実装authorityではなく、canonical文書とADRの解釈を助ける。

## adoption target／採用先候補

- `requirement.md`:
  - REQ-016〜REQ-022、AC-008〜AC-014
- `design.md`:
  - Section 8〜10、Main／Executor／Git境界
- `plan.md`:
  - Epic 4、Epic 5、Epic 7
- `ADR`:
  - Frozen Repair Batch、Main-owned Git、Delivery Topology
- `report.md`:
  - 主要repair参照、最終verification、merge結果の要約

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
  - artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md
  - artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md
  - artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md

## 推奨案

- 現時点の推奨案:
  - Frozen Repair Batchを上位Planへ従属するrepair contractとし、Plan-driven Delivery TopologyでIssue／Epic／PRの終了境界を統一する。
- 理由:
  - Current Effective Decision Snapshot、canonical三文書、accepted ADRが同じ方向を示しており、旧案を再導入する根拠がない。

## 推奨反映先

- `requirement.md`:
  - REQ-016〜REQ-022、AC-008〜AC-014
- `design.md`:
  - Section 8〜10、Main／Executor／Git境界
- `plan.md`:
  - Epic 4、Epic 5、Epic 7
- `ADR`:
  - Frozen Repair Batch、Main-owned Git、Delivery Topology
- `report.md`:
  - 主要repair参照、最終verification、merge結果の要約

## 未採用／deferred理由

- 未採用:
  - Repair BatchをPR専用に限定する
  - 一つのRepair BatchをPR期間中更新し続ける
  - Executorによるcommit／push
  - issue finishを常にmerge前またはmerge-preparedで行う
  - Epic Reviewで各Issue Reviewを再実行する
- deferred:
  - PR Delivery watcherの実装詳細
  - 最終的にGitHub Codex Reviewを外すかは実測後に判断

## 次アクション

- Epic 4でRepair Batch、Executor、Issue Execution、report.mdを実装する
- Epic 5でDelivery Topology、Epic Execution、PR Deliveryを実装する
- Epic 7でrepair後headの三重gateとHuman merge flowをdogfoodする
- 追加で作るdiscussion docs:
  - なし。本pack内のInterview、Research、Decision Snapshot、ADR、self-reviewで必要な説明面を構成する。
