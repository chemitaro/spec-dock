---
created_by_role: implementation-planner
scope_id: iss-00186
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260615t152809z-interview-issue-execution-hardening-scope-boundary.md
  - spec-dock/active/issue/discussions/20260615t153746z-draft-design-issue-execution-step-gate-hardening.md
  - spec-dock/active/issue/discussions/20260613t084318z-disc-issue-execution-skill-update-direction.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/spec_dock/templates/issue/plan.md
  - src/spec_dock/assets/spec_dock/templates/issue/report.md
  - src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending_parent_verification
---

# Draft Plan: Issue Execution Step Gate Hardening

This is delegated implementation planning evidence for `iss-00186`. It is not canonical authority. It does not claim phase promotion, reviewer pass, issue readiness, implementation readiness, or final ownership. The main orchestrator must verify scope, adopt or reject content in `report.md`, rewrite accepted content into canonical `plan.md`, and run a fresh `spec-reviewer` pass before implementation handoff.

## 1. Plan Summary

Use Option B from the adopted interview and canonical design:

- strengthen provider-side `spec-dock-issue-execution/SKILL.md` as a compact first-read gate spine;
- add minimal exact semantics to provider-side `workflow_issue.md`;
- update provider-side tests/assertions for the required wording while preserving existing fragments;
- inspect `authoring/issue-plan.md`, issue templates, and `/execute-issue` prompt for severe contradictions only;
- validate dogfooding mirrors and SpecDock state after provider changes.

The implementation plan should be a sequential command queue. No two implementation steps are executed in parallel. Each implementation step is one review scope and one commit boundary. A later final quality gate cannot replace a per-step reviewer gate or per-step commit/no-op gate.

Recommended steps:

- `S01` skill spine update.
- `S02` workflow exact semantics update.
- `S03` tests/assertion update.
- `S04` alignment check and small severe fixes or follow-up decisions.
- `S90` docs/mirror/sync validation.
- `S99` final quality gate.

## 2. Requirement / Design Traceability

Source revisions used:

- `requirement.md`: `最終更新: "2026-06-16"`, fresh requirement reviewer pass recorded in `report.md` Spec Authoring Gate.
- `design.md`: `最終更新: "2026-06-16"`, fresh design reviewer pass recorded in `report.md` Spec Authoring Gate.
- `report.md`: current scaffold includes adopted research/interview/design draft evidence and plan-phase handoff target.
- Provider and dogfooding `workflow_issue.md` and `authoring/issue-plan.md` were verified as exact matches by `diff -q`.

Traceability matrix:

| Requirement | Plan response |
|---|---|
| AC-001 First-read single-step gate | `S01` adds the skill gate spine and `S03` asserts critical phrases. |
| AC-002 Delegated mutation gate | `S01` top-loads `dev-coder` / `doc-writer` routing and Parent Implementation Exception; `S02` keeps exact policy in workflow docs. |
| AC-003 Reviewer fail and follow-up gate | `S01` and `S02` keep reviewer fail routed to bounded delegated follow-up plus fresh re-review; `S03` preserves/adds assertions. |
| AC-004 Completion terminology boundary | `S02` defines Step Result Approval, `approved-local-execution`, `degraded mode`, `waived`, and final commit boundary. |
| AC-005 Context-surface ownership compliance | `S04` checks skill/docs/templates/prompt against the accepted ownership ADR and records severe contradictions or follow-ups. |
| AC-006 Provider and dogfooding validation | `S90` handles provider-to-mirror inspection/update, `sync` when needed, and `validate`. |
| AC-007 Evidence adoption and planning readiness | Canonical `report.md` should record this draft in Evidence Adoption Ledger and Delegated Draft Evidence before plan promotion. |
| EC-001 Multiple-step bundling attempt | All implementation steps have one review scope and one commit/no-op gate. |
| EC-002 Sub-agent unavailable / denied / host conflict | `S02` exact semantics and all step gates treat these as blocked/incomplete unless explicitly handled by workflow policy. |
| EC-003 Skill-text-only / docs-only change | `S01`, `S02`, and `S04` use inspect-only / structural assertion evidence plus `spec-reviewer` gates. |
| EC-004 Final commit catch-up misconception | `S02` and `S99` state final commit is not a catch-up implementation commit. |
| EC-005 Broad template / prompt drift | `S04` permits only small severe fixes or follow-up decisions. |

## 3. Milestones

| Milestone | Included steps | Exit condition |
|---|---|---|
| M1 first-read spine fixed | `S01` | Provider skill includes compact single-step gate spine, delegated mutation boundary, reviewer fail path, and non-pass availability boundary. |
| M2 detail semantics fixed | `S02` | Provider `workflow_issue.md` owns exact semantics without copying the whole policy into the skill. |
| M3 assertions aligned | `S03` | Focused tests cover new gate phrases and still preserve existing required fragments. |
| M4 alignment triage complete | `S04` | Authoring docs, templates, and prompt have no severe contradiction, or small severe fixes/follow-ups are recorded. |
| M5 mirror and validation complete | `S90` | Dogfooding mirror is inspected/updated, `validate` passes, and `sync` is run when required by the actual diff. |
| M9 final gates complete | `S99` | Final QA, issue-wide code review, final spec review, final report ledger, and final commit/delivery evidence are complete. |

## 4. Dependency-Derived Execution Order

Design dependency order:

1. `S01` changes the first-read skill surface because this is the entry point that currently fails to top-load the loop.
2. `S02` changes workflow detail semantics because the skill spine should route to a precise policy surface rather than becoming a second policy authority.
3. `S03` changes tests after final wording exists, avoiding brittle assertions against draft text.
4. `S04` runs alignment after the core contract is explicit, so severe contradictions can be judged against the actual intended wording.
5. `S90` validates provider source and dogfooding mirror after all shipped-surface changes are known.
6. `S99` performs issue-wide gates after implementation steps and mirror/docs validation have closed.

Do not combine `S01` and `S02` into one implementation step even though both are text changes. They represent different authority surfaces and require separate step review/commit evidence.

## 5. Issue / Step Slicing

### Spec-Locked Closure Index

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| `tc-001` | S01 | skill first-read gate | acceptance | AC-001, EC-001 | Skill says one current implementation step closes before next step begins. | Provider skill text and installed mirror text. | Multi-step batching from first-read ambiguity. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| `tc-002` | S01 | delegated mutation gate | acceptance | AC-002, AC-003, EC-002 | Skill routes normal file mutation to delegated worker and requires Parent Implementation Exception for direct parent fixes. | Provider skill text. | Parent direct implementation or direct reviewer-fail fixes. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| `tc-003` | S02 | workflow exact semantics | acceptance | AC-004, EC-002, EC-004 | Workflow defines Step Result Approval and non-pass/final-commit boundaries. | Provider workflow docs. | Treating degraded/waived/final commit as gate pass. | yes | inspect-only + structural assertion | report Step/Test Contract Closure |
| `tc-004` | S03 | provider assertions | regression | AC-001 to AC-004 | Tests assert new critical fragments and preserve existing required fragments. | `tests/unit/infra/test_init_update.py` and targeted pytest. | Silent loss of shipped wording during future updates. | yes | red-required or covered-existing | report Test Contract Closure |
| `tc-005` | S04 | alignment triage | acceptance | AC-005, EC-005 | Alignment targets contain no severe contradiction or record small fix/follow-up decision. | `authoring/issue-plan.md`, templates, prompt inspection. | Template/prompt normalizes N/A delegation or bundled steps as success. | yes | inspect-only | report Decision Ledger / Closure Coverage |
| `tc-006` | S90 | provider/mirror validation | acceptance | AC-006 | Provider source and dogfooding mirror are intentionally aligned, and SpecDock validate passes. | Provider files, mirror files, validation command. | Mirror-only edit or shipped source drift. | yes | manual-required + command evidence | report Docs Impact / Closure Coverage |
| `tc-007` | S99 | final quality gate | acceptance | AC-007 | Final QA, code review, spec review, report ledger, final commit/no-op evidence all close. | Whole issue diff and report ledger. | Final review replacing step gates; incomplete completion claim. | yes | manual-required | report Final Quality Gate |

### Step Overview

| Step | Behavior goal | Depends on | Unblocks | Target files | Primary worker | Reviewer |
|---|---|---|---|---|---|---|
| S01 | Skill first-read gate spine is visible and compact. | approved requirement/design/plan | S02, S03 | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` | `doc-writer` | `spec-reviewer` |
| S02 | Workflow docs own exact gate semantics. | S01 wording intent | S03, S04 | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | `doc-writer` | `spec-reviewer` |
| S03 | Provider assertions protect the new contract. | S01, S02 | S90, S99 | `tests/unit/infra/test_init_update.py` | `dev-coder` | `code-reviewer` |
| S04 | Alignment targets are checked and only severe contradictions are fixed or followed up. | S01, S02 | S90, S99 | alignment targets only if severe fix is needed | `doc-writer` for fixes, otherwise no-op | `spec-reviewer` |
| S90 | Docs impact, mirror, sync, validate are resolved. | S01-S04 | S99 | dogfooding mirror files if update is required; report evidence | `doc-writer` if docs/mirror updates are needed | `spec-reviewer` |
| S99 | Final quality gate closes the issue-wide contract. | S01-S90 | issue delivery | report ledger and external delivery evidence | main orchestrator coordination only | `qa-reviewer`, `code-reviewer`, `spec-reviewer` |

### Implementation Step S01 - Skill Spine Update

- Behavior goal: reading provider `spec-dock-issue-execution/SKILL.md` makes the single-step execution loop and stop conditions immediately visible.
- Planned contract:
  - Scope: add a compact first-read gate spine near the top of the skill.
  - Allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`.
  - Forbidden changes: workflow docs, tests, templates, prompts, canonical docs, runtime code, agent definitions.
  - Required verification: inspect provider skill for `single current implementation step`, required verification, fresh step reviewer pass, Step Commit Gate, post-commit clean check, next-step unlock, delegated mutation, Parent Implementation Exception, and non-pass availability wording.
  - Report evidence destination: TDD/alternative evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
  - Amendment trigger: if the skill needs full lifecycle policy, field schema, or completion matrix content, stop and return to design/plan amendment.
- Delegation contract:
  - delegated role: `doc-writer`.
  - input docs: active requirement/design/plan/report, provider skill, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`.
  - acceptance criteria: `tc-001`, `tc-002`.
  - required output: changed files, wording summary, inspection result, no-material-decision or Ledger Note, unresolved risks.
  - stop conditions: any need to edit canonical docs, implementation code, tests, templates, prompts, or agent definitions in this step.
- Concrete test cases:
  - `tc-s01-001` acceptance: skill states the step loop before detailed routing.
    - Premise: provider skill lacks a top-loaded loop.
    - Operation: inspect provider skill after the `doc-writer` change.
    - Expected result: the skill says current step closure requires required verification, fresh step reviewer pass, Step Commit Gate, and post-commit clean check before next-step unlock.
    - Failure detection: catches a skill that still permits multi-step bundling by omission.
    - Verification method: targeted `rg`/manual inspection and later S03 assertion.
    - Related closure id: `tc-001`.
  - `tc-s01-002` acceptance: skill preserves delegated mutation boundary.
    - Premise: issue steps may mutate shipped docs/skills/tests.
    - Operation: inspect routing and reviewer-fail wording.
    - Expected result: runtime/tests/scaffold route to `dev-coder`, shipped docs/templates/skills/workflow text route to `doc-writer`, and parent direct fixes require Parent Implementation Exception.
    - Failure detection: catches parent direct implementation or direct reviewer-fail fixes being normalized.
    - Verification method: targeted inspection and later S03 preservation assertion.
    - Related closure id: `tc-002`.
- Step gate:
  - step reviewer gate: fresh `spec-reviewer` docs/spec alignment pass before commit.
  - commit/no-op gate: one commit containing only S01 provider skill change, or approved-no-op with documented reason and clean diff evidence.

### Implementation Step S02 - Workflow Exact Semantics

- Behavior goal: `workflow_issue.md` owns the exact semantics behind the skill spine.
- Planned contract:
  - Scope: add minimal definitions/clarifications for Step Result Approval, `approved-local-execution`, `degraded mode`, `waived`, unavailable/denied/host conflict, reviewer fail, and final commit boundary.
  - Allowed paths: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`.
  - Forbidden changes: skill, tests, templates, prompts, runtime code, canonical docs.
  - Required verification: inspect provider workflow docs for exact semantics without copying full policy into the skill.
  - Report evidence destination: TDD/alternative evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Decision Ledger if terminology tradeoff is material, Reviewer Gate Status, Step Commit Gate.
  - Amendment trigger: if exact semantics require changing durable ownership model, runtime enforcement, template authority, or agent permissions.
- Delegation contract:
  - delegated role: `doc-writer`.
  - input docs: active requirement/design/plan/report, provider workflow docs, current provider skill wording from S01.
  - acceptance criteria: `tc-003`.
  - required output: changed files, wording summary, inspection result, no-material-decision or Ledger Note, unresolved risks.
  - stop conditions: any need to rename core terminology broadly, rewrite workflow policy, or edit templates/prompts in this step.
- Concrete test cases:
  - `tc-s02-001` acceptance: Step Result Approval unlocks the next step only after required gates.
    - Premise: workflow docs define per-step review/commit but exact unlock semantics can be missed.
    - Operation: inspect provider workflow docs after update.
    - Expected result: Step Result Approval requires current step closure, required verification, fresh reviewer pass, Step Commit Gate, and post-commit clean check.
    - Failure detection: catches proceeding to next step after verification without reviewer/commit/clean evidence.
    - Verification method: targeted inspection and later S03 assertion.
    - Related closure id: `tc-003`.
  - `tc-s02-002` negative: final commit is not a catch-up implementation commit.
    - Premise: earlier step diff remains uncommitted before S99.
    - Operation: inspect completion/final commit wording.
    - Expected result: workflow says final commit cannot bundle earlier uncommitted implementation step changes.
    - Failure detection: catches missing per-step commit being rescued at final gate.
    - Verification method: targeted inspection and later S03 assertion.
    - Related closure id: `tc-003`.
  - `tc-s02-003` negative: unavailable/denied/host conflict/waiver are not reviewer passes.
    - Premise: reviewer/delegation availability is mixed with completion evidence.
    - Operation: inspect reviewer/delegation state semantics.
    - Expected result: fresh `passed` is the required reviewer gate pass; waiver is explicit risk acceptance, and degraded mode is not success/readiness.
    - Failure detection: catches degraded success or automatic parent direct implementation.
    - Verification method: targeted inspection and later S03 assertion.
    - Related closure id: `tc-003`.
- Step gate:
  - step reviewer gate: fresh `spec-reviewer` docs/spec alignment pass before commit.
  - commit/no-op gate: one commit containing only S02 provider workflow doc change, or approved-no-op with documented reason and clean diff evidence.

### Implementation Step S03 - Tests / Assertion Update

- Behavior goal: provider tests protect the new skill and workflow contract while preserving existing required fragments.
- Planned contract:
  - Scope: update focused assertions in `tests/unit/infra/test_init_update.py`.
  - Allowed paths: `tests/unit/infra/test_init_update.py`.
  - Forbidden changes: provider docs/skill, templates, prompts, runtime code, canonical docs.
  - Required verification: targeted pytest for the assertions, preferably the narrowest test class/function covering installed asset content; if collection granularity is unclear, run `uv run pytest tests/unit/infra/test_init_update.py`.
  - Report evidence destination: Red/Green/Refactor evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Discovered Tests, Reviewer Gate Status, Step Commit Gate.
  - Amendment trigger: if tests require runtime behavior changes, broad fixture rewrite, or empirical compliance harness.
- Delegation contract:
  - delegated role: `dev-coder`.
  - input docs: active requirement/design/plan, S01/S02 final wording, existing `test_init_update.py`.
  - acceptance criteria: `tc-004`.
  - required output: changed files, test command/result, any existing failures not caused by S03, no-material-decision or Ledger Note.
  - stop conditions: assertion brittleness requiring long paragraph matches, unrelated test refactor, or new dependency.
- Concrete test cases:
  - `tc-s03-001` regression: provider issue-execution skill contains the new gate spine fragments.
    - Premise: S01 final wording exists.
    - Operation: run focused provider asset assertion test.
    - Expected result: test fails without S01 wording and passes with S01 wording.
    - Failure detection: catches future removal of single-step gate, fresh reviewer pass, Step Commit Gate, or post-commit clean wording.
    - Verification method: `uv run pytest tests/unit/infra/test_init_update.py` or narrower selected test.
    - Related closure id: `tc-004`.
  - `tc-s03-002` regression: provider workflow docs contain exact semantics fragments.
    - Premise: S02 final wording exists.
    - Operation: run focused workflow doc assertion.
    - Expected result: test covers Step Result Approval, unavailable/denied/host conflict/waiver non-pass semantics, and final commit not catch-up.
    - Failure detection: catches future drift from Option B semantics.
    - Verification method: `uv run pytest tests/unit/infra/test_init_update.py` or narrower selected test.
    - Related closure id: `tc-004`.
  - `tc-s03-003` preservation: existing asserted fragments remain valid.
    - Premise: existing tests already assert source-of-truth, concise reminder, `dev-coder`, `doc-writer`, bounded delegated follow-up, and Parent Implementation Exception.
    - Operation: run the same focused assertions.
    - Expected result: existing fragments still pass.
    - Failure detection: catches accidental wording regression while adding new assertions.
    - Verification method: focused pytest.
    - Related closure id: `tc-004`.
- Step gate:
  - step reviewer gate: fresh `code-reviewer` pass before commit.
  - commit/no-op gate: one commit containing only S03 assertion changes, or approved-no-op with documented reason and clean diff evidence.

### Implementation Step S04 - Alignment Check and Small Severe Fixes / Follow-Up Decisions

- Behavior goal: adjacent surfaces do not contradict the hardened gate, without expanding this issue into broad template/prompt governance.
- Planned contract:
  - Scope: inspect provider `authoring/issue-plan.md`, issue `plan.md` template, issue `report.md` template, and `/execute-issue` prompt; apply only small severe contradiction fixes if necessary.
  - Allowed paths if severe fix is required:
    - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
    - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
    - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - Forbidden changes: broad template rewrite, empirical harness, runtime enforcement, agent definitions, canonical docs.
  - Required verification: inspection notes; targeted assertions only if a changed shipped asset already has or needs a provider assertion.
  - Report evidence destination: Decision Ledger for severe/no severe contradiction decision, Step/Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate.
  - Amendment trigger: any broad template/prompt drift that cannot be fixed in a small, directly gate-related wording change.
- Delegation contract:
  - delegated role: `doc-writer` for any file mutation; no-op inspection may be performed by the orchestrator as read-only evidence if allowed by workflow.
  - input docs: active requirement/design/plan, S01/S02 wording, S03 tests, alignment target files.
  - acceptance criteria: `tc-005`.
  - required output: changed files or approved-no-op rationale, severe contradiction inventory, follow-up recommendation, no-material-decision or Ledger Note.
  - stop conditions: if fixing requires template authority redesign, prompt redesign, empirical harness, or more than one reviewable micro-edit.
- Concrete test cases:
  - `tc-s04-001` inspect-only: plan authoring docs do not undermine step-local delegation/test gates.
    - Premise: `authoring/issue-plan.md` owns field semantics.
    - Operation: inspect for missing/contradictory delegation contract, concrete test cases, reviewer fail, and commit/no-op gate semantics.
    - Expected result: no severe contradiction, or small fix/follow-up decision recorded.
    - Failure detection: catches global-only test plans or missing step-local gate semantics.
    - Verification method: targeted inspection, and pytest if an asserted provider asset is changed.
    - Related closure id: `tc-005`.
  - `tc-s04-002` inspect-only: issue templates remain scaffold/evidence slots, not compliance authorities.
    - Premise: templates are alignment targets only.
    - Operation: inspect issue `plan.md` and `report.md` templates for N/A delegation or multi-step bundled logs being normalized as success.
    - Expected result: no severe contradiction, or small fix/follow-up decision recorded.
    - Failure detection: catches templates that invite bypassing per-step delegation/review/commit gates.
    - Verification method: targeted inspection, and pytest if template assertions change.
    - Related closure id: `tc-005`.
  - `tc-s04-003` inspect-only: `/execute-issue` prompt aligns with the skill/workflow gate.
    - Premise: prompt is an entry alignment surface, not a separate source of truth.
    - Operation: inspect prompt for readiness, step-local cases, per-step review/commit, report evidence, and final gate wording.
    - Expected result: no severe contradiction, or small fix/follow-up decision recorded.
    - Failure detection: catches prompt guidance that allows implementation before executable plan or final review replacing step review.
    - Verification method: targeted inspection.
    - Related closure id: `tc-005`.
- Step gate:
  - step reviewer gate: fresh `spec-reviewer` docs/spec alignment pass before commit/no-op.
  - commit/no-op gate: one commit for small severe alignment fixes only, or approved-no-op with checked files, no-op rationale, and clean diff evidence.

## 6. Test Strategy Mapping

| Step | Evidence level | Primary verification |
|---|---|---|
| S01 | inspect-only + S03 structural assertion | targeted skill inspection, then provider asset assertion in S03 |
| S02 | inspect-only + S03 structural assertion | targeted workflow doc inspection, then provider asset assertion in S03 |
| S03 | red-required or covered-existing | focused pytest for `tests/unit/infra/test_init_update.py` |
| S04 | inspect-only, with targeted pytest if changed | alignment inspection and follow-up/no-op record |
| S90 | manual-required + command evidence | provider/mirror diff/inspection, `validate`, `sync` when needed |
| S99 | manual-required | final QA, issue-wide code review, final spec review, final report ledger, final commit/delivery evidence |

Suggested focused commands for canonical plan:

```bash
uv run pytest tests/unit/infra/test_init_update.py
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
git status --short
```

`sync` should be run when provider-to-mirror or generated projection refresh is part of the actual implementation result. If no mirror/projection update is required, record the no-op rationale and the inspection performed.

## 7. Review Gates

Per-step gates:

- `S01`: `spec-reviewer` for skill-text docs/spec alignment.
- `S02`: `spec-reviewer` for workflow docs/spec alignment.
- `S03`: `code-reviewer` for test assertion diff and regression risk.
- `S04`: `spec-reviewer` for alignment/no-op/follow-up decision; if tests change, include `code-reviewer` or split the step.
- `S90`: `spec-reviewer` for docs/mirror/sync validation evidence.
- `S99`: final `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.

Step reviewer gates are fresh gates. `failed`, `unavailable`, `denied`, `waived`, and `provisional` are not pass states. Reviewer fail should route to bounded delegated follow-up and fresh re-review. Parent direct fixes need a new Parent Implementation Exception before mutation.

## 8. Rollback / Compatibility

Compatibility:

- Runtime CLI/API behavior should not change.
- Existing consumer update behavior should remain compatible because the issue changes shipped text assets and tests only.
- Existing required test fragments should be preserved; new assertions should focus on stable contract phrases rather than full paragraphs.

Rollback:

- Revert S01 skill wording and matching S03 skill assertions together.
- Revert S02 workflow wording and matching S03 workflow assertions together.
- Revert any S04 small severe fix independently if it proves too broad, then convert it to follow-up.
- After rollback, rerun the same focused tests, mirror inspection/update, and `validate` evidence.

## 9. Docs Impact

Docs impact is expected and must be resolved before S99:

- Provider skill impact: yes, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`.
- Provider workflow docs impact: yes, `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`.
- Provider authoring docs/templates/prompt impact: inspect-only unless S04 finds severe contradiction.
- Dogfooding mirror impact: expected for `.agents/skills/spec-dock-issue-execution/SKILL.md` and `spec-dock/docs/workflow_issue.md` after provider update/sync path.
- Canonical docs impact: `plan.md` and `report.md` adoption only by main orchestrator; this draft must not edit them.

S90 should record:

- provider/mirror parity or intentional difference;
- `sync` and `validate` results or no-op rationale;
- targeted inspection of mirror skill and workflow docs;
- docs/spec reviewer result.

## 10. Final Quality Gate

S99 should be an independent final step after S90, not a substitute for per-step gates.

Required final checks:

- all required closure ids `tc-001` to `tc-007` are closed in report Step/Test Contract Closure and Closure Coverage;
- Evidence Adoption Ledger contains this implementation-planner draft with adoption decision;
- Delegated Draft Evidence records the draft path, `created_by_role: implementation-planner`, source paths, intended targets, `adoption_status`, `reflected_to`, and diff guard result;
- no `Status=open` report decision ledger entries remain;
- all implementation steps are `committed` or valid `approved-no-op`;
- final `qa-reviewer` passes obligation coverage and integration test decision;
- issue-wide `code-reviewer` passes integrated diff review;
- final `spec-reviewer` passes requirement/design/plan/report/implementation/tests/docs alignment;
- final report ledger and external delivery evidence record final commit scope and clean state.

## 11. Plan Blockers

Blocking gaps found in design evidence: none.

Non-blocking implementation risks:

- S01/S02 wording may become too long and duplicate policy. Mitigation: keep skill compact; keep exact semantics in workflow docs.
- S03 assertions may become brittle. Mitigation: assert stable contract phrases, not full paragraphs.
- S04 may discover broad template/prompt drift. Mitigation: fix only small severe contradictions; otherwise record follow-up as non-blocking or blocking according to impact.
- Sub-agent/reviewer unavailability during actual implementation blocks the affected gate; it is not a success path.

Clarification candidates for the main orchestrator:

- none required before canonical plan drafting.
- if S04 finds severe but broad template/prompt drift, decide whether to create a follow-up issue or amend the plan after design re-check.

## 12. Integration Notes for Main Orchestrator

Recommended canonical adoption path:

1. Run post-run diff guard and confirm this delegated author only created one new flat Markdown file under the target `discussions/` directory.
2. Add an Evidence Adoption Ledger entry for this draft in `report.md`.
3. Add a Delegated Draft Evidence row for this draft in `report.md`.
4. Rewrite adopted content into canonical `plan.md`; do not copy this draft blindly.
5. Run fresh `spec-reviewer` on canonical `plan.md` and update Spec Authoring Gate before implementation start.

Suggested EAL note:

```text
EAL-004 | adopted/partially_adopted | implementation-planner delegated draft | plan.md/report.md | Draft maps Option B design to sequential implementation steps with per-step delegation, concrete test cases, reviewer gates, commit/no-op gates, S90 docs/mirror validation, and S99 final quality gate. | discussions/20260615t154722z-draft-plan-issue-execution-step-gate-hardening.md | canonical plan rewrite and fresh spec-reviewer
```

Leaf evidence used:

- No additional leaf delegation was requested.
- Evidence is source-grounded in active issue docs, accepted interview/design draft, workflow docs, provider assets, templates, prompt, and relevant tests.

Forbidden actions avoided:

- No canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edit.
- No implementation file, test, config, agent instruction, workflow, GitHub, or secret edit.
- No staging or commit.
- No phase promotion, issue close, reviewer pass, implementation readiness, or final authority claim.

Unresolved design gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
