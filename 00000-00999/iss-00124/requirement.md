---
種別: 要件定義書（Issue）
ID: "iss-00124"
タイトル: "Canonical Draft Authoring Role Rewrite"
関連GitHub: ["#124"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# iss-00124 Canonical Draft Authoring Role Rewrite — 要件定義（何を、なぜ行うか）

## 目的
- epic-00112 の v1 amendment を実装可能な追加 Issue として具体化し、rewrite system-architect and implementation-planner roles from read-only proposal producers to authority-aware canonical draft authors without final authority.
- 完了済み v0 Issue 001〜006 / #113〜#118 は historical evidence として参照のみ行い、計画・報告を上書きしない。

## 背景・現状
- v0 delegated authoring は draft-only evidence workflow として完了している。
- v1 では canonical draft authoring、authority metadata、lifecycle gates、Permission Profile probe、bounded depth=2 delegation、dogfooding evidence を追加 Issue として積み上げる。
- この Issue が閉じる親 Epic 項目: E-RQ-001, E-RQ-002, E-RQ-004, E-RQ-008, E-RQ-009 / E-AC-003, E-AC-004, E-AC-009。
- 情報源:
  - `epic-00112/requirement.md`
  - `epic-00112/design.md`
  - `epic-00112/plan.md` の `v1 Amendment Plan`
  - `epic-00112/report.md` の v1 pending E-AC table

## スコープ
- 必須:
  - Provider source of truth を起点に変更を計画する。
  - Dogfooding workspace は validation / parity surface として扱う。
  - `report.md` に reviewer gate、delegation evidence、rollback/fallback evidence を残せる形にする。
- 禁止:
  - 完了済み v0 Issue 001〜006 / #113〜#118 の計画・報告・証跡を v1 向けに書き換える。
  - proposed artifact を implementation / issue ready / issue finish / phase completion の authority として扱う。
- 対象外:
  - requirement authoring delegation
  - final authority transfer
  - runtime gate implementation

## 非交渉制約
- final authority と phase promotion は main orchestrator と fresh `spec-reviewer` gate が所有する。
- Delegated specialist / author output は証跡または proposed draft であり、final reviewer pass の代替ではない。
- Permission/Profile/host behavior が未検証または fail-open の場合は write-scoped delegated authoring を無効化する。

## 受け入れ条件
- AC-001:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: system-architect can update draft design.md as authority proposed when requirement authority is valid.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-002:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: implementation-planner can update draft plan.md as authority proposed when design authority is valid.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-003:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: Roles cannot promote, approve, claim final reviewer pass, ask user directly, or update previous phase artifacts.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-004:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: Permission unverified or revision mismatch falls back to discussions proposal path.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.

## 例外・エッジケース
- EC-001:
  - 条件: Requirement gap during design returns to requirement gate.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.
- EC-002:
  - 条件: Design gap during plan returns to design gate.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.
- EC-003:
  - 条件: Preflight pass is never final pass.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.

## 用語
- `authority: proposed`: review / planning には使えるが downstream implementation authority ではない状態。
- `authority: approved`: fresh reviewer pass と main promotion record により downstream grant を持つ状態。
- `grant`: implementation / issue ready / issue finish / phase completion など用途別の明示許可。

## 未確定事項
- なし。実装中に host / runtime の制約が判明した場合は `report.md` の decision ledger に記録し、必要なら plan amendment または follow-up Issue にする。
