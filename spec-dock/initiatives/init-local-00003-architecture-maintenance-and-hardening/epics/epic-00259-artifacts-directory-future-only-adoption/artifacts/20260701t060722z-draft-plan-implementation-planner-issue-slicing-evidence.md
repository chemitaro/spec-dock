---
created_by_role: implementation-planner
scope_id: epic-00259
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/docs/workflow_epic.md
  - spec-dock/docs/workflow_spec_authoring.md
  - spec-dock/docs/phase_plan.md
  - spec-dock/docs/phase_plan_epic.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/requirement.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/design.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/report.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t043624z-interview-delegated-authoring-artifact-boundary.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t044839z-interview-blank-versus-scratch-artifact-template.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t050929z-interview-adr-artifact-boundary.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t051314z-interview-future-adr-command-surface.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t052324z-interview-draft-artifact-command-boundary.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t052702z-interview-new-doc-removal-failure-mode.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t055220z-interview-legacy-discussions-validation-boundary.md
  - /Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/templates/README.md
  - src/spec_dock/assets/spec_dock/templates/discussions
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_delegated_authoring.py
intended_targets:
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: not_run
---

# Implementation Planner Evidence: Epic-00259 Issue Slicing

## 1. Plan Summary

This draft is planning evidence only. It proposes Issue slices, dependency order, verification gates, rollout sequencing, and canonical plan sections for `epic-00259`.

The current canonical Epic `requirement.md`, `design.md`, and `plan.md` are still scaffold placeholders. The operative planning input is the accepted ADR `20260701t055644z-adr-artifacts-future-only-command-unification.md`, supported by the answered interviews and the external ZIP pack. The ZIP pack remains useful for the original Phase 2 work breakdown and file map, but it is superseded wherever it conflicts with the accepted ADR.

Key accepted ADR deltas from the ZIP pack:

- Future artifact creation is unified under `new artifact`, including ADR, draft artifacts, and delegated authoring outputs.
- `new doc` is removed from parser, help, and command registry. There is no compatibility alias and no fail-fast migration shim.
- Future ADR originals live under `artifacts/`; legacy ADR originals under `discussions/` remain in place.
- Draft artifacts remain safety-sensitive and keep existing assurance/profile selection and no-write fail-closed behavior while moving output to `artifacts/`.
- Delegated authoring permission boundary, diff guard, validation, and safety checks move from `discussions/` direct child to `artifacts/` direct child.
- Existing `discussions/` files are not moved, renamed, deleted, or link-rewritten. Legacy `discussions/` validation remains strict.

## 2. Requirement / Design Traceability

Because canonical E-RQ / E-AC are not yet written, the following closure set should be reflected into Epic requirement/design before plan adoption.

| Proposed closure id | Source evidence | Planning implication |
|---|---|---|
| E-RQ-001 Future artifact command unification | ADR Decision; interviews for future ADR command, draft boundary, and new doc removal | All future working artifact creation goes through `new artifact`; `new doc` is removed, not aliased. |
| E-RQ-002 Legacy evidence preservation | ADR Decision; policy boundary interview; legacy validation interview | Existing `discussions/` remain valid and strict; no migration, rename, deletion, or link rewrite. |
| E-RQ-003 Safety-sensitive artifact migration | ADR Decision; draft boundary interview; delegated authoring interview | ADR, draft-* and delegated authoring outputs move to `artifacts/` without weakening assurance/profile/diff-guard fail-closed behavior. |
| E-RQ-004 Runtime projection consistency | ADR Consequences; ZIP validation plan and suggested file map; current sync/validation code | validate/sync/.agent/ADR mirror must distinguish canonical docs, future artifacts, and legacy discussions. |
| E-RQ-005 Provider/dogfooding parity | Initiative design guardrails; repo AGENTS dogfooding rule | Provider-side assets are changed first; dogfooding workspace is inspected or refreshed only as validation evidence. |

| Proposed E-AC | Closure evidence needed |
|---|---|
| E-AC-001 | `new artifact` can create blank, typed, ADR, draft-*, and delegated evidence artifacts under `artifacts/`; blank filenames omit `blank`; typed filenames include type; no output goes to `discussions/`. |
| E-AC-002 | `new doc` is absent from parser/help/registry and legacy invocations fail as unknown command / argparse behavior with no shim or alias. |
| E-AC-003 | Existing `discussions/` paths remain unchanged and strict validation still catches malformed discussion-intent filenames and duplicate timestamp/doc_id slots. |
| E-AC-004 | validate/sync accept old-only, new-only, and mixed nodes, while ADR mirror collects valid ADR originals from both `discussions/` and `artifacts/`. |
| E-AC-005 | Draft and delegated authoring artifact creation preserve fail-closed assurance/profile/diff-guard behavior after the boundary changes to `artifacts/`. |
| E-AC-006 | Provider docs, installed skills, README, templates, and dogfooding evidence consistently direct future working artifact creation to `new artifact`. |

## 3. Milestones

M0: Canonical adoption prerequisite

- Reflect the accepted ADR into Epic `requirement.md` and `design.md`.
- Convert the proposed E-RQ/E-AC above into canonical wording.
- Run fresh reviewer gates before treating this draft as plan input.

M1: Artifact contract foundation

- Define artifact filename/domain model, strict artifact validation, and legacy discussion non-interference.
- Define template source strategy for generic templates, ADR, draft-*, and delegated evidence.

M2: Runtime command and safety boundary

- Add `new artifact` creation path and remove `new doc`.
- Move ADR, draft-* and delegated authoring creation/safety boundaries to `artifacts/`.

M3: Scaffold, projection, and mirror integration

- Change future node scaffold to `artifacts/`.
- Update validate, sync, `.agent` projection, and ADR mirror for old/new/mixed states.

M4: Documentation and dogfooding rollout

- Update provider-side docs, installed skills, README, template guidance.
- Dogfood with `artifacts/` without migrating existing `discussions/`.

M9: Epic final quality gate

- Run focused test lanes, `validate`, `sync`, provider/dogfooding parity checks, and final fresh reviews.

## 4. Dependency-Derived Execution Order

```text
T0 canonical adoption gate
  -> T1 contract foundation
       -> T2 command/safety implementation
            -> T3 scaffold/projection integration
                 -> T4 docs/dogfooding rollout
                      -> T9 final Epic gate
```

Dependency rationale:

- `new artifact` should not be implemented before filename/type/domain rules exist.
- ADR/draft/delegated migration depends on both artifact output and safety-sensitive template/assurance strategy.
- New node scaffold can begin after artifact directory/rules assets exist, but final acceptance depends on validate/sync accepting old/new/mixed nodes.
- Docs/skills should be updated after runtime behavior and failure modes are fixed, otherwise agent guidance will drift.
- Dogfooding must be last because it proves the integrated behavior and should not compensate for missing runtime tests.

## 5. Issue / Step Slicing

No Issues are created by this draft. Titles/slugs below are candidate Issue definitions only.

### Candidate 01: Adopt Artifacts ADR Into Epic Specs

- slug: `adopt-artifacts-adr-into-epic-specs`
- grade: strict
- responsibility:
  - Reflect accepted ADR and answered interviews into canonical Epic requirement/design/plan.
  - Resolve ZIP-vs-ADR conflicts explicitly in the plan/report evidence.
  - Define final E-RQ/E-AC and non-scope before implementation Issues are created.
- non-scope:
  - Runtime implementation.
  - Issue creation beyond the main orchestrator's later action.
- closes:
  - E-RQ-001 through E-RQ-005 as canonical planning input.
- depends on:
  - none, but requires fresh reviewer gates after edits.

### Candidate 02: Add Artifact Domain Model And Filename Contract

- slug: `add-artifact-domain-model-and-filename-contract`
- grade: strict
- responsibility:
  - Add artifact types, filename parser/generator, timestamp collision handling, malformed candidate detection, and duplicate checks.
  - Include blank, generic typed artifacts, ADR, draft-requirement, draft-design, draft-plan, and delegated-evidence-compatible type handling as required by ADR.
  - Preserve legacy discussion parser behavior.
- non-scope:
  - CLI command wiring.
  - Node scaffold changes.
- closes:
  - E-RQ-001, E-RQ-002, E-RQ-003.
- depends on:
  - Candidate 01.

### Candidate 03: Add Artifact Templates And Safety-Sensitive Template Sources

- slug: `add-artifact-templates-and-safety-sensitive-sources`
- grade: strict
- responsibility:
  - Add generic artifact templates and `artifacts/rules.md`.
  - Define how ADR template output is created under `artifacts/`.
  - Preserve draft-* canonical/profile template sourcing and assurance/profile fail-closed checks while changing output location.
  - Keep `scratch` as legacy-only if canonical requirement confirms `blank` replaces future raw capture.
- non-scope:
  - Command parser removal.
  - Dogfooding creation.
- closes:
  - E-RQ-001, E-RQ-003.
- depends on:
  - Candidate 02.

### Candidate 04: Add `new artifact` And Remove `new doc`

- slug: `add-new-artifact-and-remove-new-doc`
- grade: critical
- responsibility:
  - Add parser/registry/use-case/presentation support for `spec-dock new artifact <type> --{initiative|epic|issue} ...`.
  - Remove `new doc` from parser/help/registry without alias or shim.
  - Ensure all future creation writes to `artifacts/`, auto-creating the directory when allowed.
  - Preserve no-overwrite, scope resolution, slug validation, and post-write duplicate guard semantics.
- non-scope:
  - Scaffold defaults.
  - Sync projection updates unless required for command tests.
- closes:
  - E-AC-001, E-AC-002.
- depends on:
  - Candidate 02 and Candidate 03.

### Candidate 05: Move Draft And Delegated Authoring Boundaries To Artifacts

- slug: `move-draft-and-delegated-authoring-boundaries-to-artifacts`
- grade: critical
- responsibility:
  - Change draft-requirement/design/plan creation to `new artifact` output under `artifacts/`.
  - Update issue profile draft assurance checks and missing/stale/invalid no-write behavior.
  - Update delegated authoring diff guard from `discussions/` direct child to `artifacts/` direct child.
  - Keep required frontmatter checks for delegated evidence and forbid canonical/source/tests/package/config writes.
- non-scope:
  - Relaxing delegated authoring policy.
  - Claiming reviewer pass or implementation readiness.
- closes:
  - E-RQ-003, E-AC-005.
- depends on:
  - Candidate 04.

### Candidate 06: Switch Future Node Scaffold To Artifacts

- slug: `switch-future-node-scaffold-to-artifacts`
- grade: strict
- responsibility:
  - Change provider-side initiative/epic/issue templates and scaffold logic so new nodes include `artifacts/` and not default `discussions/`.
  - Keep old nodes valid and avoid any migration or link rewrite.
  - Ensure installer/update behavior preserves legacy node contents.
- non-scope:
  - Removing legacy discussion validation.
  - Editing dogfooding data as source of truth.
- closes:
  - E-RQ-004, E-AC-003.
- depends on:
  - Candidate 03; final acceptance depends on Candidate 07.

### Candidate 07: Update Validate, Sync, ADR Mirror, And Agent Projection

- slug: `update-validate-sync-adr-mirror-and-agent-projection`
- grade: critical
- responsibility:
  - Add strict `artifacts/` filename/duplicate validation.
  - Keep strict legacy `discussions/` malformed/duplicate validation.
  - Make validate/sync accept old-only, new-only, and mixed nodes.
  - Update ADR mirror to collect valid ADR originals from both `discussions/` and `artifacts/`.
  - Ensure `.agent` output labels canonical docs, future artifacts, and legacy discussions without promoting artifacts to canonical authority.
- non-scope:
  - Content-level validation for every artifact type beyond safety-sensitive draft/delegated checks.
- closes:
  - E-RQ-002, E-RQ-004, E-AC-003, E-AC-004.
- depends on:
  - Candidate 02, Candidate 04, Candidate 06.

### Candidate 08: Update Workflow Docs, Skills, README, And Templates Guidance

- slug: `update-workflow-docs-skills-readme-and-template-guidance`
- grade: strict
- responsibility:
  - Update provider-side workflow docs, phase docs, rules docs, installed skills, and README examples.
  - Remove `new doc` future instructions and replace with `new artifact`.
  - Explain legacy `discussions/` validity and strict validation without recommending future creation there.
  - Keep delegated authoring docs aligned with `artifacts/` boundary and Evidence Adoption Ledger rules.
- non-scope:
  - Runtime behavior not already implemented.
- closes:
  - E-RQ-005, E-AC-006.
- depends on:
  - Candidate 04, Candidate 05, Candidate 07.

### Candidate 09: Dogfood Artifacts Future Surface Without Migrating Discussions

- slug: `dogfood-artifacts-future-surface-without-migrating-discussions`
- grade: standard
- responsibility:
  - Use the finished `new artifact` command in a low-risk dogfooding scope.
  - Create one blank artifact and one typed/ADR/draft-compatible artifact as selected by the canonical plan.
  - Confirm existing `discussions/` files were not renamed, moved, deleted, or link-rewritten.
  - Run `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync`.
  - Record evidence for Epic report adoption.
- non-scope:
  - Mass migration.
  - Cleanup of historical discussions.
- closes:
  - E-AC-001 through E-AC-006 as integrated smoke evidence.
- depends on:
  - Candidates 04, 05, 06, 07, and 08.

## 6. Test Strategy Mapping

| Test lane | Candidate Issues | E-RQ / E-AC mapped |
|---|---|---|
| Domain unit tests for artifact filenames | 02 | E-RQ-001, E-RQ-002, E-AC-001, E-AC-003 |
| CLI runtime tests for `new artifact` | 04 | E-RQ-001, E-AC-001 |
| CLI negative tests for removed `new doc` | 04, 08 | E-RQ-001, E-AC-002 |
| Safety-sensitive draft artifact tests | 03, 05 | E-RQ-003, E-AC-005 |
| Delegated authoring diff guard tests | 05 | E-RQ-003, E-AC-005 |
| Scaffold and installer/update tests | 06 | E-RQ-004, E-AC-003 |
| Validate old/new/mixed and malformed artifacts | 02, 07 | E-RQ-002, E-RQ-004, E-AC-003, E-AC-004 |
| Sync / `.agent` / ADR mirror tests | 07 | E-RQ-004, E-AC-004 |
| Docs and skill grep checks | 08 | E-RQ-005, E-AC-006 |
| Dogfooding smoke | 09 | E-AC-001 through E-AC-006 |

Minimum focused commands expected by tranche:

- T1: `uv run pytest tests/unit/domain_runtime tests/unit/domain tests/unit/application -k 'artifact or discussion or validation'`
- T2: `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_delegated_authoring.py tests/unit/domain/test_delegated_authoring.py`
- T3: `uv run pytest tests/cli_runtime/test_sync.py tests/unit/presentation/test_runtime_sync_s07.py tests/unit/infra/test_init_update.py`
- T4: `rg "new doc|new artifact|discussions/|artifacts/" README.md src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents src/spec_dock/assets/spec_dock/templates`
- T9: `uv run pytest`, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync`

The exact test selection should be narrowed by each Issue plan after inspecting local ownership and runtime test cost.

## 7. Review Gates

G0: Canonical spec gate

- Epic requirement/design/plan adopt the accepted ADR.
- Fresh `spec-reviewer` passes requirement and design before this plan evidence is adopted.

G1: Foundation gate

- Artifact filename/domain contract has tests for typed, blank, ADR, draft-*, collision, malformed, duplicate, and legacy non-interference.
- No runtime command writes to `artifacts/` until contract tests pass.

G2: Command and safety gate

- `new artifact` writes only to `artifacts/`.
- `new doc` is absent from the command surface.
- Draft/delegated fail-closed tests pass.

G3: Integration checkpoint

- New node scaffold and validate/sync/ADR mirror are consistent for old-only, new-only, and mixed layouts.
- `.agent` projection does not treat artifacts as canonical requirement/design/plan/report.

G4: Docs rollout gate

- Provider docs and installed skills stop instructing future `new doc` creation.
- Legacy `discussions/` is documented as valid historical evidence, not as future creation surface.

G9: Final Epic quality gate

- Full focused or full baseline test evidence is recorded.
- Dogfooding evidence exists.
- Fresh `spec-reviewer` and any required code/review gates are complete before implementation handoff is claimed by the main orchestrator.

## 8. Rollback / Compatibility

- Existing `discussions/` rollback is preservation-based: there is no migration to reverse.
- Reverting `new artifact` implementation should not require moving historical files; any already-created `artifacts/` files remain working evidence and can be read directly.
- If `new doc` removal causes unacceptable runtime breakage during implementation, rollback is a code/docs revert, not an alias or shim, unless canonical design is reopened.
- Artifact validation should fail closed for malformed future artifact intent, while old nodes without `artifacts/` remain valid.
- ADR mirror rollback must avoid deleting original ADR sources in either `discussions/` or `artifacts/`; only generated mirror outputs are rebuildable.

## 9. Docs Impact

Provider-side docs and assets are the source of truth:

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `src/spec_dock/assets/spec_dock/templates/README.md`
- `src/spec_dock/assets/install_root/.agents/skills/**/SKILL.md`
- `README.md`

Dogfooding docs under `spec-dock/` should be inspected after provider changes and refreshed only through the intended scaffold/update path or explicit dogfooding validation steps.

## 10. Final Quality Gate

Epic exit should require all of the following:

- Canonical Epic requirement/design/plan are reviewer-gated and contain the final E-RQ/E-AC closure matrix.
- Candidate Issues selected by the main orchestrator are either completed or explicitly deferred with non-blocking rationale.
- `new artifact` is the only future creation command for working artifacts, including ADR, draft-*, and delegated evidence.
- `new doc` is removed with no alias or shim.
- Existing `discussions/` files remain in place and strict validation is preserved.
- validate/sync/ADR mirror/.agent projection pass old-only, new-only, and mixed layout tests.
- Provider docs, installed skills, README, and templates are aligned.
- Dogfooding evidence records created artifact paths, unchanged legacy discussions, validate output, sync output, and follow-up issues if any.
- Final fresh reviews are recorded by the main orchestrator; this draft is not a reviewer pass.

## 11. Plan Blockers

- Canonical Epic `requirement.md`, `design.md`, and `plan.md` are still placeholders. The accepted ADR has not yet been reflected to them.
- Fresh reviewer gates for canonical requirement/design/plan are pending.
- The ZIP pack conflicts with the accepted ADR on `new doc` retention, ADR scope, draft-* scope, and delegated authoring scope. Canonical plan must mark the ADR as superseding the ZIP on those points.
- Current runtime lacks `new artifact`; this evidence was therefore bootstrapped directly under `artifacts/` rather than created by runtime command.
- The target Epic subtree already had untracked interviews/artifacts and a modified `report.md` before this draft. Adoption needs a main-orchestrator diff guard that separates pre-existing work from this single new evidence file.

Unresolved design gaps:

- Final artifact type catalog needs canonical naming for ADR/draft/delegated evidence under `new artifact`.
- Final output text/error behavior for removed `new doc` should state whether generic argparse unknown-command output is sufficient in tests.
- The exact `.agent` projection schema for future artifacts versus legacy discussions should be fixed before Candidate 07.

## 12. Integration Notes for Main Orchestrator

Suggested canonical `plan.md` sections:

- `この計画で閉じる E-RQ / E-AC`
- `Issue slicing policy`
- `Candidate Issue list / tranche`
- `Dependency-derived execution order`
- `Integration checkpoints`
- `Validation / test strategy mapping`
- `Rollout / docs / dogfooding sequence`
- `Issue readiness criteria`
- `Rollback / compatibility`
- `Blockers / deferrals / non-scope`
- `Final Epic exit contract`

Suggested report ledger notes:

- Record this artifact as delegated planning evidence with `adoption_status: unreviewed` until inspected.
- Record the accepted ADR as superseding conflicting ZIP assumptions.
- Record `diff_guard_result: not_run` for this draft unless the main orchestrator runs a fresh artifact-scope diff guard.

Leaf evidence used:

- No child agents or depth=3 delegation were used.
- Evidence sources were local docs, accepted ADR/interviews, ZIP pack contents, and read-only repo inspection.

Forbidden actions avoided:

- No canonical requirement/design/plan/report edit.
- No implementation, test, package/config, `.agents`, `.codex`, `.github`, secret, GitHub mutation, phase promotion, reviewer-pass claim, issue creation, or implementation-readiness claim.

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
