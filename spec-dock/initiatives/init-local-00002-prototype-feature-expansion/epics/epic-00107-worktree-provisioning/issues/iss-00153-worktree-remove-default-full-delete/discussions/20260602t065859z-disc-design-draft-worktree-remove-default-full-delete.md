---
created_by_role: system-architect
scope_id: iss-00153
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/reference_worktree.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_requirement.md
  - spec-dock/docs/reference_sync.md
  - spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00153-worktree-remove-default-full-delete/discussions/20260602t062811z-interview-worktree-remove-force-compatibility-question.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py
  - tests/cli_runtime/test_worktree.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# Design Draft: iss-00153 Default Full Delete For Worktree Remove

## Requirement Coverage

- AC-001 / AC-002: `worktree remove <target> --json` must remove linked worktrees with untracked files and tracked modifications without requiring `--force`; success keeps `removed_record=true`, `removed_directory=true`, and `branch_deleted=false`.
- AC-003: `--force` remains accepted for backward compatibility but must have the same success and failure contract as default remove. It should not introduce a separate stronger mode in this issue.
- AC-004: main checkout, current checkout, bare worktree, missing path, record missing, and containment guard failures remain hard blockers before Git remove. `--force` must not bypass them.
- AC-005: provider docs, dogfooding docs, CLI help, and tests must stop implying that `--force` is required for dirty / untracked removal.
- EC-001: locked worktree behavior should be documented as Git-adapter bounded. If the existing force depth still fails, return `git_worktree_remove_failed` and skip filesystem cleanup.
- EC-002: if Git record removal succeeds but target-only cleanup fails, preserve `post_remove_cleanup_failed` with `removed_record=true` and `removed_directory=false`.
- EC-003: unmanaged linked worktrees remain removable; unmanaged is diagnostic, not a blocker.

## Existing Context Findings

- Active context identifies `iss-00153` under `epic-00107`; issue requirement is approved, while issue design and plan are still scaffold placeholders.
- The issue report already records D-001: Option B is adopted for `--force` compatibility, with the formal interview artifact reflected into requirement/report.
- Parent epic design currently states the old behavior: default remove uses `git worktree remove <path>`, and `--force` triggers Git force removal. This issue should be framed as a localized contract delta against that accepted epic baseline.
- Current command layer stores `WorktreeRemoveArgs.force`, parses `--force`, and passes `WorktreeRemoveRequest(target=..., force=...)`.
- Current application layer runs hard blockers and containment guard before calling `ports.git_gateway.remove_worktree(..., force=req.force)`.
- Current Git adapter only appends `--force --force` when `force=True`; therefore default remove currently exposes Git's clean-worktree-only behavior.
- Current tests include a characterization named `test_worktree_remove_dirty_default_fails_and_force_removes_directory`, which should become the primary red test for the changed contract.
- Existing remove tests already cover branch retention, unmanaged removal, main/current/bare/path_missing/record_missing hard blockers, containment guard, Git failure without cleanup, target-only cleanup, and cleanup failure reporting.

## Design Decisions

- DD-001: Treat full delete as the default application contract. The application use case should always request Git force removal for eligible remove targets, independent of whether the user supplied `--force`.
- DD-002: Keep the CLI `--force` flag as compatibility input. Parser support remains, but its help text should say the flag is accepted for compatibility and is no longer required for full delete.
- DD-003: Keep `WorktreeRemoveRequest.force` only if useful for compatibility observability or future deprecation tracking. It must not select a weaker or stronger delete path in this issue.
- DD-004: Prefer the smallest implementation delta: change the application call to the Git gateway to pass force-equivalent removal unconditionally after guards pass.
- DD-005: Keep the Git gateway API name and implementation shape. `GitGateway.remove_worktree(repo_root, path, force)` can remain; the use case can pass `force=True` for the new default. A deeper rename to `force_remove` is not necessary for this issue.
- DD-006: Do not change branch lifecycle. `branch_deleted` remains false, and no branch deletion adapter call is introduced.
- DD-007: Do not broaden cleanup. Filesystem cleanup remains Git-first and target-only, only after Git remove succeeds.
- DD-008: Keep locked worktree as Git-determined failure. The current adapter sends `--force --force` for force removal; if Git still rejects a locked target, surface the existing Git error and do not clean up the filesystem target.

## Alternatives Considered

- Alternative A: Remove `--force` from CLI. Rejected because the user-approved interview chose Option B and parent epic quality gates favor backward compatibility.
- Alternative C: Preserve `--force` as a special stronger mode only for locked worktrees. Rejected for this issue because it keeps a meaningful force-mode distinction and conflicts with "default full delete" UX.
- Adapter rename / contract split: Introduce `remove_worktree_force` or a new enum. Not recommended because the existing boundary already hides Git flag depth, and only the caller default changes.
- Filesystem-first cleanup: Rejected. Requirement and parent design require Git-first semantics to avoid deleting directories while Git records remain.

## Boundary / Contract Model

- CLI boundary:
  - `spec-dock worktree remove <target> [--force] [--json]` remains the accepted shape.
  - `--force` is a deprecated or compatibility-only input, not a required full-delete switch.
- Application boundary:
  - Resolve target and refresh inventory as today.
  - Reject hard blockers before calling Git.
  - Guard containment before and after Git remove as today.
  - Call Git remove using force-equivalent behavior for all eligible removes.
  - Preserve existing `WorktreeCommandError` variants.
- Infra boundary:
  - `git_cli.remove_worktree(..., force=True)` continues to map to `git worktree remove --force --force <path>`.
  - No branch deletion is added.
- Presentation boundary:
  - Success JSON/text output can stay structurally unchanged.
  - Error JSON/text output can stay structurally unchanged.
  - CLI help/docs wording must change to remove the implication that default dirty removal fails by design.

## Dependency Analysis

- Upstream source of record is the approved issue requirement plus the user-approved Option B interview.
- Implementation dependency direction remains unchanged:
  - `commands/worktree.py` parses args and builds `WorktreeRemoveRequest`.
  - `application/worktree.py` owns target resolution, blocker policy, containment, and cleanup orchestration.
  - `application/ports.py` defines `GitGateway.remove_worktree`.
  - `infra/git_cli.py` owns concrete Git CLI flags.
  - `presentation/cli_text.py` renders remove success/error.
  - `tests/cli_runtime/test_worktree.py` validates the observable CLI/runtime contract.
- Lowest-risk implementation start is the runtime test that currently asserts default dirty removal fails. After red, the application call site can be updated with a single behavior change.
- No domain aggregate, persistence model, active pointer, sync artifact, GitHub issue, or branch lifecycle dependency changes.

## Source of Record

- Behavioral SoR:
  - `spec-dock/active/issue/requirement.md`
  - `discussions/20260602t062811z-interview-worktree-remove-force-compatibility-question.md`
- Parent boundary SoR:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
- Runtime implementation SoR:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
- Shipped docs SoR:
  - provider-side `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` should be changed first if implementation updates docs.
  - dogfooding `spec-dock/docs/reference_worktree.md` should be refreshed or inspected for parity after provider-side change.

## Data Flow / Domain Model / Interface Contract

Current flow:

1. CLI parses `worktree remove <target> [--force] [--json]`.
2. Command creates `WorktreeRemoveRequest(target, force)`.
3. Application builds inventory from Git records.
4. Application resolves target by id, absolute path, or basename.
5. Application rejects non-bypassable blockers.
6. Application refreshes inventory and verifies the target did not change.
7. Application applies containment guard.
8. Application calls `GitGateway.remove_worktree(repo_root, path, force=req.force)`.
9. Application removes leftover target path only after Git success.
10. Presentation renders result or `WorktreeCommandError`.

Proposed flow delta:

- Step 8 becomes force-equivalent regardless of request flag:
  - `force=True` or equivalent local constant such as `full_delete=True`.
- The request flag remains accepted but does not select delete strength:
  - Optional design note in canonical design: `force` is retained as compatibility input and may be removed from internal contracts later only by a separate deprecation issue.

Contract changes:

- `WorktreeRemoveRequest.force`:
  - from: user-selected Git force removal.
  - to: compatibility flag accepted by CLI; delete strength is always full-delete for eligible targets.
- `GitGateway.remove_worktree(..., force)`:
  - no required signature change.
  - call contract should state that issue-level full delete passes `force=True`.
- CLI help:
  - from: "Pass --force to git worktree remove."
  - to: "Accepted for compatibility; remove already performs full target deletion for eligible worktrees."

## File / Module Change Plan

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
|-- commands/worktree.py
|   `-- change: revise --force help text; keep parser compatibility
|-- application/worktree.py
|   `-- change: call Git remove with force-equivalent behavior after hard blockers and containment guards pass
|-- infra/git_cli.py
|   `-- likely no code change; keep --force --force mapping for force=True
|-- application/contracts.py
|   `-- likely no code change; optionally document compatibility meaning in canonical design, not code comments unless needed
|-- application/ports.py
|   `-- likely no code change; existing protocol remains sufficient
`-- presentation/cli_text.py
    `-- likely no output schema change

src/spec_dock/assets/spec_dock/docs/
`-- reference_worktree.md
    `-- change: describe default full delete and --force compatibility wording

spec-dock/docs/
`-- reference_worktree.md
    `-- dogfooding refresh/inspection target after provider update

tests/cli_runtime/
`-- test_worktree.py
    `-- change: update dirty/untracked default test; add tracked modification default test; keep --force compatibility test and hard blocker tests
```

## Migration / Compatibility / Rollback

- Migration:
  - No persisted SpecDock state migration.
  - Existing scripts using `worktree remove <target> --force` continue to work.
  - Existing scripts using `worktree remove <target>` now delete dirty / untracked eligible worktrees where they previously failed.
- Compatibility:
  - CLI shape remains backward compatible.
  - JSON success/error schema remains backward compatible.
  - Branch retention remains backward compatible.
  - Hard blockers remain backward compatible.
- Rollback:
  - Revert the application call from force-equivalent default back to request-selected force.
  - Revert docs/help wording and the updated tests.
  - Worktrees removed before rollback are normal local Git/filesystem side effects and cannot be automatically restored by SpecDock.

## Observability

- Success remains observable through:
  - exit code 0
  - `removed_record=true`
  - `removed_directory=true`
  - `branch_deleted=false`
  - absence of target path from `git worktree list --porcelain`
  - branch still present in `git branch --list`
- Failure remains observable through:
  - `remove_blocked` for hard blockers before Git remove
  - `git_worktree_remove_failed` when Git refuses even force-equivalent removal
  - `post_remove_cleanup_failed` when Git record removal succeeded but target-only cleanup failed
- No new telemetry, log file, sync artifact, active state, or report output is required.

## Test Strategy

- AC-001:
  - Update the existing dirty/untracked test so `worktree remove dirty --json` succeeds without `--force`.
  - Assert Git record removal, target path absence, `removed_record=true`, `removed_directory=true`, `branch_deleted=false`, and branch retention.
- AC-002:
  - Add a tracked modification case, for example modify a committed tracked file in the linked worktree, then run default remove and assert the same success contract.
- AC-003:
  - Keep or add a `--force` invocation against an untracked or modified worktree and assert it matches default behavior.
- AC-004:
  - Reuse existing hard blocker tests. Ensure at least one path still passes `force=True` and verifies Git remove is not called.
- AC-005:
  - Add or update CLI help assertion for `worktree remove --help`.
  - Update provider/dogfooding docs inspection obligations in plan.
- EC-001:
  - Keep locked-worktree test as Git-dependent guarded behavior. Update expectations so default uses force-equivalent behavior; if Git refuses locked removal even with current force depth, expect `git_worktree_remove_failed` and no cleanup.
- EC-002:
  - Existing application tests for cleanup failure remain sufficient if they still pass after the application default changes.
- EC-003:
  - Existing unmanaged remove tests remain relevant; add default no-`--force` coverage only if current tests all use `--force`.

Recommended focused verification:

```bash
python -m unittest tests.cli_runtime.test_worktree.TestCliWorktree -v
```

Broader final verification can remain `python -m unittest discover -v` if implementation changes are small but touch shipped runtime behavior.

## ADR Candidates

- none.
- Rationale: Option B is issue-local CLI compatibility behavior. It is documented in the user-approved interview and can be promoted into issue design/report without a durable ADR.

## Risks

- Risk: Passing `--force --force` by default is destructive for eligible dirty worktrees. This is intentional per requirement, but docs/help must make the new default explicit.
- Risk: Locked worktree behavior may vary by Git version. Keep tests guarded and design the failure contract around surfaced Git error rather than requiring universal success.
- Risk: The internal `force` field name may become misleading. A full rename is not required now, but canonical design should note that it is compatibility input, not strength selection.
- Risk: Parent epic/reference docs contain old force wording. Canonical design should call out required docs refresh to avoid stale guidance.

## Requirement Clarification Requests

none.

## Integration Notes for Main Orchestrator

- Suggested canonical `design.md` adoption:
  - Add this as delegated design evidence in `report.md` Evidence Adoption Ledger before reflecting into canonical design.
  - Promote the Option B compatibility decision into `採用方針 / トレードオフ`.
  - Promote the module flow and file plan into `依存関係分析`, `インターフェース契約`, and `ディレクトリ / ファイル変更計画`.
  - Promote AC/EC mapping into `要件 -> 設計マッピング` and `テスト戦略`.
- Suggested `plan.md` downstream:
  - S01 runtime behavior slice: red/update default untracked and tracked modification tests, implement application default full delete, verify hard blockers.
  - S90 docs/help slice: update help and provider/dogfooding docs, then inspect parity.
- Rejected portions:
  - none.
- Blockers:
  - none.
- Frontmatter note:
  - `diff_guard_result` is `not_run`; post-run diff guard remains orchestrator-owned.
- Delegated draft evidence block:
  - role: `system-architect`
  - phase: requirement/design
  - scope: `iss-00153`
  - source artifacts read: see frontmatter `source_paths`
  - draft artifact path: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00153-worktree-remove-default-full-delete/discussions/20260602t065859z-disc-design-draft-worktree-remove-default-full-delete.md`
  - draft status: `produced`
  - authority: `proposed`
  - adoption_status: `unreviewed`
  - reflected_to: `[]`
  - intended_targets:
    - `spec-dock/active/issue/design.md`
    - `spec-dock/active/issue/plan.md`
    - `spec-dock/active/issue/report.md`
  - diff_guard_result: `not_run`
  - integration notes: adopt module flow, Option B contract, file plan, and AC/EC test mapping into canonical design after orchestrator review
  - rejected portions: `none`
  - blockers: `none`
  - canonical artifacts edited: `none`
  - final authority claimed: `no`

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
