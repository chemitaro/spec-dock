# S14 bounded repair packet

## Conclusion

GitHub connector inspection verified repository `chemitaro/spec-dock`, branch `iss-00334-implement-chatgpt-issue-planning-workflow`, and exact HEAD `bb65257155a73b621b0d0b6fb3426393c46de712`; branch comparison was identical, with no default-branch fallback. The attached verifier record reports exactly the three failures addressed below.  

| Failure                                            | Disposition                       | Required repair                                                                                                                      |
| -------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Checked-in `.meta.json` path/`depends_on` snapshot | **Stale frozen test data**        | Mechanically refresh three constants in `tests/unit/infra/test_init_update.py`                                                       |
| Runtime non-empty issue dependency map             | **Stale frozen test data**        | Add the current `iss-00346` dependency entry to the same test constant                                                               |
| Stable-completion final-snapshot timeout           | **Runtime implementation defect** | Preserve the unchanged `polls == 2` assertion; repair sub-second quiet-window budget arithmetic in provider and dogfood wait engines |

No canonical Requirement, Design, Plan, report schema, public status/reason schema, metadata file, dependency implementation, CLI wrapper, or polling policy should change.

---

## 1. Checked-in graph snapshot repair

### Decision

The checked-in graph is valid authoritative data, not a metadata or dependency defect.

Exact HEAD contains one additional managed Epic and three managed Issues under `init-local-00002`:

* `epic-00343`, correctly parented to `init-local-00002`.
* `iss-00344`, correctly parented to `epic-00343`, with no direct dependencies.
* `iss-00345`, correctly parented to `epic-00343`, with no direct dependencies.
* `iss-00346`, correctly parented to `epic-00343`, depending on the two existing Issues `iss-00344` and `iss-00345`.

The tests first validate that no legacy `deps.json` exists, read every checked-in `.meta.json`, and compare the resulting exact path and `depends_on` snapshots. The runtime test then successfully performs validation and synchronization before comparing its generated non-empty issue map. Therefore, the failures are snapshot drift after authoritative graph growth, not evidence that the new graph is malformed.

### Exact frozen-data additions

Add these four entries to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`, preserving lexicographic ordering:

```python
"spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
"epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/.meta.json",

"spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
"epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
"issues/iss-00344-workbench-shell-scaffolding/.meta.json",

"spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
"epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
"issues/iss-00345-generic-single-file-artifact-import/.meta.json",

"spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
"epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
"issues/iss-00346-integration-distribution-and-final-quality/.meta.json",
```

Add the corresponding entries to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`:

```python
{
    "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
    "epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/.meta.json": [],

    "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
    "epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
    "issues/iss-00344-workbench-shell-scaffolding/.meta.json": [],

    "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
    "epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
    "issues/iss-00345-generic-single-file-artifact-import/.meta.json": [],

    "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
    "epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
    "issues/iss-00346-integration-distribution-and-final-quality/.meta.json": [
        "iss-00344",
        "iss-00345",
    ],
}
```

Add one entry to `_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP`:

```python
"iss-00346": ["iss-00344", "iss-00345"],
```

Do **not** alter any checked-in `.meta.json`.

### Deterministic derivation command

Use the same path enumeration and defaulting rules as the tests. The printed values are the source for all three frozen constants:

```bash
uv run python - <<'PY'
from pathlib import Path
import json
import pprint

repo = Path.cwd().resolve()
initiatives_root = repo / "spec-dock" / "initiatives"

meta_paths = tuple(
    sorted(
        path.relative_to(repo).as_posix()
        for path in initiatives_root.rglob(".meta.json")
    )
)

depends_on_by_meta_path: dict[str, list[str]] = {}
non_empty_issue_depends_on_map: dict[str, list[str]] = {}

for relative_path in meta_paths:
    payload = json.loads((repo / relative_path).read_text(encoding="utf-8"))
    depends_on = payload.get("depends_on", [])

    assert isinstance(depends_on, list), relative_path
    assert all(isinstance(value, str) and value for value in depends_on), relative_path

    depends_on_by_meta_path[relative_path] = depends_on

    if payload.get("type") == "issue" and depends_on:
        issue_id = payload.get("id")
        assert isinstance(issue_id, str) and issue_id, relative_path
        assert issue_id not in non_empty_issue_depends_on_map, issue_id
        non_empty_issue_depends_on_map[issue_id] = depends_on

print("_CHECKED_IN_DOGFOODING_META_JSON_PATHS =")
pprint.pp(meta_paths, sort_dicts=False, width=120)

print("\n_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH =")
pprint.pp(depends_on_by_meta_path, sort_dicts=False, width=120)

print("\n_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP =")
pprint.pp(
    dict(sorted(non_empty_issue_depends_on_map.items())),
    sort_dicts=False,
    width=120,
)
PY
```

### Smallest allowlist and expected transition

**Write allowlist:**

```text
tests/unit/infra/test_init_update.py
```

**Red:**

```bash
uv run pytest -q \
  tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json \
  tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot
```

Expected before repair: both nodes fail only on frozen exact-state comparisons.

**Green:** the same two nodes pass, with their legacy-file prohibition, validation, synchronization, and exact graph assertions unchanged.

---

## 2. Final-snapshot timeout and stable-completion repair

### Decision

The assertion is correct; the implementation violates the accepted contract.

The test deliberately launches a fast first successful snapshot and a second successful snapshot that exceeds the remaining deadline. It requires the second poll to be counted, the already stable successful state to remain `passed/merge_prepared`, and no blocking `snapshot_poll_timeout` limitation to be introduced.

That behavior was explicitly introduced as a production safety repair: the accepted change says a final snapshot timeout must not regress a previously stable completion, and it added this exact test with `polls == 2`, together with synchronized provider and dogfood implementations.

At exact HEAD, the timeout branch already knows how to preserve the latest state when a launched snapshot times out and the prior state has actually satisfied terminal or stable-completion conditions.  The defect occurs earlier: the under-budget admission check converts elapsed quiet time to an integer before deciding whether the quiet window can mature by the deadline. Sub-second elapsed time is therefore discarded. Under normal process-startup variance, an actual elapsed value such as `0.6` becomes `0`; the engine may then conclude that a full additional second is required, skip the confirmation poll, and return `polls == 1`. This is the high-confidence explanation of the reproduced exact-state failure.

### Smallest safe implementation

Replace integer-based internal quiet-window eligibility with an absolute monotonic deadline.

Conceptually:

```python
quiet_deadline = latest_change_monotonic + quiet_seconds
quiet_can_be_evaluated = deadline >= quiet_deadline
```

At final snapshot timeout, use the same exact boundary:

```python
stable_at_timeout = (
    same_count >= same_fingerprint_count
    and time.monotonic() >= latest_change_monotonic + quiet_seconds
)
```

Keep the existing integer conversion only for serialized observational metadata such as `wait.quiet_seconds_observed`.

This repair has three safety properties:

1. It does not declare completion before the configured quiet window actually elapses.
2. It permits the one final confirmation poll whenever that quiet window can mature within the hard overall deadline.
3. If that poll times out, the existing preservation branch retains the latest stable state only after the actual quiet deadline and fingerprint-count requirement have both been satisfied.

Do not change:

* `timeout_seconds`, `poll_interval_seconds`, `quiet_seconds`, or `same_fingerprint_count`;
* the test’s `polls == 2` assertion;
* under-budget zero-check-grace consumption rules;
* status, reason, recommendation, limitation, resume, or wait JSON fields;
* shell wrapper arguments or validation;
* snapshot classification rules.

The provider and dogfood Python files currently have the same Git blob identity, so the repair must retain byte parity.

### Smallest allowlist and expected transition

**Write allowlist:**

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

**Read-only test oracle:**

```text
tests/unit/infra/test_init_update.py
```

No test change is required for this failure.

**Red:**

```bash
uv run pytest -q \
  tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state
```

Expected before repair: `polls` is `1` instead of `2`, as reported by the full-regression reproduction. 

**Green:** the same unchanged node returns:

```text
wait.polls == 2
normalized_status == "passed"
overall_status == "passed"
recommended_next_action == "merge_prepared"
observation_complete is true
no blocking fetch_pr_observation_snapshot.sh/snapshot_poll_timeout limitation
```

Then verify exact projection parity:

```bash
cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py \
  .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

---

## Separately delegable bounded worker instructions

### Worker A — frozen graph snapshots

**Objective:** refresh only the authoritative checked-in graph snapshots.

**Allowed write:** `tests/unit/infra/test_init_update.py`.

**Instructions:**

1. Confirm exact HEAD `bb65257155a73b621b0d0b6fb3426393c46de712`.
2. Run the deterministic derivation command above.
3. Confirm that the only new paths are Epic `00343` and Issues `00344`–`00346`.
4. Confirm that the only new non-empty issue dependency entry is:

   ```python
   "iss-00346": ["iss-00344", "iss-00345"]
   ```
5. Mechanically update the three frozen constants; do not touch assertions or repository metadata.
6. Run the two exact snapshot nodes.
7. Return the derived output, focused pytest result, and changed-path proof.

**Stop if:** derivation produces any additional delta, a dependency target is absent, validation/synchronization fails, or a production/runtime change appears necessary.

### Worker B — stable-completion timing precision

**Objective:** restore the accepted two-poll final-timeout preservation contract.

**Allowed writes:** the two provider/dogfood `pr_observation_wait.py` files only.

**Instructions:**

1. Confirm exact HEAD and current provider/dogfood blob parity.
2. Reproduce the unchanged named timeout test.
3. Replace integer-truncated internal quiet-window eligibility with exact monotonic quiet-deadline comparisons at:

   * under-budget final-poll admission;
   * final snapshot-timeout stable-state preservation.
4. Keep public wait metadata formatting and every status/reason field unchanged.
5. Copy/project the provider bytes mechanically to the dogfood counterpart.
6. Run the exact named test and provider/dogfood `cmp`.
7. Return the focused result, byte-parity result, and changed-path proof.

**Stop if:** the repair requires changing the test assertion, wrapper, public schema, snapshot classifier, zero-check-grace policy, or any path outside the two-file allowlist.

The two workers are merge-independent: Worker A owns the test constants; Worker B treats that test file as a read-only behavioral oracle.

---

## Exact rerun matrix

| Gate                      | Command                                                                                                                                                                                                                                                                                                    | Required result                           |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Graph snapshots           | `uv run pytest -q tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot` | `2 passed`                                |
| Timeout contract          | `uv run pytest -q tests/unit/infra/test_init_update.py::TestInstalledSkillAssets::test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state`                                                                                                                                            | `1 passed`                                |
| Exact three blockers      | Run the same three node IDs in one `pytest -q` invocation                                                                                                                                                                                                                                                  | `3 passed`                                |
| PR-observation regression | `uv run pytest -q tests/unit/infra/test_init_update.py -k "s430 or pr_observation_wait"`                                                                                                                                                                                                                   | all selected tests pass                   |
| Checked-in graph validity | `./spec-dock/scripts/spec-dock validate`                                                                                                                                                                                                                                                                   | success                                   |
| Provider projection       | `cmp -s <provider-pr_observation_wait.py> <dogfood-pr_observation_wait.py>`                                                                                                                                                                                                                                | exit `0`                                  |
| Static                    | `uv run ruff check <provider> <dogfood> tests/unit/infra/test_init_update.py`                                                                                                                                                                                                                              | pass                                      |
| Format                    | `uv run ruff format --check <provider> <dogfood> tests/unit/infra/test_init_update.py`                                                                                                                                                                                                                     | pass                                      |
| Diff hygiene              | `git diff --check`                                                                                                                                                                                                                                                                                         | pass                                      |
| Changed-path guard        | Compare new edits against the pre-existing working-tree baseline                                                                                                                                                                                                                                           | only the three allowlisted paths          |
| Final merge gate          | `uv run pytest --run-full-regression`                                                                                                                                                                                                                                                                      | prior three failures pass; no new failure |

## Verification boundary

Repository identity, exact files, metadata records, current wait implementation, provider/dogfood parity, and the historical accepted timeout contract were inspected through connected GitHub. The proposed commands and repairs were not executed, and no repository or GitHub mutation was performed.
