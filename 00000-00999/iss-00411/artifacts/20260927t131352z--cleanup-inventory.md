# Issue #411 cleanup inventory

## 1. Provenance

- Repository: `chemitaro/spec-dock`
- Branch: `iss-00411-retired-cli-surface-cleanup`
- Verified full tip SHA: `d7c816d11bee1a73cb87273b15e486c3b669206c`
- Inspection method: connected GitHub repository, every file read with the verified full SHA as `ref`
- Authority rule: `src/spec_dock/` is provider source; `spec-dock/` is the current repository's dogfood consumer projection
- Scope: source, caller, test, CI, docs inventory for Issue #411; no code or GitHub write was performed while producing this artifact

This inventory is an implementation ledger. The implementation must update `決定` and `移植先 / 証拠` as each gate completes; a `VERIFY-THEN-REMOVE` item must not be deleted while its evidence cell is incomplete.

## 2. Status legend

| Status | Meaning |
|---|---|
| `REMOVE-CONFIRMED` | The observed role is retired execution/test wiring. Delete after the listed current regression is green. |
| `UPDATE-CURRENT` | The file is a current caller or current-looking guide but points at a retired path. |
| `RETAIN-CURRENT` | The file is required by the current fixed-engine route, safety, installation, migration, or a shared invariant. |
| `RETAIN-HISTORICAL` | Keep as explicitly non-current evidence. Do not make it pass current-command string scans. |
| `VERIFY-THEN-REMOVE` | Likely old-only, but current transitive use or a unique regression must be checked first. |
| `ADD-CURRENT` | Add a new current-only module, test, or artifact required by this cleanup. |
| `VERIFY-ONLY` | Expected to remain unchanged; inspect for links, stale references, or parity impact. |

## 3. Current source and caller roots

| Root | Observed source / caller | Decision | Required evidence |
|---|---|---|---|
| Installed command | `pyproject.toml` maps `spec-dock = "spec_dock.cli:main"` | `RETAIN-CURRENT` | Entry-point integration test stays green. |
| Package public entry | `src/spec_dock/cli.py::main` imports and calls `spec_dock.external_cli.main` | `UPDATE-CURRENT` | Remove `legacy_installer_main` and old installer imports; keep public `main`. |
| Fixed engine | `src/spec_dock/fixed_bundle.py` builds an isolated distribution and executable | `RETAIN-CURRENT` | Isolation and digest tests stay green. |
| External runtime | `src/spec_dock/external_cli.py` loads current parser/runtime and fixed-engine context | `UPDATE-CURRENT` | Change only asset-root import from `installer.ASSETS` to neutral `asset_layout.ASSETS`. |
| Repository shim | `src/spec_dock/assets/spec_dock/scripts/spec-dock` verifies repository engine control and `exec`s the fixed engine | `RETAIN-CURRENT` | Byte equality with `src/spec_dock/shim_vnext.py` and no old app import. |
| Current parser | `spec_dock_runtime/cli/options.py` uses current catalog and `reject_legacy` | `RETAIN-CURRENT` | 44-leaf parsing/help/JSON tests. |
| Current dispatcher | `spec_dock_runtime/cli/vnext_runtime.py` imports current `*_vnext` commands and selected shared use cases | `RETAIN-CURRENT` | Current command/integration suite. |
| Tombstone | `spec_dock_runtime/cli/legacy.py` rejects retired roots and names replacements | `RETAIN-CURRENT` | Representative old roots return current error and never execute old code. |
| Fixed CI validator | `.github/scripts/specdock-ci-validate.sh` checks full SHA, clean source, digest, and runs `workspace validate --ci --json` | `RETAIN-CURRENT` | Existing integration test plus workflow-wiring assertion. |

## 4. Package and installer inventory

| Path / symbol | Observed role | Decision | Implementation action | Migration / test evidence |
|---|---|---|---|---|
| `src/spec_dock/cli.py::legacy_installer_main` | Test-only parser for old `init`, `update`, `uninstall`; calls old directory installer | `REMOVE-CONFIRMED` | Delete after old tests are migrated. Simplify file to public fixed-engine entry. | `test_public_entrypoint_rejects_retired_installer_before_write` remains; current installation tests cover supported operations. |
| `src/spec_dock/installer.py::ASSETS` | Current `external_cli.py` dependency and old installer dependency | `UPDATE-CURRENT` | Move to `src/spec_dock/asset_layout.py`; update current imports. | Import/reference scan shows no current import from `installer.py`. |
| Other constants in `installer.py` | Possibly used by old tests and possibly current distribution assertions | `VERIFY-THEN-REMOVE` | Move only constants reached by current roots to `asset_layout.py`; do not move old behavior. | `rg` + AST import scan; provider distribution tests use neutral module. |
| `src/spec_dock/installer.py::{install,uninstall,_copy,_sources,...}` | Retired non-journaled directory installer | `REMOVE-CONFIRMED` after shared-symbol split | Delete module once no current import remains. | Current installation init/update/uninstall integration suite green; old nontransactional contract is not preserved. |
| `src/spec_dock/asset_layout.py` | New neutral asset-location module | `ADD-CURRENT` | Define side-effect-free `ASSETS` and any proven current layout constants. | Unit test validates paths exist inside source and fixed distribution. |
| `src/spec_dock/external_cli.py` | Current fixed engine entry; imports `installer.ASSETS` | `UPDATE-CURRENT` | Import from `asset_layout`; otherwise avoid security-boundary rewrite. | Existing entrypoint, tamper, digest, checkout-isolation tests. |
| `src/spec_dock/fixed_bundle.py` | Copies package into isolated fixed distribution | `RETAIN-CURRENT` | No behavior change except consequences of retired files being absent. | New distribution-absence test. |
| `src/spec_dock/runtime_loader.py` | Engine pin / digest verification | `RETAIN-CURRENT` | No cleanup-driven change. | Existing engine locator / tamper tests. |
| `src/spec_dock/shim_vnext.py` | Provider copy of current shim | `RETAIN-CURRENT` | Keep byte-equal with shipped shim. | Provider distribution test. |

## 5. Runtime CLI inventory

### 5.1 Retired shell

| Path | Observed caller | Decision | Required action / gate |
|---|---|---|---|
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` | `tests/fixtures/legacy_spec_dock.script`; old app stack | `REMOVE-CONFIRMED` | Delete after old fixture lane is removed. Assert absent from fixed distribution. |
| `.../cli/parser.py` | old app / legacy inventory test; defines old roots | `REMOVE-CONFIRMED` | Delete; remove old parser import from `test_cli_vnext_contract.py`. |
| `.../cli/registry.py` | old app; imports old command modules | `REMOVE-CONFIRMED` | Delete after command modules/test callers are handled. |
| `.../cli/dispatch.py` | old app; dispatches `CommandRegistry` to old `UseCases` | `REMOVE-CONFIRMED` | Delete after old command contracts/tests are removed. |
| `.../cli/bootstrap.py` | old fixture; composes old `UseCases` and adapters | `REMOVE-CONFIRMED` | Delete after assertion-level test migration. Its imports are an input to orphan analysis, not proof that the imported use cases are old-only. |
| `.../commands/contracts.py` | old registry / dispatch command abstraction | `VERIFY-THEN-REMOVE` | Delete if no current source/test imports remain after old command tests migrate. |
| `.../application/contracts.py` | old bootstrap `UseCases` bundle | `VERIFY-THEN-REMOVE` | Delete only if current commands/tests do not use types from it. |

### 5.2 Old command modules listed by the old registry

The verified old registry imports the following modules. They are retired public-wire implementations; their downstream application modules are not automatically retired.

| Module under `spec_dock_runtime/commands/` | Old surface | Decision | Current regression destination |
|---|---|---|---|
| `active.py` | `active set/show/clear` old syntax | `REMOVE-CONFIRMED` | `test_active_vnext.py` and active application/infra tests |
| `artifact_import.py` | old artifact import wire | `REMOVE-CONFIRMED` | `test_artifact_commands_vnext.py`, `test_artifact_vnext.py` |
| `close.py` | old top-level `close` | `REMOVE-CONFIRMED` | current scope lifecycle tests |
| `delete.py` | old top-level `delete` | `REMOVE-CONFIRMED` | current scope delete tests and tombstone test |
| `deps.py` | old `deps` group | `REMOVE-CONFIRMED` | dependency vNext tests |
| `doctor.py` | old top-level `doctor` | `REMOVE-CONFIRMED` | workspace diagnostics vNext tests |
| `import_cmd.py` | old top-level `import` | `REMOVE-CONFIRMED` | scope import vNext tests |
| `issue.py` | old `issue start/finish` | `REMOVE-CONFIRMED` | work lifecycle tests and tombstone test |
| `new.py` | old `new` group | `REMOVE-CONFIRMED` | scope create / artifact create vNext tests |
| `sync.py` | old top-level `sync` | `REMOVE-CONFIRMED` | workspace sync vNext tests |
| `uninstall.py` | old top-level installer delegation | `REMOVE-CONFIRMED` | installation uninstall tests and tombstone |
| `update.py` | old top-level installer delegation | `REMOVE-CONFIRMED` | installation update tests and tombstone |
| `validate.py` | old top-level `validate` | `REMOVE-CONFIRMED` | workspace validate/CI diagnostics tests |
| `workbench.py` | old workbench wire | `REMOVE-CONFIRMED` | workbench vNext tests |
| `worktree.py` | old worktree wire | `REMOVE-CONFIRMED` | worktree vNext tests |

Before deletion, run the current-source import/reference gate. If a module has become a shared helper despite this observed role, split the shared helper into a neutral current module and then delete the old command shell.

### 5.3 Current shell and safety boundary

| Path / family | Decision | Notes |
|---|---|---|
| `.../cli/options.py` | `RETAIN-CURRENT` | Current parser, common options, help/JSON handling. |
| `.../cli/catalog.py` | `RETAIN-CURRENT` | Approved 44 leaf catalog and effects/recovery metadata. |
| `.../cli/vnext_runtime.py` | `RETAIN-CURRENT` | Current command execution, failure envelopes, journal recovery. |
| `.../cli/admission.py` | `RETAIN-CURRENT` | Current lifecycle admission / maintenance boundary. |
| `.../cli/legacy.py` | `RETAIN-CURRENT` | Fail-closed tombstone; not a legacy executor. |
| `commands/active_vnext.py` | `RETAIN-CURRENT` | Current active command. |
| `commands/artifact_vnext.py` | `RETAIN-CURRENT` | Current artifact command. |
| `commands/branch_vnext.py` | `RETAIN-CURRENT` | Current branch command. |
| `commands/dependency_vnext.py` | `RETAIN-CURRENT` | Current dependency command. |
| `commands/installation_vnext.py` | `RETAIN-CURRENT` | Current journaled installation command. |
| `commands/scope_create_vnext.py` | `RETAIN-CURRENT` | Current scope creation. |
| `commands/scope_delete_vnext.py` | `RETAIN-CURRENT` | Current scope deletion. |
| `commands/scope_import_vnext.py` | `RETAIN-CURRENT` | Current GitHub import. |
| `commands/scope_lifecycle_vnext.py` | `RETAIN-CURRENT` | Current close/reopen. |
| `commands/scope_query_vnext.py` / `scope_result_vnext.py` | `RETAIN-CURRENT` | Current query/edit/result contract. |
| `commands/work_vnext.py` | `RETAIN-CURRENT` | Current start/finish. |
| `commands/workbench_vnext.py` | `RETAIN-CURRENT` | Current workbench copy. |
| `commands/workspace_diagnostics_vnext.py` | `RETAIN-CURRENT` | Current validate/doctor/CI validation. |
| `commands/workspace_migrate_vnext.py` | `RETAIN-CURRENT` | Current schema migration. |
| `commands/workspace_sync_vnext.py` | `RETAIN-CURRENT` | Current generation sync. |
| `commands/worktree_vnext.py` | `RETAIN-CURRENT` | Current worktree commands. |

## 6. Application / domain / infra / presentation inventory policy

These layers contain shared logic. The verified current runtime directly imports `application.active_selection`, `application.scope_query`, and `application.installation_update_vnext`, and current command modules may call older-named use cases. Therefore no directory-wide deletion is permitted.

| Candidate / family | Initial decision | Confirmation rule |
|---|---|---|
| `application/issue_lifecycle.py` | `VERIFY-THEN-REMOVE` | Delete only if current `work_vnext` and all current tests do not call it. Preserve any still-current branch/dependency/active behavior in current work lifecycle module. |
| `application/contracts.py` | `VERIFY-THEN-REMOVE` | Delete after old bootstrap/commands/tests are gone and zero current type import remains. |
| old installer-delegation application modules, if any | `VERIFY-THEN-REMOVE` | Current installation vNext route and tests must show zero caller. |
| `application/check_deps.py`, `close_node.py`, `create_*`, `delete_node.py`, `import_*`, `mutate_deps.py`, `sync_state.py`, `validate_tree.py` | `VERIFY-ONLY`, default `RETAIN-CURRENT` | Retain when any current command or current unit test reaches the invariant. Do not delete because the old bootstrap imported them. |
| `application/active_selection.py`, `scope_query.py`, `installation_*_vnext.py`, `migrate_workspace_vnext.py`, `work_lifecycle.py`, `workspace_*_vnext.py`, `worktree_*_vnext.py` | `RETAIN-CURRENT` | Current route / migration / installation. |
| `domain/**` | `RETAIN-CURRENT` by default | Remove only an individually proven orphan; no broad cleanup in this Issue. |
| `infra/**` | `RETAIN-CURRENT` by default | Current engine, repository, Git/GitHub, journal, generation, installation adapters depend on this layer. |
| `presentation/**` | `RETAIN-CURRENT` by default | Current JSON/text envelopes and rendering depend on this layer. |

### Required orphan-analysis record

For every application module deleted beyond the confirmed old shell, record in this inventory:

- current roots searched;
- static import result;
- string/resource reference result;
- tests removed or migrated;
- replacement module, if shared symbols moved;
- focused tests proving current behavior.

A blank record means the module remains.

## 7. CI inventory

| Path | Observed state | Decision | Target |
|---|---|---|---|
| `.github/workflows/ci.yml` | Runs `python3 ./spec-dock/scripts/spec-dock sync` then `validate` | `UPDATE-CURRENT` | Invoke `specdock-ci-validate.sh` with source root, target root, full `${{ github.sha }}`; no sync/write. |
| `.github/scripts/specdock-ci-validate.sh` | Full SHA, clean source, scratch fixed engine, digest, read-only `workspace validate --ci --json` | `RETAIN-CURRENT` | Keep behavior; adjust only if workflow-testability/error clarity requires. |
| `tests/integration/test_ci_fixed_validation.py` | Success, exact SHA output, target unchanged, wrong SHA failure | `RETAIN-CURRENT` | Extend with workflow wiring, dirty source, invalid expected SHA, and invalid distribution digest fail-closed cases; compare target state before/after. |
| `.github/workflows/provider-ci.yml` | Full suite plus focused matrix running old installer/harness tests | `UPDATE-CURRENT` | Before deleting old test files in Step 3, switch focused matrix to `test_provider_distribution.py`, fixed entrypoint test, current installation init test, retired-surface absence test; its final green gate follows Step 4 source removal and dogfood runtime projection. |
| `.github/workflows/commit-identity.yml` | Separate identity gate | `VERIFY-ONLY` | No Issue #411 change unless link/reference scan proves necessary. |

### CI acceptance details

- `EXPECTED_SOURCE_SHA` must be exactly 40 or 64 lowercase hex as the validator permits; GitHub commit IDs are expected to be 40 hex in the current repository.
- `git rev-parse --verify 'HEAD^{commit}'` must equal the workflow-provided SHA byte-for-byte.
- Do not substitute target branch name, PR head branch, default branch, or short SHA.
- The authoring baseline `d7c...` is provenance, not a permanent CI literal.
- Source and target may both be `$GITHUB_WORKSPACE`; the validator builds in scratch and validates the target read-only.

## 8. Test inventory

### 8.1 Retired launcher and setup

| Path | Observed role | Decision | Required migration |
|---|---|---|---|
| `tests/cli_runtime/harness.py` | Imports `legacy_installer_main`; overwrites installed shim with legacy fixture; provides large old-CLI helper surface | `REMOVE-CONFIRMED` | Move only reusable current assertions/helpers to current-specific test support; no old launcher installation. |
| `tests/cli_runtime/conftest.py` | Builds a session template via old harness and allow-lists old runtime modules | `REMOVE-CONFIRMED` or rewrite to current-only fixtures | Delete old cache logic. Add fixture only if current tests demonstrably need it. |
| `tests/fixtures/legacy_spec_dock.script` | Imports `spec_dock_runtime.app` and old bootstrap | `REMOVE-CONFIRMED` | Delete with old shell. |
| `tests/fixtures/cli_redesign/legacy_manifest.json` | Frozen 28-leaf pre-cutover inventory | `REMOVE-CONFIRMED` | Delete; Git history / Issue #409 is historical evidence. |

### 8.2 Contract tests

| Path / test | Decision | Action |
|---|---|---|
| `tests/cli_runtime/test_cli_vnext_contract.py::test_legacy_28_leaf_inventory_is_frozen_before_cutover` | `REMOVE-CONFIRMED` | Delete test and old parser/registry imports. |
| Remaining `test_cli_vnext_contract.py` tests for 44 leaf/help/options/JSON/recovery/tombstone | `RETAIN-CURRENT` | Keep; rename wording from “future/vNext” to current where useful, without changing contract. |
| `tests/integration/test_cli_entrypoint_vnext.py` | `RETAIN-CURRENT` | Keep fixed distribution, no checkout fallback, retired installer no-write tests; add assertion that public module has no `legacy_installer_main`. |

### 8.3 Old harness caller tests

The following modules depend on the old harness directly or through `tests/cli_runtime/conftest.py` and must be handled assertion-by-assertion before removal. A `_vnext` filename does not make a direct harness import safe:

- `tests/cli_runtime/test_active.py`
- `tests/cli_runtime/test_artifact_import_file.py`
- `tests/cli_runtime/test_artifact_import_s04.py`
- `tests/cli_runtime/test_close.py`
- `tests/cli_runtime/test_delete.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- `tests/cli_runtime/test_deps.py`
- `tests/cli_runtime/test_doctor.py`
- `tests/cli_runtime/test_generation_checkout.py`
- `tests/cli_runtime/test_import.py`
- `tests/cli_runtime/test_issue_lifecycle.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_runtime_handoff.py`
- `tests/cli_runtime/test_scope_github_vnext.py`
- `tests/cli_runtime/test_scope_local_vnext.py`
- `tests/cli_runtime/test_storage_core_cli.py`
- `tests/cli_runtime/test_sync.py`
- `tests/cli_runtime/test_uninstall.py`
- `tests/cli_runtime/test_update.py`
- `tests/cli_runtime/test_validate.py`
- `tests/cli_runtime/test_workbench.py`
- `tests/cli_runtime/test_worktree.py`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py`
- `tests/cli_runtime/test_wrappers.py`
- `tests/unit/infra/test_fake_gh_harness.py`

Additional non-`_vnext` `test_runtime_*` modules and unit command/presentation tests may exercise shared use cases rather than the old wire. They are `VERIFY-THEN-REMOVE`, not bulk-delete candidates.

#### Assertion migration mapping

| Old behavior family | Old files | Current destination | Delete criterion |
|---|---|---|---|
| Active selection | `test_active.py`, `test_runtime_active_*` | `test_active_vnext.py`, application/infra active tests | All current target resolution, rollback, pointer invariants covered. |
| Artifact import/create | `test_artifact_import_*`, old new-artifact assertions | `test_artifact_commands_vnext.py`, `test_artifact_vnext.py`, artifact domain/infra tests | Current opaque import, naming, collision, malformed input assertions covered. |
| Scope create/import | `test_new.py`, `test_import.py`, related runtime tests | current scope create/import tests | Local/GitHub backend, parent, title, failure invariants covered. |
| Close/delete | `test_close.py`, `test_delete.py` | current scope lifecycle/delete tests | Current effect/recovery and safety guards covered. |
| Issue start/finish | `test_issue_lifecycle.py` | current work lifecycle tests | dependency, branch, active, finish behavior covered. |
| Dependency | `test_deps.py`, `test_runtime_deps_*` | dependency vNext tests and domain topology tests | readiness/cycle/mutation invariants covered. |
| Sync/validate/doctor | `test_sync.py`, `test_validate.py`, `test_doctor.py`, related unit tests | workspace sync/diagnostics vNext and unit layers | generation, validation, read-only CI, diagnostic invariants covered. |
| Workbench/worktree | `test_workbench.py`, `test_worktree.py` | current workbench/worktree vNext tests | current options/effects/recovery covered. |
| Update/uninstall | `test_update.py`, `test_uninstall.py` | installation integration tests | journaled current behavior covered; old nontransactional behavior intentionally not carried forward. |
| Wrapper | `test_wrappers.py` | fixed entrypoint/shim tests | fixed-engine delegation and no fallback covered. |

### 8.4 Old installer / inventory anchoring tests

| Path | Observed state | Decision | Action |
|---|---|---|---|
| `tests/cli_runtime/test_distribution_cutover.py` | Directly imports old harness; mixes current provider/install-root catalog, skill parity, executable boundary, unmanaged-content and consumer-workflow preservation with old init replacement assertions | `UPDATE-CURRENT` then remove old wire | Classify every test function; move current parity to provider distribution tests and current installation invariants to installation integration tests before deleting the old harness/file. |
| `tests/cli_runtime/test_generation_checkout.py`, `test_runtime_handoff.py`, `test_worktree_lifecycle_coordination.py` | Directly subclass old `CliRuntimeHarness`; some assertions may still express current workspace/branch safety | `VERIFY-THEN-REMOVE` | Port current invariants to current fixtures/tests before removing the old base class; delete only old init/CLI wire assertions. |
| `tests/cli_runtime/test_scope_github_vnext.py`, `test_scope_local_vnext.py` | Current-named tests call `harness.main(["init", ...])` for setup | `UPDATE-CURRENT` | Replace setup with current fixed installation fixture; retain current scope behavior assertions. |
| `tests/unit/infra/test_fake_gh_harness.py` | Uses old harness stub helpers while testing shared GitHub CLI/status invariants | `UPDATE-CURRENT` | Move fake-gh helpers to current neutral test support and preserve the shared invariant assertions. |
| `tests/unit/infra/test_directory_installation.py` | Directly imports `legacy_installer_main`; asserts old replace-in-place and nontransactional update semantics | `REMOVE-CONFIRMED` after migration | Move only still-current data-preservation/security assertions to current installation tests; do not preserve old nontransactional contract. |
| `tests/unit/infra/test_init_update.py` | Imports old harness; mixes old init/update tests with current docs/skills/provider-dogfood parity assertions | `UPDATE-CURRENT` then remove old portions | Move current parity/guidance assertions into `tests/unit/infra/test_provider_distribution.py`; migrate installation assertions; remove legacy fixture exceptions. |
| `tests/unit/cli/test_cli_smoke.py` | Executes old `active set --id` through old harness | `REMOVE-CONFIRMED` | Current fixed-engine/current active integration test replaces it. |
| `tests/unit/cli/test_cli.py` | Freezes existence and grouping of old test modules | `REMOVE-CONFIRMED` or rewrite to current inventory | Prefer delete inventory-freezing assertions; retain only generic test-discovery invariant if valuable, in a neutral test. |
| `pyproject.toml` mypy overrides | Names old harness/test modules | `UPDATE-CURRENT` | Remove override entries for deleted modules; keep only justified current overrides. |

### 8.5 Current regressions to retain

- `tests/integration/test_ci_fixed_validation.py`
- `tests/integration/test_cli_docs_vnext.py`
- `tests/integration/test_cli_entrypoint_vnext.py`
- `tests/integration/test_cli_recovery_vnext.py`
- `tests/integration/test_cli_writer_compatibility_vnext.py`
- `tests/integration/test_engine_handover_vnext.py`
- `tests/integration/test_installation_finalize_vnext.py`
- `tests/integration/test_installation_group_init_vnext.py`
- `tests/integration/test_installation_group_journal_vnext.py`
- `tests/integration/test_installation_group_update_vnext.py`
- `tests/integration/test_installation_journal_vnext.py`
- `tests/integration/test_workspace_migration_journal_vnext.py`
- `tests/integration/test_workspace_migration_vnext.py`
- current `tests/cli_runtime/*_vnext.py`
- current application/domain/infra/presentation unit tests reached by the current route

The migration tests and their fixture/helper data are intentional retain candidates. A filename without `_vnext` is not sufficient reason to remove a shared-invariant test.

## 9. Docs inventory

| Path | Observed state | Decision | Target content |
|---|---|---|---|
| `src/spec_dock/assets/spec_dock/scripts/README.md` | Says daily operations use local script; shows `new`, `issue start`, `sync`, `validate`, `uvx init/update` | `UPDATE-CURRENT` | Explain fixed external `spec-dock` / verified shim, current leaf examples, installation commands, CI read-only path. |
| `spec-dock/scripts/README.md` | Byte-identical dogfood copy of provider stale guide | `UPDATE-CURRENT` | Update from provider, not independently; require byte parity. |
| `docs/github-issue-integration.md` | Current-looking v2 design centered on old `new/import/sync`, local runtime, old metadata naming | `UPDATE-CURRENT` | Current `scope create/import`, GitHub/local authority, safe failure, fixed engine, current metadata terms. |
| `docs/sync-aggregation.md` | Current-looking old `sync` aggregation design | `UPDATE-CURRENT` | Current `workspace sync`, cache/source options, generation pointer, no active mutation, CI validation distinction. |
| `docs/scope-lifecycle-start-finish-analysis.md` | Explicit analysis input, not current spec | `RETAIN-HISTORICAL` | Keep; ensure top banner and link to current `reference_cli.md`. |
| `src/spec_dock/assets/spec_dock/docs/historical/**` | Physical historical area | `RETAIN-HISTORICAL` | Keep unchanged except broken links. Exclude from stale-current scan. |
| `spec-dock/docs/historical/**` | Dogfood historical projection | `RETAIN-HISTORICAL` | Keep provider parity. |
| `src/spec_dock/assets/spec_dock/docs/reference_cli.md` | Current 44-leaf, fixed CI, installation/migration | `RETAIN-CURRENT` | Update only if cleanup changes path wording/link. |
| `src/spec_dock/assets/spec_dock/docs/migration.md` | Current migration/recovery; may mention old state | `RETAIN-CURRENT` with scan exception | Do not rewrite history merely to remove old tokens. |
| root `README.md` | Current fixed engine and current commands | `VERIFY-ONLY` | No change unless link/stale scan finds issue. |
| `AGENTS.md` | Current operation rules but architecture map still describes `parser/registry/dispatch` and test-only old installer; development command names the soon-to-be-deleted `test_directory_installation.py` | `UPDATE-CURRENT` | Replace map with `options/catalog/vnext_runtime/admission/legacy`; remove retired fixture guidance and replace the deleted test command with a current test path. |
| `src/spec_dock/assets/install_root/.agents/skills/**` | Current agent guidance introduced by cutover | `VERIFY-ONLY` | Stale-current scan; update only confirmed retired instructions. |
| dogfood `.agents/skills/**` | Current projection | `VERIFY-ONLY` | Provider parity. |
| Issue / Initiative / Epic specs under `spec-dock/initiatives/**` | Historical/project records; may contain old command text | `RETAIN-HISTORICAL` for scan purposes | Never mass-rewrite as cleanup. |

### Current-guidance stale scan

Include:

- root `README.md`, `AGENTS.md`
- root `docs/github-issue-integration.md`, `docs/sync-aggregation.md`
- provider current docs excluding `historical/**` and migration exception
- provider `scripts/README.md`
- provider installed skills
- dogfood current docs/scripts/skills after projection
- `.github/workflows/*.yml`

Search for executable guidance forms, not generic nouns:

- `./spec-dock/scripts/spec-dock new ...`
- `./spec-dock/scripts/spec-dock issue ...`
- `./spec-dock/scripts/spec-dock sync`
- `./spec-dock/scripts/spec-dock validate`
- `python3 ./spec-dock/scripts/spec-dock ...`
- `uvx spec-dock init|update`
- top-level `spec-dock new|issue|deps|sync|validate|update|uninstall|delete|close` in current guidance

Intentional allowlist:

- `spec_dock_runtime/cli/legacy.py`
- tombstone tests
- `docs/historical/**`
- `migration.md` when describing migration source state
- `docs/scope-lifecycle-start-finish-analysis.md`
- `spec-dock/initiatives/**`
- this Issue's inventory/spec documents

Every allowlist match must have a reason; blanket directory exclusion outside the listed historical/spec areas is not allowed.

## 10. Provider / dogfood parity inventory

| Provider | Dogfood | Target |
|---|---|---|
| `src/spec_dock/assets/spec_dock/scripts/**` | `spec-dock/scripts/**` | Byte-identical current projection; no legacy fixture exception. |
| `src/spec_dock/assets/spec_dock/docs/**` | `spec-dock/docs/**` | Byte-identical managed docs, including historical. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock/**` | `.agents/skills/spec-dock/**` | Byte-identical. |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/**` | `.agents/skills/spec-dock-grill-with-docs/**` | Byte-identical. |

Do not update other worktrees or consumers. The parity test applies only to the checked-in provider and this repository's dogfood projection.

## 11. Mandatory removal manifest

After all migration gates, these paths/symbols must be absent:

```text
src/spec_dock/cli.py::legacy_installer_main
src/spec_dock/installer.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py
tests/cli_runtime/harness.py
tests/fixtures/legacy_spec_dock.script
tests/fixtures/cli_redesign/legacy_manifest.json
tests/unit/infra/test_directory_installation.py
tests/unit/cli/test_cli_smoke.py
```

The old command modules listed in §5.2 must also be absent after zero-current-caller verification. `commands/contracts.py`, `application/contracts.py`, and other transitive old-stack modules are conditional until their gate record is complete.

## 12. Mandatory retain manifest

At minimum, retain:

```text
src/spec_dock/external_cli.py
src/spec_dock/fixed_bundle.py
src/spec_dock/runtime_loader.py
src/spec_dock/shim_vnext.py
src/spec_dock/assets/spec_dock/scripts/spec-dock
.../cli/options.py
.../cli/catalog.py
.../cli/vnext_runtime.py
.../cli/admission.py
.../cli/legacy.py
.../commands/*_vnext.py
.github/scripts/specdock-ci-validate.sh
tests/integration/test_ci_fixed_validation.py
tests/integration/test_cli_entrypoint_vnext.py
tests/integration/test_cli_recovery_vnext.py
tests/integration/test_installation*_vnext.py
tests/integration/test_workspace_migration*_vnext.py
src/spec_dock/assets/spec_dock/docs/historical/**
src/spec_dock/assets/spec_dock/docs/migration.md
```

Shared application/domain/infra/presentation modules remain unless an individual orphan record proves deletion safe.

## 13. Evidence-gated unresolved items

These are not open product decisions. The implementation follows the rule shown.

| Item | Evidence to collect | Deterministic outcome |
|---|---|---|
| Which `installer.py` constants besides `ASSETS` are current? | Current-root import/reference scan | Move only reached symbols to `asset_layout.py`; delete the rest with old installer. |
| Which non-vNext application modules are still current? | Transitive current import graph + focused tests | Retain reached modules; delete only zero-caller modules after tests migrate. |
| Which old test assertions remain valuable? | Assertion-level mapping to current behavior/shared invariant | Port before delete; retired syntax/history-only assertions are deleted. |
| Does root/current doc link to a retired path? | Inbound link and stale-guidance scan | Rewrite link to current reference; historical docs keep explicit label. |
| Does GitHub Actions checkout SHA equal `${{ github.sha }}` for each trigger? | Workflow unit assertion plus actual clean CI run | Keep explicit `HEAD` comparison; fail rather than choose another ref. |

## 14. Implementation completion fields

The implementer must fill this table in the PR/report, not by editing historical records.

| Gate | Result / command output summary | Status |
|---|---|---|
| Verified baseline / drift check | 独立 clone、branch、祖先、3677 entries snapshot | pass |
| Current-root import/reference scan | §15 の現行 root / 共有 module 判断 | pass |
| Assertion migration ledger complete | §8 family mapping と §15 実施判断 | pass |
| Old source removed | provider / dogfood の旧 shell と command を撤去 | pass |
| Fixed distribution retired-path absence | fixed bundle 実物で app/bootstrap/installer 不在 | pass |
| CI workflow wiring and negative tests | current CI integration 19 passed、独立 clean clone の固定SHA validator 成功 | pass |
| Provider/dogfood byte parity | test_provider_distribution.py | pass |
| Current docs stale scan | current docs 改訂、historical pointer 追加 | pass |
| Focused tests | entrypoint / CI / parity 19 passed | pass |
| `make lint` | ruff check / format、mypy 成功 | pass |
| `uv run pytest` | 1212 passed / 1 skipped | pass |
| `git diff --check` | 差分形式を確認 | pass |
| Out-of-scope side-effect check | 3677 entries 差分 0、refs は最終 push 後に確認 | pending |

## 15. 実装時の判断と証拠（2026-09-28）

- 現行の root は `spec_dock.cli:main` → `external_cli` → 固定配布、runtime は `cli.vnext_runtime` と `commands/*_vnext`。旧 `app.py`、`cli/bootstrap.py`、`parser.py`、`registry.py`、`dispatch.py` と旧 command 15 modules は現行 root から呼ばれず、旧 harness / test を除去後に provider と dogfood の双方から撤去した。
- `application/issue_lifecycle.py`、`commands/targets.py`、`commands/node_id_normalizer.py` は旧 shell 専用の参照を確認して撤去した。`application/contracts.py` は現行 Artifact / Workbench が使用し、`application/resolve_target.py` は現行 target 解決の unit tests が使用するので保持した。`application/create_node.py`、`infra/git_helper.py` など古い名前の共有モジュールも現行呼び出しまたは動的呼び出しがあるため保持した。その他の application / infra / presentation は、この Issue での削除根拠がないものを保持した。
- old harness、fixture、old command tests は旧構文や旧ディレクトリ installer を凍結していた。現行の 44 leaf / tombstone は `test_cli_vnext_contract.py` と `test_cli_entrypoint_vnext.py`、installation / migration / journal は現行 integration tests、Scope / Work / Artifact は各 `*_vnext.py` が検証する。current-named test の旧 `init` setup は provider scaffold へ差し替えた。旧 test 関数の機械的コピーは実施しない。
- 配布 parity と shim equality だけを `test_provider_distribution.py` に置き、CI workflow wiring は既存 `test_ci_fixed_validation.py` に 1 件追加した。撤去確認専用の大規模 test harness は追加しない。旧ファイル不在は fixed bundle の実物照合で確認する。
- `uv run pytest -q --maxfail=1`: 1212 passed / 1 skipped。`make lint`: ruff check / format、mypy 成功。固定 bundle の digest `fc4a0fa729e0d422bc15513cd29a7d5f7d9bb5966a5b7852f0e00f70def88f0e`、旧 app/bootstrap/installer ファイル不在、現行 help 成功。範囲 snapshot 3677 entries は、Issue #411 のみ除外して差分 0。
- `eb77cd9f` の独立 clean clone で full-SHA validator 成功（`valid=true`、240 nodes、digest `54f19658…`）。clone は clean で `.git/spec-dock` は存在しない。最終 SHA の照合と Strict v2 は最終 push 後に実施する。
