---
種別: 設計書（Issue）
ID: "iss-00266"
タイトル: "Delegated authoring artifacts boundary"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00266 Delegated authoring artifacts boundary — 設計ドラフト

## 設計要約
- Delegated authoring output boundary moves from `scope_dir / "discussions"` to `scope_dir / "artifacts"`.
- The allowed mutation is exactly one new direct-child Markdown artifact under the target scope.
- Provenance and adoption evidence remain required; canonical docs are still main-orchestrator-owned.

## 変更面
- Provider source:
  - `domain/delegated_authoring.py`
  - `application/delegated_authoring.py`
  - report / workflow guidance around delegated draft evidence.
- Tests:
  - positive direct-child artifact diff guard.
  - negative forbidden side effects.
  - provenance validation.

## 設計契約
- DES-266-001: allowed output is one new direct-child `.md` under target `artifacts/`.
- DES-266-002: symlink, nested, non-md, existing update, delete, rename/copy, mixed staged/unstaged, unmerged, out-of-scope, forbidden root side effects are rejected.
- DES-266-003: required provenance fields remain non-empty and role/scope-consistent.
- DES-266-004: `discussions/` delegated output is future-noncompliant and adoption-ineligible unless explicitly treated as historical evidence.
- DES-266-005: report ledger records adoption/rejection and diff guard result.

## テスト戦略
- Domain diff guard unit tests.
- Application boundary tests with baseline status.
- Ignored/forbidden side effect negative tests.
- Docs/spec inspection for report evidence guidance.

## 後続 Issue への引き渡し
- `iss-00267` updates docs/skills to this boundary.
- `iss-00268` can smoke delegated output only after this behavior exists.
