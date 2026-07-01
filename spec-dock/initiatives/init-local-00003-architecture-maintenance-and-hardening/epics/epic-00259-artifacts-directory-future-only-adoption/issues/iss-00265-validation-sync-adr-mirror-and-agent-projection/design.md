---
種別: 設計書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00265 Validation sync ADR mirror and agent projection — 設計ドラフト

## 設計要約
- validate は `discussions/` と `artifacts/` を別 validators として扱い、old-only/new-only/mixed layout を許容する。
- ADR mirror discovery は legacy discussions ADR originals と future artifacts ADR originals の両方を読む。
- sync / `.agent` projection は canonical docs、future artifacts、legacy discussions を distinct labels で出力する。

## 変更面
- Provider source:
  - `domain/validation.py`
  - `application/sync_state.py` and ADR mirror discovery path.
  - presentation diagnostics / projection renderers.
- Tests:
  - validation layout fixtures.
  - sync projection tests.
  - ADR mirror symlink target tests.

## 設計契約
- DES-265-001: directory absence is not by itself invalid for old or new nodes.
- DES-265-002: if `discussions/` exists, legacy strict validation still runs.
- DES-265-003: if `artifacts/` exists, artifact validation runs with artifact diagnostics.
- DES-265-004: ADR mirror collects both locations without moving originals.
- DES-265-005: projection labels must not imply artifacts are canonical docs.

## テスト戦略
- old-only/new-only/mixed pass fixtures.
- malformed artifact fail fixtures.
- legacy malformed discussion fail fixtures.
- ADR mirror mixed source fixture.
- sync output label assertions.

## 後続 Issue への引き渡し
- `iss-00266` relies on validation semantics for delegated artifacts.
- `iss-00268` uses validate/sync output as dogfooding evidence.
