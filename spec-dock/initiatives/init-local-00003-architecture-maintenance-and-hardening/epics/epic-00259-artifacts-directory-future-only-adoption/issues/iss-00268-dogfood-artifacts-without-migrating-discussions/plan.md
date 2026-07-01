---
種別: 実装計画書（Issue）
ID: "iss-00268"
タイトル: "Dogfood artifacts without migrating discussions"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00268 Dogfood artifacts without migrating discussions — 実装計画ドラフト

## この計画で満たす要件ID
- AC-268-001 through AC-268-006.
- Epic E-AC-010 and final cross-Epic evidence.

## 実装順序
1. S01 dogfooding baseline and legacy discussions snapshot.
2. S02 blank and typed artifact command smoke.
3. S03 ADR/draft/delegated safe smoke or explicit skip.
4. S04 validate/sync evidence.
5. S90 Epic report closeout.
6. S99 Epic-wide pre-PR quality gate and PR handoff.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-268-001 | AC-268-001/002 | DES-268-001 | dogfooding creates blank and typed artifacts under artifacts | command evidence |
| CLOS-268-002 | AC-268-003 | DES-268-002 | legacy discussions unchanged | before/after evidence |
| CLOS-268-003 | AC-268-004 | DES-268-003 | validate/sync pass and projection labels are clear | command evidence |
| CLOS-268-004 | AC-268-005 | DES-268-004 | safe ADR/draft/delegated smoke or skip rationale | report evidence |
| CLOS-268-005 | AC-268-006 | DES-268-005 | Epic-wide quality gate before one PR | reviewer evidence |

## 実装ステップ
### S01 baseline snapshot
- Delegation: `dev-coder` or orchestrated command execution.
- Test seed: `tc-s01-001` record `find`/`rg --files` snapshot of current discussions/artifacts paths.
- Reviewer: spec-reviewer for evidence sufficiency.

### S02 artifact command smoke
- Test seeds:
  - `tc-s02-001` create blank artifact in dogfooding node.
  - `tc-s02-002` create typed artifact in dogfooding node.
  - `tc-s02-003` verify filenames and frontmatter.
- Reviewer: code-reviewer if runtime diff is touched; otherwise spec-reviewer evidence review.

### S03 ADR/draft/delegated smoke
- Test seed: `tc-s03-001` run one safe smoke if supported after prior Issues; otherwise record skip reason and non-blocking rationale.
- Reviewer: spec-reviewer.

### S04 validate/sync
- Test seeds:
  - `tc-s04-001` `./spec-dock/scripts/spec-dock validate` passes.
  - `tc-s04-002` `./spec-dock/scripts/spec-dock sync` passes and labels are inspected.
- Reviewer: qa-reviewer/spec-reviewer.

### S90 Epic report closeout
- Update Epic `report.md` with all Issue completion and dogfooding evidence.
- No per-Issue PR is created.

### S99 Epic-wide pre-PR quality gate
- Run Epic-wide qa-reviewer, code-reviewer, and spec-reviewer against the full diff.
- Only after all pass, use Epic-level PR creation/merge-prep flow.
