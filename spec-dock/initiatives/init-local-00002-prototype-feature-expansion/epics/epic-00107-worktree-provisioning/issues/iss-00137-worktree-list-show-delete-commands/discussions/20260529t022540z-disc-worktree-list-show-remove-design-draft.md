---
created_by_role: spec-dock-system-architect
scope_id: iss-00137
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_design.md
  - spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md
  - spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md
  - spec-dock/active/issue/discussions/20260529t012346z-interview-worktree-delete-dirty-guard-interview.md
  - spec-dock/active/issue/discussions/20260529t013126z-interview-worktree-delete-confirmation-interview.md
  - spec-dock/active/issue/discussions/20260529t013748z-interview-worktree-output-contract-interview.md
  - spec-dock/active/issue/discussions/20260529t014129z-interview-worktree-target-resolution-interview.md
  - spec-dock/active/issue/discussions/20260529t014506z-interview-worktree-deletable-status-json-interview.md
  - spec-dock/active/issue/discussions/20260529t014700z-interview-worktree-delete-remove-naming-interview.md
  - spec-dock/active/issue/discussions/20260529t014953z-interview-worktree-root-env-behavior-interview.md
  - spec-dock/active/issue/discussions/20260529t015346z-interview-worktree-stale-record-handling-interview.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - tests/cli_runtime/test_worktree.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Worktree list/show/remove delegated design draft

## Requirement Coverage

- Covers AC-001 through AC-013 and EC-001 through EC-005 from `iss-00137` by proposing `worktree list`, `worktree show <target>`, and `worktree remove <target>` in the existing layered runtime.
- Covers the non-blocking requirement reviewer P2 recorded in `report.md`: JSON success payloads and JSON failure/error payloads are explicitly modeled below.
- Preserves parent epic boundaries: provider-side source remains `src/spec_dock/assets/spec_dock/...`, dogfooding `spec-dock/...` is confirmation/reflection surface, and Codex-managed `$CODEX_HOME/worktrees` cleanup remains out of scope.
- Does not add `worktree delete`, branch deletion, `worktree prune`, stale repair, orphan cleanup, GitHub mutation, active pointer mutation, or SpecDock tree mutation.

## Existing Context Findings

- `worktree create` already lives in the layered runtime: CLI parser/registry bind `worktree_create`; `commands/worktree.py` maps typed args to `WorktreeCreateRequest`; `application/worktree.py` owns label normalization, `SPEC_DOCK_WORKTREE_ROOT` validation, main-worktree normalization, collision retry, Git add, and bootstrap aggregation; `infra/git_cli.py` owns `git worktree list --porcelain` parsing and `git worktree add`; `presentation/cli_text.py` renders text output; `tests/cli_runtime/test_worktree.py` uses temp Git repos and temp central roots.
- Existing `GitWorktreeRecord` has `path`, `head`, `branch`, `detached`, and `bare`, but no locked/prunable field and no remove adapter.
- Current CLI dispatch catches uncaught `RuntimeError` globally and emits text stderr only. Because `list/show/remove --json` must also return machine-readable failures, expected worktree command failures need a worktree-specific error contract caught inside `commands/worktree.py` before dispatch fallback.
- Existing spec-node `delete --json` is a useful presentation precedent, but worktree removal must not reuse spec-node deletion semantics such as `--yes`, recursive subtree deletion, post-sync, active restore, or remote close.

## Design Decisions

- Add read/write use cases to `application/worktree.py`: `worktree_list`, `worktree_show`, and `worktree_remove`, sharing root resolution and record classification helpers with `worktree_create`.
- Refactor only the reusable parts of `worktree_create`: central-root env lookup/validation, main-worktree record selection, canonical path normalization, repo basename/container derivation, and result-safe helper functions. Do not fold create/list/show/remove into a generic manager abstraction unless the local duplication becomes material during implementation.
- Use Git metadata as source of record for linked worktree records. Classify records against `$SPEC_DOCK_WORKTREE_ROOT/<main-worktree-basename>/` rather than storing a SpecDock registry.
- Use Git-first remove semantics: `worktree_remove` validates target and non-bypassable guards, then calls `git worktree remove <path>` or `git worktree remove --force <path>`. Only after Git returns success may SpecDock remove any remaining individual managed worktree directory.
- Keep `remove --force` scoped to Git's force semantics. It may help dirty/locked Git remove cases, but it must not bypass `unmanaged`, `main_worktree`, `current_worktree`, `record_missing`, or `path_missing` blockers.
- Treat `removable` in `list/show` as a planning hint. `remove` must re-list and reclassify immediately before executing Git remove.
- Use `remove_blockers` terminology throughout new JSON contracts. Existing older discussion wording `deletable/delete_blockers` is superseded by the requirement's `removable/remove_blockers`.

## Alternatives Considered

- Branch-name target resolution: rejected for this issue. It increases ambiguity, clashes with branch lifecycle mental model, and is explicitly outside the accepted target forms.
- SpecDock registry of managed worktrees: rejected. Existing create contract derives identity from central root path naming and Git records; adding persistence would expand migration and repair scope.
- Pre-clean cache/generated files before Git remove: rejected. It would undermine Git's dirty/untracked refusal semantics. Cleanup happens only after Git remove succeeds.
- `--yes` confirmation: rejected by requirement. Safety is handled by managed-only, main/current refusal, Git rejection, and explicit `--force`.
- `worktree prune` or stale repair in `remove`: rejected. `list/show` may diagnose stale states, but repair/prune remain future scope.

## Boundary / Contract Model

- CLI surface:
  - `spec-dock worktree list [--json]`
  - `spec-dock worktree show <target> [--json]`
  - `spec-dock worktree remove <target> [--force] [--json]`
  - `spec-dock worktree delete <target>` is not registered.
- Accepted targets for `show/remove`: stable `id`, absolute path, or directory basename. Branch names are not targets.
- Target resolution order should not silently choose by priority. Resolve all accepted forms across records, de-duplicate by canonical path, and fail with `ambiguous_target` if more than one record matches.
- Stable id:
  - Managed path matching `<repo-basename>-<id>` under the namespace uses `<id>`.
  - Other records use a deterministic display id derived from basename, for example `basename`, with collision disambiguation handled by ambiguity failure rather than branch fallback.
- Classification:
  - `main=true` for the first Git worktree record, which existing create logic already treats as main worktree.
  - `current=true` when canonical record path equals the current command `repo_root`.
  - `managed=true` when record path is under the central namespace and the record is not the main worktree.
  - `unmanaged` is represented by `managed=false`.
  - `removable=true` only when there are no non-force blockers in `remove_blockers`.

## Dependency Analysis

- `commands/worktree.py` should remain the command boundary and catch expected `WorktreeCommandError` for JSON-aware error rendering.
- `application/worktree.py` should own classification, target resolution, stale diagnostics, guard evaluation, and remove orchestration.
- `application/ports.py` needs new Git and filesystem operations behind protocols. Application should not call `subprocess` or perform unrestricted filesystem deletion directly.
- `infra/git_cli.py` should stay a thin Git CLI adapter. It parses additional `git worktree list --porcelain` fields only when needed for diagnostics, and adds `remove_worktree(repo_root, path, force)`.
- A new filesystem port is recommended for post-success cleanup, e.g. `FilesystemGateway.remove_tree(path)`, wired in `cli/bootstrap.py` to an infra implementation using `shutil.rmtree`. The application calls it only after managed guards and successful Git remove.
- `presentation/cli_text.py` can hold worktree text and JSON payload builders if the file remains manageable; extraction to a worktree-specific presentation module is optional only if local size or imports become unwieldy.

## Source of Record

- Linked worktree inventory: `git worktree list --porcelain`.
- Managed namespace: `$SPEC_DOCK_WORKTREE_ROOT/<main-worktree-basename>/`.
- Current checkout: runtime `repo_root` passed to ports, canonicalized.
- Command contract: canonical issue design/plan after orchestrator adoption and reviewer pass.
- No persisted SpecDock state, active pointer, GitHub issue state, branch registry, or `.agent` artifact is source of record for these commands.

## Data Flow / Domain Model / Interface Contract

```text
parser -> commands/worktree.py -> application/worktree.py -> ports
                                                 |-> GitGateway.worktree_list/remove_worktree
                                                 |-> FilesystemGateway.path_exists/remove_tree
                                                 |-> EnvironmentGateway.getenv
                                      -> presentation/cli_text.py
```

Suggested application contracts:

- `WorktreeListRequest(json_output: bool = False)`
- `WorktreeShowRequest(target: str, json_output: bool = False)`
- `WorktreeRemoveRequest(target: str, force: bool = False, json_output: bool = False)`
- `WorktreeRecordView`: `id`, `path`, `basename`, `branch`, `head`, `managed`, `main`, `current`, `path_exists`, `record_exists`, `removable`, `remove_blockers`.
- `WorktreeRemoveResult`: `status="ok"`, `worktree`, `removed_record`, `removed_directory`, `branch_deleted=False`, `warnings`.
- `WorktreeCommandError`: `code`, `message`, `target`, `candidates`, `worktree`, `remove_blockers`, `git_error`, `root_error`.

Success JSON:

```json
{
  "status": "ok",
  "command": "worktree list",
  "worktrees": [
    {
      "id": "wt1",
      "path": "/tmp/worktrees/repo/repo-wt1",
      "basename": "repo-wt1",
      "branch": "main-wt1",
      "head": "abc123",
      "managed": true,
      "main": false,
      "current": false,
      "path_exists": true,
      "record_exists": true,
      "removable": true,
      "remove_blockers": []
    }
  ],
  "warnings": []
}
```

```json
{
  "status": "ok",
  "command": "worktree show",
  "target": "wt1",
  "worktree": {
    "id": "wt1",
    "path": "/tmp/worktrees/repo/repo-wt1",
    "basename": "repo-wt1",
    "branch": "main-wt1",
    "managed": true,
    "main": false,
    "current": false,
    "path_exists": true,
    "record_exists": true,
    "removable": true,
    "remove_blockers": []
  },
  "warnings": []
}
```

```json
{
  "status": "ok",
  "command": "worktree remove",
  "target": "wt1",
  "resolved_target": {
    "id": "wt1",
    "path": "/tmp/worktrees/repo/repo-wt1",
    "basename": "repo-wt1",
    "branch": "main-wt1",
    "managed": true
  },
  "removed_record": true,
  "removed_directory": true,
  "branch_deleted": false,
  "warnings": []
}
```

Failure JSON for expected command failures:

```json
{
  "status": "error",
  "command": "worktree remove",
  "error": {
    "code": "ambiguous_target",
    "message": "worktree target matched multiple records",
    "target": "repo-wt1",
    "candidates": [
      {"id": "wt1", "path": "/tmp/worktrees/repo/repo-wt1", "basename": "repo-wt1"},
      {"id": "other", "path": "/tmp/other/repo-wt1", "basename": "repo-wt1"}
    ]
  },
  "warnings": []
}
```

Recommended error codes:

- `worktree_root_required`
- `invalid_worktree_root`
- `target_not_found`
- `ambiguous_target`
- `unsupported_branch_target`
- `remove_blocked`
- `git_worktree_list_failed`
- `git_worktree_remove_failed`
- `post_remove_cleanup_failed`
- `worktree_use_case_not_configured`

`remove_blockers` code model:

- `unmanaged`: central namespace outside the record path.
- `main_worktree`: the main checkout record.
- `current_worktree`: the command's current checkout.
- `path_missing`: Git record path does not exist.
- `record_missing`: target cannot be backed by a current Git worktree record.
- `bare_worktree`: Git record is bare.
- `locked`: Git porcelain reports a locked record, if parsed.
- `git_remove_would_require_force`: optional prediagnostic when a lightweight check can prove default Git remove is likely to fail; final authority remains Git remove.

`remove_blocked` failure JSON should include the resolved `worktree` and `remove_blockers`. `git_worktree_remove_failed` should include `git_error` and should not claim `removed_record` or `removed_directory`.

## File / Module Change Plan

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- application/
|   |-- contracts.py      # add worktree list/show/remove request/result/error dataclasses
|   |-- ports.py          # add GitGateway.remove_worktree and FilesystemGateway
|   `-- worktree.py       # refactor shared root helpers; add list/show/remove use cases
|-- cli/
|   |-- parser.py         # bind worktree list/show/remove; do not bind delete
|   `-- bootstrap.py      # wire new use cases and filesystem/git adapters
|-- commands/
|   `-- worktree.py       # add typed args, --json/--force, JSON-aware expected-error handling
|-- infra/
|   |-- git_cli.py        # add git worktree remove adapter; optionally parse locked/prunable fields
|   `-- fs_cli.py         # new thin remove_tree/path_exists adapter if no existing home fits
`-- presentation/
    `-- cli_text.py       # add worktree list/show/remove text and JSON renderers

tests/
`-- cli_runtime/
    `-- test_worktree.py  # extend temp Git repo/temp central root runtime coverage

src/spec_dock/assets/spec_dock/docs/
`-- reference_worktree.md # provider docs update after canonical design/plan adoption

spec-dock/docs/
`-- reference_worktree.md # dogfooding parity after provider-side update/sync path
```

Provider docs and dogfooding docs are implementation-plan targets, not edited by this delegated draft.

## Migration / Compatibility / Rollback

- Existing `worktree create` CLI and text output remain backward compatible.
- `worktree list/show/remove` are additive commands.
- No persisted state migration is needed because Git and filesystem are source of record.
- Rollback is removal of the additive parser bindings, use cases, adapters, presentation functions, tests, and docs additions. Existing central-root worktrees remain normal Git worktrees and are not migrated.
- If post-success directory cleanup fails after Git remove succeeds, return non-zero with `post_remove_cleanup_failed` and `removed_record=true`, `removed_directory=false`. This accurately reports partial cleanup and avoids pretending rollback is possible.

## Observability

- Text `list` should show compact rows with id, managed/unmanaged, main/current markers, removable summary, branch, and path.
- Text `show` should show one record plus blockers.
- Text `remove` should show resolved id/path/branch and `branch_deleted=false`.
- JSON is the authoritative automation surface and should always include `status`, `command`, `warnings`, and either command payload or `error`.
- Git stderr for remove failure should be surfaced in JSON under `error.git_error` and in text stderr without pre-cleaning the directory.

## Test Strategy

- Extend `tests/cli_runtime/test_worktree.py` using temp Git repos and temp central roots, following existing create tests.
- Cover parser/help:
  - `worktree list/show/remove` exist.
  - `worktree delete` does not exist.
  - `--json` is accepted for all three new commands.
  - `--force` is accepted only for remove.
- Cover env fail-fast:
  - missing, blank, relative path, file, broken symlink fail before Git listing/removal and before filesystem cleanup.
- Cover inventory:
  - main checkout, managed linked worktree, unmanaged linked worktree.
  - text output includes id/path/branch/managed/removable summary.
  - JSON includes required fields and distinguishes managed/unmanaged/main/current.
- Cover target resolution:
  - stable id, absolute path, and basename resolve to same record.
  - branch-only target fails with not found or `unsupported_branch_target` if explicitly detected.
  - ambiguous target returns candidates and performs no removal.
- Cover remove:
  - clean managed worktree removes Git record, removes leftover individual directory/cache, and leaves local branch.
  - unmanaged, main, and current targets are refused with and without `--force`.
  - Git refusal for dirty/locked/default remove leaves directory intact and returns JSON error under `--json`.
  - `--force` calls Git force remove and cleans remaining directory only after Git success.
  - stale record/missing path appears in diagnostics but is not repaired/pruned.
- Destructive safety boundaries:
  - Never use the live repository as target.
  - Assert temp root containment before cleanup.
  - Assert namespace directory may remain while individual worktree directory is removed.

## ADR Candidates

- None required for the current issue. The decisions are issue-local and reversible.
- Future ADR candidate only if SpecDock later broadens managed worktrees beyond central-root namespace or adds persistent worktree registry/prune/repair semantics.

## Risks

- Existing target `discussions/` had pre-existing modified/untracked entries at this run. The new draft can still be useful evidence, but post-run diff guard may require orchestrator-side baseline handling before adoption.
- JSON error rendering requires bypassing global `RuntimeError` fallback for expected worktree failures. Missing this would fail the reviewer P2 requirement for machine-readable failures.
- `git worktree list --porcelain` locked/prunable output support may vary by Git version. The design should degrade by relying on Git remove as final authority while still preserving stable blocker codes for guards that SpecDock can know.
- Post-remove filesystem cleanup is destructive. It must be constrained to resolved managed individual worktree paths after successful Git remove.

## Requirement Clarification Requests

none

## Integration Notes for Main Orchestrator

- Suggested canonical adoption target is `design.md` sections covering existing implementation, adopted decisions, interface contract, file/module plan, and test strategy.
- `plan.md` should split JSON contract/presentation tests from destructive remove tests so the force/default cleanup semantics are verified independently.
- `report.md` should update Delegated Draft Evidence and Evidence Adoption Ledger only after the orchestrator runs the post-run diff guard and decides adoption.
- The draft intentionally does not claim reviewer pass, phase promotion, implementation readiness, or final authority.

## Delegated Draft Evidence

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00137`
- source artifacts read:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_design.md`
  - issue-local worktree clarification/research discussions listed in frontmatter
  - existing runtime worktree/parser/command/contracts/ports/git/presentation/tests listed in frontmatter
- draft artifact path: `spec-dock/active/issue/discussions/20260529t022540z-disc-worktree-list-show-remove-design-draft.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes:
  - Orchestrator should run the post-run diff guard and decide whether to adopt all or part of this draft into canonical artifacts.
  - Existing target discussion dirtiness should be accounted for before adoption.
- rejected portions, if any: none
- blockers, if any:
  - Potential adoption blocker: pre-existing modified/untracked files in the active issue/epic scope may affect post-run diff guard eligibility.
- canonical artifacts edited: `none`
- final authority claimed: `no`
