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

Use the attached prompt.md as the complete task brief. Inspect the mandatory GitHub branch and exact HEAD, then return only the requested S12 Markdown work packet.

## Answer

# S12 Implementation Work Packet

## Source Identity

| Field                       | Locked value                                                                                                                                                                                |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository                  | `chemitaro/spec-dock`                                                                                                                                                                       |
| Branch                      | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                                                                                       |
| Exact source HEAD           | `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`                                                                                                                                                  |
| GitHub connector comparison | Branch and exact HEAD are identical; ahead `0`, behind `0`                                                                                                                                  |
| Default-branch fallback     | Forbidden; no default-branch file content was used                                                                                                                                          |
| Issue                       | `iss-00334`                                                                                                                                                                                 |
| Milestone                   | S12 — Full Verification and New-boundary Dogfood                                                                                                                                            |
| Canonical Issue directory   | `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow` |
| `requirement.md` blob       | `8299242edfc584488f0c0caf8a3abbc29b74c61d`                                                                                                                                                  |
| `design.md` blob            | `1897e0dd8b2e238bad15806de1c1b7ea61ba5aba`                                                                                                                                                  |
| `plan.md` blob              | `9700cd915c0bc7f6ffb0b45660e518420c0484dc`                                                                                                                                                  |
| `report.md` blob            | `c7ce67f2469451f7a1411e4d6b815c5bdb82857e`                                                                                                                                                  |
| Current first-guide blob    | `bb6ba2d0259c89c111a24e973f4b9e9df43e048b`                                                                                                                                                  |

The attached brief is the controlling task input. It requires S12 only, exact-HEAD inspection, hermetic-first execution, explicit Human gating, and no canonical amendment or redesign.

Plan §22 assigns S12 the order **hermetic → distribution → static → live**, while §28.4 adds the first-guide defect review and PlantUML 1.2026.6 acceptance check.

The current Report records S11 as closed after a fresh closure Review with P0=`0`, P1=`0`, and `PASS`. Its earlier build, test, and fake-Oracle results are useful baselines but are not fresh S12 evidence.

The connector proves repository identity, not the operator’s local worktree cleanliness, writable external temp capacity, current Oracle authentication, PlantUML JAR availability, current command results, or the exact bytes and paths of the prior Human authorization. Those remain execution-time inputs.

## Disposition

**Proceed immediately with read-only and hermetic verification. Stop before any real Oracle planning submission or tracked repository mutation.**

There is no repository-grounded blocker preventing the hermetic sequence. The historical `S07LiveRunAuthorizationV1` cannot be reused as S12 authority because:

1. It was bound to an older exact HEAD.
2. The current source HEAD is `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`.
3. The inspected repository does not preserve the exact approved authorization record, worktree path, or `/private/tmp/.../live-evidence` destination bytes.
4. Candidate-derived onboarding-companion handling is now part of the live git-bound operation.

Therefore:

| Operation                                                                                               | Current disposition                                                           |
| ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Exact source/remote checks                                                                              | Proceed now                                                                   |
| Unit, integration, distribution, static, sync-probe, guide, and PlantUML checks                         | Proceed now                                                                   |
| Oracle executable resolution, `--version`, and help/capability inspection without a planning submission | Proceed now                                                                   |
| Real `planning create`                                                                                  | Stop for refreshed identity-bound Human authorization                         |
| Real `review planning`                                                                                  | Stop for the same refreshed authorization                                     |
| Human decision generation                                                                               | Human only; never infer or synthesize                                         |
| `planning apply`, its managed commit, and non-force push                                                | Stop for refreshed authorization plus a fresh exact `PlanningHumanDecisionV1` |
| Append-only `report.md` mutation                                                                        | Main only, and only when explicitly included in the refreshed mutation scope  |
| Merge, auto-merge, branch deletion, Issue close, `issue finish`                                         | Human only and outside S12                                                    |

A missing refreshed authorization is not a product defect. It prevents live execution and S12 closure but does not prevent hermetic verification.

## Scope and Non-Goals

### Execution ownership

| Owner                    | Permitted S12 work                                                                                                                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Main only**            | Lock exact source and remote identity; assign bounded workers; reconcile evidence; run final clean/parity checks; present Human gates; append the S12 Report ledger when authorized                  |
| **Worker-safe**          | Read source; run tests and static checks; build into external directories; create external local clones and fresh install targets; extract/check diagrams; return evidence without repository writes |
| **Human-gated operator** | Real Oracle create/review; supply exact authorization and decision bytes; permit apply-owned repository mutation, commit, and push                                                                   |
| **Human only**           | Merge, auto-merge, branch deletion, Issue close, Issue finish                                                                                                                                        |

### In scope

* Fresh verification from the narrowest Issue Planning tests through the explicit full-regression lane.
* Wheel and sdist build, inventory, isolated installation, init/update, installed command, fake PATH Oracle behavior, byte parity, and update idempotence.
* Active dependency denylist and direct-Oracle execution checks.
* Whole-repository lint, SpecDock validation, an external-clone sync no-op check, `git diff --check`, clean tree, and exact remote parity.
* Current first-guide validation, fresh defect-only review, complete PlantUML extraction, and PlantUML 1.2026.6 `-checkonly`.
* AC-001 through AC-025 evidence mapping.
* Fresh QA and security defect-only review.
* Human-gated git-bound dogfood of `iss-00334`.
* Minimum append-only S12 evidence integration.

### Non-goals

* No Requirement, Design, or Plan amendment.
* No provider architecture redesign.
* No new milestone, framework, schema, public command, database, registry, backend abstraction, or persistent Oracle state.
* No GPT-5.6 Prompt tuning.
* No direct edit of root dogfood projections.
* No product dependency on personal `chatgpt-use`, its path or ABI, Project, profile, host, config, LaunchAgent, API fallback, or `oracle-chatgpt`.
* No attempt to rehabilitate legacy text frames or `--write-output`.
* No baseline-failure waiver: a currently failing required check stops S12 even when a similar failure was previously observed.

## Immediate Hermetic Verification Sequence

### 1. Main-only source lock and external workspace

Run from the intended dedicated worktree:

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'
SOURCE_HEAD='ad36524d3d48545690cc7ef9f73a8bfe11ad11ff'
ISSUE_DIR='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow'
GUIDE_REL='artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md'

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git config --get "branch.$BRANCH.remote")" = 'origin'
test "$(git config --get "branch.$BRANCH.merge")" = "refs/heads/$BRANCH"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

git fetch --no-tags --prune origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$SOURCE_HEAD"
test "$(git rev-list --count "HEAD..refs/remotes/origin/$BRANCH")" = '0'
test "$(git rev-list --count "refs/remotes/origin/$BRANCH..HEAD")" = '0'
test -z "$(git status --porcelain=v1 --untracked-files=all)"

: "${S12_EXTERNAL_ROOT:?Set S12_EXTERNAL_ROOT to an external writable volume}"

python3 - "$REPO_ROOT" "$S12_EXTERNAL_ROOT" <<'PY'
from pathlib import Path
import os
import sys

repo = Path(sys.argv[1]).resolve(strict=True)
root = Path(sys.argv[2]).absolute()

if not root.is_absolute():
    raise SystemExit("S12_EXTERNAL_ROOT must be absolute")

for component in (root, *root.parents):
    if component.exists() and component.is_symlink():
        raise SystemExit(f"symlink component rejected: {component}")

root.mkdir(mode=0o700, parents=True, exist_ok=True)
resolved = root.resolve(strict=True)

if (
    resolved == repo
    or resolved.is_relative_to(repo)
    or repo.is_relative_to(resolved)
):
    raise SystemExit("S12_EXTERNAL_ROOT must not overlap the repository")

probe = resolved / ".write-probe"
probe.write_bytes(b"ok\n")
probe.unlink()
try:
    os.chmod(resolved, 0o700)
except OSError:
    pass
PY

mkdir -p \
  "$S12_EXTERNAL_ROOT/tmp" \
  "$S12_EXTERNAL_ROOT/cache" \
  "$S12_EXTERNAL_ROOT/pytest" \
  "$S12_EXTERNAL_ROOT/evidence"

export TMPDIR="$S12_EXTERNAL_ROOT/tmp"
export XDG_CACHE_HOME="$S12_EXTERNAL_ROOT/cache"
export UV_CACHE_DIR="$S12_EXTERNAL_ROOT/cache/uv"
export UV_PROJECT_ENVIRONMENT="$S12_EXTERNAL_ROOT/uv-project-env"
export RUFF_CACHE_DIR="$S12_EXTERNAL_ROOT/cache/ruff"
export MYPY_CACHE_DIR="$S12_EXTERNAL_ROOT/cache/mypy"
export PYTHONDONTWRITEBYTECODE=1
```

Do not fetch or inspect `main`. Workers receive `REPO_ROOT`, `SOURCE_HEAD`, and `S12_EXTERNAL_ROOT` after Main completes this lock.

### 2. Worker-safe test order

The repository policy classifies `tests/cli_runtime/`, `tests/integration/`, and `tests/unit/infra/test_init_update.py` as full-regression tests and skips them unless `--run-full-regression` is explicitly supplied. Ordinary `pytest` remains the fast lane.

Run in this exact escalation order.

#### A. Direct Oracle adapter and artifact boundary

```bash
uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/01-oracle" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-01" \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py
```

#### B. Candidate, contracts, Prompt, and application lifecycle

```bash
uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/02-domain-application" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-02" \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_apply.py
```

#### C. Explicit heavy CLI and Issue Planning integration

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/03-focused-heavy" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-03" \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_e2e.py
```

This is the primary hermetic proof of fresh init → installed Skill → repo-local CLI subprocess → fake `oracle` on PATH → direct argv → typed authoring ZIP or Review JSON → Candidate, Review, Human binding, and apply. The current E2E also asserts one prompt submission, no API credential inheritance, no personal wrapper, and repository-access failure without Candidate or mutation.

#### D. Explicit installer and distribution regression

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/04-distribution" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-04" \
  tests/unit/infra/test_init_update.py
```

#### E. Adjacent Core, authoring-pack, and lifecycle regression

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/05-adjacent" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-05" \
  tests/unit/authoring_pack \
  tests/cli_runtime/test_delegated_authoring.py \
  tests/cli_runtime/test_issue_lifecycle.py
```

#### F. Ordinary fast lane

```bash
uv run pytest -q \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/06-fast" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-06"
```

Record the number of passed and policy-skipped tests. Policy skips are expected only in this fast invocation.

#### G. Explicit relevant full regression

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/07-full" \
  -o "cache_dir=$S12_EXTERNAL_ROOT/pytest/cache-07"
```

Any collection error, failure, unexpected skip, timeout, or ENOSPC stops the sequence. Move temp/basetemp farther onto the approved external volume rather than deleting repository evidence or reducing test coverage.

### 3. Post-test source check

```bash
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$SOURCE_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

## Distribution and Projection Matrix

### Required matrix

| Surface                   | Required proof                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Provider authority        | Exact expected runtime, Skill, Prompt/resource, and docs files exist under `src/spec_dock/assets/`           |
| Wheel                     | Exact provider inventory present once; hash recorded                                                         |
| Sdist                     | Exact provider inventory present once; hash recorded                                                         |
| Fresh wheel install       | Installed `spec-dock` performs init and two updates; repo-local command is executable                        |
| Fresh sdist install       | Same                                                                                                         |
| Installed command         | Top-level and all four command help paths exit `0`                                                           |
| Fake PATH Oracle          | Full-regression E2E records direct executable argv, one prompt submit, safe environment, typed artifact flow |
| Installed/provider parity | Fresh targets match provider-managed bytes                                                                   |
| Dogfood parity            | Root Skill, resources, docs, executable, and runtime match provider bytes                                    |
| Second update             | Tree digest unchanged                                                                                        |
| Active denylist           | Semantic distribution test plus scoped execution-file scan finds no active dependency                        |

The current CLI requires the same Candidate for git-bound Review and apply through `--candidate`; the runbook below must not copy the older pre-S11 command form that omitted it.

### Build and inventory

```bash
set -euo pipefail

DIST_DIR="$S12_EXTERNAL_ROOT/dist"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

uv build --out-dir "$DIST_DIR"

WHEEL_COUNT="$(find "$DIST_DIR" -maxdepth 1 -type f -name '*.whl' | wc -l | tr -d ' ')"
SDIST_COUNT="$(find "$DIST_DIR" -maxdepth 1 -type f -name '*.tar.gz' | wc -l | tr -d ' ')"
test "$WHEEL_COUNT" = '1'
test "$SDIST_COUNT" = '1'

WHEEL="$(find "$DIST_DIR" -maxdepth 1 -type f -name '*.whl' -print)"
SDIST="$(find "$DIST_DIR" -maxdepth 1 -type f -name '*.tar.gz' -print)"

python3 - "$WHEEL" "$SDIST" \
  > "$S12_EXTERNAL_ROOT/evidence/distribution-sha256.txt" <<'PY'
from pathlib import Path
import hashlib
import sys

for name in sys.argv[1:]:
    path = Path(name)
    print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
PY

python3 - "$WHEEL" "$SDIST" <<'PY'
from pathlib import Path
import sys
import tarfile
import zipfile

required_suffixes = (
    "spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
    "spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py",
    "spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md",
    "spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md",
    "spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md",
    "spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md",
    "spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md",
)

for raw in sys.argv[1:]:
    artifact = Path(raw)
    if artifact.name.endswith(".whl"):
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
    else:
        with tarfile.open(artifact, "r:gz") as archive:
            names = archive.getnames()

    for suffix in required_suffixes:
        matches = [name for name in names if name.endswith(suffix)]
        if len(matches) != 1:
            raise SystemExit(
                f"{artifact.name}: expected one {suffix}, found {len(matches)}"
            )
PY

test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

### Fresh install, installed command, parity, and second-update no-op

```bash
set -euo pipefail

PROVIDER_SKILL='src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning'

SKILL_FILES=(
  'SKILL.md'
  'resources/planner-prompt.md'
  'resources/reviewer-prompt.md'
  'resources/revision-prompt.md'
  'resources/transport-output-contract.md'
)

RUNTIME_FILES=(
  'docs/README.md'
  'docs/workflow_issue.md'
  'scripts/spec-dock-chatgpt'
  'scripts/spec_dock_runtime/application/issue_planning.py'
  'scripts/spec_dock_runtime/application/issue_planning_prompt.py'
  'scripts/spec_dock_runtime/commands/issue_planning.py'
  'scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py'
  'scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py'
  'scripts/spec_dock_runtime/domain/issue_planning_candidate.py'
  'scripts/spec_dock_runtime/domain/issue_planning_contracts.py'
  'scripts/spec_dock_runtime/infra/issue_planning_apply.py'
  'scripts/spec_dock_runtime/infra/issue_planning_candidate.py'
  'scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py'
  'scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py'
)

tree_digest() {
  python3 - "$1" <<'PY'
from pathlib import Path
import hashlib
import os
import stat
import sys

root = Path(sys.argv[1]).resolve(strict=True)
records: list[bytes] = []

for path in sorted(
    root.rglob("*"),
    key=lambda item: item.relative_to(root).as_posix().encode("utf-8"),
):
    relative = path.relative_to(root).as_posix()
    metadata = path.lstat()
    mode = stat.S_IMODE(metadata.st_mode)

    if path.is_symlink():
        records.append(
            f"L\0{relative}\0{mode:o}\0{os.readlink(path)}\n".encode()
        )
    elif path.is_file():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(
            f"F\0{relative}\0{mode:o}\0{metadata.st_size}\0{digest}\n".encode()
        )
    elif path.is_dir():
        records.append(f"D\0{relative}\0{mode:o}\n".encode())

print(hashlib.sha256(b"".join(records)).hexdigest())
PY
}

assert_projection_parity() {
  local target_root="$1"
  local rel

  for rel in "${SKILL_FILES[@]}"; do
    cmp \
      "$PROVIDER_SKILL/$rel" \
      "$target_root/.agents/skills/spec-dock-issue-planning/$rel"
  done

  for rel in "${RUNTIME_FILES[@]}"; do
    cmp \
      "src/spec_dock/assets/spec_dock/$rel" \
      "$target_root/spec-dock/$rel"
  done

  test -x "$target_root/spec-dock/scripts/spec-dock-chatgpt"
}

probe_distribution() {
  local label="$1"
  local artifact="$2"
  local venv="$S12_EXTERNAL_ROOT/$label-venv"
  local target="$S12_EXTERNAL_ROOT/$label-target"

  rm -rf "$venv" "$target"
  uv venv "$venv"
  uv pip install --python "$venv/bin/python" "$artifact"

  mkdir "$target"
  "$venv/bin/spec-dock" init "$target"
  "$venv/bin/spec-dock" update "$target"

  "$target/spec-dock/scripts/spec-dock-chatgpt" --help >/dev/null
  "$target/spec-dock/scripts/spec-dock-chatgpt" planning create --help >/dev/null
  "$target/spec-dock/scripts/spec-dock-chatgpt" planning revise --help >/dev/null
  "$target/spec-dock/scripts/spec-dock-chatgpt" review planning --help >/dev/null
  "$target/spec-dock/scripts/spec-dock-chatgpt" planning apply --help >/dev/null

  assert_projection_parity "$target"

  local before
  local after
  before="$(tree_digest "$target")"
  "$venv/bin/spec-dock" update "$target"
  after="$(tree_digest "$target")"
  test "$before" = "$after"

  printf '%s %s\n' "$label" "$after" \
    >> "$S12_EXTERNAL_ROOT/evidence/second-update-tree-digests.txt"
}

probe_distribution wheel "$WHEEL"
probe_distribution sdist "$SDIST"

assert_projection_parity "$REPO_ROOT"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

The existing full-regression E2E is the behavioral fake-Oracle proof. The package inventory and byte comparisons bind that behavior to the wheel, sdist, installed, provider, and dogfood copies; do not build a second product-specific installer harness merely to duplicate it.

### Active dependency denylist

The complete semantic check is the explicit full run of `tests/unit/infra/test_init_update.py`. Supplement it with a source scan restricted to active execution files:

```bash
set -euo pipefail

if rg -n \
  '/Users/|oracle-chatgpt|SPECDOCK_CHATGPT_COMMAND|invoke_backend_with_capture|--write-output|SPECDOCK-ISSUE-PLANNING-(RESPONSE|DOCUMENT)-V1' \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  spec-dock/scripts/spec-dock-chatgpt \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
then
  echo 'active dependency denylist violation' >&2
  exit 1
fi
```

Do not apply the raw token scan to historical artifacts, research snapshots, documentation that explicitly rejects a dependency, or negative-test literals. Those are not active runtime dependencies.

## Static, Guide, and Traceability Checks

### Whole-repository static checks

```bash
set -euo pipefail

make lint
./spec-dock/scripts/spec-dock validate
git diff --check

test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$SOURCE_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

`make lint` runs Ruff check, Ruff format check, and mypy over `src/spec_dock` and `tests`. A failure is not waived by an earlier Report classification.

### SpecDock sync behavior without mutating the source worktree

```bash
set -euo pipefail

SYNC_PROBE="$S12_EXTERNAL_ROOT/sync-probe"
rm -rf "$SYNC_PROBE"

git clone --quiet --no-hardlinks --no-checkout "$REPO_ROOT" "$SYNC_PROBE"
git -C "$SYNC_PROBE" checkout --quiet --detach "$SOURCE_HEAD"

(
  cd "$SYNC_PROBE"

  test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
  test -z "$(git status --porcelain=v1 --untracked-files=all)"

  ./spec-dock/scripts/spec-dock validate
  ./spec-dock/scripts/spec-dock sync --no-github --no-update-active
  ./spec-dock/scripts/spec-dock validate
  git diff --check

  test -z "$(git status --porcelain=v1 --untracked-files=all)"
)
```

A generated diff in the probe means provider/projection or managed workspace state is not closed. Do not run sync against the source worktree merely to hide that result.

### Current first-guide validation and extraction

The exact guide is:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md
```

Its front matter binds it to source HEAD `bf9bc26c00664795842731f665def63a16a7b78c`, and it contains the subordinate-authority note and four required diagram roles.

Run the product validator and extract every PlantUML block:

````bash
set -euo pipefail

GUIDE="$REPO_ROOT/$ISSUE_DIR/$GUIDE_REL"
GUIDE_SOURCE_HEAD='bf9bc26c00664795842731f665def63a16a7b78c'
DIAGRAM_DIR="$S12_EXTERNAL_ROOT/guide-plantuml"

rm -rf "$DIAGRAM_DIR"
mkdir -p "$DIAGRAM_DIR"

PYTHONPATH='src/spec_dock/assets/spec_dock/scripts' \
uv run python - \
  "$GUIDE" \
  "$GUIDE_REL" \
  "$DIAGRAM_DIR" \
  "$REPOSITORY" \
  "$BRANCH" \
  "$GUIDE_SOURCE_HEAD" \
  > "$S12_EXTERNAL_ROOT/evidence/guide-validation.json" <<'PY'
from pathlib import Path
import hashlib
import json
import re
import sys

from spec_dock_runtime.domain.issue_planning_candidate import (
    validate_onboarding_companion,
)

guide = Path(sys.argv[1])
guide_relative = sys.argv[2]
out = Path(sys.argv[3])
expected_repository = sys.argv[4]
expected_branch = sys.argv[5]
expected_head = sys.argv[6]

payload = guide.read_bytes()
validate_onboarding_companion(guide_relative, payload)
text = payload.decode("utf-8", errors="strict")

def front_matter_value(name: str) -> str:
    match = re.search(
        rf'(?m)^{re.escape(name)}:\s*"?(.*?)"?\s*$',
        text,
    )
    if match is None:
        raise SystemExit(f"missing front-matter field: {name}")
    return match.group(1)

observed = {
    "source_repository": front_matter_value("source_repository"),
    "source_branch": front_matter_value("source_branch"),
    "source_head": front_matter_value("source_head"),
}
expected = {
    "source_repository": expected_repository,
    "source_branch": expected_branch,
    "source_head": expected_head,
}
if observed != expected:
    raise SystemExit(f"guide source identity mismatch: {observed!r}")

blocks = re.findall(r"```plantuml\n(.*?)```", text, flags=re.DOTALL)
if len(blocks) < 4:
    raise SystemExit("fewer than four PlantUML blocks")

required_roles = (
    ("system context",),
    ("responsibility", "authority boundary"),
    ("planning sequence", "issue planning sequence"),
    ("implementation roadmap", "remaining implementation roadmap"),
)
lowered = tuple(block.casefold() for block in blocks)
for alternatives in required_roles:
    if not any(any(role in block for role in alternatives) for block in lowered):
        raise SystemExit(f"missing PlantUML role: {alternatives}")

files = []
for index, block in enumerate(blocks, start=1):
    path = out / f"diagram-{index:02d}.puml"
    content = block
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8", newline="\n")
    files.append(
        {
            "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )

print(
    json.dumps(
        {
            "guide_path": guide_relative,
            "guide_sha256": hashlib.sha256(payload).hexdigest(),
            "source_identity": observed,
            "diagram_count": len(blocks),
            "diagrams": files,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
)
PY
````

Run the acceptance-only PlantUML tool:

```bash
set -euo pipefail

: "${PLANTUML_JAR:?Set PLANTUML_JAR to the external PlantUML 1.2026.6 JAR}"
test -f "$PLANTUML_JAR"

java -jar "$PLANTUML_JAR" -version 2>&1 |
  tee "$S12_EXTERNAL_ROOT/evidence/plantuml-version.txt" |
  grep -F 'PlantUML version 1.2026.6'

for diagram in "$DIAGRAM_DIR"/*.puml; do
  java -jar "$PLANTUML_JAR" -checkonly "$diagram"
done
```

The JAR must remain outside the repository, wheel, sdist, provider assets, installed assets, and dogfood projection.

The fresh guide reviewer must explicitly compare the guide’s S01–S14 status and roadmap statements with the current Report, which now closes S08 through S11. Do not pre-waive a stale statement as “historical” and do not automatically rewrite canonical documents. An actual status contradiction is a guide defect under AC-024.

### AC-001 through AC-025 traceability

The canonical Acceptance Criteria and their exact semantics are in `requirement.md`.

| AC         | Primary S12 evidence                                                                                                                                                                                      | Gate                             |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| AC-001     | Candidate domain/application tests; fake create E2E; live create Candidate identity                                                                                                                       | Hermetic + live                  |
| AC-002     | `tests/cli_runtime/test_chatgpt_cli.py`; installed five-help smoke; text/JSON assertions                                                                                                                  | Hermetic                         |
| AC-003     | application preflight tests; adapter tests; repository-access-failure E2E                                                                                                                                 | Hermetic                         |
| AC-004     | Candidate/application revision tests; failed Review → Semantic revision → fresh PASS E2E                                                                                                                  | Hermetic                         |
| AC-005     | Review identity/contracts tests; archive and git-bound E2E; same-Candidate binding                                                                                                                        | Hermetic + live                  |
| AC-006     | Candidate/archive negative fixtures for unsafe, missing, duplicate, wrong-path, or unmanifested payload                                                                                                   | Hermetic                         |
| AC-007     | Human-decision contract tests and apply rejection matrix                                                                                                                                                  | Hermetic + live Human decision   |
| AC-008     | Archive apply/fault integration and `ready` postconditions                                                                                                                                                | Hermetic                         |
| AC-009     | Git-bound apply tests and E2E with same Candidate, binding digest, companion, commit/push parity                                                                                                          | Hermetic + live                  |
| AC-010     | PA-NF fixtures, rollback, recovery-required, publication-pending, and retry tests                                                                                                                         | Hermetic                         |
| AC-011     | Secret, shell, path, symlink, ZIP, and environment-sanitization fixtures                                                                                                                                  | Hermetic + security review       |
| AC-012     | Wheel/sdist inventory; fresh init/update; installed command; provider/installed/dogfood parity                                                                                                            | Hermetic                         |
| AC-013     | Human-authorized real `iss-00334` dogfood ledger with scope mutation `0` before decision                                                                                                                  | Live                             |
| AC-014     | One Issue and current branch evidence; one Delivery PR and Human merge handoff remain downstream                                                                                                          | S13/S14 handoff                  |
| AC-015     | Direct adapter tests, fake Oracle E2E, package parity, active dependency denylist                                                                                                                         | Hermetic                         |
| **AC-016** | Fake `oracle` direct argv; resolved regular executable; version/capability preflight; one prompt submit; missing Oracle process start `0`; unsupported capability prompt submit `0`; fallback `0`         | Hermetic                         |
| **AC-017** | Local and Prompt repository/branch/HEAD binding; no default fallback; repository-access failure output/mutation `0`; source drift → stale                                                                 | Hermetic + live identity         |
| **AC-018** | Captured Prompt role/task/branch/no-fallback/output/Human boundary; attachments reference-only; no instruction attachment or legacy frame                                                                 | Hermetic                         |
| **AC-019** | Exactly one expected authoring ZIP; exact root/inventory; missing/multiple/wrong/unsafe variants produce Candidate `0`                                                                                    | Hermetic + live authoring digest |
| **AC-020** | Oracle metadata path/type/size/SHA validation; private snapshot rehash; same-session harvest; duplicate submit `0`                                                                                        | Hermetic + security review       |
| **AC-021** | Candidate MANIFEST roles, CHECKSUMS, source binding, create/revise/review/apply tests, pre-Human tracked/index/HEAD mutation `0`                                                                          | Hermetic + live                  |
| **AC-022** | Provider/wheel/sdist/fresh init/update/dogfood byte parity and semantic denylist; no personal path, wrapper, Project/profile, or `--write-output`                                                         | Hermetic                         |
| **AC-023** | Exact guide path and source identity; product guide validation; all blocks extracted; PlantUML 1.2026.6 pass; formal reviewer boundary inspected                                                          | Hermetic + fresh guide review    |
| AC-024     | Fresh defect-only guide/QA review checks contradictions, status, Oracle/branch/Human boundary, adapter path, closed JSON return, missing sections, and invalid PlantUML; style-only comments do not block | Fresh review                     |
| AC-025     | Archive transaction/rollback tests; git-bound create → same Candidate Review → approved apply; GB-OB negative fixtures; live canonical three-document hash equality                                       | Hermetic + live                  |

No AC is marked complete from legacy personal-wrapper evidence. AC-013 remains open until a refreshed Human-authorized live run succeeds. AC-014 remains finally owned by the later Delivery PR and Human handoff.

## Live Dogfood Authorization Classification

### Current authority decision

The prior S07 packet defines the exact authorization and decision separation: an initial run authorization permits create and Review, while a later `PlanningHumanDecisionV1` is independently required for apply.

| Action                                              | Existing historical scope usable now? | Reason                                                                                  |
| --------------------------------------------------- | ------------------------------------: | --------------------------------------------------------------------------------------- |
| Read repository and run hermetic verification       |                                   Yes | No live model submission or tracked mutation                                            |
| Resolve `oracle`, inspect version/help/capabilities |                                   Yes | Preflight only; no planning session or Prompt submission                                |
| Real Oracle `planning create`                       |                                **No** | Current HEAD differs; exact old authorization and destination are not repository-proven |
| Real Oracle `review planning`                       |                                **No** | Same identity and destination deficiency                                                |
| Exact Human decision                                |                                **No** | Must bind to the new raw Review bytes and reviewed identity                             |
| Apply-owned companion/decision/sync mutation        |                                **No** | Requires refreshed scope and exact decision                                             |
| Managed commit and non-force push                   |                                **No** | Requires refreshed scope and successful apply                                           |
| Report append                                       |                **No unless restated** | Must be explicitly limited to this Issue’s `report.md`                                  |
| Merge/close/finish                                  |                       Never under S12 | Human only                                                                              |

### Smallest refreshed run authorization

Reuse the existing authorization type; do not create a new framework or broaden the target:

```yaml
authorization_type: S07LiveRunAuthorizationV1
repository: chemitaro/spec-dock
target_issue: iss-00334
worktree_absolute_path: "<exact dedicated worktree path>"
branch: iss-00334-implement-chatgpt-issue-planning-workflow
expected_start_head: ad36524d3d48545690cc7ef9f73a8bfe11ad11ff

planning_mode: git-bound
live_chatgpt_and_github_use: true
oracle_browser_account_precondition_confirmed: true
external_evidence_root_absolute_path: "<exact dedicated external directory>"

repository_mutation_scope:
  before_exact_planning_decision: []
  git_bound_apply:
    canonical_requirement_design_plan_must_remain_byte_identical: true
    candidate_derived_onboarding_companion_write_or_exact_noop: allowed
    deterministic_human_decision_artifact: allowed
    apply_owned_managed_sync_outputs: allowed_only_if_generated_and_diff_reviewed
    planning_commit_on_current_branch: allowed
    fast_forward_push_to_current_branch: allowed
  post_apply_s12:
    current_issue_report_append_only: allowed

merge: false
auto_merge: false
branch_delete: false
issue_close: false
issue_finish: false
```

The exact path values may not be inferred from the old `/private/tmp/...` description. The Human must restate them. Record no browser credential, cookie, profile path, or account secret.

This authorization permits real create and fresh Review. It does not pre-approve adoption. After Review, the Human must separately supply an exact `PlanningHumanDecisionV1`.

## Live Dogfood Runbook

All commands in this section are Human-gated.

### 1. Bind the authorized worktree and evidence root

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
ISSUE_ID='iss-00334'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'
REQUIRED_HEAD='ad36524d3d48545690cc7ef9f73a8bfe11ad11ff'
ISSUE_DIR='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow'

WORKTREE='<EXACT_HUMAN_AUTHORIZED_WORKTREE>'
S12_LIVE_EVIDENCE_ROOT='<EXACT_HUMAN_AUTHORIZED_EXTERNAL_DIRECTORY>'

cd "$WORKTREE"
REPO_ROOT="$(git rev-parse --show-toplevel)"
test "$(cd "$REPO_ROOT" && pwd -P)" = "$(cd "$WORKTREE" && pwd -P)"

python3 - "$REPO_ROOT" "$S12_LIVE_EVIDENCE_ROOT" <<'PY'
from pathlib import Path
import os
import sys

repo = Path(sys.argv[1]).resolve(strict=True)
root = Path(sys.argv[2]).absolute()

if not root.is_absolute():
    raise SystemExit("live evidence root must be absolute")

for component in (root, *root.parents):
    if component.exists() and component.is_symlink():
        raise SystemExit(f"symlink component rejected: {component}")

root.mkdir(mode=0o700, parents=True, exist_ok=True)
root = root.resolve(strict=True)

if root == repo or root.is_relative_to(repo) or repo.is_relative_to(root):
    raise SystemExit("live evidence root must be external and non-overlapping")

for name in ("candidates", "reviews", "operations"):
    path = root / name
    path.mkdir(mode=0o700, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise SystemExit(f"unsafe evidence directory: {path}")

try:
    os.chmod(root, 0o700)
except OSError:
    pass
PY

CANDIDATE_DIR="$S12_LIVE_EVIDENCE_ROOT/candidates"
REVIEW_DIR="$S12_LIVE_EVIDENCE_ROOT/reviews"
OPERATION_DIR="$S12_LIVE_EVIDENCE_ROOT/operations"

CREATE_RESULT="$S12_LIVE_EVIDENCE_ROOT/planning-create-command-result.json"
REVIEW_COMMAND_RESULT="$S12_LIVE_EVIDENCE_ROOT/planning-review-command-result.json"
HUMAN_DECISION="$S12_LIVE_EVIDENCE_ROOT/planning-human-decision.json"
APPLY_RESULT="$S12_LIVE_EVIDENCE_ROOT/planning-apply-command-result.json"
```

### 2. Exact preflight

```bash
test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git config --get "branch.$BRANCH.remote")" = 'origin'
test "$(git config --get "branch.$BRANCH.merge")" = "refs/heads/$BRANCH"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

git fetch --no-tags --prune origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test "$(git rev-list --count "HEAD..refs/remotes/origin/$BRANCH")" = '0'
test "$(git rev-list --count "refs/remotes/origin/$BRANCH..HEAD")" = '0'
test -z "$(git status --porcelain=v1 --untracked-files=all)"

test -x ./spec-dock/scripts/spec-dock-chatgpt
./spec-dock/scripts/spec-dock-chatgpt --help
./spec-dock/scripts/spec-dock-chatgpt planning create --help
./spec-dock/scripts/spec-dock-chatgpt planning revise --help
./spec-dock/scripts/spec-dock-chatgpt review planning --help
./spec-dock/scripts/spec-dock-chatgpt planning apply --help
```

The shipped adapter resolves `oracle` from PATH, resolves the final regular executable, requires version `0.16.1`, invokes it with `shell=False`, submits once, and uses same-session harvest for recovery.

Verify capabilities without starting a planning run:

```bash
ORACLE="$(command -v oracle)"
test -n "$ORACLE"

ORACLE_RESOLVED="$(
  python3 - "$ORACLE" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1]).resolve(strict=True)
if not path.is_file():
    raise SystemExit("resolved Oracle is not a regular file")
print(path)
PY
)"

test -x "$ORACLE_RESOLVED"
test "$("$ORACLE_RESOLVED" --version | tr -d '\r\n')" = '0.16.1'

ROOT_HELP="$("$ORACLE_RESOLVED" --help 2>&1)"
SESSION_HELP="$("$ORACLE_RESOLVED" session --help 2>&1)"

for flag in \
  --engine \
  --file \
  --slug \
  --wait \
  --prompt \
  --browser-attachments
do
  printf '%s\n' "$ROOT_HELP" | grep -F -- "$flag" >/dev/null
done

for flag in --harvest --no-recover; do
  printf '%s\n' "$SESSION_HELP" | grep -F -- "$flag" >/dev/null
done
```

Do not invoke Oracle directly with a planning Prompt. The product command is the only permitted live boundary.

Define a strict result-field reader:

```bash
json_get() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

value = json.loads(open(sys.argv[1], "rb").read())
for part in sys.argv[2].split("."):
    value = value[part]

if isinstance(value, (dict, list)):
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))
else:
    print(value)
PY
}
```

Capture canonical hashes before live work:

```bash
canonical_manifest() {
  python3 - "$ISSUE_DIR" <<'PY'
from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1])
for name in ("design.md", "plan.md", "requirement.md"):
    path = root / name
    print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}")
PY
}

canonical_manifest > "$S12_LIVE_EVIDENCE_ROOT/canonical-preapply-sha256.txt"
```

### 3. Real create

Revalidate immediately before transport:

```bash
test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Execute:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning create \
  --issue "$ISSUE_ID" \
  --output "$CANDIDATE_DIR" \
  --format json |
  tee "$CREATE_RESULT"

test "$(json_get "$CREATE_RESULT" status)" = 'ok'
test "$(json_get "$CREATE_RESULT" reason)" = 'candidate_created'

CANDIDATE_PATH="$(json_get "$CREATE_RESULT" output.candidate_path)"
CANDIDATE_REPORTED_SHA="$(json_get "$CREATE_RESULT" output.candidate_identity.zip_sha256)"
CREATE_BINDING_SHA="$(json_get "$CREATE_RESULT" output.git_bound_operation_binding_sha256)"

test -f "$CANDIDATE_PATH"

CANDIDATE_OBSERVED_SHA="$(
  python3 - "$CANDIDATE_PATH" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
test "$CANDIDATE_OBSERVED_SHA" = "$CANDIDATE_REPORTED_SHA"

python3 - "$CANDIDATE_PATH" "$CANDIDATE_DIR" <<'PY'
from pathlib import Path
import sys

candidate = Path(sys.argv[1]).resolve(strict=True)
root = Path(sys.argv[2]).resolve(strict=True)
if not candidate.is_relative_to(root):
    raise SystemExit("reported Candidate escapes authorized candidate directory")
PY
```

Inspect the Candidate without extracting it:

```bash
python3 - \
  "$CANDIDATE_PATH" \
  "$REPOSITORY" \
  "$BRANCH" \
  "$REQUIRED_HEAD" \
  > "$S12_LIVE_EVIDENCE_ROOT/candidate-inspection.json" <<'PY'
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

candidate = Path(sys.argv[1])
repository = sys.argv[2]
branch = sys.argv[3]
head = sys.argv[4]

with zipfile.ZipFile(candidate) as archive:
    roots = {name.split("/", 1)[0] for name in archive.namelist() if "/" in name}
    if len(roots) != 1:
        raise SystemExit("Candidate must have exactly one root")
    root = next(iter(roots))

    relative_names = {
        name[len(root) + 1 :]
        for name in archive.namelist()
        if name.startswith(root + "/") and not name.endswith("/")
    }

    manifest = json.loads(archive.read(f"{root}/MANIFEST.json"))
    entries = {entry["path"]: entry for entry in manifest["entries"]}
    companions = [
        entry for entry in manifest["entries"]
        if entry["role"] == "onboarding-companion"
    ]
    if len(companions) != 1:
        raise SystemExit("Candidate must contain exactly one onboarding companion")

    companion = companions[0]
    expected = {
        "requirement.md",
        "design.md",
        "plan.md",
        companion["path"],
        "CHECKSUMS.sha256",
        "MANIFEST.json",
        "PLACEHOLDER-ORACLE-MAP.json",
        "SOURCE-BASELINE.json",
    }
    if relative_names != expected or set(entries) != expected:
        raise SystemExit("Candidate inventory mismatch")

    role_by_path = {path: entry["role"] for path, entry in entries.items()}
    expected_roles = {
        "requirement.md": "requirement",
        "design.md": "design",
        "plan.md": "plan",
        companion["path"]: "onboarding-companion",
    }
    for path, role in expected_roles.items():
        if role_by_path.get(path) != role:
            raise SystemExit(f"wrong role for {path}")

    checksum_lines = archive.read(f"{root}/CHECKSUMS.sha256").decode("ascii").splitlines()
    checksums = {}
    for line in checksum_lines:
        digest, path = line.split("  ", 1)
        checksums[path] = digest

    for path in expected - {"CHECKSUMS.sha256"}:
        observed = hashlib.sha256(archive.read(f"{root}/{path}")).hexdigest()
        if checksums.get(path) != observed:
            raise SystemExit(f"checksum mismatch: {path}")

    source = json.loads(archive.read(f"{root}/SOURCE-BASELINE.json"))
    if (
        source["source_repository"] != repository
        or source["source_branch"] != branch
        or source["source_head"] != head
    ):
        raise SystemExit("Candidate source binding mismatch")

    planner_sha = source["planner_payload_sha256"]
    planner_size = source["planner_payload_size"]
    if re.fullmatch(r"[0-9a-f]{64}", planner_sha) is None:
        raise SystemExit("invalid authoring ZIP SHA")
    if not isinstance(planner_size, int) or planner_size <= 0:
        raise SystemExit("invalid authoring ZIP size")

    result = {
        "candidate_filename": candidate.name,
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "authoring_zip_sha256": planner_sha,
        "authoring_zip_size": planner_size,
        "companion_path": companion["path"],
        "companion_sha256": checksums[companion["path"]],
        "source_repository": source["source_repository"],
        "source_branch": source["source_branch"],
        "source_head": source["source_head"],
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
PY
```

`authoring_zip_sha256` and `authoring_zip_size` are the sanitized proof that the downloadable Oracle authoring ZIP was accepted by the private adapter and Candidate builder. Do not inspect or copy Oracle session storage, raw transcript, or private staging files.

Verify no pre-Human repository mutation:

```bash
test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

### 4. Fresh git-bound Review of the same Candidate

```bash
REVIEWED_HEAD="$(git rev-parse HEAD)"
test "$REVIEWED_HEAD" = "$REQUIRED_HEAD"

./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue "$ISSUE_ID" \
  --mode git-bound \
  --candidate "$CANDIDATE_PATH" \
  --reviewed-head "$REVIEWED_HEAD" \
  --output "$REVIEW_DIR" \
  --format json |
  tee "$REVIEW_COMMAND_RESULT"

test "$(json_get "$REVIEW_COMMAND_RESULT" status)" = 'ok'
test "$(json_get "$REVIEW_COMMAND_RESULT" reason)" = 'review_completed'
test "$(json_get "$REVIEW_COMMAND_RESULT" output.git_bound_operation_binding_sha256)" = "$CREATE_BINDING_SHA"

REVIEW_RESULT_FIELD="$(json_get "$REVIEW_COMMAND_RESULT" output.review_result_file)"
case "$REVIEW_RESULT_FIELD" in
  /*) REVIEW_RESULT="$REVIEW_RESULT_FIELD" ;;
  *)  REVIEW_RESULT="$REVIEW_DIR/$REVIEW_RESULT_FIELD" ;;
esac

REVIEW_REPORTED_SHA="$(json_get "$REVIEW_COMMAND_RESULT" output.review_result_sha256)"
REVIEWED_IDENTITY_SHA="$(json_get "$REVIEW_COMMAND_RESULT" output.reviewed_identity_sha256)"

test -f "$REVIEW_RESULT"

REVIEW_OBSERVED_SHA="$(
  python3 - "$REVIEW_RESULT" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
test "$REVIEW_OBSERVED_SHA" = "$REVIEW_REPORTED_SHA"
```

Enforce the exact verdict rule:

```bash
python3 - "$REVIEW_RESULT" \
  > "$S12_LIVE_EVIDENCE_ROOT/review-classification.txt" <<'PY'
import json
import sys

review = json.loads(open(sys.argv[1], "rb").read())
findings = review["findings"]

blocking = [item for item in findings if item["severity"] in ("p0", "p1")]
nonblocking = [item for item in findings if item["severity"] in ("p2", "p3")]
expected = "fail" if blocking else "pass"

if review["verdict"] != expected:
    raise SystemExit("Review verdict contradicts P0/P1 findings")

print(f"verdict={review['verdict']}")
print(f"p0={sum(item['severity'] == 'p0' for item in findings)}")
print(f"p1={sum(item['severity'] == 'p1' for item in findings)}")
print(f"p2={sum(item['severity'] == 'p2' for item in findings)}")
print(f"p3={sum(item['severity'] == 'p3' for item in findings)}")

if blocking:
    for item in blocking:
        print(
            f"BLOCKING {item['id']} {item['severity']} "
            f"{item['exact_location']}"
        )
    raise SystemExit(20)
PY
```

Interpretation:

* P0=`0` and P1=`0`: Review must be `pass`; proceed to the Human decision gate.
* P2/P3 only: do not revise or mutate solely for those observations.
* Any P0/P1: stop. The public Semantic revision path accepts an archive-candidate Review, not this git-bound Review. Under the current no-canonical-rewrite target and authorization, do not fabricate an archive Review, revision request, or canonical repair. A new bounded repair and fresh identity/authorization cycle is required.

### 5. Exact Human decision — mandatory stop

Present the Human with:

* Repository, branch, and reviewed HEAD.
* Candidate identity and Candidate SHA-256.
* Authoring ZIP SHA-256 and byte size from `SOURCE-BASELINE.json`.
* Candidate-derived operation-binding SHA-256.
* Companion path and SHA-256.
* Full raw Review result.
* Reviewed identity and `reviewed_identity_sha256`.
* Raw Review file SHA-256.
* P0/P1/P2/P3 counts and verdict.
* Canonical pre-apply SHA-256 manifest.
* Confirmation that tracked tree, index, and HEAD remain unchanged.

The Human must supply the exact bytes of:

```text
<S12_LIVE_EVIDENCE_ROOT>/planning-human-decision.json
```

Closed shape:

```json
{
  "schema_version": 1,
  "issue_id": "iss-00334",
  "reviewed_identity": "<copy the complete reviewed_identity object verbatim from the Review>",
  "reviewed_identity_sha256": "<exact reviewed_identity_sha256>",
  "review_result_sha256": "<exact raw Review file SHA-256>",
  "decision": "approved",
  "plan_adoption": true,
  "implementation_start": true,
  "decided_at": "<Human-supplied ISO-8601 timestamp with timezone>"
}
```

The placeholder above represents an object, not a string, in the actual file. Codex, ChatGPT, workers, and scripts must not generate, infer, normalize, or pre-approve these bytes.

A rejected decision stops the run without apply.

### 6. Apply, managed commit/push, and parity

Only after exact approval:

```bash
test -f "$HUMAN_DECISION"
test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$REVIEWED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

git fetch --no-tags --prune origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REVIEWED_HEAD"

./spec-dock/scripts/spec-dock-chatgpt planning apply \
  --issue "$ISSUE_ID" \
  --mode git-bound \
  --candidate "$CANDIDATE_PATH" \
  --review-result "$REVIEW_RESULT" \
  --human-decision "$HUMAN_DECISION" \
  --expected-head "$REVIEWED_HEAD" \
  --reviewed-head "$REVIEWED_HEAD" \
  --output "$OPERATION_DIR" \
  --format json |
  tee "$APPLY_RESULT"

test "$(json_get "$APPLY_RESULT" status)" = 'ready'
test "$(json_get "$APPLY_RESULT" reason)" = 'adoption_published'

APPLY_OPERATION_ID="$(json_get "$APPLY_RESULT" output.operation_id)"
DECISION_ARTIFACT_PATH="$(json_get "$APPLY_RESULT" output.decision_artifact_path)"
LOCAL_COMMIT="$(json_get "$APPLY_RESULT" output.local_commit)"
REMOTE_COMMIT="$(json_get "$APPLY_RESULT" output.remote_commit)"

test -n "$APPLY_OPERATION_ID"
test -f "$DECISION_ARTIFACT_PATH"
test "$LOCAL_COMMIT" = "$REMOTE_COMMIT"

git fetch --no-tags --prune origin \
  "refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"

test "$(git rev-parse HEAD)" = "$LOCAL_COMMIT"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$LOCAL_COMMIT"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Verify canonical documents remain byte-identical:

```bash
canonical_manifest > "$S12_LIVE_EVIDENCE_ROOT/canonical-postapply-sha256.txt"

cmp \
  "$S12_LIVE_EVIDENCE_ROOT/canonical-preapply-sha256.txt" \
  "$S12_LIVE_EVIDENCE_ROOT/canonical-postapply-sha256.txt"
```

Inspect the managed commit:

```bash
git show --stat --oneline --decorate "$LOCAL_COMMIT"
git show --name-status --format= "$LOCAL_COMMIT"
git show --check "$LOCAL_COMMIT"
```

Permitted changed paths are limited to:

* The runtime-reported deterministic Human decision artifact.
* The Candidate-derived onboarding-companion target, either a managed write or exact-byte no-op.
* Apply-owned sync outputs that were generated and individually diff-reviewed.
* No `report.md` change unless separately authorized.
* No Requirement, Design, or Plan change.
* No unrelated Issue, Epic, Initiative, portfolio, workflow, or user-owned file.

Do not manually commit, force-push, amend, rebase, reset, or substitute another Candidate. A `publication_pending`, remote divergence, unconfirmed rollback, `recovery_required`, stale identity, or non-`ready` result is a stop condition. Resume only through the product’s exact same operation inputs when the product reports resumability.

## QA and Security Review Contract

Run both reviews in fresh, read-only reviewer contexts after all available hermetic and live evidence is stable.

### QA review inputs

* Exact repository, branch, and source or post-apply pushed HEAD.
* Canonical `requirement.md`, `design.md`, append-only `plan.md`, and current `report.md`.
* Current first guide.
* This AC-001 through AC-025 traceability ledger.
* Exact commands, timestamps, exit codes, test counts, and policy-skip counts.
* Fast-lane and explicit full-regression evidence.
* Wheel/sdist filenames, hashes, and inventory evidence.
* Fresh init/update, installed help, byte-parity, and second-update digest evidence.
* Static, validation, external sync-probe, diff, clean-tree, and remote-parity evidence.
* Guide validator output, extracted diagram hashes, PlantUML version, and `-checkonly` results.
* Live Candidate, authoring-ZIP digest/size, binding, companion, Review, Human decision, apply, commit, and remote-parity evidence.
* Explicit statement that old personal-wrapper evidence was excluded.
* Any Human-authorization stop, without treating it as a product defect.

### Security review inputs

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
* Prompt synthesis and resources.
* Candidate/archive validation and apply transaction modules.
* Corresponding provider, dogfood, unit, integration, and distribution tests.
* PATH resolution and final executable identity.
* Oracle version/capability checks and `shell=False`.
* One-submit and same-session recovery behavior.
* Child-environment allowlist and API credential removal.
* Prompt-instruction versus reference-attachment separation.
* Exact-branch/no-fallback enforcement.
* Artifact containment, `lstat`/regular-file/symlink checks, metadata size/SHA, copy and rehash.
* ZIP path, collision, encryption, size, CRC, inventory, and checksum defenses.
* Review/Human/Candidate binding, pre-Human immutability, rollback, publication retry, and remote divergence.
* Active dependency denylist and diagnostic redaction.

### Defect-only rules

* Review only concrete defects against the accepted contract.
* Do not propose architectural improvements, Prompt tuning, new commands, broader workflows, new schemas, or optional enhancements.
* Exact PASS rule: **P0=`0` and P1=`0`**.
* Any P0 or P1 requires `FAIL`.
* P2/P3 are non-blocking and do not authorize mutation solely for improvement.
* A P0/P1 repair must be limited to the exact defect, followed by the affected focused tests, the explicit full-regression lane, and a new fresh Review.
* Missing live evidence because refreshed authorization has not been supplied is an authorization stop and prevents S12 closure; it is not by itself a code finding.
* Legacy personal-wrapper or old live evidence cannot satisfy any new-boundary PASS obligation.

## Evidence and Report Updates

### Minimum append-only Report ledger

Main appends one section to:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md
```

Recommended heading:

```markdown
## 2026-07-30 — S12 Full Verification and New-boundary Dogfood
```

Record only verified evidence:

1. Exact starting repository, branch, HEAD, remote parity, and canonical blob identities.
2. External-temp mitigation class and whether ENOSPC recurred; do not record private absolute paths.
3. Every test command, lane, timestamp, exit code, passed/failed/skipped counts, and duration.
4. Explicit distinction between default fast and `--run-full-regression`.
5. Wheel and sdist filenames, SHA-256 values, and required inventory result.
6. Fresh wheel/sdist init/update results, installed help results, execution-bit result, and second-update tree digests.
7. Provider/installed/dogfood parity path set and result.
8. Active dependency denylist result.
9. `make lint`, validate, external sync-probe, `git diff --check`, and clean-tree results.
10. Guide path, blob/SHA, front-matter source identity, required-section result, diagram count/hashes, PlantUML version, and syntax result.
11. Fresh guide defect-only Review artifact, hash, P0/P1 counts, and verdict.
12. AC-001 through AC-025 status with direct evidence references.
13. Refreshed run-authorization record SHA-256 and scope classification; retain private paths externally.
14. Live Candidate identity, Candidate SHA, authoring ZIP SHA/size, operation-binding SHA, and companion path/SHA.
15. Review identity digest, raw Review SHA, P0–P3 counts, and verdict.
16. Human decision SHA.
17. Apply operation ID, status/reason, local/remote commit, changed-path inventory, canonical-documents-unchanged result, and clean remote parity.
18. Intervention count, handoff count/items, wall-clock duration, recovery attempts, and failure classifications.
19. Fresh QA and security Review artifact hashes and verdicts.
20. Explicit statements: no canonical amendment; no old-wrapper evidence credited; no merge, auto-merge, branch deletion, Issue close, or Issue finish performed.

### Evidence placement

Permitted repository evidence:

* Sanitized formal guide, QA, and security Review JSON or Markdown under the Issue `artifacts/` directory.
* Sanitized command summaries and hashes when needed for durable traceability.
* The append-only Report ledger.

Keep external:

* Candidate ZIP.
* Raw authoring ZIP or Oracle session data.
* Raw transcript.
* Browser or account data.
* Private worktree/evidence paths.
* Cookies, credentials, profiles, host configuration.
* Full environment dumps.
* Operation scratch data not explicitly managed by the product.

`requirement.md`, `design.md`, and `plan.md` must remain byte-identical.

When the refreshed authorization omits `current_issue_report_append_only`, retain the evidence externally, report the authorization stop, and do not claim S12 closed. The later mandatory evidence commit/push remains S13-owned; this packet does not silently absorb S13 or S14.

## Exit Checklist

* [ ] GitHub branch is exactly `iss-00334-implement-chatgpt-issue-planning-workflow`.
* [ ] Starting HEAD is exactly `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`.
* [ ] Local and fetched remote branch are identical.
* [ ] Source worktree is clean before and after hermetic work.
* [ ] Adapter/artifact focused unit tests pass.
* [ ] Candidate/contracts/Prompt/application focused tests pass.
* [ ] Explicit heavy CLI and Issue Planning integration tests pass.
* [ ] Explicit installer/distribution tests pass.
* [ ] Adjacent Core, authoring-pack, and lifecycle tests pass.
* [ ] Ordinary fast lane passes with only policy-expected skips.
* [ ] Explicit full regression passes without unexpected skips.
* [ ] Wheel and sdist build successfully into the external volume.
* [ ] Wheel and sdist each contain the complete provider inventory exactly once.
* [ ] Fresh wheel and sdist installs complete init and two updates.
* [ ] Installed command and all four subcommand help paths exit `0`.
* [ ] Installed repo-local command remains executable.
* [ ] Fake PATH Oracle E2E proves direct argv, one submit, typed outputs, and no fallback.
* [ ] Provider, fresh installed, and root dogfood bytes are equal for the complete parity set.
* [ ] Second update is a byte/mode tree no-op for wheel and sdist targets.
* [ ] Active dependency denylist passes.
* [ ] `make lint` passes.
* [ ] SpecDock validate passes.
* [ ] External-clone sync is a clean no-op and validates afterward.
* [ ] `git diff --check` passes.
* [ ] Current guide passes product completeness validation.
* [ ] Every PlantUML block is extracted and PlantUML 1.2026.6 `-checkonly` passes.
* [ ] Fresh guide defect-only Review has P0=`0` and P1=`0`.
* [ ] AC-001 through AC-025 have direct evidence or an explicit downstream/live gate.
* [ ] Fresh QA Review has P0=`0` and P1=`0`.
* [ ] Fresh security Review has P0=`0` and P1=`0`.
* [ ] Refreshed Human authorization binds exact worktree, branch, HEAD, target, mode, Oracle precondition, mutation scope, and evidence root.
* [ ] Real create returns one Candidate from an accepted authoring ZIP.
* [ ] Live Review uses the same Candidate and exact reviewed HEAD.
* [ ] Live Review has P0=`0`, P1=`0`, and `pass`.
* [ ] Human supplies exact `PlanningHumanDecisionV1` bytes.
* [ ] Git-bound apply returns `ready/adoption_published`.
* [ ] Canonical Requirement, Design, and Plan hashes are unchanged.
* [ ] Apply commit contains only authorized managed paths.
* [ ] Local HEAD equals remote branch HEAD after non-force publication.
* [ ] S12 Report/evidence ledger is append-only and authorized.
* [ ] Final worktree is clean.
* [ ] Merge, auto-merge, branch deletion, Issue close, and Issue finish remain untouched.

S12 cannot be marked closed while any live authorization, Review, Human decision, apply, parity, guide Review, QA Review, security Review, or required check remains incomplete.

## Stop Conditions

Stop immediately on any of the following:

* Repository, branch, starting HEAD, upstream, or remote ref mismatch.
* Detached HEAD, dirty tracked/index/untracked state, or unauthorized source mutation.
* Default-branch or alternate-branch fallback.
* External temp/evidence path overlaps the repository, contains symlink components, is unwritable, or exhausts space.
* Any focused, fast, full-regression, build, installer, parity, no-op, lint, validation, sync, diff, guide, or PlantUML failure.
* Unexpected policy skip in the explicit full-regression run.
* Wheel or sdist missing a required provider asset.
* Installed or dogfood bytes differing from provider authority.
* Active personal path, personal wrapper, Project/profile/host/config, arbitrary backend, API fallback, legacy frame, or `--write-output` dependency.
* Current guide contradicting canonical documents or current milestone status with a fresh P0/P1 finding.
* PlantUML tool becoming a product or package dependency.
* Attempt to use the old exact-HEAD authorization without a refreshed Human record.
* Unverified or inferred worktree or evidence destination.
* Missing, non-executable, replaced, or unsupported Oracle.
* Real planning call before authorization.
* Missing, ambiguous, unsafe, incorrectly named, wrong-root, or wrong-inventory authoring ZIP.
* Repository-access-failure response, missing exact current branch, or source drift.
* Candidate identity, bytes, source baseline, operation binding, companion path/SHA, reviewed identity, Review SHA, or Human decision mismatch.
* Any P0/P1 in the live git-bound Review.
* Attempt to revise from a git-bound Review under this authorization.
* Human rejection or absent exact decision bytes.
* Any pre-Human tracked tree, index, HEAD, canonical, or companion-target mutation.
* Apply result other than `ready/adoption_published`.
* Unconfirmed rollback, `recovery_required`, `publication_pending`, or remote divergence.
* Canonical Requirement, Design, or Plan byte change.
* Unauthorized changed path, manual commit, force push, amend, rebase, or reset.
* Secret, raw transcript, private Oracle path, browser state, or credential leakage.
* A requested change that requires canonical amendment, a new public interface, persistent registry/database, generic backend framework, or architecture redesign.
* Any attempt to merge, enable auto-merge, delete the branch, close the Issue, or run Issue finish.

## Worker Handoff

| Handoff                              | Scope                                                                                      | Required return                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| **Main → Adapter worker**            | Direct-Oracle and artifact unit tests only                                                 | Exact HEAD; commands; exit codes; pass/fail counts; repository status before/after; no edits |
| **Main → Domain/application worker** | Candidate, contracts, Prompt, lifecycle, and apply focused tests                           | Same, plus any exact failing node IDs                                                        |
| **Main → Heavy-regression worker**   | CLI, integration, E2E, adjacent Core with explicit `--run-full-regression`                 | Counts, skips, durations, basetemp location class, failure logs, no edits                    |
| **Main → Distribution worker**       | External build, inventory, fresh installs, help, parity, no-op, denylist                   | Artifact names/hashes; inventory report; target tree digests; parity result                  |
| **Main → Static/guide worker**       | `make lint`, validate, external sync-probe, guide validation, diagram extraction, PlantUML | Command results; guide and diagram hashes; PlantUML version/result; no guide edit            |
| **Main → Fresh guide reviewer**      | Canonical documents, current Report, exact guide, AC-023/024                               | Defect-only findings; P0–P3 counts; exact PASS/FAIL                                          |
| **Main → Fresh QA reviewer**         | Complete S12 evidence and AC ledger                                                        | Defect-only findings; evidence gaps; exact PASS/FAIL                                         |
| **Main → Fresh security reviewer**   | Adapter, artifact, Candidate/apply boundaries, tests, denylist, live evidence              | Defect-only findings; exact PASS/FAIL                                                        |
| **Main → Human**                     | Refreshed run authorization brief                                                          | Exact target/worktree/branch/HEAD/mode/Oracle precondition/evidence root/mutation scope      |
| **Human → Live operator**            | Approved authorization bytes                                                               | Authorization SHA and exact allowed operations                                               |
| **Live operator → Human**            | Candidate, Review, hashes, findings, canonical pre-hashes                                  | Exact decision brief; no inferred approval                                                   |
| **Human → Live operator**            | `PlanningHumanDecisionV1`                                                                  | Exact file bytes and SHA                                                                     |
| **Live operator → Main**             | Apply and publication evidence                                                             | Operation ID; result; commit SHAs; changed paths; canonical equality; remote parity          |
| **Main → S13**                       | Sanitized S12 evidence and append-only Report diff                                         | Exact source/post-apply HEAD; evidence index; clean-state result; no S13 execution claim     |

Every worker response must include:

```text
source_head
commands_executed
exit_codes
test_or_check_summary
external_artifact_names_and_sha256
repository_status_before
repository_status_after
findings_or_none
unverified_items
```

Workers must not edit `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`, provider assets, projections, or tests. A concrete P0/P1 is returned to Main for a separately bounded repair decision; it is not repaired opportunistically.

DISPOSITION: GO_HERMETIC_THEN_HUMAN_GATE
