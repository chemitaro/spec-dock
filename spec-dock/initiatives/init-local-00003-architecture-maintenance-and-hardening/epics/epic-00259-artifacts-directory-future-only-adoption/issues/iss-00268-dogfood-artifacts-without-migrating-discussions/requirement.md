---
種別: 要件定義書（Issue）
ID: "iss-00268"
タイトル: "Dogfood artifacts without migrating discussions"
関連GitHub: ["#268"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00268 Dogfood artifacts without migrating discussions — Issue 要件定義

## 目的
この repo の dogfooding workspace で `artifacts/` future creation、legacy `discussions/` non-migration、validate / sync / ADR / draft or delegated smoke を実証し、Epic-wide pre-PR quality gate の証跡を残す。

## 上位 trace
- Epic requirements: E-RQ-007 and cross-E-RQ evidence.
- Epic acceptance criteria: E-AC-010 and final cross-E-AC evidence.
- Depends on: `iss-00262` through `iss-00267`, plus accepted Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`.

## スコープ
- 必須:
  - Dogfooding node で blank and typed artifacts を作成する。
  - Safe な範囲で ADR / draft / delegated-output smoke を実施する。
  - Existing `discussions/` が移動/rename/delete/link rewrite されないことを確認する。
  - `./spec-dock/scripts/spec-dock validate` と `sync` evidence を残す。
  - Epic-wide pre-PR quality gate と PR creation step の準備証跡を Epic report に残す。
- 対象外:
  - Provider-side runtime の新規実装。
  - Legacy discussions migration。
  - 各 Issue ごとの個別 PR 作成。

## 受け入れ条件
- AC-268-001 blank:
  - dogfooding workspace で blank artifact が `artifacts/` に作成される。
- AC-268-002 typed:
  - typed artifact が expected filename contract で作成される。
- AC-268-003 no migration:
  - 既存 `discussions/` paths は before/after で移動/rename/delete/link rewrite されない。
- AC-268-004 validate sync:
  - validate and sync pass, and projection distinguishes artifacts/discussions/canonical docs.
- AC-268-005 smoke:
  - ADR / draft / delegated output のうち安全に実施可能な smoke が少なくとも1つ記録される。実施しない smoke は理由と non-blocking 根拠を残す。
- AC-268-006 epic-wide gate:
  - all Issues complete 後、Epic-wide spec/code/QA review gate を通し、問題がなければ Epic単位の PR 作成へ進める。

## 検証期待
- Dogfooding command output, before/after path evidence, validate/sync output, Epic report evidence.
- Final Epic pre-PR review evidence。

## 依存
- `iss-00262`, `iss-00263`, `iss-00264`, `iss-00265`, `iss-00266`, `iss-00267`。
- Epic-level artifact domain / filename / draft template ADR。
