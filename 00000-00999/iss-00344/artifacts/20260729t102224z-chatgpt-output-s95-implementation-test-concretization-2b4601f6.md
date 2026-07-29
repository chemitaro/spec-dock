# Recommendation

Proceed with S95 as a **single, auditable provider-to-mirror projection transaction**:

1. Pin the local checkout to branch `iss-00344-workbench-shell-scaffolding` at exact commit `2b4601f6e74053f3513f5fe66334c9999bf71c8b`.
2. Create external, deterministic manifests for the complete `spec-dock/initiatives/**` tree and every root/node `.workbench` state, including ignored payload.
3. Execute exactly one formal `uv run spec-dock update .`.
4. Require an exact ten-path managed-mirror delta.
5. Prove the protected snapshots are unchanged.
6. Run direct provider/mirror byte parity, the existing focused parity/no-backfill pytest nodes, `make lint`, and default `uv run pytest`.
7. Return evidence to the orchestrator; do not edit `report.md` until the final protected-state comparison has completed.

The expected primary implementation has **no provider, installer, test, specification, or existing Workbench edits**. It should consist only of the ten generated checked-in mirror changes listed below. A second update invocation is prohibited within the same snapshot envelope. This packet follows the attached S95 brief. 

---

# Repository facts observed at exact commit

## Source identity

The GitHub connector successfully opened `chemitaro/spec-dock`, Issue #344, the requested branch, and exact commit. The branch-to-commit comparison returned `identical`. Issue #344 is open and titled “Workbench Shell Scaffolding.”

Exact commit:

```text
2b4601f6e74053f3513f5fe66334c9999bf71c8b
```

That commit records S90 as committed and approved and admits S95.

The active plan is approved and defines provider-first ownership: Issue #344 owns its managed mirror projection and default PR lane; candidate-wheel consumer E2E, generic-import integration, opt-in full regression, and Epic-wide integration remain Issue #346 work.

## Update behavior relevant to S95

The installer treats `docs`, `templates`, `scripts`, and `system` as managed directories. On update, it replaces those managed trees, copies the provider `.gitignore`, and deliberately leaves `spec-dock/initiatives/**` outside the managed replacement. Root `.workbench/README.md` is copied only when `spec-dock` is fresh; an existing dogfood workspace therefore must not receive root backfill.

The `update` command requires the existing workspace, preflights managed skill installation, calls `_install_spec_dock(..., force=True)`, and then refreshes managed skills.

Consequently:

* Managed files may be physically rewritten even when their bytes remain identical.
* Git-visible differences must nevertheless be limited to the exact expected mirror paths.
* Any `.agents/**`, `.codex/**`, `.github/**`, `spec-dock/system/**`, `spec-dock/active/**`, or `spec-dock/spec-dock.version` Git delta is unexpected.
* `spec-dock/.workbench/README.md` is not an expected output because this is an update of an existing workspace.

## Exact committed provider/mirror divergence

The provider `.gitignore` has the new three-rule README-only tracking contract, while the checked-in mirror still ignores the whole `.workbench/` directory.

The four provider Workbench README assets are present and byte-identical. Their checked-in template-mirror counterparts are absent at this commit.

The three S90 provider docs and `templates/README.md` have different blob identities from their checked-in mirrors.

The provider runtime scaffolder contains the reviewed byte-stable exact-copy behavior, while the checked-in runtime mirror still contains the prior text-write implementation.

These observations give an exact expected projection of **six modified files and four added files**.

## Existing tests

The repository already contains these exact parity nodes:

```text
tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets

tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets

tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets
```

The docs node calls the existing provider/mirror byte comparator. The template node compares the complete template inventory, entry kinds, and file contents. The runtime node compares the complete runtime inventory and bytes.

The default test policy marks the docs and template parity nodes as required-fast tests. The runtime parity node remains under the heavy-file policy and needs `--run-full-regression` when run as an exact focused node. Default `uv run pytest` must not include the bare full-regression lane.

Two exact update/no-backfill tests also exist:

```text
tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme

tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_preserves_opaque_workbenches_while_refreshing_managed_assets
```

The first verifies that update does not restore a removed README or overwrite a user-owned README, including mtime preservation. The second verifies binary Workbench sentinels at root, Initiative, Epic, and Issue scopes while managed assets are refreshed.

The report already classifies the stale dogfood parity as an S95 handoff rather than an S03 defect or waiver.

---

# Pre-projection checklist

Run from the repository root in Bash:

```bash
set -euo pipefail

EXPECTED_BRANCH='iss-00344-workbench-shell-scaffolding'
EXPECTED_HEAD='2b4601f6e74053f3513f5fe66334c9999bf71c8b'
ISSUE_DIR='spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00344-workbench-shell-scaffolding'

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

test "$(git branch --show-current)" = "$EXPECTED_BRANCH"
test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"

git fetch --no-tags origin \
  "refs/heads/${EXPECTED_BRANCH}:refs/remotes/origin/${EXPECTED_BRANCH}"

test "$(git rev-parse "refs/remotes/origin/${EXPECTED_BRANCH}")" = "$EXPECTED_HEAD"

git diff --quiet
git diff --cached --quiet
test -z "$(git status --porcelain=v1 --untracked-files=all)"

grep -F '| S90 | committed |' "$ISSUE_DIR/report.md"
grep -F '| approved | S95 admitted |' "$ISSUE_DIR/report.md"

uv run python - <<'PY'
from pathlib import Path
import spec_dock.cli

repo = Path.cwd().resolve()
observed = Path(spec_dock.cli.__file__).resolve()
expected = repo / "src" / "spec_dock" / "cli.py"
assert observed == expected, (
    "uv run spec-dock is not resolving to the exact checkout: "
    f"observed={observed}, expected={expected}"
)
print(observed)
PY

test "$(uv run spec-dock --version)" = 'spec-dock 0.2.3'

SNAPDIR="$(mktemp -d "${TMPDIR:-/tmp}/spec-dock-s95.XXXXXXXX")"
export REPO SNAPDIR
printf 'S95 evidence directory: %s\n' "$SNAPDIR"
```

## Existing direct README visibility preflight

The new `.gitignore` makes a direct root/node `.workbench/README.md` tracking-eligible. A locally existing but currently ignored direct README could therefore appear as an allowlist-external untracked file after projection even though update did not change its bytes.

Detect that condition before consuming the one allowed update attempt:

```bash
while IFS= read -r -d '' workbench; do
  readme="${workbench}/README.md"

  if [ -e "$readme" ] || [ -L "$readme" ]; then
    rel="${readme#"$REPO"/}"

    if ! git ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then
      printf '%s\n' \
        "STOP: existing untracked direct Workbench README would become Git-visible: $rel" \
        >&2
      exit 20
    fi
  fi
done < <(
  printf '%s\0' "$REPO/spec-dock/.workbench"
  find "$REPO/spec-dock/initiatives" \
    -name .workbench -prune -print0
)
```

Do not delete, move, rename, stage, or locally exclude such a file. Stop for disposition.

---

# Snapshot contract

## Protected surfaces

Two manifests are mandatory:

1. **Initiatives manifest**

   * The complete `spec-dock/initiatives` tree.
   * Includes directories, empty directories, regular files, symlinks, and special entries.
   * Does not follow symlinks.

2. **Workbench manifest**

   * `spec-dock/.workbench`, including a `missing` record if absent.
   * `.workbench` for every node directory containing `.meta.json`, including missing markers.
   * Any additional/orphan `.workbench` entry found under `spec-dock/initiatives`.
   * Includes ignored payload because traversal reads the filesystem directly rather than using Git.

Each row records:

```text
relative path
entry type
SHA-256
mode
mtime_ns
size where applicable
```

For regular files, SHA-256 covers raw bytes. For symlinks, it covers the raw link target. Directories and missing paths use stable type-marker hashes; the path/type set therefore captures empty-directory addition or removal. `mtime_ns` is an additional no-backfill guard because AC-344-005 requires existing Workbench mtime preservation. The accepted requirement forbids update from adding or mutating existing root/node Workbench state.

## Deterministic snapshot helper

Create this helper only under `$SNAPDIR`:

```bash
cat > "$SNAPDIR/snapshot.py" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Iterator

repo = Path(os.environ["REPO"]).resolve()
snapshot_kind = sys.argv[1]
output_path = Path(sys.argv[2])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(repo).as_posix()


def describe(path: Path) -> dict[str, object]:
    rel = relative(path)

    try:
        metadata = os.lstat(path)
    except FileNotFoundError:
        return {
            "path": rel,
            "type": "missing",
            "sha256": sha256_bytes(b"missing"),
            "mode": None,
            "mtime_ns": None,
            "size": None,
        }

    common: dict[str, object] = {
        "path": rel,
        "mode": f"{stat.S_IMODE(metadata.st_mode):04o}",
        "mtime_ns": metadata.st_mtime_ns,
    }

    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(path)
        return {
            **common,
            "type": "symlink",
            "sha256": sha256_bytes(os.fsencode(target)),
            "size": len(os.fsencode(target)),
        }

    if stat.S_ISDIR(metadata.st_mode):
        return {
            **common,
            "type": "dir",
            "sha256": sha256_bytes(b"directory"),
            "size": None,
        }

    if stat.S_ISREG(metadata.st_mode):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return {
            **common,
            "type": "file",
            "sha256": digest.hexdigest(),
            "size": metadata.st_size,
        }

    special = (
        f"{stat.S_IFMT(metadata.st_mode)}:"
        f"{getattr(metadata, 'st_rdev', 0)}"
    ).encode("ascii")
    return {
        **common,
        "type": "other",
        "sha256": sha256_bytes(special),
        "size": metadata.st_size,
    }


def walk_without_following(root: Path) -> Iterator[dict[str, object]]:
    row = describe(root)
    yield row

    if row["type"] != "dir":
        return

    try:
        with os.scandir(root) as iterator:
            entries = sorted(list(iterator), key=lambda entry: os.fsencode(entry.name))
    except FileNotFoundError:
        return

    for entry in entries:
        yield from walk_without_following(Path(entry.path))


def workbench_roots() -> list[Path]:
    initiatives = repo / "spec-dock" / "initiatives"
    roots: set[Path] = {repo / "spec-dock" / ".workbench"}

    if initiatives.is_dir():
        for current, directory_names, file_names in os.walk(
            initiatives,
            topdown=True,
            followlinks=False,
        ):
            directory_names.sort(key=os.fsencode)
            file_names.sort(key=os.fsencode)
            current_path = Path(current)

            # Every canonical node gets an explicit present/missing record.
            if ".meta.json" in file_names:
                roots.add(current_path / ".workbench")

            # Capture orphan or noncanonical Workbench entries too.
            if ".workbench" in directory_names:
                roots.add(current_path / ".workbench")
                directory_names.remove(".workbench")
            if ".workbench" in file_names:
                roots.add(current_path / ".workbench")

    return sorted(roots, key=lambda path: os.fsencode(relative(path)))


if snapshot_kind == "initiatives":
    rows = list(walk_without_following(repo / "spec-dock" / "initiatives"))
elif snapshot_kind == "workbench":
    rows = []
    for root in workbench_roots():
        rows.extend(walk_without_following(root))
else:
    raise SystemExit(f"unknown snapshot kind: {snapshot_kind}")

rows.sort(key=lambda row: os.fsencode(str(row["path"])))

with output_path.open("w", encoding="utf-8", newline="\n") as stream:
    for row in rows:
        stream.write(
            json.dumps(
                row,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )
PY
```

Create the mandatory pre-update manifests:

```bash
uv run python "$SNAPDIR/snapshot.py" \
  initiatives "$SNAPDIR/initiatives.before.jsonl"

uv run python "$SNAPDIR/snapshot.py" \
  workbench "$SNAPDIR/workbench.before.jsonl"

sha256sum \
  "$SNAPDIR/initiatives.before.jsonl" \
  "$SNAPDIR/workbench.before.jsonl" \
  > "$SNAPDIR/snapshots.before.sha256"
```

The raw manifests must remain outside the repository. They may contain locally sensitive filenames even though they do not contain file contents. Put only counts, manifest digests, and equality results into EVD-012 unless every recorded path is safe to publish.

A manifest is evidence, not a backup. Where recovery of ignored payload is required, create a local-only protected-state archive before update, subject to local data-handling policy:

```bash
recovery_items=(spec-dock/initiatives)

if [ -e spec-dock/.workbench ] || [ -L spec-dock/.workbench ]; then
  recovery_items+=(spec-dock/.workbench)
fi

tar -cf "$SNAPDIR/protected-state.before.tar" -- "${recovery_items[@]}"
```

Do not commit or externally transmit that archive.

---

# Expected managed-mirror allowlist

The exact primary-path changed set is:

| Expected status | Checked-in mirror path                                             | Authoritative provider path                                                             |
| --------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| modified        | `spec-dock/.gitignore`                                             | `src/spec_dock/assets/spec_dock/.gitignore`                                             |
| modified        | `spec-dock/docs/README.md`                                         | `src/spec_dock/assets/spec_dock/docs/README.md`                                         |
| modified        | `spec-dock/docs/guide.md`                                          | `src/spec_dock/assets/spec_dock/docs/guide.md`                                          |
| modified        | `spec-dock/docs/reference_worktree.md`                             | `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`                             |
| modified        | `spec-dock/templates/README.md`                                    | `src/spec_dock/assets/spec_dock/templates/README.md`                                    |
| added           | `spec-dock/templates/root/.workbench/README.md`                    | `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`                    |
| added           | `spec-dock/templates/initiative/.workbench/README.md`              | `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`              |
| added           | `spec-dock/templates/epic/.workbench/README.md`                    | `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`                    |
| added           | `spec-dock/templates/issue/.workbench/README.md`                   | `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`                   |
| modified        | `spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` |

Create the machine-readable expected set:

```bash
cat > "$SNAPDIR/changed.expected.unsorted" <<'EOF'
spec-dock/.gitignore
spec-dock/docs/README.md
spec-dock/docs/guide.md
spec-dock/docs/reference_worktree.md
spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py
spec-dock/templates/README.md
spec-dock/templates/epic/.workbench/README.md
spec-dock/templates/initiative/.workbench/README.md
spec-dock/templates/issue/.workbench/README.md
spec-dock/templates/root/.workbench/README.md
EOF

LC_ALL=C sort \
  "$SNAPDIR/changed.expected.unsorted" \
  > "$SNAPDIR/changed.expected"
```

The following are forbidden in the primary projection delta:

```text
spec-dock/initiatives/**
spec-dock/.workbench/**
any node .workbench/** under initiatives
src/spec_dock/**
pyproject.toml
setup.py
tests/**
.agents/**
.codex/**
.github/**
spec-dock/active/**
spec-dock/system/**
spec-dock/spec-dock.version
the Issue report or other evidence files
```

`report.md` is edited later by the orchestrator, after the dev-coder has produced and compared the final protected snapshots. It must not be mixed into the update-effect delta.

---

# Exact execution sequence

## 1. Define changed-path collection

This collects tracked modifications, staged modifications, and newly unignored/untracked files:

```bash
collect_changed_paths() {
  {
    git diff --name-only --no-renames
    git diff --cached --name-only --no-renames
    git ls-files --others --exclude-standard
  } |
    sed '/^$/d' |
    LC_ALL=C sort -u
}
```

## 2. Execute the one formal update attempt

Write the attempt marker **before** invoking update. A nonzero command still consumes the one permitted attempt.

```bash
test ! -e "$SNAPDIR/update.attempted"

{
  printf 'command=uv run spec-dock update .\n'
  printf 'head=%s\n' "$(git rev-parse HEAD)"
  printf 'branch=%s\n' "$(git branch --show-current)"
  printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$SNAPDIR/update.attempted"

set +e
uv run spec-dock update . \
  > "$SNAPDIR/update.stdout" \
  2> "$SNAPDIR/update.stderr"
UPDATE_RC=$?
set -e

printf '%s\n' "$UPDATE_RC" > "$SNAPDIR/update.exit-code"
cat "$SNAPDIR/update.stdout"
cat "$SNAPDIR/update.stderr" >&2
```

Do **not** rerun the command regardless of its exit code.

## 3. Capture immediate post-update evidence

Capture snapshots even if update returned nonzero, because a failed update may have partially mutated the workspace:

```bash
uv run python "$SNAPDIR/snapshot.py" \
  initiatives "$SNAPDIR/initiatives.after-update.jsonl"

uv run python "$SNAPDIR/snapshot.py" \
  workbench "$SNAPDIR/workbench.after-update.jsonl"

collect_changed_paths > "$SNAPDIR/changed.after-update"

git status --short --untracked-files=all \
  > "$SNAPDIR/status.after-update"

git diff --summary \
  > "$SNAPDIR/diff-summary.after-update"

git diff --check \
  > "$SNAPDIR/diff-check.after-update"
```

Then apply the gates in this order:

```bash
test "$UPDATE_RC" -eq 0

cmp -s \
  "$SNAPDIR/initiatives.before.jsonl" \
  "$SNAPDIR/initiatives.after-update.jsonl"

cmp -s \
  "$SNAPDIR/workbench.before.jsonl" \
  "$SNAPDIR/workbench.after-update.jsonl"

diff -u \
  "$SNAPDIR/changed.expected" \
  "$SNAPDIR/changed.after-update"
```

On manifest mismatch, create a local diagnostic diff but do not copy it into the repository:

```bash
diff -u \
  "$SNAPDIR/initiatives.before.jsonl" \
  "$SNAPDIR/initiatives.after-update.jsonl" \
  > "$SNAPDIR/initiatives.after-update.diff" || true

diff -u \
  "$SNAPDIR/workbench.before.jsonl" \
  "$SNAPDIR/workbench.after-update.jsonl" \
  > "$SNAPDIR/workbench.after-update.diff" || true
```

Any mismatch is a stop condition. Do not repair or normalize protected state.

## 4. Verify all ten provider/mirror pairs directly

The existing docs parity map does not list `spec-dock/docs/README.md`, so a direct ten-pair byte check is required even when the existing pytest nodes pass.

```bash
uv run python - <<'PY' > "$SNAPDIR/direct-parity.json"
from pathlib import Path
import hashlib
import json

pairs = (
    (
        "spec-dock/.gitignore",
        "src/spec_dock/assets/spec_dock/.gitignore",
    ),
    (
        "spec-dock/docs/README.md",
        "src/spec_dock/assets/spec_dock/docs/README.md",
    ),
    (
        "spec-dock/docs/guide.md",
        "src/spec_dock/assets/spec_dock/docs/guide.md",
    ),
    (
        "spec-dock/docs/reference_worktree.md",
        "src/spec_dock/assets/spec_dock/docs/reference_worktree.md",
    ),
    (
        "spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py",
        "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py",
    ),
    (
        "spec-dock/templates/README.md",
        "src/spec_dock/assets/spec_dock/templates/README.md",
    ),
    (
        "spec-dock/templates/epic/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md",
    ),
    (
        "spec-dock/templates/initiative/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md",
    ),
    (
        "spec-dock/templates/issue/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md",
    ),
    (
        "spec-dock/templates/root/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md",
    ),
)

results = []

for mirror_rel, provider_rel in pairs:
    mirror = Path(mirror_rel)
    provider = Path(provider_rel)

    assert mirror.is_file(), f"missing mirror: {mirror_rel}"
    assert provider.is_file(), f"missing provider: {provider_rel}"

    mirror_bytes = mirror.read_bytes()
    provider_bytes = provider.read_bytes()

    assert mirror_bytes == provider_bytes, (
        f"provider/mirror byte divergence: {mirror_rel} != {provider_rel}"
    )

    results.append(
        {
            "mirror": mirror_rel,
            "provider": provider_rel,
            "sha256": hashlib.sha256(mirror_bytes).hexdigest(),
            "bytes": len(mirror_bytes),
        }
    )

print(json.dumps(results, ensure_ascii=True, sort_keys=True, indent=2))
PY

cat "$SNAPDIR/direct-parity.json"
```

## 5. Run focused existing pytest nodes

Required-fast mirror nodes:

```bash
uv run pytest \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets
```

Focused heavy nodes:

```bash
uv run pytest --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_preserves_opaque_workbenches_while_refreshing_managed_assets
```

This is an exact-node invocation. It is not the bare opt-in full-regression suite owned by Issue #346.

## 6. Run the required quality gates

```bash
make lint
uv run pytest
```

`make lint` delegates to the repository static-analysis runner.

The default pytest command must be invoked without `--run-full-regression`.

## 7. Capture final non-mutation evidence

Before editing any Issue report or Artifact:

```bash
uv run python "$SNAPDIR/snapshot.py" \
  initiatives "$SNAPDIR/initiatives.final.jsonl"

uv run python "$SNAPDIR/snapshot.py" \
  workbench "$SNAPDIR/workbench.final.jsonl"

collect_changed_paths > "$SNAPDIR/changed.final"

cmp -s \
  "$SNAPDIR/initiatives.before.jsonl" \
  "$SNAPDIR/initiatives.final.jsonl"

cmp -s \
  "$SNAPDIR/workbench.before.jsonl" \
  "$SNAPDIR/workbench.final.jsonl"

diff -u \
  "$SNAPDIR/changed.expected" \
  "$SNAPDIR/changed.final"

git diff --quiet -- \
  src/spec_dock \
  pyproject.toml \
  setup.py

git diff --check

git status --short --untracked-files=all \
  > "$SNAPDIR/status.final"

sha256sum \
  "$SNAPDIR/initiatives.before.jsonl" \
  "$SNAPDIR/initiatives.after-update.jsonl" \
  "$SNAPDIR/initiatives.final.jsonl" \
  "$SNAPDIR/workbench.before.jsonl" \
  "$SNAPDIR/workbench.after-update.jsonl" \
  "$SNAPDIR/workbench.final.jsonl" \
  "$SNAPDIR/update.stdout" \
  "$SNAPDIR/update.stderr" \
  "$SNAPDIR/direct-parity.json" \
  > "$SNAPDIR/evidence.sha256"
```

Only after all these checks pass may the orchestrator integrate the EVD-012 summary into `report.md`.

---

# Concrete test cases

| ID              | Operation                                                                                     | Required result                                                                   | Failure detected                                                              |
| --------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `S95-PRE-001`   | Verify branch, HEAD, remote HEAD, clean status, S90 admission, and local `uv run` import path | All identities exactly match the requested source                                 | Wrong branch/commit, stale package, dirty workspace                           |
| `S95-PRE-002`   | Inspect existing direct root/node Workbench READMEs                                           | No untracked direct README that would newly surface after `.gitignore` projection | Accidental Workbench staging candidate                                        |
| `S95-SNAP-001`  | Snapshot complete `spec-dock/initiatives/**` before and immediately after update              | Manifests byte-identical                                                          | Initiative content, path, type, mode, or mtime mutation                       |
| `S95-SNAP-002`  | Snapshot root and every node `.workbench`, including ignored payload and missing markers      | Manifests byte-identical                                                          | Backfill, deletion, overwrite, rename, mtime change, ignored payload omission |
| `S95-PROJ-001`  | Execute one formal update                                                                     | Exit code zero; no second attempt                                                 | Installer/update failure or repeated projection                               |
| `S95-PROJ-002`  | Compare changed-path set                                                                      | Exactly ten allowlisted paths                                                     | Broad update noise, missing mirror delta, initiative/Workbench change         |
| `S95-PAR-001`   | Direct ten-pair byte comparison                                                               | All ten mirror bytes equal provider bytes                                         | Omitted docs README coverage or incomplete update                             |
| `S95-PAR-002`   | Existing docs/template parity nodes                                                           | Two nodes pass                                                                    | Docs map or complete template inventory drift                                 |
| `S95-PAR-003`   | Existing runtime parity exact node                                                            | Pass with equal full inventory and bytes                                          | Runtime mirror still stale or has extra/missing files                         |
| `S95-NB-001`    | Existing update no-backfill exact nodes                                                       | Both pass                                                                         | Root README backfill, user README overwrite, opaque payload mutation          |
| `S95-QUAL-001`  | `make lint`                                                                                   | Exit code zero                                                                    | Static/type/format defect                                                     |
| `S95-QUAL-002`  | Default `uv run pytest`                                                                       | Exit code zero, no failures                                                       | Default PR-lane regression                                                    |
| `S95-FINAL-001` | Re-run protected manifests and exact allowlist after all gates                                | Same protected manifests and same ten paths                                       | A test or lint command mutated protected state or produced noise              |

The S95 plan makes the snapshot, exact managed allowlist, mirror parity, lint, and default suite the EVD-012 closure evidence.

---

# Failure classification and stop conditions

## 1. S95-owned projection defect

Classify as S95-owned when the defect is directly attributable to projection of the ten Issue #344 provider-managed paths, for example:

* The formal update exits nonzero because one of the reviewed provider assets cannot be installed.
* An expected mirror path is missing after update.
* An expected mirror differs from its provider bytes.
* The template or runtime mirror has an inventory difference caused by the Issue #344 provider changes.
* The two known default-lane parity failures remain after projection.
* A focused parity/no-backfill assertion is stale solely because the new mirror path was not included in its existing exact mapping.

Record:

```text
failing command
exit code
first relevant traceback/assertion
provider path
mirror path
pre/post hashes
changed-path set
protected-snapshot result
```

Do not rerun update.

## 2. Unrelated/default-lane failure requiring stop

Stop rather than repair when:

* `make lint` or default pytest fails outside the projection/parity boundary.
* Fixing the failure requires a path outside the ten mirrors or an explicitly dispositioned Issue #344 test.
* Update changes `.agents/**`, `.codex/**`, `.github/**`, unrelated docs/templates/runtime files, active pointers, system placeholders, version files, or other managed drift.
* A local permission, managed-skill collision, stale symlink, or environment problem prevents update but is not caused by the ten Issue #344 assets.
* A provider, installer, package, runtime, or canonical specification change appears necessary.
* The branch or remote HEAD no longer equals the exact source commit.

Return the failure evidence to the orchestrator. Do not “make the lane green” by broad cleanup.

## 3. Issue #346 handoff

The following remain Issue #346 work and are not run or repaired by S95:

* Bare `uv run pytest --run-full-regression`.
* Candidate-wheel consumer E2E.
* Generic `artifact import file` integration.
* Integrated dogfood across Issue #345 behavior.
* Epic-wide QA/review.
* Residual Epic integration delivery.

A failure found only in one of those surfaces may be recorded as an Issue #346 handoff **only after all S95 gates pass**. An S95 parity, snapshot, lint, or default-lane failure must not be deferred to Issue #346. The approved plan explicitly prohibits that deferral.

## Immediate stop conditions

Stop immediately on any of the following:

* Initiative manifest mismatch.
* Workbench manifest mismatch.
* Existing root/node Workbench README appears as a newly visible untracked path.
* Actual changed-path set differs from the exact expected set.
* Any attempt to run update a second time without rollback, fresh snapshots, and an explicit disposition.
* Any proposal to edit provider source to match a stale mirror.
* Any proposal to delete or move ignored Workbench payload.
* Any need for generic import, candidate wheel, integrated dogfood, or Epic-wide work.
* Any security/privacy concern while inventorying local Workbench paths.
* Any attempt to treat `git status` silence as proof that ignored Workbench payload is absent.

The accepted plan requires a return to planning if S95 projection touches initiatives or existing Workbench state.

---

# Minimal-fix boundary

## Preferred result: no fix

If the one update produces the exact ten-path delta and all gates pass, make no implementation or test edit. The projection itself is the implementation.

## Permissible bounded repair after disposition

If the formal update has already run and is insufficient, the smallest permissible repair is:

1. Protected snapshots must still be identical.
2. The defect must be confined to an exact provider/mirror pair in the ten-path allowlist.
3. The orchestrator must classify and record the update insufficiency before editing.
4. Copy provider bytes **outward** to the corresponding checked-in mirror path.
5. Do not semantically rewrite the copied content.
6. Do not rerun update.
7. Repeat direct parity, focused tests, lint, default pytest, path inspection, and final snapshots.

This is a fallback mechanical projection, not the primary implementation route. More than a bounded pair-level omission, or evidence of a systemic updater defect, requires a stop rather than a series of manual mirror normalizations.

## Conditional test-only repair

The observed `_DOGFOODING_MIRROR_PROVIDER_ASSET_MAP` includes `.gitignore`, `templates/README.md`, `docs/guide.md`, and `docs/reference_worktree.md`, but not `spec-dock/docs/README.md`.

The mandatory direct ten-pair check above closes S95 evidence without changing the repository. Where the orchestrator requires durable pytest ownership for that pair, the smallest test-only repair is one mapping entry in the existing dictionary:

```text
spec-dock/docs/README.md
    -> src/spec_dock/assets/spec_dock/docs/README.md
```

Do not create a new test node or generalized parity framework.

Because that repair changes `tests/unit/infra/test_init_update.py`, it changes the final allowlist from ten to eleven paths. It therefore requires an explicit S95 disposition and regenerated expected-path file before editing. It must not be smuggled into the projection as unclassified noise.

## Not permissible

The following are outside the minimal-fix boundary:

* Editing `src/spec_dock/cli.py`.
* Editing reviewed provider docs/assets to reproduce stale mirror content.
* Adding another updater mechanism.
* Running update again as an idempotence check.
* Broadly copying whole trees after the formal update.
* Editing existing initiative or Workbench state.
* Adding migrations, backfill, hooks, watches, sync, or copy-back.
* Expanding tests into Issue #346’s bare full-regression or consumer lane.

---

# EVD-012 handoff template

```markdown
### EVD-012 — S95 provider-first projection / default lane

#### Source identity

- Repository: `chemitaro/spec-dock`
- Branch: `iss-00344-workbench-shell-scaffolding`
- Pre-update HEAD: `2b4601f6e74053f3513f5fe66334c9999bf71c8b`
- Remote branch HEAD: `<sha>`
- Local/remote exact match: `<pass/fail>`
- Pre-update worktree clean: `<pass/fail>`
- `spec_dock.cli.__file__`: `<absolute path>`
- Tool version: `<version>`

#### One-update execution

- Command: `uv run spec-dock update .`
- Invocation count: `1`
- Attempt marker SHA-256: `<hash>`
- Exit code: `<code>`
- stdout SHA-256: `<hash>`
- stderr SHA-256: `<hash>`
- Second invocation performed: `no`

#### Protected-state snapshots

- Snapshot format: `S95 JSONL path/type/hash/mode/mtime_ns v1`
- Raw snapshot location: `<local external path; not committed>`
- Initiatives rows before / after-update / final: `<n> / <n> / <n>`
- Initiatives manifest SHA-256 before: `<hash>`
- Initiatives manifest SHA-256 after-update: `<hash>`
- Initiatives manifest SHA-256 final: `<hash>`
- Initiatives before=after-update: `<pass/fail>`
- Initiatives before=final: `<pass/fail>`
- Workbench roots observed: `<count>`
- Workbench rows before / after-update / final: `<n> / <n> / <n>`
- Workbench manifest SHA-256 before: `<hash>`
- Workbench manifest SHA-256 after-update: `<hash>`
- Workbench manifest SHA-256 final: `<hash>`
- Workbench before=after-update: `<pass/fail>`
- Workbench before=final: `<pass/fail>`
- Ignored payload included by direct filesystem traversal: `yes`
- Existing untracked direct README visibility preflight: `<pass/fail>`
- Protected-state recovery archive: `<created/not created; local only>`

#### Managed changed-path allowlist

- Expected path count: `10`
- Actual path count after update: `<n>`
- Actual path count final: `<n>`
- Expected=actual after update: `<pass/fail>`
- Expected=actual final: `<pass/fail>`
- Added mirror files: `<list>`
- Modified mirror files: `<list>`
- Deleted/renamed files: `<none or list>`
- Initiative/Workbench paths in Git delta: `<none or list>`
- Provider source paths in Git delta: `<none or list>`
- Allowlist-external paths: `<none or list>`

#### Provider/mirror parity

- Direct ten-pair byte check: `<pass/fail>`
- Direct parity record SHA-256: `<hash>`
- Docs parity node: `<command and result>`
- Template full-inventory parity node: `<command and result>`
- Runtime full-inventory parity exact node: `<command and result>`
- `spec-dock/docs/README.md` direct-pair result: `<pass/fail>`

#### No-backfill focused tests

- Update/force-init README no-backfill node: `<result>`
- Opaque root/node Workbench preservation node: `<result>`

#### Quality gates

- `make lint`: `<pass/fail; concise output>`
- Default `uv run pytest`: `<pass/fail; passed/skipped/failed counts>`
- Bare opt-in full-regression run: `no`
- `git diff --check`: `<pass/fail>`
- Final status boundary: `<exact ten paths / mismatch>`

#### Failure classification

- Classification: `<none / S95-owned projection defect / unrelated stop / Issue #346 handoff>`
- Evidence: `<command, assertion, paths, hashes>`
- Disposition: `<no fix / bounded provider-to-mirror repair / test-only repair / stopped>`
- Update rerun required or performed: `no`
- Issue #346 handoff, if any: `<scope and nonblocking rationale>`

#### Changed files proposed for implementation commit

- `<exact list>`

#### Unresolved risks

- `<none or exact residual risk>`

#### Decision ledger declaration

`No material implementation decisions beyond the approved plan.`

or:

- Decision entry required: `<ID, reason, proposed disposition>`

#### Dev-coder result

- Result: `<pass / blocked>`
- Recommended next action: `<create S95 review candidate / return for disposition>`
```

The plan defines EVD-012 as before/after snapshots, managed diff allowlist, mirror parity, lint, and default-suite evidence.

---

# Risks and uncertainties

## Verified repository facts

* The requested branch and exact commit were accessible through the GitHub connector.
* S90 is approved and S95 is admitted.
* The committed provider/mirror comparison identifies the ten paths above.
* The existing parity and no-backfill node names are present at the exact commit.
* The default policy makes docs/templates parity fast while runtime parity remains a focused heavy node.

## Local-state uncertainty

GitHub cannot expose ignored, uncommitted Workbench payload from the dev-coder’s local worktree. The local pre-snapshot is therefore the only authoritative source for:

* Existing ignored files.
* Empty Workbench directories.
* Symlinks or special entries.
* User-created direct READMEs.
* Local mtimes and modes.

No statement in this packet should be interpreted as claiming that ignored payload is absent.

## Direct README visibility risk

A pre-existing ignored direct `.workbench/README.md` can become unignored solely because the projected `.gitignore` changes. That is not byte mutation, but it prevents the final working tree from having only the intended managed delta. The packet therefore stops before update when such a local file is detected.

## Existing pytest coverage gap

The existing docs parity dictionary does not include `spec-dock/docs/README.md`. The direct ten-pair comparison is mandatory. A one-entry test-map repair is optional only after explicit disposition; it is not silently part of the ten-path primary projection.

## Snapshot versus recovery

The JSONL manifests prove equality but cannot reconstruct bytes. A protected-state archive or equivalent local backup is needed for automatic recovery of ignored data. Without one, any protected-state mismatch requires a stop and human-led recovery.

## Update breadth

The update command also refreshes managed skills and host shims. No Issue #344 install-root provider change was observed, so no `.agents`, `.codex`, or `.github` diff is expected. Any such delta is broad update noise requiring disposition.

## Validate/sync boundary

The canonical acceptance criteria mention validate/sync as part of the complete Issue-local delivery, while the approved S95/EVD-012 step contract and the attached brief specifically enumerate projection, snapshots, parity, lint, and default pytest. This dev-coder delegation should not silently add a GitHub-reading or derived-state-mutating sync operation. The orchestrator should map validate/sync to its accepted S95/S99 gate explicitly rather than expanding this worker packet without disposition. The S95 contract itself lists the exact snapshot/allowlist/parity/lint/default obligations.

---

# Dev-coder delegation packet

## Role and objective

**Role:** `dev-coder`
**Step:** S95 only
**Objective:** Project the reviewed Issue #344 provider-managed changes into the checked-in dogfood mirror through exactly one formal update, proving no mutation of initiatives or existing Workbench state and restoring the default PR lane to green.

## Locked source

```text
Repository: chemitaro/spec-dock
Branch: iss-00344-workbench-shell-scaffolding
Exact source: 2b4601f6e74053f3513f5fe66334c9999bf71c8b
```

Do not start if local HEAD or remote branch HEAD differs.

## Required operations

```text
1. Verify exact source, clean state, S90 approval, and local uv resolution.
2. Detect pre-existing untracked direct Workbench README visibility conflicts.
3. Create external initiatives and Workbench manifests.
4. Execute exactly one `uv run spec-dock update .`.
5. Capture immediate changed paths and post-update protected manifests.
6. Require exact ten-path projection and protected-state equality.
7. Run direct ten-pair byte parity.
8. Run existing docs/templates/runtime parity nodes.
9. Run existing focused no-backfill update nodes.
10. Run `make lint`.
11. Run default `uv run pytest`.
12. Recreate final protected manifests and exact changed-path list.
13. Return the EVD-012 worker summary without editing `report.md`.
```

## Primary allowed changes

Only these ten mirror paths:

```text
spec-dock/.gitignore
spec-dock/docs/README.md
spec-dock/docs/guide.md
spec-dock/docs/reference_worktree.md
spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py
spec-dock/templates/README.md
spec-dock/templates/epic/.workbench/README.md
spec-dock/templates/initiative/.workbench/README.md
spec-dock/templates/issue/.workbench/README.md
spec-dock/templates/root/.workbench/README.md
```

A test-only change requires prior explicit disposition and a revised allowlist.

## Forbidden actions

```text
Do not run update twice.
Do not edit provider source to match the mirror.
Do not edit canonical specifications.
Do not edit the Issue report during the protected comparison window.
Do not mutate, move, delete, stage, or normalize existing Workbench state.
Do not use `git clean -fdx`, `git reset --hard`, or another broad rollback.
Do not implement generic import.
Do not run the bare full-regression suite.
Do not perform candidate-wheel consumer E2E.
Do not expand into Issue #346 or S99.
Do not claim that ignored payload is absent because Git does not report it.
```

## Rollback and recovery

For an expected mirror-only rollback after a classified failure:

```bash
git restore --source=HEAD --staged --worktree -- \
  spec-dock/.gitignore \
  spec-dock/docs/README.md \
  spec-dock/docs/guide.md \
  spec-dock/docs/reference_worktree.md \
  spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  spec-dock/templates/README.md

rm -f -- \
  spec-dock/templates/root/.workbench/README.md \
  spec-dock/templates/initiative/.workbench/README.md \
  spec-dock/templates/epic/.workbench/README.md \
  spec-dock/templates/issue/.workbench/README.md

rmdir --ignore-fail-on-non-empty \
  spec-dock/templates/root/.workbench \
  spec-dock/templates/initiative/.workbench \
  spec-dock/templates/epic/.workbench \
  spec-dock/templates/issue/.workbench
```

Do not apply this rollback to allowlist-external or protected paths. Record those paths and stop.

A new update attempt is permitted only after:

```text
the prior projection is fully rolled back;
protected state equals the original pre-snapshot;
a new external snapshot directory is created;
the prior failure has an explicit disposition;
the exact branch/HEAD/clean preconditions are repeated.
```

## Required return

Return:

```text
pass/blocked result
source identity
snapshot counts and manifest hashes
one-update exit code and log hashes
expected and actual changed paths
direct parity results
focused pytest results
lint/default pytest results
final protected-state equality
failure classification
any bounded fix and its disposition
unresolved risks
completed EVD-012 template
No material implementation decisions declaration, or a proposed ledger entry
```

The dev-coder does not declare S95 approved, create the final evidence commit, or admit S99. Those remain orchestrator and reviewer-gate responsibilities.
