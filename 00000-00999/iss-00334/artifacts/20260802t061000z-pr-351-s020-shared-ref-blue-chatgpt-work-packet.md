## S020 bounded Blue Team work packet

**Repository identity:** `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, exact inspected HEAD `b544392990ef405548c36106d51a1414dd1719ab`. PR #351 identifies the same branch and HEAD; no default-branch fallback was used.

**Bounded finding:** the current guard owns only the operation worktree’s `HEAD.lock`; the operation branch ref remains shared and mutable from another linked worktree. The existing tests exclude same-worktree checkout but not cross-worktree `update-ref`.  

### 1. Minimal Git-level mechanism

Use a **composite operation-branch guard**:

1. Retain the existing per-worktree `HEAD.lock` to bind the checked-out symbolic `HEAD`.
2. In the same guard, start a long-lived Git-owned `update-ref --stdin` transaction that verifies and prepares the shared operation branch ref:

   ```text
   start
   verify refs/heads/<operation.branch> <local_commit>
   prepare
   ```
3. Require successful acknowledgements for `start` and `prepare`, then leave the `git update-ref --stdin` process running with its input pipe open. Git therefore retains the shared ref’s native lock until the guard sends:

   ```text
   abort
   ```

   and verifies successful termination.
4. Acquire the existing `HEAD.lock` first, then prepare the shared-ref transaction. Perform no branch proof, push, publication write, or result construction until both components are held.
5. Hold both components across:

   * symbolic `HEAD` / operation ref / resolved `HEAD` proof;
   * literal-commit CAS push;
   * remote commit and tree parity;
   * `_record_publication()`;
   * durable `REMOTE_PARITY`;
   * construction of `ready/adoption_published` or the rejected terminal result.
6. Immediately before the push and immediately before publication evidence, call an `assert_held()` operation that verifies:

   * the `HEAD.lock` still has the captured device/inode;
   * the guard is bound to the expected `refs/heads/<branch>` and `local_commit`;
   * the prepared `update-ref` process is still alive;
   * the sampled symbolic `HEAD`, branch ref, and resolved `HEAD` still equal the bound values.

Git documents `HEAD` as worktree-private while ordinary refs are shared, and `update-ref`’s `prepare` operation as acquiring the queued refs’ locks until commit or abort. This avoids guessing loose-ref, packed-ref, or reftable lock paths. ([Git][1])

Run the guard transaction with a private empty `core.hooksPath`. A verify-only guard transaction otherwise emits `reference-transaction` prepared/aborted phases and would alter the existing native-hook observation contract. The actual `_install_operation_commit_cas()` transaction must continue to invoke and delegate the repository’s native hook exactly as it does now.

Do **not** queue `HEAD` and its referent branch in one `update-ref` transaction. The repository’s existing Git 2.54.0 evidence records that combination as a multiple-update rejection. The composite guard is therefore intentional: Git owns the shared branch-ref lock, while the existing explicit `HEAD.lock` owns the per-worktree symbolic `HEAD`.

This closes the linked-worktree reproduction because the second worktree’s:

```text
git update-ref refs/heads/<operation.branch> D C
```

must acquire the same Git-managed shared-ref lock and returns nonzero while the prepared transaction is held. If the branch changed before preparation, the `verify ... C` command fails before any push or publication side effect. The current source instead creates only the sibling lock for `--git-path HEAD` and subsequently samples the shared ref without owning it.

Any failure to start, prepare, maintain, abort, or validate the composite guard must raise the existing `PlanningApplyRestoreMismatch`. Post-commit paths consequently remain fail-closed under the existing `recovery_required/restore_mismatch` contract: local commit retained, push absent, `publication.json` absent, and no `ready`. No new public status or reason is needed.

### 2. Exact implementation surfaces

**Provider authority**

`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

Make only these bounded changes:

* `_OperationBranchLock`

  * Extend it to own both the existing `HEAD.lock` and a prepared shared-ref transaction.
  * Bind it explicitly to `destination_ref` and `expected_commit`.
  * Add `assert_held()`.
  * On exit, validate ownership, send checked `abort`, wait for the child, and remove the owned `HEAD.lock`. Cleanup ambiguity raises `PlanningApplyRestoreMismatch`.

* `_acquire_operation_branch_lock`

  * Accept `operation` and `local_commit`, or equivalent explicit branch/ref inputs.
  * Validate the branch with the existing `check-ref-format` seam.
  * Acquire `HEAD.lock`, start the fixed-argv `git update-ref --stdin` child, queue `verify`, and prepare it.
  * On partial acquisition failure, release only objects proven to be owned.

* Add one private fixed-argv helper for the prepared ref transaction.

  * Use `subprocess.Popen`, never a shell.
  * Do not relax `validate_planning_git_argv`, whose prohibition of general `update-ref` remains correct.
  * Keep this helper as narrow as the existing private `_install_operation_commit_cas()` update-ref seam.

* `_operation_branch_commit_is_proven_locked` and `_operation_branch_commit_is_proven`

  * Require a real composite guard bound to the same destination and commit.
  * Call `assert_held()` before sampling.
  * Remove the effective acceptance of an arbitrary dummy `object()` as `branch_lock`.

* `_push_operation_commit_cas`

  * Acquire the composite guard when no guard is supplied.
  * When supplied, prove that it is bound to the same operation ref and `local_commit`.
  * Call `assert_held()` immediately before invoking `git push`.

* `_publish_initial_operation_commit`

  * Acquire the composite guard before the first branch proof.
  * Keep it through push, parity, `_record_publication()`, `REMOTE_PARITY`, and terminal result construction.

* `_resume_publication`

  * Apply the same guard lifetime to both:

    * resume requiring a push;
    * already-remote-parity publication/ready.

* `_install_operation_commit_cas`

  * No semantic redesign. Preserve its current CAS, prepared-hook proof, and native-hook delegation.

**Tests**

* `tests/unit/infra/test_issue_planning_apply.py`
* `tests/integration/test_issue_planning_apply.py`

No application, domain, CLI, Candidate, Human-decision, or Oracle contract change is required.

**Dogfood projection**

After the provider implementation is green, mechanically replace:

`spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

with the provider file’s exact bytes. The current provider and dogfood copies are already the same blob, so S020 must preserve that byte-identity property rather than authoring the projection separately.

### 3. Red-first deterministic tests

Create linked worktree B on a distinct attacker branch or detached `HEAD`. Commit an attacker change there to obtain commit `D`. Worktree A runs the operation and produces authorized commit `C`. All mutation attempts are issued from worktree B as:

```text
git -C <worktree-B> update-ref refs/heads/feature/issue D C
```

Assert the return code, not localized stderr.

#### A. Initial publication: after proof, immediately before push

Proposed test:

`test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push`

Instrument the direct `subprocess.run()` call for the real publication `git push`. When the exact push argv is reached—after `_push_operation_commit_cas()` has completed its branch proof but before the push process starts—run B’s `update-ref`.

Expected fixed behavior:

* attacker `update-ref` returns nonzero;
* operation returns `ready/adoption_published`;
* A’s symbolic `HEAD` is `refs/heads/feature/issue`;
* `HEAD == refs/heads/feature/issue == C`;
* remote branch is `C`, and its tree is the recorded local tree;
* `publication.json` records `C`;
* durable state is `REMOTE_PARITY`.

Expected red behavior on the current source:

* attacker update succeeds;
* the literal-`C` push can still occur after authority has moved to `D`;
* the safe assertions fail, even if a later proof prevents terminal `ready`.

#### B. Resume publication: after proof, immediately before retry push

Proposed test:

`test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push`

First run:

* inject one push failure;
* require `publication_pending/push_failed`;
* local operation branch is `C`;
* remote remains the operation’s prior `expected_head`;
* `commit.json` exists and `publication.json` does not.

Second run:

* restore the real push implementation;
* intercept the exact push subprocess as in test A;
* run B’s `update-ref D C`.

Expected fixed behavior is the same safe result as test A: mutation rejected, the same existing commit `C` published, no validation/sync/commit rerun, `publication.json` exact, and `ready/adoption_published`.

#### C. Already-remote-parity: after final proof, before publication/ready

Proposed test:

`test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready`

Setup:

* create `publication_pending` with local commit `C`;
* externally publish literal `C` to the test bare remote;
* wrap `_record_publication()`;
* at wrapper entry—after the final branch proof and immediately before evidence—run B’s `update-ref D C`.

Expected fixed behavior:

* mutation returns nonzero;
* `_record_publication()` writes evidence for `C`;
* durable state becomes `REMOTE_PARITY`;
* result is `ready/adoption_published`;
* local branch ref, resolved `HEAD`, and remote remain `C`.

Expected red behavior on the current source:

* mutation succeeds;
* `_record_publication()` still runs;
* the function can return `ready/adoption_published` while local `HEAD` and the operation branch now resolve to `D`.

#### Supporting unit tests

Add focused tests for:

* a real temporary repository plus linked worktree proving that the prepared transaction rejects a second `update-ref`, and that the update succeeds after the guard aborts;
* branch-ref preimage mismatch during `prepare`: acquisition fails, owned `HEAD.lock` is removed, no fallback sampling occurs;
* foreign branch-ref lock, malformed protocol acknowledgement, early child exit, and abort failure all fail closed;
* a supplied guard bound to the wrong branch or commit is rejected;
* arbitrary `object()` is no longer accepted as a meaningful lock;
* the existing same-worktree checkout exclusion tests remain green;
* `test_reference_transaction_hook_is_delegated_once_per_phase` still observes only the actual install transaction, not the verify-only guard.

The current integration tests cover only `git checkout -qb alternate` in worktree A, so they must remain as complementary `HEAD.lock` coverage rather than being replaced.

### 4. Verification and acceptance

Run the new red tests first against the current source and record that the linked-worktree mutation succeeds.

After implementation:

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_prepared_ref_transaction_blocks_linked_worktree_update_ref \
  tests/unit/infra/test_issue_planning_apply.py::test_operation_branch_lock_prepare_failure_fails_closed \
  tests/integration/test_issue_planning_apply.py::test_initial_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_resume_linked_worktree_ref_update_after_proof_is_locked_before_push \
  tests/integration/test_issue_planning_apply.py::test_already_remote_parity_linked_worktree_ref_update_is_locked_before_publication_ready
```

Then the complete Apply-focused lane:

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

Ordinary fast lane, static checks, and validation:

```bash
uv run pytest
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
```

Projection and byte identity:

```bash
cp \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py

shasum -a 256 \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

Final branch and remote parity after the bounded implementation commit is pushed:

```bash
branch=iss-00334-implement-chatgpt-issue-planning-workflow

git fetch origin "$branch"
test "$(git branch --show-current)" = "$branch"
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$branch")"
test -z "$(git status --porcelain=v2)"
```

Acceptance requires all of the following:

* all three linked-worktree mutations return nonzero at their exact checkpoints;
* no push occurs when the composite guard cannot prepare or prove ownership;
* no `publication.json`, `REMOTE_PARITY`, or `ready/adoption_published` occurs after branch/ref identity loss;
* safe initial, resume, and already-remote-parity paths still converge to the same authorized commit;
* remote divergence remains non-force and uses the existing result contract;
* same-operation retry does not create a second commit;
* existing checkout exclusion, install CAS, strict trailer, immutable publication endpoint, native hook delegation, rollback, and recovery tests remain green;
* public status/reason/schema are unchanged; `ready/adoption_published` remains conditional on exact local commit, remote branch, and tree parity.
* provider and dogfood files are byte-identical;
* final local branch, remote branch, and clean-tree evidence agree.

### 5. Non-goals and uncertainty

**Non-goals**

* No new public status, reason, JSON field, command, or option.
* No Candidate, canonical-document, Human authorization, Oracle, or provider-authority redesign.
* No persistent registry, custom Git ref, daemon, external service, or repository-wide lock.
* No retry, waiting, fairness, timeout, or stale-lock reclamation policy.
* No force push, reset, amend, rebase, or remote-policy change.
* No manual locking of guessed `refs/heads/*.lock`, `packed-refs`, or reftable storage.
* No replacement of the existing local commit installation transaction.
* No reopening of P2/P3, S01–S019, or unrelated historical findings.
* No direct independent edits to the dogfood copy.
* No extension to malicious same-UID processes that deliberately kill the guard child or remove owned locks.

**Uncertainty requiring implementation-time verification**

The official Git interface supports prepared `update-ref --stdin` transactions, but the exact minimum supported Git version and every supported ref backend have not yet been established by repository acceptance evidence. The real linked-worktree unit test must therefore execute the protocol—not mock it—on the project’s supported Git lane. Unsupported protocol, unexpected acknowledgement, hook leakage, or inability to retain the prepared lock is a hard failure; it must not fall back to repeated sampling or manual lock-path construction. Official Git documentation was consulted on August 2, 2026, but remains downstream verification input rather than independently validated repository evidence. ([Git][2])

[1]: https://git-scm.com/docs/git-worktree.html "https://git-scm.com/docs/git-worktree.html"
[2]: https://git-scm.com/docs/git-update-ref "https://git-scm.com/docs/git-update-ref"
