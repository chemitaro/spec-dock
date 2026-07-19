---
種別: disc
ID: "20260719t135413z-06-disc"
タイトル: "init-00322 完全Planning Bundle Traceability"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-19"
親: ["init-00322"]
authority: "verification evidence"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
reflected_to: []
---

# init-00322 完全Planning Bundle Traceability

## Scope

このTraceabilityは、差分だけではなく、完全置換用のRequirement、Design、Plan全体を対象とする。

## Requirement coverage

| Requirement | 主なDesign | 主なEpic |
|---|---|---|
| REQ-001〜REQ-005 | Actor／CLI／Planning／Context | 1、2、7 |
| REQ-006〜REQ-009 | Review Architecture | 3、7 |
| REQ-010 | Repair Batch | 4、7 |
| REQ-011〜REQ-013 | Actor／Brief／Executor／Issue Execution | 4、7 |
| REQ-014〜REQ-015 | Issue／Epic／PR Delivery | 5、7 |
| REQ-016〜REQ-018 | Authority／State／Cutover／Parity | 1〜7 |
| REQ-019 | Evaluation／Final Quality | 7 |
| REQ-020〜REQ-024 | Architecture-Aware Execution Brief | 1、4、7 |
| REQ-025 | Comparative evaluation | 7 |

## Acceptance Criteria coverage

| Acceptance Criteria | 主なDesign／Plan |
|---|---|
| AC-001〜AC-018 | vNext全体のActor、Planning、Review、Repair、Execution、Delivery、Cutover |
| AC-019 | exact HEADからEvidenceとApplicable Concernを選択 |
| AC-020 | 特定architectureに依存しない多様task動作 |
| AC-021 | readyのみWorkBenchからArtifactへ昇格 |
| AC-022 | plan.mdへ従属し同一candidate commitへ含める |
| AC-023 | no-hidden-Gitとdeterministic anchor |
| AC-024 | Briefなし／generic／Architecture-Aware比較 |
| AC-025 | 分析品質を第一目的、Codex資源を第二目的として評価 |

## Epic coverage

| Epic | Architecture-Aware Execution Brief responsibility |
|---|---|
| 1 | command skeleton、GitHub binding、deterministic anchors、baseline |
| 2 | Planning BundleへBriefを混入させない |
| 3 | BriefをFormal Reviewへしない。Review／Concern契約を再利用可能にする |
| 4 | Prompt、semantic retrieval、candidate、adoption、freeze、Executor integration、Issue E2E |
| 5 | Briefを利用したIssue成果をEpic／PR Deliveryへ接続 |
| 6 | provider／installed／dogfood parity、stale reference除去、global cutover |
| 7 | quality／resource／latencyの比較、汎用性、Initiative final quality |

## Cross-document consistency

- Requirementの25 REQ、7 NFR、25 AC、13 Metrics、15 RisksをDesignとPlanが扱う。
- Epic数は7で、依存DAGは`E1 → E2/E3 → E4 → E5 → E6 → E7`。
- `plan.md`はIssue全体のPlanning SSOTであり、Execution BriefはArtifactとして従属する。
- DDD／イベント駆動は動的Concernであり必須前提ではない。
- 品質向上とCodex資源効率を別指標で評価する。
