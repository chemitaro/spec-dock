---
種別: draft-plan
ID: "20260526t083220z-draft-plan"
タイトル: "Central Worktree Root Placement Implementation Plan Guidance"
状態: "draft"
作成者: "doc-writer"
最終更新: "2026-05-26"
親: ["iss-00130"]
関連: []
authority: "proposed"
derived_from:
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081259z-01-interview-requirement-interview.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081259z-research-existing-worktree-contract-research.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081356z-disc-central-root-placement-options.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t082342z-research-shell-environment-setup-research.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py"
  - "tests/cli_runtime/test_worktree.py"
  - "src/spec_dock/assets/spec_dock/docs/reference_worktree.md"
reflected_to: []
created_by_role: "doc-writer"
scope_id: "iss-00130"
source_paths:
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081259z-01-interview-requirement-interview.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081259z-research-existing-worktree-contract-research.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t081356z-disc-central-root-placement-options.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00130-central-worktree-root-placement/discussions/20260526t082342z-research-shell-environment-setup-research.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py"
  - "tests/cli_runtime/test_worktree.py"
  - "src/spec_dock/assets/spec_dock/docs/reference_worktree.md"
intended_targets:
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
adoption_status: "unreviewed"
diff_guard_result: "created this discussion draft only; current worktree also contains requirement.md/design.md diffs outside this doc-writer edit scope"
---

# 20260526t083220z-draft-plan Central Worktree Root Placement Implementation Plan Guidance

## Position
- This is a scope-local flat discussion draft for `iss-00130`.
- Canonical `requirement.md`, `design.md`, `plan.md`, and `report.md` remain parent-orchestrator owned and are not edited by this draft.
- This guidance assumes the latest user-provided facts:
  - required env var: `SPEC_DOCK_WORKTREE_ROOT`
  - missing env var is fatal for `worktree create`
  - env set but root missing may create the root and namespace directories
  - namespace is the Git main worktree basename
  - path is `$SPEC_DOCK_WORKTREE_ROOT/<namespace>/<repo-basename>-<id>`
  - current id and branch naming stay unchanged
  - no migration or backward compatibility for future sibling placement
  - existing sibling worktrees are untouched
  - local `.zshenv` setup has already been performed by the user and should be verification evidence only

## Current Implementation Summary
- `application/worktree.py` currently derives placement from the Git main worktree:
  - `main_worktree = records[0].path`
  - `repo_basename = main_worktree.name`
  - `container = main_worktree.parent / f"{repo_basename}-worktrees"`
  - `worktree_path = container / f"{repo_basename}-{worktree_id}"`
- `WorktreeCreateRequest` currently only carries `label`.
- `WorktreeCreateResult` already exposes `container_path` and `worktree_path`.
- `commands/worktree.py` should not need a new CLI option; env root is configuration, not user command input.
- `ports.py` does not currently define an environment/config port.
- `tests/cli_runtime/test_worktree.py` currently hard-codes sibling placement in integration and fake-gateway tests.
- `reference_worktree.md` documents sibling placement and must be updated when the runtime contract changes.

## Recommended Behavior Slices

### S01 - Fatal Missing Env Var
- Behavior goal:
  - `worktree create` fails before directory creation or Git mutation when `SPEC_DOCK_WORKTREE_ROOT` is unset or blank.
- Recommended implementation scope:
  - Add a narrow env/config boundary available to `application/worktree.py`.
  - Prefer an application port such as `EnvironmentGateway.getenv(name: str) -> str | None` or an equivalent small runtime config port over direct `os.environ` reads in the use case.
  - Wire the concrete implementation in `cli/bootstrap.py`.
- Test obligation:
  - Add a unit-level or CLI-runtime test that runs `worktree create` without `SPEC_DOCK_WORKTREE_ROOT`.
  - Assert non-zero exit, error text naming `SPEC_DOCK_WORKTREE_ROOT`, and no worktree root / namespace / sibling container creation.
- Verification command:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.<missing-env-test> -v`
- Closure notes:
  - This slice should close the fail-fast contract before any path behavior is changed.

### S02 - Central Root Path Derivation and Directory Creation
- Behavior goal:
  - With `SPEC_DOCK_WORKTREE_ROOT` set, future worktrees are created at `$SPEC_DOCK_WORKTREE_ROOT/<namespace>/<repo-basename>-<id>`.
  - Namespace is the Git main worktree basename.
  - Env root and namespace directories may be created if missing.
- Recommended implementation scope:
  - Replace sibling `container` derivation with env-root container derivation.
  - Keep `repo_basename = main_worktree.name`.
  - Set `container = Path(env_value).expanduser() / repo_basename`.
  - Keep `worktree_path = container / f"{repo_basename}-{worktree_id}"`.
  - Preserve existing container mkdir error handling and artifact-state reporting, but update wording if "container" now means namespace directory.
- Test obligation:
  - Update the main success test to pass `SPEC_DOCK_WORKTREE_ROOT=<tmp>/central-root`.
  - Assert path `<tmp>/central-root/sample-repo/sample-repo-wt1`.
  - Assert the root and namespace are created when they did not exist before.
  - Assert no sibling `sample-repo-worktrees` directory is created.
- Verification command:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_uses_central_root_auto_id_and_branch -v`

### S03 - Preserve Existing ID, Label, Branch, Collision, and Bootstrap Behavior
- Behavior goal:
  - Only placement changes. Current id and branch naming remain:
    - auto id: `wt1`, `wt2`, ...
    - label id: `<label>`, `<label>2`, ...
    - branch: `<current-branch>-<id>`
  - Existing collision retry and bootstrap semantics remain unchanged.
- Recommended implementation scope:
  - Keep `_candidate_id`, label validation, branch naming, retryable Git collision handling, and `make init` handling intact.
  - Update tests that compute expected paths from sibling placement to central placement.
- Test obligation:
  - Retain or update:
    - label collision retry
    - auto id collision retry
    - invalid label rejection
    - branch prefix with slash
    - make init success/failure/detection failure
    - non-retryable Git add failure
    - retryable Git add collision
  - For tests using fake worktree records, update known paths from `repo-worktrees/repo-wt1` to the central root namespace path where relevant.
- Verification command:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`

### S04 - Linked Worktree Normalization Uses Main Worktree Namespace
- Behavior goal:
  - Running `worktree create` from an existing linked worktree still derives namespace and repo basename from Git's main worktree, not from the current linked worktree directory.
  - Branch prefix still uses the current checkout branch, preserving current behavior.
- Recommended implementation scope:
  - Keep `records[0].path` as the main worktree source, subject to the existing Git record ordering assumption.
  - Do not introduce migration or discovery of old sibling worktrees.
- Test obligation:
  - Update linked-worktree test to create both outer and inner worktrees under the central root namespace:
    - `<root>/sample-repo/sample-repo-outer`
    - `<root>/sample-repo/sample-repo-inner`
  - Assert old sibling container is untouched or absent for new command output.
- Verification command:
  - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree.test_worktree_create_normalizes_container_from_linked_worktree -v`

### S05 - Documentation Impact Resolution
- Behavior goal:
  - Shipped reference docs describe the required env var, fatal missing-env behavior, new path shape, namespace rule, and legacy boundary.
- Recommended docs scope:
  - Update `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`.
  - Consider whether generated dogfooding `spec-dock/docs/reference_worktree.md` should be refreshed by the normal update/sync flow rather than edited directly.
- Required content:
  - Setup example:
    - `export SPEC_DOCK_WORKTREE_ROOT="$HOME/workspace/worktrees"`
  - Layout:
    - `$SPEC_DOCK_WORKTREE_ROOT/spec-dock/spec-dock-wt1`
  - Missing env var:
    - fatal; no fallback to sibling placement.
  - Existing sibling worktrees:
    - untouched legacy worktrees; no migration in this issue.
  - Codex app worktrees:
    - remain distinct from spec-dock managed manual worktrees.
- Verification:
  - Inspect docs diff for removal of sibling placement as the future creation contract.
  - Run `spec-reviewer` docs/spec alignment before adopting into canonical report.

### S06 - Local Environment Verification Evidence Only
- Behavior goal:
  - The repo implementation does not edit local `.zshenv`; the user's setup is only verified as evidence.
- Recommended verification evidence:
  - Confirm the current shell environment exposes `SPEC_DOCK_WORKTREE_ROOT`.
  - Confirm the value points to `/Users/iwasawayuuta/workspace/worktrees` or the user-approved equivalent.
  - Confirm the directory exists or is creatable by the command in a disposable/manual smoke flow.
- Suggested commands:
  - `printenv SPEC_DOCK_WORKTREE_ROOT`
  - `test -d "$SPEC_DOCK_WORKTREE_ROOT"`
  - A disposable fixture smoke test with explicit env:
    - `SPEC_DOCK_WORKTREE_ROOT=/Users/iwasawayuuta/workspace/worktrees <fixture>/spec-dock/scripts/spec-dock worktree create central-root-smoke`
- Boundary:
  - Do not edit `/Users/iwasawayuuta/.zshenv` in this issue unless the parent orchestrator records a new explicit approval and updates the plan.

### S99 - Final Quality Gate
- Required automated verification:
  - Targeted worktree suite:
    - `python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v`
  - Broader runtime safety, if feasible:
    - `python -m unittest discover -v`
  - spec-dock validation:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
- Required reviews:
  - Per-step `code-reviewer` for runtime/tests/scaffold behavior changes.
  - `spec-reviewer` for docs/spec alignment after docs impact resolution.
  - Final `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` per issue workflow.
- Required report evidence:
  - Missing-env fatal behavior evidence.
  - Central-root path and namespace evidence.
  - Existing naming/collision/bootstrap behavior evidence.
  - Linked-worktree normalization evidence.
  - Docs impact resolution evidence.
  - Local env verification evidence only; no local shell profile diff.

## Closure Index Draft

| ID | Slice | Type | Locked Expectation | Observable Input / State | Bug Class Prevented | Evidence Level |
|---|---|---|---|---|---|---|
| wt-root-001 | S01 | negative | Missing or blank `SPEC_DOCK_WORKTREE_ROOT` is fatal and creates no worktree path | CLI runtime env without variable | silent fallback to sibling placement | red-required |
| wt-root-002 | S02 | acceptance | Worktree path is `$SPEC_DOCK_WORKTREE_ROOT/<main-basename>/<main-basename>-<id>` | env set to missing temp root | wrong placement / root not created | red-required |
| wt-root-003 | S03 | regression | id, label retry, branch naming, bootstrap semantics remain unchanged | existing worktree tests with central-root env | unnecessary naming or bootstrap regression | covered-existing plus updates |
| wt-root-004 | S04 | regression | linked worktree invocation uses Git main worktree basename namespace | command run from linked worktree | nested or linked-worktree-derived namespace drift | red-required |
| wt-root-005 | S05 | docs | reference docs describe env root, fatal missing env, no migration | shipped docs diff | user-facing contract drift | inspect-only |
| wt-root-006 | S06 | local evidence | local setup is verified, not edited by repo implementation | shell env / directory check | hidden workspace-external mutation | manual-required |

## Affected Files and Tests
- Expected runtime files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` only if result/request naming needs additional clarity
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` only if output should expose `container_path` or root/namespace explicitly
- Expected docs:
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - generated dogfooding docs under `spec-dock/docs/` only through the normal scaffold refresh flow if the parent plan requires it
- Expected tests:
  - `tests/cli_runtime/test_worktree.py`
- Explicitly out of scope:
  - migration or moving existing sibling worktrees
  - fallback to sibling placement
  - changing id generation
  - changing branch naming
  - adding namespace override config
  - editing `.zshenv` as part of implementation

## Open Plan Risks / Parent-Orchestrator Decisions
- Env/config boundary:
  - Recommendation: use a small port/config gateway so `worktree_create` can be tested without process-global env mutation.
  - Risk: direct `os.environ` in the use case is simpler but weaker for isolated tests and boundary consistency.
- Output wording:
  - Recommendation: existing success output can remain path-focused, but fatal missing-env error must name `SPEC_DOCK_WORKTREE_ROOT`.
  - Optional: include root/namespace in error diagnostics only; do not expand success output unless needed.
- Dogfooding refresh:
  - Recommendation: update provider-side docs first and let normal update/sync decide generated dogfooding diffs.
  - Risk: directly editing generated docs can hide scaffold drift.
