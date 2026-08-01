# S020 Blue Team bounded repair work packet

## Repository binding

GitHub inspection succeeded for `chemitaro/spec-dock`. PR `#351` identifies head branch `iss-00334-implement-chatgpt-issue-planning-workflow` at exactly `92e1c8d843c1e1a8f04916dfd694c6cb86967c5b`; the default branch was not used.

That HEAD records the formal S020 combined-review failure without changing the affected implementation.  The provider and dogfood copies of `issue_planning_apply.py` are still the same Git blob, `086a07a38ebf644c56610240fc1dda47b2d14516`.

The bounded repair is therefore the single accepted P1 from the controlling Blue prompt and Red artifact: failed publication-guard acquisition must never remove a pre-existing foreign `HEAD.lock`.  

## Repair decision

Keep the accepted S020 composite guard unchanged:

* Git’s prepared `update-ref --stdin` transaction owns the shared `refs/heads/<operation.branch>` lock.
* The Git-created per-worktree `HEAD.lock` binds the symbolic `HEAD`.
* Both remain held through branch proof, push, remote commit/tree parity, `_record_publication()`, `REMOTE_PARITY`, and terminal result construction.

Repair only the ownership and teardown state machine.

The current exception path performs `lock_path.unlink()` whether or not `descriptor`, device, and inode were ever captured.  Normal teardown also removes `HEAD.lock` before sending the transaction’s `abort`.  Both orderings must be replaced.

## 1. Exact provider-side changes

### Authoritative file

Modify only the provider authority:

`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

The dogfood file is projected mechanically after Green:

`spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

### `_OperationBranchLock`

Keep its existing binding to:

* `path`
* `descriptor`
* captured `device` and `inode`
* `destination`
* `expected_commit`
* `ref_process`
* `hook_root`

Do not change its public or application-facing contract.

Strengthen `assert_held()` so that it proves all of the following before normal teardown or any publication-sensitive operation:

1. `os.fstat(descriptor)` still identifies the originally captured regular file.
2. `path.lstat()` exists and has the same device/inode as the descriptor.
3. The pathname is still a regular file with the accepted owner/mode.
4. `ref_process.poll()` is still `None`.

A missing or different pathname remains `PlanningApplyRestoreMismatch`; it must not be treated as permission to remove whatever currently occupies `HEAD.lock`.

### Split protocol abort from ambiguous abandonment

Replace the overloaded `_stop_operation_ref_transaction()` behavior with two private paths, or equivalent clearly separated logic:

#### `_abort_operation_ref_transaction(process)`

Use only after the guard has proved that the captured `HEAD.lock` is still the exact pathname object owned by this prepared transaction.

It must:

1. require a live process and writable stdin;
2. write and flush `abort\n`;
3. close stdin;
4. wait with the existing bounded timeout;
5. require exit status zero;
6. raise `PlanningApplyRestoreMismatch` for missing stdin, write failure, timeout, nonzero exit, or wait failure.

It must not unlink `HEAD.lock`.

#### `_abandon_operation_ref_transaction(process)`

Use when ownership or protocol state is ambiguous:

* no captured inode;
* malformed or missing acknowledgement;
* unexpected child exit;
* `HEAD.lock` disappeared;
* `HEAD.lock` was replaced;
* ownership capture failed after preparation.

It must terminate and reap a still-running child without sending the normal protocol `abort`, then close streams. It must not inspect or unlink `HEAD.lock`.

This path may leave a guard-owned shared-ref lock stale. That is intentional fail-closed behavior under the existing `recovery_required/restore_mismatch` contract; stale-lock reclamation is not part of this repair.

### Post-abort `HEAD.lock` handling

Add a narrow helper such as:

`_remove_captured_operation_head_lock_after_abort(...)`

It may run only after:

* the exact device/inode was captured;
* a final pre-abort ownership check passed;
* `abort` completed successfully with exit status zero.

Its closed behavior is:

| Post-abort pathname state                | Required action                                      |
| ---------------------------------------- | ---------------------------------------------------- |
| `HEAD.lock` absent                       | Success; Git completed cleanup                       |
| Same captured device/inode still present | Unlink that exact captured inode as fallback cleanup |
| Different device/inode present           | Preserve it and raise `PlanningApplyRestoreMismatch` |
| Metadata cannot be proven                | Preserve it and raise `PlanningApplyRestoreMismatch` |

Immediately before fallback `unlink()`, recheck the open descriptor and pathname identity. Do not use a bare `suppress(FileNotFoundError)` unlink.

### `_OperationBranchLock.__exit__`

Use this exact ordering:

1. Call `assert_held()` before mutation.
2. If ownership is missing or replaced:

   * do not send normal `abort`;
   * abandon/reap the child;
   * do not unlink the pathname;
   * raise `PlanningApplyRestoreMismatch`.
3. If ownership is proven:

   * send checked `abort`;
   * wait for successful zero exit;
   * only then perform post-abort handling of the captured inode.
4. If abort fails:

   * do not unlink the captured or current pathname;
   * close local descriptors/streams;
   * raise `PlanningApplyRestoreMismatch`.
5. Remove the private empty `hook_root` only after the child has terminated.
6. Preserve cleanup failure over the value that the `with` body was about to return, so `ready/adoption_published` never escapes an ambiguous teardown.

This preserves the Git protocol lifecycle: a proven, healthy transaction is aborted before any Python fallback removes its Git-created `HEAD.lock`.

### `_acquire_operation_branch_lock`

Keep the fixed argv, private empty `core.hooksPath`, `start`, `verify`, and `prepare` protocol unchanged.

Introduce explicit local acquisition state:

* `prepared_acknowledged = False`
* `descriptor: int | None = None`
* `captured_identity: tuple[int, int] | None = None`

Set `prepared_acknowledged` only after exact `prepare: ok` and a still-live child.

Set `captured_identity` only after all of these succeed:

1. `os.open(lock_path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC)`;
2. `os.fstat(descriptor)`;
3. regular-file, effective-UID, and `0600` checks;
4. `lock_path.lstat()` matching the opened descriptor’s device/inode;
5. child still alive;
6. existing descriptor synchronization.

The exception path must then follow this matrix:

| Acquisition state                                                                  | Child cleanup                                         | `HEAD.lock` mutation                                          |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------- |
| No captured identity; child already exited, including foreign-lock prepare failure | Reap and close                                        | None                                                          |
| No captured identity; child still alive                                            | Ambiguous abandonment                                 | None                                                          |
| Captured identity still matches and child is live                                  | Checked abort, then post-abort captured-inode cleanup | Only the same captured inode, and only after successful abort |
| Captured identity disappeared/replaced                                             | Ambiguous abandonment                                 | None                                                          |
| Checked abort fails                                                                | Close/reap as possible and raise cleanup failure      | None                                                          |

Delete the current unconditional block completely:

```python
with suppress(FileNotFoundError):
    lock_path.unlink()
```

### Publication call sites

No semantic change is required in:

* `_require_operation_branch_lock`
* `_operation_branch_commit_is_proven_locked`
* `_operation_branch_commit_is_proven`
* `_push_operation_commit_cas`
* `_publish_initial_operation_commit`
* `_resume_publication`
* `_install_operation_commit_cas`

The current initial path already holds one guard through push, remote parity, publication evidence, `REMOTE_PARITY`, and result construction.  The resume path does the same for both retry-push and already-remote cases.

Only adapt these functions if private helper signatures change. Do not shorten their guard lifetime.

### Dogfood projection

After provider tests pass, replace the dogfood copy with the exact provider bytes. Do not edit it independently.

```bash
cp \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

## 2. Exact Red/Green tests

### Unit tests — `tests/unit/infra/test_issue_planning_apply.py`

#### `test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink`

Use a fake prepared process and a real temporary `HEAD.lock` representing the captured inode.

The fake process must leave the pathname present after returning zero from `wait()`, forcing Python’s fallback cleanup.

Record events and assert exact order:

1. `abort` written;
2. stdin flushed/closed;
3. process waited and returned zero;
4. captured-inode identity rechecked;
5. only then `unlink`.

Current source is Red because unlink occurs before `_stop_operation_ref_transaction()`.

#### `test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock`

Use an exact captured inode and inject:

* nonzero abort exit;
* `OSError` while writing or waiting;
* timeout.

For each case assert:

* `PlanningApplyRestoreMismatch`;
* pathname still exists;
* device/inode, bytes, mode, and owner are unchanged;
* fallback unlink was not called.

Current source is Red because it removes the pathname before discovering abort failure.

#### `test_operation_branch_lock_replaced_head_lock_is_preserved_without_protocol_abort`

Capture inode A, move it aside, then create foreign inode B at the original pathname.

Assert:

* `assert_held()` or teardown raises;
* normal `abort` was not written;
* the child follows the ambiguous-abandonment path;
* inode B and its sentinel bytes remain unchanged;
* no pathname unlink occurs.

#### `test_operation_branch_lock_disappeared_head_lock_is_abandoned_without_unlink`

Remove the captured pathname before teardown.

Assert failure, no normal abort, and no unlink attempt. This preserves the existing disappeared-lock fail-closed classification.

#### Existing unit regressions

Keep Green:

* `test_operation_branch_commit_proof_rejects_unbound_lock_object`
* bound branch/commit proof tests;
* exact push lease/refspec tests;
* prohibited general `update-ref` tests.

### Integration tests — `tests/integration/test_issue_planning_apply.py`

#### Primary Red reproduction

`test_operation_branch_lock_foreign_head_lock_prepare_failure_preserves_inode`

Use a real temporary repository:

1. establish `feature/issue` at commit `C`;
2. resolve the worktree-private `HEAD` path with Git;
3. create `HEAD.lock` with sentinel bytes and mode `0600`;
4. capture its device/inode, bytes, mode, UID, and size;
5. call `_acquire_operation_branch_lock(repo, operation, C)`;
6. require `PlanningApplyRestoreMismatch`.

Green assertions:

* the sentinel pathname still exists;
* all captured metadata and bytes are unchanged;
* `HEAD == refs/heads/feature/issue == C`;
* no shared branch-ref lock leaked from the failed preparation.

The test harness may remove its own sentinel only in `finally`, after all preservation assertions. On current exact source this test is Red because the sentinel is deleted.

#### Successful captured-inode cleanup

`test_operation_branch_lock_successful_teardown_releases_prepared_locks`

Use a real repository and linked worktree.

Inside the guard:

* `HEAD.lock` exists and matches `guard.device/guard.inode`;
* the prepared shared-ref lock exists operationally;
* the linked worktree’s `git update-ref refs/heads/feature/issue D C` returns nonzero.

After normal context exit:

* the original captured `HEAD.lock` no longer exists;
* no branch-ref lock remains;
* the same linked-worktree update can acquire the ref after teardown.

This proves that the reorder preserves successful cleanup and does not permanently retain the S020 guard.

#### Initial-publication reachability

`test_initial_publication_guard_acquire_preserves_foreign_head_lock`

Create the foreign sentinel only after `_install_operation_commit_cas()` and `commit.json` creation, immediately before `_publish_initial_operation_commit()` acquires the S020 publication guard.

Assert:

* `recovery_required/restore_mismatch`;
* local operation commit retained;
* remote remains at the prior expected head;
* `commit.json` exists;
* `publication.json` is absent;
* no `REMOTE_PARITY` or `ready`;
* foreign inode, bytes, and mode unchanged.

This must not reuse the earlier install-boundary test.

#### Resume-publication reachability

`test_resume_publication_guard_acquire_preserves_foreign_head_lock`

1. First run: inject one push failure and obtain `publication_pending/push_failed`.
2. Record local commit and commit count.
3. Create the foreign `HEAD.lock`.
4. Retry the same operation.

Assert:

* `recovery_required/restore_mismatch`;
* validation, sync, and commit creation are not rerun;
* local commit and commit count are unchanged;
* remote remains at the expected pre-publication head;
* `publication.json` remains absent;
* foreign inode and bytes are unchanged.

### Existing S020 linked-worktree tests

Retain without weakening:

* `test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push`
* `test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push`
* `test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready`

These remain the proof that the shared branch ref is protected throughout all three publication paths.

Also retain:

* `test_operation_branch_ref_prepare_mismatch_fails_closed_without_locks`
* `test_existing_foreign_head_lock_aborts_install_without_ref_change`
* native `reference-transaction` hook delegation tests.

The earlier foreign-lock test stops at local commit installation and is complementary; it does not replace the new publication-guard test. The exact-head Report records that coverage distinction.

## 3. Initial, resume, and already-remote preservation

The repair must leave these path contracts unchanged:

### Initial publication

One guard spans:

`proof → push → post-push proof → remote commit/tree parity → final proof → publication.json → REMOTE_PARITY → terminal result`

A foreign guard-acquisition failure occurs after the local commit exists, so the operation returns `recovery_required/restore_mismatch` with the local commit retained and without publishing.

### Resume requiring push

One guard spans:

`resume proof → remote observation → literal-commit CAS push → remote parity → final proof → publication.json → REMOTE_PARITY → ready`

A foreign acquisition failure does not retry validation, sync, or commit creation.

### Already-remote parity

One guard spans:

`resume proof → observe remote == local_commit → remote tree parity → final proof → publication.json → REMOTE_PARITY → ready`

The teardown reorder must happen only after the terminal result has been constructed inside the guarded scope. Any teardown ambiguity overrides that result, so no `ready` escapes.

## 4. Commands and acceptance evidence

### Pre-change binding

```bash
branch=iss-00334-implement-chatgpt-issue-planning-workflow
source_head=92e1c8d843c1e1a8f04916dfd694c6cb86967c5b

test "$(git branch --show-current)" = "$branch"
test "$(git rev-parse HEAD)" = "$source_head"
test -z "$(git status --porcelain=v2)"
```

### Red evidence

Run the narrow failing reproductions against the exact source before implementation:

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_foreign_head_lock_prepare_failure_preserves_inode \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock
```

Record that the first test loses the sentinel and that the two teardown tests observe pre-abort removal on the current source.

### Green focused lane

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_replaced_head_lock_is_preserved_without_protocol_abort \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_disappeared_head_lock_is_abandoned_without_unlink \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_foreign_head_lock_prepare_failure_preserves_inode \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_successful_teardown_releases_prepared_locks \
  tests/integration/test_issue_planning_apply.py::test_initial_publication_guard_acquire_preserves_foreign_head_lock \
  tests/integration/test_issue_planning_apply.py::test_resume_publication_guard_acquire_preserves_foreign_head_lock \
  tests/integration/test_issue_planning_apply.py::test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready
```

### Complete Apply lane

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

### Ordinary regression, lint, type, and validation

```bash
uv run pytest
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

`make lint` must separately report Green for Ruff check, Ruff format check, and mypy rather than only a successful aggregate exit.

### Projection identity

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py

shasum -a 256 \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

The two printed SHA-256 values must be identical.

### Diff inventory

```bash
git diff --name-only
git diff --check
git status --porcelain=v2
```

The implementation diff should be restricted to:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
tests/unit/infra/test_issue_planning_apply.py
tests/integration/test_issue_planning_apply.py
```

Main-owned evidence integration, when performed by the surrounding workflow, is separate from this worker implementation scope.

## 5. Non-goals

* No public status, reason, schema, CLI, or JSON change.
* No Candidate, canonical document, companion, Review, or Human-decision change.
* No Oracle configuration or provider-boundary change.
* No redesign of `_install_operation_commit_cas()`, its CAS, or native hook delegation.
* No change to literal-commit push, lease semantics, remote divergence handling, force-push prohibition, or same-operation retry.
* No guessed `refs/heads/*.lock`, `packed-refs.lock`, or reftable lock paths.
* No retry, waiting, fairness, timeout policy, stale-lock reclamation, or automatic foreign-lock deletion.
* No broad subprocess or transaction abstraction.
* No reopening of S014/S015 same-UID threat scope.
* No P2/P3 hardening or S001–S019 redesign.
* No merge, auto-merge, branch deletion, Issue close, or `issue finish`.

## Repair-complete condition

Declare this P1 repaired only when all of the following are true:

1. A pre-existing foreign `HEAD.lock` survives direct S020 guard acquisition failure with identical inode, bytes, mode, and owner.
2. The same preservation is demonstrated from both initial and resume publication paths.
3. No source path can call `unlink()` without a previously captured device/inode and an immediate identity recheck.
4. Normal teardown sends and verifies `abort` before any Python fallback unlink.
5. Missing, replaced, protocol-failure, child-exit, and abort-failure paths return fail closed without deleting the current foreign or ambiguous pathname.
6. Successful teardown releases both the per-worktree and shared-ref guards.
7. All three existing linked-worktree publication tests remain Green.
8. Apply-focused, ordinary, lint/type, validate, byte-identity, and diff checks all pass.
9. The implementation is committed and pushed on the required feature branch, followed by a fresh exact-HEAD combined review with zero unresolved P0/P1 findings for this blocker.

No implementation or test execution is claimed in this packet; these are the required Codex implementation and verification steps.
