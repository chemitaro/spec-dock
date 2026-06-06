---
created_by_role: spec-dock-system-architect
scope_id: iss-00167
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/phase_design.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/workflow_issue.md
  - pyproject.toml
  - README.md
  - AGENTS.md
  - .github/workflows/provider-ci.yml
  - tests/cli_runtime/harness.py
  - tests/unit/application/test_check_deps.py
  - tests/unit/domain/test_delegated_authoring.py
  - tests/unit/infra/test_init_update.py
  - tests/integration/test_discovery.py
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_delegated_authoring.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
adoption_ledger_note: Main orchestrator must decide adoption in canonical report.md before reflecting any portion to canonical design.md or plan.md.
---

# Pytest Complete Migration Design Proposal

## Requirement Coverage

- Covers AC-001 through AC-009 by treating pytest as the only standard test runner contract across dependency metadata, collection config, test implementation, provider CI, README, AGENTS, and verification evidence.
- Preserves the post-`iss-00160` lane split: `tests/unit`, `tests/integration`, and `tests/cli_runtime` remain the execution and documentation boundaries.
- Treats `unittest.TestCase`, `self.assert*`, `assertRaises*`, `self.subTest`, `unittest.main()`, and `unittest.mock` imports as migration targets rather than compatibility leftovers.
- Keeps parent Epic trace explicit: this is deferred testing / regression infrastructure work under `epic-00158`, not a replacement for first-wave skill/docs/templates cleanup or runtime gate implementation.
- Does not change runtime public behavior, CLI contracts, shipped consumer CI, Python version policy, or add pytest plugins beyond pytest itself.

## Existing Context Findings

- Requirement gate evidence in `report.md` records fresh requirement re-review pass and promotion to design.
- `pyproject.toml` has no pytest dependency or pytest configuration. Runtime dependency remains only `tomli` for Python < 3.11.
- `README.md`, `AGENTS.md`, and `.github/workflows/provider-ci.yml` still present `python -m unittest discover` as the standard test entrypoint.
- The provider CI installs the package with `python -m pip install -e .` and runs only `python -m unittest discover -s tests/unit`.
- Test topology currently contains 55 Python files under `tests/unit`, `tests/integration`, and `tests/cli_runtime`.
- `rg -l` shows unittest-style dependency across README, AGENTS, provider CI, `tests/cli_runtime/harness.py`, most `tests/cli_runtime/test_*.py`, and representative unit tests.
- `tests/cli_runtime/harness.py` is the deepest migration boundary because `CliRuntimeHarness(unittest.TestCase)` owns runtime helpers, `skipTest`, `assert*`, temp cleanup, gh stubs, and runtime subprocess assertions used by many heavy tests.
- Unit tests mix plain helper classes with `unittest.TestCase`; many can migrate mechanically to plain functions once assertions and temp directory usage are converted.
- Integration currently has discovery smoke only, but it must still be collected and documented as a pytest lane.

## Design Decisions

1. Make pytest the only supported runner contract.
   - Add pytest as a development/test dependency and configure pytest discovery for the current lane layout.
   - Do not rely on pytest collecting `unittest.TestCase` as a transitional completion criterion.

2. Convert from the shared harness outward.
   - First migrate `tests/cli_runtime/harness.py` into pytest-native helper functions / fixtures because downstream CLI runtime tests depend on it.
   - Then migrate heavy CLI runtime tests, then unit and integration tests, while keeping lane-specific commands green.

3. Preserve helper locality instead of creating a new framework.
   - Keep test helpers near existing test lanes unless repeated pytest fixtures clearly reduce duplication.
   - Use `conftest.py` only for fixtures shared by a lane or the whole test suite; avoid broad global fixtures for single-file needs.

4. Keep CI installation simple.
   - Provider CI should install project plus test dependency in a way consistent with `uv run pytest` local commands.
   - If the project chooses optional dependency metadata, CI can use `python -m pip install -e ".[test]"`; if not, CI can install pytest explicitly. The canonical design should pick one and keep README / AGENTS aligned.

5. Treat docs and command-string tests as part of the behavioral contract.
   - Update README, AGENTS, provider CI, and tests that assert command strings in the same migration lane as test code.

## Alternatives Considered

- Pytest runner only, leaving `unittest.TestCase` tests intact.
  - Rejected because requirement AC-006 defines complete migration as removal of unittest framework and assertion API dependency.
- Big-bang conversion of all tests after adding pytest.
  - Risky because `tests/cli_runtime` is large and harness-coupled; failure localization would be poor.
- Introduce broad custom assertion helpers to mimic `self.assert*`.
  - Rejected unless a helper hides meaningful complexity. Plain assert and pytest-native facilities should be the default.
- Add pytest-xdist or coverage at the same time.
  - Rejected as non-scope; runtime optimization and coverage policy are separate follow-up concerns.

## Boundary / Contract Model

- Source of runner contract:
  - `pyproject.toml` owns dependency and pytest collection defaults.
  - README / AGENTS own contributor-facing commands and lane descriptions.
  - `.github/workflows/provider-ci.yml` owns provider CI test entrypoint.
  - `tests/` owns pytest-native implementation.
- Test lane contract:
  - Unit lane: `uv run pytest tests/unit`.
  - Integration lane: `uv run pytest tests/integration`.
  - Runtime / CLI lane: `uv run pytest tests/cli_runtime`.
  - Full fallback: `uv run pytest`.
- Compatibility contract:
  - Existing test intent, hermeticity, gh stubs, temp directories, and runtime subprocess isolation must remain.
  - No official `python -m unittest discover` fallback remains in docs or CI after completion.
- Authority contract:
  - This draft is proposal evidence only. Canonical adoption belongs in `report.md`, and design authority requires orchestrator integration plus fresh reviewer pass.

## Dependency Analysis

- Upstream prerequisite:
  - Requirement gate pass is recorded in `report.md`.
  - `iss-00160` post-merge test topology is treated as fixed input.
- Implementation dependency order:
  - Add pytest dependency and collection config first so migration can be checked incrementally.
  - Migrate shared CLI runtime harness before its subclasses.
  - Migrate CLI runtime tests after harness because they inherit its helper API.
  - Migrate unit tests by package group; most depend only on local stubs and runtime module import helpers.
  - Migrate integration discovery smoke after unit conventions are established.
  - Update README / AGENTS / provider CI and command-string assertions after command names are final.
  - Run grep-based contract checks last to prove no unittest framework dependency remains.
- Risk dependencies:
  - `skipTest` must become `pytest.skip`.
  - `self.subTest` must become `pytest.mark.parametrize` or explicit assertion messages.
  - `unittest.mock.patch` must become `monkeypatch` where possible; `unittest.mock` should not remain as an import path if AC-006 is interpreted literally.
  - `tempfile.TemporaryDirectory` may remain as a Python context manager only if the requirement allows it; prefer `tmp_path` / `tmp_path_factory` for pytest idiom and cleanup clarity.

## Source of Record

- Provider source of truth remains `src/spec_dock/` for runtime and shipped asset behavior, but this issue primarily changes test infrastructure and contributor-facing commands.
- `spec-dock/active/issue/requirement.md` is the WHAT / WHY source of record for complete migration.
- `spec-dock/active/issue/design.md` should become the HOW source of record after orchestrator adoption.
- `spec-dock/active/issue/plan.md` should own executable step sequencing, reviewer gates, and per-step verification.
- `spec-dock/active/issue/report.md` should record adoption, test evidence, grep evidence, reviewer gate outcomes, and any exception rationale.

## Data Flow / Domain Model / Interface Contract

- No product domain model or CLI runtime data flow should change.
- Test execution flow after migration:
  - Developer / CI invokes `uv run pytest [lane]`.
  - Pytest reads project configuration from `pyproject.toml`.
  - Pytest collects test functions / classes under `tests/unit`, `tests/integration`, and `tests/cli_runtime`.
  - Fixtures provide temp paths, monkeypatching, gh stubs, and runtime invocation helpers.
  - Assertions use plain `assert`, `pytest.raises`, and parametrized cases.
- Interface contract for helpers:
  - Runtime helpers should return subprocess results or raise assertion errors via plain assert statements.
  - Helpers should not require inheritance from `unittest.TestCase`.
  - Shared gh stub creation should remain hermetic and local to temp directories.

## File / Module Change Plan

```text
pyproject.toml
|-- add pytest dependency / optional test dependency
`-- add minimal [tool.pytest.ini_options] for current tests layout

.github/workflows/provider-ci.yml
`-- change provider unit test command to pytest

README.md
`-- replace Testing commands and lane descriptions with pytest commands

AGENTS.md
`-- replace Build/Test and Testing Guidelines unittest contract with pytest contract

tests/
|-- conftest.py                         (only if shared project-wide fixtures are justified)
|-- unit/
|   |-- conftest.py                     (only for unit-lane shared runtime import/tmp helpers)
|   `-- **/test_*.py                    convert TestCase/assert/subTest/raises patterns
|-- integration/
|   `-- test_discovery.py               convert smoke test to pytest function/parametrize
`-- cli_runtime/
    |-- harness.py                      convert inheritance helper to pytest-native helper module
    |-- conftest.py                     add runtime fixtures if repeated by many tests
    `-- test_*.py                       convert subclasses and assertions to pytest style
```

- Do not introduce new top-level test directories.
- Do not move tests back to legacy `tests/test_cli.py` / `tests/test_init_update.py` layout.
- Empty old directories or pycache should be touched only if they affect collection, docs, or grep evidence.

## Migration / Compatibility / Rollback

- Migration strategy:
  - Use a hard cutover for the official runner contract: once docs / CI move to pytest, do not keep unittest as a supported fallback.
  - Internally sequence changes so each lane can be run with pytest as it is converted.
  - Preserve assertion strength by mapping each old `self.assert*` to equivalent or clearer plain assert / pytest assertion.
- Compatibility:
  - Public package runtime and CLI behavior should remain unchanged.
  - Python 3.10+ support remains unchanged.
  - Local developer commands change from `python -m unittest discover...` to `uv run pytest...`.
  - Provider CI behavior remains unit-lane-only unless plan explicitly decides to broaden it; requirement only requires provider CI unit job to use pytest.
- Rollback:
  - Revert dependency/config/docs/CI/test changes as a single issue branch rollback if migration fails globally.
  - For implementation steps, rollback can be lane-local before docs/CI cutover is finalized.
  - If pytest dependency resolution fails, revert `pyproject.toml` / lock changes first and leave tests/docs untouched until dependency path is fixed.
  - If harness migration fails, stop before converting dependent CLI runtime tests; do not partially claim complete migration.

## Observability

- Primary evidence:
  - `uv run pytest --version`
  - `uv run pytest --collect-only`
  - `uv run pytest tests/unit`
  - `uv run pytest tests/integration`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest`
- Contract evidence:
  - `rg -n "unittest|self\\.assert|assertRaises|subTest|unittest\\.main|from unittest|import unittest" tests`
  - `rg -n "unittest discover|Framework: `unittest`|tests/test_cli.py|tests/test_init_update.py" README.md AGENTS.md .github/workflows tests`
  - `rg -n "pytest" uv.lock pyproject.toml tests README.md AGENTS.md .github/workflows/provider-ci.yml`
- Report evidence should include command result summaries, not raw transcripts.
- Full suite duration should be recorded if it materially affects later plan or reviewer decisions, but runtime optimization remains out of scope.

## Test Strategy

- Red / baseline evidence:
  - Before implementation, record that pytest is unavailable or unconfigured via `uv run pytest --version` / `uv run pytest --collect-only`, if dependency state allows.
  - Record current unittest dependency grep output as migration baseline.
- Green strategy by lane:
  - Dependency/config: `uv run pytest --version` and `uv run pytest --collect-only`.
  - Unit lane: migrate representative unit groups and verify with `uv run pytest tests/unit`.
  - Integration lane: verify `uv run pytest tests/integration`.
  - CLI runtime lane: migrate harness first, then heavy tests, verifying with `uv run pytest tests/cli_runtime`.
  - Full regression: verify `uv run pytest`.
- Regression preservation:
  - For `self.subTest`, prefer parametrization so case-level failure visibility improves or remains equivalent.
  - For exception checks, use `pytest.raises(..., match=...)`.
  - For patching, prefer `monkeypatch` and fixture-scoped temp paths.
  - For skipped environment conditions, use `pytest.skip` inside helper functions or pytest marks where static.
- Final QA focus:
  - Check no test was deleted or weakened to satisfy migration.
  - Check no new live network / credentialed dependency was introduced.
  - Check docs, CI, and command-string assertions all agree.

## ADR Candidates

- No ADR is required for the local pytest migration itself if it remains issue-local and reversible.
- ADR candidate if the project chooses a durable dependency policy such as a standardized `[project.optional-dependencies] test = [...]` contract for all future provider tooling.
- ADR candidate if provider CI scope is broadened beyond unit lane as a long-lived CI policy change. Current requirement does not require that expansion.

## Risks

- Large mechanical conversion can accidentally weaken assertions or skip tests.
- `tests/cli_runtime` migration may be noisy because inheritance-based helpers currently hide many assertions and cleanup paths.
- Literal AC-006 interpretation may reject any `unittest.mock` import even though `mock` is a stdlib utility; design/plan should choose a clear replacement policy before implementation.
- Provider CI currently uses pip, while requirement examples use `uv run pytest`; dependency installation policy must be explicit enough that local and CI commands do not drift.
- Full `uv run pytest` may be slow due to runtime / CLI regression tests; do not respond by skipping or shrinking tests unless requirement is amended.
- Existing docs in AGENTS include current repository map that mentions old `tests/domain_runtime` / `tests/presentation_runtime`; docs update must avoid stale path claims.

## Requirement Clarification Requests

- none blocking.
- Non-blocking design gap for orchestrator decision: choose whether pytest is added as a plain project dependency, an optional `test` extra, or dependency-group metadata. Recommended: optional test extra if compatible with the repo's packaging policy, because pytest is tooling-only and CI can install `.[test]`.
- Non-blocking design gap for orchestrator decision: decide whether AC-006 forbids `unittest.mock` specifically or all imports under `unittest`. Recommended: treat all `unittest` imports as forbidden and use `monkeypatch` / pytest fixtures / direct fakes.
- Non-blocking plan gap: decide whether provider CI should remain unit-only with pytest or add separate integration / CLI runtime jobs. Recommended: keep provider CI unit-only for this issue unless user or maintainer explicitly expands CI policy.

## Integration Notes for Main Orchestrator

Delegated draft evidence:

- role: `spec-dock-system-architect`
- phase: requirement/design
- scope: `iss-00167`
- source artifacts read: active context, issue requirement/report, parent epic requirement/plan, design/spec-authoring/issue workflow docs, package metadata, README, AGENTS, provider CI, CLI runtime harness, representative unit/integration/CLI runtime tests
- draft artifact path: `spec-dock/active/issue/discussions/20260606t045218z-disc-pytest-complete-migration-design-proposal.md`
- draft status: `produced`
- authority: `proposed`
- adoption_status: `unreviewed`
- reflected_to: `[]`
- intended_targets: `spec-dock/active/issue/design.md`, `spec-dock/active/issue/plan.md`, `spec-dock/active/issue/report.md`
- diff_guard_result: `pending`
- integration notes: adopt the dependency order, harness-first migration boundary, pytest lane commands, rollback model, and non-blocking design gaps if they align with canonical design judgment
- rejected portions: none
- blockers: none
- canonical artifacts edited: `none`
- final authority claimed: `no`

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
