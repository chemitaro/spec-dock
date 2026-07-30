# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b8dc1-c018-83e8-8281-e88f68df893d

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

Concretize only the five P1 race and crash-recovery findings in the attached S010 task brief. Inspect the exact current GitHub branch first, then treat the attached provider sources and tests as the uncommitted S009 state. Return only minimal developer work packets and tests; no P2 proposals or redesign.

## Answer

# S010 bounded P1 developer work packets

**Repository gate:** GitHub connector inspection confirmed `chemitaro/spec-dock:iss-00334-implement-chatgpt-issue-planning-workflow` is exactly `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`; `main` was not inspected or substituted. The attached provider sources and tests are treated as the authoritative uncommitted S009 state. All five findings are **confirmed P1**.

## WP1 — Candidate rejection cleanup must quarantine before unlink

**Disposition:** Confirm P1.

### Deterministic failure sequence

1. Candidate publication succeeds and `published_entry.descriptor` retains inode `P`.
2. Final attachment verification rejects, leaving `published == False`.
3. The `finally` block calls `_owned_entry_matches(...)`, which returns true for the logical Candidate name.
4. Before the following `unlink`, another actor renames `P` away and installs unknown file `U` at the logical Candidate name.
5. The unconditional descriptor-relative `unlink(name)` deletes `U`, not `P`.

The check and deletion are separate namespace operations in both the remote baseline and attached S009 source.

### Smallest safe correction

Add one **candidate-local** private cleanup primitive; do not create a shared filesystem framework.

* Under the already-captured output-directory FD, create and open an unpredictable `0700` cleanup directory; verify directory type, owner, mode, device, and inode.
* Move the logical Candidate name into that directory with descriptor-relative native **no-replace rename**:

  * Linux: `renameat2(..., RENAME_NOREPLACE)`.
  * Darwin: `renameatx_np(..., RENAME_EXCL)`.
* Inspect the moved entry against `published_entry.descriptor`.

  * If it is `P`, unlink it only inside the private cleanup directory, fsync the private directory and output directory, then remove the cleanup directory.
  * If it is not `P`, move it back with no-replace semantics when possible. If the original name is now occupied, retain the unknown bytes in the private directory and fail closed; never unlink them.
* Never call `unlink` on the public logical filename after a prior identity check.
* Missing/unsupported native primitives must preserve entries and fail closed. Do not add pathname fallback.
* Candidate ZIP construction, bytes, identity derivation, collision semantics, and success result remain unchanged.

### Red/Green tests

`tests/unit/infra/test_issue_planning_candidate.py`

1. `test_candidate_rejection_cleanup_post_match_swap_preserves_unknown_final`

   * Force `_verify_published_candidate_attachment()` to reject after publication.
   * Wrap `_owned_entry_matches()` so that, after it has obtained a true result for `published_entry`, it renames the owned Candidate aside and creates sentinel `U` at the logical name before returning.
   * **Red:** current cleanup unlinks `U`.
   * **Green:** rejection is still raised; the logical name contains byte-exact `U`; no `PublishedCandidate` is returned; cleanup removes only an entry proven to be `P`.

2. `test_candidate_cleanup_no_replace_backend_arguments`

   * Prove distinct source/destination directory FDs, names, and Linux/Darwin no-replace flags reach the native call.

3. `test_candidate_cleanup_missing_native_primitive_fails_closed`

   * Assert no fallback rename/unlink occurs and sentinel bytes remain.

**Files:** provider Candidate source and unit test only; mechanically project provider source to `spec-dock/scripts/...`.

---

## WP2 — Bind staged ownership to the apply exchange

**Disposition:** Confirm P1.

### Deterministic failure sequence

1. `compare_replace()` creates staged inode `S`, fsyncs it, and captures its identity.
2. An actor renames the staged name away and places unknown file `U` at that name.
3. `_exchange_entries_at(temporary, target)` exchanges `U` with preimage `C`.
4. The target now names `U`; the temporary name contains `C`.
5. The displaced-entry check succeeds because `C` is the expected preimage.
6. Current code unlinks the temporary name, deleting `C`.
7. Only afterward does target verification discover that the target is not `S`; recovery now has neither the canonical preimage nor a valid recorded mutation.

### Smallest safe correction

Extend `_RepositoryTargetGuard`; keep the implementation private and transaction-specific.

* Create an unpredictable, descriptor-opened `0700` workspace beneath the captured target parent.
* Create and fsync the staged file **inside that workspace**, rather than at a peer-visible parent name.
* Generalize `_exchange_entries_at` to accept two directory FDs:
  `workspace_fd/staged_name ↔ target.parent_fd/target.name`.
* After exchange, and before deleting anything, prove:

  * target name identifies staged inode `S` and exact replacement snapshot;
  * workspace slot identifies the opened preimage inode and exact expected snapshot.
* On either mismatch:

  * do not unlink either entry;
  * exchange back only while both post-exchange identities remain proven;
  * fsync both directories;
  * otherwise retain both entries and raise `PlanningApplyRestoreMismatch`.
* Delete the displaced preimage only inside the verified private workspace.
* Do not set the internal publication-success flag until both exchange postconditions hold.
* Unsupported exchange primitives remain fail-closed.

### Red/Green tests

`tests/unit/infra/test_issue_planning_apply.py`

1. `test_compare_replace_staged_name_swap_before_exchange_preserves_unknown_and_preimage`

   * Wrap `_exchange_entries_at`.
   * Immediately before the real syscall, rename the staged slot aside, create `U` at that slot, then perform the exchange.
   * **Red:** `U` becomes canonical and `C` is deleted.
   * **Green:** `C` is not deleted; `U` remains byte-exact; no replacement is accepted; ambiguity raises `PlanningApplyRestoreMismatch`.

2. Update the Linux/Darwin argument tests to prove the two distinct directory FDs and swap flag are passed exactly.

`tests/integration/test_issue_planning_apply.py`

3. `test_apply_staged_name_replacement_before_exchange_preserves_repository_preimage`

   * Inject the swap for the first canonical replacement, not the absent decision write.
   * Expect `recovery_required/restore_mismatch`.
   * Assert canonical preimage bytes remain available, unknown bytes remain available, no commit/push occurs, and transaction evidence is retained.

Existing exchange-back and unknown-postmutation tests remain and should continue to pass.

---

## WP3 — Make the mutation ledger write-ahead

**Disposition:** Confirm P1.

### Deterministic failure sequence

1. `target_guard.compare_replace()` completes replacement verification and parent fsync.
2. It returns `_TargetMutation`.
3. Before `_apply_guarded_mutation()` appends the mutation and calls `_persist_target_mutations()`, the process crashes.
4. Durable state is `MUTATING`, but the ledger still contains only earlier entries.
5. Recovery cannot associate the newly replaced target with the transaction and cannot restore it.

The current persistence occurs strictly after `compare_replace()` returns.

### Smallest safe correction

Use the existing private `mutation-ledger.json`; no public schema changes.

* Split the guarded mutation internally into **prepare** and **publish**, while retaining the current outer transaction flow.
* Once the staged file is fsynced and its identity is known—but before any target namespace mutation—append and durably persist a private ledger entry containing at least:

  * target path;
  * private phase, initially `prepared`;
  * workspace name and captured workspace device/inode;
  * staged slot name;
  * staged device/inode;
  * replacement mode and SHA-256.
* Then perform exchange/no-replace publication and fsync all changed directories.
* Atomically update the entry to `published`.
* Recovery of a `prepared` entry must classify descriptor-bound state:

  * target still equals `before`, workspace contains staged `after`: publication did not occur; remove the owned workspace and consume the entry;
  * target equals recorded `after`: publication occurred despite the stale phase; restore it;
  * any other combination: preserve all bytes and return `restore_mismatch`.
* The ledger remains private operation evidence; do not add public state, reason, or output fields.

### Red/Green tests

`tests/unit/infra/test_issue_planning_apply.py`

1. `test_mutation_intent_is_durable_before_namespace_publication`

   * At the exchange wrapper, read `mutation-ledger.json` before invoking the native syscall.
   * **Red:** no entry exists.
   * **Green:** a canonical, private `prepared` entry with the staged/workspace identity already exists.

`tests/integration/test_issue_planning_apply.py`

2. `test_crash_after_compare_replace_before_outer_return_recovers_recorded_mutation`

   * Wrap `_RepositoryTargetGuard.compare_replace()`.
   * Call the real method for `requirement.md`, then raise a `BaseException` before returning to `_apply_guarded_mutation()`.
   * **Red:** target is replaced but absent from the ledger; retry returns `recovery_required`.
   * **Green:** the write-ahead entry identifies the mutation; retry restores documents, decision, companion absence, index, and managed state; returns `rolled_back/planning_commit_failed`; local and remote HEAD remain unchanged.

---

## WP4 — Drain rollback ledger durably and make restore idempotent

**Disposition:** Confirm P1.

### Deterministic failure sequence

1. The ledger contains several mutations.
2. Rollback restores the last mutation and fsyncs its parent.
3. The process crashes before rollback completes.
4. The durable ledger still contains every original entry.
5. On retry, recovery revisits the restored entry.
6. `restore()` requires the target to have the recorded `after` inode/snapshot; it now has `before`, so recovery stops with `transaction-owned target changed`.

Current rollback iterates the full in-memory list without persisting per-entry progress.

### Smallest safe correction

* Make `_RepositoryTargetGuard.restore()` idempotent:

  * exact recorded `after` state: perform restore;
  * exact `before` state, including exact absence: return an internal “already restored” success without modifying it;
  * anything else: preserve it and raise `PlanningApplyRestoreMismatch`.
* Pass `handle` and `operation` into rollback orchestration.
* After each successful restore or already-restored classification:

  1. fsync the affected target directory;
  2. remove that entry from the in-memory outstanding list;
  3. atomically rewrite and fsync `mutation-ledger.json`;
  4. only then process the next entry.
* Never remove an entry from the ledger before its target is restored.
* Keep the transaction backup until all target entries, index restoration, managed-state restoration, and final postconditions succeed.

### Red/Green tests

`tests/unit/infra/test_issue_planning_apply.py`

1. `test_target_restore_accepts_exact_already_restored_preimage`

   * Replace an existing target, restore it, then call restore again with the same mutation.
   * **Red:** second call raises.
   * **Green:** second call is a no-op; bytes and mode remain exact.

2. `test_target_restore_accepts_exact_already_restored_absence`

   * Create an absent-state mutation, restore absence, then call restore again.
   * The second call must be a no-op.

`tests/integration/test_issue_planning_apply.py`

3. `test_recovery_retries_after_crash_between_target_restore_and_ledger_shrink`

   * First create an interrupted transaction with several recorded mutations.
   * During first recovery, wrap `target_guard.restore()` so the first real restore completes and then raises `BaseException` before progress persistence.
   * **Red:** next recovery fails on the already-restored entry.
   * **Green:** next recovery classifies it as already restored, consumes it, restores the remainder, and completes rollback.

4. `test_recovery_resumes_from_durable_shortened_mutation_ledger`

   * Raise `BaseException` immediately after the first successful ledger shrink.
   * Assert the on-disk ledger has one fewer entry.
   * Retry must process only the remaining entries and complete exact rollback.

The existing interrupted-precommit recovery test supplies the baseline setup and final assertions.

---

## WP5 — Remove absent-state targets through ownership-safe quarantine

**Disposition:** Confirm P1.

### Deterministic failure sequence

1. A mutation’s preimage is absent; the transaction-created target has inode `A`.
2. `restore()` stats and snapshots the target and verifies `A`.
3. An actor renames `A` away and creates unknown file `U` at the same name.
4. The following unconditional `unlink(target.name)` deletes `U`.
5. The subsequent absence check succeeds, falsely reporting successful rollback.

This applies directly to transaction-created decision and companion artifacts.

### Smallest safe correction

Reuse the private workspace/quarantine primitive from WP2.

* Never raw-unlink the canonical target name.
* Before removal, durably record a rollback/workspace phase in the existing mutation entry.
* Move the target name into a fresh slot in the verified private workspace using descriptor-relative native no-replace rename.
* Inspect the moved entry:

  * if it is exactly recorded inode/snapshot `A`, the canonical name is safely absent; unlink `A` only inside the workspace and fsync both directories;
  * if it is `U` or any other entry, move it back with no-replace semantics when possible; otherwise retain it in the workspace and return `restore_mismatch`.
* An already-absent canonical name is successful only when the idempotence rules from WP4 prove the `before` state.
* Missing native primitives or workspace-identity failure must retain bytes and fail closed.

### Red/Green tests

`tests/unit/infra/test_issue_planning_apply.py`

1. `test_absent_restore_post_verification_swap_preserves_unknown_file`

   * Create a mutation whose `before.existed` is false.
   * Wrap `guard.snapshot()` so it obtains the exact `after` snapshot, then renames `A` aside and creates sentinel `U` before returning.
   * **Red:** current raw unlink deletes `U`.
   * **Green:** `U` remains byte-exact; the method raises `PlanningApplyRestoreMismatch`; `A` is not confused with `U`.

`tests/integration/test_issue_planning_apply.py`

2. Parameterize `test_rollback_absent_artifact_race_preserves_concurrent_bytes` over:

   * Human decision artifact;
   * onboarding companion.
   * Trigger ordinary precommit rollback after the selected artifact exists.
   * Inject the post-verification replacement at its removal boundary.
   * Expect `recovery_required/restore_mismatch`; assert sentinel bytes survive, no commit/push occurs, reviewed local/remote HEAD remains unchanged, and transaction evidence remains available.

---

## Safe implementation order

1. Add all Red tests.
2. Implement WP1 independently in Candidate publication cleanup.
3. Implement the apply-local private workspace and cross-directory native operations required by WP2.
4. Route absent-state removal through that workspace for WP5.
5. Change the private ledger to write-ahead preparation/publication phases for WP3.
6. Add idempotent restore and per-entry durable ledger draining for WP4.
7. Run the Candidate unit suite, apply unit suite, apply integration suite, existing application retry tests, unsupported-platform tests, and provider/dogfood byte-parity checks.
8. Modify provider authority first and mechanically project only the two provider sources to their `spec-dock/scripts/...` counterparts.
