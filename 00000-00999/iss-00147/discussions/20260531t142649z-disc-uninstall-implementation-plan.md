---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00147
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/reference_deps.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
  - tests/test_init_update.py
  - tests/cli_runtime/test_update.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: manual_orchestrator_check_passed_new_issue_discussion_only_dirty_baseline
adoption_ledger_note: "Main orchestrator must decide adoption in canonical report.md before using this draft as plan authority."
source_revisions:
  requirement_hash: e755a67255fce267b0420351b17f346b7183dd76
  design_hash: aa5c5c35f9d67ed937ff44fdc8bd432fec1a3cd1
  epic_requirement_hash: 77c604bb4cd3e52bdabaea9e9ae684f23c300969
  epic_design_hash: 50c17edb26e5402d47e009b2fb29b9589e8e0d8f
  repo_head_short: fa46713a
---

# Plan Summary

This is an unreviewed implementation planning draft for `iss-00147 SpecDock uninstall command`. It translates the approved requirement and design into an executable step order, closure index candidates, and test obligations. It does not edit or supersede canonical `requirement.md`, `design.md`, `plan.md`, or `report.md`.

Planning assumption:
- The approved design is authoritative for initial flag naming: `spec-dock uninstall [path] [--apply] [--keep-specs | --remove-specs]`.
- `--json` is out of initial scope unless the main orchestrator amends the design.
- Installer-side implementation remains in `src/spec_dock/cli.py` for this issue, matching the approved design. If the implementation becomes too large, module extraction is a follow-up design/plan amendment rather than a hidden refactor.

Proposed implementation shape:
- S01 fixes installer command surface, usage errors, dry-run default, and plan/result rendering skeleton.
- S02 builds uninstall inventory and category/content-policy classification.
- S03 applies removal, idempotent rerun, partial failure reporting, and bounded empty-directory cleanup.
- S04 adds the repo-local runtime thin wrapper and parser/registry wiring.
- S90 resolves docs impact separately.
- S99 performs issue-wide final quality gates.

# Requirement / Design Traceability

Approved requirement inputs:
- `iss-00147` requirement status is `approved`.
- Core requirement: repo-local and installer uninstall remove SpecDock-managed development tooling while keeping package/global environment outside scope.
- Non-negotiable constraints:
  - destructive operation requires explicit mode and operator-visible plan.
  - agent / skill assets are the primary removal target and are deleted even when content mismatches, but only for known SpecDock-managed paths.
  - bootstrap-only and product-reusable assets are deleted only on exact content match.
  - specs deletion is explicit; no implicit spec history removal.
  - remote GitHub state is not mutated.

Approved design inputs:
- Installer CLI owns the implementation and remains the recovery path after repo-local runtime files are removed.
- Runtime command is a thin `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock uninstall TARGET ...` wrapper.
- Inventory flows from `install_root`, scaffold assets, generated state, spec history, obsolete exact paths, and shortcut inspection.
- Plan/result model separates `would_remove`, `removed`, `already_removed`, `preserved`, `failed`, and `empty_dir_removed`.

Epic traceability:
- E-RQ-011 / E-RQ-012 and E-AC-006 require uninstall to be a lifecycle command, not project-wide garbage collection.
- Epic design Flow-E requires repo-local wrapper -> installer CLI -> inventory -> dry-run / explicit specs mode / guarded removal -> recovery via installer CLI.

# Milestones

M1: Installer command contract and observable dry-run baseline
- Produces a visible uninstall command with correct exit-code behavior and no filesystem mutation by default.
- Closes the highest-risk destructive preflight boundary before any removal logic exists.

M2: Inventory and classification correctness
- Produces a deterministic uninstall plan from current shipped assets and target repo state.
- Locks ownership boundaries before apply logic can delete files.

M3: Apply, idempotency, partial failure, and cleanup
- Converts a validated plan into actual filesystem mutation.
- Keeps deletion bounded, retryable, and operator-readable.

M4: Repo-local runtime wrapper
- Adds the managed repo command surface after installer contract is stable.
- Keeps wrapper behavior aligned with the existing `update` command pattern.

M5: Docs impact and final gates
- Separates docs refresh from runtime/code implementation.
- Requires issue-wide QA, code review, spec review, validation, and delivery evidence before completion.

# Dependency-Derived Execution Order

1. S01 must precede all other steps because usage errors, dry-run default, and result buckets define the public contract that later classification/apply tests observe.
2. S02 depends on S01 because inventory/classification needs a rendered plan and stable option parsing to be tested through the public installer CLI.
3. S03 depends on S02 because apply must consume the same `UninstallAction` decisions that dry-run reports. It must not reclassify paths independently.
4. S04 depends on S01 and should follow S03, because the repo-local wrapper should forward to a stable installer command and should not become a second implementation.
5. S90 follows code/runtime steps because docs must reflect the final command contract and any intentionally deferred docs impact.
6. S99 follows all implementation and docs steps and must not replace per-step review gates.

Dependency notes:
- `src/spec_dock/cli.py` already owns installer parser, `_require_specdock`, install/update asset sync, `install_root` inventory helpers, bootstrap-only manifest parsing, obsolete exact paths, and repo-root shortcut install behavior. S01-S03 should reuse this local ownership rather than introduce a separate runtime implementation.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py` is the wrapper precedent for `uvx --no-cache`, target resolution, stdout/stderr propagation, and missing `uvx` handling. S04 should mirror this structure.
- `parser.py` and `registry.py` are downstream of the runtime command module; they are not useful until `commands/uninstall.py` has a `command_specs()` entry.

# Issue / Step Slicing

## S01 - Installer uninstall command surface and dry-run contract

Behavior goal:
- `spec-dock uninstall [path]` exists, defaults to dry-run, prints a grouped plan/result skeleton, and never mutates the filesystem without `--apply`.

Allowed targets:
- `src/spec_dock/cli.py`
- `tests/test_init_update.py`

Forbidden changes:
- no runtime wrapper files in this step.
- no shipped docs changes.
- no broad module extraction unless the plan is amended.

Step obligations:
- Add parser support for `uninstall`, `--apply`, `--keep-specs`, `--remove-specs`.
- Fail with exit `2` before mutation when `--apply` is used without exactly one specs mode.
- Reject mutually exclusive specs flags.
- Use existing target path validation style and `_require_specdock` for managed repo validation.
- Establish output bucket vocabulary even if S02/S03 later fills real inventory.

Reviewer gate:
- `code-reviewer` for CLI/tests/scaffold behavior.

## S02 - Inventory, category classification, and content policy

Behavior goal:
- Dry-run produces correct `would_remove` / `preserved` / manual-review decisions from shipped asset inventory and target repo state.

Allowed targets:
- `src/spec_dock/cli.py`
- `tests/test_init_update.py`

Forbidden changes:
- no file unlink/rmtree in this step except test fixture setup/teardown.
- no runtime wrapper files.
- no docs changes.

Step obligations:
- Build candidates from `install_root` current mappings, manifest bootstrap-only / obsolete exact paths, scaffold-managed files, generated state, spec history, repo-root `spec` shortcut, and explicit managed boundary roots.
- Classify known `.agents/skills/**`, `.codex/agents/**`, and `.github/agents/**` managed paths as delete-even-if-mismatch.
- Preserve unknown files under `.agents`, `.codex`, `.github`, and `spec-dock` as unmanaged.
- Apply exact-match policy for `.agents/host-adapters/meta.json`, `.codex/config.toml`, `.codex/prompts/**`, `.codex/rules/**`, `.codex/AGENTS.md`, `.github/workflows/**`, and scaffold-managed runtime/docs/templates/system files.
- Treat comparison error or file-type mismatch as preserve + manual review except known core agent/skill paths.
- Detect repo-root `spec` only when it is a symlink to `spec-dock/scripts/spec-dock`.

Reviewer gate:
- `code-reviewer` for classification correctness and over-delete prevention.

## S03 - Apply engine, idempotency, partial failure, and bounded cleanup

Behavior goal:
- `--apply --keep-specs` and `--apply --remove-specs` mutate only planned paths, report exact result buckets, and remain safe to rerun after partial or complete removal.

Allowed targets:
- `src/spec_dock/cli.py`
- `tests/test_init_update.py`

Forbidden changes:
- no runtime wrapper files.
- no docs changes.
- no deletion outside target repo test fixtures.

Step obligations:
- Apply only `UninstallAction` entries created by S02.
- Keep `--keep-specs` preserving `spec-dock/initiatives/**`.
- Make `--remove-specs` include `spec-dock/initiatives/**` and explicitly report spec history removal.
- Remove generated state (`spec-dock/.agent/**`, `spec-dock/active/**`) according to the approved design's workspace cleanup policy.
- Remove empty directories only within bounded roots: `.agents`, `.codex`, `.github`, `spec-dock`.
- Stop cleanup when a directory contains preserved or unmanaged files.
- Return non-zero for failed removals and distinguish deleted, not deleted, preserved, failed, and already removed.
- Support rerun after prior removal without destructive errors.

Reviewer gate:
- `code-reviewer` for filesystem safety, failure modes, and idempotency.

## S04 - Repo-local runtime uninstall wrapper

Behavior goal:
- `./spec-dock/scripts/spec-dock uninstall [path] [--apply] [--keep-specs | --remove-specs]` delegates to the installer CLI via `uvx --no-cache` and propagates stdout/stderr/exit code.

Allowed targets:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/uninstall.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `tests/cli_runtime/test_uninstall.py`
- if needed for import wiring only: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/__init__.py`

Forbidden changes:
- no installer removal logic in runtime command.
- no arbitrary `--from` / cache override option.
- no docs changes.

Step obligations:
- Mirror `update.py` structure and `UPSTREAM_SOURCE`.
- Default target resolves to current working directory.
- Explicit target is resolved and passed through.
- Forward `--apply`, `--keep-specs`, and `--remove-specs`.
- Propagate subprocess stdout/stderr/exit code.
- Return `127` with actionable guidance when `uvx` is missing.
- Reject unsupported flags through argparse without invoking `uvx`.

Reviewer gate:
- `code-reviewer` for wrapper parity and command registration.

## S90 - Docs impact resolution / docs refresh

Behavior goal:
- Documentation and help text describe uninstall boundaries without turning this issue into package/environment uninstall or GitHub mutation work.

Allowed targets:
- `src/spec_dock/assets/spec_dock/docs/reference_github.md`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- possibly tests that assert docs/help fragments if existing test structure requires it.

Forbidden changes:
- no runtime/code behavior changes.
- no canonical issue docs unless main orchestrator separately edits them.
- no generated dogfooding refresh unless the orchestrator chooses to sync/update the local consumer workspace.

Step obligations:
- Update `reference_github.md` to state uninstall does not close/delete GitHub issues, mutate remote state, or uninstall Python packages/global CLI/uvx cache.
- Inspect `reference_sync.md` for generated state (`spec-dock/.agent/**`, `spec-dock/active/**`) wording. If current wording is sufficient, record no-op rationale in `report.md`; if not, update provider-side docs.
- Ensure installer/runtime help output remains contract-aligned through tests.

Reviewer gate:
- `spec-reviewer` docs/spec alignment. If tests are changed only to assert docs/help text, `code-reviewer` may also be required by workflow mapping.

## S99 - Final quality gate

Behavior goal:
- Confirm the integrated issue satisfies requirement/design/plan, has adequate test coverage, and is ready for PR delivery and merge-preparation judgment.

Required checks:
- focused installer tests, for example `python -m unittest tests.test_init_update -v`.
- focused runtime tests, for example `python -m unittest tests.cli_runtime.test_uninstall -v`.
- full baseline `python -m unittest discover -v`.
- `./spec-dock/scripts/spec-dock validate`.
- `./spec-dock/scripts/spec-dock sync` unless GitHub/network state is intentionally unavailable; if unavailable, use `./spec-dock/scripts/spec-dock sync --no-github` and record the opt-out reason.
- `git diff --check`.

Required reviewers:
- `qa-reviewer`: issue-wide test adequacy and integration-test need.
- issue-wide `code-reviewer`: integrated diff, structure, responsibility boundaries, regression risk, maintainability.
- final `spec-reviewer`: requirement / design / plan / report / docs / implementation / tests consistency.

# Test Strategy Mapping

Closure index candidates:

| ID | Step | Slice | Spec link | Locked expectation | Evidence level | Required |
|---|---|---|---|---|---|---|
| tc-001 | S01 | installer dry-run surface | AC-001, EC-002 | `spec-dock uninstall <target>` reports plan and mutates no files | red-required | yes |
| tc-002 | S01 | apply preflight | AC-002 | `--apply` without specs mode exits `2` before any deletion | red-required | yes |
| tc-003 | S01 | flag exclusivity | design Flag contract | `--keep-specs` and `--remove-specs` cannot both be accepted for apply | red-required | yes |
| tc-004 | S02 | agent/skill classification | AC-003, AC-007 | known managed agent/skill paths are planned for removal even on mismatch | red-required | yes |
| tc-005 | S02 | unmanaged preservation | AC-007 | unknown user-created files under managed-looking roots are preserved and reported | red-required | yes |
| tc-006 | S02 | bootstrap/product-reusable exact match | AC-005 | exact-match bootstrap/product-reusable assets are planned for removal | red-required | yes |
| tc-007 | S02 | bootstrap/product-reusable mismatch | AC-006, EC-006 | mismatch or comparison-error assets are preserved for manual review | red-required | yes |
| tc-008 | S02 | scaffold-managed policy | design mapping | scaffold-managed files are exact-match delete, mismatch preserve | red-required | yes |
| tc-009 | S02 | repo-root shortcut | EC-007 | `spec` symlink to runtime is removable; nonmatching symlink/file/directory is preserved | red-required | yes |
| tc-010 | S03 | keep-specs apply | AC-003 | apply removes tooling but preserves `spec-dock/initiatives/**` | red-required | yes |
| tc-011 | S03 | remove-specs apply | AC-004 | apply includes spec history and reports that destructive choice explicitly | red-required | yes |
| tc-012 | S03 | bounded cleanup | EC-003, EC-004 | empty dirs are removed only inside boundary roots and never through preserved content | red-required | yes |
| tc-013 | S03 | idempotent rerun | AC-009 | prior removals report `already_removed` / no-op without destructive failure | red-required | yes |
| tc-014 | S03 | partial failure | requirement failure behavior | unlink/rmtree failure returns non-zero and reports `failed` separately | red-required | yes |
| tc-015 | S04 | runtime wrapper invocation | AC-008 | wrapper calls `uvx --no-cache --from ... spec-dock uninstall TARGET` | red-required | yes |
| tc-016 | S04 | runtime flag/output propagation | AC-008 | wrapper forwards supported flags and propagates stdout/stderr/exit code | red-required | yes |
| tc-017 | S04 | missing uvx | design Runtime command | missing `uvx` exits `127` with PATH/install guidance | red-required | yes |
| tc-018 | S90 | docs boundary | Docs impact | docs state no GitHub mutation and no package/environment uninstall | inspect-only | yes |
| tc-019 | S99 | integrated issue adequacy | workflow_issue.md | full tests, validate/sync, final QA/code/spec gates pass or record blocker | manual-required | yes |

Concrete test obligation notes:
- Installer tests should prefer temp directories and direct `main([...])` calls, consistent with `tests/test_init_update.py`.
- Runtime tests should mirror `tests/cli_runtime/test_update.py` and use an `uvx` stub to capture args rather than network access.
- For destructive apply behavior, fixture assertions must verify both presence and absence after execution, not only CLI text.
- For dry-run behavior, capture a pre/post filesystem snapshot for representative files and directories.
- For content policy, at least one exact-match and one mismatch fixture is required for each high-risk category: bootstrap-only, product-reusable, scaffold-managed, agent/skill, unknown unmanaged.
- For cleanup, include a preserved file inside a boundary root to prove parent directory is not removed.
- For partial failure, use a controlled failing unlink/rmtree path or permission/mock strategy that is hermetic and does not require platform-specific global state.

# Review Gates

Per-step gates:
- S01, S02, S03, S04 require `code-reviewer` pass because they touch installer/runtime behavior and tests.
- S90 requires `spec-reviewer` docs/spec alignment; if S90 changes tests or help assertions, also require `code-reviewer`.
- S99 requires independent final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` passes.

Report evidence required before each step closes:
- `Implementation Delegation Gate`: delegated role, allowed paths, forbidden changes, required verification, stop conditions, output required.
- `Step Contract Closure`: step, closure ids, close condition, evidence, result.
- `Test Contract Closure`: required closure ids, pre-implementation evidence, verification command, result.
- `Closure Coverage`: mapping from every required closure id to evidence.
- `Reviewer Gate Status`: reviewer role, freshness, state, re-review evidence if needed.
- `Step Commit Gate`: review scope, closure state, commit/no-op evidence, post-commit clean check.

Amendment triggers:
- Any deletion candidate source outside shipped inventory, explicit generated-state roots, spec-history mode, obsolete exact paths, or verified shortcut target.
- Need to delete mismatch content for non-agent/product-reusable assets.
- Need to add machine-readable `--json`.
- Need to mutate GitHub state or uninstall package/global environment.
- Need to split `src/spec_dock/cli.py` into new modules due to size or maintainability.
- Any required closure row deletion, locked expectation change, required flag change, or spec link meaning change.

# Rollback / Compatibility

Implementation compatibility:
- The change should be additive to installer and runtime command surfaces.
- Existing `init`, `update`, `delete`, `sync`, and `validate` behavior must remain unchanged.
- Runtime wrapper must not accept arbitrary package source/cache options, matching self-update safety precedent.
- No GitHub remote state, package manager environment, global CLI, pip/uvx cache, or target repo parent directory is touched.

Operational rollback:
- Code rollback is normal git revert of the issue commits.
- Uninstall apply itself has no automatic rollback after deletion. Safety is provided by dry-run default, explicit `--apply` plus specs mode, exact-match preservation, bounded cleanup, result summary, and idempotent rerun.
- Partial failure recovery path is rerun via installer CLI `spec-dock uninstall <target> ...`; repo-local runtime may already have been deleted.

# Docs Impact

S90 is required, not optional.

Required docs actions:
- `src/spec_dock/assets/spec_dock/docs/reference_github.md`:
  - add or adjust wording that uninstall does not close/delete GitHub issues and does not mutate remote GitHub state.
  - state that uninstall is repo-local managed artifact removal, not Python package / global CLI / uvx cache cleanup.
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`:
  - inspect whether generated state (`spec-dock/.agent/**`, `spec-dock/active/**`) and uninstall cleanup interaction need explanation.
  - if no update is needed, record the no-op rationale in `report.md` and include spec-reviewer alignment evidence.
- CLI help:
  - installer help and runtime help must match the final flag contract and be covered by tests.

Dogfooding impact:
- If shipped docs or runtime scaffold assets are changed, the orchestrator should decide whether to refresh the local `spec-dock/` dogfooding workspace. This draft does not request or perform that refresh.

# Final Quality Gate

S99 must remain an independent step after S90.

Required S99 inputs:
- all implementation steps closed as committed or valid approved-no-op.
- all required closure ids covered in `report.md`.
- S90 docs impact resolved.
- no open plan blockers or unadopted material decisions that are needed for implementation authority.

Required S99 commands/evidence:
- focused installer test command and result.
- focused runtime uninstall test command and result.
- full `python -m unittest discover -v` result.
- `./spec-dock/scripts/spec-dock validate` result.
- `./spec-dock/scripts/spec-dock sync` result, or explicit `--no-github` opt-out evidence and reason.
- `git diff --check` result.
- final diff summary and changed-file scope.

Required S99 reviewers:
- `qa-reviewer` pass for test sufficiency and integration-test need.
- issue-wide `code-reviewer` pass for integrated implementation quality.
- final `spec-reviewer` pass for requirement/design/plan/report/docs/implementation/test consistency.

Completion guard:
- S99 pass is not `issue finish`, PR delivery, merge readiness, or lifecycle completion by itself. The main orchestrator must still record final report ledger, final commit scope, PR delivery gate, merge preparation gate, and lifecycle closure evidence according to `workflow_issue.md`.

# Plan Blockers

none

Non-blocking notes:
- Existing working tree status showed pre-existing modified canonical docs and untracked discussion drafts before this draft was created. The main orchestrator should run the delegated-authoring diff guard from its baseline and decide adoption eligibility.
- Design Q-001 recommends no `--json` in initial implementation. This draft follows that recommendation and does not treat JSON output as a blocker.

# Integration Notes for Main Orchestrator

Delegated Draft Evidence:
- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00147`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_update.py`
- draft artifact path: `spec-dock/active/issue/discussions/20260531t142649z-disc-uninstall-implementation-plan.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `manual_orchestrator_check_passed_new_issue_discussion_only_dirty_baseline`
- integration notes:
  - Use this draft as candidate material for canonical `plan.md` only after main-orchestrator adoption and fresh `spec-reviewer` review.
  - Keep S01-S04, S90, and S99 as separate review scopes unless the orchestrator amends the plan with explicit rationale.
  - Preserve the design's no-`--json` initial scope unless a plan amendment is approved.
- rejected portions: none
- blockers: none
- canonical artifacts edited: none
- final authority claimed: no

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
