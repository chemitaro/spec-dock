---
created_by_role: spec-dock-implementation-planner
role_alias: implementation-planner
scope_id: iss-00149
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py
  - spec-dock/scripts/spec_dock_runtime/domain/authority.py
  - spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - tests/domain_runtime/test_authority.py
  - tests/cli_runtime/test_issue_lifecycle.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# Implementation Plan Draft for iss-00149

## Plan Summary

This draft proposes an executable issue plan for `iss-00149 Issue finish synthetic approval closeout bug`.

The approved requirement and design fix the strategy:

- keep `runtime_active_selection` as synthetic approval and continue rejecting it for downstream lifecycle grants;
- add a finish-only lifecycle token, `issue_finish_lifecycle_transition`;
- run `issue finish` in this order: local preconditions -> transition persistence -> existing `issue_finish` authority gate -> GitHub close / already-closed check -> active clear -> lifecycle-owned post-sync;
- update provider-side runtime first, then keep the dogfooding mirror and workflow guidance consistent.

The plan should be treated as a proposal for canonical `plan.md`. It does not claim implementation readiness, reviewer pass, phase completion, or final authority.

Assumptions:

- Requirement and design have fresh `spec-reviewer` pass as stated by the orchestrator and reflected in `report.md`.
- `issue_finish_lifecycle_transition` is issue-local and finish-only; ancestor initiative / epic synthetic downstream blocks are not widened in this issue.
- Existing public CLI command shape remains `spec-dock issue finish`; no explicit promotion command is added.

## Requirement / Design Traceability

### Spec-Locked Closure Index

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input / state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | synthetic invariant | constraint | AC-003; non-negotiable constraints; design domain invariant | `runtime_active_selection` continues to fail for `implementation_start`, `issue_ready`, `issue_finish`, and `phase_completion` with `active_synthetic_approval_not_lifecycle_approval` | `evaluate_authority_gate()` with runtime promotion record and downstream lifecycle grants | unsafe domain relaxation that makes synthetic approval lifecycle approval | yes | red-required | `tests/domain_runtime/test_authority.py` step closure |
| tc-002 | S01 | finish transition helper | acceptance / constraint | AC-001; design interface contract | helper builds `promotion_decision=issue_finish_lifecycle_transition` bound to `active:<issue-id>` and grants only `review_input`, `planning_input`, `design_baseline`, `issue_finish` | helper output for `node_id=iss-00101` | broad grants after transition enabling unrelated lifecycle operations | yes | red-required | domain helper tests |
| tc-003 | S01 | finish-only token gate | constraint | AC-003; design invariant | `issue_finish_lifecycle_transition` passes only when `required_grant=issue_finish`; it fails for other lifecycle grants with explicit reason such as `finish_transition_not_valid_for_required_grant` or missing grant | `evaluate_authority_gate()` with finish transition record and lifecycle required grants | token accepted too broadly | yes | red-required | domain authority tests |
| tc-004 | S01 | active binding | edge / negative | EC-002; design expected revision rule | stale revision / stale hash / different active id remain fail-closed before application transition can proceed | promotion record whose revision/hash is not `active:<entry.id>` | closing wrong active issue or stale active state | yes | covered-existing plus red-required for token helper | domain tests and issue lifecycle negative tests |
| tc-005 | S02 | normal closeout | acceptance | AC-001; DEC-001; design sequence | synthetic active issue satisfying local gates is internally transitioned, GitHub issue is closed, active state is cleared, and post-sync runs | temp repo after `issue start` or `active set`, linked OPEN GitHub issue stub | normal lifecycle blocked after PR/GitHub close readiness | yes | red-required | CLI runtime test |
| tc-006 | S02 | already closed closeout | edge | EC-001; AC-001 | synthetic active issue with already CLOSED GitHub issue follows the same transition path and clears active state | temp repo with GitHub issue state `CLOSED` | already-closed issue leaves active stuck | yes | red-required | CLI runtime test |
| tc-007 | S02 | local precondition failure | negative | AC-002; EC-003; EC-004 | unresolved Evidence Adoption Ledger or delegated artifact authority failure blocks before transition persistence, GitHub close, active clear, or post-sync | report with `blocked` / `stale` EAL or proposed delegated artifact metadata | auto-promoting blocked or proposed evidence | yes | red-required | application / CLI runtime tests |
| tc-008 | S02 | stale synthetic record | negative | EC-002 | synthetic active entry whose promotion record is not bound to current active entry fails before transition and before GitHub close | active issue id differs from promotion record `active:<id>` | closing wrong issue after stale active mutation | yes | red-required | issue lifecycle test |
| tc-009 | S02 | transition persistence failure | negative / compatibility | design retry / transaction semantics | persistence failure restores previous active state and does not call GitHub close, active clear, or post-sync | active store write / pointer update failure after local gates | partial lifecycle state write or external mutation after failed local write | yes | red-required | application test with failing active store |
| tc-010 | S02 | close failure retry | negative / retry | design retry semantics | GitHub view/close failure after transition persistence leaves active issue finish-ready, does not clear active, does not post-sync, and guidance says retry `issue finish` without editing `active.json` | synthetic active issue, close stub failure | retry trap where synthetic state blocks next closeout | yes | red-required | CLI runtime test |
| tc-011 | S02 | clear failure recovery | negative / recovery | design sequence; existing tests | GitHub close / already-closed followed by active clear failure keeps active, skips post-sync, and reports recovery guidance | clear_active failure after close result | false success or stale derived artifacts after clear failure | yes | covered-existing, update if wording changes | existing application test plus changed guidance inspection |
| tc-012 | S02 | post-sync ownership | acceptance / regression | AC-001; workflow_issue lifecycle-owned sync contract | `close_node` is called with `run_post_sync=False`, lifecycle post-sync runs exactly once after active clear | issue finish success path | double sync or active restoration after finish-owned sync | yes | covered-existing, extend if transition changes path | existing application / CLI runtime tests |
| tc-013 | S03 / S90 | provider / mirror / guidance parity | acceptance / docs | AC-004; provider source-of-truth constraint | provider runtime, dogfooding mirror, CLI/context-pack guidance, and `workflow_issue.md` describe the same finish-only transition and recovery boundary | `cmp` provider vs mirror, docs diff, context-pack / stderr inspection | shipped behavior diverges from dogfooding behavior or docs | yes | inspect-only plus targeted tests | parity inspection and docs spec-review evidence |
| tc-014 | S99 | issue-wide closure | final gate | workflow_issue final quality gate | all required closure ids are represented in report closure ledgers; tests, validate/sync, qa-reviewer, code-reviewer, and spec-reviewer pass | final branch diff and report ledger | local step pass but issue-wide obligation gap remains | yes | manual-required plus command evidence | final quality gate report evidence |

Coverage ledger summary:

- AC-001: tc-005, tc-006, tc-010, tc-012, tc-013, tc-014.
- AC-002: tc-007, tc-008, tc-009, tc-010, tc-011.
- AC-003: tc-001, tc-002, tc-003, tc-004.
- AC-004: tc-013, tc-014.
- EC-001: tc-006.
- EC-002: tc-004, tc-008.
- EC-003: tc-007.
- EC-004: tc-007.
- Non-negotiable constraints: tc-001, tc-002, tc-003, tc-009, tc-012, tc-013.

## Milestones

- M1 Domain authority contract fixed:
  - S01 adds and tests the finish-only token / grants contract without changing application flow.
- M2 Application transition flow fixed:
  - S02 wires local preconditions, persistence, existing authority gate, close, clear, and post-sync in the approved order.
- M3 Shipped/runtime/docs parity confirmed:
  - S03 and S90 keep provider runtime, dogfooding mirror, CLI guidance, context-pack wording, and workflow docs aligned.
- M4 Issue-wide quality gate passed:
  - S99 confirms obligation coverage, validation, reviewer gates, report ledger, and final exit contract.

## Dependency-Derived Execution Order

Implementation order is upstream-to-downstream:

1. Domain authority first.
   - `issue_lifecycle.py` depends on `authority.py` for gate semantics. The finish transition must not be wired until the domain has tests proving that synthetic approval is still rejected and the new token is finish-only.
2. Application transition second.
   - Once helper output and gate behavior are stable, `issue_finish()` can persist the updated active issue entry and then reuse the existing authority gate. This prevents the application layer from inventing one-off approval semantics.
3. Provider / mirror / guidance third.
   - Provider runtime under `src/spec_dock/assets/spec_dock/...` is the source of truth. The dogfooding mirror under `spec-dock/scripts/...` must match after runtime changes, and operator guidance must reflect the new supported transition path.
4. Docs impact and final gates last.
   - Workflow docs and final quality gates depend on knowing the exact CLI behavior, error wording, and test coverage produced by S01-S03.

Step dependency summary:

- S01 depends on approved requirement/design only. It unblocks S02.
- S02 depends on S01 token / helper / gate behavior. It unblocks S03 parity checks and docs wording.
- S03 depends on S01-S02 runtime changes. It unblocks S90 docs resolution and S99 final review.
- S90 depends on concrete behavior from S02-S03. It unblocks final spec review.
- S99 depends on all prior steps and does not introduce product changes except review-requested fixes through bounded follow-up.

## Issue / Step Slicing

### S01 Domain Authority Contract

Behavior goal:

- Introduce a finish-only domain authority contract for `issue_finish_lifecycle_transition` while preserving the safety invariant that `runtime_active_selection` is not lifecycle approval.

Planned contract:

- Scope:
  - Add domain helpers for finish transition promotion record and grants.
  - Update `evaluate_authority_gate()` to allow `issue_finish_lifecycle_transition` only for `required_grant=issue_finish`.
  - Keep all existing stale metadata, wildcard grant, missing grant, and expected revision checks fail-closed.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - `tests/domain_runtime/test_authority.py`
- Forbidden changes:
  - Do not change `issue_lifecycle.py` in S01.
  - Do not relax `runtime_active_selection`.
  - Do not introduce a persistent schema change or new command.
- Closure ids:
  - tc-001, tc-002, tc-003, tc-004.
- Green verification:
  - `python -m unittest tests.domain_runtime.test_authority -v`
- Report evidence destination:
  - `report.md` session log, TDD evidence, Step Contract Closure, Test Contract Closure, Closure Coverage, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate.
- Amendment triggers:
  - A new persistent schema field is required.
  - The token must authorize any lifecycle grant other than `issue_finish`.
  - Existing synthetic rejection cannot be preserved.
  - Existing tests imply a different authority model than the approved design.

#### Delegation Contract

- Delegated role:
  - `dev-coder`
- Input docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - canonical `plan.md` after adoption
  - `spec-dock/docs/workflow_issue.md`
  - `tests/domain_runtime/test_authority.py`
  - provider `authority.py`
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - `tests/domain_runtime/test_authority.py`
- Forbidden changes:
  - Application lifecycle flow, CLI parser, docs, mirror copy, generated active state, broad refactors.
- Acceptance criteria:
  - tc-001 through tc-004 pass and existing domain authority tests still pass.
- Required tests:
  - `python -m unittest tests.domain_runtime.test_authority -v`
- Reviewer focus:
  - `code-reviewer`: authority invariant, exact grants, token restriction, stale record behavior, no broad lifecycle relaxation.
- Output required:
  - changed files, test command/result, closure ids closed, unresolved risks, and `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Stop conditions:
  - Any implementation requires changing approved requirement/design semantics, adding a new command, or allowing synthetic approval to satisfy lifecycle grants.

#### Concrete Test Case Seeds

- `tc-s01-001` negative: synthetic approval remains non-lifecycle
  - Premise: `approved_runtime_promotion_record(node_id="iss-00101")` returns `promotion_decision=runtime_active_selection` and `approved_runtime_grants()` includes downstream lifecycle grants.
  - Operation: call `evaluate_authority_gate()` for `implementation_start`, `issue_ready`, `issue_finish`, and `phase_completion`.
  - Expected result: each call returns `ok=False` and reason `active_synthetic_approval_not_lifecycle_approval`.
  - Failure detection: detects any domain relaxation that lets synthetic active selection close an issue directly.
  - Verification method: red-first / regression test in `tests/domain_runtime/test_authority.py`.
  - Related closure id: tc-001

- `tc-s01-002` acceptance: finish transition helper output is restricted and bound
  - Premise: helper is called with `node_id="iss-00101"`.
  - Operation: inspect returned promotion record and grants.
  - Expected result: promotion decision is `issue_finish_lifecycle_transition`; `source_revision`, `approved_revision`, `approved_hash`, and `reviewer_target_hash` all equal `active:iss-00101`; grants are exactly `review_input`, `planning_input`, `design_baseline`, `issue_finish`.
  - Failure detection: detects helper output that can authorize unrelated lifecycle purposes or is not bound to the active entry.
  - Verification method: new domain test in `tests/domain_runtime/test_authority.py`.
  - Related closure id: tc-002

- `tc-s01-003` acceptance / negative: finish transition token is finish-only
  - Premise: authority is approved, grants are finish transition grants, and promotion record uses `issue_finish_lifecycle_transition`.
  - Operation: evaluate `required_grant=issue_finish`, then evaluate `implementation_start`, `issue_ready`, and `phase_completion`.
  - Expected result: `issue_finish` passes; the other lifecycle grants fail with an explicit finish-token restriction or `missing_required_grant`.
  - Failure detection: detects a token that effectively becomes `main_orchestrator_promotion`.
  - Verification method: new subTest loop in `tests/domain_runtime/test_authority.py`.
  - Related closure id: tc-003

- `tc-s01-004` negative: stale binding remains fail-closed with finish token
  - Premise: finish transition promotion record is for `active:iss-00101`, but expected revision is `active:iss-00999`.
  - Operation: call `evaluate_authority_gate(..., required_grant="issue_finish", expected_revision="active:iss-00999")`.
  - Expected result: failure reason remains `promotion_record_not_bound_to_active_entry` or `promotion_hash_not_bound_to_active_entry`.
  - Failure detection: detects closing a stale or wrong active issue after transition helper introduction.
  - Verification method: extend domain expected-revision test.
  - Related closure id: tc-004

Step closure contract:

- Close condition:
  - Domain helpers exist, gate semantics pass all S01 tests, existing domain tests remain green, and code-reviewer passes.
- Commit/no-op gate:
  - Commit only S01 allowed paths. No-op is valid only if S01 contract is already satisfied and verified with no diff.

### S02 Application Issue Finish Transition Flow

Behavior goal:

- Make `issue finish` create and persist the finish-scoped lifecycle transition after local preconditions and before GitHub close, then reuse the existing `issue_finish` authority gate.

Planned contract:

- Scope:
  - Detect a bound synthetic active issue candidate.
  - Evaluate delegated artifact and Evidence Adoption Ledger preconditions before transition persistence.
  - Persist only the issue entry with finish transition record / grants, leaving initiative and epic entries unchanged.
  - Use `commit_active_state()` / active store snapshot-rollback path or an equivalently existing atomic-ish active-state path.
  - Re-run the existing `issue_finish` authority gate after persistence.
  - Preserve existing close, clear, and lifecycle-owned post-sync behavior.
- Allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` only if existing helper extraction is necessary
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` only if existing active store API is insufficient
  - `tests/cli_runtime/test_issue_lifecycle.py`
- Forbidden changes:
  - Do not edit workflow docs in S02.
  - Do not create a separate promotion command.
  - Do not bypass delegated artifact / EAL gates based on GitHub state.
  - Do not clear active before GitHub close / already-closed confirmation.
- Closure ids:
  - tc-005, tc-006, tc-007, tc-008, tc-009, tc-010, tc-011, tc-012.
- Green verification:
  - `python -m unittest tests.cli_runtime.test_issue_lifecycle -v`
  - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
- Report evidence destination:
  - `report.md` session log, Red/Green/Refactor evidence, discovered tests, closure ledgers, Implementation Delegation Gate, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- Amendment triggers:
  - Transition must occur before local gates.
  - Retry cannot be made safe after GitHub failure.
  - Active store persistence requires a schema or migration not approved in design.
  - `issue finish` must make PR / review / test completion decisions.

#### Delegation Contract

- Delegated role:
  - `dev-coder`
- Input docs:
  - approved requirement/design, adopted canonical plan, `workflow_issue.md`
  - S01 diff / commit
  - provider `issue_lifecycle.py`, `set_active.py`, `active_store.py`, `contracts.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`
- Allowed paths:
  - S02 allowed paths above.
- Forbidden changes:
  - Domain token semantics already fixed by S01, docs, CLI command shape, GitHub gateway broad changes, unrelated lifecycle commands.
- Acceptance criteria:
  - tc-005 through tc-012 pass with close / clear / post-sync ordering proved by tests or existing coverage.
- Required tests:
  - Add or update targeted application / CLI runtime tests for synthetic transition success and failure ordering.
- Reviewer focus:
  - `code-reviewer`: call ordering, rollback semantics, retry behavior, no external mutation before local preconditions, no active clear before close, no double post-sync.
- Output required:
  - changed files, test command/result, whether any existing helper was reused or minimally extracted, closure ids closed, unresolved risks, and ledger note.
- Stop conditions:
  - Need to change public CLI contract, authority model beyond finish-only token, or docs/spec disagreement about precondition ordering.

#### Concrete Test Case Seeds

- `tc-s02-001` acceptance: `issue start` then `issue finish` closes OPEN issue without manual active edit
  - Premise: temp repo has linked issue #101 in `OPEN`; user runs `issue start --id iss-00101`; active issue remains synthetic `runtime_active_selection`.
  - Operation: run `spec-dock issue finish`.
  - Expected result: command succeeds; stdout includes `spec-dock: ok (issue finish)`, `issue=iss-00101`, `active_cleared=true`, `already_closed=false`; gh stub records close; `.agent/active.json` has no active issue; post-sync updates issue status to `done`.
  - Failure detection: detects the original closeout block or missing active clear / sync after transition.
  - Verification method: update `test_issue_start_then_finish_closes_open_issue_and_clears_active` to remove manual `_promote_active_issue_lifecycle()` and assert transition behavior.
  - Related closure id: tc-005

- `tc-s02-002` acceptance: already CLOSED issue clears active from synthetic state
  - Premise: temp repo has active synthetic issue `iss-00101`; gh stub returns issue #101 as `CLOSED`.
  - Operation: run `spec-dock issue finish`.
  - Expected result: command succeeds with `already_closed=true`; active issue is cleared; issue pointer targets `system/active-none/issue`; lifecycle post-sync runs once.
  - Failure detection: detects already-closed state still being blocked by synthetic approval.
  - Verification method: update `test_issue_finish_already_closed_clears_active` to avoid manual lifecycle promotion.
  - Related closure id: tc-006

- `tc-s02-003` negative: EAL or delegated artifact blocker prevents transition persistence and close
  - Premise: active issue is synthetic and bound; report has blocking EAL or `design.md` / `plan.md` has proposed delegated metadata.
  - Operation: run `issue_finish()`.
  - Expected result: command fails with EAL / delegated artifact guidance; active issue promotion record remains `runtime_active_selection`; gh close stub is not called; active clear and post-sync are not called.
  - Failure detection: detects transition happening before local gates or external close despite blocked local evidence.
  - Verification method: extend existing EAL / delegated artifact tests with active manifest before/after or fake store write-call assertions.
  - Related closure id: tc-007

- `tc-s02-004` negative: stale active record is not transitioned
  - Premise: active issue id is `iss-00999`, but synthetic promotion record is bound to `active:iss-00101`.
  - Operation: run `spec-dock issue finish`.
  - Expected result: command fails with stale/binding reason before transition and before gh close; active state remains unchanged.
  - Failure detection: detects transition helper overwriting a stale record and closing the wrong issue.
  - Verification method: extend stale active case in `test_issue_finish_failures_leave_active_unchanged`.
  - Related closure id: tc-008

- `tc-s02-005` negative: transition persistence failure rolls back and avoids GitHub mutation
  - Premise: local gates pass; fake active store raises during `write_active_manifest` or pointer application after snapshot.
  - Operation: call `issue_finish()` with fake close / clear / sync functions recording calls.
  - Expected result: previous active state is restored; close, clear, and post-sync call lists stay empty; error mentions transition / active-state write failure.
  - Failure detection: detects partial transition persistence followed by external mutation.
  - Verification method: application-level test with a failing active store in `tests/cli_runtime/test_issue_lifecycle.py`.
  - Related closure id: tc-009

- `tc-s02-006` negative / retry: GitHub close failure leaves finish-ready active state
  - Premise: synthetic active issue passes local gates; transition persistence succeeds; gh view or close fails.
  - Operation: run `spec-dock issue finish` with failing gh stub.
  - Expected result: command fails; active issue remains; promotion decision is now `issue_finish_lifecycle_transition`; active clear and post-sync do not run; stderr guidance suggests `active show` and retry `issue finish`, not manual `active.json` editing.
  - Failure detection: detects retry trap where persisted state remains synthetic after a close failure.
  - Verification method: extend close failure cases in `test_issue_finish_failures_leave_active_unchanged`.
  - Related closure id: tc-010

- `tc-s02-007` regression: clear failure and post-sync ordering remain correct
  - Premise: close / already-closed succeeds, `clear_active` raises.
  - Operation: call `issue_finish()` with fake close, fake clear failure, fake post-sync recorder.
  - Expected result: close called once; post-sync not called; stderr includes existing active-clear recovery guidance.
  - Failure detection: detects false success or derived artifact sync after active clear failure.
  - Verification method: keep existing `test_issue_finish_clear_active_failure_includes_recovery_guidance`; update only if transition persistence changes expected guidance.
  - Related closure id: tc-011

- `tc-s02-008` regression: lifecycle-owned post-sync still runs once after active clear
  - Premise: close and clear succeed after transition.
  - Operation: call `issue_finish()` with fake close, clear, and post-sync recorders.
  - Expected result: `close_node` receives `run_post_sync=False`; post-sync called exactly once after clear; result carries the post-sync outcome.
  - Failure detection: detects double sync or internal close sync leak.
  - Verification method: existing `test_issue_finish_suppresses_internal_close_sync_and_runs_lifecycle_sync_once`, updated to include transition if needed.
  - Related closure id: tc-012

Step closure contract:

- Close condition:
  - `issue_finish()` success and failure ordering matches design sequence; all S02 tests pass; code-reviewer passes.
- Commit/no-op gate:
  - Commit only S02 allowed paths. No-op is valid only if all S02 closure ids are already satisfied by S01 or existing implementation and verified.

### S03 Provider / Dogfooding Mirror Parity and Runtime Guidance

Behavior goal:

- Keep shipped provider runtime, dogfooding runtime mirror, and runtime-facing guidance aligned after S01-S02.

Planned contract:

- Scope:
  - Mirror provider runtime changes into `spec-dock/scripts/spec_dock_runtime/...` or refresh dogfooding workspace with the established provider-to-consumer path.
  - Confirm provider and dogfooding `authority.py` / `issue_lifecycle.py` match after the runtime change.
  - Confirm context-pack / CLI guidance no longer tells operators to manually edit `active.json` or obtain an unspecified promotion record when the supported internal transition path is available.
  - Identify docs impact that must be resolved in S90.
- Allowed paths:
  - `spec-dock/scripts/spec_dock_runtime/domain/authority.py`
  - `spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - runtime presentation files only if S02 error text requires a presentation-layer change
  - `tests/cli_runtime/test_issue_lifecycle.py` only for mirror / output assertions tightly coupled to runtime guidance
- Forbidden changes:
  - Do not edit canonical issue docs in S03.
  - Do not edit `workflow_issue.md` in S03 if S90 is kept separate.
  - Do not update generated active state by hand as product behavior.
- Closure ids:
  - tc-013.
- Green verification:
  - `cmp -s src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py spec-dock/scripts/spec_dock_runtime/domain/authority.py`
  - `cmp -s src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
- Report evidence destination:
  - `report.md` session log, Step Contract Closure, Closure Coverage, Implementation Delegation Gate, Reviewer Gate Status, Step Commit Gate, Docs Impact Resolution handoff.
- Amendment triggers:
  - Provider and mirror cannot be kept identical.
  - Guidance requires changing workflow semantics beyond approved design.
  - New generated scaffold behavior affects installer/update contracts outside this issue.

#### Delegation Contract

- Delegated role:
  - `dev-coder` for mirror/runtime output parity. If docs edits are needed, route to S90 `doc-writer`.
- Input docs:
  - approved requirement/design/canonical plan, S01-S02 diffs, `workflow_issue.md`, provider and mirror runtime files.
- Allowed paths:
  - S03 allowed paths above.
- Forbidden changes:
  - Canonical issue docs, workflow docs if S90 is separate, unrelated generated assets, active state direct edits.
- Acceptance criteria:
  - tc-013 provider/mirror parity and runtime guidance inspection pass.
- Required tests / inspection:
  - `cmp` provider vs mirror for changed runtime files.
  - targeted unit tests from S01-S02.
  - inspect stderr/context-pack wording touched by S02.
- Reviewer focus:
  - `code-reviewer`: mirror parity, shipped asset behavior, no accidental divergence.
- Output required:
  - changed files, parity commands/results, tests run, docs impact handoff for S90, unresolved risks, ledger note.
- Stop conditions:
  - Mirror differs intentionally without an approved design reason, or docs updates are needed but S90 cannot be executed.

#### Concrete Test Case Seeds

- `tc-s03-001` inspect-only: provider and dogfooding runtime parity
  - Premise: S01-S02 changed provider runtime under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`.
  - Operation: compare changed provider files with mirror files under `spec-dock/scripts/spec_dock_runtime/...`.
  - Expected result: each changed mirrored runtime file is byte-identical or documented with an approved no-op / intentional difference.
  - Failure detection: detects shipped provider and dogfooding behavior divergence.
  - Verification method: `cmp -s` commands recorded in `report.md`.
  - Related closure id: tc-013

- `tc-s03-002` inspect-only / regression: operator guidance points to official retry path
  - Premise: S02 failure paths produce stderr guidance for unsupported synthetic, stale record, transition persistence failure, and close failure after transition.
  - Operation: inspect failing test assertions and runtime guidance text.
  - Expected result: messages do not instruct direct `active.json` editing; close failure after persisted transition recommends `active show` and retry `issue finish`; unsupported/stale state still fails closed with official recovery path.
  - Failure detection: detects replacing the root fix with manual state editing guidance or losing fail-closed recovery instructions.
  - Verification method: assertions in `tests/cli_runtime/test_issue_lifecycle.py` plus code inspection.
  - Related closure id: tc-013

Step closure contract:

- Close condition:
  - Provider/mirror parity is verified, runtime guidance is consistent, and any required docs update is handed to S90.
- Commit/no-op gate:
  - Commit mirror/runtime guidance changes separately from S02 unless orchestrator chooses an approved combined runtime commit. No-op requires parity evidence.

### S90 Docs Impact Resolution

Behavior goal:

- Resolve workflow/guidance docs impact so docs match the new finish-only internal transition without expanding `issue finish` into delivery completion.

Planned contract:

- Scope:
  - Update `spec-dock/docs/workflow_issue.md` to explain that `issue finish` may internally persist an `issue_finish_lifecycle_transition` after local gates.
  - Preserve text stating `issue finish` is lifecycle-only and does not guarantee PR delivery, tests, review, merge readiness, or final delivery.
  - Mention fail-closed conditions and supported recovery path without instructing manual `active.json` edits.
- Allowed paths:
  - `spec-dock/docs/workflow_issue.md`
  - provider-side docs/template source only if the docs file is generated from provider authority and the orchestrator confirms the correct source path
- Forbidden changes:
  - Do not change runtime code or tests in S90.
  - Do not rewrite unrelated workflow sections.
  - Do not edit canonical issue `requirement.md`, `design.md`, `plan.md`, or `report.md` as a worker.
- Closure ids:
  - tc-013.
- Green verification:
  - docs diff inspection
  - `./spec-dock/scripts/spec-dock validate`
  - final `spec-reviewer` docs/spec alignment gate, or step-level `spec-reviewer` if S90 produces docs diff.
- Report evidence destination:
  - Docs Impact Resolution, Step Contract Closure, Closure Coverage, Reviewer Gate Status, Step Commit Gate.
- Amendment triggers:
  - Docs need to define a new command or lifecycle phase.
  - Docs contradict approved requirement/design or imply `issue finish` validates PR/review/tests.
  - Provider-side docs source is ambiguous and cannot be safely updated.

#### Delegation Contract

- Delegated role:
  - `doc-writer`
- Input docs:
  - approved requirement/design/canonical plan, S01-S03 observed behavior, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`.
- Allowed paths:
  - S90 allowed paths above.
- Forbidden changes:
  - Runtime, tests, canonical issue docs, broad documentation restructuring.
- Acceptance criteria:
  - workflow docs describe primary `issue start` -> `issue finish` path, finish-only transition, fail-closed local gates, and lifecycle-only boundary consistently.
- Required verification:
  - docs diff inspection; `./spec-dock/scripts/spec-dock validate`; `spec-reviewer` pass for docs/spec alignment.
- Reviewer focus:
  - `spec-reviewer`: docs match requirement/design/plan and do not add new behavior.
- Output required:
  - changed docs, validation result, reviewer result, unresolved risks, ledger note.
- Stop conditions:
  - Any docs change would modify approved behavior rather than describe it.

#### Concrete Test Case Seeds

- `tc-s90-001` inspect-only: workflow primary path matches runtime transition
  - Premise: S02 implements finish-only internal transition.
  - Operation: inspect `workflow_issue.md` lifecycle bullets around `issue start`, `issue finish`, authority gates, recovery, and lifecycle-only boundary.
  - Expected result: docs state local gates precede transition, transition precedes close/clear, and `issue finish` remains lifecycle-only.
  - Failure detection: detects docs/runtime mismatch or claims that `issue finish` completes PR/review/test delivery.
  - Verification method: docs diff inspection plus `spec-reviewer` docs/spec alignment.
  - Related closure id: tc-013

Step closure contract:

- Close condition:
  - Docs impact is resolved or explicitly proven no-op with inspection evidence; `spec-reviewer` passes docs/spec alignment.
- Commit/no-op gate:
  - Commit docs-only changes separately. No-op requires report evidence explaining why docs already match behavior.

### S99 Final Quality Gate

Behavior goal:

- Confirm issue-wide obligation coverage, integration safety, docs consistency, and final report evidence before PR delivery / merge-preparation handoff.

Planned contract:

- Scope:
  - Run final targeted and broad validation.
  - Ensure every required closure id is closed in `report.md` with evidence.
  - Run final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.
  - Confirm final report ledger and commit/no-op evidence are complete.
- Allowed paths:
  - `report.md` updates by main orchestrator only.
  - Bounded follow-up fixes through S01/S02/S03/S90-style allowed paths if reviewers fail.
- Forbidden changes:
  - Do not use final review to bypass step review.
  - Do not mark issue complete without reviewer passes and report closure evidence.
  - Do not run `issue finish` before PR delivery / merge-preparation evidence required by `workflow_issue.md`.
- Closure ids:
  - tc-014 and confirmation of tc-001 through tc-013.
- Green verification:
  - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v`
  - `python -m unittest discover -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `git diff --check`
  - provider/mirror parity checks from S03
- Report evidence destination:
  - Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Final Commit / external evidence destination.
- Amendment triggers:
  - `qa-reviewer` finds missing high-value tests for a required closure id.
  - `code-reviewer` finds architecture or failure-order regression.
  - `spec-reviewer` finds requirement/design/plan/report/docs mismatch.
  - Final validation fails due to product changes.

#### Delegation Contract

- Delegated role:
  - `qa-reviewer`, `code-reviewer`, `spec-reviewer`; bounded `dev-coder` / `doc-writer` follow-up only if a reviewer fails and the orchestrator delegates the fix.
- Input docs:
  - final requirement/design/plan/report, full branch diff, S01-S90 evidence, workflow docs, tests.
- Allowed paths:
  - Read-only review by reviewers; fixes only through bounded follow-up steps with step-specific allowed paths.
- Forbidden changes:
  - Direct implementation by reviewer, canonical phase promotion, reviewer pass self-claim, broad refactor.
- Acceptance criteria:
  - All three final reviewer gates pass; validation commands pass; report closure ledgers cover every required closure id.
- Required verification:
  - commands listed in S99 green verification plus reviewer outputs.
- Reviewer focus:
  - `qa-reviewer`: test sufficiency and missing integration cases.
  - `code-reviewer`: integrated diff, layering, rollback/retry/failure order, mirror parity.
  - `spec-reviewer`: requirement/design/plan/report/docs alignment.
- Output required:
  - reviewer verdicts, validation results, final risks, report ledger updates, final commit/external evidence destination.
- Stop conditions:
  - Any required validation or reviewer gate fails, is unavailable, denied, waived without explicit risk acceptance, or remains provisional.

#### Concrete Test Case Seeds

- `tc-s99-001` manual-required: closure ledger completeness
  - Premise: S01-S90 are complete or approved no-op.
  - Operation: inspect `report.md` Step Contract Closure, Test Contract Closure, Closure Coverage, Closure Delta, Reviewer Gate Status, and Step Commit Gate.
  - Expected result: tc-001 through tc-014 are pass or justified approved-no-op; no required closure id is missing; no unresolved blocking EAL entry remains.
  - Failure detection: detects implementation success without issue-level evidence closure.
  - Verification method: manual report inspection plus final `spec-reviewer`.
  - Related closure id: tc-014

- `tc-s99-002` manual-required / command: final validation bundle
  - Premise: final branch diff is ready.
  - Operation: run targeted tests, full unittest discover, `validate`, `sync`, `git diff --check`, and parity checks.
  - Expected result: all commands pass or any failure is classified with cause, fix, and re-run evidence.
  - Failure detection: detects cross-module regression missed by targeted tests.
  - Verification method: commands recorded in `report.md`.
  - Related closure id: tc-014

- `tc-s99-003` manual-required: final reviewer triad
  - Premise: final diff, report evidence, and docs are ready.
  - Operation: run `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.
  - Expected result: each reviewer returns fresh pass; any finding is fixed through bounded follow-up and re-reviewed.
  - Failure detection: detects treating implementation worker output or earlier spec reviewer pass as final gate.
  - Verification method: reviewer evidence recorded in final gate sections.
  - Related closure id: tc-014

Step closure contract:

- Close condition:
  - Final validation and reviewer triad pass, report ledger is complete, and remaining risks are either none or non-blocking with evidence.
- Commit/no-op gate:
  - Final commit scope includes product/docs/report changes after final gates as required by workflow. Final commit hash and clean check are recorded as external delivery evidence after commit.

## Test Strategy Mapping

Risk-calibrated test strategy:

- Domain invariant tests:
  - S01 covers token, grants, stale record, and synthetic rejection in `tests/domain_runtime/test_authority.py`.
- Application / CLI runtime tests:
  - S02 covers success from synthetic state, already-closed success, local precondition failures, stale records, persistence failure rollback, close failure retry, clear failure guidance, and post-sync ordering.
- Parity / docs inspection:
  - S03 / S90 close shipped provider vs dogfooding mirror and workflow guidance risks with `cmp`, docs diff, and spec-reviewer evidence.
- Integration / final gates:
  - S99 runs targeted tests first, then full unittest / validate / sync / diff checks and final reviewers.

Red evidence expectations:

- S01 and S02 should start with failing tests for the new token and transition behavior. Existing tests may be reclassified as covered-existing only where they already prove a behavior unchanged by the new flow, such as active clear failure guidance and post-sync suppression.
- S03 / S90 are inspect-only unless runtime guidance assertions need to change.
- S99 is manual-required plus command evidence.

## Review Gates

- Per-step code review:
  - S01, S02, and S03 require `code-reviewer` pass because they touch runtime, tests, or shipped behavior.
- Per-step spec/docs review:
  - S90 requires `spec-reviewer` pass if docs are changed. If docs are no-op, record inspection evidence and have final spec-reviewer confirm.
- Final QA:
  - S99 requires `qa-reviewer` pass for issue-wide obligation coverage and missing high-value tests.
- Final code review:
  - S99 requires issue-wide `code-reviewer` pass over integrated diff.
- Final spec review:
  - S99 requires `spec-reviewer` pass over requirement/design/plan/report/implementation/tests/docs alignment.

Reviewer output does not substitute for implementation worker evidence, and worker output does not substitute for reviewer pass.

## Rollback / Compatibility

- No persistent schema migration is planned.
- New active state uses existing `promotion_record` and `grants` fields.
- Rollback of code is ordinary revert of runtime/test/docs changes.
- Compatibility risk:
  - An active entry already persisted with `issue_finish_lifecycle_transition` is understood by the new runtime. If code is reverted before finish completes, old runtime may not treat the token as a recognized finish-only transition. Record rollback note in `report.md`; recommended operational recovery is to finish with the new runtime or use the official recovery path available at the time, not manual `active.json` editing as standard workflow.
- Failure recovery:
  - Local gate failure leaves synthetic active state unchanged.
  - Transition persistence failure restores previous active state and avoids GitHub mutation.
  - GitHub close failure after transition leaves finish-ready active state for retry.
  - Active clear failure preserves existing guidance and skips post-sync.

## Docs Impact

Docs impact is required.

Affected docs / guidance:

- `spec-dock/docs/workflow_issue.md`:
  - Update authority gate wording to explain finish-only internal transition from synthetic active selection.
  - Keep fail-closed local authority / delegated artifact / EAL gate language.
  - Keep lifecycle-only boundary: no PR delivery, tests, review, merge readiness, or final delivery guarantee.
- CLI failure guidance:
  - Error guidance should reference official recovery / retry path and should not normalize direct `active.json` editing.
- Context-pack / active display:
  - The existing `downstream_block=active_synthetic_approval_not_lifecycle_approval` may still be true for ancestors and non-finish lifecycle purposes. Any wording update must avoid implying full lifecycle approval.

S90 is separated because docs-only work has a different reviewer focus from runtime / tests.

## Final Quality Gate

Final gate inputs:

- S01-S03/S90 committed or approved no-op.
- `report.md` updated by the main orchestrator with observed evidence.
- No unresolved blocking Evidence Adoption Ledger entries.
- Provider/mirror parity evidence recorded.

Required final commands:

```bash
python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle -v
python -m unittest discover -v
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
git diff --check
```

Required final reviewers:

- `qa-reviewer`: pass.
- issue-wide `code-reviewer`: pass.
- final `spec-reviewer`: pass.

Final Exit Contract:

- AC-001 through AC-004 and EC-001 through EC-004 are all closed by required closure ids.
- Synthetic approval rejection remains intact.
- `issue finish` can close/clear from supported synthetic active state through internal finish-only transition.
- Fail-closed cases mutate neither GitHub nor active state unless transition has already been safely persisted for retry.
- Provider and dogfooding mirror behavior match.
- Workflow docs and CLI guidance match runtime behavior.
- Report closure ledgers, reviewer gates, validation commands, and commit/no-op gates are complete.
- No canonical artifact is treated as updated by this delegated draft until the main orchestrator adopts it through `report.md` Evidence Adoption Ledger and a fresh `spec-reviewer` pass.

Amendment triggers:

- Any required closure row is removed, re-scoped, made optional, or has its locked expectation changed.
- The transition token must authorize `implementation_start`, `issue_ready`, or `phase_completion`.
- Local preconditions cannot run before transition persistence.
- Active persistence cannot be made rollback-safe with existing active store contracts.
- The implementation needs a new public command, schema migration, or broader authority model redesign.
- Docs or tests reveal `issue finish` is being used as delivery completion rather than lifecycle closeout.
- Final QA/code/spec reviewer identifies an uncovered required behavior or spec mismatch.

## Plan Blockers

None.

No design gap blocks planning. The only implementation-local choice left by design is whether to call `commit_active_state()` directly from `issue_lifecycle.py` or introduce a small local helper around existing active store / context-pack rendering. That is an implementation detail under the fixed persistence contract and does not block plan authoring.

## Integration Notes for Main Orchestrator

Delegated Draft Evidence:

- role: `spec-dock-implementation-planner`
- role alias requested by orchestrator: `implementation-planner`
- phase: plan
- scope: `iss-00149`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - provider authority / lifecycle runtime
  - dogfooding mirror authority / lifecycle runtime
  - `tests/domain_runtime/test_authority.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`
- draft artifact path:
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00149-issue-finish-synthetic-approval-closeout-bug/discussions/20260601t105346z-disc-implementation-plan-draft.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `not_run`
- integration notes:
  - The canonical plan can adopt the S01/S02/S03/S90/S99 step structure, closure index rows, delegation contracts, concrete test seeds, final exit contract, and amendment triggers.
  - If canonical plan keeps S03 docs impact bundled instead of S90, keep reviewer focus explicit because runtime/code and docs have different gate mappings.
  - The main orchestrator should record adoption in `report.md` Evidence Adoption Ledger and Delegated Draft Evidence, then run fresh `spec-reviewer` for plan.
- rejected portions:
  - none
- blockers:
  - none
- canonical artifacts edited:
  - none
- implementation files edited:
  - none
- tests edited:
  - none
- final authority claimed:
  - no

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
