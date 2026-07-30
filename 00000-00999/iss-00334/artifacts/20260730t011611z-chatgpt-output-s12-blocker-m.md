# S12 Blocker M Amendment

## Source lock

* Repository: `chemitaro/spec-dock`
* Mandatory branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Exact pushed HEAD: `fd97aca1f005e2fe066a872343039c7e5b8889ca`
* GitHub connector inspection confirmed that the mandatory branch resolves identically to the required HEAD: ahead `0`, behind `0`.
* Default-branch fallback was not used.
* The attached Blocker M brief is the complete defect-only admission contract. 
* At the pushed HEAD, the named Issue 170 test contains the four identified external heredoc transports, the existing reviews transport, and the four required assertions unchanged.

## Exact 12-path boundary

* No path is added to the previously admitted Blocker L allowlist.
* The effective dirty-set boundary remains exactly 12 tracked modified paths.
* Blocker M may modify only an existing hunk within:
  `tests/unit/infra/test_init_update.py`
* Within that file, the writable scope is only:
  `TestInitUpdate::test_issue_170_pr_review_collector_excludes_resolved_thread_inline_comments_from_status`
* Any untracked path, added path, deletion, rename, symlink change, mode change, or thirteenth dirty path is a stop condition.
* The pre-edit whole-file SHA-256 must be exactly:
  `6b0388054e656a7481a2a652ad9479708c37b8d52101794d23253b7e1aa3fad3`

## Admitted fixture transport

Admit exactly four transport-only replacements in the named Issue 170 fixture:

```text
cat <<'JSON' ... JSON
```

to:

```text
builtin printf '%s\n' '<exact existing single-line JSON>'
```

The admitted replacements are limited to:

| Dispatch branch | Bytes including final LF | SHA-256                                                            |
| --------------- | -----------------------: | ------------------------------------------------------------------ |
| issues comments |                       96 | `81a117a68a62ca34ffd668d62d5212b038c057c7b796e02a460f4e40bb9928bb` |
| pull comments   |                      424 | `27fc86d8e707980ad6d296c3ef4b35ad49a8fdc77568c6303735ecd57cb27ea6` |
| pull            |                       48 | `f22bdb4c127fe8126fe93d0d4ea76342c05020ab08513d5cc7a0015ee6cdc50e` |
| GraphQL         |                      552 | `43ecf45d36be417ccbf39a39aa46ad058fb2c57ba35c87a4c314ea9873509f22` |

Each replacement must preserve the exact existing JSON bytes and append exactly one final LF. No JSON content, ordering, whitespace, dispatch condition, or branch structure may change.

The production collector invokes the transports synchronously in the required order: issues comments, reviews, pull comments, pull, then GraphQL.

## Frozen boundaries

* Blockers A–L and their exact previously admitted changes remain frozen.
* The reviews branch remains unchanged.
* Production source, provider and dogfood wrappers, helpers, timeouts, retries, assertions, test topology, and fixture behavior are read-only.
* No other fixture node or heredoc may be converted.
* No bulk transport conversion is admitted.
* Prompt, Skill, canonical documents, Report, metadata, dependencies, and every other path remain read-only.
* The existing assertions must remain byte-for-byte unchanged:

  * `review.status == "none"`
  * `thread_state == ["resolved", "outdated"]`
  * resolved count `1`
  * outdated count `1`

## Red and Green gates

The measured Red is sufficient for this bounded admission: the file-owner run passed 401 tests, reported no failure, and then stalled for more than 90 seconds at the named Issue 170 node, whose first synchronous transport is the external issues-comments heredoc.

Green requires all of the following:

1. The exact Issue 170 node exits successfully within a bounded timeout.
2. All four existing assertions remain unchanged and pass.
3. All four payloads retain the specified byte counts, SHA-256 values, and final LF.
4. Dispatch branches and call order remain issues comments → reviews → pull comments → pull → GraphQL.
5. The dirty set remains exactly 12 tracked modified paths with no topology or mode change.
6. Focused Ruff, `git diff --check`, and the existing Blocker L wrapper parity and contract checks pass.
7. The file-owner test resumes only after the exact node passes. Any subsequent measured stall or failure requires an immediate stop and a fresh JIT admission; no additional repair is authorized under Blocker M.

DISPOSITION: GO_BOUNDED_BLOCKER_M_ISSUE170_FIXTURE
