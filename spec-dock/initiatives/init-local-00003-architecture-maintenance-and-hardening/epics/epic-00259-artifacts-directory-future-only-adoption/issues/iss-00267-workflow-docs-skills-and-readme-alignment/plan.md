---
種別: 実装計画書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00267 Workflow docs skills and README alignment — 実装計画

## この計画で満たす要件ID
- AC-267-001: 新規 working artifact creation guidance は `new artifact` / `artifacts/` を示す。
- AC-267-002: `discussions/` は historical / legacy compatible surface として説明され、新規作成先として推奨されない。
- AC-267-003: `new doc` references は削除済み command、legacy historical reference、runtime removal test、または source identifier として分類される。
- AC-267-004: shipped skills and repo-local mirror は future delegated output boundary と矛盾しない。
- AC-267-005: docs が accepted ADR / Epic requirement/design/plan と一致する。

## 依存関係から導く実装順序
1. S00 planning readiness and classification baseline。
2. S01 provider docs / rules / README alignment。
3. S02 provider template guidance alignment。
4. S03 installed and repo-local skills alignment。
5. S04 dogfooding mirror parity and classification ledger。
6. S90 docs impact resolution。
7. S99 final quality gate, issue finish, and commit。

## ステップ一覧
- S00: Plan readiness and classification baseline。
- S01: Provider docs / rules / README alignment。
- S02: Provider template guidance alignment。
- S03: Installed and repo-local skills alignment。
- S04: Dogfooding mirror parity and classification ledger。
- S90: Docs impact resolution。
- S99: Final quality gate, issue finish, and commit。

## 要件 ↔ ステップ対応
- AC-267-001: S01, S02, S03, S04, S99。
- AC-267-002: S01, S02, S03, S04, S99。
- AC-267-003: S00, S04, S99。
- AC-267-004: S03, S04, S99。
- AC-267-005: S00, S01, S02, S03, S04, S90, S99。

## 仕様固定クロージャ索引
| Closure ID | Requirement | Design | Locked expectation | Evidence |
|---|---|---|---|---|
| CLOS-267-001 | AC-267-001 | DES-267-001 | future artifact creation examples use `new artifact` and target `artifacts/` | provider docs / README inspection |
| CLOS-267-002 | AC-267-002 | DES-267-002 | `discussions/` wording is legacy / historical / preservation when retained | docs / rules inspection |
| CLOS-267-003 | AC-267-003 | DES-267-003 | remaining `new doc` references are classified and no future usage example remains | `rg` classification evidence |
| CLOS-267-004 | AC-267-004 | DES-267-004 | shipped skills route future delegated output to `artifacts/` direct child | skill inspection |
| CLOS-267-005 | AC-267-001, AC-267-002, AC-267-005 | DES-267-005 | template guidance matches artifact catalog, draft-* issue scope, and legacy discussions preservation | template docs inspection |
| CLOS-267-006 | AC-267-004, AC-267-005 | DES-267-006 | dogfooding mirror is aligned or intentional divergence is recorded | diff / report evidence |
| CLOS-267-007 | AC-267-005 | DES-267-007 | runtime/source/test semantics are not changed by this docs Issue unless explicitly justified | diff inspection |
| CLOS-267-008 | AC-267-005 | all | final docs/spec alignment receives fresh `spec-reviewer` pass | reviewer gate |

## 実装ステップ

## S00 Plan Readiness and Classification Baseline
- Owner: main orchestrator。
- Allowed edits: issue-level `design.md`, `plan.md`, `report.md`。
- Activities:
  - Confirm active issue and guidance state。
  - Inspect accepted Epic ADR / Epic design / Issue requirement。
  - Run initial `rg -n "new doc|new artifact|discussions|artifacts"` over target docs / skills / README / mirrors。
  - Classify findings using design classification: future guidance, legacy preservation, removed-command evidence, runtime/source identifier, ambiguous stale guidance。
  - Obtain or record specialist evidence for the standard-grade planning gate。
  - Run fresh `spec-reviewer` for planning docs before implementation。
- Exit criteria:
  - `design.md` and `plan.md` are approved and substantive。
  - `guidance issue-planning` no longer blocks on `design-not-substantive` or missing plan readiness。
  - No open decision blocks docs alignment。
- Report evidence destination:
  - Spec Interpretation / Decision Ledger。
  - Evidence Adoption Ledger。
  - Spec Authoring Gate。
  - Grade Specialist Evidence Gate。
  - Reviewer Gate Status。

## S01 Provider Docs / Rules / README Alignment
- Delegation: `doc-writer`。
- Source of truth:
  - `requirement.md`
  - `design.md` DES-267-001, DES-267-002, DES-267-003, DES-267-007
  - Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`
- Allowed paths:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/**`
- Expected implementation:
  - Update future artifact creation examples to `new artifact`。
  - Update `discussions/` descriptions to legacy / historical / preservation wording where retained。
  - Replace delegated authoring future destination references from `discussions/` to `artifacts/` direct child。
  - Preserve references that are explicitly about reading existing legacy `discussions/` or historical ADRs。
- Forbidden changes:
  - Do not change runtime command implementation。
  - Do not delete or migrate existing discussions。
  - Do not edit tests or source code for wording-only changes。
- Closure evidence:
  - CLOS-267-001, CLOS-267-002, CLOS-267-003, CLOS-267-007。

## S02 Provider Template Guidance Alignment
- Delegation: `doc-writer`。
- Source of truth:
  - `design.md` DES-267-001, DES-267-002, DES-267-005
  - prior Issue 262 template catalog and prior Issue 266 report guidance。
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - provider-side scaffold text only if it embeds user/agent guidance and does not alter runtime behavior。
- Expected implementation:
  - Align template README with artifacts catalog and `new artifact` creation。
  - State that draft-* artifacts are Issue scope only and reuse requirement/design/plan template routing。
  - State that `scratch` is legacy-only and blank is future untyped capture。
  - Keep legacy `discussions/` template references only as preservation/historical context。
- Closure evidence:
  - CLOS-267-001, CLOS-267-002, CLOS-267-005, CLOS-267-007。

## S03 Installed and Repo-local Skills Alignment
- Delegation: `doc-writer`。
- Source of truth:
  - `design.md` DES-267-004, DES-267-006, DES-267-007
  - prior Issue 266 delegated authoring artifacts boundary。
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/**`
  - `.agents/skills/**`
- Expected implementation:
  - Update skills that instruct delegated draft / analysis / report-local output to use target scope `artifacts/` direct child。
  - Ensure skills do not invoke `new doc` for future artifact creation。
  - Keep historical examples only when explicitly labelled as historical or replaced with `new artifact`。
  - Keep canonical docs single-writer / adoption ledger / fresh reviewer gate wording intact。
- Closure evidence:
  - CLOS-267-003, CLOS-267-004, CLOS-267-006, CLOS-267-007。

## S04 Dogfooding Mirror Parity and Classification Ledger
- Delegation: `doc-writer` for docs/skills mirror updates; `dev-coder` only if a focused parity test must change。
- Source of truth:
  - `design.md` DES-267-003, DES-267-006, DES-267-007
  - S00 classification baseline and S01-S03 changes。
- Allowed paths:
  - `spec-dock/docs/**`
  - `spec-dock/templates/**`
  - `.agents/skills/**`
  - issue `report.md`
- Conditional test-edit path:
  - If a focused docs/string/parity assertion fails solely because this Issue intentionally changes shipped guidance wording, delegate the minimal assertion update to `dev-coder`.
  - Allowed test path for that exception: `tests/unit/infra/test_init_update.py`.
  - The exception does not allow runtime implementation, command behavior, fixture migration, or broad test refactors.
- Expected implementation:
  - Mirror provider-side docs/skills where dogfooding consumer surface should match。
  - Record intentional divergence or skipped mirror updates in report。
  - Record final classification evidence for remaining `new doc` / `discussions` references。
  - Confirm remaining `new doc` occurrences are not future usage instructions。
- Closure evidence:
  - CLOS-267-002, CLOS-267-003, CLOS-267-006, CLOS-267-007。

## S90 Docs Impact Resolution
- Owner: main orchestrator with `doc-writer` evidence。
- Activities:
  - Integrate worker evidence into `report.md` ledgers。
  - Confirm all planned docs/skills/template/README surfaces are either updated or explicitly no-op with reason。
  - Confirm no open decision entry blocks Issue finish。
  - Request `spec-reviewer` after report integration。
- Exit criteria:
  - Docs Impact Resolution table marks docs/templates/README/workflow/skills as resolved。
  - Fresh `spec-reviewer` pass is recorded。

## S99 Final Quality Gate
- Owner: main orchestrator。
- Required checks:
  - `rg -n "new doc|new artifact|discussions|artifacts" README.md src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/install_root/.agents/skills spec-dock/docs spec-dock/templates .agents/skills`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - `uv run pytest tests/unit/infra/test_init_update.py -q` only if the conditional docs/string/parity assertion exception is used。
- Required reviews:
  - `spec-reviewer` pass after docs/skills/report integration。
  - `code-reviewer` and `qa-reviewer` only if source/tests/runtime behavior changed。
- Completion:
  - Run `./spec-dock/scripts/spec-dock issue finish` only after all blocking gates pass。
  - Commit this Issue's completed diff on the Issue branch。
  - Do not create per-Issue PR; Epic PR is created after `iss-00268` and Epic-wide quality gate。

## Allowed Files
- Provider-side docs / rules:
  - `src/spec_dock/assets/spec_dock/docs/**`
- Provider-side template guidance:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - wording-only template guidance if needed to remove contradictory future instructions。
- Provider-side installed skills:
  - `src/spec_dock/assets/install_root/.agents/skills/**`
- Repo-local / dogfooding mirrors:
  - `.agents/skills/**`
  - `spec-dock/docs/**`
  - `spec-dock/templates/**`
- Repository README:
  - `README.md`
- Conditional tests:
  - `tests/unit/infra/test_init_update.py` only for minimal docs/string/parity assertion updates caused by intentional shipped guidance wording changes.
- Issue-level canonical evidence:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00267-workflow-docs-skills-and-readme-alignment/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00267-workflow-docs-skills-and-readme-alignment/plan.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00267-workflow-docs-skills-and-readme-alignment/report.md`

## Forbidden Files / Actions
- Do not edit runtime command implementation, parser, registry, artifact validation, sync, scaffold logic, or delegated authoring diff guard in this Issue。
- Do not edit tests unless the conditional `tests/unit/infra/test_init_update.py` path above is needed for a focused docs/string/parity assertion after docs changes。
- Do not move, rename, delete, or auto-migrate existing `discussions/`。
- Do not reintroduce `new doc` command or compatibility shim。
- Do not create new draft-only templates for draft requirement/design/plan。
- Do not create per-Issue PR。
