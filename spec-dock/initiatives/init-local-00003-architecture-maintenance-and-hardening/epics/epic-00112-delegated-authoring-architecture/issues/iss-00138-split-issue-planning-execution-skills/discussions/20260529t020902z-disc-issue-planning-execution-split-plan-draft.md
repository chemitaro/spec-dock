---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00138
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/README.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - tests/test_init_update.py
  - tests/cli_runtime/harness.py
  - tests/cli_runtime/test_wrappers.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

## Plan Summary

This advisory draft proposes an issue plan for `iss-00138` that turns the accepted requirement and corrected design into provider-first, behavior-sliced implementation steps. The plan should keep the implementation scope narrow: add `spec-dock-issue-planning`, clarify `spec-dock-issue-execution`, update hub routing and shipped docs, update tests that detect the new split, refresh or verify dogfooding parity, then run final quality gates.

Requirement phase passed `spec-reviewer` per `report.md`. Design phase also passed a fresh `spec-reviewer` after corrections; the report records that prior P1/P2 design findings were corrected, including the `authoring/issue-plan.md` field-level plan contract and dogfooding parity wording.

The canonical `plan.md` should remain main-orchestrator-authored. This draft is planning evidence only and does not claim adoption, readiness, reviewer pass, phase completion, or authority.

## Requirement / Design Traceability

- AC-001 maps to S01: add provider-side `.agents/skills/spec-dock-issue-planning/SKILL.md` as an Issue requirement/design/plan planning leaf skill.
- AC-002 maps to S01 and S02: preserve main orchestrator ownership, delegated draft boundaries, and reviewer gate language in the new planning skill and hub route.
- AC-003 maps to S03: revise `spec-dock-issue-execution` wording so execution requires approved/reviewer-pass planning artifacts and stops on unresolved spec gaps.
- AC-004 maps to S02: update `spec-driven-tdd-workflow` routing so Issue planning and Issue execution are distinct, and planning + execution sequencing cannot bypass gates.
- AC-005 maps to S04 and S05: update managed asset inventory, docs assertions, wrapper checks, and dogfooding parity detection.
- AC-006 maps to S01 through S99: keep `workflow_spec_authoring.md`, `workflow_issue.md`, delegated draft rules, and fresh reviewer gates intact.
- EC-001 maps to S03: `$spec-dock-issue-execution` alone with incomplete specs returns to planning/clarification instead of implementation.
- EC-002 maps to S02: simultaneous planning + execution requests route through planning gates before execution handoff.
- EC-003 maps to S01/S02: `system-architect` and `implementation-planner` remain delegated draft evidence producers, not substitutes for planning skill or reviewer pass.
- EC-004 maps to S05: provider-only skill addition without dogfooding/update parity is detected by tests or explicit parity verification.

Design traceability:
- The design's dependency analysis sets the implementation order as skill addition -> routing/docs update -> tests update -> dogfooding parity -> validation.
- The design's directory/file change plan scopes expected changes to provider install-root skills, provider docs, dogfooding parity outputs, and tests.
- The design explicitly excludes runtime domain model changes, Permission Profile work, `.github/agents` / Copilot support, and direct delegated canonical writes.

## Milestones

- M1 Skill surface fixed: new Issue planning skill exists and execution boundary is sharpened without granting new authority.
- M2 Routing and shipped docs aligned: hub skill, provider README, and provider `workflow_issue.md` present Issue planning and Issue execution as separate routes.
- M3 Regression coverage updated: init/update, managed asset inventory, bundled routing, wrapper, and harness expectations detect the new skill and split.
- M4 Dogfooding parity resolved: provider assets and checked-in dogfooding surfaces are refreshed or explicitly inspected, with drift evidence recorded.
- M5 Closure and quality gates complete: focused tests, `validate`, `sync`, per-step reviewer gates, S90 docs impact, and S99 final QA/code/spec review are represented in `report.md`.

## Dependency-Derived Execution Order

1. Add the provider-side `spec-dock-issue-planning` skill first because hub/docs/tests can only reference a managed skill after the source asset exists.
2. Update hub routing and execution boundary wording second because these texts define how users and agents choose planning vs execution.
3. Update provider docs after the skill/routing surface is stable, keeping policy ownership in `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md`.
4. Update tests after expected text and file inventory are fixed, so assertions encode the final contract instead of intermediate wording.
5. Refresh or verify dogfooding mirrors after provider-side source changes; dogfooding files are validation/parity surfaces, not the primary source of truth.
6. Run focused tests and spec-dock checks, then final review gates.

No runtime command, dependency graph, sync behavior, or domain model step is required unless tests reveal an existing managed-asset installer gap.

## Issue / Step Slicing

Suggested canonical step order:

- S01 Add Issue planning leaf skill.
  - Behavior goal: installed assets expose `spec-dock-issue-planning` as an Issue requirement/design/plan planning entrypoint.
  - Primary worker: `doc-writer`.
  - Target files: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`.
  - Close condition: skill text references `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md`; states main orchestrator canonical ownership; states delegated drafts are evidence only.
  - Reviewer focus: `spec-reviewer` docs/spec alignment.

- S02 Split hub routing for Issue planning and Issue execution.
  - Behavior goal: `spec-driven-tdd-workflow` routes Issue planning to `spec-dock-issue-planning`, execution to `spec-dock-issue-execution`, and planning + execution requests preserve gate sequencing.
  - Primary worker: `doc-writer`.
  - Target files: `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`.
  - Close condition: hub text lists both Issue planning and Issue execution, keeps clarification as a first-class companion, and does not include detailed runtime/deps commands outside execution references.
  - Reviewer focus: `spec-reviewer` docs/spec alignment.

- S03 Narrow Issue execution boundary.
  - Behavior goal: execution skill clearly requires approved/reviewer-pass requirement/design/plan plus executable `plan.md`, and sends unresolved gaps to planning/clarification.
  - Primary worker: `doc-writer`.
  - Target files: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`.
  - Close condition: execution no longer appears to own requirement/design/plan authoring; runtime command reminders remain in execution skill only.
  - Reviewer focus: `spec-reviewer` docs/spec alignment.

- S04 Update shipped docs for the split.
  - Behavior goal: provider docs list the new planning skill and describe `workflow_issue.md` corresponding leaf skills as planning + execution without changing completion policy.
  - Primary worker: `doc-writer`.
  - Target files: `src/spec_dock/assets/spec_dock/docs/README.md`, `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`.
  - Close condition: docs point planning to spec authoring/clarification and execution to Issue workflow execution gates; no broad rewrite of PR delivery or issue finish policy.
  - Reviewer focus: `spec-reviewer` docs/spec alignment.

- S05 Update regression tests and managed asset expectations.
  - Behavior goal: tests fail if `spec-dock-issue-planning` is missing from managed assets, installed output, hub routing, docs list, or dogfooding parity expectations.
  - Primary worker: `dev-coder` if modifying tests; `doc-writer` can provide expected wording but should not own code/test edits.
  - Target files: `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`, `tests/test_init_update.py`.
  - Close condition: `_EXPECTED_MANAGED_SKILL_NAMES`, managed maps, duplicate-boundary expectations, bundled routing assertions, docs README assertions, workflow issue assertions, and wrapper-installed skill checks all account for the new skill.
  - Reviewer focus: `code-reviewer` for tests and installer/scaffold behavior; `spec-reviewer` for wording assertions if test text materially encodes workflow policy.

- S06 Refresh and verify dogfooding parity.
  - Behavior goal: checked-in dogfooding `.agents/skills` and `spec-dock/docs` match provider assets or any intentional non-refresh is explicitly recorded as non-blocking.
  - Primary worker: `doc-writer` for parity file refresh; orchestrator records evidence.
  - Target files: dogfooding mirrors only if provider refresh is intentionally applied, likely `.agents/skills/spec-dock-issue-planning/SKILL.md`, `.agents/skills/spec-dock-issue-execution/SKILL.md`, `.agents/skills/spec-driven-tdd-workflow/SKILL.md`, `spec-dock/docs/README.md`, `spec-dock/docs/workflow_issue.md`.
  - Close condition: dogfooding parity is confirmed by existing mirror tests, explicit diff inspection, or `spec-dock update .` evidence if the orchestrator chooses that route.
  - Reviewer focus: `code-reviewer` if scaffold/update behavior changes; otherwise `spec-reviewer` docs/spec alignment.

- S90 Docs impact resolution.
  - Behavior goal: confirm all docs/templates/README/workflow/skill/migration-note impacts are resolved.
  - Close condition: `report.md` records updated docs and `spec-reviewer` docs/spec alignment result, or records why no further docs are required.

- S99 Final quality gate.
  - Behavior goal: issue-wide closure evidence is complete.
  - Close condition: focused tests, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync` or justified `--no-github` alternative, final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` gates are recorded for main-orchestrator decision.

## Test Strategy Mapping

- `tc-001` / AC-001: managed skill existence.
  - Candidate checks: `_EXPECTED_MANAGED_SKILL_NAMES`, managed install plan expectations, initialized target contains `.agents/skills/spec-dock-issue-planning/SKILL.md`.
  - Suggested focused tests: `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`, plus the existing init/update test that asserts docs and installed managed assets.

- `tc-002` / AC-002 and EC-003: authority boundary in planning skill.
  - Candidate checks: text assertions for main orchestrator ownership, delegated draft evidence boundary, no reviewer-pass/phase-promotion/implementation-readiness claim, and references to `system-architect` / `implementation-planner` as draft producers only.

- `tc-003` / AC-003 and EC-001: execution stop condition.
  - Candidate checks: bundled issue-execution skill text includes approved planning prerequisite and unresolved gap return to `workflow_clarification.md` / authoring phase.

- `tc-004` / AC-004 and EC-002: hub routing and sequencing.
  - Candidate checks: `spec-driven-tdd-workflow` includes `spec-dock-issue-planning`, keeps `spec-dock-issue-execution`, and states planning + execution sequencing cannot bypass gates.

- `tc-005` / AC-005 and EC-004: shipped docs and parity detection.
  - Candidate checks: provider docs README skill list, provider `workflow_issue.md` corresponding leaf skills, test wrapper installed output, `_DOGFOODING_MIRROR_PROVIDER_ASSET_MAP`, `_ISSUE_68_AUTHORITATIVE_RELATIVE_PATHS`, `_ISSUE_68_CLASSIFICATION_PREFIX_TO_RELATIVE_PATHS`, duplicate-boundary allowed paths.

- `tc-006` / AC-006: workflow semantics preserved.
  - Candidate checks: no new Permission Profile/direct canonical authoring/full automation language; `workflow_spec_authoring.md` gate semantics remain referenced; final `spec-reviewer` review covers requirement/design/plan/report/docs alignment.

Focused command candidates for canonical plan:
- `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`
- `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs`
- Add the narrowest existing init/update docs/asset test name once the orchestrator selects the exact assertion home.
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync` after final docs and parity updates, or `sync --no-github` only if the orchestrator records why GitHub live state is intentionally skipped.

## Review Gates

- Entry gate: requirement `spec-reviewer` pass and corrected design fresh `spec-reviewer` pass are recorded in `report.md`; no current design-blocking question is recorded.
- Per-step gate: docs-only/skill-text-only steps use `spec-reviewer` docs/spec alignment; test/scaffold behavior steps use `code-reviewer`; mixed steps should be split or explicitly require both review focuses.
- Delegation gate: implementation steps that edit shipped skills/docs/tests should use the `workflow_issue.md` Implementation Delegation Gate, with `doc-writer` for shipped docs/skills and `dev-coder` for tests/scaffold behavior.
- Report gate: each step should record Step Contract Closure, Test Contract Closure where applicable, Closure Coverage, Closure Delta, Reviewer Gate Status, and Step Commit Gate or justified approved-no-op.
- Final gates: S99 must include `qa-reviewer` test sufficiency, issue-wide `code-reviewer`, and final `spec-reviewer` requirement/design/plan/report/docs alignment.

## Rollback / Compatibility

- Rollback should be file-asset rollback: remove the new planning skill asset, revert hub/docs references, revert test expectations, and revert dogfooding parity outputs.
- Existing `spec-dock-issue-execution` remains installed, so current execution-only entrypoints stay backward-compatible.
- `spec-dock-issue-planning` should not introduce a runtime command, dependency metadata migration, Permission Profile change, `.github/agents` support, or direct canonical write authority.
- If dogfooding parity refresh creates broad generated churn, the orchestrator should stop and decide whether to narrow to explicit mirror files or record manual parity evidence; do not hide generated drift.

## Docs Impact

Docs impact is expected and should not be marked `none`.

Expected docs/skill surfaces:
- Provider skill list: `src/spec_dock/assets/spec_dock/docs/README.md`.
- Issue workflow corresponding leaf skills and authoring/execution boundary: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`.
- Hub route: `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`.
- New planning skill and revised execution skill in `src/spec_dock/assets/install_root/.agents/skills/`.
- Dogfooding mirrors only as parity outputs, not implementation source of truth.

`workflow_spec_authoring.md`, `workflow_clarification.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md` appear sufficient as source-of-truth references; the design does not require changing them unless review finds wording drift after implementation.

## Final Quality Gate

The canonical `plan.md` should require these before issue completion:

- All behavior-slice closure rows are closed in `report.md`.
- All required tests/inspection checks pass or have approved no-op evidence.
- `./spec-dock/scripts/spec-dock validate` passes.
- `./spec-dock/scripts/spec-dock sync` passes with GitHub default, or a recorded `--no-github` rationale if live GitHub is intentionally unavailable for this run.
- Dogfooding parity is verified against provider assets or explicitly resolved with evidence.
- S90 docs impact is resolved with `spec-reviewer` docs/spec alignment.
- S99 final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass.
- PR delivery and merge-preparation evidence are handled by the main orchestrator after final commit gates, before any `issue finish` claim.

## Plan Blockers

none

## Integration Notes for Main Orchestrator

Suggested adoption path:
- Treat this file as `adoption_status: unreviewed` delegated plan evidence.
- Run the post-run diff guard before considering adoption. The target discussion directory had pre-existing untracked discussion files at baseline, so adoption eligibility may need the same baseline hygiene handling described in `report.md` for the prior design draft.
- If adopted, record a new Evidence Adoption Ledger row in `report.md`, then manually author canonical `plan.md` from the accepted portions.
- Keep canonical `plan.md` focused on executable step schema from `docs/authoring/issue-plan.md`, including `Spec-Locked Closure Index`, step-local `具体テストケース一覧`, delegation contracts, closure IDs, review gates, S90, S99, and final exit contract.
- Do not copy any statement from this draft as a reviewer verdict, phase promotion, implementation readiness, or final authority claim.

Delegated draft evidence block for report synthesis:
- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00138`
- source artifacts read: see frontmatter `source_paths`
- draft artifact path: `spec-dock/active/issue/discussions/20260529t020902z-disc-issue-planning-execution-split-plan-draft.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets: `spec-dock/active/issue/plan.md`, `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: provider-first skill/docs/test/parity plan slices proposed; main orchestrator must decide adoption and write canonical plan
- rejected portions: none proposed
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
