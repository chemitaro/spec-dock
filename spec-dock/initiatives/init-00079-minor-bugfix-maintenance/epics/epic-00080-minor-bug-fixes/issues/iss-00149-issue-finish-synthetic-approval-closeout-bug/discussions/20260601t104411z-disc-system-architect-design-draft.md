---
created_by_role: system-architect
scope_id: iss-00149
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md
  - spec-dock/active/issue/discussions/20260601t091408z-01-interview-closeout-recovery-path-preference.md
  - spec-dock/active/issue/discussions/20260601t092641z-disc-deep-consultant-lifecycle-transition-decision.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/.agent/active.json
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py
  - spec-dock/scripts/spec_dock_runtime/domain/authority.py
  - spec-dock/scripts/spec_dock_runtime/application/set_active.py
  - spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py
  - tests/domain_runtime/test_authority.py
  - tests/cli_runtime/test_issue_lifecycle.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# System Architect Design Draft: finish-scoped lifecycle transition

Adoption note: this is delegated draft evidence only. The main orchestrator owns canonical integration, Evidence Adoption Ledger updates, fresh reviewer gates, Promotion Records, phase movement, and any user-facing clarification.

## Requirement Coverage

- AC-001 is covered by an internal transition inside `issue_finish()`: when the active issue entry is a bound `runtime_active_selection`, `issue finish` first runs fail-closed local preconditions, then persists an issue-finish-scoped lifecycle promotion record, reloads or reuses the updated entry, and finally re-enters the existing `issue_finish` authority gate before GitHub close, active clear, and lifecycle-owned post-mutation sync.
- AC-002 is covered by preserving fail-closed behavior before GitHub close and active clear when transition preconditions fail. Failure guidance should point to official CLI recovery and artifact/report gates, not manual `spec-dock/.agent/active.json` editing.
- AC-003 is covered by leaving `evaluate_authority_gate()` unchanged for `runtime_active_selection` and adding tests that only the transition-produced finish record opens `issue_finish`.
- AC-004 is covered by updating runtime guidance, `workflow_issue.md`, and context-pack wording so the primary `issue start` -> `issue finish` path no longer contradicts the authority model.
- EC-001 is covered because already-closed GitHub issues use the same transition path before the existing already-closed closeout branch clears active state.
- EC-002 is covered by keeping `expected_revision=active:<entry-id>` binding checks before any transition. A stale promotion record for another issue must remain a pre-close failure.
- EC-003 is covered by running Evidence Adoption Ledger clearance before generating the finish lifecycle record.
- EC-004 is covered by running delegated artifact authority validation before generating the finish lifecycle record.

## Existing Context Findings

- The current active manifest gives initiative, epic, and issue entries `authority=approved`, all runtime grants, and `promotion_record.promotion_decision=runtime_active_selection`. The generated context-pack therefore reports `downstream_block=active_synthetic_approval_not_lifecycle_approval`.
- `set_active.build_active_manifest()` is the source of runtime active selection records. It correctly uses `approved_runtime_grants()` and `approved_runtime_promotion_record()`.
- `domain/authority.py` owns the invariant that `runtime_active_selection` can authorize input grants but cannot authorize lifecycle grants: `implementation_start`, `issue_ready`, `issue_finish`, and `phase_completion`.
- `issue_lifecycle.issue_finish()` currently calls `_require_issue_finish_authority()` before delegated artifact, Evidence Adoption Ledger, GitHub close, active clear, and post-mutation sync. This makes normal active selections fail before any official transition can occur.
- Existing tests already encode the safety invariant and the manual workaround: `_promote_active_issue_lifecycle()` changes `promotion_decision` to `main_orchestrator_promotion`, after which finish succeeds.
- Provider-side runtime files under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` and the dogfooding mirror currently match for the inspected authority, active, and issue lifecycle modules. Implementation should update the provider side first and refresh or maintain mirror parity intentionally.

## Design Decisions

- Add a narrow application-layer transition in `issue_lifecycle.py`, not a broad domain gate relaxation.
- Introduce a dedicated promotion decision token for this transition: `issue_finish_lifecycle_transition`.
- Generate a lifecycle record with `status=approved`, `authority=approved`, `source_revision=active:<issue-id>`, `approved_revision=active:<issue-id>`, `approved_hash=active:<issue-id>`, `reviewer_target_hash=active:<issue-id>`, and `promotion_decision=issue_finish_lifecycle_transition`.
- The record grants only what is required for closeout. Prefer preserving the existing entry grants only if tests confirm no broadening occurs through the token; otherwise narrow the updated issue entry grants to include `issue_finish` plus non-lifecycle input grants. Do not introduce `*`, `grants.*`, or `all`.
- Persist the transition after local preconditions pass and before GitHub close. This makes retry behavior deterministic: a post-persistence GitHub close failure can be retried with an already lifecycle-ready active issue, while active clear remains withheld until close/already-closed succeeds.
- Reuse the existing `issue_finish` authority gate after persistence. The transition is not itself the authorization decision; it produces the state that the existing authorization decision already knows how to evaluate.
- Keep the transition issue-only. Initiative and epic active entries may still show synthetic lifecycle blocks in context-pack; `issue finish` should only require and update the active issue entry unless a future requirement explicitly adds ancestor lifecycle closure semantics.

## Alternatives Considered

- Allow `runtime_active_selection` directly for `issue_finish`: rejected. It would weaken the domain invariant and make active selection equivalent to lifecycle approval for at least one lifecycle grant.
- Add a new explicit command such as `issue approve-finish` or `active promote`: rejected for this issue. The requirement DEC-001 states there is no evidence that an independent human approval event is required, and it would lengthen the primary lifecycle.
- Improve guidance only: rejected as a standalone fix. It would explain the failure but leave the supported transition path missing.
- Generalize auto-transition for all lifecycle grants: rejected. The observed bug is closeout-specific; broader automation would change implementation start, issue ready, and phase completion authority without requirement coverage.
- Mutate `active.json` only after GitHub close succeeds: rejected. A close failure would keep the system in the same unsupported state and make retry semantics less clear; after local preconditions pass, the lifecycle transition is a local authority-state repair, not proof that GitHub close succeeded.

## Boundary / Contract Model

- Domain boundary: `evaluate_authority_gate()` remains the single evaluator of authority, grants, stale records, wildcard grants, and synthetic approval rejection.
- Application boundary: `issue_lifecycle.py` owns the closeout workflow and is the right place to create a finish-scoped transition because it can order local gates, persistence, GitHub close, active clear, and post-mutation sync.
- Infra boundary: `ActiveStateStore` persists `ActiveManifest` and active pointers. The transition should use this store rather than ad hoc JSON writes.
- CLI boundary: `issue finish` takes no new user arguments. User-visible output stays the existing finish result; stderr guidance changes only for fail-closed paths.
- Persistence contract: active state is updated atomically through the active state store snapshot/restore mechanism or an equivalent helper. No manual state editing is part of the supported path.
- Retry contract: before GitHub mutation, failure leaves active state unchanged unless the lifecycle transition was already successfully persisted; after transition persistence, repeated `issue finish` should pass the authority gate and retry close/already-closed plus clear.

## Dependency Analysis

- `issue_lifecycle.issue_finish()` depends on active manifest loading, authority helpers, delegated artifact validation, Evidence Adoption Ledger validation, `close_node()`, `clear_active()`, and `post_mutation_sync()`.
- A small helper such as `_transition_active_issue_for_finish_if_supported()` can depend on `ActiveManifestEntry`, `ActiveManifest`, and `active_state_store.write_active_manifest()` or a new store-level patch helper.
- The helper must not depend on CLI parsing or presentation modules.
- If context-pack needs refreshed wording immediately after transition persistence, the design should prefer the existing active-state commit path that writes both `active.json` and pointers/context-pack. If that path is too tied to full selection rebuild, add a minimal infra/application helper rather than duplicating pointer write logic in `issue_lifecycle.py`.
- Tests should be written against provider-side runtime imports; mirror parity should be checked by the existing scaffold/update or direct comparison pattern.

## Source of Record

- Requirement SoR: `spec-dock/active/issue/requirement.md`, especially DEC-001, AC-001 through AC-004, and EC-001 through EC-004.
- Workflow SoR: `spec-dock/docs/workflow_issue.md` for primary lifecycle and completion boundaries; `spec-dock/docs/workflow_spec_authoring.md` for authority, delegated draft, and reviewer gate semantics.
- Runtime SoR: provider-side `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`.
- Consumer mirror: `spec-dock/scripts/spec_dock_runtime/...` must match the shipped runtime behavior after implementation.
- Generated state SoR: `spec-dock/.agent/active.json`; `spec-dock/active/context-pack.md` is human guidance that mirrors the state.

## Data Flow / Domain Model / Interface Contract

Proposed success flow:

1. `issue_finish()` loads active manifest and active issue entry.
2. If no active issue exists, keep the existing fail-closed recovery guidance.
3. If the active issue is already lifecycle-ready for `issue_finish`, continue without transition.
4. If the active issue has a bound `runtime_active_selection`, run local preconditions first:
   - promotion record fields are complete and bound to `active:<issue-id>`;
   - exact `issue_finish` grant is present;
   - delegated `design.md` / `plan.md` artifacts are approved for `issue_finish`;
   - Evidence Adoption Ledger has no unresolved `blocked` or `stale` entry.
5. If any precondition fails, fail before GitHub close and active clear with official recovery guidance.
6. If all preconditions pass, persist the issue entry with `promotion_decision=issue_finish_lifecycle_transition` and active-bound revision/hash fields.
7. Re-run `_require_issue_finish_authority()` against the updated issue entry.
8. Call `close_node(..., run_post_sync=False)`.
9. Call `clear_active()`.
10. Run lifecycle-owned `post_mutation_sync()`.

Promotion decision token contract:

- `runtime_active_selection`: active selection only; still rejected by all lifecycle grants.
- `issue_finish_lifecycle_transition`: generated only by `issue finish`; valid only when the required grant is `issue_finish` and the record is bound to the active issue.
- `main_orchestrator_promotion` / `fresh_reviewer_promotion`: existing lifecycle/artifact-grade records remain accepted as before.

Failure semantics:

- Precondition failure: no GitHub close, no active clear. Active state stays as it was.
- Transition persistence failure: no GitHub close, no active clear. Active state store rollback should restore previous state.
- GitHub close failure after transition persistence: active is not cleared; retry `issue finish` is valid and should not ask for manual `active.json` edits.
- Active clear failure after successful close/already-closed: keep existing warning guidance; retry can clear later after inspecting active state.

## File / Module Change Plan

```text
.
|-- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|   |-- domain/
|   |   `-- authority.py          # change: token classification helper only if needed; keep synthetic rejection invariant
|   |-- application/
|   |   |-- issue_lifecycle.py    # change: finish-scoped transition helper and issue_finish ordering
|   |   `-- set_active.py         # inspect/possible reuse only; no broad active selection behavior change
|   |-- infra/
|   |   |-- active_store.py       # possible change: active manifest patch/commit helper if current API is insufficient
|   |   `-- contracts.py          # possible no-op; use existing ActiveManifestEntry/ActiveManifest
|   `-- presentation/
|       `-- cli_text.py           # possible guidance/output no-op; errors are currently raised in application
|-- spec-dock/scripts/spec_dock_runtime/
|   `-- ...                       # mirror provider runtime changes intentionally
|-- spec-dock/docs/
|   `-- workflow_issue.md         # change: document internal finish-scoped transition and retained boundaries
|-- tests/
|   |-- domain_runtime/
|   |   `-- test_authority.py     # change: preserve synthetic rejection; add token-specific expectations if domain helper added
|   `-- cli_runtime/
|       `-- test_issue_lifecycle.py # change: normal issue start/set finish succeeds via transition; negative gates stay pre-close
```

## Migration / Compatibility / Rollback

- Compatibility: existing lifecycle-ready active records should continue to finish without mutation other than normal closeout. Existing synthetic active records gain an official transition path.
- No data migration command is required. The transition is lazy and local to `issue finish`.
- Existing manually repaired records using `main_orchestrator_promotion` remain valid.
- Rollback: revert the issue lifecycle transition changes and tests. Active records already changed to `issue_finish_lifecycle_transition` should either still be accepted by `evaluate_authority_gate()` as a non-synthetic decision or require a small rollback note; to reduce rollback risk, keep accepted token handling generic as "not runtime_active_selection" unless future policy enumerates lifecycle tokens.
- Partial failure rollback: rely on active store snapshot/restore for write failures; do not clear active or run post-mutation sync unless close/already-closed and clear have succeeded.

## Observability

- CLI failure messages should distinguish:
  - `runtime_active_selection` rejected because transition preconditions failed;
  - stale or unbound promotion records;
  - delegated artifact gate failure;
  - Evidence Adoption Ledger blocker;
  - GitHub close failure after transition persistence;
  - active clear failure after GitHub close/already-closed.
- The context-pack should continue to show `active_synthetic_approval_not_lifecycle_approval` for ordinary synthetic lifecycle contexts, but after a successful finish transition and before active clear it should be capable of showing issue finish readiness if inspected.
- Test assertions should verify that GitHub close stubs are not called for precondition failures.
- Report evidence should record the transition design adoption decision separately from runtime verification.

## Test Strategy

- Domain tests:
  - Keep `test_active_synthetic_approval_cannot_satisfy_lifecycle_grants` unchanged.
  - If a token helper is introduced, test that `issue_finish_lifecycle_transition` is not accepted by direct synthetic bypass logic and does not authorize non-finish lifecycle grants unless explicitly intended.
  - Keep stale hash/revision and active binding tests.
- Application tests:
  - Add a unit-level test that synthetic active issue plus clear local gates persists the finish transition before close.
  - Add a test that delegated artifact failure blocks before transition persistence and before close.
  - Add a test that unresolved EAL blocks before transition persistence and before close.
  - Add a test that stale promotion record for another issue blocks before transition persistence and before close.
  - Add a test that GitHub close failure after transition persistence leaves active selected and retryable.
- CLI/runtime tests:
  - Replace or split `test_issue_finish_blocks_normal_active_set_synthetic_approval_before_close`: the success case should cover normal synthetic active state; negative cases should cover unsupported transition conditions.
  - Cover already-closed GitHub issue with synthetic active state and active clear success.
  - Preserve existing tests for lifecycle-owned post-mutation sync running once after active clear.
- Docs inspection:
  - Verify `workflow_issue.md` describes the internal finish transition, retained non-guarantees, and official recovery path.
- Verification commands:
  - `python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_issue_lifecycle`
  - broader `python -m unittest discover -v` if runtime and scaffold mirrors are both touched.

## ADR Candidates

- No ADR is required for this issue-local repair.
- ADR candidate only if implementation discovers a need to generalize lifecycle transitions beyond `issue_finish`, enumerate all promotion decision tokens globally, or redefine active selection grants.

## Risks

- Over-broad token acceptance could accidentally authorize `implementation_start`, `issue_ready`, or `phase_completion`.
- Persisting the transition before local preconditions are complete would convert blocked or stale evidence into lifecycle-ready state.
- Persisting the transition after GitHub close would preserve the existing retry trap on close failure.
- Updating provider runtime without mirror parity would make dogfooding behavior diverge from shipped behavior.
- Context-pack may still show initiative/epic synthetic downstream blocks after issue-only transition. That is acceptable for this issue if `issue finish` only gates on the issue entry, but documentation should avoid implying all ancestor lifecycle states were promoted.

## Requirement Clarification Requests

- none.

調査で解ける未確定事項:

- Whether active store needs a small patch helper or can reuse `commit_active_state()` cleanly from `set_active.py`.
- Exact wording of CLI recovery guidance after the transition exists.
- Whether context-pack should display a specific `issue_finish_lifecycle_transition` readiness detail.

ユーザー判断が必要な未確定事項:

- none at design-draft time. DEC-001 already fixes the internal auto-transition direction and excludes broader lifecycle auto-promotion.

## Integration Notes for Main Orchestrator

Delegated draft evidence:

- role: `system-architect`
- phase: requirement/design
- scope: `iss-00149`
- source artifacts read: see frontmatter `source_paths`
- draft artifact path: `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00149-issue-finish-synthetic-approval-closeout-bug/discussions/20260601t104411z-disc-system-architect-design-draft.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets: `spec-dock/active/issue/design.md`, `spec-dock/active/issue/report.md`
- diff_guard_result: `not_run`
- integration notes: integrate only after post-run diff guard and main-orchestrator adoption ledger entry; run a fresh `spec-reviewer` on canonical `design.md` after integration.
- rejected portions: none.
- blockers: none.
- canonical artifacts edited: none.
- final authority claimed: no.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
