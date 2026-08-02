# Fresh Red Team exact-head review

## Verdict

**PASS**

* **P0 findings: 0**
* **P1 findings: 0**

The three bounded repairs—P1-A publication revalidation, P1-B descriptor-relative prompt-source reads, and P1-C non-destructive rules-link rollback—satisfy the supplied review contract at the exact required HEAD. The explicitly excluded blocker-vocabulary observation was not reopened. 

## 1. Exact identity and model-selection evidence

| Field                    | Verified value                                                                                                                                                                     |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                                                                                                                              |
| Required branch          | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                                                                              |
| Pull request             | `#351`                                                                                                                                                                             |
| PR state                 | `open`, not merged                                                                                                                                                                 |
| PR head branch           | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                                                                              |
| Exact reviewed HEAD      | `cccd79263cfed9ba8f05c9861c1cf22d6f825fff`                                                                                                                                         |
| Branch-to-HEAD relation  | `identical`; ahead `0`, behind `0`                                                                                                                                                 |
| Default-branch fallback  | Not used                                                                                                                                                                           |
| Review role              | Fresh Red Team, exact-head, read-only                                                                                                                                              |
| Active model             | GPT-5.6 Pro                                                                                                                                                                        |
| Model-selection evidence | Current thread runtime model identity. No Oracle, wrapper, or separate model-selector process was invoked, so no additional requested/resolved/verified selector tuple is claimed. |

GitHub reports PR #351 as open and binds its head branch and head SHA to the required values.  The exact commit was independently opened through the connector.

## 2. Inspected material and exact-head binding

### Provider, dogfood, and attached-source binding

The uploaded sources and tests were hashed as Git blobs and matched the connector-returned blobs at the required HEAD:

| Surface                                         |                       Exact Git blob SHA-1 | Result                        |
| ----------------------------------------------- | -----------------------------------------: | ----------------------------- |
| Provider and dogfood `issue_planning.py`        | `2ffbba91352499122d97b4b103252ee4b90e3282` | Byte-identical                |
| Provider and dogfood `issue_planning_prompt.py` | `b743e3ca3ddf337a7fa9d74e62924e953753e6c0` | Byte-identical                |
| Provider and dogfood `import_file_artifact.py`  | `3124ca517e6726d7984c5c59c9ed8123889ddbca` | Byte-identical                |
| `test_issue_planning.py`                        | `b098f9e396f8bcfca32395ae8ed0904557171ff1` | Attachment matches exact HEAD |
| `test_issue_planning_prompt.py`                 | `80a9719786de4b3a728c7a0a2afaf7572de83ce2` | Attachment matches exact HEAD |
| `test_import_file_artifact.py`                  | `6541c53d09a97c05116e3331c6c85813906ff4f1` | Attachment matches exact HEAD |

The provider `issue_planning.py` blob and dogfood projection report the same SHA.   The same is true for the prompt source.   The artifact-import pair also matches.

The attached provider sources and tests inspected were:      

The attached Blue packet also matches the file committed at the exact reviewed HEAD. It is correctly treated as a repair plan bound to the earlier source head `c8e1ac2c…`, not as current-head implementation evidence. 

### Repair-delta scope

The connector comparison from the Blue packet’s source head `c8e1ac2c75502d94d47d097d4a6ee8e63b698a9f` to the reviewed HEAD shows twelve changed paths:

* Three provider sources.
* Three byte-identical dogfood projections.
* Three focused unit-test files.
* `report.md`.
* One observation JSON.
* The Blue work packet.

No ports, domain contracts, CLI, Oracle adapter, publisher interface, canonical Requirement/Design/Plan, or P2 classifier changed in this repair delta.

The canonical requirement continues to require same-branch/HEAD/source-manifest verification before Candidate or Review publication and stale rejection on drift.  The design keeps public commands, Candidate controls, Human authority, and publication semantics unchanged.

## 3. Acceptance analysis

### P1-A — Planning publication opposite-side TOCTOU: PASS

Both private publication guards now implement the required sequence on Candidate-bearing paths:

1. Load and validate the current Candidate against the captured Candidate.
2. Run exactly one source preflight.
3. Load and validate the Candidate again.

`_candidate_view_is_current()` fails closed on loader exceptions and requires both `identity` and exact `zip_bytes` equality. `_source_evidence_is_current()` likewise closes preflight exceptions to `False`. The review and semantic-revision paths therefore reject:

* Candidate identity drift before the first load.
* Candidate ZIP-byte drift before the first load.
* Source drift caused during the first Candidate load.
* Candidate identity drift during source preflight.
* Candidate ZIP-byte drift during source preflight.
* Loader or source-preflight failure.

The source implements the required Candidate → source → Candidate ordering without changing the existing review or revision command-result schemas.

The exact-head tests cover both review and revision, identity and ZIP drift, source mutation during the first loader call, preflight exceptions, exact event ordering, and the no-drift positive case.

This is correctly a **sequential revalidation sandwich**, not a repository lock or linearizable joint snapshot. A mutation after the second Candidate validation remains outside the stated guarantee.

### P1-B — Planning prompt ancestor symlink/pathname race: PASS

Canonical and relevant prompt-source bytes are no longer obtained from the path returned by `_safe_source_file()`.

The source now:

* Retains the existing lexical, credential-like-path, containment, and symlink checks.
* Opens the repository root with `O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`.
* Compares root `lstat`/`fstat`/post-open `lstat` identity.
* Traverses every intermediate component relative to an already-open directory descriptor.
* Opens the final component with `O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC`.
* Requires a regular final file.
* Reads bytes through `os.read()` from the opened descriptor.
* Preserves existing relevant-file and aggregate byte limits.
* Uses no `Path.read_bytes()` or resolved-path byte-reading fallback for these source attachments.
* Closes all acquired descriptors.
* Fails closed when required flags or descriptor-relative capability are unavailable, or when traversal/opening fails.

Consequently, replacing a validated source ancestor with a symlink cannot redirect the read to repository-external bytes: traversal either fails on `O_NOFOLLOW`, or continues from a descriptor already bound to the original directory.

The focused tests replace the Issue ancestor with an outside-directory symlink immediately after pathname validation and require a content-free failure without the outside sentinel. They also reject pathname source reads while preserving exact attachment names, UTF-8 byte ordering, source set, and source bytes.

Prompt body construction, output expectations, attachment labeling, GitHub binding, and Oracle transport boundaries remain unchanged.

### P1-C — Rules-link rollback ownership race: PASS

`_rollback_bound_rules_link()` performs no pathname unlink, even when the current `rules.md` tuple exactly matches the captured device/inode/mode/ctime tuple. The helper explicitly recognizes that this tuple cannot prove ownership at the unlink instant and therefore retains the entry.

This closes the same-identity/same-ctime replacement case and preserves:

* Wrong-target replacement links.
* Broken replacement links.
* Alternate links to the expected rules source.
* Replacement during creation.
* Replacement after setup.
* Reused-inode replacement with a new ctime.
* Same observable identity and ctime.
* Publisher-call count zero on setup failure.
* The existing `artifact_setup_failed` and `not_committed` envelope.

The exact-head tests cover all six creation/after-setup variants and directly make any `os.unlink` call fail in the same-identity case.

The normal opaque-file import positive path and the separate fresh-directory rollback path remain present and unchanged in the exact-head test file. 

## 4. Formal P0/P1 findings

| Stable ID | Severity | Location | Mechanism                        | Concrete impact | Minimal fix |
| --------- | -------- | -------- | -------------------------------- | --------------- | ----------- |
| None      | P0       | —        | No concrete P0 defect identified | —               | —           |
| None      | P1       | —        | No concrete P1 defect identified | —               | —           |

## 5. Evidence limitations and unverified claims

GitHub Actions reported successful exact-head runs for both `CI` and `Provider CI`; the Provider job included static analysis and the provider pytest suite. Those workflow conclusions were inspected but were not used as a substitute for source review.

I did not independently execute the repository test suite in this read-only connector review. Test-pass counts recorded in the report or Blue packet therefore remain observed project evidence rather than independently reproduced results.

The verdict is limited to the three P1 repairs and directly affected source, tests, projections, and evidence surfaces specified by the review contract. It is not a fresh review of every one of the PR’s broader feature changes.

## 6. Read-only declaration

No repository, branch, pull request, report, artifact, Candidate ZIP, replacement ZIP, test, source file, or attached file was changed. No patch or Candidate was generated.
