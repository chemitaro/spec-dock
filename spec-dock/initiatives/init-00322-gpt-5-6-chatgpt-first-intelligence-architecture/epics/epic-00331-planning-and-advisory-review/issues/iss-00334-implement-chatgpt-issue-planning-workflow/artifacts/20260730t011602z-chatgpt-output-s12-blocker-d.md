# S12 Blocker D — Trigger Shell Admission Amendment

## Admission decision and source lock

The effective repair scope may expand from six paths to exactly eight paths. GitHub connector inspection resolved `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, as identical to exact pushed HEAD `fd97aca1f005e2fe066a872343039c7e5b8889ca`; default-branch fallback was not used. The inspected commit identity is consistent with the bounded admission brief.  

At that HEAD, the provider trigger shell uses the external `cat` usage heredoc and the `python3 -` source heredoc described by the Red evidence. The dogfood copy has the same Git blob ID, confirming byte identity at the inspected source state.

## Exact eight-path effective allowlist

```text
tests/cli_runtime/test_authoring.py
tests/unit/infra/test_init_update.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh
.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh
```

The first six paths remain limited to their already-admitted Blocker A/B/C changes. Blocker D adds only the final two trigger-shell paths. No ninth path, new file, deletion, rename, symlink, executable-bit change, packaging change, or generated metadata change is admitted.

## Exact permitted Blocker D changes

The provider trigger shell is the sole editing authority.

1. Replace only the `usage()` external `cat` heredoc with one `builtin printf '%s\n'` invocation using literal arguments and exactly one stderr redirection. Every existing usage line, empty line, character, order, and terminal newline must remain byte-identical.

2. Replace only the `python3 - <<'PY' … PY` transport with a Bash-builtin-held literal source, using `builtin printf -v` or an equivalently byte-preserving builtin-only construction, followed by:

   ```text
   python3 -c "$python_source"
   ```

   The logical Python source supplied to `-c` must equal the current heredoc body byte-for-byte, including indentation, blank lines, ordering, and final newline. The six existing `TRIGGER_*` environment assignments must remain unchanged and attached to the same Python invocation.

3. Mechanically copy the complete provider trigger-shell bytes to the dogfood path. No independent dogfood edit is permitted.

No temporary file, new command substitution, new subshell, external preprocessing command, generated Python file, or alternate interpreter transport is admitted. Any other trigger-shell change is a stop condition.

## Frozen behavior and boundaries

All options, regexes, accepted values, exit codes, usage text, environment values, instruction validation, hashing, metadata, JSON schema, `gh` argument vectors, recovery behavior, stdout/stderr behavior, and side-effect ordering remain unchanged.

For a missing instruction, preserve the current `missing_plain_fallback` body and JSON assertions exactly. “Plain” means that no instruction text is included; it is not authority to replace the current metadata-bearing fallback body with a one-line comment. The inspected source and tests require the current source path, fallback status, reviewed HEAD metadata, and resulting payload to remain unchanged.

Valid instructions must retain the existing instruction body and SHA-256 metadata. Empty, non-UTF-8, oversized, or unreadable instructions must retain the existing `human_gate` result and make no POST. Invalid shell-owned inputs must return `64`, emit the exact usage text on stderr, call no `gh`, and produce no side effect. The existing tests already encode these behaviors and must not be edited for Blocker D.

Prompt, Skill, canonical Requirement/Design/Plan, Report, tests, Python helpers, public commands, packaging logic, and every other path remain read-only.

## Red and required Green

The supplied Red evidence is admitted as runtime evidence but was not independently rerun in this review:

* Full file-owner execution: `6 failed, 553 passed, 1 skipped`, interrupted after `1700.81s`.
* The six named Issue 244 trigger nodes timed out through the valid Python-heredoc path.
* The Issue 176 invalid-input node failed to terminate through the usage heredoc path.

Green is required after the bounded repair and is not yet claimed:

* All six named Issue 244 nodes pass within their existing 10-second limits.
* `test_issue_176_s01_trigger_helper_rejects_invalid_inputs_before_gh` terminates, returns `64`, emits unchanged usage on stderr, and records zero `gh` calls.
* Existing valid, missing, and invalid instruction assertions pass without test changes.
* Provider and dogfood trigger-shell bytes compare equal.
* `bash -n` passes for both trigger shells.
* Prior Blocker A/B/C focused checks, file-owner tests, lint, distribution/projection checks, and full regression all remain mandatory.

## Corrected SHA requirements

The attached evidence records the two pre-change trigger shells as SHA-256:

```text
69b6d0566cc744e80a53ab303924a356519b5074fe386bed3db1ff8f5f3f2945
```

GitHub connector inspection independently confirms that both current files share Git blob ID `c4cb45dc09b21f7553159b71712cf24f1a875302`; the SHA-256 value above remains brief-provided pre-change evidence.

Because the admitted transport changes alter whole-file bytes:

* `69b6d056…` must not be reported as the post-repair whole-file SHA-256.
* Compute a new SHA-256 separately for provider and dogfood after projection.
* The two new whole-file SHA-256 values must be identical and must differ from the pre-change value.
* The extracted logical Python-program SHA-256 must be identical before and after the transport conversion.
* The captured usage stderr bytes, including the final newline, must be identical before and after the conversion.

Any provider/dogfood digest mismatch, embedded-Python digest mismatch, or usage-byte mismatch is a stop condition.

DISPOSITION: GO_BOUNDED_BLOCKER_D_TRIGGER_SHELL_AMENDMENT
