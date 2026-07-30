# S12 Blocker G — S420 Review Fixture Transport Amendment

## Source lock

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Exact pushed HEAD: `fd97aca1f005e2fe066a872343039c7e5b8889ca`
* GitHub connector comparison: `identical`, ahead `0`, behind `0`; default-branch fallback was not used.
* Scope is exclusively the generated review fixture in `TestInitUpdate::_issue_187_s420_run_observation_snapshot`. The exact HEAD already imports `shlex`; the checks fixture and review fixture are distinct, and the review fixture currently uses the external `cat <<'JSON'` transport.
* The attached admission brief is controlling. 

## Admitted transport change

Inside only `_issue_187_s420_run_observation_snapshot`, replace only the body of `review_script.write_text(...)` with:

```python
review_script.write_text(
    f"""#!/usr/bin/env bash
builtin printf '%s\\n' {shlex.quote(json.dumps(review_wrapper_payload, sort_keys=True, separators=(",", ":")))}
""",
    encoding="utf-8",
)
```

The source-level `\\n` is mandatory so the generated Bash contains the literal format `'%s\n'`. `builtin printf` must receive exactly one mechanically quoted dynamic JSON argument. No variable interpolation, command substitution, external preprocessing, pipe, subshell, temporary file, or alternate serializer is admitted.

## Frozen boundaries

The effective dirty-worktree allowlist remains exactly ten paths. This amendment changes no path beyond the already-allowed `tests/unit/infra/test_init_update.py`.

The following remain byte- or behavior-frozen:

* `review_wrapper_payload` and all callers.
* `json.dumps(..., sort_keys=True, separators=(",", ":"))`.
* The generated checks fixture and every other heredoc.
* Fake `gh`, copied snapshot wrapper, subprocess arguments, environment, chmod operations, assertions, timeout policy, and retry behavior.
* Production, provider, dogfood, Prompt, Skill, canonical documents, Report, packaging, metadata, file modes, and repository topology.

The frozen S420 assertions remain `review == "approved"`, top-level action `wait`, pending decision, `missing_current_completion_signal`, exact carryover ID `RT_carryover`, and exclusion of `review_completion_unknown`.

## Red, Green, and digest gates

**Red:** The exact-HEAD source confirms the external `cat` child transport. The supplied measurement records no progress for 25.22 seconds and a greater-than-30-second hang outside the Codex sandbox. Those timings are admission evidence from the brief and were not independently rerun here.

**Transport-equivalence probe:** Executing the proposed generated Bash line against the exact reconstructed S420 payload returned exit `0` with:

* Length: `1,239` UTF-8 bytes
* SHA-256: `b3b3699fc025d7f88465670cd969e6ca9f7ec422449194d8a3983b39567a4a5d`
* Final newline: present
* Stderr: empty

This establishes byte-equivalent transport, not repository-suite Green.

**Required Green before integration:**

```text
uv run pytest -q tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_s420_snapshot_carryover_only_missing_completion_stays_waitable
```

The node must terminate and pass without weakened assertions. The unchanged ten-path guard, all prior A–F focused checks, file-owner tests, lint, distribution/projection verification, and explicit full regression must then pass. The serialized stdout must again satisfy the exact length, SHA-256, and final-newline gate above. Any further measured stall or required change outside this single transport is a mandatory stop for a new JIT admission.

DISPOSITION: GO_BOUNDED_BLOCKER_G_S420_REVIEW_FIXTURE
