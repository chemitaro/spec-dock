# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6a2dd4-5400-83ee-9392-dd74c9db5c98

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt.md as the complete bounded S12 regression blocker follow-up. Inspect the exact GitHub branch and pushed HEAD, then return only the requested Markdown repair packet.

## Answer

# S12 Regression Blocker Repair Packet

## Source Identity

| Field                             | Locked value                                                                                                |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Repository                        | `chemitaro/spec-dock`                                                                                       |
| Mandatory branch                  | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                       |
| Exact pushed HEAD                 | `b5814936a05dde83c586b273a915ae6a25512552`                                                                  |
| Connector comparison              | Branch and exact HEAD are identical; ahead `0`, behind `0`                                                  |
| Default-branch fallback           | Forbidden and not used                                                                                      |
| Scope                             | Three independent S12 regression blockers only                                                              |
| Static repair                     | Running separately; its uncommitted state must not be inspected, inferred, or merged into this worker scope |
| Live Oracle / Human authorization | Out of scope                                                                                                |

The attached follow-up is the complete bounded repair contract. It fixes the three observed regression blockers without changing canonical planning, public commands, schemas, Prompt behavior, polling features, or live-operation authority. 

The inspected pushed commit is exactly `b5814936a05dde83c586b273a915ae6a25512552`.

## Repair Disposition

**GO — bounded regression repair.**

| Blocker                                    | Classification                                                                                 | Production change                                                   |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| A — stale authoring transcript expectation | Test expectation drift after an already-reviewed false-positive correction                     | None                                                                |
| B — dogfooding snapshot drift              | Mechanical snapshot synchronization with approved checked-in metadata                          | None                                                                |
| C — unsafe wait arguments hang             | Missing final fail-fast validation in the Python wait engine plus an unbounded regression test | One provider Python file, followed by mechanical dogfood projection |

The admitted repair does not require a Requirement, Design, Plan, Report, Prompt, Skill, CLI, schema, or polling-policy change.

Blocker C has one mandatory reconciliation gate: the checked-in shell wrapper already contains value guards for repository, PR number, SHA, positive integers, timestamp, trigger mode, body mode, and progress before invoking Python.  It then delegates to `pr_observation_wait.py`.  The worker must therefore reproduce the missing validation directly at the Python-engine boundary and must not blindly duplicate or redesign shell parsing.

## Exact Write Allowlist

Only these four tracked paths are writable:

```text
tests/cli_runtime/test_authoring.py
tests/unit/infra/test_init_update.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

Ownership:

| Path                                   | Permitted change                                                            |
| -------------------------------------- | --------------------------------------------------------------------------- |
| `tests/cli_runtime/test_authoring.py`  | Blocker A expectation correction only                                       |
| `tests/unit/infra/test_init_update.py` | Blocker B snapshot constants; Blocker C timeout and negative-boundary tests |
| Provider `pr_observation_wait.py`      | Blocker C pre-side-effect contract validation only                          |
| Dogfood `pr_observation_wait.py`       | Mechanical byte projection from provider only                               |

The provider shell and its dogfood counterpart are read-only:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
```

No `.meta.json` file may change. No new file, deletion, rename, symlink, executable-bit change, canonical document change, Report update, or dependency declaration is authorized.

Because the static repair is separate and also owns parts of the test corpus, this repair must run in a clean isolated worktree at the exact pushed HEAD. Main must serialize the two repairs later; workers must not inspect or absorb each other’s uncommitted changes.

## Blocker A Repair

### Diagnosis

The failing test currently supplies three genuine secret-like payloads plus the prose phrase `raw transcript text`, then expects all four findings, including:

```text
raw_transcript:raw transcript
```

The stale assertion is visible in the exact test.

The current production contract intentionally distinguishes:

* secret-like payloads, which remain findings; and
* an actual transcript structure, which requires transcript markers and a complete dialogue pair.

The constraint scanner still performs both secret detection and structural transcript detection.  The word `transcript` in ordinary prose is therefore not independently prohibited.

Actual transcript-content detection remains covered elsewhere:

* a test with `raw transcript: browser text` expects a raw-transcript finding while checking public redaction;
* a parameterized test expressly supplies actual raw transcript payload and expects `raw_transcript:raw transcript`.

### Minimum correction

Edit only:

```text
tests/cli_runtime/test_authoring.py
```

In `test_authoring_pack_review_rejects_sensitive_constraint_text`:

1. Preserve the current input text, including the ordinary phrase containing `transcript`.

2. Preserve the rejected status.

3. Preserve these three positive assertions exactly:

   ```text
   secret_like_payload:token
   secret_like_payload:api_key
   secret_like_payload:private key
   ```

4. Remove the stale positive assertion for `raw_transcript:raw transcript`.

5. Add an explicit negative assertion that this input produces no finding whose code starts with `raw_transcript:`.

Do not modify:

* `authority_boundary.py`;
* the transcript marker grammar;
* secret scanning;
* the two positive actual-transcript tests;
* public finding redaction.

### Required outcome

For this fixture:

```text
token/API-key/private-key findings: present
raw-transcript finding: absent
result status: rejected
```

Actual transcript fixtures must continue producing the raw-transcript finding.

## Blocker B Repair

### Diagnosis

The checked-in snapshot constants lag the approved `init-00322` projection by exactly ten `.meta.json` paths. The current path tuple presently contains the Initiative root but not its three Epics and seven Issues.

The full dependency snapshot likewise contains the Initiative root but not those descendants.

The checked-in metadata establishes these exact relationships:

* `epic-00331`: no `depends_on`;
* `epic-00332`: `["epic-00331"]`;
* `epic-00333`: `["epic-00332"]`;
* `iss-00334`: no `depends_on`;
* `iss-00335`: `["iss-00334"]`;
* `iss-00336`: `["iss-00334", "iss-00335"]`;
* `iss-00337`: `["epic-00331"]`;
* `iss-00338`: `["epic-00332"]`;
* `iss-00339`: `["iss-00338"]`;
* `iss-00340`: `["iss-00339"]`.

### Exact mechanical snapshot update

Edit only:

```text
tests/unit/infra/test_init_update.py
```

#### `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`

Insert these ten paths in the tuple’s existing lexicographic order, immediately after the `init-00322` Initiative root and before the next Initiative:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00335-implement-initiative-epic-portfolio-planning-workflow/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00336-implement-targeted-review-and-planning-surface-cutover/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/issues/iss-00337-analysis-guided-issue-execution-and-per-issue-delivery/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00338-multi-issue-epic-coordination-and-finish/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00339-official-global-cutover-and-rollback-activation/.meta.json
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00340-post-cutover-evaluation-release-and-closure/.meta.json
```

Expected tuple count:

```text
213 + 10 = 223
```

#### `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`

Add the same ten keys with these exact values:

| Path suffix                                                                   | Exact value                  |
| ----------------------------------------------------------------------------- | ---------------------------- |
| `epic-00331-planning-and-advisory-review/.meta.json`                          | `[]`                         |
| `iss-00334-implement-chatgpt-issue-planning-workflow/.meta.json`              | `[]`                         |
| `iss-00335-implement-initiative-epic-portfolio-planning-workflow/.meta.json`  | `["iss-00334"]`              |
| `iss-00336-implement-targeted-review-and-planning-surface-cutover/.meta.json` | `["iss-00334", "iss-00335"]` |
| `epic-00332-issue-execution-and-per-issue-delivery/.meta.json`                | `["epic-00331"]`             |
| `iss-00337-analysis-guided-issue-execution-and-per-issue-delivery/.meta.json` | `["epic-00331"]`             |
| `epic-00333-epic-completion-and-global-cutover/.meta.json`                    | `["epic-00332"]`             |
| `iss-00338-multi-issue-epic-coordination-and-finish/.meta.json`               | `["epic-00332"]`             |
| `iss-00339-official-global-cutover-and-rollback-activation/.meta.json`        | `["iss-00338"]`              |
| `iss-00340-post-cutover-evaluation-release-and-closure/.meta.json`            | `["iss-00339"]`              |

Expected full dependency-map key count:

```text
213 + 10 = 223
```

#### `_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP`

Add only these six issue entries:

```python
"iss-00335": ["iss-00334"],
"iss-00336": ["iss-00334", "iss-00335"],
"iss-00337": ["epic-00331"],
"iss-00338": ["epic-00332"],
"iss-00339": ["iss-00338"],
"iss-00340": ["iss-00339"],
```

Do not add:

* `iss-00334`, because its dependency list is empty;
* Epic entries, because this constant is the non-empty **Issue** dependency map.

Expected non-empty Issue-map count:

```text
62 + 6 = 68
```

### Validation requirements

The two existing snapshot tests must prove:

```text
observed paths == expected paths
observed full depends_on map == expected full map
observed non-empty Issue map == expected non-empty Issue map
missing prior baseline paths == 0
unexpected paths beyond the ten approved nodes == 0
unexpected non-empty dependency entries beyond the six approved entries == 0
```

Do not edit the generated `.meta.json` files. A mismatch between those files and the values above is a stop condition, not permission to rewrite metadata.

## Blocker C Repair

### Current boundary

The public shell wrapper already:

* rejects unknown options with usage and exit `64`;
* validates repository, PR number, SHA, positive timing/count fields, trigger fields, timestamp, body mode, progress mode, and unsafe `--out`;
* invokes the Python wait engine only after those checks.

The provider and checked-in dogfood shell wrappers are currently byte-identical.

By contrast, the Python engine reads trusted-looking `OBS_*` strings, immediately converts numeric values, establishes the deadline, and proceeds toward output cleanup, trigger execution, and polling without validating the complete contract itself.  Its polling loop then begins from those unchecked values.

### Validation ownership

Keep the existing shell validation for public CLI usability.

Add the authoritative last-chance validation to:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

Rationale:

1. The Python engine is the final boundary before trigger, snapshot, filesystem, and polling side effects.
2. It can be invoked independently from the shell wrapper.
3. Environment values are presently treated as trusted despite being untyped strings.
4. A Python-side guard closes both direct-entry and wrapper-bypass paths without changing the public shell contract.
5. Duplicating more validation in shell alone would leave the actual side-effect owner unguarded.

This is defense in depth, not a new CLI schema or polling feature.

### Mandatory source/execution reconciliation

Before editing:

```bash
set -euo pipefail

SOURCE_HEAD='b5814936a05dde83c586b273a915ae6a25512552'
PROVIDER_WAIT='src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh'
DOGFOOD_WAIT='.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh'

test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

test "$(
  python3 - "$PROVIDER_WAIT" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)" = '0ef1a4f282ac206489388ac74aeead73babfe82d'

cmp "$PROVIDER_WAIT" "$DOGFOOD_WAIT"
bash -n "$PROVIDER_WAIT"
```

Run the first invalid wrapper case under the new bounded test helper before attributing the hang. If the checked-in wrapper with this exact hash still bypasses its visible SHA guard, stop and report a source/execution mismatch. Do not compensate by changing unrelated polling behavior.

Separately, reproduce the Python-engine Red directly. That is the production gap this packet authorizes.

### Provider Python repair

Add one internal validation step before:

* converting any `OBS_*` value to `int`;
* creating `Path(OBS_OUT_DIR)`;
* reading prior state;
* clearing output artifacts;
* invoking the trigger helper;
* invoking the snapshot helper;
* computing or entering the polling deadline.

The validation must accept exactly the current shell contract:

| Field                              | Required validation                                                      |
| ---------------------------------- | ------------------------------------------------------------------------ |
| `OBS_REPO`                         | `OWNER/REPO` using the current shell character allowlist                 |
| `OBS_PR`                           | positive decimal integer                                                 |
| `OBS_HEAD_SHA`                     | 7–64 hexadecimal characters                                              |
| `OBS_TIMEOUT_SECONDS`              | positive decimal integer                                                 |
| `OBS_POLL_INTERVAL_SECONDS`        | positive decimal integer                                                 |
| `OBS_QUIET_SECONDS`                | positive decimal integer                                                 |
| `OBS_SAME_FINGERPRINT_COUNT`       | positive decimal integer                                                 |
| `OBS_ZERO_CHECK_GRACE_POLLS`       | positive decimal integer                                                 |
| `OBS_TRIGGER_MODE`                 | `post-once` or `resume`                                                  |
| `OBS_TRIGGER_COMMENT_ID`           | empty or positive decimal integer                                        |
| `OBS_TRIGGER_CREATED_AT`           | empty or the existing accepted ISO-8601 shape                            |
| post-once trigger fields           | both must be empty                                                       |
| resume trigger fields              | both must be present and valid                                           |
| `OBS_BODY_MODE`                    | `none`, `trigger-window-truncated`, `trigger-window-full`, or `out-only` |
| `OBS_PROGRESS`                     | `stderr-summary` or `none`                                               |
| `OBS_OUT_DIR`                      | empty or not beginning with `-`                                          |
| missing required environment value | usage failure, not traceback or polling                                  |

On any invalid value:

```text
exit code: 64
stdout: empty
stderr: contains exactly the public usage first line
helpers called: 0
gh calls: 0
output mutation: 0
polling: 0
```

Required usage line:

```text
usage: wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA [options]
```

Do not expose raw invalid values in the error.

Do not add:

* `argparse`;
* a new public option;
* a new exit status;
* a new polling state;
* a new result schema;
* a new dependency;
* retry or timeout behavior;
* filesystem discovery;
* shell-command execution.

### Exact projection counterpart

After the provider repair, run the official projection path:

```bash
uv run python -m spec_dock.cli update .
```

The only permitted projected production change is:

```text
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

Then require:

```bash
cmp \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py \
  .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

The shell wrappers must remain unchanged and byte-identical.

### Exact six wrapper cases

Preserve all six current invalid-input cases:

| ID         | Invalid condition                                           |
| ---------- | ----------------------------------------------------------- |
| WAIT-NF-01 | `--head-sha not-a-sha`                                      |
| WAIT-NF-02 | `--pr 0`                                                    |
| WAIT-NF-03 | `--progress verbose`                                        |
| WAIT-NF-04 | `--timeout-seconds 0`                                       |
| WAIT-NF-05 | malformed `--trigger-created-at 2026-06-08T01:02:03not-iso` |
| WAIT-NF-06 | unknown `--endpoint x`                                      |

For every case assert:

```text
returncode == 64
stdout == ""
usage first line is present in stderr
fake gh log does not exist
```

WAIT-NF-06 remains shell-owned because an unknown option is not represented in the `OBS_*` environment contract.

WAIT-NF-01 through WAIT-NF-05 must also be exercised directly against the Python engine with malformed `OBS_*` values, valid harmless values for all unrelated fields, and fake trigger/snapshot helpers that record any invocation.

### Test hardening

The existing invalid wait subprocess must no longer be unbounded.

Use a small test-local bounded-process helper in `tests/unit/infra/test_init_update.py`:

1. Start the subprocess in a new process session.
2. Capture stdout and stderr.
3. Wait no more than five seconds.
4. On timeout, terminate the entire process group, reap it, and fail the test with the exact argument case.
5. Return a `CompletedProcess`-equivalent result for the normal assertions.

A plain unlimited `subprocess.run` is forbidden. A timeout that kills only the shell while leaving the Python child holding inherited pipes is also insufficient.

This helper is test infrastructure only. It must not become a product timeout or polling feature.

### No-`gh` and no-helper evidence

For every invalid case:

* remove any previous fake `gh` log before invocation;
* assert the log is absent afterward;
* for direct Python-engine cases, use separate fake trigger and snapshot helper logs;
* assert both helper logs are absent;
* assert no output directory or managed observation artifact was created.

## Red and Green Verification

Use an external basetemp because prior S12 execution encountered system-temp pressure.

```bash
set -euo pipefail

SOURCE_HEAD='b5814936a05dde83c586b273a915ae6a25512552'
: "${S12_EXTERNAL_ROOT:?Set S12_EXTERNAL_ROOT to an external writable directory}"

mkdir -p \
  "$S12_EXTERNAL_ROOT/pytest/regression-a" \
  "$S12_EXTERNAL_ROOT/pytest/regression-bc" \
  "$S12_EXTERNAL_ROOT/pytest/regression-files" \
  "$S12_EXTERNAL_ROOT/pytest/regression-full"

test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

### Red evidence

The supplied observed Red is valid execution input:

* Blocker A fails only on the stale raw-transcript expectation.
* Blocker B reports 213 expected versus 223 actual paths and the six specified non-empty dependencies.
* Blocker C hangs without a test timeout and records no fake `gh` call. 

Before production repair, add the bounded C tests and prove:

```text
direct Python invalid-contract test: fails or reaches the five-second timeout
wrapper test: cannot hang indefinitely
fake gh/helper calls: 0
```

Do not intentionally rerun an unbounded hanging test.

### Blocker A Green

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-a" \
  tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_review_rejects_sensitive_constraint_text \
  tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_review_redacts_sensitive_findings_in_report_path \
  tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_review_rejects_secret_and_raw_transcript_payloads
```

Required:

```text
ordinary transcript phrase: no raw-transcript finding
three secret-like findings: preserved
actual transcript positive tests: preserved
```

### Blocker B and C Green

Use the existing wrapper test plus one new direct-engine test, for example:

```text
TestInitUpdate.test_issue_75_pr_observation_wait_engine_rejects_invalid_environment_before_helpers
```

Run:

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-bc" \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_review_wrapper_rejects_unsafe_inputs_before_gh_api \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_wait_engine_rejects_invalid_environment_before_helpers
```

Also verify provider projection parity:

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-files" \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets
```

Static syntax checks for the C repair:

```bash
bash -n \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh

uv run python -m py_compile \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py

cmp \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py \
  .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

### File-owner regressions

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-files" \
  tests/cli_runtime/test_authoring.py \
  tests/unit/infra/test_init_update.py
```

### Mandatory full regression

After integrating these repairs with the independently completed static repair on a new clean commit candidate, rerun the complete explicit full-regression lane:

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-full"
```

Requirements:

```text
collection errors: 0
failures: 0
unexpected skips: 0
hangs: 0
timeout-hardening failures: 0
```

No prior baseline failure is waived. Results obtained against the pre-repair HEAD do not close the repaired HEAD.

Main must also rerun `make lint` after serializing the static and regression repairs. This regression packet does not infer the static worker’s result.

## Changed-Path Guard

Run from the isolated regression-repair worktree before handoff:

```bash
python3 - 'b5814936a05dde83c586b273a915ae6a25512552' <<'PY'
from __future__ import annotations

import subprocess
import sys

base = sys.argv[1]

allowed = {
    "tests/cli_runtime/test_authoring.py",
    "tests/unit/infra/test_init_update.py",
    (
        "src/spec_dock/assets/install_root/.agents/skills/"
        "github-pr-observation/scripts/lib/pr_observation_wait.py"
    ),
    ".agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py",
}

untracked = subprocess.check_output(
    ["git", "ls-files", "--others", "--exclude-standard"],
    text=True,
).splitlines()
if untracked:
    raise SystemExit(f"untracked paths are forbidden: {untracked}")

lines = subprocess.check_output(
    ["git", "diff", "--name-status", base, "--"],
    text=True,
).splitlines()

observed: set[str] = set()
for line in lines:
    status, path = line.split("\t", 1)
    if status != "M":
        raise SystemExit(f"only tracked modifications are allowed: {line}")
    observed.add(path)

if observed != allowed:
    raise SystemExit(
        "changed-path mismatch\n"
        f"unexpected={sorted(observed - allowed)}\n"
        f"missing={sorted(allowed - observed)}"
    )

print(f"changed_path_count={len(observed)}")
PY
```

Additional guards:

```bash
test -z "$(
  git diff --name-only \
    b5814936a05dde83c586b273a915ae6a25512552 -- \
    'spec-dock/initiatives/**/.meta.json'
)"

cmp \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh

cmp \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py \
  .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py

git diff --check
```

The two Python files must be byte-identical after projection. The two shell files must remain byte-identical to their starting bytes.

Main must not apply this four-path guard to the later combined static-plus-regression integration tree. Main must instead review and union the two separately approved allowlists after rebasing or cherry-picking in a clean integration step.

## Stop Conditions

Stop and return to Main if any of the following occurs:

* Branch or starting HEAD differs from the locked identity.
* The isolated regression-repair worktree is not clean.
* Any static worker uncommitted state is visible in this worktree.
* Blocker A requires a production scanner change.
* A secret-like finding disappears.
* An actual-transcript positive test stops detecting transcript content.
* Blocker B reveals any missing prior baseline path.
* Blocker B reveals a path delta other than the exact ten approved nodes.
* A dependency differs from the exact metadata values listed above.
* A `.meta.json` edit appears.
* Blocker C cannot reproduce the direct Python-engine validation gap safely.
* The checked-in shell hash or behavior differs from the inspected exact-HEAD source.
* The wrapper still hangs after bounded test hardening.
* Invalid input reaches trigger, snapshot, `gh`, output cleanup, or polling.
* The repair needs a shell option change, new public error code, new schema, new dependency, or polling-policy change.
* Validation would expose raw invalid values.
* Official update changes any projected path other than the one Python counterpart.
* Provider and dogfood Python bytes differ.
* Any path outside the four-path allowlist changes.
* Any focused test, file-owner suite, syntax check, parity test, or full regression fails.
* A required full-regression test is unexpectedly skipped.
* A canonical Requirement, Design, Plan, Report, Prompt, Skill, `.assurance.json`, workflow, or package configuration changes.
* The worker attempts a commit, push, live Oracle run, authorization change, or S12 closure claim.

## Worker Handoff

### Bounded dev-coder input

```text
repository: chemitaro/spec-dock
branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: b5814936a05dde83c586b273a915ae6a25512552
scope:
  - one stale authoring test expectation
  - three exact dogfooding snapshot constants
  - provider Python wait-contract fail-fast
  - mechanical dogfood Python projection
  - bounded anti-hang/no-helper/no-gh tests
write_allowlist: exact four paths in this packet
canonical_changes: forbidden
report_changes: forbidden
shell_changes: forbidden
commit_or_push: forbidden
live_oracle: forbidden
```

### Required worker return

Return all of the following:

```text
source_head
repository_status_before
exact changed-path inventory

Blocker A:
  removed stale assertion
  retained secret findings
  retained actual-transcript positive tests
  targeted test counts and exit code

Blocker B:
  meta path count before/after
  exact ten added paths
  full depends_on map count before/after
  exact ten added full-map values
  non-empty Issue map count before/after
  exact six added non-empty values
  metadata files changed: no
  two snapshot test results

Blocker C:
  provider shell SHA-256 and bash syntax result
  direct Python Red result
  validation fields covered
  exact six wrapper-case results
  exact five direct-engine-case results
  per-case return code
  per-case stdout/stderr classification
  per-case usage-line assertion
  fake gh call count
  fake trigger call count
  fake snapshot call count
  timeout-helper result
  provider Python SHA-256
  projected Python SHA-256
  provider/projection byte parity

Verification:
  focused commands and exit codes
  file-owner suite counts
  explicit full-regression counts
  failures/skips/timeouts
  git diff --check
  repository_status_after

Unverified:
  static worker result
  combined static-plus-regression integration
  combined commit-SHA-bound full regression
```

Main must independently inspect the four-path diff, integrate it only after the separate static repair is stable, rerun `make lint` and the complete `--run-full-regression` suite on the resulting clean commit candidate, and obtain the required fresh S12 reviews before any closure claim.

DISPOSITION: GO_BOUNDED_REGRESSION_REPAIR
