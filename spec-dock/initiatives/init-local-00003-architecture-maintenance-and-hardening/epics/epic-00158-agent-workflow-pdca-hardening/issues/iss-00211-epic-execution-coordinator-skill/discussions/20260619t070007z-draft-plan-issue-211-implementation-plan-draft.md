---
created_by_role: implementation-planner
scope_id: iss-00211
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_epic.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
  - src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md
  - tests/cli_runtime/harness.py
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
source_snapshot:
  git_head: 519c1452befbc64e41d737385590e09760a9751f
  observed_at: 2026-06-19T07:00:07Z
leaf_evidence_used: none
---

# iss-00211 Epic Execution Coordinator Skill - delegated implementation plan draft

This is proposal-only planning evidence for main-orchestrator integration into canonical `plan.md`. It does not edit or replace canonical docs, does not claim reviewer pass, and does not claim implementation readiness.

## 1. Plan Summary

Implement `spec-dock-epic-execution` as a first-read Epic execution coordinator skill and connect it to the smallest required discovery and workflow surfaces.

The implementation should be split into three executable slices:

- S01: lock managed skill availability with tests/inventories, then add the provider skill and dogfooding mirror.
- S02: connect Epic execution discoverability by updating `workflow_epic.md`, `spec-dock-hub`, and `/execute-epic` provider/mirror pairs.
- S03: run targeted integration verification and close any bounded parity/content regression found in the planned file set.
- S90: resolve docs impact.
- S99: run final quality gates.

Normal mutation should be delegated. Use `doc-writer` for shipped docs, skills, prompts, and workflow text. Use `dev-coder` for tests, inventories, and runtime/scaffold regression assertions. If a step mixes shipped text and tests because the vertical slice would otherwise stay red, record both delegated worker contracts and require both reviewer focuses.

## 2. Requirement / Design Traceability

### Requirements Covered

- AC-001 New skill availability
- AC-002 Coordinator responsibility boundary
- AC-003 Epic workflow reference
- AC-004 Discoverability and routing
- AC-005 Installer / update regression coverage
- EC-001 Active Issue already exists
- EC-002 No ready Issue
- EC-003 Multiple ready Issues
- EC-004 Small Epic / no-op Epic
- EC-005 PR preparation blocked
- Non-negotiable constraints:
  - provider-side installed assets remain source of truth
  - dogfooding mirrors match provider-side changes
  - no new runtime CLI command
  - no dependency algorithm or GitHub state mutation code path
  - no PR merge automation or merge-ready self-claim

### Design Evidence Used

- `design.md` fixes Option B: new skill plus short `workflow_epic.md` reference.
- `design.md` identifies `/execute-epic` as a direct discovery conflict because it currently says not to create a new skill.
- `design.md` file plan names provider/mirror pairs for:
  - `spec-dock-epic-execution/SKILL.md`
  - `spec-dock-hub/SKILL.md`
  - `.codex/prompts/execute-epic.md`
  - `workflow_epic.md`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
- `workflow_issue.md` requires one step at a time, per-step delegation, per-step reviewer gate, per-step commit/no-op gate, S90, and S99.
- `authoring/issue-plan.md` requires delegation contracts, concrete test case cards, closure contracts, and report evidence destinations.

## 3. Milestones

- M1 Availability locked:
  - new managed skill is present in provider source and dogfooding mirror
  - managed asset inventories and install/update tests know the new skill
- M2 Coordinator contract locked:
  - new skill states bootstrap checks, ready Issue selection, one-Issue-at-a-time execution, existing active Issue stop, no-ready blocked state, no-op Epic path, and PR-preparer handoff boundary
- M3 Discovery connected:
  - `workflow_epic.md` explains the planning handoff -> Epic execution coordinator relation
  - `spec-dock-hub` routes Epic execution to the new skill
  - `/execute-epic` no longer contradicts Issue 211 and routes to the new skill
- M4 Regression evidence collected:
  - managed skill install/list/parity tests and content regression checks pass
- M5 Final gates:
  - docs impact resolved
  - final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` gates pass in canonical execution

## 4. Dependency-Derived Execution Order

1. Update tests/inventories and add the provider skill/mirror in one vertical slice.
   - Reason: adding only the skill can break authoritative inventory/parity tests; adding only tests can leave the suite red without the intended asset.
2. Update route and workflow text after the new skill file exists.
   - Reason: `workflow_epic.md`, `spec-dock-hub`, and `/execute-epic` should route to a real managed skill path.
3. Run integration-level targeted checks.
   - Reason: provider assets, dogfooding mirrors, and install/update parity are coupled across tests.
4. Resolve docs impact and final gates.
   - Reason: S90 and S99 must not substitute for per-step review/commit, but they are required before issue completion.

## 5. Issue / Step Slicing

### Step List

- S01 Managed skill availability and coordinator contract
  - Depends on: reviewer-passed requirement/design evidence recorded by main orchestrator
  - Unblocks: S02 route references
  - Target files:
    - `tests/cli_runtime/harness.py`
    - `tests/unit/infra/test_init_update.py`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
    - `.agents/skills/spec-dock-epic-execution/SKILL.md`
  - Primary roles: `dev-coder` for test/inventory updates; `doc-writer` for skill prose
  - Review focus: `code-reviewer` for tests/scaffold behavior; `spec-reviewer` for skill boundary text

- S02 Epic workflow and discovery route connection
  - Depends on: S01 Step Result Approval
  - Unblocks: S03 integration verification
  - Target files:
    - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
    - `spec-dock/docs/workflow_epic.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
    - `.agents/skills/spec-dock-hub/SKILL.md`
    - `src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md`
    - `.codex/prompts/execute-epic.md`
    - targeted content assertions in `tests/unit/infra/test_init_update.py` if not already covered in S01
  - Primary roles: `doc-writer`; `dev-coder` only for content regression assertions
  - Review focus: `spec-reviewer` plus `code-reviewer` if tests change

- S03 Targeted integration verification and bounded repair
  - Depends on: S02 Step Result Approval
  - Unblocks: S90 and S99
  - Target files:
    - no planned file mutation
    - if verification fails because S01/S02 missed a planned file-set update, bounded repair may touch only S01/S02 target files
  - Primary role: `dev-coder` only if a test repair is required; otherwise parent records verification evidence
  - Review focus: `code-reviewer` only if a repair diff exists; otherwise approved-no-op evidence

- S90 Docs impact resolution
  - Depends on: S03 closure
  - Target files:
    - docs/skills/prompts already touched by S01/S02, or none
    - only update `workflow_issue.md`, `workflow_spec_authoring.md`, `decision-routing.md`, or `reference_github.md` if S90 inspection finds a direct contradiction with the accepted design
  - Primary role: `doc-writer` when updates are required
  - Review focus: `spec-reviewer`

- S99 Final quality gate
  - Depends on: S90 closure
  - Target files:
    - no planned implementation mutation except bounded fixes required by final reviewers
  - Required reviewers: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`

## 6. Test Strategy Mapping

### Spec-Locked Closure Index

| ID | Step | Slice | Type | Spec Link | Locked Expectation | Observable Input / State | Bug Class Guarded | Required | Evidence Level | Closure Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | Managed skill availability | acceptance | AC-001, AC-005 | `spec-dock-epic-execution` is installed as a managed skill and included in expected skill lists/inventories. | provider install_root tree, initialized/updated target repo, `tests/cli_runtime/harness.py` expected names | missing managed asset, installer omission | yes | red-required | `Test Contract Closure` with failing-first or characterization evidence and green pytest result |
| tc-002 | S01 | Provider/dogfooding skill parity | acceptance | AC-001, constraints | provider skill and `.agents/` mirror exist and provide the same coordinator contract. | two `SKILL.md` files and host-pack parity tests | provider/mirror drift | yes | red-required | parity assertion or byte/content comparison evidence |
| tc-003 | S01 | Coordinator boundary | acceptance/negative | AC-002, EC-001..EC-005 | skill delegates planning, issue execution, PR preparation, and finish policy instead of absorbing or self-claiming them. | skill prose inspection/content assertions | role absorption, merge-ready self-claim, active Issue bypass | yes | inspect-only or red-required content assertion | step review plus targeted content test if added |
| tc-004 | S02 | Epic workflow reference | acceptance | AC-003 | `workflow_epic.md` connects planning handoff to Epic execution lifecycle, completion gate, and PR-preparer handoff. | provider and dogfooding `workflow_epic.md` | orphaned planning handoff, docs drift | yes | inspect-only plus parity test | docs inspection and provider/mirror parity evidence |
| tc-005 | S02 | Discovery routing | acceptance/negative | AC-004 | hub and `/execute-epic` route Epic execution to `spec-dock-epic-execution`; `/execute-epic` no longer says not to create a new skill for this workflow. | provider/mirror hub and prompt text | future agent ignores new coordinator, direct contradiction remains | yes | red-required content assertion or inspect-only | content regression evidence and spec review |
| tc-006 | S03 | Targeted regression lane | regression | AC-001..AC-005 | relevant CLI runtime and installer/update tests pass after all planned changes. | pytest commands and `git diff --check` | inventory, package-data, or prompt regressions | yes | covered-existing | command results recorded in report |
| tc-007 | S90 | Docs impact boundary | invariant | constraints, AC-003, AC-004 | docs updates are limited to accepted design surfaces unless a direct contradiction is found. | `git diff --name-status`, `rg` for route/conflict terms | broad docs cleanup or unplanned workflow drift | yes | inspect-only | S90 report evidence and spec review |
| tc-008 | S99 | Final quality gate | final gate | all AC/EC | qa/code/spec final reviewers pass and report ledgers close all required closure IDs. | final diff, tests, report ledgers, reviewer outputs | incomplete issue closure | yes | manual-required | final gate ledger evidence |

### Requirement -> Step Mapping

- AC-001 -> S01, S03, S99
- AC-002 -> S01, S03, S99
- AC-003 -> S02, S90, S99
- AC-004 -> S02, S03, S99
- AC-005 -> S01, S03, S99
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- EC-004 -> S01, S02
- EC-005 -> S01, S02
- Non-negotiable constraints -> S01, S02, S90, S99

## 7. Review Gates

- Each implementation step must close in this order:
  - closure contract check
  - implementation delegation decision
  - bounded implementation batch
  - verification
  - refactor/tidy guardrail
  - report draft update
  - step reviewer gate
  - bounded fix and re-review until pass
  - step commit or approved-no-op gate
  - post-commit clean check
- Step reviewer mapping:
  - tests/scaffold/installer behavior -> `code-reviewer`
  - shipped docs/skills/prompts/workflow text -> `spec-reviewer`
  - mixed vertical slice -> both reviewer focuses are required unless the main orchestrator splits the step before implementation
- Delegated worker output is not reviewer evidence.
- `waived`, `provisional`, `unavailable`, or `denied` reviewer results do not satisfy required gates.

## 8. Rollback / Compatibility

- Rollback path:
  - remove `spec-dock-epic-execution` provider and mirror skill files
  - remove expected skill/inventory/test additions
  - revert `workflow_epic.md`, hub, and `/execute-epic` route references
  - rerun managed asset and dogfooding parity tests to ensure no stale managed file remains
- Compatibility:
  - no runtime CLI command is added
  - no dependency algorithm is changed
  - existing consumer repos receive the managed skill and prompt/docs updates through `spec-dock update`
  - existing Epic planning remains routed to `spec-dock-epic-planning`
  - existing Issue execution remains routed to `spec-dock-issue-execution`
  - PR creation/observation/merge-prepared evidence remains owned by `github-pr-merge-preparer`

## 9. Docs Impact

Known docs impact:

- Required:
  - provider and dogfooding `workflow_epic.md`
  - provider and dogfooding `spec-dock-hub/SKILL.md`
  - provider and dogfooding `.codex/prompts/execute-epic.md`
  - new provider and dogfooding `spec-dock-epic-execution/SKILL.md`
- Conditional only if direct contradiction is found:
  - `workflow_issue.md`
  - `workflow_spec_authoring.md`
  - `authoring/decision-routing.md`
  - `reference_github.md`

S90 must explicitly record whether conditional docs were inspected and why they were updated or left unchanged.

## 10. Final Quality Gate

S99 must require:

- `qa-reviewer`:
  - verifies obligation coverage for AC/EC and checks whether integration tests are sufficient
  - requests additional tests if high-value coverage is missing
- issue-wide `code-reviewer`:
  - reviews integrated diff across provider assets, mirrors, tests, and scaffold behavior
  - checks no runtime CLI/dependency/GitHub mutation path was added
- final `spec-reviewer`:
  - checks requirement/design/plan/report alignment
  - checks docs/skill/prompt wording does not claim reviewer pass, issue finish, PR merge, or merge-ready authority
- final validation:
  - targeted pytest commands pass or blocked reason is recorded
  - `git diff --check` passes
  - `git status --short` evidence is recorded after final commit in external delivery evidence

## 11. Plan Blockers

None found in the source docs reviewed.

Non-blocking adoption cautions:

- This draft updates an existing pre-created discussion file because the user explicitly allowed exactly this path. Main orchestrator should record that this is a task-local exception to the static adapter's normal "new doc" creation path before adopting it.
- Current `git status --short` already shows canonical requirement/design/report changes and prior discussion artifacts. Main orchestrator must run a post-run diff guard and separate pre-existing dirtiness from this draft.
- The final canonical plan should not claim implementation readiness until it receives its own fresh `spec-reviewer` pass.

## 12. Integration Notes for Main Orchestrator

- Changed discussion artifact path:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00211-epic-execution-coordinator-skill/discussions/20260619t070007z-draft-plan-issue-211-implementation-plan-draft.md`
- Source requirement/design revisions:
  - observed from active symlink docs at git `HEAD` 519c1452befbc64e41d737385590e09760a9751f with pre-existing working-tree changes
  - `requirement.md` and `design.md` both identify `iss-00211` and `2026-06-19`
- Lightweight provenance summary:
  - role: `implementation-planner`
  - scope: `iss-00211`
  - source docs: active requirement/design/report, issue plan workflow docs, design-named files
  - intended targets: canonical `plan.md` and `report.md`
  - adoption status: `unreviewed`
  - diff guard: `pending`
- Leaf evidence used:
  - none
- Forbidden actions avoided:
  - no canonical requirement/design/plan/report edit
  - no implementation/test/provider asset edit
  - no GitHub state mutation
  - no `git add`, commit, or push
  - no reviewer pass, phase promotion, final authority, or implementation readiness claim
- Unresolved design gaps:
  - none
- Recommended adoption notes:
  - integrate the closure index, S01/S02/S03/S90/S99 structure, and step-local concrete test cards into canonical `plan.md`
  - record this draft in `report.md` Delegated Draft Evidence and Evidence Adoption Ledger only after post-run diff guard
  - run a fresh `spec-reviewer` on the canonical plan after integration

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.

## Executable Step Draft Details

### S01 - Managed skill availability and coordinator contract

- Behavior goal:
  - A future install/update target exposes `spec-dock-epic-execution` as a managed first-read skill, and the skill text defines the coordinator boundary required by AC-002 and EC-001..EC-005.
- Design references:
  - `design.md` dependency analysis
  - `design.md` file change plan
  - Module Dependency Diagram nodes: new provider skill, managed asset tests, dogfooding mirror
- Depends on:
  - reviewer-passed requirement/design evidence recorded by main orchestrator
- Unblocks:
  - S02 route references
- Target files:
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `.agents/skills/spec-dock-epic-execution/SKILL.md`

#### Planned Contract

- Scope:
  - Add expected managed skill name and authoritative installed asset inventory entries.
  - Add provider skill and dogfooding mirror.
  - Add or extend content/parity assertions that detect missing coordinator boundaries.
- Test obligation:
  - closure ids: `tc-001`, `tc-002`, `tc-003`
  - risk: new shipped managed asset can be omitted from installer/update, drift from checked-in dogfooding mirror, or absorb responsibilities from existing skills.
- Red or alternative evidence requirement:
  - red-required where practical:
    - expected managed skill inventory fails before new asset is present
    - parity/inventory tests fail before mirror/provider path is registered
  - inspect-only acceptable for prose-only boundary clauses that are better validated by `spec-reviewer`, but prefer targeted content assertions for high-risk phrases:
    - `spec-dock-issue-planning`
    - `spec-dock-issue-execution`
    - `github-pr-merge-preparer`
    - `issue start`
    - `issue finish`
    - no PR merge / merge-ready self-claim
- Green verification:
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "managed or issue_68 or issue_71 or dogfooding_agent_tooling_parity"`
  - If the `-k` expression is too broad or too narrow in the live test file, record the adjusted focused command in `report.md`.
- Refactor / cleanup guardrail:
  - Do not rewrite existing skills.
  - Do not introduce a runtime command or dependency algorithm.
  - Do not update unrelated managed assets.
- Report evidence destination:
  - Implementation Delegation Gate
  - Delegated Worker Evidence
  - Test Contract Closure for `tc-001`..`tc-003`
  - Step Contract Closure
  - Reviewer Gate Status
  - Step Commit Gate
- Amendment trigger:
  - Need for new runtime behavior, new GitHub mutation path, or responsibility change in existing issue planning/execution/PR skills.

#### Delegation Contract

- Delegated role:
  - `dev-coder` for tests/inventories.
  - `doc-writer` for skill prose.
- Input docs:
  - active `requirement.md`, `design.md`, `plan.md` after integration
  - `workflow_issue.md`
  - `workflow_epic.md`
  - existing `spec-dock-epic-planning`, `spec-dock-issue-planning`, `spec-dock-issue-execution`, and `github-pr-merge-preparer` skills
  - target test files
- Allowed paths:
  - only S01 target files listed above
- Forbidden changes:
  - canonical docs except report evidence by main orchestrator
  - runtime CLI command implementation
  - dependency algorithm implementation
  - GitHub issue/PR mutation code
  - existing skill rewrites beyond references needed in later S02
- Acceptance criteria:
  - `tc-001`, `tc-002`, `tc-003` close with pass or documented approved-no-op for non-code inspection.
- Required tests or docs-only verification:
  - targeted pytest commands above
  - direct inspection of provider/mirror skill equality or parity test output
- Reviewer focus:
  - `code-reviewer`: test/inventory/scaffold behavior
  - `spec-reviewer`: skill prose and responsibility boundary
- Stop conditions:
  - tests require files outside S01/S02 plan
  - skill cannot state coordinator semantics without changing `workflow_issue.md`
  - provider/mirror cannot be kept in parity
  - reviewer result is not fresh `pass`
- Output required:
  - changed files
  - verification result
  - worker summary
  - unresolved risks
  - Ledger Note or `No material implementation decisions beyond the approved plan.`

#### Concrete Test Cases

- `tc-s01-001` acceptance: managed skill is installed and listed
  - Precondition: expected managed skill lists do not contain `spec-dock-epic-execution`.
  - Operation: add an assertion/list entry for the new managed skill and run the focused CLI runtime managed-skill test path.
  - Expected result: the test fails before the provider asset exists and passes after the provider asset and mirror are added.
  - Failure detection: detects a new skill that exists in source but is not installed or not treated as managed.
  - Verification method: `uv run pytest tests/cli_runtime` or the narrowest test containing `_assert_managed_skills_installed`.
  - Related closure id: `tc-001`

- `tc-s01-002` acceptance: provider and dogfooding skill paths stay in parity
  - Precondition: provider install_root is source of truth and `.agents/` is checked-in mirror.
  - Operation: update asset map/inventory/parity assertions and compare provider and mirror skill files through existing dogfooding parity tests.
  - Expected result: provider and mirror `SKILL.md` exist and match the same coordinator contract.
  - Failure detection: detects missing mirror, stale mirror, or unregistered provider path.
  - Verification method: `uv run pytest tests/unit/infra/test_init_update.py -k "dogfooding_agent_tooling_parity or issue_68 or issue_71"`
  - Related closure id: `tc-002`

- `tc-s01-003` boundary: coordinator delegates instead of absorbing downstream workflows
  - Precondition: the new skill text is available in provider and mirror.
  - Operation: inspect or assert content for active context bootstrap, `deps check`, one ready Issue selection, `issue start`, handoff to `spec-dock-issue-planning`, handoff to `spec-dock-issue-execution`, handoff to `github-pr-merge-preparer`, return to `workflow_issue.md` for `issue finish`, and no PR merge self-claim.
  - Expected result: the skill reads as a coordinator and not as a replacement implementation workflow.
  - Failure detection: catches prose that skips active Issue guard, claims merge readiness, claims reviewer pass, or hides blocked/no-ready states.
  - Verification method: content assertions in `tests/unit/infra/test_init_update.py` where practical, plus `spec-reviewer` docs/spec alignment.
  - Related closure id: `tc-003`

#### Step Closure Contract

- Close conditions:
  - `tc-001`, `tc-002`, and `tc-003` are recorded as pass or justified inspect-only pass.
  - Both provider and dogfooding skill files exist.
  - Relevant tests pass or blocked reason is recorded.
  - Required reviewer gates are fresh pass.
- Residual risk:
  - Low after parity and content boundary assertions; remaining prose nuance is covered by `spec-reviewer`.

#### Step Gate

- Step reviewer gate:
  - `code-reviewer` for tests/inventory changes.
  - `spec-reviewer` for skill boundary text.
- Commit/no-op gate:
  - expected state: committed
  - commit scope: S01 target files and report evidence only
  - no-op allowed only if canonical adoption decides S01 is already fully satisfied and records exact evidence.

### S02 - Epic workflow and discovery route connection

- Behavior goal:
  - Future agents that start from Epic workflow docs, the hub skill, or `/execute-epic` can discover and use `spec-dock-epic-execution` without confusing it with planning or issue execution.
- Design references:
  - `design.md` adopted Option B
  - `design.md` D-002 `/execute-epic.md` conflict
- Depends on:
  - S01 Step Result Approval
- Unblocks:
  - S03 integration verification
- Target files:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md`
  - `.codex/prompts/execute-epic.md`
  - `tests/unit/infra/test_init_update.py` only for route/content regression assertions

#### Planned Contract

- Scope:
  - Add a short Epic execution lifecycle reference to `workflow_epic.md`.
  - Add hub route from Epic execution work to `spec-dock-epic-execution`.
  - Update `/execute-epic` to use the new coordinator and remove the contradictory "Do not create a new skill" wording.
  - Preserve provider/mirror parity.
- Test obligation:
  - closure ids: `tc-004`, `tc-005`
  - risk: future agents keep following stale prompt/hub guidance even though the new skill exists.
- Red or alternative evidence requirement:
  - red-required content assertion preferred for the old `/execute-epic` phrase.
  - inspect-only acceptable for concise workflow prose if parity tests and `spec-reviewer` cover it.
- Green verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "execute_epic or workflow_epic or dogfooding_agent_tooling_parity"`
  - `rg -n "Do not create a new skill for this workflow" src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md` should return no matches after update.
  - `rg -n "spec-dock-epic-execution|Epic execution" src/spec_dock/assets/spec_dock/docs/workflow_epic.md spec-dock/docs/workflow_epic.md src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md`
- Refactor / cleanup guardrail:
  - Keep skill prose first-read and docs concise.
  - Do not rewrite `workflow_issue.md` or `github-pr-merge-preparer`.
  - Do not broaden to unrelated docs cleanup.
- Report evidence destination:
  - Implementation Delegation Gate
  - Delegated Worker Evidence
  - Test Contract Closure for `tc-004` and `tc-005`
  - Step Contract Closure
  - Reviewer Gate Status
  - Step Commit Gate
- Amendment trigger:
  - route update requires changing runtime command behavior
  - docs require changing Issue finish/PR merge-preparer semantics
  - direct contradiction found in other workflow docs that changes accepted scope

#### Delegation Contract

- Delegated role:
  - `doc-writer` for workflow docs, hub skill, and prompt.
  - `dev-coder` for any test/content assertion updates.
- Input docs:
  - active `requirement.md`, `design.md`, canonical `plan.md` after integration
  - `workflow_epic.md`
  - `workflow_issue.md`
  - `workflow_spec_authoring.md`
  - current hub and prompt files
- Allowed paths:
  - only S02 target files
- Forbidden changes:
  - unrelated docs cleanup
  - PR merge automation wording
  - `issue finish` authority changes
  - runtime command or GitHub state mutation code
- Acceptance criteria:
  - `tc-004` and `tc-005` close.
  - provider and mirror docs/prompt/skill files remain aligned.
- Required tests or docs-only verification:
  - targeted pytest/content assertions above
  - `rg` checks for new route and removed contradiction
- Reviewer focus:
  - `spec-reviewer`: workflow/prompt/skill wording and requirement/design alignment
  - `code-reviewer`: only if test assertions change
- Stop conditions:
  - route cannot be represented without broad docs rewrite
  - accepted design Option B no longer matches implementation need
  - prompt/hub update requires changing slash command semantics
- Output required:
  - changed files
  - verification result
  - docs impact note
  - unresolved risks
  - Ledger Note or `No material implementation decisions beyond the approved plan.`

#### Concrete Test Cases

- `tc-s02-001` acceptance: `workflow_epic.md` references Epic execution lifecycle
  - Precondition: existing `workflow_epic.md` says execution coordinator behavior is outside the planning handoff section.
  - Operation: add a short reference section that points to `spec-dock-epic-execution`, Epic completion gate, and PR merge-preparer handoff.
  - Expected result: future agents can see how Issue 210 planning handoff connects to Issue 211 execution coordinator without duplicating Issue execution policy.
  - Failure detection: catches a workflow doc that leaves the new skill orphaned or duplicates downstream issue execution semantics.
  - Verification method: docs inspection, parity test, and `spec-reviewer`.
  - Related closure id: `tc-004`

- `tc-s02-002` negative: `/execute-epic` no longer contradicts the new skill
  - Precondition: current prompt contains "Do not create a new skill for this workflow".
  - Operation: update provider and mirror prompts to route Epic execution through `spec-dock-epic-execution`.
  - Expected result: the old contradictory phrase is absent and the new skill route is present.
  - Failure detection: catches stale prompt guidance that would make agents ignore the new coordinator.
  - Verification method: `rg` no-match for the old phrase and targeted content assertion if added.
  - Related closure id: `tc-005`

- `tc-s02-003` acceptance: hub route distinguishes planning, execution, and issue execution
  - Precondition: hub lists `spec-dock-epic-planning` and `spec-dock-issue-execution` but not the new Epic execution coordinator.
  - Operation: add a route entry for `spec-dock-epic-execution` while preserving existing planning and issue execution routes.
  - Expected result: Epic execution requests route to the new skill; Epic requirement/design/plan authoring still routes to `spec-dock-epic-planning`.
  - Failure detection: catches route ambiguity or replacement of existing leaf skill ownership.
  - Verification method: content assertion or inspection plus `spec-reviewer`.
  - Related closure id: `tc-005`

#### Step Closure Contract

- Close conditions:
  - `tc-004` and `tc-005` close.
  - Old `/execute-epic` contradiction is absent.
  - Provider/mirror pairs are aligned.
  - Required reviewer gates are fresh pass.
- Residual risk:
  - Conditional docs may still contain indirect ambiguity; S90 must inspect and record whether any direct contradiction remains.

#### Step Gate

- Step reviewer gate:
  - `spec-reviewer` for docs/spec route alignment.
  - `code-reviewer` if tests changed.
- Commit/no-op gate:
  - expected state: committed
  - commit scope: S02 target files and report evidence only

### S03 - Targeted integration verification and bounded repair

- Behavior goal:
  - The integrated S01/S02 changes pass the targeted regression lane for managed assets, dogfooding parity, and route/content assertions.
- Depends on:
  - S02 Step Result Approval
- Unblocks:
  - S90 docs impact resolution
- Target files:
  - no planned mutation
  - if repair is needed, only S01/S02 target files

#### Planned Contract

- Scope:
  - Run targeted verification and record evidence.
  - Delegate bounded repair only for failures directly caused by S01/S02 changes.
- Test obligation:
  - closure id: `tc-006`
  - risk: per-step checks miss cross-surface packaging or parity failures.
- Red or alternative evidence requirement:
  - covered-existing; S03 is an integration check step, not a new behavior implementation.
- Green verification:
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest tests/unit/infra/test_init_update.py`
  - `git diff --check`
  - `rg -n "Do not create a new skill for this workflow" src/spec_dock/assets/install_root/.codex/prompts/execute-epic.md .codex/prompts/execute-epic.md` should return no matches.
- Refactor / cleanup guardrail:
  - No opportunistic cleanup.
  - Repair only planned files and only failures caused by this issue.
- Report evidence destination:
  - Test Contract Closure for `tc-006`
  - Closure Coverage
  - Reviewer Gate Status if repair diff exists
  - Step Commit Gate or approved-no-op evidence
- Amendment trigger:
  - verification failure requires files outside the design file plan
  - integration failure exposes missing requirement/design decision

#### Delegation Contract

- Delegated role:
  - N/A for read-only verification.
  - `dev-coder` for bounded repair if failures are caused by planned implementation.
- Input docs:
  - canonical plan after integration
  - S01/S02 report evidence
  - failing command output
- Allowed paths:
  - none for read-only verification
  - if repair is needed, only S01/S02 target files
- Forbidden changes:
  - broad test rewrites
  - unrelated runtime or docs cleanup
  - skipping failed checks without blocker evidence
- Acceptance criteria:
  - `tc-006` closes with pass, or blocked reason and next action are recorded.
- Required verification:
  - commands listed in Green verification
- Reviewer focus:
  - no reviewer needed for no-op read-only pass beyond final gates
  - `code-reviewer` if repair diff exists
- Stop conditions:
  - tests cannot run due environment/tooling issue
  - failures are unrelated or require design amendment
  - repair would exceed S01/S02 allowed paths
- Output required:
  - command results
  - repair summary if any
  - unresolved risks
  - Ledger Note or `No material implementation decisions beyond the approved plan.`

#### Concrete Test Cases

- `tc-s03-001` regression: targeted CLI runtime lane passes
  - Precondition: S01/S02 changes are present.
  - Operation: run `uv run pytest tests/cli_runtime`.
  - Expected result: CLI runtime tests pass with the new managed skill list.
  - Failure detection: catches install/update behavior that omits or mishandles managed skills.
  - Verification method: command result in `report.md`.
  - Related closure id: `tc-006`

- `tc-s03-002` regression: install/update parity lane passes
  - Precondition: S01/S02 changes are present.
  - Operation: run `uv run pytest tests/unit/infra/test_init_update.py`.
  - Expected result: authoritative inventory, dogfooding parity, content, and package-data tests pass.
  - Failure detection: catches provider/mirror drift, unregistered files, or stale prompt guidance.
  - Verification method: command result in `report.md`.
  - Related closure id: `tc-006`

- `tc-s03-003` formatting/content guard: diff and stale prompt phrase checks pass
  - Precondition: S01/S02 changes are present.
  - Operation: run `git diff --check` and `rg` no-match for the old `/execute-epic` contradiction.
  - Expected result: no whitespace errors and no old contradiction remains.
  - Failure detection: catches formatting churn and stale route guidance.
  - Verification method: command results in `report.md`.
  - Related closure id: `tc-006`

#### Step Closure Contract

- Close conditions:
  - `tc-006` closes.
  - all targeted commands pass or blocked/incomplete evidence is recorded.
  - repair diff, if any, receives required reviewer pass and commit gate.
- Residual risk:
  - full `uv run pytest` may still be deferred by main orchestrator as final or CI evidence; record if deferred.

#### Step Gate

- Step reviewer gate:
  - none for approved-no-op verification pass.
  - `code-reviewer` if repair diff exists.
- Commit/no-op gate:
  - expected state: approved-no-op if no repair diff; committed if repair diff exists.

### S90 - Docs impact resolution / docs refresh

- Behavior goal:
  - Confirm all docs/skill/prompt impact from Issue 211 is complete and no direct contradictions remain outside the planned surfaces.
- Depends on:
  - S03 closure
- Target files:
  - no planned mutation beyond S01/S02 surfaces
  - conditional docs only if direct contradiction is found:
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/authoring/decision-routing.md`
    - `spec-dock/docs/reference_github.md`
    - provider-side counterparts if the file is shipped from `src/spec_dock/assets/spec_dock/docs/`

#### Planned Contract

- Scope:
  - Inspect docs impact and update only direct contradictions.
- Test obligation:
  - closure id: `tc-007`
- Evidence requirement:
  - inspect-only.
- Verification:
  - `git diff --name-status`
  - `rg -n "spec-dock-epic-execution|Epic execution|execute-epic|issue finish|github-pr-merge-preparer" spec-dock/docs src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills src/spec_dock/assets/install_root/.codex/prompts .agents/skills .codex/prompts`
  - targeted docs inspection recorded in `report.md`
- Report evidence destination:
  - Docs Impact section
  - Test Contract Closure for `tc-007`
  - Reviewer Gate Status
- Amendment trigger:
  - conditional docs require a new durable policy decision beyond Option B
  - docs inspection finds a requirement/design gap

#### Delegation Contract

- Delegated role:
  - `doc-writer` only if updates are required.
  - N/A for read-only docs impact inspection.
- Allowed paths:
  - S90 conditional docs only when a direct contradiction is found.
- Forbidden changes:
  - broad docs cleanup
  - examples or policy rewrites not needed for Issue 211
  - implementation/test/provider asset changes
- Required verification:
  - inspection commands above
  - `spec-reviewer` docs/spec alignment pass if any docs update occurs, or docs impact no-op evidence if none.
- Reviewer focus:
  - `spec-reviewer`
- Stop conditions:
  - docs gap changes accepted requirement/design scope
  - update would exceed conditional docs list
- Output required:
  - docs impact decision
  - changed files or approved-no-op evidence
  - unresolved risks

#### Concrete Test Cases

- `tc-s90-001` inspect-only: conditional docs have no direct contradiction
  - Precondition: S01/S02 route changes are present.
  - Operation: inspect docs and prompts for Epic execution, issue finish, PR-preparer, and old no-skill wording.
  - Expected result: no unplanned direct contradiction remains; if one is found, it is updated within the conditional docs boundary.
  - Failure detection: catches stale workflow policy that conflicts with the new skill.
  - Verification method: `rg` output and docs inspection recorded in `report.md`.
  - Related closure id: `tc-007`

#### Step Closure Contract

- Close conditions:
  - `tc-007` closes.
  - docs impact is either resolved by updates or approved-no-op with evidence.
  - `spec-reviewer` passes docs/spec alignment if docs changed.
- Residual risk:
  - none expected if no direct contradiction remains.

#### Step Gate

- Step reviewer gate:
  - `spec-reviewer` if docs changed; otherwise read-only docs impact confirmation.
- Commit/no-op gate:
  - committed if docs changed; approved-no-op if inspection finds no updates required.

### S99 - Final quality gate

- Behavior goal:
  - Confirm the entire issue satisfies requirement/design/plan/report alignment and all closure IDs are closed before downstream handoff.
- Depends on:
  - S90 closure
- Target files:
  - no planned mutation except bounded reviewer-requested fixes.

#### Planned Contract

- Scope:
  - final QA, code, and spec review.
  - final report ledger closure.
  - PR delivery / merge-preparation handoff remains later execution evidence and must follow `workflow_issue.md`.
- Test obligation:
  - closure id: `tc-008`
- Verification:
  - verify all required closure IDs closed in report
  - verify targeted tests from S03 are recorded
  - run any extra tests required by `qa-reviewer`
  - `git diff --check`
- Report evidence destination:
  - Final QA Gate
  - Final Code Review Gate
  - Final Spec Review Gate
  - Closure Coverage
  - Final Commit / external delivery evidence destination
- Amendment trigger:
  - final reviewer finds missing requirement/design coverage
  - final reviewer requires a new closure ID not covered by current plan

#### Delegation Contract

- Delegated role:
  - `qa-reviewer`
  - issue-wide `code-reviewer`
  - final `spec-reviewer`
  - `dev-coder` or `doc-writer` only for bounded reviewer-requested fixes matching changed file type.
- Allowed paths:
  - only files already in S01/S02/S90 scope unless reviewer finding requires plan amendment.
- Forbidden changes:
  - using final review as a substitute for missing step review
  - merging PR or closing GitHub issue
  - claiming issue finish before `workflow_issue.md` completion gates
- Required verification:
  - all final reviewers fresh pass
  - final report evidence updated
  - final commit gate handled by main orchestrator
- Reviewer focus:
  - `qa-reviewer`: test sufficiency and integration test need
  - `code-reviewer`: integrated diff, structure, regression risk
  - `spec-reviewer`: requirement/design/plan/report/docs consistency
- Stop conditions:
  - any final reviewer is not fresh pass
  - unresolved closure ID
  - missing report evidence
  - uncommitted implementation step diff remains
- Output required:
  - final reviewer verdicts
  - final risk status
  - final report ledger state
  - final commit/external evidence destination

#### Concrete Test Cases

- `tc-s99-001` final QA: test sufficiency reviewed
  - Precondition: S01/S02/S03/S90 are closed.
  - Operation: run `qa-reviewer` against requirement/design/plan/report and test evidence.
  - Expected result: QA reviewer passes or identifies missing tests that are fixed and re-reviewed.
  - Failure detection: catches under-tested managed asset or route behavior.
  - Verification method: final QA gate evidence in `report.md`.
  - Related closure id: `tc-008`

- `tc-s99-002` final code review: integrated diff reviewed
  - Precondition: final diff includes provider/mirror/tests/docs changes.
  - Operation: run issue-wide `code-reviewer`.
  - Expected result: code reviewer passes integrated scaffold/test changes and confirms no forbidden runtime/GitHub mutation path.
  - Failure detection: catches structural/test regressions or accidental implementation drift.
  - Verification method: final code review gate evidence in `report.md`.
  - Related closure id: `tc-008`

- `tc-s99-003` final spec review: requirements and docs align
  - Precondition: final plan/report/docs/skills/prompts are ready.
  - Operation: run final `spec-reviewer`.
  - Expected result: spec reviewer passes AC/EC traceability and docs/spec alignment.
  - Failure detection: catches missing AC/EC coverage, stale delegated evidence, or unauthorized self-claim.
  - Verification method: final spec review gate evidence in `report.md`.
  - Related closure id: `tc-008`

#### Step Closure Contract

- Close conditions:
  - `tc-008` closes.
  - final QA/code/spec reviewers pass.
  - final report ledger records closure coverage and reviewer gate evidence.
  - final commit/external evidence destination is recorded by main orchestrator.
- Residual risk:
  - none acceptable for issue completion; unresolved final reviewer findings block completion.

#### Step Gate

- Step reviewer gate:
  - final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
- Commit/no-op gate:
  - final commit after all implementation steps and report ledger are closed.
  - final commit must not catch up uncommitted implementation step work.

## Final Exit Contract

The canonical plan should require all of the following before the issue can be reported complete:

- all AC/EC rows in the Requirement -> Step Mapping are closed
- every required closure ID in the Spec-Locked Closure Index is pass or valid approved-no-op in `report.md`
- every implementation step is committed or valid approved-no-op
- S90 docs impact is resolved
- S99 final QA/code/spec reviewers are fresh pass
- targeted tests and `git diff --check` are recorded
- final report ledger is updated before final commit
- PR delivery and merge-preparation evidence are handled through `github-pr-merge-preparer` before `issue finish`, per `workflow_issue.md`
- `issue finish` is not claimed by this plan draft or any delegated worker
