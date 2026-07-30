# S12 Blocker H Admission Amendment

## Admission and source lock

**GO — admit only the Issue 75 generated reviews-payload transport replacement.**

| Field                            | Locked value                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Repository                       | `chemitaro/spec-dock`                                                                                  |
| Branch                           | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                  |
| Exact pushed HEAD                | `fd97aca1f005e2fe066a872343039c7e5b8889ca`                                                             |
| Connector verification           | Branch and exact HEAD are identical; ahead `0`, behind `0`                                             |
| Default-branch fallback          | Forbidden and not used                                                                                 |
| Writable file for this amendment | `tests/unit/infra/test_init_update.py`                                                                 |
| Exact node                       | `TestInitUpdate::test_issue_75_pr_observation_review_collector_explicit_trigger_body_caps_and_threads` |

The exact pushed source contains the targeted generated fake-`gh` branch, its external reviews-payload heredoc, and the dynamically concatenated `12050`-character body.  The runtime measurements and admission boundaries are those supplied in the complete brief. 

## Admitted transport change

Only in the fake-`gh` case serving:

```text
api repos/owner/repo/pulls/13/reviews --paginate
```

replace:

```bash
cat <<'JSON'
<existing dynamically concatenated reviews payload>
JSON
```

with exactly one Bash builtin:

```bash
builtin printf '%s\n' '<the identical existing dynamically concatenated reviews payload>'
```

Preserve the existing Python string segments, `("x" * 12050)` concatenation, JSON bytes, ordering, and final newline. The payload must remain the argument to the fixed `'%s\n'` format; it must not become the format string.

Discovery of any apostrophe in the pre-edit logical payload is an immediate stop condition. It does not authorize escaping changes or a different transport.

## Frozen boundaries

The previously admitted dirty-worktree allowlist remains **exactly ten paths**. This amendment adds no path and authorizes one localized edit inside the already-allowed `tests/unit/infra/test_init_update.py`.

Do not change any other fake-`gh` case, heredoc, helper, assertion, cap, timeout, retry, serializer, payload, provider or dogfood runtime file, production file, Prompt, Skill, canonical document, Report, package surface, or metadata.

No temporary file, command substitution, subshell, pipe, external preprocessing, reformatting, new file, deletion, rename, symlink, or mode change is admitted. Any further measured blocker requires separate JIT admission.

## Red evidence

The pushed source confirms that the exact node launches the provider collector through the generated fake `gh`, and that the targeted reviews endpoint currently uses the external heredoc transport.

The supplied measured Red is accepted for this admission:

* the node stalls for more than 30 seconds both inside and outside the Codex sandbox;
* the trace stops at the second reviews-payload external `cat`;
* the logical payload is otherwise valid and deterministic.

This runtime stall was supplied as measured evidence; it was not independently re-executed through the read-only GitHub connector.

## Digest gate

Reconstruction from the exact pushed source confirms:

```text
logical byte length: 12448
SHA-256: 2708c2a5fd2cb759fd9af56e1b7b614cf584f08155f808ee5392a56929fe04d7
final newline: present
apostrophe: absent
```

The same four facts must be recorded after the edit against the bytes emitted by the new builtin transport. Any length, digest, ordering, content, or final-newline mismatch is a stop condition. Digest verification is evidence only and must not add or modify repository assertions.

## Required Green evidence

The exact node must terminate and pass while preserving all existing semantics:

* return code `0`;
* `review.status == "unresolved"`;
* exact status inventory through `dismissed`;
* all-total `8`, review-request total `1`, Codex-authored total `6`;
* exact Codex review request preserved;
* unresolved/resolved/outdated threads `1/1/1`;
* body mode `trigger-window-truncated`;
* caps `12000`, `120000`, `50`, omitted `0`;
* every signal contains `body_sha256`;
* same-timestamp body included, old trigger excluded, at least one body truncated;
* limitations empty.

The existing assertions already lock the totals, request inventory, thread counts, body caps, hashes, trigger filtering, truncation, and empty limitations.  The `gh` log must still contain issue comments, reviews, inline comments, and GraphQL calls.

Completion additionally requires the exact ten-path guard, all previously required focused checks, file-owner tests, lint, distribution/projection checks, and explicit full regression. Green is a post-edit gate and is not claimed by this admission.

DISPOSITION: GO_BOUNDED_BLOCKER_H_ISSUE75_REVIEWS_FIXTURE
