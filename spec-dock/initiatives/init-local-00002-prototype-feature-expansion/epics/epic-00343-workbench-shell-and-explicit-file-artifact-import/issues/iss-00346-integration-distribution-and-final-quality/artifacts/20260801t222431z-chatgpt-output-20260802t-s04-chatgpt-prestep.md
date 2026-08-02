# S04 Implementation Elaboration

## Verified repository binding

GitHub connector inspection succeeded for `chemitaro/spec-dock`. The feature branch `iss-00346-integration-distribution-and-final-quality` exists and resolves to:

```text
c3da337ad10f51b75943f4856484467bb53f1272
```

The default-branch fallback was not used. The attached canonical plan, report, `test_artifact_import_s04.py`, and `test_epic_00343_distribution.py` have Git blob identities matching the files at that exact commit.

The attached S04 brief, plan, report, and tests are therefore suitable as the implementation contract for this elaboration.     

## Conclusion and smallest likely change set

**Provisional production conclusion: no-op.** Current code inspection already shows the intended filter-before-read structure:

* Artifact validation and shared-slot allocation classify direct entries by filename and regular-file status without opening artifact bodies.
* Generic imported filenames are recognized before malformed-Markdown checks.
* ADR mirror collection derives typed ADR identity from the filename before calling the frontmatter reader.
* Delegated-authoring checks reject or ignore non-typed filenames before reading a candidate draft body.
* Context-pack generation operates from the active manifest and fixed canonical documents, not from arbitrary artifact bodies.

The smallest defensible implementation batch is therefore:

| Path                                                                            | Intended action                                                                                                   |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `tests/cli_runtime/test_artifact_import_s04.py`                                 | Complete and harden `tc-346-s04-001` and `002`; preserve or alias existing compatibility/slot tests for `003`.    |
| `tests/integration/test_epic_00343_distribution.py`                             | Add the disposable exact-revision dogfood helper and `tc-346-s04-004`/`005`.                                      |
| Existing ChatGPT-output, Workbench, generic-import, and new-artifact test files | Run unchanged. Change only if an objectively missing characterization is discovered before any production repair. |
| Production files                                                                | No change unless a new S04 test reproduces a contract defect on the exact candidate wheel/runtime.                |
| `report.md`                                                                     | Orchestrator-only evidence transcription after the executable work is committed, pushed, and verified.            |

The current CLI-runtime test already combines some body-open and projection checks, but it writes the same invalid-UTF-8/NUL payload directly into four artifact directories rather than importing the required distinct fixture classes. It also does not explicitly exercise the delegated-authoring filter. The current integration test ends after S03 and contains no disposable dogfood S04 cards.

Do not treat the current combined test name’s `_003` suffix as closing the full legacy compatibility bundle. Either rename it to reflect `001/002`, or record an explicit test-ID alias in the report.

---

## `tc-346-s04-001` — Opaque body-open denial matrix

### Suggested test node

```text
tests/cli_runtime/test_artifact_import_s04.py::
TestArtifactImportS04::
test_tc_346_s04_001_opaque_body_open_denial_matrix
```

### Fixture preparation

Use a temporary initialized consumer and the existing same-repository hierarchy helper. Set the projected runtime clock deterministically. Create the existing valid typed ADR baseline before introducing generic files.

Create five source fixtures with unique ASCII sentinels embedded in their bytes:

| Fixture       | Recommended basename      | Important property                                         | Suggested target |
| ------------- | ------------------------- | ---------------------------------------------------------- | ---------------- |
| Binary        | `opaque-binary.bin`       | Arbitrary non-text bytes                                   | root             |
| ZIP           | `opaque-archive.zip`      | Structurally valid ZIP produced with `zipfile`             | Initiative       |
| Invalid UTF-8 | `opaque-invalid.md`       | Invalid UTF-8 and `.md` extension                          | Epic             |
| NUL-bearing   | `opaque-nul.md`           | Valid surrounding text with embedded NUL                   | Issue            |
| ADR-looking   | `accepted-adr-looking.md` | Valid-looking accepted ADR frontmatter and `.md` extension | Issue            |

Import every fixture through the public projected command before installing the lifecycle spy:

```text
artifact import file --root ...
artifact import file --initiative ...
artifact import file --epic ...
artifact import file --issue ...
```

Use JSON mode and retain only the returned destination paths and public result fields. Assert at import time that:

* `import_kind=file`
* `storage_identity=generic`
* `canonical=false`
* no public `sha256`, `byte_count`, MIME, encoding, or content-derived field is emitted
* the source remains present

Do not populate the artifact directories by direct test writes; doing so would bypass the integration behavior this card is intended to characterize.

### Lifecycle operations under the guard

Run these against the same consumer:

1. `validate_tree(ValidateTreeRequest())`
2. `check_deps(CheckDepsRequest(..., use_github=False))`
3. `sync(SyncRequest(..., github_enabled=False))`
4. `load_active_manifest(...)`
5. `build_context_pack_text(...)`
6. Delegated-authoring diff-guard evaluation for one valid typed draft artifact

The authoring check can use the current domain `evaluate_diff_guard` with one valid typed Markdown draft as its declared diff entry. The guard may read that typed draft; it must not open any of the five generic destinations.

`sync` is the public exercise of ADR discovery and mirror handling. The ADR-looking generic fixture is specifically intended to prove that `--accepted-adr-looking.md` is rejected by filename classification before frontmatter parsing.

### Required assertions

* Every operation succeeds under the existing name-only policy.
* Generic body-open attempts during the measured lifecycle window: exactly `0`.
* Decode errors: `0`.
* ADR-looking generic file is not included in the ADR source or mirror set.
* Root generic file creates no root graph node or root `.meta.json`.
* The five imported generic files remain classified as generic filenames, not typed or blank artifacts.

---

## Filter-before-read spy design

The spy must distinguish an intentional sensitivity check from the actual zero-open measurement.

### Two independent guard instances

1. Install a first guard and deliberately call an open operation on one generic destination. It must raise before the underlying file is opened.
2. Exit that context completely.
3. Install a fresh guard with an empty attempt ledger.
4. Run the lifecycle consumers.
5. Assert the fresh ledger is empty.

Do not reuse the first ledger and clear it. A fresh instance gives an unambiguous observed count of zero.

### APIs to intercept

At minimum intercept:

* `Path.open`
* direct `builtins.open`
* `io.open`

`Path.read_text` and `Path.read_bytes` route through `Path.open`, but they may also be wrapped explicitly if that makes the local helper clearer.

The guard should compare both the lexical absolute path and its symlink-resolved path against the generic destination set. This prevents a body read through a newly created mirror alias from escaping the spy.

The current inspected lifecycle readers use `Path.read_text` or filename/stat-only operations. Do not add a generalized filesystem interception framework or production hook. If the implementation starts using raw descriptor-based body reads, stop and reassess the test instrumentation rather than claiming zero coverage.

### Avoiding accidental harness reads

During the measured lifecycle window:

* Do not call `read_bytes`, `read_text`, hashing functions, ZIP inspection, or MIME/encoding probes on a generic destination.
* Do not compute a destination digest.
* Build the guarded path set from import result paths only.
* Projection snapshots may read generated projection files, because those are not generic bodies.
* ADR mirror snapshots must record entry name, entry type, and `readlink()` target only. Do not follow a regular file or symlink to read its body.
* Optional byte-equality checks may occur only after the zero-open measurement has been finalized and the guard removed.

The import itself necessarily reads the source file; that occurs before the lifecycle measurement and is not counted as a lifecycle body open.

---

## `tc-346-s04-002` — Projection and context equivalence

### Suggested test node

```text
tests/cli_runtime/test_artifact_import_s04.py::
TestArtifactImportS04::
test_tc_346_s04_002_projection_and_context_equivalence
```

### Baseline

Before importing the generic fixtures:

1. Set the active Issue.
2. Run `validate`.
3. Run `sync --no-github`.
4. Run JSON dependency check.
5. Capture every required projection path:

```text
.agent/index-all.json
.agent/index.json
.agent/tree-all.json
.agent/tree.json
.agent/deps-issues.json
tree-all.puml
tree.puml
deps-issues.puml
deps-raw.puml
dashboard.md
active/context-pack.md
```

Assert that the complete expected path set exists. Do not silently omit missing paths as the current helper does.

Capture:

* normalized projection values
* dependency-check JSON/text
* ADR mirror entry names and symlink targets
* typed/blank artifact filename set
* active context-pack text

### Allowed normalization

Normalize only an explicitly known generated timestamp field such as the top-level JSON `generated_at`. With the fixed runtime clock, Markdown, PUML, dashboard, and context-pack bytes should normally compare exactly.

Do not normalize:

* arbitrary ISO timestamps
* path values
* ordering
* IDs
* titles
* generated filenames
* missing outputs

If broader normalization is required for Green, stop and identify the actual nondeterministic field before changing the oracle.

### After generic imports

Run the same lifecycle sequence and assert:

* identical required path set
* normalized projection equality
* dependency output equality
* context-pack equality
* unchanged typed/blank discovery set
* unchanged ADR mirror set
* no generic filename in the ADR mirror
* no generic filename or known body sentinel in any generated projection
* no generic artifact promoted to typed, blank, canonical, or ADR status

A single helper may prepare the consumer for both `001` and `002`, but each test should receive a fresh temporary consumer. Avoid a mutable module-scoped fixture whose result depends on test order.

---

## `tc-346-s04-003` — Legacy compatibility bundle

This card should primarily reuse existing tests without changing their expectations. The current suites already characterize:

* ChatGPT-output byte preservation and its specific `sha256`/`byte_count`/source result contract
* typed and blank naming
* generic/typed shared timestamp slots
* concurrent import/new allocation
* no-overwrite and bounded retry behavior
* Workbench copy scope, result shape, opacity, and source-wins behavior
* generic import target, privacy, collision, and slot behavior.

The existing test that places a generic file in the unsuffixed slot and expects blank and typed creations to allocate `-01` and `-02` can be mapped to this card. The existing concurrent shared-lock tests must also remain part of the closure.

### Required run set

```bash
uv run pytest tests/cli_runtime/test_artifact_import_s04.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/cli_runtime/test_workbench.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py
```

Discover and record the current new-artifact nodes before closure:

```bash
uv run pytest --collect-only -q tests/cli_runtime/test_runtime_new_doc_s09.py \
  | rg 'artifact|blank|slot|collision'
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py -k 'artifact'
```

The report must record the exact collected nodes, not only the `-k` expression.

### Compatibility failure policy

* Add a characterization expectation before production repair only when the existing suite genuinely lacks the affected contract.
* Do not change an existing expected filename, output field, selector, digest/count rule, or source-wins rule merely to make the suite pass.
* A failure requiring a changed legacy public contract is an S04 stop condition.

---

## `tc-346-s04-004` — Exact dogfood no-backfill

### Suggested test node

```text
tests/integration/test_epic_00343_distribution.py::
test_tc_346_s04_004_disposable_exact_dogfood_update_keeps_epic_00343_unbackfilled
```

### Disposable checkout construction

Use the current `candidate_wheel` fixture and create a fully independent local clone rather than a linked worktree:

```text
git clone --no-hardlinks --no-checkout <provider-repo> <temporary-checkout>
git -C <temporary-checkout> checkout --detach <candidate-head>
git -C <temporary-checkout> remote set-url origin https://github.com/chemitaro/spec-dock.git
```

The remote rewrite provides the expected repository slug to runtime code without making a network request. Use the existing local `gh` stub environment.

Preflight assertions:

* candidate wheel pre/post HEAD are identical
* disposable checkout HEAD equals that exact candidate HEAD
* disposable checkout status is clean
* real provider worktree HEAD/status are captured
* `epic-00343` resolves from `.meta.json`
* `epic-00343/.workbench/README.md` is absent
* provider source tree snapshot is captured
* canonical `spec-dock/initiatives` snapshot is captured

Do not reuse the S03 wheel receipt as the S04 candidate receipt. The S04 implementation/test commit will move the branch head; build and use the wheel from the then-current clean pushed revision.

### Update operation

Run the candidate-wheel-installed top-level CLI:

```text
<installed-venv>/bin/spec-dock update <temporary-checkout>
```

Do not use the checkout’s repository wrapper as the update provider.

Post-update assertions:

* return code `0`
* checkout remains at the exact candidate commit
* existing Epic README remains absent
* canonical Initiative/Epic/Issue bytes are unchanged
* provider `src/spec_dock/assets/spec_dock` bytes are unchanged
* same-revision update leaves the working tree clean, or any non-empty managed delta is explicitly enumerated and limited to provider-managed projection files
* critical provider/projection pairs are byte-equal, including the projected runtime and all four Workbench README templates
* no consumer path was copied back into provider source

### No-backfill sensitivity negative

In the disposable checkout only:

1. Create the forbidden `epic-00343/.workbench/README.md`.
2. Run the no-backfill assertion helper.
3. Require a path-specific assertion failure.
4. Remove the injected file.
5. Reassert the clean post-update state.

This proves that the oracle detects one-path backfill rather than merely comparing aggregate counts.

### Cleanup

Always remove the disposable clone in `finally`. At test exit assert:

* disposable path no longer exists
* real provider HEAD is unchanged
* real provider status equals its pre-test value

---

## `tc-346-s04-005` — Future shell plus generic import in dogfood projection

### Suggested test node

```text
tests/integration/test_epic_00343_distribution.py::
test_tc_346_s04_005_disposable_dogfood_future_shell_and_generic_import
```

Start from a fresh disposable checkout that has passed the same exact-revision update preflight.

### Future node creation

Choose an unused GitHub issue number by scanning existing `.meta.json` records; do not hard-code an ID that could later collide.

Through the projected runtime, create one future Issue under existing Epic 343:

```text
<venv-python> <checkout>/spec-dock/scripts/spec-dock \
  new issue \
  --epic 343 \
  --title "S04 future dogfood" \
  --github-issue <unused-number>
```

Resolve the new Issue from its resulting metadata rather than depending on a guessed directory slug.

Assert:

* new Issue README exists
* README bytes equal the candidate wheel’s Issue Workbench template
* README is not ignored
* existing Epic 343 README remains absent

### Generic import

Create an ignored payload at:

```text
<future-issue>/.workbench/s04-opaque.bin
```

Preflight it with:

```text
git check-ignore --no-index <relative-source>
git ls-files -- <relative-source>
```

Require ignored=`true` and tracked=`false`.

Import through the projected runtime:

```text
artifact import file
  --issue <future-issue-id>
  --file <repo-relative-source>
  --json
```

Assert:

* `status=ok`
* `storage_identity=generic`
* `canonical=false`
* no public digest or byte count
* destination is under the future Issue’s `artifacts/`
* source bytes remain unchanged
* destination bytes equal source bytes
* no absolute checkout path appears in stdout or stderr

Then run through the projected runtime:

```text
validate
sync --no-github
```

Both must succeed.

### Final state assertions

* existing Epic 343 README remains absent
* future Issue README remains byte-identical to the provider template
* ignored Workbench source remains ignored and untracked
* imported generic artifact remains non-canonical
* provider source snapshot remains unchanged
* no consumer-to-provider write occurred

Capture a sorted, repository-relative status manifest. Permit only:

* the exact future Issue subtree
* known generated projection paths changed by node creation/sync

Reject any path under:

```text
src/spec_dock/assets/spec_dock
```

The Workbench source itself must not appear in the status manifest because it is ignored.

---

## Execution sequence

After implementing the test-only delta, commit and push it before collecting closure evidence. Reconfirm local and remote head equality, then execute:

```bash
git rev-parse HEAD
git status --short
git rev-parse origin/iss-00346-integration-distribution-and-final-quality
```

Focused opaque lifecycle:

```bash
uv run pytest \
  tests/cli_runtime/test_artifact_import_s04.py::TestArtifactImportS04::test_tc_346_s04_001_opaque_body_open_denial_matrix \
  tests/cli_runtime/test_artifact_import_s04.py::TestArtifactImportS04::test_tc_346_s04_002_projection_and_context_equivalence \
  -q
```

Dogfood cards:

```bash
uv run pytest \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s04_004_disposable_exact_dogfood_update_keeps_epic_00343_unbackfilled \
  tests/integration/test_epic_00343_distribution.py::test_tc_346_s04_005_disposable_dogfood_future_shell_and_generic_import \
  --run-full-regression -q
```

Compatibility bundle:

```bash
uv run pytest tests/cli_runtime/test_artifact_import_s04.py -q
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py -q
uv run pytest tests/cli_runtime/test_workbench.py -q
uv run pytest tests/cli_runtime/test_artifact_import_file.py -q
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py -k 'artifact' -q
uv run pytest tests/unit/application/test_import_file_artifact.py \
  tests/unit/presentation/test_artifact_import_file.py -q
```

Integrated regression:

```bash
uv run pytest tests/integration/test_epic_00343_distribution.py \
  --run-full-regression -q
uv run ruff check \
  tests/cli_runtime/test_artifact_import_s04.py \
  tests/integration/test_epic_00343_distribution.py
git diff --check
```

Repository closure checks:

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
git diff --check
git status --short
```

The real repository `sync --no-github` is the plan-required closure check, not the dogfood update. Capture pre/post status and reject any unexpected mutation.

---

## Repair boundary

Proceed with a production no-op when all new tests pass on the candidate wheel/runtime.

If a failure is observed, preserve:

* first failing consumer
* exact generic basename
* whether any body-open attempt occurred
* pre/post projection difference
* candidate head and wheel identity
* content-free error/result

Then identify the smallest allowed root cause.

A repair in one of the plan’s listed repair-only paths is permissible only when it directly closes the observed failure. Do not introduce a body classifier or generalized artifact reader.

Several currently relevant lifecycle implementations are **not** in the S04 repair-only list, including:

```text
application/sync_state.py
domain/validation.py
domain/delegated_authoring.py
application/delegated_authoring.py
```

If the required fix is in one of those paths and cannot be expressed as a correct, bounded change to an allowed shared classifier such as `domain/artifacts.py`, stop for an amendment. Do not silently expand the path list.

---

## Stop conditions

Stop S04 implementation or closure when any of the following occurs:

1. Local HEAD, remote HEAD, wheel source, or disposable checkout revision differ.
2. The real working tree is dirty in a way that prevents attribution.
3. Any lifecycle consumer attempts to open a generic body.
4. Projection equality requires normalization beyond a named generated timestamp field.
5. A required projection is missing and the test would pass only by silently omitting it.
6. A generic file must be interpreted as Markdown, ADR, MIME, encoding, or canonical content.
7. Existing Epic 343 receives a Workbench README.
8. Future-shell support requires backfill or a change to an unlisted installer/template/node-creation path.
9. Dogfood update changes provider source or requires consumer-first copying.
10. A compatibility failure requires changing an existing public output, filename, selector, slot, digest/count, or source-wins contract.
11. Production repair requires a path outside plan §11.3.
12. A production repair touches generic publication/platform behavior and thereby invalidates S03 host evidence; affected S03 lanes must be rerun before S04 can close.
13. The disposable checkout cannot be cleaned up or the real provider worktree changes during the test.

---

## Evidence to add to `report.md`

### Source Revision and S04 Candidate Receipt

Record:

* branch and exact pushed HEAD
* local/remote equality
* clean status
* candidate wheel basename and distribution digest
* installed origin classification
* exact disposable checkout revision
* production repair: `false`, or exact justified repair paths

### Opaque Lifecycle Matrix

One row per fixture and lifecycle consumer:

| Field                | Required value                                   |
| -------------------- | ------------------------------------------------ |
| Fixture class        | binary / ZIP / invalid UTF-8 / NUL / ADR-looking |
| Generic target       | root / Initiative / Epic / Issue                 |
| Import status        | pass                                             |
| Body-open attempts   | `0`                                              |
| Decode errors        | `0`                                              |
| Typed promotion      | false                                            |
| ADR mirror promotion | false                                            |

Do not record fixture bodies, host-local absolute paths, user-file digests, or byte counts.

### Projection and Context Equivalence

Record:

* complete projection path set
* normalization rule: named `generated_at` field only
* before/after semantic equality
* dependency output equality
* context-pack equality
* typed artifact set unchanged
* ADR mirror set unchanged
* generic projection entries: `0`

### Compatibility Regression Evidence

Record exact commands, collected node names, counts, and result for:

* ChatGPT-output
* typed/blank creation
* shared slot and concurrency
* Workbench copy/source-wins
* generic import
* nearest new-artifact suite

State whether any expectations were changed. Expected value is `none`.

### Fresh-Update-Dogfood Matrix / dogfood

Record:

* exact checkout head
* Epic 343 README before update: absent
* Epic 343 README after update: absent
* installed CLI update result
* post-update managed delta
* future Issue ID
* future README/provider equality
* generic import result and `canonical=false`
* validate result
* sync result
* disposable cleanup result
* real provider worktree unchanged

### Provider-to-Dogfood Projection Manifest

Record only content-free data:

* provider source unchanged: true
* critical provider/projection pair equality
* sorted repo-relative changed paths or path categories
* unexpected paths: none
* consumer-to-provider writes: zero

### Closure ledgers

Add one result row for each of `tc-346-s04-001` through `005`, with its closure IDs and exact pushed-head binding.

If the existing historical test names are retained, add explicit aliases in `Closure Delta`; do not rely on suggestive suffixes alone.

### Delegated Worker Evidence

Record:

* changed files
* production repair decision
* exact tests run
* disposable cleanup result
* unresolved risks
* `No material implementation decisions beyond the approved plan.` when applicable

After the S04 implementation/evidence commit is pushed, obtain the required exact-head ChatGPT Pro code review and record its thread/session identity, reviewed SHA, finding counts, and unresolved blocker count.

---

## Assumptions and uncertainty

* The production no-op conclusion is based on exact-head code and test inspection; tests were not executed in this consultation.
* The current runtime’s visible filter ordering strongly supports Green, but the new spy is the closure evidence.
* A same-revision dogfood update is expected to leave the disposable checkout clean. If it produces a managed delta, the delta must be explicitly classified rather than normalized away.
* The future GitHub issue number must be selected dynamically to avoid repository evolution causing a collision.
* The branch head will move when S04 tests and evidence are committed. All final wheel, checkout, test, and review receipts must bind that later pushed head rather than reusing `c3da337ad10f51b75943f4856484467bb53f1272`.
