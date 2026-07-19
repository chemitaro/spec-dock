---
種別: disc
ID: "20260716t131924z-disc"
タイトル: "Epic Slice Materialization Handoff"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
authority: "user-approved"
derived_from:
  - "plan.md#Epicポートフォリオ"
  - "20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "plan.md"
---

# Epic Slice Materialization Handoff

## 位置づけ

このArtifactは、Initiative Planning ReviewとHuman approval後にCodexがEpic Nodeとdependency edgeを作成するための操作上のhandoffである。Epic名と意味をauthorityとし、永続Seed IDや独自mapperを作らない。

## Materialization前提

- Initiative Planning ReviewがP0／P1なしでPASSしている。
- Humanが7 Epicの名称、責務境界、依存関係を承認している。
- Initiative Planning BundleのcommitがGitHubへpush済みである。
- 既存`init-00322`を利用し、新しいInitiativeを作らない。

## 1. Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter

- 推奨slug:
  - `delegation-foundation-asset-inventory-and-thin-chatgpt-adapter`
- 目的:
  - 全vNext Epicが依存する現状inventory、共有境界、`spec-dock-chatgpt`の薄いCLI／Oracle／GitHub bindingを確立する。
- 依存するEpic名:
  - なし
- Requirement coverage:
  - REQ-001, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010, REQ-023, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 2. Integrated Planning Bundle and Planning Workflow Cutover

- 推奨slug:
  - `integrated-planning-bundle-and-planning-workflow-cutover`
- 目的:
  - Initiative／Epic／Issue Planningをcomplete-file生成、セルフレビュー、canonical copy、fresh Planning Reviewへ切り替える。
- 依存するEpic名:
  - `Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter`
- Requirement coverage:
  - REQ-003, REQ-004, REQ-005, REQ-023, REQ-024, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 3. Contract-Driven Review Protocols and Targeted Review

- 推奨slug:
  - `contract-driven-review-protocols-and-targeted-review`
- 目的:
  - Planning／Checkpoint／DeliveryのFormal Reviewとユーザー向けTargeted Reviewを、契約駆動のScope・Perspective・JSONへ統一する。
- 依存するEpic名:
  - `Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter`
- Requirement coverage:
  - REQ-011, REQ-012, REQ-013, REQ-014, REQ-015, REQ-021, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 4. Repair Batch and Executor-Centered Issue Execution

- 推奨slug:
  - `repair-batch-and-executor-centered-issue-execution`
- 目的:
  - Formal blockerをfrozen Repair Batchへ変換し、custom Executor一つとExecution TrancheでIssueを実行する。
- 依存するEpic名:
  - `Integrated Planning Bundle and Planning Workflow Cutover`
  - `Contract-Driven Review Protocols and Targeted Review`
- Requirement coverage:
  - REQ-016, REQ-017, REQ-018, REQ-019, REQ-023, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 5. Plan-Driven Epic and PR Delivery

- 推奨slug:
  - `plan-driven-epic-and-pr-delivery`
- 目的:
  - Epic Delivery Topology、Issue Exit Contract、Delivery Owner、PR repair、Human Merge Gate、finish semanticsを実装する。
- 依存するEpic名:
  - `Integrated Planning Bundle and Planning Workflow Cutover`
  - `Contract-Driven Review Protocols and Targeted Review`
  - `Repair Batch and Executor-Centered Issue Execution`
- Requirement coverage:
  - REQ-002, REQ-020, REQ-021, REQ-022, REQ-023, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 6. Global Cutover, Asset Parity, and Legacy Surface Removal

- 推奨slug:
  - `global-cutover-asset-parity-and-legacy-surface-removal`
- 目的:
  - 新surfaceの安定後、旧Workflow／Skill／Agent／Doc／Template／Scriptを除去し、全ScopeをvNextへ一括cutoverする。
- 依存するEpic名:
  - `Integrated Planning Bundle and Planning Workflow Cutover`
  - `Contract-Driven Review Protocols and Targeted Review`
  - `Repair Batch and Executor-Centered Issue Execution`
  - `Plan-Driven Epic and PR Delivery`
- Requirement coverage:
  - REQ-023, REQ-024, REQ-025
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。

## 7. End-to-End Dogfood, Final Quality, and Release

- 推奨slug:
  - `end-to-end-dogfood-final-quality-and-release`
- 目的:
  - vNext全体を実際のScopeとPRでdogfoodし、Initiative契約、統合品質、運用性、変更耐性を検証してreleaseする。
- 依存するEpic名:
  - `Delegation Foundation, Asset Inventory, and Thin ChatGPT Adapter`
  - `Integrated Planning Bundle and Planning Workflow Cutover`
  - `Contract-Driven Review Protocols and Targeted Review`
  - `Repair Batch and Executor-Centered Issue Execution`
  - `Plan-Driven Epic and PR Delivery`
  - `Global Cutover, Asset Parity, and Legacy Surface Removal`
- Requirement coverage:
  - REQ-001, REQ-002, REQ-003, REQ-008, REQ-011, REQ-016, REQ-019, REQ-020, REQ-022, REQ-026
- Node作成後の最初のPlanning input:
  - Initiative `requirement.md`、`design.md`、`plan.md`
  - 関連ADR
  - Epicの目的／Scope／Non-goal／completion criteria
  - dependencyのmerge状態
- Exit expectation:
  - 独立したmerge boundaryを持つ。
  - 複数Issueの場合はFinal Quality／Delivery Issueを原則計画する。


## Dependency edge

```text
E1 -> E2
E1 -> E3
E2 -> E4
E3 -> E4
E2 -> E5
E3 -> E5
E4 -> E5
E2 -> E6
E3 -> E6
E4 -> E6
E5 -> E6
E1..E6 -> E7
```

実際の`deps add`操作は、作成後のEpic IDを名前で照合して実行する。

## 作成後の検証

1. 7 EpicがInitiativeの直接子である。
2. Epic名とslugが重複しない。
3. dependency graphがacyclicである。
4. Epic 2と3はEpic 1後に並列readyとなる。
5. Epic 7はEpic 1〜6のすべてに依存する。
6. `validate`と`sync`がPASSする。
7. Node materializationだけを理由にInitiative Planning Bundleを変更しない。
