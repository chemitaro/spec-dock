---
種別: disc
ID: "20260630t204853z-disc"
タイトル: "Strict Plan Augmentation For G4 Smoke Tests"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00255"]
関連: []
authority: "proposed"
derived_from: []
created_by_role: implementation-planner
scope_id: iss-00255
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_workflow.py
  - tests/unit/domain/test_workflow_state.py
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: failed
---

# Strict Plan Augmentation For G4 Smoke Tests

## 1. Plan Summary

This draft proposes a strict, executable augmentation for `iss-00255` plan hardening. It does not edit canonical docs, implementation code, or tests. The main gap in the current `plan.md` is not scope: it already identifies M1-M6, M90, M95, and M99. The gap is executable step detail: strict plan rows need closure ids, delegation contracts, concrete test seeds, path boundaries, verification commands, report evidence destinations, and amendment triggers.

G4 must remain a closure slice for smoke tests, parity, and evidence fixtures. It must not implement R0-G3 body logic. Issue-local M99 must remain a local handoff checkpoint to the Epic final quality gate, not a PR creation or merge-preparation gate.

Source snapshot used for this draft: repository HEAD `da0f0361dab1a7b4bccebcb7fe49d094df47da69`; active scope `iss-00255`; Epic `epic-00224`.

## 2. Requirement / Design Traceability

- `AC-001` maps to `C-G4-001`: Lite smoke must prove no mid-step commit gate or full static analysis mandate is introduced.
- `AC-002` maps to `C-G4-002`: Standard / Strict / Critical smoke must prove M99 includes static analysis, lint, tests, report, and commit candidate gate.
- `AC-003` maps to `C-G4-003`: `draft-design` / `draft-plan` source must follow `.assurance.json` `classification.authorized_profile`.
- `AC-004` maps to `C-G4-004`: missing / invalid / stale `.assurance.json` must fail closed with no discussion write.
- `AC-005` maps to `C-G4-005`: placeholder, heading-only, and stale evidence fixtures must remain not execution-ready.
- `AC-006` maps to `C-G4-006`: delegated specialist evidence, Evidence Adoption Ledger, and fresh `spec-reviewer` evidence must be observable in readiness smoke.
- `AC-007` maps to `C-G4-007`: provider and dogfooding docs/templates parity must be inspected by test or deterministic assertion.
- `AC-008` maps to `C-G4-008`: `report.md` must receive commands, results, skipped checks, and residual risk evidence.

Epic trace:

- `E-RQ-006` / `E-AC-006`: readiness false-positive regression subset only.
- `E-RQ-022` / `E-AC-022`: grade-aware authoring workflow smoke subset only.
- Epic plan G4: integrated smoke after R0, G1, G2, and G3.

## 3. Milestones

- `M0 Baseline`: inspect existing test surfaces and identify already-covered G2/G3 cases.
- `M1 Lite Smoke`: lock lightweight Lite plan expectations.
- `M2 Standard+ M99 Smoke`: lock Standard / Strict / Critical final local gate expectations.
- `M3 Draft Routing Smoke`: lock authorized-profile draft source routing.
- `M4 Fail-Closed Draft Smoke`: lock no-write behavior for invalid assurance state.
- `M5 Readiness Regression Smoke`: lock placeholder / heading-only / stale evidence negative cases.
- `M6 Evidence Gate Smoke`: lock delegated evidence, EAL, and fresh reviewer evidence relation.
- `M90 Parity`: inspect provider / dogfooding docs and template parity.
- `M95 Strict Spec Review`: fresh spec review over the integrated issue evidence.
- `M99 Issue-Local Handoff`: local closure checkpoint for Epic final quality gate; no PR creation.

## 4. Dependency-Derived Execution Order

Strict order should be:

1. `S00` baseline inspection and closure index confirmation.
2. `S01` Lite and Standard+ profile template smoke, because later routing tests need profile fixture conventions.
3. `S02` draft routing and fail-closed no-write smoke, because it depends on G2 behavior and `.assurance.json` fixtures.
4. `S03` readiness regression smoke, because it validates R0 behavior after draft/profile fixture setup.
5. `S04` evidence gate smoke, because it validates G3 behavior and uses report evidence fixtures.
6. `S90` parity inspection, after all relevant docs/templates test expectations are known.
7. `S95` strict spec review readiness.
8. `M99/S99` issue-local handoff to Epic final quality gate.

This order follows Epic dependencies `R0 -> G1 -> G2/G3 -> G4` and avoids implementing any upstream body logic in G4.

## 5. Issue / Step Slicing

### Spec-Locked Closure Index

| id | spec link | locked expectation | observable input/state | guarded bug class | required | evidence level | owner step |
|---|---|---|---|---|---|---|---|
| `C-G4-001` | AC-001 / G4 Lite smoke | Lite does not require mid-step commit or full static analysis | Lite profile plan fixture | Lite over-hardening | yes | red-required | S01 |
| `C-G4-002` | AC-002 / G4 Standard+ smoke | Standard / Strict / Critical include M99 static analysis, lint, tests, report, commit gate | profile plan fixtures | missing final quality gate | yes | red-required | S01 |
| `C-G4-003` | AC-003 / G2 handoff | draft source follows `authorized_profile` | classified issue + `.assurance.json` | wrong profile template routing | yes | covered-existing plus smoke | S02 |
| `C-G4-004` | AC-004 / G2 fail-closed | missing / invalid / stale assurance creates no draft | no valid `.assurance.json` | fallback draft write | yes | covered-existing plus smoke | S02 |
| `C-G4-005` | AC-005 / R0 handoff | placeholder / heading-only / stale evidence is not ready | workflow status / guidance fixtures | readiness false positive | yes | red-required | S03 |
| `C-G4-006` | AC-006 / G3 handoff | specialist evidence, EAL, fresh reviewer evidence are jointly observed | report evidence fixture | evidence gate shortcut | yes | red-required | S04 |
| `C-G4-007` | AC-007 / Epic parity | provider and dogfooding docs/templates match or have documented exception | provider and dogfooding paths | shipped asset drift | yes | inspect-only or assertion | S90 |
| `C-G4-008` | AC-008 / report evidence | report captures commands, results, skipped checks, and risks | issue report session log | unverifiable closure | yes | manual-required | M99 |

### `S00` Baseline And Test Surface Confirmation

- `delegation contract`: `repo-analyst` or parent read-only inspection. Input docs are this Issue requirement/design/plan/report, Epic requirement/design/plan, workflow docs, and listed tests. No file writes except report adoption by main orchestrator.
- `allowed paths`: read-only `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_workflow.py`, `tests/unit/domain/test_workflow_state.py`, `tests/unit/infra/test_init_update.py`, active Issue/Epic docs.
- `forbidden paths`: all implementation code, canonical docs, tests edits during planning.
- `concrete test cases`: `tc-s00-001` inspect existing G2 draft routing tests; `tc-s00-002` inspect existing R0/G3 readiness tests; both link to `C-G4-003` through `C-G4-006`.
- `verification command`: `rg -n "draft-design|draft-plan|Evidence Adoption|stale|workflow_issue_doc_matches_bundled_asset" tests/cli_runtime tests/unit`.
- `report evidence destination`: `report.md` session log, Test Contract Closure, Closure Coverage.
- `amendment trigger`: existing tests already close an AC with no new G4 smoke needed, or no stable public interface exists for a required smoke.

### `S01` Profile Template And M99 Gate Smoke

- `delegation contract`: `dev-coder` owns test additions only. Reviewer focus is `code-reviewer` for test behavior and `spec-reviewer` for plan/spec alignment.
- `allowed paths`: `tests/cli_runtime/test_new.py` for profile draft/template materialization smoke; optionally a focused fixture helper inside the same file.
- `forbidden paths`: runtime template resolver, profile templates, docs, `.assurance.json` production logic, canonical Issue docs.
- `concrete test cases`: `tc-s01-001` Lite profile draft-plan contains lightweight completion and does not contain required mid-step commit/full static analysis language (`C-G4-001`); `tc-s01-002` Standard / Strict / Critical draft-plan contains M99 static analysis, lint, tests, report, and commit candidate gate (`C-G4-002`).
- `verification command`: `uv run pytest tests/cli_runtime/test_new.py -k "profile_templates or grade_aware_m99 or lite"`.
- `report evidence destination`: Implementation Delegation Gate, Test Contract Closure rows for `C-G4-001` and `C-G4-002`, Milestone / Commit Candidate Gate for `M1/M2`.
- `amendment trigger`: any fixture requires changing profile template body semantics beyond assertion hardening, or Lite needs new policy interpretation.

### `S02` Draft Routing And Assurance Fail-Closed Smoke

- `delegation contract`: `dev-coder` owns smoke tests against public `new doc` CLI. Use existing helpers from `tests/cli_runtime/test_new.py`.
- `allowed paths`: `tests/cli_runtime/test_new.py`.
- `forbidden paths`: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`, profile templates, canonical docs, generated dogfooding docs.
- `concrete test cases`: `tc-s02-001` `draft-design` and `draft-plan` for Standard / Strict / Critical use `templates/issue-profiles/<authorized_profile>/{design,plan}.md` (`C-G4-003`); `tc-s02-002` missing / invalid / stale `.assurance.json` returns failure and leaves `discussions/` unchanged (`C-G4-004`).
- `verification command`: `uv run pytest tests/cli_runtime/test_new.py -k "authorized_profile_templates or fail_closed_without_valid_assurance_contract"`.
- `report evidence destination`: Test Contract Closure for `C-G4-003` and `C-G4-004`, Closure Coverage, discovered tests if existing G2 tests are reused as covered-existing.
- `amendment trigger`: no-write cannot be asserted without changing CLI output contract, or unsupported profile handling differs from Issue design.

### `S03` Readiness False-Positive Regression Smoke

- `delegation contract`: `dev-coder` owns domain/CLI smoke tests. This step validates R0 behavior and must not implement readiness classifier logic unless a failing smoke exposes a G4-only fixture error; otherwise return to R0/follow-up.
- `allowed paths`: `tests/cli_runtime/test_workflow.py`, `tests/unit/domain/test_workflow_state.py`.
- `forbidden paths`: workflow state implementation, guidance compiler, report evidence parser, canonical docs.
- `concrete test cases`: `tc-s03-001` placeholder or heading-only plan remains blocked even with executable-looking markers (`C-G4-005`); `tc-s03-002` stale source binding remains blocked with `assurance-classification-required` (`C-G4-005`); `tc-s03-003` substantive use of words like template/placeholder remains ready to avoid over-blocking (`C-G4-005`).
- `verification command`: `uv run pytest tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py -k "placeholder or stale or substantive"`.
- `report evidence destination`: TDD Red/Green evidence, Test Contract Closure for `C-G4-005`, Closure Delta if any bug class is split.
- `amendment trigger`: R0 behavior is absent or wrong in production code, because G4 must not absorb R0 logic.

### `S04` Evidence Gate Smoke

- `delegation contract`: `dev-coder` owns report evidence fixture tests; `spec-reviewer` checks that the fixture semantics match G3 and workflow docs.
- `allowed paths`: `tests/unit/domain/test_workflow_state.py`, `tests/cli_runtime/test_workflow.py` only if CLI-level readiness assertion is necessary.
- `forbidden paths`: evidence gate implementation, report template, canonical report, delegated draft files.
- `concrete test cases`: `tc-s04-001` stale EAL entry blocks readiness (`C-G4-006`); `tc-s04-002` stale or non-pass `spec-reviewer` row blocks readiness even if other text says pass (`C-G4-006`); `tc-s04-003` Strict/Critical specialist skipped without unavailable/manual fallback evidence blocks readiness (`C-G4-006`).
- `verification command`: `uv run pytest tests/unit/domain/test_workflow_state.py -k "report_evidence_gate or stale_spec_reviewer or specialist"`.
- `report evidence destination`: Test Contract Closure for `C-G4-006`, Reviewer Gate Status, Evidence Adoption Ledger if delegated evidence is used.
- `amendment trigger`: G3 semantics are ambiguous, especially around Standard skip reason versus Strict/Critical fallback evidence.

### `S90` Provider / Dogfooding Parity Inspection

- `delegation contract`: `dev-coder` for assertion if parity is automated; `repo-analyst` read-only if parity is manual inspection. `spec-reviewer` reviews docs/spec alignment.
- `allowed paths`: `tests/unit/infra/test_init_update.py` for parity assertions; read-only provider paths under `src/spec_dock/assets/spec_dock/...`; read-only dogfooding paths under `spec-dock/...`.
- `forbidden paths`: provider docs/templates and dogfooding mirror edits in G4 unless the finding is explicitly routed back to the owning upstream slice.
- `concrete test cases`: `tc-s90-001` `workflow_issue.md`, `workflow_spec_authoring.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md` provider/dogfooding parity or documented exception (`C-G4-007`); `tc-s90-002` profile issue plan/design templates exist for `lite`, `standard`, `strict`, `critical` on provider and dogfooding surfaces (`C-G4-007`).
- `verification command`: `uv run pytest tests/unit/infra/test_init_update.py -k "workflow_issue_doc_matches_bundled_asset or workflow_spec_authoring or issue_profiles"`.
- `report evidence destination`: Docs Impact Resolution S90, Closure Coverage for `C-G4-007`.
- `amendment trigger`: parity failure requires source edit, because G4 should not silently repair provider/dogfooding drift without doc-writer/spec-reviewer gating.

### `S95` Strict Spec Review Readiness

- `delegation contract`: `spec-reviewer` clean-room review over canonical docs after main orchestrator adopts any plan changes. This draft is not reviewer pass.
- `allowed paths`: read-only canonical Issue/Epic docs, discussion draft path, test evidence.
- `forbidden paths`: canonical edits by delegated reviewer, implementation edits.
- `concrete test cases`: `tc-s95-001` review confirms all required closure ids have step-local contracts and report destinations (`C-G4-008`).
- `verification command`: reviewer invocation evidence selected by main orchestrator; no local command is claimed here.
- `report evidence destination`: Reviewer Gate Status and Final Spec Review Gate.
- `amendment trigger`: reviewer finds missing closure id, missing step-local test case, or G4 scope creep into R0-G3 logic.

### `M99/S99` Issue-Local Handoff Gate

- `delegation contract`: main orchestrator integrates report evidence; `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` run only if canonical plan requires them. This is not PR creation.
- `allowed paths`: `report.md` evidence updates by main orchestrator; final test evidence references.
- `forbidden paths`: PR creation, PR Delivery Gate, Merge Preparation Gate, GitHub issue finish claim, Epic final gate claim.
- `concrete test cases`: `tc-s99-001` report contains executed commands, skipped-check reasons, residual risks, closure coverage, and handoff note to Epic final quality gate (`C-G4-008`).
- `verification command`: `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py tests/unit/infra/test_init_update.py -k "new_doc or workflow or report_evidence_gate or workflow_issue_doc_matches_bundled_asset"` plus `./spec-dock/scripts/spec-dock validate` if required by canonical plan.
- `report evidence destination`: Final Quality Gate, Step Contract Closure, Test Contract Closure, Closure Coverage, Milestone / Commit Candidate Gate.
- `amendment trigger`: any need to create a PR, run merge-prep, or claim Epic final readiness from Issue-local M99.

## 6. Test Strategy Mapping

- `tests/cli_runtime/test_new.py`: profile-aware draft source, no-write fail-closed, Lite/Standard+/M99 profile template smoke.
- `tests/cli_runtime/test_workflow.py`: CLI readiness smoke for placeholder, stale source, report evidence readiness.
- `tests/unit/domain/test_workflow_state.py`: domain-level evidence gate and readiness classifier fixtures.
- `tests/unit/infra/test_init_update.py`: provider/dogfooding docs and template parity assertions.

Prefer public CLI/runtime behavior over private helper assertions. When a current test already covers a closure id, mark it `covered-existing` in report rather than duplicating assertions.

## 7. Review Gates

- Per test-behavior step: `code-reviewer` focuses on test sensitivity, fixture reliability, and absence of production logic in G4.
- Docs/spec alignment step: `spec-reviewer` focuses on AC traceability, G4 scope boundary, and M99 handoff semantics.
- Final quality gate: `qa-reviewer` checks whether the integrated smoke matrix is sufficient across Lite / Standard / Strict / Critical; issue-wide `code-reviewer` checks test integration; final `spec-reviewer` checks requirement/design/plan/report alignment.

Reviewer outputs do not replace report evidence, closure coverage, or Evidence Adoption Ledger adoption.

## 8. Rollback / Compatibility

- G4 changes should be test-only unless S90 exposes a parity assertion placement gap.
- If a new smoke fails because R0-G3 production behavior is missing, do not implement the missing logic in G4. Record the failure and route it to the owning upstream Issue or Epic-level follow-up.
- Existing `draft-requirement`, Initiative/Epic `draft-design` / `draft-plan`, and strict-legacy issue behavior must remain compatible.
- Lite must remain lightweight. Any requirement for mid-step commit or full static analysis in Lite is a regression, not a G4 enhancement.

## 9. Docs Impact

Expected docs impact for this draft: canonical Issue `plan.md` can adopt the closure index and step contracts; canonical `report.md` can adopt the delegated draft evidence and later observed execution results. No provider docs, templates, workflow docs, or implementation files should be changed by this planning draft.

If implementation finds provider/dogfooding docs drift during S90, the main orchestrator should decide whether to route the fix to G1/G2/G3 ownership or create a follow-up. G4 should not silently broaden into docs repair.

## 10. Final Quality Gate

The final gate should require:

- all required closure ids `C-G4-001` through `C-G4-008` closed in report evidence;
- focused pytest commands recorded with pass/fail/skipped reason;
- `spec-dock validate` result or documented reason if not run;
- docs impact decision recorded;
- fresh QA, code, and spec review evidence if canonical plan requires full strict issue closure;
- explicit statement that Issue-local M99 is a handoff to Epic final quality gate and not PR creation.

## 11. Plan Blockers

No blocker was found that prevents the main orchestrator from adopting a stricter plan schema. Remaining risks:

- Some desired G4 smoke may already be covered by G2/G3 tests; duplication should be avoided by marking covered-existing where appropriate.
- Current test names may differ after upstream slices land; canonical plan should describe observable behavior and command target, not overfit to a future exact test name.
- If R0-G3 logic is incomplete, G4 must stop at evidence and routing rather than implement missing upstream behavior.

## 12. Integration Notes for Main Orchestrator

- This draft is proposal evidence only. It should be recorded in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger before any canonical adoption.
- Recommended adoption target: replace or extend `plan.md` sections for milestones, closure index, implementation steps, S90, S95, and M99/S99 handoff.
- Recommended report target: Delegated Draft Evidence row with `created_by_role=implementation-planner`, `adoption_status=unreviewed`, this discussion path, and `diff_guard_result=failed` because post-run status showed an additional untracked Issue discussion file outside this draft.
- Leaf evidence used: none. Only repository docs/tests were inspected directly.
- Forbidden actions avoided: no canonical doc edit, no implementation edit, no test edit, no package/config edit, no GitHub mutation, no phase promotion, no reviewer-pass claim.
- Unresolved design gaps: none for planning adoption; execution may still reveal upstream R0-G3 behavior gaps.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
