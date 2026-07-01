---
種別: 実装計画書（Issue）
ID: "iss-00263"
タイトル: "New artifact command and new doc removal"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00263 New artifact command and new doc removal — 実装計画ドラフト

## この計画で満たす要件ID
- AC-263-001 through AC-263-007.
- Epic E-AC-001, E-AC-002, E-AC-003, E-AC-004, E-AC-006, E-AC-009.

## 実装順序
1. S01 request/result and use case.
2. S02 CLI parser/help and `new doc` removal.
3. S03 artifact creation happy paths and old-node setup.
4. S04 draft-* assurance/profile no-write preflight.
5. S90 docs impact check.
6. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-263-001 | AC-263-001/002 | DES-263-001/003 | blank and typed commands create artifacts | CLI tests |
| CLOS-263-002 | AC-263-003 | DES-263-001/005 | catalog coverage and unknown type no-write | CLI/unit tests |
| CLOS-263-003 | AC-263-004 | DES-263-006 | `new doc` removed without custom hint | help/CLI tests |
| CLOS-263-004 | AC-263-005/006 | DES-263-005 | draft profile preflight and unsupported scope no-write | CLI tests |
| CLOS-263-005 | AC-263-007 | DES-263-004 | old-node on-demand setup preserves discussions | filesystem test |

## 実装ステップ
### S01 use case contract
- Delegation: `dev-coder`.
- Allowed paths: application contracts/use case, focused tests.
- Test seeds:
  - `tc-s01-001` request requires exactly one scope.
  - `tc-s01-002` result includes type/id/path.
- Reviewer: code-reviewer.

### S02 CLI registration and removal
- Delegation: `dev-coder`.
- Allowed paths: command parser/presentation/CLI tests.
- Test seeds:
  - `tc-s02-001` `new artifact --help` lists supported shape.
  - `tc-s02-002` `new --help` omits `doc`.
  - `tc-s02-003` `new doc ...` fails as unknown/argparse without custom migration hint.
- Reviewer: code-reviewer.

### S03 creation behavior
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s03-001` blank issue artifact success.
  - `tc-s03-002` typed epic artifact success.
  - `tc-s03-003` legacy node creates `artifacts/` without touching `discussions/`.
- Verification: `uv run pytest tests/cli_runtime`.
- Reviewer: code-reviewer.

### S04 draft safety
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s04-001` valid issue `.assurance.json` creates draft artifact.
  - `tc-s04-002` missing/stale/invalid profile fails no-write.
  - `tc-s04-003` initiative/epic draft scope fails no-write.
- Reviewer: code-reviewer.

## S90 / S99
- S90 classifies docs impact for command examples.
- S99 requires focused cli_runtime/unit tests, qa-reviewer, issue-wide code-reviewer, final spec-reviewer.
- No per-Issue PR; delivery waits for Epic PR.
