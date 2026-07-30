# S12 Blocker E Admission Amendment

## Source lock and admission

| Field                   | Locked value                                               |
| ----------------------- | ---------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                      |
| Branch                  | `iss-00334-implement-chatgpt-issue-planning-workflow`      |
| Exact pushed HEAD       | `fd97aca1f005e2fe066a872343039c7e5b8889ca`                 |
| Connector result        | Branch and exact HEAD are identical; ahead `0`, behind `0` |
| Default-branch fallback | Not used                                                   |
| Decision                | **GO — two transport-only fixture repairs**                |

The exact pushed source contains the E1 generated `python3 - … <<'PY'` transport and reads only `sys.argv[1]` and `sys.argv[2]`; it also contains the E2 generated checks script using `cat <<'JSON'`.

The failure timings, dirty-worktree payload digests, and process observations below are supplied measured evidence from the admission brief; they were not independently rerun through the read-only connector. 

## Authorized transport amendments

Only `tests/unit/infra/test_init_update.py` may gain the following two changes.

### E1 — Issue 176 resume snapshot fixture

In `TestInitUpdate::_issue_176_write_wait_mode_scripts`, replace only:

```bash
python3 - "$trigger_id" "$trigger_created_at" <<'PY'
<existing Python payload>
PY
```

with:

```bash
builtin printf -v python_source '%s\n' \
  <each existing logical Python line as one mechanically escaped literal argument>
python3 -c "$python_source" "$trigger_id" "$trigger_created_at"
```

Mandatory construction rules:

* Generate the arguments mechanically from the current dirty-worktree payload; do not retype or reformat it.
* Represent every logical line as one argument and every blank line as an empty argument.
* Use a fixed `'%s\n'` format. Payload text must never become the format string.
* Escape any literal single quote using the standard Bash single-quote break-and-resume sequence.
* Preserve `"$trigger_id"` as `sys.argv[1]` and `"$trigger_created_at"` as `sys.argv[2]`.
* The change from `sys.argv[0] == "-"` to `sys.argv[0] == "-c"` is admissible because the inspected payload does not read `sys.argv[0]`, `__file__`, or script-relative state.
* Do not change the generated JSON, logging, helper invocation count, timeout, or assertions. The existing test requires one snapshot invocation, no trigger-helper invocation, and exact trigger metadata `777` / `2026-06-09T02:03:04Z`.

### E2 — Issue 187 informational supplemental-permission fixture

In `TestInitUpdate::test_issue_187_snapshot_propagates_actions_pass_with_informational_supplemental_permission`, replace only the first generated checks-shell transport:

```bash
cat <<'JSON'
<existing JSON payload>
JSON
```

with:

```bash
builtin printf '%s\n' \
  <each existing logical JSON line as one mechanically escaped literal argument>
```

Mandatory construction rules:

* Derive the literal arguments mechanically from the current dirty-worktree JSON.
* Keep the fixed `'%s\n'` format and preserve all payload bytes, ordering, indentation, blank lines, and the final newline.
* Do not alter the review fixture, fake `gh`, snapshot wrapper, JSON semantics, or assertions.
* The existing test must continue to produce `passed` at the CI, normalized, and overall levels, recommend `merge_prepared`, and emit no blocking `github_token_permission_denied` limitation.

## Mandatory byte-identity gates

Calculate each digest over the logical UTF-8 payload only: heredoc delimiters excluded and the final newline included.

| Fixture   |        Length | SHA-256                                                            | Final newline |
| --------- | ------------: | ------------------------------------------------------------------ | ------------- |
| E1 Python | `1,168` bytes | `dfb8fea53589eb583e0392a314b52ad6e6960fea9b8c73a1ab4e669112e07e0a` | Present       |
| E2 JSON   |   `870` bytes | `622cc01806ad0023035ea862317377163f09d43949c24b34e62fbc5c44cacfcf` | Present       |

These values must be checked both immediately before and immediately after editing. GitHub exposes the pushed HEAD, not the integrated dirty worktree carrying prior Blockers A–D; therefore any pre-edit mismatch is a stop condition rather than permission to adopt the pushed-HEAD payload or recalculate a new baseline.

## Frozen boundaries

* Preserve the previously frozen exact eight-path changed set. No ninth path may appear.
* Make no other heredoc conversion, including any of the remaining 562 inventoried records.
* Do not change another helper, assertion, timeout, retry policy, payload, production/provider/dogfood file, Prompt, Skill, canonical document, Report, packaging file, or metadata file.
* No temporary file, command substitution, subshell, pipe, external preprocessing command, payload reformatting, or assertion weakening is authorized.
* No new file, deletion, rename, symlink, executable-bit change, or other mode change is authorized.
* If another measured heredoc blocker appears, stop and obtain a separate JIT admission.

## Red and Green evidence

Accepted Red evidence:

* E1 consistently completed in approximately `2.66s`, missed the unchanged two-second product deadline, and produced `snapshot_poll_timeout` with missing trigger metadata.
* E2 made no progress for `43.48s`; bounded process inspection located the stall at its first external heredoc with empty stdout and stderr. 

Required focused Green:

```bash
uv run pytest -q --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_176_s02_wait_resume_uses_explicit_trigger_without_helper \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_snapshot_propagates_actions_pass_with_informational_supplemental_permission
```

Green is valid only when:

* E1 passes under the unchanged `--timeout-seconds 2` contract, calls the snapshot once, does not call the trigger helper, and preserves the exact trigger ID and timestamp.
* E2 terminates and passes with its existing semantic assertions unchanged.
* Both post-edit payload measurements exactly match the table above.
* The exact eight-path guard passes with no mode or topology change.
* All previously mandatory focused, file-owner, lint, distribution, projection-parity, and explicit full-regression checks pass with no failure, unexpected skip, hang, or timeout.

DISPOSITION: GO_BOUNDED_BLOCKER_E_TWO_FIXTURE_TRANSPORTS
