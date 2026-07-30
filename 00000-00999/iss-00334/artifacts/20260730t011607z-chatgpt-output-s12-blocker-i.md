# S12 Blocker I — Issue 75 GraphQL Fixture Transport Amendment

## Admission

**GO — one transport-only amendment is admitted.**

Connector inspection confirmed `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, is identical to exact pushed HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`; default-branch fallback was not used. The exact HEAD contains the identified `api\ graphql*` external heredoc and the matching logical payload.

The dirty-worktree H closure and subsequent GraphQL stall are accepted as measured admission evidence supplied by the brief; they are not independently present in the pushed HEAD. 

## Sole Authorized Edit

Within `TestInitUpdate::test_issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads`, modify only the generated fake-`gh` `api\ graphql*` branch.

Replace its external heredoc with this exact generated-shell command:

```bash
builtin printf '%s\n' '{"data":{"repository":{"pullRequest":{"reviewThreads":{"nodes":[{"id":"RT_kw_unresolved","isResolved":false,"isOutdated":false,"comments":{"nodes":[{"id":"RTC_1","databaseId":301,"author":{"login":"codex"},"createdAt":"2026-06-08T01:08:00Z","body":"thread body should not duplicate old bodies"}]}},{"id":"RT_kw_resolved","isResolved":true,"isOutdated":false,"comments":{"nodes":[{"id":"RTC_2","databaseId":302,"author":{"login":"alice"},"createdAt":"2026-06-08T01:09:00Z","body":"resolved thread body"}]}},{"id":"RT_kw_outdated","isResolved":false,"isOutdated":true,"comments":{"nodes":[{"id":"RTC_3","databaseId":303,"author":{"login":"alice"},"createdAt":"2026-06-08T01:10:00Z","body":"outdated thread body"}]}}]}}}}}'
```

The JSON remains one argument to the fixed `'%s\n'` format. `builtin printf` removes the external child transport, `%s` performs no payload escape interpretation, and the format emits exactly one final newline.

## Frozen Boundaries

The only additional hunk is in the already-authorized `tests/unit/infra/test_init_update.py`. The effective changed-path allowlist remains exactly ten paths; no path may be added.

All other fake-`gh` branches, heredocs, helpers, assertions, caps, timeouts, retries, serializers, payloads, provider or dogfood assets, Prompt, Skill, canonical documents, Report, packaging, metadata, modes, and filesystem topology remain read-only. The H reviews-payload transport remains locked at 12,448 bytes and SHA-256 `2708c2a5fd2cb759fd9af56e1b7b614cf584f08155f808ee5392a56929fe04d7`.

The existing node’s return-code, review-status, inventory, totals, request identity, thread counts, body mode, caps, hashes, temporal filtering, truncation, empty limitations, and `gh`-call assertions remain unchanged. These assertions are already explicit at the exact HEAD.

## Red / Green Evidence Gate

**Red:** record that the exact Issue 75 node reaches the generated fake-`gh` GraphQL branch after issue comments, reviews, inline comments, and requested reviewers, then fails to terminate at the external GraphQL heredoc.

**Green:** after only the admitted replacement:

* The exact Issue 75 node terminates with return code `0` and passes.
* The `gh` log retains issue-comment, review, inline-comment, requested-reviewer, and GraphQL calls.
* All existing semantic assertions pass without modification.
* The exact ten-path guard, prior focused checks, file-owner tests, lint, distribution/projection checks, and explicit full regression pass.

A different measured blocker is not admitted by this amendment.

## Digest Gate

The pre-edit logical payload and post-edit emitted stdout must satisfy all four conditions:

| Property      |                                                       Locked value |
| ------------- | -----------------------------------------------------------------: |
| Length        |                                                        `720` bytes |
| SHA-256       | `21fc7f2e36a8eebe5875b4c3b9dfcbf8c42594555fc968b54873d68fac9c8244` |
| Final newline |                                                            present |
| Apostrophe    |                                                             absent |

Independent extraction from the exact HEAD and static evaluation of the authorized `builtin printf` command both produce those locked bytes. Any pre-edit apostrophe, byte inequality, digest mismatch, missing or duplicated newline, semantic drift, new changed path, or further stall is a stop condition; it does not authorize escaping, reformatting, another transport, or broader repair.

DISPOSITION: GO_BOUNDED_BLOCKER_I_ISSUE75_GRAPHQL_FIXTURE
