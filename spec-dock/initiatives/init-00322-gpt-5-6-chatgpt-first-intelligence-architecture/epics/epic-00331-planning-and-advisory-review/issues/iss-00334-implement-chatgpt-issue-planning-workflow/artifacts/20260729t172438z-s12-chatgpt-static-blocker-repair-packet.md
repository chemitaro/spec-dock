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

Use the attached prompt.md as the complete bounded S12 static blocker follow-up. Inspect the exact GitHub branch and current HEAD, then return only the requested Markdown repair packet.

## Answer

# S12 Static Blocker Repair Packet

## Source Identity

| Field                                   | Locked value                                                        |
| --------------------------------------- | ------------------------------------------------------------------- |
| Repository                              | `chemitaro/spec-dock`                                               |
| Mandatory branch                        | `iss-00334-implement-chatgpt-issue-planning-workflow`               |
| Exact current HEAD                      | `6af86ac02a26970f5ca9050089cea2fab80ccff3`                          |
| Connector comparison                    | Branch is identical to the required HEAD; ahead `0`, behind `0`     |
| Default-branch fallback                 | Forbidden and not used                                              |
| Issue / milestone                       | `iss-00334` / S12 static blocker repair                             |
| Starting tree                           | Must be clean before the worker begins                              |
| Full-regression / distribution evidence | Still running; no result may be inferred or credited by this packet |

The exact HEAD is the S12 JIT work-packet and Report-evidence commit.  The attached bounded follow-up supplies the observed `make lint` failures, the current guide hash, and the explicit restriction to formatting, six mypy-owning files, and external-only PlantUML verification. Those command results were supplied as read-only execution evidence; they were not rerun through the GitHub connector. 

## Repair Disposition

**GO — bounded static repair only.**

Repository inspection shows no need to change a public command, domain schema, Candidate or Review identity, Prompt contract, Human authority, apply semantics, or canonical specification.

The blockers divide cleanly into:

1. **Mechanical formatting:** run the existing Ruff formatter only on the exact files that Ruff identifies from the locked clean HEAD.
2. **One provider-source typing repair:** make the optional working directory an explicit `cwd: str | None` argument to `subprocess.run`.
3. **Five test-only typing repairs:** add precise narrowing or annotations around dynamically constructed test fixtures.
4. **Mechanical provider projection:** regenerate the one corresponding dogfood runtime file through the official update command.
5. **External acceptance tooling:** download and verify PlantUML 1.2026.6 outside the repository and run `-checkonly` against externally extracted diagrams.

The worker must not alter behavior to satisfy mypy and must not suppress the errors through `# type: ignore`, a new mypy override, broad `Any`, disabled diagnostics, or configuration weakening.

## Exact Write Allowlist

### Normative provider-source edit

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
```

### Test-only typing edits

```text
tests/unit/authoring_pack/test_backend_invoke_capture.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_candidate.py
tests/unit/application/test_issue_planning_apply.py
tests/unit/application/test_issue_planning.py
```

### Mechanical provider projection

This file may change only as output of the official update command after the provider edit:

```text
spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
```

The provider and projection currently have the same blob identity, so the projection edit must remain a byte copy of the repaired provider file.

### Mechanical Ruff formatting set

The attached evidence gives an approximate count but not the exact path list. Do not invent that list. Freeze it mechanically from `ruff format --check` on the clean exact HEAD before making any edit.

The final write allowlist is exactly:

```text
frozen Ruff-reported path set
UNION
the six provider/test paths above
UNION
the one mechanical projection path
```

No new file is authorized. In particular, the following remain read-only:

```text
pyproject.toml
scripts/static_analysis/run.sh
requirement.md
design.md
plan.md
report.md
.assurance.json
all Prompt and Skill resources
all other provider or projection files
```

## Mechanical Formatting

Formatting is a **mechanical, meaning-invariant repair**. It may not be combined with cleanup, renaming, import redesign, comment rewriting, assertion weakening, or unrelated modernization.

### 1. Lock the source and freeze the Ruff path list

```bash
set -euo pipefail

SOURCE_HEAD='6af86ac02a26970f5ca9050089cea2fab80ccff3'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

: "${S12_EXTERNAL_ROOT:?Set S12_EXTERNAL_ROOT to an external writable directory}"
mkdir -p "$S12_EXTERNAL_ROOT/static-repair"

FORMAT_LOG="$S12_EXTERNAL_ROOT/static-repair/ruff-format-check.log"
FORMAT_LIST="$S12_EXTERNAL_ROOT/static-repair/ruff-format-paths.txt"

set +e
uv run ruff format --check src/spec_dock tests >"$FORMAT_LOG" 2>&1
FORMAT_STATUS=$?
set -e

# Ruff uses exit 1 when valid files need formatting.
test "$FORMAT_STATUS" -eq 1

python3 - "$FORMAT_LOG" "$FORMAT_LIST" <<'PY'
from pathlib import Path
import re
import sys

log = Path(sys.argv[1]).read_text(encoding="utf-8")
destination = Path(sys.argv[2])

paths = sorted({
    match.group(1)
    for line in log.splitlines()
    if (match := re.fullmatch(r"Would reformat: (.+)", line))
})

if not paths:
    raise SystemExit("Ruff reported no parseable format paths")

special = {
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/"
    "application/authoring_pack/backend_invoke.py",
    "tests/unit/authoring_pack/test_backend_invoke_capture.py",
    "tests/cli_runtime/test_chatgpt_cli.py",
    "tests/unit/infra/test_init_update.py",
}

for raw in paths:
    path = Path(raw)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.suffix not in {".py", ".pyi"}
        or not path.is_file()
        or path.is_symlink()
    ):
        raise SystemExit(f"unsafe Ruff path: {raw}")

    if not (
        "issue_planning" in raw
        or raw in special
    ):
        raise SystemExit(
            "Ruff path is outside the observed Issue Planning/static corpus; "
            f"Main review required: {raw}"
        )

destination.write_text("\n".join(paths) + "\n", encoding="utf-8")
print(f"frozen_format_path_count={len(paths)}")
PY

python3 - "$FORMAT_LIST" <<'PY'
from pathlib import Path
import hashlib
import sys

path = Path(sys.argv[1])
print(f"format_list_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
PY
```

Keep the log, exact list, count, and list SHA outside the repository as execution evidence.

### 2. Run Ruff only on the frozen list plus the six edited Python files

Make the mypy edits described below first. Then run:

```bash
python3 - "$FORMAT_LIST" <<'PY'
from pathlib import Path
import subprocess
import sys

frozen = [
    line
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if line
]

typed_edits = [
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/"
    "application/authoring_pack/backend_invoke.py",
    "tests/unit/authoring_pack/test_backend_invoke_capture.py",
    "tests/unit/infra/test_issue_planning_oracle_artifact.py",
    "tests/unit/infra/test_issue_planning_candidate.py",
    "tests/unit/application/test_issue_planning_apply.py",
    "tests/unit/application/test_issue_planning.py",
]

targets = sorted(set(frozen) | set(typed_edits))
subprocess.run(["uv", "run", "ruff", "format", *targets], check=True)
PY
```

Do not run a repository-wide formatter against Markdown, generated dogfood files, or canonical documents.

### 3. Regenerate the provider projection

After the provider file is formatted and type-correct:

```bash
uv run python -m spec_dock.cli update .

cmp \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py \
  spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
```

If official update changes any other projected path, stop rather than expanding the allowlist.

### 4. Enforce the exact changed-path set

Run after all edits and projection:

```bash
python3 - "$SOURCE_HEAD" "$FORMAT_LIST" <<'PY'
from pathlib import Path
import subprocess
import sys

source_head = sys.argv[1]
format_paths = {
    line
    for line in Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
    if line
}

explicit = {
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/"
    "application/authoring_pack/backend_invoke.py",
    "tests/unit/authoring_pack/test_backend_invoke_capture.py",
    "tests/unit/infra/test_issue_planning_oracle_artifact.py",
    "tests/unit/infra/test_issue_planning_candidate.py",
    "tests/unit/application/test_issue_planning_apply.py",
    "tests/unit/application/test_issue_planning.py",
    "spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py",
}
allowed = format_paths | explicit

untracked = subprocess.check_output(
    ["git", "ls-files", "--others", "--exclude-standard"],
    text=True,
).splitlines()
if untracked:
    raise SystemExit(f"untracked files are forbidden: {untracked}")

name_status = subprocess.check_output(
    ["git", "diff", "--name-status", source_head, "--"],
    text=True,
).splitlines()

observed: set[str] = set()
for line in name_status:
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

## Mypy Repairs

### Provider-source repair

#### `application/authoring_pack/backend_invoke.py`

The current implementation conditionally expands a dictionary into the overloaded `subprocess.run` call. Mypy cannot prove that the dictionary contains only the valid `cwd` keyword. Runtime behavior is otherwise already correct.

Make only this structural change:

1. Compute one local value immediately before `subprocess.run`:

   * resolved working-directory string when `request.working_dir` is present;
   * `None` otherwise.
2. Pass that value explicitly as `cwd=<local>`.
3. Remove the conditional `**({...} if ... else {})` expansion.

Required invariant:

```text
working_dir present:
    still resolve(strict=True)
    still pass the resolved string to subprocess.run

working_dir absent:
    pass cwd=None, which preserves inherited-current-directory behavior
```

Do not alter:

* `invocation_argv`;
* `check=False`;
* `capture_output=True`;
* timeout calculation;
* exception classification;
* stream capture;
* environment handling;
* shell behavior;
* public result types.

### Test-only typing fixes

#### `tests/unit/authoring_pack/test_backend_invoke_capture.py`

The capture dictionary is deliberately `dict[str, object]`; direct nested indexing is not type-safe.

Before the three argv/kwargs assertions:

1. Read `captured["argv"]` and `captured["kwargs"]` into local variables.
2. Narrow them with runtime assertions:

   * argv is a `list`;
   * kwargs is a `dict`.
3. Perform the existing assertions through those narrowed locals.

Do not change the fake subprocess result or expected command values.

#### `tests/unit/infra/test_issue_planning_oracle_artifact.py`

`_artifact` correctly returns `dict[str, object]`, so `entry["sizeBytes"] += 1` is not statically valid.

For the `failure == "size"` branch:

1. Read `entry["sizeBytes"]` into a local.
2. Assert that the local is an `int`.
3. Assign `local + 1` back to `entry["sizeBytes"]`.

Keep the malformed-metadata fixture and expected rejection unchanged.

#### `tests/unit/infra/test_issue_planning_candidate.py`

`_valid_candidate` currently declares its identity result as `object`, but callers intentionally use `IssueCandidateIdentity.logical_filename`.

Use a typing-only precise declaration:

1. Import `TYPE_CHECKING`.
2. Under `if TYPE_CHECKING:`, import `IssueCandidateIdentity`.
3. Change the third tuple member in `_valid_candidate`’s return annotation from `object` to the quoted `IssueCandidateIdentity` type.

Do not add a runtime import, cast the value to `Any`, or change candidate construction.

#### `tests/unit/application/test_issue_planning_apply.py`

Three fixture-typing repairs are required.

1. In `_evidence_files`, explicitly declare:

   ```text
   findings: tuple[PlanningReviewFinding, ...]
   ```

   Initialize it to the empty tuple, then assign the existing one-finding tuple for a failed verdict.

2. In the wrong-review-identity test, declare `changes` as `dict[str, object]` before branching. Add the reviewed-head value by key assignment rather than replacing it with an inferred `dict[str, str]`.

3. In the apply-target-drift test, remove the heterogeneous `dict[str, object]` expanded through `**kwargs`. Use typed locals instead:

   ```text
   mode: str
   preflight: object | None
   candidate: VerifiedIssueCandidate | None
   ```

   Set the relevant local for each parameterized branch and call `_run` with the three named arguments explicitly.

The branch behavior and expected result must remain identical.

#### `tests/unit/application/test_issue_planning.py`

Three lists are declared as `list[object]` even though their contents have exact known test types. The later `.exact_attachments` and `.name` access is therefore rejected by mypy.

Use typing-only imports:

```text
SynthesizedPlanningPrompt
PlanningPromptAttachment
```

Import them under `TYPE_CHECKING`, and use quoted annotations so runtime import behavior does not change.

Apply these exact declarations:

* archive Review `calls` → `list["SynthesizedPlanningPrompt"]`;
* git-bound Review `captured` → `list["PlanningPromptAttachment"]`;
* semantic-revision `calls` → `list["SynthesizedPlanningPrompt"]`.

Do not replace these with `list[Any]`, add ignores, or alter Prompt construction.

## PlantUML External Verification

PlantUML’s official GitHub release page lists release `v1.2026.6`, the `plantuml-1.2026.6.jar` asset, and SHA-256:

```text
89948f14c93756c7a3fb7b69078ff37e8489fd79dd430c582b931e2f65358690
```

([GitHub][1])

The JAR must live entirely under the external S12 workspace. It must not be copied into the repository, declared in `pyproject.toml`, included in wheel or sdist, projected into `spec-dock/`, or invoked by product runtime.

### 1. Download and authenticate the official release asset

```bash
set -euo pipefail

: "${S12_EXTERNAL_ROOT:?}"
PLANTUML_ROOT="$S12_EXTERNAL_ROOT/tools/plantuml-1.2026.6"
PLANTUML_JAR="$PLANTUML_ROOT/plantuml-1.2026.6.jar"
EXPECTED_PLANTUML_SHA='89948f14c93756c7a3fb7b69078ff37e8489fd79dd430c582b931e2f65358690'

mkdir -p "$PLANTUML_ROOT"

curl \
  --fail \
  --location \
  --proto '=https' \
  --tlsv1.2 \
  --output "$PLANTUML_JAR" \
  'https://github.com/plantuml/plantuml/releases/download/v1.2026.6/plantuml-1.2026.6.jar'

python3 - "$PLANTUML_JAR" "$EXPECTED_PLANTUML_SHA" <<'PY'
from pathlib import Path
import hashlib
import sys

path = Path(sys.argv[1])
expected = sys.argv[2]
observed = hashlib.sha256(path.read_bytes()).hexdigest()

if observed != expected:
    raise SystemExit(
        f"PlantUML SHA-256 mismatch: expected={expected} observed={observed}"
    )

print(f"plantuml_jar_sha256={observed}")
PY

java -jar "$PLANTUML_JAR" -version |
  tee "$S12_EXTERNAL_ROOT/static-repair/plantuml-version.txt"

grep -F 'PlantUML version 1.2026.6' \
  "$S12_EXTERNAL_ROOT/static-repair/plantuml-version.txt"
```

A missing Java runtime, download failure, checksum mismatch, or version mismatch leaves AC-023 unverified. Do not vendor an alternative binary to bypass the failure.

### 2. Recompute and verify the current guide hash

```bash
ISSUE_DIR='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow'
GUIDE="$ISSUE_DIR/artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"
EXPECTED_GUIDE_SHA='664bd6647104142a298d4f8ec2e9cbed5ab6c67acf85328ff1c5bbfc276f0f78'

python3 - "$GUIDE" "$EXPECTED_GUIDE_SHA" <<'PY'
from pathlib import Path
import hashlib
import sys

path = Path(sys.argv[1])
expected = sys.argv[2]
observed = hashlib.sha256(path.read_bytes()).hexdigest()

if observed != expected:
    raise SystemExit(
        f"guide SHA-256 mismatch: expected={expected} observed={observed}"
    )

print(f"guide_sha256={observed}")
PY
```

### 3. Extract all fenced PlantUML blocks externally

````bash
DIAGRAM_DIR="$S12_EXTERNAL_ROOT/static-repair/guide-plantuml"
rm -rf "$DIAGRAM_DIR"
mkdir -p "$DIAGRAM_DIR"

python3 - "$GUIDE" "$DIAGRAM_DIR" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

guide = Path(sys.argv[1])
destination = Path(sys.argv[2])
text = guide.read_text(encoding="utf-8", errors="strict")

blocks = re.findall(r"```plantuml\n(.*?)```", text, flags=re.DOTALL)
if len(blocks) != 4:
    raise SystemExit(f"expected exactly four PlantUML blocks, found {len(blocks)}")

for index, block in enumerate(blocks, start=1):
    payload = block if block.endswith("\n") else block + "\n"
    path = destination / f"diagram-{index:02d}.puml"
    path.write_text(payload, encoding="utf-8", newline="\n")
    print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
PY
````

### 4. Run syntax-only acceptance

```bash
for diagram in "$DIAGRAM_DIR"/*.puml; do
  java -jar "$PLANTUML_JAR" -checkonly "$diagram"
done
```

Then prove that external tooling produced no repository change:

```bash
git diff --check
git status --short
```

Only the bounded static-repair paths may appear.

## Verification Sequence

Run in this order.

### 1. Focused Ruff checks

```bash
uv run ruff check src/spec_dock tests
uv run ruff format --check src/spec_dock tests
```

Expected: both exit `0`.

### 2. Focused mypy on the six owning files

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning.py
```

Expected: no errors.

### 3. Directly affected tests

Use an external basetemp because the system temp volume previously reached ENOSPC:

```bash
mkdir -p "$S12_EXTERNAL_ROOT/pytest"

uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/static-authoring" \
  tests/unit/authoring_pack/test_backend_invoke_capture.py

uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/static-a" \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py

uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/static-b" \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_apply.py
```

The two S12 A/B lanes must remain Green; the supplied baseline is `359 passed`.

### 4. Provider/projection parity

```bash
cmp \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py \
  spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
```

### 5. Full static gate

```bash
make lint
```

Expected:

```text
ruff check: pass
ruff format check: pass
mypy: pass
```

### 6. Existing S12 static gates

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

Expected validation node count remains `223`, unless a separately explained pre-existing repository-state change has occurred. This repair itself must not change the node count.

Re-run the already established active Issue Planning dependency denylist without expanding it to historical artifacts, documentation, or negative-test literals.

### 7. PlantUML acceptance

Run the external download, hash, version, extraction, and four `-checkonly` commands from the preceding section.

### 8. Exact diff guard

Run the changed-path enforcement script from **Mechanical Formatting**. Then inspect:

```bash
git diff --stat "$SOURCE_HEAD"
git diff --check "$SOURCE_HEAD"
git diff "$SOURCE_HEAD" -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
```

The formatter-only files must contain formatting changes only.

Full-regression and distribution workers remain independent. Their results must be reported exactly as observed and must not be inferred here. Results produced against `6af86ac02a26970f5ca9050089cea2fab80ccff3` are old-tree evidence after this repair and cannot, by themselves, close S12 on the eventual repair commit.

## Stop Conditions

Stop and return control to Main if any of the following occurs:

* Branch or starting HEAD differs from the locked identity.
* The worktree is not clean before the repair.
* Ruff’s output cannot be parsed into an exact file list.
* Ruff identifies a path outside the Issue Planning/static corpus guard.
* A formatter path is missing, untracked, a symlink, or outside `src/spec_dock/` and `tests/`.
* A mypy fix requires changing a public signature, result contract, schema, Prompt, Candidate identity, Human decision, or apply semantics.
* A repair requires `# type: ignore`, mypy configuration changes, a new override, diagnostic suppression, or broad `Any`.
* The provider repair changes argv, timeout, stream capture, exception mapping, shell behavior, or working-directory semantics.
* Official update changes any projected path other than the exact backend-invoke counterpart.
* Provider and dogfood projection bytes differ after update.
* Any changed path falls outside the frozen formatter set plus the seven explicit paths.
* Any new, deleted, or renamed repository file appears.
* Focused Ruff, mypy, or pytest fails.
* `make lint`, SpecDock validation, dependency denylist, or `git diff --check` fails.
* The guide SHA differs from the supplied exact value.
* PlantUML download, SHA-256, version, extraction, or any `-checkonly` run fails.
* PlantUML would need to be added to `pyproject.toml`, package data, wheel, sdist, provider assets, projection, or runtime.
* A worker attempts to infer the still-running full-regression or distribution results.
* A change to Requirement, Design, Plan, Report, `.assurance.json`, Prompt resources, or Skill resources appears.
* The worker attempts to commit, push, perform live Oracle work, or change Human authorization state.

## Worker Handoff

### Bounded dev-coder input

Provide:

```text
repository: chemitaro/spec-dock
branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: 6af86ac02a26970f5ca9050089cea2fab80ccff3
scope: Ruff mechanical formatting + exact six-file mypy repair + one official projection
canonical_changes: forbidden
prompt_or_schema_changes: forbidden
commit_or_push: forbidden
```

### Required worker return

Return all of the following to Main:

```text
source_head
frozen Ruff format path list
frozen path count
frozen path-list SHA-256
exact changed-path inventory
provider-source diff summary
test-only typing diff summary
projection parity result
focused Ruff result
focused mypy result
affected pytest commands and counts
make lint component results
SpecDock validate result and node count
dependency denylist result
git diff --check result
PlantUML asset URL class
PlantUML JAR SHA-256
PlantUML reported version
guide SHA-256
extracted diagram count and SHA-256 values
four PlantUML check results
unverified full-regression/distribution state
repository status after repair
```

Main must independently inspect the diff and rerun the final static gate before deciding whether to commit. This packet does not authorize a Report update, commit, push, S12 closure claim, live dogfood, or downstream S13/S14 work.

DISPOSITION: GO_BOUNDED_STATIC_REPAIR

[1]: https://github.com/plantuml/plantuml/releases "Releases · plantuml/plantuml · GitHub"
