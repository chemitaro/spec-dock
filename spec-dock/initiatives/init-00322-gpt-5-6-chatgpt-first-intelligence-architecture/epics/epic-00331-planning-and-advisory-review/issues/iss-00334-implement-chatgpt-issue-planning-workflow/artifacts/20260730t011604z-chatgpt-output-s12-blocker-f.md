# S12 Blocker F — Bounded Admission Amendment

## Source lock

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Exact pushed HEAD: `fd97aca1f005e2fe066a872343039c7e5b8889ca`
* GitHub connector comparison: branch and exact HEAD are identical; ahead `0`, behind `0`.
* Default-branch fallback: forbidden and not used.
* The reported Red outcomes and timings are measured evidence supplied by the admission brief; they were not independently rerun during this read-only review. 

## Exact ten-path lock

The effective write allowlist is:

1–8. The previously admitted **exact Blockers A–E eight-path set**, incorporated unchanged by reference. No member may be removed, substituted, or granted broader ownership. It already includes:

```text
tests/unit/infra/test_init_update.py
```

9–10. Exactly these two new paths:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
```

The resulting cardinality must be exactly `10`. Any other changed path is a guard failure.

## Admitted transports

### F1 — pending snapshot fixture

Inside only:

```text
tests/unit/infra/test_init_update.py
```

and only within:

```text
TestInitUpdate::test_issue_187_wait_preserves_actions_pending_with_informational_supplemental_permission
```

replace the single generated snapshot-shell:

```bash
cat <<'JSON'
...
JSON
```

with one:

```bash
builtin printf '%s\n' ...
```

invocation using mechanically escaped literal JSON line arguments. The pushed source contains the exact Bash fixture, payload, unchanged one-second timing arguments, and expected running-state assertions.

Locked F1 payload gates:

```text
logical length: 1365 bytes
SHA-256: e9f124fb151c5e296e1d160e373b999dfe905a3e6381d771f4c47fe260ecc243
final newline: present
```

No assertion, timeout, polling value, trigger value, timestamp, argument, or production file may change.

### F2 — checks snapshot wrapper usage

The provider is the sole editing authority. Replace only its `usage()` external heredoc with one `builtin printf '%s\n'` invocation, mechanically preserving every logical line and using exactly one stderr redirection. The pushed provider currently uses the bounded `cat >&2 <<'USAGE'` transport and validates before invoking Python.

Afterward, mechanically copy the complete provider file to the dogfood path. The pushed provider and dogfood files are byte-identical before repair.

Locked F2 usage gates:

```text
logical length: 703 bytes
SHA-256: 8841a7830181bd4f8af5adba577ade767efc2a50879d2bbbf872763fbd065e7f
final newline: present
```

Locked whole-file pre-edit gate for both copies:

```text
6043ceef93084c7fba3349eeae5066d616808880cfeb49adef05cde2929707fd
```

The exact Red node exercises invalid repository, PR, and SHA cases and requires exit `64`, no `gh` invocation, and no permission-denied diagnostic.

## Frozen boundaries

Only the two transports above are admitted. No other heredoc, helper, assertion, timeout, retry, option, regex, accepted value, exit code, public text, JSON, metadata, `gh` logic, Prompt, Skill, canonical document, Report, packaging file, or path may change.

No temporary file, command substitution, subshell, pipe, external preprocessing command, payload reformatting, new file, deletion, rename, symlink, or mode/topology change is permitted. Other inventoried heredocs remain untouched. Any additional measured blocker requires a separate JIT admission.

## Mandatory Green and digest gates

* F1 exact node terminates and passes under the unchanged one-second contract:

  * exit `0`;
  * `ci.status=running`;
  * normalized status `running` or `timeout`;
  * next action `wait_or_resume`;
  * no blocking `github_token_permission_denied`.
* F1 payload length, SHA-256, and final-newline gates pass before and after.
* F2 exact node completes all three invalid cases:

  * exit `64`;
  * zero `gh` calls;
  * unchanged usage and diagnostics;
  * no `github_token_permission_denied`.
* F2 usage length, SHA-256, and final-newline gates pass before and after.
* Both F2 files pass `bash -n`.
* Provider and dogfood post-edit bytes and whole-file SHA-256 values are equal.
* Their common post-edit SHA-256 differs from `6043ceef93084c7fba3349eeae5066d616808880cfeb49adef05cde2929707fd`.
* The exact ten-path guard passes with no mode or topology change.
* All previously required focused, file-owner, lint, distribution/projection, and explicit full-regression checks remain mandatory.
* Green is a post-edit requirement; this admission does not claim it has already been observed.

DISPOSITION: GO_BOUNDED_BLOCKER_F_TWO_TRANSPORTS
