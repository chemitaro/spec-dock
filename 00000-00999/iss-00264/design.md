---
種別: 設計書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00264 Future node scaffold artifacts default — 設計ドラフト

## 設計要約
- Provider-side scaffold assets for initiative/epic/issue create `artifacts/` by default.
- `discussions/` remains legacy-valid but is not created by default for new nodes.
- update/init behavior must preserve existing legacy directories.

## 変更面
- Provider source:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/` or scaffold source locations.
  - installer/update expectations in `src/spec_dock/cli.py` if asset list changes.
- Tests:
  - `tests/unit/infra/test_init_update.py`
  - CLI runtime scaffold fixtures if present.

## 設計契約
- DES-264-001: new initiative/epic/issue scaffold includes `artifacts/` and rules entry.
- DES-264-002: new scaffold does not create `discussions/` by default.
- DES-264-003: update does not move, delete, or rewrite existing `discussions/`.
- DES-264-004: old-only layout remains valid; validation behavior itself is completed by `iss-00265`.

## テスト戦略
- Scaffold snapshot/content assertions.
- init/update tests for new target repo.
- before/after assertions that existing `discussions/` remains untouched.

## 後続 Issue への引き渡し
- `iss-00265` uses new/old/mixed scaffold fixtures for validation and projection.
