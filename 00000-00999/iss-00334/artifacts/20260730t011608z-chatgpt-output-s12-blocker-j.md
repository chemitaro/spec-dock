# S12 Blocker J — S100 GraphQL Fixture Transport Amendment

## Admission

Repository access succeeded. Branch `iss-00334-implement-chatgpt-issue-planning-workflow` resolves identically to exact pushed HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`; default-branch fallback was not used. The inspected test contains the specified Bash fake-`gh` `api\ graphql*` branch, external GraphQL heredoc, and unchanged semantic assertions.

Admit exactly one transport substitution inside:

```text
tests/unit/infra/test_init_update.py
TestInitUpdate::test_issue_187_s100_missing_current_completion_signal_preserves_pending_review
api\ graphql*
```

Replace only the external `cat <<'JSON' … JSON` transport with generated Bash equivalent to:

```bash
builtin printf '%s\n' '<the identical GraphQL JSON>'
```

The format is fixed, and the complete JSON payload remains exactly one argument. Any Python-literal escaping may serve only to emit the exact generated Bash format `%s\n`; it must not alter payload bytes.

## Digest gate

The inspected logical payload is:

```text
JSON bytes excluding final LF: 518
JSON bytes including final LF: 519
SHA-256 including final LF: c16f67535bbbd255c1e4bd59f7a82cd5c49f031e04fe1fc790f7857d18e5bd3e
Final newline: present
Apostrophe: absent
```

The payload visible at HEAD is the frozen two-thread GraphQL response.

Before and after editing, re-extract the generated fake-`gh` payload and require all five properties above. A pre-edit apostrophe, byte-count difference, digest difference, ordering change, or missing final newline is an immediate stop condition.

## Frozen boundary

The effective changed-path allowlist remains exactly ten paths; this amendment adds none. No other fake-`gh` branch, heredoc, helper, assertion, timeout, retry, serializer, payload, provider/dogfood/production asset, Prompt, Skill, canonical document, Report, package metadata, mode, symlink, rename, deletion, or new file is admitted. No temporary file, command substitution, subshell, pipe, or external preprocessing is permitted. 

## Red and required Green

**Red evidence accepted:** the exact S100 node stalls beyond 30 seconds along the measured path `pytest → fetch_pr_review_snapshot.sh → generated fake gh → api graphql → external cat heredoc`. This admission changes only that measured transport.

**Required Green:** the exact node must terminate and return `0`, while preserving:

* lifecycle `pending`; completion signal `none`;
* empty selected review, review-comment, and thread IDs;
* `no_completion_evidence`: present `false`, category `pending_review`, pending-review-present `true`, promotes-top-level-status `false`;
* recommended action not `merge_prepared`;
* fetched thread IDs exactly `["RT_human", "RT_codex_unrelated"]`;
* selected thread IDs empty;
* unresolved thread IDs exactly both fetched IDs.

Those assertions are already present and must not be weakened.

After the exact-node Green, retain the H/I focused Green and exact ten-path guard, then run the file-owner tests, lint, distribution/projection checks, and explicit full regression. Any additional measured blocker requires separate JIT admission.

DISPOSITION: GO_BOUNDED_BLOCKER_J_S100_GRAPHQL_FIXTURE
