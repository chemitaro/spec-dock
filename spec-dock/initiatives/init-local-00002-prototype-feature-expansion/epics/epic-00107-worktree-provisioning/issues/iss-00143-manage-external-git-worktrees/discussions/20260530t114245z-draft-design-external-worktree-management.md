---
created_by_role: spec-dock-system-architect
scope_id: iss-00143
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md
  - spec-dock/active/issue/discussions/20260530t100431z-research-external-worktree-requirement-analysis.md
  - spec-dock/active/issue/discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md
  - spec-dock/active/issue/discussions/20260530t111421z-interview-worktree-root-requirement-for-external-management.md
  - spec-dock/active/issue/discussions/20260530t112038z-interview-external-worktree-post-remove-cleanup.md
  - spec-dock/active/issue/discussions/20260530t112440z-interview-managed-classification-when-root-absent.md
  - spec-dock/active/issue/discussions/20260530t112713z-interview-codex-desktop-specific-scope.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py
  - src/spec_dock/assets/spec_dock/docs/reference_worktree.md
  - spec-dock/docs/reference_worktree.md
  - tests/cli_runtime/test_worktree.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
adoption_ledger_note: "Main orchestrator decides adoption in canonical report.md before any canonical integration."
---

# Draft Design: External Git Worktree Management

## 1. Requirement Coverage

- AC-001 / AC-002: `worktree list` / `show` / `remove` should build inventory from Git worktree records without requiring `SPEC_DOCK_WORKTREE_ROOT`; root state becomes classification diagnostic, not command availability.
- AC-003: `worktree create` keeps the existing `SPEC_DOCK_WORKTREE_ROOT` requirement and `_resolve_worktree_root` behavior.
- AC-004: `worktree remove` should allow external linked worktrees, run Git removal first, then clean only the resolved target path if it remains; local branch deletion stays out of scope.
- AC-005: main checkout, current checkout, bare worktree, and stale record/path-missing remain hard blockers that `--force` cannot bypass.
- AC-006: `managed` remains boolean; classification availability and origin diagnostics are added so `managed=false` can mean either external or unavailable classification.
- AC-007: provider-side runtime/docs/tests are the source of truth; dogfooding docs should be inspected or refreshed after provider-side updates.
- EC-001 / EC-002 / EC-003 / EC-004 / EC-005: ambiguous target, branch-only target, Git remove failure, invalid root diagnostics, and symlink/cleanup containment are addressed below.

## 2. Existing Context Findings

- Current `application/worktree.py` already inventories Git worktree records, resolves targets by stable id / absolute path / basename, and rejects branch-only targets.
- Current `list` / `show` / `remove` call `_resolve_worktree_root_for_command`, so missing or invalid root short-circuits Git inventory. This conflicts with approved issue requirement AC-002.
- Current `_remove_blockers` and `_non_bypassable_remove_blockers` treat `unmanaged` as a hard blocker, and `_guard_remove_containment` also blocks unmanaged paths. This conflicts with approved Option A for external removal.
- Current JSON payload has `managed: bool`, `removable`, and `remove_blockers`, but no classification availability or origin reason field.
- Current docs still state that Codex app worktrees are not managed by this command and that remove only targets SpecDock managed namespace worktrees. That wording is stale for `list/show/remove`, while still correct for Codex-specific lifecycle being out of scope.
- Current tests intentionally assert fail-fast on missing/invalid root and unmanaged remove rejection; those are now regression expectations to update, not preserve.

## 3. Design Decisions

- D-001: Keep Git worktree records as the source of record for `list` / `show` / `remove`.
  - `SPEC_DOCK_WORKTREE_ROOT` is read only to classify SpecDock-created managed placement.
  - Missing / blank / invalid root should not prevent inventory, detail, or removal.
- D-002: Split root handling into create-only required resolution and optional classification context.
  - Keep `_resolve_worktree_root` for `worktree_create`.
  - Replace `_resolve_worktree_root_for_command` use in `_build_inventory` with a non-throwing classification context builder.
- D-003: Preserve `managed: bool` and add flat diagnostics:
  - `managed_classification_available: bool`
  - `classification_reason: "root_valid" | "root_missing" | "root_blank" | "root_invalid" | "namespace_symlink"`
  - `origin: "spec_dock_managed" | "external" | "classification_unavailable"`
  - Optional result-level warning may include invalid root detail, but the per-record fields are the machine-readable contract.
- D-004: Remove `unmanaged` from hard remove blockers.
  - Hard blockers are `main_worktree`, `current_worktree`, `path_missing`, `record_missing`, and `bare_worktree`.
  - Git-level dirty / untracked / locked behavior is surfaced by `git worktree remove`; filesystem cleanup never runs after Git failure.
- D-005: Use a Git-first, target-path-only cleanup model.
  - Re-read Git records immediately before removal and match the canonical target path.
  - After Git remove succeeds, clean only the original resolved target path.
  - Do not delete parent directory, central root, namespace directory, branch, orphan directories, or stale records via prune/repair.
- D-006: Treat Codex Desktop as motivation only.
  - No `$CODEX_HOME/worktrees` detection, Handoff cleanup, environment setup, or Codex metadata cleanup enters runtime scope.

## 4. Alternatives Considered

- Keep `SPEC_DOCK_WORKTREE_ROOT` required for list/show/remove: rejected by approved clarification and would keep external cleanup blocked by environment setup.
- Make `managed` nullable: rejected because requirement preserves boolean JSON compatibility.
- Keep external removal Git-record-only without filesystem cleanup: rejected by approved cleanup clarification.
- Add Codex Desktop-specific origin detection: rejected because the requirement generalizes to Git linked worktrees and parent epic excludes Codex app internals.
- Add prune/repair/orphan cleanup: rejected as explicit non-scope and higher destructive risk.

## 5. Boundary / Contract Model

- In scope:
  - Same-repository Git linked worktrees returned by `git worktree list --porcelain`.
  - Target selectors already supported: stable id, absolute path, basename.
  - Provider-side runtime command, JSON/text output, docs, and focused tests.
- Out of scope:
  - Branch-name targets.
  - Branch deletion.
  - `git worktree prune`, stale record repair, orphan directory cleanup.
  - Codex Desktop-specific paths, metadata, Handoff, or setup behavior.
- Non-bypassable remove guards:
  - main worktree, current worktree, bare worktree, path missing/stale record, record missing after pre-remove refresh.
- Compatibility guard:
  - Existing consumers can continue reading `managed` as boolean. New consumers should prefer `managed_classification_available` and `origin` for interpretation.

## 6. Dependency Analysis

- `commands/worktree.py` should remain thin: argument mapping, use-case invocation, and renderer selection only.
- `application/contracts.py` owns the expanded `WorktreeRecordView` fields and result warnings.
- `application/worktree.py` owns optional classification context, target resolution, remove guard evaluation, and Git-first cleanup sequence.
- `presentation/cli_text.py` owns JSON/text serialization of the new diagnostics.
- `infra/git_cli.py` remains a thin Git adapter; no Codex-specific detection should be added.
- `infra/fs_cli.py` likely needs a safer target cleanup operation or stricter behavior around symlinks/files because `shutil.rmtree` alone is unsafe or incorrect for non-directory targets.
- `tests/cli_runtime/test_worktree.py` is the main regression surface because behavior spans runtime CLI, temp Git repos, JSON payloads, and filesystem cleanup.

## 7. Source of Record

- Linked worktree existence and target identity: `git worktree list --porcelain`.
- Removal semantics for dirty/untracked/locked worktrees: `git worktree remove` / `git worktree remove --force`.
- SpecDock managed placement classification: valid `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` namespace only.
- Command contract and docs: provider-side `src/spec_dock/assets/spec_dock/...`.
- Dogfooding workspace: verification/parity target, not implementation source of truth.

## 8. Data Flow / Domain Model / Interface Contract

1. `worktree list/show/remove` calls `_build_inventory`.
2. `_build_inventory` reads Git records first, resolves `main_record`, and builds an optional classification context:
   - valid root: namespace is available and classification can distinguish managed vs external.
   - missing/blank/invalid root: namespace is unavailable; all records set `managed=false`, `managed_classification_available=false`, `origin=classification_unavailable`.
3. Each `WorktreeRecordView` includes:
   - existing fields: `id`, `path`, `basename`, `branch`, `head`, `managed`, `main`, `current`, `path_exists`, `record_exists`, `removable`, `remove_blockers`
   - new fields: `managed_classification_available`, `classification_reason`, `origin`
4. Remove target resolution remains id/path/basename only.
5. `worktree_remove` re-reads Git records before mutation and rejects if the exact target record is gone.
6. `git_gateway.remove_worktree(..., force=req.force)` runs before any filesystem cleanup.
7. Post-remove cleanup:
   - if target path does not exist: `removed_directory=true` because there is no remaining target directory to clean.
   - if target path is a symlink: remove the symlink itself without following it, or fail closed if filesystem gateway cannot guarantee non-following behavior.
   - if target path is a directory and not a symlink: remove that directory tree only.
   - if target path is another file type: remove only that path if explicitly supported by the filesystem gateway; otherwise fail closed with `post_remove_cleanup_failed`.

Suggested JSON example for root missing:

```json
{
  "managed": false,
  "managed_classification_available": false,
  "classification_reason": "root_missing",
  "origin": "classification_unavailable"
}
```

Suggested JSON example for valid root external worktree:

```json
{
  "managed": false,
  "managed_classification_available": true,
  "classification_reason": "root_valid",
  "origin": "external"
}
```

## 9. File / Module Change Plan

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- application/
|   |-- contracts.py      # change: add classification diagnostics to WorktreeRecordView
|   |-- worktree.py       # change: optional root classification, external remove, target-only cleanup guards
|   `-- ports.py          # change only if filesystem cleanup protocol needs non-following target removal
|-- commands/
|   `-- worktree.py       # change: help text no longer says remove target must be managed
|-- cli/
|   `-- parser.py         # change: remove help text should mention linked worktree, not managed-only
|-- infra/
|   |-- fs_cli.py         # change: safe cleanup for directory/symlink/file target path if protocol changes
|   `-- git_cli.py        # inspect-only unless Git force/remove invocation needs no change
`-- presentation/
    `-- cli_text.py       # change: include classification fields in JSON and useful text diagnostics

src/spec_dock/assets/spec_dock/docs/
`-- reference_worktree.md # change: root-optional list/show/remove, external remove, Codex non-scope

spec-dock/docs/
`-- reference_worktree.md # dogfooding parity inspection or refresh target

tests/cli_runtime/
`-- test_worktree.py      # update stale expectations and add external/root-optional/safety tests
```

## 10. Migration / Compatibility / Rollback

- No persisted SpecDock state migration is required.
- Backward compatibility:
  - `worktree create` remains unchanged.
  - Existing JSON `managed` field remains boolean.
  - Existing target selectors remain supported.
- Behavior intentionally changes:
  - missing/invalid `SPEC_DOCK_WORKTREE_ROOT` no longer fails `list/show/remove`.
  - external/unmanaged linked worktrees are no longer remove-blocked solely due to placement.
- Rollback path:
  - Revert provider-side runtime/docs/tests changes for this issue.
  - No data migration rollback is needed because the command mutates Git/filesystem only when explicitly invoked.

## 11. Observability

- JSON diagnostics should make these states machine-readable:
  - classification available/unavailable
  - classification reason
  - origin: managed, external, unavailable
  - hard remove blockers
  - Git remove failure vs post-remove cleanup failure
  - `removed_record`, `removed_directory`, `branch_deleted=false`
- Text output should remain concise but include classification availability or origin when it prevents misreading `managed=false`.
- Invalid root should be visible as a diagnostic/warning, not as command failure, for list/show/remove.

## 12. Test Strategy

- Update existing tests that now encode stale behavior:
  - invalid/missing root fail-fast for list/show/remove
  - unmanaged list marking remove-blocked
  - unmanaged remove rejection
  - containment guard that assumes managed namespace is the only safe cleanup boundary
- Add or revise focused runtime tests:
  - `list --json` without `SPEC_DOCK_WORKTREE_ROOT` returns all Git records with `managed=false`, unavailable classification diagnostics, and no root error.
  - `show <external> --json` without root works.
  - `remove <external> --json` without root removes Git record, cleans remaining target path, and preserves branch.
  - invalid root produces classification diagnostic rather than availability error for list/show/remove.
  - `create` still fails when root is missing/blank/invalid.
  - main/current/bare/stale/path-missing remain blocked even with `--force`.
  - branch-only and ambiguous targets still stop before Git remove.
  - Git remove failure prevents filesystem cleanup.
  - post-remove cleanup removes only the resolved target path and leaves parent directory.
  - symlink target cleanup does not follow the symlink; either unlink the symlink itself or fail closed with no traversal.
- Suggested verification command after implementation:
  - `python -m unittest tests.cli_runtime.test_worktree -v`
  - broaden to `python -m unittest discover -v` if shared contracts or docs scaffolding behavior changes beyond this command family.

## 13. ADR Candidates

- No required ADR candidate at this point.
- Consider an ADR only if the team wants a durable cross-issue policy that SpecDock may remove external Git-linked worktree directories after Git confirms record removal. Current evidence suggests this can remain issue/epic design because it is bounded to the worktree command family.

## 14. Risks

- Destructive cleanup risk increases because target paths may be outside SpecDock central root. Mitigation: Git-record source of truth, pre-remove refresh, hard main/current/bare/stale guards, target-path-only cleanup, and symlink non-following behavior.
- JSON ambiguity risk remains if consumers read only `managed=false`. Mitigation: explicit `managed_classification_available`, `classification_reason`, and `origin`.
- Invalid root diagnostic could be missed if only warnings carry it. Mitigation: per-record machine-readable fields.
- Existing tests may need careful rewrite because several currently assert the old safety contract.
- Dogfooding docs can drift if provider-side docs are updated without refresh or inspection.

## 15. Requirement Clarification Requests

None.

The requirement already contains approved answers for remove scope, root optional behavior, filesystem cleanup, boolean `managed`, and Codex-specific non-scope. This draft resolves the remaining design-phase field-name and containment details as proposed design decisions, not as new requirement assumptions.

## 16. Integration Notes for Main Orchestrator

- This draft is proposed evidence only and is not reflected into canonical docs.
- Recommended canonical integration:
  - Pull D-001 through D-006 into `design.md`.
  - Convert the test strategy into concrete `plan.md` closure obligations before implementation.
  - Record adoption or rejection in `report.md` Evidence Adoption Ledger before using this draft.
  - Run a fresh `spec-reviewer` after canonical integration.
- Leaf evidence used: none beyond direct repo/docs inspection by this delegated role.
- Rejected portions: none at draft time.
- Blockers: none identified; no requirement clarification request is needed.
- Canonical artifacts edited: none.
- Final authority claimed: no.
- No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.

Delegated Draft Evidence:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00143`
- source artifacts read: see frontmatter `source_paths`
- draft artifact path: `spec-dock/active/issue/discussions/20260530t114245z-draft-design-external-worktree-management.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets: see frontmatter `intended_targets`
- diff_guard_result: `not_run`
- integration notes: main orchestrator must decide adoption and run post-run diff guard before canonical integration
- rejected portions: none
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`
