# Read-only combined review

**overall_verdict: `FAIL`**

This review follows the bounded, P0/P1-only exact-head contract. 

The SPEC, CODE, and QA entries below describe **one underlying P1 defect** viewed from three independent perspectives, not three unrelated implementation defects.

## Repository identity

* **Repository:** `chemitaro/spec-dock`
* **Required and inspected branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Required and inspected HEAD:** `fec2e190cce8cc1823cd65dc83cca167f7c85c73`
* **PR:** `#351`
* **Exact feature branch inspected:** yes
* **Default branch inspected or used as fallback:** no

The GitHub connector reported the required branch at exactly the required HEAD. PR #351 independently identifies the same branch and head SHA.

## 1. SPEC reviewer

**P0 count:** 0
**P1 count:** 1

### `SPEC-P1-001` — S020 evidence incorrectly records foreign-lock cleanup as fail-closed

**Locations**

* `report.md:1082-1089`
* `artifacts/20260802t061000z-pr-351-s020-shared-ref-blue-chatgpt-work-packet.md`, implementation requirements for `_OperationBranchLock` and `_acquire_operation_branch_lock`

The accepted S020 work packet requires partial acquisition cleanup to release **only objects proven to be owned**. It also requires cleanup ambiguity, foreign locks, and replaced locks to fail closed. 

The exact-head Report nevertheless records that foreign, disappeared, and replaced locks now fail closed and treats the focused `264 passed` result as implementation closure.

That claim is false for `_acquire_operation_branch_lock()`. Its exception path removes `HEAD.lock` unconditionally, even when preparation failed before the function opened the lock or established its device/inode identity. The canonical contract permits successful publication only after the required Git identity and parity conditions hold, while the Plan permits final handoff only with zero unresolved blockers.

**Concrete impact**

The Report can support an incorrect exact-head closure or merge-ready disposition while the implementation can remove another Git process’s lock. That is an unauthorized mutation of repository Git metadata and breaks the explicitly recorded fail-closed behavior.

The canonical Requirement, Design, Plan, and Report reviewed here are the exact GitHub blobs at the required HEAD.    

## 2. CODE reviewer

**P0 count:** 0
**P1 count:** 1

### `CODE-P1-001` — Failed guard acquisition unlinks an unowned `HEAD.lock`

**Locations**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py:2537-2627`
* Same projected file:
  `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

`_acquire_operation_branch_lock()` calculates `lock_path` before starting the prepared `update-ref` transaction. Ownership of that path is not established until after both protocol acknowledgements and the successful `os.open()` at lines 2596-2604.

However, every exception reaches this unconditional cleanup:

```python
with suppress(FileNotFoundError):
    lock_path.unlink()
```

This executes even when `descriptor is None` and the path existed before the S020 guard began.

A legitimate concurrent Git operation can therefore produce this sequence:

1. Another Git process owns the operation worktree’s existing `HEAD.lock`.
2. The S020 `update-ref --stdin` transaction cannot prepare.
3. `_read_operation_ref_ack()` raises because `prepare: ok` was not received.
4. The exception cleanup unlinks the pre-existing foreign lock despite never capturing its identity.

The same guard is used by both initial publication and publication resume, so the defect is reachable after local commit installation and during a later `publication_pending` retry.

**Deterministic reviewer reproduction**

Using the exact source bytes and Git 2.47.3:

* created a clean `feature/issue` repository at commit `C`;
* created `.git/HEAD.lock` with sentinel bytes and mode `0600`;
* invoked `_acquire_operation_branch_lock(repo, operation, C)`;
* observed `PlanningApplyRestoreMismatch`;
* observed the sentinel `HEAD.lock` had been deleted;
* confirmed `HEAD` and the branch ref itself remained at `C`.

The unconditional unlink is source-level and does not depend on the result status: the operation reports failure while still modifying another Git operation’s synchronization object. Exact reproduction under the Report’s Git 2.54.0 was not independently run, but once Git rejects preparation because a foreign lock exists, the Python cleanup necessarily executes the same unconditional unlink.

Normal guard teardown has the same ownership-ordering hazard: `_OperationBranchLock.__exit__()` removes the Git-created `HEAD.lock` pathname before sending `abort` to the transaction.

The provider and dogfood files have the same Git blob SHA, so this is not projection drift; both copies contain the defect.  

**Concrete impact**

Deleting a foreign Git lock can disrupt or de-serialize a concurrent checkout, symbolic-HEAD update, or ref transaction. This violates the required fail-closed repository-integrity boundary and meets the task’s P1 criterion for unauthorized repository mutation.

## 3. QA reviewer

**P0 count:** 0
**P1 count:** 1

### `QA-P1-001` — S020 tests do not exercise foreign-lock preservation at the new publication guard

**Test evidence**

The exact-head integration suite contains:

* `test_existing_foreign_head_lock_aborts_install_without_ref_change`
* `test_operation_branch_ref_prepare_mismatch_fails_closed_without_locks`
* the three new linked-worktree shared-ref tests for initial push, resume push, and already-remote publication.

The existing foreign-lock test executes the complete initial apply and asserts that `commit.json` was never created. It therefore stops at the earlier local commit-install transaction; it does **not** reach the S020 publication guard’s `_acquire_operation_branch_lock()` cleanup.

The prepare-mismatch test calls `_acquire_operation_branch_lock()` with a wrong commit but starts with no foreign lock and then merely asserts that lock paths are absent. It cannot distinguish correct cleanup from deletion of an object owned by another Git operation.

The linked-worktree tests correctly demonstrate that a successfully prepared guard blocks another worktree’s `update-ref`, but they cover only the successfully acquired guard. They do not cover partial acquisition with a pre-existing foreign `HEAD.lock`.

Consequently, all recorded S020 tests can pass while the exact implementation still deletes a foreign lock. This is a concrete false-PASS gap, not a request for additional confidence testing. The attached unit and integration evidence reflects the same coverage boundary.  

## Verification summary

Observed directly through the GitHub connector:

* the exact required feature branch and HEAD, without default-branch fallback;
* PR #351 bound to `fec2e190cce8cc1823cd65dc83cca167f7c85c73`;
* the exact canonical Requirement, Design, Plan, and Report;
* the prior S019 shared-ref P1 and the bounded S020 work packet; 
* the complete provider guard implementation and its initial/resume call sites;
* provider/dogfood byte identity;
* the three linked-worktree mutation tests, the prepare-mismatch test, and the earlier foreign-lock install test;
* successful exact-head GitHub Actions runs for both `CI` and `Provider CI`.

Recorded in the exact-head Report:

* Apply unit/application/integration: `264 passed`;
* Ruff check, Ruff format, and mypy: passed;
* provider/dogfood SHA-256 parity: passed.

Those recorded local commands were inspected but not independently re-executed. The exact-source foreign-lock reproduction was independently executed as described above. The successful checks do not close the blocker because none exercises foreign-lock ownership at the S020 publication-guard acquisition boundary.

**No patch, no replacement ZIP, and no repository modification was produced.**
