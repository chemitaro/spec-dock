---
種別: 実装計画書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00265 Validation sync ADR mirror and agent projection — 実装計画ドラフト

## この計画で満たす要件ID
- AC-265-001 through AC-265-005.

## 実装順序
1. S01 validation layout support.
2. S02 artifact diagnostics and legacy strictness.
3. S03 ADR mirror mixed sources.
4. S04 sync / `.agent` projection labels.
5. S90 docs impact.
6. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-265-001 | AC-265-001 | DES-265-001/002/003 | old/new/mixed layouts pass | validation tests |
| CLOS-265-002 | AC-265-002/003 | DES-265-002/003 | artifact and discussion diagnostics remain distinct | validation tests |
| CLOS-265-003 | AC-265-004 | DES-265-004 | ADR mirror collects both sources | mirror tests |
| CLOS-265-004 | AC-265-005 | DES-265-005 | projection labels are distinct | sync tests |

## 実装ステップ
### S01 validation layout support
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s01-001` old-only pass.
  - `tc-s01-002` new-only pass.
  - `tc-s01-003` mixed pass.
- Reviewer: code-reviewer.

### S02 diagnostics
- Test seeds:
  - `tc-s02-001` malformed artifact fails with artifact diagnostic.
  - `tc-s02-002` malformed discussion still fails with discussion diagnostic.
  - `tc-s02-003` duplicate artifact id fails.
- Reviewer: code-reviewer.

### S03 ADR mirror
- Test seeds:
  - `tc-s03-001` legacy discussion ADR collected.
  - `tc-s03-002` future artifact ADR collected.
  - `tc-s03-003` originals are not moved.
- Reviewer: code-reviewer.

### S04 projection labels
- Test seeds:
  - `tc-s04-001` sync output labels artifacts separately from discussions.
  - `tc-s04-002` canonical docs remain canonical in projection.
- Reviewer: code-reviewer.

## S90 / S99
- S90 documents any changed diagnostics wording.
- S99 requires focused validation/sync tests and final qa/code/spec gates.
- No per-Issue PR; delivery waits for Epic PR.
