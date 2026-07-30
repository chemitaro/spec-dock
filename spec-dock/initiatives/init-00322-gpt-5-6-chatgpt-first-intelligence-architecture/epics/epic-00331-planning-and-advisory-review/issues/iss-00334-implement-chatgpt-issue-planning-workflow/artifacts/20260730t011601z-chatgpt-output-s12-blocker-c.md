# S12 Blocker C Shell-Usage Amendment

## Source lock and admission

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Exact source HEAD: `fd97aca1f005e2fe066a872343039c7e5b8889ca`
* Connector comparison: branch and exact HEAD are identical; default-branch fallback was not used.
* Decision: admit only the bounded shell-usage amendment below.

The current wait wrapper sends both `--help` and every shell-owned usage failure through `usage()`, whose first operation is the external `cat` heredoc; `fail_usage()` cannot reach exit `64` until that command returns.  The help path and invalid-head-SHA path likewise reach that same function before any Python invocation.  This makes the prior four-path contract internally unexecutable under the independently reproduced Red.

## Effective six-path allowlist

The changed-path guard must use `fd97aca1f005e2fe066a872343039c7e5b8889ca` as its base and permit exactly these six tracked modifications:

```text
tests/cli_runtime/test_authoring.py
tests/unit/infra/test_init_update.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
```

The first four retain their prior ownership. The last two are admitted solely for the usage-emission correction. This supersedes the prior declaration that both shell paths were read-only.

## Exact permitted shell change

In the provider `wait_pr_observation.sh` only:

* Replace the external `cat >&2 <<'USAGE' … USAGE` implementation inside `usage()` with `builtin printf '%s\n'` using literal arguments and a single stderr redirection.
* Emit exactly the existing usage lines, blank lines, ordering, spacing, and final newline.
* Preserve this first line exactly:

```text
usage: wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA [options]
```

* Do not introduce a command substitution, subshell, variable interpolation, external executable, or additional diagnostic.
* Make no other provider-shell change.
* Mechanically project the complete provider shell to the dogfood path and require byte identity.

The snapshot wrapper remains read-only; its separate, shorter external heredoc is not part of this defect.

## Unchanged boundaries

All prior Blocker A and B instructions and the Python last-chance validation remain unchanged. Do not change options, regexes, accepted values, exit codes, environment fields, Python invocation, trigger behavior, snapshot behavior, `gh`, output handling, polling, public usage text, Prompt, Skill, schemas, metadata, canonical Requirement/Design/Plan, Report, package configuration, executable bits, or any other path.

## Red and Green evidence

**Accepted Red:** the five-second process-group timeout terminates both inherited-stdin and `DEVNULL` reproductions; `--help` and invalid head SHA both time out; Bash trace stops at the external `cat`; no fake `gh` call occurs; Main independently reproduced both cases. The provider and dogfood shells are unchanged and byte-identical, and `bash -n` passes.

**Corrected pre-edit SHA requirement:**

```text
provider SHA-256:
e31e5f5a70809929cef7faabab900ced1d2f457636764c7dbe9d1eeb824e266f

dogfood SHA-256:
e31e5f5a70809929cef7faabab900ced1d2f457636764c7dbe9d1eeb824e266f
```

The prior packet’s comparison of a computed SHA-256 against `0ef1a4f282ac206489388ac74aeead73babfe82d` is superseded: that 40-character value is the Git blob SHA reported for both files, not a SHA-256 digest.   The previous mismatched check must not be retained.  After editing, record the new 64-character provider SHA-256 and require the dogfood SHA-256 to equal it.

**Required Green:**

* `--help`: exit `0`, empty stdout, unchanged usage on stderr, and no timeout.
* Each of WAIT-NF-01 through WAIT-NF-06: exit `64`, empty stdout, the exact usage first line on stderr, and no timeout.
* The inherited-stdin and `DEVNULL` reproductions both terminate normally.
* `gh`, trigger helper, snapshot helper, output mutation, and polling counts remain zero for invalid inputs.
* Provider and dogfood shell bytes are identical.
* `bash -n` passes for both shell paths.
* All previously required Blocker A/B/C focused, parity, file-owner, lint, and full-regression checks remain mandatory.

DISPOSITION: GO_BOUNDED_BLOCKER_C_SHELL_USAGE_AMENDMENT
