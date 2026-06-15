---
created_by_role: system-architect
scope_id: iss-00186
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260615t152809z-interview-issue-execution-hardening-scope-boundary.md
  - spec-dock/active/issue/discussions/20260613t084318z-disc-issue-execution-skill-update-direction.md
  - spec-dock/active/issue/discussions/20260613t082454z-research-issue-execution-step-gate-analysis.md
  - spec-dock/active/issue/discussions/20260613t082641z-research-skill-workflow-spine-policy-analysis.md
  - spec-dock/active/issue/discussions/20260613t083027z-research-deep-consultant-skill-policy-findings.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
  - src/spec_dock/assets/spec_dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending_parent_verification
---

# Draft Design: Issue Execution Step Gate Hardening

This is delegated design evidence for `iss-00186`. It is not canonical authority, does not claim reviewer pass, and does not mark the issue ready for implementation. The main orchestrator must verify the diff, adopt or reject claims in `report.md`, and rewrite accepted content into canonical `design.md` before phase promotion.

## 1. Requirement Coverage

The requirement evidence and fresh `spec-reviewer` pass establish Option B as the intended scope:

- Strengthen provider-side `spec-dock-issue-execution` as a compact first-read gate spine.
- Add only necessary exact semantics to provider-side `workflow_issue.md`.
- Update tests/assertions for required wording and existing fragment preservation.
- Validate the dogfooding mirror after provider-side changes.
- Inspect `authoring/issue-plan.md`, templates, and `/execute-issue` prompt for alignment, fixing only severe contradictions in this issue or recording follow-up.

Coverage mapping:

| Requirement / AC | Design response |
|---|---|
| AC-001 First-read single-step gate | Put the single current step loop near the top of `spec-dock-issue-execution/SKILL.md`. |
| AC-002 Delegated mutation gate | Keep normal file mutation routed to `dev-coder` / `doc-writer`; parent mutation requires `Parent Implementation Exception`. |
| AC-003 Reviewer fail and follow-up gate | Skill and workflow wording must make reviewer fail route to bounded delegated follow-up plus fresh re-review. |
| AC-004 Completion terminology boundary | `workflow_issue.md` owns exact semantics for `approved-local-execution`, `degraded mode`, `waived`, and final commit boundaries. |
| AC-005 Context-surface ownership compliance | Apply accepted ADR: skills own compact spine, docs own detail semantics, templates own scaffold/evidence slots. |
| AC-006 Provider and dogfooding validation | Change provider source first, then inspect/update dogfooding mirror and run validate/sync evidence as planned. |
| AC-007 Evidence adoption and planning readiness | Record this draft and prior research adoption in `report.md` before canonical integration. |

## 2. Existing Context Findings

Current provider `spec-dock-issue-execution/SKILL.md` already points to `workflow_issue.md`, requires approved / reviewer-pass planning artifacts, treats `plan.md` as an executable contract, routes runtime/tests/scaffold behavior to `dev-coder`, routes shipped docs/templates/skills/workflow text to `doc-writer`, and requires bounded delegated follow-up after review failure.

The gap is not missing policy. The gap is that the first-read surface does not top-load the operational loop:

```text
single current step
-> required verification
-> fresh step reviewer pass
-> step commit or approved-no-op
-> post-commit clean check
-> next step unlock
```

`workflow_issue.md` already contains much of the detail, including parent orchestration ownership, reviewer gate mapping, `1 implementation step = 1 review scope = 1 commit`, post-commit clean checks, `approved-no-op`, final quality gates, and completion evidence. However, the exact "step result approval" and final-commit-not-catch-up semantics are still easier to miss than they should be.

`authoring/issue-plan.md` is already the detail surface for executable step schema and delegation contracts. It should not be turned into the runtime execution authority, but it is a necessary alignment-check target because poor step schema can reintroduce batching.

`tests/unit/infra/test_init_update.py` asserts exact fragments in the provider skill and workflow doc. The safest design is additive wording that preserves existing fragments while adding new required fragments.

## 3. Design Decisions

### D-001: Adopt Option B as a bounded text-surface hardening design

Use provider skill + minimal workflow exact semantics + targeted assertion update + dogfooding mirror validation as the core implementation path. Do not expand the issue into broad template governance, prompt redesign, empirical harness, runtime enforcement, or agent definition changes.

### D-002: Keep skill compact but operationally executable

Add a short "Execution Gate Spine" or equivalent section near the top of the skill. It should state:

- Work on exactly one current implementation step.
- Do not start the next step's implementation, delegation, review, or commit until the current step closes.
- Current step closure requires planned verification, fresh step reviewer pass, Step Commit Gate, and post-commit clean check.
- File mutation normally goes through `dev-coder` or `doc-writer`.
- Parent direct mutation requires a pre-recorded `Parent Implementation Exception`.
- Reviewer failure requires bounded delegated follow-up and fresh re-review.
- Unavailable / denied / host conflict / waiver states are not required gate passes.

This is intentionally a spine, not a copied completion matrix.

### D-003: Put exact terminology semantics in `workflow_issue.md`

Use `workflow_issue.md` for detailed definitions:

- `Step Result Approval`: the condition that unlocks the next step.
- `approved-local-execution`: valid only when `Parent Implementation Exception` is recorded before parent mutation.
- `degraded mode`: availability/status context only; not reviewer pass, implementation readiness, or final quality pass.
- `waived`: explicit risk acceptance only; not a reviewer pass.
- `final commit`: final report/delivery evidence closure; not a catch-up implementation commit for earlier uncommitted steps.

### D-004: Treat templates and prompt as alignment-check surfaces

Inspect `authoring/issue-plan.md`, provider templates, and `/execute-issue` prompt for severe contradictions against Option B. Fix only contradictions that would directly undermine this issue's gates, such as mutating implementation step examples that normalize `N/A` delegated roles or bundled multi-step reporting as success. Broader scaffold cleanup belongs to follow-up, especially where it overlaps `iss-00166`.

### D-005: Preserve provider authority and mirror as validation

Provider-side files are source of truth. Dogfooding mirror files are validation surfaces. The implementation plan should modify provider source first, then update or inspect the installed mirror and record evidence.

## 4. Alternatives Considered

| Alternative | Outcome | Reason |
|---|---|---|
| Skill-only minimal reminder | Rejected as too narrow for Option B | It improves first-read behavior but leaves `Step Result Approval`, final commit, and exception terminology less exact. |
| Copy full `workflow_issue.md` policy into skill | Rejected | It creates skill bloat and two policy authorities, contrary to the accepted ADR. |
| Broad template / prompt / empirical harness sweep | Rejected for this issue | It overlaps existing template-surface work and makes the issue too large for per-step review/commit discipline. |
| Runtime enforcement / CLI validation | Deferred | The current issue targets agent-facing context surfaces, not runtime lifecycle implementation. |

## 5. Boundary / Contract Model

Surface responsibility table:

| Surface | Owns | Must not own in this issue |
|---|---|---|
| `spec-dock-issue-execution/SKILL.md` | First-read execution gate spine, stop conditions, route map, exit gate reminders | Full lifecycle policy, field schema, completion matrix |
| `workflow_issue.md` | Lifecycle detail, reviewer/delegation/commit/completion semantics, hard cases | Hidden mandatory first action that the skill omits |
| `authoring/issue-plan.md` | Executable plan schema, field semantics, delegation contract detail | Runtime execution authority or duplicate completion policy |
| Provider templates | Scaffold shape, evidence slots, examples | Compliance authority, phase promotion authority |
| `/execute-issue` prompt | Entry prompt alignment with skill/workflow gates | Separate source of truth or broad prompt redesign |
| Tests | Installed asset preservation and required wording assertions | Behavioral proof of empirical agent compliance |
| Dogfooding mirror | Installed-surface validation | Provider authority |
| `report.md` | Evidence Adoption Ledger and actual verification evidence | Silent adoption of delegated draft without main-orchestrator decision |

## 6. Dependency Analysis

Primary dependency order:

1. Canonical requirement and accepted ADR constrain the design.
2. Provider skill change depends on `workflow_issue.md` as detailed policy but must not copy it wholesale.
3. `workflow_issue.md` exact semantics should be written before finalizing test assertions for new fragments.
4. Test updates depend on final wording in provider skill/workflow docs.
5. Dogfooding mirror validation depends on provider-side source changes.
6. Alignment check can run after core wording decisions and should not block unless it finds a severe contradiction.

Target files:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
tests/unit/infra/test_init_update.py
.agents/skills/spec-dock-issue-execution/SKILL.md
spec-dock/docs/workflow_issue.md
```

Alignment-check targets:

```text
src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
src/spec_dock/assets/spec_dock/templates/issue/plan.md
src/spec_dock/assets/spec_dock/templates/issue/report.md
src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md
```

Non-targets:

```text
runtime CLI behavior
runtime validation / enforcement
agent definition expansion
global role registry
GitHub workflow state
empirical compliance harness
past issue report backfill
broad template rewrite
canonical docs by delegated author
```

## 7. Source of Record

Canonical adoption remains main-orchestrator-owned:

- `spec-dock/active/issue/design.md` is the intended canonical design target.
- `spec-dock/active/issue/report.md` is the intended evidence adoption and delegated draft tracking target.
- This draft remains `adoption_status: unreviewed` until adopted by the main orchestrator.
- Fresh `spec-reviewer` pass is still required after canonical design integration.

The source requirement revision used here is `spec-dock/active/issue/requirement.md` with `最終更新: "2026-06-16"` and Option B adopted by the interview artifact.

## 8. Data Flow / Domain Model / Interface Contract

No runtime domain model or API contract changes are proposed. The contract is an agent-facing text-surface contract.

Sequence / flow:

```text
Main orchestrator reads approved requirement/design/plan
-> skill first-read gate checks readiness and current step
-> current step is delegated to dev-coder/doc-writer unless Parent Implementation Exception is recorded
-> worker returns changed files, verification, risks, and ledger note/no-material-decision note
-> orchestrator integrates evidence into report
-> fresh step reviewer pass is obtained
-> step commit or approved-no-op evidence is recorded
-> post-commit clean check confirms no unintended carryover
-> next step unlocks
-> final quality gates run independently; final review does not replace per-step review
```

Expected skill interface is short imperative text, not structured machine validation. Expected workflow interface is detailed policy prose. Expected test interface is fragment assertion and installed asset parity/preservation checks.

## 9. File / Module Change Plan

Recommended implementation slices:

1. Skill spine update:
   - Add a compact execution gate section near the top of provider `SKILL.md`.
   - Preserve existing phrases asserted by tests.
   - Avoid embedding field tables or long policy.

2. Workflow exact semantics update:
   - Add or refine definitions for `Step Result Approval`, `approved-local-execution`, `degraded mode`, `waived`, and final commit boundary.
   - Keep lifecycle detail in `workflow_issue.md`.

3. Test assertion update:
   - Add assertions for the new critical phrases.
   - Preserve existing assertion fragments unless intentional wording changes require minimal updates.
   - Prefer asserting core contract terms over long paragraphs.

4. Alignment check:
   - Inspect `authoring/issue-plan.md`, templates, and prompt for severe contradictions.
   - Apply only small fixes that directly prevent gate inversion, or record follow-up.

5. Dogfooding mirror validation:
   - Sync/update mirror as the workflow requires.
   - Inspect `.agents/skills/spec-dock-issue-execution/SKILL.md` and `spec-dock/docs/workflow_issue.md`.
   - Run `./spec-dock/scripts/spec-dock validate` and, if required, `./spec-dock/scripts/spec-dock sync`.

## 10. Migration / Compatibility / Rollback

Migration impact is limited to shipped text assets and tests. Existing consumer repositories receive the updated skill/workflow text through `spec-dock update`.

Compatibility:

- Existing skill references to `workflow_issue.md` remain valid.
- Existing test fragments should remain valid if wording is additive.
- Existing templates should remain scaffold surfaces, not authorities.

Rollback:

- Revert provider skill/workflow wording and matching test assertion changes together.
- Re-run dogfooding mirror update/inspection after rollback.
- If alignment fixes were made and found too broad, revert them or convert to follow-up issue evidence.

## 11. Observability

Observability is evidence-led, not runtime telemetry:

- `report.md` Evidence Adoption Ledger records adoption of this draft and prior research/interview artifacts.
- `report.md` Spec Interpretation / Decision Ledger records any scope decisions found during alignment check.
- Test output records provider asset wording and installed asset preservation.
- Dogfooding mirror inspection records provider/mirror consistency.
- `validate` / `sync` output records scaffold health.

## 12. Test Strategy

Primary checks:

- Focused unit test lane around `tests/unit/infra/test_init_update.py`.
- Targeted fragment assertions for:
  - single current step
  - required verification before next step
  - fresh step reviewer pass
  - Step Commit Gate
  - post-commit clean check
  - final commit is not catch-up implementation commit
  - unavailable / denied / host conflict / waiver are not reviewer passes
- Preservation assertions for existing required fragments:
  - `spec-dock/docs/workflow_issue.md as the source of truth`
  - `concise reminder for issue execution`
  - `Route runtime, tests, and scaffold behavior to `dev-coder``
  - `Route shipped docs, templates, skills, and workflow text to `doc-writer``
  - `bounded delegated follow-up`
  - `Parent direct fixes require a documented Parent Implementation Exception`
- Dogfooding mirror inspection of installed skill/workflow files.
- `./spec-dock/scripts/spec-dock validate`.

Optional checks:

- `./spec-dock/scripts/spec-dock sync` if workflow requires generated projection refresh.
- `git diff --check` for whitespace safety.

Empirical agent compliance testing is useful but should remain follow-up unless the main orchestrator deliberately expands scope.

## 13. ADR Candidates

No new ADR is recommended.

The existing accepted ADR `Skill Docs Template Context Surface Ownership` already decides the durable architecture:

- Skills own operational workflow spine.
- Docs own concepts, field meanings, policy details, references, and hard cases.
- Templates own scaffolds, evidence slots, and examples.
- Templates are not compliance authorities.

This issue applies that ADR to issue execution step gates. A new ADR would be needed only if implementation changes the durable ownership model, introduces runtime enforcement as policy authority, or makes templates compliance authorities.

## 14. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Skill bloat | Drift from `workflow_issue.md` and lower readability | Keep skill to first action, stop conditions, routing, and exit gates. |
| Docs-only hidden workflow | Agent still misses hard gates | Top-load the gate loop in skill. |
| Assertion brittleness | Small wording changes break tests | Preserve existing fragments and add focused new fragments. |
| Template scope creep | Issue expands into scaffold governance | Fix only severe contradictions; record follow-up for broader cleanup. |
| Terminology inversion | `approved-local-execution` or `degraded mode` read as success | Define exact exception/availability semantics in `workflow_issue.md`. |
| Final commit misuse | Earlier uncommitted step diffs are bundled late | State final commit is not a catch-up implementation commit. |
| Mirror-only edits | Shipped source is not actually changed | Provider source first; mirror validation second. |

## 15. Requirement Clarification Requests

Blocking clarification requests: none.

Non-blocking design questions for main orchestrator:

- Should `approved-local-execution` be retained with stricter semantics, or renamed in a later issue to make the exception nature more visible?
- If alignment check finds prompt/template wording that is problematic but not severe, should it be deferred to `iss-00166` or a new follow-up?
- Should empirical compliance harness become a follow-up after this issue dogfoods the updated surfaces?

## 16. Integration Notes for Main Orchestrator

Recommended adoption path:

1. Record this draft in `report.md` Delegated Draft Evidence with `adoption_status: unreviewed` until reviewed.
2. Add an Evidence Adoption Ledger entry for adopted / partially adopted / deferred claims.
3. Integrate the surface responsibility table, decision list, target/non-target list, flow, test strategy, risks, rollback, and open questions into canonical `design.md`.
4. Keep canonical wording stricter than this draft where needed, but avoid promoting this draft itself to accepted authority.
5. Run fresh `spec-reviewer` on canonical `design.md` before moving to plan.

Forbidden actions avoided by this draft:

- No canonical docs were edited.
- No implementation files, tests, config, agent instructions, workflow files, GitHub state, or secrets were edited.
- No phase promotion, reviewer pass, issue readiness, or implementation readiness is claimed.
- No runtime enforcement or role registry expansion is proposed as in-scope implementation.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
