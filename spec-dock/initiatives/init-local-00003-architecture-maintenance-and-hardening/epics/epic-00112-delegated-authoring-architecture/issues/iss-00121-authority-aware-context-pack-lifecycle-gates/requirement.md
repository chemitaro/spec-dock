---
種別: 要件定義書（Issue）
ID: "iss-00121"
タイトル: "Authority Aware Context Pack and Lifecycle Gates"
関連GitHub: ["#121"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# iss-00121 Authority Aware Context Pack and Lifecycle Gates — 要件定義（何を、なぜ行うか）

## 目的
- epic-00112 の v1 amendment を実装可能な追加 Issue として具体化し、purpose-aware context-pack and lifecycle gates that prevent proposed artifacts from becoming implementation authority.
- 完了済み v0 Issue 001〜006 / #113〜#118 は historical evidence として参照のみ行い、計画・報告を上書きしない。

## 背景・現状
- v0 delegated authoring は draft-only evidence workflow として完了している。
- v1 では canonical draft authoring、authority metadata、lifecycle gates、Permission Profile probe、bounded depth=2 delegation、dogfooding evidence を追加 Issue として積み上げる。
- この Issue が閉じる親 Epic 項目: E-RQ-003, E-RQ-005, E-RQ-012 / E-AC-002, E-AC-005。
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
  - schema redefinition owned by iss-00120
  - role permission/profile changes
  - dogfooding pilot success claim

## 非交渉制約
- final authority と phase promotion は main orchestrator と fresh `spec-reviewer` gate が所有する。
- Delegated specialist / author output は証跡または proposed draft であり、final reviewer pass の代替ではない。
- Permission/Profile/host behavior が未検証または fail-open の場合は write-scoped delegated authoring を無効化する。

## 受け入れ条件
- AC-001:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: review/planning contexts may show proposed artifacts as non-authoritative input.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-002:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: implementation, issue ready, issue finish, and phase completion contexts require authority approved plus exact grant.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-003:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: Missing approved artifact, stale promotion record, or insufficient grant blocks lifecycle handoff.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.
- AC-004:
  - アクター: spec-dock maintainer / delegated authoring orchestrator
  - 前提: epic-00112 v1 amendment is the approved parent scope.
  - 操作: Context-pack and .agent state do not disagree about authority/grants.
  - 期待結果: The behavior is observable in provider artifacts, dogfooding evidence, or report gate evidence.
  - 観測点: issue report, managed assets, reviewer verdict, and targeted tests.

## 例外・エッジケース
- EC-001:
  - 条件: Proposed artifact in implementation context is block/incomplete.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.
- EC-002:
  - 条件: Approved artifact without required grant is block/incomplete.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.
- EC-003:
  - 条件: Stale promotion hash/revision blocks downstream handoff.
  - 期待: fail closed, record evidence, and keep v0 workflow available.
  - 観測点: report decision ledger / reviewer finding / targeted test or inspection evidence.

## 用語
- `authority: proposed`: review / planning には使えるが downstream implementation authority ではない状態。
- `authority: approved`: fresh reviewer pass と main promotion record により downstream grant を持つ状態。
- `grant`: implementation / issue ready / issue finish / phase completion など用途別の明示許可。

## 未確定事項
- なし。実装中に host / runtime の制約が判明した場合は `report.md` の decision ledger に記録し、必要なら plan amendment または follow-up Issue にする。
