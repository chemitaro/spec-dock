# Read-only combined review

**overall_verdict: `PASS`**

This review follows the authoritative exact-head, read-only, defect-only S020 review contract. 

The prior P1—rejection of a legitimate Git-created `HEAD.lock` at mode `0644` under umask `0022`—is closed at the inspected exact HEAD. No concrete, reproducible, contract-breaking P0 or P1 defect remains in the bounded lock-mode repair.

## Repository identity

* **Repository:** `chemitaro/spec-dock`
* **Required and inspected branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Required and inspected exact HEAD:** `42e2af3fd89ac956541ede4e65992684ac86eb69`
* **PR:** `#351`
* **Exact feature branch inspected:** yes
* **Default branch:** `main`
* **Default-branch source or fallback used:** **no**
* **Fallback result:** not attempted and not applicable

The GitHub connector confirmed PR #351 has the required feature branch and exact head SHA.  A direct GitHub comparison between the required SHA and the named branch returned `identical`, with zero commits ahead or behind.

## 1. SPEC perspective

**P0 count:** 0
**P1 count:** 0

### Findings

**None.**

### Assessment

The canonical publication contract requires validation, a dedicated local commit, push, and equality of the local commit, remote branch HEAD, and commit tree before returning `ready/adoption_published`. Post-commit publication failure must retain the local commit for same-operation retry rather than reset or amend it.

The Design preserves the same failure semantics: pre-commit failures are rollback candidates, unverified restoration becomes `recovery_required`, post-commit publication uncertainty becomes `publication_pending`, and remote divergence remains fail-closed without force push.  The Plan correspondingly requires publication retry, remote-parity verification, and derivation of `ready` only from the complete Review/Human/parity/validation/publication conjunction.

The repaired implementation now accepts the ordinary Git lock modes that caused the prior failure while preserving these publication and failure contracts. The current Report records the exact bounded repair, provider/projection parity, positive `0022` and `0077` coverage, and the remaining fresh-review gate without claiming premature merge readiness.

The earlier formal S020 FAIL identified one underlying defect across its SPEC, CODE, and QA perspectives: exact `0600` validation rejected the valid `0644` lock produced by Git under umask `0022`.  The current repair directly removes that contradiction rather than changing the surrounding specification.

## 2. CODE perspective

**P0 count:** 0
**P1 count:** 0

### Findings

**None.**

### Assessment

The provider implementation now gives `_OperationBranchLock` an explicit captured `mode` field. Every subsequent `assert_held()` check requires both the descriptor and pathname to remain regular files owned by the effective UID, to retain the captured device and inode, and to retain exactly the captured mode. It also continues to require the prepared Git child transaction to remain live. Fallback cleanup independently requires the same captured mode and identity before unlinking.

After Git acknowledges `prepare: ok`, `_acquire_operation_branch_lock()`:

1. Opens the existing `HEAD.lock` without `O_CREAT` and with no-follow semantics.
2. Reads the descriptor and pathname metadata.
3. Requires both objects to be regular and effective-UID-owned.
4. Requires descriptor/pathname mode equality.
5. Requires descriptor/pathname device and inode equality.
6. Applies `_git_ref_lock_mode_is_compatible(mode)`, implemented as `(mode & ~0o666) == 0`, which rejects execute and special bits while accepting permission subsets derivable from Git’s `0666` request.
7. Rechecks that the Git transaction remains live.
8. Captures the observed device, inode, and mode only after the complete predicate succeeds.

Thus, ordinary `0644` and restrictive `0600` modes are accepted at acquisition, but a later transition between those modes is rejected because later checks use exact captured-mode equality. A pre-capture ambiguity remains on the abandonment path; a fully captured lock remains eligible only for checked abort and exact captured-object cleanup. This matches the bounded Blue Team decision. 

The production path does not read, force, or modify the process umask and does not `chmod` or `fchmod` the Git-created lock. The fixed `0600` requirements for private operation evidence and transaction workspaces remain separate and unchanged.

The shared-ref transaction lifetime is also preserved. Initial publication holds one guard through branch proof, push, post-push proof, remote commit/tree parity, publication evidence, durable `REMOTE_PARITY`, and result construction.  Resume publication acquires the same guard before selecting retry-push or already-remote parity processing.

Provider authority and dogfood projection resolve to the same Git blob SHA, `382a7b57b7936771b47bd43b4a53bf14733a3df4`.   No public status, reason, schema, CLI, Oracle boundary, Candidate contract, Human-decision contract, or publication-state semantic change was introduced.

## 3. QA perspective

**P0 count:** 0
**P1 count:** 0

### Findings

**None.**

### Assessment

The ordinary unit suite now contains the real-Git characterization:

* `test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask`

  * umask `0022` → captured mode `0644`
  * umask `0077` → captured mode `0600`

The same unit surface parameterizes successful teardown and abort failure over both `0600` and `0644`, verifies preservation on post-capture mode change, verifies preservation when the mode changes after checked abort but before fallback cleanup, and retains replaced-lock and disappeared-lock regressions.

The full-regression integration surface includes:

* `test_operation_branch_lock_successful_teardown_releases_prepared_locks`, covering both `0022 → 0644` and `0077 → 0600`;
* `test_initial_publication_succeeds_with_git_lock_mode_from_umask_0022`;
* `test_resume_publication_succeeds_with_git_lock_mode_from_umask_0022`;
* `test_already_remote_publication_succeeds_with_git_lock_mode_from_umask_0022`.

Those tests require `ready/adoption_published`, durable `REMOTE_PARITY`, exact local/remote commit convergence, publication evidence, and absence of both `.git/HEAD.lock` and the shared branch-ref lock after teardown. The direct teardown test also proves that a competing linked-worktree ref update is blocked while the transaction is prepared and succeeds after release.

The existing foreign-lock acquisition and publication regressions remain present, alongside the prior replaced/disappeared-lock and linked-worktree shared-ref exclusion coverage. The former false-PASS condition is therefore covered both in the ordinary unit lane and in initial, retry-push, and already-remote full publication paths.

The exact-head Report records these verification outcomes:

* focused lock/publication lane: `13 passed`;
* complete Apply unit/application/integration lane: `282 passed in 77.76s`;
* ordinary suite: `1373 passed, 2235 skipped`;
* Ruff check and formatting: pass;
* mypy over 287 files: pass;
* SpecDock validation: `nodes=227`;
* `git diff --check`: pass;
* provider/dogfood SHA-256 parity: pass.

The GitHub connector additionally reported successful exact-SHA runs for both `CI` and `Provider CI`; the provider job completed its static-analysis and pytest steps successfully.

## Verification summary

### Exact GitHub binding verified

* Repository access through the GitHub connector: **verified**
* Required feature branch existence: **verified**
* Required branch HEAD equals `42e2af3fd89ac956541ede4e65992684ac86eb69`: **verified**
* PR #351 head branch and head SHA: **verified**
* Default branch inspected as a source or fallback: **no**
* Source drift from the required exact HEAD: **none observed**

### Exact files inspected

Canonical and evidence:

* `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/requirement.md`
* `.../design.md`
* `.../plan.md`
* `.../report.md`
* `.../artifacts/20260801t185408z-pr-351-s020-mode-compatibility-combined-review-fail.md`
* `.../artifacts/20260801t191908z-pr-351-s020-lock-mode-blue-chatgpt-work-packet.md`

Implementation and projection:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

Tests:

* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

The initial-publication and resume/already-remote call sites were inspected in the exact provider file. Attached provider and unit-test copies were also checked against the GitHub exact-head content where available.

### Commands and evidence inspected

The following prescribed or recorded verification commands were inspected:

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_mode_change_is_preserved_without_protocol_abort \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_mode_change_after_abort_is_preserved_without_fallback_unlink
```

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_successful_teardown_releases_prepared_locks \
  tests/integration/test_issue_planning_apply.py::test_initial_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_resume_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_already_remote_publication_succeeds_with_git_lock_mode_from_umask_0022
```

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py

uv run pytest -q
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

Provider/dogfood blob and byte parity were also inspected.

### Verification limits

The complete repository test suite, lint suite, and full integration suite were not independently re-executed in this review thread; their exact-head Report evidence and successful GitHub Actions outcomes were inspected. A focused subset of ten exact lock-mode unit cases was independently executed against the supplied exact source in an isolated harness and passed. No contrary runtime evidence or unresolved P0/P1 was found.

**No patch, replacement ZIP, or repository modification was produced.**
