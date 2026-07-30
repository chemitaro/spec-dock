# S12 Blocker K — bounded transport amendment

## Source lock

GitHub connector inspection succeeded for `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`. The branch is identical to exact HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`; default-branch fallback was not used.

At that HEAD, the exact target node contains a distinct 21-comment external heredoc under `comments(last: 100)`, retains a separate 20-comment `else` payload, and already enforces the frozen status, count, timestamps, and GraphQL-query assertions.

## Admitted transport

Modify only `tests/unit/infra/test_init_update.py`, only within:

```text
TestInitUpdate::test_issue_75_pr_observation_review_collector_uses_latest_thread_comment_beyond_first_20
api\ graphql*
comments(last: 100)
first 21-comment payload
```

Replace only that payload’s external heredoc transport with:

```bash
builtin printf '%s\n' '<the identical 21-comment GraphQL JSON>'
```

The complete JSON must remain one single-quoted argument to the fixed `%s\n` format. No escaping or payload rewriting is authorized. The 20-comment `else` payload remains byte-for-byte untouched.

## Digest gate

The extracted logical payload must satisfy these values both before and after the edit:

| Property                   |                                                       Locked value |
| -------------------------- | -----------------------------------------------------------------: |
| Bytes excluding final LF   |                                                            `3,857` |
| Bytes including final LF   |                                                            `3,858` |
| SHA-256 including final LF | `d94f8d3141c0f4521b611728139fa217a5f904b4575b728c6592aa5dfb37db6a` |
| Final newline              |                                                            Present |
| Apostrophe                 |                                                             Absent |

Discovery of a pre-edit apostrophe, any digest or byte-count mismatch, reordered JSON, altered whitespace, or any final-newline difference is an immediate stop condition. 

## Frozen boundaries

The effective dirty-worktree allowlist remains exactly ten paths; this amendment adds no path. It authorizes no other fake-`gh` branch, heredoc, helper, assertion, timeout, retry, serializer, payload, production/provider/dogfood file, Prompt, Skill, canonical document, Report, packaging file, or metadata change.

Temporary files, command substitution, subshells, pipes, external preprocessing, reformatting, new files, deletion, rename, symlink changes, and mode changes remain forbidden.

## Red/Green evidence gate

**Red:** the supplied measurement records that the exact node exceeds 30 seconds outside the Codex sandbox and stalls at the first 21-comment external heredoc. This review admits that measured defect without broadening its diagnosis.

**Required Green, in order:**

1. The exact latest-thread node terminates and passes with return code `0`.
2. `review.status == "unresolved"`.
3. First-thread `comment_count == 21`.
4. Latest comment creation is `2026-06-08T01:30:00Z`.
5. Latest update and activity are `2026-06-08T01:31:00Z`.
6. The `gh` log includes `comments(last: 100)` and excludes `comments(first: 20)`.
7. Blockers H, I, and J focused Green and the exact ten-path guard pass.
8. File-owner tests, lint, distribution/projection checks, and an explicit full regression pass.

Any further measured blocker requires a separate JIT admission.

DISPOSITION: GO_BOUNDED_BLOCKER_K_LATEST_THREAD_GRAPHQL
