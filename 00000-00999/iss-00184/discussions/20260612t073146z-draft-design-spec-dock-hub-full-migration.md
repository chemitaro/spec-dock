---
created_by_role: system-architect
scope_id: iss-00184
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260612t070646z-interview-hub-skill-naming-compatibility-direction.md
  - spec-dock/active/issue/discussions/20260612t071326z-interview-canonical-hub-skill-name.md
  - spec-dock/active/issue/discussions/20260612t072453z-research-spec-dock-hub-rename-surface-inventory.md
  - spec-dock/active/epic/requirement.md
  - AGENTS.md
  - src/spec_dock/cli.py
  - src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md
  - .agents/skills/spec-driven-tdd-workflow/SKILL.md
  - README.md
  - src/spec_dock/assets/spec_dock/docs/README.md
  - spec-dock/docs/README.md
  - tests/cli_runtime/test_wrappers.py
  - tests/cli_runtime/harness.py
  - tests/unit/infra/test_init_update.py
intended_targets:
  - spec-dock/active/issue/design.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# Draft Design: SpecDock Hub Full Migration

## 1. Requirement Coverage

Adopted requirement decisions are:

- Canonical hub skill name is `spec-dock-hub`.
- `spec-driven-tdd-workflow` must not remain as a compatibility alias, forwarding skill, current discovery entry, or current docs entry.
- The hub/leaf boundary from `iss-00164` remains unchanged: hub is route selector + global invariant surface; leaf skills own task-specific workflow spines.
- Provider-side installed agent tooling under `src/spec_dock/assets/install_root/` is the source of record for shipped skills.
- `.agents/skills/` is the dogfooding mirror and parity target, not an independent authority.
- Historical specs, reports, and discussions may preserve old-name evidence; current runtime/discovery/docs/test surfaces should migrate.

Acceptance coverage mapping:

- AC-001: rename provider and mirror hub directory/frontmatter/heading/description to `spec-dock-hub`.
- AC-002 and AC-005: inventory and classify old-name references; use scoped negative inspection for current surfaces only.
- AC-003: keep hub content as routing/invariant guidance and do not absorb leaf workflow details.
- AC-004: verify provider/mirror parity and dogfooding docs after scaffold-affecting changes.
- AC-006: update installer managed skill ownership so new hub is installed and old managed hub path is cleaned up, not exposed as compatibility.

## 2. Existing Context Findings

Current observed hub files:

- Provider: `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- Dogfooding mirror: `.agents/skills/spec-driven-tdd-workflow/SKILL.md`

Current hub metadata says `name: spec-driven-tdd-workflow`, description says it routes work to leaf workflows, and the heading says `Spec-driven TDD Workflow (Hub)`. The content already describes entry/routing, route selector, global invariants, reviewer gate handling, evidence adoption, and leaf routing.

Current installer/update surface:

- `src/spec_dock/cli.py` lists `spec-driven-tdd-workflow` in `_MANAGED_SKILL_NAMES`.
- `src/spec_dock/cli.py` also lists `spec-driven-tdd-workflow` in `_LEGACY_MANAGED_SKILL_NAMES`.
- `_managed_skill_ownership_names()` unions current and legacy names for pruning decisions.

Current docs/tests surface:

- `README.md`, `src/spec_dock/assets/spec_dock/docs/README.md`, and `spec-dock/docs/README.md` expose the old hub path.
- `tests/cli_runtime/harness.py` expects the old managed skill name.
- `tests/cli_runtime/test_wrappers.py` reads the installed old hub path.
- `tests/unit/infra/test_init_update.py` has provider/mirror parity mappings, managed asset assertions, update/prune tests, install/update inventories, and routing contract reads that mention the old path.

Historical evidence surface:

- Older `spec-dock/initiatives/**` specs, reports, and discussions contain old-name references as evidence of the prior state. Those should not be mechanically rewritten unless a current test or active canonical artifact deliberately adopts a migration note.

## 3. Design Decisions

1. Hard-cutover the current hub skill directory from `spec-driven-tdd-workflow` to `spec-dock-hub`.
2. Set provider and mirror `SKILL.md` frontmatter to `name: spec-dock-hub`.
3. Rewrite the heading and description to make the role explicit, for example `# SpecDock Hub` and a description that says it is the SpecDock entry/routing skill and global invariant surface.
4. Keep the body focused on route selection, global invariants, phase/reviewer gates, evidence adoption, and links to leaf skills/docs.
5. Do not create a `spec-driven-tdd-workflow` skill directory, stub, symlink, forwarding note, or alias.
6. Change `_MANAGED_SKILL_NAMES` to include `spec-dock-hub` and remove `spec-driven-tdd-workflow`.
7. Keep `spec-driven-tdd-workflow` in `_LEGACY_MANAGED_SKILL_NAMES` only if it is needed as cleanup ownership metadata for update pruning. It must not be copied, installed, advertised, or counted as a current managed skill.
8. Update README/docs current skill lists to show `.agents/skills/spec-dock-hub/SKILL.md`.
9. Update tests to assert both positive new-name installation and negative old-name absence on current surfaces.
10. Preserve historical evidence by narrowing negative search scopes instead of global rewriting.

## 4. Alternatives Considered

- Compatibility alias: rejected by approved requirement. It lowers migration risk but creates mixed naming and violates the user decision.
- Metadata-only rename inside old directory: rejected because discovery/path remains misleading and violates full migration.
- Global rewrite of every old-name occurrence: rejected because historical specs/discussions are evidence, not current surface, and mass rewrite would damage auditability.
- Remove old name from both managed and legacy lists: possible only if tests show existing consumer update still prunes the obsolete old path through another explicit obsolete-path mechanism. Current architecture already uses legacy managed names for pruning, so keeping it there as cleanup metadata is lower risk.

## 5. Boundary / Contract Model

Provider source:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md` is the shipped hub skill authority.

Dogfooding mirror:

- `.agents/skills/spec-dock-hub/SKILL.md` must byte-match provider source under the existing parity contract.

Installer/update:

- `_MANAGED_SKILL_NAMES` is the current installed skill contract.
- `_LEGACY_MANAGED_SKILL_NAMES` is cleanup ownership for stale managed paths only.
- A legacy name in `_LEGACY_MANAGED_SKILL_NAMES` is not a compatibility promise.

Docs:

- Top-level README and shipped docs README advertise current installed skill paths.
- Dogfooding `spec-dock/docs/README.md` mirrors shipped docs after sync/update or intentional direct parity update.

Tests:

- Runtime harness validates installed managed skill set.
- Installer/unit tests validate provider assets, parity, update behavior, and obsolete path cleanup.

Historical evidence:

- Prior issue specs/discussions/report entries keep old names when describing past state.

## 6. Dependency Analysis

Dependency ordering:

```text
requirement decisions
  -> provider hub skill path/content
  -> installer current managed skill list
  -> legacy cleanup ownership for obsolete old hub path
  -> dogfooding mirror parity
  -> README/docs current skill references
  -> test expected inventories and update/prune assertions
  -> focused pytest + scoped negative inspection
  -> sync/validate dogfooding evidence
```

Critical dependency:

- Tests that install or update a target repo use `_EXPECTED_MANAGED_SKILL_NAMES`; this must move in lockstep with `_MANAGED_SKILL_NAMES`.
- Provider/mirror parity test will fail unless both path inventory and file bytes are updated together.
- Update cleanup must be tested with a target that contains stale `.agents/skills/spec-driven-tdd-workflow/SKILL.md` and confirms new `.agents/skills/spec-dock-hub/SKILL.md` exists while old path is removed.

## 7. Source of Record

Design evidence sources:

- Requirement decisions: `spec-dock/active/issue/requirement.md`
- Compatibility and naming answers: the two interview discussion artifacts.
- Surface classification: `20260612t072453z-research-spec-dock-hub-rename-surface-inventory.md`
- Repository boundary: `AGENTS.md`
- Implementation contracts: `src/spec_dock/cli.py` and tests under `tests/cli_runtime/` and `tests/unit/infra/`

Canonical adoption target:

- `spec-dock/active/issue/design.md`

This draft does not claim adoption, canonical authority, phase promotion, or reviewer pass.

## 8. Data Flow / Domain Model / Interface Contract

Install/update flow:

```text
package assets
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md
      |
      | _MANAGED_SKILL_NAMES current entry
      v
consumer repo
  .agents/skills/spec-dock-hub/SKILL.md
      |
      | Codex skill discovery
      v
agent reads SpecDock hub and routes to leaf skills
```

Update cleanup flow for existing consumers:

```text
existing target has old managed path
  .agents/skills/spec-driven-tdd-workflow/SKILL.md
      |
      | _LEGACY_MANAGED_SKILL_NAMES cleanup ownership
      v
update prunes obsolete old path
      |
      v
target keeps only current hub path
  .agents/skills/spec-dock-hub/SKILL.md
```

Interface contract:

- Skill name/path visible to agents: `spec-dock-hub`.
- Old name visibility on current surface: absent.
- Old name visibility in historical evidence: allowed and documented as historical.

## 9. File / Module Change Plan

Provider skill:

- Move `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/` to `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/`.
- Update frontmatter `name`, `description`, and heading.
- Keep leaf routing references unchanged except where they mention the old hub name.

Dogfooding mirror:

- Move `.agents/skills/spec-driven-tdd-workflow/` to `.agents/skills/spec-dock-hub/`.
- Keep bytes aligned with provider after final content update.

Installer/update:

- In `src/spec_dock/cli.py`, replace `_MANAGED_SKILL_NAMES` entry with `spec-dock-hub`.
- Preserve `spec-driven-tdd-workflow` in `_LEGACY_MANAGED_SKILL_NAMES` as obsolete managed cleanup metadata unless implementation inspection proves another pruning contract covers it.
- Do not add a copy source, shim, alias, or new compatibility branch for the old name.

Docs:

- Update `README.md` current skill list from `spec-driven-tdd-workflow/` to `spec-dock-hub/`.
- Update `src/spec_dock/assets/spec_dock/docs/README.md` hub path.
- Update `spec-dock/docs/README.md` hub path.

Tests:

- Update `tests/cli_runtime/harness.py` expected managed skill names.
- Update `tests/cli_runtime/test_wrappers.py` installed hub path read.
- Update `tests/unit/infra/test_init_update.py` parity maps, required installed file lists, provider duplicate boundaries, bundled asset coverage, routing contract reads, and any update fixture paths.
- Add or update assertions that stale `.agents/skills/spec-driven-tdd-workflow/SKILL.md` is pruned on update while custom non-managed skills survive.
- Add or update negative assertions that installed target does not contain `spec-driven-tdd-workflow` as a managed current skill.

No canonical docs, implementation, tests, or configs are edited by this delegated draft.

## 10. Migration / Compatibility / Rollback

Migration:

- New installs receive `spec-dock-hub` only.
- Existing consumer updates receive `spec-dock-hub` and should have obsolete managed `spec-driven-tdd-workflow` pruned.
- Custom user skills under unrelated names remain untouched.

Compatibility:

- No compatibility alias, forwarding skill, or old discovery entry.
- `_LEGACY_MANAGED_SKILL_NAMES` may still include the old name as cleanup metadata; this is not user-facing compatibility.

Rollback:

- Revert the provider/mirror directory rename, managed list change, docs references, and tests together.
- Re-run focused init/update tests to confirm old managed skill behavior is restored.
- If a release already shipped the new name, rollback must consider consumer repos that now have `spec-dock-hub`; that would require a separate compatibility decision and is outside this issue's approved no-alias requirement.

## 11. Observability

Required evidence to record in canonical report after implementation:

- `rg` inventory before/after for current surfaces.
- Provider/mirror parity result.
- Focused pytest results for installer/update and wrapper tests.
- `./spec-dock/scripts/spec-dock validate` result.
- `./spec-dock/scripts/spec-dock sync` result or explicit no-op rationale.
- Final scoped negative inspection showing old name absent from current runtime/discovery/docs/test surfaces, with historical evidence exclusions documented.

## 12. Test Strategy

Focused commands:

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "managed_skill or bundled_skill or prunes or parity or routing_contract or guidance"
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/cli_runtime
```

Fallback command if focused selection is too brittle:

```bash
uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py tests/cli_runtime/harness.py
```

Dogfooding verification:

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

Current-surface inspection:

```bash
rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills
rg -n "spec-dock-hub" README.md src/spec_dock/cli.py src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md tests/cli_runtime tests/unit/infra src/spec_dock/assets/install_root/.agents/skills .agents/skills
```

Expected first command result after implementation:

- No hits for old name in the listed current surfaces, except deliberate negative-test strings if tests need to seed stale old paths. If such fixture strings remain, they must be clearly in obsolete cleanup tests, not in installed current skill lists or docs.

## 13. ADR Candidates

- No ADR is required for this issue-local rename because the user-approved requirement already fixes the product name and compatibility policy.
- Possible future ADR: general skill naming policy for SpecDock hub/leaf names if more skill renames are planned.

## 14. Risks

- `_LEGACY_MANAGED_SKILL_NAMES` can be misread as compatibility if not documented/tested as cleanup-only.
- A global negative `rg` can fail on valid historical evidence; scope must be explicit.
- Missing one test fixture path can leave update tests passing for new install while existing consumers retain the old hub path.
- Manual provider/mirror edits can drift unless parity tests are run.
- Description-only changes could accidentally weaken the hub/leaf boundary by pulling leaf workflow steps into the hub.

## 15. Requirement Clarification Requests

None.

Technical follow-up for the main orchestrator, not a user clarification:

- During implementation, decide whether keeping `spec-driven-tdd-workflow` in `_LEGACY_MANAGED_SKILL_NAMES` is sufficient and necessary for pruning, or whether an explicit obsolete path test should drive a smaller cleanup mechanism. This does not change the requirement because both options expose no compatibility alias.

## 16. Integration Notes for Main Orchestrator

Recommended design adoption points:

- Adopt the hard-cutover architecture: provider/mirror rename, current managed list rename, docs/test update, cleanup-only legacy ownership.
- In canonical `design.md`, explicitly state that `spec-driven-tdd-workflow` may appear in historical issue evidence and in cleanup test fixtures only.
- In canonical `plan.md`, split implementation into:
  1. Provider/mirror skill rename and metadata update.
  2. Installer managed/legacy ownership update.
  3. Docs current-surface update.
  4. Tests/parity/update cleanup update.
  5. Scoped negative inspection and dogfooding validation.
- In `report.md`, record this draft in Delegated Draft Evidence and Evidence Adoption Ledger only after the orchestrator reviews it.

Unresolved requirement gaps: none.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
