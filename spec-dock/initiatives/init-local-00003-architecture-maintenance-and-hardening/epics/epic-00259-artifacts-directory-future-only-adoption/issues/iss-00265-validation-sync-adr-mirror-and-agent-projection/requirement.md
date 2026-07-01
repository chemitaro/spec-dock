---
種別: 要件定義書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
関連GitHub: ["#265"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00265 Validation sync ADR mirror and agent projection — Issue 要件定義

## 目的
validate / sync / `.agent` projection / ADR mirror を artifacts-aware にし、canonical docs、future artifacts、legacy discussions を混同しない projection と diagnostics を提供する。

## 上位 trace
- Epic requirements: E-RQ-002, E-RQ-006.
- Epic acceptance criteria: E-AC-005, E-AC-007.
- Epic design decisions: D-000, D-001, D-005.
- Depends on: `iss-00263`, `iss-00264`, and accepted Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`.

## スコープ
- 必須:
  - Artifact filename validation and duplicate guard を validate に接続する。
  - old-only / new-only / mixed layout の validation を pass させる。
  - malformed discussion と malformed artifact を区別した diagnostics を出す。
  - ADR mirror は `discussions/` と `artifacts/` の両方から ADR originals を収集する。
  - sync / `.agent` projection は canonical docs、future artifacts、legacy discussions を distinct labels で出力する。
- 対象外:
  - Artifact creation command。
  - delegated authoring diff guard。
  - docs/skills guidance の文言全面更新。

## 受け入れ条件
- AC-265-001 layouts:
  - old-only, new-only, mixed layout fixtures が validate pass する。
- AC-265-002 malformed:
  - malformed artifact-intent filename と duplicate artifact id は artifact diagnostics として fail する。
- AC-265-003 legacy strictness:
  - malformed/duplicate legacy discussion validation は緩まない。
- AC-265-004 ADR mirror:
  - ADR mirror は legacy `discussions/` ADR と future `artifacts/` ADR を両方収集し、original を移動しない。
- AC-265-005 projection:
  - sync / `.agent` output は canonical docs / artifacts / discussions を区別する。

## 検証期待
- Validation tests, sync projection tests, ADR mirror tests.
- `uv run pytest tests/cli_runtime` and focused unit lanes。

## 依存
- `iss-00263`, `iss-00264`。
- Epic-level artifact domain / filename / draft template ADR。
