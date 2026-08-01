# Read-only combined review

**overall_verdict: `FAIL`**

This review follows the authoritative exact-head, P0/P1-only contract. 

The SPEC, CODE, and QA findings below describe **one underlying P1 defect from three independent perspectives**: the repaired guard requires a Git-created `HEAD.lock` to have mode exactly `0600`, although Git normally creates ref lock files with mode `0666` filtered through the process umask. Consequently, an ordinary non-shared repository under umask `0022` produces mode `0644`, which the implementation rejects.

## Repository identity

* **Repository:** `chemitaro/spec-dock`
* **Required and inspected branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Required and inspected HEAD:** `4abb7f8296d4dab69cd393a107ff49bd7fc77370`
* **PR:** `#351`
* **Exact feature branch inspected:** yes
* **Default branch used as source or fallback:** no

The GitHub connector confirmed PR #351’s head branch and head SHA exactly match the required feature branch and HEAD.

## 1. SPEC reviewer

**P0 count:** 0
**P1 count:** 1

### `SPEC-P1-001` — S020 closure evidence records a lock-mode contract that rejects ordinary Git-owned locks

**Locations**

* `report.md`, section `2026-08-02 — S020 foreign-lock cleanup implementation`
* `requirement.md`, `REQ-010 Validation and Publication`
* `design.md`, §8.3 failure semantics

The exact-head Report records that `_OperationBranchLock` now proves regular-file, owner, mode, device, and inode identity, that successful teardown releases the captured lock, and that the repaired Apply lane passed `272` tests. It then treats only a fresh exact-head review as the remaining closure gate.

That recorded closure is not valid across an ordinary supported Git environment. The exact implementation accepts the Git-created `HEAD.lock` only when its permission bits equal `0600`. Git v2.54.0’s files backend, however, acquires ref locks through `hold_lock_file_for_update_timeout()`, whose default mode is `0666`; `create_tempfile_mode()` passes that mode to `open(O_CREAT | O_EXCL, ...)`, and a non-shared repository does not subsequently alter it. A standard umask of `0022` therefore yields `0644`, not `0600`.

The canonical contract requires an approved operation to complete validation, commit, push, and local/remote/tree parity before publication is successful.  The accepted failure semantics preserve a post-commit operation for safe publication handling; they do not authorize ordinary valid Git lock metadata to make every publication attempt unrecoverable.

**Concrete impact**

On a normal non-shared repository under umask `0022`, an approved apply can install its local commit and then fail at publication-guard acquisition with `recovery_required/restore_mismatch`. The Report’s current S020 closure evidence can therefore support a false merge-readiness conclusion even though the publication contract is not operational under a common Git execution environment. The Plan explicitly prohibits merge-ready handoff while a P0/P1 blocker remains.

## 2. CODE reviewer

**P0 count:** 0
**P1 count:** 1

### `CODE-P1-001` — Exact `0600` validation abandons Git’s valid prepared transaction and leaves both lock objects stale

**Locations**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py:162-223`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py:223-330`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py:2655-2735`
* Same projected file under `spec-dock/scripts/spec_dock_runtime/infra/`
* Initial publication: `_publish_initial_operation_commit()`
* Resume and already-remote publication: `_resume_publication()`

Both `assert_held()` and the acquisition path require:

```python
stat.S_IMODE(...st_mode) == 0o600
```

for the descriptor and pathname.  The acquisition function performs that exact-mode check **before** assigning `captured_identity`.

For a Git-created mode of `0644`, the resulting sequence is:

1. `git update-ref --stdin` successfully acknowledges `start` and `prepare`.
2. Git holds the shared operation-branch ref lock and creates the per-worktree `HEAD.lock`.
3. Python opens that legitimate lock successfully.
4. The exact `0600` check rejects it as unsafe.
5. Because `captured_identity` has not yet been assigned, the exception path selects ambiguous abandonment rather than checked abort.
6. `_abandon_operation_ref_transaction()` kills the Git process and deliberately performs no pathname cleanup.

I reproduced that sequence with the exact provider source bytes, a clean non-shared repository, explicit umask `0022`, and Git 2.47.3. The call raised `PlanningApplyRestoreMismatch` with `operation branch HEAD lock is unsafe`; afterward:

* `.git/HEAD.lock` still existed;
* `.git/refs/heads/feature/issue.lock` still existed;
* `HEAD` and the branch ref remained at the expected commit.

The upstream Git v2.54.0 source follows the same `0666`-plus-umask creation path, so the mode mismatch is not dependent on the reproduced Git 2.47.3 implementation.

The defect reaches every publication variant. Initial publication acquires the guard before proof and push, while resume publication acquires the same guard before either retry-push or already-remote parity processing.   In the resume route, a guard failure is converted to `recovery_required/restore_mismatch`; no `ready` result escapes, but the repository can remain obstructed by stale locks.

The provider and dogfood copies contain the same implementation, so this is not projection drift.

**Concrete impact**

A common ambient umask causes valid publication to fail after the local operation commit has already been installed. The failure can also leave both the per-worktree `HEAD.lock` and shared branch-ref lock in place, obstructing subsequent Git operations and requiring manual recovery. This is a concrete availability and repository-integrity failure in the required publication path.

## 3. QA reviewer

**P0 count:** 0
**P1 count:** 1

### `QA-P1-001` — The lock tests and required CI permit a false PASS because lock mode is controlled by the ambient umask

**Test evidence**

The unit lock fixture manually creates `HEAD.lock` and explicitly changes it to `0600`. The abort-before-unlink, abort-failure, replaced-lock, and disappeared-lock tests therefore cannot detect rejection of Git’s ordinary `0644` lock.

The integration repository fixture initializes a real repository but neither fixes nor records the process umask.  Its successful-teardown test uses real Git and thus has an environment-dependent result:

* under umask `0077`, Git’s `0666` request becomes `0600`, so the test can pass;
* under umask `0022`, it becomes `0644`, so guard acquisition fails and leaves prepared locks.

The integration suite is automatically classified as `full_regression` and skipped unless pytest receives `--run-full-regression`.  Required Provider CI invokes only plain `uv run pytest`, so the green CI job does not exercise the real successful publication-guard acquisition path.

The Report’s locally recorded `272 passed` Apply lane does not record or normalize the umask. Therefore it demonstrates success only under that particular execution environment and cannot establish the claimed portable guard behavior.

**Concrete impact**

All required GitHub checks can be green while the shipped guard fails in a standard umask `0022` environment. The tests therefore allow a false PASS for the exact publication behavior that S020 claims to close. This is a direct contract-breaking coverage gap, not a request for an additional confidence test.

## Verification summary

Observed through the GitHub connector on **2026-08-02**:

* the exact required feature branch and HEAD, without default-branch fallback;
* PR #351 bound to that branch and SHA;
* the exact canonical Requirement, Design, Plan, and Report;
* the provider implementation, dogfood projection, initial/resume/already-remote call sites, and exact lock tests;
* the repaired foreign/replaced/disappeared-lock ownership behavior;
* the recorded focused, complete Apply, ordinary pytest, lint/type, validate, projection-parity, and diff-check evidence;
* the required Provider CI command and the repository’s full-regression skip policy;
* upstream Git v2.54.0 lock creation and permission-handling source.

The reported local test, lint, type, and validation commands were inspected but not independently re-executed in full. I independently executed the focused exact-source reproduction under Git 2.47.3 and umask `0022`. Exact runtime reproduction under Git 2.54.0 was not separately executed; the immutable v2.54.0 source confirms the same `0666` mode request, umask application, and non-shared-repository permission path.

**No patch, no replacement ZIP, and no repository modification was produced.**
