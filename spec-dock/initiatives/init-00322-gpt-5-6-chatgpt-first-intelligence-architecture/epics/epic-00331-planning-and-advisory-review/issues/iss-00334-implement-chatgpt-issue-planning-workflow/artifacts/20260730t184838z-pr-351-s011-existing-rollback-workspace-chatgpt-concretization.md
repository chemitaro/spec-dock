# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b9a0d-5824-83e8-99e9-5809d0a48a16

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached S011 task brief. Inspect the exact GitHub branch and attached uncommitted source/tests, then concretize only the single confirmed existing-file rollback workspace P1.

## Answer

# S011 — Existing-preimage rollback workspace P1

**Repository gate:** GitHub connector access succeeded for `chemitaro/spec-dock`. The current branch `iss-00334-implement-chatgpt-issue-planning-workflow` resolves to pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`; `main` was not substituted. The provider apply source was inspected at that exact commit before reviewing the attached uncommitted S010 source and tests.

**Disposition: CONFIRMED P1.**

The attached S010 implementation durably tracks the outer publication workspace, but existing-preimage rollback invokes a second `compare_replace()` without its `prepare`/`publish` callbacks. Consequently, the reverse exchange’s workspace is not represented in `mutation-ledger.json`. The existing `current_snapshot == mutation.before` idempotence branch then masks the incomplete inner cleanup.

## 1. Deterministic failure sequence

Let:

* `B` be the original existing preimage.
* `A` be the transaction-published replacement.
* `O` be the durable outer mutation entry.
* `W₂/staged` be the nested rollback workspace and newly staged copy of `B`.

Sequence:

1. Initial publication completes:

   * canonical target contains `A`;
   * outer mutation `O` is durable with `phase="published"`;
   * the original publication workspace has already been removed.

2. Rollback processes `O`. `restore()` proves that the target is still the transaction-owned `A`.

3. Because `O.before.existed` is true, `restore()` calls nested:

   ```python
   compare_replace(
       expected=O.after,       # A
       replacement=O.before,   # B
   )
   ```

   It supplies no ledger callbacks.

4. Nested `compare_replace()` creates private workspace `W₂`, writes and fsyncs a new staged inode containing `B`, and then atomically exchanges:

   ```text
   W₂/staged(B₂) ↔ canonical(A)
   ```

5. Immediately after the exchange:

   ```text
   canonical = B₂
   W₂/staged = A
   ```

   The durable ledger still contains only `O`; it has no name or identity for `W₂`.

6. The process dies before nested `compare_replace()` unlinks `W₂/staged` and removes `W₂`.

7. Retry loads `O`. Since the canonical target now has the exact `B` snapshot, the general idempotence branch returns immediately.

8. Generic cleanup uses `O.workspace_name`, which refers to the already-removed initial publication workspace—not `W₂`.

9. `_restore_transaction()` removes `O` from the durable ledger. Its final Git worktree check finds the untracked `W₂/staged`.

10. Recovery returns `recovery_required/restore_mismatch`. The ledger is now empty, so subsequent retries have no ownership evidence for `W₂`; safely sweeping `.spec-dock-apply-*` names is impossible. The operation remains blocked indefinitely.

## 2. Smallest private implementation correction

### 2.1 Reuse the existing private rollback phase

Do not add a public state, status, reason, or output field. Reuse:

```python
phase="rollback-prepared"
```

for both rollback directions:

* `before.existed is False`: existing quarantine-based absence restoration;
* `before.existed is True`: existing-file reverse-exchange restoration.

No new ledger entry should be added. The existing outer entry remains the sole per-path mutation record.

### 2.2 Bind the nested workspace to the outer entry before exchange

In the existing-preimage branch of `_RepositoryTargetGuard.restore()`, pass a `prepare` callback to the nested `compare_replace()`.

The callback must atomically replace the outer ledger entry with:

```python
rollback = dataclass_replace(
    mutation,
    phase="rollback-prepared",
    workspace_name=reverse.workspace_name,
    workspace_device=reverse.workspace_device,
    workspace_inode=reverse.workspace_inode,
    staged_name=reverse.staged_name,
    staged_device=reverse.staged_device,
    staged_inode=reverse.staged_inode,
)
phase_update(rollback)
```

Field rules:

* Preserve outer `before` and `after` snapshots.
* Preserve outer `after_device` and `after_inode`; they identify transaction-owned `A`.
* Copy only the nested workspace and staged-`B` identity into the outer record.
* Do not replace the outer record with the inner `_TargetMutation`. Its `after` snapshot would be `B`, whereas the current private loader requires the operation replacement `A` as the durable outer `after`.
* Do not introduce a second mutation entry for the same path.

The ledger rewrite must complete before `_exchange_entries_at()` is invoked.

A nested `discard` callback should restore the original outer `mutation` entry only after `compare_replace()` has safely exchanged back, deleted its owned staged file, and removed its workspace.

### 2.3 Resume existing-file rollback from the recorded workspace

Change the phase dispatch so it occurs before the generic already-restored return:

```python
if mutation.phase == "rollback-prepared":
    if mutation.before.existed:
        self._resume_existing_restore(target, mutation)
    else:
        self._resume_absent_restore(target, mutation)
    return
```

Add a private `_resume_existing_restore()` helper. Define:

* `A` = `mutation.after`, identity `after_device/after_inode`;
* `B` = `mutation.before`;
* `B₂` = staged rollback inode, identity `staged_device/staged_inode`.

It must recognize only these states:

| Canonical target                                                      | Recorded workspace slot                   | Action                                                                                           |
| --------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------ |
| exact `A` at the recorded `A` identity                                | exact `B` at the recorded `B₂` identity   | Pre-exchange. Perform the atomic exchange, fsync both directories, then re-verify.               |
| exact `B` at the recorded `B₂` identity                               | exact `A` at the recorded `A` identity    | Post-exchange. Unlink only the proven `A` inside the workspace, fsync, and remove the workspace. |
| exact `B` at the recorded `B₂` identity                               | slot absent and workspace otherwise empty | Post-unlink crash. Remove the empty workspace and fsync the target parent.                       |
| exact `B` at the recorded `B₂` identity                               | recorded workspace absent                 | Cleanup completed. Return idempotent success.                                                    |
| Any other identity, snapshot, missing entry, or extra workspace entry | Any                                       | Preserve every entry and raise `PlanningApplyRestoreMismatch`.                                   |

In particular, `target == before` is not sufficient while a `rollback-prepared` workspace exists. The workspace must first be classified and drained.

### 2.4 Cleanup ordering

For the reverse exchange:

1. Persist the `rollback-prepared` outer entry.
2. Perform the atomic exchange.
3. Fsync the workspace and captured target parent.
4. Verify canonical `B₂/B` and displaced `A`.
5. Unlink only displaced `A` inside the verified private workspace.
6. Fsync the workspace.
7. Verify the workspace is otherwise empty.
8. Remove the workspace and fsync the target parent.
9. Return from `restore()`.
10. Only then may `_restore_transaction()` pop the outer ledger entry and durably rewrite the shortened ledger.

`cleanup_workspace(resolved)` may remain as a defensive no-op after the dedicated helper has removed the rollback workspace.

## 3. Exact Red/Green tests

The attached S010 tests already cover write-ahead forward publication, idempotent restoration, durable ledger shrinking, and absence rollback, but not a crash inside the nested existing-file reverse exchange.

### Unit — durable reverse-exchange intent and recovery

**File:** `tests/unit/infra/test_issue_planning_apply.py`

**Add:**

```python
test_existing_restore_intent_is_durable_before_reverse_exchange
```

Test procedure:

1. Create an existing `target.md` containing `B` with a non-default mode.
2. Publish `A` with `guard.compare_replace()` and retain outer mutation `O`.
3. Persist `O` as the sole in-memory and on-disk mutation-ledger entry.
4. Call `guard.restore(O, phase_update=...)`.
5. Wrap `_exchange_entries_at()` for the rollback call.
6. Before invoking the real syscall, read `mutation-ledger.json` and assert:

   * one entry still exists for `target.md`;
   * `phase == "rollback-prepared"`;
   * its workspace device/inode matches `fstat(source_fd)`;
   * its staged identity matches `stat(staged_name, dir_fd=source_fd)`;
   * outer `after_device/after_inode` still identify canonical `A`;
   * outer before/after digests are unchanged.
7. Invoke the real exchange, then raise a `BaseException` to model process death.
8. Assert the crash state is:

   * canonical target contains exact `B`;
   * recorded workspace contains exact `A`.
9. Call `guard.restore()` with the recorded rollback mutation.
10. Assert:

    * exact `B` bytes and mode;
    * no `.spec-dock-apply-*` workspace remains.

**Red:** current S010 reaches the reverse exchange while the ledger entry is still `published`; no inner workspace identity is durable.

**Green:** the ledger is `rollback-prepared` before the syscall, and the recorded state completes cleanup after the injected crash.

### Unit — ambiguity preserves every byte

**File:** `tests/unit/infra/test_issue_planning_apply.py`

**Add:**

```python
test_existing_restore_resume_workspace_slot_swap_preserves_unknown_and_displaced_after
```

Test procedure:

1. Produce the post-exchange crash state from the preceding setup.
2. Inside the recorded workspace:

   * rename the displaced transaction-owned `A` to a different name;
   * install unknown sentinel bytes at the recorded staged slot.
3. Resume the rollback mutation.
4. Expect `PlanningApplyRestoreMismatch`.
5. Assert:

   * canonical exact `B` remains;
   * unknown sentinel bytes remain;
   * displaced `A` remains;
   * the workspace is retained;
   * no entry was unlinked based only on its filename.

**Red:** no current durable record exists for this inner workspace, so the state cannot be safely classified.

**Green:** the helper detects the slot identity mismatch and preserves all bytes.

### Integration — crash after reverse exchange, before workspace cleanup

**File:** `tests/integration/test_issue_planning_apply.py`

**Add:**

```python
test_recovery_resumes_existing_restore_after_reverse_exchange_before_workspace_cleanup
```

Test procedure:

1. Create the standard repository, bare origin, output directory, operation, document baseline, raw index snapshot, and managed-state snapshot.
2. Make validation return an error so ordinary precommit rollback starts after canonical existing files have been replaced.
3. In `fault_hook("during_restore")`, arm a rollback-only exchange fault.
4. Wrap `_exchange_entries_at()`:

   * allow all forward exchanges unchanged;
   * during rollback, for the first existing canonical target, invoke the real reverse exchange and then raise `ProcessCrash(BaseException)`.
5. After the crash, assert:

   * transaction evidence remains;
   * the affected ledger entry is `rollback-prepared`;
   * its recorded workspace exists;
   * canonical target contains baseline bytes;
   * workspace slot contains the operation replacement.
6. Retry the same operation with validation and sync runners that fail the test if called.
7. Assert:

   * result is `rolled_back/planning_commit_failed`;
   * all three documents equal their exact baseline bytes and modes;
   * decision and newly created companion are absent;
   * raw Git index and managed state equal their snapshots;
   * local and remote HEAD remain the reviewed HEAD;
   * no `.spec-dock-apply-*` directory remains beneath any captured target parent;
   * transaction evidence is removed only after all postconditions pass;
   * durable state is `ROLLED_BACK`.

**Red:** current S010 reloads only the outer mutation, returns on `target == before`, leaves the inner workspace untracked, and ends in `recovery_required/restore_mismatch`.

**Green:** retry classifies the recorded post-exchange state, removes only the proven displaced `A`, drains the ledger, and completes exact rollback.

## 4. Crash-recovery and durable-evidence invariants

1. **One path, one durable mutation entry.** Existing-file rollback updates the outer entry; it does not append a nested entry.

2. **Write-ahead before reverse namespace mutation.** A reverse exchange must never execute unless its workspace and staged identity are represented in the durable outer entry.

3. **Outer semantic evidence remains stable.** `before`, `after`, `after_device`, and `after_inode` continue to describe the original transaction mutation. Only rollback workspace/staged metadata changes.

4. **Phase is state-classified, not step-counted.** `rollback-prepared` may represent pre-exchange, post-exchange, post-unlink, or post-rmdir state; recovery determines which from descriptor-relative identities and exact snapshots.

5. **No snapshot-only early return for a recorded rollback workspace.** Exact `before` bytes do not authorize ledger removal while a workspace may still contain displaced `after`.

6. **No public-name unlink.** Cleanup deletes only an entry inside the verified private workspace after proving both its recorded identity and exact `after` snapshot.

7. **Ambiguity retains evidence.** Wrong inode, wrong bytes, wrong mode, unexpected entry, missing workspace in a non-completed state, or unsupported atomic primitive retains the workspace and ledger and fails closed.

8. **Ledger shrink follows physical cleanup.** The path entry remains durable until the target is exact `before`, the rollback workspace is gone, and both directory durability boundaries have been crossed.

9. **Transaction backup remains authoritative.** Index, managed-state, and file backups are not removed until all target entries are drained and final rollback postconditions pass.

10. **No public contract change.** Statuses, reasons, operation schema, CLI output, Oracle configuration, and application orchestration remain unchanged.

## 5. Allowed files and safe implementation order

### Files allowed to change

Provider authority:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

Mechanical projection only:

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

No Candidate, application, ports, bootstrap, public contract, documentation, Oracle configuration, or unrelated test changes are authorized.

### Safe order

1. Add the two unit Red tests.
2. Add the integration Red test and confirm the current S010 state leaves the inner workspace and cannot complete recovery.
3. In the provider source, wire the nested reverse `compare_replace.prepare` callback to the existing outer ledger entry.
4. Add existing-file dispatch for `rollback-prepared` and implement `_resume_existing_restore()`.
5. Add the safe `discard` transition back to the original outer entry.
6. Run the focused unit and integration tests.
7. Run the complete apply unit and integration suites, including all S010 race, unknown-byte preservation, unsupported-primitive, durable-ledger, and interrupted-transaction tests.
8. Mechanically project the provider source to the dogfood path.
9. Run the existing provider/dogfood byte-parity, lint, and validation gates.

**Verification boundary:** This is a read-only static concretization against exact GitHub HEAD plus the attached authoritative uncommitted S010 source/tests. No patch, repository mutation, or test execution was performed.
