---
created_by_role: spec-dock-system-architect
scope_id: iss-00138
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md
  - spec-dock/active/issue/discussions/20260529t012153z-01-research-issue-planning-execution-split-source-grounding.md
  - spec-dock/active/issue/discussions/20260529t012153z-interview-issue-planning-skill-authority-boundary.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/spec_dock/docs/README.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - tests/test_init_update.py
  - tests/cli_runtime/test_wrappers.py
  - tests/cli_runtime/harness.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/plan.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: "Main orchestrator must decide adoption in canonical report.md."
---

## Requirement Coverage

- AC-001 maps to adding provider-side `.agents/skills/spec-dock-issue-planning/SKILL.md` as a concise Issue requirement/design/plan planning leaf skill.
- AC-002 maps to wording in the new planning skill and hub route that keeps canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` under main orchestrator ownership. `system-architect` and `implementation-planner` remain delegated draft evidence producers only.
- AC-003 maps to narrowing `spec-dock-issue-execution` wording around approved/reviewer-pass requirement/design/plan, executable `plan.md`, and a stop condition for unresolved spec gaps.
- AC-004 maps to `spec-driven-tdd-workflow` routing: Issue planning goes to `spec-dock-issue-planning`, Issue execution goes to `spec-dock-issue-execution`, and clarification remains a first-class companion before or during authoring.
- AC-005 maps to provider docs/tests: managed asset lists, bundled skill routing assertions, docs README skill list, wrapper scaffold checks, and dogfooding parity.
- AC-006 maps to preserving `workflow_spec_authoring.md`, `workflow_clarification.md`, delegated draft evidence boundaries, fresh reviewer gates, and `workflow_issue.md` execution completion policy.
- EC-001 is covered by execution stop wording: `$spec-dock-issue-execution` must not implement from template/gapped docs.
- EC-002 is covered by hub sequencing: planning plus execution in one request means planning artifacts and reviewer/handoff gates first, execution second.
- EC-003 is covered by delegated draft boundary text: design/plan drafts are `discussions/` evidence, not canonical authority.
- EC-004 is covered by provider-first implementation plus dogfooding parity verification.

## Existing Context Findings

- Active context is `init-local-00003` / `epic-00112` / `iss-00138`; active issue authority is approved, but active context still warns that synthetic active approval is not lifecycle approval.
- Current `design.md` and `plan.md` are still scaffold templates; the current source requirement revision read for this draft is `git hash-object spec-dock/active/issue/requirement.md = 6e3875096ca267fb7b815ff2b15a35c5b7f7af3a`.
- The scope memo requests an Issue planning skill, a tighter Issue execution skill, hub routing, clarification composition, provider/dogfooding parity, and tests.
- Source-grounding confirms Initiative and Epic planning skills already exist, but Issue currently has only `spec-dock-issue-execution`.
- The answered interview resolves the authority boundary as Option A: keep existing workflow rules, split planning/execution, use `system-architect` for design draft evidence and `implementation-planner` for plan draft evidence, and keep canonical docs main-orchestrator-owned.
- `workflow_spec_authoring.md` already owns requirement/design/plan authoring and fresh `spec-reviewer` phase gates for Initiative, Epic, and Issue.
- `workflow_clarification.md` is a first-class workflow, not an Issue-only subsection, and requires source-grounded read before human questions.
- `workflow_issue.md` currently lists only `.agents/skills/spec-dock-issue-execution/SKILL.md` as the corresponding leaf skill, while also containing spec authoring and execution sections.
- `src/spec_dock/assets/spec_dock/docs/README.md` currently lists Issue only as `.agents/skills/spec-dock-issue-execution/SKILL.md`.
- `tests/cli_runtime/harness.py` and `tests/test_init_update.py` fix expected managed skill names and installed asset mappings; they currently include `spec-dock-issue-execution` but not `spec-dock-issue-planning`.
- `tests/cli_runtime/test_wrappers.py` checks initialized wrapper surfaces and currently reads hub and issue execution skills.

## Design Decisions

- Add `spec-dock-issue-planning` as a concise leaf skill, not a new policy source. Its primary references should be `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, and `phase_plan_issue.md`.
- Model the new skill after Initiative/Epic planning: short, directive, and source-of-truth oriented. It should not duplicate workflow docs.
- State that Issue planning covers creating/improving/review-preparing Issue `requirement.md`, `design.md`, and `plan.md`, including source-grounded clarification and delegated draft evidence where appropriate.
- State that canonical artifact editing and adoption decisions remain with the main orchestrator. The planning skill can be an orchestrator entrypoint, but not a delegated direct-write authority.
- Keep `spec-dock-issue-execution` as execution-only in effect: it starts after approved/reviewer-pass planning artifacts and executable `plan.md`; unresolved spec gaps route back to planning/clarification.
- Update `spec-driven-tdd-workflow` so Issue planning and Issue execution are separate routes. Planning plus execution must be sequenced through authoring gates before execution.
- Update shipped docs so the installed skill list exposes both Issue planning and Issue execution. In `workflow_issue.md`, list both corresponding leaf skills because the file owns both Issue spec authoring linkage and execution policy.
- Implement provider-first under `src/spec_dock/assets/install_root/` and `src/spec_dock/assets/spec_dock/`; treat checked-in `.agents/skills/` and `spec-dock/docs/` as dogfooding parity surfaces, not the source of truth.

## Alternatives Considered

- Keep Issue planning inside `spec-dock-issue-execution`: rejected because it preserves the current asymmetry and keeps authoring and implementation entrypoints conflated.
- Make `spec-dock-issue-planning` a delegated draft author: rejected for this issue because the answered interview keeps existing delegated draft roles and avoids new direct authoring authority.
- Give `spec-dock-issue-planning` canonical direct-write authority: rejected because it collides with the main-orchestrator single-writer model and would expand into Permission Profile / promotion / direct-write design.
- Put Issue planning only in hub text and not in `workflow_issue.md`: rejected for this design because `workflow_issue.md` has a "corresponding leaf skill" section and currently contains Issue spec authoring guidance. Listing both skills reduces entrypoint ambiguity while preserving `workflow_spec_authoring.md` as the phase-gate source of truth.
- Skip dogfooding parity and rely only on init/update output: rejected because this repo has checked-in dogfooding agent-tooling parity tests, and source-grounding identifies dogfooding `.agents/skills` as an observation point.

## Boundary / Contract Model

- `spec-dock-issue-planning` contract:
  - Entry: Issue requirement/design/plan authoring or review-readiness work.
  - Owns: concise route reminders, source document order, planning/execution sequencing guardrails.
  - Does not own: canonical final authority, direct delegated draft writing, reviewer pass, phase promotion, implementation readiness, runtime validation, PR delivery, issue finish.
- `spec-dock-issue-execution` contract:
  - Entry: approved/reviewer-pass Issue requirement/design/plan with an executable `plan.md`.
  - Owns: implementation-step execution reminders, report evidence, gap stop condition, delivery handoff reminders.
  - Does not own: filling incomplete requirement/design/plan by implementation assumption.
- Hub contract:
  - Route "Issue planning" to `spec-dock-issue-planning`.
  - Route "Issue execution" to `spec-dock-issue-execution`.
  - Route ambiguity, source-grounded questions, and one-question interviews to `spec-dock-clarification`.
  - When both planning and execution are requested, express an ordered workflow rather than an automatic gate bypass.
- Canonical artifact contract:
  - Main orchestrator remains single-writer for canonical docs and report ledger adoption.
  - Delegated drafts are proposal evidence until adopted in `report.md` and reflected into canonical docs followed by fresh reviewer gates.

## Dependency Analysis

- Provider install asset dependency:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` must exist before managed asset lists and installation/update tests can pass.
  - `spec-driven-tdd-workflow/SKILL.md` depends on the new skill name for routing text.
  - `spec-dock-issue-execution/SKILL.md` depends on the planning skill only as a boundary reference, not as a runtime import.
- Shipped docs dependency:
  - `src/spec_dock/assets/spec_dock/docs/README.md` must list both Issue planning and Issue execution.
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` should list both corresponding leaf skills and preserve authoring/execution policy separation.
- Test dependency:
  - `_EXPECTED_MANAGED_SKILL_NAMES` in `tests/cli_runtime/harness.py` must include `spec-dock-issue-planning`.
  - Managed asset maps and path inventories in `tests/test_init_update.py` must include `.agents/skills/spec-dock-issue-planning/SKILL.md`.
  - Bundled routing assertions must read and assert the new planning skill and updated hub route text.
  - `tests/cli_runtime/test_wrappers.py` should assert initialized repos include the new skill and that hub/issue planning text avoids legacy `./spec ` aliases.
- Dogfooding parity dependency:
  - Checked-in `.agents/skills/spec-dock-issue-planning/SKILL.md` and modified checked-in skill/docs mirrors must match provider assets after refresh or explicit parity update.

## Source of Record

- Source of record for installable skill assets: `src/spec_dock/assets/install_root/.agents/skills/`.
- Source of record for shipped spec-dock docs: `src/spec_dock/assets/spec_dock/docs/`.
- Source of record for workflow semantics:
  - Authoring phase gates: `workflow_spec_authoring.md`.
  - Clarification: `workflow_clarification.md`.
  - Issue execution and completion policy: `workflow_issue.md`.
  - Issue plan authoring shape: `phase_plan_issue.md` and `docs/authoring/issue-plan.md`.
- Dogfooding workspace:
  - Checked-in `.agents/skills/` and `spec-dock/docs/` are parity/validation surfaces, not primary implementation source.
- Canonical issue adoption:
  - Main orchestrator decides whether this draft is reflected to `design.md`, `plan.md`, and `report.md`.

## Data Flow / Domain Model / Interface Contract

```text
User request / active issue state
|-- Issue planning intent
|   |-- hub routes to spec-dock-issue-planning
|   |-- planning skill routes to workflow_spec_authoring + workflow_clarification
|   |-- optional system-architect / implementation-planner drafts go to discussions/
|   |-- main orchestrator adopts into canonical docs and report ledger
|   `-- fresh spec-reviewer gates produce handoff readiness
`-- Issue execution intent
    |-- hub routes to spec-dock-issue-execution
    |-- execution verifies approved/reviewer-pass docs and executable plan.md
    |-- unresolved gaps route back to planning / clarification
    `-- implementation evidence is recorded in report.md
```

- Domain vocabulary:
  - `Issue planning`: Issue-level requirement/design/plan authoring entrypoint.
  - `Issue execution`: implementation, verification, observed evidence, delivery handoff after planning readiness.
  - `handoff readiness`: reviewer-gated planning artifacts plus report evidence sufficient for execution to start.
- Interface contract:
  - Skills expose Markdown text only; no runtime API or CLI parser contract changes are required.
  - Installation/update contract is file inventory and byte parity through managed asset tests.
  - Docs contract is user/agent routing clarity, not a new permission model.

## File / Module Change Plan

```text
.
|-- src/
|   `-- spec_dock/
|       `-- assets/
|           |-- install_root/
|           |   `-- .agents/
|           |       `-- skills/
|           |           |-- spec-dock-issue-planning/
|           |           |   `-- SKILL.md                 # Add: Issue requirement/design/plan planning entrypoint
|           |           |-- spec-dock-issue-execution/
|           |           |   `-- SKILL.md                 # Modify: sharpen approved-plan execution boundary and gap stop
|           |           `-- spec-driven-tdd-workflow/
|           |               `-- SKILL.md                 # Modify: route Issue planning vs execution separately
|           `-- spec_dock/
|               `-- docs/
|                   |-- README.md                       # Modify: list Issue planning and Issue execution
|                   `-- workflow_issue.md               # Modify: corresponding leaf skills and boundary wording
|-- .agents/
|   `-- skills/                                         # Modify/Add via provider-first parity refresh, not source of truth
|       |-- spec-dock-issue-planning/SKILL.md
|       |-- spec-dock-issue-execution/SKILL.md
|       `-- spec-driven-tdd-workflow/SKILL.md
|-- spec-dock/
|   `-- docs/                                           # Modify via provider-first parity refresh/inspection
|       |-- README.md
|       `-- workflow_issue.md
`-- tests/
    |-- cli_runtime/
    |   |-- harness.py                                  # Modify: expected managed skill names
    |   `-- test_wrappers.py                           # Modify: initialized wrapper skill presence/text checks
    `-- test_init_update.py                            # Modify: managed map, inventories, docs/readme/routing assertions
```

## Migration / Compatibility / Rollback

- Migration impact is install/update asset migration only; existing repos receive the new managed skill on update.
- Existing `spec-dock-issue-execution` path remains, so current Issue execution entrypoints are not removed.
- Existing custom unmanaged skills should remain preserved by the managed asset boundary; tests should keep custom skill preservation assertions intact.
- Rollback path is removing `spec-dock-issue-planning` from provider managed skill lists/docs/hub/tests and restoring prior `workflow_issue.md` / README wording. Because no runtime command behavior changes are required, rollback risk is low.
- Compatibility risk is mainly stale dogfooding parity: if provider assets are updated without checked-in parity surfaces, parity tests should fail.

## Observability

- Primary observability is static and test-based:
  - managed asset inventory includes `spec-dock-issue-planning`;
  - init/update output contains the new skill;
  - docs README and hub skill text expose the split;
  - `workflow_issue.md` still preserves existing execution gates and stop conditions;
  - checked-in dogfooding parity matches provider assets.
- Report observability:
  - `report.md` should record this delegated draft in Delegated Draft Evidence with `adoption_status: unreviewed` until the orchestrator integrates it.
  - If adopted, Evidence Adoption Ledger should state which design sections were used and whether any portions were rejected.
- Runtime observability:
  - No new runtime telemetry is needed. `spec-dock validate`, focused unittest targets, and diff inspection are sufficient.

## Test Strategy

- Add or update structural tests:
  - `tests/cli_runtime/harness.py`: include `spec-dock-issue-planning` in `_EXPECTED_MANAGED_SKILL_NAMES`.
  - `tests/test_init_update.py`: include provider and target managed asset mapping for `.agents/skills/spec-dock-issue-planning/SKILL.md`.
  - `tests/test_init_update.py`: assert docs README includes `spec-dock-issue-planning` and still includes `spec-dock-issue-execution`.
  - `tests/test_init_update.py`: assert bundled hub routing text contains Issue planning and Issue execution as distinct routes and planning plus execution gate sequencing language.
  - `tests/test_init_update.py`: assert new planning skill references `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, and `phase_plan_issue.md`, and does not claim delegated/canonical authority.
  - `tests/cli_runtime/test_wrappers.py`: assert initialized repos include the new skill and that checked skill text avoids `./spec ` aliases.
- Verification commands for implementation phase:
  - focused: `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract`
  - focused: `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs`
  - parity-relevant: `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
  - broader if touched assertions are dispersed: `python -m unittest discover -v`
  - dogfooding: `./spec-dock/scripts/spec-dock validate`

## ADR Candidates

- No ADR is recommended for the current requirement. The decision is a local skill routing split that preserves existing workflow semantics.
- Create an ADR only if implementation discovers a durable cross-issue policy change, such as granting Issue planning direct canonical authoring authority or changing delegated authoring permission boundaries. Those are currently out of scope.

## Risks

- Hub wording could imply planning plus execution bypasses reviewer gates. Mitigation: explicitly state sequencing and handoff readiness.
- New planning skill could be read as a replacement for `system-architect` or `implementation-planner`. Mitigation: state it is an orchestrator entrypoint and route design/plan drafts to existing delegated authoring roles.
- Updating only provider assets could leave checked-in dogfooding `.agents/skills` stale. Mitigation: run parity update/inspection and parity tests.
- Over-editing `workflow_issue.md` could accidentally redesign completion policy. Mitigation: limit docs change to corresponding leaf skills and authoring/execution boundary references.
- Tests may have multiple hard-coded skill inventories. Mitigation: search for `spec-dock-issue-execution`, `_EXPECTED_MANAGED_SKILL_NAMES`, and `.agents/skills/` expectations before implementation.

## Requirement Clarification Requests

Requirement Clarification Requests: none.

The requirement and answered interview are sufficient for design. Previously open Q-001 is resolved by listing both Issue planning and Issue execution where `workflow_issue.md` names corresponding leaf skills, while keeping `workflow_spec_authoring.md` as the authoring phase-gate source of truth. Previously open Q-002 is resolved by provider-first implementation plus dogfooding parity verification.

## Integration Notes for Main Orchestrator

- Suggested canonical `design.md` integration:
  - Replace scaffold sections with the boundary/contract model, dependency analysis, source of record, data flow, file/module change plan, migration/rollback, observability, test strategy, and risks above.
  - Keep this as an Issue-local design; do not promote an ADR unless implementation finds a durable policy change.
- Suggested `report.md` Delegated Draft Evidence entry:
  - role: `spec-dock-system-architect`
  - phase: requirement/design
  - scope: `iss-00138`
  - source artifacts read: see frontmatter `source_paths`
  - draft artifact path: `spec-dock/active/issue/discussions/20260529t015038z-disc-issue-planning-execution-split-design-analysis.md`
  - draft status: `produced`
  - authority: `proposed`
  - adoption_status: `unreviewed`
  - reflected_to: `[]`
  - intended_targets: `spec-dock/active/issue/design.md`, `spec-dock/active/issue/report.md`, `spec-dock/active/issue/plan.md`
  - diff_guard_result: `pending`
  - integration notes: use as design input for provider-side Issue planning skill addition, execution boundary clarification, hub/docs/tests updates, and provider-first dogfooding parity.
  - rejected portions: none proposed
  - blockers: none
  - canonical artifacts edited: `none`
  - final authority claimed: `no`
- Leaf evidence used: none; this draft used repository/source-document reading only.
- Forbidden actions avoided: no canonical docs, implementation files, tests, package/config, existing discussions, GitHub state, git add/commit/push, phase promotion, reviewer-pass claim, or user dialogue.
- No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
