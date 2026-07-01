---
種別: 実装計画書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00267 Workflow docs skills and README alignment — 実装計画ドラフト

## この計画で満たす要件ID
- AC-267-001 through AC-267-005.

## 実装順序
1. S01 classify remaining `new doc` references.
2. S02 provider docs / README update.
3. S03 shipped skills / workflow guidance update.
4. S04 mirror/parity verification.
5. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-267-001 | AC-267-001/002 | DES-267-001/002 | guidance points future creation to `new artifact` and `artifacts/` | docs inspection |
| CLOS-267-002 | AC-267-003 | DES-267-003 | remaining `new doc` references are classified | `rg` evidence |
| CLOS-267-003 | AC-267-004 | DES-267-004 | skills no longer route future delegated output to discussions | skill inspection |
| CLOS-267-004 | AC-267-005 | all | docs match ADR/Epic specs | spec-reviewer |

## 実装ステップ
### S01 classify references
- Delegation: `doc-writer`.
- Test seed: `tc-s01-001` `rg "new doc|new artifact|discussions|artifacts"` classification table is recorded in report.
- Reviewer: spec-reviewer.

### S02 provider docs / README
- Delegation: `doc-writer`.
- Allowed paths: provider docs/templates README/top README as needed.
- Test seeds:
  - `tc-s02-001` new creation examples use `new artifact`.
  - `tc-s02-002` legacy discussions wording is compatibility/historical.
- Reviewer: spec-reviewer.

### S03 skills / workflow guidance
- Delegation: `doc-writer`.
- Test seeds:
  - `tc-s03-001` shipped skills point future delegated output to artifacts.
  - `tc-s03-002` issue/epic workflow text does not contradict accepted ADR.
- Reviewer: spec-reviewer.

### S04 mirror/parity
- Delegation: `doc-writer` or `dev-coder` if parity tests need update.
- Test seed: `tc-s04-001` provider and dogfooding mirror are intentionally aligned or divergence is recorded.
- Reviewer: spec-reviewer/code-reviewer as appropriate.

## S99 final quality gate
- docs/spec reviewer pass is mandatory; code-reviewer only if tests/runtime asset list changes.
- No per-Issue PR; delivery waits for Epic PR.
