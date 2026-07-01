---
種別: 設計書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00267 Workflow docs skills and README alignment — 設計ドラフト

## 設計要約
- Provider-side docs and shipped skills become the primary guidance source for `new artifact` and `artifacts/`.
- Dogfooding mirror is inspected/refreshed only as provider-side validation/mirror work.
- `new doc` references are classified, not blindly removed.

## 変更面
- Provider source:
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/install_root/.agents/skills/**`
  - top-level README / shipped guide if applicable.
- Dogfooding mirror:
  - corresponding `spec-dock/docs/**`, `.agents/skills/**` when provider mirror parity is expected.

## 設計契約
- DES-267-001: new working artifact creation guidance uses `new artifact`.
- DES-267-002: `discussions/` is described as legacy/historical compatible surface.
- DES-267-003: remaining `new doc` text is explicitly historical, removed-command behavior, or test fixture context.
- DES-267-004: skills must not instruct delegated authoring to write future drafts under `discussions/`.

## テスト戦略
- `rg` classification evidence.
- Provider/mirror content comparison where existing tests expect parity.
- docs/spec alignment review by `spec-reviewer`.

## 後続 Issue への引き渡し
- `iss-00268` uses updated guidance during dogfooding and final Epic report evidence.
