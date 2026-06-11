---
種別: discussion
ID: "20260611t161800z-disc-pr-repair-batch"
タイトル: "PR #181 repair batch"
作成者: "codex"
作成日: "2026-06-11"
関連PR: "https://github.com/chemitaro/spec-dock/pull/181"
head_sha: "2fa6da0d2f55a07eb6c60bbd01d1f7a67234c75b"
---

# PR #181 Repair Batch

## Context
- PR: https://github.com/chemitaro/spec-dock/pull/181
- Base: `main`
- Head branch: `iss-00180-github-token-capability-preflight`
- Observed head SHA: `2fa6da0d2f55a07eb6c60bbd01d1f7a67234c75b`
- Observation command:
  - `./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh --repo chemitaro/spec-dock --pr 181 --head-sha 2fa6da0d2f55a07eb6c60bbd01d1f7a67234c75b --timeout-seconds 1200 --poll-interval-seconds 30 --quiet-seconds 90 --same-fingerprint-count 2 --zero-check-grace-polls 2 --body-mode trigger-window-truncated --out /private/tmp/iss-00180-pr181-observation`
- Observation result:
  - `normalized_status=failed`
  - `overall_status=failed`
  - CI: one `provider-tests` failure, one `provider-tests` run still in progress at observation terminal point.
  - Review: Codex review completed with 3 unresolved P2 comments.

## Concern Catalog
| concern_id | label | summary | root cause hypothesis |
|---|---|---|---|
| C001 | check_failure:provider-tests | Full provider suite fails on stale checked-in dogfooding metadata snapshot | `iss-00180` import added `.meta.json`; snapshot constant was not updated in final focused selector |
| C002 | check_failure:provider-tests | Full provider suite fails on old wait-contract expectation | PR metadata rate-limit failures are now classified as `github_rate_limited`, but legacy test expects generic `pr_metadata_collection_failed` |
| C003 | review_feedback:github-capability-classifier | Runtime doctor classifier misses `Resource not accessible by integration` | S99 follow-up fixed PR metadata classifier, but not runtime doctor classifier or checks snapshot helper |
| C004 | review_feedback:token-source | Runtime doctor reports `gh_saved_auth` when only `GITHUB_TOKEN` is set | `_token_source()` only checks `GH_TOKEN` |
| C005 | review_feedback:missing-gh | Runtime doctor raises `FileNotFoundError` when `gh` is absent | `_run_fixed_gh()` does not convert missing binary into a diagnostic process-like result |
| C006 | review_feedback:pr-observation-token-source | PR metadata / trigger write limitations report `gh_saved_auth` when only `GITHUB_TOKEN` is set | PR observation script token-source helpers only checked `GH_TOKEN`; trigger permission matching also missed integration wording |

## Inventory
| item_id | source | source_link | failure_class | concern_id | validity | risk_class | need_to_fix | disposition | status |
|---|---|---|---|---|---|---|---|---|---|
| I001 | GitHub Actions `provider-tests` | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` | `check_failure:provider-tests` | C001 | valid | blocking | yes | fix-now | triaged |
| I002 | GitHub Actions `provider-tests` | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_wait_stdout_stderr_progress_and_out_contract` | `check_failure:provider-tests` | C002 | valid | blocking | yes | fix-now | triaged |
| I003 | Codex review P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py` line 155 | `review_feedback:github-capability-classifier` | C003 | valid | material-follow-up | yes | fix-now | triaged |
| I004 | Codex review P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py` line 141 | `review_feedback:token-source` | C004 | valid | material-follow-up | yes | fix-now | triaged |
| I005 | Codex review P2 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py` line 106 | `review_feedback:missing-gh` | C005 | valid | material-follow-up | yes | fix-now | triaged |
| I006 | local code-review P2 | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh` token_source | `review_feedback:pr-observation-token-source` | C006 | valid | material-follow-up | yes | fix-now | triaged |
| I007 | local code-review P2 | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh` token_source | `review_feedback:pr-observation-token-source` | C006 | valid | material-follow-up | yes | fix-now | triaged |

## Per-Concern Analysis
### C001
- Validity: valid.
- Need-to-fix: yes.
- Root cause: dogfooding `.meta.json` snapshot constant did not include imported issue `iss-00180`.
- Recommended design: update only the checked-in snapshot constant / expectation, preserving the contract that the dogfooding tree has no legacy `deps.json`.

### C002
- Validity: valid.
- Need-to-fix: yes.
- Root cause: classifier improvement changed a metadata collection failure from generic to typed rate-limit limitation.
- Recommended design: update the legacy wait-contract test to expect `github_rate_limited` plus rate-limit fields, if that is now the intentional contract.

### C003
- Validity: valid.
- Need-to-fix: yes.
- Root cause: runtime doctor and checks collector classifier still miss integration permission wording.
- Recommended design: add `resource not accessible by integration` to permission-denied classifiers and cover with focused tests.

### C004
- Validity: valid.
- Need-to-fix: yes.
- Root cause: token source logic handles `GH_TOKEN` but not `GITHUB_TOKEN`.
- Recommended design: return `GITHUB_TOKEN` when only that env var is present, preserving `GH_TOKEN` precedence.

### C005
- Validity: valid.
- Need-to-fix: yes.
- Root cause: missing `gh` binary escapes as `FileNotFoundError`.
- Recommended design: convert missing binary to a diagnostic with `auth_missing` or equivalent prerequisite-unavailable status, without treating it as structural doctor failure.

### C006
- Validity: valid.
- Need-to-fix: yes.
- Root cause: runtime doctor and checks helper were fixed for `GITHUB_TOKEN`, but PR metadata and trigger write helpers still used the old `GH_TOKEN`-only source logic.
- Recommended design: use the same `GH_TOKEN` -> `GITHUB_TOKEN` -> `gh_saved_auth` precedence in all PR observation token-source helpers.

## Repair Queue
| unit_id | covered_items | owner | status | validation |
|---|---|---|---|---|
| U001 | I001-I007 | dev-coder | implemented | focused tests, full `tests/unit/infra/test_init_update.py`, runtime doctor suite, mirror diffs, `validate`, `git diff --check` |

## Unit Discussion Plan
- A separate repair unit is not necessary because the five items are a single bounded PR repair pass and all changes are within iss-00180's existing surfaces:
  - runtime doctor GitHub capability adapter and tests
  - PR observation checks/snapshot scripts and tests
  - checked-in dogfooding metadata snapshot
  - provider/dogfooding mirrors

## Stop Conditions
- Stop for human decision if fixing requires broad GitHub API scanning, credential repair, live GitHub tests, changing workflow permissions, resolving review threads, or PR merge.

## Merge-Prepared Gate
- Required before merge-prepared:
  - U001 implemented and committed.
  - Branch pushed.
  - PR observation rerun on latest head SHA.
  - No required check failure remains.
  - Codex review findings are stale/resolved by newer commit or no blocking unresolved findings remain.
  - Any remaining limitation is explicitly classified and not hidden.

## Implementation Result
- U001 status: implemented, commit pending.
- I001: fixed by adding `iss-00180` checked-in dogfooding `.meta.json` path and `depends_on=[]` expectation.
- I002: fixed by updating the wait-contract test to expect typed `github_rate_limited` / `rate_limited` / `wait_or_retry_later`.
- I003: fixed by classifying `Resource not accessible by integration` as permission denied in runtime doctor and PR observation checks helper.
- I004: fixed by adding `GITHUB_TOKEN` token source with `GH_TOKEN` precedence.
- I005: fixed by converting missing `gh` binary into `auth_missing` diagnostic instead of letting `FileNotFoundError` escape.
- I006: fixed by adding `GITHUB_TOKEN` token source handling to PR metadata limitation output with `GH_TOKEN` precedence.
- I007: fixed by adding `GITHUB_TOKEN` token source handling to trigger write limitation output with `GH_TOKEN` precedence and classifying trigger write `Resource not accessible by integration` as permission denied.

## Validation Result
- `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> 41 passed
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_wait_stdout_stderr_progress_and_out_contract -q` -> 1 passed
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q` -> 1 passed
- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_180_s02_checks_collector_maps_integration_permission_denied -q` -> 1 passed
- `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 and (pr_metadata or trigger)'` -> 7 passed, 331 deselected
- `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_180_s02 and trigger'` -> 4 passed, 334 deselected
- `uv run pytest tests/unit/infra/test_init_update.py -q` -> 338 passed
- `diff -qr -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime` -> clean
- `diff -qr -x __pycache__ src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation` -> clean
- `./spec-dock/scripts/spec-dock validate` -> ok nodes=92
- `git diff --check` -> pass

## Re-observation Plan
- Commit U001.
- Push branch.
- Re-run `wait_pr_observation.sh` against PR #181 latest head SHA.
- Treat previous Codex P2 threads as resolved only if they become stale on the new head or the new observation has no blocking unresolved findings.
