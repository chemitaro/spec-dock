# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6badde-0a50-83ee-a45f-e98489422f8c

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

Use the attached S014 task brief. Inspect the exact GitHub branch and attached uncommitted source/tests, then concretize only the three private-entry final CAS P1 findings.

## Answer

# S014 — Private-entry final-CAS P1 work packets

## Repository gate and disposition

The GitHub connector opened `chemitaro/spec-dock` on `iss-00334-implement-chatgpt-issue-planning-workflow` first. PR #351 identifies that branch at exact pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`, based on `main`; the default branch was not substituted.

The attached Candidate and Apply provider sources and tests are treated as the authoritative uncommitted S013 layer over that HEAD, as required by the S014 brief.

**All three findings are confirmed P1.**

1. Candidate private cleanup can delete a same-UID replacement.
2. Apply staged/quarantine cleanup can delete a same-UID replacement for all three purposes.
3. Existing-file rollback can exchange an unverified replacement into the canonical path and currently lacks a safe compensating exchange.

The pushed Candidate baseline already had a check followed by a pathname unlink during rejection cleanup. The attached S013 Candidate source moves the public entry to a private cleanup directory first, but retains the same final check-then-unlink boundary inside that directory.

## Required common invariant: atomic retirement, not another check before unlink

A second `stat`, `fstat`, or snapshot immediately before `unlink` does not fix these findings. Linux, Darwin, and POSIX unlink interfaces remove the entry currently attached to a pathname and accept no expected-device/inode predicate. Under the stated same-UID threat, the pathname can be replaced after any final check. This is an inference from the unlink API contracts and the threat model. ([The Open Group][1])

Therefore the shared private-entry CAS pattern must be:

```text
private source slot
    -- descriptor-relative atomic no-replace rename -->
private retained slot

verify the moved object after the atomic move

exact expected object:
    commit by retention; source slot is safely absent
unexpected object:
    make at most one no-replace compensation attempt
    otherwise retain every entry and fail closed

never pathname-unlink the retained object
```

The concrete rules are:

1. The retirement destination is beneath an already opened and identity-verified `0700` directory.
2. Its filename is deterministic from the durable object identity where recovery is required, or collision-resistant where no durable recovery exists.
3. Use only the existing descriptor-relative native no-replace backends:

   * Linux `renameat2(..., RENAME_NOREPLACE)`;
   * Darwin `renameatx_np(..., RENAME_EXCL)`.
4. Fsync both source and retirement directories after a successful move.
5. Open the retired name with `O_NOFOLLOW` and verify its inode and exact snapshot against the recorded object.
6. On an exact match, leave the object retained. Do not unlink it later through an automated cleanup path.
7. On mismatch:

   * if the original source slot is absent, attempt one no-replace move back;
   * verify the compensated state;
   * on collision, unsupported operation, changed identity, or failed verification, retain all objects and report ambiguity.
8. Do not use `os.rename`, `os.replace`, copy-and-unlink, or pathname-unlink fallback.
9. Candidate and Apply implement mirrored semantics privately in their own modules; no shared filesystem framework is introduced.

Persistent private retention is not optional under the specified same-UID threat. Any implementation that eventually pathname-unlinks the retained name recreates the same P1 at a later pathname.

---

# WP1 — Candidate rejection cleanup final CAS

## Disposition

**Confirmed P1.**

The attached `_cleanup_rejected_published_candidate()`:

1. moves the public logical filename into a private cleanup directory;
2. checks that the private name still resolves to `published_entry`;
3. pathname-unlinks that name.

The move into private storage closes the earlier public-name race, but mode `0700` does not isolate against another process operating as the same UID.

## Deterministic race

Let `P` be the published Candidate inode and `U` unknown same-UID bytes.

1. Final Candidate attachment verification rejects, so rejection cleanup starts.
2. Cleanup atomically moves the public Candidate name into `cleanup_fd/logical.zip`.
3. `_owned_entry_matches(cleanup_fd, published_entry)` proves that `logical.zip` is `P`.
4. Before `os.unlink(logical.zip, dir_fd=cleanup_fd)`:

   * the racing actor renames `P` to `owned-aside.zip`;
   * the actor creates `U` at `logical.zip`.
5. The current unlink deletes `U`.
6. `P` survives under the aside name, so the loss of `U` can be masked by the original Candidate rejection.

This is distinct from the existing test that swaps the **public** logical filename before the public-to-private rename; that earlier race must remain covered.

## Smallest correction

Add a Candidate-private retirement helper, for example:

```python
_retire_candidate_cleanup_entry(
    *,
    cleanup: _OwnedEntry,
    published_entry: _OwnedEntry,
    output_descriptor: int,
) -> None
```

Required behavior:

1. Derive a fresh hidden retained name under a verified Candidate retention directory beneath `output_descriptor`.

2. Atomically no-replace-rename:

   ```text
   cleanup_fd/published_entry.name
       ->
   retention_fd/retained_name
   ```

3. Fsync `cleanup_fd` and `retention_fd`.

4. Verify the retained entry against the already open `published_entry.descriptor`.

5. Exact `P`:

   * leave `P` at the retained name;
   * remove the now-empty cleanup directory using the existing empty-directory path;
   * preserve the original Candidate rejection.

6. Retired entry is not `P`:

   * attempt one no-replace move back to the cleanup slot;
   * never move an unproven entry to the public logical filename;
   * retain the cleanup and retention inventories on any collision or mismatch;
   * preserve the original Candidate rejection.

7. Unsupported native operations preserve the cleanup entry and directory. They must not activate a pathname fallback.

No Candidate ZIP identity, archive bytes, collision result, public filename, or success result changes.

## Exact Red/Green tests

### Candidate unit: swap after private match

Add to `tests/unit/infra/test_issue_planning_candidate.py`:

```python
test_candidate_rejection_cleanup_private_slot_swap_preserves_unknown_and_owned_candidate
```

Procedure:

1. Force `_verify_published_candidate_attachment()` to reject after publication.
2. Wrap `_owned_entry_matches()`.
3. When it returns `True` for `published_entry` under the cleanup-directory FD:

   * rename the private logical name to `owned-aside.zip`;
   * create sentinel `U` at the original private logical name;
   * return the previously obtained `True`.
4. Invoke Candidate publication.

**Red:** current code pathname-unlinks `U`.

**Green:**

* Candidate rejection is still raised;
* no public logical Candidate remains;
* `U` remains byte-exact;
* the owned Candidate bytes remain byte-exact under the aside or retained name;
* no private entry is unlinked;
* ambiguous private directories are retained.

### Candidate unit: retirement destination replacement

Add:

```python
test_candidate_retirement_post_move_destination_swap_preserves_every_entry
```

After the real no-replace retirement move succeeds but before destination verification:

1. rename the retired expected Candidate aside;
2. create unknown sentinel bytes at the retained name.

Assert that verification fails closed, any compensation is no-replace, and both the expected Candidate and sentinel bytes survive.

### Candidate native-backend tests

Extend the current no-replace backend tests to prove that the retirement helper passes:

* distinct cleanup and retention directory FDs;
* exact source and destination names;
* Linux `RENAME_NOREPLACE`;
* Darwin `RENAME_EXCL`.

The missing-symbol and native-error cases must assert:

* no `os.rename` or `os.replace` fallback;
* no unlink;
* byte-identical cleanup inventory. Existing Candidate backend tests provide the fixture pattern.

### Candidate regression adjustment

Update:

```python
test_candidate_publish_rejects_detached_public_path_and_removes_published_entry
```

The Green postcondition becomes:

* no Candidate remains at the public logical filename;
* no redirected output receives bytes;
* the rejected owned Candidate may remain under the private retained-entry namespace.

It must no longer require the captured output directory to be physically empty, because safe retention is the replacement for unsafe deletion.

---

# WP2 — Apply workspace staged/quarantine final CAS

## Disposition

**Confirmed P1 for forward, rollback-existing, and rollback-absent purposes.**

The attached Apply source has separate identity/snapshot proof followed by pathname-unlink in multiple private workspace paths, including:

* ordinary `cleanup_workspace`;
* bound and unbound `resolve_workspace_intent` cleanup;
* forward publication cleanup and exchange-back cleanup;
* prepared-mutation cleanup;
* existing rollback displaced-target cleanup;
* absent rollback quarantine cleanup.

A same-UID actor can replace `staged` or `quarantine` after the proof and before any of those unlink calls.

## Deterministic race

For each purpose, let `E` be the recorded private entry and `U` unknown bytes.

1. Apply opens the exact recorded workspace and proves its identity.
2. It proves that `staged` or `quarantine` has `E`’s inode and expected snapshot.
3. The racing actor renames `E` aside and creates `U` at the recorded slot.
4. The current pathname-unlink deletes `U`.
5. Recovery may then observe an empty recorded slot and incorrectly treat cleanup as complete.

The purpose changes the meaning of `E`, but not the vulnerability:

* `forward`: staged replacement or displaced preimage;
* `rollback-existing`: staged original preimage or displaced transaction replacement;
* `rollback-absent`: quarantined transaction-created target;
* unbound workspace intent: the nominally zero-byte staged placeholder can be replaced with nonzero unknown bytes before unlink.

## Smallest correction

### 1. Add one Apply-private retirement sink

Add an optional top-level private directory inside the existing operation evidence directory, for example:

```text
planning-apply-<operation-id>/retired-private-entries/
```

Properties:

* mode `0700`;
* opened descriptor-relatively from `handle.operation_fd`;
* exact directory device/inode retained in an Apply-private handle;
* permitted as optional private operation evidence;
* child names restricted to the private retirement naming scheme;
* not removed by `_remove_transaction_backup()`.

Do not place retained entries inside `transaction/`, because transaction cleanup must still be able to remove the backup directory while retired entries remain preserved.

### 2. Establish same-filesystem capability before mutation

A native rename cannot cross filesystems. Before the first repository mutation:

1. compare the retirement-sink `st_dev` to every captured target-parent `st_dev`;
2. if any differ, stop through the existing pre-mutation blocked path;
3. do not create a transaction mutation or copy-and-unlink fallback;
4. introduce no new public status or reason.

After mutation has started, `EXDEV`, missing native symbols, or equivalent capability loss is `PlanningApplyRestoreMismatch` and retains all transaction evidence.

### 3. Add one Apply-private regular-entry retirement helper

For example:

```python
_retire_workspace_entry(
    *,
    workspace: _MutationWorkspace,
    source_name: str,
    expected_device: int,
    expected_inode: int,
    expected_snapshot: FileSnapshot,
    retirement_sink: _PrivateRetirementSink,
    retirement_key: str,
) -> None
```

The retained filename must be deterministically derivable from durable data such as:

* operation ID;
* target relative path;
* purpose/phase;
* workspace device/inode;
* staged device/inode.

That permits recovery after process death between the atomic move and subsequent ledger progress.

Required classification:

**Source exists, retained destination absent**

* atomically no-replace-retire the source;
* fsync both directories;
* verify the moved entry.

**Source absent, retained destination is exact expected entry**

* retirement already completed;
* continue empty-workspace cleanup without unlinking the retained entry.

**Source and destination both absent**

* accept only where the surrounding durable phase and canonical target state independently prove cleanup had completed;
* otherwise return ambiguity.

**Source or retained destination has an unexpected inode/snapshot**

* attempt at most one no-replace compensation when its direction is unambiguous;
* retain all entries and raise `PlanningApplyRestoreMismatch`.

### 4. Route every bounded private-file unlink through retirement

Within the S014 scope, replace direct `staged`/`quarantine` unlink operations in:

* `cleanup_workspace`;
* `resolve_workspace_intent`;
* `compare_replace` cleanup branches;
* `_resume_existing_restore`;
* `resolve_prepared`;
* `_resume_absent_restore`.

Do not expand this packet to transaction-evidence removal, managed-state cleanup, Git index restoration, Candidate success staging, or unrelated filesystem helpers.

### 5. Preserve current durable ownership order

The S012/S013 workspace intent and mutation ledger remain authoritative:

* intent owns pre-handoff private objects;
* `prepared`, `published`, or `rollback-prepared` owns post-handoff objects;
* retirement happens only while that durable owner is still present;
* intent or mutation progress is cleared only after the retirement rename and both directory fsyncs.

The attached S013 tests already establish the intended workspace-intent write-ahead and handoff order and must remain unchanged.

## Exact Red/Green unit tests

### Parameterized private-slot replacement

Add to `tests/unit/infra/test_issue_planning_apply.py`:

```python
@pytest.mark.parametrize(
    "purpose",
    ["forward", "rollback-existing", "rollback-absent"],
)
def test_apply_private_entry_swap_after_final_proof_preserves_all_bytes(...)
```

Construct these exact states:

* `forward`: a bound staged entry being drained by workspace-intent or prepared cleanup;
* `rollback-existing`: canonical preimage already restored and the workspace contains the recorded displaced transaction replacement;
* `rollback-absent`: canonical target is absent and the workspace contains the exact recorded quarantine.

At the last identity/snapshot proof before the current unlink:

1. rename the expected entry aside;
2. create byte-distinct `U` at `staged` or `quarantine`;
3. allow the caller to continue.

**Red:** current code deletes `U`.

**Green:**

* `PlanningApplyRestoreMismatch` is raised;
* `U` remains byte-exact;
* the recorded expected entry remains byte-exact;
* canonical bytes/absence remain unchanged from the pre-cleanup state;
* workspace and durable ledger/intent remain available;
* no retirement or compensation call overwrites an occupied name.

### Unbound zero-byte placeholder replacement

Add:

```python
test_unbound_workspace_placeholder_replacement_is_retained_not_unlinked
```

1. Create the S012 unbound-staged intent state with a legitimate zero-byte `0600` placeholder.
2. After its safety proof, rename it aside and create nonzero sentinel bytes at `staged`.
3. Run intent recovery.

**Red:** current code deletes the sentinel because it acts on the verified pathname.

**Green:** the sentinel and placeholder both remain; the intent remains byte-identical; recovery reports `PlanningApplyRestoreMismatch`.

### Retirement crash idempotence

Add:

```python
test_private_entry_retirement_resume_accepts_exact_retained_entry
```

1. Perform the real no-replace move to the deterministic retained name.
2. Raise `ProcessCrash(BaseException)` after both directory fsyncs but before workspace removal or ledger shrink.
3. Resume the same cleanup.

Assert:

* source slot is absent;
* deterministic retained destination identifies the exact expected entry;
* no second rename or unlink occurs;
* the workspace can be removed if otherwise empty;
* the mutation or intent is consumed only afterward.

### Direct-unlink prohibition

Add:

```python
test_apply_transaction_private_entries_are_never_pathname_unlinked
```

Monkeypatch `os.unlink` to fail when the target name is `staged` or `quarantine`, then execute representative forward, rollback-existing, and rollback-absent cleanup paths.

Green must complete through retirement or fail closed without invoking pathname unlink for those entries.

### Apply backend and capability tests

Add tests proving:

* distinct workspace and retention FDs reach Linux/Darwin no-replace primitives;
* the retirement destination name is deterministic from durable identity;
* same-device preflight runs before any target namespace mutation;
* `EXDEV` and missing symbols do not invoke copy, `shutil`, `os.rename`, `os.replace`, or unlink fallback.

The existing no-replace backend tests supply the native-call fixture pattern.

## Exact Red/Green integration test

Add to `tests/integration/test_issue_planning_apply.py`:

```python
@pytest.mark.parametrize(
    "purpose",
    ["forward", "rollback-existing", "rollback-absent"],
)
def test_apply_private_entry_final_cas_race_preserves_every_byte_and_evidence(...)
```

Use the existing repository/origin/operation fixtures.

### `forward`

Inject after an existing canonical target has been exchanged but immediately before its displaced preimage would currently be unlinked from the forward workspace.

### `rollback-existing`

Force precommit rollback. Inject after the reverse exchange has restored the original canonical file but immediately before the displaced transaction replacement would currently be unlinked.

### `rollback-absent`

Select the decision artifact or newly created companion. Inject after the artifact has been moved into `quarantine` and canonical absence is established, but immediately before the quarantine unlink.

For each case:

1. rename the recorded private entry aside;
2. create `U` at the recorded private slot;
3. resume the current code path.

**Red:** `U` disappears.

**Green:**

* result is `recovery_required/restore_mismatch`;
* `U` and the recorded expected bytes both remain available;
* canonical preimage, transaction replacement, or exact absence is preserved according to the case;
* no commit or push occurs;
* local and remote HEAD remain the reviewed HEAD;
* transaction evidence, mutation ledger, and ambiguous workspace remain;
* validation and sync are not rerun during recovery.

Keep the existing forward staged-name exchange race and absent canonical-removal race as regressions; they cover earlier namespace boundaries, not this final private-entry CAS.

---

# WP3 — Existing rollback exchange must compensate from an atomic postcondition

## Disposition

**Confirmed P1.**

In `rollback-prepared` recovery for an existing preimage, the attached code:

1. proves `workspace/staged` is the recorded preimage `B`;
2. atomically exchanges that pathname with canonical transaction replacement `A`;
3. verifies the resulting target and workspace;
4. raises on mismatch without reliably returning the exchanged objects to their prior sides.

A same-UID actor can replace `staged` after step 1 and before step 2. Unknown `U` then becomes canonical, while `A` moves to the workspace.

The existing unit test that swaps the workspace slot **after a completed reverse exchange and process interruption** remains valuable, but does not cover this pre-exchange final-CAS window.

## Deterministic staged-side race

Initial state:

```text
canonical target = A, exact transaction replacement
workspace/staged = B, exact original preimage
```

Sequence:

1. Recovery verifies `B`.

2. The actor renames `B` aside and creates `U` at `workspace/staged`.

3. Native exchange swaps `U` and `A`.

4. Result:

   ```text
   canonical target = U
   workspace/staged = A
   B remains aside
   ```

5. The target postcondition fails.

6. Current recovery raises without safely restoring `A` to canonical.

7. Unknown bytes remain canonical and the operation is wedged in recovery.

No bytes are necessarily deleted at this point, but canonical integrity is lost and a later cleanup path may hit the WP2 unlink defect.

## Smallest correction

Add an Apply-private reverse-exchange CAS helper; do not alter the public mutation schema:

```python
_exchange_existing_restore_cas(
    *,
    target: _GuardedRepositoryTarget,
    workspace: _MutationWorkspace,
    mutation: _TargetMutation,
) -> None
```

### Pre-exchange captures

Immediately before the exchange:

1. open canonical target with `O_NOFOLLOW`;
2. open the staged slot with `O_NOFOLLOW`;
3. verify both are regular files;
4. capture their exact descriptors, device/inode identities, and snapshots;
5. require:

   * canonical descriptor is recorded `A`;
   * staged descriptor is recorded `B`.

These checks do not authorize success by themselves; they provide post-exchange and compensation anchors.

### First exchange postcondition

After `_exchange_entries_at(...)`:

1. fsync workspace and target parent;
2. success requires both:

   * canonical name identifies exact opened/recorded `B`;
   * workspace slot identifies exact opened/recorded `A`.

Only that two-sided state establishes a completed rollback exchange.

### Exchange-back rules

On any mismatch, do not retire or unlink either side.

Allow at most one compensating exchange:

1. **Workspace slot is exact `A`:**

   * exchange back;
   * require canonical name to become exact `A`;
   * the current canonical occupant is moved into private workspace storage;
   * preserve that occupant and fail closed.

   This covers the staged-side `B → U` race.

2. **Canonical target is exact `B`:**

   * exchange back;
   * require workspace slot to become exact `B`;
   * require canonical name to match the target descriptor/snapshot captured immediately before the first exchange;
   * preserve all entries and fail closed.

   This covers a target-side `A → C` replacement before the exchange.

3. **Neither side proves a recorded exchange member:**

   * do not perform another exchange;
   * preserve the current topology and return `PlanningApplyRestoreMismatch`.

4. **Both expected sides are present but either snapshot changed:**

   * do not accept success;
   * one anchored exchange-back may restore the pre-exchange attachment;
   * retain all bytes and return mismatch.

5. **Exchange-back syscall or postcondition fails:**

   * do not retry or loop;
   * do not unlink;
   * retain the workspace and transaction evidence.

After an exact successful first exchange, remove displaced `A` only through WP2 retirement. Never call pathname-unlink.

Unsupported platforms and missing native symbols remain fail closed.

## Exact Red/Green unit tests

### Staged-side replacement

Add:

```python
test_existing_restore_pre_exchange_staged_swap_exchanges_back_and_preserves_all_entries
```

1. Create durable `rollback-prepared` state with target `A` and staged `B`.
2. Wrap `_exchange_entries_at()`.
3. Immediately before the real first exchange:

   * rename `B` to `preimage-aside`;
   * create `U` at `staged`;
   * invoke the real exchange.
4. Resume existing rollback.

**Red:** canonical target ends as `U`.

**Green:**

* `PlanningApplyRestoreMismatch` is raised;
* the compensating exchange restores exact `A` to canonical;
* `U` is retained privately;
* `B` remains byte-exact under its aside name;
* workspace and durable mutation evidence remain;
* neither `U`, `A`, nor `B` is unlinked.

### Target-side replacement

Add:

```python
test_existing_restore_pre_exchange_target_swap_restores_concurrent_canonical_attachment
```

1. Before the real exchange, rename recorded `A` aside and create concurrent canonical file `C`.
2. Let the exchange put `B` canonical and `C` in the workspace.
3. Run the compensating exchange.

Green assertions:

* `C` is restored byte-exact at the canonical pathname;
* `B` returns to the staged slot;
* `A` remains aside;
* recovery returns mismatch and retains the workspace.

The transaction must not overwrite a concurrent canonical attachment merely because the desired preimage `B` briefly became canonical.

### Ambiguity stops after one compensation

Add:

```python
test_existing_restore_exchange_back_ambiguity_never_loops_or_unlinks
```

Inject another namespace replacement between the first exchange and compensation. Assert:

* at most two exchange calls total;
* no unlink or retirement occurs after ambiguous exchange-back;
* every discoverable file remains byte-exact;
* `PlanningApplyRestoreMismatch` is raised.

## Exact Red/Green integration test

Add:

```python
@pytest.mark.parametrize("race_side", ["staged", "target"])
def test_existing_rollback_final_cas_race_preserves_canonical_and_private_bytes(...)
```

Procedure:

1. Create the standard repository, bare origin, operation, baseline documents, index snapshot, and managed snapshot.
2. Force a precommit failure after forward replacements so existing-file rollback begins.
3. Intercept the first reverse existing-file exchange.
4. For `staged`:

   * rename staged `B` aside;
   * install `U` at the staged slot.
5. For `target`:

   * rename canonical transaction replacement `A` aside;
   * install concurrent canonical `C`.
6. Invoke the real exchange and allow recovery classification.

**Red:**

* staged case leaves `U` canonical;
* target case may leave an attachment not equal to the pre-exchange canonical state.

**Green:**

* result is `recovery_required/restore_mismatch`;
* staged case restores exact `A` canonical and retains `B` plus `U`;
* target case restores exact `C` canonical and retains `A` plus `B`;
* no private entry is unlinked;
* no commit or push occurs;
* local and remote HEAD remain the reviewed HEAD;
* raw index and managed-state recovery do not claim success;
* transaction evidence and the rollback workspace remain available.

Keep these existing tests unchanged as regressions:

* forward staged-name replacement before exchange;
* reverse-exchange crash followed by normal resume;
* post-exchange workspace-slot replacement;
* absent quarantine rename interruption.

---

# Allowed files

## Provider authority

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_candidate.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

## Mechanical projection only

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`
* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

No application, domain contract, operation schema, public status/reason, CLI, Oracle configuration, documentation, or unrelated cleanup changes are authorized.

---

# Safe implementation order

1. Add the Candidate private-slot and retirement-destination Red tests.
2. Add the Apply forward/rollback-existing/rollback-absent final-private-entry Red tests.
3. Add the existing-rollback staged-side and target-side exchange Red tests.
4. Implement the Candidate-private retire-and-verify helper using the existing descriptor-relative no-replace primitive.
5. Add the Apply operation-evidence retirement directory, validation, and pre-mutation same-device capability check.
6. Implement the Apply-private retire-and-verify helper and its deterministic retirement naming.
7. Route every S014-scoped `staged` and `quarantine` unlink through the helper.
8. Update recovery to accept an exact deterministic retained destination as completed retirement while preserving all ambiguous states.
9. Implement the two-sided existing-rollback exchange postcondition and one-shot anchored exchange-back.
10. Route exact post-reverse-exchange displaced-target cleanup through Apply retirement.
11. Run focused Red/Green tests.
12. Run the complete Candidate unit suite and Apply unit/integration suites, particularly every S010–S013 race, intent, crash, ledger-draining, and quarantine test.
13. Run unsupported-platform, missing-symbol, `EXDEV`, provider/projection parity, lint, validation, and `git diff --check` gates.
14. Change provider authority first; mechanically project only after provider tests pass.

## Assumptions, uncertainty, and unverified claims

**Assumption:** the attached provider sources and two Apply test layers are the complete authoritative uncommitted S013 state, as directed.

**Necessary consequence:** exact transaction-owned bytes will remain in private retained-entry storage after successful logical cleanup. Under the same-UID threat and currently allowed pathname-based primitives, safely deleting those named bytes cannot be proven. No automatic retained-entry purger belongs in this packet.

**Filesystem boundary:** Apply retirement requires the operation-evidence retention directory and target workspaces to share `st_dev`. A different-device configuration must stop before mutation rather than fall back to copying and unlinking.

**Unverified execution:** no repository file was modified, no patch/ZIP/commit was created, and no test command or native syscall experiment was run as part of this analysis.

[1]: https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html "https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html"
