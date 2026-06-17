---
artifact_kind: disc
id: 20260616t030000z-disc-python-extraction-from-shell-scripts
issue: iss-00187
title: Python Extraction From GitHub PR Observation Shell Scripts
created_at: 2026-06-16T03:00:00Z
status: adopted
adoption_status: adopted
reflected_to:
  - design.md
  - plan.md
  - report.md
---

# Python Extraction From GitHub PR Observation Shell Scripts

## Purpose

This artifact analyzes whether the current GitHub PR observation scripts should extract embedded Python into standalone Python modules before or during the next bug-fix pass.

The motivation is the current review situation:

- P1 fixes are needed in `fetch_pr_checks_snapshot.sh`.
- The script's main behavior is implemented as a large Python heredoc inside a shell wrapper.
- The same pattern appears across multiple PR observation scripts.
- Review, testing, and future fixes are harder because Python logic, shell argument parsing, environment setup, and stdout contract are physically mixed.

## Current Script Structure

The provider-side PR observation scripts currently include large embedded Python blocks:

| Script | Approx. lines | Embedded Python entry |
|---|---:|---|
| `scripts/lib/fetch_pr_checks_snapshot.sh` | 1247 | `python3 - <<'PY'` |
| `scripts/lib/fetch_pr_review_snapshot.sh` | 1468 | `python3 - <<'PY'` |
| `scripts/fetch_pr_observation_snapshot.sh` | 807 | several short Python snippets plus one large block |
| `scripts/wait_pr_observation.sh` | 1503 | `python3 - <<'PY'` |
| `scripts/trigger_codex_review.sh` | 434 | `python3 - <<'PY'` |

The shell wrappers currently own:

- fixed CLI surface and usage text,
- argument validation,
- environment variable passing,
- temporary directory handling in wrapper scripts,
- invocation of `python3`,
- stdout JSON contract.

The embedded Python currently owns:

- GitHub API invocation through `gh`,
- stderr/auth/permission classification,
- GitHub JSON parsing,
- CI/review lifecycle taxonomy,
- fingerprint generation,
- final JSON payload construction.

## Maintainability Problems

### 1. Review diffs are hard to read

A change to CI taxonomy appears inside a `.sh` file, even though the changed behavior is Python. Reviewers must mentally switch between shell and Python semantics in the same file.

This matters for the current P1 review because both findings are about Python data-flow and classification logic, not shell behavior.

### 2. Unit boundaries are unclear

The current tests exercise the scripts end-to-end with fake `gh`. That is valuable, but it makes small logic defects harder to isolate.

Examples:

- zero Actions runs plus green external checks is a pure classifier rule.
- job expansion budgeting is a collector policy rule.
- review completion timing is a wait-state rule.

Each could be tested more directly if the Python logic were importable.

### 3. Shell wrappers become too large

The wrappers are no longer thin host scripts. They contain hundreds to more than a thousand lines of Python. This increases the risk of accidental changes to quoting, heredoc boundaries, environment passing, and stdout behavior.

### 4. Future fixes encourage patching the heredoc

Once logic lives in a heredoc, the easiest local patch is to keep adding logic there. This makes every subsequent issue more expensive.

## Design Goal

Separate responsibilities without changing the public script contract.

The external command surface should remain:

```bash
fetch_pr_checks_snapshot.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA
fetch_pr_review_snapshot.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA
fetch_pr_observation_snapshot.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA
wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA ...
trigger_codex_review.sh ...
```

The shell scripts should become thin wrappers that:

- validate fixed arguments where shell validation is still useful,
- locate the adjacent Python entrypoint,
- pass arguments explicitly,
- preserve stdout/stderr behavior,
- exit with the Python process status.

Standalone Python scripts/modules should own:

- GitHub API reads through `gh`,
- JSON parsing,
- state classification,
- fingerprinting,
- payload rendering,
- timing policy,
- testable helper functions.

## Proposed File Layout

Provider source of truth:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/
|-- fetch_pr_observation_snapshot.sh
|-- wait_pr_observation.sh
|-- trigger_codex_review.sh
`-- lib/
    |-- fetch_pr_checks_snapshot.sh
    |-- fetch_pr_review_snapshot.sh
    |-- pr_observation_checks.py
    |-- pr_observation_review.py
    |-- pr_observation_snapshot.py
    |-- pr_observation_wait.py
    |-- pr_observation_trigger.py
    `-- pr_observation_common.py
```

Dogfooding mirror:

```text
.agents/skills/github-pr-observation/scripts/
```

The mirror should match provider files after each provider-side change.

## Recommended Extraction Strategy

### Phase A: Extract only `fetch_pr_checks_snapshot.sh` Python first

Reason:

- Both current P1 review threads are in the checks collector.
- It is the highest-value extraction target.
- It avoids a giant all-script refactor before the urgent review fixes.

Work:

1. Create `scripts/lib/pr_observation_checks.py`.
2. Move the embedded Python body from `fetch_pr_checks_snapshot.sh` into `main(argv=None)`.
3. Let the shell wrapper call:

   ```bash
   python3 "$script_dir/pr_observation_checks.py" --repo "$repo" --pr "$pr" --head-sha "$head_sha"
   ```

4. Preserve the exact JSON contract and exit behavior.
5. Keep fake-`gh` end-to-end tests as the primary regression gate.

### Phase B: Fix the two current P1 defects inside the extracted Python

Reason:

- Once extracted, the status ladder and job expansion policy can be reviewed as Python.
- Focused helper functions can be introduced only where they directly support the P1 fixes.

Candidate helper boundaries:

- `classify_ci_status(...)`
- `collect_actions_runs(...)`
- `collect_actions_jobs(...)`
- `should_expand_actions_jobs(...)`
- `build_actions_summary(...)`

Avoid creating a framework. Add helpers only where they reduce the current review risk.

### Phase C: Extract review and wait scripts later

Reason:

- `fetch_pr_review_snapshot.sh` and `wait_pr_observation.sh` also have large embedded Python.
- They are relevant to the review-completion timing gap.
- However, extracting all scripts before fixing current P1 feedback increases blast radius.

Recommended follow-up:

1. Extract checks collector first.
2. Fix and close current P1 review threads.
3. Add a separate plan step for review/wait extraction and review-completion timing hardening.

## Tradeoffs

### Benefits

- Python syntax and behavior become directly reviewable.
- Future helper-level tests become possible.
- Shell wrappers return to a narrow host-adapter role.
- Bug fixes in status classification become smaller and less fragile.
- Provider/mirror sync remains mechanical.

### Costs

- Initial diff is larger than a direct heredoc patch.
- Existing tests that assert generated file content may need updates.
- Script-relative path handling must be correct in both provider and mirror locations.
- Consumers may rely on files being single-script artifacts, although the public command name remains the same.

## Compatibility Requirements

The extraction must preserve:

- command names,
- flags,
- validation behavior unless intentionally changed,
- stdout final JSON as authority,
- stderr diagnostic behavior,
- exit status semantics,
- no raw token / auth stderr leakage,
- provider-first implementation,
- dogfooding mirror consistency.

The extraction must not introduce:

- new third-party dependencies,
- network behavior outside existing `gh` calls,
- arbitrary GitHub API proxy capability,
- broad package installation assumptions.

## Test Strategy

Minimum tests after Phase A extraction:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "actions or pr_observation or issue_187"
git diff --check
```

Minimum tests after Phase B P1 fixes:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "actions_zero_runs or external or jobs_summary or pr_observation or issue_187"
uv run pytest tests/unit/infra/test_init_update.py -q
git diff --check
./spec-dock/scripts/spec-dock validate
```

Provider/mirror checks should compare:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py
```

## Implementation Plan Candidate

### S200: Discussion and plan amendment

- Adopt this artifact into `design.md` and append concrete S200+ steps to `plan.md`.
- Record current P1 review findings and review-completion timing gap.

### S201: Extract checks collector Python

- Move Python code from `fetch_pr_checks_snapshot.sh` to `pr_observation_checks.py`.
- Keep wrapper behavior unchanged.
- Mirror provider file.
- Run existing focused tests before behavior changes.

### S202: Fix external CI with zero Actions runs

- Add red test for zero Actions runs plus green external checks.
- Change status ladder so external green evidence can pass when Actions has zero runs.
- Preserve zero Actions plus zero external evidence as non-pass.

### S203: Bound Actions jobs collection

- Add red or characterization test showing job expansion is bounded in wait/default mode.
- Implement a cap or selective expansion rule.
- Preserve failure diagnostics.

### S204: Review-completion timing hardening

- Add tests for no-review-yet below threshold vs beyond threshold.
- Prevent premature `review_completion_unknown` before the review-latency allowance.

### S299: Final validation and PR observation

- Run focused and broad tests.
- Validate provider/mirror sync.
- Re-run PR observation for the latest head.
- Confirm selected unresolved review threads are resolved or superseded.

## Recommendation

Do not patch the current P1 findings directly inside the large heredoc unless the extraction proves too risky.

The preferred path is:

1. Extract the checks collector Python first.
2. Keep the shell wrapper command contract unchanged.
3. Fix the two current P1 review issues in the extracted Python.
4. Defer full extraction of review/wait/trigger scripts to a separate follow-up step unless review-completion timing work requires it immediately.

This balances urgent review repair with improved maintainability.
