---
種別: 設計書（Issue）
ID: "iss-00268"
タイトル: "Dogfood artifacts without migrating discussions"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00268 Dogfood artifacts without migrating discussions — 設計ドラフト

## 設計要約
- Dogfooding is an evidence Issue, not a provider implementation Issue.
- The target is this repo's `spec-dock/` workspace after Issues 261-267 have landed in the same Epic branch.
- Final Epic-wide quality gate and one Epic-level PR handoff are part of this Issue's closeout contract.

## 変更面
- Dogfooding workspace:
  - create artifacts through runtime command.
  - record before/after path evidence.
  - run validate/sync.
- Epic docs:
  - update Epic `report.md` with final evidence and pre-PR gate summary.
- 禁止:
  - no legacy `discussions/` migration.
  - no per-Issue PR creation.

## 設計契約
- DES-268-001: dogfooding commands operate on final provider behavior.
- DES-268-002: before/after evidence proves legacy `discussions/` paths are not moved/renamed/deleted.
- DES-268-003: validate/sync evidence is recorded after dogfooding artifact creation.
- DES-268-004: safe smoke covers at least one of ADR/draft/delegated output, or records non-blocking skip rationale.
- DES-268-005: Epic-wide pre-PR gate reviews all Issue changes together before a single Epic PR.

## テスト戦略
- Manual/dogfooding command evidence.
- `./spec-dock/scripts/spec-dock validate`.
- `./spec-dock/scripts/spec-dock sync`.
- Final fresh Epic-wide qa/code/spec review before PR creation.

## 後続 Issue への引き渡し
- This is the final Issue before Epic PR handoff.
