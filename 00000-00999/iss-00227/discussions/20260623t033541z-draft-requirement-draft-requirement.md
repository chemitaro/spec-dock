---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00227"
タイトル: "Introduce Assurance Contract And Classification Runtime"
関連GitHub: ["#227"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00227 Draft Requirement

## 目的
- Active Issue に tracked `assurance.json` を作成し、risk facts から Profile / Complexity を deterministic に分類・表示・検証できる最小 capability を提供する。

## スコープ
- 必須:
  - Assurance domain model / JSON schema / policy preset。
  - `assurance show / classify / verify`。
  - `lite / standard / strict / critical` と `routine / normal / complex / deep` の分離。
  - Standard default、Lite all-positive predicate、hard trigger、unknown fail-closed。
  - `lite_candidate` と `lite_authorized` の分離。
  - `strict-legacy` detection prerequisite。
- 禁止:
  - Skill kernel 切替。
  - artifact composition。
  - GitHub review trigger / blocker policy。
- 対象外:
  - E-RQ-012 の rollout / rollback formal close。I07 が正式 owner。

## Trace
- closes: E-RQ-002, E-RQ-003, E-AC-002, E-AC-003。
- contributes: E-RQ-012 strict-legacy detection prerequisite。

## 受け入れ条件
- AC-001: `assurance classify --stage requirement` が valid JSON を生成する。
- AC-002: 同じ canonical input / policy version から byte-identical classification になる。
- AC-003: Lite predicate に false / unknown があれば `lite_authorized` にならない。
- AC-004: `assurance.json` を持たない既存 Issue は strict-legacy candidate として検出される。

## 依存
- Upstream: G0 Epic Decision Baseline（当初 Epic-scope accepted ADR 5 件）と `epic-00158` の context-surface 境界。後続の dogfooding corrective work により、review instruction source と review completion semantics は `../../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md` を含む後続ADRで追加変更済み。
- Downstream: iss-00228, iss-00229, iss-00231。

## 静的解析前提
- 新規 domain / application / infra modules は型注釈を持ち、MyPy / Ruff 適用後の baseline で追加警告を増やさない。
