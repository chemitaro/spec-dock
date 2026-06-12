---
created_by_role: implementation-planner
scope_id: iss-00184
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260612t072453z-research-spec-dock-hub-rename-surface-inventory.md
  - spec-dock/docs/authoring/issue-plan.md
  - spec-dock/docs/phase_plan_issue.md
  - spec-dock/docs/workflow_issue.md
  - src/spec_dock/cli.py
  - src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
  - tests/unit/infra/test_init_update.py
  - tests/cli_runtime/harness.py
  - tests/cli_runtime/test_wrappers.py
intended_targets:
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Implementation Plan Draft: Spec Dock Hub Full Migration

This is delegated planning evidence for `iss-00184 Rename Spec Dock Hub Skill`.
It is not canonical `plan.md`, does not claim adoption, and does not authorize implementation.

## 1. Plan Summary

Plan the full hard cutover from `spec-driven-tdd-workflow` to `spec-dock-hub` across current provider assets, dogfooding mirror, installer/update cleanup, docs references, tests, and final verification.

The planned execution order should be:

1. Provider/mirror skill rename and skill text.
2. Installer/update cleanup, including `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` obsolete exact path `.agents/skills/spec-driven-tdd-workflow/SKILL.md`.
3. Current docs references.
4. Tests/harness expectations.
5. Dogfooding sync/validate and current-surface inspections.
6. S90 docs impact resolution and S99 final quality gates.

The plan must keep historical evidence under prior specs/discussions as historical evidence, not current runtime/discovery surface. No compatibility alias, forwarding skill, stub, or symlink should be introduced.

## 2. Requirement / Design Traceability

| Requirement item | Design / evidence basis | Planned closure owner |
|---|---|---|
| AC-001: `spec-dock-hub` is discoverable as SpecDock hub | Skill path/frontmatter/heading/description in provider and mirror | S01 |
| AC-002: old-name references are inventoried and classified | Research inventory and current-surface/historical boundary | S03, S05 |
| AC-003: hub/leaf boundary remains intact | Existing hub text and `iss-00164` boundary; no leaf workflow absorption | S01, S99 |
| AC-004: provider/mirror relationship verified | `cmp` parity and dogfooding sync/validate evidence | S01, S05 |
| AC-005: current surfaces use new name, historical evidence preserved | scoped positive/negative `rg`, docs updates, report rationale | S03, S05, S90 |
| AC-006: update removes obsolete old managed entry | `cli.py`, `host-adapters/meta.json`, update prune tests | S02, S04 |
| EC-001: old path dependencies fixed without alias | tests and harness updated to new path/name | S04 |
| EC-002: short name is clarified by text | description/heading/first bullets mention hub, route selector, global invariant | S01 |
| EC-003: historical references remain allowed | negative inspection excludes `spec-dock/initiatives/**` historical evidence | S05 |

Source requirement/design revisions observed in this draft run:

- `requirement.md`: draft, last updated `2026-06-12`, fixes canonical name `spec-dock-hub` and no compatibility alias.
- `design.md`: draft, last updated `2026-06-12`, includes provider/mirror rename, manifest obsolete exact cleanup, docs/tests, historical boundary, and reviewer-corrected manifest contract.
- `report.md`: draft ledger contains requirement/design reviewer evidence and prior research/design draft adoption entries; this draft does not claim those gates itself.

## 3. Milestones

- M1: Hub identity cutover is represented in the shipped provider skill and dogfooding mirror.
- M2: Installer/update treats the old path as obsolete managed cleanup metadata, not compatibility.
- M3: Current docs and current tests/harness use `spec-dock-hub`.
- M4: Focused tests and current-surface inspections prove new-name presence, old-name current-surface absence, and old-path cleanup.
- M5: Dogfooding sync/validate and final reviewer gates close the issue-wide risk.

## 4. Dependency-Derived Execution Order

```text
reviewed requirement/design evidence
  -> S01 provider + mirror hub skill rename and text
  -> S02 installer/update cleanup contract and obsolete exact path
  -> S03 current docs references
  -> S04 tests/harness expected inventory and prune coverage
  -> S05 dogfooding sync/validate + scoped inspections
  -> S90 docs impact resolution
  -> S99 final quality gate
```

Rationale:

- Tests and docs need the new provider path and skill text as their reference.
- Existing consumer cleanup cannot be safely tested until `meta.json` and installer managed lists agree on current/obsolete paths.
- Negative old-name inspection must run after docs/tests are updated, otherwise expected current-surface matches will be indistinguishable from failures.

## 5. Issue / Step Slicing

### S01 Provider / Mirror Skill Rename And Skill Text

- Behavior goal: current provider and dogfooding skill surfaces expose `spec-dock-hub` as the hub skill and no current old-name skill directory remains.
- Allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` deletion only
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md` deletion only
- Forbidden changes:
  - leaf skill workflows, runtime validation, canonical specs, tests, docs, config.
  - any compatibility alias / forwarding skill / symlink at `spec-driven-tdd-workflow`.
- Delegated role: `doc-writer` for skill text and path-level scaffold evidence; reviewer focus: `spec-reviewer` for wording/boundary and `code-reviewer` for shipped asset path behavior.
- Stop conditions:
  - old-name skill must remain for a technical reason,
  - provider/mirror bytes cannot be made equivalent,
  - hub text requires absorbing leaf workflow steps.
- Output required:
  - changed files, old/new path summary, `cmp` result, scoped `rg` result, `No material implementation decisions beyond the approved plan.` or Ledger Note.

### S02 Installer / Update Cleanup Contract

- Behavior goal: new installs install `spec-dock-hub`; updates prune old managed `.agents/skills/spec-driven-tdd-workflow/SKILL.md` without preserving it as compatibility.
- Allowed paths:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - focused assertions/fixtures in `tests/unit/infra/test_init_update.py` only as needed for this behavior
- Forbidden changes:
  - installer architecture rewrite, broad cleanup policy changes, unrelated obsolete paths, runtime command changes, docs, skill text.
- Delegated role: `dev-coder`; reviewer focus: `code-reviewer`.
- Stop conditions:
  - `managed_assets.obsolete_exact_file_paths` conflicts with a current managed path,
  - `_LEGACY_MANAGED_SKILL_NAMES` is needed in a way that reintroduces old discovery,
  - old path cleanup cannot be represented as exact-file cleanup.
- Output required:
  - `cli.py` managed/current/legacy treatment, exact manifest path added, prune fixture/test result, manifest validation result, rollback note.

### S03 Current Docs References

- Behavior goal: current user-facing docs point to `.agents/skills/spec-dock-hub/SKILL.md` and do not present old name as a current entry.
- Allowed paths:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `spec-dock/docs/README.md`
- Forbidden changes:
  - historical specs/discussions, canonical issue docs, implementation code/tests, new migration docs unless S90 determines they are required.
- Delegated role: `doc-writer`; reviewer focus: `spec-reviewer`.
- Stop conditions:
  - docs require mentioning old name as current compatibility,
  - generated dogfooding docs need refresh beyond these current references.
- Output required:
  - docs changed, current-surface `rg` positive/negative evidence, historical evidence exclusion rationale.

### S04 Tests / Harness Expectations

- Behavior goal: tests encode `spec-dock-hub` as the current managed skill, verify obsolete old path cleanup, and keep provider/mirror parity coverage.
- Allowed paths:
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/unit/infra/test_init_update.py`
- Forbidden changes:
  - production code, docs, skill files, broad test rewrites, deleting existing coverage unrelated to the rename.
- Delegated role: `dev-coder`; reviewer focus: `code-reviewer` with QA attention on test sensitivity.
- Stop conditions:
  - tests require a compatibility alias to pass,
  - expected managed inventory no longer matches installer behavior,
  - update-prune fixture cannot distinguish old managed skill from custom skills.
- Output required:
  - focused test list, updated expected names/paths, red/characterization or existing-failure evidence where practical, green results.

### S05 Dogfooding Sync / Validate And Current-Surface Inspections

- Behavior goal: dogfooding workspace reflects the shipped cutover and generated projections remain valid.
- Allowed paths:
  - generated dogfooding outputs produced by `./spec-dock/scripts/spec-dock sync` only if canonical implementation steps intentionally require them
  - `spec-dock/active/issue/report.md` evidence recording by main orchestrator only, not by this delegated draft
- Forbidden changes:
  - manual rewrite of historical evidence, canonical plan/report by delegated worker, unrelated dogfooding data edits.
- Delegated role: `dev-coder` or parent orchestrator approved-local-execution if sync/validate are operational gates; reviewer focus: `code-reviewer` for generated diff and `spec-reviewer` for spec/doc consistency.
- Stop conditions:
  - sync rewrites active canonical docs unexpectedly,
  - validation fails for reasons outside the rename,
  - old current-surface references remain outside allowed cleanup metadata/tests.
- Output required:
  - sync/validate results, `git diff --check`, scoped `rg` inspections, generated diff summary.

### S90 Docs Impact Resolution

- Behavior goal: confirm whether docs impact is fully covered by S03 or whether additional current docs/templates/skill references require doc-writer update.
- Allowed paths:
  - docs/templates/skill reference files identified by current-surface inspection, if and only if they are current references and not historical evidence
  - `spec-dock/active/issue/report.md` evidence recording by main orchestrator only
- Forbidden changes:
  - historical evidence rewrite, implementation/tests unless plan is amended, acceptance/reviewer-pass claims.
- Delegated role: `doc-writer`; reviewer focus: `spec-reviewer`.
- Stop conditions:
  - additional docs surface changes exceed design scope,
  - old-name references are ambiguous between current docs and historical evidence.
- Output required:
  - docs impact decision, files updated or no-op rationale, docs/spec alignment review requirement.

### S99 Final Quality Gate

- Behavior goal: close issue-wide risk after step-level reviews and verification.
- Allowed paths:
  - no implementation edits unless reviewer findings trigger bounded follow-up under the owning step
  - `spec-dock/active/issue/report.md` final evidence recording by main orchestrator only
- Forbidden changes:
  - using final review as replacement for step review, claiming completion without required evidence, direct unplanned fixes.
- Delegated roles and reviewer focus:
  - `qa-reviewer`: test sufficiency and integration-test need.
  - issue-wide `code-reviewer`: integrated diff, installer/update behavior, scaffold path risks.
  - `spec-reviewer`: requirement/design/plan/report/docs consistency and AC/EC closure.
- Stop conditions:
  - any final reviewer fails,
  - closure index rows lack evidence,
  - sync/validate/focused tests are missing or failing,
  - report ledgers are incomplete.
- Output required:
  - final reviewer verdicts, closure coverage, unresolved risks, final validation command results.

## 6. Test Strategy Mapping

### Focused pytest seeds

Run the narrow lane first:

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py -k "managed or skill or bundled or parity or routing or prunes or obsolete or manifest or README"
```

If `-k` selection becomes brittle or misses renamed tests, broaden to:

```bash
uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py
uv run pytest tests/cli_runtime
```

### Concrete test / inspection seeds

- Provider/mirror byte parity:

```bash
cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md
```

- Positive current-surface inspection:

```bash
rg -n "spec-dock-hub|SpecDock Hub" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
```

- Negative current-surface inspection with expected exceptions:

```bash
rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
```

Expected remaining current-surface matches should be limited to cleanup metadata and tests/fixtures that explicitly assert old managed path pruning:

- `_LEGACY_MANAGED_SKILL_NAMES` only if it is cleanup metadata, not discovery.
- `managed_assets.obsolete_exact_file_paths` item `.agents/skills/spec-driven-tdd-workflow/SKILL.md`.
- test names/fixtures/assertions that seed and verify obsolete old managed path removal.

- Historical evidence exclusion:

```bash
rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" spec-dock/initiatives
```

This command is evidence for excluded historical references, not a failure condition by itself.

### Required fixture/test coverage

- Update prune fixture:
  - seed existing install with `.agents/skills/spec-driven-tdd-workflow/SKILL.md`;
  - run `main(["update", str(target)])`;
  - assert `.agents/skills/spec-dock-hub/SKILL.md` exists;
  - assert old exact file path no longer exists;
  - assert custom skill remains.
- Manifest obsolete exact path validation:
  - assert build plan contains `.agents/skills/spec-driven-tdd-workflow/SKILL.md` in `obsolete_exact_rel_paths`;
  - assert manifest validation still rejects overlaps with current managed paths;
  - assert old path is not in current managed targets.
- Harness/current inventory:
  - `_EXPECTED_MANAGED_SKILL_NAMES` uses `spec-dock-hub`;
  - `_assert_managed_skills_installed` expects `spec-dock-hub/SKILL.md`.

## 7. Review Gates

- S01: `spec-reviewer` for hub/leaf wording and `code-reviewer` for shipped asset path behavior.
- S02: `code-reviewer` for installer/update cleanup semantics and manifest exact-path safety.
- S03: `spec-reviewer` for docs/spec alignment and historical evidence boundary.
- S04: `code-reviewer` plus QA attention for test sensitivity and fixture validity.
- S05: `code-reviewer` for generated/runtime impact and `spec-reviewer` if docs/spec references changed.
- S90: `doc-writer` output followed by `spec-reviewer` docs/spec alignment.
- S99: fresh `qa-reviewer`, issue-wide `code-reviewer`, and `spec-reviewer` pass are required before the main orchestrator may treat the issue as ready for completion.

Delegated worker output is not a reviewer pass. Reviewer failures should route to bounded follow-up under the affected step, or trigger plan amendment if outside the planned contract.

## 8. Rollback / Compatibility

- Rollback must revert the provider/mirror rename, `cli.py` managed lists, manifest obsolete exact path, docs references, and tests together.
- Partial rollback that leaves both old and new hub skills is not acceptable.
- Compatibility alias, forwarding skill, stub, or symlink is forbidden by requirement/design.
- `_LEGACY_MANAGED_SKILL_NAMES` may only be treated as obsolete cleanup metadata if tests and docs make clear it is not a current discovery surface.

## 9. Docs Impact

Known docs/current references:

- `README.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `spec-dock/docs/README.md`

S90 should resolve whether any additional current docs/templates/skill references appear after S01-S05. Historical specs, reports, and prior discussions should not be mass-rewritten. If a current docs reference is discovered outside the known set, S90 may update it only if it remains within design scope; otherwise it should trigger plan amendment and re-review.

## 10. Final Quality Gate

Final validation commands:

```bash
uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py
uv run pytest tests/cli_runtime
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock validate
git diff --check
```

Final inspections:

```bash
cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md
rg -n "spec-dock-hub|SpecDock Hub" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills src/spec_dock/assets/install_root/.agents/host-adapters/meta.json
```

The old-name `rg` must be interpreted with the expected cleanup/test exceptions above. Any old-name match in current docs, current provider/mirror skill paths, or current discovery inventory is a failure.

## 11. Plan Blockers

Blocking design gaps found by this planning draft: none.

Potential plan amendment triggers:

- A hidden old-name current surface appears outside the planned current-surface path list.
- `host-adapters/meta.json` obsolete exact cleanup conflicts with current managed target validation.
- Provider/mirror parity fails after rename or sync.
- Tests can only pass by introducing a compatibility alias or forwarding skill.
- Historical evidence ambiguity makes it unclear whether a reference is current surface or preserved past evidence.
- `spec-dock sync` changes canonical requirement/design/report/plan unexpectedly.

If any trigger occurs, report the finding to the main orchestrator and amend/re-review the canonical plan before continuing.

## 12. Integration Notes for Main Orchestrator

- Suggested canonical `plan.md` structure:
  - requirements covered;
  - dependency-derived execution order;
  - milestone list;
  - Spec-Locked Closure Index;
  - S01-S05 implementation steps with delegation contracts and concrete test cases;
  - S90 docs impact resolution;
  - S99 final quality gate;
  - Final Exit Contract.
- `report.md` should record this draft in Delegated Draft Evidence and Evidence Adoption Ledger only after main-orchestrator diff guard and adoption decision.
- The main orchestrator should run a post-run diff guard confirming this delegated authoring created only this discussion draft.
- A fresh `spec-reviewer` pass remains required for any canonical `plan.md` produced from this draft.

### Spec-Locked Closure Index Candidates

| ID | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Owner step |
|---|---|---|---|---|---|---|---|
| cl-ac-001 | AC-001 | `spec-dock-hub` name/path/description identify the SpecDock hub route selector and global invariant surface | provider and mirror `SKILL.md`, current skill inventory | unclear hub discovery / wrong entry skill | yes | inspect-only + pytest | S01, S04 |
| cl-ac-002 | AC-002 | old-name references are classified as current update targets or historical evidence | scoped `rg`, report rationale | unreviewed stale references or historical rewrite | yes | inspect-only | S03, S05 |
| cl-ac-003 | AC-003 | hub keeps route selector + global invariant role and does not absorb leaf workflows | skill text diff and reviewer check | hub/leaf boundary regression | yes | inspect-only + reviewer | S01, S99 |
| cl-ac-004 | AC-004 | provider/mirror parity and dogfooding validation are recorded | `cmp`, sync, validate | provider/mirror drift | yes | command | S01, S05 |
| cl-ac-005 | AC-005 | current surface uses new name; old name remains only historical or cleanup/test evidence | positive/negative `rg` with exception list | mixed naming on current docs/discovery | yes | inspect-only | S03, S05, S90 |
| cl-ac-006 | AC-006 | update installs new hub and removes obsolete old managed exact file path | update prune fixture, manifest path, installed skill inventory | existing consumers retain both hub skills | yes | pytest + inspect-only | S02, S04 |
| cl-ec-001 | EC-001 | old path dependencies in tests/docs are updated, not hidden behind alias | focused pytest and no old alias path | compatibility alias masks broken references | yes | pytest | S04 |
| cl-ec-002 | EC-002 | `spec-dock-hub` text compensates for short name with hub/route/global invariant wording | provider/mirror skill text | name becomes too vague | yes | inspect-only + reviewer | S01 |
| cl-ec-003 | EC-003 | historical references are excluded from current-surface negative gate and documented as non-current | `rg spec-dock/initiatives` as exclusion evidence | false negative gate or destructive historical rewrite | yes | inspect-only | S05, S90 |

### Lightweight Provenance Summary

- Leaf evidence used: requirement, design, report ledgers, surface inventory research, issue plan authoring docs, issue workflow docs, current installer/test/harness surfaces.
- Forbidden actions avoided: no canonical docs edited, no implementation files edited, no tests edited, no config/readme/skill files edited, no GitHub state mutated, no phase promoted.
- Unresolved design gaps: none identified; amendment triggers are listed above.
- No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
