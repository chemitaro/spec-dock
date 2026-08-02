# Corrective Work Packet — `iss-00334` Final Five P1s

## 0. Source lock and immutable boundaries

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Inspected HEAD: `bb65257155a73b621b0d0b6fb3426393c46de712`
* GitHub connector comparison: branch and HEAD are identical; ahead `0`, behind `0`.
* Default branch and all other branches: not used.
* Repository mutation performed: none.
* Review input: exactly five P1 findings and no P0 findings. 
* Canonical `requirement.md`, `design.md`, and append-only `plan.md` remain read-only and byte-identical.
* No public command, option, schema, status, reason, Candidate identity, Review identity, Human decision, or publication semantic may change.

All five findings are **confirmed** at the locked HEAD.

| Work unit | Finding       | Disposition | Primary owner               |
| --------- | ------------- | ----------- | --------------------------- |
| WU-1      | `SPEC-P1-001` | Confirmed   | Documentation worker        |
| WU-2      | `CODE-P1-001` | Confirmed   | Application worker          |
| WU-3      | `CODE-P1-002` | Confirmed   | Apply-infrastructure worker |
| WU-4      | `CODE-P1-003` | Confirmed   | Application-test worker     |
| WU-5      | `QA-P1-001`   | Confirmed   | Main/report evidence owner  |

---

## WU-1 — Correct the managed onboarding guide’s current state

### Verification

**Confirmed.** The managed guide still binds itself to old source HEAD `bf9bc26…` and presents S08 through S14 as remaining work.

At the reviewed HEAD, the Report records S08, S09, S10, and S11 as closed, while S12 remains at the Human live gate.  Incorrect current status is explicitly a defect under REQ-006, and REQ-022/023 require the guide to carry the current roadmap without contradicting canonical authority.

### Exact allowlist

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md
tests/unit/domain/test_issue_planning_candidate.py
```

No production runtime file is admitted.

### Red test

Add one test without deleting the historical immutable-v4 ZIP test:

```text
test_current_managed_guide_matches_current_milestone_state
```

The test must read the actual managed guide path, not the historical v4 Candidate ZIP. The current test only validates the historical ZIP-contained guide.

The new Red must require:

* source baseline identifies `bb65257155a73b621b0d0b6fb3426393c46de712`;
* S08, S09, S10, and S11 are closed;
* S12 is open pending refreshed Human authorization and the live acceptance chain;
* S13 and S14 are not admitted or closed;
* the guide contains no assertion that all of S08 through S14 remain;
* S07 remains historical and does not substitute for new-boundary S12 evidence.

### Implementation action

Change only:

1. front-matter/source-identity text;
2. §8.1 status table;
3. §8.2 roadmap labels and explanatory rows;
4. the first-day checklist item that currently describes S08–S14 collectively as remaining.

Preserve the authority note, canonical precedence, architecture, direct-Oracle boundary, same-Candidate binding, failure semantics, and all four PlantUML roles. Do not describe S12 as closed.

### Focused verification

```bash
uv run pytest -q \
  tests/unit/domain/test_issue_planning_candidate.py \
  -k 'current_managed_guide or current_v4_guide'
```

Then run the existing S12 guide extraction and:

```bash
java -jar plantuml-1.2026.6.jar -checkonly <all-extracted-guide-diagrams>
```

### Stop condition

Stop if correctness would require changing Requirement, Design, Plan, Candidate identity, guide authority, or claiming that live S12 acceptance has occurred.

---

## WU-2 — Preserve archive-validator findings in apply results

### Verification

**Confirmed.** `IssuePlanningCandidateArchiveRejected` stores the concrete tuple in `error.findings`, while its exception argument is the fixed string `"Issue Candidate archive validation failed"`.

`run_issue_planning_apply()` inspects `error.args[0]` only when that value is a tuple, so the returned `details` are always empty.  This violates REQ-011, which requires archive findings to remain in `details` while retaining public reason `archive_rejected`.

### Exact allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning_apply.py
```

### Red test

Add:

```text
test_archive_apply_preserves_candidate_archive_findings_in_result_details
```

The Candidate loader must raise the application-owned error:

```python
IssuePlanningCandidateArchiveRejected(
    ("unsafe_entry_symlink", "checksum_mismatch")
)
```

Required assertions:

```text
status == rejected
reason == archive_rejected
details == ("unsafe_entry_symlink", "checksum_mismatch")
transaction call count == 0
```

### Implementation action

Replace the `error.args[0]` inference with direct use of the application-owned field:

```python
details=tuple(str(item) for item in error.findings)
```

Do not alter the exception class, gateway translation, status, reason, result output, or catch breadth.

Provider authority must be changed first. Regenerate or synchronize only the exact dogfood counterpart and reject any additional projection change.

### Focused verification

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_apply.py \
  -k 'archive_rejected or archive_findings'

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
```

### Stop condition

Stop on any required change to `application/ports.py`, concrete infra exceptions, public status/reason mapping, diagnostic redaction, or any path outside the three-file allowlist.

---

## WU-3 — Reject dangling symlink destinations before mutation

### Verification

**Confirmed.** `snapshot_regular_file()` first calls `Path.exists()`, which follows symlinks. A dangling symlink therefore enters the “absent” branch before the non-symlink check.

The absent-state rollback removes any surviving path or symlink rather than restoring the original link.  The snapshot is taken on the companion destination before transaction mutation.

The existing negative test covers a symlink whose target exists, but not a dangling symlink.  Design §8 requires differing or symlink destinations to stop before mutation and requires exact prior/absent-state rollback.

### Exact allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
tests/unit/infra/test_issue_planning_apply.py
```

### Red test

Add:

```text
test_dangling_symlink_destination_is_rejected_before_mutation_and_preserved
```

Setup:

1. create `companion.md` as a symlink to a nonexistent target;
2. record the exact `readlink()` value;
3. call `snapshot_regular_file()`.

Required pre-fix Red and post-fix Green behavior:

```text
raises ValueError matching "regular non-symlink"
target remains a symlink
readlink target is unchanged
no replacement file is written
```

### Implementation action

Make non-following metadata the existence authority:

```python
try:
    opened = path.stat(follow_symlinks=False)
except FileNotFoundError:
    return absent_snapshot
```

Then reject every non-regular entry, including any symlink, before reading bytes. Do not use `Path.exists()` to decide absence.

Retain the current `FileSnapshot` shape, byte/mode preservation, restore classifications, and public transaction results. This unit does not authorize broader descriptor or transaction redesign.

### Focused verification

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  -k 'dangling or snapshot or unsafe_companion'

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py
```

### Stop condition

Stop if the fix requires following the link target, representing symlinks as valid snapshots, changing rollback semantics, changing result reasons, or modifying another infra module.

---

## WU-4 — Make application unit tests independent of bootstrap and infra

### Verification

**Confirmed.** `tests/unit/application/test_issue_planning.py` imports `_Clock` and `_IssuePlanningGateway` from the concrete bootstrap composition root and imports infra-owned records.

`tests/unit/application/test_issue_planning_apply.py` does the same and additionally imports concrete `VerifiedIssueCandidate`.  Its transaction fake dynamically imports concrete `PlanningApplyExecution`, so the coupling is not limited to the import block.

The application layer already owns the required structural views, normalized errors, gateway protocol, and dependency object.   The accepted corrected Blocker N boundary expressly requires application unit-test fakes to use that contract without concrete infra dependencies.

### Exact allowlist

```text
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_apply.py
```

No production file is admitted.

### Red test

Add one structural test in `test_issue_planning.py`:

```text
test_application_issue_planning_unit_tests_use_application_owned_test_doubles_only
```

It must inspect both application test files and reject:

```text
spec_dock_runtime.cli.bootstrap
spec_dock_runtime.infra.
```

The check must cover ordinary imports and string-based dynamic imports.

### Implementation action

Within the two test files only:

* define a local `_FakeClock`;
* define a local `_FakeIssuePlanningGateway`;
* construct `IssuePlanningDependencies` from those local fakes;
* replace `StoredMetaRecord` and `DirectDependencyResolution` with local structural records exposing only fields the application reads;
* replace concrete `VerifiedIssueCandidate` with a local object conforming to `VerifiedIssueCandidateView`;
* replace concrete apply execution with a local object conforming to `PlanningApplyExecutionView`;
* keep unexpected gateway methods fail-fast with `AssertionError`;
* preserve all current behavioral assertions and explicit callable-override seams.

Do not weaken or edit the production structural regression test, whose application-layer rule permits only exact `infra.contracts` production imports.

### Focused verification

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py

! grep -nE \
  'spec_dock_runtime\.(cli\.bootstrap|infra\.)' \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py
```

### Stop condition

Stop if any production change is required, if the application port must be weakened, if concrete filesystem/archive/transaction behavior must be simulated as application behavior, or if `tests/cli_runtime/test_runtime_shell_s11.py` would need modification.

---

## WU-5 — Correct the S12/S14 gate ledger without inventing closure

### Verification

**Confirmed.** This finding has two distinct parts.

### A. Stale and contradictory Report text

The current gate ledger records S07 as blocked and S12 as Human-gate pending.  The Final Quality Gate still records Final QA and Final Code Review as not started, an obsolete Final Spec Review failure, and Final Commit as blocked.

A later heading nevertheless calls the work “S12 closure” and records hermetic, full-regression, distribution, and prompt-tuning results without recording the required live acceptance chain.  The heading and closure implication are stale/incorrect; the underlying hermetic evidence should be retained.

### B. Missing live acceptance evidence

Plan §22 requires:

1. refreshed Human authorization;
2. real PATH Oracle create;
3. downloadable authoring ZIP → Candidate;
4. fresh Review;
5. exact Human decision;
6. apply returning `ready`;
7. remote parity.

Without Human-approved live evidence, the Plan requires the run to remain open and forbids merge-ready promotion.  The accepted S12 packet states that the older S07 authorization cannot be reused and that the exact refreshed authorization record was not preserved in the inspected repository evidence.

The same packet requires exact Human-supplied decision bytes and then a successful git-bound apply with local/remote parity.  Its exit checklist says S12 cannot close while authorization, live Review, Human decision, apply, parity, guide Review, QA Review, security Review, or another required check remains incomplete.

**Repository-visible existing evidence at the locked HEAD:** focused/full regression, build/distribution, parity, static checks, PlantUML, Blocker repairs, and prompt tuning.

**Repository-visible or user-presented live evidence:** none for a refreshed authorization, real Candidate, live Review result, exact Human decision, apply result, `ready/adoption_published`, or the resulting remote-parity identity. External evidence may exist elsewhere, but none was presented and therefore none may be credited.

### Exact allowlist

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md
```

No code or test path is admitted.

### Red consistency check

Before editing, this command must fail:

```bash
python - <<'PY'
from pathlib import Path

path = Path(
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00334-implement-chatgpt-issue-planning-workflow/"
    "report.md"
)
text = path.read_text(encoding="utf-8")

assert "## 2026-07-30 — S12 closure" not in text
assert "S12 remains open pending refreshed Human live authorization" in text
assert (
    "live create / fresh Review / exact Human decision / "
    "apply / ready / remote parity: not performed"
) in text
assert "S13 not admitted" in text
assert "S14 not admitted" in text
PY
```

### Implementation action

Within `report.md` only:

1. Rename the misleading S12 closure heading to an explicitly non-closing hermetic-verification heading.
2. Preserve all verified focused/full/distribution/static/prompt-tuning evidence.
3. Add the exact statement that the live create/Review/Human/apply/parity chain was not performed or was not evidenced.
4. Correct the S12 Implementation Delegation Gate row to `open — refreshed Human live gate pending`.
5. Mark S13 and S14 as not admitted.
6. Correct the Final Quality Gate:

   * prior spec failures remain historical evidence, not current exact-HEAD final verdicts;
   * Final QA, Final Code Review, and Final Spec Review have not passed on the final exact pushed SHA;
   * Final Commit/merge-ready remains blocked by S12 live evidence, S13, and S14.
7. Do not remove or rewrite historical test evidence.

### Exact missing authorized operation

Only Main/Human may subsequently perform this sequence:

1. Human supplies a refreshed authorization binding:

   * target Issue;
   * exact worktree;
   * branch and starting HEAD;
   * `git-bound` mode;
   * Oracle browser/account precondition;
   * external evidence destination;
   * permitted repository mutation, commit, and push scope;
   * whether append-only Report integration is permitted.
2. Run real `planning create`.
3. Run fresh git-bound `review planning` with the same Candidate; require P0=`0`, P1=`0`, verdict `pass`.
4. Human supplies the exact `PlanningHumanDecisionV1` bytes bound to the reviewed identity and raw Review SHA.
5. Run `planning apply --mode git-bound` with the same Candidate.
6. Require `ready/adoption_published`, canonical three-document byte equality, authorized changed paths only, clean worktree, and local HEAD equal to remote branch HEAD.
7. Obtain fresh S12 QA and security PASS evidence.
8. Only then admit S13; only after S13’s mandatory commit/push and fresh code review may S14 run. Plan S14 requires fresh spec, code, and QA PASS on the exact pushed SHA before merge-ready handoff.

### Focused verification

```bash
python - <<'PY'
from pathlib import Path

path = Path(
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00334-implement-chatgpt-issue-planning-workflow/"
    "report.md"
)
text = path.read_text(encoding="utf-8")

assert "## 2026-07-30 — S12 closure" not in text
assert "S12 remains open pending refreshed Human live authorization" in text
assert (
    "live create / fresh Review / exact Human decision / "
    "apply / ready / remote parity: not performed"
) in text
assert "S13 not admitted" in text
assert "S14 not admitted" in text
PY

./spec-dock/scripts/spec-dock validate
git diff --check
```

### Stop condition

Stop on any attempt to:

* synthesize Human authorization or decision bytes;
* credit old-wrapper or older-HEAD live evidence;
* claim S12, S13, or S14 closure without the exact evidence above;
* run real Oracle or apply before refreshed authorization;
* modify Requirement, Design, or Plan;
* turn this Report correction into S13 execution.

---

## File overlap and execution order

```text
WU-4 ──> WU-2
WU-5 ──> WU-1
WU-3 independent
WU-2 + WU-3 ──> one provider-to-dogfood projection reconciliation
all units ──> final rerun matrix
```

Constraints:

* **WU-4 precedes WU-2** because both touch `tests/unit/application/test_issue_planning_apply.py`. First remove concrete test dependencies; then add the archive-findings Red against the application-owned fake boundary.
* **WU-5 precedes WU-1** so the guide’s roadmap is derived from the corrected gate ledger rather than the misleading “S12 closure” text.
* **WU-3 is file-independent** and may run in parallel in a separate checkout.
* WU-2 and WU-3 modify different provider/projection pairs. Main should perform one final projection reconciliation and reject every unrelated generated change.
* No implementation worker may execute the Human-gated live operation.

---

## Bounded implementation-subagent contract

Each subagent receives exactly one work unit and must:

```text
source_head: bb65257155a73b621b0d0b6fb3426393c46de712
allowed_paths: the exact unit allowlist
canonical_requirement_design_plan: read-only
github_mutation: prohibited unless separately authorized by Main
commit_push: prohibited unless separately authorized by Main
scope_expansion: prohibited
```

Required return:

```text
source_head
changed_paths
red_command_and_observed_failure
implementation_summary
green_commands_and_results
projection_parity_result
repository_status_before
repository_status_after
unverified_items
stop_condition_triggered_or_none
```

A worker must stop rather than opportunistically fix another finding, change a non-allowlisted file, weaken a test, or update canonical planning documents.

---

## Final rerun matrix

| Stage                          | Command                                                                                                                                                                                                                               | Required result                                                      |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Application test boundary      | `uv run pytest -q tests/unit/application/test_issue_planning.py tests/unit/application/test_issue_planning_apply.py`                                                                                                                  | Green; no bootstrap/infra dependency in either test                  |
| Archive findings               | `uv run pytest -q tests/unit/application/test_issue_planning_apply.py -k 'archive_rejected or archive_findings'`                                                                                                                      | Exact findings retained                                              |
| Apply destination safety       | `uv run pytest -q tests/unit/infra/test_issue_planning_apply.py -k 'dangling or snapshot or unsafe_companion'`                                                                                                                        | Dangling and live symlinks rejected unchanged                        |
| Guide status                   | `uv run pytest -q tests/unit/domain/test_issue_planning_candidate.py -k 'current_managed_guide or current_v4_guide'`                                                                                                                  | Managed guide current; historical v4 evidence preserved              |
| Structural boundary            | `uv run pytest -q tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression`                                                                                               | Green unchanged                                                      |
| Issue Planning integration     | `uv run pytest -q --run-full-regression tests/cli_runtime/test_chatgpt_cli.py tests/integration/test_issue_planning_chatgpt_transport.py tests/integration/test_issue_planning_apply.py tests/integration/test_issue_planning_e2e.py` | Green                                                                |
| Relevant projection parity     | `cmp -s` for provider/dogfood `application/issue_planning.py` and `infra/issue_planning_apply.py`                                                                                                                                     | Both byte-identical                                                  |
| Guide syntax                   | PlantUML 1.2026.6 `-checkonly` over every extracted managed-guide block                                                                                                                                                               | All diagrams pass                                                    |
| Report consistency             | WU-5 Python assertion                                                                                                                                                                                                                 | S12 open; S13/S14 not admitted                                       |
| Fast regression                | `uv run pytest -q`                                                                                                                                                                                                                    | Green with policy-expected skips only                                |
| Explicit full regression       | `uv run pytest -q --run-full-regression`                                                                                                                                                                                              | Green; no unexpected skips                                           |
| Distribution                   | `uv build`                                                                                                                                                                                                                            | Wheel and sdist build                                                |
| Canonical validation           | `./spec-dock/scripts/spec-dock validate`                                                                                                                                                                                              | Pass                                                                 |
| Diff hygiene                   | `git diff --check`                                                                                                                                                                                                                    | Pass                                                                 |
| Scope guard                    | `git status --short` plus exact changed-path comparison                                                                                                                                                                               | Only union of five allowlists                                        |
| Authorization-gated acceptance | Plan §22 live sequence                                                                                                                                                                                                                | **Not run by repair subagents; remains pending Human authorization** |
| Final promotion                | S13 followed by S14 exact-SHA fresh spec/code/QA reviews                                                                                                                                                                              | Required before any merge-ready claim                                |

## Assumption and unverified boundary

This packet is based only on the exact connected GitHub snapshot and the supplied final Red Team JSON. No tests were executed and no external live-evidence store was supplied. Consequently, post-repair Green results and S12 live acceptance remain future evidence, not established facts.
