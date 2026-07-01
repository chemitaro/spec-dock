---
種別: 実装計画書（Issue）
ID: "iss-00266"
タイトル: "Delegated authoring artifacts boundary"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00266 Delegated authoring artifacts boundary — 実装計画ドラフト

## この計画で満たす要件ID
- AC-266-001 through AC-266-005.

## 実装順序
1. S01 diff guard allowed artifact path.
2. S02 forbidden side effects rejection.
3. S03 provenance and report guidance.
4. S90 docs/skill impact handoff.
5. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-266-001 | AC-266-001 | DES-266-001 | exactly one new direct-child artifact allowed | diff guard tests |
| CLOS-266-002 | AC-266-002 | DES-266-002 | forbidden side effects fail-closed | negative tests |
| CLOS-266-003 | AC-266-003 | DES-266-003 | provenance is validated | unit tests |
| CLOS-266-004 | AC-266-004/005 | DES-266-004/005 | discussions output is future-noncompliant and report ledger records disposition | tests/docs inspection |

## 実装ステップ
### S01 allowed artifact path
- Delegation: `dev-coder`.
- Test seed: `tc-s01-001` exactly one new artifact direct child passes.
- Reviewer: code-reviewer.

### S02 forbidden side effects
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s02-001` canonical doc write fails.
  - `tc-s02-002` nested/symlink/non-md fails.
  - `tc-s02-003` ignored forbidden side effect fails if created after baseline.
- Reviewer: code-reviewer.

### S03 provenance and report guidance
- Delegation: `dev-coder` for runtime validation, `doc-writer` for report/workflow text.
- Test seeds:
  - `tc-s03-001` missing source_paths/intended_targets fails.
  - `tc-s03-002` role/scope mismatch fails.
  - `tc-s03-003` report ledger examples reference artifacts output.
- Reviewer: code-reviewer for runtime, spec-reviewer for docs.

## S90 / S99
- S90 confirms docs/skills updates are completed here or deferred to `iss-00267`.
- S99 requires focused diff-guard tests and final qa/code/spec gates.
- No per-Issue PR; delivery waits for Epic PR.
