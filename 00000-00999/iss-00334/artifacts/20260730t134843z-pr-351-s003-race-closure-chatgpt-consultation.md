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

Use the attached prompt as the complete defect-only task brief. You MUST inspect the exact current GitHub branch and confirm HEAD 6c9302ab08c7f352e85a199b65bdeb522376171c; if unavailable, return repository access failed and DO NOT inspect or substitute the default branch. Then use the attached uncommitted source/test files as the S002 delta. Return only the requested bounded repair guidance.

## Answer

## F002/U002

### `minimal_strategy`

Replace the stage tuple with a private ownership record containing the stage name, still-open directory descriptor, and captured `(st_dev, st_ino)`. After `mkdirat`, capture the new entry with parent-descriptor-relative, non-following `stat`; open it with `O_DIRECTORY | O_NOFOLLOW`; then require the pre-open stat, `fstat(stage_fd)`, and a post-open stat of the parent entry to identify the same directory. Merely proving that the opened object is a directory is insufficient.

Likewise, after creating the staged ZIP with `O_CREAT | O_EXCL`, retain its descriptor and captured `(st_dev, st_ino)`. All ZIP construction, `fsync`, bounded reading, validation, and identity derivation remain descriptor-bound. Immediately before no-replace publication, require the staged filename beneath the stage descriptor to identify that same open regular file; otherwise fail closed without publishing any replacement entry.

Use one bounded identity helper for stage creation, publication eligibility, and cleanup. Public Candidate schema, deterministic ZIP generation, Candidate identity derivation, and the Linux/Darwin no-replace helpers remain unchanged. 

### `operation_order`

1. Open and verify the guarded output-directory descriptor.
2. Check the final Candidate name relative to that descriptor.
3. `mkdirat` the random private stage name.
4. Capture the parent-visible stage identity before opening it.
5. Open the stage by name with `O_DIRECTORY | O_NOFOLLOW`.
6. Compare pre-open identity, opened descriptor identity, and post-open parent-visible identity. On any mismatch, stop before creating the ZIP.
7. Create the ZIP with `O_EXCL` relative to the verified stage descriptor; capture its descriptor identity.
8. Write, flush, `fsync`, reread, validate, and derive Candidate identity exclusively through that descriptor.
9. Recheck that the staged filename still denotes the captured ZIP object.
10. Perform the existing descriptor-relative atomic no-replace publication.
11. Keep both descriptors open until identity-checked cleanup is complete.

### `failure_cleanup`

* For an unpublished ZIP, call `unlink` only when the staged name still resolves, without following links, to the exact `(st_dev, st_ino)` held by the staged-file descriptor. A missing or mismatched name is preserved.
* Close the staged-file descriptor only after that decision.
* Remove the stage directory only when the output-directory entry still resolves to the exact object held by the stage descriptor and the directory is empty. A mismatch, rename, replacement, or nonempty directory is intentionally left in place.
* Close the stage descriptor only after the directory-removal decision.
* Apply the same ownership check inside `_create_private_stage_directory` when opening the just-created directory fails. Its current unconditional `rmdir` error path must not remove a replacement.
* Do not use recursive deletion, search for a renamed stage, delete based only on prefix/permissions/owner, or remove an alternate entry. Leakage is preferable to deleting third-party state.

### `tests`

1. **Replacement between `mkdirat` and `openat`:** intercept the stage-directory `os.open`; rename the newly created directory aside and create a replacement at the original name before the real open. Expect `CandidateBuildFailed`, no final Candidate, no ZIP written into the replacement, and the replacement’s sentinel state preserved.
2. **Stage replacement immediately before cleanup:** after successful ZIP publication—or immediately before a forced publication failure—rename the exact stage directory aside and create an empty replacement at its original name. Expect the final Candidate result appropriate to the injected path, but the replacement directory must remain present and untouched.
3. **Staged-ZIP replacement before publication/failure cleanup:** after ZIP validation, rename the owned ZIP entry within the exact stage descriptor and create a sentinel file under the logical filename. Expect publication to fail closed; cleanup must preserve the sentinel and must not claim or remove the renamed file.
4. Retain the existing reproducibility, collision, unsupported-platform, and unowned staged-collision tests; the existing collision-before-create test does not substitute for the two post-creation identity races. 

### `residual_risk`

The currently used Python APIs remove directories and named files through a parent descriptor plus a name; they do not provide an fd-only stage-directory removal operation. Therefore, the implementation can perform an immediate identity check before `unlink`/`rmdir`, fail closed on every observed replacement, and retain the descriptors throughout cleanup, but it cannot prove safety against a hostile same-credential process replacing the name in the final check-to-removal syscall interval.

Local acceptance must confirm that the supported threat model treats the immediate identity handshake and final identity check as sufficient. If an adversarial actor is explicitly allowed to win that final syscall-sized interval, literal F002 closure is blocked under the current portable Linux/Darwin API design.

---

## F003/U003

### `minimal_strategy`

Extract one private preimage-comparison helper and call it after `fault_hook("after_operation_recorded")`, but before `mutation_started`, `MUTATING`, or the decision-artifact write.

The helper should recheck:

* exact branch and HEAD;
* every canonical target against its already validated `FileSnapshot`, including existence, bytes, and mode;
* the companion against its already validated snapshot, thereby detecting both modification and absent-to-present creation.

Comparing with the captured snapshots is sufficient because those snapshots have already been proven against the operation’s canonical document bytes/blob OIDs and the expected-HEAD companion preimage. Any mismatch, non-regular replacement, symlink, disappearance, or read failure at this boundary is `stale/apply_target_changed`.

Give the existing `BACKED_UP` state a strict internal meaning: the durable backup exists, but no managed repository mutation has begun. Recovery from a surviving `BACKED_UP` transaction must discard the backup rather than restore it. `MUTATING` and later states retain the existing rollback behavior. This is an internal state-semantics correction, not a public result or operation-identity change. 

### `operation_order`

1. Perform the current HEAD, branch, canonical, companion, index, managed-state, and decision-artifact preflight.
2. Persist the transaction backup.
3. Set state to `BACKED_UP`.
4. Invoke `fault_hook("after_operation_recorded")`.
5. Immediately resnapshot and compare the canonical and companion targets, and recheck branch/HEAD.
6. On drift:

   * leave `mutation_started` false;
   * do not set `MUTATING`;
   * do not write the decision artifact or any canonical/companion bytes;
   * remove the transaction backup;
   * reset state to `OPERATION_RECORDED`;
   * return `stale/apply_target_changed`.
7. On a match:

   * durably set state to `MUTATING`;
   * set `mutation_started = True`;
   * begin the existing decision, canonical, companion, validation, sync, commit, and publication sequence.
8. Failures after the `MUTATING` boundary continue through the existing exact rollback path.

### `failure_cleanup`

The stale-before-mutation path must never call `_restore_transaction`; its snapshots predate the concurrent edit and restoring them would destroy the very bytes that triggered the stale result.

Remove the transaction backup before resetting the state so a normal retry cannot interpret it as an interrupted mutating transaction. After removal, synchronize the operation directory using the same durability standard already used for private evidence, then atomically reset `state.json` to `OPERATION_RECORDED`.

If backup removal or state reconciliation fails, do not return a successful stale cleanup result. Return the existing `recovery_required/restore_mismatch` outcome. Recovery must inspect the durable state: a `BACKED_UP` transaction is pre-mutation and therefore discard-only; it must never restore canonical, companion, decision, managed-state, or index snapshots. `MUTATING` or later retains current restoration semantics.

Operation metadata and attempt evidence may remain. The transaction directory and any state implying active mutation must not remain after a successfully returned stale result.

### `tests`

1. **Canonical edit at the required boundary:** in `after_operation_recorded`, replace one canonical document with distinctive concurrent bytes. `validation_runner` and `sync_runner` must fail the test if invoked. Expect:

   * `stale/apply_target_changed`;
   * concurrent bytes preserved exactly;
   * other canonical files unchanged;
   * no decision artifact;
   * no companion;
   * unchanged local/remote HEAD;
   * no transaction directory;
   * state reset to `OPERATION_RECORDED`.
2. **Companion creation at the required boundary:** create the previously absent companion with distinctive concurrent bytes in the same hook. Expect the same stale result and cleanup invariants, with the concurrent companion preserved exactly.
3. **Pre-mutation cleanup interruption:** inject failure while removing the backup after hook-boundary drift. Expect `recovery_required/restore_mismatch`; a subsequent recovery of the surviving `BACKED_UP` transaction must discard evidence without restoring over the concurrent bytes.
4. Retain one representative post-mutation checkpoint test, such as failure after a canonical replacement, to prove that `MUTATING` and later still produce the existing `rolled_back` result and exact baseline restoration. The current checkpoint-oriented integration tests provide the appropriate fixture pattern.
5. Tests that mutate through `snapshot_git_index` remain useful earlier-window coverage but do not count as closure; both new primary tests must inject through the exact `after_operation_recorded` hook specified by U003. 

### `residual_risk`

This closes the specified deterministic boundary between `after_operation_recorded` and the first managed write. It is not a general multi-file locking or compare-and-swap mechanism: an external process that modifies a target after the final comparison may still race a later write. Eliminating every such interval would require a broader repository mutation protocol and is outside this defect-only repair.

`advisory_verdict: implementable`

`assumptions_to_verify_locally:`

* The GitHub current branch is confirmed at exact HEAD `6c9302ab08c7f352e85a199b65bdeb522376171c`.
* Linux and Darwin runners provide the currently assumed `dir_fd`, `O_DIRECTORY`, `O_NOFOLLOW`, inode/device identity, and descriptor-relative no-replace rename behavior.
* F002’s accepted threat model excludes an adversarial same-credential replacement inside the final identity-check-to-removal syscall interval.
* No external consumer assigns meaning to `BACKED_UP` beyond the repository’s apply implementation, so making it a strict “no managed mutation yet” boundary is compatible.
* The provider and dogfood projection copies receive byte-identical source changes and the focused tests run against the provider source.
