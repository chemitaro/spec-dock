---
種別: 要件定義書（Issue）
ID: "iss-00262"
タイトル: "Artifact templates and rules"
関連GitHub: ["#262"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00262 Artifact templates and rules — Issue 要件定義

## 目的
`templates/artifacts/` catalog と artifact rules を provider-side source of truth として追加し、`new artifact` が利用する blank / generic / ADR / draft-* / delegated evidence-friendly templates の境界を固定する。

## 上位 trace
- Epic requirements: E-RQ-001, E-RQ-004, E-RQ-005, E-RQ-008.
- Epic acceptance criteria: E-AC-001, E-AC-002, E-AC-004, E-AC-006.
- Epic design decisions: D-000, D-002, D-003, D-004.
- Depends on: accepted Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`.

## スコープ
- 必須:
  - `templates/artifacts/` を provider-side assets に追加する。
  - `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`, `adr`, `draft-requirement`, `draft-design`, `draft-plan` の template routing を提供する。
  - blank template は frontmatter に `template: "blank"` を記録する。
  - draft-* は独自の draft-only content templates を作らず、既存の requirement / design / plan templates と Issue grade/profile-aware template selection を再利用する routing を定義する。
  - `artifacts/rules.md` の source docs を用意する。
  - template README / catalog guidance を更新する。
- 対象外:
  - `new artifact` command implementation。
  - `.assurance.json` preflight の実行。
  - new node scaffold default 変更。

## 受け入れ条件
- AC-262-001 catalog templates:
  - future catalog の全 supported type に template または明示 routing がある。
- AC-262-002 blank:
  - blank template は filename token としての `blank` を要求せず、frontmatter で template identity を示す。
- AC-262-003 ADR:
  - ADR template は future original が `artifacts/` に置かれ、accepted ADR authority と mirror eligibility を表現できる。
- AC-262-004 draft:
  - draft-requirement/design/plan routing は既存の requirement/design/plan template contract と issue scope profile-aware template selection へ接続できる。
- AC-262-005 rules:
  - `artifacts/rules.md` は future working artifact surface と legacy `discussions/` preservation を説明する。
- AC-262-006 no scratch:
  - `scratch` template は future artifact catalog として追加されない。

## 検証期待
- Template presence / rendering source tests.
- README/rules structural inspection.
- `uv run pytest tests/unit` の scaffold/template lane。

## 依存
- Epic-level artifact domain / filename / draft template ADR。
