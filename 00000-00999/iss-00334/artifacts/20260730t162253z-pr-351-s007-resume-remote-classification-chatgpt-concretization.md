# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b78bd-eea4-83e8-aa71-bfc6b4dd042a

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

S007 bounded task: classify a remote branch deleted before resume as blocked_remote_diverged while keeping observation-unavailable pending. Use the attached prompt as the complete task brief, inspect the required GitHub branch first, and return only the implementation work packet.

## Answer

# Implementation Work Packet

## Repository basis

GitHub connector inspection succeeded for `chemitaro/spec-dock`. PR `#351` points to branch `iss-00334-implement-chatgpt-issue-planning-workflow` at the required exact HEAD `91715eecf306bd0c978da922f87193151764cdcd`.

At that branch baseline, `_remote_head()` collapses both failed observation and an absent ref to `None`; `_resume_publication()` consequently maps both to `publication_pending/remote_parity_unconfirmed`.   The attached S007 delta introduces the required three-state `_remote_head_observation()` and exact expected-old CAS machinery, but its first resume observation still goes through `_remote_head()`.  

## Change scope

Apply one byte-identical source change to:

* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`

Add two regression tests to:

* `tests/integration/test_issue_planning_apply.py`

Keep the existing S007 unit coverage in `tests/unit/infra/test_issue_planning_apply.py`, especially the exact-old lease test and `_cas_failure_result()` unavailable-observation test. No public contract, documentation, application, Human-boundary, or Oracle/configuration file changes.

## Minimal implementation

In `_resume_publication()`, change **only its first remote observation** from `_remote_head()` to the existing `_remote_head_observation()`.

Use this classification before any resume push:

| First resume observation                           | Required behavior                                                                                                 |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `present`, remote equals `operation.expected_head` | Continue through the existing `_push_operation_commit_cas()` path.                                                |
| `present`, remote equals `local_commit`            | Skip push and continue existing remote-tree parity verification.                                                  |
| `present`, any other SHA                           | Return `blocked_remote_diverged/remote_diverged`, with that SHA in `remote_commit`.                               |
| `absent`                                           | Return `blocked_remote_diverged/remote_diverged`, with `remote_commit=None`. Do not invoke the push helper.       |
| `unavailable`                                      | Return `publication_pending/remote_parity_unconfirmed`, with `remote_commit=None`. Do not invoke the push helper. |

Implementation ordering:

1. Obtain `(disposition, remote)` from `_remote_head_observation()`.
2. Handle `absent` first as deterministic divergence.
3. Handle `unavailable`—and defensively any non-present observation without a SHA—as parity unconfirmed.
4. Continue the current present-SHA control flow unchanged.

Do **not** call `_cas_failure_result()` for this initial observation. That helper owns classification after an attempted CAS push; its unavailable branch intentionally returns `publication_pending/push_failed`, which is not the resume-entry unavailable contract.

Leave these paths unchanged:

* `_push_operation_commit_cas()` and its exact `--force-with-lease=<ref>:<expected-old>` semantics.
* `_cas_failure_result()`:

  * absent or observed divergent SHA after failed CAS → `blocked_remote_diverged/remote_diverged`;
  * unavailable after failed CAS → `publication_pending/push_failed`.
* The observation after an apparently successful push.
* Existing remote-tree parity verification.
* Durable state, attempt recording, `commit.json`, and `publication.json` formats.

For both new early returns, retain `commit.json`, do not create `publication.json`, do not advance to `REMOTE_PARITY`, and do not change the local commit. The normal resume attempt record may still be added under the existing execution order.

## Regression tests

### 1. Remote deleted before resume

Add `test_resume_publication_remote_deleted_before_retry_is_blocked`.

Test sequence:

1. Create the local bare-origin fixture and operation.
2. Inject one initial `_push_operation_commit_cas()` failure, producing a committed resumable operation with `publication_pending/push_failed`.
3. Record the local operation commit and commit count.
4. Delete `refs/heads/feature/issue` from the bare origin **between invocations**, before the second call begins.
5. Make validation and sync fail the test if called.
6. Make `_push_operation_commit_cas()` fail the test if called during resume.
7. Invoke the same operation again.

Required assertions:

* Result is `blocked_remote_diverged/remote_diverged`.
* `remote_commit is None`.
* The remote ref remains absent.
* Local HEAD and commit count are unchanged.
* `commit.json` remains present.
* `publication.json` remains absent.
* No validation, sync, new commit, or push occurs.

This test is distinct from the existing `test_resume_publication_remote_delete_or_rewind_is_blocked_by_cas`: that existing test deletes or rewinds the ref at `before_push`, after the first resume observation, and must remain unchanged as the exact-old CAS race regression. 

### 2. Observation unavailable before resume

Add `test_resume_publication_remote_observation_unavailable_before_retry_stays_pending`.

Use the same initial fail-once push setup to create committed resume evidence. Before the second invocation:

* monkeypatch `_remote_head_observation()` to return `("unavailable", None)`;
* make `_push_operation_commit_cas()` fail the test if called;
* make validation and sync fail the test if called.

Required assertions:

* Result remains `publication_pending/remote_parity_unconfirmed`.
* `remote_commit is None`.
* The actual bare-origin ref remains at `operation.expected_head`.
* Local HEAD and commit count are unchanged.
* `commit.json` remains present.
* `publication.json` remains absent.
* No push is attempted.

Retain the existing unit test proving that unavailable observation **after a failed CAS attempt** continues to mean `publication_pending/push_failed`; the two unavailable cases intentionally have different reasons.

## Narrow verification

Run from the repository root:

```bash
cmp -s \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

```bash
python -m pytest -q tests/unit/infra/test_issue_planning_apply.py \
  -k "dedicated_push_uses_exact_expected_old_lease or cas_failure_with_unavailable_remote_preserves_push_failed"
```

```bash
python -m pytest -q tests/integration/test_issue_planning_apply.py \
  -k "resume_publication_remote_deleted_before_retry_is_blocked or resume_publication_remote_observation_unavailable_before_retry_stays_pending or resume_publication_remote_delete_or_rewind_is_blocked_by_cas or push_failure_keeps_local_commit_for_same_operation_retry"
```

```bash
python -m pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py
```

```bash
git diff --check
```

## Acceptance boundary

The repair is complete when deletion before resume is blocked without attempting publication, unavailable observation remains pending/unconfirmed, the existing CAS-race tests still pass, provider/projection source copies remain byte-identical, and no status, reason, schema, retry policy, Human boundary, or Oracle/configuration behavior changes.

`advisory_verdict: implementable`

`verification_status: commands specified; not executed in this consultation`
