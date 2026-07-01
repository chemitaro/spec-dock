---
種別: 実装計画書（Issue）
ID: "iss-00262"
タイトル: "Artifact templates and rules"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00262 Artifact templates and rules — 実装計画ドラフト

## この計画で満たす要件ID
- AC-262-001 through AC-262-006.
- Depends on `iss-00261`.

## 実装順序
1. S01 artifact template catalog.
2. S02 artifact rules and README guidance.
3. S03 template/routing tests.
4. S90 docs impact alignment.
5. S99 final quality gate.

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-262-001 | AC-262-001 | DES-262-001 | all supported types have template/routing | structural test |
| CLOS-262-002 | AC-262-002/006 | DES-262-002 | blank has no filename token; no scratch | test/inspection |
| CLOS-262-003 | AC-262-003/004 | DES-262-003/005 | ADR and draft routing are represented | template inspection |
| CLOS-262-004 | AC-262-005 | DES-262-004 | rules explain future artifacts and legacy preservation | docs inspection |

## 実装ステップ
### S01 artifact template catalog
- Delegation: `doc-writer` if docs/templates only, `dev-coder` if renderer test support is needed.
- Allowed paths: `src/spec_dock/assets/spec_dock/templates/artifacts/**`, template tests.
- Test seeds:
  - `tc-s01-001` acceptance: each supported type has a template or routing record.
  - `tc-s01-002` negative: `scratch` has no future artifact template.
- Reviewer: spec-reviewer for docs/templates, code-reviewer if tests/code change.

### S02 artifact rules and README guidance
- Delegation: `doc-writer`.
- Allowed paths: provider docs/rules/template README and dogfooding mirror if required.
- Test seeds:
  - `tc-s02-001` inspect: rules mention `artifacts/` as future surface.
  - `tc-s02-002` inspect: rules preserve legacy `discussions/`.
- Reviewer: spec-reviewer docs/spec alignment.

### S03 template/routing tests
- Delegation: `dev-coder` if automated structural tests are added.
- Test seeds:
  - `tc-s03-001` acceptance: template catalog structural assertion passes.
  - `tc-s03-002` acceptance: blank frontmatter records template identity.
- Verification: focused pytest lane.
- Reviewer: code-reviewer.

## S90 / S99
- S90 confirms docs/template guidance is coherent.
- S99 requires focused tests plus final qa/code/spec review.
- No per-Issue PR; delivery waits for Epic PR.
