---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00143
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/reference_naming.md
  - spec-dock/templates/issue/plan.md
  - spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00143-manage-external-git-worktrees/discussions/rules.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - src/spec_dock/assets/spec_dock/docs/reference_worktree.md
  - spec-dock/docs/reference_worktree.md
  - tests/cli_runtime/test_worktree.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
report_evidence_destination: spec-dock/active/issue/report.md Evidence Adoption Ledger and Delegated Draft Evidence
adoption_ledger_note: Main orchestrator must decide adoption before canonical plan integration; this draft claims no authority.
---

# Draft Plan: iss-00143 Manage External Git Worktrees

## Plan Summary

This draft converts approved `requirement.md` and approved `design.md` into an issue-plan-ready execution contract for extending `worktree list` / `show` / `remove` from SpecDock-managed worktrees to all Git linked worktrees in the same repository.

Recommended step shape:

- S01 contract/model diagnostics: add classification fields and preserve `managed: bool`.
- S02 root-optional inventory: make `list` / `show` / `remove` work without valid `SPEC_DOCK_WORKTREE_ROOT`, while keeping `create` root-required.
- S03 external remove blockers: allow external/unmanaged linked worktree removal and keep hard blockers non-bypassable.
- S04 Git-first remove and target-only cleanup: no cleanup on Git failure; cleanup only the resolved Git-record target, covering directory, symlink, broken symlink, file, unsupported type, and race/failure behavior.
- S05 presentation/CLI text/help: expose new diagnostics and remove managed-only wording.
- S90 docs parity: update provider docs and dogfooding docs.
- S99 final quality gate: validation, targeted/full tests, QA/code/spec reviewers, final report/commit gates.

Assumption: canonical plan integration will preserve the approved design field names `managed_classification_available`, `classification_reason`, and `origin`.

## Requirement / Design Traceability

Approved issue requirement source:

- `status=approved`, `ID=iss-00143`, `last_updated=2026-05-30`.
- AC-001: all linked worktrees in list JSON.
- AC-002: root missing does not block list/show/remove.
- AC-003: create remains root-required.
- AC-004: external worktree remove, target directory cleanup, no branch deletion.
- AC-005: main/current/bare/stale hard blockers.
- AC-006: `managed` boolean compatibility plus classification diagnostics.
- AC-007: provider docs / dogfooding docs parity.
- EC-001: ambiguous target rejects with candidates.
- EC-002: branch target rejects.
- EC-003: Git remove failure means no filesystem cleanup.
- EC-004: invalid root is classification diagnostic, not availability blocker.
- EC-005: symlink / containment risk follows fixed target-only cleanup guard.

Approved issue design source:

- D-001: Git worktree records are source of truth for `list` / `show` / `remove`.
- D-002: add `managed_classification_available`, `classification_reason`, and `origin`; keep `managed: bool`.
- D-003: remove `unmanaged` from remove blockers; keep main/current/path_missing/record_missing/bare hard blockers.
- D-004: Git-first remove; cleanup only after Git success; target-only cleanup via `FilesystemGateway.remove_target(path)`-equivalent.
- D-005: invalid root is non-fatal for list/show/remove and appears as classification diagnostic.

Parent epic traceability:

- E-RQ-011 / E-RQ-012 and E-AC-012 / E-AC-013 are amended by this issue.
- `worktree create` central root contract, branch non-deletion, no prune/repair, no Codex Desktop lifecycle implementation, and provider-side source of truth remain unchanged.

## Milestones

- M1 contract and inventory foundation:
  - Close classification field compatibility and root optional inventory.
  - Candidate steps: S01, S02.
- M2 removal behavior:
  - Close external remove, hard blockers, Git failure, and target-only cleanup.
  - Candidate steps: S03, S04.
- M3 command surface and docs:
  - Close CLI JSON/text/help wording and docs parity.
  - Candidate steps: S05, S90.
- M4 final gates:
  - Close issue-wide verification, reviewer gates, validation, and report/commit evidence.
  - Candidate step: S99.

## Dependency-Derived Execution Order

Source dependency order from design:

1. `application/contracts.py` first because `WorktreeRecordView` is consumed by application and presentation.
2. `application/worktree.py` next because it owns inventory classification, target resolution, remove blockers, Git-first remove, and cleanup orchestration.
3. `application/ports.py` and `infra/fs_cli.py` with remove behavior because cleanup semantics require a filesystem port change.
4. `presentation/cli_text.py`, `commands/worktree.py`, and `cli/parser.py` after behavior fields exist.
5. tests should be added with each behavior slice, not only at the end.
6. docs and dogfooding parity belong after runtime behavior is stable.
7. final gates run after all implementation/docs slices are closed.

Step dependency graph:

- S01 -> S02, S03, S05.
- S02 -> S03 and S05.
- S03 -> S04.
- S04 -> S90.
- S05 -> S90.
- S90 -> S99.

## Issue / Step Slicing

### Spec-Locked Closure Index Candidate

| ID | Step | Type | Spec links | Locked expectation | Evidence level |
|---|---|---|---|---|---|
| tc-001 | S01 | compatibility | AC-006, D-002 | `managed` remains boolean and new classification fields are present in record JSON/text source model | red-required |
| tc-002 | S02 | acceptance | AC-001, AC-002, EC-004, D-001, D-005 | `list --json` includes all linked worktrees and root missing/blank/invalid does not fail list/show/remove availability | red-required |
| tc-003 | S02 | regression | AC-003 | `worktree create` still fails without valid `SPEC_DOCK_WORKTREE_ROOT` and creates no side effects | covered-existing plus targeted regression |
| tc-004 | S03 | acceptance | AC-004, D-003 | external/unmanaged linked worktree is removable; `unmanaged` is diagnostic only, not a blocker | red-required |
| tc-005 | S03 | safety | AC-005 | main/current/bare/path_missing/record_missing remain non-bypassable even with `--force` | red-required |
| tc-006 | S03 | regression | EC-001, EC-002 | ambiguous targets and branch-only targets reject before Git remove | covered-existing plus targeted regression |
| tc-007 | S04 | safety | EC-003, D-004 | Git remove failure returns surfaced error and performs no filesystem cleanup | red-required |
| tc-008 | S04 | cleanup | AC-004, EC-005, D-004 | cleanup is target-only for remaining directory, symlink, broken symlink, and regular file | red-required |
| tc-009 | S04 | cleanup-negative | EC-005, D-004 | unsupported file type, permission/race/lstat/unlink/rmtree failure returns `post_remove_cleanup_failed` after Git success and does not clean parent/root/namespace | red-required |
| tc-010 | S05 | output | AC-001, AC-002, AC-006 | JSON/text expose classification diagnostics and no managed-only/root-required wording remains for list/show/remove | red-required |
| tc-011 | S90 | docs | AC-007 | provider docs and dogfooding docs describe root optional list/show/remove, create root required, external remove, cleanup, no branch deletion, no Codex-specific lifecycle | inspect-only |
| tc-012 | S99 | final-gate | AC-001..AC-007, EC-001..EC-005 | targeted tests, validation, sync decision, report closure, and final QA/code/spec reviews are complete | manual-required |

### S01 - Contract Fields and Compatibility

- Behavior goal:
  - Make classification diagnostics explicit without breaking existing `managed` consumers.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Add `managed_classification_available: bool`, `classification_reason: str`, and `origin: str` to `WorktreeRecordView`.
  - Use design-approved values: `root_valid`, `root_missing`, `root_blank`, `root_invalid`, `namespace_symlink`; `spec_dock_managed`, `external`, `classification_unavailable`.
  - Keep `managed` boolean and existing field names stable.
- Concrete test seeds:
  - `tc-s01-001`: instantiate/render managed, external, and unavailable records; assert `managed` stays boolean and diagnostic fields serialize.
  - `tc-s01-002`: existing tests that construct `WorktreeRecordView` must be updated intentionally, not hidden by default values unless reviewer accepts compatibility rationale.
- Delegation contract:
  - delegated role: `dev-coder`.
  - allowed paths: contracts and worktree tests only.
  - forbidden changes: behavior changes in `worktree.py`, docs, CLI wording.
  - reviewer focus: `code-reviewer`.
  - required output: changed files, failing-first or characterization evidence, targeted test result, `Ledger Note`.
- Closure ids: `tc-001`.

### S02 - Root-Optional List / Show / Remove Inventory

- Behavior goal:
  - `list` / `show` / `remove` build inventory from Git records even when root is missing, blank, relative, file, broken symlink, or namespace symlink.
- Target files:
  - `application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Split create-only root requirement from optional classification context.
  - Git records are read before classification.
  - Missing/blank/invalid root produces `managed=false`, `managed_classification_available=false`, and `origin=classification_unavailable`.
  - Valid root produces `origin=spec_dock_managed` or `origin=external`.
  - `worktree create` still calls the strict root resolver.
- Concrete test seeds:
  - `tc-s02-001`: no `SPEC_DOCK_WORKTREE_ROOT`; `list --json` and `show <external> --json` succeed and include classification unavailable.
  - `tc-s02-002`: invalid root variants no longer return `worktree_root_required` / `invalid_worktree_root` for list/show/remove inventory; they emit diagnostics.
  - `tc-s02-003`: create with missing/blank/invalid root still fails and creates no branch/worktree/bootstrap side effect.
- Delegation contract:
  - delegated role: `dev-coder`.
  - allowed paths: `application/worktree.py`, focused tests.
  - forbidden changes: remove execution/cleanup behavior except whatever is needed to pass inventory construction for remove preflight.
  - reviewer focus: `code-reviewer`.
  - required verification: targeted `tests/cli_runtime/test_worktree.py` cases.
- Closure ids: `tc-002`, `tc-003`.

### S03 - External Remove and Hard Blockers

- Behavior goal:
  - External linked worktrees are removable while main/current/bare/stale/record-missing safety blockers stay non-bypassable.
- Target files:
  - `application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Remove `unmanaged` from `_remove_blockers()` / `_non_bypassable_remove_blockers()` as a blocker.
  - Preserve diagnostics so external worktrees remain identifiable.
  - Re-read Git records immediately before removal and reject `record_missing`.
  - Keep branch-only target and ambiguous target rejection before Git remove.
  - Keep `branch_deleted=false`.
- Concrete test seeds:
  - `tc-s03-001`: external worktree under a non-root path removes successfully with `--json`; branch remains.
  - `tc-s03-002`: main/current/bare/path_missing/record_missing fail with `remove_blocked` even with `--force`; Git remove and filesystem cleanup are not called.
  - `tc-s03-003`: branch-only target and ambiguous basename still reject before Git remove.
- Delegation contract:
  - delegated role: `dev-coder`.
  - allowed paths: `application/worktree.py`, focused tests.
  - forbidden changes: filesystem cleanup implementation and docs.
  - reviewer focus: `code-reviewer`.
  - required output: blocker matrix, test evidence, unresolved Git portability risks.
- Closure ids: `tc-004`, `tc-005`, `tc-006`.

### S04 - Git-First Target-Only Cleanup

- Behavior goal:
  - After successful Git remove, cleanup only the resolved target path, including non-directory leftovers, without following symlinks or deleting parent/root/namespace.
- Target files:
  - `application/ports.py`
  - `application/worktree.py`
  - `infra/fs_cli.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Replace `path_exists` + `remove_tree` cleanup with a target-only cleanup port such as `remove_target(path)`.
  - Existence detection must use lstat-style behavior so broken symlinks can be removed.
  - Directory: remove tree.
  - Symlink/broken symlink: unlink symlink itself; never follow target.
  - Regular file: unlink file.
  - Unsupported file type, lstat/unlink/rmtree failure, and race are surfaced as `post_remove_cleanup_failed` after Git success.
  - If Git remove fails, no filesystem cleanup is attempted.
- Concrete test seeds:
  - `tc-s04-001`: fake Git remove failure with a filesystem spy confirms no cleanup call.
  - `tc-s04-002`: leftover directory cleanup removes only target and preserves parent/root/namespace.
  - `tc-s04-003`: leftover symlink and broken symlink cleanup unlinks the symlink while preserving symlink target or missing target state.
  - `tc-s04-004`: leftover regular file is unlinked.
  - `tc-s04-005`: unsupported file type or simulated lstat/unlink/rmtree race returns `post_remove_cleanup_failed` with `removed_record=true` and `removed_directory=false`.
- Delegation contract:
  - delegated role: `dev-coder`.
  - allowed paths: ports, application remove orchestration, fs infra, focused tests.
  - forbidden changes: broad filesystem helper refactors, parent directory cleanup, branch deletion, `git worktree prune`.
  - reviewer focus: `code-reviewer`.
  - stop conditions: platform cannot represent a fixture safely; cleanup boundary requires design change; Git failure path cannot be observed.
- Closure ids: `tc-007`, `tc-008`, `tc-009`.

### S05 - Presentation, CLI Text, and Help

- Behavior goal:
  - Command output and help reflect all-linked-worktree management and classification diagnostics.
- Target files:
  - `presentation/cli_text.py`
  - `commands/worktree.py`
  - `cli/parser.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - JSON payload includes classification fields on list/show/remove success and errors with embedded worktree/candidates.
  - Text output includes concise classification diagnostics without hiding existing `managed`, `removable`, and `remove_blockers`.
  - Help/target wording says `worktree id, absolute path, or directory basename`, not managed-only.
  - Error JSON for remove blockers and cleanup failures remains machine-readable.
- Concrete test seeds:
  - `tc-s05-001`: `list --json`, `show --json`, and remove error JSON contain classification fields.
  - `tc-s05-002`: `worktree remove --help` no longer says "Managed worktree id".
  - `tc-s05-003`: text list/show output shows origin/classification reason and remains scan-friendly.
- Delegation contract:
  - delegated role: `dev-coder`.
  - allowed paths: presentation, command argument help, parser help, focused tests.
  - forbidden changes: application behavior, docs.
  - reviewer focus: `code-reviewer`.
- Closure ids: `tc-010`.

### S90 - Docs Impact Resolution / Docs Refresh

- Behavior goal:
  - Shipped docs and dogfooding docs match the new runtime contract.
- Target files:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - optionally `src/spec_dock/assets/spec_dock/docs/guide.md` and `spec-dock/docs/guide.md` only if stale wording is found.
- Planned contract:
  - State that `worktree create` requires `SPEC_DOCK_WORKTREE_ROOT`.
  - State that `list` / `show` / `remove` work without root and use Git records as source of truth.
  - Document classification diagnostics and `managed` compatibility.
  - Document external remove, Git-first behavior, target-only cleanup, no branch deletion, no prune/repair, no orphan cleanup.
  - Keep Codex Desktop as background/non-scope; no Handoff/env/metadata lifecycle claims.
- Concrete inspection seeds:
  - `tc-s90-001`: provider `reference_worktree.md` has no stale "list/show/remove require root" or "unmanaged cannot be removed" wording.
  - `tc-s90-002`: dogfooding `spec-dock/docs/reference_worktree.md` matches provider docs on user-visible contract.
  - `tc-s90-003`: docs mention branch deletion remains out of scope and `branch_deleted=false`.
- Delegation contract:
  - delegated role: `doc-writer`.
  - allowed paths: docs paths listed above only.
  - forbidden changes: runtime code, tests, canonical spec docs, unrelated guide sections.
  - reviewer focus: `spec-reviewer` docs/spec alignment.
  - required output: docs changed, docs inspection result, stale wording scan, `Ledger Note`.
- Closure ids: `tc-011`.

### S99 - Final Quality Gate

- Behavior goal:
  - Confirm issue-wide implementation, docs, tests, report evidence, and reviewers are complete before any issue finish / PR merge-prep decision.
- Target files:
  - no product files by default; report updates are main-orchestrator-owned.
- Required gates:
  - Run targeted runtime tests for worktree behavior, at minimum `python -m unittest tests.cli_runtime.test_worktree -v`.
  - Run broader relevant baseline: `python -m unittest discover -v` if feasible; otherwise document why targeted-only is accepted.
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Decide whether `./spec-dock/scripts/spec-dock sync` is required and record result or no-op rationale.
  - Final `qa-reviewer`: test sufficiency and missing integration tests.
  - Final issue-wide `code-reviewer`: integrated diff, layering, cleanup safety, compatibility.
  - Final `spec-reviewer`: requirement/design/plan/report/docs/implementation alignment.
  - Final commit gate and post-commit clean check are orchestrator-owned.
- Concrete evidence seeds:
  - `tc-s99-001`: closure coverage ledger maps every required `tc-001`..`tc-012` to pass or approved-no-op evidence.
  - `tc-s99-002`: final reviewer states are fresh `passed`.
  - `tc-s99-003`: no forbidden side effects: no branch deletion, no prune/repair, no Codex-specific lifecycle, no canonical docs edited by delegated workers.
- Delegation contract:
  - delegated role: no implementation worker by default; use `qa-reviewer`, `code-reviewer`, and `spec-reviewer` as review roles after implementation/docs are integrated.
  - allowed paths: report evidence updates by main orchestrator only; reviewer outputs are evidence.
  - forbidden changes: product changes during final gate unless a reviewer finding triggers a bounded follow-up step and re-review.
- Closure ids: `tc-012`.

## Test Strategy Mapping

- Root optional list/show/remove:
  - AC-001, AC-002, EC-004 -> `tc-002`, S02.
  - Include missing, blank, relative, file, broken symlink, and namespace symlink/root-invalid classification unavailable cases.
- Create root required:
  - AC-003 -> `tc-003`, S02.
  - Preserve existing no-side-effect tests and add regression if S02 touches root resolver boundaries.
- Classification fields:
  - AC-006 -> `tc-001`, `tc-010`, S01/S05.
  - Assert both structured model and JSON payload.
- External remove allowed:
  - AC-004 -> `tc-004`, S03.
  - Assert Git record removed, target path cleaned when leftover exists, branch remains.
- Hard blockers:
  - AC-005 -> `tc-005`, S03.
  - main/current/bare/path_missing/record_missing must be non-bypassable with `--force`.
- Git failure no cleanup:
  - EC-003 -> `tc-007`, S04.
  - Use fake filesystem spy where Git remove raises.
- Target-only cleanup:
  - AC-004, EC-005 -> `tc-008`, `tc-009`, S04.
  - Cover directory, symlink, broken symlink, regular file, unsupported type, and race/failure.
- Docs parity:
  - AC-007 -> `tc-011`, S90.
- Validation/final gates:
  - all AC/EC -> `tc-012`, S99.

## Review Gates

- Per implementation step S01..S05:
  - Primary worker: `dev-coder`.
  - Reviewer: `code-reviewer`.
  - Required before commit: targeted tests pass or failure is fixed; report evidence records Red/Green/Refactor, Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, and Step Commit Gate.
- Docs step S90:
  - Primary worker: `doc-writer`.
  - Reviewer: `spec-reviewer` for docs/spec alignment.
  - Required before commit: stale wording scan, provider/dogfooding parity inspection, docs closure evidence.
- Final step S99:
  - Reviewers: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`.
  - Fresh `passed` is required; unavailable/denied/provisional/waived does not count as pass unless the main orchestrator records explicit risk acceptance where workflow allows it.
- Delegated worker work is not a reviewer pass and must not be recorded as such.

## Rollback / Compatibility

- Compatibility:
  - Preserve `managed: bool`.
  - Add classification fields instead of renaming existing JSON fields.
  - Preserve stable `id`, `path`, `basename`, `branch`, `main`, `current`, `path_exists`, `record_exists`, `removable`, and `remove_blockers`.
  - Preserve `branch_deleted=false`.
  - Preserve `worktree create` root requirement and no-side-effect failure behavior.
- Rollback:
  - Each step should be one commit boundary, enabling rollback by reverting the failed step commit.
  - S04 filesystem cleanup is the highest-risk step and should not be mixed with presentation/docs changes.
  - If target-only cleanup uncovers a design conflict, stop and route to plan/design amendment rather than weakening cleanup guards ad hoc.
- Non-scope guardrails:
  - No branch deletion.
  - No `git worktree prune` / repair.
  - No orphan directory cleanup for paths absent from Git records.
  - No Codex Desktop Handoff, environment setup, metadata cleanup, or `$CODEX_HOME/worktrees` special detection.

## Docs Impact

Docs update is required, not optional.

Required docs destinations:

- Provider source: `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`.
- Dogfooding parity: `spec-dock/docs/reference_worktree.md`.

Potential docs inspection destinations:

- `src/spec_dock/assets/spec_dock/docs/guide.md`.
- `spec-dock/docs/guide.md`.

Docs must remove stale statements that:

- `list` / `show` / `remove` require `SPEC_DOCK_WORKTREE_ROOT`.
- `remove` targets only SpecDock managed namespace worktrees.
- `unmanaged` is a non-bypassable remove blocker.
- cleanup is only directory-tree cleanup.

Docs must add or preserve statements that:

- `worktree create` root requirement remains.
- external linked worktrees can be inspected and removed.
- classification unavailable is diagnostic, not a failure.
- Git remove failure prevents cleanup.
- target-only cleanup may unlink symlink/broken symlink/file or remove directory, and never deletes parent/root/namespace.
- branch deletion, prune/repair, orphan cleanup, and Codex-specific lifecycle remain out of scope.

## Final Quality Gate

Minimum final commands/evidence for canonical plan:

- `python -m unittest tests.cli_runtime.test_worktree -v`
- `python -m unittest discover -v` or documented targeted-only rationale if full suite is impractical.
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync` if scaffold/docs changes require regenerated dogfooding state; otherwise record no-op rationale.
- `git status --short` after final commit for external delivery evidence.

Minimum final reviewers:

- `qa-reviewer`: confirms closure/test sufficiency and integration test needs.
- `code-reviewer`: confirms issue-wide diff, layering, filesystem safety, Git semantics, and compatibility.
- `spec-reviewer`: confirms requirement/design/plan/report/docs/implementation alignment.

Final report evidence destination:

- `Spec Interpretation / Decision Ledger` for material decisions or `No material interpretation changes`.
- `Evidence Adoption Ledger` for this draft if adopted.
- `Delegated Draft Evidence` for this draft metadata.
- `Workflow Delegation Consent`.
- `Implementation Delegation Gate` / `Delegated Worker Evidence`.
- `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Closure Delta`.
- `Reviewer Gate Status`, `Final QA Gate`, `Final Code Review Gate`, `Final Spec Review Gate`, `Step Commit Gate`, `Final Commit`.

## Plan Blockers

none.

Risks to keep visible, but not blockers:

- Existing target `discussions/` contained untracked discussion files before this draft creation, so post-run diff guard adoption may need orchestrator baseline context.
- Git behavior around locked worktrees can vary by Git version; tests should accept Git's force semantics without weakening hard SpecDock blockers.
- Filesystem fixtures for unsupported file types and race conditions may need fake filesystem gateway coverage rather than platform-specific real files.
- `sync` necessity after provider docs changes is an orchestrator decision; docs parity must still be verified.

## Integration Notes for Main Orchestrator

Delegated Draft Evidence block:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00143`
- source artifacts read:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - parent epic requirement/design/plan
  - issue plan/workflow docs
  - relevant runtime files, docs, and tests listed in frontmatter
- draft artifact path: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00143-manage-external-git-worktrees/discussions/20260530t120052z-draft-plan-external-worktree-management.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes:
  - Integrate only through main-orchestrator canonical `plan.md` edit.
  - Record adoption in canonical `report.md` Evidence Adoption Ledger and Delegated Draft Evidence.
  - Fresh `spec-reviewer` pass remains required after canonical plan integration.
- rejected portions: none.
- blockers: none.
- canonical artifacts edited: `none`
- final authority claimed: `no`

Leaf evidence used: none. This draft is based on direct source reads only.

Forbidden actions avoided:

- No canonical `requirement.md`, `design.md`, `plan.md`, or `report.md` edits.
- No implementation, tests, package/config, `.agents`, `.codex`, `.github`, or secrets edits.
- No GitHub mutation, phase promotion, reviewer-pass claim, implementation-readiness claim, or issue completion claim.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
