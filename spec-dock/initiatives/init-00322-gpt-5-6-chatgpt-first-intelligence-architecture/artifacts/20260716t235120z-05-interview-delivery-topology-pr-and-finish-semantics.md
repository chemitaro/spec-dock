---
種別: interview
ID: "20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics"
タイトル: "Delivery Topology・PR・Issue/Epic Finish Semantics"
状態: "answered"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
  - "artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md"
scope: "initiative"
scope_id: "init-00322"
created_at: "2026-07-16T23:51:20Z"
created_by: "GPT-5.6 Pro"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "ChatGPTによるGrill Me／Grill with Docs形式の長時間インタビュー"
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md"
---

# 20260716t235120z-05-interview-delivery-topology-pr-and-finish-semantics Delivery Topology・PR・Issue/Epic Finish Semantics

## 位置づけ

- このArtifactは、長時間インタビューで確定した一つの本質的判断を、現在有効な状態へ正規化した回答済みInterview recordである。
- 過去の逐次会話や途中で上書きされた案を運用規則として残さず、最終回答、比較した代替、採用理由、canonical文書への含意だけを残す。
- 本文は生ログや非公開の内部推論ではなく、会話上で提示・比較・承認された判断材料の説明可能な要約である。

## 正式質問として扱う理由

- 影響するartifact:
  - Epic `plan.md`:
    - Delivery Topology、Boundary、Owner
  - Issue Seed／Issue `plan.md`:
    - Exit expectation／Exit Contract
  - Issue／Epic Execution:
    - review階層とfinish
  - PR Delivery:
    - merge-preparedとHuman Gate
- chat上の軽微な一問では足りない理由:
  - PR粒度、Review階層、Issue close、Epic close、人間停止点が全運用へ影響するため。

## 質問の目的

- 対象者:
  - Initiativeの意思決定者である人間ユーザー。
- 何を明確にする質問か:
  - Delivery Boundary、Delivery Owner、Issue Exit Contract、Issue／Epic Review、Human Merge Gateを固定すること。
- 回答が後続判断へ与える影響:
  - Requirement、Design、Initiative Plan、ADR、Epic boundary、Skill／Agent／CLIの具体化に直接影響する。

## 質問

- pressure-test question:
  - PRを小さく保つ小回りとEpic単位の統合品質を両立し、呼び出し経路に依存しない終了条件をどう定義するか。
- 質問:
  - PRを小さく保つ小回りとEpic単位の統合品質を両立し、呼び出し経路に依存しない終了条件をどう定義するか。
- 回答してほしいこと:
  - 採用する原則。
  - 棄却する代替。
  - Scope、authority、停止条件。
  - 後続Planningへ委譲する詳細。

## source-grounded context

- 確認済みのdocs／code／tests／ADR／discussions／primary source:
  - 単独Issue Executionでmergeable PRまで進める現行運用
  - Epic Executionで中間Issueをfinishし最終quality IssueでEpic PRを作る運用
  - Epic-wide PR肥大化と品質gateの課題
- local contextで解決できたこと:
  - per-Issue／Epic-wideの二択ではなくIssue列上のDelivery Boundaryでbatch PRも表現できる
  - Invocation contextだけで終了条件を変えると途中再開時に契約が不安定になる
- まだ人間判断が必要だった理由:
  - PR粒度とHuman merge gateは開発運用の価値判断だから。

## 回答案

- Option A: 常にIssueごとにPR:
  - 小さいがHuman Gateが頻発する。
- Option B: 常にEpic最後に一つのPR:
  - 連続実行しやすいがPRが肥大化する。
- Option C: Plan-driven Delivery Topology:
  - Epic PlanがBoundaryとOwnerを明示しIssue PlanがExit Contractへ具体化する。

## Codexの分析

- 判断軸:
  - PRサイズ
  - integration quality
  - Human interruption
  - 責務再現性
  - 途中再開
- tradeoff:
  - 固定policyは単純だがEpic規模に適応できない
  - Invocation context分岐は同じIssueの終了契約を不安定にする
  - PlanへExit Contractを固定すると単独／Epic内で同じauthorityを使える
- リスク:
  - 中間Issue Reviewを省くと欠陥がEpic Reviewへ累積する
  - Epic ReviewがIssue Reviewを再実行すると重複する
  - `merge-prepared`でfinishすると未merge Issueがclosedになる
- 具体シナリオ／edge case:
  - 中間IssueはIssue Delivery Review後にHandoff Exitでfinish可能
  - Delivery Owner Issueは自身のIssue ReviewとEpic Reviewを通す
  - merge-preparedで停止し人間merge後にreviewed head一致を確認してfinish
  - bounded integration repairはDelivery Owner、material変更はEpic Planning

## Codexの推奨案

- 推奨:
  - Option C: Plan-driven Delivery Topology
- 理由:
  - 小規模Issue PR、Epic-wide PR、batch PRを同じ概念で表現できる
  - 呼び出し経路ではなくPlanが終了条件を所有する
  - Issue ReviewとEpic Reviewの責務を分離できる
- 未回答時の影響:
  - Issue Execution／Epic Execution／PR Deliveryの完了境界が曖昧になる。

## ユーザー回答

- answer capture:
  - Issue ExecutionはPlanに従いHandoff ExitとMerge Exitの両方を持ち得る
  - Epic PlanのSeedがdelivery expectationを持ちIssue PlanがExit Contractへ具体化
  - Issue ReviewとEpic Reviewは異なるContract Ownerのため両方必要
- 回答:
  - Option Cを採用
  - Delivery Owner IssueはEpic Planで明示
  - 複数Issue Epicでは専用Final Quality／Delivery Issueを原則推奨
  - auto-mergeせず人間merge確認後にfinish
- 回答日時:
  - 2026-07-16までのインタビューで逐次承認し、Current Effective Decision Snapshotへ統合。

## 追加確認の要否

- 追加確認が必要か:
  - no
- 必要な場合に次のunanswered `interview`として切り出す質問:
  - なし。field名、Prompt本文、正確なfile inventory等の実装詳細は各Epic Planningへ委譲する。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`、`design.md`、`plan.md`、accepted ADR
- 採用／棄却／deferredの理由:
  - 採用案がInitiative全体のauthorityとWorkflowを一貫させ、過剰なstate、二重authoring、暗黙分岐を避けるため。
- `report.md`への反映要否:
  - no。vNextの`report.md`はFinal Completion Summaryであり、このInterview全文を台帳へ転記しない。

## requirement／design／plan／ADRへの含意

- `requirement.md`:
  - Plan-driven Exit Contract、Issue／Epic Review、Human Merge Gate
- `design.md`:
  - Delivery Boundary／Scope／Owner、Handoff／Merge Exit、finish確認
- `plan.md`:
  - Epic DeliveryとPR Deliveryを独立Epicへ配置
- `ADR`:
  - Plan-driven Delivery Topologyを固定

## 条件付き補足

- 後続reflection proposal:
  - canonical三文書またはaccepted ADRと矛盾する場合は、Interviewを直接実行authorityにせず、Planningで整合させる。
- 追加で作るdiscussion docs:
  - 複数Interviewを横断したrationaleは同梱の`disc-*`へ整理する。
