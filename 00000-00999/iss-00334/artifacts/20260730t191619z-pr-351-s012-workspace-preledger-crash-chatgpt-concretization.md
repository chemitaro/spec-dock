# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b9f45-cd28-83ee-8832-f44d66d48722

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

Use the attached S012 task brief. Inspect the exact GitHub branch and attached uncommitted source/tests, then concretize only the single confirmed workspace-before-ledger crash P1.

## Answer

# S012 — Workspace-before-ledger crash P1 work packet

**Repository gate:** GitHub connector access succeeded for `chemitaro/spec-dock`. The current branch `iss-00334-implement-chatgpt-issue-planning-workflow` resolves to exact pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`; `main` was not substituted.  The provider source and the established unit/integration test locations were inspected at that exact revision before applying the attached S011 source and tests as the authoritative uncommitted layer.

## Disposition

**CONFIRMED P1.**

The S011 source closes the write-ahead gap before target exchange, including existing-file reverse exchange, but it still creates and durably publishes the private workspace directory before any durable evidence names that workspace.

In forward mutation, `_create_workspace()` runs before the staged inode is created and before the `prepare()` callback persists the `_TargetMutation`. Existing-file rollback calls the same `compare_replace()` path; its `prepare_reverse()` callback likewise runs only after the reverse workspace and staged preimage already exist.

The supplied tests prove that a complete `prepared` or `rollback-prepared` entry is durable before exchange, and that post-exchange recovery works. They do not cover process death before those callbacks, while the workspace is already present.

---

## 1. Deterministic failure sequences

### 1.1 Forward publication

Let:

* `B` be the target preimage.
* `A` be the intended replacement.
* `W/staged` be the private staging workspace and staged inode.

Sequence:

1. The transaction backup and empty `mutation-ledger.json` are durable; operation state is `MUTATING`.
2. `_apply_guarded_mutation()` enters `compare_replace()`.
3. `_create_workspace()` chooses `W`, performs `mkdirat(..., 0700)`, opens and validates it, fsyncs the captured target parent, and returns.
4. The process may additionally create, write, and fsync `W/staged` containing `A`.
5. The process dies before `prepare(prepared)` completes.
6. Durable evidence still has no mutation entry for this target and no workspace name or inode for `W`.
7. Retry loads only previously completed mutation entries. Nothing authorizes association with `W`.
8. Recovery may restore every recorded target successfully, but final Git worktree verification sees `W` or `W/staged` as untracked.
9. Recovery returns `recovery_required/restore_mismatch`.
10. No later retry may safely sweep the `.spec-dock-apply-*` prefix. Once the recorded mutations are drained, `W` remains unowned indefinitely.

This applies whether the crash leaves an empty workspace or a workspace containing a fully or partially written staged file.

### 1.2 Existing-preimage reverse rollback

Let:

* `O` be the durable outer mutation.
* `B` be its original existing preimage.
* `A` be the transaction-published replacement.
* `W₂/staged` be the new reverse workspace and staged copy of `B`.

Sequence:

1. Forward publication has completed:

   * target contains exact transaction-owned `A`;
   * `O.phase == "published"` is durable;
   * the original forward workspace is already gone.
2. Rollback processes `O`.
3. `restore()` calls nested `compare_replace(expected=A, replacement=B)`.
4. Nested `_create_workspace()` creates and fsyncs `W₂`; it may also create and write `W₂/staged`.
5. The process dies before `prepare_reverse()` updates `O` to `rollback-prepared`.
6. Durable evidence still contains only the old `published` entry `O`; it has no reference to `W₂`.
7. On retry, the target is still `A`, so recovery may perform another reverse replacement using a new workspace `W₃`.
8. The second rollback can restore `B`, remove `W₃`, and pop `O`.
9. Final verification still sees orphaned `W₂`.
10. Recovery returns `recovery_required/restore_mismatch`, now potentially with an empty mutation inventory and no safe ownership evidence for `W₂`.

The S011 reverse-exchange repair starts too late to cover this sequence: it becomes durable only when `prepare_reverse()` runs.

---

## 2. Smallest private durable correction

### 2.1 Extend only the private mutation ledger

Keep the existing per-path mutation entries. Add one singleton, private workspace intent to `transaction/mutation-ledger.json`:

```json
{
  "operation_id": "<operation-id>",
  "workspace_intent": null,
  "entries": []
}
```

When active:

```json
{
  "operation_id": "<operation-id>",
  "workspace_intent": {
    "path": "repository/relative/path",
    "purpose": "forward",
    "workspace_name": ".spec-dock-apply-<32 lowercase hex>",
    "workspace_device": null,
    "workspace_inode": null,
    "staged_name": "staged",
    "staged_device": null,
    "staged_inode": null
  },
  "entries": []
}
```

`purpose` is private and limited to:

```text
forward
rollback-existing
```

Validation rules:

* Only one workspace intent may exist because transaction mutation and rollback are sequential.
* `workspace_device` and `workspace_inode` must be either both `null` or both integers.
* `staged_device` and `staged_inode` must be either both `null` or both integers.
* A staged binding is invalid unless the workspace binding is present.
* The path must be one of the operation’s permitted target paths.
* The workspace name must retain the existing `.spec-dock-apply-[0-9a-f]{32}` form.
* All mutation-ledger rewrites must preserve the current `workspace_intent`; an ordinary entry update must never overwrite it with `null`.

This is a private recovery-schema change only. Do not add an operation state, public status, public reason, output field, or operation-schema field.

### 2.2 Write-ahead lifecycle

Refactor workspace creation so the name is chosen outside the namespace-mutating portion.

Required order for forward publication:

1. Generate workspace name `W`.
2. Atomically persist and fsync the unbound workspace intent for `W`.
3. Only then call `mkdirat(W, 0700)` through the captured parent descriptor.
4. Open with `O_DIRECTORY | O_NOFOLLOW`, verify directory/effective owner/mode, and fsync the target parent.
5. Atomically bind `workspace_device/workspace_inode` in the intent.
6. Only after workspace binding, create `staged` with `O_CREAT | O_EXCL | O_NOFOLLOW`, initially `0600`.
7. Fsync the workspace directory so the staged namespace entry is durable.
8. Fstat the new staged descriptor and atomically bind `staged_device/staged_inode` in the intent.
9. Only after staged binding, apply the final mode, write replacement bytes, and fsync the staged descriptor.
10. Construct the existing complete `_TargetMutation`.
11. Run the existing `prepare()` callback and durably persist its `prepared` entry.
12. Clear `workspace_intent` only after the complete entry is durable.
13. Perform the existing atomic exchange or no-replace rename unchanged.

Binding the staged inode before the first byte write is necessary. It makes a partial staged file recoverable by identity. A crash between `O_EXCL` creation and staged binding can leave only a zero-length `0600` file, which is separately classifiable without deleting bytes.

### 2.3 Existing-file reverse path

Use the same lifecycle with `purpose="rollback-existing"`.

Before the nested reverse workspace is created:

* the outer entry remains the sole path mutation entry;
* it remains `phase="published"`;
* the workspace intent names the pending reverse workspace.

After staging `B`:

1. `prepare_reverse()` replaces the outer entry with `rollback-prepared`, preserving outer `before`, `after`, `after_device`, and `after_inode`.
2. The complete `rollback-prepared` entry and its workspace/staged identities become durable while the workspace intent still exists.
3. Clear the intent.
4. Perform the reverse atomic exchange.

A crash with both a matching workspace intent and matching `rollback-prepared` entry is a completed handoff, not an orphan: recovery clears only the redundant intent and leaves physical cleanup to `_resume_existing_restore()`.

### 2.4 No constructor bypass

The transaction workspace constructor must not remain callable from a transaction path without the reservation/binding recorder. Every transaction-owned invocation of `_create_workspace()` must pass through the same private ownership protocol. Standalone primitive tests may retain an explicit non-journaled mode, but application transaction and recovery paths must not use it.

No global or prefix-based workspace scan is authorized.

---

## 3. Recovery classification

Workspace-intent recovery must run before normal `resolve_prepared()` and target restoration.

### 3.1 Crash before `mkdir`

Durable state:

```text
workspace name recorded
workspace device/inode = null
staged device/inode = null
workspace name absent from captured parent
```

Safe action:

1. Verify there is no complete matching `prepared` or `rollback-prepared` handoff.
2. Clear the intent.
3. Continue ordinary recovery.

No worktree entry is removed.

For reverse rollback, the outer `published` entry remains and ordinary rollback may retry it.

### 3.2 Crash after `mkdir`, before workspace inode binding

Durable state:

```text
workspace name recorded
workspace device/inode = null
name may exist
no child creation was permitted before workspace binding
```

Safe classification:

* If the name is absent, clear the intent.
* If the name exists:

  1. Open it descriptor-relatively with `O_DIRECTORY | O_NOFOLLOW`.
  2. Require a directory owned by the effective user with mode `0700`.
  3. Require it to be empty.
  4. Remove it with `rmdir` through the captured parent descriptor.
  5. Fsync the parent.
  6. Clear the intent.

If it is a symlink, wrong type, wrong owner, wrong mode, or non-empty, retain both the directory and intent and raise `PlanningApplyRestoreMismatch`.

An unbound non-empty directory is ownership-ambiguous and must never be drained.

### 3.3 Crash after workspace inode binding

First open the exact recorded name and require its device/inode to match the intent.

#### Matching complete mutation handoff

When a `prepared` or `rollback-prepared` entry has the same path, workspace identity, staged name, and staged identity:

* clear only the redundant workspace intent;
* do not unlink or remove anything;
* continue existing mutation recovery.

#### No staged inode binding yet

Allowed states are:

* exact bound workspace is empty; or
* its complete inventory is one regular, non-symlink, effective-user-owned `staged` entry that is still zero bytes and mode `0600`.

The second state represents death after `O_EXCL` creation but before staged-inode binding; no byte write was permitted. Unlink that zero-byte entry, fsync the workspace, remove the empty workspace, fsync the target parent, and clear the intent.

A non-zero unbound file or any extra entry is ambiguous. Preserve everything and return `restore_mismatch`.

#### Staged inode is bound

Allowed states are:

* exact bound workspace is already empty, representing interruption during prior intent cleanup; or
* the only entry is `staged`, and its device/inode matches the bound staged identity.

Because the staged inode was durably bound before any write, that exact inode is transaction-owned even if its write is partial. It may be unlinked, followed by workspace fsync, empty-workspace removal, parent fsync, and intent clearing.

Do not unlink anything when:

* the staged slot has a different inode;
* another entry exists;
* the workspace name resolves to another inode;
* the expected workspace is replaced by a symlink or unsafe object.

If the workspace is absent while a staged inode is recorded, clear the intent only after proving that recorded staged inode is not present at the target and there is no unmatched namespace publication. Otherwise retain evidence and fail closed.

### 3.4 Cleanup ordering

For an orphan intent:

1. Classify ledger handoff state.
2. Open and verify the exact captured-parent workspace object.
3. Remove only a zero-byte unbound staged placeholder or the exact bound staged inode.
4. Fsync the workspace.
5. Verify the workspace is empty.
6. Remove the workspace.
7. Fsync the target parent.
8. Clear the workspace intent.
9. Continue ordinary mutation-ledger restoration.

For a completed handoff:

1. Verify the complete mutation entry matches the intent.
2. Clear the intent.
3. Let existing `prepared` or `rollback-prepared` recovery own all physical actions.

---

## 4. Exact Red/Green tests

The S011 tests should remain. They prove the later prepared/exchange boundaries; the following tests add the earlier workspace ownership boundary.

### Unit: intent exists before forward `mkdir`

**File:** `tests/unit/infra/test_issue_planning_apply.py`

**Add:**

```python
test_workspace_ownership_intent_is_durable_before_forward_mkdir
```

Procedure:

1. Create a guarded existing target and private transaction evidence.
2. Initialize the new mutation-ledger shape with `workspace_intent=None`.
3. Call `_apply_guarded_mutation()`.
4. Wrap the workspace `os.mkdir` call.
5. Before invoking the real `mkdir`, read `mutation-ledger.json` and assert:

   * `entries == []`;
   * intent path is the target;
   * `purpose == "forward"`;
   * intent workspace name is exactly the name passed to `mkdir`;
   * both workspace identities are `null`;
   * both staged identities are `null`.
6. Raise `ProcessCrash(BaseException)` before the real `mkdir`.
7. Assert no workspace exists but the intent remains durable.
8. Invoke the private intent resolver.
9. Assert the intent is cleared without any target mutation.

**Red:** S011 reaches `mkdir` with only an empty mutation inventory and no workspace intent.

**Green:** the exact name is durable before the first worktree namespace mutation.

### Unit: reverse intent exists before nested `mkdir`

**Add:**

```python
test_existing_restore_workspace_intent_is_durable_before_reverse_mkdir
```

Procedure:

1. Publish `A` over existing `B` and persist the outer `published` mutation.
2. Call `restore()` with the transaction intent recorder and the existing `phase_update`.
3. Wrap the nested workspace `mkdir`.
4. Before the real call, assert:

   * the outer mutation remains the sole entry;
   * its phase is still `published`;
   * its outer before/after snapshots and `after_device/after_inode` are unchanged;
   * workspace intent has `purpose == "rollback-existing"`;
   * its name matches the pending reverse `mkdir`;
   * all intent identities are still `null`.
5. Raise `ProcessCrash` before `mkdir`.
6. Resolve the intent and retry the outer restore.
7. Assert exact `B` bytes/mode and no workspace.

**Red:** S011 has no durable reference to the pending nested workspace.

**Green:** reverse workspace ownership begins before its namespace creation without replacing the outer semantic mutation.

### Unit: classify all pre-handoff creation boundaries

**Add parameterized test:**

```python
test_workspace_intent_recovery_classifies_creation_boundaries
```

Cases:

```text
before_mkdir
after_mkdir_before_workspace_binding
after_workspace_and_staged_binding
```

For each case construct canonical ledger evidence and filesystem state, run the private resolver, and assert:

* intent becomes `null`;
* target bytes and identity are unchanged;
* exact owned workspace is absent afterward;
* ordinary mutation entries are unchanged.

For `after_workspace_and_staged_binding`, put partial bytes in the exact bound staged inode. Recovery must remove it by the pre-write durable inode binding, not by filename alone.

### Unit: ambiguity retains every byte

**Add:**

```python
test_workspace_intent_recovery_preserves_ambiguous_nonempty_workspace
```

Parameterize at least:

1. Unbound private workspace containing an unknown sentinel file.
2. Bound workspace whose staged slot has a different inode.
3. Bound workspace with the exact staged inode plus an unexpected additional entry.

Expect `PlanningApplyRestoreMismatch`. Assert:

* all sentinel bytes remain;
* the workspace remains;
* the durable intent remains unchanged;
* no known entry is selectively removed while unknown entries are present.

### Integration: forward crash after staging, before complete mutation entry

**File:** `tests/integration/test_issue_planning_apply.py`

**Add:**

```python
test_recovery_cleans_forward_workspace_crash_before_mutation_handoff
```

Procedure:

1. Create the standard repository, origin, operation, document baseline, raw index snapshot, and managed-state snapshot.
2. Intercept the first attempted persistence of a non-empty mutation list whose final entry is `phase="prepared"`.
3. Raise `ProcessCrash` before that entry is written.
4. This places the crash after:

   * workspace name reservation;
   * workspace binding;
   * staged binding;
   * replacement write/fsync;
     but before complete target-mutation handoff.
5. After death, assert:

   * on-disk `entries` has no entry for the selected forward target;
   * `workspace_intent` contains matching workspace and staged identities;
   * the workspace contains the exact recorded staged inode;
   * the target remains at its preimage.
6. Retry with validation and sync runners that fail the test if called.
7. Assert:

   * result is `rolled_back/planning_commit_failed`;
   * documents, decision absence, companion absence, index, managed state, local HEAD, and remote HEAD equal baseline;
   * no `.spec-dock-apply-*` directory remains;
   * transaction evidence is removed only after final postconditions;
   * durable operation state is `ROLLED_BACK`.

**Red:** S011 leaves the non-empty workspace unrecorded, and retry ends in `recovery_required/restore_mismatch`.

**Green:** the bound staged inode is drained before normal rollback and recovery completes.

### Integration: reverse crash before `rollback-prepared` handoff

**Add:**

```python
test_recovery_cleans_existing_rollback_workspace_crash_before_reverse_handoff
```

Procedure:

1. Start the standard successful forward replacements.
2. Force a precommit failure after staging so rollback begins.
3. Intercept the first attempted persistence where the last mutation is being changed from `published` to `rollback-prepared`.
4. Raise `ProcessCrash` before that ledger rewrite.
5. After death, assert:

   * the durable outer entry is still `published`;
   * target contains transaction-owned `A`;
   * workspace intent has `purpose="rollback-existing"`;
   * its bound workspace contains the exact recorded staged preimage inode;
   * no reverse exchange occurred.
6. Retry with validation and sync forbidden.
7. Assert:

   * result is `rolled_back/planning_commit_failed`;
   * all documents equal exact baseline bytes and modes;
   * decision and newly created companion are absent;
   * raw index and managed-state snapshots match;
   * local and remote HEAD remain the reviewed HEAD;
   * no workspace remains under any captured target parent;
   * transaction evidence is removed;
   * durable state is `ROLLED_BACK`.

**Red:** S011 can complete a second reverse rollback but leaves the first unrecorded workspace, causing final `restore_mismatch`.

**Green:** retry first drains the recorded pre-handoff workspace, then resumes the outer mutation normally.

---

## 5. Files allowed to change

### Provider authority

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

### Mechanical projection only

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

No application, Candidate, ports, bootstrap, public contract, operation schema, status/reason, documentation, Oracle configuration, or unrelated test changes are authorized.

---

## 6. Safe implementation order

1. Add the two ordering Red tests and the boundary-classification/ambiguity unit tests.
2. Add both integration Red tests and confirm the current S011 state leaves an unowned workspace and cannot complete recovery.
3. Extend only the private mutation-ledger shape with singleton `workspace_intent`, strict canonical validation, and `None` initialization.
4. Add private reserve, workspace-bind, staged-bind, and clear operations. Ensure ordinary entry persistence preserves the active intent.
5. Refactor workspace creation to accept a pre-reserved name and persist the workspace binding after parent fsync but before child creation.
6. Reorder staged setup to bind its inode before mode change or byte writes.
7. Wire the recorder through forward `_apply_guarded_mutation()`.
8. Wire the same recorder through existing-preimage reverse rollback; retain the S011 `rollback-prepared` outer-entry semantics.
9. Resolve active workspace intent before ordinary mutation recovery, including completed-handoff reconciliation and ambiguity retention.
10. Run the focused new unit and integration tests.
11. Run the complete apply unit and integration suites, especially all S010/S011 exchange, unknown-byte preservation, shortened-ledger, and interrupted-recovery tests.
12. Mechanically project the provider source to the dogfood path.
13. Run provider/dogfood byte parity, lint, validation, and `git diff --check`.

**Verification boundary:** This is a read-only static concretization against exact pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2` plus the attached authoritative uncommitted S011 source/tests. No patch, test execution, file creation, commit, or repository mutation was performed.
