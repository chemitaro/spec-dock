---
種別: disc
ID: "20260716t131924z-02-disc"
タイトル: "Initiative Requirement Design Epic Traceability Matrix"
状態: "proposed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
authority: "synthesized"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
reflected_to:
  - "plan.md"
---

# Initiative Requirement–Design–Epic Traceability Matrix

## 目的

全Initiative Requirementが設計sectionと少なくとも一つのEpicへ割り当てられていることを確認する。

| Requirement | Design coverage | Epic coverage |
|---|---|---|
| REQ-001 | 設計 3〜4 | Epic 1, Epic 7 |
| REQ-002 | 設計 4、10 | Epic 5, Epic 7 |
| REQ-003 | 設計 6 | Epic 2, Epic 7 |
| REQ-004 | 設計 6.2 | Epic 2 |
| REQ-005 | 設計 6.3 | Epic 2 |
| REQ-006 | 設計 5.1〜5.2 | Epic 1 |
| REQ-007 | 設計 5.1、5.4 | Epic 1 |
| REQ-008 | 設計 5.3、13 | Epic 1, Epic 7 |
| REQ-009 | 設計 5.2 | Epic 1 |
| REQ-010 | 設計 5.5 | Epic 1 |
| REQ-011 | 設計 7.1 | Epic 3, Epic 7 |
| REQ-012 | 設計 7.2 | Epic 3 |
| REQ-013 | 設計 7.3 | Epic 3 |
| REQ-014 | 設計 7.4〜7.5 | Epic 3 |
| REQ-015 | 設計 7.1、7.4 | Epic 3 |
| REQ-016 | 設計 8 | Epic 4, Epic 7 |
| REQ-017 | 設計 9.1 | Epic 4 |
| REQ-018 | 設計 9.2 | Epic 4 |
| REQ-019 | 設計 10.1〜10.2 | Epic 4, Epic 7 |
| REQ-020 | 設計 10.2〜10.3 | Epic 5, Epic 7 |
| REQ-021 | 設計 7.1、10.3 | Epic 3, Epic 5 |
| REQ-022 | 設計 10.4 | Epic 5, Epic 7 |
| REQ-023 | 設計 3、11 | Epic 1, Epic 2, Epic 4, Epic 5, Epic 6 |
| REQ-024 | 設計 12 | Epic 2, Epic 6 |
| REQ-025 | 設計 12、14 | Epic 1, Epic 2, Epic 3, Epic 4, Epic 5, Epic 6 |
| REQ-026 | 設計 14 | Epic 7 |

## Acceptance Criteria coverage

| Acceptance Criteria | 主なEpic |
|---|---|
| AC-001 | Initiative Planning adoption、Epic 7 |
| AC-002〜AC-003 | Epic 1 |
| AC-004 | Epic 2 |
| AC-005〜AC-007 | Epic 3 |
| AC-008〜AC-010 | Epic 4 |
| AC-011〜AC-014 | Epic 5 |
| AC-015〜AC-017 | Epic 6 |
| AC-018 | Epic 7 |

## Review rule

- Epic Planning時に、自Epicへ割り当てられたRequirementとACをRequirement／Design／Planへ具体化する。
- Epic間の責務移動が必要な場合はInitiative `plan.md`を更新し、fresh Initiative Planning ReviewとHuman approvalを得る。
- Final Epicはこのmatrixを証拠indexとして使い、各Epicの局所Reviewを再実行せず、欠落と統合不整合を評価する。
