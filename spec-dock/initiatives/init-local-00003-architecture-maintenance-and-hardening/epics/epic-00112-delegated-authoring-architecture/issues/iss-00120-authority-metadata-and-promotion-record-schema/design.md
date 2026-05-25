---
種別: 設計書（Issue）
ID: "iss-00120"
タイトル: "Authority Metadata and Promotion Record Schema"
関連GitHub: ["#120"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00120 Authority Metadata and Promotion Record Schema — 設計（どう実現するか）

## 目的・制約
- 目的: authority metadata, grants, approval, requirement authority source, and promotion records for delegated canonical drafts.
- 制約: v1 は additive amendment。v0 Issue 001〜006 / #113〜#118 は変更しない。
- 完了条件: E-RQ-001, E-RQ-003, E-RQ-004, E-RQ-012 / E-AC-001, E-AC-005, E-AC-012 を、この Issue の provider change、dogfooding validation、tests、rollback/fallback evidence へ追跡できること。

## 既存実装 / 規約の理解
- Provider source of truth:
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `src/spec_dock/assets/spec_dock/system/active-none/`
- Dogfooding validation surface:
  - `spec-dock/docs/`
  - `spec-dock/templates/`
  - `spec-dock/system/active-none/`
- Runtime / docs / managed asset の変更は provider 側から始め、dogfooding workspace は同期・検証対象として扱う。

## 採用方針 / トレードオフ
- 採用: fail-closed、provider-first、additive rollout、fresh reviewer gate。
- 不採用: v0 完了証跡の再解釈、host behavior の未検証 claim、report-only durable decision。
- rollback / fallback: Revert schema docs/templates/system active-none changes and keep v0 draft-only evidence workflow active.

## 依存関係分析
- 上流:
  - epic-00112 v1 requirement/design/plan/report
  - v0 historical Issue #113〜#118 evidence
- 下流:
  - Later v1 Issues that depend on this contract must not start implementation until this Issue is reviewed and either complete or explicitly fallbacked.
- 実装順序への影響:
  - Provider contract -> tests/content assertions -> dogfooding parity -> final reviews.

## モジュール依存図
```plantuml
@startuml
top to bottom direction
rectangle "epic-00112 v1 amendment" as Epic
rectangle "iss-00120 provider source" as Provider
rectangle "managed tests / assertions" as Tests
rectangle "dogfooding validation" as Dogfood
rectangle "report evidence / reviewer gates" as Report
Epic --> Provider
Provider --> Tests
Provider --> Dogfood
Tests --> Report
Dogfood --> Report
@enduml
```

## インターフェース契約
- Provider artifacts define the durable contract.
- Dogfooding artifacts prove parity and execution evidence only.
- `report.md` records delegated draft evidence, reviewer verdicts, decision ledger entries, and fallback/rollback outcomes.

## ディレクトリ / ファイル変更計画
```text
src/spec_dock/assets/spec_dock/
|-- docs/
|   |-- workflow_spec_authoring.md
|   |-- phase_requirement.md
|   |-- phase_design.md
|   |-- phase_plan.md
|   |-- phase_plan_epic.md
|   `-- phase_plan_issue.md
|-- templates/
|   |-- initiative/report.md
|   |-- epic/report.md
|   `-- issue/report.md
`-- system/active-none/
    |-- initiative/report.md
    |-- epic/report.md
    `-- issue/report.md

tests/
`-- test_init_update.py

spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00112-delegated-authoring-architecture/issues/iss-00120-authority-metadata-and-promotion-record-schema/
|-- report.md
`-- discussions/
```
- S01 は provider docs/templates/system active-none と issue-local report/discussions のみを編集対象にする。
- S02 は managed scaffold/content assertion のため `tests/test_init_update.py` を編集対象に含める。
- S90 は provider source や tests を編集しない。dogfooding docs/templates/system active-none は手動編集せず、`spec-dock update .` による tool-generated parity update のみ許可し、その後 inspection で provider/consumer parity を確認する。

## 要件 → 設計マッピング
- AC-001 -> provider contract, dogfooding evidence, and reviewer gate for iss-00120.
- AC-002 -> provider contract, dogfooding evidence, and reviewer gate for iss-00120.
- AC-003 -> provider contract, dogfooding evidence, and reviewer gate for iss-00120.
- AC-004 -> provider contract, dogfooding evidence, and reviewer gate for iss-00120.

## テスト戦略
  - tests/test_init_update.py managed asset assertions
  - scaffold parity assertions for generated docs/templates/system active-none
- `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` evidence are recorded when relevant.
- Final review gates include `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` during execution.

## リスク / 移行 / ロールバック
- Risk: scope creep into adjacent v1 Issues. Mitigation: keep allowed paths and closes mapping issue-local.
- Risk: delegated/preflight evidence is mistaken for final authority. Mitigation: final reviewer and promotion remain separate.
- Rollback / fallback: Revert schema docs/templates/system active-none changes and keep v0 draft-only evidence workflow active.

## 未確定事項
- なし。Implementation-time discoveries must be recorded in `report.md` and promoted to design/plan/follow-up when durable.
