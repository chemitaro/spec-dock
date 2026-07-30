# S12 Blocker L Amendment

## Source lock

Repository access succeeded for `chemitaro/spec-dock`. The mandatory branch `iss-00334-implement-chatgpt-issue-planning-workflow` resolves to exact pushed HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`; default-branch fallback was not used.

At that HEAD, the provider and dogfood review-snapshot wrappers have the same Git blob and contain the same external `cat >&2 <<'USAGE'` transport in `usage()`.   The measured Blocker L contract and requested transport-only boundary are accepted as the complete amendment brief. 

## Exact 12-path allowlist

The effective dirty-worktree allowlist is locked to exactly:

```text
tests/cli_runtime/test_authoring.py
tests/unit/infra/test_init_update.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh
.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
```

Blocker L adds only the final provider/dogfood pair. The prior ten paths and all Blocker A–K decisions remain frozen.

## Admitted usage transport

Only the provider wrapper may be edited authoritatively:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
```

Replace only its `usage()` external heredoc with one Bash-builtin invocation:

```bash
builtin printf '%s\n' <the 13 exact current usage lines as literal arguments> >&2
```

Each existing blank line is represented by an empty literal argument. Preserve line text, ordering, spacing, and the final newline exactly. Then mechanically copy the complete provider file to:

```text
.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh
```

Both files must remain mode `100755`.

## Frozen boundaries

No other line in either wrapper may change. Parsing, options, accepted values, validation, exit codes, diagnostics, Python invocation, environment, `gh` behavior, output, and every later execution path remain unchanged.

No other path, heredoc, helper, test, assertion, timeout, retry, payload, provider/dogfood file, Prompt, Skill, canonical document, Report, packaging file, or metadata may change. Temporary files, command substitution, subshells, pipes, external preprocessing, new files, deletions, renames, symlinks, and mode changes are forbidden.

## Red, Green, and digest gates

The admitted Red is the measured exact node:

```text
TestInitUpdate::test_issue_197_pr_review_snapshot_wrapper_usage_exits_before_gh
```

It exceeds 30 seconds outside the Codex sandbox at the unchanged external usage heredoc.

Before editing, both wrappers must match:

```text
whole-file SHA-256: 668764cdbb6a2935d2f7d038e152a84a4d85abac93ae9b404779ee4b55b2556c
mode:                  100755
provider/dogfood:      byte-identical
```

The logical usage payload gate is:

```text
length:                549 bytes
SHA-256:               be090795991e825bfb6b8f9667003bc9ec5a245fce82b93fb3df7f69578fbd56
final newline:         present
```

Required Green:

* Both wrappers pass `bash -n`.
* Invalid `--repo bad --pr 13` exits `64`, emits empty stdout and the exact 549-byte usage on stderr, and makes zero `gh` calls.
* `--help` exits `0`, emits empty stdout and the same exact usage on stderr, and makes zero `gh` calls.
* The exact Issue 197 node terminates and passes both cases.
* Post-edit provider and dogfood bytes and whole-file SHA-256 values are equal.
* Their post-edit whole-file SHA-256 differs from the pre-edit value.
* Mode remains `100755`; no topology change occurs.
* The exact 12-path guard, all prior focused checks, file-owner tests, lint, distribution/projection checks, and explicit full regression pass.
* Any additional measured blocker requires a separate JIT admission.

DISPOSITION: GO_BOUNDED_BLOCKER_L_REVIEW_WRAPPER_USAGE
