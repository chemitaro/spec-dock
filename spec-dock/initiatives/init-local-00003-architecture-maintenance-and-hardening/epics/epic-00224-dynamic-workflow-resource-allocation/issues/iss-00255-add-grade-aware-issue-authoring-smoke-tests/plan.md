---
種別: 実装計画書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — Issue 実装計画書（Strict）

## 1. 実装戦略

R0〜G3 の成果を前提に、representative fixture と focused smoke tests で grade-aware authoring workflow の統合崩れを検出する。テストは hermetic に保ち、live GitHub や外部サービスを必要としない。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | current test / template baseline | inspection |
| M1 | Lite template smoke | focused CLI / template test |
| M2 | Standard / Strict / Critical M99 gate smoke | focused CLI / template test |
| M3 | draft-design / draft-plan routing smoke | `new doc` CLI test |
| M4 | missing / invalid / stale assurance fail-closed smoke | no-write test |
| M5 | readiness false-positive regression smoke | workflow/guidance test |
| M6 | delegated evidence / EAL / fresh review evidence smoke | docs / report fixture test |
| M90 | provider / dogfooding parity inspection | parity check |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | static analysis, lint, tests, validate |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | Lite remains lightweight | AC-001 |
| B-002 | Standard+ M99 quality gate exists | AC-002 |
| B-003 | draft source follows `authorized_profile` | AC-003 |
| B-004 | invalid assurance state is no-write | AC-004 |
| B-005 | placeholder artifacts are not ready | AC-005 |
| B-006 | evidence gates are observable | AC-006 |
| B-007 | provider and dogfooding docs stay aligned | AC-007 |
| B-008 | report records commands/results/risks | AC-008 |

## 4. 変更対象

- focused smoke tests for grade-aware authoring workflow
- test fixtures for Lite / Standard / Strict / Critical
- provider / dogfooding parity inspection helper or test assertions
- report evidence for executed / skipped checks

## 5. 禁止変更

- G4 で R0〜G3 の本体責務を実装しない。
- Lite に Standard 以上の gate を混入させない。
- external GitHub repository を必須条件にしない。

## 6. Review / commit gate

- M1〜M6 は、失敗時にどの upstream slice の漏れか分かる単位で review する。
- M99 では static analysis / lint / focused tests / validate の結果と、未実施理由を `report.md` に記録する。

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は Epic 最終品質ゲートへ渡す local closure checkpoint とする。
- M99 通過後、grade-aware smoke tests、provider / dogfooding parity evidence、report evidence を commit し、その HEAD を Epic #224 corrective tranche の PR candidate head とする。
- PR 作成前に、Epic `plan.md` の「Epic 最終品質ゲート（単一 PR 前）」を実行し、fresh spec review、code review、QA review、required tests の結果を Epic / Issue reports に記録する。
