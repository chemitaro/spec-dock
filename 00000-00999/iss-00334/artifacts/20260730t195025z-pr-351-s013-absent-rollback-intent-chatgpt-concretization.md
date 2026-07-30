# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6ba7ab-8cc4-83e8-a6ce-cf31aa44f937

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

Use the attached S013 task brief. Inspect the exact GitHub branch and attached uncommitted source/tests, then concretize only the absent-preimage rollback workspace-intent P1.

## Answer

# S013 — Absent-preimage rollback workspace-intent P1 work packet

## Repository gate

GitHub connector access succeeded for `chemitaro/spec-dock`. The current branch `iss-00334-implement-chatgpt-issue-planning-workflow` was opened directly and resolves to exact pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`; `main` was not substituted.

The attached S013 brief defines the bounded finding, and the attached provider source and two test files were treated as the authoritative uncommitted S012 layer over that pushed HEAD.

## Disposition

**CONFIRMED P1, with one symptom-level correction.**

The S012 source wires `workspace_intent_update` through existing-preimage rollback, but the `mutation.before.existed == False` branch still calls `_create_workspace()` directly. Only after that durable namespace mutation does it construct `rollback-prepared` and call `phase_update()`. No S012 intent identifies that workspace during the gap.

The exact process-death window leaves an **empty** workspace: the transaction-owned target is not moved into `quarantine` until the later `_resume_absent_restore()` call. Therefore, immediate `recovery_required/restore_mismatch` is not guaranteed—Git normally does not report empty directories, so retry can complete while silently leaking the first workspace. If that orphan becomes non-empty, recovery cannot safely attribute or remove its contents and must retain them under `recovery_required/restore_mismatch`. The durable-ownership defect is therefore confirmed; its failure modes are both silent permanent leakage and, once non-empty, permanent fail-closed recovery.

---

## 1. Deterministic failure sequence

Let:

* `O` be the durable outer mutation.
* `O.before.existed == False`.
* `A` be the exact transaction-published target represented by `O.after`, `O.after_device`, and `O.after_inode`.
* `W₁` be the first absent-rollback workspace.
* `W₂` be a later retry workspace.

Sequence:

1. Forward publication is complete:

   * the canonical target contains exact transaction-owned `A`;
   * `O.phase == "published"` is durable;
   * the forward workspace has already been removed.
2. Rollback processes `O`.
3. `restore()` verifies the canonical target still has `A`’s exact snapshot and inode.
4. The absent-preimage branch generates a new name and calls `_create_workspace()`.
5. `_create_workspace()` performs `mkdirat(W₁, 0700)`, opens and validates it, fsyncs the captured parent, and returns.
6. The process dies before `phase_update(rollback)` durably replaces `O` with `phase="rollback-prepared"`.
7. Durable evidence still contains:

   * `O.phase == "published"`;
   * `workspace_intent == null`;
   * no workspace name or inode for `W₁`.
8. The target still contains `A`; `W₁` is empty and untracked by the transaction ledger.
9. Retry loads only `O` and creates `W₂`. It can durably hand off `W₂`, move `A` into `W₂/quarantine`, establish absence, and remove `W₂`.
10. `O` is popped and transaction evidence may be finalized, but `W₁` remains permanently unowned.
11. Two outcomes are possible:

    * while `W₁` remains empty, recovery may report `rolled_back` despite the leaked workspace;
    * if `W₁` contains any entry, final worktree verification or later recovery encounters unexplained bytes, which cannot be removed by prefix scanning and must yield `recovery_required/restore_mismatch`.

The existing post-handoff absent rollback logic correctly verifies the quarantined inode and bytes once `rollback-prepared` is durable; the missing coverage is exclusively the workspace-creation-to-phase-handoff interval.

---

## 2. Smallest private correction

### 2.1 Extend the existing singleton intent

Add one private purpose to `_WorkspaceIntent`:

```python
Literal[
    "forward",
    "rollback-existing",
    "rollback-absent",
]
```

Purpose-specific staged names become:

```text
forward          -> staged
rollback-existing -> staged
rollback-absent   -> quarantine
```

No second ledger, operation state, public status, public reason, output field, or operation-schema change is authorized.

For `rollback-absent`, the existing `staged_device/staged_inode` fields identify the transaction-owned inode that is intended to occupy `quarantine`. Before handoff, that inode still resides at the canonical target; after handoff, `_resume_absent_restore()` may move it into the workspace. This purpose-specific interpretation avoids adding another identity field.

The current S012 validator only accepts the two existing purposes and requires `staged_name == "staged"`, so both checks must become purpose-sensitive rather than generally permissive.

### 2.2 Required write-ahead order

For the journaled transaction path, replace the current direct workspace creation with:

1. Reuse the already-completed proof that the canonical target is exact `A`.
2. Generate `workspace_name = W`.
3. Persist and fsync an unbound intent:

```json
{
  "path": "<O.relative>",
  "purpose": "rollback-absent",
  "workspace_name": "W",
  "workspace_device": null,
  "workspace_inode": null,
  "staged_name": "quarantine",
  "staged_device": null,
  "staged_inode": null
}
```

4. Call `_create_workspace(target, W)`.
5. After `_create_workspace()` has validated the directory and fsynced the parent, atomically persist the bound intent:

```json
{
  "path": "<O.relative>",
  "purpose": "rollback-absent",
  "workspace_name": "W",
  "workspace_device": "<W.st_dev>",
  "workspace_inode": "<W.st_ino>",
  "staged_name": "quarantine",
  "staged_device": "<O.after_device>",
  "staged_inode": "<O.after_inode>"
}
```

The workspace and future quarantine-occupant identities should be bound in the same ledger rewrite. There is no need for a durable workspace-bound/staged-unbound state.

6. Construct the existing rollback mutation:

```python
rollback = dataclass_replace(
    mutation,
    phase="rollback-prepared",
    workspace_name=workspace.name,
    workspace_device=workspace.device,
    workspace_inode=workspace.inode,
    staged_name="quarantine",
    staged_device=mutation.after_device,
    staged_inode=mutation.after_inode,
)
```

7. Call `phase_update(rollback)` while the intent remains active.
8. Clear `workspace_intent` only after the complete `rollback-prepared` entry is durable.
9. Close the temporary workspace descriptor.
10. Invoke the existing `_resume_absent_restore(target, rollback)` unchanged.

This creates the same handoff structure already used by S012 forward and existing-preimage rollback: intent owns pre-handoff workspace creation; the mutation entry owns all post-handoff physical recovery.

### 2.3 Callback boundary

Preserve non-journaled primitive use only when both callbacks are absent:

```text
phase_update is None
workspace_intent_update is None
```

For absent rollback, exactly one callback being supplied is invalid and must fail before `mkdir`. The application transaction path supplies both callbacks; allowing a phase-only transaction path would recreate the confirmed gap.

### 2.4 Purpose/phase handoff

The resolver must recognize only these combinations:

| Intent purpose    | Durable mutation                                              | Meaning                 | Resolver action                                              |
| ----------------- | ------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------ |
| `rollback-absent` | matching outer `published`, `before.existed == False`         | Pre-handoff reservation | Classify and clean only the empty reserved workspace         |
| `rollback-absent` | exact matching `rollback-prepared`, `before.existed == False` | Completed handoff       | Clear only the redundant intent                              |
| `rollback-absent` | any other phase, duplicate path, or identity mismatch         | Ambiguous evidence      | Preserve everything and raise `PlanningApplyRestoreMismatch` |

A completed match requires equality of:

* path;
* workspace name/device/inode;
* staged name `quarantine`;
* staged device/inode;
* `before.existed == False`;
* `phase == "rollback-prepared"`.

Do not scan or sweep `.spec-dock-apply-*` names.

---

## 3. Recovery classification

Implement this as a purpose-specific branch inside the existing `resolve_workspace_intent()` path. The existing singleton ledger, loader, persistence functions, and `_recover_workspace_intent()` ordering remain authoritative. The S012 resolver already runs before ordinary per-mutation restoration.

### 3.1 Before `mkdir`—unbound intent

Durable evidence:

```text
outer entry: published, before.existed == False
workspace identity: null
quarantine identity: null
workspace name absent
target: exact A
```

Required classification:

1. Require exactly one matching outer `published` mutation.
2. Re-prove the target is exact `A` by snapshot and inode.
3. If the workspace name is absent, clear the intent.
4. Leave `O` unchanged as `published`.
5. Continue ordinary rollback, which may reserve another workspace.

If the generated name exists despite the unbound record:

* open it descriptor-relatively with `O_DIRECTORY | O_NOFOLLOW`;
* require effective-user ownership and mode `0700`;
* require it to be empty;
* remove it with `rmdir`;
* fsync the parent;
* clear the intent.

A wrong type, symlink, wrong owner, wrong mode, or non-empty directory is ambiguous. Retain the object and intent and raise `PlanningApplyRestoreMismatch`.

### 3.2 After workspace bind, before phase handoff

Durable evidence:

```text
outer entry: published, before.existed == False
workspace identity: bound
quarantine identity: O.after_device/O.after_inode
workspace: expected to be empty
target: exact A
```

Required classification:

1. Require the intent’s staged identity to equal `O.after_device/O.after_inode`.
2. Re-prove the canonical target is exact `A`.
3. Open the workspace by its exact recorded name.
4. Require exact workspace device/inode, effective-user ownership, directory type, and mode `0700`.
5. Require a completely empty inventory.
6. Remove the workspace, fsync the parent, and clear the intent.
7. Leave the outer mutation `published` so normal rollback can retry.

If the recorded workspace is already absent, clearing the intent is safe only while the outer entry remains `published` and the target still proves exact `A`.

**Any non-empty inventory is ambiguous before handoff.** Do not unlink a `quarantine` entry even when its inode appears to equal `A`; the durable phase says the namespace move was not authorized. Preserve all bytes, retain the intent, and return `restore_mismatch`.

### 3.3 After `rollback-prepared` handoff

Durable evidence:

```text
outer entry: rollback-prepared, before.existed == False
intent: rollback-absent
workspace/staged identities: exact match
```

Required classification:

1. Require one exact mutation-intent match.
2. Clear only `workspace_intent`.
3. Do not unlink `quarantine`.
4. Do not remove the workspace.
5. Continue to the existing `_resume_absent_restore()` logic.

That existing logic classifies:

* target still `A`, empty workspace: move `A` into `quarantine`;
* target absent, exact `A` in `quarantine`: verify and finish cleanup;
* target absent, empty workspace: cleanup was already completed;
* changed target, changed quarantine inode, changed bytes, or extra entries: preserve and fail closed.

---

## 4. Exact Red/Green tests

### Unit — intent is durable before absent-rollback `mkdir`

**File:** `tests/unit/infra/test_issue_planning_apply.py`

Add:

```python
test_absent_restore_workspace_intent_is_durable_before_rollback_mkdir
```

Procedure:

1. Capture a guarded target that is initially absent.
2. Publish transaction-owned `A` and retain the resulting outer mutation `O`.
3. Persist `O` as the sole `published` ledger entry.
4. Call `guard.restore()` with both `phase_update` and `workspace_intent_update`.
5. Wrap `os.mkdir`.
6. Before the real workspace `mkdir`, read `mutation-ledger.json` and assert:

   * one entry exists;
   * it is still `published`;
   * `before.existed is False`;
   * intent purpose is `rollback-absent`;
   * intent path equals `O.relative`;
   * intent workspace name equals the pending `mkdir` name;
   * `staged_name == "quarantine"`;
   * all workspace and staged identities are `null`.
7. Raise `ProcessCrash(BaseException)` before the real `mkdir`.
8. Run `_recover_workspace_intent()`.
9. Assert:

   * the intent is cleared;
   * `O` remains `published`;
   * the target still contains exact `A`;
   * no workspace exists.
10. Retry restore and assert exact target absence and no workspace.

**Red:** S012 reaches `mkdir` with `workspace_intent == null`.

**Green:** the exact absent-rollback workspace name is durable before namespace creation.

### Unit — classify all absent-rollback handoff boundaries

Add parameterized:

```python
test_absent_restore_workspace_intent_recovery_classifies_boundaries
```

Cases:

```text
before_mkdir
after_mkdir_before_bind
after_workspace_bind
after_rollback_prepared_handoff
```

Assertions:

* `before_mkdir`: intent cleared; outer remains `published`; target remains exact `A`.
* `after_mkdir_before_bind`: exact safe empty workspace removed; intent cleared; outer remains `published`.
* `after_workspace_bind`: exact bound empty workspace removed; intent cleared; target remains `A`; staged identity in the intent equals `O.after_device/O.after_inode`.
* `after_rollback_prepared_handoff`: resolver clears only the intent and leaves the workspace; subsequent `restore()` establishes absence and removes the workspace.

**Red:** the attached S012 intent parser/resolver has no `rollback-absent` purpose or `quarantine` staged-name contract.

**Green:** all four states are deterministic without a second recovery mechanism.

### Unit — preserve ambiguous non-empty workspaces

Add parameterized:

```python
test_absent_restore_workspace_intent_preserves_ambiguous_nonempty_workspace
```

Cases:

1. Unbound safe workspace containing unknown sentinel bytes.
2. Bound exact workspace containing an unexpected `quarantine` entry before phase handoff.
3. Bound exact workspace containing any extra entry.
4. Workspace name replaced with a different inode or unsafe object.

Expect `PlanningApplyRestoreMismatch`. Assert byte-for-byte that:

* all entries remain;
* the workspace remains;
* the target remains unchanged;
* the mutation entry remains `published`;
* the ledger intent remains byte-identical.

This test must prohibit selectively deleting an apparently known inode while any unexpected inventory exists. The existing S012 ambiguity test establishes this policy for forward intent and should remain unchanged.

### Integration — crash before absent `rollback-prepared` handoff

**File:** `tests/integration/test_issue_planning_apply.py`

Add:

```python
@pytest.mark.parametrize("artifact", ["decision", "companion"])
def test_recovery_cleans_absent_rollback_workspace_crash_before_phase_handoff(...)
```

Procedure:

1. Create the standard repository, bare origin, operation, output directory, document snapshots, raw index snapshot, and managed-state snapshot.
2. Select:

   * decision artifact, with rollback triggered after `after_decision_write`; or
   * newly created companion, with rollback triggered after `after_companion_write`.
3. Wrap `_persist_target_mutations()`.
4. When the selected mutation is first presented as:

   * `phase == "rollback-prepared"`;
   * `before.existed is False`;
     raise `ProcessCrash` **before** invoking the real persistence function.
5. After death, assert:

   * on-disk outer entry is still `published`;
   * active intent has `purpose == "rollback-absent"`;
   * `staged_name == "quarantine"`;
   * workspace identity is bound;
   * staged identity equals the selected mutation’s `after_device/after_inode`;
   * the workspace exists and is empty;
   * the canonical target still contains exact transaction-owned bytes.
6. Retry with validation and sync runners that fail the test if called.
7. Assert:

   * result is `rolled_back/planning_commit_failed`;
   * all canonical documents equal exact baseline bytes and modes;
   * decision and newly created companion are absent;
   * raw index and managed state equal their snapshots;
   * local and remote HEAD remain the reviewed HEAD;
   * no `.spec-dock-apply-*` workspace remains;
   * transaction evidence is removed only after rollback postconditions;
   * operation state is `ROLLED_BACK`.

**Red:** S012 records no intent for this path and leaves the first empty workspace behind; the test fails either at intent inspection or the final no-workspace assertion.

**Green:** retry drains the exact pre-handoff reservation through the existing resolver, then retries the outer published mutation normally.

### Required regression tests

Run without semantic changes:

* `test_recovery_resumes_absent_restore_after_quarantine_rename`, which covers process death after the target has entered the recorded quarantine.
* `test_rollback_absent_artifact_race_preserves_concurrent_bytes`.
* all S012 forward and existing-preimage workspace-intent ordering and ambiguity tests. The existing reverse-workspace test demonstrates the intended reserve-before-`mkdir` pattern.

---

## 5. Allowed files

### Provider authority

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

### Mechanical projection only

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

No application, Candidate, ports, bootstrap, public contract, operation schema, status/reason, documentation, Oracle configuration, or unrelated test changes are authorized.

---

## 6. Safe implementation order

1. Add the absent-rollback pre-`mkdir` Red test.
2. Add the boundary-classification and non-empty ambiguity unit Red tests.
3. Add the decision/companion integration Red test and explicitly assert the leaked-workspace condition, not only the returned status.
4. Extend `_WorkspaceIntent.purpose` and the private ledger parser with `rollback-absent`.
5. Make `staged_name` validation purpose-specific: `staged` for existing purposes, `quarantine` for absent rollback.
6. Add the `rollback-absent` branch to the existing resolver:

   * exact outer-entry validation;
   * exact target proof;
   * empty-workspace-only pre-handoff cleanup;
   * completed-handoff reconciliation.
7. Wire the absent branch as:

   * reserve intent;
   * create workspace using the reserved name;
   * bind workspace and future quarantine inode;
   * persist `rollback-prepared`;
   * clear intent;
   * invoke existing absent restore.
8. Run the focused new unit and integration tests.
9. Run the complete apply unit and integration suites, especially all S010–S012 unknown-byte, quarantine-rename, shortened-ledger, interrupted-recovery, and retry tests.
10. Modify the provider source first, then mechanically project it to the dogfood path.
11. Verify provider/dogfood byte parity, lint, validation, and `git diff --check`.

## Assumptions and verification boundary

* The attached provider source and tests are assumed to be the complete authoritative uncommitted S012 state, as directed.
* The immediate-status distinction for an empty leaked directory is a static code-and-Git-semantics conclusion; the proposed integration Red test should make that behavior executable.
* No repository file was changed, no patch or archive was created, and no test command was run.
