# S12 Blocker B Authority-Reconciliation Amendment

## Source Identity

| Field                   | Locked value                                                 |
| ----------------------- | ------------------------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                                        |
| Branch                  | `iss-00334-implement-chatgpt-issue-planning-workflow`        |
| Exact pushed HEAD       | `fd97aca1f005e2fe066a872343039c7e5b8889ca`                   |
| Connector result        | Branch is identical to the exact HEAD; ahead `0`, behind `0` |
| Default-branch fallback | Forbidden and not used                                       |
| Amendment scope         | Blocker B only                                               |

The exact pushed HEAD records the immutable regression-repair packet and append-only Report evidence.  This amendment resolves only the authority mismatch identified in the bounded follow-up. 

## Authority Distinction

**The two snapshot authorities are correctly distinguished as follows:**

1. `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` is a **raw checked-in metadata snapshot**. The owning test reads each `.meta.json`, takes `payload.get("depends_on", [])`, and compares those direct values without projection.
2. `_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP` is a **runtime-projected Issue dependency snapshot**. The owning test compares it against the non-empty entries of `result.state.issue_depends_on_map`, not against raw `.meta.json` values.

Therefore, Epic IDs in raw `depends_on` fields must remain Epic IDs in the full raw-map constant, while the non-empty Issue map must contain the runtime-expanded Issue dependencies.

This supersedes only the incorrect six-value block under the prior packet’s `_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP` instructions. Blockers A and C are unchanged.

## Amended Blocker B Instructions

### Path inventory

The prior packet’s ten additions to `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` remain unchanged.

Expected count:

```text
213 + 10 = 223
```

### Raw full-map additions

Add these exact entries to `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`:

```python
"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/.meta.json": [],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/.meta.json": [],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00335-implement-initiative-epic-portfolio-planning-workflow/.meta.json": [
    "iss-00334",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00336-implement-targeted-review-and-planning-surface-cutover/.meta.json": [
    "iss-00334",
    "iss-00335",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/.meta.json": [
    "epic-00331",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/issues/iss-00337-analysis-guided-issue-execution-and-per-issue-delivery/.meta.json": [
    "epic-00331",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/.meta.json": [
    "epic-00332",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00338-multi-issue-epic-coordination-and-finish/.meta.json": [
    "epic-00332",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00339-official-global-cutover-and-rollback-activation/.meta.json": [
    "iss-00338",
],

"spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00333-epic-completion-and-global-cutover/issues/iss-00340-post-cutover-evaluation-release-and-closure/.meta.json": [
    "iss-00339",
],
```

These values match the exact checked-in metadata: `epic-00331` and `iss-00334` omit `depends_on`; `iss-00335` and `iss-00336` use direct Issue dependencies.

The later nodes preserve their raw Epic or Issue dependency identities exactly as checked in.

Expected raw full-map key count:

```text
213 + 10 = 223
```

### Projected non-empty Issue-map additions

Replace the prior packet’s six incorrect entries with these exact runtime-projected values:

```python
"iss-00335": ["iss-00334"],
"iss-00336": ["iss-00334", "iss-00335"],
"iss-00337": ["iss-00334", "iss-00335", "iss-00336"],
"iss-00338": ["iss-00337"],
"iss-00339": ["iss-00337", "iss-00338"],
"iss-00340": ["iss-00337", "iss-00339"],
```

These values belong only in:

```text
_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP
```

Do not place raw Epic IDs in this runtime-projection constant.

The expected count remains:

```text
62 + 6 = 68
```

The authority correction changes the six values, not the number of added non-empty Issue entries.

## Red and Green Amendment

The worker’s prior Red is accepted as the correct stop:

```text
raw path/full-map snapshot: failed because ten approved nodes were absent
runtime non-empty Issue snapshot: failed because raw dependency values were assigned to a projected authority
production changes: 0
metadata changes: 0
```

After applying the corrected Blocker B constants, run:

```bash
uv run pytest -q --run-full-regression \
  --basetemp "$S12_EXTERNAL_ROOT/pytest/regression-blocker-b" \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot
```

Green requires all of the following:

```text
.meta.json path count = 223
raw depends_on full-map key count = 223
runtime non-empty Issue-map count = 68

raw iss-00337 value = ["epic-00331"]
raw iss-00338 value = ["epic-00332"]
raw iss-00339 value = ["iss-00338"]
raw iss-00340 value = ["iss-00339"]

projected iss-00337 value = ["iss-00334", "iss-00335", "iss-00336"]
projected iss-00338 value = ["iss-00337"]
projected iss-00339 value = ["iss-00337", "iss-00338"]
projected iss-00340 value = ["iss-00337", "iss-00339"]

missing prior baseline paths = 0
unexpected paths = 0
unexpected raw full-map entries = 0
unexpected projected non-empty entries = 0
```

The complete explicit full regression remains mandatory after Blockers A, B, and C and the separate static repair are integrated on one clean commit candidate.

## Write Allowlist and Read-Only Boundaries

The exact four-path write allowlist remains unchanged:

```text
tests/cli_runtime/test_authoring.py
tests/unit/infra/test_init_update.py
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
```

For Blocker B itself, the only permitted edit is:

```text
tests/unit/infra/test_init_update.py
```

The following remain read-only:

```text
all .meta.json files
Requirement / Design / Plan
report.md
Prompt resources
Skill files
shell wrappers
runtime production behavior
public commands
schemas
```

Blockers A and C are not amended.

## Amended Stop Conditions

Stop and return to Main if any of the following occurs:

* A raw full-map entry is populated with the runtime-projected value rather than the exact checked-in `.meta.json` value.
* A projected non-empty Issue-map entry contains `epic-00331` or `epic-00332`.
* The projected six entries differ from the exact values locked above.
* The raw ten entries differ from the exact checked-in metadata.
* The path or raw full-map count is not `223`.
* The projected non-empty Issue-map count is not `68`.
* Any previously expected path or dependency entry disappears.
* Any additional path or dependency beyond the exact ten raw and six projected additions appears.
* A `.meta.json` file is edited to make the snapshot pass.
* Runtime production code is changed to make the snapshot match.
* Any path outside the unchanged four-path allowlist changes.
* Blocker A or C is altered under this amendment.
* A canonical document, Report, Prompt, Skill, shell wrapper, public behavior, or schema changes.

DISPOSITION: GO_BOUNDED_BLOCKER_B_AMENDMENT
