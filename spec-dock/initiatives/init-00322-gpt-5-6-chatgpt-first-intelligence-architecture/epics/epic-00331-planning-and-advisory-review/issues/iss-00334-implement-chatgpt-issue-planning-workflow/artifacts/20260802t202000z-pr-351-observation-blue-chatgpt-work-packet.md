# Blue Team Work Packet

## 1. Repository binding and scope

**Repository:** `chemitaro/spec-dock`
**Required branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
**Analyzed HEAD:** `97798b93bf8bf0e1b6793f3567fc1976ef2556ac`
**PR:** `#351`

GitHub reports that PR #351 is open with the required feature branch at the exact specified HEAD; no default-branch fallback was used.

This packet is limited to the four current P0/P1 findings in the attached brief and observation result. It excludes carryover findings, architectural redesign, P2/P3 work, patches, ZIP generation, and repository modification.  

Implementation status: **planned only; no fix is claimed as implemented.**

Path shorthand below:

* `P/` = `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
* `D/` = `spec-dock/scripts/spec_dock_runtime/`

## 2. Finding-to-code mapping

| Finding                                   | Current boundary                                                                                                                                                                                                                                  | Minimal code surface                                                                                                                                                                             | Required result contract                                                                                                                                                                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0 apply-origin-credential-disclosure** | `run_issue_planning_apply()` calls `repo_slug_resolver(repo_root)` without a `RuntimeError` guard. The top-level CLI prints an escaped exception with `error: {error}`.                                                                           | `P/application/issue_planning.py`, `D/application/issue_planning.py`, `tests/unit/application/test_issue_planning_apply.py`                                                                      | Resolver `RuntimeError` or `None` → `blocked/github_upstream_required`, with empty output/details and no exception text. A successfully resolved but different repository remains `stale/apply_target_changed`.                                     |
| **P1 planning-json-recursion-contract**   | `_strict_json_object()` normalizes `JSONDecodeError` and `UnicodeDecodeError`, but not `RecursionError`.                                                                                                                                          | `P/domain/issue_planning_contracts.py`, `D/domain/issue_planning_contracts.py`, domain and application tests                                                                                     | `RecursionError` → `ValueError("invalid JSON")`; existing application handlers then return their current structured `rejected` reasons.                                                                                                             |
| **P1 review-stage-identity-toctou**       | Review publication closes the staging-directory descriptor, then renames the staging pathname. Its failure cleanup also opens and recursively deletes whichever directory currently occupies that name.                                           | `P/infra/issue_planning_review.py`, `D/infra/issue_planning_review.py`, `tests/unit/infra/test_issue_planning_review.py`                                                                         | A successful result must be bound to the staged directory and exact two staged files. Any identity/content substitution must return `blocked/review_publication_failed`, never `review_completed`; unknown replacement entries must not be deleted. |
| **P1 planning-source-publication-toctou** | Create, Review, and Revise validate source state before invoking their publisher, then return success from the publisher result without a publication-completion source guard. Review and revision show the check-then-publish ordering directly. | `P/application/issue_planning.py`, `P/application/ports.py`, `P/infra/issue_planning_candidate.py`, `P/infra/issue_planning_review.py`, `P/cli/bootstrap.py`; matching `D/` files; focused tests | The original source evidence and Candidate snapshot must remain current through publication completion. A stale publication is removed only when ownership is proven, then maps to the existing command-specific structured stale reason.           |

The provider and dogfood copies of the affected application, contract, port, candidate, and review modules currently have matching blob SHAs. The repair must preserve that whole-file parity.

## 3. Minimal change sequence

### 3.1 Normalize apply origin resolution without disclosing exception content

In `run_issue_planning_apply()`:

1. Wrap only `repo_slug_resolver(repo_root)` in `except RuntimeError`.
2. Treat both a caught `RuntimeError` and a returned `None` as:

   ```text
   status = blocked
   reason = github_upstream_required
   issue_id = resolved issue ID
   output = {}
   details = ()
   ```
3. Do not call `str(error)`, log the exception, or copy it into any result field.
4. Preserve the existing repository-identity branch:

   * resolved repository differs from `identity.repository` → `stale/apply_target_changed`;
   * exact repository match → continue.
5. Do not broaden the catch to `Exception`; unrelated programmer or infrastructure faults must retain existing behavior.

This mirrors the already content-free transport-side `github_upstream_required` treatment rather than inventing a new result reason.

### 3.2 Normalize recursive JSON failure at the shared parser

In `_strict_json_object()` change only the parser-failure catch set:

```python
except (json.JSONDecodeError, UnicodeDecodeError, RecursionError) as error:
    raise ValueError("invalid JSON") from error
```

Constraints:

* Do not catch `ValueError` broadly. Duplicate-key and non-standard-number rejection semantics must remain intact.
* Do not catch `MemoryError`, `KeyboardInterrupt`, or other process-level failures.
* Preserve the exact public message `invalid JSON`.
* Leave all callers unchanged so their existing `except ValueError` branches produce:

  * malformed Review input → `rejected/review_result_rejected`;
  * malformed Human decision → `rejected/human_decision_rejected`;
  * malformed revision request → `rejected/revision_request_rejected`.

### 3.3 Add a publication-completion guard to the existing publisher ports

Add a required keyword-only callback to both publication contracts:

```python
publication_guard: Callable[[], bool]
```

Affected gateway methods:

```python
build_and_publish_candidate(..., publication_guard=...)
publish_planning_review_evidence(..., publication_guard=...)
```

Add one application-facing typed exception, for example:

```python
class IssuePlanningSourceStale(ValueError):
    pass
```

Use corresponding fixed-message infra exceptions, such as `CandidateSourceStale` and `ReviewSourceStale`, and translate them in `cli/bootstrap.py` to `IssuePlanningSourceStale`.

Required behavior:

1. The callback is invoked **exactly once**, after the final object has been atomically installed and its identity/content verified, but before the publisher marks the operation successful or returns.
2. Destination collision is detected before callback invocation.
3. `False` means source stale.
4. A callback exception must not be stringified or exposed. After safe cleanup, map it to the existing generic publication-failure path rather than a stale result.
5. `IssuePlanningSourceStale` must be caught before broader `ValueError`/`OSError` handlers.

An optional callback default must not be added; production callers should be unable to omit the publication-boundary guard accidentally.

### 3.4 Extend the Candidate publisher using its existing ownership model

The Candidate publisher already retains a descriptor/device/inode tuple for the staged and published file, verifies final bytes, and has identity-sensitive rejected-publication cleanup.

Make the smallest extension:

1. Invoke `publication_guard()` after:

   * atomic no-replace publication;
   * re-reading the published fd;
   * digest/length verification;
   * output-directory attachment verification.
2. Invoke it before setting `published = True`.
3. If it returns `False`, synchronously remove the exact captured `published_entry`.
4. Change the ownership cleanup helper to report whether it actually removed that exact entry.
5. Raise `CandidateSourceStale` only when:

   * the final entry still matches the retained device/inode;
   * the exact owned file was isolated and deleted;
   * the output directory was fsynced.
6. If the final name has been replaced, ownership cannot be proven, or cleanup fails:

   * preserve the replacement;
   * do not return stale;
   * raise fixed, content-free `CandidatePublicationFailed`.
7. Preserve the existing no-replace collision and opaque output-guard paths.

### 3.5 Bind Review publication to the open staging identity and exact bytes

Refactor `publish_planning_review_evidence()` around small private ownership records:

```text
OwnedReviewDirectory
- name
- descriptor
- device
- inode

OwnedReviewFile
- name
- descriptor
- device
- inode
- expected size
- expected SHA-256
```

Required sequence:

1. Create and open the private staging directory.
2. Keep its descriptor open through the no-replace namespace transition.
3. Write both files with `O_EXCL | O_NOFOLLOW`, retaining descriptors or reopening them immediately and recording device/inode.
4. Fsync both files and the staging directory.
5. Perform the existing atomic no-replace rename.
6. Before any success result:

   * verify the destination name resolves to the same directory device/inode as the retained staging descriptor;
   * open the destination directory independently and verify it has the same identity;
   * require the exact inventory:

     * `planning-review-result.json`
     * `planning-review-summary.md`
   * reject extra or missing entries;
   * verify each child is a regular file and matches the retained child identity;
   * read the published bytes through captured descriptors and compare size and SHA-256 with the supplied inputs;
   * compute `review_result_sha256` from those verified published bytes;
   * fsync the published directory and output directory;
   * revalidate the output-directory guard.
7. Invoke `publication_guard()` only after those checks.
8. Mark publication successful only after the guard returns `True`.

A pre-rename `stat()` or a second pathname check alone is not sufficient. The success result must depend on post-transition directory identity and child-byte verification.

Replace `_remove_evidence_directory_at()` with ownership-bound cleanup:

* never enumerate and delete arbitrary children from a pathname that may have been replaced;
* isolate the captured directory through an identity-checked quarantine move where supported by the existing no-replace primitives;
* inspect the moved directory identity before deleting;
* unlink only the two captured child identities;
* remove only the captured directory;
* if any identity differs, preserve the unknown object and return publication failure.

A deterministic staging-name replacement may therefore leave attacker-created material untouched, but it must never produce `review_completed` or cause that unknown material to be deleted.

### 3.6 Carry the source/Candidate guard through each application publication

#### Create

Build a closure that checks the original `transport.source_evidence` with `_source_evidence_is_current()`.

Use it in two places:

1. Recheck immediately after authoring/material construction and before invoking the publisher. This prevents unnecessary publication when `authoring_loader` changed the source.
2. Pass the same closure as `publication_guard` so a change during Candidate publication is detected.

Mapping:

```text
IssuePlanningSourceStale
→ stale/planning_source_stale
```

No Candidate output may be reported.

#### Review

Build a total boolean guard that requires both:

1. `_source_evidence_is_current()` against `transport.source_evidence`; and
2. reloading `request.candidate_path` and matching the originally reviewed Candidate’s identity and exact `zip_bytes`.

Pass it to the Review publisher.

Mapping:

```text
IssuePlanningSourceStale
→ stale/review_target_changed
```

The newly published Review directory must already have been removed by the publisher before this result is returned.

#### Revise

For both revision lanes, build a guard requiring:

1. the captured `source_evidence` to remain current; and
2. the input Candidate to reload with the same identity and exact `zip_bytes`.

The mandatory regression is the mechanical lane, but the shared publisher call must protect semantic revision as well.

Mapping:

```text
IssuePlanningSourceStale
→ stale/revision_source_stale
```

The original Candidate remains untouched, and no revised Candidate may remain at the requested destination.

## 4. Exact tests to add or update

### `tests/unit/application/test_issue_planning_apply.py`

Add:

* `test_apply_origin_resolver_runtime_error_is_content_free_blocked`

  * Resolver raises `RuntimeError` containing distinct credential-bearing fetch and push strings.
  * Assert `blocked/github_upstream_required`.
  * Assert `output == {}` and `details == ()`.
  * Assert both secret strings are absent from:

    * `repr(result)`;
    * `str(result.to_dict())`;
    * rendered text;
    * rendered JSON;
    * captured logs/stderr.
  * Assert preflight, resume, and transaction runners are not called.

* `test_apply_origin_resolver_none_is_github_upstream_required`

  * `None` maps to the same blocked result.

* `test_apply_resolved_repository_mismatch_remains_stale`

  * A non-`None` different slug remains `stale/apply_target_changed`.

* `test_apply_recursive_review_json_is_structured_rejected`

  * Bounded deeply nested JSON in the Review file.
  * Assert `rejected/review_result_rejected`.
  * Assert rendered JSON parses as one `PlanningCommandResult`.
  * Assert no mutation path is reached.

* `test_apply_recursive_human_decision_json_is_structured_rejected`

  * Same requirements, expecting `rejected/human_decision_rejected`.

Update the `_run` fixture/helper to accept an injected `repo_slug_resolver`.

### `tests/unit/domain/test_issue_planning_contracts.py`

Add:

* `test_strict_json_recursion_is_normalized_to_invalid_json`

  * Construct a root object containing nested arrays with a payload comfortably below the 1 MiB input bound.
  * Assert exact exception text:

    ```text
    invalid JSON
    ```

* `test_strict_json_recursion_normalization_does_not_change_other_failures`

  * Retain existing duplicate-key, non-standard-number, and non-object-root expectations.

### `tests/unit/application/test_issue_planning.py`

Update all fake Candidate and Review publishers to accept the required `publication_guard`.

Add:

* `test_revise_recursive_request_json_is_structured_rejected`

  * Expect `rejected/revision_request_rejected`.
  * Assert valid JSON rendering and no publisher/backend call.

* `test_create_source_drift_during_authoring_stops_before_publication`

  * `authoring_loader` modifies one canonical source path.
  * Expect `stale/planning_source_stale`.
  * Assert publisher was not called and output directory stayed empty.

* `test_create_publication_boundary_source_drift_maps_to_stale`

  * Fake publisher mutates source, invokes the supplied guard, and raises `IssuePlanningSourceStale`.
  * Expect `stale/planning_source_stale` with no output.

* `test_review_publication_boundary_source_drift_maps_to_stale`

  * Expect `stale/review_target_changed`.
  * Assert no successful Review output fields.

* `test_review_publication_boundary_candidate_drift_maps_to_stale`

  * Replace the Candidate during publication.
  * Expect the same stale result.

* `test_mechanical_revision_publication_boundary_source_drift_maps_to_stale`

  * Mutate source during the Candidate publisher.
  * Expect `stale/revision_source_stale`.
  * Assert the original v1 Candidate is byte-identical and no v2 remains.
  * Assert semantic backend transport was not invoked.

* `test_publication_guard_is_not_invoked_on_output_collision`

  * Cover both Candidate-producing paths as applicable.

### `tests/unit/infra/test_issue_planning_candidate.py`

Add:

* `test_candidate_source_stale_removes_only_owned_published_file`

  * Guard returns `False`.
  * Expect `CandidateSourceStale`.
  * Final Candidate absent.
  * Unrelated sentinel entries unchanged.

* `test_candidate_stale_cleanup_preserves_replaced_final_name`

  * Guard moves the owned final aside, creates a replacement at the final name, then returns `False`.
  * Replacement bytes remain untouched.
  * Expect `CandidatePublicationFailed`, not `CandidateSourceStale`.

* `test_candidate_publication_guard_runs_once_after_final_byte_verification`

  * Guard observes a final file whose bytes and digest match the returned identity.

Update existing direct publisher tests to pass `publication_guard=lambda: True`.

### `tests/unit/infra/test_issue_planning_review.py`

Add:

* `test_review_publication_rejects_staging_directory_name_replacement`

  * Immediately before the real no-replace rename:

    * rename the legitimate staging directory to another name;
    * install a malicious replacement at the original staging name.
  * Assert the function does not return `PublishedPlanningReview`.
  * Assert unknown replacement bytes are not deleted.
  * Assert no success digest is claimed.

* `test_review_publication_rejects_staging_child_identity_replacement`

  * Replace either result or summary entry after write but before publication.
  * Assert fixed publication failure and no success.

* `test_review_success_digest_matches_verified_final_bytes`

  * On success, read the final result file and assert its SHA-256 equals `review_result_sha256`.

* `test_review_source_stale_removes_only_owned_published_directory`

  * Guard returns `False`.
  * Expect `ReviewSourceStale`.
  * Newly published Review directory absent.
  * Unrelated output entries unchanged.

* `test_review_stale_cleanup_preserves_replaced_final_directory`

  * Replace the final directory before stale cleanup.
  * Preserve the replacement.
  * Expect generic Review publication failure, not source stale.

* `test_review_publication_guard_runs_once_after_identity_and_content_verification`

Update all existing direct publisher calls with an always-true publication guard. Retain the existing output-directory swap and collision tests.

## 5. Safety invariants

1. **Exact repository binding remains unchanged.** No default-branch fallback is introduced into source guards, Review, Create, Revise, or Apply.

2. **Origin resolution remains content-free.** Resolver exception messages, remote URLs, credentials, filesystem paths, and exception causes never appear in status, reason, details, output, text rendering, JSON rendering, or logs.

3. **JSON rejection remains centralized.** Recursive parser failure is normalized once in `_strict_json_object()`; individual command handlers retain their existing reason vocabulary.

4. **No false publication success.** `candidate_created`, `candidate_revised`, or `review_completed` is possible only after:

   * atomic no-replace publication;
   * exact final identity/content verification;
   * publication-completion source/Candidate guard success.

5. **Stale means cleanup completed.** A structured stale result is returned only after the exact newly published object has been proven owned and removed. Cleanup ambiguity maps to existing publication failure instead.

6. **No pathname-only destructive cleanup.** Cleanup requires retained descriptor plus device/inode identity. Unknown replacements are preserved.

7. **Collision semantics are unchanged.** Existing output is never overwritten or removed, and the publication guard is not invoked after an initial no-replace collision.

8. **Output guards remain authoritative.** Candidate publication continues to use the opaque validated guard; Review retains output-directory identity validation before and after publication.

9. **Review handoff digest remains byte-bound.** `review_result_sha256` is calculated from bytes re-read from the verified final published file, not solely from the original input buffer.

10. **Provider/dogfood parity remains whole-file exact.** All changed runtime files are projected byte-for-byte, with no dogfood-only repair.

11. **No external dependency is added.** Use the repository’s existing descriptor, `renameat2`/`renameatx_np`, no-replace, hashing, and fsync machinery.

## 6. Must-fix acceptance criteria

* [ ] Resolver `RuntimeError` and `None` return `blocked/github_upstream_required`.
* [ ] Credential-bearing resolver text is absent from every observable result and log surface.
* [ ] A resolved but mismatched repository still returns `stale/apply_target_changed`.
* [ ] Deep bounded Review, Human decision, and revision JSON produce their existing structured `rejected` results under JSON rendering.
* [ ] `_strict_json_object()` raises exactly `ValueError("invalid JSON")` for `RecursionError`.
* [ ] Replacing the Review staging pathname cannot produce `review_completed`.
* [ ] Replacing either staged Review child cannot produce `review_completed`.
* [ ] Every successful Review result identifies exactly the bytes present in the final published files.
* [ ] Create source drift during authoring stops before publication.
* [ ] Source or Candidate drift during Create, Review, and mechanical Revise publication returns the command-specific stale result.
* [ ] A stale result leaves no newly published Candidate or Review evidence.
* [ ] Unknown replacement entries are never deleted during stale or rejected-publication cleanup.
* [ ] Cleanup ambiguity returns existing publication failure rather than false success or false stale.
* [ ] Existing collision, output-guard, and no-replace tests continue to pass.
* [ ] Provider and dogfood files compare byte-identically.
* [ ] Focused, integration, lint, and full regression commands pass.

## 7. Verification commands

Run from the feature-branch checkout after implementation:

```bash
test "$(git branch --show-current)" = \
  "iss-00334-implement-chatgpt-issue-planning-workflow"

git merge-base --is-ancestor \
  97798b93bf8bf0e1b6793f3567fc1976ef2556ac \
  HEAD
```

Focused tests:

```bash
pytest -q \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/commands/test_issue_planning.py
```

Integration and CLI coverage:

```bash
pytest -q \
  tests/integration/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_e2e.py \
  tests/cli_runtime/test_chatgpt_cli.py
```

Provider-to-dogfood parity:

```bash
for file in \
  application/issue_planning.py \
  application/ports.py \
  cli/bootstrap.py \
  domain/issue_planning_contracts.py \
  infra/issue_planning_candidate.py \
  infra/issue_planning_review.py
do
  cmp -s \
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/${file}" \
    "spec-dock/scripts/spec_dock_runtime/${file}" \
    || {
      echo "provider/dogfood mismatch: ${file}" >&2
      exit 1
    }
done
```

Repository checks:

```bash
git diff --check
make lint
pytest -q
```

The Review publication race tests must also be exercised on both supported syscall branches:

* Linux: `renameat2(..., RENAME_NOREPLACE)`
* macOS: `renameatx_np(..., RENAME_EXCL)`

## 8. Assumptions and local verification obligations

* The proposed `publication_guard` callback is the smallest layer-compatible way to reuse existing source evidence without moving Git/preflight responsibilities into infra.
* Exact exception class names may be adjusted to repository naming conventions, but the distinct stale-vs-publication-failure semantics and catch ordering are mandatory.
* Linux/macOS descriptor and rename behavior has not been executed in this read-only planning pass. Deterministic fault-hook tests must verify both supported implementations locally.
* Every fake gateway, direct infra publisher call, and bootstrap adapter affected by the required callback must be found by type checking and full regression; no compatibility default should conceal a missed caller.
