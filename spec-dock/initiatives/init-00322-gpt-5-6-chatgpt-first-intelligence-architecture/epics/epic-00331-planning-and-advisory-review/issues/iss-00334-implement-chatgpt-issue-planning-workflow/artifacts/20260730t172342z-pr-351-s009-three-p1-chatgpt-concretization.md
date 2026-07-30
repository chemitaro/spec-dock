# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b856d-9df4-83ee-a7b5-74204d786df7

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

Triage and concretize only the three P1 findings from fixed PR observation on exact HEAD be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2. Use the attached task brief, raw observation, sources, and tests; inspect the exact branch with @GitHub first; return only bounded developer work packets and no P2 proposals.

## Answer

# S009 bounded P1 developer work packets

**Validated source:** `chemitaro/spec-dock`, PR `#351`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, exact HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`. No default-branch substitution was used.
**Triage verdict:** all three observed families remain deterministic, merge-blocking P1 defects. None should be rejected or downgraded. Scope is limited to the three requested findings.

## Work packet 1 — `candidate-output-path-detachment`

**Disposition:** valid P1; independent repair unit.

### Deterministic defect

`build_and_publish_candidate()` derives `final_path` from the lexical guarded path, then performs staging and publication through the captured directory descriptor. After descriptor-bound publication and hash verification, it marks the operation published and returns the original lexical `final_path` without proving that the visible path still names the captured directory.

The existing test deterministically renames the captured output directory and replaces its visible pathname with a symlink during staged-file creation. Publication succeeds in the renamed original directory, while the returned path points through the replacement and contains no Candidate.

This breaks the required structured create-result handoff: the official workflow passes the exact Candidate path returned by create into review/apply.

### Smallest safe correction boundary

Change only the Candidate success boundary in `build_and_publish_candidate()`:

1. After published bytes/hash verification, staged-entry cleanup, and output-directory `fsync`, but before `published = True`, perform a final attachment proof.
2. The proof must establish:

   * the retained `output_descriptor` still has the guard’s device/inode;
   * `output_guard.path` can still be traversed component-by-component with no-follow semantics;
   * the directory reached through the visible pathname has the same device/inode;
   * the final filename still resolves, through that attached directory, to the same regular-file identity as `published_entry`.
3. On any failure, raise the existing `CandidateOutputRejected` or `CandidatePublicationFailed` boundary; do not add a public status, reason, or schema field.
4. Leave `published` false so the existing descriptor-relative `finally` cleanup removes the published entry from the captured original directory.
5. Do not introduce a pathname publication fallback or change deterministic ZIP bytes, identity derivation, collision behavior, or Linux/Darwin descriptor publication.

Reusable implementation pieces are `open_safe_directory_descriptor()`, `_open_guarded_output_directory()`, `_owned_entry_matches()`, `_entry_matches_identity()`, and the existing descriptor-relative cleanup.

### Deterministic Red/Green tests

In `tests/unit/infra/test_issue_planning_candidate.py`:

1. Replace `test_candidate_publish_remains_bound_after_captured_path_is_replaced` with `test_candidate_publish_rejects_detached_public_path_and_removes_published_entry`.

   * Preserve the existing deterministic injection point at private staged-file creation.
   * Expect `CandidateOutputRejected`.
   * Assert the renamed original directory contains neither the final Candidate nor a private staged entry.
   * Assert the replacement directory contains nothing.
   * Assert no `PublishedCandidate` success value is returned.

2. Parameterize the replacement shape:

   * visible path replaced by a symlink to another directory;
   * visible path replaced by a distinct ordinary directory.

   Both must reject and clean the descriptor-published Candidate. This prevents a symlink-only check from passing while ordinary directory replacement remains detached.

3. Retain the existing normal-success, collision, descriptor-source-identity, unprivileged Linux, and unsupported-platform tests unchanged.

### Required files

Provider authority:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`
* `tests/unit/infra/test_issue_planning_candidate.py`

Mechanical dogfood projection:

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`

The provider and dogfood source currently share blob `a0fa38be145f603c45a9c10b6f458a3e23aeea51`; preserve byte parity after projection.

---

## Work packet 2 — `canonical-write-ancestor-symlink-race`

**Disposition:** valid P1; serial apply repair unit, implemented before work packet 3.

### Deterministic defect

`_atomic_write_exact()` tests only `path.parent.is_symlink()` and `path.parent.is_dir()`, then calls pathname-based `tempfile.mkstemp()`, `Path.replace()`, and `os.open(parent)`. A renamed ancestor replaced by a symlink is followed before the final parent is inspected; the final resolved parent itself can be an ordinary directory outside the repository.

The same pathname authority is reused by rollback: `_restore_transaction()` restores the companion, all canonical documents, and the decision artifact through lexical paths. A post-check ancestor replacement can therefore redirect both forward mutation and rollback outside the repository.

This is a deterministic repository-boundary violation and remains P1 even when later Git or restore verification rejects the operation: an external write has already occurred.

### Smallest safe correction boundary

Introduce one private, transaction-specific repository target guard inside `issue_planning_apply.py`; do not add a general filesystem framework.

1. Before transaction snapshots or mutation:

   * open `repo_root` component-by-component with `O_DIRECTORY | O_NOFOLLOW`;
   * resolve each apply-owned repository-relative target parent from that descriptor;
   * retain parent descriptors, basename, and captured parent device/inode.
2. Mandatory guarded inventory:

   * three canonical document targets;
   * onboarding companion target;
   * Human decision artifact target;
   * repository-relative entries directly restored by this module during rollback.
3. Convert transaction-owned snapshot, staging, replacement, parity-read, unlink, and rollback operations for those entries to `dir_fd`-relative operations.
4. Every target open must use no-follow semantics and verify regular-file or expected-absence type.
5. Every temporary file must be created with a private unpredictable name, `O_CREAT | O_EXCL | O_NOFOLLOW`, in the retained parent descriptor; publication/replacement and directory `fsync` must use that same descriptor.
6. The live rollback path must reuse the already-held descriptors rather than reopening lexical paths.
7. Crash recovery must reopen from the repository descriptor with no-follow traversal and verify the recorded parent identities before writing. Identity proof may be added to the existing private transaction backup manifest; it is not a public schema. If identity cannot be re-established, return the existing `recovery_required/restore_mismatch` without writing.
8. No pathname fallback is permitted after descriptor capture.

Reusable patterns already exist in:

* Candidate `open_safe_directory_descriptor()` and `read_bounded_regular_file_at()` for component-wise no-follow traversal;
* apply evidence `_parent_fd()`, `_open_directory_at()`, `_write_private_atomic_at()`, `_unlink_at()`, and `_rmdir_at()` for descriptor-relative ownership;
* `FileSnapshot` and current exact-byte/mode restore assertions.

Do not change public statuses/reasons, Human binding, commit construction, push CAS, or managed sync policy.

### Deterministic Red/Green tests

In `tests/integration/test_issue_planning_apply.py`:

1. `test_canonical_replace_uses_captured_parent_after_ancestor_symlink_swap`

   * Build an external issue-directory mirror containing sentinel document bytes.
   * Let the transaction write the decision artifact normally.
   * At `after_decision_write`, rename the real issue directory and replace its lexical repository path with a symlink to the external mirror.
   * At `after_requirement_replace`, record the external requirement bytes and raise an injected failure.
   * **Red:** current code records Candidate replacement bytes in the external mirror.
   * **Green:** external sentinel bytes are unchanged; the replacement occurred only in the captured original directory.
   * Final result may be the existing `recovery_required/restore_mismatch`, because the repository pathname topology was externally altered and clean restore cannot be proven.
   * Local and remote HEAD must remain at the reviewed HEAD.

2. `test_rollback_uses_captured_parents_after_ancestor_symlink_swap`

   * At `after_decision_write`, perform the same ancestor swap and immediately raise.
   * Seed all external canonical files with distinct sentinels.
   * **Red:** current rollback overwrites external sentinels with captured repository preimages.
   * **Green:** every external sentinel remains byte-identical; no external decision artifact or private temporary file is created.
   * Expect existing `recovery_required/restore_mismatch`, with no commit or push.

In `tests/unit/infra/test_issue_planning_apply.py`:

3. `test_repository_target_parent_walk_rejects_symlink_component`

   * Replace an intermediate repository-relative component with a symlink.
   * Assert target guard construction rejects before any create, unlink, or replace call.

4. `test_descriptor_relative_atomic_write_survives_lexical_parent_replacement`

   * Capture a parent descriptor, rename that directory, replace its visible pathname, and invoke the private writer.
   * Assert bytes appear only under the captured directory and never under the replacement.

### Required files

Provider authority:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

Mechanical dogfood projection:

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

The provider and dogfood source currently share blob `5859b5e076c053e6306dc9b46cd069bdba8dbed1`; preserve byte parity after projection.

---

## Work packet 3 — `archive-preimage-revalidation`

**Disposition:** valid P1; serial apply repair unit built on work packet 2.

### Deterministic defect

The transaction captures and validates canonical preimages, persists its backup, and performs one additional `_apply_targets_match_snapshots()` check. It then durably writes `MUTATING` before any canonical replacement.

An edit injected while `_set_operation_state(..., "MUTATING")` runs occurs after the final global check. Each canonical file is then replaced unconditionally by `_atomic_write_exact()`, and final Candidate parity checks only the new bytes. The concurrent edit is lost and the operation can commit and publish successfully.

The accepted contract requires exact canonical target blobs to remain unchanged until apply and requires destination drift to be rejected without losing prior state.  Existing tests cover changes before the global post-backup check, but not changes after it.

### Smallest safe correction boundary

Extend the descriptor-anchored target primitive from work packet 2 with exact preimage compare-and-replace semantics.

For each existing canonical target:

1. Create and `fsync` the staged replacement in the retained parent descriptor.
2. Open the current target through that parent with `O_NOFOLLOW`, retain its device/inode, and do not trust its pathname.
3. Atomically exchange staged and target entries:

   * Linux: descriptor-relative `renameat2(..., RENAME_EXCHANGE)`;
   * Darwin: descriptor-relative `renameatx_np(..., RENAME_SWAP)`;
   * no non-atomic fallback.
4. Prove that the displaced entry is the same identity opened before exchange and that its complete `FileSnapshot`—existence, regular-file type, bytes, mode, and digest—equals the captured preimage.
5. On mismatch:

   * exchange the entries back;
   * preserve the concurrent file byte-for-byte;
   * remove only the owned staged replacement;
   * raise an internal target-drift signal mapped to existing `stale/apply_target_changed`.
6. On match, retain the new target, safely remove the displaced old entry, and `fsync` the parent.
7. Apply the same invariant to captured-absence destinations such as a not-yet-existing companion or decision artifact using atomic no-replace publication. A concurrently created entry must be preserved and classified as drift.

Rollback must be ownership-aware:

* Record internally which targets were successfully replaced by this attempt.
* On drift, reverse only those proven transaction-owned replacements.
* Never restore the preimage over the target whose compare-and-replace failed.
* Verify that all transaction-owned writes—including the decision artifact and any earlier canonical replacement—were removed or restored.
* When only externally drifted bytes remain, remove the transaction backup, return the durable state to `OPERATION_RECORDED`, and return existing `stale/apply_target_changed`.
* If ownership or reverse replacement cannot be proven, preserve unknown bytes and use existing `recovery_required/restore_mismatch`.

A new global recheck immediately before the loop is insufficient; comparison must be coupled to every individual replacement boundary.

### Deterministic Red/Green tests

In `tests/integration/test_issue_planning_apply.py`:

1. `test_archive_apply_preserves_edit_injected_during_mutating_state`

   * Wrap `_set_operation_state`.
   * Call the real implementation first; when state is `MUTATING`, write concurrent bytes to `design.md`.
   * **Red:** current implementation returns `ready/adoption_published`, overwrites the concurrent bytes, and advances local/remote HEAD.
   * **Green:** return `stale/apply_target_changed`; preserve concurrent `design.md`; restore any earlier requirement/decision mutation; leave companion absent; retain reviewed local/remote HEAD; remove the transaction backup; durable state is `OPERATION_RECORDED`.

2. `test_archive_apply_revalidates_each_canonical_replacement_boundary`

   * At `after_requirement_replace`, edit `design.md`.
   * This must fail even if a one-time global check after `MUTATING` would have passed.
   * Expect the same Green postconditions as test 1: requirement restored, design concurrent bytes preserved, plan unchanged, no decision/companion residue, no commit or push.

3. `test_archive_apply_preserves_companion_created_after_canonical_replacements`

   * At `after_plan_replace`, create the previously absent companion with concurrent bytes.
   * Atomic no-replace publication must reject the drift.
   * Restore the transaction-owned canonical and decision writes, preserve the concurrent companion, return `stale/apply_target_changed`, and keep local/remote HEAD unchanged.

In `tests/unit/infra/test_issue_planning_apply.py`:

4. Platform-backend argument tests equivalent to the existing Candidate FD-publication syscall tests:

   * prove the verified parent descriptors and names are passed to the Linux/Darwin exchange primitives;
   * prove unsupported/missing primitives fail closed.

5. `test_compare_replace_mismatch_exchanges_back_and_preserves_current_bytes`

   * Inject a completed in-place write before exchange validation.
   * Assert the target remains the concurrent version and the proposed replacement is not published.

6. `test_reverse_compare_replace_does_not_overwrite_unknown_postmutation_bytes`

   * After a transaction-owned replacement, substitute a third byte sequence.
   * Rollback must preserve it and raise restore mismatch rather than restoring the old snapshot.

### Required files

Use the same provider, dogfood, unit-test, and integration-test files listed in work packet 2. Do not change application-layer result schemas or add status/reason values.

---

## Combined repair and test order

1. Add all Red tests first and confirm each fails for the intended reason at exact HEAD.
2. Implement work packet 1 independently; run the Candidate unit suite.
3. Implement work packet 2 before work packet 3. It establishes the descriptor authority on which safe compare-and-replace must depend.
4. Run the new ancestor-symlink tests plus the existing apply output-guard, exact restore, precommit fault, interrupted recovery, and rollback suites.
5. Implement work packet 3 by extending the work-packet-2 primitive; do not create a second path-based writer.
6. Run:

   * `tests/unit/infra/test_issue_planning_candidate.py`
   * `tests/unit/infra/test_issue_planning_apply.py`
   * `tests/integration/test_issue_planning_apply.py`
   * existing application apply/retry tests
   * provider/dogfood byte-parity checks
   * required Provider CI, lint/type gates, validation, and full regression.
7. Mechanically project provider source into `spec-dock/scripts/...`; do not author the dogfood copies independently.

**Independence verdict:** the Candidate fix is fully independent. The two apply fixes are independently reviewable behavioral units but must be implemented serially because both own the canonical replacement/rollback primitive. The non-overlapping order is `canonical-write-ancestor-symlink-race` first, then `archive-preimage-revalidation`.

**Advisory verdict:** repair all three P1s before merge; no downgrade, rejection, public-contract expansion, or additional branch scope is justified.
