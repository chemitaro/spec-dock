# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b510a-f674-83ee-ba87-74d1e307e536

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

Use the attached S005 brief as the complete defect-only follow-up. You MUST inspect the exact current GitHub branch and confirm HEAD 6c9302ab08c7f352e85a199b65bdeb522376171c; if unavailable return repository access failed and DO NOT inspect or substitute the default branch. Return only the requested bounded guidance.

## Answer

GitHub binding confirmed: `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, exact HEAD `6c9302ab08c7f352e85a199b65bdeb522376171c`.

## Defect A — Stage ownership is first observed after `mkdir`

### `minimal_strategy`

Adopt the preferred direct-file direction. No concrete Candidate contract requires a private staging **directory**; the contract requires deterministic Candidate bytes and identity, safe collision handling, atomic publication, and no partial final Candidate.  

Replace the stage-directory-plus-file pair with one private `_OwnedEntry` representing a randomly named staged ZIP directly beneath the already verified output-directory descriptor:

* Generate a hidden random name such as `.spec-dock-issue-candidate-<128-bit-token>.zip`.
* Create it with one descriptor-relative `os.open` using `O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW | O_NONBLOCK`, mode `0o600`.
* Treat the successful `openat` return as the ownership-establishing event. Do not `stat` the name before creation.
* Immediately `fstat` the returned descriptor, require a regular file, and capture `(st_dev, st_ino)`.
* Keep the descriptor open through ZIP construction, reread, validation, identity derivation, publication, and failure cleanup.
* Before publication, require the random staged name under the output descriptor to denote the same open regular file.
* Publish with the existing descriptor-relative Linux/Darwin no-replace helper, using the output descriptor as both source and destination parent.
* On failure, unlink only when the random staged name still denotes the captured file.

The existing `_OwnedEntry`, `_owned_entry_matches`, descriptor reader, deterministic writer, and no-replace helpers remain suitable. `_create_private_stage_directory` is replaced by a bounded `_create_private_staged_file`; no new public abstraction is needed. 

### `exact_operation_order`

1. Open the validated output directory and verify its device/inode against `OutputDirectoryGuard`.
2. Check the final logical filename relative to that descriptor. An existing entry remains an immediate `CandidateCollision`.
3. Generate a random staged filename.
4. Call `openat(O_CREAT | O_EXCL | O_NOFOLLOW, 0o600)` relative to the output descriptor.

   * On `EEXIST`, generate another name, retaining the current bounded retry count.
   * On another error, return `CandidateBuildFailed`.
5. `fstat` the returned descriptor:

   * require `S_ISREG`;
   * capture device and inode in `_OwnedEntry`;
   * do not trust or inspect the pathname as proof of initial ownership.
6. Write the ZIP through a duplicate of that descriptor using the unchanged `_write_deterministic_zip`.
7. Flush and `fsync` the descriptor-backed stream.
8. Rewind and bounded-read through the original descriptor.
9. Review the captured bytes and derive Candidate identity exactly as now. The random staging name must not enter the ZIP, manifest, logical filename, observed transport filename, or identity digest.
10. Immediately before publication, call `_owned_entry_matches(output_descriptor, staged, expected_kind="file")`.

    * A missing, renamed, replaced, symlinked, or type-changed name produces `CandidatePublicationFailed`.
11. Call `_atomic_publish_no_replace_at` with:

    * source parent: output descriptor;
    * source name: random staged name;
    * destination parent: output descriptor;
    * destination name: `material.logical_filename`.
12. Preserve current error mapping:

    * destination `EEXIST` → `CandidateCollision`;
    * unsupported platform or other publication error → `CandidatePublicationFailed`.
13. On successful rename, mark the entry published and return the existing `PublishedCandidate`.
14. In `finally`, when unpublished:

    * unlink the random name only after a fresh descriptor/name identity match;
    * otherwise preserve the entry;
    * close the descriptor in all cases.
15. Do not search for renamed files, recursively remove anything, or clean entries based only on prefix, owner, or permissions.

If `fstat` itself fails before identity capture, close the descriptor and leave any name untouched. A possible leak is safer than deleting an entry whose identity was never established.

### `tests`

1. **No staging-directory interval remains**

   Replace the directory-race tests with a test that:

   * intercepts `os.mkdir`;
   * fails if a descriptor-relative name beginning with `.spec-dock-issue-candidate-` is created beneath the output descriptor;
   * records the staged-file `os.open` call;
   * requires `O_CREAT`, `O_EXCL`, and `O_NOFOLLOW`;
   * completes a successful publication;
   * verifies exactly one final Candidate and no random staged entry remain.

   Path-based temporary directories used solely by the archive reviewer may continue; the assertion is specifically against an output-descriptor-relative Candidate stage directory.

2. **Replacement immediately after atomic file creation**

   Intercept the first matching staged-file `os.open`:

   * call the real `os.open` and retain its returned descriptor;
   * rename the created random entry to `<random-name>.owned`;
   * create a sentinel regular file under the original random name;
   * return the original descriptor to the publisher.

   Expected result:

   * the publisher may write and validate through the descriptor for the renamed owned file;
   * pre-publication identity comparison fails;
   * result is `CandidatePublicationFailed`;
   * the final logical Candidate is absent;
   * sentinel bytes under the replacement name remain exact;
   * the renamed owned file is preserved rather than searched for or deleted.

   This closes the previously untested interval immediately after atomic creation, rather than merely replacing the name later during review. 

3. **Unowned random-name collision**

   Fix the random-name sequence, precreate a sentinel at the first staged name, and require the publisher to retry without modifying that sentinel. A bounded sequence in which every name collides must end in `CandidateBuildFailed` and preserve every existing entry.

4. Retain the existing assertions for:

   * deterministic ZIP bytes and metadata;
   * Candidate identity and schema;
   * preexisting final collision;
   * racing final collision;
   * unsupported-platform failure with no final Candidate;
   * output-directory descriptor binding after pathname replacement.

   Remove or rewrite tests whose premise is the now-eliminated private stage directory. 

### `contract_preservation`

* `PublishedCandidate`, Candidate schema, control files, logical filename, observed transport filename, and identity derivation remain unchanged.
* `_write_deterministic_zip` receives the same inputs, so ZIP entry order, timestamps, permissions encoded inside the ZIP, compression, comments, and byte identity remain unchanged.
* The final publication still uses the existing Darwin `renameatx_np` and Linux `renameat2` no-replace behavior.
* Both early and racing final-name collisions continue to return `CandidateCollision` without replacing existing bytes.
* Unsupported platforms continue to return `CandidatePublicationFailed`.
* The staged file’s random name is private implementation state and never becomes Candidate evidence.
* Mode `0o600` keeps the directly staged artifact private. The attached public Candidate contract does not require a particular host-filesystem mode for the final ZIP. 

### `residual_risk`

A same-credential actor can still replace the random name after the final identity check but before the subsequent rename or unlink syscall. The current portable Linux/Darwin interface does not provide a common descriptor-only no-replace publication or unlink operation. This remains the explicitly accepted identity-check-to-name-operation syscall-sized interval.

When an actor renames the owned staged file, the implementation intentionally does not search for or delete the renamed object. Such a file may remain as leaked temporary state, but third-party state is not overwritten or removed.

## Defect B — Unknown durable state enters restore

### `minimal_strategy`

Define and validate a closed internal durable-state vocabulary before loading a recovery backup or selecting discard versus restore:

```text
OPERATION_RECORDED
BACKED_UP
MUTATING
VALIDATED
SYNCED
STAGED
COMMITTED
PUSHED
REMOTE_PARITY
ROLLED_BACK
```

Then define the only transaction-bearing recovery classifications:

```text
discard-only pre-mutation:
  BACKED_UP

restore-capable post-mutation:
  MUTATING
  VALIDATED
  SYNCED
  STAGED
```

Every other known state combined with `transaction/`, and every unknown state such as `BOGUS`, is invalid recovery evidence.

The smallest correction is:

* make `_load_operation_state` reject values outside the closed vocabulary with `PlanningApplyRestoreMismatch`;
* add a private recovery-state classifier that accepts only `BACKED_UP` or the four restore-capable states when `transaction/` is present;
* reject a transaction recovery path containing `commit.json` or `publication.json`, because commit-bearing operations belong to `_resume_publication`;
* perform this classification before `_load_transaction_backup`, `_apply_targets_match_snapshots`, `_restore_transaction`, or `_discard_pre_mutation_backup`.

Do not move unknown-state rejection into `record_planning_apply_operation` in a way that changes the result to `rejected/apply_output_rejected`. Invalid durable recovery evidence must retain the existing `recovery_required/restore_mismatch` result.  

### `exact_operation_order`

1. Preserve current top-level precedence:

   * valid `commit.json` path → `_resume_publication`;
   * otherwise, presence of `transaction/` → `_recover_interrupted_transaction`.
2. Read `state.json`.
3. Validate:

   * private/canonical JSON shape;
   * exact operation ID;
   * string state;
   * membership in the closed vocabulary.
4. Validate the transaction/state combination:

   * `BACKED_UP` → pre-mutation discard-only recovery;
   * `MUTATING`, `VALIDATED`, `SYNCED`, or `STAGED` → post-mutation restore recovery;
   * all other states → invalid;
   * `commit.json` or `publication.json` present in this path → invalid.
5. For unknown or invalid evidence:

   * return `recovery_required/restore_mismatch`;
   * do not load the backup;
   * do not compare targets;
   * do not restore;
   * do not discard;
   * do not rewrite `state.json`;
   * retain `transaction/` and the invalid state for diagnosis.
6. For valid `BACKED_UP`:

   * load and validate the backup;
   * compare branch, HEAD, canonical targets, and companion against `backup.files`;
   * preserve the S004 behavior:

     * actual drift → discard-only, `stale/apply_target_changed`, final state `OPERATION_RECORDED`;
     * no drift plus remote parity → discard-only, `rolled_back/planning_commit_failed`, final state `ROLLED_BACK`;
     * invalid backup, remote uncertainty, or cleanup failure → `recovery_required/restore_mismatch`.
   * never call `_restore_transaction`.
7. For valid `MUTATING` through `STAGED`:

   * preserve the existing branch/HEAD proof;
   * load the validated backup;
   * execute the existing exact restore;
   * confirm remote HEAD;
   * remove the transaction;
   * set `ROLLED_BACK`;
   * return `rolled_back/planning_commit_failed`.
8. No other state can reach either destructive helper.

### `tests`

1. **Canonical unknown-state test**

   * Produce a valid `BACKED_UP` transaction by crashing with a `BaseException` at `after_operation_recorded`.
   * Replace `state.json` with canonical, mode-`0600` evidence containing the correct operation ID and `"state":"BOGUS"`.
   * Patch each of these to fail the test if called:

     * `_load_transaction_backup`;
     * `_restore_transaction`;
     * `_discard_pre_mutation_backup`;
     * `_remove_transaction_backup`.
   * Make validation and sync runners fail if called.
   * Invoke the same operation again.

   Required result and postconditions:

   * `recovery_required/restore_mismatch`;
   * canonical documents unchanged;
   * companion absent;
   * decision artifact absent;
   * local and remote HEAD unchanged;
   * `transaction/` retained;
   * `state.json` still contains `BOGUS`;
   * no restore or discard helper called.

2. **Known but invalid state/transaction combinations**

   Using the same valid backup fixture, parameterize:

   ```text
   OPERATION_RECORDED
   COMMITTED
   PUSHED
   REMOTE_PARITY
   ROLLED_BACK
   ```

   Each must return `recovery_required/restore_mismatch`, retain evidence, and call neither restore nor discard. This verifies that closed vocabulary membership alone is insufficient; the state must also be valid with a surviving transaction.

3. Preserve the S004 `BACKED_UP` tests unchanged:

   * no-drift `after_operation_recorded` crash recovery → `rolled_back/planning_commit_failed`, transaction absent, state `ROLLED_BACK`;
   * drifted `BACKED_UP` cleanup retry → `stale/apply_target_changed`, concurrent bytes preserved, transaction absent, state `OPERATION_RECORDED`.

4. Preserve a representative valid post-mutation recovery, preferably `after_decision_write` or `after_index_stage`, proving that a `MUTATING` or `STAGED` transaction still restores exact canonical, companion, decision, index, and managed-state preimages and returns `rolled_back/planning_commit_failed`. 

### `contract_preservation`

* No public status or reason is added.
* Invalid recovery evidence uses the existing `recovery_required/restore_mismatch`.
* `PlanningApplyExecution`, its serialized output, and `PlanningApplyStatus` remain unchanged.
* Durable state is not part of `operation_core_bytes`; operation identity is unchanged.
* Valid S004 `BACKED_UP` drift and no-drift outcomes remain unchanged.
* Valid `MUTATING` through `STAGED` rollback remains unchanged.
* Commit/publication retry remains owned by `_resume_publication`.
* Post-hook F003 checks, canonical byte rules, companion handling, and git-bound behavior remain unchanged. 

### `residual_risk`

Closed vocabulary and state/transaction validation establish semantic admissibility, not cryptographic authenticity. A same-credential actor capable of rewriting private evidence could substitute another valid state such as `MUTATING`; the current ownership and permission model does not authenticate durable evidence against that actor.

A crash after durably writing `MUTATING` but before the first managed write remains conservatively restore-capable. That preserves the existing `MUTATING`-and-later rollback contract and may perform an unnecessary exact restore, but it no longer permits an unknown or invalid state to select that path.

`advisory_verdict: implementable`
