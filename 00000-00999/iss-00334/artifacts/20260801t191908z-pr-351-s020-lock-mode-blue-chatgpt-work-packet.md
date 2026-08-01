# S020 Blue Team lock-mode compatibility work packet

## Repository binding

* **Repository:** `chemitaro/spec-dock`
* **Branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Exact inspected baseline HEAD:** `c5439cdc139462c3c9dfa9730d3d688ee42e76d1`
* **PR:** `#351`
* **Default-branch fallback:** not used

GitHub identifies PR `#351` with the required feature branch and exact HEAD.  The provider and dogfood copies of `issue_planning_apply.py` are byte-identical Git blobs at this HEAD (`95dbf1d8355c7a6733f650772aa7750e36137b2a`).

This packet addresses only the controlling lock-mode P1. 

## One P1 being repaired

`_OperationBranchLock.assert_held()`, `_acquire_operation_branch_lock()`, and `_remove_captured_operation_head_lock()` require both descriptor and pathname modes to equal exactly `0600`. A real Git ref transaction creates the lock using requested mode `0666` filtered by the child process umask. Thus, for a normal non-shared repository:

* umask `0077` produces `0600`;
* umask `0022` produces `0644`;
* umask `0002` would produce `0664`.

The exact source rejects `0644` before assigning `captured_identity`, then takes ambiguous abandonment rather than checked abort and captured-inode cleanup.  The attached Red evidence records the resulting stale per-worktree and shared-ref locks and the corresponding initial, resume, and already-remote publication impact. 

The canonical publication contract remains unchanged: success requires local commit, remote branch HEAD, and commit-tree parity; post-commit publication failure retains the local commit for the same-operation retry.

---

## Repair decision

Replace the fixed `0600` contract with a **capture-and-compare mode contract**:

1. After Git acknowledges `prepare: ok`, validate that the descriptor and pathname identify the same regular file owned by the effective UID.
2. Validate that the observed permission mode is compatible with Git’s `0666` creation request.
3. Capture that actual mode together with device and inode.
4. During every later ownership check and fallback cleanup, require the exact captured mode to remain unchanged.

Do not force the child umask, call `chmod()`/`fchmod()` on Git’s lock, or derive an expected mode by reading the production process umask.

### Explicit metadata predicate

Let:

* `fd_stat = os.fstat(descriptor)`
* `path_stat = lock_path.lstat()`
* `m_fd = stat.S_IMODE(fd_stat.st_mode)`
* `m_path = stat.S_IMODE(path_stat.st_mode)`
* `git_mode(m) := (m & ~0o666) == 0`

Acquisition succeeds only when all of the following hold:

```text
regular(fd_stat)
AND regular(path_stat)
AND fd_stat.st_uid == path_stat.st_uid == os.geteuid()
AND (fd_stat.st_dev, fd_stat.st_ino)
    == (path_stat.st_dev, path_stat.st_ino)
AND m_fd == m_path
AND git_mode(m_fd)
AND ref_process.poll() is None
```

On success, capture:

```text
device = fd_stat.st_dev
inode  = fd_stat.st_ino
mode   = m_fd
```

`git_mode(m)` accepts every mode that Git can obtain by applying a umask to requested mode `0666`, while rejecting execute and special bits that the `0666` request cannot create.

After capture, `assert_held()` and post-abort fallback cleanup require:

```text
same regular-file type
AND same effective owner
AND same captured device/inode
AND exact current mode == captured mode
```

A change from `0644` to `0600`, or from `0600` to `0644`, is rejected even though both are individually Git-compatible. The first observation chooses the accepted mode; no later mode transition is authorized.

### Mode and state matrix

| State or observation                                                 | Result                           | Process handling               | Pathname handling                                       |
| -------------------------------------------------------------------- | -------------------------------- | ------------------------------ | ------------------------------------------------------- |
| Initial mode `0600`, all other metadata valid                        | Accept and capture `0600`        | Keep prepared transaction live | None                                                    |
| Initial mode `0644`, all other metadata valid                        | Accept and capture `0644`        | Keep prepared transaction live | None                                                    |
| Other subset of `0666`, all other metadata valid                     | Accept and capture observed mode | Keep prepared transaction live | None                                                    |
| Execute or special bits present                                      | Reject as unsafe                 | Ambiguous abandonment          | No unlink                                               |
| Descriptor/path modes differ during acquisition                      | Reject as unstable metadata      | Ambiguous abandonment          | No unlink                                               |
| Captured mode remains exact                                          | Continue                         | Transaction remains live       | None                                                    |
| Mode changes after capture, including to another Git-compatible mode | Reject                           | Ambiguous abandonment          | Preserve pathname                                       |
| Wrong owner                                                          | Reject                           | Ambiguous abandonment          | Preserve pathname                                       |
| Non-regular descriptor or pathname                                   | Reject                           | Ambiguous abandonment          | Preserve pathname                                       |
| Path disappears                                                      | Reject                           | Ambiguous abandonment          | No unlink                                               |
| Path is replaced with another inode                                  | Reject                           | Ambiguous abandonment          | Preserve replacement                                    |
| Child exits unexpectedly                                             | Reject                           | Reap/close as applicable       | Preserve pathname                                       |
| Checked `abort` succeeds and pathname is absent                      | Successful teardown              | Child exited zero              | No fallback needed                                      |
| Checked `abort` succeeds and exact captured object/mode remains      | Successful fallback cleanup      | Child exited zero              | Unlink only that captured inode after immediate recheck |
| Checked `abort` fails                                                | `PlanningApplyRestoreMismatch`   | Reap/close as possible         | No unlink                                               |
| Metadata changes between checked abort and fallback cleanup          | `PlanningApplyRestoreMismatch`   | Child already terminated       | Preserve pathname                                       |

---

## Exact source changes

### Provider authority

Modify:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

#### `_OperationBranchLock`

Add a private captured field:

```text
mode: int
```

Keep all existing fields and application-facing behavior unchanged.

Update `assert_held()` to compare descriptor and pathname mode with `self.mode`, rather than `0o600`. It must continue to require:

* regular descriptor and pathname;
* effective-UID ownership;
* captured device/inode identity;
* live prepared ref process.

A narrow helper such as `_git_ref_lock_mode_is_compatible()` and an exact metadata-matching helper may be used to keep the three predicates identical. Do not introduce a generic lock-policy abstraction.

#### `_acquire_operation_branch_lock()`

Make only these bounded changes:

1. Open the existing Git-created pathname with the current no-follow/read-only flags, without the misleading unused `0o600` creation argument. The flags do not include `O_CREAT`.
2. Compute descriptor and pathname `S_IMODE` values.
3. Apply the acquisition predicate above.
4. Store the observed mode in the returned `_OperationBranchLock`.
5. Assign captured device/inode/mode only after the complete predicate succeeds.
6. Leave pre-capture failures on the existing ambiguous-abandonment path.
7. Leave checked abort and captured-inode cleanup behavior unchanged apart from passing the captured mode.

Do not read or alter the production process umask.

#### `_remove_captured_operation_head_lock()`

Add the captured mode to its input and require exact mode equality for both:

* the open descriptor;
* the pathname immediately before fallback unlink.

It may unlink only when regular-file type, owner, device, inode, and captured mode all still match. If Git already removed the pathname after a successful abort, return successfully. Any changed metadata or replacement remains preserved and raises `PlanningApplyRestoreMismatch`.

#### Other `0600` checks

Do not globally replace `0600`. Private operation evidence, transaction workspaces, staged files, and related provider safety checks intentionally remain `0600`/`0700`. Only the Git-created `HEAD.lock` predicates are in scope.

### Publication call sites

No semantic changes are required in:

* `_publish_initial_operation_commit()`
* `_resume_publication()`
* `_push_operation_commit_cas()`
* `_operation_branch_commit_is_proven()`
* `_require_operation_branch_lock()`

Initial publication already holds one guard through push, post-push proof, remote tree parity, publication evidence, `REMOTE_PARITY`, and terminal result construction.  Resume uses the same guard for both retry-push and already-remote parity.  Teardown failure therefore continues to override a result constructed inside the `with` scope.

### Dogfood projection

After provider Green, project the exact provider bytes to:

```text
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

Do not edit the dogfood copy independently.

---

## Test changes

### Unit tests

Modify:

```text
tests/unit/infra/test_issue_planning_apply.py
```

The current fixture always writes and captures mode `0600`, so it cannot expose the compatibility failure.

#### Fixture and existing-test updates

Update `_operation_branch_lock_fixture()` to accept a `mode` argument and construct `_OperationBranchLock` with the actual captured mode. Update every direct `_OperationBranchLock(...)` construction with the new field.

Parameterize the successful teardown and abort-failure tests over at least:

```text
0600
0644
```

Strengthen the replaced-lock test to preserve and compare:

* device;
* inode;
* bytes;
* permission mode;
* UID.

Keep the existing disappeared-lock and abort-before-unlink expectations unchanged.

#### New ordinary-CI real-Git characterization

Add:

```text
test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask
```

Parameterize:

| Child umask | Expected Git `HEAD.lock` mode |
| ----------: | ----------------------------: |
|      `0022` |                        `0644` |
|      `0077` |                        `0600` |

Use a real temporary Git repository and `_acquire_operation_branch_lock()`. Set the Git child’s umask deterministically through a test-only `subprocess.Popen(..., umask=mask)` wrapper installed by `monkeypatch`; do not mutate the parent process with `os.umask()`.

Inside the guard, assert:

* `branch_lock.mode` equals the expected mode;
* descriptor and pathname match captured device/inode/mode;
* the shared branch-ref lock blocks a competing update if the existing helper is reused.

After exit, assert the per-worktree and shared-ref locks are absent.

This test must remain in the ordinary unit suite and must not receive the `full_regression` marker. That makes plain `uv run pytest` sensitive to a future restoration of the fixed-`0600` defect.

#### New metadata-preservation tests

Add:

```text
test_operation_branch_lock_mode_change_is_preserved_without_protocol_abort
```

Capture a `0644` file, change the same inode to `0600`, then exit the guard. Assert:

* `PlanningApplyRestoreMismatch`;
* normal protocol `abort` was not written;
* ambiguous abandonment occurred;
* device/inode, bytes, UID, and the changed mode remain intact;
* no fallback unlink occurred.

Add:

```text
test_operation_branch_lock_mode_change_after_abort_is_preserved_without_fallback_unlink
```

Inject a mode change after checked abort succeeds but before fallback cleanup. Assert the pathname remains and teardown raises, proving `_remove_captured_operation_head_lock()` compares captured mode independently.

Add:

```text
test_operation_branch_lock_wrong_owner_is_preserved_without_protocol_abort
```

Use a controlled stat-result substitution rather than privileged `chown`. Assert no normal abort or unlink and unchanged actual pathname evidence.

Add:

```text
test_operation_branch_lock_non_regular_path_is_preserved_without_protocol_abort
```

Replace the pathname with a directory or symlink after capture. Assert the non-regular replacement, its identity, and any sentinel target/content remain unchanged; normal abort and unlink must not run.

### Integration tests

Modify:

```text
tests/integration/test_issue_planning_apply.py
```

Add `import os` only if required by the test helper. Prefer the child-only `Popen(umask=...)` technique over process-global `os.umask()`.

#### Update successful teardown

Parameterize:

```text
test_operation_branch_lock_successful_teardown_releases_prepared_locks
```

over `0022 → 0644` and `0077 → 0600`.

Inside the guard, assert the captured mode explicitly. After exit, assert:

* `HEAD.lock` absent;
* shared branch-ref lock absent;
* linked-worktree `update-ref` can acquire the ref again.

#### Initial publication Red/Green test

Add:

```text
test_initial_publication_succeeds_with_git_lock_mode_from_umask_0022
```

Run a complete approved initial apply with Git children under umask `0022`.

At `before_push`, record that the live Git-created `HEAD.lock` mode is `0644`.

Assert:

* `ready/adoption_published`;
* local commit equals remote branch HEAD;
* local and remote tree parity;
* `publication.json` exists;
* durable state is `REMOTE_PARITY`;
* no per-worktree or shared-ref lock remains.

Current source is Red because guard acquisition rejects `0644`.

#### Resume requiring push

Add:

```text
test_resume_publication_succeeds_with_git_lock_mode_from_umask_0022
```

1. Run the first attempt under child umask `0077`.
2. Inject one push failure and require `publication_pending/push_failed`.
3. Record local commit, commit count, and commit evidence.
4. Retry the same operation under child umask `0022`.
5. At `before_push`, record mode `0644`.

Assert:

* validation and sync are not rerun;
* no new commit is created;
* the same local commit is pushed;
* result is `ready/adoption_published`;
* publication evidence and `REMOTE_PARITY` exist;
* both lock objects are absent.

#### Already-remote parity

Add:

```text
test_already_remote_publication_succeeds_with_git_lock_mode_from_umask_0022
```

1. Create `publication_pending` under `0077`.
2. Publish the exact existing local operation commit to the test remote.
3. Retry under `0022`.
4. Make `_push_operation_commit_cas()` fail the test if invoked.
5. Wrap `_record_publication()` and record that `HEAD.lock` is live at mode `0644`.

Assert:

* no validation, sync, commit creation, or push is repeated;
* remote observation selects the already-remote path;
* result is `ready/adoption_published`;
* local/remote/tree parity remains exact;
* publication evidence and `REMOTE_PARITY` exist;
* neither lock remains after context exit.

#### Preservation regressions retained

Keep without weakening:

```text
test_operation_branch_lock_foreign_head_lock_prepare_failure_preserves_inode
test_initial_publication_guard_acquire_preserves_foreign_head_lock
test_resume_publication_guard_acquire_preserves_foreign_head_lock
test_existing_foreign_head_lock_aborts_install_without_ref_change
test_operation_branch_ref_prepare_mismatch_fails_closed_without_locks
test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push
test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push
test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready
```

The current integration tests already separate successful captured-lock cleanup, publication-time foreign-lock preservation, and shared-ref linked-worktree exclusion. 

---

## Verification commands

### Exact baseline

```bash
branch=iss-00334-implement-chatgpt-issue-planning-workflow
source_head=c5439cdc139462c3c9dfa9730d3d688ee42e76d1

test "$(git branch --show-current)" = "$branch"
test "$(git rev-parse HEAD)" = "$source_head"
test -z "$(git status --porcelain=v2)"
```

### Red evidence

Add the tests first, then run them against the unchanged implementation:

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask
```

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_apply.py::test_initial_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_resume_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_already_remote_publication_succeeds_with_git_lock_mode_from_umask_0022
```

Record that the `0022` cases reject the legitimate `0644` lock on the exact baseline.

### Green focused lane

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_captures_real_git_created_mode_for_normal_umask \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_teardown_aborts_before_owned_head_lock_fallback_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_abort_failure_does_not_unlink_captured_head_lock \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_replaced_head_lock_is_preserved_without_protocol_abort \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_disappeared_head_lock_is_abandoned_without_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_mode_change_is_preserved_without_protocol_abort \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_mode_change_after_abort_is_preserved_without_fallback_unlink \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_wrong_owner_is_preserved_without_protocol_abort \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_non_regular_path_is_preserved_without_protocol_abort
```

```bash
uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_successful_teardown_releases_prepared_locks \
  tests/integration/test_issue_planning_apply.py::test_initial_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_resume_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_already_remote_publication_succeeds_with_git_lock_mode_from_umask_0022 \
  tests/integration/test_issue_planning_apply.py::test_operation_branch_lock_foreign_head_lock_prepare_failure_preserves_inode \
  tests/integration/test_issue_planning_apply.py::test_initial_publication_guard_acquire_preserves_foreign_head_lock \
  tests/integration/test_issue_planning_apply.py::test_resume_publication_guard_acquire_preserves_foreign_head_lock \
  tests/integration/test_issue_planning_apply.py::test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready
```

### Complete Apply and ordinary lanes

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py

uv run pytest
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

`make lint` must independently show Green for Ruff check, Ruff format check, and mypy.

### Projection parity

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py

shasum -a 256 \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

The printed SHA-256 values must match.

### Diff inventory

```bash
git diff --name-only
git diff --check
git status --porcelain=v2
```

Implementation scope is limited to:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
tests/unit/infra/test_issue_planning_apply.py
tests/integration/test_issue_planning_apply.py
```

---

## Repair acceptance criteria

The lock-mode P1 is closed only when all of these are demonstrated:

1. Real Git acquisition under child umask `0022` captures `0644`; under `0077` it captures `0600`.
2. Neither production code nor tests treat `0600` as the sole valid Git lock mode.
3. The acquired mode is captured and later compared exactly.
4. Execute/special-bit modes are rejected as not derivable from Git’s `0666` request.
5. Any post-capture mode transition is rejected and preserved, even when both old and new modes are individually Git-compatible.
6. Foreign, replaced, disappeared, wrong-owner, non-regular, abort-failure, and metadata-change paths remain fail closed without deleting the current pathname.
7. Successful checked abort releases both the per-worktree and shared-ref locks.
8. Initial, retry-push, and already-remote publication all reach `ready/adoption_published` under umask `0022`, with exact local/remote/tree parity and no stale locks.
9. The three existing linked-worktree publication tests remain Green.
10. Plain `uv run pytest` executes the real-Git normal-umask unit characterization rather than skipping all real lock-mode coverage.
11. Provider and dogfood bytes are identical.
12. The diff remains limited to the four files above.
13. The implementation is committed and pushed on the required feature branch, then reviewed at its new exact HEAD with no unresolved P0/P1 for this blocker, as required by the existing final-review gate.

## Non-goals

* No public status, reason, schema, CLI, or JSON changes.
* No Candidate, canonical document, companion, Review, or Human-decision changes.
* No Oracle configuration or provider-boundary changes.
* No production umask normalization or lock `chmod`.
* No stale-lock reclamation, retry, waiting, fairness, or timeout-policy changes.
* No change to shared-ref guard lifetime, native `reference-transaction` hook delegation, literal-commit push, lease semantics, remote-divergence behavior, or same-operation retry.
* No guessed additional Git lock paths or reftable policy.
* No broad lock/security framework or reopening of same-UID threat scope.
* No S001–S019 redesign or unrelated cleanup.
* No canonical document/report mutation in this bounded worker scope.
* No merge, auto-merge, branch deletion, Issue close, or `issue finish`.

No repository modification, patch, replacement ZIP, or test execution is claimed by this work packet.
