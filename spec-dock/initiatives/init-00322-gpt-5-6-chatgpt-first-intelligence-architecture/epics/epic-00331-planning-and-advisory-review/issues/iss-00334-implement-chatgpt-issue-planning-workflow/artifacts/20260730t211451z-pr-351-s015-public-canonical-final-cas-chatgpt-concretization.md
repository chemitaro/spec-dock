# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6bbbd9-ed54-83e8-acbf-e988425464d4

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

Use the attached S015 task brief. Inspect the exact GitHub branch and attached uncommitted source/tests, then concretize only the two public/canonical pre-boundary CAS P1 findings.

## Answer

## Verdict

GitHub access succeeded. PR #351 is open with head branch `iss-00334-implement-chatgpt-issue-planning-workflow` at pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`, based on `main`.  The attached provider sources and tests were then treated as the authoritative uncommitted S013 overlay, as required by the S015 brief.

**Both findings are confirmed P1.**

They concern ordinary public/canonical pathname replacement before ownership is established. They do not require adopting the rejected same-UID private-namespace threat model or adding retained-storage architecture.

---

## WP1 — Pre-bind Candidate ownership before public publication

**Disposition:** Confirm P1.

The pushed implementation already shows the critical sequence: publish to the logical pathname, then open that pathname and infer `published_entry` ownership from whatever object was opened.  The attached S013 implementation adds safer rejection cleanup, but still performs the same publication-then-open sequence and subsequently passes the captured entry to cleanup.

### Deterministic race

Let:

* `S` be the verified staged inode.
* `P` be the inode actually created by publication.
* `U` be an unrelated concurrent replacement at the final name.

Sequence:

1. `_publish_verified_fd_no_replace_at()` succeeds.

   * Linux: the final name hard-links `S`, so `P == S`.
   * Darwin: `fclonefileat()` creates a clone, so `P` may differ from `S`.
2. Before `_open_owned_regular_file(final_name)`, another process atomically moves or deletes `P` and installs regular inode `U` at the final name.
3. `_open_owned_regular_file()` captures `U` as `published_entry`.
4. A byte mismatch, forced attachment rejection, or later failure enters rejection cleanup.
5. Because both the descriptor and pathname now identify `U`, `_owned_entry_matches()` treats `U` as owned.
6. Cleanup moves and unlinks `U`.

This is concurrent-data destruction. A same-byte `U` is the strongest reproduction: digest verification succeeds, demonstrating that byte equality cannot establish inode ownership.

### Smallest platform-correct correction

Change the private helper contract to:

```python
def _publish_verified_fd_no_replace_at(...) -> _OwnedEntry:
    ...
```

`build_and_publish_candidate()` must assign that returned entry directly:

```python
published_entry = _publish_verified_fd_no_replace_at(...)
```

It must no longer reopen the public final pathname to establish ownership.

#### Linux rule

Before `linkat`:

1. Duplicate the verified staged descriptor.
2. `fstat` the duplicate and construct the final-named `_OwnedEntry`.
3. Perform the exclusive hard-link publication.
4. Return the preconstructed entry.

All potentially failing descriptor acquisition and validation must occur before `linkat`. After successful publication, returning the already-bound token must be the next non-cleanup action.

The returned identity is the staged identity because Linux hard-link publication preserves the inode.

#### Darwin rule

The clone inode is not knowable from the staged descriptor, so do not clone directly into the public final name.

1. Generate an unpredictable private capture name under the already-captured output directory.
2. `fclonefileat()` the verified staged descriptor into that private name.
3. Open the private clone and record its actual descriptor/device/inode.
4. Preconstruct an `_OwnedEntry` whose logical name is the final filename but whose descriptor and identity are those of the private clone.
5. Atomically rename the private clone to the final name using descriptor-relative no-replace rename.
6. Return the pre-bound entry.

If final-name collision or another pre-rename failure occurs, remove only the private clone after proving its captured identity. Never unlink the public final name.

This relies only on the existing private-name assumption accepted by D-20260730-S014-SCOPE; it introduces no retained-storage policy.

#### Caller and cleanup rules

After helper return:

1. Read and verify bytes through `published_entry.descriptor`.
2. Fsync the output directory.
3. Verify the final attachment against the pre-bound identity.
4. Mark publication successful only after that verification.
5. On failure, pass the same pre-bound entry to `_cleanup_rejected_published_candidate()`.

If `U` has replaced the final path, the final path no longer matches `P`; cleanup therefore returns without touching `U`.

### Exact Red/Green tests

Provider test path: `tests/unit/infra/test_issue_planning_candidate.py`. The branch confirms that this test module loads the provider runtime from `src/spec_dock/assets/...`.

#### 1. `test_candidate_post_publication_pre_capture_same_bytes_replacement_is_preserved`

* Wrap the real `_publish_verified_fd_no_replace_at()`.
* After the real publication succeeds:

  * rename the published final entry to `published-aside`;
  * create a new regular file `U` at the final name with byte-identical Candidate ZIP contents;
  * record that `U` has a different inode.
* Force `_verify_published_candidate_attachment()` to reject.
* Expect `CandidateOutputRejected`.
* Assert:

  * the final pathname still identifies `U`;
  * `U` remains byte-exact;
  * `U` has not been moved into or deleted from a cleanup directory;
  * `published-aside` remains the original `P`;
  * no `PublishedCandidate` is returned.

**Red:** current code opens `U`, records it as `published_entry`, and cleanup deletes it.

**Green:** the helper returns the pre-bound `P`; cleanup sees that the final path is `U` and preserves it.

#### 2. `test_candidate_publication_entry_binding_covers_linux_link_and_darwin_clone`

Parameterize or split into two tests:

* Linux:

  * assert the returned entry identity equals the staged identity and the final pathname identity.
* Simulated Darwin clone:

  * fake `fclonefileat` with a distinct-inode copy into the private capture name;
  * fake descriptor-relative no-replace rename;
  * assert the returned entry identity differs from the staged identity but exactly matches the final pathname.

Keep the existing native syscall argument, collision, unsupported-platform, and unprivileged Linux publication tests green.

### Allowed files

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`
* `tests/unit/infra/test_issue_planning_candidate.py`
* Mechanical byte projection only:

  * `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`

No domain, application, public contract, status, evidence schema, or Oracle configuration changes.

---

## WP2 — Exchange back the actual canonical attachment on CAS miss

**Disposition:** Confirm P1.

In attached S013, `compare_replace()` opens the canonical target and records inode `A`, persists the prepared mutation, and then exchanges the staged inode with the pathname. After exchange, rollback is attempted only when the displaced inode still equals opened inode `A`. An atomic editor replacement produces a different displaced inode, so the code skips exchange-back and raises with the transaction replacement still attached to the canonical pathname.

### Deterministic race

Let:

* `A` be the expected canonical inode opened by `current_fd`.
* `B` be a normal editor’s newly created replacement inode.
* `S` be the transaction’s staged replacement inode.

Sequence:

1. `compare_replace()` opens canonical target `A`.
2. A normal editor writes temporary inode `B` and atomically replaces the canonical pathname with `B`.
3. `_exchange_entries_at()` exchanges `S` with the current pathname.
4. The canonical pathname now identifies `S`.
5. The private workspace slot now contains `B`.
6. `target_is_staged` is true.
7. `displaced_is_opened` is false because `B != A`.
8. Current mismatch handling does not exchange back because it requires both predicates.
9. It raises `PlanningApplyRestoreMismatch`, leaving:

   * unauthorized transaction bytes `S` at the canonical pathname;
   * actual displaced attachment `B` in the workspace;
   * a prepared ledger entry that records `A`, not `B`.

Recovery cannot classify that state through the existing prepared-entry rules.

### Smallest correction

Treat the private workspace entry produced by the atomic exchange as the authoritative **actual displaced canonical attachment**, even when it does not equal the previously opened inode.

No mutation-ledger schema or public status change is required.

### Exchange-back rules

| Post-exchange state                                                                                        | Required action                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Canonical target is exact staged inode `S`, and displaced entry is exact opened inode/snapshot `A`         | Normal successful publication path.                                                                                                    |
| Canonical target is still staged inode `S`, but displaced identity or snapshot differs from `A`/`expected` | CAS miss. Exchange the actual displaced entry back, clean only exact `S`, discard the prepared record, then raise `_ApplyTargetDrift`. |
| Canonical target no longer identifies `S`                                                                  | Do not exchange automatically. Preserve all entries and raise `PlanningApplyRestoreMismatch`.                                          |
| Workspace slot no longer identifies the just-observed displaced entry                                      | Do not exchange or unlink. Preserve evidence and raise `PlanningApplyRestoreMismatch`.                                                 |
| Exchange-back postconditions cannot be proved                                                              | Do not unlink or discard evidence; raise `PlanningApplyRestoreMismatch`.                                                               |

For the CAS-miss path:

1. Capture displaced identity `D` and its exact snapshot from the private workspace.
2. Re-prove immediately before exchange-back:

   * canonical target still identifies `S`;
   * workspace slot still identifies `D`.
3. Exchange `D` back to the canonical pathname.
4. Fsync both the workspace and canonical parent directories.
5. Re-prove:

   * canonical target identifies `D` and has the captured displaced snapshot;
   * workspace slot identifies `S`.
6. Delete the workspace entry only when it is still `S` and has the exact transaction replacement snapshot.
7. Fsync and remove the empty workspace.
8. Invoke `discard(prepared)` so the durable prepared mutation is removed.
9. Raise `_ApplyTargetDrift(relative)`.

The permission to exchange back must depend on ownership of the **canonical side** (`target == S`) and continuity of the captured workspace attachment (`workspace == D`). It must not depend on `D == A`; that comparison determines success versus drift, not whether the actual displaced attachment should be restored.

A byte-identical `B` with a different inode must also be classified as drift and restored. Otherwise the compare-and-swap remains attachment-blind.

### Exact Red/Green tests

Provider unit path: `tests/unit/infra/test_issue_planning_apply.py`.
Integration path: `tests/integration/test_issue_planning_apply.py`.

#### 1. `test_compare_replace_atomic_editor_swap_after_open_restores_actual_attachment`

* Create canonical inode `A` and capture `expected`.
* Wrap `_exchange_entries_at()`.
* On its first call, before invoking the real exchange:

  * create temporary inode `B`;
  * atomically replace the canonical pathname with `B`;
  * record `B`’s identity.
* Run `compare_replace()` with `prepare` and `discard` observers.
* Parameterize `B` as:

  * byte-different from `expected`;
  * byte-identical to `expected` but inode-distinct.
* Expect `_ApplyTargetDrift`.
* Assert:

  * the exchange primitive was invoked twice;
  * the canonical pathname identifies the exact recorded `B`;
  * the canonical bytes equal `B`;
  * transaction replacement `S` is not canonical;
  * the private workspace is gone;
  * `discard` received the prepared mutation exactly once.

**Red:** current code raises `PlanningApplyRestoreMismatch`, leaves `S` canonical, and retains the prepared workspace.

**Green:** `B` is restored and the operation reports target drift.

The existing in-place-write test remains green; it covers same-inode byte drift but not atomic pathname replacement.

#### 2. `test_archive_apply_atomic_editor_swap_after_target_open_is_stale_and_preserved`

* Use the integration repository fixture.
* Inject the atomic `B` replacement immediately before the first canonical `requirement.md` exchange.
* Make validation and sync fail if called.
* Expect:

```python
("stale", "apply_target_changed")
```

* Assert:

  * `requirement.md` identifies and contains exact `B`;
  * previously completed transaction mutations, including the decision artifact, are rolled back;
  * the other canonical documents retain their original bytes;
  * companion and decision artifacts are absent;
  * local and remote HEAD remain unchanged;
  * no transaction directory or `.spec-dock-apply-*` workspace remains;
  * durable state returns to `OPERATION_RECORDED`;
  * no commit or push occurs.

**Red:** current behavior is `recovery_required/restore_mismatch`, with transaction replacement bytes left canonical and transaction evidence retained.

**Green:** the actual editor attachment is restored and the live transaction closes as stale.

Keep the existing private staged-slot ambiguity test unchanged; it remains a fail-closed defense and is not the public-path race addressed here.

### Allowed files

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`
* Mechanical byte projection only:

  * `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

No new durable phase, ledger field, status, reason, public output, retention store, or locking contract.

---

## Safe implementation order

1. Add the two focused Red unit tests without altering production code.
2. Implement Candidate pre-bound publication binding in the provider source.
3. Run the Candidate focused suite, including Linux native publication and simulated Darwin distinct-inode coverage.
4. Mechanically project the Candidate provider file and verify byte parity.
5. Add the Apply atomic-editor unit and integration Red tests.
6. Implement the Apply exchange-back rule in the provider source.
7. Run focused Apply unit and integration suites, including existing crash-recovery, workspace-intent, rollback, and private-slot ambiguity tests.
8. Mechanically project the Apply provider file and verify byte parity.
9. Run provider/projection parity, `git diff --check`, and the relevant full regression.

This assessment is static and read-only; no tests were executed and no files were modified. Darwin runtime behavior remains a native macOS verification target, while the required distinct-inode semantics can be covered deterministically in the provider unit suite.
