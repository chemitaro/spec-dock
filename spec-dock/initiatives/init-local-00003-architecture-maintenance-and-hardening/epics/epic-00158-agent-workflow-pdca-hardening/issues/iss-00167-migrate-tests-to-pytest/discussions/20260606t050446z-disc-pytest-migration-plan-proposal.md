---
created_by_role: spec-dock-implementation-planner
scope_id: iss-00167
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_issue.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/authoring/issue-plan.md
  - pyproject.toml
  - uv.lock
  - README.md
  - AGENTS.md
  - .github/workflows/provider-ci.yml
  - tests/cli_runtime/harness.py
  - tests/unit/infra/test_init_update.py
  - tests/unit/commands/test_runtime_new_s08.py
  - tests/unit/domain/test_runtime_domain_s03.py
  - tests/cli_runtime/test_runtime_import_s10.py
  - tests/cli_runtime/test_delegated_authoring.py
  - tests/integration/test_discovery.py
  - spec-dock/active/issue/discussions/20260606t045218z-disc-pytest-complete-migration-design-proposal.md
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: Main orchestrator must decide adoption in canonical report.md before reflecting any portion to canonical plan.md or report.md.
---

# Pytest Migration Plan Proposal

## Plan Summary

This draft proposes an executable, delegated issue plan for completing `iss-00167` without changing product runtime behavior.

The plan preserves the post-`iss-00160` test lanes:

- Unit lane: `tests/unit`, verified by `uv run pytest tests/unit`.
- Integration lane: `tests/integration`, verified by `uv run pytest tests/integration`.
- Runtime / CLI regression lane: `tests/cli_runtime`, verified by `uv run pytest tests/cli_runtime`.
- Full fallback: `uv run pytest`.

Implementation should proceed as a hard runner cutover, not a compatibility-only pytest collection pass. `unittest.TestCase`, `self.assert*`, `assertRaises*`, `self.subTest`, `unittest.main()`, `unittest.skip`, and `unittest.mock` import paths are migration targets.

Assumptions:

- Fresh requirement and design `spec-reviewer` pass are the current entry gate, as recorded in `report.md`.
- `dependency-groups.dev` is the accepted pytest dependency location.
- Provider CI remains unit-lane-only and changes its command to `uv run pytest tests/unit`.
- Existing dirty canonical docs and the existing system-architect discussion are pre-existing state for this draft; this file does not adopt or modify them.

## Requirement / Design Traceability

- AC-001 maps to S01 dependency/config and `uv run pytest --version`, `uv run pytest --collect-only`.
- AC-002 maps to S04/S05 unit migration and S90 provider CI command update.
- AC-003 maps to S06 integration lane migration.
- AC-004 maps to S02/S03 runtime harness and runtime lane migration.
- AC-005 maps to S99 full `uv run pytest`.
- AC-006 maps to S02 through S08 and final grep absence checks.
- AC-007 maps to S90 docs / CI / command-string tests.
- AC-008 maps to per-step `code-reviewer`, S99 `qa-reviewer`, and no weak assert / no skip or xfail audit.
- AC-009 maps to S99 `spec-reviewer` and explicit parent Epic deferred-work boundary check.
- EC-001 maps to S01 collect-only.
- EC-002 maps to S03/S04/S05 parametrization or explicit assertion-message conversions.
- EC-003 maps to S03/S04/S05 `pytest.raises(..., match=...)`.
- EC-004 maps to S02/S04/S05 `tmp_path`, `tmp_path_factory`, and `monkeypatch`.
- EC-005 maps to S03 and S99 recording runtime lane and full-suite duration without adding optimization scope.
- EC-006 maps to S01 collect-only and S08 cleanup inspection.
- EC-007 maps to S90 docs / command-string tests.

Design trace:

- D-001: implement pytest in `dependency-groups.dev` and add minimal pytest config.
- D-002: keep provider CI unit-only.
- D-003: remove all `unittest` imports, including `unittest.mock`.
- D-004: migrate harness first, then dependent runtime tests, then unit groups, integration, docs/CI.

## Milestones

- M1 runner contract: pytest dependency, lock, and collection config exist and collect the three lanes.
- M2 runtime helper cutover: `tests/cli_runtime/harness.py` no longer inherits from `unittest.TestCase` and exposes pytest-native helpers/fixtures.
- M3 runtime lane cutover: all `tests/cli_runtime` tests are pytest-native and pass as a lane.
- M4 unit lane cutover: all `tests/unit` tests are pytest-native, including the large installer/update file, and pass as a lane.
- M5 integration lane cutover: `tests/integration` remains a pytest lane and passes.
- M6 docs / CI contract cutover: README, AGENTS, provider CI, and tests asserting command strings all name pytest commands.
- M7 final quality gate: full pytest suite, grep absence checks, reviewer gates, report evidence, and final spec alignment pass.

## Dependency-Derived Execution Order

1. Establish pytest availability and collection first, because every later slice needs a pytest command as Green evidence.
2. Convert `tests/cli_runtime/harness.py` before broad runtime tests because many runtime files depend on inherited helper behavior.
3. Convert small representative runtime tests immediately after the harness to prove the helper API before migrating the whole runtime lane.
4. Convert smaller unit packages before `tests/unit/infra/test_init_update.py`; the latter is over 16k lines and should not be mixed with low-risk unit conversions.
5. Convert integration discovery smoke after unit conventions are stable.
6. Update docs / CI after command strings are final, then update tests that assert those strings.
7. Run final grep and full-suite gates last, because they prove complete cutover rather than partial compatibility.

## Issue / Step Slicing

### S00 preflight characterization

- Delegated role: `dev-coder` for read-only command evidence; no source edits.
- Scope: current test/config/docs state only.
- Target evidence:
  - `uv run pytest --version` or dependency-unavailable evidence.
  - `uv run pytest --collect-only` or dependency-unavailable evidence.
  - `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests`.
  - `rg -n "unittest discover|Framework: `unittest`|tests/test_cli.py|tests/test_init_update.py" README.md AGENTS.md .github/workflows tests`.
- Reviewer gate: none for read-only, but evidence must be recorded in `report.md`.
- Stop condition: if current requirement/design gate evidence is stale or missing, return to spec authoring before implementation.

### S01 pytest dependency and collection contract

- Delegated role: `dev-coder`.
- Allowed paths: `pyproject.toml`, `uv.lock`, minimal pytest config in `pyproject.toml`.
- Forbidden changes: tests, docs, CI, runtime source, new plugins beyond pytest.
- Behavior goal: `uv run pytest --version` works and pytest can collect the existing `tests` tree.
- Concrete test seeds:
  - `tc-s01-001` acceptance: pytest dependency resolves.
    - Operation: run `uv run pytest --version`.
    - Expected: command succeeds and reports pytest.
    - Failure detected: pytest is not lock-backed or not available to local commands.
  - `tc-s01-002` collection: current lanes are discoverable.
    - Operation: run `uv run pytest --collect-only`.
    - Expected: collection reaches `tests/unit`, `tests/integration`, and `tests/cli_runtime`; helper artifacts are not miscollected.
    - Failure detected: pytest config is too narrow, too broad, or blocked by imports.
- Step reviewer: `code-reviewer`.
- Step gate: record Green evidence, reviewer pass, and one focused commit before S02.

### S02 runtime harness pytest-native conversion

- Delegated role: `dev-coder`.
- Allowed paths: `tests/cli_runtime/harness.py`, `tests/cli_runtime/conftest.py` only if repeated fixture value is clear.
- Forbidden changes: product runtime behavior, broad runtime test conversion, docs / CI.
- Behavior goal: runtime helper setup, temp repo creation, `gh` stubs, runtime subprocess helpers, and skip behavior work without `unittest.TestCase`.
- Concrete test seeds:
  - `tc-s02-001` helper smoke: a migrated minimal runtime test can create a target repo and run the runtime helper.
  - `tc-s02-002` skip path: unavailable git or symlink conditions use `pytest.skip` and do not rely on `self.skipTest`.
  - `tc-s02-003` assertion helper: helper failures raise plain assertion failures with stdout/stderr context preserved.
- Verification: focused pytest command for a small runtime file or harness smoke selected by the worker.
- Step reviewer: `code-reviewer`.
- Step gate: no `import unittest`, `unittest.TestCase`, `self.assert*`, or `skipTest` remains in `tests/cli_runtime/harness.py`.

### S03 runtime / CLI regression lane migration

- Delegated role: `dev-coder`.
- Allowed paths: `tests/cli_runtime/test_*.py`, `tests/cli_runtime/conftest.py` if already introduced in S02.
- Forbidden changes: `tests/unit`, `tests/integration`, docs, CI, product runtime source.
- Behavior goal: the full `tests/cli_runtime` lane runs under pytest without unittest framework dependency.
- Suggested internal order:
  - S03a low-coupling files such as wrappers, sync/update/validate/close smoke.
  - S03b active/deps/import/new lifecycle files with parametrized replacements for `subTest`.
  - S03c large delegated-authoring and runtime import/new-doc/close/delete files.
- Concrete test seeds:
  - `tc-s03-001` runtime lane command: `uv run pytest tests/cli_runtime`.
  - `tc-s03-002` exception assertions: converted tests use `pytest.raises(..., match=...)` where previous tests checked exception regex.
  - `tc-s03-003` multi-case visibility: former `subTest` loops use `pytest.mark.parametrize` or explicit case IDs in assertion messages.
  - `tc-s03-004` skip audit: former `@unittest.skip` entries use pytest-native skip marks or are removed only when duplicate coverage is documented.
- Step reviewer: `code-reviewer`.
- Step gate: runtime lane pass plus `rg` absence check scoped to `tests/cli_runtime`.

### S04 small and medium unit package migration

- Delegated role: `dev-coder`.
- Allowed paths: `tests/unit/application`, `tests/unit/cli`, `tests/unit/domain`, `tests/unit/presentation`, `tests/unit/test_discovery.py`, `tests/unit/conftest.py` if justified.
- Forbidden changes: `tests/unit/infra/test_init_update.py`, docs, CI, runtime source.
- Behavior goal: unit tests outside the largest infra file use pytest-native functions/classes and pass by package group.
- Concrete test seeds:
  - `tc-s04-001` application/domain groups: `uv run pytest tests/unit/application tests/unit/domain`.
  - `tc-s04-002` cli/presentation groups: `uv run pytest tests/unit/cli tests/unit/presentation`.
  - `tc-s04-003` mock migration: previous `unittest.mock.patch` usage is replaced by `monkeypatch` or local fakes without importing `unittest`.
- Step reviewer: `code-reviewer`.
- Step gate: focused package-group pytest pass plus scoped `rg` absence excluding the intentionally deferred infra file.

### S05 large installer/update unit migration

- Delegated role: `dev-coder`.
- Allowed paths: `tests/unit/infra/test_init_update.py`, `tests/unit/infra/test_fake_gh_harness.py`, `tests/unit/infra/test_active_store.py`, `tests/unit/infra/conftest.py` if justified.
- Forbidden changes: docs / CI except command-string test expectations that must wait for S90 unless the canonical plan chooses to include them here.
- Behavior goal: the largest unit file and infra helpers migrate without assertion weakening or test deletion.
- Concrete test seeds:
  - `tc-s05-001` infra lane: `uv run pytest tests/unit/infra`.
  - `tc-s05-002` command-string characterization: expectations for old unittest commands remain unchanged until S90 or are updated only with docs/CI in the same commit if S90 is merged into this slice.
  - `tc-s05-003` assertion-strength audit: representative generated-file assertions remain equality/containment checks, not broad truthiness checks.
- Step reviewer: `code-reviewer`.
- Step gate: `uv run pytest tests/unit/infra`, then `uv run pytest tests/unit`.

### S06 integration lane migration

- Delegated role: `dev-coder`.
- Allowed paths: `tests/integration/test_discovery.py`, integration package markers only if collection evidence requires it.
- Forbidden changes: live external integration behavior or credentialed dependencies.
- Behavior goal: integration lane remains hermetic and pytest-native.
- Concrete test seed:
  - `tc-s06-001` integration lane: `uv run pytest tests/integration`.
- Step reviewer: `code-reviewer`.
- Step gate: no `unittest` import remains in `tests/integration`.

### S08 unittest absence cleanup and lane consolidation

- Delegated role: `dev-coder`.
- Allowed paths: tests only, limited to cleanup caused by S02-S06 migration.
- Forbidden changes: new feature tests, runtime optimization, docs/CI cutover.
- Behavior goal: all test implementation files are free of unittest framework dependency while preserving the three lane layout.
- Concrete test seeds:
  - `tc-s08-001` implementation absence: `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests` returns no migration-blocking matches.
  - `tc-s08-002` lane pass: `uv run pytest tests/unit`, `uv run pytest tests/integration`, and `uv run pytest tests/cli_runtime` pass.
  - `tc-s08-003` collection sanity: `uv run pytest --collect-only` does not collect fixture wheelhouse or cache artifacts.
- Step reviewer: `code-reviewer`.
- Step gate: scoped cleanup diff only; no skip / xfail addition without report rationale.

### S90 docs impact resolution and CI cutover

- Delegated role: `doc-writer` for README / AGENTS text; `dev-coder` for workflow and tests that assert command strings if needed.
- Allowed paths: `README.md`, `AGENTS.md`, `.github/workflows/provider-ci.yml`, tests that assert README / AGENTS / CI command strings.
- Forbidden changes: provider CI scope expansion beyond unit lane, shipped consumer CI changes, unrelated docs cleanup.
- Behavior goal: contributor-facing and CI-facing test contract uses pytest and the current lane names.
- Concrete test seeds:
  - `tc-s90-001` docs command grep: old unittest command references are gone from README / AGENTS / provider CI and test assertions.
  - `tc-s90-002` provider CI command: `.github/workflows/provider-ci.yml` runs `uv run pytest tests/unit` or an equivalent command aligned with `pyproject.toml` dependency setup.
  - `tc-s90-003` command-string tests: tests that assert docs/CI strings pass under `uv run pytest tests/unit`.
- Reviewer gates:
  - `code-reviewer` for workflow/tests changed in this step.
  - `spec-reviewer` for docs/spec alignment after doc changes.
- Step gate: docs/CI grep pass plus relevant unit tests.

### S99 final quality gate

- Delegated roles:
  - `qa-reviewer` for test sufficiency and assertion-strength review.
  - issue-wide `code-reviewer` for integrated diff review.
  - final `spec-reviewer` for requirement/design/plan/report/docs/test alignment.
- Allowed paths: no implementation edit unless a reviewer fail triggers bounded follow-up delegation.
- Behavior goal: prove complete pytest migration and record issue-ready evidence for the orchestrator.
- Required commands:
  - `uv run pytest --version`
  - `uv run pytest --collect-only`
  - `uv run pytest tests/unit`
  - `uv run pytest tests/integration`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest`
  - `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests`
  - `rg -n "unittest discover|Framework: `unittest`|tests/test_cli.py|tests/test_init_update.py" README.md AGENTS.md .github/workflows tests`
  - `git diff --check`
- Reviewer gates:
  - `qa-reviewer`: pass required.
  - issue-wide `code-reviewer`: pass required.
  - final `spec-reviewer`: pass required after canonical plan/report adoption by orchestrator.
- Step gate: any fail becomes bounded follow-up work; no reviewer pass is inferred from worker output.

## Test Strategy Mapping

- Red or alternative evidence:
  - S00 captures pytest absence/unconfigured evidence and current unittest grep baseline.
  - S01 uses collect-only as the first observable runner contract.
  - S02-S06 use focused lane or package commands as Green evidence.
  - S08 uses grep absence plus all lane commands as migration-completeness evidence.
  - S90 uses docs/CI grep and command-string test updates.
  - S99 uses full suite and reviewer gates.
- Required verification ladder:
  - First narrow: package/file/lane commands in each slice.
  - Then lane: `tests/unit`, `tests/integration`, `tests/cli_runtime`.
  - Then global: `uv run pytest`, grep absence, `git diff --check`.
- Test sufficiency risks:
  - Large mechanical conversion can weaken assertions.
  - Former `subTest` visibility can be lost unless parametrized or message-labeled.
  - Former `unittest.mock.patch` cleanup can accidentally broaden monkeypatch scope.
  - Runtime lane duration can hide late failures, so S99 must record full command outcome and duration if material.

## Review Gates

- Each code/test/config step uses `dev-coder` and then `code-reviewer` pass before commit.
- Docs text uses `doc-writer`; docs/spec alignment uses `spec-reviewer`.
- S90 mixes docs and CI/tests only if the canonical plan makes the reviewer focus explicit; otherwise split docs and test-command assertions into adjacent substeps.
- S99 requires fresh `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` passes.
- Worker output is not reviewer approval. A reviewer `fail` requires bounded follow-up delegation and fresh re-review.
- Plan adoption still requires main orchestrator integration into canonical `plan.md` and a fresh plan `spec-reviewer` pass.

## Rollback / Compatibility

- Compatibility:
  - Product runtime and CLI public contracts do not change.
  - Python 3.10+ policy remains unchanged.
  - Provider CI remains unit-lane-only.
  - Test lane names and directories remain `tests/unit`, `tests/integration`, and `tests/cli_runtime`.
- Rollback strategy:
  - Before S90, lane-local test conversions can be reverted by step commit if a migration slice fails.
  - If S01 dependency resolution fails, revert `pyproject.toml` and `uv.lock` first and do not proceed to test rewrites.
  - If S02 harness migration fails, stop before S03; do not partially migrate dependent runtime tests and claim progress.
  - After S90, rollback should revert the issue branch as a coordinated runner-contract cutover because docs, CI, and tests are intentionally synchronized.
- Amendment triggers:
  - Need for pytest plugins beyond pytest.
  - Need to preserve any `unittest` import as a permanent exception.
  - Provider CI scope expansion beyond `tests/unit`.
  - Test deletion, skip/xfail additions, or assertion weakening needed to make pytest pass.
  - Product runtime source change required to satisfy pytest migration.

## Docs Impact

- Docs / config targets:
  - `README.md` Testing section must list pytest lane commands.
  - `AGENTS.md` Build/Test and Testing Guidelines must reflect pytest and the current `tests/unit`, `tests/integration`, `tests/cli_runtime` layout.
  - `.github/workflows/provider-ci.yml` must run provider unit tests with pytest.
  - Tests that assert README / AGENTS / CI command strings must be updated with the docs/CI cutover.
- Out of scope:
  - Shipped consumer CI migration unless current provider docs/tests reveal a direct conflict.
  - Broad AGENTS rewrite outside test command and layout accuracy.
  - New coverage, xdist, or performance documentation.

## Final Quality Gate

Final gate should not replace per-step review. It should confirm integrated completeness after all step commits:

- `qa-reviewer` checks:
  - Assertion strength is preserved.
  - No test deletion, skip/xfail abuse, or coverage-intent shrink occurred.
  - Lane and full-suite verification are sufficient for AC-001 through AC-008.
- issue-wide `code-reviewer` checks:
  - `pyproject.toml`, `uv.lock`, CI, docs, tests, and helpers form a coherent pytest-only contract.
  - Helper/fixture changes remain local and do not introduce a test framework inside pytest.
  - No product runtime behavior changed unintentionally.
- final `spec-reviewer` checks:
  - Requirement/design/plan/report trace AC-001 through AC-009.
  - Parent Epic deferred-work boundary remains explicit.
  - Delegated draft evidence is adopted or rejected in `report.md` before being used.
  - No reviewer-pass, phase promotion, implementation readiness, issue ready, or issue finish is claimed by a draft.

## Plan Blockers

Plan Blockers: none.

Non-blocking adoption caveat:

- A formal post-run diff guard is still pending. Current `git status --short` before this draft already showed modified canonical issue docs and one untracked system-architect discussion. The orchestrator should treat this draft as adoption-ineligible until the expected single new discussion file and no additional side effects are verified against the actual baseline policy.

## Integration Notes for Main Orchestrator

Suggested canonical adoption path:

1. Verify this draft is the only new file created by this invocation.
2. Record the draft in `report.md` Delegated Draft Evidence with `adoption_status: unreviewed`, `reflected_to: []`, and `diff_guard_result` from the orchestrator's guard.
3. Adopt only the useful step structure into canonical `plan.md`; do not copy the draft's authority caveats as final plan authority.
4. Update canonical `report.md` Evidence Adoption Ledger with adopted, partially adopted, or rejected portions.
5. Run fresh plan `spec-reviewer` on canonical `plan.md` and upstream docs before implementation handoff.

Delegated Draft Evidence block:

- role: `spec-dock-implementation-planner`
- phase: plan
- scope: `iss-00167`
- source artifacts read: active context pack; active issue requirement/design/report; parent epic requirement/design/plan; workflow/phase/authoring docs; current pytest/unittest config, docs, CI, and representative tests
- draft artifact path: `spec-dock/active/issue/discussions/20260606t050446z-disc-pytest-migration-plan-proposal.md`
- draft status: produced
- authority: proposed
- adoption_status: unreviewed
- reflected_to: `[]`
- intended_targets: `spec-dock/active/issue/plan.md`, `spec-dock/active/issue/report.md`
- diff_guard_result: pending
- integration notes: use as a step-order and gate proposal only; main orchestrator owns canonical integration and plan review
- rejected portions: none identified by this draft
- blockers: none
- canonical artifacts edited: none
- final authority claimed: no

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
