---
created_by_role: spec-dock-system-architect
scope_id: iss-00147
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/issue/discussions/20260531t141121z-research-uninstall-repo-analysis-evidence.md
  - spec-dock/active/issue/discussions/20260531t141123z-disc-uninstall-requirement-risk-synthesis.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_clarification.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/reference_sync.md
  - src/spec_dock/cli.py
  - src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
  - src/spec_dock/assets/install_root/
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
  - tests/test_init_update.py
  - tests/cli_runtime/test_update.py
  - tests/cli_runtime/harness.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: manual_orchestrator_check_passed_new_issue_discussion_only
---

# Uninstall Design Draft

## 1. Requirement Coverage

- Requirement source revision:
  - `iss-00147` frontmatter: `状態: "approved"`, `最終更新: "2026-05-31"`.
- Covered requirement clusters:
  - Installer CLI: add `spec-dock uninstall [path]` without changing `init` / `update` behavior.
  - Repo-local runtime: add `./spec-dock/scripts/spec-dock uninstall` as a thin wrapper that calls the installer CLI implementation.
  - Removal modes: real deletion requires explicit specs handling, proposed as exactly one of `--keep-specs` or `--remove-specs`.
  - Dry-run / plan: default invocation should produce an operator-visible plan without filesystem mutation.
  - Inventory classification: known SpecDock agent / skill paths are core removal targets; bootstrap-only and product-reusable files require exact content match for auto-removal.
  - Result reporting: removed, would_remove, already_removed, preserved, failed, and empty_dirs must be distinguishable.
  - Safety: no Python package, global CLI, uvx cache, parent directory, `.git`, unknown unmanaged path, or remote GitHub state mutation.
  - Idempotency: missing managed artifacts are no-op / already removed rather than fatal.

## 2. Existing Context Findings

- `src/spec_dock/cli.py` is the installer entrypoint and currently owns `init` / `update`, target path validation, scaffold sync, install-root asset sync, manifest validation, and repo-root `spec` shortcut creation.
- `_install_spec_dock()` owns `spec-dock/{docs,templates,scripts,system}`, `spec-dock/.gitignore`, `spec-dock/active`, `spec-dock/.agent`, `spec-dock/spec-dock.version`, and the repo-root `spec` symlink creation.
- `_build_managed_skill_install_plan()` and related helpers already produce current install-root file mappings plus `bootstrap_only_exact_file_paths` and `obsolete_exact_file_paths` from `.agents/host-adapters/meta.json`.
- `.agents/host-adapters/meta.json` currently marks `.codex/config.toml` as bootstrap-only and defines Codex / Copilot native shim ownership.
- `src/spec_dock/assets/install_root/` is the provider-side authority for shipped agent tooling assets, including `.agents/skills/**`, `.codex/agents/**`, `.codex/prompts/**`, `.codex/rules/**`, `.codex/AGENTS.md`, `.github/agents/**`, and `.github/workflows/ci.yml`.
- Runtime `update` already establishes the desired wrapper pattern: it does not reimplement installer logic; it shells out to `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` and propagates stdout, stderr, and exit code.
- Runtime command integration requires a command module, `cli/registry.py` registration, and `cli/parser.py` parser binding.
- Existing tests split installer behavior under `tests/test_init_update.py` and runtime wrapper behavior under `tests/cli_runtime/test_update.py`.
- `reference_sync.md` confirms `.agent/**` and `active/**` are generated runtime state, not product specification history.

## 3. Design Decisions

- Put destructive uninstall implementation in installer CLI, not repo-local runtime.
  - Reason: repo-local runtime files are themselves removal targets. A thin wrapper leaves recovery and rerun available through external `spec-dock uninstall <target>`.
- Add `uninstall` to installer parser as an additive subcommand.
  - Proposed shape:
    - `spec-dock uninstall [path]` renders a dry-run plan.
    - `spec-dock uninstall [path] --apply --keep-specs` performs removal while preserving `spec-dock/initiatives/**`.
    - `spec-dock uninstall [path] --apply --remove-specs` performs removal including `spec-dock/initiatives/**`.
    - `--keep-specs` and `--remove-specs` are mutually exclusive.
    - `--apply` without exactly one specs mode fails before mutation.
- Represent uninstall as a plan/result model before filesystem mutation.
  - The inventory pass should classify paths and produce deterministic actions first.
  - The apply pass should execute actions and update statuses without recomputing ownership rules mid-delete.
- Use category-based ownership, not a single exact-match rule.
  - Known `.agents/skills/**`, `.codex/agents/**`, and `.github/agents/**` shipped or obsolete managed agent files are deleted even on content mismatch.
  - Bootstrap-only and product-reusable shipped files are removed only when current content equals the package asset bytes.
  - Unknown files under managed boundary roots are preserved.
- Compare against the currently executing installer package assets.
  - This matches `init` / `update` package authority and avoids relying on installed repo metadata that may be stale or missing.
- Cleanup only empty directories inside explicit boundary roots.
  - Proposed boundary roots: `.agents`, `.codex`, `.github`, and `spec-dock`.
  - Directory cleanup must walk upward only from removed files and stop at the boundary root, repo root, non-empty directories, or filesystem errors.

## 4. Alternatives Considered

- Runtime self-removal implementation:
  - Rejected. It couples deletion to files being deleted and weakens recovery after partial failure.
- Reuse `delete` command:
  - Rejected. Existing `delete` is local spec node lifecycle, while uninstall is repo-local managed tooling removal.
- Exact content match for all managed assets:
  - Rejected. It would preserve modified agent / skill assets and fail the primary objective of removing SpecDock agent discovery noise.
- Delete all files under `.agents`, `.codex`, `.github`, and `spec-dock`:
  - Rejected. It would silently remove user-authored or product-reused content.
- Make `--keep-specs` the implicit apply default:
  - Rejected for apply mode. Requirement says real deletion must require explicit specs handling.

## 5. Boundary / Contract Model

- Installer command contract:
  - Input: target repo path, dry-run/apply mode, specs mode, optional machine-readable output if main orchestrator later chooses to add `--json`.
  - Output: human-readable plan/result with stable status buckets.
  - Exit code:
    - `0`: dry-run completed or apply completed without failed removals.
    - `1`: apply had one or more failed removals or unrecoverable inventory/comparison error.
    - `2`: CLI usage error, invalid target, missing specs mode for apply, or mutually exclusive flags.
- Runtime command contract:
  - Input: optional path and pass-through uninstall flags that are intentionally supported by the installer.
  - Invocation: `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock uninstall <target> ...`.
  - Output: propagate installer stdout, stderr, and exit code.
  - Missing `uvx`: same style as update, exit `127` with actionable PATH guidance.
- Ownership boundary:
  - The command owns only known SpecDock-managed paths and generated state under explicit target repo boundaries.
  - The command never interprets product-specific meaning of unknown files.

## 6. Dependency Analysis

- Upstream dependencies:
  - `src/spec_dock/assets/install_root/` file inventory.
  - `.agents/host-adapters/meta.json` for bootstrap-only and obsolete exact file path contracts.
  - `src/spec_dock/assets/spec_dock/` for managed scaffold docs/templates/scripts/system comparisons.
  - Current installer CLI target path validation and `_require_specdock()` behavior.
- Module dependencies:
  - Installer uninstall helpers should stay in `src/spec_dock/cli.py` initially unless size forces a focused internal module. This keeps parity with existing installer architecture and avoids a broader package restructuring.
  - Runtime uninstall should mirror `commands/update.py`; it should not depend on application use cases.
  - Parser and registry changes depend on the new runtime command module.
- Test dependencies:
  - Installer tests can call `spec_dock.cli.main([...])` directly via existing harness patterns.
  - Runtime wrapper tests can reuse the `uvx` stub pattern from `test_update.py`.

## 7. Source of Record

- Shipped install-root assets:
  - `src/spec_dock/assets/install_root/`.
- Shipped scaffold assets:
  - `src/spec_dock/assets/spec_dock/{docs,templates,scripts,system,.gitignore}`.
- Spec history:
  - target repo `spec-dock/initiatives/**`.
- Generated runtime state:
  - target repo `spec-dock/.agent/**`, `spec-dock/active/**`, and generated diagrams/dashboard described by `reference_sync.md`.
- Runtime wrapper precedent:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`.
- Canonical user-facing contract after adoption:
  - `spec-dock/active/issue/design.md`, then `plan.md`; this draft is unreviewed evidence only.

## 8. Data Flow / Domain Model / Interface Contract

- Proposed data objects:
  - `UninstallMode`:
    - fields: `apply: bool`, `specs_mode: "keep" | "remove" | None`.
  - `UninstallCategory`:
    - examples: `agent_skill`, `native_agent`, `bootstrap_only`, `product_reusable`, `scaffold_managed`, `generated_state`, `spec_history`, `shortcut`, `obsolete_managed`, `unmanaged`.
  - `ContentPolicy`:
    - values: `delete_even_if_mismatch`, `delete_if_exact_match`, `delete_by_mode`, `delete_if_shortcut_target_matches`, `preserve`.
  - `UninstallAction`:
    - fields: `rel_path`, `entry_kind`, `category`, `policy`, `planned_operation`, `reason`, `source_asset_rel`.
  - `UninstallActionResult`:
    - fields: `rel_path`, `category`, `status`, `reason`, `error`.
  - `UninstallResult`:
    - fields: `target_root`, `dry_run`, `specs_mode`, `actions`, `empty_dirs`, `summary`, `exit_code`.
- Proposed flow:
  - Resolve target root and require `spec-dock/` exists.
  - Build current managed mappings from package assets.
  - Build uninstall inventory:
    - current install-root files.
    - obsolete exact files from manifest.
    - managed scaffold files and directories.
    - generated state files/directories.
    - spec history root.
    - repo-root `spec` shortcut.
  - Classify each candidate by category and content policy.
  - Render dry-run if `apply` is false.
  - If applying, execute file/symlink removals first, then bounded empty directory cleanup.
  - Render result with removed, already_removed, preserved, failed, and empty_dirs.
- Content comparison contract:
  - Compare bytes for regular files.
  - Preserve on symlink/file-type mismatch unless the category explicitly supports symlink target verification.
  - Preserve on read/comparison error except core agent / skill removal targets where ownership is known by path.
- Shortcut contract:
  - Delete repo-root `spec` only if it is a symlink whose normalized target is `spec-dock/scripts/spec-dock`.
  - Preserve regular file, directory, missing target mismatch, or unrelated symlink target.

## 9. File / Module Change Plan

```text
src/spec_dock/
|-- cli.py
|   `-- change: add installer uninstall parser, inventory/result helpers, content comparison, apply, rendering
|-- assets/
|   |-- install_root/
|   |   `-- read-only source: managed agent/tooling inventory and manifest contracts
|   `-- spec_dock/
|       |-- docs/templates/system/scripts
|       |   `-- read-only source: scaffold comparison inventory
|       `-- scripts/spec_dock_runtime/
|           |-- commands/uninstall.py
|           |   `-- add: thin uvx wrapper for installer uninstall
|           |-- commands/update.py
|           |   `-- read-only precedent
|           |-- cli/registry.py
|           |   `-- change: register uninstall command
|           `-- cli/parser.py
|               `-- change: bind uninstall parser
tests/
|-- test_init_update.py
|   `-- change/add: installer uninstall tests
`-- cli_runtime/
    `-- test_uninstall.py
        `-- add: runtime wrapper tests mirroring update
```

- No implementation change is made by this draft.
- Dogfooding `spec-dock/` generated workspace may need inspection after implementation, but direct consumer-side edits are not part of this design draft.

## 10. Migration / Compatibility / Rollback

- Migration:
  - Additive CLI command; existing managed repos continue to work until operator explicitly runs uninstall.
  - Older managed repos may contain obsolete exact files listed in manifest; uninstall should report and remove known obsolete files according to category policy.
- Compatibility:
  - `init` / `update` behavior should remain unchanged.
  - After `--keep-specs`, future development recovery is `spec-dock init/update <target>` from installer CLI, with preserved `spec-dock/initiatives/**`.
  - After `--remove-specs`, recovery requires reinitializing from scratch; the result output should state that spec history was removed.
- Rollback:
  - There is no automatic rollback after deletion.
  - Safety is provided by dry-run default, explicit apply mode, exact-match preservation for user-owned candidates, and idempotent rerun.
  - If apply partially fails, rerun from installer CLI after addressing filesystem permissions or preserved conflicts.

## 11. Observability

- Dry-run output should include:
  - target root.
  - apply mode: false.
  - specs mode: `not_selected`, `keep`, or `remove`.
  - planned removal buckets.
  - preserved/manual-review buckets with reasons.
  - empty directory cleanup plan.
- Apply output should include:
  - removed files/symlinks.
  - already removed candidates.
  - preserved paths with reason.
  - failed removals with error text.
  - removed empty directories.
  - final summary counts.
- Runtime wrapper should preserve installer stdout/stderr separation and exit code.
- If future `--json` is added, it should serialize the same result model rather than a separate data shape.

## 12. Test Strategy

- Installer CLI tests in `tests/test_init_update.py` or a focused new installer test module:
  - `spec-dock uninstall <target>` dry-run has exit `0` and makes no filesystem changes.
  - `--apply` without `--keep-specs` / `--remove-specs` fails before mutation.
  - `--apply --keep-specs` removes known agent / skill assets and preserves `spec-dock/initiatives/**`.
  - `--apply --remove-specs` removes spec history and reports it explicitly.
  - bootstrap-only `.codex/config.toml` exact match is removed; mismatch is preserved with manual-review reason.
  - product-reusable `.github/workflows/ci.yml`, `.codex/prompts/**`, `.codex/rules/**`, `.codex/AGENTS.md` exact match is removed; mismatch is preserved.
  - known managed agent / skill mismatch is removed.
  - unknown files under `.agents`, `.codex`, `.github`, and `spec-dock` are preserved.
  - repo-root `spec` symlink to `spec-dock/scripts/spec-dock` is removed; nonmatching symlink or regular file is preserved.
  - generated `spec-dock/.agent/**` and `spec-dock/active/**` are removed or skipped according to design, without deleting preserved specs.
  - empty directory cleanup removes only empty directories inside boundary roots and does not remove repo root, `.git`, target parent, or directories containing preserved files.
  - rerun after prior removal reports already removed / preserved and exits successfully when no failed removals remain.
  - injected permission/unlink failure produces non-zero exit and distinguishes failed from preserved and removed.
- Runtime wrapper tests in `tests/cli_runtime/test_uninstall.py`:
  - help describes dry-run default, `uvx --no-cache`, upstream source, default current working directory, and explicit specs mode.
  - default target passes resolved current working directory to installer uninstall.
  - explicit target is resolved and passed through.
  - supported uninstall flags are forwarded.
  - subprocess failure stdout/stderr/exit code are propagated.
  - missing `uvx` exits `127` with actionable error.
  - unsupported source/cache override options are rejected without invoking `uvx`, matching update's safety style if such options are not defined.
- Verification bundle after implementation:
  - focused unittest targets first.
  - `python -m unittest discover -v` if change size warrants full regression.
  - `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync --no-github` only if dogfooding workspace state is intentionally refreshed or inspected.

## 13. ADR Candidates

- No ADR is required for the initial issue design.
- Rationale:
  - The main decisions are local to uninstall command behavior and already anchored in issue/epic requirement.
  - Category-based removal is important, but reversible and better captured as issue design plus tests.
- Revisit ADR only if future work wants uninstall policy to become a cross-issue/global managed asset lifecycle rule.

## 14. Risks

- Version drift risk:
  - Comparing target files to current package assets may preserve older but valid SpecDock-managed files as mismatches.
  - Mitigation: report preserved/manual-review clearly; keep agent / skill core removal path-based.
- Over-delete risk:
  - Path-prefix classification can accidentally own user files if too broad.
  - Mitigation: known managed candidates should come from shipped inventory, manifest obsolete exact paths, explicit generated-state roots, and exact boundary rules; unknown files preserve.
- Under-delete risk:
  - Conservative preservation may leave some product-reused SpecDock prompts/configs behind.
  - Mitigation: result summary should make preserved manual-review items visible.
- Self-removal risk:
  - Runtime script may be deleted during uninstall.
  - Mitigation: runtime command delegates to external installer process and tells operator to rerun installer CLI directly if recovery is needed.
- Platform risk:
  - Symlink behavior differs across OSes.
  - Mitigation: tests should skip symlink-specific assertions where symlinks are unsupported and separately cover regular-file preservation.
- Large output risk:
  - Full inventory output can be noisy.
  - Mitigation: summary first with grouped detailed paths below; keep enough detail for manual review.

## 15. Requirement Clarification Requests

none

## 16. Integration Notes for Main Orchestrator

- Recommended canonical design adoption:
  - Adopt installer/runtime split, category-based inventory, result model, bounded cleanup, and test surface into `design.md`.
  - Decide whether exact flag names `--apply`, `--keep-specs`, and `--remove-specs` should be canonical or adjusted to existing CLI wording before plan authoring.
  - Reflect test obligations into `plan.md` as step-local closure cases.
- Delegated draft evidence:
  - role: `spec-dock-system-architect`
  - phase: requirement/design
  - scope: `iss-00147`
  - source artifacts read:
    - `spec-dock/active/issue/requirement.md`
    - `spec-dock/active/epic/requirement.md`
    - `spec-dock/active/epic/design.md`
    - `src/spec_dock/cli.py`
    - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_update.py`
  - draft artifact path: `spec-dock/active/issue/discussions/20260531t141545z-disc-uninstall-design-draft.md`
  - draft status: `produced`
  - authority: `proposed`
  - adoption_status: `unreviewed`
  - reflected_to: `[]`
  - intended_targets:
    - `spec-dock/active/issue/design.md`
    - `spec-dock/active/issue/plan.md`
    - `spec-dock/active/issue/report.md`
  - diff_guard_result: `manual_orchestrator_check_passed_new_issue_discussion_only`
  - integration notes:
    - This draft should be adopted only by the main orchestrator through canonical `design.md` / `plan.md` / `report.md` updates and a fresh `spec-reviewer` pass.
  - rejected portions, if any: none
  - blockers, if any: none
  - canonical artifacts edited: none
  - final authority claimed: no
