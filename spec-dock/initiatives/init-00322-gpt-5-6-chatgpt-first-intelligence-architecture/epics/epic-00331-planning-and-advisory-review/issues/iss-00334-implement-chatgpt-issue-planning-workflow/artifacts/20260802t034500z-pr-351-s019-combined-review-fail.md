# Read-only combined review

**overall_verdict: `FAIL`**

The review was performed under the bounded P0/P1-only contract in the mandatory task brief. 

## Repository identity

* **Repository:** `chemitaro/spec-dock`
* **Required and inspected branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Required and inspected HEAD:** `caa419afac594d445030e5b28d4f599bbbdfd892`
* **PR:** `#351`
* **Exact branch inspected:** yes
* **Default branch inspected or used as fallback:** no

The GitHub connector reported the required HEAD and branch as `identical`, with `ahead_by=0` and `behind_by=0`. PR #351 independently identifies the same branch and exact head SHA.

The three perspective findings below are manifestations of **one underlying P1 blocker**, rather than three unrelated implementation defects.

## 1. SPEC reviewer

**P0 count:** 0
**P1 count:** 1

### `SPEC-P1-001` — S019 evidence overstates the branch-ref guarantee

**Location**

* `report.md`, section `2026-08-02 — S019 branch-proof repair`
* `artifacts/20260802t005500z-pr-351-s019-branch-proof-blue-chatgpt-recovery.md`, “Bounded implementation packet adopted from local evidence”

The S019 evidence states that one `.git/HEAD.lock` coherently binds the symbolic HEAD, operation branch ref, resolved HEAD, CAS push, remote parity, publication evidence, and terminal result.

That closure claim is not supported by the implementation. The lock is created only at the path returned for `--git-path HEAD`; in a multi-worktree repository this is a per-worktree HEAD lock, while `refs/heads/<operation.branch>` remains a shared ref. The prior exact-head Red finding explicitly required the **operation branch ref itself** to remain lock- or transaction-bound through push and terminal publication.

This matters to the formal gate because the canonical requirement permits `ready/adoption_published` only after current-branch publication and remote parity, while the Plan requires exact-SHA final review and zero blockers before merge-ready handoff.

**Concrete impact**

The Report currently records this authority defect as closed. That can support an incorrect S14 PASS or merge-ready disposition even though a shared operation-branch ref can still change during the claimed lock lifetime.

The attached canonical documents and Report were reviewed only after their exact GitHub blobs were established.    

## 2. CODE reviewer

**P0 count:** 0
**P1 count:** 1

### `CODE-P1-001` — `HEAD.lock` does not serialize the shared operation branch ref across worktrees

**Location**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py:2466-2498`
* same file: `2501-2529`
* same file: `2743-2805`
* same file: `3430-3455`
* same file: `4295-4323`

`_acquire_operation_branch_lock()` resolves `--git-path HEAD` and creates only its sibling `HEAD.lock`. `_operation_branch_commit_is_proven_locked()` then samples the symbolic HEAD, `refs/heads/<operation.branch>`, and resolved HEAD, but no lock or active ref transaction protects `refs/heads/<operation.branch>` after those reads.

The push path performs the proof and then pushes the literal `local_commit`.  The initial-publication path performs its final proof and immediately writes publication evidence and constructs `ready` without another branch-ref guard.  The resume/already-remote-parity path has the same final-proof-to-publication interval.

**Deterministic reviewer reproduction**

Using two linked worktrees:

1. Worktree A checked out the operation branch at commit `C`.

2. Worktree A’s per-worktree `HEAD.lock` was created.

3. From worktree B, this command succeeded:

   ```text
   git update-ref refs/heads/<operation-branch> D C
   ```

4. A subsequent literal-`C` CAS push also succeeded, leaving:

   * local operation branch and worktree-A `HEAD` at `D`;
   * remote operation branch at `C`.

This demonstrates that the new lock prevents checkout in the operation worktree but does **not** preserve the operation branch ref against a normal Git ref update issued through another linked worktree.

Two contract-breaking outcomes remain possible:

* A branch-ref update after the pre-push proof permits an **unauthorized push** of `local_commit` after the checked-out branch/ref/HEAD binding has been lost.
* A branch-ref update after the final proof but before `_record_publication()` permits publication evidence and `ready/adoption_published` while local `HEAD` and `refs/heads/<operation.branch>` no longer equal the published commit.

Both are P1 impacts under the task brief.

The provider and dogfood copies are byte-identical—the connector returned the same blob SHA, `c6c4c17974f4eebaeabb112b46e6b9d414fd5a12`, for both—so the defect is consistently projected rather than caused by projection drift.   The attached source is the same exact implementation. 

## 3. QA reviewer

**P0 count:** 0
**P1 count:** 1

### `QA-P1-001` — The deterministic S019 tests prove checkout exclusion, not branch-ref immutability

**Test evidence**

The three new integration tests are:

* `test_branch_switch_after_symbolic_head_observation_is_locked_before_push`
* `test_resume_branch_switch_after_symbolic_head_observation_is_locked_before_push`
* `test_final_ready_branch_switch_after_symbolic_head_observation_is_locked`

Each test intercepts the symbolic-HEAD observation and attempts:

```text
git checkout -qb alternate
```

in the same operation worktree. Each asserts that checkout is rejected by `HEAD.lock`.

Those tests do not create a second linked worktree or attempt a shared-ref mutation such as:

```text
git update-ref refs/heads/<operation.branch> <new> <proved-local-commit>
```

between the proof and push, or between the final proof and publication evidence. Consequently, the suite cannot distinguish the implemented HEAD-only lock from the required HEAD-plus-operation-branch-ref binding.

The focused unit test also passes a dummy `object()` as `branch_lock` and validates only sampled command results; it does not establish that the supplied lock protects the branch ref.  The attached integration test evidence reflects the same checkout-only coverage. 

This is not a request for an extra confidence test. The omitted concurrency action demonstrably succeeds and reaches the P1 behavior described above, so the gap allowed the recorded S019 PASS evidence to miss a broken required contract.

## Verification summary

Observed directly through the GitHub connector:

* Exact required branch and HEAD identity, with no default-branch fallback.
* PR #351 head bound to `caa419afac594d445030e5b28d4f599bbbdfd892`.
* Exact S018 `FINAL-P1-001` finding and S019 repair commit.
* Provider/dogfood byte identity.
* The complete lock implementation and initial/resume/final publication paths.
* The three S019 checkout-race tests.
* Successful head-associated GitHub Actions runs for both `CI` and `Provider CI`.

Recorded in the exact-head Report and S019 artifact:

* Explicit Apply unit/application/integration: `259 passed`.
* Ordinary fast lane: `1362 passed, 2223 skipped`.
* Ruff check/format and mypy: passed.
* `spec-dock validate`: `nodes=227`.
* `git diff --check`: passed.
* Provider/dogfood byte identity. 

The recorded local command counts were inspected but not independently re-executed in this review. The linked-worktree ref-mutation reproduction was executed with the reviewer environment’s Git 2.47.3; independent reproduction under the project’s logged Git 2.54.0 remains a downstream verification target. The source-level gap does not depend on the recorded test counts.

**No patch, no replacement ZIP, and no repository modification was produced.**
