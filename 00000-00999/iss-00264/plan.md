---
種別: 実装計画書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00264 Future node scaffold artifacts default — 実装計画ドラフト

## この計画で満たす要件ID
- AC-264-001 through AC-264-005.

## 実装順序
1. S01 provider scaffold assets.
2. S02 installer/update expectations.
3. S03 legacy preservation tests.
4. S90 docs impact.
5. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-264-001 | AC-264-001/003 | DES-264-001 | new nodes include artifacts/rules | scaffold tests |
| CLOS-264-002 | AC-264-002 | DES-264-002 | new nodes do not default-create discussions | scaffold tests |
| CLOS-264-003 | AC-264-004/005 | DES-264-003/004 | update preserves legacy discussions and old-only validity | init/update tests |

## 実装ステップ
### S01 provider scaffold assets
- Delegation: `dev-coder` or `doc-writer` depending on asset type.
- Test seeds:
  - `tc-s01-001` new initiative scaffold has `artifacts/`.
  - `tc-s01-002` new epic scaffold has `artifacts/`.
  - `tc-s01-003` new issue scaffold has `artifacts/`.
- Reviewer: code-reviewer for scaffold behavior.

### S02 installer/update expectations
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s02-001` init/update copies artifact rules assets.
  - `tc-s02-002` update does not remove existing `discussions/`.
- Verification: `uv run pytest tests/unit/infra`.
- Reviewer: code-reviewer.

### S03 legacy preservation
- Delegation: `dev-coder`.
- Test seeds:
  - `tc-s03-001` old-only fixture remains valid enough for later validation Issue.
  - `tc-s03-002` no discussion path is renamed.
- Reviewer: code-reviewer.

## S90 / S99
- S90 confirms scaffold docs impact is either updated or handed to `iss-00267`.
- S99 requires focused infra tests and final reviewer gates.
- No per-Issue PR; delivery waits for Epic PR.
