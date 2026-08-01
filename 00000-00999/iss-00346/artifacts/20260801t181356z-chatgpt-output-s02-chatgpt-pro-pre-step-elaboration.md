# S02 ChatGPT Pro pre-step elaboration

## Scope and current-state assessment

S02 should begin as a test-only characterization slice. At the connector-observed HEAD `23a2c25eafa86ec0a02a3773a69c74b2b3e3be8e`, no production repair is justified. Reuse the S01 `candidate_wheel` fixture and installed-runtime helpers; change production only after a reproducible candidate-wheel failure.

The current behavior indicates that `spec-dock update` overwrites managed provider subtrees, copies root `.workbench/README.md` only for a fresh installation, and does not traverse existing `spec-dock/initiatives/**` as an update-managed subtree. Existing Initiative/Epic/Issue shells should therefore remain absent while future nodes created after update receive shells. This is advisory; canonical requirement/design/plan remain authoritative.

Allowed primary path is `tests/integration/test_epic_00343_distribution.py`, with `tests/unit/infra/test_init_update.py` only for focused characterization. Repair-only paths are `src/spec_dock/cli.py` and the four Workbench README templates. Do not add migration/backfill modes, schema rewrites, unrelated template changes, historical fixtures, or root copy expansion.

## Test cards and negative controls

Use one synthetic current-runtime hierarchy and exactly four cards:

1. `test_tc_346_s02_001_existing_consumer_fixture_is_valid_without_readmes`: create Initiative `401`, Epic `402`, Issue `403` through the installed runtime; remove the four existing README files; keep directories; add one ignored untracked payload under the Issue Workbench; replace `spec-dock/docs/guide.md` with fixed bytes different from the wheel asset; validate and snapshot before update.
2. `test_tc_346_s02_002_existing_consumer_update_preserves_data_without_backfill`: run installed `spec-dock update`; existing four README paths stay absent; canonical and `.meta.json` bytes, graph/dependency snapshot, payload bytes/ignore/untracked state remain unchanged; only the intentionally stale `docs/guide.md` becomes equal to the wheel asset.
3. `test_tc_346_s02_003_existing_consumer_future_nodes_receive_workbench_shell`: after update create future `501/502/503`; each future README must equal its corresponding wheel template and be tracked, while all four preexisting scopes remain README-absent and payload remains unchanged/untracked.
4. `test_tc_346_s02_004_existing_consumer_illegal_preexisting_readme_is_rejected`: inject exactly one README into a preexisting scope (prefer Issue `403`) and assert the fixture preflight fails naming that exact path before update.

Use wheel-projected assets, not the source checkout, for template comparisons. Reuse S01 helpers (`candidate_wheel`, `_runtime_env`, `_run_installed_runtime`, `_find_node`, `_Issue69Harness`). Avoid a new snapshot framework; a test-local immutable dict/tuple is sufficient.

## Minimal implementation sequence

1. Re-read branch/head/status and bind a fresh S02 candidate revision; do not hard-code the pre-step HEAD.
2. Reuse S01 build/install and runtime helpers. Add only narrow helpers for wheel asset bytes, synthetic hierarchy, immutable snapshot, and README matrix.
3. Add legal fixture and illegal README negative first; confirm sensitivity.
4. Add update characterization before any production change. If green, record `production_repair_justified=false`; if not, preserve before/after matrix and localize the installer path before a repair.
5. Add future-only shell characterization and recheck preexisting absence.
6. Run focused nodes, the canonical unit selector, `git diff --check`, and clean-state checks. Return exact nodes/results and report-ready content-free evidence; the worker does not edit canonical reports.
7. Push any implementation/test commit and obtain a fresh current-head ChatGPT Pro code review. A changed HEAD requires a new wheel receipt.

## Verification and evidence receipt

Focused command:

```bash
uv run pytest \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s02_001_existing_consumer_fixture_is_valid_without_readmes \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s02_002_existing_consumer_update_preserves_data_without_backfill \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s02_003_existing_consumer_future_nodes_receive_workbench_shell \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s02_004_existing_consumer_illegal_preexisting_readme_is_rejected \
  --run-full-regression
```

Canonical checks:

```bash
git rev-parse HEAD
git status --short
uv run pytest tests/unit/infra/test_init_update.py -k 'update and workbench'
uv run pytest tests/integration/test_epic_00343_distribution.py -k 'existing_consumer or no_backfill or future_node' --run-full-regression
git diff --check
git status --short
```

Record branch, pre/post HEAD/status, fresh candidate basename/SHA and isolated origin, existing/future node IDs, README presence matrix, ignored payload relative path and equality/ignore/tracked booleans, canonical/metadata/graph equality, intended managed delta, exact test node IDs/results, `production_repair_justified`, review head/status, and changed paths. Do not reproduce payload/body/digest/count values beyond the receipt fields required by the canonical plan.

## Stop conditions and non-goals

Stop without expanding implementation if HEAD moves, wheel cannot be uniquely bound, the fixture fails validation/graph load, any existing README is present before the positive case, stale `guide.md` is not observably different, existing canonical data or ignored payload changes, an existing README appears during update/future creation, a repair needs an unlisted path, or a migration/public API/history fixture is required.

S02 does not implement backfill/migration, historical-revision machinery, generic snapshot frameworks, new schemas/selectors/commands, root `workbench copy`, generic import/privacy/platform publication (S03), opaque lifecycle/dogfood (S04), or canonical report edits by the worker.

## Assumptions and uncertainty

The no-backfill behavior is source-backed at the observed branch but must still be proven through the candidate wheel. `401/402/403` and `501/502/503` are deterministic test data only. The large unit test file must be inspected locally before adding characterization; do not duplicate existing nodes. A production repair is justified only by a reproducible installer/template failure; a green characterization remains test-only.
