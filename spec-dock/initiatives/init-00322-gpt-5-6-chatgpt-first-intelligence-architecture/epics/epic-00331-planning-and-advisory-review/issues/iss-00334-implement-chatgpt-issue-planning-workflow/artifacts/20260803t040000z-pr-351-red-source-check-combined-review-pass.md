# Fresh Red Team Read-Only Review

## 1. Verdict and exact review identity

**Overall verdict: PASS**

| Item                     | Verified value                                                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository               | `chemitaro/spec-dock`                                                                                                                                                                            |
| Required branch          | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                                                                                            |
| Pull request             | `#351`, open                                                                                                                                                                                     |
| Exact reviewed HEAD      | `dcf15fca0dcce74da0fc0f20855b5f125dc64564`                                                                                                                                                       |
| Branch binding           | Required branch is identical to the exact reviewed HEAD                                                                                                                                          |
| PR binding               | PR head branch and head SHA equal the required branch and exact HEAD                                                                                                                             |
| Default-branch fallback  | Not used                                                                                                                                                                                         |
| Review role              | Fresh Red Team, read-only                                                                                                                                                                        |
| Active model             | GPT-5.6 Pro                                                                                                                                                                                      |
| Model-selection evidence | Active runtime model identity. No Oracle or wrapper model-selector transcript was invoked for this connector-only review, so no separate `requested/resolved/verified` wrapper tuple is claimed. |

The GitHub branch ref resolves to the exact required commit.  PR #351 is open, with head branch `iss-00334-implement-chatgpt-issue-planning-workflow` and head SHA `dcf15fca0dcce74da0fc0f20855b5f125dc64564`.  A direct GitHub comparison of the required SHA against the branch returned `identical`, with zero commits ahead or behind.

The attached fresh Red Team prompt was used as the review contract. 

## 2. Inspected files and evidence

### Production and dogfood application sources

Inspected at the exact HEAD:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
* `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py`

Both files have the same Git blob SHA:

```text
76e766dc1e5cb47adf759a3cab8533a15a4b1da2
```

The provider implementation contains the repaired guards at approximately lines 1935–1985.  The dogfood projection contains the same code and identical blob identity.

The attached application source is byte-identical to that exact-head GitHub blob and was treated only as supplementary evidence. 

### Application tests

Inspected:

* `tests/unit/application/test_issue_planning.py`, approximately lines 2763–2832
* Git blob SHA: `b2983b9ae834897f8120445dcae566fe56d23dee`

The exact-head test source defines the shared guard probe and parameterizes it for both Review and semantic revision.  The attached test file is byte-identical to this GitHub blob. 

### Result mappings and publisher boundaries

Inspected:

* Review post-transport revalidation, publication-guard wiring, and result mapping in `run_issue_planning_review()`, approximately lines 1284–1381.
* Revision source revalidation, publication-guard wiring, and result mapping in `run_issue_planning_revise()`, approximately lines 1683–1764.
* Review evidence publisher fail-closed behavior in `infra/issue_planning_review.py`.
* Candidate publisher guard-false cleanup contract and its exact tests.

### Exact Issue contract

Inspected the exact-head canonical Issue documents:

* `requirement.md`: REQ-003 requires the exact current branch, prohibits default-branch substitution, and requires branch/HEAD/source-manifest revalidation with drift rejected before a successful Candidate or Review publication.
* `design.md`: application owns exact local Git preflight; post-Oracle source revalidation uses the expected manifest, and provider/dogfood ownership remains separated.
* `plan.md`: the planned surfaces identify provider `application/issue_planning.py`, focused application tests, provider-first projection, Review/revision regression coverage, and provider/dogfood parity.

The bounded Blue Team packet expressly limits the repair to guard ordering, retains identity plus exact ZIP bytes as the Candidate equality contract, and does not claim a lock, transaction, or linearizable snapshot. 

### Diff boundary

GitHub comparison from the Blue-packet source HEAD `bc7b160b0a710bf799214d0cc5f8d0a34e18672b` to the reviewed HEAD showed exactly one commit and only these five changed paths:

1. Blue Team work packet artifact
2. Issue `report.md`
3. Provider `application/issue_planning.py`
4. Dogfood `application/issue_planning.py`
5. `tests/unit/application/test_issue_planning.py`

No domain, ports, Oracle adapter, CLI, presentation, publisher, cleanup, or public-schema file changed in this repair commit.

The old source-first implementation is independently visible at the prior HEAD; both helpers performed source validation before loading the Candidate.

### Exact-head automated checks

The GitHub connector showed both exact-head workflow runs completed successfully:

* `CI / validate`
* `Provider CI / provider-tests`, including provider static analysis and provider pytest

The larger local counts recorded in `report.md` were inspected but not independently re-executed in this read-only review. The report records focused, Issue Planning, ordinary pytest, lint, validation, diff-check, and provider/dogfood parity as passing.

## 3. Repair verification

### Review publication guard

`_review_publication_is_current()` now performs:

1. `candidate_loader(candidate_path, repo_root)`
2. Fail-closed handling of `IssuePlanningCandidateArchiveRejected`, `OSError`, and `ValueError`
3. Exact Candidate identity comparison
4. Exact Candidate ZIP-byte comparison
5. Final `_source_evidence_is_current()` preflight

A loader failure or Candidate mismatch returns `False`; source-preflight failure or mismatch also returns `False`. No success result can be produced from a false guard.

### Semantic-revision publication guard

`_revision_publication_is_current()` now performs:

1. `current_candidate_loader(candidate_path, repo_root)`
2. Fail-closed loader exception handling
3. Exact identity and ZIP-byte comparison
4. Final source preflight using canonical paths plus the Candidate baseline’s relevant paths

This matches the bounded repair objective and preserves the existing equality fields and public interfaces.

### Final source preflight

`_source_evidence_is_current()`:

* sets `allow_default_branch_fallback=False`;
* passes the captured source-manifest hash as `expected_source_hash`;
* returns `False` on the expected preflight exceptions;
* requires equality of branch, upstream, local HEAD, remote HEAD, remote-head disposition, and source-manifest hash.

### Deterministic tests

The new parameterized tests exercise both guard variants:

* `revision=False`: Review guard
* `revision=True`: semantic-revision guard

For the negative path, the loader changes the simulated source-manifest hash before returning an otherwise unchanged Candidate. The asserted result is `False`, and the asserted event order is:

```text
candidate_loader
source_preflight
```

For the positive path, source evidence remains unchanged; the result is `True` with the same loader-before-preflight order.

The tests directly instrument loader versus source-preflight order. The identity and ZIP comparisons between those events are established by exact production-source inspection rather than separate property-access events.

The two new tests are helper-level and do not themselves maintain a publisher write counter. The unchanged surrounding publisher contracts supply the side-effect closure:

* Candidate publication with a false guard removes the newly published Candidate and raises the stale condition.
* Review publication with a false or exceptional guard never returns `review_completed`; under the previously accepted fail-closed cleanup contract, non-authoritative evidence can be preserved when safe conditional deletion cannot be proven.

Accordingly, “publication zero” is verified as **zero successful or authoritative publication outcome**. Literal absence of every Review evidence pathname is not the current cleanup contract and was explicitly outside this repair’s scope.

### Public result preservation

The repair preserves the existing mappings:

| Path     | Guard/publisher outcome       | Application result                               |
| -------- | ----------------------------- | ------------------------------------------------ |
| Review   | Successful publication        | `ok/review_completed`                            |
| Review   | Proven stale                  | `stale/review_target_changed`                    |
| Review   | Fail-closed publication error | `blocked/review_publication_failed`              |
| Revision | Successful publication        | `ok/candidate_revised`                           |
| Revision | Source stale                  | `stale/revision_source_stale`                    |
| Revision | Publication failure           | Existing `blocked` or `rejected` classifications |

No status, reason, output key, details schema, publisher signature, Candidate field, Oracle boundary, or CLI option changed.

### Remaining concurrency boundary

The implementation is sequential, not atomic:

```text
Candidate snapshot and comparison
→ final source preflight
→ publisher completion
```

It does not claim to prevent mutations after the final source check or to provide a linearizable Candidate/source snapshot. That limitation is consistent with the bounded repair contract and does not establish a concrete P0/P1 defect in this review scope.

## 4. P0/P1 findings

**No P0 or P1 findings.**

The exact-head implementation closes the reported `planning-source-publication-toctou` window at the accepted guard boundary. I found no deterministic material merge, execution, public-contract, safety, or availability defect requiring correction in this PR.

## 5. Counts and final verdict

| Severity | Count |
| -------- | ----: |
| P0       |     0 |
| P1       |     0 |

# PASS

No patch, replacement ZIP, Candidate, repository file, branch, pull request, comment, review submission, or artifact was created, modified, deleted, or published during this review.
