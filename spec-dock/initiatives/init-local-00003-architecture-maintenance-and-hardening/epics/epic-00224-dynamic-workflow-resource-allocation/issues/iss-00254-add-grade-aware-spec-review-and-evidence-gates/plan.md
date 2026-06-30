---
種別: 実装計画書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 実装計画書（Strict）

## 1. 実装戦略

G1 の guidance wording と G2 の draft routingを前提に、phase promotion / issue readiness に必要な report evidence を docs / templates / tests へ接続する。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | current report / authoring gate baseline | inspection |
| M1 | Draft Adoption Gate wording / template update | docs / template tests |
| M2 | Fresh Spec Review Gate wording / stale reviewer handling | docs / readiness tests |
| M3 | Grade Evidence Gate wording for Standard / Strict / Critical | docs inspection |
| M4 | Readiness Evidence Gate alignment with R0 | focused tests |
| M90 | provider / dogfooding parity | parity inspection |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | focused tests, validate |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | fresh spec-reviewer pass required for promotion | AC-001 |
| B-002 | delegated adoption ledger required | AC-002 |
| B-003 | stale draft/reviewer cannot promote | AC-003 |
| B-004 | grade-specific specialist evidence required | AC-004 |
| B-005 | missing evidence blocks readiness | AC-005 |
| B-006 | draft cannot self-claim authority | AC-006 |

## 4. 変更対象

- spec authoring workflow docs
- phase docs
- report templates / evidence ledger wording
- issue planning skill guidance
- focused tests for stale / missing evidence where runtime supports them

## 5. 禁止変更

- G3 で `new doc` routing を変更しない。
- G3 で placeholder readiness detector を広げない。
- reviewer pass を human waiver で置き換えない。

## 6. Review / commit gate

- M1〜M4 の docs/templates/runtime hooks は review 可能な単位で分ける。
- M99 では focused tests、validate、未実施理由を `report.md` に記録する。

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00255` に渡せる local closure checkpoint とする。
- M99 通過後、review / evidence gate、readiness evidence hook、report evidence を commit し、その HEAD から `iss-00255` の branch を開始する。
- G4 に渡す前に、Spec review / Evidence Adoption Ledger / delegated evidence の smoke 対象が report から追跡できる状態にする。
