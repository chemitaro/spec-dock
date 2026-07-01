---
種別: 実装計画書（Issue）
ID: "iss-00261"
タイトル: "Artifact domain model and filename contract"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00261 Artifact domain model and filename contract — 実装計画ドラフト

## この計画で満たす要件ID
- AC-261-001 through AC-261-005.
- Epic E-AC-001, E-AC-002, E-AC-004, E-AC-007 foundations.

## 実装順序
1. S01 artifact type catalog.
2. S02 filename parse/generate and id contract.
3. S03 collision / malformed / duplicate detection.
4. S90 docs impact inspection.
5. S99 issue final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-261-001 | AC-261-001 | DES-261-001 | supported catalog excludes `scratch` | unit tests |
| CLOS-261-002 | AC-261-002 | DES-261-002/003 | blank and typed filenames round-trip | unit tests |
| CLOS-261-003 | AC-261-003/004 | DES-261-004/005 | id namespace, malformed and duplicate detection | unit tests |
| CLOS-261-004 | AC-261-005 | DES-261-005 | legacy discussion validation is untouched | regression/inspection |

## 実装ステップ
### S01 artifact type catalog
- Delegation: `dev-coder`; allowed paths `src/.../domain/`, `tests/unit/domain/`; forbidden command/template/scaffold edits.
- Test seeds:
  - `tc-s01-001` acceptance: catalog contains all supported future types.
  - `tc-s01-002` negative: `scratch` is not in future catalog.
- Verification: focused unit test.
- Reviewer: code-reviewer.

### S02 filename parse/generate and id contract
- Delegation: `dev-coder`; allowed paths same as S01.
- Test seeds:
  - `tc-s02-001` typed round-trip for `<ts>-research-slug.md`.
  - `tc-s02-002` blank round-trip for `<ts>-slug.md`.
  - `tc-s02-003` suffix round-trip for `<ts>-01-adr-slug.md`.
- Verification: focused unit test.
- Reviewer: code-reviewer.

### S03 malformed / duplicate detection
- Delegation: `dev-coder`; allowed paths same as S01.
- Test seeds:
  - `tc-s03-001` malformed timestamp/type/slug fail.
  - `tc-s03-002` duplicate artifact id fail.
  - `tc-s03-003` legacy discussion examples remain valid under legacy parser.
- Verification: focused unit test.
- Reviewer: code-reviewer.

## S90 docs impact
- Expected no user-facing docs change except possibly internal developer notes.
- If docs are touched, use `doc-writer` and spec-reviewer docs/spec alignment.

## S99 final quality gate
- `uv run pytest tests/unit` focused lane or narrower equivalent.
- Final qa-reviewer/code-reviewer/spec-reviewer pass before this Issue is considered implementation-complete.
- No PR is created for this Issue alone; delivery waits for the Epic-level PR.
