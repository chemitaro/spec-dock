---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00137
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/plan.md
  - spec-dock/templates/issue/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - tests/cli_runtime/test_worktree.py
  - src/spec_dock/assets/spec_dock/docs/reference_worktree.md
  - spec-dock/docs/reference_worktree.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: "Main orchestrator decides adoption in canonical report.md Evidence Adoption Ledger."
---

# Delegated Plan Draft: iss-00137 Worktree list/show/remove

## 1. Plan Summary

This draft proposes an executable issue plan for `iss-00137` only. It is based on reviewer-passed requirement/design evidence recorded in `report.md` and the current runtime shape where only `worktree create` is implemented.

Primary implementation order:

1. Establish shared application contracts, ports, and helper model for inventory, target resolution, remove diagnostics, expected errors, and filesystem cleanup.
2. Add CLI parser / command / presentation contracts for `list`, `show`, and `remove`, including `--json` success and expected failure payloads.
3. Implement inventory and show behavior: root validation, Git record inventory, stable id derivation, managed classification, removable diagnostics, target resolver, and text output.
4. Implement remove behavior: non-bypassable guards, pre-Git containment, Git-first remove / force semantics, post-Git cleanup containment, and partial failure output.
5. Refresh provider and dogfooding docs for the new command family.
6. Close with targeted runtime tests, `validate` / `sync`, per-step reviews, and final QA / code / spec gates.

Assumptions:

- `spec-dock/active/issue/plan.md` was unavailable on the first read attempt, then was observed later in the same run as a canonical draft; the shipped issue plan template was also read from `spec-dock/templates/issue/plan.md`.
- If the orchestrator uses this delegated draft, reconcile it against the current canonical plan draft rather than overwriting canonical content blindly.
- No design gap was found that blocks drafting. This draft does not claim implementation readiness or reviewer approval.

## 2. Requirement / Design Traceability

Requirement trace:

- AC-001, AC-002: `worktree list` text / JSON inventory with id, path, branch, managed, current/main, path existence, removable summary, and remove blockers.
- AC-003, AC-004, AC-005: `show` target resolution for stable id / absolute path / basename, ambiguity failure with candidates, and branch-only target rejection.
- AC-006, AC-007: clean managed remove deletes Git record and remaining individual directory, leaves local branch, and returns JSON result with `branch_deleted=false`.
- AC-008, AC-009: dirty / locked / untracked default remove fails via Git; `--force` maps to Git force semantics when non-bypassable guards pass.
- AC-010: main, current, and unmanaged worktrees remain refused with or without `--force`.
- AC-011: missing / invalid `SPEC_DOCK_WORKTREE_ROOT` fail-fast before Git listing, Git remove, or filesystem cleanup.
- AC-012: stale diagnostics are observable through `path_exists`, `record_exists`, and `remove_blockers`; no prune / repair / orphan cleanup.
- AC-013: no `worktree delete` alias.
- EC-001..EC-005: remove revalidation, unmanaged/current/main guards, ambiguity failure, and stale diagnostic-only behavior.

Design trace:

- D-001 command family maps to parser / command specs under existing `worktree` subcommand.
- D-002 Git-first remove maps to `GitGateway.remove_worktree`, post-success `FilesystemGateway.remove_tree`, and no pre-clean.
- D-003 JSON expected failure contract maps to command-layer handling for `WorktreeCommandError`, not global dispatch fallback.
- D-004 target resolution maps to accepted target forms: stable id, absolute path, directory basename; branch names are not target forms.
- D-005 stable id maps to `main`, managed suffix from `<repo-basename>-<suffix>`, full basename fallback, unmanaged basename, and deterministic `~2`, `~3` disambiguators.
- Interface contract maps to `WorktreeListRequest`, `WorktreeShowRequest`, `WorktreeRemoveRequest`, `WorktreeRecordView`, result dataclasses, and `WorktreeCommandError`.
- Directory / file change plan maps to `application/contracts.py`, `application/ports.py`, `application/worktree.py`, `commands/worktree.py`, `cli/parser.py`, `cli/bootstrap.py`, `infra/git_cli.py`, optional `infra/fs_cli.py`, `presentation/cli_text.py`, `tests/cli_runtime/test_worktree.py`, provider docs, and dogfooding docs.

## 3. Milestones

- M1 contracts and shared helper model:
  - Close application request/result/error dataclasses, `UseCases` additions, `GitGateway.remove_worktree`, `FilesystemGateway`, root validation reuse, inventory helper, stable id helper, target resolver, and guard result model.
  - Evidence: unit-style tests or direct application tests for root validation ordering, id derivation, classification, and expected error shape.
- M2 command and output surface:
  - Close parser bindings, command arg dataclasses, `--json` / `--force` routing, text renderers, JSON success payloads, and expected JSON failure payloads.
  - Evidence: help/parser tests, JSON error tests that prove expected failures do not fall through to dispatch text stderr.
- M3 inventory and show:
  - Close `list` and `show` behavior against temp Git repos with main, managed, unmanaged, duplicate basename/id, branch-only target, ambiguous target, and stale diagnostic cases.
  - Evidence: CLI runtime tests and JSON payload assertions.
- M4 remove:
  - Close managed-only remove, revalidation, non-bypassable guards, pre-Git containment, Git-first default failure, `--force`, post-Git cleanup, branch preservation, and partial cleanup failure behavior.
  - Evidence: destructive temp repo tests with Git record, filesystem, and branch assertions.
- M5 docs and dogfooding parity:
  - Close provider reference update and dogfooding reference refresh / inspection.
  - Evidence: docs diff, command help alignment, and spec-reviewer docs/spec alignment gate.
- M6 final quality gate:
  - Close targeted tests, broader relevant test run, `validate`, `sync`, final QA review, issue-wide code review, final spec review, final report ledgers, step commits, and clean check.

## 4. Dependency-Derived Execution Order

Design dependency order is:

1. `central root validation -> Git worktree list/main record discovery -> namespace derivation -> managed classification -> target resolution/remove guard`.
2. Contracts and ports must exist before command and bootstrap wiring can call use cases.
3. Inventory helpers must exist before `show` and `remove` can reuse stable ids, classification, and blocker calculation.
4. Parser / presentation can be introduced with expected-error handling once contracts are fixed.
5. `remove` must depend on inventory and target resolution, then add Git remove and filesystem cleanup.
6. Docs and dogfooding refresh must happen after command behavior is fixed enough to describe accurately.
7. Final quality gates run after all behavior slices and docs are closed.

Recommended step order:

- S01 contracts / ports / shared helper model.
- S02 parser / commands / presentation JSON and text contract.
- S03 inventory list behavior.
- S04 show target resolution behavior.
- S05 remove guard, Git-first execution, force, and cleanup.
- S90 docs impact resolution and dogfooding reference refresh.
- S99 final quality gate.

## 5. Issue / Step Slicing

### S01 contracts / ports / shared worktree helper model

- Behavior goal:
  - Runtime has typed worktree list/show/remove contracts and shared pure helper behavior that later CLI steps can call without duplicating classification and target resolution rules.
- Depends on:
  - Reviewer-passed requirement/design evidence.
- Unblocks:
  - S02, S03, S04, S05.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - optional `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Add `WorktreeListRequest`, `WorktreeShowRequest`, `WorktreeRemoveRequest`, `WorktreeRecordView`, `WorktreeListResult`, `WorktreeShowResult`, `WorktreeRemoveResult`, and `WorktreeCommandError`.
  - Add `worktree_list`, `worktree_show`, and `worktree_remove` callables to `UseCases`.
  - Add `GitGateway.remove_worktree(repo_root, *, path, force)`.
  - Add `FilesystemGateway.path_exists(path)` and `FilesystemGateway.remove_tree(path)`.
  - Reuse or extract root validation so `list/show/remove` match `worktree create` fail-fast behavior before Git/filesystem side effects.
  - Shared helpers must implement canonical path normalization, main record discovery, namespace derivation, managed classification, stable id assignment, `remove_blockers`, and target resolution.
- Red / alternative evidence:
  - `red-required`: direct application tests or CLI-runtime tests that fail before new contracts/helpers exist.
- Delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: target files above only.
  - forbidden changes: canonical docs, package/config, unrelated command behavior, persistent SpecDock registry for worktrees, branch deletion, prune/repair.
  - reviewer focus: `code-reviewer`.
  - output required: changed files, tests run, helper contract summary, unresolved risks, `Ledger Note` or `No material implementation decisions beyond the approved plan.`
- Concrete test seeds:
  - `tc-s01-001` acceptance: root validation is shared by list/show/remove.
    - Premise: `SPEC_DOCK_WORKTREE_ROOT` is missing or invalid.
    - Operation: call new use cases through minimal fake ports.
    - Expected result: command/use case returns expected root error before Git list/remove and filesystem cleanup calls.
    - Failure detection: catches accidental Git/filesystem side effects before env validation.
    - Verification method: application-level fake-port test or focused runtime test.
    - Related closure id: AC-011.
  - `tc-s01-002` acceptance: stable ids are unique and deterministic.
    - Premise: Git records include main, managed `<repo>-wt1`, managed non-prefix basename, unmanaged basename, and duplicate ids.
    - Operation: build inventory through helper.
    - Expected result: ids follow `main`, suffix/full basename, and deterministic `~2`, `~3`.
    - Failure detection: catches unstable agent target ids and ambiguous JSON records.
    - Verification method: helper-level test or CLI JSON assertion.
    - Related closure id: AC-002, AC-003.
  - `tc-s01-003` negative: non-bypassable blockers are calculated before remove.
    - Premise: records include unmanaged, main, current, missing path, bare, and clean managed cases.
    - Operation: build `WorktreeRecordView`.
    - Expected result: `remove_blockers` contains canonical codes and `removable` is false iff blockers exist.
    - Failure detection: catches `--force` accidentally bypassing SpecDock-managed guards.
    - Verification method: helper-level test or runtime JSON assertion.
    - Related closure id: AC-010, AC-012, EC-002, EC-003.
- Step closure contract:
  - Close when helper model and ports exist, tests prove root validation ordering / id algorithm / classification / blocker calculation, and `code-reviewer` passes.

### S02 parser / command / presentation JSON and text contracts

- Behavior goal:
  - CLI exposes `worktree list [--json]`, `worktree show <target> [--json]`, and `worktree remove <target> [--force] [--json]`, with expected failures rendered as JSON when requested.
- Depends on:
  - S01 contracts.
- Unblocks:
  - S03, S04, S05 runtime behavior.
- Target files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Add arg dataclasses and command specs for list/show/remove.
  - Add parser subcommands under existing `worktree`; do not add `delete`.
  - Add `--json` for list/show/remove and `--force` only for remove.
  - Expected failures under `--json` return stdout payload with `status: "error"`, `command`, `error`, `warnings`, and non-zero exit.
  - Error codes include `worktree_root_required`, `invalid_worktree_root`, `target_not_found`, `ambiguous_target`, `unsupported_branch_target`, `remove_blocked`, `git_worktree_list_failed`, `git_worktree_remove_failed`, and `post_remove_cleanup_failed`.
  - Unexpected exceptions may keep existing dispatch fallback.
- Red / alternative evidence:
  - `red-required`: parser/help and JSON error tests before implementation.
- Delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: target files above only.
  - forbidden changes: global dispatch fallback rewrite unless narrowly required; `worktree delete` alias; unrelated JSON schemas.
  - reviewer focus: `code-reviewer`.
  - output required: changed files, parser/help evidence, JSON success/error evidence, unresolved risks, ledger note.
- Concrete test seeds:
  - `tc-s02-001` acceptance: parser exposes list/show/remove and options.
    - Premise: runtime script is available.
    - Operation: run `worktree --help`, `worktree list --help`, `worktree show --help`, `worktree remove --help`.
    - Expected result: list/show/remove exist; list/show/remove expose `--json`; remove exposes `--force`.
    - Failure detection: catches missing command wiring or wrong option placement.
    - Verification method: CLI runtime help tests.
    - Related closure id: AC-001, AC-003, AC-006, AC-013.
  - `tc-s02-002` negative: delete alias is absent.
    - Premise: runtime parser is available.
    - Operation: run `spec-dock worktree delete <target>`.
    - Expected result: parser rejects command; no use case runs.
    - Failure detection: catches accidental deprecated alias.
    - Verification method: CLI runtime parser test.
    - Related closure id: AC-013.
  - `tc-s02-003` negative JSON: expected failures are JSON, not dispatch text.
    - Premise: invalid root or not-found target with `--json`.
    - Operation: run `worktree list --json` or `worktree show missing --json`.
    - Expected result: non-zero exit, stdout JSON `status=error`, correct `error.code`, stderr does not contain only fallback traceback-like text.
    - Failure detection: catches `RuntimeError` escaping command-layer expected-error handling.
    - Verification method: CLI runtime JSON assertion.
    - Related closure id: AC-011, AC-003, D-003.
- Step closure contract:
  - Close when parser/presentation contracts are observable and expected JSON failures are covered, with `code-reviewer` pass.

### S03 inventory list behavior

- Behavior goal:
  - `worktree list` and `worktree list --json` return a stable inventory across Git worktree records with managed/unmanaged classification and removable diagnostics.
- Depends on:
  - S01, S02.
- Unblocks:
  - S04 target resolution and S05 remove revalidation.
- Target files:
  - `application/worktree.py`
  - `presentation/cli_text.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Validate root first.
  - Call `GitGateway.worktree_list`.
  - Discover main worktree record and derive namespace from main basename.
  - Classify records as managed if canonical path is under `$SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/`.
  - Set `main=true` for main record and `current=true` for current `ports.repo_root` canonical path.
  - Compute `path_exists`, `record_exists`, `remove_blockers`, and `removable`.
  - Text output includes id/path/branch/managed/removable summary.
  - JSON output includes all required record fields.
- Red / alternative evidence:
  - `red-required`: temp Git repo runtime tests.
- Delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: target files above and S01 contract files only if test-discovered adjustments are required.
  - forbidden changes: remove implementation beyond diagnostic hint; prune/repair; active pointer or sync mutation.
  - reviewer focus: `code-reviewer`.
- Concrete test seeds:
  - `tc-s03-001` acceptance: list text includes core inventory.
    - Premise: temp repo has main, one managed linked worktree, and one unmanaged linked worktree.
    - Operation: run `worktree list`.
    - Expected result: exit 0; output exposes ids, paths, branches, managed/unmanaged, and removable summary.
    - Failure detection: catches text renderer missing key operator fields.
    - Verification method: CLI runtime text assertion.
    - Related closure id: AC-001.
  - `tc-s03-002` acceptance: list JSON includes required fields.
    - Premise: same as `tc-s03-001`.
    - Operation: run `worktree list --json`.
    - Expected result: `status=ok`, `worktrees[]` records contain `id`, `path`, `basename`, `branch`, `managed`, `main`, `current`, `path_exists`, `record_exists`, `removable`, `remove_blockers`.
    - Failure detection: catches agent contract gaps.
    - Verification method: JSON payload assertion.
    - Related closure id: AC-002.
  - `tc-s03-003` diagnostic: stale/missing path is diagnostic only.
    - Premise: Git record exists while path is missing or otherwise diagnosable as stale.
    - Operation: run `worktree list --json`.
    - Expected result: record remains visible with diagnostic blockers; command does not prune/repair.
    - Failure detection: catches accidental mutation from read-only inventory.
    - Verification method: JSON and `git worktree list --porcelain` / filesystem assertion.
    - Related closure id: AC-012, EC-005.
- Step closure contract:
  - Close when list text/JSON and diagnostic-only behavior are covered and `code-reviewer` passes.

### S04 show target resolution behavior

- Behavior goal:
  - `worktree show <target>` resolves stable id, absolute path, or directory basename to exactly one current inventory record and returns detail; ambiguous and unsupported branch-only targets fail without side effects.
- Depends on:
  - S03.
- Unblocks:
  - S05 remove target selection.
- Target files:
  - `application/worktree.py`
  - `commands/worktree.py`
  - `presentation/cli_text.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Accepted target forms are only current JSON `id`, absolute path, and directory basename.
  - A single record matched by multiple forms is not ambiguous.
  - A target matching multiple records is `ambiguous_target` and includes `candidates`.
  - A target matching only a branch name is `unsupported_branch_target` or target-not-found per implemented classifier, but must not resolve to a record.
  - Text output presents single record detail; JSON output returns `status=ok`, `target`, `worktree`, and warnings.
- Red / alternative evidence:
  - `red-required`: target resolver runtime tests.
- Delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: target files above.
  - forbidden changes: branch-name target support; implicit partial matching not specified by design.
  - reviewer focus: `code-reviewer`.
- Concrete test seeds:
  - `tc-s04-001` acceptance: id/path/basename resolve to the same record.
    - Premise: `worktree list --json` returns a managed worktree id.
    - Operation: run `show <id> --json`, `show <absolute-path> --json`, and `show <basename> --json`.
    - Expected result: all three return the same `worktree.path` and id.
    - Failure detection: catches inconsistent agent target forms.
    - Verification method: CLI runtime JSON assertion.
    - Related closure id: AC-003.
  - `tc-s04-002` negative: ambiguous target fails with candidates.
    - Premise: inventory contains records where a target string matches more than one accepted form/record.
    - Operation: run `show <target> --json`.
    - Expected result: non-zero exit, `status=error`, `error.code=ambiguous_target`, candidates present.
    - Failure detection: catches destructive or misleading target selection.
    - Verification method: CLI runtime JSON assertion.
    - Related closure id: AC-004, EC-004.
  - `tc-s04-003` negative: branch-only target is unsupported.
    - Premise: a branch name exists only as branch metadata and not as id/path/basename.
    - Operation: run `show <branch-name> --json`.
    - Expected result: non-zero target error; branch is not resolved.
    - Failure detection: catches accidental branch-name targeting.
    - Verification method: CLI runtime JSON assertion.
    - Related closure id: AC-005.
- Step closure contract:
  - Close when resolver success/failure behavior is covered and `code-reviewer` passes.

### S05 remove Git-first semantics, containment, cleanup, and force behavior

- Behavior goal:
  - `worktree remove <target>` removes only managed, non-main, non-current worktrees through Git-first semantics, performs post-Git individual directory cleanup only after success, and never deletes branches.
- Depends on:
  - S03, S04.
- Target files:
  - `application/contracts.py`
  - `application/ports.py`
  - `application/worktree.py`
  - `cli/bootstrap.py`
  - `infra/git_cli.py`
  - optional `infra/fs_cli.py`
  - `commands/worktree.py`
  - `presentation/cli_text.py`
  - `tests/cli_runtime/test_worktree.py`
- Planned contract:
  - Revalidate current inventory at remove time; `list/show removable=true` remains only a planning hint.
  - Pre-Git guard refuses unmanaged, main, current, missing record/path as specified, namespace parent, repo root/main path, and symlink-resolved namespace escape.
  - `--force` bypasses only Git dirty/locked/untracked refusal by passing `force=True` to Git; it does not bypass SpecDock guards.
  - Default remove calls `git worktree remove <path>`.
  - Force remove calls `git worktree remove --force <path>`.
  - If Git remove fails, return `git_worktree_remove_failed`; do not call filesystem cleanup.
  - If Git succeeds, repeat containment before filesystem cleanup.
  - If target directory remains, remove only the individual managed worktree directory.
  - Cleanup failure returns/raises expected `post_remove_cleanup_failed` with `removed_record=true`, `removed_directory=false`; it must not claim full success.
  - Result JSON includes `target`, `resolved_target`, `removed_record`, `removed_directory`, `branch_deleted=false`, and warnings. `resolved_target` includes at least id/path/basename/branch/managed/main/current.
- Red / alternative evidence:
  - `red-required`: destructive temp repo tests; no live checkout mutation.
- Delegation contract:
  - delegated role: `dev-coder`
  - allowed paths: target files above.
  - forbidden changes: branch deletion, prune/repair, orphan directory cleanup outside the resolved managed individual directory, active pointer mutation, GitHub mutation, provider docs in this step.
  - reviewer focus: `code-reviewer`.
  - stop conditions: inability to create hermetic temp Git worktrees; containment ambiguity; need to delete outside managed namespace; new requirement/design gap.
- Concrete test seeds:
  - `tc-s05-001` acceptance: clean managed remove deletes record and directory, leaves branch.
    - Premise: temp repo has managed linked worktree and local branch.
    - Operation: run `worktree remove <id>`.
    - Expected result: exit 0; `git worktree list --porcelain` no longer lists target; directory is absent; local branch remains.
    - Failure detection: catches missing Git remove, missing cleanup, or branch deletion.
    - Verification method: CLI runtime, Git porcelain, filesystem, branch assertions.
    - Related closure id: AC-006.
  - `tc-s05-002` acceptance JSON: remove JSON exposes operation result.
    - Premise: same as `tc-s05-001`.
    - Operation: run `worktree remove <id> --json`.
    - Expected result: `status=ok`, `resolved_target` fields present, `removed_record=true`, `removed_directory=true`, `branch_deleted=false`.
    - Failure detection: catches incomplete agent-facing remove result.
    - Verification method: JSON payload assertion.
    - Related closure id: AC-007.
  - `tc-s05-003` negative: dirty/untracked default remove fails without cleanup.
    - Premise: managed target has dirty or untracked file that makes Git default remove fail.
    - Operation: run `worktree remove <target> --json`.
    - Expected result: non-zero `git_worktree_remove_failed`; target directory remains; cleanup adapter not called.
    - Failure detection: catches pre-clean or filesystem deletion after Git refusal.
    - Verification method: CLI runtime, filesystem assertion.
    - Related closure id: AC-008.
  - `tc-s05-004` force: dirty/untracked target is removed when Git allows force.
    - Premise: same target state as `tc-s05-003`.
    - Operation: run `worktree remove <target> --force --json`.
    - Expected result: Git force remove semantics apply; target directory is gone; branch remains.
    - Failure detection: catches missing force propagation or branch deletion.
    - Verification method: CLI runtime, Git porcelain, filesystem, branch assertions.
    - Related closure id: AC-009.
  - `tc-s05-005` negative: main/current/unmanaged refused even with force.
    - Premise: target is main checkout, current checkout, or unmanaged linked worktree.
    - Operation: run `worktree remove <target> --force --json`.
    - Expected result: non-zero `remove_blocked`, blockers identify reason, Git remove and filesystem cleanup are not called.
    - Failure detection: catches `--force` bypassing non-bypassable guards.
    - Verification method: CLI runtime JSON and side-effect assertions.
    - Related closure id: AC-010, EC-002, EC-003.
  - `tc-s05-006` negative: pre-Git containment prevents namespace parent/repo root/symlink escape deletion.
    - Premise: target resolution or filesystem state would point at namespace parent, repo root/main path, or symlink-resolved namespace escape.
    - Operation: run `worktree remove <target> --force --json`.
    - Expected result: non-zero remove error before Git remove; no filesystem deletion.
    - Failure detection: catches destructive containment regressions.
    - Verification method: fake-port application tests and temp filesystem assertions.
    - Related closure id: destructive containment invariant.
  - `tc-s05-007` partial failure: post-Git cleanup failure is reported.
    - Premise: Git remove succeeds but remaining directory cleanup fails in a controlled fake filesystem adapter.
    - Operation: call remove use case or command with fake adapter.
    - Expected result: expected error/result indicates `post_remove_cleanup_failed`, `removed_record=true`, `removed_directory=false`; no success claim.
    - Failure detection: catches partial failure hidden as success.
    - Verification method: application fake-port test.
    - Related closure id: D-002, D-003.
- Step closure contract:
  - Close when remove safety, JSON/text output, branch preservation, force semantics, containment, and partial failure evidence pass, with `code-reviewer` pass.

### S90 docs impact resolution / docs refresh

- Behavior goal:
  - Provider and dogfooding references describe the shipped command surface and non-scope accurately.
- Depends on:
  - S02 through S05 behavior and command shape.
- Target files:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `spec-dock/docs/reference_worktree.md`
  - optionally related shipped docs only if command reference is linked elsewhere and stale.
- Planned contract:
  - Provider docs cover create/list/show/remove, `SPEC_DOCK_WORKTREE_ROOT`, JSON fields, target forms, managed/unmanaged classification, remove blockers, Git-first remove, force semantics, no branch deletion, no prune/repair, no Codex-managed cleanup.
  - Dogfooding docs match provider docs after provider-side source is updated or refreshed.
  - Existing future-extension wording must no longer claim list/show/remove are future; `status` / `prune` / `repair` remain future/out of scope.
- Red / alternative evidence:
  - `inspect-only`: docs diff and command help alignment; code test not required unless docs generation is test-covered.
- Delegation contract:
  - delegated role: `doc-writer`
  - allowed paths: docs target files only.
  - forbidden changes: runtime code/tests, canonical issue docs, workflow policy, skill files.
  - reviewer focus: `spec-reviewer` docs/spec alignment.
- Concrete test seeds:
  - `tc-s90-001` inspect-only: provider docs show current command family.
    - Premise: implementation command shape is fixed.
    - Operation: inspect provider reference.
    - Expected result: docs mention list/show/remove and no longer label them future.
    - Failure detection: catches stale shipped reference.
    - Verification method: docs diff inspection and optional `rg` checks.
    - Related closure id: E-AC-011, E-AC-012, E-AC-013.
  - `tc-s90-002` inspect-only: dogfooding docs match provider reference.
    - Premise: provider docs updated.
    - Operation: inspect `spec-dock/docs/reference_worktree.md`.
    - Expected result: dogfooding reference has matching command contract.
    - Failure detection: catches provider/dogfooding divergence.
    - Verification method: docs diff or side-by-side inspection.
    - Related closure id: E-AC-011.
- Step closure contract:
  - Close when docs impact is resolved, docs/spec alignment reviewer passes, and report records docs update or approved no-op rationale.

### S99 final quality gate

- Behavior goal:
  - Issue-wide evidence proves requirements, design, implementation, tests, docs, and report ledgers align before downstream delivery.
- Depends on:
  - S01 through S90 closed.
- Planned contract:
  - Run targeted runtime tests, then broader relevant tests such as `python -m unittest tests.cli_runtime.test_worktree -v` and broader `python -m unittest discover -v` if feasible.
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Run `./spec-dock/scripts/spec-dock sync`.
  - Run `git diff --check`.
  - Run final `qa-reviewer` for test sufficiency and integration risk.
  - Run issue-wide `code-reviewer` for integrated runtime/code/test/docs diff.
  - Run final `spec-reviewer` for requirement/design/plan/report/docs alignment.
  - Record Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit, PR Delivery Gate, and Merge Preparation Gate obligations in report before completion claims.
- Red / alternative evidence:
  - `manual-required`: reviewer gates and lifecycle/PR gates cannot be substituted by local tests.
- Delegation contract:
  - delegated roles: `qa-reviewer`, `code-reviewer`, `spec-reviewer` as final independent gates; implementation fixes remain delegated per `workflow_issue.md`.
  - forbidden changes: using final review to replace per-step review; claiming completion without report evidence and final commit/clean check.
- Concrete test seeds:
  - `tc-s99-001` final verification: targeted and broad tests pass.
    - Premise: all implementation steps are closed.
    - Operation: run targeted worktree tests and broader relevant suite.
    - Expected result: commands pass or documented blocker/next action is recorded.
    - Failure detection: catches integration breakage outside narrow slices.
    - Verification method: command output recorded in `report.md`.
  - `tc-s99-002` final reviews: three final gates pass.
    - Premise: final diff and report evidence are ready for review.
    - Operation: run `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer`.
    - Expected result: each returns fresh pass, or issue remains blocked/incomplete with next action.
    - Failure detection: catches reviewer-gate bypass.
    - Verification method: report gate evidence.
- Step closure contract:
  - Close only after final gates and report ledger obligations are satisfied. This draft does not claim that state.

## 6. Test Strategy Mapping

Spec-Locked Closure Index candidates for canonical `plan.md`:

| Closure ID | Step | Spec link | Locked expectation | Evidence level |
|---|---|---|---|---|
| wt-001 | S03 | AC-001 | list text shows id/path/branch/managed/removable summary | red-required |
| wt-002 | S03 | AC-002 | list JSON records contain required fields and unique stable ids | red-required |
| wt-003 | S04 | AC-003 | show resolves id/path/basename to the same record | red-required |
| wt-004 | S04 | AC-004, EC-004 | ambiguous target fails with candidates and no mutation | red-required |
| wt-005 | S04 | AC-005 | branch-only target is not accepted | red-required |
| wt-006 | S05 | AC-006 | clean managed remove deletes record/directory and keeps branch | red-required |
| wt-007 | S05 | AC-007 | remove JSON contains resolved target and operation status | red-required |
| wt-008 | S05 | AC-008 | default dirty/locked/untracked remove fails and keeps directory | red-required |
| wt-009 | S05 | AC-009 | `--force` maps to Git force and still keeps branch | red-required |
| wt-010 | S05 | AC-010, EC-002, EC-003 | main/current/unmanaged refused even with force | red-required |
| wt-011 | S01/S02 | AC-011 | invalid root fail-fast prevents Git/filesystem side effects and JSON failures are structured | red-required |
| wt-012 | S03 | AC-012, EC-005 | stale diagnostics are read-only and no prune/repair occurs | red-required |
| wt-013 | S02 | AC-013 | no `worktree delete` alias | red-required |
| wt-014 | S05 | destructive containment invariant | pre-Git and post-Git containment prevent namespace parent/repo root/symlink escape deletion | red-required |
| wt-090 | S90 | E-AC-011..E-AC-013 | provider and dogfooding references match current command contract | inspect-only |
| wt-099 | S99 | workflow_issue final gate | final QA/code/spec gates and validate/sync/test evidence are recorded | manual-required |

Recommended verification commands:

- `python -m unittest tests.cli_runtime.test_worktree -v`
- `python -m unittest discover -v` when feasible after targeted pass
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`
- `git diff --check`

Runtime tests must use temp Git repos and temp `SPEC_DOCK_WORKTREE_ROOT`; no live checkout deletion.

## 7. Review Gates

- Per-step code/runtime/test changes:
  - reviewer: `code-reviewer`
  - applies to S01, S02, S03, S04, S05
  - pass condition: fresh `review_status: pass`
  - failure handling: delegate bounded fixes and rerun reviewer; do not count worker output as reviewer pass.
- Docs-only changes:
  - reviewer: `spec-reviewer` docs/spec alignment
  - applies to S90
  - pass condition: fresh pass against requirement/design/plan/docs.
- Final QA gate:
  - reviewer: `qa-reviewer`
  - scope: test sufficiency, missing high-value integration tests, destructive safety coverage.
- Final code review gate:
  - reviewer: issue-wide `code-reviewer`
  - scope: integrated code/tests/docs diff, architecture boundaries, regression risk.
- Final spec review gate:
  - reviewer: `spec-reviewer`
  - scope: requirement/design/plan/report/docs/implementation/test alignment.

Report evidence destinations:

- `Implementation Delegation Gate`: S01..S05, S90, S99 delegation decisions.
- `Delegated Worker Evidence`: worker summaries and verification results.
- `Reviewer Gate Status`: per-step and final reviewer verdicts.
- `Step Contract Closure`, `Test Contract Closure`, `Closure Coverage`, `Closure Delta`: closure rows above.
- `Final QA Gate`, `Final Code Review Gate`, `Final Spec Review Gate`: S99.
- `Step Commit Gate`: each implementation step commit or approved-no-op.

## 8. Rollback / Compatibility

Compatibility:

- `worktree create` remains backward-compatible.
- No persisted SpecDock state migration.
- No active pointer, SpecDock tree, GitHub issue, sync, or branch lifecycle mutation from worktree list/show/remove.
- `remove` never deletes local branches and always returns `branch_deleted=false`.
- Missing / invalid `SPEC_DOCK_WORKTREE_ROOT` remains fail-fast; no legacy sibling fallback.
- `status` / `prune` / `repair` remain out of scope.

Rollback:

- Revert additive parser bindings and command specs for list/show/remove.
- Revert application dataclasses, use cases, helper additions, `UseCases` additions, ports, bootstrap wiring, Git remove adapter, filesystem adapter, presentation renderers, tests, and docs.
- Already-existing Git linked worktrees remain normal Git worktrees; rollback has no SpecDock state migration to unwind.

Risk controls:

- Pre-Git containment and post-Git cleanup containment must be independently tested.
- Git refusal must occur before filesystem cleanup.
- Cleanup is limited to the resolved managed individual worktree directory, never namespace parent.
- Tests must isolate destructive behavior in temp repos/root.

## 9. Docs Impact

Provider docs:

- Update `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`.
- Replace "create only / list/remove future" wording with current create/list/show/remove contract.
- Document `--json`, accepted target forms, stable id caveat, managed/unmanaged classification, `removable` / `remove_blockers`, expected JSON failures, Git-first remove, force behavior, no branch deletion, no prune/repair, stale diagnostics only, and Codex-managed worktree boundary.

Dogfooding docs:

- Refresh or inspect `spec-dock/docs/reference_worktree.md` to match provider-side source of truth.
- Report whether dogfooding workspace was updated by provider-side change propagation or intentionally edited/refreshed for parity.

Docs review:

- S90 requires `doc-writer` when docs change and `spec-reviewer` docs/spec alignment before completion claims.

## 10. Final Quality Gate

S99 final quality gate must verify:

- All required closure ids are closed in report `Step Contract Closure`, `Test Contract Closure`, and `Closure Coverage`.
- Each implementation step is `committed` or valid `approved-no-op`.
- Per-step reviewer gates have fresh pass evidence.
- S90 docs impact is resolved.
- Targeted runtime tests pass.
- Broader relevant tests are run or a blocker / infeasible reason is recorded.
- `./spec-dock/scripts/spec-dock validate` passes.
- `./spec-dock/scripts/spec-dock sync` passes.
- `git diff --check` passes.
- Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` have fresh pass evidence.
- PR Delivery Gate and Merge Preparation Gate obligations are recorded before lifecycle completion claims.
- Final clean check and final commit evidence are external delivery evidence, not pre-claimed in this draft.

## 11. Plan Blockers

none

Notes for orchestrator:

- `spec-dock/active/issue/plan.md` was unavailable on the first read attempt, then observed later as a canonical draft; this delegated draft may still be useful as comparison / refinement evidence, but adoption must reconcile against the current canonical plan.
- The working tree already had modified/deleted/untracked canonical/discussion files before this draft. This draft treats them as baseline state and does not modify them.
- Post-run diff guard remains pending and must be run by the main orchestrator before any adoption.

## 12. Integration Notes for Main Orchestrator

Recommended integration approach:

- Adopt only after post-run diff guard confirms exactly this new issue-local discussion draft is attributable to the delegated run.
- If adopted, reconcile accepted portions with the current canonical `spec-dock/active/issue/plan.md`; do not treat this draft as canonical by reference.
- Record adoption disposition in canonical `report.md` Evidence Adoption Ledger and Delegated Draft Evidence.
- Run a fresh `spec-reviewer` on canonical `plan.md` after integration.
- Keep S01..S05 as code/runtime/test steps, S90 as docs-only, and S99 as final gate.
- Preserve the design clarification that `remove.resolved_target` includes at least `id`, `path`, `basename`, `branch`, `managed`, `main`, and `current`.
- Do not use this draft to bypass per-step code reviews, docs/spec review, final QA/code/spec reviews, PR Delivery Gate, Merge Preparation Gate, or issue finish requirements.

Delegated Draft Evidence:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00137`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/templates/issue/plan.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - workflow / phase / issue-plan docs
  - runtime worktree source, tests, and docs listed in frontmatter
- draft artifact path: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t024332z-disc-worktree-list-show-remove-plan-draft.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: main orchestrator must decide adoption, update canonical plan/report if accepted, and run fresh plan `spec-reviewer`
- rejected portions: none proposed
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`
